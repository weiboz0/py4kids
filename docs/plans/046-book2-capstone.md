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
preserved** — only the I/O contract transforms (top-level `return X` → `print(X)`, AST-scoped; the two
multi-return solvers (P4, P5) hand-written flat), and this is PROVEN by the per-solver source-delta audit
(B8), not assumed.

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
  wall/edge, P8 pre-order-vs-other-order; **P4** already carries YES and NO asserts — confirm both
  survive as a self-pair / wrong-pointer witness).
  **Cross-check the transform against the ORIGINAL asserts (guards against a buggy transform blessing
  its own output — gate finding sol-2):** for every fixture derived from an original
  `assert solve(IN) == OUT`, verify the transformed solver's stdout token-matches the ORIGINAL `OUT`
  before committing its `.out`. The committed `.out` must reproduce the pre-migration expected answer,
  not merely whatever the new `.py` happens to print. (Crafted witnesses with no original assert are
  recomputed from the pristine solver as usual.)
- [ ] A3: Write `assets/pK.py` + fixtures; rebuild `solutions.ipynb` = an intro rewritten off the
  `solve(data)`/inline-assert model (to "display-only mirrors of stdin/stdout programs in `assets/`" —
  the current intro says "one pure `solve(data)` per problem … runs top-to-bottom clean") + per-problem
  `## Problem K` heading + `**Notice:**` (derived from the ACTUAL solver) + no-exec byte-identical
  mirror (`mirror(pysrc)=pysrc.splitlines(keepends=True)`).
- [ ] A4: Rewrite `brief.ipynb` intro off `solve(data)` (stdin/stdout, markdown wrapper — the intro
  currently shows the `print(solve(sys.stdin.read()))` wrapper). The `### Problem N` statements are
  ALREADY stdin-phrased ("Print …"/Sample I/O, no `return` prose), so their sweep is near-noop; the real
  rewrites are the intro, the `## Requirements` pure-`solve(data)`-function checklist line, and any
  `solve(data)`-adjacent phrasing in `## Make it yours`. Empty the 8 student code cells; preserve the
  five `## Milestone N` + `## Make it yours` + `## Requirements` headings.
- [ ] A5: Reword `teacher-notes.md` — the `solve(data)`/inline-assert CODE references (backticked
  `solve`, `solve(data)`; "runs top-to-bottom clean with its asserts"; "hidden asserts catch" →
  "display-only mirror judged by piping each committed input case"/"hidden cases catch"); semantic-repair
  return-value prose ("returns a longer, wrong hop count" → "prints"). Keep `## Rubric` + the six
  headings. Do NOT touch the English verb "solve"/"solves".

### Phase B — Verification (REQUIRED)

- [ ] B1: Subprocess-run every `pK.py` against every fixture; stdout matches `.out` exactly. AND every
  assert-derived fixture's `.out` token-matches the ORIGINAL pre-migration assert RHS (the shipped
  asserts are the independent oracle — per A2, so a wrong transform cannot self-bless).
- [ ] B2: Mutation-test each crafted witness (sole-killer): P5 FIFO + edge-directionality, P7
  no-restore, P2 wall/edge, P8 traversal-order, plus per-problem boundary mutants.
- [ ] B3: All no-exec mirrors byte-identical to their `.py`; every brief problem sample re-run through
  its solver matches.
- [ ] B4: AST closure audit over `assets/*.py` (no banned construct; pinned builtins only).
- [ ] B5: Contract sweep — zero references to the `solve(data)` CODE IDENTIFIER (backticked `solve`,
  `solve(data)`, `print(solve(...))`, `def solve`) and zero return-value/contract `return`/`returns`/
  `returned` prose in brief statements/`## Requirements`/`## Make it yours`, the solutions intro, or
  teacher-notes. The English verb "solve"/"solves" ("solve them in any order", "solves all eight") is
  legitimate contest prose and is RETAINED — the sweep targets the code identifier, not the verb. No
  `def solve`/wrapper CODE cell anywhere (migrated units carry NO `solve()` wrapper — there is no
  sanctioned-wrapper exception); no solution heading; 3–6 sequential milestones; `## Make it yours` +
  `## Requirements` present; all 8 student cells empty; no `assets/*.py`-style literal in prose
  (ASSET_REF `assets/[\w.-]+\.py`).
- [ ] B6: Metadata byte-preservation — scoped `git diff` shows `manifest.yaml` +
  `book2/curriculum/coverage-map.yaml` UNCHANGED; `practice_findings` still passes (pre_capstone 31/31).
