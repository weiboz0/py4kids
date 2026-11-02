#!/usr/bin/env bash
# Fill the aio books' git-ignored external-artifact cache (design 014 D8).
#
# Usage: scripts/aio/aio-provision-cache.sh [--root REPO]
#
# Reads the artifact manifest <REPO>/<round-1 book>/curriculum/artifacts.yaml (REPO defaults to
# this script's repository; the round-1 book is the `content_model: aio`, `aio_round: 1` entry of
# <REPO>/books.yaml, so no book root is hard-coded) and, for every artifact:
#   - file present with the recorded SHA-256  -> skip;
#   - otherwise download it (curl -fsSL --retry 3) to <path>.tmp, verify the SHA-256, mv into place;
#   - a SHA-256 mismatch after download        -> loud failure, non-zero exit (nothing moved).
# Idempotent: a second run over a provisioned cache downloads nothing.
#
# Manifest schema (version 1):
#   schema: 1
#   artifacts:
#     - id: <unique name>
#       url: https://...                 # public source (file:// only with AIO_PROVISION_ALLOW_FILE_URLS=1)
#       path: <book>/reference/cache/... # repo-relative destination, always under a reference/cache/
#       sha256: <64 lowercase hex>
#       size: <bytes>                    # optional, informational
#       consumers: [...]                 # optional, informational
#
# The manifest is parsed by Python + PyYAML: $AIO_PYTHON if set, else this repository's uv
# project (`uv run --frozen python`; pyyaml is a core dependency, so no group is needed).
set -euo pipefail

TOOL_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ROOT="$TOOL_ROOT"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --root)
            [[ $# -ge 2 ]] || { echo "aio-provision-cache: --root needs a value" >&2; exit 2; }
            ROOT="$2"; shift 2 ;;
        -h|--help)
            sed -n '2,4p' "$0"; exit 0 ;;
        *)
            echo "aio-provision-cache: unknown argument: $1" >&2; exit 2 ;;
    esac
done

ROOT="$(cd "$ROOT" && pwd)"

if [[ -n "${AIO_PYTHON:-}" ]]; then
    PY=("$AIO_PYTHON")
else
    PY=(uv run --project "$TOOL_ROOT" --frozen python)
fi

# The round-1 aio book's root, from registry data (design 014 D1).
read -r -d '' ROUND1_PARSER <<'PYEOF' || true
import sys
import yaml

registry = sys.argv[1]
try:
    books = yaml.safe_load(open(registry, encoding="utf-8"))["books"]
except Exception as exc:
    sys.exit(f"aio-provision-cache: FAIL {registry}: cannot read the book registry ({exc})")
roots = [
    book.get("root") for book in books
    if isinstance(book, dict) and book.get("content_model") == "aio" and book.get("aio_round") == 1
]
if len(roots) != 1 or not isinstance(roots[0], str) or not roots[0]:
    sys.exit(f"aio-provision-cache: FAIL {registry}: expected one aio_round 1 book, found {len(roots)}")
print(roots[0])
PYEOF
ROUND1_ROOT="$("${PY[@]}" -I -c "$ROUND1_PARSER" "$ROOT/books.yaml")"
MANIFEST="$ROOT/$ROUND1_ROOT/curriculum/artifacts.yaml"
[[ -f "$MANIFEST" ]] || { echo "aio-provision-cache: FAIL no manifest at $MANIFEST" >&2; exit 1; }

# Validate the manifest and emit one TAB-separated line per artifact: id url path sha256.
read -r -d '' PARSER <<'PYEOF' || true
import re, sys
import yaml

manifest, allow_file = sys.argv[1], sys.argv[2] == "1"
def die(msg):
    sys.exit(f"aio-provision-cache: FAIL {manifest}: {msg}")
try:
    data = yaml.safe_load(open(manifest, encoding="utf-8"))
except Exception as exc:
    die(f"unparseable YAML ({exc})")
if not isinstance(data, dict) or data.get("schema") != 1:
    die("expected a mapping with `schema: 1`")
arts = data.get("artifacts")
if not isinstance(arts, list) or not arts:
    die("`artifacts` must be a non-empty list")
seen_ids, seen_paths = set(), set()
for i, a in enumerate(arts):
    if not isinstance(a, dict):
        die(f"artifact #{i} is not a mapping")
    for key in ("id", "url", "path", "sha256"):
        if not isinstance(a.get(key), str) or not a[key].strip():
            die(f"artifact #{i}: missing or non-string `{key}`")
    aid, url, path, sha = a["id"], a["url"], a["path"], a["sha256"]
    if any(c in v for v in (aid, url, path, sha) for c in "\t\n\r"):
        die(f"{aid}: control characters in a field")
    if aid in seen_ids:
        die(f"duplicate id {aid}")
    seen_ids.add(aid)
    if not re.fullmatch(r"[0-9a-f]{64}", sha):
        die(f"{aid}: sha256 must be 64 lowercase hex characters")
    if not (url.startswith("https://") or (allow_file and url.startswith("file://"))):
        die(f"{aid}: url must be https:// ({url})")
    parts = path.split("/")
    if path.startswith("/") or ".." in parts or "" in parts or "." in parts:
        die(f"{aid}: path must be a normalized repo-relative path ({path})")
    if "/reference/cache/" not in "/" + path:
        die(f"{aid}: path must lie under a reference/cache/ directory ({path})")
    if path in seen_paths:
        die(f"duplicate path {path}")
    seen_paths.add(path)
    print("\t".join((aid, url, path, sha)))
PYEOF

LINES="$("${PY[@]}" -I -c "$PARSER" "$MANIFEST" "${AIO_PROVISION_ALLOW_FILE_URLS:-0}")"

sha_of() { sha256sum "$1" | cut -d' ' -f1; }

fetched=0; skipped=0
while IFS=$'\t' read -r id url rel sha; do
    dest="$ROOT/$rel"
    if [[ -f "$dest" ]] && [[ "$(sha_of "$dest")" == "$sha" ]]; then
        echo "aio-provision-cache: OK   $id (present, sha256 verified)"
        skipped=$((skipped + 1))
        continue
    fi
    if [[ -e "$dest" ]]; then
        echo "aio-provision-cache: WARN $id: $rel has the wrong sha256; re-fetching" >&2
    fi
    mkdir -p "$(dirname "$dest")"
    tmp="$dest.tmp"
    rm -f "$tmp"
    echo "aio-provision-cache: GET  $id <- $url"
    if ! curl -fsSL --retry 3 -o "$tmp" "$url"; then
        rm -f "$tmp"
        echo "aio-provision-cache: FAIL $id: download failed ($url)" >&2
        exit 1
    fi
    got="$(sha_of "$tmp")"
    if [[ "$got" != "$sha" ]]; then
        rm -f "$tmp"
        echo "aio-provision-cache: FAIL $id: sha256 MISMATCH for $url" >&2
        echo "aio-provision-cache:      expected $sha" >&2
        echo "aio-provision-cache:      got      $got" >&2
        exit 1
    fi
    mv -f "$tmp" "$dest"
    echo "aio-provision-cache: OK   $id (fetched, sha256 verified)"
    fetched=$((fetched + 1))
done <<< "$LINES"

echo "aio-provision-cache: PASS ($fetched fetched, $skipped already present)"
