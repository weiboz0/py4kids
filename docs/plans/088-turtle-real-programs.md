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

For each exercise, the real program:
1. reads, with bare `input()` (one value per line, in the order the exercise's Real version line
   states), exactly the settings that the solution asset hard-codes as literals — e.g. Courtyard Square
   reads the side length, then the pen colour; Nine-Hexagon Wheel reads the number of sides, the side
   length, then the number of shapes; U08 programs read their counts (the seed stays `random.seed(4)`);
2. converts numbers with `int(...)` (or `float(...)` where the solution uses a decimal) and uses text
   input as-is for colours;
3. otherwise draws exactly as the solution asset does, ending with `turtle.done()`;
4. prints exactly what the solution asset prints (e.g. `Dashes: 12`, `Squares: 9`), if anything.

**Parity (checked in CI):** run with its **Sample input** — the exercise's own values — the real program
must record the **identical segment list** (coordinates, colours, pen widths) and the identical stdout as
the solution asset `solutions_exN*.py`, under the headless `fake_turtle`.

Only concepts taught by that unit are used (U06: `input`, `int`, `float` are U01–U02 concepts, already
taught; U07/U08 programs call the student's function / seeded randomness as their assets do).

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
    number you type and watch the loop draw more or fewer sides"). Each cell carries its sample input in
    cell metadata (`"sample_input": "…"`) so the book can print the drawing it makes.
  - run instructions: explain once, in "First terminal encounter", how to run a program file — Windows
    `py assets/l1_square.py`, Mac `python3 assets/l1_square.py`, from the **course folder**'s Unit 6
    folder (JupyterLab's File ▸ New ▸ Terminal opens there) — and change every later
    "Run `python assets/X.py`." to "Run `assets/X.py` the same way."; replace "repository root" with
    "course folder"; move "Budget about 15 minutes…" to the Unit 6 teacher notes.
- **Unit 6 teacher notes** (inline): the timing note, the real-program idea for turtle (vary the typed
  numbers and compare the drawings), and the Real-version count.

## Phase C — Solutions (Codex gpt-6-sol, a separate fresh session)

For each of the 21 exercises, add to its solutions notebook, after the existing solution asset listing and
headless check: `**The real program** (reads …):` + a ```python fence (bare `input()`), `Sample input:`
(the exercise's own values, one per line) and, when the program prints, `Expected output:`. Existing
solution assets and checks stay unchanged.

## Phase D — Tooling (Codex gpt-6-sol)

- `tools/fake_turtle.py` (or a new `tools/turtle_real.py`) + CLI check `turtle-real-check --book B`: for every
  turtle real-program fence (a fence importing `turtle` under a "The real program" heading), run it
  headlessly with its Sample input on stdin (fake turtle, fresh tracker) and the matching solution asset
  headlessly; FAIL on any difference in segments or stdout, on no pen-down segment, or on a fence whose
  Sample input is missing. Wire it into `scripts/ci-local.sh` beside `turtle-check`.
- The Phase-E contract audit (plan 080's fence-parity audit and `publish-audit`'s contract count): turtle
  fences are compared by the new check instead of plain stdout-only execution.
- `tools/publish.py`: (a) Teacher's Edition answer keys render a turtle real-program fence with its sample
  input and the **drawing** it makes (replayed with the sample input); (b) a lesson `no-exec` turtle cell
  that reads `input()` routes to "Try it yourself" and, when it has `sample_input` metadata, is followed by
  its drawing captioned "Drawing for the sample input …"; (c) the Student Book's Real-program notes for
  these exercises render like every other Real version note.
- Tests: parity pass and fail cases (a changed colour or side length is caught), missing sample input,
  stdout mismatch, figure replay with sample input, the lesson try-it figure.

## Phase E — VERIFICATION

1. `turtle-real-check` PASS for all 21 fences; `turtle-check`, `lesson-outputs-check`, structure /
   hygiene / noexec / concept-scan / cell-lint PASS.
2. Contract audit: no exercise in U06/U07/U08 keeps a turtle "No real version" line; repairs and traces
   keep theirs.
3. Books rebuilt; `publish-audit` PASS; rendered-page review of a U06 exercise, a U06 lesson try-it with
   its drawing, and a Teacher answer key with a real-program drawing.
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

## Content Review
_(filled before PR.)_

## Post-Execution Report
_(filled before merge.)_
