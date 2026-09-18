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
if [[ "$book" == "book1" ]]; then
    if ! pattern_state="$(uv run python tools/patterns_doc.py --pdf-probe)"; then
        echo "$pattern_state" >&2
        echo "FAIL: book1: unable to validate pattern PDF inputs" >&2
        exit 1
    fi
    case "$pattern_state" in
        "empty") ;;
        "present") build_patterns=1 ;;
        *)
            echo "FAIL: book1: unexpected pattern PDF probe result: $pattern_state" >&2
            exit 1
            ;;
    esac
fi

handouts="$book_root/build/handouts"
mkdir -p "$handouts"

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
done

pandoc "$book_root/syllabus.md" --pdf-engine=xelatex \
    -o "$book_root/build/syllabus.pdf"
if [[ ! -s "$book_root/build/syllabus.pdf" ]]; then
    echo "FAIL: $book: missing or empty syllabus PDF" >&2
    exit 1
fi

if [[ "$build_patterns" == 1 ]]; then
    pandoc "$book_root/reference/patterns.md" --pdf-engine=xelatex \
        -o "$book_root/build/patterns.pdf"
    if [[ ! -s "$book_root/build/patterns.pdf" ]]; then
        echo "FAIL: book1: missing or empty patterns PDF" >&2
        exit 1
    fi
fi

echo "build-pdf: $book PASS"
