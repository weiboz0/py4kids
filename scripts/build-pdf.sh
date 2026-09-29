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
mkdir -p "$handouts"
# Every PDF built here is copied to output/<book>/ at the end (this script owns syllabus.pdf,
# patterns.pdf and handouts/ there; build-book.sh owns the <id>-*.pdf editions).
built=()

for unit_dir in "$book_root"/units/unit-*; do
    [[ -d "$unit_dir" ]] || continue
    unit_id="$(basename "$unit_dir")"
    exercise="$unit_dir/exercises.ipynb"
    if [[ ! -f "$exercise" ]]; then
        echo "FAIL: $unit_id: missing exercises.ipynb" >&2
        exit 1
    fi
    uv run jupyter nbconvert --to pdf --output "$unit_id" \
        --output-dir "$handouts" "$exercise"
    output="$handouts/$unit_id.pdf"
    if [[ ! -s "$output" ]]; then
        echo "FAIL: $unit_id: missing or empty PDF output" >&2
        exit 1
    fi
    built+=("$output")
done

pandoc "$book_root/syllabus.md" --pdf-engine=xelatex \
    -o "$book_root/build/syllabus.pdf"
if [[ ! -s "$book_root/build/syllabus.pdf" ]]; then
    echo "FAIL: $book: missing or empty syllabus PDF" >&2
    exit 1
fi
built+=("$book_root/build/syllabus.pdf")

if [[ "$build_patterns" == 1 ]]; then
    pandoc "$book_root/reference/patterns.md" --pdf-engine=xelatex \
        -o "$book_root/build/patterns.pdf"
    if [[ ! -s "$book_root/build/patterns.pdf" ]]; then
        echo "FAIL: $book: missing or empty patterns PDF" >&2
        exit 1
    fi
    built+=("$book_root/build/patterns.pdf")
fi

uv run python -m tools.publish_output --book "$book" --owner pdf "${built[@]}"

echo "build-pdf: $book PASS"
