# MCQ Trap Archetype Catalog

This file catalogs the common trap patterns that medical examiners use when constructing multiple-choice questions. Use this as a reference when extracting MCQ traps from clinical documents.

---

## Category 1: The "EXCEPT" Trap

**Pattern:** "All of the following are features of X EXCEPT:" or "Which of the following is NOT a risk factor for X?"

**Why it works:** Students are trained to find the "right" answer, so they instinctively select a correct statement instead of the one wrong statement. The cognitive switch from "find correct" to "find incorrect" trips people up.

**Common variants:**
- "All of the following are true EXCEPT"
- "Which finding is LEAST likely"
- "Which is NOT indicated"
- "Each of the following is consistent EXCEPT"

**How to extract from text:** Look for lists of features, risk factors, symptoms, or findings. The trap is in the item that *doesn't belong* — which examiners know students will overlook because it sounds similar to items that *do* belong.

**Example extraction:**
```
Source text: "Risk factors for DVT include: prolonged immobility, recent surgery, oral contraceptive use, factor V Leiden, and pregnancy."

Trap: "All of the following are risk factors for DVT EXCEPT:
A) Prolonged immobility
B) Recent surgery
C) Factor V Leiden
D) Low-dose aspirin use ← TRAP (aspirin is protective, not a risk factor)
E) Oral contraceptive use

Why tricky: Students see "aspirin use" and think "medication use = risk factor" without distinguishing which medications increase vs decrease risk."
```

---

## Category 2: The Near-Miss Distractor

**Pattern:** Two answer choices differ by a single critical word, and the wrong one sounds almost as plausible.

**Why it works:** Partial matching creates false confidence. The student recognizes most of the answer and fills in the gap with the wrong detail.

**Common word-pairs that create near-misses:**
- Sensitive vs Specific
- Common vs Characteristic
- Associated vs Causal
- Necessary vs Sufficient
- Primary vs Secondary
- Acute vs Chronic
- Unilateral vs Bilateral
- Focal vs Diffuse
- Reversible vs Irreversible
- Sympathetic vs Parasympathetic
- Systolic vs Diastolic
- Arterial vs Venous
- Sensory vs Motor
- Afferent vs Efferent

**Example extraction:**
```
Source text: "B-type natriuretic peptide (BNP) is a sensitive marker for heart failure but is not specific — it can be elevated in pulmonary hypertension, renal failure, and PE."

Trap: "Regarding BNP in heart failure:
A) It is a specific marker for HF ← TRAP (sensitive, not specific)
B) It is a sensitive marker for HF ← CORRECT

Why tricky: Students conflate 'sensitive' and 'specific' — both sound like 'good test' but have very different meanings. BNP will catch most HF cases (sensitive) but also flags non-HF causes (not specific)."
```

---

## Category 3: The Demographic Trap

**Pattern:** A classic presentation but in an unexpected demographic, OR a disease that presents differently in a specific demographic.

**Why it works:** Students learn the "classic" presentation (often based on the most common demographic) and forget that the same disease can look different — or that a different disease is more likely — in other populations.

**Key demographic axes examiners exploit:**
- Age (pediatric vs adult vs elderly)
- Sex (male vs female — especially autoimmune diseases, cardiovascular)
- Pregnancy (many rules change)
- Ethnicity (sickle cell in African descent, thalassemia in Mediterranean)
- Immunocompromised status (opportunistic infections)

**Example extraction:**
```
Source text: "In women, the presentation of acute MI often includes atypical symptoms such as fatigue, nausea, and back pain rather than classic crushing chest pain."

Trap: "A 62-year-old woman presents with fatigue, nausea, and back pain. The LEAST likely diagnosis is:
A) Acute MI ← TRAP (student thinks 'no chest pain = not MI')
B) GERD
C) Musculoskeletal pain

Why tricky: Students anchor on 'chest pain' as mandatory for MI. Women commonly present atypically."
```

---

## Category 4: "Most Common" vs "Most Lethal"

**Pattern:** Conflating frequency with severity. The most common cause of X is not necessarily the most dangerous cause of X.

