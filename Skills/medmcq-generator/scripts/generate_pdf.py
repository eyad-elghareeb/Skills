#!/usr/bin/env python3
"""
Premium medical textbook PDF — Impeccable-grade design.

Key design principles (from Impeccable skill):
  - No side-stripe borders (ABSOLUTE BAN — replaced with full outline or bg tint only)
  - ALL-CAPS labels get proper charSpace tracking (0.8–1.2pt)
  - Type hierarchy ≥1.25× ratio per step: caption 7 / label 8 / body 9.5 / heading 11 / display 16+
  - 4pt grid spacing: 4 | 8 | 12 | 16 | 24 | 36 | 48
  - Vertical rhythm anchored to body leading: 9.5pt × 1.47 ≈ 14pt base unit
  - Color 60/30/10: navy dominates, cobalt/emerald carry structure, gold is the 10% accent
  - Cover: dominant committed color strategy, extreme scale contrast, decisive geometry

Typography:
  Poppins (headings/labels) + Lora variable (body/vignette) + LiberationMono (lab values)
"""

import json, sys, os, argparse
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    Table, TableStyle, PageBreak, KeepTogether, NextPageTemplate, Flowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# ═══════════════════════════════════════════════════════════════
# FONTS
# ═══════════════════════════════════════════════════════════════

_FD = "/usr/share/fonts/truetype"

def register_fonts():
    pairs = [
        ("Poppins",             f"{_FD}/google-fonts/Poppins-Regular.ttf"),
        ("Poppins-Bold",        f"{_FD}/google-fonts/Poppins-Bold.ttf"),
        ("Poppins-Italic",      f"{_FD}/google-fonts/Poppins-Italic.ttf"),
        ("Poppins-BoldItalic",  f"{_FD}/google-fonts/Poppins-BoldItalic.ttf"),
        ("Poppins-Medium",      f"{_FD}/google-fonts/Poppins-Medium.ttf"),
        ("Poppins-Light",       f"{_FD}/google-fonts/Poppins-Light.ttf"),
        ("Poppins-LightItalic", f"{_FD}/google-fonts/Poppins-LightItalic.ttf"),
        ("Lora",                f"{_FD}/google-fonts/Lora-Variable.ttf"),
        ("Lora-Italic",         f"{_FD}/google-fonts/Lora-Italic-Variable.ttf"),
        ("LoraB",               f"{_FD}/liberation/LiberationSerif-Bold.ttf"),
        ("LoraBI",              f"{_FD}/liberation/LiberationSerif-BoldItalic.ttf"),
        ("Mono",                f"{_FD}/liberation/LiberationMono-Regular.ttf"),
        ("Mono-Bold",           f"{_FD}/liberation/LiberationMono-Bold.ttf"),
    ]
    for name, path in pairs:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(name, path))
        else:
            print(f"⚠  Font not found: {path}", file=sys.stderr)
    registerFontFamily("Poppins", normal="Poppins", bold="Poppins-Bold",
                       italic="Poppins-Italic", boldItalic="Poppins-BoldItalic")
    registerFontFamily("Lora", normal="Lora", bold="LoraB",
                       italic="Lora-Italic", boldItalic="LoraBI")


# ═══════════════════════════════════════════════════════════════
# COLOR PALETTE  — 60 / 30 / 10 strategy
# 60% neutrals (navy/charcoal), 30% structural (cobalt/emerald), 10% accent (gold)
# ═══════════════════════════════════════════════════════════════

NAVY         = HexColor("#0B1E33")   # cover bg / dominant dark surface
COBALT       = HexColor("#1A3A5C")   # Q-section header, question labels
ROYAL        = HexColor("#1E5FA8")   # option letters
PALE_BLUE    = HexColor("#EBF3FA")   # educational objective callout bg

GOLD         = HexColor("#C9920A")   # primary accent (the 10%)
GOLD_MID     = HexColor("#E8A912")   # lighter gold for secondary marks

EMERALD      = HexColor("#0A5C36")   # A-section header, answer labels
SAGE         = HexColor("#18855A")   # medium green for answer rules
PALE_GREEN   = HexColor("#E6F5ED")   # key concept callout bg
MINT_RULE    = HexColor("#A8D8BC")   # answer section separator

CHARCOAL     = HexColor("#1A1A2E")   # primary body text
SLATE        = HexColor("#3A4554")   # secondary text / options
MUTED        = HexColor("#6B7A8D")   # vignette preview, captions
RULE_GRAY    = HexColor("#D0D8E4")   # body rules
PALE_GRAY    = HexColor("#F4F6F9")   # very subtle fills

