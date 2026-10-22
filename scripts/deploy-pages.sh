#!/usr/bin/env bash
# Deploy the learning website to Cloudflare Pages (plan 105 Phase F). Run by the user: this is a
# production deploy, never run by CI or tests.
#
#   bash scripts/deploy-pages.sh alias   # py4kids-alias: py4kids.futurespark.cc -> 301 to learn.futurespark.cc
#   bash scripts/deploy-pages.sh site    # py4kids:     site/dist   -> learn.futurespark.cc
#   bash scripts/deploy-pages.sh runner  # py4kids-run: runner/dist -> run-learn.futurespark.cc
#   bash scripts/deploy-pages.sh all     # runner, then site, then alias
#
# Needs CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN in the main checkout's .env (gitignored)
# and, for site/runner, a production build from `scripts/build-release.sh <tag>`. Each step
# creates its Pages project, custom domain and proxied CNAME when missing, then uploads.
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
ENV_FILE=${PY4KIDS_ENV_FILE:-/home/chris/workshop/py4kids_2/.env}
WRANGLER=(npx -y wrangler@4.151.3)
ZONE_NAME=futurespark.cc

[[ -f "$ENV_FILE" ]] || { echo "deploy-pages: no $ENV_FILE" >&2; exit 1; }
set -a; . "$ENV_FILE"; set +a
: "${CLOUDFLARE_ACCOUNT_ID:?missing in .env}" "${CLOUDFLARE_API_TOKEN:?missing in .env}"
export CLOUDFLARE_ACCOUNT_ID CLOUDFLARE_API_TOKEN

API=https://api.cloudflare.com/client/v4
AUTH=(-H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" -H "Content-Type: application/json")
ok() { python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["success"], [e["message"] for e in d.get("errors", [])])'; }

zone_id() {
  curl -s "${AUTH[@]}" "$API/zones?name=$ZONE_NAME" | python3 -c 'import sys,json; print(json.load(sys.stdin)["result"][0]["id"])'
}

# ensure <project> <custom domain> <dns label>
ensure() {
  local project=$1 domain=$2 label=$3 projects="$API/accounts/$CLOUDFLARE_ACCOUNT_ID/pages/projects" zone
  if ! curl -sf "${AUTH[@]}" "$projects/$project" >/dev/null; then
    echo -n "create project $project: "
    curl -s -X POST "${AUTH[@]}" "$projects" -d "{\"name\":\"$project\",\"production_branch\":\"main\"}" | ok
  fi
  if ! curl -s "${AUTH[@]}" "$projects/$project/domains" | grep -q "\"name\":\"$domain\""; then
    echo -n "attach $domain: "
    curl -s -X POST "${AUTH[@]}" "$projects/$project/domains" -d "{\"name\":\"$domain\"}" | ok
  fi
  zone=$(zone_id)
  if ! curl -s "${AUTH[@]}" "$API/zones/$zone/dns_records?name=$domain" | grep -q "\"name\":\"$domain\""; then
    echo -n "dns CNAME $domain -> $project.pages.dev: "
    curl -s -X POST "${AUTH[@]}" "$API/zones/$zone/dns_records" \
      -d "{\"type\":\"CNAME\",\"name\":\"$label\",\"content\":\"$project.pages.dev\",\"proxied\":true,\"comment\":\"py4kids learning website (Cloudflare Pages)\"}" | ok
  fi
}

upload() { # upload <project> <dir>
  (cd "$ROOT" && "${WRANGLER[@]}" pages deploy "$2" --project-name "$1" --branch main --commit-dirty=true)
}

production_built() {
  python3 - "$ROOT" <<'PY'
import json, sys, pathlib
root = pathlib.Path(sys.argv[1])
headers = (root / "site/dist/_headers").read_text()
if "https://run-learn.futurespark.cc" not in headers:
    sys.exit("deploy-pages: site/dist is not a production build (run scripts/build-release.sh <tag> first)")
PY
}

step() {
  case $1 in
    alias)  ensure py4kids-alias py4kids.futurespark.cc py4kids; upload py4kids-alias deploy/alias/public ;;
    runner) production_built; ensure py4kids-run run-learn.futurespark.cc run-learn; upload py4kids-run runner/dist ;;
    site)   production_built; ensure py4kids learn.futurespark.cc learn; upload py4kids site/dist ;;
    *) echo "usage: scripts/deploy-pages.sh alias|site|runner|all" >&2; exit 2 ;;
  esac
}

case ${1:-} in
  all) step runner; step site; step alias ;;
  *) step "${1:-}" ;;
esac
echo "deploy-pages: done ($*)"
