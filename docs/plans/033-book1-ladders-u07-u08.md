# Plan 033 — Book 1 Worked-Example Ladders: U07 + U08 (rollout batch 2)

**Goal:** Apply the proven worked-example-ladder standard (plan 031) to U07 (High-Score Hall) and U08 (Word
Wizard), giving each newly-introduced concept a graduated ladder.

**Architecture:** Same as the plan-031 pilot and the plan-032 batch (both merged): each introduced concept →
minimal → one-step-up → realistic ladder + a one-line `**Notice:**` per rung; completeness + gradual pacing
(exactly one increment per rung — including the "realistic" rung: if the full program jumps hard, add a
bridge rung and frame the full build as a "put it together" application, not a ladder rung); rung count
follows difficulty; reused concepts get a one-line recap. Lesson-only; concepts/exercises/solutions/
checkpoints unchanged; `lessons` counts advisory (book1 budget ceiling `[28, 44]`, current total 36). Standard
defined in `docs/plans/031-book1-worked-examples.md`.

**Tech stack:** Jupyter lesson notebooks; `tools/`; `scripts/ci-local.sh`.

## Global Constraints (closure specifics — reviewer-enforced; concept-scan is unit-level)

A rung uses only concepts taught by its point in the unit's lesson ORDER. Per-unit:
- **Closure here is REVIEWER-ENFORCED, not tool-caught.** concept-scan's builtin/method sets are GLOBAL:
  `sum`, `sorted`, `abs`, `round`, `.keys()`, `.values()` all pass concept-scan GREEN even though these units
  don't teach them. So the author MUST hand-restrict to the taught set below; the Phase C manual audit is the
  real enforcement.
- **U07 High-Score Hall** introduces `list-literal, list-index, list-append, list-loop, list-sort,
  builtin-functions`; union also has `for-loop, range-function, variable, def-function, comparison,
  parameters, return-value, accumulator, f-string, while-loop, string-methods, print, arithmetic, int-type,
  loop-counter, if-statement, elif-else, string-concat, float-type, type-conversion, input, in-operator`.
  `for`-loops are available. **Taught builtins are EXACTLY `len`, `max`, `min`** — NOT `sum` (the unit
  deliberately teaches an accumulator total instead; do not use `sum`). **`list-sort` is `.sort()` and
  `.sort(reverse=True)` ONLY** — never `sorted()`. **Actual intra-unit order: list-literal → index → append →
  loop → builtin-functions (L1) → list-sort (L2)** — builtins come BEFORE sort. A `list-loop` rung (before
  builtins) must use an accumulator total or comparison "best so far", NOT a `max()`/`min()` call (those are
  taught in the next block); `len()` appearing inside a `range(len(...))` loop rung is the sanctioned
  usage-before-naming case (as in the shipped notebook).
- **U08 Word Wizard** introduces `dict-literal, dict-access, dict-loop`; union has `list-loop, list-literal,
  list-append, string-methods, in-operator, def-function, for-loop, parameters, return-value, if-statement,
  f-string, print, variable, comparison, string-concat, elif-else, arithmetic, int-type, input,
  type-conversion, accumulator, boolean, string-literal`. Order: dict-literal → dict-access → dict-loop.
  **Taught dict methods are EXACTLY `.get(key, default)` and `.items()`** — NOT `.keys()`/`.values()` (they
  pass scan green but are untaught → reviewer-caught). `dict-access` rungs use `d[key]` read, `d[key] = value`
  write, and `.get` default; `in` on a dict tests keys (`in-operator` is a require).
- **Execution:** `exec-lessons` runs every non-`no-exec` cell; prefer executable rungs with literal values;
  `no-exec` any `input()`/error rung.
- **Concepts unchanged:** U07/U08 `manifest.concepts` and coverage-map entries stay identical EXCEPT the
  `lessons` count. Exercises/solutions/checkpoints untouched; lessons open project-first.
- **House style:** allowed Book-1 constructs only; unique cell ids; no stored outputs; `**Notice:**` lines;
  teacher-notes `## Pacing` blocks == the new `lessons` count (manual check).

## Out of scope

- U09, U10 (batch 3, plan 034); turtle U03, U05 (batch 4, plan 035).
- Any change to the concept set, exercises, solutions, checkpoints.
- **Verification-phase note:** ships reworked unit lessons WITH a named verification phase (Phase C).

## Phases

### Phase A — U07 "High-Score Hall" lesson ladders

