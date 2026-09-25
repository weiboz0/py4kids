#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ "${1:-}" != --book ] || [ "${2:-}" != book1b ] || [ "$#" != 2 ]; then
  echo 'usage: build-book.sh --book book1b' >&2
  exit 2
fi
export PATH="$HOME/.local/bin:$PATH"
export TEXMFCACHE="${TMPDIR:-/tmp}/py4kids-tex-cache"
export XDG_CACHE_HOME="${TMPDIR:-/tmp}/py4kids-xdg-cache"
mkdir -p "$TEXMFCACHE" "$XDG_CACHE_HOME"
for edition in student teacher; do
  project="book1b/build/publish/$edition"
  .venv/bin/py4kids-tools --book book1b publish --edition "$edition"
  start=$SECONDS
  quarto render "$project" --to pdf > "$project/render.log" 2>&1 || {
    tail -80 "$project/render.log" >&2
    exit 1
  }
  render_seconds=$((SECONDS-start))
  name="Book1b-${edition^}"
  (cd "$project" && for pass in 1 2; do
    lualatex -draftmode -interaction=nonstopmode -halt-on-error "$name.tex" > latex-audit.log 2>&1 || exit 1
  done) || {
    tail -80 "$project/latex-audit.log" >&2
    exit 1
  }
  echo "$edition render: ${render_seconds}s"
  pdf="$project/_book/Book1b-${edition^}.pdf"
  pdfinfo "$pdf" | awk '/^Pages:/ {print "pages: " $2}'
done
