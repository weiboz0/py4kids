# Plan 073 — Book 1b Unit 06 (Turtle Geometry)

**Origin:** Book 1b buildout ("full book 1b implementation").
**Design:** `docs/designs/005-book1b-concept-first.md` §3 (U06 row), §7 (turtle exercises verified by
execution + `turtle-check`, exempt from output asserts), §8 (turtle runs as `.py` scripts).
**Templates:** Book 1b U01–U05 for prose/teacher-notes conventions; **Book 1's `unit-03-turtle-art-studio`
for the turtle FILE STRUCTURE** (assets/*.py + no-exec lesson cells + turtle-check).

## Scope

One unit — **U06 Turtle Geometry** — authored in the turtle format. It is done ALONE (distinct format).
The next checkpoint is after U08, so no checkpoint here. Book 1b stays `buildout: true`.

## Coverage-map entry (the contract)

**unit-06-turtle-geometry** — `lessons: 3`
- introduces: `[import-statement, turtle-basics, turtle-drawing]`
- requires: `[for-loop, range-function, arithmetic, variable]`
- practices: `[nested-loops, loop-counter, int-type, comment, naming]`

Closure: requires ⊆ U01–U05 (for-loop/range U05; arithmetic U02; variable U01). No self-practice.
`import-statement` is introduced HERE (`import turtle` is its first structural need — design §3/§5).
30 → 33 concepts introduced. Metadata honest: nested-loops (spirals/rings), loop-counter, int-type,
comment, naming are all used by the turtle scripts.

### Design §6 practice-coverage record
All concepts introduced through U06 are practiced: `import-statement`/`turtle-basics`/`turtle-drawing` in
U06 (and later — turtle practice sites in U07 `draw_polygon`, U08 turtle random walk per design §3);
`nested-loops`/`loop-counter` (U05/U04) practiced by U06's spirals/rings. Everything else unchanged from
plan 072's record. Capstone anchor stays dormant (buildout).

## File structure (clone Book 1 `unit-03-turtle-art-studio`)

Turtle code lives in `book1b/units/unit-06-turtle-geometry/assets/*.py`, run HEADLESS by `turtle-check`
(the `fake_turtle` stub records the turtle's state; `turtle_findings` runs every `*.py` that `import turtle`).
- **assets/lN_*.py** — lesson scripts (each `import turtle`, draws one thing).
- **assets/exN_*.py** — exercise STARTER scripts (the task + a scaffold; NO finished solution).
- **assets/solutions_*.py** — the solution scripts (finished turtle code).
- **lesson.ipynb** — markdown teaching + the turtle code shown in **`no-exec`-tagged** code cells (turtle
  opens its own window; `exec-lessons` skips `no-exec`). Problem-first opening (draw a polygon gallery).
- **exercises.ipynb** — mini-CP-style statements (background + Specification + a description of the exact
  shape to draw + which `assets/exN_*.py` to complete and run in the terminal). Solution-free, NO executed
  outputs, NO "Solution" headings, `## Exercise N` headings, ≥8 exercises, core ≤7, ≥2 `stretch` Challenge.
- **solutions.ipynb** — mirrors every `## Exercise N`; each shows the finished turtle code in a `no-exec`
  cell and points to `assets/solutions_*.py`. **Turtle exercises are EXEMPT from output asserts** (design §7)
  — correctness is verified by `turtle-check` running the scripts, not by `assert`.
- **teacher-notes.md** — Goals/Pacing (+60-MIN CUT)/Common mistakes/Discussion prompts/Differentiation.
- **manifest.yaml** — matches the coverage-map entry (a turtle unit MUST ship `assets/`, `notebooks.py:356`).

## Teaching notes ("angles as math")

- **Lesson 1 — Move & Draw (import-statement, turtle-basics).** `import turtle`, `forward`/`left`/`right`,
  pen up/down; a square by hand, then a square with a `for` loop (`for _ in range(4): forward(100); left(90)`).
- **Lesson 2 — Any Polygon (turtle-drawing).** The exterior-angle insight: a regular n-gon turns
  `360 / n` each corner (`for _ in range(n): forward(side); left(360 // n)`); pen color/fill. **Use integer
  `//` for the angle so the value is exact** (e.g. n dividing 360: 3/4/5/6/8/9/10/12) — a Notice states this
  and the exercises pick such n; avoid non-divisors that need floats.
- **Lesson 3 — Patterns with Nested Loops (nested-loops).** A ring of polygons / a spiral
  (`for … : draw a shape; left(angle)`), a growing spiral (side increases each pass). Gallery Final build.

60-MINUTE CUT: L1 square + polygon loop live; leave the spirals as "try it".

## Authoring guardrails

- Pre-function (no `def` — U07). No lists/dicts/builtins beyond taught. Loops use `for`/`range` (U05).
- Turtle methods only from the taught set (the scanner's `TAUGHT_METHODS` turtle subset: forward/backward/
  left/right/penup/pendown/color/pencolor/fillcolor/begin_fill/end_fill/goto/setheading/circle/dot/stamp/
  speed/done/hideturtle/shape/bgcolor/width/pensize/setup/title/exitonclick/up/down). No untaught turtle method.
- Angles via integer `//` on divisors of 360 (exact); no float angles / no `:.2f`.
- Every `.py` that draws ends cleanly for headless `turtle-check` (no blocking `exitonclick()` that hangs —
  follow Book 1 u03's asset convention exactly; check whether its scripts call `done()`/`exitonclick()` and
  mirror that so `turtle-check` passes).
- Values distinct across lesson/exercises (the plan-072 lesson: pick different n / sizes / colors per item).
- lesson turtle cells `no-exec`; exercises solution-free; unique cell ids; problem-first openings; ≥2 stretch.

## Phases

### Phase A — plan-review gate (4-way). No implementation until consensus.
### Phase B — contracts: coverage-map entry + syllabus row + manifest; `--book book1b coverage-check` + `prereq-check` GREEN.
### Phase C — statements + assets (Codex): lesson.ipynb (no-exec turtle cells) + exercises.ipynb + assets/lN_*.py + assets/exN_*.py starters.
### Phase D — solutions (SEPARATE fresh Codex): solutions.ipynb (no-exec) + assets/solutions_*.py; verify `turtle-check` passes on all scripts.
### Phase E — teacher-notes (inline) + verification: full `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN
across the three books (esp. `turtle-check`, `structure-check`, `exec-lessons` skipping no-exec turtle cells,
`stretch-check`, `manifest-check` asset presence, PDF build). Scope allowlist = this plan + the U06 tree +
coverage-map + syllabus.

## Out of scope
- U07–U13, checkpoints, Algorithm Challenge — plans 074+. No tooling/governance/Book-1/Book-2 changes.
- **Verification phase:** Phase E is the named verification phase (unit → required).

## Plan Review

### Round 1 (2026-09-23) — [self] inline; [sol]/[glm]/[fable] dispatched.
#### [self] — **APPROVE.** Closure holds (requires ⊆ U01–U05; import-statement introduced here per design §3).
Turtle format cloned from Book 1 u03 (assets/*.py + no-exec lesson cells + turtle-check; exempt from asserts
per §7). Metadata honest; §6 record present. Phase E named. Risk noted: the `.py` assets must end cleanly for
headless turtle-check (mirror Book 1 u03's convention) — flagged in guardrails. No open blockers.

_(Awaiting [sol] / [glm] (volcengine-plan/glm-5.3) / [fable].)_

## Content Review

_(4-way content-review gate — filled before PR.)_

## Post-Execution Report

_(Filled before shipping.)_