Rework `book1/units/unit-07-high-score-hall/lesson.ipynb` in the actual order **list-literal → index →
append → loop → builtin-functions (L1) → list-sort (L2)**: ladders for `list-literal` (empty `[]` → a few
items → the scores list), `list-index` (`[0]` → another position → `[-1]`), `list-append` (append one → append
again → append inside a loop to build a list), `list-loop` (print each with `for` → accumulate a total with an
accumulator — NOT `max()`), `builtin-functions` (`len` → `max` → `min`, one distinct builtin per rung — NOT
`sum`), `list-sort` (`.sort()` ascending → `.sort(reverse=True)` → rank the hall; never `sorted()`). Executable
rungs with literal lists. Set `manifest.yaml` `lessons: 3` and update teacher-notes `## Pacing`.

### Phase B — U08 "Word Wizard" lesson ladders

Rework `book1/units/unit-08-word-wizard/lesson.ipynb`: ladders for `dict-literal` (one pair → a few pairs →
the word→translation map), `dict-access` (`d[key]` read → `d[key] = value` add/update → `.get(key, default)`
for a safe miss), `dict-loop` (`for key in d` → `for k, v in d.items()` → build a count/translation).
Taught dict methods are ONLY `.get` and `.items()` (no `.keys`/`.values`). Respect order dict-literal →
access → loop. Executable rungs with literal dicts. Set `manifest.yaml` `lessons: 3` and update teacher-notes
`## Pacing`.

### Phase C — map/syllabus + Verification (named verification phase)

- `book1/curriculum/coverage-map.yaml`: U07 `lessons: 3`, U08 `lessons: 3` (= manifests; book1 total 36 → 38,
  ≤ 44). `book1/syllabus.md`: update the U07/U08 arc-table `Lessons` cells, and the figures on line ~4
  ("~36 lessons" → 38), line ~30 ("summing to 36 — 28 unit lessons" → 38/30, and the ladder parenthetical to
  include U07/U08), and line ~31 ("~34–36 class sessions" → ~36–38).
- `scripts/ci-local.sh` ALL GREEN: `exec-lessons`, `concept-scan`, `coverage`/`prereq`, `lesson-budget` (≤ 44),
  manifest==map, structure/hygiene/noexec, PDF build, pre-merge guard. **NOTE: concept-scan will NOT catch a
  `sum`/`sorted()`/`.keys`/`.values` leak (global sets) — the closure audit below is the real guard.**
- **Closure + completeness/gradual audit (primary content-review duty):** no rung uses a later-in-unit/
  untaught concept/method/builtin; each ladder complete + one-increment (incl. the realistic rung — bridge +
  "put it together" framing if it would jump); Notices accurate; lessons open project-first; `## Pacing`
  blocks == `lessons`.

## Post-Execution Report

**Shipped:** worked-example ladders for U07 (High-Score Hall) and U08 (Word Wizard) — rollout batch 2.

**U07** `lesson.ipynb` 35 → 59 cells (24 code, 1 `no-exec`), 3 lesson sections (build → rank → polish).
Ladders: list-literal 3 (`[]`→items→board), list-index 3 (`[0]`→`[2]`→`[-1]`), list-append 3 (one→again→in a
loop), list-loop 3 (print each→accumulate a total→`range(len)` entry numbers), builtin-functions 3
(`len`→`max`→`min`, **no `sum`**), list-sort (`.sort()`→`.sort(reverse=True)`→ranked board with `board_line`,
**no `sorted()`**). `board_line`/`add_score`/tier/membership/threshold/IndexError preserved as realistic
rungs/application. teacher-notes + manifest → 3 lessons.

**U08** `lesson.ipynb` 32 → 33 cells (13 code, 1 `no-exec`), 3 lesson sections (phrasebook → walk → count).
Ladders: dict-literal 3 (one pair→a few→map), dict-access 3 (`d[key]` read→`d[key]=v` add→`.get` default),
dict-loop 3 (`for key in d`→`.items()`→`translate` helper over a list). **Only dict methods `.get`/`.items`.**
KeyError demo + count-log + most-common preserved. teacher-notes + manifest → 3 lessons.

