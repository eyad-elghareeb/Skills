# Clinical Flowchart Patterns — Mermaid Templates

This file provides ready-to-adapt Mermaid flowchart templates for common clinical algorithm types. Use these as starting points and customize the nodes, branches, and labels to match the extracted content.

---

## Pattern 1: Diagnostic Workup Flow

Use when: The document describes how to investigate a presenting complaint or suspected diagnosis.

```mermaid
flowchart TD
    A[🏥 Presenting Complaint] --> B{Red Flags Present?}
    B -->|Yes| C[🚨 Urgent/Emergency Workup]
    B -->|No| D[📋 Initial Workup]
    C --> E[Targeted Imaging/Labs]
    D --> F[Basic Labs + Imaging]
    F --> G{Results Consistent with Diagnosis X?}
    G -->|Yes| H[✅ Confirm Diagnosis X]
    G -->|No| I{Alternative Diagnosis Suspected?}
    I -->|Yes| J[🔄 Redirect Workup]
    I -->|No| K[🔍 Additional Investigation]
    K --> G
    E --> L{Diagnosis Confirmed?}
    L -->|Yes| H
    L -->|No| M[Consider Rare Causes]
    M --> E

    style C fill:#ff6b6b,color:#fff
    style H fill:#51cf66,color:#fff
    style B fill:#ffd43b,color:#333
    style G fill:#ffd43b,color:#333
    style I fill:#ffd43b,color:#333
    style L fill:#ffd43b,color:#333
```

**Adaptation guide:**
- Replace "Presenting Complaint" with the specific complaint (e.g., "Chest Pain," "Dyspnea")
- Add specific red flags from the text
- Replace "Diagnosis X" with the suspected condition
- Add specific labs/imaging mentioned in the document
- Add branch points for differential diagnosis paths

---

## Pattern 2: Treatment Escalation Flow

Use when: The document describes a step-wise treatment approach (first-line → second-line → etc.).

```mermaid
flowchart TD
    A[📝 Confirm Diagnosis] --> B[💊 First-Line Treatment]
    B --> C{Response?}
    C -->|Adequate| D[✅ Continue + Monitor]
    C -->|Inadequate| E{Contraindications to Step-Up?}
    E -->|No| F[💊 Second-Line Treatment]
    E -->|Yes| G[⚡ Consider Alternative Approach]
    F --> H{Response?}
    H -->|Adequate| D
    H -->|Inadequate| I[💊 Third-Line / Specialist Referral]
    I --> J{Response?}
    J -->|Adequate| D
    J -->|Inadequate| K[🔬 Consider Clinical Trial / Advanced Therapy]

    D --> L[📅 Follow-Up Schedule]
    L --> M{Stable?}
    M -->|Yes| N[✅ Continue Management]
    M -->|No| A

    style A fill:#74c0fc,color:#fff
    style D fill:#51cf66,color:#fff
    style G fill:#ff6b6b,color:#fff
    style K fill:#cc5de8,color:#fff
```

**Adaptation guide:**
- Replace "First-Line" with specific drug/therapy names
- Add dose information where relevant
- Include monitoring parameters for each step
- Add specific contraindications that redirect the algorithm
- Include timeframe expectations ("reassess in 2-4 weeks")

---

## Pattern 3: Emergency Management Flow

Use when: The document describes acute/emergency management (ACLS, sepsis, status epilepticus, etc.).

```mermaid
flowchart TD
    A[🚨 EMERGENCY PRESENTATION] --> B[ABC Assessment]
    B --> C[Airway]
    C --> D{Patent?}
    D -->|No| E[Intubate / Secure Airway]
    D -->|Yes| F[Breathing]
    E --> F
    F --> G{Adequate?}
    G -->|No| H[O2 / Ventilate]
    G -->|Yes| I[Circulation]
    H --> I
    I --> J[IV Access + Fluid Resuscitation]
    J --> K{Hemodynamically Stable?}
    K -->|No| L[Vasopressors / Inotropes]
    K -->|Yes| M[Targeted Emergency Treatment]
    L --> M
    M --> N{Improving?}
    N -->|Yes| O[ICU Admission + Monitoring]
    N -->|No| P[Escalate Intervention]
    P --> N

    style A fill:#ff0000,color:#fff
    style E fill:#ff6b6b,color:#fff
    style H fill:#ff6b6b,color:#fff
    style L fill:#ff6b6b,color:#fff
    style O fill:#51cf66,color:#fff
```

