#!/usr/bin/env python3
"""
Med PDF Digest — Flashcard Exporter
====================================
Converts extraction JSON into study flashcard formats:
  - Anki TSV     (import via File → Import in Anki; two-field Basic note type)
  - Quizlet CSV  (import via quizlet.com/create-set → Import)
  - Markdown     (human-readable cards for Obsidian, Notion, printing)

Usage:
    python3 make_flashcards.py <extraction.json> [options]

Options:
    --format    anki|quizlet|markdown|all   (default: all)
    --output    Output file path prefix     (default: derived from input filename)
    --include   pearls,traps,atoms,all      (default: pearls,traps)
    --depth     all|high-yield-only         (default: all)

Output files:
    <prefix>_anki.tsv        Anki-compatible tab-separated values
    <prefix>_quizlet.csv     Quizlet-compatible CSV
    <prefix>_review.md       Markdown flashcards for manual review / printing

Anki Import Instructions:
    1. In Anki: File → Import
    2. Select the .tsv file
    3. Note type: Basic
    4. Fields: Front [Tab] Back [Tab] Tags
    5. Allow HTML: Yes
    6. Field separator: Tab
"""

import json
import sys
import csv
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Card generation
# ---------------------------------------------------------------------------

def make_pearl_cards(pearls: list[dict], high_yield_only: bool) -> list[dict]:
    """Convert clinical pearls to flashcard dicts {front, back, tags}."""
    cards = []
    for pearl in pearls:
        if high_yield_only and pearl.get("exam_relevance") != "high":
            continue

        buzzword = pearl.get("buzzword", "")
        context = pearl.get("context", "")
        assoc = ", ".join(pearl.get("associations", []))
        why = pearl.get("why_tested", "")
        category = pearl.get("category", "").replace("_", " ")

        # Front: the clinical context / question
        if buzzword:
            front = f"<b>Clinical Pearl:</b><br><em>'{buzzword}'</em> — What does this classic buzzword indicate?"
        elif context:
            front = f"<b>Clinical Pearl:</b><br>{context}"
        else:
            front = f"<b>Clinical Pearl</b> ({category})"

        # Back: the pearl + context
        back_parts = [f"<b>{pearl.get('pearl', '')}</b>"]
        if assoc:
            back_parts.append(f"<br><em>Associations:</em> {assoc}")
        if why:
            back_parts.append(f"<br><em>Why boards test this:</em> {why}")

        cards.append({
            "front": front,
            "back": "".join(back_parts),
            "tags": f"med-digest::pearls {category.replace(' ', '-')}"
        })

    return cards


def make_trap_cards(traps: list[dict]) -> list[dict]:
    """Convert MCQ traps to flashcard dicts."""
    cards = []
    for trap in traps:
        scenario = trap.get("scenario", "")
        distractor = trap.get("distractor", "")
        correct = trap.get("correct_answer", "")
        why = trap.get("why_tricky", "")
        avoid = trap.get("avoidance_strategy", "")
        category = trap.get("trap_category", "")
        topic = trap.get("topic", "")

        front = (
            f"<b>MCQ Trap — {category}</b><br><br>"
            f"{scenario}<br><br>"
            f"<em>What looks correct but is wrong?</em><br>"
            f"<span style='color:#c0392b'>{distractor}</span>"
        )

        back_parts = [f"<b>Correct Answer:</b> {correct}"]
        if why:
            back_parts.append(f"<br><br><em>Why tricky:</em> {why}")
        if avoid:
            back_parts.append(f"<br><br><em>How to avoid:</em> {avoid}")

        cards.append({
            "front": front,
            "back": "<br>".join(back_parts),
            "tags": f"med-digest::traps {category.replace(' ', '-')} {topic.replace(' ', '-')}"
        })

    return cards


def make_atom_cards(atoms: list[dict], high_yield_only: bool) -> list[dict]:
    """Convert atomic facts to flashcard dicts."""
    cards = []
    for i, atom in enumerate(atoms):
        if high_yield_only and not atom.get("high_yield"):
            continue

        fact = atom.get("fact", "")
        category = atom.get("category", "")
        source = atom.get("source_section", "")

        # Split the fact into a question-answer format when possible
        # Simple heuristic: if fact contains " is ", " are ", " causes ", " indicates "
        question = None
        for separator in [" is characterized by ", " is defined as ", " causes ", " indicates "]:
            if separator in fact.lower():
                idx = fact.lower().index(separator)
                subject = fact[:idx]
                predicate = fact[idx:]
                question = f"Complete: <em>{subject} ___________</em>"
                break

        if not question:
            question = (
                f"<b>Atomic Fact — {category}</b><br>"
                f"<em>What is the key clinical statement about:</em><br>"
                f"{fact[:60]}..."
            ) if len(fact) > 60 else f"<b>{category}:</b><br>{fact}"

        back = f"<b>{fact}</b>"
        if source:
            back += f"<br><br><em>Source: {source}</em>"

        hy_marker = " high-yield" if atom.get("high_yield") else ""
        cards.append({
            "front": question,
            "back": back,
            "tags": f"med-digest::atoms {category.replace(' ', '-')}{hy_marker}"
        })

    return cards


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------

