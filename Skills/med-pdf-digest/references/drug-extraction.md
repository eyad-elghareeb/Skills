# Drug Extraction Reference Guide
## Specialized Extraction for Pharmacology Documents and Drug Monographs

Use this reference when the document type is `drug_monograph` or when the content is predominantly pharmacological (drug mechanisms, side effects, interactions, dosing).

---

## When to Use This Guide

Activate drug-specific extraction when you detect:
- Drug monograph format (sections: Mechanism, Indications, Dosing, Adverse Effects, Contraindications)
- Pharmacology textbook chapter covering a drug class
- Formulary entries or prescribing information
- Comparative pharmacology tables
- Clinical guidelines where drug selection is the primary focus

---

## Drug Extraction Schema Extension

In addition to the standard extraction pillars, add a `drug_profiles` array to the extraction JSON:

```json
"drug_profiles": [
  {
    "name": "generic name",
    "brand_names": ["Brand1", "Brand2"],
    "drug_class": "e.g. ACE inhibitor, beta-blocker, loop diuretic",
    "mechanism": "One sentence: exact mechanism of action",
    "key_indications": ["indication 1", "indication 2"],
    "board_relevant_side_effects": [
      {
        "effect": "string",
        "mechanism_hint": "why this happens",
        "clinical_pearl": "what to watch for / what exam asks"
      }
    ],
    "critical_contraindications": ["CI 1", "CI 2"],
    "key_interactions": [
      {"interacts_with": "drug/food", "result": "outcome"}
    ],
    "monitoring_parameters": ["parameter 1", "parameter 2"],
    "board_traps": [
      {
        "trap": "description of common exam trap",
        "correct": "what is actually right"
      }
    ],
    "dosing_pearls": ["Specific numeric values that boards test"],
    "unique_features": ["What makes this drug different from others in its class"]
  }
]
```

---

## Pharmacology Extraction Rules

### Side Effects — Board Relevance Filter

INCLUDE (these appear on boards):
- Class-defining adverse effects (ACEi → dry cough; aminoglycosides → nephrotoxicity + ototoxicity)
- Life-threatening effects regardless of frequency (e.g. agranulocytosis with clozapine)
- Effects that require dose adjustment or drug switching
- Effects that are counter-intuitive or paradoxical
- Effects with a clear mechanism-based explanation

DO NOT INCLUDE:
- Generic "GI upset" unless that is the primary adverse effect of this drug class
- Effects reported in <0.1% of patients with no clinical significance
- Adverse effects that apply to all drugs in the entire class without differentiation

### Mechanism — Precision Required

Bad (too vague): "Works on the renin-angiotensin system"
Good (board-ready): "Inhibits angiotensin-converting enzyme, preventing conversion of angiotensin I → angiotensin II, reducing vasoconstriction and aldosterone secretion"

Always include: the molecular target, the downstream effect, and why this produces the clinical benefit.

### Dosing Pearls — Numeric Precision

Numeric cutoffs are among the highest-yield drug facts. Examples of what to capture:
- "Metformin: contraindicated if GFR <30 mL/min/1.73m²"
- "Digoxin toxicity risk increases significantly when K⁺ <3.5 mEq/L"
- "Aspirin at 81mg is antiplatelet; at 325-650mg is anti-inflammatory; >1g/day is uricosuric"

Never approximate these values.

---

## Drug Class Organization for Mind Maps

When digesting a drug class (e.g. all beta-blockers, all statins), organize the mind map as:

```
[Drug Class]
├── 🔵 Mechanism of Action
│   └── [shared mechanism]
├── 🟢 Individual Agents
│   ├── Drug A → unique features, indications
│   └── Drug B → unique features, indications
├── 🔴 Class-Wide Side Effects
│   └── [shared effects across all agents]
├── 🟠 Drug-Specific Side Effects
│   └── Drug A: [unique SE] | Drug B: [unique SE]
└── 🟣 Class-Wide Contraindications
    └── [shared CIs]
```

---

## Pharmacology Flowchart Templates

### Drug Selection Algorithm
```
Patient has [condition]
        ↓
Does patient have [contraindication A]?
   YES → Consider [alternative drug class]
   NO  ↓
Does patient have [comorbidity B]?
   YES → [Drug X] preferred (benefit in comorbidity B)
   NO  ↓
[Standard first-line drug] → Titrate to [target parameter]
        ↓
Reassess at [timeframe]. Adequate response?
   NO → Add [second agent] or uptitrate
   YES → Continue; monitor [parameter]
```

### Side Effect Management Algorithm
```
Patient develops [side effect] on [drug]
        ↓
Is this a class effect?
   YES → Switch to different drug class
   NO  ↓
Is the effect dose-dependent?
   YES → Reduce dose; reassess
   NO  ↓
Is this contraindication to continued use?
   YES → Stop drug; use [alternative]
   NO  → Symptomatic management; continue if benefit > risk
```

---

