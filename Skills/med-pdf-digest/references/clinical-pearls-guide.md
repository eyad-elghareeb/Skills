# Clinical Pearls Extraction Guide

This file provides heuristics for identifying and extracting high-yield clinical pearls from medical documents. Not every fact is a pearl — a pearl must be both clinically important AND frequently tested.

---

## What Makes a Pearl?

A clinical pearl must satisfy at least TWO of these three criteria:

1. **High exam yield:** This fact has appeared or would appear on board-style exams
2. **Clinically actionable:** Knowing this fact changes management or prevents harm
3. **Memorable anchor:** This fact has a hook (buzzword, visual, acronym, paradox) that makes it stick

A fact that satisfies all three is a **top-tier pearl**. A fact that satisfies only one is just a fact — include it in atomic summaries, not in the pearls section.

---

## Pearl Categories

### Category 1: Buzzword Associations

The bread and butter of medical exams. A specific term → a specific diagnosis.

**Extraction pattern:** Look for terms that are in quotes, italicized, or otherwise highlighted in the text. These are almost always exam-relevant.

**Common buzzword types:**

| Buzzword Type | Example | Pearl |
|---------------|---------|-------|
| Pathognomonic finding | "Owl's eye inclusions" | CMV infection |
| Classic description | "Currant jelly sputum" | Klebsiella pneumoniae |
| Eponymous sign | "Murphy's sign" | Acute cholecystitis |
| Histological pattern | "Starry sky pattern" | Burkitt lymphoma |
| Radiological sign | "Air bronchogram" | Alveolar disease (not interstitial) |
| Lab finding | "M spike on protein electrophoresis" | Multiple myeloma |
| Gross appearance | "Nutmeg liver" | Chronic passive congestion (right heart failure) |

**How to format:**
```
PEARL: "Owl's eye inclusions" on biopsy
Buzzword: Owl's eye
Association: CMV infection
Context: Seen in immunocompromised patients with CMV; intranuclear inclusions in biopsy specimens
Exam Relevance: High — classic buzzword for CMV, tested to distinguish from other viral inclusions
```

---

### Category 2: Classic Presentations

The "textbook case" that every student should recognize instantly.

**Extraction pattern:** Look for phrases like "typically presents," "classic triad," "hallmark finding," "pathognomonic."

**Triads and pentads are especially high-yield:**

| Name | Components | Diagnosis |
|------|-----------|-----------|
| Virchow's triad | Stasis + Hypercoagulability + Endothelial injury | DVT/Thrombosis risk |
| Cushing's triad | Hypertension + Bradycardia + Irregular respirations | Elevated ICP |
| Beck's triad | Hypotension + JVD + Muffled heart sounds | Cardiac tamponade |
| Charcot's triad | Fever + RUQ pain + Jaundice | Ascending cholangitis |
| Reynolds' pentad | Charcot's triad + AMS + Hypotension | Suppurative cholangitis |
| Wiskott-Aldrich triad | Eczema + Thrombocytopenia + Recurrent infections | Wiskott-Aldrich syndrome |

**How to format:**
```
PEARL: Beck's Triad — the tamponade emergency
Buzzword: Beck's triad
Association: Hypotension + JVD + Muffled heart sounds ↔ Cardiac tamponade
Context: The triad is present in only ~30% of tamponade cases, but when present, it's diagnostic. Absence doesn't rule it out.
Exam Relevance: High — classic emergency medicine and cardiology board question
```

---

### Category 3: Don't-Miss Diagnoses

Conditions where delayed diagnosis leads to catastrophic outcomes. These are the diagnoses that keep emergency physicians up at night.

**Extraction pattern:** Look for phrases like "must not miss," "time-sensitive," "emergent," "immediate," "life-threatening if delayed."

**Common don't-miss categories:**
- Aortic dissection (in any severe chest/back pain)
- Ectopic pregnancy (in any woman of childbearing age with abdominal pain + positive pregnancy test)
- Meningococcal meningitis (in any fever + rash + AMS)
- Tension pneumothorax (in any trauma + absent breath sounds + tracheal deviation)
- Cauda equina syndrome (in any low back pain + saddle anesthesia + urinary retention)
- Testicular torsion (in any acute scrotal pain — time window is 6 hours)

**How to format:**
```
PEARL: Ectopic pregnancy — the don't-miss in women with abdominal pain
Buzzword: Positive pregnancy test + abdominal pain
Association: Reproductive-age woman + abdominal pain + positive hCG → rule out ectopic BEFORE discharging
Context: Any woman of childbearing age with abdominal pain needs a pregnancy test. A positive test with abdominal pain is ectopic until proven otherwise.
Exam Relevance: High — universally tested, and getting it wrong has real consequences
```

