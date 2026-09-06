# Teacher Notes — Unit 03: Turtle Art Studio

## Goals

Students leave able to command the turtle (move, turn, pen, color), repeat with `for` and `range`, use the loop variable as a counter, compute angles with `360 / n` (meeting floats where they're needed), and nest loops for compound patterns.
Success looks like: every student runs a polygon script whose shape they PREDICTED before running, and a spirograph of their own design hangs in the class gallery.

## Pacing

Budget: three lessons of 60–90 minutes.
Per D-005, drawing happens in `.py` scripts run from the terminal; notebooks carry the reasoning, predictions, and exercises.

- **Lesson 1 — turtle-basics (60–90 min). FIRST TERMINAL ENCOUNTER.**
  Open on the project thread: the teacher runs `assets/l3_spirograph.py` as a teaser — "by Friday you'll write this."
  15 min: FIRST-RUN TERMINAL WALKTHROUGH (this is most students' first terminal): open a terminal in JupyterLab (File → New → Terminal), `cd` to the unit directory, `python assets/l1_square.py`.
    Expect to repeat it slowly twice; put the three commands on the board.
    Also show how to OPEN and EDIT a script: double-click the `.py` file in the JupyterLab file browser, change a number, save (Ctrl+S), re-run in the terminal — the exercises assume students can do this.
  25 min: forward/turn; edit `l1_square.py` to change sizes and directions.
  25 min: the pain of drawing a square with eight copy-pasted lines — leave the pain unresolved (loops rescue us next lesson).
  Window tips: the turtle window may open BEHIND JupyterLab (alt-tab); closing the window ends the script; re-run rather than rescue a half-drawn shape.
- **Lesson 2 — for-loop, range-function, loop-counter, turtle-drawing, float-type (60–90 min).**
  Open on the thread: the eight sad lines become three with `for`.
  This is one of the year's two densest lessons (five introductions) — hold the allocation strictly and push everything else to exercises.
  20 min: `for side_number in range(4)` redraws the square; predict-then-run.
  15 min: the loop variable counts — the lesson scales PEN THICKNESS with it (`pensize`).
  20 min: any polygon: `angle = 360 / n` — the calculator shows 51.42857…: floats arrive because the turtle NEEDS them (`l2_polygons.py` jumps straight to the 7-gon).
  15 min: pen up/down, colors (turtle-drawing) in `l2_polygons.py`.
  60-MINUTE CUT: drop the pensize-scaling segment (it returns in the exercises); the polygon-angle discovery is the lesson's non-negotiable core.
- **Lesson 3 — nested-loops (60–90 min).**
  Open on the thread: what if the whole polygon repeats, turned a little each time?
  25 min: read `l3_spirograph.py` together; the outer loop turns, the inner loop draws.
  Rest: design-your-own gallery; export by screenshot for the classroom wall.

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
