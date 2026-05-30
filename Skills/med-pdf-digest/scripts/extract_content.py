#!/usr/bin/env python3
"""
Med PDF Digest — Automated LLM Content Extractor
=================================================
Calls the Anthropic API to perform structured clinical content extraction,
producing the extraction JSON consumed by generate_digest.py and make_flashcards.py.

Handles large documents by auto-chunking, extracting each section, and merging.

Requirements:
    pip install anthropic

Usage:
    python3 extract_content.py <input.txt> <output.json> [options]
    python3 extract_content.py - <output.json>           # read from stdin

Options:
    --doc-type      textbook|guideline|review|drug_monograph|case_based  (default: auto)
    --specialty     e.g. cardiology, pharmacology, neurology  (default: auto)
    --model         Anthropic model ID  (default: claude-sonnet-4-20250514)
    --chunk-size    Max words per chunk  (default: 12000)
    --save-chunks   Directory to save partial extraction JSONs for recovery
    --depth         brief|standard|comprehensive  (default: standard)
    --verbose       Print detailed progress to stderr

Environment:
    ANTHROPIC_API_KEY   Required. Set before running:
                        export ANTHROPIC_API_KEY=sk-ant-...

Exit codes:
    0  Success
    1  Input/output error
    2  API error
    3  Parse error (JSON from model was invalid)
"""

import os
import sys
import json
import re
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed.\n  Run: pip install anthropic", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Depth-aware extraction schemas
# ---------------------------------------------------------------------------

DEPTH_TARGETS = {
    "brief":          {"pearls": (5, 10),  "traps": (5, 10),  "atoms": (15, 30)},
    "standard":       {"pearls": (15, 30), "traps": (10, 20), "atoms": (40, 80)},
    "comprehensive":  {"pearls": (30, 60), "traps": (20, 40), "atoms": (80, 150)},
}

SYSTEM_PROMPT = """\
You are a precision clinical knowledge extraction engine for medical exam preparation.

RULES (non-negotiable):
1. Extract ONLY content present in the source text. No external knowledge additions.
2. Preserve ALL numeric values exactly — doses, cutoffs, scores, percentages. Never round.
3. Every pearl must satisfy ≥2 of: (a) exam-high-yield, (b) clinically actionable, (c) has a memorable hook.
4. Every MCQ trap must be a real exam pattern — not contrived.
5. Atomic facts must be fully self-contained. No "see above" or forward references.
6. For connections in atomic_facts, use zero-based array indices referring to other atoms in this extraction.

Respond ONLY with a valid JSON object matching the schema. No prose, no markdown fences, no explanation."""

EXTRACTION_USER_TMPL = """\
Extract structured clinical knowledge from the text below.

Document type: {doc_type}
Specialty: {specialty}
Depth target: {depth} ({pearl_min}–{pearl_max} pearls, {trap_min}–{trap_max} traps, {atom_min}–{atom_max} atoms)

Output schema:
{{
  "metadata": {{
    "title": "string",
    "specialty": "string",
    "topics": ["string"],
    "document_type": "textbook|guideline|review|drug_monograph|case_based",
    "word_count_estimate": 0
  }},
  "clinical_approaches": [
    {{
      "name": "string",
      "trigger": "string (when does this algorithm start?)",
      "steps": ["string"],
      "branch_points": [
        {{"condition": "string", "yes_path": "string", "no_path": "string"}}
      ],
      "endpoints": ["string"],
      "mermaid_hint": "string (brief description of algorithm shape)"
    }}
  ],
  "knowledge_hierarchy": {{
    "topic": "string (central node)",
    "subtopics": [
      {{
        "name": "string",
        "color_hint": "red|orange|blue|green|purple|gray",
        "children": [
          {{"name": "string", "detail": "string"}}
        ]
      }}
    ]
  }},
  "clinical_pearls": [
    {{
      "pearl": "string (the clinical fact)",
      "context": "string (when does this matter?)",
      "buzzword": "string or null",
      "associations": ["string"],
      "exam_relevance": "high|medium",
      "why_tested": "string",
      "category": "buzzword_association|classic_presentation|dont_miss|paradox|drug_disease|demographic"
    }}
  ],
  "mcq_traps": [
    {{
      "trap_category": "string (one of the 10 archetypes)",
      "scenario": "string (brief clinical vignette)",
      "distractor": "string (what looks right but is not)",
      "correct_answer": "string",
      "why_tricky": "string",
      "avoidance_strategy": "string",
      "topic": "string"
    }}
  ],
  "atomic_facts": [
    {{
      "fact": "string (one self-contained clinical statement)",
      "category": "Diagnosis|Treatment|Pharmacology|Pathophysiology|Epidemiology|Classification|Monitoring",
      "connections": [0],
      "source_section": "string",
      "high_yield": true
    }}
  ],
  "simplified_sections": [
    {{
      "original_heading": "string",
      "simplified_text": "string (plain language, all details preserved)",
      "key_details_preserved": ["string"]
    }}
  ]
}}

--- BEGIN CLINICAL TEXT ---
{text}
--- END CLINICAL TEXT ---"""


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def word_count(text: str) -> int:
    return len(text.split())


