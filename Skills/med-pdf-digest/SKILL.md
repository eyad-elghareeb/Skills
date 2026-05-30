---
name: med-pdf-digest
description: Comprehensive medical PDF digestion skill that transforms clinical textbooks, guidelines, and review articles into multi-format study aids. Activates whenever the user wants to break down, digest, summarize, or study from a medical/clinical PDF or document. Triggers on phrases like "digest this PDF", "break down this medical PDF", "extract clinical pearls", "make flowcharts from this", "create mind maps from my notes", "find MCQ traps", "summarize this clinically", "study guide from PDF", "medical study aids", "clinical approach flowchart", or any request involving medical/clinical document processing for study purposes. Also triggers when users mention USMLE, PLAB, board prep, clinical exams, or medical exam preparation with a document. Use this skill even if the user simply says "help me study this" while sharing a medical document.
---

# Med PDF Digest — Clinical Knowledge Decompiler

Transforms dense clinical documents into exam-ready, clinically actionable study units. Six output pillars, each targeting a distinct cognitive memory system. Every detail preserved; nothing lost in translation.

**Core philosophy: Simplify without skipping. Every detail matters, but not every detail needs the same format.**

---

## The Six Output Pillars

| # | Pillar | Purpose | Cognitive Target |
|---|--------|---------|-----------------|
| 1 | Clinical Approach Flowcharts | Step-by-step diagnostic/treatment algorithms | Procedural memory — "what do I DO?" |
| 2 | Mind Maps | Hierarchical knowledge organization | Structural memory — "how does this FIT TOGETHER?" |
| 3 | Clinical Pearls | High-yield nuggets, buzzwords, key associations | Associative memory — "what MUST I remember?" |
| 4 | MCQ Traps | Common exam distractors, pitfalls, "except" patterns | Defensive memory — "what will TRIP ME UP?" |
| 5 | Atomic Summaries | Bite-sized, interconnected knowledge units | Foundational memory — "what is EACH piece?" |
| 6 | Simplified Yet Complete | Plain-language rewrite preserving every detail | Comprehension — "do I actually UNDERSTAND this?" |

---

## Pipeline

The pipeline has four phases. Phases 1 and 2 have user gates — do not advance until the user confirms or the gate condition is met.

### Phase 1: Ingest and Survey

**Extract text from the user's PDF or document.**

Locate the PDF skill's scripts directory dynamically. If the PDF skill is installed alongside this skill, derive the path from this skill's location (sibling directory). If the user pastes text directly, skip extraction and use the text as-is.

```bash
# PDF extraction
python3 "$PDF_SCRIPTS/pdf.py" extract.text <file_path>

# Word/PowerPoint — convert first, then extract
python3 "$PDF_SCRIPTS/pdf.py" convert.office <file_path>
```

Where `$PDF_SCRIPTS` resolves to the PDF skill's scripts directory relative to this skill's parent.

**After extraction, perform a rapid content survey:**
- Identify the document type: textbook chapter, clinical guideline, review article, case series, drug monograph
- Count the major topics and sections
- Flag the presence of: tables, algorithms, drug dosing, diagnostic criteria, staging systems, classification schemes
- Estimate scope: single disease vs. system-wide vs. pharmacology vs. general principles

**Output the survey and stop. Wait for user confirmation.**

```
DOCUMENT SURVEY
Type:        [textbook chapter / clinical guideline / review article / ...]
Scope:       [e.g., "Cardiology — Heart Failure (comprehensive)"]
Sections:    [list 3-8 section headings]
Key Elements: [e.g., "diagnostic criteria, NYHA classification, drug dosing tables, treatment algorithm"]
Digest Size: [Small / Medium / Large]
```

Ask: "Ready to digest? Or do you want to focus on specific sections only?"

**Gate: Do not proceed to Phase 2 until the user confirms scope.**

---

### Phase 2: Extract and Structure

Send the extracted text to LLM with a structured extraction prompt. This is the most critical step — the quality of everything downstream depends on what happens here.

Read the extraction prompt template from `references/extraction-prompt.md` and adapt it to the document type detected in Phase 1. The prompt instructs the LLM to produce a structured JSON with these top-level keys:

```json
{
  "metadata": { "title", "specialty", "topics", "document_type" },
  "clinical_approaches": [ { "name", "trigger", "steps", "branch_points", "endpoints" } ],
  "knowledge_hierarchy": { "topic", "subtopics": [ { "name", "children": [...] } ] },
  "clinical_pearls": [ { "pearl", "context", "buzzword", "associations" } ],
  "mcq_traps": [ { "trap", "distractor", "correct_answer", "why_tricky", "topic" } ],
  "atomic_facts": [ { "fact", "category", "connections": [], "source_section" } ],
  "simplified_sections": [ { "original_heading", "simplified_text", "key_details_preserved": [] } ]
}
```

