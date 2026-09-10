# Plan 035 — Book 1 Worked-Example Ladders: U03 + U05 (rollout batch 4, FINAL)

**Goal:** Apply the proven worked-example-ladder standard (plan 031) to the two turtle units — U03
(Turtle Art Studio) and U05 (Function Factory) — completing the Book-1 rollout (U01–U10).

**Architecture:** Same standard as merged plans 031–034: each concept a unit INTRODUCES gets a
graduated ladder (minimal → one step up → realistic) each followed by a one-line `**Notice:**` naming
the SINGLE new thing; **completeness + gradual pacing** (exactly one increment per rung — the
"realistic" rung stays FOCUSED; full multi-concept programs become separate **"Put it together:"**
cells); rung count follows difficulty; reused concepts get a one-line recap. Lesson-only;
concepts/exercises/solutions unchanged. **Both units are ALREADY 3 lessons and STAY 3** (ladders add
rungs within the existing L1/L2/L3 arc, as U10 did) — so `lessons`, coverage-map, and syllabus
figures are UNCHANGED. Standard in `docs/plans/031-book1-worked-examples.md`; batch-3 gate lessons
folded in below.

**Tech stack:** Jupyter lesson notebooks; turtle `assets/*.py`; `tools/` (`turtle-check`,
`fake_turtle`); `scripts/ci-local.sh`.

## Turtle execution contract (verified in tooling — the batch-specific risk)