LINK         = HexColor("#1565C0")   # hyperlinks

def _hx(c):
    """6-char lowercase hex for use in Paragraph HTML."""
    return f"{int(c.red*255):02x}{int(c.green*255):02x}{int(c.blue*255):02x}"


# ═══════════════════════════════════════════════════════════════
# SPACING GRID  — 4pt base
# ═══════════════════════════════════════════════════════════════
SP = {1: 4, 2: 8, 3: 12, 4: 16, 6: 24, 9: 36, 12: 48}
def sp(n): return n * 4   # e.g. sp(3) = 12pt


# ═══════════════════════════════════════════════════════════════
# CUSTOM FLOWABLES
# ═══════════════════════════════════════════════════════════════

class HRule(Flowable):
    """Horizontal rule on 4pt grid."""
    def __init__(self, width, thickness=0.5, color=RULE_GRAY, before=8, after=8):
        super().__init__()
        self.width     = width
        self.height    = thickness + before + after
        self.thickness = thickness
        self.color     = color
        self.before    = before
        self.after     = after

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(self.color)
        c.setLineWidth(self.thickness)
        y = self.height - self.before - self.thickness
        c.line(0, y, self.width, y)
        c.restoreState()


class DoubleRule(Flowable):
    """Thick + thin double rule ornament — classic textbook device."""
    def __init__(self, width, color=GOLD, before=8, after=8):
        super().__init__()
        self.width  = width
        self.color  = color
        self.before = before
        self.after  = after
        self.height = before + after + 8

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(self.color)
        base = self.after
        c.setLineWidth(2.4)
        c.line(0, base + 5, self.width, base + 5)
        c.setLineWidth(0.7)
        c.line(0, base + 1.5, self.width, base + 1.5)
        c.restoreState()


class Anchor(Flowable):
    """Zero-size PDF anchor / bookmark destination."""
    def __init__(self, name):
        super().__init__()
        self.name   = name
        self.width  = 0
        self.height = 0

    def wrap(self, aw, ah): return (0, 0)

    def draw(self):
        self.canv.bookmarkPage(self.name, fit='XYZ', left=0, top=None, zoom=0)


class TrackedLabel(Flowable):
    """
    ALL-CAPS label with charSpace tracking — fixes the 'no letter-spacing'
    problem that makes uppercase labels look cramped.
    Impeccable: ALL-CAPS labels need 0.05–0.12em tracking.
    At 10pt that is 0.5–1.2pt charSpace; we use 0.9pt.
    """
    def __init__(self, text, font_name="Poppins-Bold", font_size=10,
                 color=COBALT, tracking=0.9, col_width=200):
        super().__init__()
        self.text       = text
        self.font_name  = font_name
        self.font_size  = font_size
        self.color      = color
        self.tracking   = tracking
        self.col_width  = col_width
        self.height     = font_size * 1.55   # 1.2 line-height for label

    def wrap(self, aw, ah):
        self.col_width = aw
        return (aw, self.height)

    def draw(self):
        c = self.canv
        c.saveState()
        t = c.beginText(0, self.height * 0.18)
        t.setFont(self.font_name, self.font_size)
        t.setFillColor(self.color)
        t.setCharSpace(self.tracking)
        t.textLine(self.text)
        c.drawText(t)
        c.restoreState()


