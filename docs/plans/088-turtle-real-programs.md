# Plan 088 — Book 1b: real programs for turtle exercises

**Goal:** Give every Book 1b turtle drawing exercise a **real program** — the same drawing, with its
settings (number of sides, side length, colour, count…) read from the keyboard with `input()` — so
students see a loop's count turn into a picture they choose. Remove the "no real program … draws with
turtle" notes, add turtle "Try it yourself" input programs to the Unit 6 lessons, and align Unit 6's run
instructions with Unit 0.

**Spec:** user direction (2026-09-27): "the turtle exercises has no real program, that's not expected,
turtle is a good way visualize the learning of loops". This reverses design 006 D3's turtle exemption
("Turtle work (U06) is exempt (no stdin in turtle scripts)"); design 006 D3 is amended in this plan.
Reader-review findings (2026-09-27, [sol]/[fable]) on Unit 6's notebook/repository wording are folded in
for the Unit 6 lesson only.

## Scope — the 21 turtle drawing exercises

- **Unit 6 (15):** Ex 1–12, 16, 17, 18 (Courtyard Square … Grid of Squares). Ex 13–15 are repairs of
  broken code and keep **No real version**.
- **Unit 7 (3):** Ex 7 Turtle Polygon Tool, Ex 27 Star Function, Ex 28 Polygon Row.
- **Unit 8 (3):** Ex 7 Rescue-Robot Random Walk, Ex 16 Random Polygon, Ex 17 Random Color Row.

Non-turtle repair and trace exercises keep their No-real lines (they fix or trace given code).

## The real-program rule (binding)

Each real program reads **exactly the inputs in the table below, in that order**, with bare `input()`
(one value per line; numbers via `int(...)`, colours as typed text), each `input()` line carrying a
short trailing comment naming the value (`side = int(input())  # side length`) so a reader knows what to
type. Everything not listed stays code:
shape rules (e.g. a square's four sides, the Ring's red/blue/green palette), seeds (`random.seed(4)`),
and the derived values shown. With the **Sample input** (the exercise's own values) it must reproduce the
solution asset exactly (see Parity). It ends with `turtle.done()` and prints what the asset prints.

| Unit / Ex | Exercise | Inputs, in order (sample) | Derived or fixed in code |
|---|---|---|---|
| U06 1 | Courtyard Square | side (62), colour (royalblue) | 4 sides; angle `360 / 4` |
| U06 2 | Trail-Sign Triangle | side (74), colour (forestgreen) | 3 sides |
| U06 3 | Festival Pentagon | side (68), colour (orchid), pen width (4) | 5 sides |
| U06 4 | Decimal-Turn Heptagon | sides (7), side (57), colour (darkorange) | angle `360 / sides`, printed |
| U06 5 | Move, Then Mark | travel (39), sides (8), side (44), colour (crimson) | pen-up travel first |
| U06 6 | Nine-Hexagon Wheel | sides (6), side (41), shapes (9), colour (turquoise) | turn between shapes `360 / shapes` |
| U06 7 | Growing Radar Spiral | start side (11), step (6), moves (14), colour (maroon) | 92° turn; final side printed |
| U06 8 | Row of Squares | squares (4), side (40), travel (60) | return `backward(squares * travel)` |
| U06 9 | Dashed Line | segments (24), step (10) | dash on even `i`; `Dashes: N` printed |
| U06 10 | Color-Alternating Ring | squares (8), side (40) | palette by `i % 3`; turn `360 / squares` (true division, as Unit 6 teaches); `turned` adds each turn and prints `Turned: {int(turned)}` (8 × 45.0 = 360.0 → `Turned: 360`, matching the asset); teacher notes: counts that divide 360 give an exact total |
| U06 11 | Growing Squares | squares (5), start side (20), growth (20) | `Squares: N` printed |
| U06 12 | Seven-Point Star | points (7), side (90) | turn `3 * 360 / points` |
| U06 16 | Five-Point Star | points (5), side (96), colour (goldenrod), pen width (3) | turn `720 / points` |
| U06 17 | The Eight-Degree Gap | sides (11), side (34), colour (magenta) | angle `360 / sides` |
| U06 18 | Grid of Squares | rows (3), columns (3), side (30), travel (45) | return path as the asset; `Squares: N` printed |
| U07 7 | Turtle Polygon Tool | sides (6), side (48), colour (teal) | calls `draw_polygon(sides, side)` |
| U07 27 | Star Function | size (80) | calls `draw_star(size)`; 144° turns |
| U07 28 | Polygon Row | sides (6), length (30), count (3), travel (70) | `polygon_row(count, sides, length, travel)`; return `backward(count * travel)` |
| U08 7 | Rescue-Robot Random Walk | step (31), moves (20), colour (seagreen) | `random.seed(4)`; pen width 3; left/right from `randint(0, 1)` |
| U08 16 | Random Polygon | length (70) | `random.seed(4)`; sides from `randint(3, 8)` (kept for uniformity — the loop count stays random, only the length is chosen) |
| U08 17 | Random Color Row | side (30), squares (4) | `random.seed(4)`; colour from `choice("rgb")`; return `backward(squares * side)` |

**Parity (checked in CI):** under `fake_turtle` with a fresh tracker, the real program run with its Sample
input and the solution asset must produce (a) the same ordered list of pen-down segments (endpoints,
colour, pen width), (b) the same final position and heading, (c) the same pen state at the end, and (d)
identical stdout. Coordinates and headings compare with a tolerance of 1e-6; everything else exactly.
(Final position/heading catch a missing pen-up return, which draws no segment.)

Only concepts taught by that unit are used (`input`, `int` are U01–U02 concepts; U07 programs define and
call functions; U08 programs use the unit's seeded randomness).

## Phase A — Design amendment (inline)

`docs/designs/006-book1b-enrichment.md` D3: replace "Turtle work (U06) is exempt (no stdin in turtle
scripts)" with the rule above (turtle real programs read the drawing's settings; parity with the solution
asset is checked headlessly), citing the user decision of 2026-09-27.

