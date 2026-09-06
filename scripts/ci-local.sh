#!/usr/bin/env bash
# Authoritative local gate for py4kids.
set -euo pipefail
cd "$(dirname "$0")/.."

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

step "3/6 notebook execution + hygiene"
echo "SKIP (plan 003): solution-notebook execution, student-notebook hygiene, notebook-cell lint"

step "4/6 manifest + curriculum checks"
echo "SKIP (plan 003): manifest validation, prereq closure, practice coverage, stretch presence"

step "5/6 PDF build"
echo "SKIP (plan 003): PDF build"

step "6/6 pre-merge guard"
bash scripts/pre-merge-guard.sh

echo
echo "ci-local: ALL GREEN"
