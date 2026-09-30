#!/usr/bin/env bash
set -euo pipefail

export JUPYTER_CONFIG_DIR="$(mktemp -d)"
trap 'rm -rf "$JUPYTER_CONFIG_DIR"' EXIT

cd "$(dirname "$0")/.."

if [[ $# -ne 2 || "$1" != "--book" ]]; then
    echo "usage: scripts/build-pdf.sh --book <book-id>" >&2
    exit 2
fi

book="$2"
book_root="$PWD/$book"
if [[ ! -d "$book_root" ]]; then
    echo "FAIL: $book: book directory does not exist" >&2
    exit 1
fi

build_patterns=0
# The `patterns: true` book (books.yaml) also builds patterns.pdf.
is_patterns_book="$(uv run python -c 'import sys; from pathlib import Path; from tools.books import book_flag; print(int(book_flag(Path("."), sys.argv[1], "patterns")))' "$book")"
if [[ "$is_patterns_book" == 1 ]]; then
    if ! pattern_state="$(uv run python tools/patterns_doc.py --pdf-probe)"; then
        echo "$pattern_state" >&2
        echo "FAIL: $book: unable to validate pattern PDF inputs" >&2
        exit 1
    fi
    case "$pattern_state" in
        "empty") ;;
        "present") build_patterns=1 ;;
        *)
            echo "FAIL: $book: unexpected pattern PDF probe result: $pattern_state" >&2
            exit 1
            ;;
    esac
fi

handouts="$book_root/build/handouts"
# Every PDF is built in two steps (design 010 D4): nbconvert or pandoc writes the .tex, then
# lualatex compiles it in a kept folder under build/latex/, so its log can be checked for missing
# glyphs (tools/pdf_glyphs.py). The templates and py4kidsfonts.sty are in tools/pdf_templates/.
latex_root="$book_root/build/latex"
templates="$PWD/tools/pdf_templates"
mkdir -p "$handouts"
rm -rf "$latex_root"
# Every PDF built here is copied to output/<book>/ at the end (this script owns syllabus.pdf,
# patterns.pdf and handouts/ there; build-book.sh owns the <id>-*.pdf editions).
built=()

# compile <dir> <stem> <source dir>: lualatex <dir>/<stem>.tex with a kept log (a second pass
# only when the first asks for one), then the missing-glyph check on that log.
compile() {
    local dir="$1" stem="$2" source_dir="$3" pass
    for pass in 1 2; do
        if ! (cd "$dir" && TEXINPUTS="$templates:$source_dir:" \
                lualatex -interaction=nonstopmode -halt-on-error "$stem.tex" > /dev/null 2>&1); then
            echo "FAIL: $book: lualatex $dir/$stem.tex (log: $dir/$stem.log)" >&2
            tail -40 "$dir/$stem.log" >&2 || true
            exit 1
        fi
        grep -qE 'Rerun to get|rerunfilecheck Warning' "$dir/$stem.log" || break
    done
    uv run python -m tools.pdf_glyphs "$dir/$stem.log" > /dev/null
}

for unit_dir in "$book_root"/units/unit-*; do
    [[ -d "$unit_dir" ]] || continue
    unit_id="$(basename "$unit_dir")"
    exercise="$unit_dir/exercises.ipynb"
    if [[ ! -f "$exercise" ]]; then
        echo "FAIL: $unit_id: missing exercises.ipynb" >&2
        exit 1
    fi
    tex_dir="$latex_root/handouts/$unit_id"
    uv run jupyter nbconvert --to latex --template-file "$templates/handout.tex.j2" \
        --output "$unit_id" --output-dir "$tex_dir" "$exercise"
    compile "$tex_dir" "$unit_id" "$unit_dir"
    output="$handouts/$unit_id.pdf"
    cp "$tex_dir/$unit_id.pdf" "$output"
    if [[ ! -s "$output" ]]; then
        echo "FAIL: $unit_id: missing or empty PDF output" >&2
        exit 1
    fi
    built+=("$output")
done

# pandoc_pdf <markdown> <stem>: build/<stem>.pdf through tools/pdf_templates/pandoc.latex.
pandoc_pdf() {
    local source="$1" stem="$2"
    local tex_dir="$latex_root/$stem"
    mkdir -p "$tex_dir"
    pandoc "$source" -s --template "$templates/pandoc.latex" -o "$tex_dir/$stem.tex"
    compile "$tex_dir" "$stem" "$(dirname "$source")"
    cp "$tex_dir/$stem.pdf" "$book_root/build/$stem.pdf"
    if [[ ! -s "$book_root/build/$stem.pdf" ]]; then
        echo "FAIL: $book: missing or empty $stem PDF" >&2
        exit 1
    fi
    built+=("$book_root/build/$stem.pdf")
}

pandoc_pdf "$book_root/syllabus.md" syllabus

if [[ "$build_patterns" == 1 ]]; then
    pandoc_pdf "$book_root/reference/patterns.md" patterns
fi

uv run python -m tools.publish_output --book "$book" --owner pdf "${built[@]}"

echo "build-pdf: $book PASS"