**Phase C / verification:** `ci-local.sh` ALL GREEN. coverage-map U07/U08 `lessons: 3` (= manifests; book1
total 36 → 38 ≤ 44); syllabus arc-table + figures updated (30 unit lessons, 38 total). concept-scan clean
(no `sum`/`sorted`/`.keys`/`.values` — verified by AST, since scan's sets are global); exec-lessons runs every
non-`no-exec` rung clean; closure audit clean. Concepts/exercises/solutions/checkpoints unchanged.

**Deviations:** none.

## Plan Review

### Round 1 (2026-09-09, HEAD ec48926) — [fable] AWN · [glm] REJECT · [sol] pending

Both externals verified U08 is sound (order dict-literal→access→loop; taught methods `.get`/`.items` only)
and metadata is stable. They converge on U07 specifics + a tooling-claim correction:

1. `[FIXED]` **[glm B1 / fable B] `sum` is untaught in U07** — builtins are exactly `len`/`max`/`min` (the
   unit teaches an accumulator total, not `sum`); concept-scan passes `sum` green. → Builtins ladder pinned
   to `len`→`max`→`min` (3 distinct one-increment rungs); `sum` dropped.
2. `[FIXED]` **[glm B2] `sorted()` untaught** — `list-sort` is `.sort()`/`.sort(reverse=True)` only (scan
   passes `sorted` green). → Pinned; `sorted()` removed.
3. `[FIXED]` **[glm B3 / fable A] U07 order mis-stated** — builtins are taught in L1 BEFORE `list-sort` in L2.
   → Order pinned: list-literal → index → append → loop → builtin-functions → list-sort. The `list-loop` rung
   (before builtins) uses an accumulator total, not `max()`.
4. `[FIXED]` **[glm N1 / fable D] overstated tooling claims** — `sum`/`sorted`/`.keys`/`.values` all pass
   concept-scan green (global builtin/method sets), so closure for them is REVIEWER-enforced. → Global
   Constraints + Phase C corrected to say concept-scan will NOT catch these; the manual audit is the guard.
   U08 dict methods pinned to `.get`/`.items` (no `.keys`/`.values` rungs).
5. `[FIXED]` **[glm N2] syllabus figures** — Phase C now names lines 4/30/31 + the ladder parenthetical.

[fable] APPROVE WITH NITS (no blocking); [glm] REJECT on B1–B3 (now fixed). Re-confirming [glm]; [sol] pending.

### Round 2 (HEAD f7077fc) — [glm] AWN · [sol] APPROVE · CONSENSUS

[glm] re-confirm: APPROVE WITH NITS (B1/B2/B3 verified resolved against the tooling; 2 non-blocking nits — the "union has…" enumerations omit a few always-available practices concepts (harmless), and the list-loop print→accumulate rung may need a bridge (content-gate/authoring will enforce one increment)). [sol] re-confirm: APPROVE (all five findings RESOLVED).

**CONSENSUS — plan-review gate CLOSED:** [self] APPROVE · [fable] APPROVE WITH NITS · [glm] APPROVE WITH NITS · [sol] APPROVE. Cleared for implementation. Author note: add a bridge rung if the U07 list-loop print→total rung jumps.

## Content Review

### Round 1 (2026-09-09, HEAD 1909b46) — [self] APPROVE · [glm] AWN · [fable] AWN · [sol] REJECT

All reviewers AST-verified closure clean (U07 only len/max/min + .append/.sort, no sum/sorted; U08 only
.get/.items), executable rungs run clean, conventions clean. [glm]/[fable] APPROVED WITH NITS; [sol] REJECTed
on three pacing jumps (the recurring "realistic rung combines too much" tension — resolved as in batch 1 by a
focused rung + a separate "put it together" application). Findings:

1. `[FIXED]` **[sol, blocking] U07 list-loop realistic rung jumped** (accumulate → `range(len)` + index +
   `#{position+1}` numbering at once). → Split into a bridge rung (position iteration, `print(scores[position])`)
   then the numbered rung (one increment).
2. `[FIXED]` **[sol, blocking] U07 list-sort realistic rung didn't demonstrate sorting + jumped** (straight to
   the `board_line` renderer). → Added a focused sort-use rung (`.sort(reverse=True)` → read `scores[0]`/`[1]`
   as champion/runner-up); `board_line` + `add_score` reframed as "**Put it together**" applications.
3. `[FIXED]` **[sol, blocking] U08 dict-loop realistic rung looped a LIST, not the dict.** → Replaced with a
   focused dict-loop rung (loop `.items()` to count the phrasebook's entries); the translate-helper-over-a-list
   reframed as a "**Put it together**" application.
4. `[FIXED]` **[glm/sol] U07 teacher-notes "Lesson-2 bug" stale** → "Lesson-3 bug".
5. `[FIXED]` **[glm] U07 teacher-notes referenced the removed `winner` demo** → reworded to point at the
   exercises.
6. `[FIXED]` **[glm] U07 append rung 2 thin** (append a literal again) → now appends a value held in a
   variable (a genuine increment).
7. `[FIXED]` **[glm] U07 board_line rung re-declared the list** → now uses the already-sorted `scores` with an
   honest Notice.

U07 now 63 cells, U08 35 cells; all book1 checks PASS. Re-running ci-local + re-dispatching [sol].

### Round 2

_(pending — [sol] on the fixed HEAD; [glm]/[fable] AWN stands, nits fixed)_
