# Design System — Med PDF Digest
## Impeccable-Grade Visual Language for All Digest Outputs

Read this file before generating any flowchart, mind map, HTML output, or PDF layout.
It is the single source of truth for every visual decision in the digest pipeline.

---

## 1. Color System (OKLCH-based)

All colors are defined in OKLCH for perceptual uniformity. Use CSS custom properties throughout.
Never use raw hex values in component code — always reference a token.

### Semantic Palette

```css
:root {
  /* ── Brand / Surface ─────────────────────────────── */
  --color-bg:          oklch(98% 0.005 250);   /* Near-white, slight blue-cool */
  --color-surface:     oklch(100% 0 0);        /* Pure white cards */
  --color-surface-dim: oklch(96% 0.008 250);   /* Alternate row / panel */
  --color-border:      oklch(88% 0.010 250);   /* Subtle dividers */

  /* ── Ink / Text ──────────────────────────────────── */
  --color-ink:         oklch(18% 0.015 250);   /* Primary text — rich near-black */
  --color-ink-muted:   oklch(42% 0.015 250);   /* Labels, captions — verified 4.6:1 on bg */
  --color-ink-ghost:   oklch(62% 0.010 250);   /* Placeholder — 4.5:1 minimum */

  /* ── Section Accent Hues ─────────────────────────── */
  /* Each pillar owns one hue. Shared lightness (55%) & chroma (0.19) = visually equal. */
  --hue-flowchart:  220;   /* Blue */
  --hue-mindmap:    285;   /* Violet */
  --hue-pearl:       45;   /* Amber */
  --hue-trap:         15;  /* Red-Orange */
  --hue-atom:        155;  /* Teal-Green */
  --hue-simplified:  195;  /* Cyan */

  --color-flowchart: oklch(55% 0.19 var(--hue-flowchart));
  --color-mindmap:   oklch(55% 0.19 var(--hue-mindmap));
  --color-pearl:     oklch(55% 0.19 var(--hue-pearl));
  --color-trap:      oklch(55% 0.19 var(--hue-trap));
  --color-atom:      oklch(55% 0.19 var(--hue-atom));
  --color-simplified:oklch(55% 0.19 var(--hue-simplified));

  /* Tinted backgrounds (for cards): L=97%, C=0.025 — barely-there tint */
  --bg-flowchart: oklch(97% 0.025 var(--hue-flowchart));
  --bg-mindmap:   oklch(97% 0.025 var(--hue-mindmap));
  --bg-pearl:     oklch(97% 0.025 var(--hue-pearl));
  --bg-trap:      oklch(97% 0.025 var(--hue-trap));
  --bg-atom:      oklch(97% 0.025 var(--hue-atom));
  --bg-simplified:oklch(97% 0.025 var(--hue-simplified));

  /* ── Clinical Semantic Colors ────────────────────── */
  /* Used INSIDE flowcharts and mind map nodes — not in UI chrome */
  --clinical-emergency: oklch(52% 0.23 22);    /* Red — don't-miss, danger */
  --clinical-decision:  oklch(80% 0.19 90);    /* Amber-yellow — decision diamonds */
  --clinical-positive:  oklch(58% 0.20 145);   /* Green — confirmed, resolved */
  --clinical-process:   oklch(58% 0.18 225);   /* Blue — investigation, action */
  --clinical-referral:  oklch(55% 0.20 290);   /* Purple — specialist, referral */
  --clinical-excluded:  oklch(70% 0.04 250);   /* Gray — ruled out, not indicated */

  /* ── Clinical Semantic (light tints for node fills) */
  --clinical-emergency-bg: oklch(96% 0.05 22);
  --clinical-decision-bg:  oklch(98% 0.05 90);
  --clinical-positive-bg:  oklch(96% 0.05 145);
  --clinical-process-bg:   oklch(96% 0.05 225);
  --clinical-referral-bg:  oklch(96% 0.05 290);
  --clinical-excluded-bg:  oklch(96% 0.02 250);

  /* ── Elevation / Shadow ──────────────────────────── */
  --shadow-xs:   0 1px 2px  oklch(0% 0 0 / 0.06);
  --shadow-sm:   0 2px 6px  oklch(0% 0 0 / 0.09);
  --shadow-md:   0 4px 16px oklch(0% 0 0 / 0.10);
  --shadow-lg:   0 8px 32px oklch(0% 0 0 / 0.12);

  /* ── Radius ───────────────────────────────────────── */
  --radius-sm:  6px;
  --radius-md:  10px;
  --radius-lg:  16px;
  --radius-xl:  24px;
}
```

