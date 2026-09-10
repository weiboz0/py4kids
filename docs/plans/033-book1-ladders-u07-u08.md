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
- **U07 High-Score Hall** introduces `list-literal, list-index, list-append, list-loop, list-sort,
  builtin-functions`; union also has `for-loop, range-function, variable, def-function, comparison,
  parameters, return-value, accumulator, f-string, while-loop, string-methods, print, arithmetic, int-type,
  loop-counter, if-statement, elif-else, string-concat, float-type, type-conversion, input, in-operator`
  (requires+practices). So `for`-loops ARE available here (list-loop can iterate with `for`). **ENUMERATE at
  authoring which builtins the unit teaches** (`builtin-functions` — likely `len`, `max`, `min`, `sum`; a
  builtin not used by the unit must not appear, and any builtin call must be one concept-scan treats as
  taught). `list-sort` = `.sort()` (in-place) and/or `sorted()` — use the forms the unit teaches. Order:
  list-literal → index → append → loop → sort (confirm against the notebook).
- **U08 Word Wizard** introduces `dict-literal, dict-access, dict-loop`; union has `list-loop, list-literal,
  list-append, string-methods, in-operator, def-function, for-loop, parameters, return-value, if-statement,
  f-string, print, variable, comparison, string-concat, elif-else, arithmetic, int-type, input,
  type-conversion, accumulator, boolean, string-literal`. Order: dict-literal → dict-access → dict-loop. A
  `dict-access` rung may use `d[key]` and `.get()` only if the unit teaches `.get` (enumerate taught dict
  methods; an untaught method reds concept-scan). `in` on a dict tests keys — fine (`in-operator` is a
  require).
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

Rework `book1/units/unit-07-high-score-hall/lesson.ipynb`: ladders for `list-literal` (empty list → a few
items → a list of scores), `list-index` (`[0]` → another position → `[-1]`), `list-append` (append one →
append in a loop to build a list), `list-loop` (print each with `for` → accumulate a total/`max` over the
list), `list-sort` (`.sort()` ascending → reverse/`sorted` as the unit teaches → rank the hall),
`builtin-functions` (the taught builtins, e.g. `len` → `max`/`min` → `sum`, one per rung). Respect order;
executable rungs with literal lists. Set `manifest.yaml` `lessons: 3` (from 2) and update teacher-notes
`## Pacing`.

### Phase B — U08 "Word Wizard" lesson ladders

Rework `book1/units/unit-08-word-wizard/lesson.ipynb`: ladders for `dict-literal` (one pair → a few pairs →
a realistic word→meaning map), `dict-access` (`d[key]` → update/add a key → the taught `.get` default if the
unit teaches it; else membership-guarded access), `dict-loop` (loop keys → use each value → build a
count/translation). Respect order dict-literal → access → loop. Executable rungs with literal dicts. Set
`manifest.yaml` `lessons: 3` (from 2) and update teacher-notes `## Pacing`.

### Phase C — map/syllabus + Verification (named verification phase)

- `book1/curriculum/coverage-map.yaml`: U07 `lessons: 3`, U08 `lessons: 3` (= manifests; book1 total 36 → 38,
  ≤ 44). `book1/syllabus.md`: update the U07/U08 arc-table cells and the "36/28 unit lessons/class-sessions"
  figures (→ 38, 30 unit lessons).
- `scripts/ci-local.sh` ALL GREEN: `exec-lessons`, `concept-scan` (**watch: only taught builtins in U07;
  only taught dict methods in U08; respect within-unit order**), `coverage`/`prereq`, `lesson-budget` (≤ 44),
  manifest==map, structure/hygiene/noexec, PDF build, pre-merge guard.
- **Closure + completeness/gradual audit (primary content-review duty):** no rung uses a later-in-unit/
  untaught concept/method/builtin; each ladder complete + one-increment (incl. the realistic rung — bridge +
  "put it together" framing if it would jump); Notices accurate; lessons open project-first; `## Pacing`
  blocks == `lessons`.

## Post-Execution Report

_(filled at Phase C)_

## Plan Review

_(4-way plan-review gate — consensus before any implementation)_

## Content Review

_(4-way content-review gate — consensus before PR)_