## High-Yield MCQ Trap Patterns for Pharmacology

These trap patterns appear with high frequency in pharmacology questions:

### 1. Drug Class vs Specific Agent Trap
- Boards name a drug class in the stem but the correct answer requires knowing a specific agent
- Example: "Start a calcium channel blocker" — wrong. "Start amlodipine" — right (if DHP preferred over non-DHP for HTN without arrhythmia)

### 2. Prodrug vs Active Drug Trap
- "Clopidogrel is a prodrug requiring CYP2C19 activation"
- Board trap: CYP2C19 poor metabolizers → reduced effect → use prasugrel instead

### 3. Same Class, Different Indication Trap
- Metoprolol (selective β1) vs Carvedilol (β1+β2+α) — same class, different roles
- Propranolol used for essential tremor/performance anxiety — not just hypertension

### 4. Correct Drug, Wrong Indication Trap
- Patient has asthma → beta-blockers contraindicated → wrong to give metoprolol even if HTN present

### 5. Monitoring Trap
- Right drug, but student forgets mandatory monitoring
- LFTs for statins? Not routinely, but baseline + if symptoms
- CBC for clozapine? YES — mandatory weekly then biweekly then monthly

### 6. Dosing Route/Timing Trap
- Bisphosphonates: take with water, remain upright for 30 min — exam tests this
- Levothyroxine: take 30-60 min before food — exam tests this

### 7. Drug Interaction Trap
- The correct answer depends on recognizing an interaction the student might not know
- Classic combos: MAOIs + anything serotonergic; warfarin + NSAIDs; lithium + NSAIDs/diuretics

---

## Drug Pearls — Extraction Heuristics

For each drug in the document, extract a pearl only if it meets one of:

**Class-defining pearl:** Something that is unique to this drug class and explains why it is preferred over alternatives. Example: "ACE inhibitors reduce proteinuria and slow CKD progression independent of blood pressure lowering — this is why they are preferred in diabetic nephropathy."

**Exam-anchor pearl:** A fact that boards specifically test because students confuse it with something else. Example: "ACE inhibitors cause hyperkalemia (blocks aldosterone → K⁺ retention) — students confuse this with the cough, which is bradykinin-mediated, not aldosterone-mediated."

**Paradox pearl:** A drug that does the opposite of what the student might expect. Example: "Beta-blockers initially worsen heart failure (negative inotropy) but improve long-term outcomes — they must be started at low doses in stable patients, never in acute decompensation."

**Absolute contraindication pearl:** A CI that causes patient harm and is therefore exam-perfect. Example: "Metformin in AKI/contrast exposure → lactic acidosis risk. Hold for 48h before contrast, resume after confirming renal function stable."

---

## Drug-Specific Atomic Fact Categories

When categorizing atomic facts for pharmacology documents, use these categories in addition to the standard set:

- **Mechanism** — Molecular target and downstream effect
- **Indication** — Approved uses (primary and secondary)
- **Pharmacology** — PK/PD: half-life, route, renal/hepatic dosing
- **Monitoring** — What to check and how often
- **Interaction** — Drug-drug and drug-food interactions
- **Contraindication** — When to avoid, absolute vs relative
- **Side Effect** — Adverse effects (board-relevant only)
- **Dosing** — Specific numeric doses or dose ranges

---

## Example Drug Atom Set (Furosemide)

```
ATOM: [Mechanism] Furosemide inhibits the Na-K-2Cl cotransporter in the thick ascending limb of the loop of Henle, blocking sodium reabsorption and producing a brisk diuresis.

ATOM: [Side Effect] Furosemide causes hypokalemia (K⁺ wasting), hypomagnesemia, and hypocalcemia via increased urinary cation loss — monitor electrolytes in patients on loop diuretics.

ATOM: [Side Effect] Furosemide is ototoxic, especially at high IV doses or when co-administered with aminoglycosides — the combination is synergistically toxic to cochlear hair cells.

ATOM: [Pharmacology] Furosemide requires tubular secretion via OAT transporters to reach its site of action in the tubular lumen — NSAIDs and probenecid compete for these transporters, reducing furosemide efficacy.

ATOM: [Contraindication] Furosemide is contraindicated in sulfonamide allergy (cross-reactivity possible, though rare) and in anuria (no urine to act on).

ATOM: [Monitoring] Monitor BMP (electrolytes, BUN, creatinine) and weight daily in patients receiving IV furosemide for acute decompensated heart failure.
```

---

## Drug Mind Map Color Convention (override)

For pharmacology-specific mind maps, use this color system instead of the standard clinical map colors:

| Color | Meaning |
|-------|---------|
| 🔵 Blue | Mechanism of action |
| 🟢 Green | Indications and benefits |
| 🔴 Red | Contraindications and absolute bans |
| 🟠 Orange | Adverse effects and cautions |
| 🟣 Purple | Drug interactions |
| ⚫ Gray | Monitoring requirements |
| 🟡 Yellow | Unique features / pearls |