## Phase B — Statements and lessons (Codex gpt-6-sol)

- **Exercises (U06/U07/U08):** replace each of the 21 `**No real version:** … turtle …` lines with
  `**Real version:** the real program reads <settings, in order> with input(), then draws the same
  picture — see the solution.` Nothing else in the statements changes.
- **Unit 6 lesson:**
  - add one `no-exec` "Try it yourself" turtle input program per lesson — Lesson 1: read a side length and
    draw a square; Lesson 2: read the number of sides and the side length and draw that polygon;
    Lesson 3: read the number of shapes and draw a ring — each with a lead-in and a Notice ("change the
    number you type and watch the loop draw more or fewer sides"). These lesson programs **use prompt
    text** in `input("Side length: ")` (a child at a terminal otherwise sees a blank cursor before the
    window opens; design 006 D3 already allows prompts in lesson cells). Each cell carries its sample input
    in cell metadata (`"sample_input": "…"`) so the book can print the drawing it makes, and each is also
    saved as a runnable asset — `assets/l1_square_input.py`, `assets/l2_polygon_input.py`,
    `assets/l3_ring_input.py` — whose first line is a `# sample-input: …` comment — the values separated by
    ` | ` (space, bar, space), e.g. `# sample-input: 6 | 50`; every reader of the header (`turtle-check`,
    `figure_tikz`, the publisher) splits on ` | ` and feeds one value per line, so the lesson's "run it the same way" works and `turtle-check` can feed it.
  - run instructions: explain once, in "First terminal encounter", how to run a program file: open a
    terminal (JupyterLab's File ▸ New ▸ Terminal opens in the **course folder**, as Unit 0 says), move into
    Unit 6's folder with `cd book1b/units/unit-06-turtle-geometry`, then run Windows
    `py assets/l1_square.py` / Mac `python3 assets/l1_square.py` — and change every later
    "Run `python assets/X.py`." to "Run `assets/X.py` the same way."; replace "repository root" with
    "course folder"; move "Budget about 15 minutes…" to the Unit 6 teacher notes. Also rewrite: the unit
    opener's "Your teacher will run `python assets/l3_gallery.py`" (→ "Your teacher will run the gallery
    program `assets/l3_gallery.py`"); "Turtle drawings run as Python files, not inside this notebook" (→
    "…not inside the lesson notebook"); the "errors are directions" Notice's "from the repository root,
    then rerun `python assets/l1_square.py`" and its error text `python: can't open file` (→ the `py` /
    `python3` forms and "course folder").
- **Unit 6 teacher notes** (inline): the timing note, the real-program idea for turtle (vary the typed
  numbers and compare the drawings), and the Real-version count.

## Phase C — Solutions (Codex gpt-6-sol, a separate fresh session)

For each of the 21 exercises, add to its solutions notebook, after the existing solution asset listing and
headless check: `**The real program** (reads …):` + a ```python fence (bare `input()`), `Sample input:`
(the exercise's own values, one per line) and, when the program prints, `Expected output:`. Existing
solution assets and checks stay unchanged.

## Phase D — Tooling (Codex gpt-6-sol)

- **`turtle-check` and input assets:** `tools/fake_turtle.turtle_findings` reads a leading
  `# sample-input: …` comment and supplies those lines on stdin when it runs an asset (assets without the
  comment still run with empty stdin, as now); a turtle asset that calls `input()` without that comment
  FAILs with a clear message.
