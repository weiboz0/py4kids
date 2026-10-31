#!/usr/bin/env bash
set -euo pipefail

repo_root=$(git rev-parse --show-toplevel)
archive_dir=$(mktemp -d)
trap 'rm -rf "$archive_dir"' EXIT

git -C "$repo_root" archive --format=tar HEAD | tar -xf - -C "$archive_dir"
cd "$archive_dir"

if [[ -n "${AIO_REFERENCE_CACHE:-}" && -d "$AIO_REFERENCE_CACHE" ]]; then
  mkdir -p aio-ml/reference/cache
  cp -a "$AIO_REFERENCE_CACHE"/. aio-ml/reference/cache/
fi

bash scripts/ci-local.sh
