#!/usr/bin/env bash
# =============================================================================
# Med PDF Digest — Full Pipeline Orchestrator
# =============================================================================
# Runs the complete extraction and digest generation pipeline for a single PDF
# or text file.
#
# Usage:
#   ./pipeline.sh [OPTIONS] <input_file>
#
# Options:
#   -o, --output DIR        Output directory (default: ./digest_output)
#   -f, --format FORMAT     Output format: pdf|html|md|anki|all (default: html)
#   -d, --depth DEPTH       Extraction depth: brief|standard|comprehensive (default: standard)
#   -s, --specialty NAME    Medical specialty hint (default: auto)
#   -t, --doc-type TYPE     textbook|guideline|review|drug_monograph|case_based (default: auto)
#       --flashcards        Also generate Anki/Quizlet flashcards
#       --model MODEL       Anthropic model (default: claude-sonnet-4-20250514)
#       --keep-temp         Keep intermediate files in output dir
#   -v, --verbose           Verbose output
#   -h, --help              Show this help message
#
# Environment:
#   ANTHROPIC_API_KEY       Required for automated extraction.
#                           If unset, pipeline stops at Phase 2 and prints instructions.
#
# Examples:
#   ./pipeline.sh heart_failure.pdf
#   ./pipeline.sh --format all --flashcards --depth comprehensive cardiology_chapter.pdf
#   ./pipeline.sh --format html --specialty neurology seizure_guidelines.pdf -o ~/study/neuro
#
# Dependencies:
#   - Python 3.11+
#   - pip install anthropic
#   - For PDF extraction: pip install pymupdf (or the PDF skill's pdf.py)
#   - For PDF output: pip install reportlab
# =============================================================================

set -euo pipefail

# ---- Defaults ---------------------------------------------------------------
OUTPUT_DIR="./digest_output"
FORMAT="html"
DEPTH="standard"
SPECIALTY="auto"
DOC_TYPE="auto"
FLASHCARDS=false
MODEL="claude-sonnet-4-20250514"
KEEP_TEMP=false
VERBOSE=false

# ---- Colors -----------------------------------------------------------------
RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

log()   { echo -e "${CYAN}[PIPELINE]${RESET} $*"; }
ok()    { echo -e "${GREEN}[OK]${RESET} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${RESET} $*"; }
die()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; exit 1; }

# ---- Help -------------------------------------------------------------------
usage() {
    sed -n '4,52p' "$0" | sed 's/^# //' | sed 's/^#//'
    exit 0
}

# ---- Parse arguments --------------------------------------------------------
INPUT_FILE=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)        usage ;;
        -o|--output)      OUTPUT_DIR="$2"; shift 2 ;;
        -f|--format)      FORMAT="$2"; shift 2 ;;
        -d|--depth)       DEPTH="$2"; shift 2 ;;
        -s|--specialty)   SPECIALTY="$2"; shift 2 ;;
        -t|--doc-type)    DOC_TYPE="$2"; shift 2 ;;
        --flashcards)     FLASHCARDS=true; shift ;;
        --model)          MODEL="$2"; shift 2 ;;
        --keep-temp)      KEEP_TEMP=true; shift ;;
        -v|--verbose)     VERBOSE=true; shift ;;
        -*)               die "Unknown option: $1" ;;
        *)                INPUT_FILE="$1"; shift ;;
    esac
done

[[ -z "$INPUT_FILE" ]] && die "No input file specified. Run with --help for usage."
[[ -f "$INPUT_FILE" ]] || die "Input file not found: $INPUT_FILE"

# ---- Locate scripts ---------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRACT_PY="$SCRIPT_DIR/extract_content.py"
DIGEST_PY="$SCRIPT_DIR/generate_digest.py"
FLASHCARD_PY="$SCRIPT_DIR/make_flashcards.py"

for f in "$EXTRACT_PY" "$DIGEST_PY" "$FLASHCARD_PY"; do
    [[ -f "$f" ]] || die "Required script not found: $f"
done

# ---- Setup output directory -------------------------------------------------
STEM=$(basename "$INPUT_FILE" | sed 's/\.[^.]*$//' | tr ' ' '_')
DATE_TAG=$(date +%Y%m%d)
WORK_DIR="$OUTPUT_DIR/${STEM}_${DATE_TAG}"
TEMP_DIR="$WORK_DIR/.tmp"

mkdir -p "$WORK_DIR" "$TEMP_DIR"
log "Output directory: $WORK_DIR"

# ---- Phase 1: Extract text from file ----------------------------------------
log "Phase 1: Extracting text from $(basename "$INPUT_FILE")..."

TEXT_FILE="$TEMP_DIR/extracted_text.txt"
INPUT_EXT="${INPUT_FILE##*.}"
INPUT_EXT_LOWER=$(echo "$INPUT_EXT" | tr '[:upper:]' '[:lower:]')

case "$INPUT_EXT_LOWER" in
    txt|md)
        cp "$INPUT_FILE" "$TEXT_FILE"
        ;;
    pdf)
        # Try pymupdf first, then fallback to pdf.py skill script
        if python3 -c "import fitz" 2>/dev/null; then
            python3 - <<PYEOF > "$TEXT_FILE"
