# LLM Extraction Prompt Template

This file contains the prompt template for extracting structured clinical knowledge from medical documents. Adapt this template based on the document type detected in Phase 1 of the pipeline.

---

## System Prompt

```
You are a medical knowledge extraction engine. Your job is to parse clinical text and extract structured knowledge that will be transformed into study aids (flowcharts, mind maps, clinical pearls, MCQ traps, atomic summaries, and simplified explanations).

You must be:
- EXHAUSTIVE: Don't skip details because they seem minor. A single lab value cutoff might be the difference between a correct and wrong answer on boards.
- PRECISE: Preserve exact numbers, drug names, criteria, and cutoffs. Never round, never approximate.
- STRUCTURED: Output valid JSON matching the schema exactly. No prose, no explanations outside the JSON.
- CLINICAL: Think like a medical educator. What would a board examiner test? What would a student struggle with?

Critical rules:
1. Every diagnostic criterion mentioned must appear as at least one atomic fact
2. Every drug mentioned must have its class, indication, and key side effects captured
3. Treatment algorithms must be captured as step-by-step sequences with branch points
4. Differentials must be captured as comparison-ready structures
5. Numeric values are sacred — preserve them exactly as written
6. If the text is ambiguous, capture both interpretations with a note
7. Do NOT invent information not present in the source text
8. Do NOT skip content because it seems "obvious" or "basic"
```

---

## User Prompt (adapt per document type)

### For Textbook Chapters

```
Extract structured clinical knowledge from this textbook chapter. The chapter covers: [topic].

For each section of the text, extract:

1. **clinical_approaches**: Any diagnostic workup, treatment algorithm, or management sequence.
   - Each approach needs: name (e.g., "Heart Failure Diagnostic Workup"), trigger (what starts this algorithm), steps (ordered list of actions), branch_points (decision nodes with yes/no paths), endpoints (outcomes/destinations)
   - If a section describes sequential clinical reasoning, that's a clinical approach
   - If a section describes "if X then Y, if not X then Z" logic, that's a branch point

2. **knowledge_hierarchy**: The organizational structure of the topic.
   - Build a tree: main topic → major categories → sub-categories → specific facts
   - This will become mind maps, so structure matters more than detail
   - Classification systems go here (e.g., NYHA I-IV, Killip class)

3. **clinical_pearls**: High-yield facts that boards love.
   - Buzzword associations (e.g., "owl's eye inclusions = CMV")
   - Classic presentations (e.g., "young female + morning stiffness = rheumatoid arthritis")
   - Don't-miss diagnoses
   - Paradoxical findings
   - Demographic associations
   - Each pearl needs: the pearl itself, clinical context, buzzword (if any), associated conditions

4. **mcq_traps**: Common exam pitfalls hidden in this content.
   - What would an examiner use as a distractor?
   - What is the common wrong answer and why do students pick it?
   - Near-miss differentials that trip people up
   - Each trap needs: trap description, the distractor, correct answer, why it's tricky, topic

5. **atomic_facts**: Every distinct piece of knowledge as a standalone unit.
   - One fact per atom — no compound statements
   - Include exact numbers, cutoffs, criteria
   - Each atom needs: the fact, category, connections to other atoms, source section
   - Mark high-yield atoms (board-relevant)

6. **simplified_sections**: Rewrite each section in plain language.
   - Preserve ALL details but make them understandable
   - Add "why" explanations where the text only states "what"
   - Mark sections that students typically find confusing

Note: The extracted JSON will be rendered into either a PDF or HTML document. Ensure all text is clean ASCII/UTF-8 without CJK punctuation artifacts. Image file references should use relative filenames (e.g., "flowchart_heart_failure_diagnostic_workup.png") so the build script can resolve them from the image output directory.

Here is the text to extract from:

[INSERT TEXT HERE]
```

### For Clinical Guidelines

```
Extract structured clinical knowledge from this clinical guideline. The guideline covers: [topic].

Guidelines have specific structures you must capture:

1. **clinical_approaches**: The guideline's recommendation algorithms are the most important flowcharts.
   - Capture each recommendation pathway as a separate approach
   - Class of recommendation (I, IIa, IIb, III) and Level of Evidence (A, B, C) are critical — make them part of the steps
   - "Consider" vs "Recommend" vs "May be reasonable" distinctions matter

2. **knowledge_hierarchy**: Organize by guideline section structure.

3. **clinical_pearls**:
   - Class I recommendations that are must-knows
   - Class III (harm) recommendations — these are frequent exam traps
   - Strong recommendations with weak evidence (counter-intuitive)

4. **mcq_traps**:
   - Class IIa vs IIb distinctions (examiners love these)
   - Interventions that seem right but are Class III (harmful)
   - Old recommendations that the guideline has now reversed

5. **atomic_facts**:
   - Each recommendation = at least one atom with its class and evidence level
   - Dose targets and thresholds with exact values

6. **simplified_sections**:
   - Translate recommendation language into plain clinical decisions
   - "Class IIa, LOE B" -> "Probably helpful, based on moderate evidence"

Note: The extracted JSON will be rendered into either a PDF or HTML document. Ensure all text is clean ASCII/UTF-8 without CJK punctuation artifacts.

Here is the guideline text:

[INSERT TEXT HERE]
```

### For Pharmacology / Drug Monographs