**Contrast mandate:** Before emitting any text color, mentally check:
- Body text on surface: must be ≥ 4.5:1 (`--color-ink` on `--color-surface` is ~18:1 — pass)
- Muted text: ≥ 4.5:1 (`--color-ink-muted` at L=42% — verified pass)
- Large heading on tinted bg: ≥ 3:1
- Never use gray text on a colored background — use a darker shade of that hue instead.

---

## 2. Typography Scale

```css
:root {
  /* Typeface stack — one family, three roles */
  --font-body:    'Inter', 'Segoe UI', system-ui, sans-serif;
  --font-display: 'Inter', 'Segoe UI', system-ui, sans-serif;   /* Use weight to differentiate */
  --font-mono:    'JetBrains Mono', 'Cascadia Code', 'Fira Code', monospace;

  /* Scale — 1.25 ratio (Major Third) */
  --text-xs:   0.64rem;   /* 10.2px — badges, fine print */
  --text-sm:   0.80rem;   /* 12.8px — captions, labels */
  --text-base: 1.00rem;   /* 16px   — body */
  --text-md:   1.25rem;   /* 20px   — card title, pillar sub-heading */
  --text-lg:   1.56rem;   /* 25px   — section heading (h2) */
  --text-xl:   1.95rem;   /* 31px   — page title (h1) */
  --text-2xl:  2.44rem;   /* 39px   — cover display */

  /* Weight */
  --weight-regular: 400;
  --weight-medium:  500;
  --weight-semibold:600;
  --weight-bold:    700;

  /* Leading */
  --leading-tight:  1.20;  /* Headings only */
  --leading-snug:   1.40;  /* Cards, short runs */
  --leading-body:   1.65;  /* Body paragraphs */

  /* Measure */
  --measure-body: 68ch;    /* Hard cap on body line length */
}
```

**Typography rules (from impeccable):**
- Hierarchy through scale + weight contrast, never scale alone.
- No all-caps body copy. Labels ≤ 4 words in uppercase only.
- `text-wrap: balance` on h1–h3. `text-wrap: pretty` on prose.
- Do not use more than 2 weights for one section — pick regular + bold, or medium + semibold.
- Inter at 400 for body, 600 for section headings, 700 for pillar titles.

---

## 3. Spacing Scale

```css
:root {
  --space-1:  4px;
  --space-2:  8px;
  --space-3:  12px;
  --space-4:  16px;
  --space-5:  24px;
  --space-6:  32px;
  --space-7:  48px;
  --space-8:  64px;
  --space-9:  96px;
  --space-10: 128px;
}
```

**Spacing rhythm rules:**
- Between pillars: `--space-9` (96px).
- Between section heading and first card: `--space-5` (24px).
- Between consecutive cards: `--space-3` (12px).
- Padding inside cards: `--space-4` vertical / `--space-5` horizontal.
- Page margins (HTML): `clamp(16px, 5vw, 80px)` left/right; max-width 900px centered.

---

## 4. Layout Principles

- **Single column for the digest body.** No two-up card grids — medical content is sequential.
- **Sticky sidebar TOC** on desktop (≥ 900px): 220px wide, `position: sticky; top: 2rem`. Collapses to horizontal scrollable pill-nav on mobile.
- **Flowchart images:** Full bleed within the content column. `width: 100%; max-width: 720px; margin: 0 auto; display: block`.
- **Mind map images:** Same as flowchart.
- **Cards use `display: grid; grid-template-columns: 4px 1fr`** — the accent strip is a grid item, not a border. This avoids the "border-left trick" that bleeds at rounded corners.
- **Nested cards are always wrong.** Never put a card inside a card.
- Z-index scale: `--z-toc: 10; --z-toast: 80; --z-modal: 100`.