- [ ] B7: `bash scripts/ci-local.sh` → ALL GREEN, exit 0.
- [ ] B8: **Per-solver source-delta audit** — for each `assets/pK.py`, diff it against main's shipped
  `solve()` for that problem and confirm the ONLY differences are the I/O-contract transform (drop the
  `def solve(...)` header + `data = sys.stdin.read()`; solve's own top-level `return X` → `print(X)`; the
  found-flag flattening for P4/P5; P4's module-level `skill_of` kept verbatim). No algorithm/logic change,
  so every assessed concept-home survives verbatim (`sorted-key` in P4, `deque` FIFO in P5, recursion in
  P3/P6/P7/P8, prefix-sum in P1, grid-sim in P2). This PROVES the "logic preserved" claim rather than
  assuming it.

### Phase C — Post-execution report + gates

- [ ] C1: Write the post-execution report in this plan file.
- [ ] C2: 4-way content-review gate (all four blind-solve all 8 problems); resolve all `[OPEN]`.
- [ ] C3: PR → `pre-merge-guard --pr` → squash-merge. **On merge: Book 2 fully stdin-migrated.**

## Out of scope

- No tooling changes; no manifest/concept-map changes; no new problems; no logic changes to any solver.
- No changes to the milestone grouping or the pedagogy of the brief beyond the I/O-contract rewrite.

## Plan Review

### Round 1 — external reviewers ([sol]/[glm]/[fable])

- **[sol] REJECT** — (sol-1) P4 misclassified mechanical: its `solve` has `return "YES"` inside the
  loop + a top-level `return "NO"`, and a module-level `skill_of` helper — reclassify hand-write-flat,
  preserve `skill_of`. (sol-2) verification can self-bless a bad transform (A2 generates the `.out` from
  the transformed `.py`, B1 compares the same solver against it) — cross-check every original assert's
  RHS against the transformed output.
- **[glm] APPROVE WITH NITS** — P4 (as corrected) verified; conventions/practice-completeness/witnesses
  all PASS against tooling. MUST-fix nits: teacher-notes stale "runs top-to-bottom clean with its
  asserts"/"hidden asserts catch"; the solutions.ipynb intro still describes `solve(data)` + inline
  asserts; B5 sweep must target the code identifier (not the English verb); drop the sanctioned-wrapper
  exception; "one" → "two" multi-return solvers.
- **[fable] REJECT** — (fable-1) same P4 blocker (in-loop `return "YES"` → module-level SyntaxError if
  transformed mechanically) + note the module-level `skill_of`. Nits: B5 must scope to the code
  identifier; A4's statement sweep is near-noop (real rewrites = intro, `## Requirements`,
  Make-it-yours); P5 reverse-edge witness genuinely required; confirm the plan commit is on the branch.

**Fixes applied (this HEAD):** P4 → multi-return hand-write-flat with `skill_of` preserved verbatim
(inventory + A1); "one" → "two"; A2/B1 add the original-assert cross-check (sol-2); A3 rewrites the
solutions intro; A5 rewords teacher-notes' assert/`solve(data)` prose; A4 clarifies the real rewrites;
B5 scoped to the `solve(data)` code identifier (English verb retained), sanctioned-wrapper exception
dropped. Round 2 re-dispatched to all three.

### Round 2 (HEAD 948a375 → this HEAD) — CONSENSUS: all three external APPROVE ✅

- **[sol] APPROVE** — sol-1 (P4 reclassify + `skill_of`) and sol-2 (original-assert cross-check in
  A2 + B1) both resolved; Phase B substantive; conventions, practice-completeness, and witnesses all
  re-confirmed.
- **[fable] APPROVE** — round-1 blocker + all nits resolved and re-verified against the committed
  sources; the self-blessing cross-check correctly threaded through A2 (build) and B1 (verify); no new
  findings.
- **[glm] APPROVE WITH NITS** — all round-1 nits + both sol fixes verified fixed. One new nit **F1**:
  the Goal referenced a "B8 source-delta audit" that Phase B did not define. `[FIXED]` — B8 is now
  defined (per-solver source-delta audit proving the I/O-only transform), and the Goal ties to it
  intentionally. _(The dangling reference originated from a stray fork of this session that was
  concurrently editing the plan; the fork has been stopped and its orphaned edit reconciled.)_

**Gate CLOSED — 4-way consensus ([self] + all three external), no blockers.** Cleared for Phase A
implementation.

## Content Review

_(pending)_

## Post-Execution Report

_(pending)_