```
Extract structured pharmacological knowledge from this text covering: [topic].

Pharmacology extraction has special requirements:

1. **clinical_approaches**: Drug selection algorithms (first-line, second-line, alternatives).
   - When to switch drugs
   - Contraindication-based routing
   - Side effect management algorithms

2. **knowledge_hierarchy**: Organize by drug class, mechanism, then individual agents.

3. **clinical_pearls**:
   - Unique side effects (e.g., "ACEi → dry cough")
   - Black box warnings
   - Drug-food interactions (e.g., "warfarin + vitamin K foods")
   - Monitoring requirements (e.g., "lithium → check levels, thyroid, renal")
   - Teratogenicity

4. **mcq_traps**:
   - Right drug, wrong dose
   - Right class, wrong specific agent
   - Shared side effects vs unique side effects
   - Prodrug activation requirements

5. **atomic_facts**: One atom per drug property:
   - Mechanism of action
   - Indication
   - Key side effect
   - Contraindication
   - Interaction
   - Monitoring requirement
   - Dosing note

6. **simplified_sections**: Explain mechanism with analogies where possible.

Note: The extracted JSON will be rendered into either a PDF or HTML document. Ensure all text is clean ASCII/UTF-8 without CJK punctuation artifacts. Drug names should use the generic name as the primary identifier.

Here is the pharmacology text:

[INSERT TEXT HERE]
```

---

## Output JSON Schema

```json
{
  "metadata": {
    "title": "string — document title",
    "specialty": "string — medical specialty",
    "topics": ["array of strings — major topics covered"],
    "document_type": "string — textbook/guideline/review/pharmacology/case-based",
    "extraction_date": "ISO date string",
    "word_count_estimate": "number"
  },
  "clinical_approaches": [
    {
      "name": "string — descriptive name of the approach",
      "type": "diagnostic_workup | treatment_algorithm | emergency_management | screening | monitoring | drug_selection",
      "trigger": "string — what clinical scenario starts this algorithm",
      "steps": [
        {
          "order": "number",
          "action": "string — what to do",
          "rationale": "string — why (brief)",
          "critical": "boolean — is this a don't-miss step?"
        }
      ],
      "branch_points": [
        {
          "question": "string — the decision criterion",
          "yes_path": "string — what to do if yes",
          "no_path": "string — what to do if no",
          "clinical_significance": "string — why this branch matters"
        }
      ],
      "endpoints": ["array of strings — possible outcomes"],
      "red_flags": ["array of strings — danger signs within this approach"]
    }
  ],
  "knowledge_hierarchy": {
    "topic": "string — central topic",
    "subtopics": [
      {
        "name": "string",
        "color_suggestion": "string — red/orange/blue/green/purple/gray",
        "children": [
          {
            "name": "string",
            "children": [
              {
                "name": "string — leaf node, specific fact",
                "detail": "string — optional brief elaboration"
              }
            ]
          }
        ]
      }
    ]
  },
  "clinical_pearls": [
    {
      "pearl": "string — the high-yield fact",
      "context": "string — when this matters clinically",
      "buzzword": "string or null — associated buzzword",
      "associations": ["array of strings — linked conditions/findings"],
      "exam_relevance": "high | medium",
      "why_tested": "string — why boards love this pearl"
    }
  ],
  "mcq_traps": [
    {
      "trap_category": "except_trap | near_miss | demographic_trap | most_common_vs_lethal | first_step | drug_trap | always_never | overstatement | numerical_trap | next_best_step",
      "scenario": "string — brief clinical vignette or question stem",
      "distractor": "string — the tempting wrong answer",
      "correct_answer": "string — the right answer",
      "why_tricky": "string — cognitive pitfall explanation",
      "avoidance_strategy": "string — how to not fall for it",
      "topic": "string — the subject area"
    }
  ],
  "atomic_facts": [
    {
      "fact": "string — one clear, complete sentence",
      "category": "diagnosis | treatment | pharmacology | pathophysiology | epidemiology | classification | monitoring | prognosis",
      "high_yield": "boolean — board-relevant?",
      "connections": ["array of numbers — other atom IDs this relates to"],
      "source_section": "string — where in the original document"
    }
  ],
  "simplified_sections": [
    {
      "original_heading": "string — section title from source",
      "simplified_text": "string — plain language rewrite preserving all details",
      "confusing_areas": [
        {
          "text": "string — the confusing part",
          "clarification": "string — why it's confusing + clarification"
        }
      ],
      "key_details_preserved": ["array of strings — critical details that were kept"]
    }
  ]
}
```

---

## Merging Partial Extractions

When processing large documents in sections, merge the JSON outputs:

1. `metadata` — combine topics lists, take the highest word count
2. `clinical_approaches` — concatenate arrays; deduplicate by name
3. `knowledge_hierarchy` — merge trees by matching topic names at each level
4. `clinical_pearls` — concatenate; deduplicate by pearl text
5. `mcq_traps` — concatenate; deduplicate by scenario
6. `atomic_facts` — concatenate and re-number; update connection IDs to new numbering
7. `simplified_sections` — concatenate in document order

After merging, do a final pass to:
- Ensure cross-references (atom connections, flowchart references) are consistent
- Remove any duplicates that slipped through
- Verify that the total content covers all major topics from the original document
