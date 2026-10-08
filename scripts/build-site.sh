#!/usr/bin/env bash
# Build the learning website (design 012 part B; plan 103):
#   1. export every `site: true` book (books.yaml flags; no id is pinned) to site/content/<book>/
#   2. install the site's pinned dependencies (frozen lockfile) and run `astro build` to site/dist/
#   3. index the built pages with Pagefind (`pnpm -C site search-index`; self-hosted under /pagefind/)
#   4. run the slide audit (`pnpm -C site slide-audit`; <book>/site.yaml slides: limits)
#   5. build the Python runner (plan 104) to runner/dist/: its own origin, served beside the site
# Usage: scripts/build-site.sh [--release <tag>]   (the tag fills the bundles' PDF links)
set -euo pipefail
cd "$(dirname "$0")/.."

release=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --release) [[ $# -ge 2 ]] || { echo "usage: scripts/build-site.sh [--release <tag>]" >&2; exit 2; }
               release=(--release "$2"); shift 2 ;;
    *) echo "usage: scripts/build-site.sh [--release <tag>]" >&2; exit 2 ;;
  esac
done

# shellcheck source=scripts/site-env.sh
. scripts/site-env.sh
if ! site_node_env; then
  echo "FAIL: build-site: Node >= 22.12 is required (.nvmrc pins $(cat .nvmrc)); install it with: nvm install" >&2
  exit 1
fi
if ! site_pnpm; then
  echo "FAIL: build-site: pnpm not found (enable it with: corepack enable)" >&2
  exit 1
fi
echo "build-site: node $(node --version), pnpm $("${SITE_PNPM[@]}" --version)"

# 1. Export. The content directory is generated and gitignored: it is rebuilt from scratch so a
# book that loses its flag leaves nothing behind.
books="$(uv run python - <<'PY'
import yaml

catalog = yaml.safe_load(open("books.yaml", encoding="utf-8"))
print(" ".join(book["id"] for book in catalog["books"] if book.get("site") is True))
PY
)"
[[ -n "$books" ]] || { echo "FAIL: build-site: no book in books.yaml has site: true" >&2; exit 1; }
rm -rf site/content
for book in $books; do
  uv run py4kids-tools --book "$book" export "${release[@]}"
done

# 2. Build (Astro telemetry off: the build makes no call home).
export ASTRO_TELEMETRY_DISABLED=1
"${SITE_PNPM[@]}" -C site install --frozen-lockfile
"${SITE_PNPM[@]}" -C site build

# 3. Search: Pagefind indexes the pages that carry data-pagefind-body (plan 103 Phase E).
"${SITE_PNPM[@]}" -C site search-index
# 4. The slide audit (plan 103 D6): every slide within its book's limits, or allow-listed.
"${SITE_PNPM[@]}" -C site slide-audit
# 5. The runner (plan 104): the isolated Pyodide app, with the self-hosted Pyodide runtime.
"${SITE_PNPM[@]}" -C runner install --frozen-lockfile
"${SITE_PNPM[@]}" -C runner build

echo "build-site: built $(wc -w <<< "$books") book(s) to site/dist/ and the runner to runner/dist/"
