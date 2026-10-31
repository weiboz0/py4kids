#!/usr/bin/env bash
# Clean-checkout verification for py4kids with the aio books (plan aio-001 Phase D / F.2).
#
# 1. `git clone` the current branch's HEAD into a fresh directory under /dev/shm
#    (nothing from the working tree: only committed content).
# 2. Provision step B INTO the clone, from sources outside it:
#      scripts/aio/fetch-reference.sh --root <clone> --all     (the 2026 past papers)
#      scripts/aio/aio-provision-cache.sh --root <clone>       (the external-artifact cache)
#    AIO_REFERENCE_SOURCE=<dir> replaces the fetch with a copy of a local corpus: for every
#    registered aio book root R, <dir>/R/reference/ is copied into <clone>/R/reference/
#    (fetch-reference only covers the 2026 papers; the scanner's local index.yaml files and
#    older papers can only come from a local corpus). <dir> must lie outside the clone.
# 3. Run `bash scripts/ci-local.sh` in the clone (TMPDIR=/dev/shm).
# 4. Assert `git -C <clone> status --porcelain --ignored` lists every provisioned file as
#    ignored, and nothing as tracked-modified or untracked-unignored.
#
# Overrides (tests stub them): AIO_CLEAN_CHECKOUT_PARENT (default /dev/shm),
# AIO_CLEAN_CHECKOUT_FETCH, AIO_CLEAN_CHECKOUT_PROVISION, AIO_CLEAN_CHECKOUT_CI (commands run
# with the clone as cwd and CLONE exported), AIO_CLEAN_CHECKOUT_KEEP=1 keeps the clone.
set -euo pipefail

repo_root=$(git rev-parse --show-toplevel)
head_sha=$(git -C "$repo_root" rev-parse HEAD)
branch=$(git -C "$repo_root" rev-parse --abbrev-ref HEAD)
parent=${AIO_CLEAN_CHECKOUT_PARENT:-/dev/shm}
clone=$(mktemp -d "$parent/aio-clean-checkout.XXXXXX")
if [[ ${AIO_CLEAN_CHECKOUT_KEEP:-0} != 1 ]]; then
  trap 'rm -rf "$clone"' EXIT
fi
export CLONE=$clone

echo "verify-clean-checkout: cloning $branch ($head_sha) into $clone"
git clone --quiet --no-hardlinks "$repo_root" "$clone"
git -C "$clone" checkout --quiet --detach "$head_sha"

aio_roots=$(cd "$clone" && uv run --frozen python - <<'PY'
from tools.books import books_with_content_model, book_entry
from pathlib import Path
root = Path(".").resolve()
for book in books_with_content_model(root, "aio"):
    print(book_entry(root, book)["root"])
PY
)

if [[ -n ${AIO_CLEAN_CHECKOUT_FETCH:-} ]]; then
  (cd "$clone" && bash -c "$AIO_CLEAN_CHECKOUT_FETCH")
elif [[ -n ${AIO_REFERENCE_SOURCE:-} ]]; then
  source_dir=$(cd "$AIO_REFERENCE_SOURCE" && pwd -P)
  clone_real=$(cd "$clone" && pwd -P)
  case "$source_dir/" in
    "$clone_real"/*) echo "FAIL: AIO_REFERENCE_SOURCE lies inside the clone" >&2; exit 1 ;;
  esac
  while IFS= read -r book_root; do
    [[ -n $book_root ]] || continue
    if [[ ! -d "$source_dir/$book_root/reference" ]]; then
      echo "FAIL: AIO_REFERENCE_SOURCE has no $book_root/reference/" >&2
      exit 1
    fi
    echo "verify-clean-checkout: copying $source_dir/$book_root/reference/ into the clone"
    cp -a "$source_dir/$book_root/reference/." "$clone/$book_root/reference/"
  done <<<"$aio_roots"
else
  bash "$clone/scripts/aio/fetch-reference.sh" --root "$clone" --all
fi

if [[ -n ${AIO_CLEAN_CHECKOUT_PROVISION:-} ]]; then
  (cd "$clone" && bash -c "$AIO_CLEAN_CHECKOUT_PROVISION")
else
  bash "$clone/scripts/aio/aio-provision-cache.sh" --root "$clone"
fi

# Every untracked file under an aio book's reference/ is a provisioned file.
provisioned=$(cd "$clone" && while IFS= read -r book_root; do
  [[ -n $book_root ]] || continue
  git ls-files --others --ignored --exclude-standard -- "$book_root/reference"
  git ls-files --others --exclude-standard -- "$book_root/reference"
done <<<"$aio_roots" | LC_ALL=C sort -u)
echo "verify-clean-checkout: $(printf '%s' "$provisioned" | grep -c . || true) provisioned file(s)"

ci_cmd=${AIO_CLEAN_CHECKOUT_CI:-bash scripts/ci-local.sh}
(cd "$clone" && TMPDIR=/dev/shm bash -c "$ci_cmd")

fail=0
tracked=$(cd "$clone" && LC_ALL=C comm -12 <(printf '%s\n' "$provisioned" | grep . || true) \
  <(git ls-files --cached | LC_ALL=C sort -u))
if [[ -n $tracked ]]; then
  echo "FAIL: provisioned file(s) are tracked:" >&2
  printf '  %s\n' "$tracked" >&2
  fail=1
fi
while IFS= read -r path; do
  [[ -n $path ]] || continue
  if ! git -C "$clone" check-ignore -q -- "$path"; then
    echo "FAIL: provisioned file is not ignored: $path" >&2
    fail=1
  fi
done <<<"$provisioned"
unclean=$(git -C "$clone" status --porcelain --ignored | grep -v '^!! ' || true)
if [[ -n $unclean ]]; then
  echo "FAIL: the clone has tracked changes or untracked-unignored files after provisioning and CI:" >&2
  printf '%s\n' "$unclean" >&2
  fail=1
fi
((fail == 0)) || exit 1
echo "PASS verify-clean-checkout: $head_sha"