---

## 5. Flowchart Visual Language

### Node Vocabulary

| Node Type           | Mermaid Syntax      | Fill                       | Stroke                     | Use For |
|---------------------|---------------------|----------------------------|----------------------------|---------|
| Trigger / Start     | `([text])`          | `--clinical-process-bg`    | `--clinical-process`       | Entry point, presenting complaint |
| Decision            | `{text}`            | `--clinical-decision-bg`   | `--clinical-decision`      | Yes/No branches, criteria gates |
| Action / Process    | `[text]`            | `--color-surface`          | `--color-border`           | Investigations, treatments |
| Emergency           | `[[text]]`          | `--clinical-emergency-bg`  | `--clinical-emergency`     | Don't-miss, activate emergency |
| Positive Outcome    | `([text])`          | `--clinical-positive-bg`   | `--clinical-positive`      | Confirmed diagnosis, goals met |
| Referral            | `[/text/]`          | `--clinical-referral-bg`   | `--clinical-referral`      | Specialist, escalation |
| Ruled Out           | `[text]`            | `--clinical-excluded-bg`   | `--clinical-excluded`      | Condition excluded |

### Mermaid Stylesheet Block

Every generated flowchart must begin with this classDef block:

```
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#eef4ff',
  'primaryBorderColor': '#4d8ef0',
  'primaryTextColor': '#111827',
  'lineColor': '#6b7280',
  'fontSize': '14px',
  'fontFamily': 'Inter, Segoe UI, system-ui, sans-serif'
}}}%%
flowchart TD
  classDef trigger   fill:#eef4ff,stroke:#4d8ef0,color:#111827,font-weight:600
  classDef decision  fill:#fffbeb,stroke:#d97706,color:#111827,font-weight:600
  classDef action    fill:#ffffff,stroke:#d1d5db,color:#111827
  classDef emergency fill:#fef2f2,stroke:#dc2626,color:#7f1d1d,font-weight:700
  classDef positive  fill:#f0fdf4,stroke:#16a34a,color:#14532d
  classDef referral  fill:#faf5ff,stroke:#7c3aed,color:#4c1d95
  classDef excluded  fill:#f9fafb,stroke:#9ca3af,color:#6b7280,font-style:italic
```

### Flowchart Rules
- **Max 15 nodes per flowchart.** If more are needed, split into linked sub-flowcharts and name them `[topic]_overview`, `[topic]_detail_A`, etc.
- **Every flowchart must have a title** as an annotation comment `%% Title: ...` at the top.
- **Label edges** at every Yes/No branch: `-->|Yes|` and `-->|No|`.
- **Cap label length** at 8 words per edge; 12 words per node.
- **Emergency branches** always terminate in an emergency-styled node. Never leave a "danger" branch unresolved.
- **Flowchart is horizontal-first if > 8 nodes** (`flowchart LR`), vertical if ≤ 8 (`flowchart TD`).

---

## 6. Mind Map Visual Language

### Structure Hierarchy

```
Central Node (L0): The disease / topic — large, bold, brand accent color
  ├── Branch (L1): Major category — medium, colored by category role
  │     ├── Sub-branch (L2): Sub-category — smaller, lighter shade
  │     │     └── Leaf (L3): Specific fact — smallest, text only, no fill
  │     └── Sub-branch (L2): ...
  └── Branch (L1): ...
```

**Maximum depth: Level 3.** If a Level 4 is needed, create a separate named sub-map (`mindmap_[topic]_[L1-branch-name].png`).

### Mind Map Color Coding (consistent per digest)

