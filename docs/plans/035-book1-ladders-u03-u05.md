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

- **Lesson turtle code cells MUST be `no-exec`.** `noexec-check` (`tools/notebooks.py`
  `noexec_findings`) FAILs any lesson code cell that imports turtle/tkinter or calls `input()` unless
  it is `no-exec`. So every U03 rung cell (all turtle) is `no-exec`; in U05 the executable rungs are
  plain Python and only the `NameError` scope demo is `no-exec` (turtle in U05 stays as fenced
  ```python excerpts, not cells).
- **Correctness of turtle rungs is verified via `assets/*.py` under `turtle-check`** (headless
  `fake_turtle` stub): each asset must (1) compile, (2) run to completion using only the stub API —
  which is exactly `forward, backward, left, right, penup, pendown, pensize, pencolor, color, speed,
  bgcolor, Screen, done, exitonclick, Turtle` (NO `circle`/`dot`/`stamp`/`hideturtle`/`shape` — those
  AttributeError under the stub; U05's `stamp` is a USER-DEFINED function built from `forward`/`right`,
  never `turtle.stamp()`), (3) make ≥1 pen-down move, (4) stay under 10000 moves, and (5) **close the
  path** — return to the draw-start position AND total heading change ≡ 0 (mod 360) — UNLESS the file
  carries the bare exact comment `# turtle-check: open-path` (token-matched — no trailing text) for a
  deliberately open figure (e.g. an "L" or a single stroke).
- **`turtle.done()` must be the LAST statement of every asset** (real `done()` blocks; the stub
  no-ops it, so NO tool — `turtle-check` included — can catch code after it; **reviewer-enforced**, see
  `turtle-asset-conventions`). One drawing concern per asset, single `done()` at the end.
- **Asset rules (tooling-enforced by `structure-check`):** every `assets/foo.py` named in a notebook
  (`python assets/foo.py`) must exist, and all assets must compile. New runnable rungs each ship an
  asset; the notebook cell mirrors the asset and is `no-exec`. A rung that is illustration-only
  (read/trace, not run) may be a `no-exec` cell with no asset, but PREFER a runnable asset so students
  see the drawing.

## Global Constraints (closure specifics — reviewer-enforced; concept-scan is unit-level/global-sets)

- **U03 Turtle Art Studio** introduces `turtle-basics, turtle-drawing, for-loop, range-function,
  loop-counter, nested-loops, float-type`; requires `import-statement, variable, arithmetic`;
  practices `naming, comment, run-program, f-string, string-literal`. **No conditionals, no lists, no
  string methods, no functions** (functions are U05) — rungs stay within this union. Lesson order and
  co-teaching:
  - **L1 — Ladder A: `turtle-basics` + `turtle-drawing` (CO-TAUGHT** — moving and drawing are the same
    pen primitives). Rungs 2–5 are written OUT (no `for` — that is L2), and each rung adds EXACTLY one
    pen action so its Notice names one thing: rung 1 `forward` + one `right` turn (an open corner —
    asset carries the bare `# turtle-check: open-path`); rung 2 the full four-sided square, commands
    written out (closes); rung 3 **travel** — `penup`/`pendown` to move without drawing (lift, hop,
    drop, then draw a shape); rung 4 **color** — `color("blue")` on the shape; rung 5 **thickness** —
    `pensize(4)` on the shape. (Per the batch-4 gate, pen-travel, color, and thickness are three
    separate increments, not one "styling" rung.) `import turtle` recap up top.
  - **L2 — Ladder B: `for-loop` + `range-function` + `loop-counter` (CO-TAUGHT** — Python's loop IS
    `for i in range(n)`): rung 1 redraw the square with `for side in range(4)` (the loop replaces the
    written-out repetition — one increment); rung 2 a hard-coded triangle — `for side in range(3)`
    with the typed literal `angle = 120` (an `int`; the increment is "change the side count"); rung 3
    tie the angle to the count with `n` + `angle = 360 / n` (**`float-type` CO-TAUGHT here** — it is
    INSEPARABLE from the computed angle: Python's `/` ALWAYS yields a float, so `360 / 5` is `72.0` and
    `360 / 7` is `51.428…`; the focused Notice names that `/` makes a decimal the turtle turns by just
    the same). rung 4 use the `loop-counter` to vary each side (`pensize = side_number + 1`). `angle =
    360 / n` is arithmetic (in `requires`); `pensize = side_number + 1` is counter-derived, NOT an
    accumulator (no read-modify-write of one variable). (NOTE: a "compute from `n` but still `int`"
    rung is impossible — `360 / n` is a float for every `n` — so computed-angle and `float-type` share
    one co-taught rung rather than being split.)
  - **L3 — Ladder C: `nested-loops`**: rung 1 a minimal nest — an outer `for` repeating a square twice
    with a `right(90)` between (`2 × 90 = 180`? NO — pick a turn whose total closes: two squares with
    `right(180)` between → `2 × 180 = 360`, closes); rung 2 step up — more repeats / a smaller
    between-turn whose `shape_count × turn ≡ 0 (mod 360)` (e.g. `6 × 60`), else the asset carries
    `open-path`; rung 3 the full spirograph as a **"Put it together"** runnable gallery.
- **U05 Function Factory** introduces `def-function, parameters, return-value, scope`; requires
  `turtle-basics, turtle-drawing, for-loop, variable, f-string`; practices `range-function,
  loop-counter, arithmetic, nested-loops, float-type, accumulator, import-statement, string-literal`.
  Executable rungs are PLAIN PYTHON (run under `exec-lessons`); turtle stays as fenced ```python
  excerpts + runnable assets. Lesson order:
  - **L1 — Ladder A: `def-function`**: rung 1 define a NO-parameter function (`def banner(): print(...)`)
    and call it; rung 2 call it several times (define once, call many). **Ladder B: `parameters`**:
    rung 1 one parameter (`greeting_card(name)`); rung 2 two parameters (`card(name, message)`). (The
    two ladders are kept SEPARATE — the no-parameter `def` rung introduces the function idea cleanly
    before a blank-to-fill is added; this fixes the current notebook's conflation of `def` and
    `parameters` in one cell.)
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

- `scripts/ci-local.sh` ALL GREEN: `noexec-check` (all turtle/GUI/`input` lesson cells `no-exec`),
  `structure-check` (referenced assets exist + all assets compile), `exec-lessons` (U05 plain-Python
  rungs run clean; error/turtle cells skipped), `turtle-check` (every U03 asset completes, ≥1
  pen-down, <10000 moves, closes or `open-path`), `concept-scan` (unit-level concept union only — it
  does NOT check within-unit order, so lesson-order closure is the manual audit's job below;
  `loop-counter`/`scope` are MANUAL_ONLY in concept-scan), `coverage`/`prereq`, manifest==map
  (unchanged), hygiene, PDF, pre-merge guard. `done()`-last is NOT tool-checkable — audited manually.
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

### Round 1 (HEAD 8ad8b24) — [self] APPROVE

- **Closure ✓** — U03 ladders use only turtle primitives + `for`/`range`/`loop-counter`/
  `nested-loops`/`float-type` + `import`/`variable`/`arithmetic` + `f-string`/`string-literal`; NO
  functions/conditionals/lists/string-methods (all other units). U05 executable rungs are plain
  Python (`def`/`parameters`/`return`/`scope` + `print`/`f-string`/`arithmetic`); turtle stays fenced.
- **Turtle contract ✓** — verified against `tools/notebooks.py` (`noexec-check` FAILs a non-`no-exec`
  GUI/`input` lesson cell; structure-check does asset existence/compile) and `tools/fake_turtle.py`
  (closure = return-to-start AND heading ≡ 0 mod
  360, `# turtle-check: open-path` escape hatch, ≥1 pen-down, <10000 moves, stub API); `done()`-last
  is reviewer-enforced. Plan's model is accurate.
- **Pacing ✓** — ladders one-increment; co-taught pairs (`turtle-basics`+`turtle-drawing`;
  `for`+`range`+`counter`; `def`+`parameters`) each get a focused rung; `float-type` focused Notice at
  `360/n`; spirograph + turtle galleries framed "Put it together". Named verification Phase C present;
  both units stay 3 lessons (no figure changes).
- **Author watch-items (not blocking):** (a) U03 Ladder A rung 1 open corner MUST carry
  `# turtle-check: open-path`; (b) every nested-loops asset must close — pick between-shape turns whose
  sum is a multiple of 360 (e.g. 24×15°, 3×120°); (c) `done()` last in every asset; (d) re-sync both
  teacher-notes `## Pacing` bullets to the rebuilt rungs.

**[glm] APPROVE WITH NITS · [fable] APPROVE WITH NITS** (HEAD 8ad8b24). Both verified: closure
(unions + order), turtle contract (closure math, open-path fork, `done()`-last reviewer-enforced),
one-increment ladders with focused co-taught rungs + `float-type` Notice, and the named Phase C. All
findings `[FIXED]` in the plan text (glm G1–G6 / fable N1–N6 overlap):

1. `[FIXED]` **[glm G1 / fable N1] stub-API list overstated** — removed `circle/dot/stamp/hideturtle/
   shape` (verified absent from `tools/fake_turtle.py`; stub is exactly forward/backward/left/right/
   penup/pendown/pensize/pencolor/color/speed/bgcolor/Screen/done/exitonclick/Turtle); noted U05
   `stamp` is a user-defined function, never `turtle.stamp()`.
2. `[FIXED]` **[glm G2/G4 / fable N2] tool attribution** — no-exec enforced by `noexec-check` (not
   structure-check); structure-check does asset existence/compile; `done()`-last and within-unit
   lesson order are manual/reviewer duties, not `turtle-check`/`concept-scan`. Contract + Phase C
   reworded.
3. `[FIXED]` **[glm G3] open-path comment** — stated it must be the bare token `# turtle-check:
   open-path` (no trailing text).
4. `[FIXED]` **[fable N4 / glm G5] U03 L1 pen rung split** — travel (`penup`/`pendown`) and stroke
   styling (`color`/`pensize`) are now two rungs, one category each.
5. `[FIXED]` **[fable N6] U03 L2 float jump** — added a hard-coded triangle bridge (`range(3)`,
   `angle = 120`) before the general `360/n` float rung.
6. `[FIXED]` **[fable N3] nested-loops one-rung** — L3 now has two genuine rungs (minimal 2×square with
   a closing between-turn; step-up more repeats/smaller turn) before the spirograph "Put it together".
7. `[FIXED]` **[fable N5 / glm G6] U05 def/parameter parenthetical** — removed the contradiction; the
   no-parameter `def` rung and the `parameters` ladder stay separate.

**[sol] REJECT** (HEAD 8ad8b24) — confirmed unions/order, the open-path fork, the turtle-check math,
U05's ordered ladders, the named Phase C, and no scope creep. Three must-changes, all overlapping
glm/fable and now `[FIXED]` with FINER splits than round-1:

- `[FIXED]` **[sol #5]** U03 Ladder A bundled pen-lift/lower + color + pensize. → Now FIVE rungs:
  move+turn, square, `penup`/`pendown` travel, `color`, `pensize` — three separate pen increments.
- `[FIXED]` **[sol #6]** U03 Ladder B coupled "generalize via `n`" with "float appears". → Now split:
  rung 3 `n=5` (`360/5=72`, still whole — the "compute the turn from `n`" increment) then rung 4 `n=7`
  (`360/7` — the `float-type` increment, its own focused Notice).
- `[FIXED]` **[sol #4/#2]** checker contract — already corrected (noexec-check attribution, real stub
  API, manual lesson-order) in fixes 1–2 above.

### Round 2 (HEAD e4051ad) — re-dispatched to [sol]

The round-1 fixes only TIGHTEN pacing (more granular rungs) and correct plan-text tool attributions;
they introduce no new closure risk, so [glm]/[fable] APPROVE-WITH-NITS (all their findings `[FIXED]`)
carry forward. Re-dispatching [sol] (the sole REJECT) to confirm the two finer splits.

**[sol] REJECT** (HEAD e4051ad) — Ladder A five-rung split confirmed resolved; closure math confirmed
(`2×180`, `6×60 ≡ 0 mod 360`). Two must-changes, both a correct catch, now `[FIXED]`:

- `[FIXED]` **[sol #2] Ladder B `360/5` is `72.0`, a float** — Python's `/` always yields a float, so a
  "compute from `n` but still `int`" rung 3 is impossible; my `n=5` whole-number rung was wrong. →
  Redesigned: computed-angle and `float-type` are now ONE CO-TAUGHT rung 3 (`angle = 360 / n`,
  inseparable — `/` always makes a decimal), preceded by the typed-literal `int` triangle (rung 2).
  Ladder B is now 4 rungs; float gets its focused Notice on the co-taught rung.
- `[FIXED]` **[sol #3] stale Round-1 self-review line** said `structure-check` enforces `no-exec`. →
  Corrected to `noexec-check` (structure-check does asset existence/compile).

### Round 3 (HEAD 0d970e2) — [sol] APPROVE

Both round-2 must-changes verified resolved: Ladder B computed-angle + `float-type` legitimately
co-taught (a pre-float `int` computed rung is impossible — `/` always yields a float), and no
remaining `structure-check`/`no-exec` misattribution anywhere in the file. No new nits or blockers.

**CONSENSUS — plan-review gate CLOSED:** [self] APPROVE · [sol] APPROVE · [glm] APPROVE WITH NITS ·
[fable] APPROVE WITH NITS. Cleared for implementation. Author notes: U03 Ladder A = 5 pen rungs
(move+turn open-path, square, penup/pendown, color, pensize); Ladder B = 4 rungs (range(4) square,
range(3) int triangle, `360/n` float co-taught, loop-counter pensize); Ladder C = 2 genuine nested
rungs + spirograph "Put it together". Every asset: `done()` last, closes or bare `# turtle-check:
open-path`. U05 = plain-Python def/parameters/return/scope ladders + `no-exec` NameError + fenced
turtle "Put it together".

## Content Review

_(4-way content-review gate — consensus before PR)_
