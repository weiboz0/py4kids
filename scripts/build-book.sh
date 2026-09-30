#!/usr/bin/env bash
# Build every edition named in tools/publish.py EDITIONS for a `publication: true` book (books.yaml),
# then copy the PDFs (<id>-<edition>.pdf) to output/<id>/.
# The editions render in parallel, each with its own TeX and Quarto caches;
# set BOOK_BUILD_PARALLEL=0 to render them one after another.
set -euo pipefail
cd "$(dirname "$0")/.."
if [ "${1:-}" != --book ] || [ -z "${2:-}" ] || [ "$#" != 2 ]; then
  echo 'usage: build-book.sh --book <publication book id>' >&2
  exit 2
fi
book="$2"
if ! .venv/bin/python -c 'import sys; from pathlib import Path; from tools.books import book_flag; sys.exit(not book_flag(Path("."), sys.argv[1], "publication"))' "$book"; then
  echo "FAIL: $book: not a publication book (books.yaml publication: true)" >&2
  exit 2
fi
# A publication book needs a valid <book>/publication.yaml (design 010 D1).
if ! .venv/bin/python -c '
import sys
from pathlib import Path
from tools.books import publication_config_errors
errors = publication_config_errors(Path("."), sys.argv[1])
for error in errors:
    print("FAIL: " + error, file=sys.stderr)
sys.exit(1 if errors else 0)
' "$book"; then
  exit 2
fi
export PATH="$HOME/.local/bin:$PATH"
cache_root="${TMPDIR:-/tmp}/py4kids-book-cache"
build_start=$SECONDS

# One line per edition: "<edition> <output name> <1 if it has an index, else 0>".
profiles="$(.venv/bin/python -c '
import sys
from tools.publish import EDITIONS, output_stem
for name, profile in EDITIONS.items():
    print(name, output_stem(sys.argv[1], name), int(profile["index"]))
' "$book")"

# Generate every Quarto project first (Python; fast, sequential).
while read -r edition _ _; do
  .venv/bin/py4kids-tools --book "$book" publish --edition "$edition" > /dev/null
done <<< "$profiles"

render() {
  local edition="$1" name="$2" index="$3"
  local project="$book/build/publish/$edition"
  export TEXMFCACHE="$cache_root/$edition/tex" XDG_CACHE_HOME="$cache_root/$edition/xdg"
  mkdir -p "$TEXMFCACHE" "$XDG_CACHE_HOME"
  local start=$SECONDS
  if ! quarto render "$project" --to pdf > "$project/render.log" 2>&1; then
    echo "FAIL: $edition: quarto render" >&2
    tail -80 "$project/render.log" >&2
    return 1
  fi
  # Draft-mode passes give the audit a clean LaTeX log (labels, references, overfull boxes).
  if ! (cd "$project" && for pass in 1 2; do
      lualatex -draftmode -interaction=nonstopmode -halt-on-error "$name.tex" > latex-audit.log 2>&1 || exit 1
      if [ "$index" = 1 ]; then
        makeindex "$name.idx" >> latex-audit.log 2>&1 || exit 1
      fi
    done); then
    echo "FAIL: $edition: LaTeX audit pass" >&2
    tail -80 "$project/latex-audit.log" >&2
    return 1
  fi
  echo "$((SECONDS-start))" > "$project/render-seconds.txt"
}

pids=()
editions=()
while read -r edition name index; do
  editions+=("$edition")
  if [ "${BOOK_BUILD_PARALLEL:-1}" = 0 ]; then
    render "$edition" "$name" "$index"
  else
    render "$edition" "$name" "$index" &
    pids+=("$!")
  fi
done <<< "$profiles"
failed=0
for pid in "${pids[@]}"; do
  wait "$pid" || failed=1
done
[ "$failed" = 0 ] || exit 1

pdfs=()
while read -r edition name _; do
  project="$book/build/publish/$edition"
  pdf="$project/_book/$name.pdf"
  pages="$(pdfinfo "$pdf" | awk '/^Pages:/ {print $2}')"
  echo "$edition render: $(cat "$project/render-seconds.txt")s, pages: $pages"
  pdfs+=("$pdf")
done <<< "$profiles"

.venv/bin/python -m tools.publish_output --book "$book" --owner book "${pdfs[@]}"
echo "build-book: ${#editions[@]} editions in $((SECONDS-build_start))s"
