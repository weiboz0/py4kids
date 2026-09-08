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
  executable cell; the `import sys; print(solve(sys.stdin.read()))` wrapper appears ONLY in a
  `no-exec`-tagged checkpoint cell or teacher-notes (NEVER in solutions.ipynb). Deterministic.
- **Checkpoint structure (structure-check):** required files are exactly `manifest.yaml`,
  `checkpoint.ipynb`, `solutions.ipynb`, `teacher-notes.md`. Problem headings are `## Question N`
  (NOT `## Exercise`/`## Problem`) — **≥ 6 required**. Student code cells are EMPTY (`''`).
  Checkpoints have NO stretch tier. teacher-notes has exactly SIX headings — the five unit headings
  `## Goals`/`## Pacing`/`## Common mistakes`/`## Discussion prompts`/`## Differentiation` PLUS
  `## Grading` (points per question + total, and the time budget).
- **Closure (same scanner rules as U04/U05):** only Book-1 + U01–U05 concepts. set-ops ONLY via
  `.add`/`.discard`/`.remove` on a `{…}`/`set()` var in-cell, or `-`; NEVER `&|^`; NEVER
  `.union`/`.intersection`/`.difference`. `sorted(seq, key=named_fn)` (NO lambda). binary-search
  `lo/hi/mid` and fixed-depth nested-loop complete-search are allowed (taught in U05); **NO recursion,
  NO subset/permutation generation, NO converging two-pointer scan** (U09/U11/U14). NO comprehensions/
  generator expressions (`comprehension` is U09). NO untaught methods (.join/.splitlines/.index/.count/
  .find/.pop). Allowed builtins ONLY `{len,min,max,sorted,sum,abs,round}` — NO `all`/`any`/`enumerate`/
  `zip`/`reversed`/`map`/`filter`. concept-scan `--book book2` must be clean.
- **Two-tier metadata:** `introduces: []`. `requires:` = the U01–U05 introduced concepts actually
  assessed (trim any not used, per manifest==map + the requires-are-genuine convention). `practices:` =
  scanner-derived features (`str-split`, and any U04 feature used) + hand-listed techniques
  (`input-parse`, and `complexity`/`binary-search`/`complete-search`/`boolean-algebra` if a problem
  genuinely uses them) + the Book-1 concepts the solutions use, minus wrapper artifacts (`file-read`,
  `import-statement`). `requires ∩ practices = ∅`; manifest == coverage-map exactly.
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

- [ ] **A1 — checkpoint.ipynb.** Opening markdown: contest title, the time budget (~60–75 min for the
  class sitting), rules (each `solve(data)` reads the whole input string; submit via the wrapper), and a
  points table pointer. Then 6 `## Question N` problems, each: title (### …), one-paragraph statement,
  `### Constraints`, `### Sample Input`, `### Sample Output` (```text fences), then an EMPTY code cell.
  Coverage: Q1 input/grid parsing (U01), Q2 boolean-logic rule (U02), Q3 efficiency-sensitive count/scan
  whose constraints (N up to ~1e5/2e5) force O(n)/O(n log n) (U03), Q4 sets/dedup + tuple-keyed sort
  (U04), Q5 binary-search query/count (U05), Q6 fixed-depth complete-search or search-over-answer (U05).
  Include one `no-exec`-tagged cell showing the submission wrapper. Decisive values placed last / after
  sort. Unambiguous single-reading statements.
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
  and the time budget; `## Pacing` frames the single timed sitting (0.5 lesson); a per-question Big-O line;
  which Term-1 unit each question assesses.
- [ ] **B2 — manifest.yaml + map (inline).** `introduces: []`; `requires:` = the U01–U05 concepts actually
  assessed (trim unused); `practices:` = scanner-derived features + hand-listed techniques (`input-parse`
  etc.) + Book-1 concepts used (minus wrapper artifacts); `requires ∩ practices = ∅`; `practices ∩
  introduces = ∅` (trivially, introduces empty). Copy identically into the coverage-map CP1 entry
  (manifest == map). Derive `practices` from an ad-hoc `detect()` over both notebooks (concept-scan is
  one-directional); hand-add any genuinely-used-but-scanner-invisible concept (e.g. `dict-access`,
  techniques).

### Phase C — Verification (named verification phase)

- [ ] **C1 — blind-solve + mutation self-check** on both notebooks (off-by-one, wrong-aggregate, self-pair,
  boundary, decisive-last-after-sort — every mutant fails an assert; every pristine solver passes; use a
  step cap for binary-search mutants). Confirm each of the assessed U01–U05 concepts is genuinely exercised
  (ad-hoc `detect()` for features; manual for techniques). Fix any vacuous assert.
- [ ] **C2 — full `scripts/ci-local.sh` ALL GREEN both books.**
- [ ] **C3 — commit Phase A+B+C** on `feature/plan-021-book2-cp1`.
- [ ] **C4 — 4-way content-review gate** ([self]/[sol]/[glm]/[fable], read-only, HEAD-pinned): blind-solve
  all 6; mutation sweep (categories above); closure (no untaught builtins/methods, no premature technique —
  no converging two-pointer/recursion/subset-gen; features listed); `## Question N` headings ≥6, empty
  student cells, no-exec wrapper isolation; teacher-notes six headings incl `## Grading`; manifest==map;
  each problem prereq-closed to U01–U05; the set collectively covers the term. Resolve every `[OPEN]`;
  re-verify fixes in round-2 before consensus.
- [ ] **C5 — write the post-execution report** in this file + re-run full `ci-local.sh` ALL GREEN after any
  content-gate fix — both precede the PR.
- [ ] **C6 — PR** → `pre-merge-guard.sh --pr` OK → squash-merge → delete branch → update memory.

## Post-Execution Report

_(filled at Phase C)_

## Plan Review

_(4-way plan-review gate verdicts recorded here before implementation)_

## Content Review

_(4-way content-review gate — findings `[OPEN]`/`[FIXED]`/`[WONTFIX]`, all resolve before merge)_