**Why it works:** Students study the most common causes (because they're tested most) and forget that boards also test the most dangerous causes — especially when they're *not* the most common.

**Classic examples:**
- Most common cause of viral meningitis: Enterovirus | Most lethal: HSV
- Most common cause of pneumonia: S. pneumoniae | Most lethal in ICU: Pseudomonas, MRSA
- Most common heart valve disease: Mitral valve prolapse | Most lethal: Aortic stenosis
- Most common liver tumor: Hemangioma (benign) | Most lethal: HCC

**How to extract:** Whenever the text mentions "most common," immediately look for "most lethal/deadly/important to not miss" in the same topic. The trap is in the gap between them.

---

## Category 5: The First-Step Trap

**Pattern:** Asking for the FIRST action or FIRST test, where the obvious answer is a later (or more definitive) step.

**Why it works:** Students think of the "best" test or the "gold standard" test, but the question asks for the FIRST. In clinical medicine, the first step is often cheaper, faster, or stabilizing rather than diagnostic.

**Common first-step traps:**
- "First step in PE" → Clinical prediction score (Wells), NOT CT angiogram
- "First step in chest pain" → ECG, NOT troponin (ECG is instant, troponin takes time)
- "First step in acute GI bleed" → ABC + volume resuscitation, NOT endoscopy
- "First step in suspected meningitis" → Blood cultures + empiric antibiotics BEFORE LP (don't delay antibiotics for LP)
- "First step in anaphylaxis" → IM epinephrine, NOT antihistamines or steroids

**How to extract:** When the text describes a sequence, identify what's done FIRST vs what's most definitive. The trap is always in the gap between first and definitive.

---

## Category 6: The Drug Trap

**Pattern:** Exploiting knowledge of drug classes, mechanisms, or side effects.

**Sub-types:**
- **Right drug, wrong indication:** The drug exists and is real, but it's not used for the stated purpose
- **Right class, wrong agent:** A drug from the right class is listed, but it's not the specific agent indicated
- **Mechanism trap:** The drug's mechanism is described incorrectly (especially with similar-sounding mechanisms)
- **Side effect swap:** Drug A's famous side effect is attributed to Drug B
- **Contraindication confusion:** A contraindication for one drug is applied to its classmate

**Common drug trap pairs:**
- ACE inhibitors (dry cough) vs ARBs (no dry cough) — examiners test if you know ARBs were designed to avoid the ACEi cough
- Metformin (lactic acidosis in renal failure) vs Glipizide (hypoglycemia) — both are oral hypoglycemics with very different danger profiles
- Heparin (HIT) vs Warfarin (skin necrosis) — both anticoagulants, very different unique side effects
- Amiodarone (pulmonary fibrosis, thyroid dysfunction) vs other antiarrhythmics — amiodarone's side effect profile is uniquely massive

**How to extract:** For every drug mentioned in the text, identify its unique side effect or contraindication. The trap is in confusing one drug's unique feature with another drug in the same class.

---

## Category 7: The "Always/Never" Trap

**Pattern:** Answer options contain absolute words like "always," "never," "all," "none," "must," "impossible." In medicine, these are almost always wrong.

**Why it works:** Students who know the general rule forget that medicine has exceptions. The distractor with "always/never" sounds authoritative and confident.

**Common "always/never" trap constructions:**
- "Patients with X always present with Y" (wrong — there are atypical presentations)
- "Drug X should never be used in condition Y" (wrong — there may be specific indications)
- "All patients with finding X must undergo test Y" (wrong — may depend on clinical context)

**How to extract:** Look for statements in the text that describe general rules AND their exceptions. The trap is in the option that states the rule without acknowledging the exception.

---

## Category 8: The Overstatement Trap

**Pattern:** A true statement is broadened slightly beyond what the evidence supports.

**Why it works:** The student recognizes the true core of the statement and doesn't notice the extra scope.

**Examples:**
- True: "ACE inhibitors reduce mortality in HFrEF" → Overstatement trap: "ACE inhibitors reduce mortality in all heart failure" (wrong — benefit in HFpEF is not established)
- True: "Metformin is first-line in Type 2 DM" → Overstatement trap: "Metformin is first-line in all diabetes" (wrong — not Type 1)
- True: "Statins reduce cardiovascular events in secondary prevention" → Overstatement trap: "Statins reduce all-cause mortality in primary prevention" (wrong — evidence is weaker for primary prevention)

**How to extract:** When the text describes a benefit or indication with specific qualifiers (population, condition type, severity), the trap is in removing those qualifiers.

---

## Category 9: The Numerical Trap

**Pattern:** Close-but-wrong numbers used as distractors. Examiners know students remember "a number" but not exactly which one.

**Common numerical trap categories:**
- Diagnostic cutoffs (FPG: 126 mg/dL, not 120 or 130)
- Drug doses (the usual vs the loading dose)
- Sensitivity/specificity values (98% vs 95% — both sound high, but exams test the exact number)
- Time intervals (window for tPA: 4.5 hours, not 3 or 6)
- Lab value ranges (correct reference range vs a shifted number)

**How to extract:** Every number in the text is a potential trap. Capture exact values and note what they're commonly confused with.

---

## Category 10: The "Next Best Step" Trap

**Pattern:** "What is the next best step in management?" — The answer depends on whether the patient is stable or unstable, and examiners test if you check stability first.

**The golden rule:**
- **Unstable patient:** Stabilize first (ABCs, IV, O2, monitor) → then diagnose
- **Stable patient:** Diagnose first → then treat

**Why it works:** Students jump to the diagnostic or therapeutic step that makes intellectual sense, without first confirming the patient is stable enough for that step.

**Common traps:**
- Patient with chest pain + hypotension → Next step is NOT stress test, it's emergent management
- Patient with GI bleed + tachycardia → Next step is NOT endoscopy, it's volume resuscitation
- Patient with suspected meningitis + septic shock → Next step is NOT LP, it's antibiotics + stabilize

**How to extract:** Whenever the text describes a clinical scenario with a management sequence, identify the stability checkpoint. The trap is in skipping it.

---

## Trap Extraction Priority

When extracting traps from a document, prioritize in this order:

1. **Drug traps** — Most frequently tested in pharmacology-heavy documents
2. **First-step traps** — Universal across all clinical topics
3. **Near-miss distractors** — Especially in differential diagnosis sections
4. **Numerical traps** — Especially in guidelines and pharmacology
5. **"Except" traps** — Common in list-heavy content
6. **Next-best-step traps** — Common in emergency/critical care content
7. **Demographic traps** — Common in internal medicine
8. **"Most common" vs "most lethal"** — Common in epidemiology-heavy sections
9. **Overstatement traps** — Common in guideline content
10. **"Always/never" traps** — Common in textbook content

Each document will have a different trap profile. Don't force traps where they don't naturally exist — manufactured traps are worse than no traps.