def chunk_at_boundaries(text: str, max_words: int) -> list[str]:
    """
    Split text into chunks at double-newline paragraph boundaries.
    Each chunk targets max_words but never splits mid-paragraph.
    """
    paragraphs = re.split(r'\n{2,}', text)
    chunks: list[str] = []
    current: list[str] = []
    current_wc = 0

    for para in paragraphs:
        pwc = word_count(para)
        if current_wc + pwc > max_words and current:
            chunks.append('\n\n'.join(current))
            current = [para]
            current_wc = pwc
        else:
            current.append(para)
            current_wc += pwc

    if current:
        chunks.append('\n\n'.join(current))

    return chunks


# ---------------------------------------------------------------------------
# API call with retry
# ---------------------------------------------------------------------------

def call_api(client: "anthropic.Anthropic", user_message: str, model: str,
             max_retries: int = 3, verbose: bool = False) -> dict:
    """Send a single extraction request to the API. Returns parsed JSON."""
    for attempt in range(1, max_retries + 1):
        try:
            if verbose:
                print(f"    API call attempt {attempt}...", file=sys.stderr)

            response = client.messages.create(
                model=model,
                max_tokens=8000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}]
            )

            raw = response.content[0].text.strip()

            # Strip markdown code fences if model added them despite instructions
            raw = re.sub(r'^```(?:json)?\s*', '', raw)
            raw = re.sub(r'\s*```$', '', raw)

            return json.loads(raw)

        except json.JSONDecodeError as e:
            if attempt < max_retries:
                print(f"    JSON parse error on attempt {attempt}: {e}. Retrying...", file=sys.stderr)
                time.sleep(2 ** attempt)
            else:
                print(f"    FATAL: Could not parse JSON after {max_retries} attempts.", file=sys.stderr)
                # Save the raw response for debugging
                debug_path = f"/tmp/extract_debug_{int(time.time())}.txt"
                with open(debug_path, 'w') as f:
                    f.write(raw)
                print(f"    Raw response saved to {debug_path}", file=sys.stderr)
                raise SystemExit(3)

        except anthropic.RateLimitError:
            wait = 30 * attempt
            print(f"    Rate limited. Waiting {wait}s...", file=sys.stderr)
            time.sleep(wait)

        except anthropic.APIError as e:
            if attempt < max_retries:
                print(f"    API error on attempt {attempt}: {e}. Retrying...", file=sys.stderr)
                time.sleep(5 * attempt)
            else:
                print(f"    FATAL: API error after {max_retries} attempts: {e}", file=sys.stderr)
                raise SystemExit(2)

    raise SystemExit(2)  # Should never reach here


# ---------------------------------------------------------------------------
# Merge partial extractions
# ---------------------------------------------------------------------------

