# Plan 021 — Book 2 CP1 "Mock Contest 1"

**Goal:** Ship `checkpoint-01-mock-contest-1` — the first timed mock contest, assessing Term-1
(U01–U05) on the `solve(data:str)->str` contract — following the Book-1 checkpoint pattern and the
established Book-2 authoring pipeline.

**Architecture:** A checkpoint entry (`checkpoint.ipynb` + `solutions.ipynb` + `teacher-notes.md` +
`manifest.yaml`). `checkpoint.ipynb` opens with contest framing (time budget + rules), then 6 timed
`## Question N` problems that collectively exercise the Term-1 span — input/grid parsing (U01), boolean
logic (U02), an efficiency-sensitive problem whose constraints force the fast shape (U03), sets/dedup +
tuple-keyed sorting (U04), and binary search + complete search (U05) — each with an EMPTY student code
cell. `solutions.ipynb` mirrors the `## Question N` headings with pure `solve(data)` references and
non-vacuous asserts. The checkpoint introduces nothing; it REQUIRES the U01–U05 introduced concepts it
assesses and practices the Book-1 concepts its solutions use.

**Tech Stack:** Jupyter notebooks (nbformat), `tools/` checks, `scripts/ci-local.sh`,
`py4kids-tools --book book2`; Python 3 stdlib only.

**Spec:** `docs/designs/001-book2-algorithms.md` (§7 CP1; §8 mock-contest timing); `book2/syllabus.md`;
`book2/curriculum/coverage-map.yaml` (the `checkpoint-01-mock-contest-1` entry); the shipped Book-1
checkpoints (`book1/checkpoints/checkpoint-04-year-one-finale/` — the closest mock-contest precedent);
plans 018–020 (the Book-2 unit/authoring pattern — the closure rules transfer verbatim).

## Global Constraints

Copied from the design + registry + the plan-020 gate lessons; every task's requirements include this.

