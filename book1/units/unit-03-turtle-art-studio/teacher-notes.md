# Teacher Notes — Unit 03: Turtle Art Studio

## Goals

Students leave able to command the turtle (move, turn, pen, color), repeat with `for` and `range`, use the loop variable as a counter, compute angles with `360 / n` (meeting floats where they're needed), and nest loops for compound patterns.
Success looks like: every student runs a polygon script whose shape they PREDICTED before running, and a spirograph of their own design hangs in the class gallery.

## Pacing

Budget: three lessons of 60–90 minutes. Each concept is a short **worked-example ladder** (simplest first, then one step up, with a *Notice* per rung); the lesson-count is advisory. Per D-005, drawing happens in `.py` scripts run from the terminal; the notebook carries the reasoning, predictions, and the ladders (every turtle cell is `no-exec`, and each rung also lives in `assets/` so students run it).

- **Lesson 1 — turtle-basics + turtle-drawing (60–90 min). FIRST TERMINAL ENCOUNTER.**
  Open on the project thread: the teacher runs `assets/l3_spirograph.py` as a teaser — "by Friday you'll write this."
  15 min: FIRST-RUN TERMINAL WALKTHROUGH (most students' first terminal): open a terminal in JupyterLab (File → New → Terminal), `cd` to the unit directory, `python assets/l1_corner.py`.
    Expect to repeat it slowly twice; put the commands on the board. Also show how to OPEN and EDIT a script: double-click the `.py` in the file browser, change a number, save (Ctrl+S), re-run — the exercises assume this.
  25 min: the five-rung pen ladder — `forward`+`right` (open corner) → a full written-out square → `penup`/`pendown` travel → `color` → `pensize`. One pen action per rung; run each asset (`l1_corner`, `l1_plain_square`, `l1_travel`, `l1_color`, `l1_square`).
  25 min: the pain of drawing the square with eight copy-pasted lines — leave it unresolved (loops rescue us next lesson).
  Window tips: the turtle window may open BEHIND JupyterLab (alt-tab); closing the window ends the script; re-run rather than rescue a half-drawn shape.
- **Lesson 2 — for-loop, range-function, loop-counter, float-type (60–90 min).**
  Open on the thread: the eight sad lines become three with `for`.
  One of the year's two densest lessons — hold the allocation strictly and push everything else to exercises.
  15 min: `for side in range(4)` redraws the square (`l2_square_loop`); predict-then-run.
  15 min: change the count — a triangle with `range(3)` and a typed `angle = 120` (`l2_triangle`): the number of sides is now yours to choose.
  20 min: any polygon — `angle = 360 / n` (`l2_polygon`, the 7-gon): the calculator shows 51.42857…; floats arrive because `/` always makes a decimal and the turtle turns by it just the same. `float-type` is co-taught here (it is inseparable from the computed angle).
  15 min: the loop **counter** does work — `pensize(side_number + 1)` thickens each side (`l2_polygons`).
  60-MINUTE CUT: drop the pensize-scaling rung (it returns in the exercises); the polygon-angle discovery is the non-negotiable core.
  In-class exercises: complete Exercise 2's `360 / 7` prediction, Exercise 3's counter-driven repair, and the Exercise 5 flagship seven-sided script.
  Exercise 5 is the proficiency check: students author turtle setup, pen controls, the loop, the counter expression, and the decimal angle rather than editing a finished lesson asset.
- **Lesson 3 — nested-loops (60–90 min).**
  Open on the thread: what if the whole polygon repeats, turned a little each time?
  20 min: the two nested rungs — two squares with a 180° turn between (`l3_two_squares`), then six squares fanned into a ring (`l3_rings`): the inner loop finishes one shape before the outer turns.
  20 min: **put it together** — read `l3_spirograph.py`; the outer loop sweeps, the inner draws, `angle = 360 / n` shapes each polygon.
  20 min: Exercises 4 and 6 move from tracing to authored nested-loop plans and repairs.
  Rest: finish the flagship gallery piece; export by screenshot for the classroom wall.

Exercise allocation: Exercises 1, 2, 3, and 5 are the Lesson-2 in-class path; Exercises 4 and 6 are the Lesson-3 in-class path.
This path includes at least one authored repetition of every unit concept, including the required f-string report in Exercise 1.
Exercises 7–10 are labelled **More Practice** in the notebook and are assigned as homework or independent studio time: Exercises 7, 8, and 10 after Lesson 2, and Exercise 9 after Lesson 3.
They provide the remaining proficiency repetitions without crowding the 60–90 minute in-class path.

Practices reappearance: naming (script variables), comment (script headers students edit), run-program (the terminal itself) — all three throughout every lesson; all reappear in unit 04 and beyond.

## Common mistakes

- Running the script from the wrong directory (`can't open file` — a planned error-messages callback; re-walk the `cd`).
- Degrees vs "how far to turn": exterior angle 360/n, not interior — let a wrong prediction happen, then fix it.
- `range(4)` giving 0,1,2,3 — the off-by-one surprise; use the loop-table exercise.
- Indentation of the loop body (first meaningful indentation of the year — name it explicitly).
- Nested-loop confusion about which loop the turn belongs to — trace one iteration on the board.

## Discussion prompts

- Why does `360 / 7` need to be a decimal? What would the shape look like if we rounded it?
- The loop variable went 0,1,2,3 — who decided that? Would 1,2,3,4 be better?
- Where ELSE in life is a "loop inside a loop"? (Weeks/days, songs/verses.)

## Differentiation

- Strugglers: pair at one screen for terminal work; the predict-the-drawing exercises work on paper with no computer pressure.
  Differentiation is MANDATORY in lesson 2 (dense): strugglers stop after the plain polygon; the `i`-scaled variant is the middle tier.
- Fast finishers: Challenge exercises — star polygons (angle 720/5) and the rainbow rosette.

## Visual checklist (teacher's first classroom run)

Before teaching, run each script once on the classroom machine:
- `l1_square.py`: a closed square, pen visible, window stays open until clicked/closed.
- `l2_polygons.py`: draws ONE polygon per run (ships with `n = 7`); edit `n` to 3, 4, 6 and re-run — each closes cleanly, including the 7-gon's 51.428… angle.
- `l3_spirograph.py`: a symmetric rosette; total runtime under ~30 seconds.
- Solutions scripts (`assets/solutions_*.py`, added with the solutions pass): same standard.