- **`turtle-real-check --book B`** (registered in the `tools/checks.py` check registry next to
  `turtle-check`, so `tools/cli.py` offers it automatically;
  implemented beside `tools/fake_turtle.py`): builds the expected inventory from the notebooks — every
  exercise in a unit whose solutions notebook lists a turtle solution asset (`assets/solutions_ex*.py`
  importing `turtle`) and whose statement carries a Real version line — and requires **exactly one**
  turtle real-program fence (under "The real program") per such exercise, associated by its
  `## Exercise N` heading to that asset; Book 1b must yield exactly the 21 rows of the table. For each,
  it runs the fence (Sample input on stdin) and the asset under a fresh `fake_turtle` and compares per the
  Parity rule. FAILs: missing/extra fence, missing Sample input, segment / final-state / pen-state / stdout
  mismatch, no pen-down segment, and **unconsumed input** (the fence reads fewer lines than its Sample
  input provides). `fake_turtle` gains a `final_state()` (x, y, heading, pen down) if it
  lacks one. Wired into `scripts/ci-local.sh` beside `turtle-check`.
- **Contract audit:** turtle fences are verified by `turtle-real-check`, not by stdout-only execution
  (the fence-parity step skips fences that import `turtle`).
- **`tools/turtle_figure.py`:** `figure_tikz(source, stdin: str | None = None)` feeds `stdin` to `input()`
  during replay; when `stdin` is None and the source starts with a `# sample-input: …` header, that header
  supplies it (so **referenced lesson assets** such as `assets/l1_square_input.py`, listed by the
  publisher's asset path in `asset_blocks`, replay with their sample input too); a source that calls
  `input()` with neither fails the build clearly. Tested on both the cell path and the referenced-asset
  path.
- **`tools/publish.py`:** lesson `no-exec` routing adds a rule before the turtle-figure rule: a turtle cell
  that calls `input(` routes to `tryit`, followed by `figure_tikz(source, stdin=metadata["sample_input"])`
  captioned "Drawing for the sample input: …" when the metadata exists (inventory kind `tryit+figure`);
  Teacher's Edition answer keys render each turtle real-program fence, its Sample input, and the drawing
  replayed with that input; Student Book Real-program notes render like all others.
- **`tools/publish_audit.py`:** in lockstep with the publisher's routing — `_expected_lesson_kind` and the
  plan-080 candidate filter learn the turtle+`input(` → `tryit+figure` route — and the audit checks the
  three U06 try-it figures and the 21 answer-key drawings are present.
- Tests: parity pass; failures for a changed colour, a changed side length, a missing pen-up return (final
  position), a missing fence, a missing Sample input; `figure_tikz` with stdin; the lesson try-it route and
  figure; the answer-key drawing; the 21-row inventory on Book 1b.

## Phase E — VERIFICATION

1. `turtle-real-check` PASS with exactly 21 inventory rows (segments, final state, pen state, stdout, no
   unconsumed input); `turtle-check` PASS including the three new input assets; `turtle-check`, `lesson-outputs-check`, structure /
   hygiene / noexec / concept-scan / cell-lint PASS.
2. Contract audit: no **drawing** exercise in U06/U07/U08 keeps a turtle "No real version" line; repairs and traces
   keep theirs. A grep finds no `python assets/` and no "repository root" left in the U06 lesson.
3. Books rebuilt; `publish-audit` PASS including the new `tryit+figure` route and the 21 answer-key
   drawings; rendered-page review of a U06 exercise, each U06 lesson try-it with its drawing, and Teacher
   answer keys with real-program drawings (U06, U07, U08).
4. `scripts/ci-local.sh` ALL GREEN; post-execution report.

## Out of scope

Other reader-review findings (front/back matter, Real-program boilerplate elsewhere, glossary/index,
lesson naming, jargon) — a separate publication-polish plan. Book 1 and Book 2 turtle work.

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- Surveyed the 21 turtle exercises (U06 15, U07 3, U08 3) and their assets: every solution asset
  hard-codes its settings as literals, so "read the literals, sample input = the exercise's own values"
  gives an exact, checkable parity target (identical segments and stdout under `fake_turtle`).
- Watch items for reviewers: exercises whose assets use several colours or computed sequences (Ring,
  Growing Squares, Grid, Random Color Row) need an explicit reading order; U08 keeps `random.seed(4)` so
  parity stays deterministic; the lesson "run it the same way" rewrite must keep every existing asset run.
- `[glm]` skipped for this gate by user decision (2026-09-26: "skip glm reviewer for 1 day").

### Round 1 — verdicts

- `[sol]` **REJECT** — the "read the literals" rule is ambiguous (needs an ordered per-exercise input table
  with fixed and derived values); parity must catch invisible travel (final position/heading, tolerance);
  the JupyterLab terminal opens in the course folder, not Unit 6's folder; the publisher route, sample-stdin
  replay, audit routes and CLI registry must be explicit; the check must require exactly 21 associated
  fences; the `[glm]` skip must be resolved.
- `[fable]` APPROVE WITH NITS — parity confirmed empirically (scratch real programs for the Ring and the
  Grid reproduce the assets' segments and stdout; a changed side is caught); required: the input table
  (N1), runnable assets + `turtle-check` stdin for the lesson try-its (N2), publisher/audit routing in
  lockstep (N3), four more U06 wording spots (N4); suggestions: prompts in lesson try-its, comments on
  fence `input()` lines, unconsumed-input failure, a wording grep.
- `[glm]` skipped — a user-authorised one-day exception (2026-09-26: "skip glm reviewer for 1 day, then
  use volcengine-plan/glm-5.3"); recorded here as the resolution of the gate-composition point.

### Round 1 — fold

- `[FIXED]` a 21-row input table (order, samples, fixed and derived values incl. the Row/Polygon Row/Random
  Color Row return distances and the Ring's whole-number turn); parity now compares segments, final
  position and heading, final pen state and stdout with a 1e-6 tolerance for coordinates; the U06 run
  instructions include the `cd` from the course folder; Phase D specifies the check's inventory (exactly
  21 associated fences), CLI registration, contract-audit skip, `figure_tikz(stdin=…)`, the `tryit+figure`
  route, answer-key drawings and audit changes, with tests.

### Round 1 — [fable] fold

- `[FIXED]` N1 (the table, above); N2 three runnable input assets with `# sample-input:` headers and
  `turtle-check` feeding them; N3 audit routing in lockstep; N4 the four extra U06 wording spots; lesson
  try-its use prompts; fence `input()` lines carry a comment; unconsumed input fails; Phase E greps the
  U06 lesson and runs `turtle-check` on the new assets; the Random Polygon note.

### Round 2 — [sol] REJECT (folded)

- `[FIXED]` referenced lesson input assets replay with their `# sample-input:` header (`figure_tikz`
  falls back to it; both publisher paths tested); Ex 10 uses true division for the turn and prints
  `Turned: {int(turned)}` (identical `Turned: 360` for the sample); the check is registered in
  `tools/checks.py`.

### Round 3 — CONSENSUS

- `[sol]` APPROVE WITH NITS (r3) — inventory and the input table confirmed against every asset; nits folded
  (the `# sample-input:` header uses ` | ` separators, read the same way everywhere; Phase E says
  "drawing exercise").
- `[fable]` APPROVE WITH NITS (r1, folded) · `[self]` APPROVE WITH NITS · `[glm]` skipped (user-authorised
  one-day exception, 2026-09-26/27).

**Consensus reached — implementation starts.**

## Content Review

### Round 1

- `[self]` APPROVE WITH NITS — rendered pages checked (U06 try-its with drawings; Teacher answer keys U06/U07/U08).
  - `[FIXED]` S1 each sample-input drawing carried two captions (the frame's "Drawing made by the program
    above" plus "Drawing for the sample input: …" below); the sample caption now replaces the frame caption
    (`figure_tikz(caption=…)`), audit and test updated.
  - `[FIXED]` S2 runs of blank lines where literals were removed in the real-program fences (same as F4).
- `[fable]` APPROVE WITH NITS — blind solve 6/6 exact parity (U06 3, 7, 11, 12; U07 7; U08 7); 17 mutation
  cases all caught.
  - `[FIXED]` F1 each U06 try-it printed twice (the lead-in named the asset before the cell, so the publisher
    listed the asset in full); the run line moved into the Notice after the cell.
  - `[FIXED]` F2 lowercase lead-in sentences capitalised.
  - `[FIXED]` F3 the first try-it lead-in explains the `# sample-input:` comment line.
  - `[FIXED]` F4 blank-line runs in turtle real-program fences collapsed (comments sit on their code again);
    non-turtle fences untouched.
  - `[FIXED]` F5 U08 Ex 16 statement says "edge length", matching the fence.
  - `[WONTFIX]` F6 the error Notice's `py: can't open file` wording is hedged by "text like" (reviewer: no
    action needed). Optional audit rule for input-asset listings not added: F1's cause is removed and the
    rendered pages are re-checked in round 2.
- `[sol]` REJECT — blind solve 5 programs; 4 matched.
  - `[FIXED]` O1 U08 Ex 17 did not say which way the square turns (a left-turn program drew a mirror image);
    the statement now says `turtle.forward(30)` and `turtle.right(90)`.
  - `[FIXED]` O2 parity used `math.isclose` with its default relative tolerance; now `rel_tol=0,
    abs_tol=1e-6`, with a test at coordinate 1,000,000.
- `[glm]` skipped — user-authorised one-day exception (2026-09-26: "skip glm reviewer for 1 day").

## Post-Execution Report
_(filled before merge.)_