import fitz, sys
doc = fitz.open("$INPUT_FILE")
text = "\n\n".join(page.get_text() for page in doc)
print(text)
PYEOF
        elif [[ -f "$SCRIPT_DIR/../../pdf/scripts/pdf.py" ]]; then
            python3 "$SCRIPT_DIR/../../pdf/scripts/pdf.py" extract.text "$INPUT_FILE" > "$TEXT_FILE"
        else
            die "PDF extraction requires pymupdf: pip install pymupdf\n  Or install the PDF skill."
        fi
        ;;
    docx|doc)
        if python3 -c "import docx" 2>/dev/null; then
            python3 - <<PYEOF > "$TEXT_FILE"
from docx import Document
doc = Document("$INPUT_FILE")
print("\n\n".join(p.text for p in doc.paragraphs if p.text.strip()))
PYEOF
        else
            die "DOCX extraction requires python-docx: pip install python-docx"
        fi
        ;;
    *)
        warn "Unknown extension '$INPUT_EXT' — treating as plain text."
        cp "$INPUT_FILE" "$TEXT_FILE"
        ;;
esac

WORD_COUNT=$(wc -w < "$TEXT_FILE" | tr -d ' ')
ok "Text extracted: ~${WORD_COUNT} words → $TEXT_FILE"

# ---- Phase 2: LLM extraction ------------------------------------------------
log "Phase 2: Structured content extraction..."

EXTRACTION_JSON="$TEMP_DIR/extraction.json"
CHUNKS_DIR="$TEMP_DIR/chunks"

if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
    warn "ANTHROPIC_API_KEY not set."
    warn "Automated extraction skipped."
    warn ""
    warn "To run automated extraction:"
    warn "  export ANTHROPIC_API_KEY=sk-ant-..."
    warn "  ./pipeline.sh $(basename "$INPUT_FILE")"
    warn ""
    warn "OR: run Claude manually with the extraction prompt from:"
    warn "  $SCRIPT_DIR/../references/extraction-prompt.md"
    warn "and save the result to: $EXTRACTION_JSON"
    warn ""
    warn "Then re-run with --keep-temp to skip extraction and go straight to digest."
    exit 0
fi

VERBOSE_FLAG=""
[[ "$VERBOSE" == "true" ]] && VERBOSE_FLAG="--verbose"

python3 "$EXTRACT_PY" "$TEXT_FILE" "$EXTRACTION_JSON" \
    --doc-type "$DOC_TYPE" \
    --specialty "$SPECIALTY" \
    --depth "$DEPTH" \
    --model "$MODEL" \
    --save-chunks "$CHUNKS_DIR" \
    $VERBOSE_FLAG

ok "Extraction complete → $EXTRACTION_JSON"

# ---- Phase 2b: Validate & survey --------------------------------------------
log "Validating extraction..."
python3 "$DIGEST_PY" validate "$EXTRACTION_JSON"
echo ""
python3 "$DIGEST_PY" stats "$EXTRACTION_JSON"
echo ""

# ---- Phase 3 & 4: Build output(s) ------------------------------------------
log "Phase 3/4: Generating digest output(s)..."

build_output() {
    local fmt="$1"
    local out_file=""

    case "$fmt" in
        html)
            out_file="$WORK_DIR/clinical_digest_${STEM}_${DATE_TAG}.html"
            python3 "$DIGEST_PY" build-html "$EXTRACTION_JSON" "$TEMP_DIR/images" "$out_file"
            ;;
        md|markdown)
            out_file="$WORK_DIR/clinical_digest_${STEM}_${DATE_TAG}.md"
            python3 "$DIGEST_PY" build-md "$EXTRACTION_JSON" "$out_file"
            ;;
        pdf)
            out_file="$WORK_DIR/clinical_digest_${STEM}_${DATE_TAG}.pdf"
            python3 "$DIGEST_PY" build-pdf "$EXTRACTION_JSON" "$TEMP_DIR/images" "$out_file"
            ;;
        *)
            warn "Unknown format: $fmt (skipping)"
            return
            ;;
    esac

    [[ -f "$out_file" ]] && ok "Generated: $out_file"
}

if [[ "$FORMAT" == "all" ]]; then
    for fmt in html md pdf; do
        build_output "$fmt"
    done
else
    build_output "$FORMAT"
fi

# ---- Phase 5: Flashcards (optional) -----------------------------------------
if [[ "$FLASHCARDS" == "true" ]]; then
    log "Generating flashcards..."
    CARD_PREFIX="$WORK_DIR/flashcards_${STEM}_${DATE_TAG}"
    python3 "$FLASHCARD_PY" "$EXTRACTION_JSON" \
        --format all \
        --output "$CARD_PREFIX" \
        --include pearls,traps
    ok "Flashcards generated: $CARD_PREFIX_*.{tsv,csv,md}"
fi

# ---- Cleanup ----------------------------------------------------------------
if [[ "$KEEP_TEMP" == "false" ]]; then
    rm -rf "$TEMP_DIR"
    log "Temporary files removed (use --keep-temp to retain)"
fi

# ---- Summary ----------------------------------------------------------------
echo ""
echo -e "${BOLD}========================================${RESET}"
echo -e "${GREEN}Digest complete!${RESET}"
echo -e "Output: ${CYAN}$WORK_DIR/${RESET}"
ls -lh "$WORK_DIR"/ 2>/dev/null || true
echo -e "${BOLD}========================================${RESET}"