def merge_partial_extractions(partials: list[dict]) -> dict:
    """
    Merge multiple partial extraction JSONs (e.g. from chunked processing).
    Deduplicates pearls, traps, and approaches by content.
    Re-numbers atomic fact connections to account for offset.
    """
    merged = {
        "metadata": {
            "title": "", "specialty": "", "topics": [],
            "document_type": "", "word_count_estimate": 0,
            "extraction_date": datetime.now().isoformat()
        },
        "clinical_approaches": [],
        "knowledge_hierarchy": {"topic": "", "subtopics": []},
        "clinical_pearls": [],
        "mcq_traps": [],
        "atomic_facts": [],
        "simplified_sections": []
    }

    seen_approach_names: set[str] = set()
    seen_pearl_texts: set[str] = set()
    seen_trap_scenarios: set[str] = set()
    atom_offset = 0

    for partial in partials:
        meta = partial.get("metadata", {})
        if not merged["metadata"]["title"] and meta.get("title"):
            merged["metadata"]["title"] = meta["title"]
        if not merged["metadata"]["specialty"] and meta.get("specialty"):
            merged["metadata"]["specialty"] = meta["specialty"]
        if not merged["metadata"]["document_type"] and meta.get("document_type"):
            merged["metadata"]["document_type"] = meta["document_type"]
        for topic in meta.get("topics", []):
            if topic and topic not in merged["metadata"]["topics"]:
                merged["metadata"]["topics"].append(topic)
        merged["metadata"]["word_count_estimate"] = max(
            merged["metadata"]["word_count_estimate"],
            meta.get("word_count_estimate", 0)
        )

        # Clinical approaches — deduplicate by name
        for approach in partial.get("clinical_approaches", []):
            name = approach.get("name", "").strip()
            if name and name not in seen_approach_names:
                seen_approach_names.add(name)
                merged["clinical_approaches"].append(approach)

        # Knowledge hierarchy — merge subtopics
        kh = partial.get("knowledge_hierarchy", {})
        if kh.get("topic") and not merged["knowledge_hierarchy"]["topic"]:
            merged["knowledge_hierarchy"]["topic"] = kh["topic"]
        for sub in kh.get("subtopics", []):
            merged["knowledge_hierarchy"]["subtopics"].append(sub)

        # Pearls — deduplicate by pearl text (first 80 chars)
        for pearl in partial.get("clinical_pearls", []):
            key = pearl.get("pearl", "")[:80]
            if key and key not in seen_pearl_texts:
                seen_pearl_texts.add(key)
                merged["clinical_pearls"].append(pearl)

        # MCQ traps — deduplicate by scenario
        for trap in partial.get("mcq_traps", []):
            key = trap.get("scenario", "")[:80]
            if key and key not in seen_trap_scenarios:
                seen_trap_scenarios.add(key)
                merged["mcq_traps"].append(trap)

        # Atomic facts — re-number connections
        chunk_atoms = partial.get("atomic_facts", [])
        for atom in chunk_atoms:
            new_conns = []
            for c in atom.get("connections", []):
                if isinstance(c, int) and 0 <= c < len(chunk_atoms):
                    new_conns.append(c + atom_offset)
            atom = dict(atom)  # shallow copy
            atom["connections"] = new_conns
            merged["atomic_facts"].append(atom)
        atom_offset += len(chunk_atoms)

        # Simplified sections
        merged["simplified_sections"].extend(partial.get("simplified_sections", []))

    return merged


# ---------------------------------------------------------------------------
# Main extraction orchestrator
# ---------------------------------------------------------------------------

