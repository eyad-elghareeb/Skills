#!/usr/bin/env python3
"""
Med PDF Digest — Orchestration Helper Script

Handles all file I/O, JSON merging, and output generation.
Does NOT perform LLM extraction — use extract_content.py for that.

Usage:
    python3 generate_digest.py <command> [options]

Commands:
    merge         Merge multiple partial extraction JSONs into one
    survey        Quick survey of extracted JSON content
    validate      Validate extraction JSON against schema
    stats         Print statistics about the extracted content
    build-html    Build a self-contained HTML file from extraction JSON + images
    build-md      Build a Markdown file (Obsidian/Roam/Notion compatible)
    build-pdf     Build a print-ready PDF via ReportLab
    flashcards    Export Anki TSV + Quizlet CSV + Markdown flashcards
    search        Search content across all pillars by keyword
"""

import json
import sys
import os
import base64
import html as html_module
from pathlib import Path
from datetime import datetime
from typing import Any, Optional


# ---------------------------------------------------------------------------
# JSON I/O
# ---------------------------------------------------------------------------

def load_json(path: str) -> dict:
    """Load and parse a JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: dict, path: str) -> None:
    """Save data as formatted JSON."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------

def merge_extractions(files: list[str]) -> dict:
    """Merge multiple partial extraction JSONs into a single unified extraction."""
    merged = {
        "metadata": {
            "title": "",
            "specialty": "",
            "topics": [],
            "document_type": "",
            "extraction_date": datetime.now().isoformat(),
            "word_count_estimate": 0
        },
        "clinical_approaches": [],
        "knowledge_hierarchy": {"topic": "", "subtopics": []},
        "clinical_pearls": [],
        "mcq_traps": [],
        "atomic_facts": [],
        "simplified_sections": []
    }

    seen_approaches = set()
    seen_pearls = set()
    seen_traps = set()
    atom_offset = 0

    for filepath in files:
        data = load_json(filepath)

        # Merge metadata
        if not merged["metadata"]["title"]:
            merged["metadata"]["title"] = data.get("metadata", {}).get("title", "")
        if not merged["metadata"]["specialty"]:
            merged["metadata"]["specialty"] = data.get("metadata", {}).get("specialty", "")

        for topic in data.get("metadata", {}).get("topics", []):
            if topic not in merged["metadata"]["topics"]:
                merged["metadata"]["topics"].append(topic)

        doc_type = data.get("metadata", {}).get("document_type", "")
        if doc_type and not merged["metadata"]["document_type"]:
            merged["metadata"]["document_type"] = doc_type

        wc = data.get("metadata", {}).get("word_count_estimate", 0)
        merged["metadata"]["word_count_estimate"] = max(
            merged["metadata"]["word_count_estimate"], wc
        )

        # Merge clinical approaches (deduplicate by name)
        for approach in data.get("clinical_approaches", []):
            name = approach.get("name", "")
            if name not in seen_approaches:
                seen_approaches.add(name)
                merged["clinical_approaches"].append(approach)

        # Merge knowledge hierarchy
        kh = data.get("knowledge_hierarchy", {})
        if kh:
            if not merged["knowledge_hierarchy"]["topic"]:
                merged["knowledge_hierarchy"]["topic"] = kh.get("topic", "")
            for subtopic in kh.get("subtopics", []):
                merged["knowledge_hierarchy"]["subtopics"].append(subtopic)

        # Merge clinical pearls (deduplicate by pearl text)
        for pearl in data.get("clinical_pearls", []):
            pearl_text = pearl.get("pearl", "")
            if pearl_text not in seen_pearls:
                seen_pearls.add(pearl_text)
                merged["clinical_pearls"].append(pearl)

        # Merge MCQ traps (deduplicate by scenario)
        for trap in data.get("mcq_traps", []):
            scenario = trap.get("scenario", "")
            if scenario not in seen_traps:
                seen_traps.add(scenario)
                merged["mcq_traps"].append(trap)

        # Merge atomic facts (re-number and update connections)
        new_atoms = []
        for atom in data.get("atomic_facts", []):
            old_connections = atom.get("connections", [])
            new_connections = [c + atom_offset for c in old_connections if isinstance(c, int)]
            atom["connections"] = new_connections
            new_atoms.append(atom)

        merged["atomic_facts"].extend(new_atoms)
        atom_offset += len(new_atoms)

        # Merge simplified sections
        merged["simplified_sections"].extend(data.get("simplified_sections", []))

    return merged


# ---------------------------------------------------------------------------
# Survey
# ---------------------------------------------------------------------------

def survey_extraction(data: dict) -> str:
    """Generate a brief survey of the extracted content."""
    lines = []
    lines.append("=" * 60)
    lines.append("CLINICAL DIGEST CONTENT SURVEY")
    lines.append("=" * 60)

    meta = data.get("metadata", {})
    lines.append(f"\nTitle: {meta.get('title', 'N/A')}")
    lines.append(f"Specialty: {meta.get('specialty', 'N/A')}")
    lines.append(f"Type: {meta.get('document_type', 'N/A')}")
    lines.append(f"Topics: {', '.join(meta.get('topics', []))}")
    lines.append(f"Estimated Word Count: {meta.get('word_count_estimate', 'N/A')}")

    approaches = data.get("clinical_approaches", [])
    lines.append(f"\n--- Clinical Approaches: {len(approaches)} ---")
    for a in approaches:
        steps = len(a.get("steps", []))
        branches = len(a.get("branch_points", []))
        lines.append(f"  * {a.get('name', 'Unnamed')} ({steps} steps, {branches} branches)")

    kh = data.get("knowledge_hierarchy", {})
    subtopics = kh.get("subtopics", [])
    lines.append(f"\n--- Knowledge Hierarchy: {len(subtopics)} top-level branches ---")
    for st in subtopics:
        children = len(st.get("children", []))
        lines.append(f"  * {st.get('name', 'Unnamed')} ({children} children)")

    pearls = data.get("clinical_pearls", [])
    lines.append(f"\n--- Clinical Pearls: {len(pearls)} ---")
    high_yield = sum(1 for p in pearls if p.get("exam_relevance") == "high")
    lines.append(f"  High-yield: {high_yield}, Medium: {len(pearls) - high_yield}")

    traps = data.get("mcq_traps", [])
    lines.append(f"\n--- MCQ Traps: {len(traps)} ---")
    trap_cats = {}
    for t in traps:
        cat = t.get("trap_category", "unknown")
        trap_cats[cat] = trap_cats.get(cat, 0) + 1
    for cat, count in sorted(trap_cats.items(), key=lambda x: -x[1]):
        lines.append(f"  * {cat}: {count}")

    atoms = data.get("atomic_facts", [])
    lines.append(f"\n--- Atomic Facts: {len(atoms)} ---")
    atom_cats = {}
    for a in atoms:
        cat = a.get("category", "unknown")
        atom_cats[cat] = atom_cats.get(cat, 0) + 1
    for cat, count in sorted(atom_cats.items(), key=lambda x: -x[1]):
        lines.append(f"  * {cat}: {count}")

    sections = data.get("simplified_sections", [])
    lines.append(f"\n--- Simplified Sections: {len(sections)} ---")

    lines.append("\n" + "=" * 60)
    digest_size = "Small" if len(atoms) < 40 else "Medium" if len(atoms) < 70 else "Large"
    lines.append(f"Estimated Digest Size: {digest_size}")
    lines.append("=" * 60)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------

