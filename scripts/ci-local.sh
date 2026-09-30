#!/usr/bin/env bash
# Authoritative local gate for py4kids.
set -euo pipefail
cd "$(dirname "$0")/.."
export PY4KIDS_CI=1

# --all-books renders every publication book's editions (required before a release); without it,
# step 5 renders only the books the change touches (design 010 D7).
scope_args=()
for arg in "$@"; do
  case "$arg" in
    --all-books) scope_args=(--all-books) ;;
    *) echo "usage: scripts/ci-local.sh [--all-books]" >&2; exit 2 ;;
  esac
done

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
# Handouts and the syllabus for every book, judge books included (design 010 D5); build-pdf.sh
# fails on a missing glyph. A publication book's editions render only when the change touches the
# book, or anything under tools/ or scripts/, or books.yaml (design 010 D7, tools/ci_scope.py), or
# with --all-books. publish-audit needs the render, so it is skipped with it; never silently.
rendered=()
skipped=()
while read -r book flags <&3; do
  bash scripts/build-pdf.sh --book "$book"
  if has_flag publication "$flags"; then
    decision="$(uv run python -m tools.ci_scope --book "$book" "${scope_args[@]}")"
    echo "book editions: $book: $decision"
    if [[ "$decision" == render:* ]]; then
      bash scripts/build-book.sh --book "$book"
      uv run py4kids-tools --book "$book" publish-audit
      rendered+=("$book")
    else
      echo "SKIP: $book: book editions and publish-audit (${decision#skip: })"
      skipped+=("$book")
    fi
  fi
done 3<<< "$books"
echo "book editions rendered: ${rendered[*]:-none}; skipped: ${skipped[*]:-none}"

step "6/6 pre-merge guard"
bash scripts/pre-merge-guard.sh

echo
echo "ci-local: ALL GREEN"
