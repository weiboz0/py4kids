#!/usr/bin/env bash
# Build a deployable release of the learning website (design 012 D1; plan 105 Phase D).
# NOTHING here deploys: `wrangler pages deploy` runs only in plan 105 Phase F, after the user
# confirms and provides the hosting account (AGENTS.md hard safeguard).
#
#   1. Refuse a build with the test-only service-worker hooks (PY4KIDS_TEST_HOOKS) in it.
#   2. Stand-in build: both apps built with `--release <tag>` (the PDF links point at that GitHub
#      Release) for two local origins standing in for production (the PY4KIDS_SITE_ORIGIN /
#      PY4KIDS_RUNNER_ORIGIN overrides, else deploy/origins.json "local"), and the full site test
#      suite run against it: site and runner unit tests, the site's Python checks, and the browser
#      suites (Playwright `site` and `lighthouse` projects).
#   3. With --target production (the default): rebuild for the production origins in
#      deploy/origins.json (plus the preview pair) and rerun the unit tests on that build, so
#      site/dist/ and runner/dist/ are the deployable release. A placeholder (`.example`)
#      production domain is refused: set the real one first (Phase F).
#      With --target stand-in: stop after step 2 (the stand-in build stays in the dists).
# Every build fails on a file over Cloudflare Pages' 25 MiB limit and writes release.json
# (release_id) into both dists (deploy/release.mjs).
#
# Usage: scripts/build-release.sh <tag> [--target production|stand-in] [--skip-e2e]
set -euo pipefail
cd "$(dirname "$0")/.."

usage() { echo "usage: scripts/build-release.sh <tag> [--target production|stand-in] [--skip-e2e]" >&2; exit 2; }
[[ $# -ge 1 ]] || usage
tag="$1"; shift
[[ "$tag" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || { echo "FAIL: build-release: not a release tag: $tag" >&2; exit 2; }
target=production
e2e=1
while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) [[ $# -ge 2 ]] || usage; target="$2"; shift 2 ;;
    --skip-e2e) e2e=0; shift ;;
    *) usage ;;
  esac
done
[[ "$target" == production || "$target" == stand-in ]] || usage

if [[ -n "${PY4KIDS_TEST_HOOKS:-}" ]]; then
  echo "FAIL: build-release: PY4KIDS_TEST_HOOKS is set; a release never carries the test-only hooks" >&2
  exit 1
fi

# shellcheck source=scripts/site-env.sh
. scripts/site-env.sh
site_node_env || { echo "FAIL: build-release: Node >= 22.12 is required" >&2; exit 1; }
site_pnpm || { echo "FAIL: build-release: pnpm not found" >&2; exit 1; }

if [[ "$target" == production ]]; then
  # Refuse early (before the long stand-in build) when production still has the placeholder.
  PY4KIDS_TARGET=production PY4KIDS_SITE_ORIGIN= PY4KIDS_RUNNER_ORIGIN= node --input-type=module -e '
    import { resolveOrigins, isPlaceholder } from "./deploy/origins.mjs";
    const { primary } = resolveOrigins({ env: { PY4KIDS_TARGET: "production" } });
    if (isPlaceholder(primary)) {
      console.error(`FAIL: build-release: deploy/origins.json "production" is still the placeholder ${primary.site}; set the real domain (plan 105 Phase F) or use --target stand-in`);
      process.exit(1);
    }'
fi

echo "build-release: stand-in build for ${PY4KIDS_SITE_ORIGIN:-local site} / ${PY4KIDS_RUNNER_ORIGIN:-local runner} (release $tag)"
PY4KIDS_TARGET=local bash scripts/build-site.sh --release "$tag"
PY4KIDS_TARGET=local "${SITE_PNPM[@]}" -C site test
"${SITE_PNPM[@]}" -C runner test
uv run pytest -q tests/test_site_*.py tests/test_runner_harness.py
if [[ "$e2e" == 1 ]]; then
  PY4KIDS_TARGET=local "${SITE_PNPM[@]}" -C site e2e
fi

if [[ "$target" == stand-in ]]; then
  echo "build-release: stand-in release $tag built and verified (site/dist, runner/dist); not a production build"
  exit 0
fi

echo "build-release: production build (release $tag)"
export PY4KIDS_TARGET=production
unset PY4KIDS_SITE_ORIGIN PY4KIDS_RUNNER_ORIGIN
bash scripts/build-site.sh --release "$tag"
"${SITE_PNPM[@]}" -C site test
"${SITE_PNPM[@]}" -C runner test
echo "build-release: production release $tag built in site/dist and runner/dist ($(node -e 'console.log(JSON.parse(require("fs").readFileSync("site/dist/release.json","utf8")).release_id)'))"
echo "build-release: not deployed (plan 105 Phase F deploys, after the user confirms)"