def validate_extraction(data: dict) -> list[str]:
    """Validate extraction JSON against expected schema. Returns list of issues."""
    issues = []

    # Check top-level keys
    required_keys = ["metadata", "clinical_approaches", "knowledge_hierarchy",
                     "clinical_pearls", "mcq_traps", "atomic_facts", "simplified_sections"]
    for key in required_keys:
        if key not in data:
            issues.append(f"Missing top-level key: {key}")

    # Check metadata
    meta = data.get("metadata", {})
    if not meta.get("title"):
        issues.append("Metadata: title is empty")
    if not meta.get("specialty"):
        issues.append("Metadata: specialty is empty")

    # Check clinical approaches
    for i, approach in enumerate(data.get("clinical_approaches", [])):
        if not approach.get("name"):
            issues.append(f"Clinical approach #{i+1}: missing name")
        if not approach.get("steps"):
            issues.append(f"Clinical approach #{i+1} ({approach.get('name', 'unnamed')}): no steps defined")

    # Check knowledge hierarchy
    kh = data.get("knowledge_hierarchy", {})
    if not kh.get("topic"):
        issues.append("Knowledge hierarchy: central topic is empty")
    if not kh.get("subtopics"):
        issues.append("Knowledge hierarchy: no subtopics defined")

    # Check pearls
    for i, pearl in enumerate(data.get("clinical_pearls", [])):
        if not pearl.get("pearl"):
            issues.append(f"Clinical pearl #{i+1}: empty pearl text")
        if not pearl.get("context"):
            issues.append(f"Clinical pearl #{i+1}: missing context")

    # Check traps
    for i, trap in enumerate(data.get("mcq_traps", [])):
        if not trap.get("scenario"):
            issues.append(f"MCQ trap #{i+1}: missing scenario")
        if not trap.get("correct_answer"):
            issues.append(f"MCQ trap #{i+1}: missing correct answer")

    # Check atomic facts
    total_atoms = len(data.get("atomic_facts", []))
    for i, atom in enumerate(data.get("atomic_facts", [])):
        if not atom.get("fact"):
            issues.append(f"Atomic fact #{i+1}: empty fact text")
        for conn in atom.get("connections", []):
            if isinstance(conn, int) and (conn < 0 or conn >= total_atoms):
                issues.append(f"Atomic fact #{i+1}: invalid connection reference {conn} (total atoms: {total_atoms})")

    # Check simplified sections
    for i, section in enumerate(data.get("simplified_sections", [])):
        if not section.get("original_heading"):
            issues.append(f"Simplified section #{i+1}: missing original heading")
        if not section.get("simplified_text"):
            issues.append(f"Simplified section #{i+1}: empty simplified text")

    return issues


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def print_stats(data: dict) -> str:
    """Print detailed statistics about the extraction."""
    lines = []

    atoms = data.get("atomic_facts", [])
    pearls = data.get("clinical_pearls", [])
    traps = data.get("mcq_traps", [])
    approaches = data.get("clinical_approaches", [])
    sections = data.get("simplified_sections", [])

    lines.append("CLINICAL DIGEST STATISTICS")
    lines.append("-" * 40)
    lines.append(f"Clinical Approaches: {len(approaches)}")
    total_steps = sum(len(a.get('steps', [])) for a in approaches)
    total_branches = sum(len(a.get('branch_points', [])) for a in approaches)
    lines.append(f"  Total Steps: {total_steps}")
    lines.append(f"  Total Branch Points: {total_branches}")

    kh = data.get("knowledge_hierarchy", {})
    lines.append(f"Mind Map Branches: {len(kh.get('subtopics', []))}")

    lines.append(f"Clinical Pearls: {len(pearls)}")
    lines.append(f"  High-yield: {sum(1 for p in pearls if p.get('exam_relevance') == 'high')}")

    lines.append(f"MCQ Traps: {len(traps)}")

    lines.append(f"Atomic Facts: {len(atoms)}")
    lines.append(f"  High-yield: {sum(1 for a in atoms if a.get('high_yield'))}")

    # Check connectivity
    connected = sum(1 for a in atoms if a.get('connections'))
    lines.append(f"  Connected atoms: {connected}/{len(atoms)} ({100*connected//max(len(atoms),1)}%)")

    lines.append(f"Simplified Sections: {len(sections)}")

    # Coverage estimate
    coverage_score = 0
    if approaches: coverage_score += 1
    if kh.get('subtopics'): coverage_score += 1
    if pearls: coverage_score += 1
    if traps: coverage_score += 1
    if atoms: coverage_score += 1
    if sections: coverage_score += 1
    lines.append(f"\nPillar Coverage: {coverage_score}/6 ({'Complete' if coverage_score == 6 else 'Partial'})")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# HTML Builder
# ---------------------------------------------------------------------------