- **Lesson turtle code cells MUST be `no-exec`.** `structure-check` FAILs any lesson code cell that
  imports turtle/tkinter or calls `input()` unless it is `no-exec` (`tools/notebooks.py`). So every
  U03 rung cell (all turtle) is `no-exec`; in U05 the executable rungs are plain Python and only the
  `NameError` scope demo is `no-exec` (turtle in U05 stays as fenced ```python excerpts, not cells).
- **Correctness of turtle rungs is verified via `assets/*.py` under `turtle-check`** (headless
  `fake_turtle` stub): each asset must (1) compile, (2) run to completion using only the stub API
  (`forward/backward/left/right/penup/pendown/pensize/pencolor/color/speed/bgcolor/Screen/done/`
  `exitonclick/Turtle/circle/dot/stamp/hideturtle/shape`), (3) make ≥1 pen-down move, (4) stay under
  10000 moves, and (5) **close the path** — return to the draw-start position AND total heading change
  ≡ 0 (mod 360) — UNLESS the file carries a `# turtle-check: open-path` comment (the sanctioned escape
  hatch for a deliberately open figure, e.g. an "L" or a single stroke).
- **`turtle.done()` must be the LAST statement of every asset** (real `done()` blocks; the stub
  no-ops it, so `turtle-check` CANNOT catch code after it — reviewer-enforced, see
  `turtle-asset-conventions`). One drawing concern per asset, single `done()` at the end.
- **Asset reference rule:** every `assets/foo.py` named in a notebook (`python assets/foo.py`) must
  exist and compile. New runnable rungs each ship an asset; the notebook cell mirrors the asset and
  is `no-exec`. A rung that is illustration-only (read/trace, not run) may be a `no-exec` cell with no
  asset, but PREFER a runnable asset so students see the drawing.

## Global Constraints (closure specifics — reviewer-enforced; concept-scan is unit-level/global-sets)

- **U03 Turtle Art Studio** introduces `turtle-basics, turtle-drawing, for-loop, range-function,
  loop-counter, nested-loops, float-type`; requires `import-statement, variable, arithmetic`;
  practices `naming, comment, run-program, f-string, string-literal`. **No conditionals, no lists, no
  string methods, no functions** (functions are U05) — rungs stay within this union. Lesson order and
  co-teaching:
  - **L1 — Ladder A: `turtle-basics` + `turtle-drawing` (CO-TAUGHT** — moving and drawing are the same
    pen primitives): rung 1 `forward` + one `right` turn (an open corner — asset carries
    `# turtle-check: open-path`); rung 2 the full four-sided square (closes); rung 3 pen control —
    `penup`/`pendown` + `color`/`pensize` on a shape (closes). `import turtle` recap up top.
  - **L2 — Ladder B: `for-loop` + `range-function` + `loop-counter` (CO-TAUGHT** — Python's loop IS
    `for i in range(n)`): rung 1 redraw the square with `for side in range(4)`; rung 2 any regular
    polygon via `n` + `angle = 360 / n` (**`float-type` co-taught here** with its own focused Notice
    that `360/n` can be a decimal); rung 3 use the `loop-counter` to vary each side (`pensize =
    side_number + 1`). `angle = 360 / n` is arithmetic (in `requires`); `pensize = side_number + 1`
    is counter-derived, NOT an accumulator (no read-modify-write of one variable).
  - **L3 — Ladder C: `nested-loops`**: rung 1 an outer loop repeating one polygon a few times with a
    small turn between (closes if `shape_count * turn ≡ 0 mod 360`, else `open-path`); rung 2 the full
    spirograph as a **"Put it together"** runnable gallery.
- **U05 Function Factory** introduces `def-function, parameters, return-value, scope`; requires
  `turtle-basics, turtle-drawing, for-loop, variable, f-string`; practices `range-function,
  loop-counter, arithmetic, nested-loops, float-type, accumulator, import-statement, string-literal`.
  Executable rungs are PLAIN PYTHON (run under `exec-lessons`); turtle stays as fenced ```python
  excerpts + runnable assets. Lesson order:
  - **L1 — Ladder A: `def-function`**: rung 1 define a no-parameter function and call it; rung 2 call
    it several times (define once, call many). **Ladder B: `parameters`**: rung 1 one parameter
    (`greeting_card(name)`); rung 2 two parameters (`card(name, message)`). (def + first parameter may
    share the introducing rung — a function is naturally introduced with a job to do; give
    `parameters` its own focused rung/Notice, the co-taught pattern from earlier batches.)
  - **L2 — Ladder C: `return-value`**: rung 1 `def area(w, h): return w * h`, store + use the result;
    rung 2 `def polygon_points(n): return 360 / n` used in an f-string (`float-type` recap). Keep the
    return-vs-print contrast Notice.
  - **L3 — Ladder D: `scope`**: rung 1 local vs global (a function reads a global, makes a local,
    returns it); rung 2 the `NameError` bug — printing a local outside its function (**`no-exec`**).
  - Turtle stamp/shape/gallery excerpts stay as fenced ```python tied to the kept assets
    (`l1_cards.py`, `l2_shapes.py`, `l3_stamps.py`) — framed **"Put it together"** applications.
- **Execution:** `exec-lessons` runs U05's plain-Python rungs (one kernel); U05 `NameError` demo and
  ALL U03 turtle cells are `no-exec`. `turtle-check` runs every `assets/*.py`.
- **Concepts unchanged:** manifests + coverage-map entries identical (both stay `lessons: 3`).
  Exercises/solutions untouched; lessons open project-first.
- **House style:** allowed Book-1 constructs; unique cell ids; no stored outputs; `**Notice:**` lines;
  teacher-notes `## Pacing` blocks == 3 lessons each (re-sync bullet framing to the rebuilt rungs).

## Out of scope

- Any change to concepts/exercises/solutions, to `lessons` counts, or to coverage-map/syllabus figures
  (both units already 3 lessons). Non-turtle units (all merged, plans 031–034).
- **Verification-phase note:** ships reworked unit lessons WITH a named verification phase (Phase C).

## Phases

### Phase A — U03 "Turtle Art Studio" lesson ladders + assets

Rework `book1/units/unit-03-turtle-art-studio/lesson.ipynb` into the three ladders above; every turtle
code cell `no-exec`. Add/refresh `assets/*.py` so each runnable rung has a compiling, `turtle-check`-
passing asset with `done()` last (closing, or `# turtle-check: open-path` for the open corner). Keep
the existing spirograph as the L3 "Put it together" gallery. Update `teacher-notes.md` `## Pacing`
framing (stays 3 lessons). Referenced asset names in the notebook must match shipped files.

### Phase B — U05 "Function Factory" lesson ladders

Rework `book1/units/unit-05-function-factory/lesson.ipynb`: plain-Python executable ladders for
`def-function`, `parameters`, `return-value`, `scope` (per order above); the `NameError` scope demo
stays `no-exec`; turtle stamp/shape/gallery stay as fenced ```python "Put it together" excerpts tied
to the kept assets. Update `teacher-notes.md` `## Pacing` framing (stays 3 lessons).

### Phase C — Verification (named verification phase)

- `scripts/ci-local.sh` ALL GREEN: `structure-check` (all turtle/GUI/`input` cells `no-exec`),
  `exec-lessons` (U05 plain-Python rungs run clean; error/turtle cells skipped), `turtle-check` (every
  U03 asset compiles, completes, ≥1 pen-down, closes or `open-path`, `done()` last), `concept-scan`
  (closure within each union + lesson order), `coverage`/`prereq`, manifest==map (unchanged),
  hygiene/noexec, PDF, pre-merge guard.
- `book1/syllabus.md`: update ONLY the ladder parenthetical to name U03 + U05 as reworked (no figure
  changes — both stay 3 lessons; total remains 39).
- **Closure + completeness/gradual audit (primary content-review duty):** no rung uses a later-in-
  unit/untaught concept (U03 has no functions/conditionals/lists; U05 executable rungs are plain
  Python); each ladder complete + one-increment with the realistic rung FOCUSED (spirograph / turtle
  galleries framed "Put it together"); co-taught `turtle-basics`+`turtle-drawing`,
  `for`+`range`+`counter`, `def`+`parameters` each get a genuine focused rung; `float-type` gets a
  focused Notice at `360/n`; Notices name exactly one new thing; every U03 asset has `done()` last;
  lessons open project-first; `## Pacing` blocks == 3 lessons.

## Post-Execution Report

_(filled at Phase C)_

## Plan Review

_(4-way plan-review gate — consensus before implementation)_

## Content Review

_(4-way content-review gate — consensus before PR)_