class SectionBanner(Flowable):
    """
    Full-width section opener.
    Impeccable fix: uses a TOP accent strip (not a left side-stripe — that's banned).
    The gold top strip sits above the band; bottom has a subtle separator line.
    """
    def __init__(self, width, main_text, sub_text="",
                 bg=COBALT, accent=GOLD, fg=white, height=52):
        super().__init__()
        self.width     = width
        self.height    = height
        self.main_text = main_text
        self.sub_text  = sub_text
        self.bg        = bg
        self.accent    = accent
        self.fg        = fg

    def wrap(self, aw, ah):
        self.width = aw
        return (aw, self.height)

    def draw(self):
        c = self.canv
        c.saveState()
        # Main band
        c.setFillColor(self.bg)
        c.rect(0, 0, self.width, self.height - 4, fill=1, stroke=0)
        # TOP accent strip (not a side strip — impeccable compliant)
        c.setFillColor(self.accent)
        c.rect(0, self.height - 4, self.width, 4, fill=1, stroke=0)
        # Bottom separator line
        c.setStrokeColor(self.accent)
        c.setLineWidth(0.8)
        c.line(0, 0, self.width, 0)
        # Main text — use beginText for charSpace tracking
        # Fixed positions: main text baseline at 30pt, sub text at 10pt from bottom
        if self.sub_text:
            t = c.beginText(12, 30)
            t.setFont("Poppins-Bold", 11)
            t.setFillColor(self.fg)
            t.setCharSpace(0.6)
            t.textLine(self.main_text)
            c.drawText(t)
            sub_color = HexColor("#A8C4DC") if self.bg == COBALT else HexColor("#A8D8BE")
            t2 = c.beginText(12, 10)
            t2.setFont("Poppins-Light", 7.5)
            t2.setFillColor(sub_color)
            t2.textLine(self.sub_text)
            c.drawText(t2)
        else:
            t = c.beginText(12, 18)
            t.setFont("Poppins-Bold", 11)
            t.setFillColor(self.fg)
            t.setCharSpace(0.6)
            t.textLine(self.main_text)
            c.drawText(t)
        c.restoreState()


# ═══════════════════════════════════════════════════════════════
# PARAGRAPH STYLES
# ═══════════════════════════════════════════════════════════════
# Type scale (≥1.25 ratio between steps — impeccable typeset rule):
#   caption  7.0pt  (0.74×)
#   label    8.0pt  (0.84×)
#   body     9.5pt  (1.00×)  ← base
#   subhead  11.0pt (1.16×)
#   heading  13.5pt (1.42×)
#   display  16pt+
# Body leading: 9.5 × 1.47 ≈ 14pt  → rhythm base = 14pt
# ═══════════════════════════════════════════════════════════════

def make_styles(compact=False):
    fs = 0.88 if compact else 1.0
    s  = {}

    # ── Cover ──
    s["cv_eyebrow"] = ParagraphStyle(
        "cv_eyebrow", fontName="Poppins-Light", fontSize=8, leading=12,
        textColor=HexColor("#6A90B8"), alignment=TA_CENTER, spaceAfter=sp(3),
    )
    s["cv_title"] = ParagraphStyle(
        "cv_title", fontName="Poppins-Bold", fontSize=44, leading=50,
        textColor=white, alignment=TA_CENTER, spaceAfter=sp(2),
    )
    s["cv_subtitle"] = ParagraphStyle(
        "cv_subtitle", fontName="Lora-Italic", fontSize=17, leading=24,
        textColor=HexColor("#C0D8F0"), alignment=TA_CENTER, spaceAfter=sp(2),
    )
    s["cv_meta"] = ParagraphStyle(
        "cv_meta", fontName="Poppins-Light", fontSize=10, leading=16,
        textColor=HexColor("#8CAECE"), alignment=TA_CENTER, spaceAfter=sp(1),
    )
    s["cv_feature"] = ParagraphStyle(
        "cv_feature", fontName="Poppins", fontSize=9, leading=14,
        textColor=HexColor("#C8DFF0"), alignment=TA_CENTER, spaceAfter=sp(1),
    )
    s["cv_footer"] = ParagraphStyle(
        "cv_footer", fontName="Poppins-Light", fontSize=7.5, leading=11,
        textColor=HexColor("#456080"), alignment=TA_CENTER,
    )

    # ── Questions ──
    # body = 9.5pt Lora, leading 14pt (1.47×) — good for justified text
    s["vignette"] = ParagraphStyle(
        "vignette", fontName="Lora",
        fontSize=round(9.5 * fs, 1), leading=round(14 * fs, 1),
        textColor=CHARCOAL, alignment=TA_JUSTIFY,
        spaceBefore=sp(2), spaceAfter=round(14 * fs, 1),  # one rhythm unit gap
    )
    # options: 9pt Lora, indent = 1 rhythm unit
    s["option"] = ParagraphStyle(
        "option", fontName="Lora",
        fontSize=round(9 * fs, 1), leading=round(13 * fs, 1),
        textColor=SLATE, leftIndent=sp(4),  # 16pt indent on 4pt grid
        spaceAfter=round(4 * fs, 1),        # tight 4pt between options
    )
    s["see_ans"] = ParagraphStyle(
        "see_ans", fontName="Poppins", fontSize=7.5, leading=10,
        textColor=LINK, alignment=TA_RIGHT,
        spaceBefore=sp(2), spaceAfter=sp(1),
    )

    # ── Answers ──
    s["a_preview"] = ParagraphStyle(
        "a_preview", fontName="Lora-Italic",
        fontSize=round(8 * fs, 1), leading=round(12 * fs, 1),
        textColor=MUTED, spaceAfter=sp(3),
    )
    s["explanation"] = ParagraphStyle(
        "explanation", fontName="Lora",
        fontSize=round(9.5 * fs, 1), leading=round(14 * fs, 1),
        textColor=CHARCOAL, alignment=TA_JUSTIFY,
        spaceBefore=sp(2), spaceAfter=sp(3),
    )
    # Callout inner text: 8.5pt Lora-Italic
    s["callout_label"] = ParagraphStyle(
        "callout_label", fontName="Poppins-Bold",
        fontSize=round(7 * fs, 1), leading=round(10 * fs, 1),
        textColor=ROYAL, spaceAfter=sp(1),
    )
    s["callout_text"] = ParagraphStyle(
        "callout_text", fontName="Lora-Italic",
        fontSize=round(8.5 * fs, 1), leading=round(12.5 * fs, 1),
        textColor=SLATE,
    )
    s["back_lnk"] = ParagraphStyle(
        "back_lnk", fontName="Poppins", fontSize=7, leading=9,
        textColor=LINK, alignment=TA_RIGHT,
        spaceBefore=sp(2), spaceAfter=sp(1),
    )
    s["q_ref_title"] = ParagraphStyle(
        "q_ref_title", fontName="Poppins-Bold", fontSize=7, leading=10,
        textColor=COBALT, alignment=TA_CENTER, spaceBefore=sp(1), spaceAfter=sp(1),
    )
    s["q_ref"] = ParagraphStyle(
        "q_ref", fontName="Poppins", fontSize=7.5, leading=11,
        textColor=COBALT, alignment=TA_CENTER, spaceAfter=sp(2),
    )
    return s