---

### Category 4: Paradoxical Findings

Findings that seem counterintuitive — exactly what examiners love to test.

**Extraction pattern:** Look for phrases like "paradoxically," "counterintuitively," "despite," "surprisingly," or situations where the expected relationship is reversed.

**Classic paradoxes:**
- Hypercalcemia in PTHrP-secreting tumors: PTH is LOW (suppressed), but calcium is HIGH
- SIADH: Volume status is euvolemic despite hyponatremia (not hypovolemic)
- Iron deficiency: TIBC is HIGH (not low, as you'd expect with low iron)
- Digoxin toxicity: Hyperkalemia (not hypokalemia) — because Na/K-ATPase is blocked
- Acute pancreatitis: Hypocalcemia (not hypercalcemia) — saponification of fat
- Pheochromocytoma: Orthostatic hypotension despite hypertension (volume depletion)

**How to format:**
```
PEARL: The iron deficiency paradox — TIBC goes UP
Buzzword: High TIBC in iron deficiency
Association: Iron deficiency → Low ferritin + Low serum iron + HIGH TIBC + Low transferrin saturation
Context: Counterintuitive because in most deficiency states, binding proteins decrease. In iron deficiency, the body increases transferrin (TIBC) to capture more iron.
Exam Relevance: High — the high TIBC is the single most tested lab finding in iron deficiency
```

---

### Category 5: Drug-Disease Associations

Specific relationships between drugs and their effects on specific conditions — both positive and negative.

**Extraction pattern:** Look for drug mentions paired with disease outcomes, especially in treatment sections.

**High-yield association types:**
- Drug causing a condition (ACEi → dry cough, Valproate → pancreatitis)
- Drug being the treatment of choice for a condition (N-acetylcysteine → acetaminophen overdose)
- Drug being contraindicated in a condition (Beta-blockers → asthma, Verapamil → HFrEF)
- Drug-disease interaction (NSAIDs → worsen heart failure, Metformin → avoid in severe renal failure)

**How to format:**
```
PEARL: ACE inhibitor cough → switch to ARB
Buzzword: ACEi dry cough
Association: ACE inhibitor → dry cough (10-20%) → switch to ARB (same benefit, no cough)
Context: The cough is due to bradykinin accumulation (ACE normally degrades bradykinin; ARBs don't affect bradykinin). Not dangerous, but intolerable for many patients.
Exam Relevance: High — boards test both the cause (bradykinin) and the solution (ARB)
```

---

### Category 6: Demographic Anchors

Diseases that classically appear in specific populations.

**Extraction pattern:** Look for phrases like "most common in," "typically affects," "predominantly seen in," with demographic qualifiers.

**Classic demographic-anchored pearls:**
- Young Asian female → Takayasu arteritis, SLE
- Elderly Caucasian male → Temporal arteritis (giant cell arteritis)
- Young African male → Sarcoidosis
- Mediterranean descent → Beta-thalassemia
- African descent → Sickle cell disease
- Ashkenazi Jewish → Tay-Sachs, Gaucher disease
- Male smoker >50 → Buerger disease, AAA
- Young female → SLE, rheumatoid arthritis, Graves disease

**How to format:**
```
PEARL: Young Asian female + pulseless upper limbs → Takayasu arteritis
Buzzword: Pulseless disease
Association: Young Asian female + absent radial pulses + aortic arch involvement → Takayasu arteritis
Context: Large vessel vasculitis of the aorta and its branches. Called "pulseless disease" because upper extremity pulses disappear.
Exam Relevance: High — the demographic anchor is the key to diagnosis
```

---

## Pearl Quality Checklist

Before finalizing each pearl, ask:

1. **Would this actually appear on a board exam?** If you can't imagine an examiner testing it, it's not a pearl.
2. **Is the association specific?** "Infection causes fever" is not a pearl. "EBV causes heterophile-positive infectious mononucleosis" is.
3. **Is the context necessary?** A pearl without context is just trivia. Add the "when this matters" piece.
4. **Is the buzzword real?** Don't invent buzzwords. Only use terms that appear in standard medical textbooks and board review materials.
5. **Is the exam relevance justified?** Don't mark everything as "High" — reserve it for pearls that are virtually guaranteed to appear.

## Red Flags: What NOT to Include as a Pearl

- **Overly broad statements:** "Hypertension is a risk factor for stroke" (too obvious)
- **Personal clinical anecdotes** not supported by the source text
- **Controversial associations** where evidence is disputed
- **Ultra-rare conditions** that are unlikely to appear on exams (unless the document specifically covers them)
- **Common knowledge** that every medical student knows (e.g., "insulin lowers blood glucose")
- **Facts not present in the source document** — pearls must be derived from the provided text
