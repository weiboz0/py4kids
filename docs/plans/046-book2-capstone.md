# Plan 046 — Migrate the Book-2 project-03 capstone to stdin-first

**Goal:** Migrate the Book-2 capstone `project-03-mock-contest` (8 problems, kind:project) from the
`solve(data:str)->str` inline-assert contract to the **stdin-first, subprocess-judged** model — the
FINAL entry. On merge, all of Book 2 (14 units + 4 checkpoints + capstone) is stdin-first.

**Architecture:** Each problem's reference solution becomes a real `.py` in `assets/` reading
`sys.stdin` and printing stdout, judged by `tools/judge.py` against committed `assets/pN/<k>.in` /
`<k>.out` fixtures (≥2 per solver, non-vacuous). `solutions.ipynb` becomes all-`no-exec` cells
**byte-identical** to each `.py`, under `## Problem N` headings, each with a per-problem Notice.
`brief.ipynb` keeps its milestone structure; its intro + problem statements + `## Requirements`
checklist are rewritten off `solve(data)` to the stdin/stdout contract, and the 8 student starter-stub
code cells are emptied (matching the migrated units' exercises cells). Shipped solver **logic
preserved** — only the I/O contract transforms (top-level `return X` → `print(X)`, AST-scoped; the one
multi-return solver hand-written flat).

**Tech Stack:** Python 3.12, `uv`, `tools/judge.py`, `tools/source_policy.py`, `tools/concept_scan.py`,
`scripts/ci-local.sh`. Reusable **temporary, uncommitted** scratchpad builder `build_capstone.py` (same
machinery as `build_uNN.py` / `build_cp.py`).

**Spec:** `docs/designs/001-book2-algorithms.md` §3/§4 + the project conventions in `tools/notebooks.py`
/ `tools/judge.py`: PID `pN` from `### Problem N` in `brief.ipynb` (the mirror lives under `## Problem N`
in `solutions.ipynb`); brief needs 3–6 sequential `## Milestone N` + a standalone `## Make it yours` + a
`## Requirements` checklist + NO solution heading; teacher-notes uses `## Rubric` (six headings =
five unit headings + `## Rubric`); submission wrapper markdown-only (cell-lint's no-exec exemption is
`kind=='unit'` ONLY).

## Global Constraints

- **PID convention:** `p1..p8` per `### Problem N` (brief.ipynb). 8 problems across 5 milestones.
- **Closure (preserved from each shipped solver, no new constructs):** pinned builtins only; NO
  comprehension / ternary / `+=` / chained-compare / `[x]*n` / lambda / class / `nonlocal` / `global` /
  `del` / banned methods `{pop,join,index,count,find}`; `deque` FIFO uses `append`/`popleft` (never bare
  `.pop`); recursion preserved exactly as shipped (P6/P7/P8 nested helpers may close over captured
  state — left verbatim, no rewrite). Grid bounds non-chained. Same rules as the units the capstone
  draws on; the migration is an I/O transform, never a logic change.
- **brief has NO solution heading** (structure-check FAILs `#+ solution`); milestones stay 3–6
  sequential; `## Make it yours` + `## Requirements` retained.
- **Submission wrapper markdown-only**; 8 student code cells emptied (source `[]`).
- **Fixtures:** ≥2 per solver, non-vacuous; every `.out` recomputed by running the pristine `.py` on the
  materialized `.in`; drop empty-stdout; dedupe.
- **Manifest + coverage-map unchanged** (byte-identical). Authoring the capstone dir already ACTIVATES
  `practice_findings` (pre_capstone 31/31 from CP4); the stdin migration keeps every practiced concept.
  `is_stdin_model_entry` waives `exec-solutions`/solution-policy for the project once `assets/` with
  `.py` exists.

## File Structure

- Create: `book2/projects/project-03-mock-contest/assets/pK.py` (K=1..8) + `assets/pK/<j>.in`/`.out`.
- Modify: `.../solutions.ipynb` — each `def solve`+asserts cell → a `no-exec` cell byte-identical to
  `pK.py` under `## Problem K`; per-problem `**Notice:**` describing that solver.
- Modify: `.../brief.ipynb` — intro rewritten off `solve(data)`; `### Problem N` statements swept
  `return`→`print` (repairing legitimate function-return prose); `## Requirements` checklist rewritten
  to the stdin contract; `## Make it yours` refreshed if it references `solve`; 8 student code cells
  emptied. Milestones / `## Make it yours` / `## Requirements` headings preserved.
- Modify: `.../teacher-notes.md` — reword every `solve`/`return` token (whole-word, semantic repair for
  recursion prose); keep `## Rubric` + the six headings.

## Multi-return / nested inventory

- **Multi-return (hand-write flat — loop-return → found-flag):** **P4** (two-pointer pair:
  `return "YES"` inside the `while lo < hi` loop + `return "NO"` after → `answer` found-flag with
  `and answer == "NO"`; its module-level `skill_of` sort-key helper, defined ABOVE `solve`, is preserved
  verbatim above the `data = sys.stdin.read()` line) and **P5** (City Network BFS: `return str(dist)`
  inside the loop + `return "-1"` after → `answer` found-flag with `and answer == "-1"`).
- **Nested helper (AST-scoped `to_stdin` converts only solve's OWN top-level return):** P3 (binary
  search on the answer + greedy `groups_needed` split helper), P6 (flood-fill `fill` recursion), P7
  (backtracking `place`/recurse), P8 (tree pre-order `walk`). Helper returns left verbatim.
- **Mechanical (single top-level return):** P1 (prefix-sum ledger), P2 (grid-sim robot). _(Corrected —
  P4 has TWO top-level returns, so it is hand-written flat like P5, not mechanical; P3's helper is
  `groups_needed`, not `feasible`.)_

## Tasks / Phases

### Phase A — Build (`scratchpad/build_capstone.py`)

- [ ] A1: Read the ORIGINAL `solve()`+asserts from the committed `solutions.ipynb`; `to_stdin` each
  mechanical/nested solver (import-aware, AST-scoped return conversion); hand-write P4 and P5 flat
  (found-flag, I/O-preserving; P4 keeps its top-level `skill_of` helper above the stdin read).
- [ ] A2: Extract fixtures from the asserts; recompute every `.out` by running the pristine `.py` on the
  materialized `.in` (trailing newline added to the `.in`, `.out` computed from it); dedupe; drop
  empty-stdout; ensure ≥2 non-vacuous per solver (add a crafted mutation-witness where vacuous — esp.
  P5 BFS FIFO witness and directed/undirected discipline, P7 backtracking no-restore witness, P2 grid
  wall/edge, P8 pre-order-vs-other-order).
- [ ] A3: Write `assets/pK.py` + fixtures; rebuild `solutions.ipynb` = `## Problem K` heading +
  `**Notice:**` (derived from the ACTUAL solver) + no-exec byte-identical mirror
  (`mirror(pysrc)=pysrc.splitlines(keepends=True)`).
- [ ] A4: Rewrite `brief.ipynb` intro off `solve(data)` (stdin/stdout, markdown wrapper); sweep
  `### Problem N` statements `return`→`print` (repair function-return prose); rewrite `## Requirements`
  to the stdin contract; empty the 8 student code cells; preserve milestones / Make-it-yours.
- [ ] A5: Sweep `teacher-notes.md` (`solve`/`return` tokens; keep `## Rubric` + six headings).

### Phase B — Verification (REQUIRED)

- [ ] B1: Subprocess-run every `pK.py` against every fixture; stdout matches `.out` exactly.
- [ ] B2: Mutation-test each crafted witness (sole-killer): P5 FIFO + edge-directionality, P7
  no-restore, P2 wall/edge, P8 traversal-order, plus per-problem boundary mutants.
- [ ] B3: All no-exec mirrors byte-identical to their `.py`; every brief problem sample re-run through
  its solver matches.
- [ ] B4: AST closure audit over `assets/*.py` (no banned construct; pinned builtins only).
- [ ] B5: Contract sweep — zero whole-word `return`/`returns`/`returned`/bare `solve` in brief
  statements/`## Requirements`/`## Make it yours` or teacher-notes (except a sanctioned intro wrapper
  mention); no solution heading; 3–6 sequential milestones; `## Make it yours` + `## Requirements`
  present; all 8 student cells empty; no `def solve`/wrapper code cell; no `assets/*.py` literal in
  prose (ASSET_REF).
- [ ] B6: Metadata byte-preservation — scoped `git diff` shows `manifest.yaml` +
  `book2/curriculum/coverage-map.yaml` UNCHANGED; `practice_findings` still passes (pre_capstone 31/31).
- [ ] B7: `bash scripts/ci-local.sh` → ALL GREEN, exit 0.

### Phase C — Post-execution report + gates

- [ ] C1: Write the post-execution report in this plan file.
- [ ] C2: 4-way content-review gate (all four blind-solve all 8 problems); resolve all `[OPEN]`.
- [ ] C3: PR → `pre-merge-guard --pr` → squash-merge. **On merge: Book 2 fully stdin-migrated.**

## Out of scope

- No tooling changes; no manifest/concept-map changes; no new problems; no logic changes to any solver.
- No changes to the milestone grouping or the pedagogy of the brief beyond the I/O-contract rewrite.

## Plan Review

_(4-way gate — pending dispatch.)_

## Content Review

_(pending)_

## Post-Execution Report

_(pending)_
