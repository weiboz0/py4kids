#!/usr/bin/env bash
# Authoritative local gate for py4kids.
set -euo pipefail
script_repo_root=$(cd "$(dirname "$0")/.." && pwd)
export PY4KIDS_CI=1

# --all-books renders every publication book's editions (required before a release); without it,
# step 5 renders only the books the change touches and step 6 builds the site only when the change
# touches it (design 010 D7). For the aio books it also runs the fail-closed overlap scan
# (`overlap-scan --require-corpus`, design 014 D4).
# The two probes are ported from usaaio's ci-local (plan aio-001 Phase E) and exit before step 1:
# --registry-probe [--root REPO] prints the aio catalog adapter's records ("<id>\t<aio_round>\t<root>"),
# --solution-probe BOOK_ROOT RELATIVE runs one aio solution notebook exactly as step 3 does.
usage="usage: scripts/ci-local.sh [--all-books] | --registry-probe [--root REPO] | --solution-probe BOOK_ROOT RELATIVE"
scope_args=()
all_books=0
registry_probe=0
probe_root=
solution_probe_root=
solution_probe_relative=
while (($#)); do
  case "$1" in
    --all-books) scope_args=(--all-books) ;;
    --registry-probe) registry_probe=1 ;;
    --root) (($# >= 2)) || { echo "$usage" >&2; exit 2; }; probe_root=$2; shift ;;
    --solution-probe)
      (($# >= 3)) || { echo "$usage" >&2; exit 2; }
      solution_probe_root=$2
      solution_probe_relative=$3
      shift 2
      ;;
    *) echo "$usage" >&2; exit 2 ;;
  esac
  shift
done
((${#scope_args[@]})) && all_books=1
if [[ -n $probe_root ]] && ((!registry_probe)); then
  echo "$usage" >&2; exit 2
fi

# aio notebook execution (usaaio a20128f ci-local step 3, ported verbatim apart from the
# AIO_BOOK_ROOT rename and the aio dependency group): each notebook runs from its book root, where
# `--project ..` is the py4kids root. The round-2 book's transformer-to-capstone practice solutions
# (units B2-020..B2-024) and the r2-001 mock-test solutions are bounded at 20 s each.
run_solution_notebook() {
  local book_root=$1
  local relative=$2
  {
    if [[ $relative == units/B2-020-language-transformers/practice/p??_solution.ipynb || $relative == units/B2-021-cross-modal-transformers-vision/practice/p??_solution.ipynb || $relative == units/B2-022-probabilistic-latent-models/practice/p??_solution.ipynb || $relative == units/B2-023-generative-models-diffusion/practice/p??_solution.ipynb || $relative == units/B2-024-gpu-scientific-ml-capstone/practice/p??_solution.ipynb || $relative == mocktests/r2-001/solutions/p??_solution.ipynb ]]; then
      (cd "$book_root" && AIO_BOOK_ROOT="$book_root" timeout 20s uv run --project .. --group aio jupyter execute "$relative")
    else
      (cd "$book_root" && AIO_BOOK_ROOT="$book_root" uv run --project .. --group aio jupyter execute "$relative")
    fi
  }
}

if [[ -n $solution_probe_root || -n $solution_probe_relative ]]; then
  [[ -n $solution_probe_root && -n $solution_probe_relative ]] || exit 2
  run_solution_notebook "$solution_probe_root" "$solution_probe_relative"
  exit $?
fi

cd "$script_repo_root"
repo_root=$(pwd -P)

# The aio catalog adapter (tools/aio/books.py, design 014 D1/D4): the content_model: aio books in
# dependency order, one "<id>\t<aio_round>\t<absolute root>" line each (BookSpec.number := aio_round).
aio_registry_records() {
  PYTHONPATH="$script_repo_root${PYTHONPATH:+:$PYTHONPATH}" \
    uv run --project "$script_repo_root" --group aio python - "$1" <<'PY'
import sys

from tools.aio.books import load_book_catalog

for book in load_book_catalog(sys.argv[1]).books:
    print(f"{book.id}\t{book.number}\t{book.root}")
PY
}

if ((registry_probe)); then
  if ! records=$(aio_registry_records "${probe_root:-$repo_root}"); then
    echo "FAIL: cannot load registered aio books from ${probe_root:-$repo_root}" >&2
    exit 1
  fi
  printf '%s\n' "$records"
  exit 0
fi

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
    # content_model / aio_round (design 014 D1): an `aio` book is an imported olympiad book.
    model = book.get("content_model", "py4kids")
    if model not in ("py4kids", "aio"):
        sys.exit(f"FAIL: book {book['id']!r}: content_model must be 'py4kids' or 'aio', got {model!r}")
    if model == "aio":
        rnd = book.get("aio_round")
        if not isinstance(rnd, int) or isinstance(rnd, bool) or rnd < 1:
            sys.exit(f"FAIL: book {book['id']!r}: an aio book requires a positive integer aio_round")
        forbidden = [flag for flag in ("judge", "patterns", "acsl", "labs") if flag in book]
        if forbidden:
            sys.exit(f"FAIL: book {book['id']!r}: flags not allowed on an aio book: {', '.join(forbidden)}")
    elif "aio_round" in book:
        sys.exit(f"FAIL: book {book['id']!r}: aio_round is allowed only on a content_model: aio book")
    flags = [flag for flag in ("publication", "judge", "patterns", "acsl", "site", "labs") if book.get(flag) is True]
    print(book["id"], *flags)
PY
)"
echo "registry: $(cut -d' ' -f1 <<< "$books" | paste -sd' ')"
uv run ruff check tools/ tests/ scripts/ runner/py recsys/projects/bookrec recsys/data \
  roar/projects/racekit roar/data roar/tests

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

# `content_model` and `aio_round` (design 014 D1/D2) are likewise VALUES read on their own line:
# "<id> <model> <aio_round-or-empty>" (py4kids when absent; validated in the registry check above).
# Steps 2-5 route on MODEL: an aio book runs the aio commands and none of the py4kids-model ones.
models="$(uv run python - <<'PY'
import yaml

catalog = yaml.safe_load(open("books.yaml", encoding="utf-8"))
for book in catalog["books"]:
    print(book["id"], book.get("content_model") or "py4kids", book.get("aio_round") or "")
PY
)"
declare -A MODEL
declare -A ROUND
while read -r mid mmodel mround; do MODEL["$mid"]="$mmodel"; ROUND["$mid"]="$mround"; done <<< "$models"
is_aio() { [[ "${MODEL[$1]:-py4kids}" == aio ]]; }

# The aio books, from the aio catalog adapter (usaaio step 1: load the catalog and validate every
# root). Every aio command runs under the aio dependency group (design 014 D8), so an aio book
# must declare `dependency_group: aio`, and the adapter must see exactly the aio books above.
AIO_IDS=()
AIO_ROUNDS=()
AIO_ROOTS=()
aio_expected=()
while read -r mid _; do
  if is_aio "$mid"; then
    aio_expected+=("$mid")
    if [[ "${GROUP[$mid]:-}" != aio ]]; then
      echo "FAIL: book '$mid': a content_model: aio book requires dependency_group: aio" >&2; exit 1
    fi
  fi
done <<< "$models"
if ((${#aio_expected[@]})); then
  if ! aio_records=$(aio_registry_records "$repo_root"); then
    echo "FAIL: cannot load the registered aio books" >&2; exit 1
  fi
  while IFS=$'\t' read -r aid around aroot; do
    AIO_IDS+=("$aid"); AIO_ROUNDS+=("$around"); AIO_ROOTS+=("$aroot")
    if [[ "${ROUND[$aid]:-}" != "$around" ]]; then
      echo "FAIL: aio book '$aid': adapter round $around != books.yaml aio_round ${ROUND[$aid]:-}" >&2; exit 1
    fi
  done <<< "$aio_records"
  if [[ "$(printf '%s\n' "${AIO_IDS[@]}" | LC_ALL=C sort)" != "$(printf '%s\n' "${aio_expected[@]}" | LC_ALL=C sort)" ]]; then
    echo "FAIL: the aio catalog adapter books (${AIO_IDS[*]}) differ from books.yaml (${aio_expected[*]})" >&2; exit 1
  fi
  PYTHONPATH="$script_repo_root${PYTHONPATH:+:$PYTHONPATH}" uv run --group aio python - <<'PY'
from tools.aio.books import load_book_catalog, validate_book_root

catalog = load_book_catalog(".")
errors = [error for book in catalog.books for error in validate_book_root(book)]
if errors:
    raise SystemExit("\n".join(errors))
print("aio registry: " + " -> ".join(f"{book.id} (aio_round {book.number})" for book in catalog.books))
PY
fi
# The registered aio book serving round N (the role usaaio's book number played).
aio_root_for_round() {
  local i
  for i in "${!AIO_IDS[@]}"; do
    [[ ${AIO_ROUNDS[$i]} == "$1" ]] && { echo "${AIO_ROOTS[$i]}"; return 0; }
  done
  return 1
}
aio_id_for_round() {
  local i
  for i in "${!AIO_IDS[@]}"; do
    [[ ${AIO_ROUNDS[$i]} == "$1" ]] && { echo "${AIO_IDS[$i]}"; return 0; }
  done
  return 1
}
# An aio per-book or all-books check (`py4kids-tools aio`, the ported usaaio CLI; exit codes pass
# through unchanged, 3 = SKIP).
aio_tools() { uv run --group aio py4kids-tools aio "$@"; }

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
  # aio books have no per-book suite: the aio content model's one suite runs below.
  is_aio "$book" && continue
  echo "routed suite: $book (uv run --group $grp)"
  # A book with a single generator driver (design 013 §4.3) regenerates through it; the driver
  # generates every output twice in-process and fails on a checksum mismatch. Otherwise the
  # catalog + interactions generator pair runs, unchanged.
  if [[ -f "$book/data/generate.py" ]]; then
    PYTHONHASHSEED=0 uv run --group "$grp" python "$book/data/generate.py"
  elif [[ -f "$book/data/gen_catalog.py" && -f "$book/data/gen_interactions.py" ]]; then
    PYTHONHASHSEED=0 uv run --group "$grp" python "$book/data/gen_catalog.py"
    PYTHONHASHSEED=0 uv run --group "$grp" python "$book/data/gen_interactions.py"
  fi
  # A book's seeded model cache (design 011 §9; the U14 plan): regenerated-only like the data and
  # rebuilt from that fresh data every run, BEFORE the suite whose required check validates it.
  for build_models in "$book"/projects/*/scripts/build_models.py; do
    if [[ -f "$build_models" ]]; then
      PYTHONHASHSEED=0 uv run --group "$grp" python "$build_models"
    fi
  done
  PYTHONHASHSEED=0 uv run --group "$grp" pytest -q "$book"
done 3<<< "$groups"

# The aio content model's suite (design 014 D2/D4): one routed run, not per book, since it covers
# both books; it lives outside tests/ so the group-free run above never imports the aio stack.
# It includes the six content suites usaaio re-ran in its step 7 (language transformer, latent,
# generative, capstone, vision transformer, r2-001), so they are not repeated below.
if ((${#AIO_IDS[@]})); then
  echo "routed suite: aio content model (uv run --group aio)"
  uv run --group aio pytest -q tools/aio/tests
fi

step "3/7 notebook structure + execution"
while read -r book flags <&3; do
  # aio books run none of the py4kids-model step-3 commands (their own exec + hygiene follow).
  is_aio "$book" && continue
  for check in hygiene-check structure-check noexec-check cell-lint milestone-check exec-solutions exec-lessons; do
    book_run "$book" "$check"
  done
  if has_flag publication "$flags"; then
    book_run "$book" lesson-outputs-check
  fi
  # Real-simulator labs (design 013 §7.2): static lab rules, then the analysis cells executed
  # against the book's generated sample CSV, under the book's dependency group.
  if has_flag labs "$flags"; then
    book_run "$book" lab-check
  fi
done 3<<< "$books"

# aio books (design 014 D2; usaaio step 3 ported verbatim): problem-notebook hygiene, then every
# solution, practice-solution and mock-test-solution notebook, then every lesson, executed
# top to bottom from the book root (run_solution_notebook, above).
# CI budget (design 014 D9): the full aio run measured over 60 CI-minutes (plan aio-001 Phase E),
# so on an ordinary branch tools/aio/ci_scope.py --exec routes each aio book to `full`, `scoped`
# (only the changed unit and mock-test folders) or `none`; --all-books, a missing merge-base, and
# any change to the aio tooling, the gate or the environment run everything. A book with no route
# line runs in full (fail-safe). Hygiene always runs.
declare -A AIO_EXEC
if ((${#AIO_IDS[@]})); then
  aio_exec_routes=$(uv run --group aio python -m tools.aio.ci_scope --exec "${scope_args[@]}")
  while read -r route_mode route_book route_rest; do
    [[ -n ${route_mode:-} ]] || continue
    AIO_EXEC["$route_book"]="$route_mode ${route_rest:-}"
  done <<< "$aio_exec_routes"
fi
aio_exec_prefixes=()
aio_exec_mode=full
aio_in_exec_scope() {
  [[ $aio_exec_mode == full ]] && return 0
  local prefix
  for prefix in "${aio_exec_prefixes[@]}"; do
    [[ $1 == "$prefix"* ]] && return 0
  done
  return 1
}
# The executed notebooks import their units' data/*.py helpers; no bytecode is written into the
# book trees, whose step-2 inventory tests require them cache-free (a re-run would otherwise fail).
export PYTHONDONTWRITEBYTECODE=1
for index in "${!AIO_IDS[@]}"; do
  book=${AIO_IDS[$index]}
  book_root=${AIO_ROOTS[$index]}
  echo "running [$book]: hygiene-check"
  aio_tools --book "$book" hygiene-check || { rc=$?; [[ $rc -eq 3 ]] || exit "$rc"; }
  read -r aio_exec_mode aio_exec_rest <<< "${AIO_EXEC[$book]:-full}"
  aio_exec_prefixes=()
  route_kind=
  for token in ${aio_exec_rest:-}; do
    case $token in
      --units) route_kind=units ;;
      --mocktests) route_kind=mocktests ;;
      *) aio_exec_prefixes+=("$route_kind/$token/") ;;
    esac
  done
  case $aio_exec_mode in
    full) echo "aio exec: $book: full" ;;
    scoped) echo "aio exec: $book: scoped to ${aio_exec_prefixes[*]}" ;;
    none)
      echo "SKIP: $book: aio notebook execution (change-routed: no aio exec input changed; --all-books runs it)"
      continue
      ;;
    *) echo "FAIL: unknown aio exec route: $aio_exec_mode $book" >&2; exit 1 ;;
  esac
  mapfile -t notebooks < <(
    find "$book_root/units" "$book_root/mocktests" -type f \
      \( -path '*/solutions/*.ipynb' -o -path '*/practice/*solution*.ipynb' \) \
      | LC_ALL=C sort
  )
  for notebook in "${notebooks[@]}"; do
    relative=${notebook#"$book_root"/}
    aio_in_exec_scope "$relative" || continue
    echo "executing [$book]: $relative"
    run_solution_notebook "$book_root" "$relative"
  done
  mapfile -t lessons < <(
    find "$book_root/units" -type f -name '*.ipynb' \
      -not -path '*/practice/*' -not -path '*/.ipynb_checkpoints/*' | LC_ALL=C sort
  )
  for notebook in "${lessons[@]}"; do
    relative=${notebook#"$book_root"/}
    aio_in_exec_scope "$relative" || continue
    echo "executing [$book]: $relative"
    (cd "$book_root" && AIO_BOOK_ROOT="$book_root" uv run --project .. --group aio jupyter execute "$relative")
  done
done
unset PYTHONDONTWRITEBYTECODE

step "4/7 curriculum + assets"
# Per-entry checks iterate existing dirs, so they cover authored entries and are inert for
# unauthored ones. Flag-gated checks follow each book's books.yaml flags (see the comments there);
# books without `judge` run the turtle checks. Fastforward relaxation keys on prereq_policy.
while read -r book flags <&3; do
  if is_aio "$book"; then
    # aio books run none of the py4kids-model curriculum checks above or below, turtle checks
    # included (their own checks follow); only the site export check keeps its meaning (D2).
    if has_flag site "$flags"; then
      book_run "$book" site-check
    fi
    continue
  fi
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

if ((${#AIO_IDS[@]})); then
  # aio per-book checks (usaaio step 5; hygiene-check ran in step 3). Exit 3 is the printed SKIP,
  # tolerated here exactly as usaaio does; --all-books then runs the fail-closed overlap scan.
  for book in "${AIO_IDS[@]}"; do
    for c in prereq-check coverage-check scope-check schedule-check tolerance-check blueprint-check overlap-scan answerkey-check layer-boundary-check unit-order-check api-comments-check; do
      echo "running [$book]: $c"
      aio_tools --book "$book" "$c" || { rc=$?; [[ $rc -eq 3 ]] || exit "$rc"; }
    done
    if ((all_books)); then
      echo "running [$book]: overlap-scan --require-corpus"
      aio_tools --book "$book" overlap-scan --require-corpus
    fi
  done
  # aio all-books checks (usaaio step 6): no SKIP tolerance.
  for c in prereq-check scope-check schedule-check; do
    aio_tools --all "$c"
  done
  # Register verification (usaaio step 4) for the aio_round 1 book; verify-register's own
  # `number != 1` guard reads aio_round through the adapter.
  aio_round1_id=$(aio_id_for_round 1) || { echo "FAIL: no registered aio_round 1 book" >&2; exit 1; }
  uv run --group aio python scripts/aio/verify-register.py --book "$aio_round1_id"
fi

if ((${#AIO_IDS[@]})); then
  # Step 4b (a part of step 4, so the gate keeps its seven steps) is usaaio step 7: the generated material inventories and course-structure documents must be
  # current, and the three mutation verifiers must kill every planted mutant. Book roots resolve
  # from aio_round, never from an id; no command here tolerates a SKIP.
  aio_round1_root=$(aio_root_for_round 1) || { echo "FAIL: no registered aio_round 1 book" >&2; exit 1; }
  aio_round2_root=$(aio_root_for_round 2) || { echo "FAIL: no registered aio_round 2 book" >&2; exit 1; }
  echo "--- 4b: aio generated evidence + mutation checks ---"
  uv run --group aio python -m tools.aio.audit_curriculum --root "$aio_round1_root" --check
  uv run --group aio python -m tools.aio.audit_curriculum --root "$aio_round2_root" --check
  uv run --group aio python -m tools.aio.render_curriculum_roadmap --root "$repo_root" --check
  for book_root in "${AIO_ROOTS[@]}"; do
    uv run --group aio python -m tools.aio.render_course_structure --root "$book_root" --check
  done
  uv run --group aio python -m tools.aio.verify_training_mutations --repo-root "$repo_root"
  uv run --group aio python -m tools.aio.verify_classical_mutations --repo-root "$repo_root"
  uv run --group aio python -m tools.aio.verify_attention_mutations --repo-root "$repo_root"
fi

step "5/7 PDF build"
# Handouts and the syllabus for every book, judge books included (design 010 D5); build-pdf.sh
# fails on a missing glyph. A publication book's editions render only when the change touches the
# book, or anything under tools/ or scripts/, or books.yaml (design 010 D7, tools/ci_scope.py), or
# with --all-books. publish-audit needs the render, so it is skipped with it; never silently.
rendered=()
skipped=()
while read -r book flags <&3; do
  if ! is_aio "$book"; then
    bash scripts/build-pdf.sh --book "$book"
  else
    # aio PDFs (design 014 D2; usaaio step 8): syllabus, unit practice handouts, mock-test papers
    # and solutions, through the aio group. Exit 3 means the toolchain is absent: SKIP, as usaaio.
    uv run --group aio bash scripts/aio/build-pdf.sh --book "$book" \
      || { rc=$?; [[ $rc -eq 3 ]] || exit "$rc"; echo "SKIP: $book: aio PDFs (lualatex or pandoc absent)"; }
  fi
  if has_flag publication "$flags"; then
    # The aio edition route (aio build-book + publish_audit through tools/aio/ci_scope.py) lands with
    # `publication` in aio-002; until then an aio publication book must fail, never skip silently.
    if is_aio "$book"; then
      echo "FAIL: $book: aio editions are not routed yet (plan aio-002)" >&2; exit 1
    fi
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
# book and builds site/ with Astro, then the site's vitest suite and its browser tests run (plan 103
# Phase F: `pnpm -C site e2e`, Playwright on Chromium). It needs Node >= 22.12
# (.nvmrc; activated through nvm when the shell's default is older), pnpm and a Chromium. The
# build is scoped like the editions (design 010 D7): it runs when the change touches site/, tools/,
# runner/, scripts/, books.yaml, .nvmrc or a site book (tools/ci_scope.py --site), or with --all-books.
# A site change with a missing tool fails; an out-of-scope change skips, printed, never silent.
. scripts/site-env.sh
# Scope is resolved first. A change in the site's scope MUST be verified: a missing tool then fails
# the gate (plan 103 content review). Only an out-of-scope change skips, and the skip is printed.
decision="$(uv run python -m tools.ci_scope --site "${scope_args[@]}")"
echo "site: $decision"
if [[ "$decision" == render:* ]]; then
  if ! site_node_env; then
    echo "FAIL: site in scope but node >= 22.12 is missing (.nvmrc; nvm install)" >&2; exit 1
  elif ! site_pnpm; then
    echo "FAIL: site in scope but pnpm is missing (corepack enable)" >&2; exit 1
  elif ! site_chromium; then
    echo "FAIL: site in scope but no Chromium was found" >&2; exit 1
  fi
  bash scripts/build-site.sh
  "${SITE_PNPM[@]}" -C site test
  # The Python runner's envelope tests (plan 104; its harness is tested by pytest in step 2).
  "${SITE_PNPM[@]}" -C runner test
  # Phase F: Playwright end-to-end, axe, the no-network and header proofs (again with the service
  # workers active: project site-sw), then Lighthouse, against the built dist/ served by
  # site/scripts/serve.mjs; then the installable, offline site (plan 105 Phase E,
  # site/playwright.pwa.config.ts: every book offline with both servers stopped, the update path,
  # installability, axe on the new UI) on dist/, and its hook tests on a PY4KIDS_TEST_HOOKS=1 build
  # made into build/site-hooks/ (site/scripts/hooks-build.ts), never into the dists.
  "${SITE_PNPM[@]}" -C site e2e
  # Plan 104 Phase D (slow): every reference solver of every `judge: true` book runs in Pyodide through
  # the runner against all its fixtures, and every verdict must equal tools/judge.py's.
  "${SITE_PNPM[@]}" -C site e2e:solvers
else
  echo "SKIP: site (${decision#skip: })"
fi

step "7/7 pre-merge guard"
bash scripts/pre-merge-guard.sh

echo
echo "ci-local: ALL GREEN"
