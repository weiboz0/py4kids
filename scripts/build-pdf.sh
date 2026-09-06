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

echo "build-pdf: $book PASS"
