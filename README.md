# Skills

A collection of AI-powered tools designed to assist with medical education and exam preparation. Each skill is a self-contained package with its own scripts, references, and usage instructions.

## Skills

### [med-pdf-digest](./Skills/med-pdf-digest/)

A comprehensive medical PDF digestion skill that transforms clinical textbooks, guidelines, and review articles into multi-format study aids. It decomposes dense clinical content into six cognitive-memory-targeted output pillars:

| Pillar | Purpose | Cognitive Target |
|--------|---------|-----------------|
| Clinical Approach Flowcharts | Step-by-step diagnostic/treatment algorithms | Procedural memory |
| Mind Maps | Hierarchical knowledge organization | Structural memory |
| Clinical Pearls | High-yield nuggets, buzzwords, key associations | Associative memory |
| MCQ Traps | Common exam distractors, pitfalls | Defensive memory |
| Atomic Summaries | Bite-sized, interconnected knowledge units | Foundational memory |
| Simplified Yet Complete | Plain-language rewrite preserving every detail | Comprehension |

**Key features:**
- Multi-format output: PDF, HTML, Markdown, Anki/Quizlet flashcards
- Document type adaptation (textbook, guidelines, review articles, drug monographs, case studies)
- Language-agnostic input with medical terminology preservation
- Full pipeline automation via `pipeline.sh`

### [medmcq-generator](./Skills/medmcq-generator/)

A tool for generating high-quality, UWorld-style **Best of Five** multiple-choice questions for medical students. Builds rich clinical vignettes that demand multi-step clinical reasoning across all USMLE levels (Step 1, Step 2 CK, Step 3) and general med school exams.

**Key features:**
- Structured vignette framework: demographics → HPI → exam → labs → lead-in
- Five answer options with educationally valuable distractors
- Comprehensive explanations (bottom line, vignette analysis, distractor breakdown, educational objective, key concept)
- Multi-format output: PDF (2-column textbook layout), Markdown, JSON
- Difficulty calibration (Easy, Medium, Hard, Mixed)
- Compact mode for rapid review
- Interactive parameter elicitation for question generation