#!/usr/bin/env bash
# Authoritative local gate for py4kids.
set -euo pipefail
cd "$(dirname "$0")/.."
export PY4KIDS_CI=1

# --all-books renders every publication book's editions (required before a release); without it,
# step 5 renders only the books the change touches and step 6 builds the site only when the change
# touches it (design 010 D7).
scope_args=()
for arg in "$@"; do
  case "$arg" in
    --all-books) scope_args=(--all-books) ;;
    *) echo "usage: scripts/ci-local.sh [--all-books]" >&2; exit 2 ;;
  esac
done

step() { echo; echo "=== $1 ==="; }

step "1/7 registry + lint"
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
    flags = [flag for flag in ("publication", "judge", "patterns", "acsl", "site") if book.get(flag) is True]
    print(book["id"], *flags)
PY
)"
echo "registry: $(cut -d' ' -f1 <<< "$books" | paste -sd' ')"
uv run ruff check tools/ tests/ scripts/ recsys/projects/bookrec recsys/data

# Committed GloVe subset (design 011 §6): a REAL, executed integrity check (never a skip) --
# the tracked .npy must match its sidecar sha256 and stay under the 1 MB publish-safe cap.
# (tools.glove_integrity discovers the artifact itself; no book id is pinned here.)
uv run python -m tools.glove_integrity

# `dependency_group` is a routing VALUE (design 011 §7), read as a SEPARATE line from the boolean
# feature flags above: "<id> <group-or-empty>". A book with a group runs its heavy notebook/exec
# and test commands under `uv run --group <group>`; a group-free book runs plain `uv run`.
groups="$(uv run python - <<'PY'
import yaml

catalog = yaml.safe_load(open("books.yaml", encoding="utf-8"))
for book in catalog["books"]:
    print(book["id"], book.get("dependency_group") or "")
PY
)"
declare -A GROUP
while read -r gid ggrp; do GROUP["$gid"]="$ggrp"; done <<< "$groups"

has_flag() { [[ " $2 " == *" $1 "* ]]; }

# Run a py4kids-tools check for a book, routed through its dependency group when it declares one.
book_run() {
  local book="$1"; shift
  local grp="${GROUP[$book]:-}"
  if [[ -n "$grp" ]]; then
    uv run --group "$grp" py4kids-tools --book "$book" "$@"
  else
    uv run py4kids-tools --book "$book" "$@"
  fi
}

step "2/7 unit tests"
# The global suite stays GROUP-FREE: it must not require any book's dependency group (design 011
# §7). A routed book's own tests live OUTSIDE tests/ (under its <root>/**/tests/) precisely so this
# run does not import that book's heavy stack.
uv run pytest -q

# Routed per-book suites: a book with a dependency_group runs its own tests under that group. For a
# book that ships a data/ generator substrate (design 011 §6/§9), CI first REGENERATES the seeded
# catalog + interactions (nothing is committed — output is gitignored), then runs the invariant +
# package tests against fresh output, so the substrate is verified every run without tracked data.
# PYTHONHASHSEED pins hash-dependent iteration for the routed (heavy/ML) commands (design 011 §7
# determinism contract); the seeded generators already thread one numpy rng and normalise gzip mtime.
while read -r book grp <&3; do
  [[ -n "$grp" ]] || continue
  echo "routed suite: $book (uv run --group $grp)"
  if [[ -f "$book/data/gen_catalog.py" && -f "$book/data/gen_interactions.py" ]]; then
    PYTHONHASHSEED=0 uv run --group "$grp" python "$book/data/gen_catalog.py"
    PYTHONHASHSEED=0 uv run --group "$grp" python "$book/data/gen_interactions.py"
  fi
  PYTHONHASHSEED=0 uv run --group "$grp" pytest -q "$book"
done 3<<< "$groups"

step "3/7 notebook structure + execution"
while read -r book flags <&3; do
  for check in hygiene-check structure-check noexec-check cell-lint milestone-check exec-solutions exec-lessons; do
    book_run "$book" "$check"
  done
  if has_flag publication "$flags"; then
    book_run "$book" lesson-outputs-check
  fi
done 3<<< "$books"

step "4/7 curriculum + assets"
# Per-entry checks iterate existing dirs, so they cover authored entries and are inert for
# unauthored ones. Flag-gated checks follow each book's books.yaml flags (see the comments there);
# books without `judge` run the turtle checks. Fastforward relaxation keys on prereq_policy.
while read -r book flags <&3; do
  for check in manifest-check prereq-check coverage-check concept-scan; do
    book_run "$book" "$check"
  done
  if has_flag patterns "$flags"; then
    for check in technique-spiral pattern-marker patterns-doc-check; do
      book_run "$book" "$check"
    done
  fi
  book_run "$book" stretch-check
  if has_flag judge "$flags"; then
    book_run "$book" judge-check
    book_run "$book" source-policy
  else
    book_run "$book" turtle-check
    book_run "$book" turtle-real-check
  fi
  if has_flag acsl "$flags"; then
    book_run "$book" acsl-check
  fi
  # The learning-website export (design 012; plan 101): prints its INFO:/WARN: lines and fails on
  # FAIL:. Its findings are cached by committed tree hashes, so the unit-test run above (which
  # checks the same books) is not repeated on a clean tree.
  if has_flag site "$flags"; then
    book_run "$book" site-check
  fi
done 3<<< "$books"

step "5/7 PDF build"
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

step "6/7 site"
# The learning website (design 012 part B; plan 103): build-site.sh exports every `site: true`
# book and builds site/ with Astro, then the site's vitest suite runs. It needs Node >= 22.12
# (.nvmrc; activated through nvm when the shell's default is older), pnpm and a Chromium. The
# build is scoped like the editions (design 010 D7): it runs when the change touches site/, tools/,
# scripts/, books.yaml, .nvmrc or a site book (tools/ci_scope.py --site), or with --all-books.
# Every skip is printed; never silent.
. scripts/site-env.sh
if ! site_node_env; then
  echo "SKIP (Node missing): site build and tests need node >= 22.12 (.nvmrc; nvm install)"
elif ! site_pnpm; then
  echo "SKIP: site (pnpm missing; corepack enable)"
elif ! site_chromium; then
  echo "SKIP: site (Chromium missing)"
else
  decision="$(uv run python -m tools.ci_scope --site "${scope_args[@]}")"
  echo "site: $decision"
  if [[ "$decision" == render:* ]]; then
    bash scripts/build-site.sh
    "${SITE_PNPM[@]}" -C site test
  else
    echo "SKIP: site (${decision#skip: })"
  fi
fi

step "7/7 pre-merge guard"
bash scripts/pre-merge-guard.sh

echo
echo "ci-local: ALL GREEN"