| Branch Role           | Hue   | L0 Fill             | L1 Fill              | L2 Text Only |
|-----------------------|-------|---------------------|----------------------|--------------|
| Etiology / Causes     | Red   | `#fef2f2`           | `#fee2e2`            | `#7f1d1d`    |
| Pathophysiology       | Orange| `#fff7ed`           | `#fed7aa`            | `#7c2d12`    |
| Diagnosis / Workup    | Blue  | `#eff6ff`           | `#dbeafe`            | `#1e3a5f`    |
| Treatment / Mgmt      | Green | `#f0fdf4`           | `#dcfce7`            | `#14532d`    |
| Complications         | Purple| `#faf5ff`           | `#ede9fe`            | `#4c1d95`    |
| Classification / Types| Violet| `#f5f3ff`           | `#ddd6fe`            | `#3b0764`    |
| Pharmacology          | Teal  | `#f0fdfa`           | `#ccfbf1`            | `#134e4a`    |
| Epidemiology / RF     | Gray  | `#f9fafb`           | `#f3f4f6`            | `#1f2937`    |

### Mind Map Generation (CSS + Playwright)

When generating mind maps via CSS+Playwright, apply these rules:

```css
.mindmap-root {
  font-family: 'Inter', system-ui, sans-serif;
  padding: 60px;
  background: oklch(98% 0.005 250);
}

.node-central {
  background: oklch(55% 0.19 250);
  color: white;
  border-radius: 16px;
  padding: 16px 28px;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.02em;
  box-shadow: 0 4px 16px oklch(0% 0 0 / 0.15);
}

.node-l1 {
  border-radius: 10px;
  padding: 10px 18px;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 2px 6px oklch(0% 0 0 / 0.09);
}

.node-l2 {
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 500;
  background: transparent;
  border: 1.5px solid currentColor;
}

.node-l3 {
  font-size: 11px;
  font-weight: 400;
  color: var(--color-ink-muted);
  padding: 4px 8px;
  background: none;
  border: none;
}

/* Connector lines */
.connector {
  stroke-width: 2px;
  stroke-linecap: round;
  opacity: 0.5;
}
```

### Mind Map Anti-Patterns (ban list)
- No more than 7 L1 branches on a single map — split if needed.
- No text overlapping connector lines.
- No all-caps node labels.
- No more than 5 L2 items per L1 branch — create a sub-map.
- Do not use color for decoration — every color carries semantic meaning from the table above.
- Never repeat the same color for two different category roles in one digest.

---

## 7. HTML Output: Full Design Specification

### Fonts (load from Google Fonts CDN)
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```
Fallback: `system-ui, -apple-system, sans-serif`.

### Page Shell
```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: var(--font-body);
  font-size: var(--text-base);
  line-height: var(--leading-body);
  color: var(--color-ink);
  background: var(--color-bg);
}

.layout {
  display: grid;
  grid-template-columns: 220px 1fr;
  grid-template-areas: "toc main";
  max-width: 1100px;
  margin: 0 auto;
  gap: var(--space-7);
  padding: var(--space-6) clamp(16px, 5vw, 48px);
}

@media (max-width: 860px) {
  .layout { grid-template-columns: 1fr; grid-template-areas: "toc" "main"; }
}
```

### Cover Header
```css
.cover {
  background: linear-gradient(135deg,
    oklch(22% 0.07 250) 0%,
    oklch(30% 0.12 270) 60%,
    oklch(35% 0.18 290) 100%
  );
  color: white;
  padding: var(--space-9) clamp(24px, 6vw, 80px);
  text-align: center;
  border-radius: 0 0 var(--radius-xl) var(--radius-xl);
  margin-bottom: var(--space-7);
}

.cover-specialty {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  letter-spacing: 0.10em;
  text-transform: uppercase;
  color: oklch(80% 0.15 200);   /* Teal label — readable on dark bg */
  margin-bottom: var(--space-3);
}

.cover-title {
  font-size: clamp(1.8rem, 4vw, 2.8rem);
  font-weight: var(--weight-bold);
  letter-spacing: -0.03em;
  line-height: var(--leading-tight);
  text-wrap: balance;
  margin-bottom: var(--space-4);
}

.cover-subtitle {
  font-size: var(--text-md);
  color: oklch(88% 0.04 250);
  font-weight: var(--weight-regular);
}