# ═══════════════════════════════════════════════════════════════
# PAGE BACKGROUNDS
# ═══════════════════════════════════════════════════════════════

def draw_cover(canvas, doc):
    canvas.saveState()
    pw, ph = A4

    # ── Full navy bg ──
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, pw, ph, fill=1, stroke=0)

    # ── Upper geometry: large cobalt block ──
    canvas.setFillColor(HexColor("#0D2744"))
    canvas.rect(0, ph - 200, pw, 200, fill=1, stroke=0)

    # ── First diagonal band (dark navy over cobalt) ──
    canvas.setFillColor(HexColor("#0F3060"))
    p = canvas.beginPath()
    p.moveTo(0, ph - 110)
    p.lineTo(pw * 0.62, ph - 110)
    p.lineTo(pw * 0.46, ph)
    p.lineTo(0, ph)
    p.close()
    canvas.drawPath(p, fill=1, stroke=0)

    # ── Second diagonal — a thinner lighter wedge, right side ──
    canvas.setFillColor(HexColor("#132D50"))
    p2 = canvas.beginPath()
    p2.moveTo(pw * 0.70, ph)
    p2.lineTo(pw, ph)
    p2.lineTo(pw, ph - 200)
    p2.lineTo(pw * 0.85, ph - 200)
    p2.close()
    canvas.drawPath(p2, fill=1, stroke=0)

    # ── GOLD top-edge accent bar ──
    canvas.setFillColor(GOLD)
    canvas.rect(0, ph - 5, pw, 5, fill=1, stroke=0)

    # ── Thin gold separator below cobalt block ──
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(0.8)
    canvas.line(pw * 0.06, ph - 202, pw * 0.94, ph - 202)

    # ── Right-side vertical accent pillar ──
    canvas.setFillColor(HexColor("#14304E"))
    canvas.rect(pw - 20, 0, 20, ph, fill=1, stroke=0)
    # Gold chip in the pillar at golden ratio height
    canvas.setFillColor(GOLD)
    canvas.rect(pw - 20, ph * 0.382, 5, ph * 0.236, fill=1, stroke=0)

    # ── Bottom footer band ──
    canvas.setFillColor(HexColor("#060E18"))
    canvas.rect(0, 0, pw, 64, fill=1, stroke=0)
    # Gold top edge of footer
    canvas.setFillColor(GOLD)
    canvas.rect(0, 64, pw, 2, fill=1, stroke=0)

    # ── Subtle diamond/grid pattern in footer ──
    canvas.setStrokeColor(HexColor("#18304A"))
    canvas.setLineWidth(0.35)
    for x in range(0, int(pw), 24):
        canvas.line(x, 0, x, 62)
    for y in [20, 42]:
        canvas.line(0, y, pw - 22, y)

    # ── Content well subtle border ──
    canvas.setStrokeColor(HexColor("#1C3D60"))
    canvas.setLineWidth(0.6)
    canvas.roundRect(pw * 0.05, 76, pw * 0.87, ph - 300, 3, fill=0, stroke=1)

    # ── Three decorative circles — top-left of content well ──
    for i, shade in enumerate(["#0E2E50", "#163A64", "#1E4878"]):
        canvas.setFillColor(HexColor(shade))
        canvas.circle(pw * 0.10 + i * 13, ph - 228, 5 - i * 0.5, fill=1, stroke=0)

    canvas.restoreState()