def write_anki_tsv(cards: list[dict], path: str) -> int:
    """Write Anki-compatible TSV. Returns card count."""
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        # Anki ignores the header but it helps humans reading the file
        # writer.writerow(["Front", "Back", "Tags"])
        for card in cards:
            writer.writerow([card["front"], card["back"], card["tags"]])
    return len(cards)


def write_quizlet_csv(cards: list[dict], path: str) -> int:
    """Write Quizlet-compatible CSV (Term, Definition)."""
    # Quizlet: comma-separated, each field in quotes, one card per line
    # Strip HTML tags for Quizlet (it doesn't render HTML)
    def strip_html(s: str) -> str:
        return re.sub(r'<[^>]+>', '', s).strip()

    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for card in cards:
            writer.writerow([strip_html(card["front"]), strip_html(card["back"])])
    return len(cards)


def write_markdown(cards: list[dict], path: str, title: str, meta: dict) -> int:
    """Write human-readable Markdown flashcards for Obsidian/printing."""
    specialty = meta.get("specialty", "")
    date = datetime.now().strftime("%Y-%m-%d")

    lines = [
        f"# {title} — Flashcards",
        f"**Specialty:** {specialty}  **Generated:** {date}  **Total cards:** {len(cards)}",
        "",
        "---",
        ""
    ]

    def strip_html(s: str) -> str:
        return re.sub(r'<[^>]+>', '', s).strip()

    # Group by tag prefix
    current_group = ""
    for i, card in enumerate(cards, 1):
        tag_group = card["tags"].split("::")[1].split(" ")[0] if "::" in card["tags"] else "misc"
        if tag_group != current_group:
            current_group = tag_group
            lines.append(f"## {current_group.upper()}")
            lines.append("")

        front = strip_html(card["front"])
        back = strip_html(card["back"])
        lines += [
            f"### Card {i}",
            f"**Q:** {front}",
            f"",
            f"**A:** {back}",
            f"",
            f"---",
            ""
        ]

    with open(path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    return len(cards)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Med PDF Digest — Flashcard Exporter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("input", help="Path to extraction JSON from extract_content.py")
    parser.add_argument("--format", default="all",
                        choices=["anki", "quizlet", "markdown", "all"],
                        help="Output format(s) (default: all)")
    parser.add_argument("--output", default=None,
                        help="Output file path prefix (default: same dir as input, no extension)")
    parser.add_argument("--include", default="pearls,traps",
                        help="Content to include: comma-separated list of pearls,traps,atoms or 'all'")
    parser.add_argument("--depth", default="all",
                        choices=["all", "high-yield-only"],
                        help="Include all cards or only high-yield ones (default: all)")

    args = parser.parse_args()

    # Load extraction JSON
    try:
        data = json.loads(Path(args.input).read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: Cannot load extraction JSON: {e}", file=sys.stderr)
        sys.exit(1)

    meta = data.get("metadata", {})
    title = meta.get("title", "Clinical Digest")
    high_yield_only = args.depth == "high-yield-only"

    # Determine output prefix
    if args.output:
        prefix = args.output
    else:
        input_stem = Path(args.input).stem
        prefix = str(Path(args.input).parent / input_stem)

    # Determine what to include
    include_all = "all" in args.include
    include_pearls = include_all or "pearls" in args.include
    include_traps  = include_all or "traps"  in args.include
    include_atoms  = include_all or "atoms"  in args.include

    # Build card sets
    pearl_cards = make_pearl_cards(data.get("clinical_pearls", []), high_yield_only) if include_pearls else []
    trap_cards  = make_trap_cards(data.get("mcq_traps", []))                          if include_traps  else []
    atom_cards  = make_atom_cards(data.get("atomic_facts", []), high_yield_only)      if include_atoms  else []

    all_cards = pearl_cards + trap_cards + atom_cards

    if not all_cards:
        print("WARNING: No cards generated. Check that the extraction JSON has content.", file=sys.stderr)
        sys.exit(0)

    print(f"\nCard breakdown:", file=sys.stderr)
    if include_pearls: print(f"  Pearls: {len(pearl_cards)}", file=sys.stderr)
    if include_traps:  print(f"  Traps:  {len(trap_cards)}", file=sys.stderr)
    if include_atoms:  print(f"  Atoms:  {len(atom_cards)}", file=sys.stderr)
    print(f"  Total:  {len(all_cards)}", file=sys.stderr)

    # Write outputs
    fmt = args.format
    written = []

    if fmt in ("anki", "all"):
        path = f"{prefix}_anki.tsv"
        n = write_anki_tsv(all_cards, path)
        print(f"\nAnki TSV:  {path}  ({n} cards)", file=sys.stderr)
        written.append(path)

    if fmt in ("quizlet", "all"):
        path = f"{prefix}_quizlet.csv"
        n = write_quizlet_csv(all_cards, path)
        print(f"Quizlet CSV: {path}  ({n} cards)", file=sys.stderr)
        written.append(path)

    if fmt in ("markdown", "all"):
        path = f"{prefix}_flashcards.md"
        n = write_markdown(all_cards, path, title, meta)
        print(f"Markdown:  {path}  ({n} cards)", file=sys.stderr)
        written.append(path)

    print(f"\nImport instructions:")
    print(f"  Anki:    File → Import → select .tsv | Note type: Basic | Separator: Tab")
    print(f"  Quizlet: Create Set → Import → select .csv | Between Term and Def: Comma")

    # Print written paths to stdout for pipeline use
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
