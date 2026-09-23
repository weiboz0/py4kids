# Plan 073 — Book 1b Unit 06 (Turtle Geometry)

**Origin:** Book 1b buildout ("full book 1b implementation").
**Design:** `docs/designs/005-book1b-concept-first.md` §3 (U06 row), §7 (turtle exercises verified by
execution + `turtle-check`; the assert-exemption is the per-exercise authoring rule, NOT the CI minimum),
§8 (turtle runs as `.py` scripts).
**Templates:** Book 1b U01–U05 (prose/teacher-notes); **Book 1 `unit-03-turtle-art-studio` for the turtle
FILE STRUCTURE** (assets/*.py + no-exec lesson cells + headless-companion solutions + turtle-check).

## Scope

One unit — **U06 Turtle Geometry** — in the turtle format, done ALONE (distinct format; first terminal
encounter). Next checkpoint is after U08, so none here. Book 1b stays `buildout: true`.

## Coverage-map entry (the contract) — 7-key shape

**unit-06-turtle-geometry** — `kind: unit`, `title: "Turtle Geometry — drawing with loops and angles"`, `lessons: 3`
- introduces: `[import-statement, turtle-basics, turtle-drawing]`
- requires: `[for-loop, range-function, arithmetic, variable]`
- practices: `[nested-loops, loop-counter, accumulator, int-type, comment, naming, run-program]`

Closure: requires ⊆ U01–U05 (for-loop/range U05, arithmetic U02, variable U01); `import-statement`
introduced here (design §3/§5). No self-practice. 30→33 introduced-once.

### Design §6 practice-coverage record (reworded per [glm]/[sol])
A unit cannot practice its OWN introductions, so U06's three intros (`import-statement`/`turtle-basics`/
`turtle-drawing`) get their later practice sites in **U07** (`draw_polygon`) and **U08** (turtle random
walk) per design §3 — deferred, not claimed here. U06 ADDS practice sites for earlier intros:
`nested-loops` (rings/spirals), `loop-counter` (side/shape counters), `accumulator` (growing spiral
`side = side + step`), `int-type` (`360 // n`), `comment`/`naming` (the asset-script convention),
`run-program` (the terminal run — this unit's core activity). All 30 pre-U06 introductions remain
practiced (plan-072 record). Capstone anchor dormant (buildout).

## File structure (clone Book 1 `unit-03-turtle-art-studio` EXACTLY)

Turtle CODE lives ONLY in `assets/*.py` (run headless by `turtle-check` via the `fake_turtle` stub) and in
`lesson.ipynb` **`no-exec`-tagged** cells. **No `import turtle` anywhere in `exercises.ipynb` or
`solutions.ipynb` code cells** — `_solution_policy_findings` flags it "solutions import a GUI" regardless of
`no-exec` (notebooks.py:287), and requires **≥3 non-vacuous assert cells** notebook-wide (notebooks.py:281-283).

- **assets/lN_*.py** — lesson turtle scripts (`import turtle`, draw one thing, one terminal `turtle.done()`).
- **assets/exN_*.py** — exercise STARTER scripts: a VALID CLOSED placeholder that already draws (≥1 pen-down
  move, e.g. a small square) with the task in comments (NOT an empty TODO — every asset runs under
  turtle-check and must make ≥1 pen-down move and close its path).
- **assets/solutions_*.py** — finished turtle programs.
- **lesson.ipynb** — markdown teaching; turtle demos shown in **`no-exec`** code cells; optional NON-turtle
  headless cells (the "angles as math" computation) may run. Problem-first opening (see below).
- **exercises.ipynb** — mini-CP statements: `## Exercise N` / `### Title` / background / **Specification** /
  a **checkable "expected output"** for a drawing = the shape named PLUS a checkable number (n, side, the
  turn angle `360 // n`, total turn, pen-down-move count, "ends where it started: yes/no") / which
  `assets/exN_*.py` to complete and run in the terminal. Solution-free, NO executed outputs, NO "Solution"
  headings, ≥8 exercises, core ≤7, ≥2 `stretch` Challenge. Code cells (if any) are HEADLESS (no `import turtle`).
- **solutions.ipynb** — mirrors every `## Exercise N`. Per exercise: a **markdown fenced block** "The real
  program (`assets/solutions_*.py`)" showing the turtle code, AND a **headless companion code cell** that
  computes the math (`angle = 360 // n`, `total_turn = n * angle`, side/shape counts, ends-at-start bool)
  with **asserts** (≥3 non-vacuous assert cells notebook-wide; NO `import turtle`). This is where "angles as
  math" is written down and blind-solved by the gate roster; turtle-drawing correctness is verified by
  `turtle-check` on the `.py`.
- **teacher-notes.md** — Goals / Pacing (per-lesson 60-MIN CUTs) / Common mistakes / Discussion prompts /
  Differentiation. (Asset presence is enforced by `structure-check`/`layout_findings` (notebooks.py:348-356),
  not `manifest-check`.)
- **manifest.yaml** — matches the coverage-map entry.

## Turtle API — PIN to the `fake_turtle` stub subset (turtle-check executes every asset)

Use ONLY: `forward`, `backward`, `left`, `right`, `penup`, `pendown`, `pencolor`, `color`, `pensize`,
`speed`, `bgcolor`, and one terminal `done()`. **Do NOT use** `begin_fill`/`end_fill`/`fillcolor`, `circle`,
`goto`, `setheading`, `dot`, `stamp`, `hideturtle`, `shape`, `setup`, `title`, `width`, `up`, `down`,
`exitonclick` — the stub lacks them → `AttributeError` → turtle-check FAIL. So **`turtle-drawing` = pen
color (`pencolor`/`color`) + `pensize` + shapes drawn with `forward`/turn — NO fill, NO circle.** Use `left`
consistently (a Notice states `left(90)` mirrors `right(90)`). Loop variable is a real name (`corner`,
`side_number`, `shape`) — NOT `_` (never taught).

## Path-closure contract (fake_turtle.py:207-220)

Every `assets/*.py` must EITHER close its path (end at the draw-start position AND total heading change ≡ 0
mod 360) OR carry the exact comment `# turtle-check: open-path`. Also: ≥1 pen-down move; < 10,000 moves.
- Polygons: `n × (360 // n)` — use n | 360 so it's exactly 360 (closes). Rings: `shapes × between_turn == 360`.
  Stars: 5-point uses `720 // 5 == 144`, and `5 × 144 == 720 ≡ 0 (mod 360)` — closes.
- The **growing spiral** (L3) and any open corner do NOT close → carry `# turtle-check: open-path`
  (Book 1 `assets/l1_corner.py` precedent). exN STARTERS draw a closed placeholder (so they pass too).

## Teaching ("angles as math")

- **Lesson 1 — Move & Draw (import-statement, turtle-basics).** Problem-first opener: "the turtle only knows
  forward and turn — what turn makes a triangle? a pentagon? Predict, then run." `import turtle`,
  `forward`/`left`/`right`, `penup`/`pendown`; a square by hand, then with a `for` loop. **FIRST TERMINAL
  ENCOUNTER (~15 min, budget it like Book 1 u03):** File → New → Terminal, `cd` to the unit dir,
  `python assets/l1_square.py`, edit-save-rerun; expect to repeat twice.
- **Lesson 2 — Any Polygon (turtle-drawing).** The exterior-angle insight: a regular n-gon turns `360 // n`
  each corner (`for corner in range(n): forward(side); left(360 // n)`), + `pencolor`/`pensize` (NO fill).
  **The `//` moment (own it):** `//` is exact only when n divides 360; a Notice shows `360 // 7 = 51`,
  `7 × 51 = 357 ≠ 360` → the 7-gon would NOT close (that's when you'd use `/`, taught U02) — a Challenge
  "predict what `n = 7` with `//` draws, then fix it" turns the trap into the unit's best math moment.
  Stars need `720 // n` (5 → 144, "two full turns").
- **Lesson 3 — Patterns with Nested Loops (nested-loops).** A ring of polygons (`for shape … : draw; left`),
  then a growing spiral (`side = side + step` — `accumulator`; open-path marker). Gallery Final build.

Per-lesson 60-MIN CUT: L1 square + polygon loop live (leave the terminal-rerun as "try it"); L2 the polygon
loop is non-negotiable core (drop color/pensize flourishes); L3 ring live, growing spiral as "try it".

## Beginner traps (teacher-notes Common mistakes + lesson Notices)

Running from the wrong directory (`can't open file` — an `error-messages` callback); the turtle window opens
BEHIND JupyterLab; closing the window ends the script (re-run, don't rescue); forgetting the turn → a
straight line; forgetting `forward` → a spinning turtle; **exterior vs interior angle** (a triangle turns
120, not 60 — let the wrong prediction happen, then fix it); `left` vs `right` mirror; `penup` without
`pendown` (nothing draws); missing `turtle.done()` (window flashes and vanishes); `range(n)` gives 0..n-1.

## Value plan (per plan-072 lesson)

Each lesson rung / exercise / Challenge uses a DISTINCT `(n, side, color)` and its own checkable number
(distinct from the lesson rungs and from each other). List them in teacher-notes so the gate can check.

## Phases

### Phase A — plan-review gate (4-way). No implementation until consensus.
### Phase B — contracts: coverage-map entry (7-key: kind/title/lessons + introduces/requires/practices) + syllabus row + manifest; `--book book1b coverage-check` + `prereq-check` GREEN.
### Phase C — statements + assets (Codex): lesson.ipynb (no-exec turtle demos) + exercises.ipynb + assets/lN_*.py + assets/exN_*.py starters (closed placeholders). Pin the API subset + closure rule.
### Phase D — solutions (SEPARATE fresh Codex): solutions.ipynb (markdown "real program" blocks + headless-companion asserts, NO `import turtle`, ≥3 assert cells) + assets/solutions_*.py; verify `turtle-check` passes on all scripts.
### Phase E — teacher-notes (inline) + verification: full `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN
across the three books (esp. `turtle-check`, `structure-check` incl. the GUI-import + ≥3-assert rules,
`exec-lessons` skipping no-exec turtle cells, `stretch-check`, layout/asset presence, PDF). **AST/static audit:**
every `assets/*.py` uses only the pinned method subset, ends with exactly one terminal `turtle.done()` (no
`exitonclick()`), and either closes its path or carries `# turtle-check: open-path`. Scope allowlist = this
plan + the U06 tree + coverage-map + syllabus.

## Out of scope
- U07–U13, checkpoints, Algorithm Challenge — plans 074+. No tooling/stub extension, no governance/Book-1/2 changes.
- **Verification phase:** Phase E is the named verification phase (unit → required).

## Plan Review

### Round 1 (2026-09-23) — [self] APPROVE (superseded by folds below); [sol] REJECT; [glm] REJECT; [fable] REJECT.
All three REJECTed on the turtle-format spec (not the curriculum contract, which all verified GREEN:
closure, 30→33 introduced-once, honest metadata, named verification). Blockers, ALL FOLDED into the rewrite
above:
- **solutions.ipynb** re-specified to the u03 convention: NO `import turtle` in code cells; turtle program in
  a markdown "real program" block + `assets/solutions_*.py`; solutions code cells are **headless companions
  with ≥3 non-vacuous asserts** (the §7 exemption is the per-exercise rule, not the CI minimum). ([fable]1/[sol]1/[glm]1-2)
- **Turtle API pinned to the fake_turtle stub subset** (no fill/circle/goto/setheading/etc.); turtle-drawing
  = color + pensize + polygons. ([sol]2/[glm]3/[fable])
- **Path-closure contract** added (close, or `# turtle-check: open-path`; ≥1 pen-down; exN starters draw a
  closed placeholder). ([sol]3/[glm]4/[fable]2)
- **Lifecycle** pinned: one terminal `turtle.done()`, no `exitonclick()`; Phase-E AST audit. ([sol]4/[glm]6)
- §6 record reworded (U06 doesn't practice its own intros; deferred to U07/U08). ([glm]5)
- 7-key coverage entry (kind/title) ([glm]7); asset-presence attribution → structure-check/layout ([sol]6/[glm]).
- [fable] P1/P2 folded: FIRST-TERMINAL-ENCOUNTER pacing; beginner-traps list; the `//`-angle "why" + n=7
  Challenge (stars 720//n); per-lesson cuts; "expected output" = shape + checkable number; named loop var;
  value plan; metadata `practices += accumulator, run-program`.

### Round 2 (2026-09-23) — rewritten to the correct turtle format. Re-dispatching [sol]/[glm]/[fable].
_(Awaiting round-2 verdicts.)_

## Content Review

_(4-way content-review gate — filled before PR.)_

## Post-Execution Report

_(Filled before shipping.)_
