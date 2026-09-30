# Teacher Notes — Checkpoint 4: Mock Contest 4

A timed mini mock-contest closing Term 4 and the year's technique roster before the capstone. Seven
questions: grids/graphs (flood-fill, BFS, DFS), two pointers / sliding window, and a modular-power problem
reprising Unit 11. It assesses only already-taught techniques (Units 01–14); it introduces nothing.

## Goals

By the end of this checkpoint students can, under a clock:

- Flood-fill a grid **once** with a recursive walk, labelling every 4-connected region and recording its
  size, so that many lookups are answered without filling again.
- Run **BFS** with a `deque` FIFO queue from **several starting cells at once** (every mold cell starts at
  time `0`) and report `-1` when some cell is never reached.
- Build an **adjacency-list graph** (plain dict) and use a **recursive DFS** that gives neighbours the
  opposite team, restarting from every unvisited node to cover separate groups.
- Apply **converging two pointers** from both ends of a row (largest rain trough, moving the shorter wall)
  and a **sliding window** with incrementally maintained counts (the shortest stretch holding every
  flavor).
- Use **repeated squaring** with every product reduced `% M` — here on a pair of values (a power and a
  running total) walked through the bits of the exponent — the reduce-as-you-go discipline from Unit 11.

## Pacing

One timed session of about **45–60 minutes** (`lessons: 0.5`). Suggested clock: 7 questions, roughly
6–8 minutes each. Q1–Q3 (grids/graphs) and Q4–Q5 (two pointers) are the core; Q6 (modular power) is short
to code but needs the doubling rules applied carefully, and Q7 (trace) rewards careful reading. Students
run each program and self-check against the stated sample; grade from the solutions notebook after the
clock stops.

## Common mistakes

- **Q1 filling per question:** re-running the flood fill for each of up to `200000` questions is far too
  slow; fill each pasture once, store its number per cell and its size per pasture, then look answers up.
  A fence cell answers `0`, and diagonal contact does not join pastures (the sample's corner cell).
- **Q2 one source at a time:** running a separate BFS from each mold cell (or re-scanning the whole map
  every minute) is too slow; all mold cells go on the queue at time `0` before the first `popleft`. Forgetting
  the `-1` check (a walled-off clean cell) or the `0` case (no clean cell) are the edge-case slips.
- **Q2 with a LIFO stack:** a stack instead of a FIFO `deque` (`append` + `popleft`) reaches cells at the
  wrong times and overstates the answer. BFS needs FIFO.
- **Q3 one DFS only:** starting only from student `1` misses rival groups that are not connected to it —
  restart the DFS from every unplaced student. Checking only the rivals a student places (not the ones
  already placed) misses an odd ring.
- **Q4 moving the wrong pointer:** moving the TALLER wall can never help (the width shrinks and the shorter
  wall still limits the water), so always move the shorter one; moving the taller one skips the best trough.
  Forgetting to record the first trough (the two end posts) misses cases where the outer walls are best,
  such as a row of equal heights.
- **Q5 never shrinking, or shrinking too little:** record the length *while* the window still holds every
  flavor, then shrink; decrease the "flavors held" count only when a flavor's count drops to `0`. Counting
  distinct flavors afresh for each window is O(n²).
- **Q6 the doubling order:** when doubling, the new total must use the *old* power
  (`total + power * total`) before `power` is squared; adding a day uses the *new* power. Reduce after every
  multiplication, and remember `E = 0` (answer `0`) and `M = 1` (answer `0`). Looping over the days, or
  dividing by `A - 1`, does not work.
- **Q7 reading the queue as a stack:** the routine dequeues from the FRONT (FIFO) and appends neighbours in
  input order — trace it exactly.

## Discussion prompts

- Why does a BFS that starts from all mold cells at once give each cell the time of its *nearest* mold?
  What goes wrong if the sources are added one at a time?
- Q1 and Q2 both explore a grid. Why is Q1's recursive walk safe here (how deep can it go when `R*C <= 400`),
  while Q2's much larger maps call for a queue?
- Q3: why does a ring with an odd number of students make the split impossible? Trace the DFS on a triangle.
- Q4's pointers move toward each other and Q5's both move right. Why does each pointer move at most `N`
  times, making both linear?
- Q6: check the doubling rule on a small case — from `e = 2` to `e = 4` with `A = 3`, what are the power and
  the total before and after?

## Differentiation

- **More support:** provide the four-neighbour offset list and the BFS-queue / recursive-DFS skeletons;
  pre-write the grid/graph parsing for Q1–Q3 so students focus on the traversal. For Q6, let students check
  their doubling step against a day-by-day loop on small inputs first.
- **More challenge:** ask for the worst-case Big-O and the recursion depth of Q1/Q3, and why Q6 is O(log E)
  rather than O(E).
- **Extension:** have fast finishers argue why moving the shorter wall in Q4 never discards the best trough.

## Grading

Grade from the answer key (each reference is a display-only mirror of a stdin/stdout program in
`assets/`, judged by piping each committed input case to it and comparing the printed output). Each
question is judged as a stdin-to-stdout program against the sample plus hidden cases, including one large
case (thousands of items, large enough to expose a quadratic or per-query approach); award full credit for a correct, in-budget solver, partial credit for a correct
approach with a boundary slip (e.g. Q2 missing the `-1` case, Q3 missing a separate rival group).
Per-question intended complexity:

| Q | Technique | Intended complexity |
|---|-----------|---------------------|
| 1 | Flood-fill labelling + lookups | O(R·C + Q) |
| 2 | Multi-source BFS | O(R·C) |
| 3 | DFS two-team placement | O(N + M) |
| 4 | Converging two pointers | O(N) |
| 5 | Sliding window with counts | O(N) |
| 6 | Repeated squaring on (power, total) | O(log E) |
| 7 | BFS trace | O(N + M) |

Signature checks the hidden cases enforce: Q1's large case (a `20 × 20` map with `12000` questions) times
out a per-question flood fill, and a fence question answers `0`; Q2 needs every mold cell as a source, answers
`0` with no clean cell and `-1` for a walled-off one, and its snake-shaped large case defeats minute-by-minute
rescans; Q3 reports `NO` for an odd ring hidden in a second group; Q4 moves the shorter wall's pointer; Q5
keeps shrinking while the window is complete; Q6 handles `E = 0`, `M = 1`, `A = 0` and `A = 1`, and its
exponents near `10^18` rule out a day-by-day loop; Q7 prints in FIFO (not stack) order.