def _header_band(canvas, doc, bg_color, section_label, label_color):
    canvas.saveState()
    pw, ph = A4
    lm, rm = doc.leftMargin, doc.rightMargin

    # Band
    canvas.setFillColor(bg_color)
    canvas.rect(0, ph - 28, pw, 28, fill=1, stroke=0)
    # GOLD top strip (top accent, not side strip)
    canvas.setFillColor(GOLD)
    canvas.rect(0, ph - 5, pw, 5, fill=1, stroke=0)

    # Doc title left
    canvas.setFillColor(white)
    canvas.setFont("Poppins-Bold", 7.5)
    canvas.drawString(lm, ph - 19, getattr(doc, "header_left", "Medical MCQ Bank"))

    # Section label right, letter-spaced — use beginText for charSpace
    lbl_w = canvas.stringWidth(section_label, "Poppins-Light", 7)
    t = canvas.beginText(pw - rm - lbl_w, ph - 19)
    t.setFont("Poppins-Light", 7)
    t.setFillColor(label_color)
    t.setCharSpace(0.7)
    t.textLine(section_label)
    canvas.drawText(t)

    # Footer
    canvas.setFillColor(MUTED)
    canvas.setFont("Poppins-Light", 7)
    canvas.drawCentredString(pw / 2, 14, f"\u2014  {doc.page}  \u2014")
    canvas.setStrokeColor(RULE_GRAY)
    canvas.setLineWidth(0.35)
    canvas.line(lm, 28, pw - rm, 28)

    canvas.restoreState()


def draw_header_q(canvas, doc):
    _header_band(canvas, doc, COBALT, "QUESTIONS", HexColor("#A8C4DC"))


def draw_header_a(canvas, doc):
    _header_band(canvas, doc, EMERALD, "ANSWER KEY & EXPLANATIONS", HexColor("#A8D8BE"))


# ═══════════════════════════════════════════════════════════════
# CONTENT HELPERS
# ═══════════════════════════════════════════════════════════════

LETTERS = ["A", "B", "C", "D", "E", "F", "G", "H"]


def xesc(text):
    if not text: return ""
    return (str(text)
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace("\n", "<br/>").strip())


def preview(text, n=22):
    w = str(text).split()
    return (" ".join(w[:n]) + "\u2026") if len(w) > n else text


def correct_badge(letter, opt_text, col_width, compact=False):
    """
    Green correct-answer badge.
    IMPECCABLE: uses a full-perimeter 0 border (no side stripe).
    White Poppins-Bold text on EMERALD background.
    """
    fs = 0.88 if compact else 1.0
    inner = ParagraphStyle(
        "ca", fontName="Poppins-Bold",
        fontSize=round(9.5 * fs, 1), leading=round(14 * fs, 1),
        textColor=white,
    )
    cell = Paragraph(f"\u2713\u2003Correct Answer:  {letter}.\u2002{xesc(opt_text)}", inner)
    t = Table([[cell]], colWidths=[col_width])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), EMERALD),
        ("TOPPADDING",    (0, 0), (-1, -1), sp(2)),
        ("BOTTOMPADDING", (0, 0), (-1, -1), sp(2)),
        ("LEFTPADDING",   (0, 0), (-1, -1), sp(3)),
        ("RIGHTPADDING",  (0, 0), (-1, -1), sp(2)),
    ]))
    return t