- **Contract:** every reference solution is a pure `solve(data: str) -> str`; ZERO `input()` in any
  executable cell. The `import sys; print(solve(sys.stdin.read()))` wrapper is shown ONLY as a **markdown
  fenced code block** in `checkpoint.ipynb` or in teacher-notes — **NEVER as a code cell** (checkpoint code
  cells are ruff-linted with NO `no-exec` exemption — that exemption is `kind=="unit"` only — so a wrapper
  code cell's undefined `solve` fails cell-lint with F821) and NEVER in solutions.ipynb. Deterministic.
- **Checkpoint structure (structure-check):** required files are exactly `manifest.yaml`,
  `checkpoint.ipynb`, `solutions.ipynb`, `teacher-notes.md`. Problem headings are `## Question N`
  (NOT `## Exercise`/`## Problem`) — **≥ 6 required**. Student code cells are EMPTY (`''`).
  Checkpoints have NO stretch tier. teacher-notes has exactly SIX headings — the five unit headings
  `## Goals`/`## Pacing`/`## Common mistakes`/`## Discussion prompts`/`## Differentiation` PLUS
  `## Grading` (points per question + total, and the time budget).
- **Closure (same scanner rules as U04/U05):** only Book-1 + U01–U05 concepts. set-ops ONLY via
  `.add`/`.discard` on a `{…}`/`set()` var in-cell, or `-`; **NOT `.remove`** (the scanner silently
  treats `.remove` as taught, but U04 taught only `.add`/`.discard` — using it would ship untaught
  surface that CI cannot catch); NEVER `&|^`; NEVER `.union`/`.intersection`/`.difference`. `sorted(seq, key=named_fn)` (NO lambda). binary-search
  `lo/hi/mid` and fixed-depth nested-loop complete-search are allowed (taught in U05); **NO recursion,
  NO subset/permutation generation, NO converging two-pointer scan** (U09/U11/U14). NO comprehensions/
  generator expressions (`comprehension` is U09). NO untaught methods (.join/.splitlines/.index/.count/
  .find/.pop). Allowed builtins ONLY `{len,min,max,sorted,sum,abs,round}` — NO `all`/`any`/`enumerate`/
  `zip`/`reversed`/`map`/`filter`. concept-scan `--book book2` must be clean.
- **Two-tier metadata:** `introduces: []`. `requires:` = EVERY U01–U05 introduced concept the solutions
  actually USE (`input-parse`/`str-split`/`grid-2d`/`boolean-algebra`/`complexity`/`set-literal`/`set-ops`/
  `tuple`/`sorted-key`/`binary-search`/`complete-search` — trim any genuinely not used). Because a
  checkpoint ASSESSES these concepts, they belong in `requires`, NOT `practices` (this is the key
  difference from a unit, where earlier-taught concepts are re-practiced). `practices:` =
  `(detected ∪ manually-listed used concepts) − requires − introduces − wrapper-artifacts` — i.e. ONLY the
  Book-1 concepts the solutions use (`def-function`, `parameters`, `return-value`, `for-loop`,
  `if-statement`, `arithmetic`, `list-*`, `dict-access`, `type-conversion`, `print`, …); NO U01–U05
  introduce and NO `file-read`/`import-statement` (wrapper artifacts) appear in `practices`. Hand-add any
  genuinely-used-but-scanner-invisible Book-1 concept (e.g. `dict-access` via `.get`/`[]`).
  `requires ∩ practices = ∅`; manifest == coverage-map exactly; manifest `lessons: 0.5` (manifest-check
  enforces it against the map).
- **Non-vacuous asserts (the plan-020 mutation categories):** every reference solution carries the
  sample assert PLUS crafted edge cases that kill off-by-one (drop-last / range(n-1) / binary-search
  `lo<=hi`↔`lo<hi`, `mid±1`), wrong-aggregate/tie boundary, self-pair, and **decisive-last-AFTER-SORT**
  for any sort-then-scan/search solution. Decisive values placed last (and last-after-sort).
- **Assessment integrity:** every problem is solvable with ONLY U01–U05 material (prereq closure); the
  set collectively covers the term; difficulty is contest-appropriate for a timed sitting (no
  stretch-only insight required, since checkpoints have no stretch tier).

## Out of scope

- No new unit/technique/feature (introduces is empty by design).
- No tooling change (checkpoint per-entry checks already exist and auto-cover the new dir).
- **Verification is NOT out of scope:** Phase C is the named verification phase (blind-solve + mutation +
  full ci-local + 4-way content gate).

---

## Phases

### Phase A — checkpoint.ipynb + solutions.ipynb (the contest)

**Files:**
- Create: `book2/checkpoints/checkpoint-01-mock-contest-1/checkpoint.ipynb`
- Create: `book2/checkpoints/checkpoint-01-mock-contest-1/solutions.ipynb`

**Interfaces:**
- Consumes: U01–U05 introduced concepts + Book-1.
- Produces: nothing (introduces `[]`); it is an assessment leaf.

- [ ] **A1 — checkpoint.ipynb.** Opening markdown: contest title, the time budget (~35–45 min for the
  class sitting, matching the `lessons: 0.5` weight and the Book-1 0.5-lesson checkpoint precedent), rules
  (each `solve(data)` reads the whole input string; the submission wrapper is shown as a markdown fenced
  block, NOT run here), and a points-table pointer. Then EXACTLY 6 `## Question N` problems numbered
  sequentially 1..6 (checkpoint_question_findings requires 6–8, sequential), each: title (### …),
  one-paragraph statement, `### Constraints`, `### Sample Input`, `### Sample Output` (```text fences),
  then an EMPTY code cell. Coverage: Q1 input/grid parsing (U01), Q2 boolean-logic rule (U02), Q3
  efficiency-sensitive count/scan whose constraints (N up to ~1e5/2e5) force O(n)/O(n log n) (U03), Q4
  sets/dedup + tuple-keyed sort (U04), Q5 binary-search query/count (U05), Q6 **fixed-depth nested-loop
  complete-search** (pinned — NOT search-over-answer, which is binary-search again and would leave
  `complete-search` unassessed → an unused require) (U05). The submission wrapper appears ONLY in a
  markdown cell (fenced block), never a code cell. Decisive values placed last / after sort. Unambiguous
  single-reading statements.
- [ ] **A2 — solutions.ipynb (FRESH author, blind).** Mirror `## Question N`; pure `solve(data)`; scanner-
  clean forms (set-ops via `.add`/`.discard`/`-`; named sort keys; binary-search `lo/hi/mid`; nested-loop
  complete-search; NO converging two-pointer, NO recursion/subset-gen). Each solution's inline asserts are
  non-vacuous per the mutation categories above (decisive-last / decisive-last-after-sort / self-pair /
  boundary). Output matches each stated Sample Output.

### Phase B — teacher-notes.md + manifest.yaml + map

**Files:**
- Create: `book2/checkpoints/checkpoint-01-mock-contest-1/teacher-notes.md`
- Create: `book2/checkpoints/checkpoint-01-mock-contest-1/manifest.yaml`
- Modify: `book2/curriculum/coverage-map.yaml` (fill the CP1 entry's `requires`/`practices`)

- [ ] **B1 — teacher-notes.md (inline).** The SIX headings (`## Goals`/`## Pacing`/`## Common mistakes`/
  `## Discussion prompts`/`## Differentiation`/`## Grading`). `## Grading` gives points per question + total
  and the ~35–45 min time budget; `## Pacing` frames the single timed 0.5-lesson sitting; a per-question
  Big-O line; which Term-1 unit each question assesses. May also carry the submission-wrapper snippet
  (allowed here, unlike checkpoint.ipynb code cells).
- [ ] **B2 — manifest.yaml + map (inline).** `introduces: []`; `lessons: 0.5`. `requires:` = EVERY U01–U05
  introduced concept the solutions USE (trim any not used) — including `str-split`, the U04 features, and
  the U05 techniques; these are ASSESSED, so they live in `requires`, never `practices`. `practices:` =
  `(detected ∪ manually-listed used concepts) − requires − introduces − wrapper-artifacts` = ONLY the
  Book-1 concepts the solutions use (e.g. `def-function`, `parameters`, `return-value`, `for-loop`,
  `if-statement`, `arithmetic`, `list-append`, `dict-access`, `type-conversion`, `print`); NO U01–U05
  introduce (no `str-split`/`input-parse`/feature/technique) and NO `file-read`/`import-statement` appear
  in `practices`. `requires ∩ practices = ∅`; `practices ∩ introduces = ∅` (trivial, introduces empty).
  Copy identically into the coverage-map CP1 entry (manifest == map). Derive from an ad-hoc `detect()` over
  both notebooks (concept-scan is one-directional); hand-add any genuinely-used-but-scanner-invisible
  Book-1 concept (e.g. `dict-access` via `.get`/`[]`).

### Phase C — Verification (named verification phase)

- [ ] **C1 — blind-solve + mutation self-check** on both notebooks (off-by-one, wrong-aggregate, self-pair,
  boundary, decisive-last-after-sort — every mutant fails an assert; every pristine solver passes; use a
  step cap for binary-search mutants). Confirm each of the assessed U01–U05 concepts is genuinely exercised
  (ad-hoc `detect()` for features; manual for techniques). Fix any vacuous assert.
- [ ] **C2 — full `scripts/ci-local.sh` ALL GREEN both books.**
- [ ] **C3 — commit Phase A+B+C** on `feature/plan-021-book2-cp1`.
- [ ] **C4 — 4-way content-review gate** ([self]/[sol]/[glm]/[fable], read-only, HEAD-pinned): blind-solve
  all 6; mutation sweep (categories above); closure (no untaught builtins/methods, no premature technique —
  no converging two-pointer/recursion/subset-gen; NO `.remove` on sets; features listed); `## Question N`
  headings 6–8 sequential, empty student cells, submission wrapper in markdown/teacher-notes only (never a
  code cell → cell-lint clean); teacher-notes six headings incl `## Grading`; manifest==map;
  each problem prereq-closed to U01–U05; the set collectively covers the term. Resolve every `[OPEN]`;
  re-verify fixes in round-2 before consensus.
- [ ] **C5 — write the post-execution report** in this file + re-run full `ci-local.sh` ALL GREEN after any
  content-gate fix — both precede the PR.
- [ ] **C6 — PR** → `pre-merge-guard.sh --pr` OK → squash-merge → delete branch → update memory.

## Post-Execution Report

_(filled at Phase C)_

## Plan Review

### Round 1 (2026-09-08, HEAD 1563057) — [self] APPROVE · [glm] APPROVE-WITH-NITS · [fable] REJECT · [sol] REJECT
All reviewers verified the checkpoint STRUCTURE claims correct against `tools/notebooks.py` (files,
`## Question N` 6–8 sequential, six teacher-note headings incl `## Grading`, no stretch, scan over
checkpoint+solutions / exec over solutions only). Three blockers folded (no architecture change):
- **[FIXED] BLOCKER (fable; confirmed empirically with ruff) — submission-wrapper CODE cell fails
  cell-lint F821.** The `no-exec` lint exemption is `kind=="unit"` only (`notebooks.py:947`), so a
  checkpoint wrapper code cell's undefined `solve` reds cell-lint. Fix: the wrapper is shown ONLY as a
  markdown fenced block / in teacher-notes, never a code cell (Global Constraint + A1 + C4). (glm's claim
  that the cell passes was wrong — I ran the repo's ruff invocation and got F821 exit 1.)
- **[FIXED] BLOCKER (fable+glm+sol) — requires/practices disjointness.** A checkpoint ASSESSES its
  concepts, so every used U01–U05 introduce → `requires` only; `practices = used − requires − introduces −
  wrapper-artifacts` = Book-1 concepts only. Removed the unit-template leftover that listed `str-split`/
  U04-features/techniques as practices (Q4 uses the four U04 features, already in requires → would violate
  `requires ∩ practices = ∅`).
- **[FIXED] BLOCKER (sol) — `.remove` must be banned.** The scanner silently credits `.remove` as taught,
  but U04 taught only `.add`/`.discard` → `.remove` would ship untaught surface CI can't catch. Restricted
  set mutation to `.add`/`.discard`/`-`.
Nits folded: pinned Q6 to fixed-depth nested-loop complete-search (glm — search-over-answer would leave
`complete-search` unassessed); time budget ~35–45 min to match `lessons: 0.5` (glm+fable, not 60–75);
stated manifest `lessons: 0.5` (glm); noted 6–8 sequential question bound (fable). No reviewer found a
wrong structure claim or missing/placeholder task. Round-2 dispatched at the revised HEAD.

### Round 2 — [self] APPROVE; [sol]/[glm]/[fable] dispatched (revised HEAD), pending
Consensus recorded here once all four APPROVE; no `[OPEN]` blocker remains before implementation.

## Content Review

_(4-way content-review gate — findings `[OPEN]`/`[FIXED]`/`[WONTFIX]`, all resolve before merge)_
