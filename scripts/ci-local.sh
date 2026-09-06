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
if ids != ["book1", "book2"]:
    sys.exit(f"FAIL: unexpected book registry: {ids}")
print("registry: book1 -> book2")
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

step "4/6 curriculum + assets"
uv run py4kids-tools --book book1 manifest-check
uv run py4kids-tools --book book1 prereq-check
uv run py4kids-tools --book book1 coverage-check
uv run py4kids-tools --book book1 stretch-check
uv run py4kids-tools --book book1 turtle-check

step "5/6 PDF build"
bash scripts/build-pdf.sh --book book1

step "6/6 pre-merge guard"
bash scripts/pre-merge-guard.sh

echo
echo "ci-local: ALL GREEN"