def callout_box(label, body_text, col_width, bg, border_color, compact=False):
    """
    Callout box for Educational Objective / Key Concept.

    IMPECCABLE FIX — ABSOLUTE BAN observed:
      BEFORE: LINEBEFORE 3pt side-stripe (explicitly banned for callouts in Impeccable)
      AFTER:  OUTLINE 0.75pt full-perimeter hairline + background tint
      This is the compliant pattern: "full hairline border or background tint" per colorize.md

    Type hierarchy: 7pt Poppins-Bold TRACKED label above 8.5pt Lora-Italic body.
    """
    fs = 0.88 if compact else 1.0
    lbl_sty = ParagraphStyle(
        "co_l", fontName="Poppins-Bold",
        fontSize=round(7 * fs, 1), leading=round(10 * fs, 1),
        textColor=border_color,
    )
    txt_sty = ParagraphStyle(
        "co_t", fontName="Lora-Italic",
        fontSize=round(8.5 * fs, 1), leading=round(12.5 * fs, 1),
        textColor=SLATE,
    )
    rows = [
        [Paragraph(label, lbl_sty)],
        [Paragraph(xesc(body_text), txt_sty)],
    ]
    t = Table(rows, colWidths=[col_width])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), bg),
        ("TOPPADDING",    (0, 0), (0, 0), sp(1)),   # 4pt above label
        ("BOTTOMPADDING", (0, 0), (0, 0), sp(1)),   # 4pt below label
        ("TOPPADDING",    (0, 1), (0, 1), 0),
        ("BOTTOMPADDING", (0, 1), (0, 1), sp(2)),   # 8pt bottom
        ("LEFTPADDING",   (0, 0), (-1, -1), sp(3)), # 12pt left
        ("RIGHTPADDING",  (0, 0), (-1, -1), sp(2)), # 8pt right
        # ── IMPECCABLE COMPLIANT: full hairline outline, NOT a side stripe ──
        ("OUTLINE",       (0, 0), (-1, -1), 0.75, border_color),
    ]))
    return t


# ═══════════════════════════════════════════════════════════════
# QUESTION FLOWABLES
# ═══════════════════════════════════════════════════════════════

def build_question(q_data, q_num, styles, col_width, compact=False):
    sp_f = 0.5 if compact else 1.0
    elems = []

    anchor_name  = f"q{q_num}"
    target_name  = f"a{q_num}"

    # Anchor (zero-height; no longer embedded in a Paragraph)
    elems.append(Anchor(anchor_name))

    # Tracked label "QUESTION N" — proper letter-spacing (impeccable fix)
    elems.append(TrackedLabel(
        f"QUESTION {q_num}",
        font_name="Poppins-Bold", font_size=round(10.5 * (0.88 if compact else 1), 1),
        color=COBALT, tracking=0.9, col_width=col_width,
    ))

    # 1.5pt cobalt rule, on 4pt grid spacing
    elems.append(HRule(col_width, thickness=1.5, color=ROYAL, before=sp(1), after=sp(2)))

    # Vignette — 9.5pt Lora justified, 14pt leading (1.47×)
    elems.append(Paragraph(xesc(q_data.get("question", "")), styles["vignette"]))

    # Options — letter badge in Poppins-Bold cobalt
    for i, opt in enumerate(q_data.get("options", [])):
        ltr = LETTERS[i] if i < len(LETTERS) else str(i + 1)
        opt_html = (
            f'<font name="Poppins-Bold" color="#{_hx(ROYAL)}">{ltr})</font>'
            f'\u2002{xesc(opt)}'
        )
        elems.append(Paragraph(opt_html, styles["option"]))

    # See Answer link
    link = (
        f'<a href="#{target_name}" color="#{_hx(LINK)}">'
        f'See Answer &amp; Explanation \u25ba</a>'
    )
    elems.append(Paragraph(link, styles["see_ans"]))

    # Separator — on 4pt grid
    elems.append(HRule(col_width, thickness=0.4, color=RULE_GRAY, before=sp(2), after=sp(3)))

    return elems


# ═══════════════════════════════════════════════════════════════
# ANSWER FLOWABLES
# ═══════════════════════════════════════════════════════════════