def extract_document(text: str, doc_type: str, specialty: str, depth: str,
                     model: str, chunk_size: int,
                     save_chunks_dir: Optional[str],
                     verbose: bool) -> dict:
    """
    Extract structured content from a clinical text document.
    Automatically chunks large documents.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "ERROR: ANTHROPIC_API_KEY not set.\n"
            "  Export your key: export ANTHROPIC_API_KEY=sk-ant-...",
            file=sys.stderr
        )
        raise SystemExit(2)

    client = anthropic.Anthropic(api_key=api_key)
    targets = DEPTH_TARGETS[depth]
    wc = word_count(text)

    print(f"Document: ~{wc:,} words | model: {model} | depth: {depth}", file=sys.stderr)

    def build_user_msg(chunk_text: str) -> str:
        return EXTRACTION_USER_TMPL.format(
            doc_type=doc_type, specialty=specialty, depth=depth,
            pearl_min=targets["pearls"][0], pearl_max=targets["pearls"][1],
            trap_min=targets["traps"][0],  trap_max=targets["traps"][1],
            atom_min=targets["atoms"][0],  atom_max=targets["atoms"][1],
            text=chunk_text
        )

    if wc <= chunk_size:
        print("Extracting (single pass)...", file=sys.stderr)
        result = call_api(client, build_user_msg(text), model, verbose=verbose)
        result.setdefault("metadata", {})["word_count_estimate"] = wc
        result.setdefault("metadata", {})["extraction_date"] = datetime.now().isoformat()
        return result

    # Large document — chunk and merge
    chunks = chunk_at_boundaries(text, chunk_size)
    print(f"Large document: {len(chunks)} chunks (≤{chunk_size:,} words each)...", file=sys.stderr)

    partials: list[dict] = []
    for i, chunk in enumerate(chunks, 1):
        cwc = word_count(chunk)
        print(f"  [{i}/{len(chunks)}] Extracting ~{cwc:,} words...", file=sys.stderr)
        partial = call_api(client, build_user_msg(chunk), model, verbose=verbose)
        partials.append(partial)

        if save_chunks_dir:
            os.makedirs(save_chunks_dir, exist_ok=True)
            path = os.path.join(save_chunks_dir, f"chunk_{i:03d}.json")
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(partial, f, ensure_ascii=False, indent=2)
            if verbose:
                print(f"    Saved chunk: {path}", file=sys.stderr)

    print("Merging chunks...", file=sys.stderr)
    merged = merge_partial_extractions(partials)
    merged["metadata"]["word_count_estimate"] = wc
    return merged


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Med PDF Digest — Automated LLM Content Extractor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("input",  help="Input text file path, or '-' for stdin")
    parser.add_argument("output", help="Output JSON file path")
    parser.add_argument("--doc-type",   default="auto",
                        choices=["auto", "textbook", "guideline", "review", "drug_monograph", "case_based"],
                        help="Document type (default: auto-detected)")
    parser.add_argument("--specialty",  default="auto",
                        help="Medical specialty hint (default: auto-detected)")
    parser.add_argument("--model",      default="claude-sonnet-4-20250514",
                        help="Anthropic model ID")
    parser.add_argument("--chunk-size", type=int, default=12000,
                        help="Max words per extraction chunk (default: 12000)")
    parser.add_argument("--save-chunks", metavar="DIR",
                        help="Directory to save partial JSONs (useful for large docs / recovery)")
    parser.add_argument("--depth",      default="standard",
                        choices=["brief", "standard", "comprehensive"],
                        help="Extraction depth (default: standard)")
    parser.add_argument("--verbose",    action="store_true",
                        help="Print detailed progress")

    args = parser.parse_args()

    # Read input
    try:
        if args.input == "-":
            text = sys.stdin.read()
        else:
            text = Path(args.input).read_text(encoding='utf-8')
    except (FileNotFoundError, PermissionError) as e:
        print(f"ERROR: Cannot read input: {e}", file=sys.stderr)
        raise SystemExit(1)

    text = text.strip()
    if not text:
        print("ERROR: Input text is empty.", file=sys.stderr)
        raise SystemExit(1)

    # Run extraction
    start = time.time()
    result = extract_document(
        text=text,
        doc_type=args.doc_type,
        specialty=args.specialty,
        depth=args.depth,
        model=args.model,
        chunk_size=args.chunk_size,
        save_chunks_dir=args.save_chunks,
        verbose=args.verbose
    )
    elapsed = time.time() - start

    # Write output
    try:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
    except (PermissionError, OSError) as e:
        print(f"ERROR: Cannot write output: {e}", file=sys.stderr)
        raise SystemExit(1)

    # Summary
    meta = result.get("metadata", {})
    print(f"\nExtraction complete ({elapsed:.1f}s):", file=sys.stderr)
    print(f"  Title:     {meta.get('title', 'N/A')}", file=sys.stderr)
    print(f"  Specialty: {meta.get('specialty', 'N/A')}", file=sys.stderr)
    print(f"  Approaches:{len(result.get('clinical_approaches', []))}", file=sys.stderr)
    print(f"  Pearls:    {len(result.get('clinical_pearls', []))}", file=sys.stderr)
    print(f"  Traps:     {len(result.get('mcq_traps', []))}", file=sys.stderr)
    print(f"  Atoms:     {len(result.get('atomic_facts', []))}", file=sys.stderr)
    print(f"  Sections:  {len(result.get('simplified_sections', []))}", file=sys.stderr)
    print(f"  Output:    {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