**Adaptation guide:**
- Add specific emergency interventions (e.g., "Defibrillate VF/VT" for cardiac arrest)
- Include drug names and doses (e.g., "Epinephrine 1mg IV q3-5min")
- Add time targets (e.g., "within 10 minutes")
- Include "DO NOT" actions as red-flagged nodes

---

## Pattern 4: Screening Algorithm Flow

Use when: The document describes who to screen, when, and with what test.

```mermaid
flowchart TD
    A[👤 Patient Presentation] --> B{Age ≥ Screening Threshold?}
    B -->|No| C[❌ No Screening Indicated]
    B -->|Yes| D{Risk Factors Present?}
    D -->|Average Risk| E[📋 Standard Screening Test]
    D -->|High Risk| F[🔬 Enhanced Screening Protocol]
    E --> G{Result?}
    F --> H{Result?}
    G -->|Negative| I[✅ Repeat at Standard Interval]
    G -->|Positive| J[📝 Diagnostic Confirmation]
    G -->|Indeterminate| K[🔄 Repeat or Alternative Test]
    H -->|Negative| L[✅ Repeat at Shorter Interval]
    H -->|Positive| J
    H -->|Indeterminate| K
    J --> M{Diagnosis Confirmed?}
    M -->|Yes| N[💊 Treatment Pathway]
    M -->|No| O[🔄 Re-evaluate / Surveillance]

    style C fill:#dee2e6,color:#333
    style I fill:#51cf66,color:#fff
    style N fill:#74c0fc,color:#fff
```

**Adaptation guide:**
- Add specific age thresholds from the guideline
- List specific risk factors that change the algorithm
- Name the screening test (mammography, colonoscopy, etc.)
- Include recommended intervals (annually, every 2 years, etc.)

---

## Pattern 5: Differential Diagnosis Tree

Use when: The document presents a differential diagnosis and helps distinguish between conditions.

```mermaid
flowchart TD
    A[🔍 Presenting Feature] --> B{Key Discriminator 1}
    B -->|Option A| C{Discriminator 2a}
    B -->|Option B| D{Discriminator 2b}
    B -->|Option C| E{Discriminator 2c}

    C -->|Finding X| F[Diagnosis 1]
    C -->|Finding Y| G[Diagnosis 2]
    D -->|Finding Z| H[Diagnosis 3]
    D -->|Finding W| I[Diagnosis 4]
    E -->|Finding V| J[Diagnosis 5]
    E -->|Finding U| K[Diagnosis 6]

    F --> L[🎯 Key Distinguishing Features]
    G --> M[🎯 Key Distinguishing Features]
    H --> N[🎯 Key Distinguishing Features]
    I --> O[🎯 Key Distinguishing Features]
    J --> P[🎯 Key Distinguishing Features]
    K --> Q[🎯 Key Distinguishing Features]

    style A fill:#74c0fc,color:#fff
    style F fill:#51cf66,color:#fff
    style G fill:#51cf66,color:#fff
    style H fill:#51cf66,color:#fff
    style I fill:#51cf66,color:#fff
    style J fill:#51cf66,color:#fff
    style K fill:#51cf66,color:#fff
```

**Adaptation guide:**
- Replace "Presenting Feature" with the specific symptom/finding
- Use discriminators from the text (e.g., "Acute vs Chronic," "Painful vs Painless")
- Add specific distinguishing features at each leaf
- Consider adding a comparison table as a companion

---

## General Flowchart Style Rules

1. **Node shapes:**
   - `[]` Rectangle = Action/Step
   - `{}` Diamond = Decision/Question
   - `([ ]) Rounded = Start/End
   - `[[ ]] Subroutine = Sub-process (link to another flowchart)

2. **Colors:**
   - 🔴 Red (#ff6b6b): Emergency, danger, don't-miss
   - 🟡 Yellow (#ffd43b): Decision points
   - 🟢 Green (#51cf66): Positive outcome, confirmed
   - 🔵 Blue (#74c0fc): Process, investigation
   - 🟣 Purple (#cc5de8): Specialist/referral
   - ⚪ Gray (#dee2e6): Not indicated, ruled out

3. **Emojis:** Use sparingly for visual anchoring — 🚨 emergency, 💊 drug, 🔬 test, ✅ confirmed, ❌ ruled out, 📋 assessment

4. **Flow direction:**
   - `TD` (top-down) for sequential processes
   - `LR` (left-right) for comparison/parallel paths
   - Use `---` for same-level connections, `-->` for directional flow

5. **Keep it readable:**
   - Maximum 15 nodes per flowchart — if more, split into sub-flowcharts
   - Keep node labels under 30 characters
   - Use subgraphs to group related steps