# Section color mapping
SECTION_COLORS = {
    "flowcharts": "#3498db",
    "mindmaps": "#9b59b6",
    "pearls": "#e67e22",
    "traps": "#e74c3c",
    "atoms": "#2ecc71",
    "simplified": "#1abc9c",
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Clinical Digest</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
      max-width: 900px; margin: 0 auto; padding: 20px;
      line-height: 1.6; color: #1a1a2e; background: #fafafa;
    }}

    /* Cover header */
    .cover {{
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
      color: #fff; text-align: center; padding: 60px 20px;
      border-radius: 8px; margin-bottom: 30px;
    }}
    .cover h1 {{ font-size: 2rem; margin-bottom: 8px; }}
    .cover .subtitle {{ font-size: 1rem; opacity: 0.85; margin-bottom: 4px; }}
    .cover .meta {{ font-size: 0.85rem; opacity: 0.7; }}

    /* TOC */
    .toc {{
      background: #fff; border: 1px solid #e0e0e0; border-radius: 8px;
      padding: 20px 24px; margin-bottom: 30px;
    }}
    .toc h2 {{ font-size: 1.2rem; margin-bottom: 12px; }}
    .toc ol {{ padding-left: 20px; }}
    .toc li {{ margin-bottom: 6px; }}
    .toc a {{ color: #1a1a2e; text-decoration: none; }}
    .toc a:hover {{ text-decoration: underline; }}

    /* Sections */
    .section {{
      margin-top: 3rem; background: #fff;
      border: 1px solid #e0e0e0; border-radius: 8px;
      padding: 24px; overflow: hidden;
    }}
    .section-header {{
      font-size: 1.6rem; font-weight: 700;
      border-left: 5px solid; padding-left: 14px;
      margin-bottom: 20px;
    }}
    .section-header.blue {{ border-color: {colors[flowcharts]}; }}
    .section-header.purple {{ border-color: {colors[mindmaps]}; }}
    .section-header.orange {{ border-color: {colors[pearls]}; }}
    .section-header.red {{ border-color: {colors[traps]}; }}
    .section-header.green {{ border-color: {colors[atoms]}; }}
    .section-header.teal {{ border-color: {colors[simplified]}; }}

    details > summary {{
      cursor: pointer; list-style: none; display: flex;
      align-items: center; gap: 8px;
    }}
    details > summary::before {{
      content: '\\25B6'; font-size: 0.7rem; transition: transform 0.2s;
    }}
    details[open] > summary::before {{ transform: rotate(90deg); }}

    /* Images */
    .digest-image {{
      max-width: 100%; border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      display: block; margin: 16px auto;
    }}
    .caption {{
      text-align: center; font-size: 0.85rem; color: #666;
      margin-top: 8px; margin-bottom: 20px;
    }}

    /* Pearl cards */
    .pearl-card {{
      border-left: 4px solid {colors[pearls]};
      background: #fef9f3; padding: 16px;
      border-radius: 4px; margin: 12px 0;
      transition: transform 0.15s, box-shadow 0.15s;
    }}
    .pearl-card:hover {{
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}
    .pearl-card .pearl-title {{
      font-weight: 700; font-size: 1.05rem; margin-bottom: 6px;
    }}
    .pearl-card .pearl-label {{
      display: inline-block; font-size: 0.75rem;
      padding: 2px 8px; border-radius: 10px;
      background: {colors[pearls]}; color: #fff;
      margin-right: 6px; margin-bottom: 4px;
    }}
    .pearl-card .pearl-meta {{ font-size: 0.9rem; color: #444; }}

    /* Trap cards */
    .trap-card {{
      border-left: 4px solid {colors[traps]};
      background: #fef2f2; padding: 16px;
      border-radius: 4px; margin: 12px 0;
      transition: transform 0.15s, box-shadow 0.15s;
    }}
    .trap-card:hover {{
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}
    .trap-card .trap-title {{ font-weight: 700; font-size: 1.05rem; margin-bottom: 6px; }}
    .trap-card .trap-label {{
      display: inline-block; font-size: 0.75rem;
      padding: 2px 8px; border-radius: 10px;
      background: {colors[traps]}; color: #fff;
      margin-right: 6px; margin-bottom: 4px;
    }}
    .trap-card .trap-meta {{ font-size: 0.9rem; color: #444; }}

    /* Atom entries */
    .atom-card {{
      background: #f8f9fa; padding: 10px 14px;
      border-radius: 4px; margin: 8px 0;
      border: 1px solid #e9ecef;
    }}
    .atom-card .atom-badge {{
      display: inline-block; font-size: 0.7rem;
      padding: 2px 8px; border-radius: 10px;
      margin-right: 6px; color: #fff;
    }}
    .atom-card .atom-badge.diagnosis {{ background: #3498db; }}
    .atom-card .atom-badge.treatment {{ background: #2ecc71; }}
    .atom-card .atom-badge.pharmacology {{ background: #9b59b6; }}
    .atom-card .atom-badge.pathophysiology {{ background: #e74c3c; }}
    .atom-card .atom-badge.epidemiology {{ background: #f39c12; }}
    .atom-card .atom-badge.classification {{ background: #1abc9c; }}
    .atom-card .atom-badge.monitoring {{ background: #e67e22; }}
    .atom-card .atom-badge.prognosis {{ background: #95a5a6; }}
    .atom-card .atom-fact {{ font-size: 0.95rem; }}
    .atom-card .atom-connections {{ font-size: 0.8rem; color: #888; margin-top: 4px; }}
    .atom-card .atom-connections a {{ color: #3498db; text-decoration: none; }}

    /* Simplified section */
    .simplified-block {{
      margin: 16px 0; padding: 16px;
      background: #f0faf7; border-radius: 4px;
      border: 1px solid #d5f5e3;
    }}
    .simplified-block h4 {{ color: {colors[simplified]}; margin-bottom: 8px; }}

    /* Back to top */
    .back-to-top {{
      position: fixed; bottom: 30px; right: 30px;
      width: 44px; height: 44px; border-radius: 50%;
      background: #1a1a2e; color: #fff;
      text-align: center; line-height: 44px;
      text-decoration: none; font-size: 1.2rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
      display: none; z-index: 100;
    }}

    /* Print */
    @media print {{
      .toc {{ display: none; }}
      .back-to-top {{ display: none !important; }}
      .section {{ box-shadow: none; border: 1px solid #ccc; }}
      .digest-image {{ box-shadow: none; }}
    }}

    /* Mobile */
    @media (max-width: 768px) {{
      body {{ padding: 10px; }}
      .cover {{ padding: 30px 15px; }}
      .cover h1 {{ font-size: 1.4rem; }}
      .section {{ padding: 14px; }}
      .section-header {{ font-size: 1.3rem; }}
    }}
  </style>
</head>
<body>

  <!-- Cover -->
  <header class="cover">
    <h1>{title} — Clinical Digest</h1>
    <div class="subtitle">Flowcharts | Mind Maps | Pearls | MCQ Traps | Atoms | Simplified</div>
    <div class="meta">Source: {source} | Generated: {date}</div>
  </header>

  <!-- TOC -->
  <nav class="toc">
    <h2>Table of Contents</h2>
    <ol>
      <li><a href="#flowcharts">Clinical Approach Flowcharts</a></li>
      <li><a href="#mindmaps">Mind Maps</a></li>
      <li><a href="#pearls">Clinical Pearls</a></li>
      <li><a href="#traps">MCQ Traps</a></li>
      <li><a href="#atoms">Atomic Summaries</a></li>
      <li><a href="#simplified">Simplified Yet Complete</a></li>
    </ol>
  </nav>

  <main>
    {sections}
  </main>

  <!-- Back to top -->
  <a href="#" class="back-to-top" id="backToTop" title="Back to Top">&#8679;</a>

  <script>
    window.addEventListener('scroll', function() {{
      var btn = document.getElementById('backToTop');
      btn.style.display = window.scrollY > 300 ? 'block' : 'none';
    }});
  </script>

</body>
</html>"""


def image_to_data_uri(image_path: str) -> Optional[str]:
    """Convert an image file to a base64 data URI."""
    if not os.path.exists(image_path):
        return None
    with open(image_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
    ext = os.path.splitext(image_path)[1].lower()
    mime = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
            '.gif': 'image/gif', '.svg': 'image/svg+xml', '.webp': 'image/webp'}
    mime_type = mime.get(ext, 'image/png')
    return f'data:{mime_type};base64,{b64}'


def build_flowcharts_html(data: dict, image_dir: str) -> str:
    """Build HTML for the Flowcharts section."""
    approaches = data.get("clinical_approaches", [])
    if not approaches:
        return ""

    parts = []
    parts.append(f'''<section id="flowcharts" class="section">
      <details open>
        <summary><h2 class="section-header blue">1. Clinical Approach Flowcharts</h2></summary>''')

    for i, approach in enumerate(approaches, 1):
        name = html_module.escape(approach.get("name", f"Flowchart {i}"))
        trigger = html_module.escape(approach.get("trigger", ""))

        # Try to find a matching image file
        image_html = ""
        safe_name = approach.get("name", "").lower().replace(" ", "_").replace("/", "_")
        for ext in [".png", ".jpg", ".svg"]:
            img_path = os.path.join(image_dir, f"flowchart_{safe_name}{ext}")
            data_uri = image_to_data_uri(img_path)
            if data_uri:
                image_html = f'<img class="digest-image" src="{data_uri}" alt="{name}" />'
                break

        parts.append(f'''
        <div style="margin: 20px 0;">
          <h3>1.{i} {name}</h3>
          {f'<p><strong>Trigger:</strong> {trigger}</p>' if trigger else ''}
          {image_html}
          {f'<p class="caption">{name}</p>' if image_html else '<p><em>Flowchart image not found — render from Mermaid source.</em></p>'}
        </div>''')

    parts.append("      </details>\n    </section>")
    return "\n".join(parts)


def build_mindmaps_html(data: dict, image_dir: str) -> str:
    """Build HTML for the Mind Maps section."""
    kh = data.get("knowledge_hierarchy", {})
    subtopics = kh.get("subtopics", [])
    if not subtopics:
        return ""

    topic = html_module.escape(kh.get("topic", "Topic"))

    parts = []
    parts.append(f'''<section id="mindmaps" class="section">
      <details open>
        <summary><h2 class="section-header purple">2. Mind Maps</h2></summary>''')

    # Main mind map image
    safe_topic = topic.lower().replace(" ", "_").replace("/", "_")
    image_html = ""
    for ext in [".png", ".jpg", ".svg"]:
        img_path = os.path.join(image_dir, f"mindmap_{safe_topic}{ext}")
        data_uri = image_to_data_uri(img_path)
        if data_uri:
            image_html = f'<img class="digest-image" src="{data_uri}" alt="{topic} Mind Map" />'
            break

    parts.append(f'''
        <div style="margin: 20px 0;">
          <h3>2.1 {topic} — Main Mind Map</h3>
          {image_html}
          {f'<p class="caption">{topic} Mind Map</p>' if image_html else '<p><em>Mind map image not found — render from hierarchy data.</em></p>'}
        </div>''')

    # Sub-maps
    for i, sub in enumerate(subtopics, 2):
        sub_name = html_module.escape(sub.get("name", f"Sub-topic {i}"))
        safe_sub = sub.get("name", "").lower().replace(" ", "_").replace("/", "_")
        sub_image_html = ""
        for ext in [".png", ".jpg", ".svg"]:
            img_path = os.path.join(image_dir, f"mindmap_{safe_topic}_{safe_sub}{ext}")
            data_uri = image_to_data_uri(img_path)
            if data_uri:
                sub_image_html = f'<img class="digest-image" src="{data_uri}" alt="{sub_name}" />'
                break

        if sub_image_html:
            parts.append(f'''
        <div style="margin: 20px 0;">
          <h3>2.{i-1} {sub_name}</h3>
          {sub_image_html}
          <p class="caption">{sub_name} Sub-Map</p>
        </div>''')

    parts.append("      </details>\n    </section>")
    return "\n".join(parts)


def build_pearls_html(data: dict) -> str:
    """Build HTML for the Clinical Pearls section."""
    pearls = data.get("clinical_pearls", [])
    if not pearls:
        return ""

    parts = []
    parts.append(f'''<section id="pearls" class="section">
      <details open>
        <summary><h2 class="section-header orange">3. Clinical Pearls</h2></summary>''')

    for i, pearl in enumerate(pearls, 1):
        pearl_text = html_module.escape(pearl.get("pearl", ""))
        context = html_module.escape(pearl.get("context", ""))
        buzzword = html_module.escape(pearl.get("buzzword", ""))
        associations = html_module.escape(", ".join(pearl.get("associations", [])))
        exam_rel = pearl.get("exam_relevance", "medium")
        why_tested = html_module.escape(pearl.get("why_tested", ""))

        buzzword_html = f'<span class="pearl-label">Buzzword: {buzzword}</span>' if buzzword else ""
        exam_label = f'<span class="pearl-label">{exam_rel.upper()}</span>'

        parts.append(f'''
        <div class="pearl-card">
          <div class="pearl-title">PEARL #{i}</div>
          {exam_label}{buzzword_html}
          <p class="pearl-meta"><strong>Pearl:</strong> {pearl_text}</p>
          {f'<p class="pearl-meta"><strong>Context:</strong> {context}</p>' if context else ''}
          {f'<p class="pearl-meta"><strong>Associations:</strong> {associations}</p>' if associations else ''}
          {f'<p class="pearl-meta"><strong>Why tested:</strong> {why_tested}</p>' if why_tested else ''}
        </div>''')

    parts.append("      </details>\n    </section>")
    return "\n".join(parts)


def build_traps_html(data: dict) -> str:
    """Build HTML for the MCQ Traps section."""
    traps = data.get("mcq_traps", [])
    if not traps:
        return ""

    parts = []
    parts.append(f'''<section id="traps" class="section">
      <details open>
        <summary><h2 class="section-header red">4. MCQ Traps</h2></summary>''')

    for i, trap in enumerate(traps, 1):
        category = html_module.escape(trap.get("trap_category", "unknown"))
        scenario = html_module.escape(trap.get("scenario", ""))
        distractor = html_module.escape(trap.get("distractor", ""))
        correct = html_module.escape(trap.get("correct_answer", ""))
        why_tricky = html_module.escape(trap.get("why_tricky", ""))
        avoidance = html_module.escape(trap.get("avoidance_strategy", ""))

        parts.append(f'''
        <div class="trap-card">
          <div class="trap-title">TRAP #{i}</div>
          <span class="trap-label">{category}</span>
          <p class="trap-meta"><strong>Scenario:</strong> {scenario}</p>
          <p class="trap-meta"><strong>The Trap:</strong> {distractor}</p>
          <p class="trap-meta"><strong>Correct Answer:</strong> {correct}</p>
          {f'<p class="trap-meta"><strong>Why tricky:</strong> {why_tricky}</p>' if why_tricky else ''}
          {f'<p class="trap-meta"><strong>How to avoid:</strong> {avoidance}</p>' if avoidance else ''}
        </div>''')

    parts.append("      </details>\n    </section>")
    return "\n".join(parts)


def build_atoms_html(data: dict) -> str:
    """Build HTML for the Atomic Summaries section."""
    atoms = data.get("atomic_facts", [])
    if not atoms:
        return ""

    parts = []
    parts.append(f'''<section id="atoms" class="section">
      <details open>
        <summary><h2 class="section-header green">5. Atomic Summaries</h2></summary>''')

    for i, atom in enumerate(atoms, 1):
        fact = html_module.escape(atom.get("fact", ""))
        category = html_module.escape(atom.get("category", "unknown"))
        high_yield = atom.get("high_yield", False)
        connections = atom.get("connections", [])
        source = html_module.escape(atom.get("source_section", ""))

        badge_class = category.lower().replace(" ", "-")
        yield_marker = ' <strong style="color:#e74c3c;">[HIGH YIELD]</strong>' if high_yield else ""

        conn_links = []
        for c in connections:
            if isinstance(c, int) and 0 <= c < len(atoms):
                conn_links.append(f'<a href="#atom-{c+1}">Atom #{c+1}</a>')
        conn_html = " | ".join(conn_links)

        parts.append(f'''
        <div class="atom-card" id="atom-{i}">
          <span class="atom-badge {badge_class}">{category}</span>
          {yield_marker}
          <div class="atom-fact">{fact}</div>
          {f'<div class="atom-connections">Links: {conn_html}</div>' if conn_html else ''}
          {f'<div class="atom-connections">Source: {source}</div>' if source else ''}
        </div>''')

    parts.append("      </details>\n    </section>")
    return "\n".join(parts)


def build_simplified_html(data: dict) -> str:
    """Build HTML for the Simplified Yet Complete section."""
    sections = data.get("simplified_sections", [])
    if not sections:
        return ""

    parts = []
    parts.append(f'''<section id="simplified" class="section">
      <details open>
        <summary><h2 class="section-header teal">6. Simplified Yet Complete</h2></summary>''')

    for section in sections:
        heading = html_module.escape(section.get("original_heading", ""))
        text = html_module.escape(section.get("simplified_text", ""))

        parts.append(f'''
        <div class="simplified-block">
          <h4>{heading}</h4>
          <p>{text}</p>
        </div>''')

    parts.append("      </details>\n    </section>")
    return "\n".join(parts)


def build_html(extraction_json_path: str, image_dir: str, output_path: str) -> None:
    """Build a self-contained HTML clinical digest from an extraction JSON and image directory."""
    data = load_json(extraction_json_path)

    meta = data.get("metadata", {})
    title = meta.get("title", "Clinical Digest")
    source = meta.get("title", "Unknown Source")
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    lang = "en"

    # Build each section
    sections_html = ""
    sections_html += build_flowcharts_html(data, image_dir)
    sections_html += build_mindmaps_html(data, image_dir)
    sections_html += build_pearls_html(data)
    sections_html += build_traps_html(data)
    sections_html += build_atoms_html(data)
    sections_html += build_simplified_html(data)

    # Fill template
    html_content = HTML_TEMPLATE.format(
        lang=lang,
        title=html_module.escape(title),
        source=html_module.escape(source),
        date=date,
        sections=sections_html,
        colors={
            "flowcharts": SECTION_COLORS["flowcharts"],
            "mindmaps": SECTION_COLORS["mindmaps"],
            "pearls": SECTION_COLORS["pearls"],
            "traps": SECTION_COLORS["traps"],
            "atoms": SECTION_COLORS["atoms"],
            "simplified": SECTION_COLORS["simplified"],
        }
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML digest built: {output_path}")
    file_size_kb = os.path.getsize(output_path) / 1024
    print(f"File size: {file_size_kb:.1f} KB")


# ---------------------------------------------------------------------------
# Markdown Builder
# ---------------------------------------------------------------------------

def build_markdown(extraction_json_path: str, output_path: str) -> None:
    """Build a Markdown clinical digest (Obsidian/Roam/Notion compatible)."""
    data = load_json(extraction_json_path)
    meta = data.get("metadata", {})
    title = meta.get("title", "Clinical Digest")
    specialty = meta.get("specialty", "")
    date = datetime.now().strftime("%Y-%m-%d")

    lines = []
    lines.append(f"# {title} — Clinical Digest")
    lines.append(f"**Specialty:** {specialty} | **Generated:** {date} | **Source:** {title}")
    lines.append(f"\n**Tags:** #medicine #clinical-digest #{specialty.lower().replace(' ', '-')}")
    lines.append("\n---\n")
    lines.append("## Table of Contents")
    lines.append("1. [[#Clinical Approach Flowcharts]]")
    lines.append("2. [[#Mind Maps]]")
    lines.append("3. [[#Clinical Pearls]]")
    lines.append("4. [[#MCQ Traps]]")
    lines.append("5. [[#Atomic Summaries]]")
    lines.append("6. [[#Simplified Yet Complete]]")
    lines.append("\n---\n")

    # Section 1: Flowcharts
    approaches = data.get("clinical_approaches", [])
    lines.append("## Clinical Approach Flowcharts\n")
    for i, approach in enumerate(approaches, 1):
        name = approach.get("name", f"Flowchart {i}")
        trigger = approach.get("trigger", "")
        steps = approach.get("steps", [])
        branches = approach.get("branch_points", [])
        endpoints = approach.get("endpoints", [])

        lines.append(f"### {i}. {name}")
        if trigger:
            lines.append(f"> **Trigger:** {trigger}\n")
        if steps:
            lines.append("**Steps:**")
            for j, step in enumerate(steps, 1):
                lines.append(f"{j}. {step}")
        if branches:
            lines.append("\n**Key Decision Points:**")
            for bp in branches:
                cond = bp.get("condition", "")
                yes_p = bp.get("yes_path", "")
                no_p = bp.get("no_path", "")
                lines.append(f"- **If {cond}:** → {yes_p}")
                if no_p:
                    lines.append(f"  - **Else:** → {no_p}")
        if endpoints:
            lines.append("\n**Endpoints:** " + " | ".join(endpoints))
        lines.append("")

    lines.append("---\n")

    # Section 2: Mind Maps
    kh = data.get("knowledge_hierarchy", {})
    lines.append("## Mind Maps\n")
    lines.append(f"### {kh.get('topic', 'Topic')} — Knowledge Hierarchy\n")
    for sub in kh.get("subtopics", []):
        color = sub.get("color_hint", "")
        color_marker = {"red": "🔴", "orange": "🟠", "blue": "🔵", "green": "🟢",
                        "purple": "🟣", "gray": "⚫"}.get(color, "⚪")
        lines.append(f"- {color_marker} **{sub.get('name', '')}**")
        for child in sub.get("children", []):
            detail = child.get("detail", "")
            lines.append(f"  - {child.get('name', '')}" + (f": {detail}" if detail else ""))
    lines.append("\n---\n")

    # Section 3: Pearls
    pearls = data.get("clinical_pearls", [])
    lines.append("## Clinical Pearls\n")
    for i, pearl in enumerate(pearls, 1):
        exam_rel = pearl.get("exam_relevance", "medium").upper()
        buzzword = pearl.get("buzzword", "")
        category = pearl.get("category", "").replace("_", " ")
        hi = "⭐ " if exam_rel == "HIGH" else ""

        lines.append(f"### Pearl {i}: {hi}{pearl.get('pearl', '')[:60]}")
        lines.append(f"> **{pearl.get('pearl', '')}**")
        lines.append(f"\n- **Exam relevance:** {exam_rel} | **Category:** {category}")
        if buzzword:
            lines.append(f"- **Buzzword:** `{buzzword}`")
        if pearl.get("context"):
            lines.append(f"- **Context:** {pearl['context']}")
        assoc = pearl.get("associations", [])
        if assoc:
            lines.append(f"- **Associations:** {', '.join(assoc)}")
        if pearl.get("why_tested"):
            lines.append(f"- **Why tested:** {pearl['why_tested']}")
        lines.append("")

    lines.append("---\n")

    # Section 4: MCQ Traps
    traps = data.get("mcq_traps", [])
    lines.append("## MCQ Traps\n")
    for i, trap in enumerate(traps, 1):
        category = trap.get("trap_category", "")
        topic = trap.get("topic", "")
        lines.append(f"### Trap {i}: {category} [{topic}]")
        lines.append(f"\n**Scenario:** {trap.get('scenario', '')}")
        lines.append(f"\n> ⚠️ **The Trap:** {trap.get('distractor', '')}")
        lines.append(f"\n✅ **Correct Answer:** {trap.get('correct_answer', '')}")
        if trap.get("why_tricky"):
            lines.append(f"\n**Why tricky:** {trap['why_tricky']}")
        if trap.get("avoidance_strategy"):
            lines.append(f"\n**How to avoid:** {trap['avoidance_strategy']}")
        lines.append("")

    lines.append("---\n")

    # Section 5: Atoms
    atoms = data.get("atomic_facts", [])
    lines.append("## Atomic Summaries\n")
    category_groups: dict[str, list] = {}
    for atom in atoms:
        cat = atom.get("category", "Other")
        category_groups.setdefault(cat, []).append(atom)

    for cat, cat_atoms in sorted(category_groups.items()):
        lines.append(f"### {cat}")
        for i, atom in enumerate(cat_atoms, 1):
            hy = "⭐ " if atom.get("high_yield") else ""
            lines.append(f"- {hy}{atom.get('fact', '')}")
        lines.append("")

    lines.append("---\n")

    # Section 6: Simplified
    sections = data.get("simplified_sections", [])
    lines.append("## Simplified Yet Complete\n")
    for section in sections:
        heading = section.get("original_heading", "Section")
        text = section.get("simplified_text", "")
        preserved = section.get("key_details_preserved", [])
        lines.append(f"### {heading}")
        lines.append(f"\n{text}\n")
        if preserved:
            lines.append("**Key details preserved:**")
            for detail in preserved:
                lines.append(f"- {detail}")
        lines.append("")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    print(f"Markdown digest built: {output_path}")
    size_kb = os.path.getsize(output_path) / 1024
    print(f"File size: {size_kb:.1f} KB")


# ---------------------------------------------------------------------------
# PDF Builder (ReportLab)
# ---------------------------------------------------------------------------

def build_pdf(extraction_json_path: str, image_dir: str, output_path: str) -> None:
    """Build a print-ready PDF clinical digest via ReportLab."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,
            Table, TableStyle, PageBreak, HRFlowable
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
    except ImportError:
        print("ERROR: reportlab not installed. Run: pip install reportlab", file=sys.stderr)
        raise SystemExit(1)

    data = load_json(extraction_json_path)
    meta = data.get("metadata", {})
    title = meta.get("title", "Clinical Digest")
    date = datetime.now().strftime("%Y-%m-%d")

    SECTION_COLORS_RL = {
        "flowcharts": colors.HexColor("#3498db"),
        "mindmaps":   colors.HexColor("#9b59b6"),
        "pearls":     colors.HexColor("#e67e22"),
        "traps":      colors.HexColor("#e74c3c"),
        "atoms":      colors.HexColor("#2ecc71"),
        "simplified": colors.HexColor("#1abc9c"),
    }

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm
    )

    styles = getSampleStyleSheet()
    story = []

    # Styles
    cover_style = ParagraphStyle("Cover", parent=styles["Title"],
                                  fontSize=20, textColor=colors.white, alignment=TA_CENTER)
    h1_base = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=14, spaceAfter=8)
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12, spaceAfter=4)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=14)
    label_style = ParagraphStyle("Label", parent=styles["Normal"], fontSize=8,
                                  textColor=colors.white, alignment=TA_CENTER)
    pearl_style = ParagraphStyle("Pearl", parent=styles["Normal"], fontSize=10,
                                  leading=14, leftIndent=8, borderPadding=6)
    small_style = ParagraphStyle("Small", parent=styles["Normal"], fontSize=8,
                                  textColor=colors.HexColor("#666666"))

    def section_header(text: str, color: Any) -> list:
        h = ParagraphStyle(f"SH_{text[:8]}", parent=h1_base,
                            textColor=color, borderPadding=(0, 0, 4, 10))
        return [Paragraph(text, h), HRFlowable(color=color, thickness=2, spaceAfter=6)]

    # Cover
    story.append(Spacer(1, 30*mm))
    story.append(Paragraph(f"{title}", styles["Title"]))
    story.append(Paragraph("Clinical Digest", styles["Heading2"]))
    story.append(Paragraph("Flowcharts · Mind Maps · Pearls · MCQ Traps · Atoms · Simplified",
                            styles["Normal"]))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(f"Generated: {date}", small_style))
    story.append(PageBreak())

    # Section 1: Clinical Approaches
    story.extend(section_header("1. Clinical Approach Flowcharts", SECTION_COLORS_RL["flowcharts"]))
    for i, approach in enumerate(data.get("clinical_approaches", []), 1):
        name = approach.get("name", f"Approach {i}")
        trigger = approach.get("trigger", "")
        steps = approach.get("steps", [])

        story.append(Paragraph(f"1.{i}. {name}", h2_style))
        if trigger:
            story.append(Paragraph(f"<b>Trigger:</b> {trigger}", body_style))

        # Try to load rendered image
        safe = name.lower().replace(" ", "_").replace("/", "_")
        img_path = None
        for ext in [".png", ".jpg", ".svg"]:
            p = os.path.join(image_dir, f"flowchart_{safe}{ext}")
            if os.path.exists(p):
                img_path = p
                break

        if img_path:
            try:
                story.append(RLImage(img_path, width=160*mm, height=80*mm))
            except Exception:
                pass
        elif steps:
            # Fallback: numbered list
            for j, step in enumerate(steps, 1):
                story.append(Paragraph(f"{j}. {step}", body_style))

        story.append(Spacer(1, 4*mm))

    story.append(PageBreak())

    # Section 3: Clinical Pearls
    story.extend(section_header("3. Clinical Pearls", SECTION_COLORS_RL["pearls"]))
    for i, pearl in enumerate(data.get("clinical_pearls", []), 1):
        exam_rel = pearl.get("exam_relevance", "medium").upper()
        buzzword = pearl.get("buzzword", "")
        pearl_text = pearl.get("pearl", "")
        context = pearl.get("context", "")

        card_data = [[
            Paragraph(f"<b>PEARL #{i}</b>", label_style),
            Paragraph(f"<b>{pearl_text}</b>", pearl_style)
        ]]
        card_table = Table(card_data, colWidths=[20*mm, None])
        card_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), SECTION_COLORS_RL["pearls"]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e67e22")),
            ("ROWBACKGROUNDS", (1, 0), (-1, -1), [colors.HexColor("#fef9f3")]),
        ]))
        story.append(card_table)
        if context:
            story.append(Paragraph(f"<i>Context:</i> {context}", small_style))
        if buzzword:
            story.append(Paragraph(f"<i>Buzzword:</i> {buzzword}", small_style))
        story.append(Spacer(1, 3*mm))

    story.append(PageBreak())

    # Section 4: MCQ Traps
    story.extend(section_header("4. MCQ Traps", SECTION_COLORS_RL["traps"]))
    for i, trap in enumerate(data.get("mcq_traps", []), 1):
        category = trap.get("trap_category", "")
        scenario = trap.get("scenario", "")
        distractor = trap.get("distractor", "")
        correct = trap.get("correct_answer", "")
        why = trap.get("why_tricky", "")

        story.append(Paragraph(f"<b>TRAP #{i}:</b> {category}", h2_style))
        story.append(Paragraph(scenario, body_style))
        story.append(Paragraph(f"⚠️ <b>The Trap:</b> {distractor}", body_style))
        story.append(Paragraph(f"✅ <b>Correct:</b> {correct}", body_style))
        if why:
            story.append(Paragraph(f"<i>{why}</i>", small_style))
        story.append(Spacer(1, 3*mm))

    story.append(PageBreak())

    # Section 5: Atoms
    story.extend(section_header("5. Atomic Summaries", SECTION_COLORS_RL["atoms"]))
    atoms = data.get("atomic_facts", [])
    category_groups: dict[str, list] = {}
    for atom in atoms:
        cat = atom.get("category", "Other")
        category_groups.setdefault(cat, []).append(atom)

    for cat, cat_atoms in sorted(category_groups.items()):
        story.append(Paragraph(cat, h2_style))
        for atom in cat_atoms:
            hy = "⭐ " if atom.get("high_yield") else "• "
            story.append(Paragraph(f"{hy}{atom.get('fact', '')}", body_style))
        story.append(Spacer(1, 2*mm))

    story.append(PageBreak())

    # Section 6: Simplified
    story.extend(section_header("6. Simplified Yet Complete", SECTION_COLORS_RL["simplified"]))
    for section in data.get("simplified_sections", []):
        heading = section.get("original_heading", "")
        text = section.get("simplified_text", "")
        story.append(Paragraph(heading, h2_style))
        story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 3*mm))

    # Build
    doc.build(story)
    print(f"PDF digest built: {output_path}")
    size_kb = os.path.getsize(output_path) / 1024
    print(f"File size: {size_kb:.1f} KB")


# ---------------------------------------------------------------------------
# Flashcard Exporter (inline — delegates to make_flashcards.py if available)
# ---------------------------------------------------------------------------

def export_flashcards(extraction_json_path: str, output_prefix: str,
                      include: str = "pearls,traps") -> None:
    """
    Export flashcards from an extraction JSON.
    Calls make_flashcards.py if it is present in the same scripts/ directory,
    otherwise runs a minimal inline version.
    """
    import csv

    data = load_json(extraction_json_path)
    meta = data.get("metadata", {})
    title = meta.get("title", "Clinical Digest")

    # Attempt to delegate to make_flashcards.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fc_script = os.path.join(script_dir, "make_flashcards.py")

    if os.path.exists(fc_script):
        import subprocess
        result = subprocess.run(
            ["python3", fc_script, extraction_json_path,
             "--format", "all", "--output", output_prefix, "--include", include],
            capture_output=False
        )
        return

    # Inline fallback: simple TSV export
    cards: list[tuple[str, str]] = []

    include_list = [x.strip() for x in include.split(",")]

    if "pearls" in include_list or "all" in include_list:
        for pearl in data.get("clinical_pearls", []):
            buzzword = pearl.get("buzzword", "")
            front = f"Clinical Pearl: {buzzword or pearl.get('context', pearl.get('pearl', '')[:60])}"
            back = pearl.get("pearl", "")
            cards.append((front, back))

    if "traps" in include_list or "all" in include_list:
        for trap in data.get("mcq_traps", []):
            front = f"MCQ Trap [{trap.get('trap_category', '')}]: {trap.get('scenario', '')}"
            back = f"Correct: {trap.get('correct_answer', '')}. Why tricky: {trap.get('why_tricky', '')}"
            cards.append((front, back))

    if "atoms" in include_list or "all" in include_list:
        for atom in data.get("atomic_facts", []):
            fact = atom.get("fact", "")
            cat = atom.get("category", "")
            cards.append((f"[{cat}] Recall this clinical fact:", fact))

    tsv_path = f"{output_prefix}_anki.tsv"
    with open(tsv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        for front, back in cards:
            writer.writerow([front, back])
    print(f"Flashcards (Anki TSV): {tsv_path}  ({len(cards)} cards)")


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search_content(data: dict, keyword: str) -> str:
    """Search all pillars for a keyword. Returns a formatted results string."""
    kw = keyword.lower()
    lines = [f"Search results for: '{keyword}'", "=" * 50]

    # Pearls
    pearl_hits = [p for p in data.get("clinical_pearls", [])
                  if kw in p.get("pearl", "").lower()
                  or kw in p.get("buzzword", "").lower()
                  or kw in p.get("context", "").lower()]
    if pearl_hits:
        lines.append(f"\nPEARLS ({len(pearl_hits)} matches):")
        for p in pearl_hits:
            lines.append(f"  • {p.get('pearl', '')}")

    # Traps
    trap_hits = [t for t in data.get("mcq_traps", [])
                 if kw in t.get("scenario", "").lower()
                 or kw in t.get("correct_answer", "").lower()
                 or kw in t.get("topic", "").lower()]
    if trap_hits:
        lines.append(f"\nTRAPS ({len(trap_hits)} matches):")
        for t in trap_hits:
            lines.append(f"  • [{t.get('trap_category', '')}] {t.get('scenario', '')[:80]}")

    # Atoms
    atom_hits = [a for a in data.get("atomic_facts", [])
                 if kw in a.get("fact", "").lower()
                 or kw in a.get("source_section", "").lower()]
    if atom_hits:
        lines.append(f"\nATOMS ({len(atom_hits)} matches):")
        for a in atom_hits:
            hy = " [HY]" if a.get("high_yield") else ""
            lines.append(f"  • [{a.get('category', '')}]{hy} {a.get('fact', '')[:100]}")

    # Approaches
    approach_hits = [ap for ap in data.get("clinical_approaches", [])
                     if kw in ap.get("name", "").lower()
                     or kw in ap.get("trigger", "").lower()
                     or any(kw in s.lower() for s in ap.get("steps", []))]
    if approach_hits:
        lines.append(f"\nFLOWCHARTS ({len(approach_hits)} matches):")
        for ap in approach_hits:
            lines.append(f"  • {ap.get('name', '')} (trigger: {ap.get('trigger', '')[:60]})")

    total = len(pearl_hits) + len(trap_hits) + len(atom_hits) + len(approach_hits)
    lines.append(f"\nTotal: {total} matches across all pillars")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "merge":
        if len(sys.argv) < 4:
            print("Usage: generate_digest.py merge <output.json> <input1.json> [input2.json ...]")
            sys.exit(1)
        output_path = sys.argv[2]
        input_files = sys.argv[3:]
        merged = merge_extractions(input_files)
        save_json(merged, output_path)
        print(f"Merged {len(input_files)} extractions -> {output_path}")
        print(survey_extraction(merged))

    elif command == "survey":
        if len(sys.argv) < 3:
            print("Usage: generate_digest.py survey <extraction.json>")
            sys.exit(1)
        data = load_json(sys.argv[2])
        print(survey_extraction(data))

    elif command == "validate":
        if len(sys.argv) < 3:
            print("Usage: generate_digest.py validate <extraction.json>")
            sys.exit(1)
        data = load_json(sys.argv[2])
        issues = validate_extraction(data)
        if issues:
            print(f"Found {len(issues)} issues:")
            for issue in issues:
                print(f"  WARNING: {issue}")
        else:
            print("PASS: Extraction JSON is valid -- all required fields present and populated.")

    elif command == "stats":
        if len(sys.argv) < 3:
            print("Usage: generate_digest.py stats <extraction.json>")
            sys.exit(1)
        data = load_json(sys.argv[2])
        print(print_stats(data))

    elif command == "build-html":
        if len(sys.argv) < 4:
            print("Usage: generate_digest.py build-html <extraction.json> <image_dir> [output.html]")
            sys.exit(1)
        extraction_path = sys.argv[2]
        image_dir = sys.argv[3]
        output_path = sys.argv[4] if len(sys.argv) >= 5 else "clinical_digest.html"
        build_html(extraction_path, image_dir, output_path)

    elif command == "build-md":
        if len(sys.argv) < 3:
            print("Usage: generate_digest.py build-md <extraction.json> [output.md]")
            sys.exit(1)
        extraction_path = sys.argv[2]
        output_path = sys.argv[3] if len(sys.argv) >= 4 else "clinical_digest.md"
        build_markdown(extraction_path, output_path)

    elif command == "build-pdf":
        if len(sys.argv) < 4:
            print("Usage: generate_digest.py build-pdf <extraction.json> <image_dir> [output.pdf]")
            print("  Requires: pip install reportlab")
            sys.exit(1)
        extraction_path = sys.argv[2]
        image_dir = sys.argv[3]
        output_path = sys.argv[4] if len(sys.argv) >= 5 else "clinical_digest.pdf"
        build_pdf(extraction_path, image_dir, output_path)

    elif command in ("flashcards", "export-anki"):
        if len(sys.argv) < 3:
            print("Usage: generate_digest.py flashcards <extraction.json> [output_prefix] [--include pearls,traps,atoms]")
            sys.exit(1)
        extraction_path = sys.argv[2]
        output_prefix = sys.argv[3] if len(sys.argv) >= 4 else os.path.splitext(extraction_path)[0]
        include = "pearls,traps"
        if "--include" in sys.argv:
            idx = sys.argv.index("--include")
            if idx + 1 < len(sys.argv):
                include = sys.argv[idx + 1]
        export_flashcards(extraction_path, output_prefix, include)

    elif command == "search":
        if len(sys.argv) < 4:
            print("Usage: generate_digest.py search <extraction.json> <keyword>")
            sys.exit(1)
        data = load_json(sys.argv[2])
        keyword = " ".join(sys.argv[3:])
        print(search_content(data, keyword))

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