**Scaling rules for large documents:**
- **Under 15,000 words:** Single extraction pass
- **15,000 to 30,000 words:** Split into logical sections, extract each separately, merge with the helper script
- **Over 30,000 words:** Offer the Progressive Digest interaction pattern (see Interaction Patterns). Do not attempt a single pass — quality degrades with length

**For documents with drug tables or dosing:** Add a special extraction pass that captures:
- Drug name (generic + brand if mentioned)
- Class and mechanism
- Key indications
- Critical side effects (only the board-relevant ones, not every reported adverse event)
- Contraindications and interactions
- Unique monitoring requirements

**Run validation on the extraction JSON** using the helper script:

```bash
python3 "$SKILL_DIR/scripts/generate_digest.py" validate <extraction.json>
```

Where `$SKILL_DIR` is the directory containing this SKILL.md. Fix any reported issues before proceeding.

**Gate: Validate that all six top-level keys are present and populated before generating pillars.**

---

### Phase 3: Generate Pillars

Process the extracted JSON to produce each of the six output pillars. Generate them in the order below — earlier outputs inform later ones.

#### Pillar 1: Clinical Approach Flowcharts

**What to flowchart:** Any clinical scenario involving a sequence of decisions — diagnostic workup, treatment escalation, emergency management, screening algorithms, differential diagnosis trees.

**How to identify flowchart-worthy content:**
- Phrases like "first-line," "if unresponsive," "step-up therapy," "rule out," "proceed to"
- Algorithms with decision diamonds (Is X present? leads to Yes/No branches)
- Staged approaches (Stage 1 leads to Stage 2 leads to Stage 3)
- Differential diagnosis trees with discriminator-based branching

