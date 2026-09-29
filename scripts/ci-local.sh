#!/usr/bin/env bash
# Authoritative local gate for py4kids.
set -euo pipefail
cd "$(dirname "$0")/.."
export PY4KIDS_CI=1

step() { echo; echo "=== $1 ==="; }

step "1/6 registry + lint"
# The book list and each book's feature flags come from books.yaml (design 008); nothing here pins
# a book id. One line per book: "<id> <flag> <flag> ...".
books="$(uv run python - <<'PY'
import sys
from pathlib import Path

import yaml

catalog = yaml.safe_load(open("books.yaml", encoding="utf-8"))
if catalog.get("books_version") != 2:
    sys.exit("FAIL: books.yaml books_version must be 2")
for book in catalog["books"]:
    if book.get("root") != book["id"] or not Path(book["root"]).is_dir():
        sys.exit(f"FAIL: book {book['id']!r}: root must equal the id and exist")
    flags = [flag for flag in ("publication", "judge", "patterns", "acsl") if book.get(flag) is True]
    print(book["id"], *flags)
PY
)"
echo "registry: $(cut -d' ' -f1 <<< "$books" | paste -sd' ')"
uv run ruff check tools/ tests/ scripts/

has_flag() { [[ " $2 " == *" $1 "* ]]; }

step "2/6 unit tests"
uv run pytest -q

step "3/6 notebook structure + execution"
while read -r book flags <&3; do
  for check in hygiene-check structure-check noexec-check cell-lint exec-solutions exec-lessons; do
    uv run py4kids-tools --book "$book" "$check"
  done
  if has_flag publication "$flags"; then
    uv run py4kids-tools --book "$book" lesson-outputs-check
  fi
done 3<<< "$books"

step "4/6 curriculum + assets"
# Per-entry checks iterate existing dirs, so they cover authored entries and are inert for
# unauthored ones. Flag-gated checks follow each book's books.yaml flags (see the comments there);
# books without `judge` run the turtle checks. Fastforward relaxation keys on prereq_policy.
while read -r book flags <&3; do
  for check in manifest-check prereq-check coverage-check concept-scan; do
    uv run py4kids-tools --book "$book" "$check"
  done
  if has_flag patterns "$flags"; then
    for check in technique-spiral pattern-marker patterns-doc-check; do
      uv run py4kids-tools --book "$book" "$check"
    done
  fi
  uv run py4kids-tools --book "$book" stretch-check
  if has_flag judge "$flags"; then
    uv run py4kids-tools --book "$book" judge-check
    uv run py4kids-tools --book "$book" source-policy
  else
    uv run py4kids-tools --book "$book" turtle-check
    uv run py4kids-tools --book "$book" turtle-real-check
  fi
  if has_flag acsl "$flags"; then
    uv run py4kids-tools --book "$book" acsl-check
  fi
done 3<<< "$books"

step "5/6 PDF build"
# Handouts and syllabus PDFs for the Python books (contest books build no PDFs yet); the
# publication pipeline for `publication: true` books.
while read -r book flags <&3; do
  if ! has_flag judge "$flags"; then
    bash scripts/build-pdf.sh --book "$book"
  fi
  if has_flag publication "$flags"; then
    bash scripts/build-book.sh --book "$book"
    uv run py4kids-tools --book "$book" publish-audit
  fi
done 3<<< "$books"

step "6/6 pre-merge guard"
bash scripts/pre-merge-guard.sh

echo
echo "ci-local: ALL GREEN"