def build_answer(q_data, q_num, styles, col_width, compact=False):
    sp_f = 0.5 if compact else 1.0
    elems = []

    anchor_name = f"a{q_num}"
    back_name   = f"q{q_num}"

    # Anchor
    elems.append(Anchor(anchor_name))

    # Tracked label "ANSWER N"
    elems.append(TrackedLabel(
        f"ANSWER {q_num}",
        font_name="Poppins-Bold", font_size=round(10.5 * (0.88 if compact else 1), 1),
        color=EMERALD, tracking=0.9, col_width=col_width,
    ))

    # Sage rule
    elems.append(HRule(col_width, thickness=1.5, color=SAGE, before=sp(1), after=sp(2)))

    # Vignette preview in 8pt Lora-Italic
    preview_n = 14 if compact else 22
    elems.append(Paragraph(
        f'\u201c{xesc(preview(q_data.get("question", ""), preview_n))}\u201d',
        styles["a_preview"]
    ))

    # Correct answer badge
    opts    = q_data.get("options", [])
    correct = q_data.get("correct", -1)
    if 0 <= correct < len(opts):
        ltr = LETTERS[correct]
        elems.append(correct_badge(ltr, opts[correct], col_width, compact))
        elems.append(Spacer(1, sp(3)))

    # Explanation — 9.5pt Lora, same as vignette for continuity
    explanation = q_data.get("explanation", "")
    if explanation:
        elems.append(Paragraph(xesc(explanation), styles["explanation"]))

    # Educational Objective callout (impeccable-compliant: full outline, no side stripe)
    edu = q_data.get("educational_objective", "")
    if edu:
        elems.append(callout_box(
            "EDUCATIONAL OBJECTIVE", edu, col_width,
            bg=PALE_BLUE, border_color=ROYAL, compact=compact,
        ))
        elems.append(Spacer(1, sp(2)))

    # Key Concept callout
    key = q_data.get("key_concept", "")
    if key:
        elems.append(callout_box(
            "KEY CONCEPT", key, col_width,
            bg=PALE_GREEN, border_color=SAGE, compact=compact,
        ))
        elems.append(Spacer(1, sp(2)))

    # Back link
    back = (
        f'<a href="#{back_name}" color="#{_hx(LINK)}">'
        f'\u25c4 Back to Question {q_num}</a>'
    )
    elems.append(Paragraph(back, styles["back_lnk"]))

    # Separator
    elems.append(HRule(col_width, thickness=0.4, color=MINT_RULE, before=sp(2), after=sp(3)))

    return elems


# ═══════════════════════════════════════════════════════════════
# MAIN PDF BUILDER
# ═══════════════════════════════════════════════════════════════