**Generation method:** Use Mermaid flowchart syntax. Each flowchart must:
- Have a clear **trigger** (what clinical scenario starts this algorithm?)
- Use **diamond nodes** `{}` for decision points
- Use **rounded nodes** `()` for actions
- Include **red-flag branches** where appropriate (danger signs, don't-miss conditions)
- End with clear **outcomes and endpoints**
- Cap at **15 nodes per flowchart** — if the algorithm is more complex, split into sub-flowcharts linked by reference

Read `references/flowchart-patterns.md` for five clinical flowchart templates: diagnostic workup, treatment escalation, emergency management, screening algorithm, and differential diagnosis tree.

**Render Mermaid to PNG** using the charts skill (Playwright+CSS rendering for Mermaid diagrams).

**Naming convention:** `flowchart_[topic]_[type].png`

**Color system (consistent across all flowcharts in one digest):**
- Red (#ff6b6b): Emergency, danger, don't-miss
- Yellow (#ffd43b): Decision points
- Green (#51cf66): Confirmed diagnosis, positive outcome
- Blue (#74c0fc): Investigation, process step
- Purple (#cc5de8): Referral, specialist input
- Gray (#dee2e6): Ruled out, not indicated

---

#### Pillar 2: Mind Maps

**What to mind-map:** Topic hierarchies, classification systems, anatomy/physiology relationships, drug class organizations, disease feature groupings.

**Generation method:** Use Playwright+CSS mind map rendering (charts skill).

**Mind map structure rules:**
- **Central node:** The main topic (e.g., "Heart Failure")
- **Level 1 branches:** Major categories (Etiology, Diagnosis, Treatment, Complications)
- **Level 2 branches:** Sub-categories (within Etiology: Ischemic, Valvular, Hypertensive)
- **Level 3 leaves:** Specific facts (within Ischemic: "MI leads to remodeling leads to systolic HF")
- **No deeper than Level 3** — if Level 4 is needed, create a separate sub-map

**Color coding (consistent across all mind maps in one digest):**
- Red: Emergency, critical, don't-miss
- Orange: Warning, caution, contraindication
- Blue: Diagnostic information
- Green: Treatment and management
- Purple: Classification and taxonomy
- Gray: Background and context

**Naming convention:** `mindmap_[topic].png` or `mindmap_[topic]_[subcategory].png` for sub-maps

---

#### Pillar 3: Clinical Pearls

Read `references/clinical-pearls-guide.md` for the full extraction heuristics. Below is the summary.

**A clinical pearl must satisfy at least two of these three criteria:**
1. **High exam yield** — this fact has appeared or would appear on board-style exams
2. **Clinically actionable** — knowing this fact changes management or prevents harm
3. **Memorable anchor** — this fact has a hook (buzzword, visual, acronym, paradox) that makes it stick

**Format each pearl as:**
```
PEARL #[number]: [Short punchy title]
Buzzword: [if applicable]
Association: [A <-> B]
Context: [1-2 sentences: when does this matter?]
Exam Relevance: [High/Medium] — [why boards love it]
```

**Six pearl categories** (see the reference file for extraction patterns):
1. Buzzword associations ("currant jelly sputum" equals Klebsiella)
2. Classic presentations ("worst headache of my life" equals subarachnoid hemorrhage)
3. Don't-miss diagnoses (fever plus rash plus palms/soles equals consider Rocky Mountain spotted fever)
4. Paradoxical findings (iron deficiency leads to HIGH TIBC, not low)
5. Drug-disease associations (ACE inhibitors cause dry cough, switch to ARB)
6. Demographic anchors (young Asian female equals consider Takayasu arteritis)

**Target: 15 to 30 pearls per digest** depending on document size. Quality over quantity — every pearl must be genuinely high-yield, not just a fact.

---

#### Pillar 4: MCQ Traps

Read `references/mcq-trap-patterns.md` for the full archetype catalog with examples. Below is the summary.

**Ten trap archetypes:**

| # | Trap Type | The Cognitive Pitfall |
|---|-----------|----------------------|
| 1 | The "Except" Trap | Student finds the correct statement instead of the incorrect one |
| 2 | Near-Miss Distractor | Two answers differ by one critical word (sensitive vs specific) |
| 3 | Demographic Trap | Classic disease in unexpected demographic changes the answer |
| 4 | Most Common vs Most Lethal | Frequency does not equal severity |
| 5 | First-Step Trap | The "best" test is not always the "first" test |
| 6 | Drug Trap | Right drug wrong indication, or right class wrong agent |
| 7 | Always/Never Trap | Absolute words in options are almost always wrong |
| 8 | Overstatement Trap | True statement broadened beyond what evidence supports |
| 9 | Numerical Trap | Close-but-wrong values as distractors |
| 10 | Next Best Step | The answer depends on whether the patient is stable |

**Format each trap as:**
```
TRAP #[number]: [Category type]
Scenario: [Brief clinical vignette or question stem]
The Trap: [What looks right but is not / what the distractor exploits]
The Correct Answer: [What is actually right]
Why It Is Tricky: [1-2 sentences explaining the cognitive pitfall]
How to Avoid: [Specific strategy for this type of trap]
```

**Target: 10 to 20 traps per digest.** Do not manufacture traps where they do not naturally exist — contrived traps are worse than no traps.

---

#### Pillar 5: Atomic Summaries

**What is an atomic summary:** Each piece of knowledge broken into the smallest standalone unit that still makes sense. An atom is a single clinical fact that can be understood without reading surrounding context.

**Atomic fact format:**
```
ATOM #[number]
Category: [Diagnosis / Treatment / Pharmacology / Pathophysiology / Epidemiology / Classification]
Statement: [One clear, complete sentence]
Connections: [List of other atom numbers this relates to]
Source: [Section or page in original document]
```

**Rules for atomic facts:**
- One fact per atom — never combine two facts into one
- Each atom must be self-contained — no "as mentioned above" or "see previous"
- Use precise medical terminology — isolate the fact, do not dumb down the language
- Include numeric values where the original has them — do not round, do not approximate
- Flag high-yield atoms with a target marker

**Target: 40 to 80 atoms per digest** depending on document size.

---

#### Pillar 6: Simplified Yet Complete

**This is NOT a summary — it is a translation.** The goal is to rewrite the entire document in plain, conversational language while preserving every single detail.

**Simplification rules:**
- Replace jargon only when a simpler term exists without losing precision ("myocardial infarction" stays because it is precise; "atherosclerotic cardiovascular disease" can become "plaque buildup in heart arteries" with the formal term in parentheses)
- Break compound-complex sentences into 2-3 shorter ones
- Replace passive voice with active voice
- Add "why" explanations where the original just states "what" ("Give furosemide first" becomes "Give furosemide first because you need to reduce preload before the patient drowns in their own fluid")
- Preserve all numbers, cutoffs, criteria, drug names, and dosages exactly as stated
- Organize with clear headers matching the original structure
- Mark sections that students typically find confusing and add a clarifying note

**Format:** Full narrative text, section by section, mirroring the original document's organization. Each section heading from the original gets a corresponding simplified section.

---

### Phase 4: Assemble and Deliver

Compile all six pillars into a single comprehensive document. The output format is determined by the `--format` option:

- **`pdf`** (default): Professional print-ready document via the PDF skill's Report route (ReportLab)
- **`html`**: Interactive, self-contained HTML file with inline styles, collapsible sections, and embedded images (base64)

If the user does not specify a format, default to `pdf`. If the user says "web page", "interactive", "browser", or "HTML", use `html`.

**Document structure (shared across both formats):**

```
COVER / HEADER
  Title: [Document Topic] — Clinical Digest
  Subtitle: Flowcharts | Mind Maps | Pearls | MCQ Traps | Atoms | Simplified
  Source: [Original document title]
  Generated: [Date]

TABLE OF CONTENTS

SECTION 1: CLINICAL APPROACH FLOWCHARTS
  1.1 [Flowchart Name] — rendered image
  1.2 [Flowchart Name] — rendered image
  Each flowchart gets dedicated space with the image centered and a brief caption.

SECTION 2: MIND MAPS
  2.1 [Main Mind Map] — rendered image
  2.2 [Sub-Map: Topic] — rendered image
  Each mind map gets dedicated space.

SECTION 3: CLINICAL PEARLS
  3.1-3.N [Individual pearls]
  Grouped by topic with mini-headers.

SECTION 4: MCQ TRAPS
  4.1-4.N [Individual traps]
  Grouped by trap category.

SECTION 5: ATOMIC SUMMARIES
  5.1-5.N [Individual atoms]
  Grouped by category (Diagnosis, Treatment, etc.)
  Cross-references shown as links where the format supports it.

SECTION 6: SIMPLIFIED YET COMPLETE
  Full simplified narrative, section by section.
```

---

#### PDF Output Specifications

Use the PDF skill's Report route (ReportLab) for generation.

- Page size: A4
- Margins: 20mm all sides
- Section headers: 14pt bold, colored (each section gets a distinct color)
- Body text: 10pt, 1.4 line spacing
- Flowchart and mind map images: full-width, centered, with captions
- Pearls and traps: bordered cards with distinct background colors
- Atoms: compact table format where possible
- Page numbers: bottom center
- Continuous flow within each pillar (no page breaks between sub-sections)
- Page break between major sections only
- File name: `clinical_digest_[topic]_[date].pdf`

---

#### HTML Output Specifications

Generate a single, self-contained `.html` file. All images must be embedded as base64 data URIs so the file is portable and works offline. No external CSS or JS dependencies.

**HTML structure:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Topic] — Clinical Digest</title>
  <style>
    /* All styles inline — see CSS specifications below */
  </style>
</head>
<body>
  <header class="cover"> ... </header>
  <nav class="toc"> ... </nav>
  <main>
    <section id="flowcharts"> ... </section>
    <section id="mindmaps"> ... </section>
    <section id="pearls"> ... </section>
    <section id="traps"> ... </section>
    <section id="atoms"> ... </section>
    <section id="simplified"> ... </section>
  </main>
</body>
</html>
```

**CSS specifications:**
- Font: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif
- Body: max-width 900px, margin 0 auto, padding 20px, line-height 1.6, color #1a1a2e
- Cover header: gradient background (#1a1a2e to #16213e), white text, centered, padding 60px 20px
- TOC: sticky sidebar on desktop (left), collapsible on mobile; links with smooth scroll
- Section headers: 1.6rem bold, colored left border (5px), margin-top 3rem
  - Flowcharts: #3498db (blue)
  - Mind Maps: #9b59b6 (purple)
  - Pearls: #e67e22 (orange)
  - Traps: #e74c3c (red)
  - Atoms: #2ecc71 (green)
  - Simplified: #1abc9c (teal)
- Images: max-width 100%, border-radius 8px, box-shadow 0 2px 8px rgba(0,0,0,0.1), centered
- Pearl cards: border-left 4px solid #e67e22, background #fef9f3, padding 16px, border-radius 4px, margin 12px 0
- Trap cards: border-left 4px solid #e74c3c, background #fef2f2, padding 16px, border-radius 4px, margin 12px 0
- Atom entries: compact cards with category badge, subtle background (#f8f9fa), padding 10px 14px
- Collapsible sections: each pillar section has a clickable header that toggles content visibility; use `<details><summary>` elements for native HTML collapsing without JavaScript
- Responsive: single column on mobile (<768px), sidebar TOC on desktop (>=768px)
- Print media: hide TOC sidebar, remove shadows, ensure images fit page width
- File name: `clinical_digest_[topic]_[date].html`

**Image embedding:** Convert all rendered flowchart and mind map PNG images to base64 data URIs:
```python
import base64
with open(image_path, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')
data_uri = f'data:image/png;base64,{b64}'
```
Embed as `<img src="{data_uri}" alt="..." />`.

**HTML-specific interactive features:**
- Each section is wrapped in `<details open>` so users can collapse/expand pillars
- Atom cross-references use anchor links: `<a href="#atom-42">Atom #42</a>`
- TOC links use anchor smooth-scroll: `<a href="#flowcharts">Flowcharts</a>`
- Pearl and trap cards have subtle hover effects (transform, shadow) via CSS only
- A "Back to Top" floating button appears after scrolling 300px (CSS + minimal inline JS)

---

**Save the output** to the user's download directory as either `clinical_digest_[topic]_[date].pdf` or `clinical_digest_[topic]_[date].html` depending on the selected format. Resolve the download directory from the project workspace, not from a hardcoded absolute path.

---

## Commands

The skill supports sub-commands for targeted use. See the **Updated Commands Reference** section at the bottom for the complete table including new commands (`flashcards`, `search`).

**Quick reference — output routing:**
1. **No command:** Run the full `digest` pipeline
2. **Named pillar(s):** Run only those pillars
3. **"just the high-yield stuff":** Run `pearls` + `traps`
4. **"visual study aids":** Run `flowcharts` + `mindmaps`
5. **"flashcards" / "Anki" / "Quizlet":** Run `flashcards`
6. **"search [keyword]":** Run `search`

**Format routing:**
1. **No format:** Default `pdf`
2. **"web page" / "interactive" / "HTML":** → `html`
3. **"Obsidian" / "Notion" / "markdown" / "notes app":** → `md`
4. **"Anki" / "flashcards":** → `anki`
5. **"Quizlet":** → `quizlet`
6. **"both":** → `pdf` + `html`
7. **"all":** → `pdf` + `html` + `md`
8. **"comprehensive" / "thorough":** Set `--depth comprehensive`

**Depth routing:**
1. **"quick" / "brief" / "just the key points":** → `--depth brief`
2. **Default:** → `--depth standard`
3. **"comprehensive" / "everything" / "full":** → `--depth comprehensive`

---

## Exam-Oriented Design Principles

Every output from this skill is designed for one purpose: help the user pass clinical board exams and apply knowledge at the bedside. These principles govern every decision:

### 1. Board Relevance First
Not every fact in a textbook is exam-relevant. Prioritize content that appears on USMLE, PLAB, and other standardized medical exams. When in doubt, include it — but tag the exam relevance so the user can triage.

### 2. Clinical Reasoning Over Rote Memorization
Flowcharts must show *why* each step follows from the previous one. Pearls must include *context* (when does this matter?). Atoms must include *connections* to other atoms. Disconnected facts are forgotten facts.

### 3. Test the Trap, Not Just the Fact
MCQ traps are not an afterthought — they are a core output. Boards test whether students can avoid distractors, not just whether they know the right answer. Every trap must represent a real exam pattern with a concrete avoidance strategy.

### 4. Systematic Coverage
The six pillars are not six random formats — they are a systematic coverage of cognitive targets. If a topic is only covered in one pillar, the coverage is incomplete. Aim for every major topic to appear in at least two pillars.

### 5. Precision in Numbers
Cutoffs, doses, sensitivities, specificities — these are the most tested and most easily confused facts. Preserve exact values. Never round. Never approximate. A cutoff of 6.5 is not "approximately 6" — it is 6.5.

### 6. No Invented Content
Every pearl, trap, and atom must be derivable from the source document. If the document does not mention a classic association, do not add it, even if you know it is true. The skill is a decompiler, not an encyclopedia. Flag gaps where the document is incomplete and suggest web-search supplementation instead.

---

## Interaction Patterns

### Pattern 1: Full Digest (default)
User provides a PDF. Run the complete 6-pillar pipeline. Deliver the compiled document in the requested format (default: PDF; use `--format html` for HTML output).

### Pattern 2: Targeted Digest
User specifies which pillars they want ("just the flowcharts" or "pearls and traps only"). Run only the requested pillars. Deliver as PDF or HTML depending on the `--format` flag, or present inline for small extractions.

### Pattern 3: Progressive Digest
For large documents, offer section-by-section processing:
"This document has 8 main chapters. Full processing will take approximately X minutes. Would you like to:
1. Process everything at once
2. Process section by section (confirm after each chapter)
3. Process only specific chapters"
The format flag applies to the final assembled output.

### Pattern 4: Augment Existing Digest
User says "add more MCQ traps" or "expand the mind map for section 3." Augment the existing output without reprocessing everything. Reuse the extraction JSON from the previous run. Regenerate the output file in the previously used format (or the new format if the user specifies one).

### Pattern 5: Quick Extraction
User says "just give me the high-yield pearls." Skip the full pipeline, extract pearls only, present inline. No file generation needed unless the user requests a specific format.

---

## Document Type Adaptation

Different document types require different extraction emphasis.

### Textbook Chapters
- Dense with information — expect 60-80 atoms, 20-30 pearls
- Classification systems become mind maps
- Management algorithms become flowcharts
- "Key points" and "summary" boxes become pearls directly

### Clinical Guidelines
- Algorithm-heavy — prioritize flowcharts
- Recommendation grading (Class I/IIa/IIb/III) becomes atomic facts plus traps
- Drug recommendations become pharmacology atoms
- "Consider" vs "Recommend" distinction becomes MCQ traps
- Reversed recommendations (old vs new guideline) become high-yield traps

### Review Articles
- Broad but shallow — fewer atoms per topic, more topics
- Comparison tables become mind maps
- "Key takeaways" sections become pearls
- Controversies become trap material (both sides as distractors)

### Drug Monographs / Pharmacology
- Organize by drug class — one mind map per class
- Mechanism of action becomes simplified section with analogy
- Side effect profiles become pearl plus trap combinations
- Dosing cutoffs become numerical traps
- Prodrug requirements and monitoring requirements become atoms

### Case-Based Learning
- Each case becomes a diagnostic flowchart
- Differential diagnosis becomes a mind map
- Key learning points become pearls
- Common misdiagnoses become traps
- What the case "teaches" becomes simplified section

---

## Quality Verification

Before delivering, verify every item. This is not optional — a digest that fails verification is incomplete.

### Completeness
- Every major topic in the original document is covered in at least 2 pillars
- No diagnostic criteria, staging system, or classification is missing
- All drug names mentioned in the original appear in at least one pillar
- Numeric values (cutoffs, doses, sensitivity/specificity) are preserved exactly

### Accuracy
- No pearl or atom contradicts the original text
- Flowchart logic matches the described algorithm
- MCQ trap correct answers are verified against the source
- Simplified text does not introduce errors during simplification

### Exam Utility
- Each pearl would actually appear on a board exam
- Each trap represents a real exam pattern, not a contrived scenario
- Flowcharts are usable as quick references (not too cluttered)
- Mind maps are readable at print size (not too dense)
- Atoms are truly self-contained (no "see above" references)
- Simplified text is genuinely easier to understand than the original

### Visual
- Flowchart images are high resolution and readable
- Mind map color coding is consistent
- PDF formatting is clean (no overflow, no cut-off images)

### Run the helper script for stats
```bash
python3 "$SKILL_DIR/scripts/generate_digest.py" stats <extraction.json>
```

Check the "Pillar Coverage" score. If it is below 6/6, identify which pillars are empty and generate them before delivering.

---

## Language Handling

- **Input language:** Accept documents in any language
- **Output language:** Match the user's conversation language
- **Medical terminology:** Always preserve the original medical term alongside any translation (e.g., if the document uses a non-English term, include both the original and the English equivalent)
- **Drug names:** Generic name in original language plus INN (International Nonproprietary Name) if different
- **Flowchart and mind map labels:** Use the user's language but include English medical abbreviations where standard (e.g., NYHA, LVEF, ACEi)

---

## Dependencies on Other Skills

| Skill | How Used |
|-------|----------|
| PDF skill | Text extraction from PDFs; final PDF report generation (ReportLab) |
| Charts skill | Mermaid flowchart rendering to PNG; Playwright+CSS mind map rendering to PNG |
| LLM skill | Structured content extraction (clinical approaches, pearls, traps, atoms) |
| web-search | Supplement missing context when document is incomplete |

HTML output is generated natively within this skill using Python's string templating and base64 image embedding. No external HTML framework or skill is required.

Resolve skill paths dynamically from the skill directory structure. Never hardcode absolute paths.

---

## Edge Cases

**Document has images or tables that cannot be extracted:** Note which visual elements were skipped and ask if the user can provide the key data from those elements as text.

**Document is very short (under 500 words):** Still run the full pipeline but scale expectations down. You might only get 3-5 pearls and 1 flowchart. Do not pad with invented content.

**Document is very long (over 30,000 words):** Split processing by section. Warn the user about processing time. Offer the Progressive Digest pattern.

**Document is in a non-medical field but user wants the same treatment:** The pipeline still works. Adapt the terminology: "clinical approach" becomes "analytical approach," "clinical pearls" becomes "key insights," etc. The cognitive targets remain the same.

**Ambiguous or contradictory content in the source:** Flag it explicitly. Do not silently resolve contradictions — present both versions and note the discrepancy.

---

## Absolute Bans

These rules are match-and-refuse. If you are about to do any of these, rewrite the output.

- **Invented content.** Every pearl, trap, and atom must be derivable from the source document. No external knowledge insertion.
- **Rounded numbers.** A cutoff of 126 mg/dL is not "about 125." A dose of 4.5 hours is not "about 4 hours." Precision is non-negotiable.
- **Self-referential atoms.** An atom that says "see above" or "as mentioned previously" is not atomic. Rewrite it to be self-contained.
- **Decorative flowcharts.** A flowchart without decision points is just a list. If there are no branches, use a numbered list instead of a flowchart.
- **Overstuffed mind maps.** A mind map with more than 3 levels of depth is unreadable. Split it into sub-maps.
- **Contrived traps.** A trap that no real exam would use is noise. Every trap must represent an actual exam pattern from the trap archetype catalog.
- **Shallow pearls.** A pearl without context is trivia. Every pearl must include when it matters clinically.

---

## Output Format: Markdown (`--format md`)

Markdown output is ideal for knowledge management systems (Obsidian, Roam, Notion, Logseq).

**Generate:**
```bash
python3 "$SKILL_DIR/scripts/generate_digest.py" build-md <extraction.json> [output.md]
```

**Features:**
- Wikilink-style table of contents compatible with Obsidian (`[[#Section]]` anchors)
- Color-coded mind map branches (emoji markers: 🔴 emergency, 🟢 treatment, 🔵 diagnosis, etc.)
- High-yield pearls marked with ⭐
- Trap sections with ⚠️ distractor / ✅ correct answer formatting
- Atomic facts grouped by category with high-yield stars
- YAML-compatible tags in frontmatter area (`#medicine #clinical-digest #specialty`)
- File name: `clinical_digest_[topic]_[date].md`

---

## Output Format: Anki Flashcards (`--format anki` / `--format quizlet`)

Export clinical pearls and MCQ traps as study flashcards.

**Generate flashcards:**
```bash
# From generate_digest.py (delegates to make_flashcards.py if available)
python3 "$SKILL_DIR/scripts/generate_digest.py" flashcards <extraction.json> [prefix] [--include pearls,traps,atoms]

# Directly from make_flashcards.py (more options)
python3 "$SKILL_DIR/scripts/make_flashcards.py" <extraction.json> \
    --format all \
    --include pearls,traps \
    --depth high-yield-only
```

**Output files:**
- `[prefix]_anki.tsv` — Import into Anki: File → Import → Note type: Basic → Separator: Tab
- `[prefix]_quizlet.csv` — Import at quizlet.com/create-set → Import (comma-separated)
- `[prefix]_flashcards.md` — Human-readable review cards (print or paste into Notion)

**Card generation logic:**
- **Pearl cards:** Front = buzzword/context question; Back = pearl + associations + why tested
- **Trap cards:** Front = scenario + distractor (highlighted red); Back = correct answer + avoidance strategy
- **Atom cards:** Front = completion question derived from the fact; Back = full fact statement

**When to use flashcards:** Always offer flashcard export at the end of a full digest. Add this message:
> "I've also generated Anki/Quizlet flashcards from the pearls and traps — import `[filename]_anki.tsv` into Anki to start spaced-repetition review."

---

## Pharmacology / Drug Documents

When the document is a drug monograph, pharmacology chapter, or formulary entry, read `references/drug-extraction.md` before Phase 2.

**Additional extraction output:** Add a `drug_profiles` array to the extraction JSON (schema in `references/drug-extraction.md`). This array is then used to populate a dedicated **Drug Cards** section in the HTML and PDF output, and generates a drug-specific Anki deck.

**Document type:** Set `document_type: "drug_monograph"` in metadata.

**Trigger signals:** Drug name in document title; sections titled "Mechanism of Action", "Adverse Effects", "Contraindications", "Drug Interactions", "Monitoring"; comparative drug tables.

---

## Automation: Full Pipeline Script

For users with `ANTHROPIC_API_KEY` set, the entire pipeline can run with one command:

```bash
# Make executable
chmod +x "$SKILL_DIR/scripts/pipeline.sh"

# Run full pipeline
"$SKILL_DIR/scripts/pipeline.sh" heart_failure.pdf

# With options
"$SKILL_DIR/scripts/pipeline.sh" \
    --format all \
    --depth comprehensive \
    --flashcards \
    --specialty cardiology \
    --output ~/study/cardiology \
    heart_failure.pdf
```

**Pipeline steps:**
1. Text extraction (PDF → txt via PyMuPDF, or DOCX via python-docx)
2. LLM extraction via `extract_content.py` (auto-chunks large documents)
3. JSON validation and stats via `generate_digest.py`
4. Output generation (HTML, Markdown, PDF — whichever formats requested)
5. Optional: Flashcard export

**Dependencies for full automation:**
```bash
pip install anthropic pymupdf python-docx reportlab
```

---

## Search / Quick Lookup

Find content across all pillars without re-reading the full digest:

```bash
python3 "$SKILL_DIR/scripts/generate_digest.py" search <extraction.json> <keyword>
```

Example:
```
$ python3 generate_digest.py search extraction.json "furosemide"

Search results for: 'furosemide'
==================================================
PEARLS (2 matches):
  • Furosemide is ototoxic — especially when combined with aminoglycosides...
  • Loop diuretics cause hypokalemia and hypomagnesemia...

TRAPS (1 match):
  • [Drug Trap] Patient on furosemide + gentamicin develops hearing loss...

ATOMS (4 matches):
  • [Pharmacology][HY] Furosemide inhibits Na-K-2Cl cotransporter...
  ...
Total: 7 matches across all pillars
```

---

## Updated File Structure

```
med-pdf-digest/
├── SKILL.md                                This file
├── references/
│   ├── extraction-prompt.md                LLM extraction prompt template
│   ├── flowchart-patterns.md               Clinical flowchart Mermaid templates
│   ├── mcq-trap-patterns.md                MCQ trap archetype catalog
│   ├── clinical-pearls-guide.md            Pearl extraction heuristics
│   └── drug-extraction.md                  Drug/pharmacology extraction guide  ← NEW
├── scripts/
│   ├── generate_digest.py                  Orchestration helper (merge, validate, build)
│   ├── extract_content.py                  Anthropic API extraction script          ← NEW
│   ├── make_flashcards.py                  Anki/Quizlet/Markdown flashcard exporter ← NEW
│   └── pipeline.sh                         End-to-end automation shell script       ← NEW
└── evals/
    └── evals.json                          Test cases
```

---

## Updated Commands Reference

| Command | Description | New? |
|---------|-------------|------|
| `digest` | Full 6-pillar pipeline (default) | |
| `flowcharts` | Clinical approach flowcharts only | |
| `mindmaps` | Mind maps only | |
| `pearls` | Clinical pearls only | |
| `traps` | MCQ traps only | |
| `atoms` | Atomic summaries only | |
| `simplified` | Simplified rewrite only | |
| `survey` | Phase 1 only — document survey | |
| `validate` | Validate extraction JSON | |
| `flashcards` | Export Anki TSV + Quizlet CSV + Markdown cards | ← NEW |
| `search <keyword>` | Full-text search across all pillars | ← NEW |

**Updated format flags:**

| Flag | Values | Description |
|------|--------|-------------|
| `--format` | `pdf` | Print-ready PDF (default) |
| `--format` | `html` | Self-contained interactive HTML |
| `--format` | `md` | Markdown (Obsidian/Notion compatible) ← NEW |
| `--format` | `anki` | Anki TSV flashcards ← NEW |
| `--format` | `quizlet` | Quizlet CSV flashcards ← NEW |
| `--format` | `both` | PDF + HTML |
| `--format` | `all` | PDF + HTML + Markdown ← NEW |
| `--depth` | `brief\|standard\|comprehensive` | Extraction depth ← NEW |

---

## Updated Dependencies

| Component | How Used | Required? |
|-----------|----------|-----------|
| PDF skill | Text extraction from PDFs (Phase 1) | Required for PDFs |
| Charts skill | Mermaid flowchart + mind map rendering to PNG | Required for visuals |
| `extract_content.py` | Automated LLM extraction via Anthropic API | Optional (automation) |
| `make_flashcards.py` | Export to Anki TSV / Quizlet CSV / Markdown | Optional |
| `pipeline.sh` | Full end-to-end orchestration | Optional |
| `anthropic` (pip) | Required by extract_content.py | Optional |
| `reportlab` (pip) | Required by build-pdf command | Optional |
| `pymupdf` (pip) | PDF text extraction in pipeline.sh | Optional |