.cover-meta {
  margin-top: var(--space-5);
  font-size: var(--text-sm);
  color: oklch(72% 0.04 250);
  display: flex;
  gap: var(--space-5);
  justify-content: center;
  flex-wrap: wrap;
}

.pillar-badges {
  display: flex;
  gap: var(--space-2);
  justify-content: center;
  flex-wrap: wrap;
  margin-top: var(--space-4);
}

.pillar-badge {
  background: oklch(100% 0 0 / 0.12);
  border: 1px solid oklch(100% 0 0 / 0.20);
  color: white;
  padding: var(--space-1) var(--space-3);
  border-radius: 100px;
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  letter-spacing: 0.04em;
}
```

### Sticky TOC
```css
.toc {
  grid-area: toc;
  position: sticky;
  top: var(--space-5);
  align-self: start;
  height: calc(100vh - var(--space-5) * 2);
  overflow-y: auto;
  padding-right: var(--space-4);
  scrollbar-width: thin;
}

.toc-title {
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.10em;
  color: var(--color-ink-muted);
  margin-bottom: var(--space-3);
}

.toc-link {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  color: var(--color-ink-muted);
  text-decoration: none;
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  transition: background 180ms ease-out, color 180ms ease-out;
  margin-bottom: 2px;
}

.toc-link:hover {
  background: var(--color-surface-dim);
  color: var(--color-ink);
}

.toc-link.active {
  background: var(--color-surface-dim);
  color: var(--color-ink);
  font-weight: var(--weight-semibold);
}

