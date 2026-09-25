#!/usr/bin/env bash
# Authoritative local gate for py4kids.
set -euo pipefail
cd "$(dirname "$0")/.."
export PY4KIDS_CI=1

step() { echo; echo "=== $1 ==="; }

step "1/6 registry + lint"
uv run python - <<'PY'
import sys

import yaml

catalog = yaml.safe_load(open("books.yaml", encoding="utf-8"))
ids = [book["id"] for book in catalog["books"]]
if ids != ["book1", "book1b", "book2"]:
    sys.exit(f"FAIL: unexpected book registry: {ids}")
print("registry: book1 -> book1b -> book2")
PY
uv run ruff check tools/ tests/ scripts/

step "2/6 unit tests"
uv run pytest -q

step "3/6 notebook structure + execution"
uv run py4kids-tools --book book1 hygiene-check
uv run py4kids-tools --book book1 structure-check
uv run py4kids-tools --book book1 noexec-check
uv run py4kids-tools --book book1 cell-lint
uv run py4kids-tools --book book1 exec-solutions
uv run py4kids-tools --book book1 exec-lessons
if [ -d book1b ]; then
  uv run py4kids-tools --book book1b lesson-outputs-check
fi

step "4/6 curriculum + assets"
uv run py4kids-tools --book book1 manifest-check
uv run py4kids-tools --book book1 prereq-check
uv run py4kids-tools --book book1 coverage-check
uv run py4kids-tools --book book1 concept-scan
uv run py4kids-tools --book book1 technique-spiral
uv run py4kids-tools --book book1 pattern-marker
uv run py4kids-tools --book book1 patterns-doc-check
uv run py4kids-tools --book book1 stretch-check
uv run py4kids-tools --book book1 turtle-check

# Book 2: map-level checks + per-entry checks (per-entry iterate existing dirs, so they cover
# authored units and are inert for unauthored entries).
uv run py4kids-tools --book book2 prereq-check
uv run py4kids-tools --book book2 coverage-check
uv run py4kids-tools --book book2 concept-scan
uv run py4kids-tools --book book2 manifest-check
uv run py4kids-tools --book book2 structure-check
uv run py4kids-tools --book book2 hygiene-check
uv run py4kids-tools --book book2 cell-lint
uv run py4kids-tools --book book2 noexec-check
uv run py4kids-tools --book book2 stretch-check
uv run py4kids-tools --book book2 exec-solutions
uv run py4kids-tools --book book2 exec-lessons
uv run py4kids-tools --book book2 judge-check
uv run py4kids-tools --book book2 source-policy

# Book 1b: concept-first variant, now COMPLETE (fastforward relaxation keys on its per-book flag; the
# buildout flag was removed in plan 078, so introduction-completeness + lesson-lower-bound now apply).
# Per-entry checks iterate existing dirs, so they cover authored units and are inert for
# unauthored entries. Existence-guarded so this block is a no-op until book1b/ exists. No Book-1-only
# pattern checks (technique-spiral/pattern-marker/patterns-doc are hard-gated to book1); no book2-only
# judge-check/source-policy.
if [ -d book1b ]; then
  uv run py4kids-tools --book book1b coverage-check
  uv run py4kids-tools --book book1b prereq-check
  uv run py4kids-tools --book book1b concept-scan
  uv run py4kids-tools --book book1b manifest-check
  uv run py4kids-tools --book book1b structure-check
  uv run py4kids-tools --book book1b hygiene-check
  uv run py4kids-tools --book book1b cell-lint
  uv run py4kids-tools --book book1b noexec-check
  uv run py4kids-tools --book book1b stretch-check
  uv run py4kids-tools --book book1b turtle-check
  uv run py4kids-tools --book book1b exec-solutions
  uv run py4kids-tools --book book1b exec-lessons
fi

step "5/6 PDF build"
bash scripts/build-pdf.sh --book book1
[ -d book1b ] && bash scripts/build-pdf.sh --book book1b
[ -d book1b ] && bash scripts/build-book.sh --book book1b
[ -d book1b ] && uv run py4kids-tools --book book1b publish-audit

step "6/6 pre-merge guard"
bash scripts/pre-merge-guard.sh

echo
echo "ci-local: ALL GREEN"
