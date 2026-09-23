# Teacher Notes — Unit 06: Turtle Geometry

## Goals

Students leave able to import a module (`import turtle`), drive the turtle with `forward` and
`left`/`right`, lift and lower the pen (`penup`/`pendown`), and set the pen's look (`pencolor`/`color`,
`pensize`).
The mathematical core is the exterior-angle rule: a regular n-gon turns `360 / n` at each corner, written
with TRUE division so it is honest for every n (including the seven-sided token, where `360 / 7 ≈ 51.43°`).
Success looks like: every student runs a `.py` turtle script from the terminal, edits it, and re-runs it;
draws a chosen regular polygon with a `for` loop and the `360 / n` rule; and stacks a loop inside a loop to
repeat a shape into a ring.
This is the first unit whose programs run as `.py` files in a terminal rather than in notebook cells — the
terminal run is the unit's core `run-program` activity.

The project hook is a **turtle gallery**: the teacher opens Lesson 1 by running the finished
`assets/l3_gallery.py` for thirty seconds ("we will build this — today, the first shape"), and the unit
works back up to it.

## Pacing

Budget: three lessons of 60–90 minutes; ladders with a *Notice* per rung.

- **Lesson 1 — Move & Draw (`import-statement`, `turtle-basics`).**
  Open with the gallery teaser, then the reachable question "what turn makes a square? predict, then run."
  Teach `import turtle`, `turtle.forward`/`turtle.left`/`turtle.right`, and `penup`/`pendown` (a
  travel-without-drawing rung, `assets/l1_travel.py`); draw a square by hand (`assets/l1_square.py`), then
  with a `for` loop (`assets/l1_square_loop.py`).
  **First terminal encounter (~15 min, budget it):** File → New → Terminal, `cd` into the unit directory,
  `python assets/l1_square.py`, then edit-save-rerun; expect to walk the room and repeat this twice.
  Show the two errors students WILL hit, and read them together: calling `forward(100)` without the
  `turtle.` prefix raises `NameError: name 'forward' is not defined` (module-level style means every call is
  `turtle.forward`), and running from the wrong folder prints `can't open file '.../l1_square.py'`.