.toc-pip {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
```

### Section Headings
```css
.section-heading {
  display: grid;
  grid-template-columns: 4px 1fr;
  gap: var(--space-4);
  align-items: center;
  margin: var(--space-9) 0 var(--space-5);
}

.section-heading-accent {
  height: 2.4rem;
  border-radius: 2px;
  background: currentColor;
}

.section-heading-text {
  font-size: var(--text-lg);
  font-weight: var(--weight-bold);
  letter-spacing: -0.025em;
  text-wrap: balance;
}

/* Per-pillar accent color applied via class */
.section--flowchart  { color: var(--color-flowchart); }
.section--mindmap    { color: var(--color-mindmap); }
.section--pearl      { color: var(--color-pearl); }
.section--trap       { color: var(--color-trap); }
.section--atom       { color: var(--color-atom); }
.section--simplified { color: var(--color-simplified); }
```

### Cards (Pearl, Trap, Atom)
Cards use a 2-column grid: a 4px accent strip + content area. No border-left trick.

```css
.card {
  display: grid;
  grid-template-columns: 4px 1fr;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  box-shadow: var(--shadow-sm);
  overflow: hidden;  /* clips the accent strip to border-radius */
  margin-bottom: var(--space-3);
  transition: box-shadow 220ms ease-out, transform 220ms ease-out;
}

.card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.card-accent { background: currentColor; }

.card-body {
  padding: var(--space-4) var(--space-5);
}

.card-label {
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: currentColor;
  margin-bottom: var(--space-2);
}

.card-title {
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  color: var(--color-ink);
  margin-bottom: var(--space-2);
  text-wrap: balance;
}

.card-content {
  font-size: var(--text-base);
  color: var(--color-ink);
  line-height: var(--leading-snug);
  max-width: var(--measure-body);
}

.card-meta {
  margin-top: var(--space-3);
  font-size: var(--text-sm);
  color: var(--color-ink-muted);
  display: flex;
  gap: var(--space-4);
  flex-wrap: wrap;
}

/* Pillar-specific card colors */
.card--pearl    { color: var(--color-pearl);  background: var(--bg-pearl); }
.card--trap     { color: var(--color-trap);   background: var(--bg-trap);  }
.card--atom     { color: var(--color-atom);   background: var(--bg-atom);  }
```

### Badges / Pills

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 10px;
  border-radius: 100px;
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  letter-spacing: 0.04em;
  white-space: nowrap;
}

.badge--high-yield {
  background: oklch(98% 0.06 90);
  color: oklch(38% 0.15 90);
  border: 1px solid oklch(80% 0.12 90);
}

.badge--emergency {
  background: oklch(97% 0.06 22);
  color: oklch(38% 0.20 22);
  border: 1px solid oklch(75% 0.15 22);
}

.badge--trap-type {
  background: oklch(97% 0.04 15);
  color: oklch(40% 0.18 15);
  border: 1px solid oklch(78% 0.12 15);
}
```

### Motion

```css
@media (prefers-reduced-motion: no-preference) {
  /* Section entrance — fade + rise. Default state must be visible;
     animation enhances, never gates content visibility. */
  .pillar-section {
    animation: fadeRise 400ms ease-out both;
    animation-timeline: view();
    animation-range: entry 0% entry 20%;
  }

  @keyframes fadeRise {
    from { opacity: 0; translate: 0 20px; }
    to   { opacity: 1; translate: 0 0;    }
  }

  .card {
    transition: box-shadow 220ms cubic-bezier(0.16, 1, 0.3, 1),
                transform   220ms cubic-bezier(0.16, 1, 0.3, 1);
  }

  .toc-link {
    transition: background 180ms ease-out, color 180ms ease-out;
  }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
```

### Image Display (Flowcharts & Mind Maps)

```css
.visual-figure {
  margin: var(--space-6) 0;
  text-align: center;
}

.visual-figure img {
  max-width: 100%;
  width: 100%;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-border);
}

.visual-caption {
  margin-top: var(--space-3);
  font-size: var(--text-sm);
  color: var(--color-ink-muted);
  font-style: italic;
  text-align: center;
}

.visual-label {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 100px;
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  color: var(--color-ink-muted);
  margin-bottom: var(--space-3);
}
```

---

## 8. PDF Output: Design Specifications (ReportLab)

### Document Setup
```python
from reportlab.lib.units import mm
from reportlab.lib import colors

PAGE_SIZE = (210*mm, 297*mm)  # A4
MARGIN = 22*mm
GUTTER = 8*mm

# Colors (hex approximations of OKLCH tokens)
COLOR_INK        = colors.HexColor('#1a1c2e')
COLOR_INK_MUTED  = colors.HexColor('#5a6278')
COLOR_BG         = colors.HexColor('#f7f8fc')
COLOR_SURFACE    = colors.HexColor('#ffffff')
COLOR_BORDER     = colors.HexColor('#e2e5ef')

PILLAR_COLORS = {
    'flowchart':  colors.HexColor('#3b82f6'),
    'mindmap':    colors.HexColor('#8b5cf6'),
    'pearl':      colors.HexColor('#f59e0b'),
    'trap':       colors.HexColor('#ef4444'),
    'atom':       colors.HexColor('#10b981'),
    'simplified': colors.HexColor('#06b6d4'),
}

PILLAR_BG = {
    'flowchart':  colors.HexColor('#eff6ff'),
    'mindmap':    colors.HexColor('#f5f3ff'),
    'pearl':      colors.HexColor('#fffbeb'),
    'trap':       colors.HexColor('#fef2f2'),
    'atom':       colors.HexColor('#f0fdf4'),
    'simplified': colors.HexColor('#f0fdfa'),
}
```

### Type Styles (ParagraphStyle)
```python
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

STYLES = {
    'cover_title':    ParagraphStyle('CoverTitle',   fontName='Helvetica-Bold',   fontSize=28, leading=34,  textColor=colors.white,      alignment=TA_CENTER, spaceAfter=6),
    'cover_subtitle': ParagraphStyle('CoverSub',     fontName='Helvetica',        fontSize=13, leading=18,  textColor=colors.HexColor('#c7d2fe'), alignment=TA_CENTER),
    'section_heading':ParagraphStyle('SectionH',     fontName='Helvetica-Bold',   fontSize=16, leading=20,  spaceBefore=32, spaceAfter=12),
    'card_label':     ParagraphStyle('CardLabel',    fontName='Helvetica-Bold',   fontSize=7.5,leading=10,  textColor=colors.HexColor('#6b7280'), spaceAfter=4, wordWrap='CJK'),
    'card_title':     ParagraphStyle('CardTitle',    fontName='Helvetica-Bold',   fontSize=11, leading=14,  spaceAfter=4),
    'card_body':      ParagraphStyle('CardBody',     fontName='Helvetica',        fontSize=9.5,leading=14,  spaceAfter=0),
    'atom':           ParagraphStyle('Atom',         fontName='Helvetica',        fontSize=9,  leading=13),
    'caption':        ParagraphStyle('Caption',      fontName='Helvetica-Oblique',fontSize=8,  leading=11,  textColor=colors.HexColor('#6b7280'), alignment=TA_CENTER),
}
```

### Card Drawing Function
```python
def draw_card(canvas, x, y, width, height, pillar_type, label, title, body):
    """Draws a pillar card with accent strip + content area."""
    accent_w = 4
    radius = 6
    accent_color = PILLAR_COLORS[pillar_type]
    bg_color = PILLAR_BG[pillar_type]

    # Background
    canvas.setFillColor(bg_color)
    canvas.roundRect(x, y, width, height, radius, fill=1, stroke=0)

    # Accent strip
    canvas.setFillColor(accent_color)
    canvas.rect(x, y, accent_w, height, fill=1, stroke=0)

    # Light border
    canvas.setStrokeColor(COLOR_BORDER)
    canvas.setLineWidth(0.5)
    canvas.roundRect(x, y, width, height, radius, fill=0, stroke=1)

    # Text is rendered separately via Paragraph flowables positioned over this rect
```

### Section Header with Accent Bar
```python
def draw_section_header(canvas, x, y, width, pillar_type, title_text):
    accent_color = PILLAR_COLORS[pillar_type]
    bar_h = 3
    canvas.setFillColor(accent_color)
    canvas.rect(x, y - bar_h, width, bar_h, fill=1, stroke=0)
    # Title text drawn above the bar via Paragraph
```

### Cover Page
```python
def draw_cover(canvas, title, specialty, source, date_str):
    # Gradient approximation: dark navy → deep indigo
    canvas.setFillColor(colors.HexColor('#1e2140'))
    canvas.rect(0, 0, 210*mm, 297*mm, fill=1, stroke=0)

    # Decorative gradient rectangle (upper)
    canvas.setFillColor(colors.HexColor('#2d3480'))
    canvas.roundRect(0, 200*mm, 210*mm, 97*mm, 0, fill=1, stroke=0)

    # Pillar pill badges (strip near top)
    badge_labels = ['Flowcharts', 'Mind Maps', 'Pearls', 'MCQ Traps', 'Atoms', 'Simplified']
    badge_colors = list(PILLAR_COLORS.values())
    # Draw pills in a row, centered
```

---

## 9. Anti-Patterns — Absolute Bans

These patterns must never appear in any output from this skill. If you are about to emit any of them, stop and rewrite.

**Color:**
- No raw `#ff6b6b` / `#ffd43b` etc. — always use the token system above.
- No gray text on a colored background. Use the hue's own darker shade.
- No color-only encoding — always pair color with shape, icon, or label.
- No more than 6 distinct hues in a single visual (flowchart or mind map).

**Typography:**
- No all-caps body copy (uppercase labels ≤ 4 words only).
- No more than 3 font sizes in a single card.
- No font-weight below 400 in the digest (thin text is unreadable in medical context).
- No `font-family` mixing (2 families max: Inter + JetBrains Mono).

**Layout:**
- No nested cards.
- No `border-left` for card accents — use the `grid-template-columns: 4px 1fr` pattern.
- No absolute widths in HTML output — use `max-width` + `width: 100%`.
- No `z-index: 9999` or arbitrary z-values.

**Visuals:**
- No flowchart without at least one decision diamond.
- No mind map deeper than 3 levels.
- No unlabeled edges at branch points.
- No text inside flowchart nodes exceeding 12 words.
- No mind map with more than 7 L1 branches (split instead).

**Motion:**
- No bounce or elastic easing.
- No animation that gates content visibility (initial state must be visible).
- Every animation must have a `prefers-reduced-motion` counterpart.
