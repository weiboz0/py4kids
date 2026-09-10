# Plan 034 — Book 1 Worked-Example Ladders: U09 + U10 (rollout batch 3)

**Goal:** Apply the proven worked-example-ladder standard (plan 031) to U09 (Save Point — files) and U10
(Pet Simulator — classes), the Book-1 finale units.

**Architecture:** Same as the merged plan-031/032/033 batches: each introduced concept → minimal →
one-step-up → realistic ladder + one-line `**Notice:**`; completeness + gradual pacing (exactly one increment
per rung — the "realistic" rung stays FOCUSED on the concept; the full multi-concept program becomes a
separate **"Put it together:"** application cell, NOT a ladder rung — the pattern [sol] required in batches
1–2); rung count follows difficulty; reused concepts get a one-line recap. Lesson-only; concepts/exercises/
solutions/checkpoints unchanged; `lessons` advisory (book1 budget `[28, 44]`, current total 38). Standard in
`docs/plans/031-book1-worked-examples.md`.

**Tech stack:** Jupyter lesson notebooks; `tools/`; `scripts/ci-local.sh`.

## Global Constraints (closure specifics — reviewer-enforced; concept-scan is unit-level/global-sets)

- **U09 Save Point** introduces `file-read, file-write, with-statement`; union has `list-append,
  string-methods, def-function, for-loop, parameters, return-value, list-loop, dict-access, f-string,
  in-operator, builtin-functions, dict-literal, if-statement, list-literal, print, variable, string-concat,
  string-literal, type-conversion, int-type, error-messages, input`. Order: file-write → file-read;
  **`with-statement` is CO-TAUGHT** — it wraps every file op (`with open(...) as f:`), so it shares the
  write/read ladders with its own focused "the `with` block closes the file automatically" rung/Notice (the
  import+random pattern from batch 1). Real file I/O EXECUTES under `exec-lessons` (writes/reads
  `savegame.txt`/`settings.txt`, as the shipped lesson already does) — keep the same filenames; the
  `FileNotFoundError` demo stays `no-exec`. Taught string method here: `.strip()`.
- **U10 Pet Simulator** introduces `class-def, init-method, attributes, methods`; union has `def-function,
  parameters, return-value, dict-access, while-loop, f-string, if-statement, accumulator, list-append,
  arithmetic, comparison, dict-literal, elif-else, for-loop, list-loop, list-literal, list-index, print,
  variable, int-type, input`. Order: class-def + `__init__` (CO-TAUGHT — a class is introduced with its
  `__init__`) → attributes (`self.x`, read/change) → methods. The class is re-defined to add methods (fine in
  one kernel). The `AttributeError` misspelling demo stays `no-exec`.
- **Execution:** `exec-lessons` runs every non-`no-exec` cell in one kernel; prefer executable rungs; `no-exec`
  the error demos. (U09 has no `input()` rungs in the core; U10's are executable with literal calls.)
- **Concepts unchanged:** U09/U10 `manifest.concepts` + coverage-map entries identical EXCEPT `lessons`.
  Exercises/solutions/checkpoints untouched; lessons open project-first.
- **House style:** allowed Book-1 constructs; unique ids; no stored outputs; `**Notice:**` lines;
  teacher-notes `## Pacing` blocks == the new `lessons` count.

## Out of scope

- Turtle units U03, U05 (final batch, plan 035). Any change to concepts/exercises/solutions/checkpoints.
- **Verification-phase note:** ships reworked unit lessons WITH a named verification phase (Phase C).

## Phases

### Phase A — U09 "Save Point" lesson ladders

Rework `book1/units/unit-09-save-point/lesson.ipynb`: ladders for `file-write` (`with open("f","w") as f:
f.write(one line)` → write several lines with a loop → write a mixed settings file), `file-read` (read the
whole file with `.read()` → loop the file object line-by-line → build a list with `.strip()`+`int()`+
`.append()`), with `with-statement` given a focused Notice/rung that the `with` block auto-closes the file.
`load_scores` helper + the `in`-search settings read become **"Put it together:"** applications. `\n` newline
explained. Set `manifest.yaml` `lessons: 3` (from 2) and update teacher-notes `## Pacing`.

### Phase B — U10 "Pet Simulator" lesson ladders

Rework `book1/units/unit-10-pet-simulator/lesson.ipynb`: ladders for `class-def`+`init-method` (a minimal
`class Pet` with `__init__` setting one attribute → set several attributes), `attributes` (read `buddy.name`
→ two independent objects → change an attribute `luna.hunger = 7`), `methods` (add one method → a method with
a parameter (`feed(amount)`) → a method that changes attributes (`play`/`pass_time`) → a method that returns
(`status`)). The foods-dict feed, the multi-pet loop, and the `while buddy.happiness < 10` play-loop become
**"Put it together:"** applications. Set `manifest.yaml` `lessons: 3` (from 2) and update teacher-notes
`## Pacing`.

### Phase C — map/syllabus + Verification (named verification phase)

- `book1/curriculum/coverage-map.yaml`: U09 `lessons: 3`, U10 `lessons: 3` (= manifests; book1 total 38 → 40,
  ≤ 44). `book1/syllabus.md`: update the U09/U10 arc-table `Lessons` cells and the "38 / 30 unit lessons /
  ~36–38 class sessions" figures (→ 40, 32 unit lessons) + the ladder parenthetical.
- `scripts/ci-local.sh` ALL GREEN: `exec-lessons` (file I/O + class cells run clean), `concept-scan`,
  `coverage`/`prereq`, `lesson-budget` (≤ 44), manifest==map, structure/hygiene/noexec, PDF, pre-merge guard.
- **Closure + completeness/gradual audit (primary content-review duty):** no rung uses a later-in-unit/
  untaught concept; each ladder complete + one-increment with the realistic rung FOCUSED (full programs
  framed "Put it together"); co-taught `with-statement` / `class-def`+`__init__` each get a genuine focused
  rung; Notices accurate; lessons open project-first; `## Pacing` blocks == `lessons`.

## Post-Execution Report

_(filled at Phase C)_

## Plan Review

_(4-way plan-review gate — consensus before any implementation)_

## Content Review

_(4-way content-review gate — consensus before PR)_