- **Lesson 2 — Any Polygon (`turtle-drawing`).**
  The exterior-angle insight as the GENERAL rule: `angle = 360 / n`, drawn with
  `for corner in range(n): turtle.forward(side); turtle.left(angle)`.
  The heptagon (`assets/l2_heptagon.py`, `n = 7`) is a **core predict-then-run rung**, not a challenge —
  `360 / 7 = 51.428…`, "the turtle turns by a decimal just the same," and the seven turns still total 360°,
  so it closes.
  Add colour and thickness (`assets/l2_styled_pentagon.py`).
  Then the **contrast Notice** (this is where `//` appears, and ONLY here): `360 // n` is a whole-number
  shortcut that lands on the same angle only when n divides 360 (3, 4, 5, 6, 8, 9, 10, 12); for `n = 7`,
  `360 // 7 = 51` and `7 × 51 = 357 ≠ 360`, so the shape would leave a three-degree gap.
  Close the lesson with the five-point star (`assets/l2_star.py`, `angle = 720 / n`, `144°` — "two full
  turns").
- **Lesson 3 — Patterns with Nested Loops (`nested-loops`).**
  A ring of polygons (`assets/l3_ring.py`): an outer loop turns `360 / shape_count` between shapes, an inner
  loop draws each polygon; use `shape` and `corner`, and finish the inner loop before the outer turn.
  A growing spiral (`assets/l3_spiral.py`): `side = side + step` is the accumulator, and the path does NOT
  close, so the file carries the exact comment `# turtle-check: open-path`.
  Then the gallery final build (`assets/l3_gallery.py`).

**60-minute cut (any lesson):** In Lesson 1 keep the square loop AND the edit-save-rerun live — the terminal
run is this unit's core skill and is introduced here; drop the `penup`/`pendown` travel rung instead.
In Lesson 2 the `360 / n` polygon loop is non-negotiable core; defer the colour/`pensize` flourishes and the
`//` contrast Notice.
In Lesson 3 run the ring live and leave the growing spiral as a "try it."

## Exercises — core vs. extra vs. challenge

Core (1–7): Courtyard Square (`n=4`, side 62, royalblue), Trail-Sign Triangle (`n=3`, side 74, forestgreen,
120° — the outside angle, not 60°), Festival Pentagon (`n=5`, side 68, orchid, `pensize` 4), Decimal-Turn
Heptagon (`n=7`, side 57, darkorange — the float-angle rung; the student states `360 / 7` before running and
reads it back with a `print`, total turn 360°), Move Then Mark (travel 39, then an OCTAGON `n=8` side 44
crimson, 45° turns, 8 pen-down moves), Nine-Hexagon Wheel (`n=6` side 41 turquoise, `shape_count=9`, 40°
between shapes, 54 pen-down moves — the nested loop), Growing Radar Spiral (`side=11`, `step=6`, 14 moves,
maroon, open-path, accumulator ends at 95, does NOT close).
Challenges (8–9, tagged `stretch`): Five-Point Star (`n=5`, side 96, goldenrod, `angle = 720 / n = 144°`,
total turn 720°); The Eight-Degree Gap (draw the honest eleven-sided shape with `n=11`, side 34, magenta,
`360 / n` ≈ 32.73°, total turn 360°, closes; then predict what `turtle.left(360 // 11)` would draw —
`360 // 11 = 32`, `11 × 32 = 352`, an 8° gap, does NOT close).
Every core exercise uses a distinct polygon `n` (4, 3, 5, 7, 8, 6) with a distinct `(side, colour)`; the two
challenges are a star (`720 / n`) and an eleven-sided almost-shape, distinct from the lesson rungs and from
each other in shape, size, colour, and checkable number.
No core exercise depends on a challenge; all angles use `/`, never `//`, in the drawn assets.

## Common mistakes

- Calling `forward(100)` without the `turtle.` prefix → `NameError` — module-level style means every call is
  `turtle.forward`; read the error and add the prefix.
- Running `python assets/lN.py` from the wrong directory → `can't open file` — `cd` into the unit folder first.
- Putting `turtle.done()` inside the loop (drawing stalls after one side) — it goes once, at the very end;
  a missing final `turtle.done()` makes the window flash and vanish.
- Using the inside angle: a triangle turns 120°, not 60° (the turtle turns through the EXTERIOR angle).
- Replacing `360 / n` with a rounded whole number or `//` — the heptagon then leaves a gap and will not close.
- `left` vs `right` mirror the drawing; `penup` without a later `pendown` leaves nothing on the page.
- The turtle window opens BEHIND JupyterLab; closing the window ends the script (re-run, don't rescue).
- Nested loops: finish the inner (per-side) loop before the outer per-shape turn; `range(n)` gives 0..n-1.

## Discussion prompts

- Why does a regular polygon turn `360 / n` and not `180 / n` or `60`? Where does the 360 come from?
- The heptagon turns by 51.428…°, a decimal. Why does it still close after seven turns?
- When is `360 // n` exactly equal to `360 / n`, and when does it leave a gap? Give an n for each case.
- Why does the five-point star use 720 instead of 360? What does "two full turns" mean here?
- In the nine-hexagon wheel, which loop draws a shape and which loop places the shapes around the center?
- Why does the growing spiral need the `# turtle-check: open-path` comment when the polygons do not?

## Differentiation

- Strugglers: give the outer loop of the ring and have them write only the inner polygon loop; keep them on
  polygons whose `360 / n` is a whole number (square, triangle, hexagon) before the heptagon.
- Fast finishers: the two Challenges (star, the eight-degree gap), then extend the gallery with another
  polygon or a second ring at a new colour.
- Middle tier: change one polygon's `n` and predict the new turn angle and total-turn before running, then
  confirm the drawing closes.