def build_pdf(input_json_path, output_pdf_path,
              title=None, subtitle=None,
              exam_level=None, difficulty=None,
              compact=False):

    register_fonts()

    with open(input_json_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    if not title:
        base  = os.path.splitext(os.path.basename(input_json_path))[0]
        title = base.replace("-", " ").replace("_", " ").title()

    total_q = len(questions)
    pw, ph  = A4

    # Margins on 4pt grid
    ms = 28 if compact else 36   # side
    mt = 52                       # top (header = 28pt + 24pt clearance)
    mb = 36                       # bottom
    gu = 12 if compact else 16   # gutter
    cw = (pw - 2 * ms - gu) / 2

    doc = BaseDocTemplate(
        output_pdf_path, pagesize=A4,
        leftMargin=ms, rightMargin=ms, topMargin=mt, bottomMargin=mb,
        title=title, author="MedMCQ Generator",
        subject="Medical Board Review — Best of Five",
    )
    doc.header_left = title

    # Frames
    cover_f = Frame(ms, mb, pw - 2 * ms, ph - mt - mb, id="cover")
    left_f  = Frame(ms,        mb, cw, ph - mt - mb, id="L", leftPadding=0, rightPadding=sp(2))
    right_f = Frame(ms + cw + gu, mb, cw, ph - mt - mb, id="R", leftPadding=sp(2), rightPadding=0)

    doc.addPageTemplates([
        PageTemplate(id="cover",     frames=[cover_f],              onPage=draw_cover),
        PageTemplate(id="questions", frames=[left_f, right_f],      onPage=draw_header_q),
        PageTemplate(id="answers",   frames=[left_f, right_f],      onPage=draw_header_a),
    ])

    styles = make_styles(compact=compact)
    story  = []

    # ══════════════════════════════════════════════════════════
    # COVER
    # ══════════════════════════════════════════════════════════
    story.append(Spacer(1, 64))

    # Eyebrow — letter-spaced via Paragraph (Poppins-Light small)
    story.append(Paragraph(
        "M E D I C A L  &nbsp; B O A R D  &nbsp; R E V I E W",
        styles["cv_eyebrow"]
    ))
    story.append(Spacer(1, sp(3)))

    # Hero title — 44pt Poppins-Bold (3× the body base for extreme scale)
    story.append(Paragraph(title, styles["cv_title"]))

    if subtitle:
        story.append(Paragraph(subtitle, styles["cv_subtitle"]))
        story.append(Spacer(1, sp(1)))

    # Double rule ornament (thick + thin gold lines)
    story.append(DoubleRule(pw - 2 * ms, color=GOLD, before=sp(2), after=sp(2)))
    story.append(Spacer(1, sp(4)))

    # Metadata in Poppins-Light — weight contrast: Bold title vs Light meta
    meta_lines = []
    if exam_level:  meta_lines.append(exam_level)
    if difficulty:  meta_lines.append(f"Difficulty: {difficulty}")
    meta_lines += [
        f"{total_q} Best-of-Five Questions",
        "Format:  A  \u00b7  B  \u00b7  C  \u00b7  D  \u00b7  E",
    ]
    for line in meta_lines:
        story.append(Paragraph(line, styles["cv_meta"]))
        story.append(Spacer(1, sp(1)))

    story.append(Spacer(1, sp(6)))

    # Feature lines in Poppins
    for feat in [
        "UWorld-Style Clinical Vignettes",
        "Multi-Step Clinical Reasoning  \u00b7  Comprehensive Explanations",
        "Hyperlinked Questions  \u2194  Answers",
    ]:
        story.append(Paragraph(feat, styles["cv_feature"]))
        story.append(Spacer(1, sp(1)))

    story.append(Spacer(1, sp(9)))
    story.append(HRule(pw - 2 * ms, thickness=0.4, color=HexColor("#162E48"),
                       before=0, after=sp(2)))
    story.append(Paragraph(
        "Questions first, then Answers \u2014 test yourself before peeking!",
        styles["cv_footer"]
    ))

    # ══════════════════════════════════════════════════════════
    # QUESTIONS SECTION
    # ══════════════════════════════════════════════════════════
    story.append(NextPageTemplate("questions"))
    story.append(PageBreak())

    story.append(SectionBanner(
        cw, "QUESTIONS",
        sub_text=f"{total_q} Best-of-Five  \u00b7  Attempt all questions before checking answers",
        bg=COBALT, accent=GOLD,
    ))
    story.append(Spacer(1, sp(3)))

    for i, q in enumerate(questions, 1):
        for elem in build_question(q, i, styles, cw, compact=compact):
            story.append(elem)

    # ══════════════════════════════════════════════════════════
    # ANSWERS SECTION
    # ══════════════════════════════════════════════════════════
    story.append(NextPageTemplate("answers"))
    story.append(PageBreak())

    story.append(SectionBanner(
        cw, "ANSWER KEY & EXPLANATIONS",
        sub_text="Tap any link to navigate between questions and answers",
        bg=EMERALD, accent=GOLD,
    ))
    story.append(Spacer(1, sp(2)))

    # Quick-reference strip
    story.append(Paragraph("Quick Reference", styles["q_ref_title"]))
    parts = []
    for i, q in enumerate(questions, 1):
        cidx = q.get("correct", -1)
        opts = q.get("options", [])
        if 0 <= cidx < len(opts):
            ltr = LETTERS[cidx]
            parts.append(f'<a href="#a{i}" color="#{_hx(LINK)}">Q{i}={ltr}</a>')
    story.append(Paragraph("  \u00b7  ".join(parts), styles["q_ref"]))
    story.append(HRule(cw, thickness=0.4, color=MINT_RULE, before=sp(1), after=sp(2)))

    for i, q in enumerate(questions, 1):
        for elem in build_answer(q, i, styles, cw, compact=compact):
            story.append(elem)

    doc.build(story)
    print(f"PDF generated: {output_pdf_path}")
    return output_pdf_path


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    ap = argparse.ArgumentParser(description="Impeccable-grade medical textbook PDF")
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--title",       default=None)
    ap.add_argument("--subtitle",    default=None)
    ap.add_argument("--exam-level",  default=None)
    ap.add_argument("--difficulty",  default=None)
    ap.add_argument("--compact",     action="store_true")
    args = ap.parse_args()
    build_pdf(args.input, args.output,
              title=args.title, subtitle=args.subtitle,
              exam_level=args.exam_level, difficulty=args.difficulty,
              compact=args.compact)


if __name__ == "__main__":
    main()
