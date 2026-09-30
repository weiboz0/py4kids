# Teacher Notes — Checkpoint 4: Mock Contest 4

A timed mini mock-contest closing Term 4 and the year's technique roster before the capstone. Seven
questions: grids/graphs (flood-fill, BFS, DFS), two pointers / sliding window, and a modular-power problem
reprising Unit 11. It assesses only already-taught techniques (Units 01–14); it introduces nothing.

## Goals

By the end of this checkpoint students can, under a clock:

- Flood-fill a grid to **count 4-connected regions** with a recursive walk and a `visited` set.
- Run **BFS** with a `deque` FIFO queue for a fewest-steps shortest path (and report unreachable as `-1`).
- Build an **adjacency-list graph** (plain dict) and test **connectivity with a recursive DFS** that passes
  `visited` as an argument.
- Apply **converging two pointers** from both ends of a row (largest rain trough, moving the shorter wall)
  and a **sliding window** with an incrementally maintained count (longest stretch with at most `K` rainy
  days).
- Compute a **modular power** by repeated squaring, reducing `% M` after every multiplication — the
  reduce-as-you-go discipline from Unit 11 — and print the last `D` digits with leading zeros restored.

## Pacing

One timed session of about **45–60 minutes** (`lessons: 0.5`). Suggested clock: 7 questions, roughly
6–8 minutes each. Q1–Q3 (grids/graphs) and Q4–Q5 (two pointers) are the core; Q6 (modular power) and Q7
(trace) are the shortest to code but reward careful reading. Students run each program and self-check
against the stated sample; grade from the solutions notebook after the clock stops.

## Common mistakes

- **Q1/Q2 diagonals:** these are 4-neighbour problems — adding diagonal steps merges lakes (Q1) or finds
  illegally short paths (Q2).
- **Q1 legend:** in this map `#` is lake water and `.` is dry ground; counting the `.` regions answers the
  wrong question.
- **Q2 with a LIFO stack:** using a stack instead of a FIFO `deque` (`append` + `popleft`) gives a longer,
  wrong step count. BFS needs FIFO.
- **Q2/Q3 forgetting `visited`:** an unmarked search loops forever (BFS) or recurses without end (DFS).
- **Q3 marking too late / only direct neighbours:** mark a node when first reached; recurse through the whole
  component, not just node 1's immediate neighbours.
- **Q4 moving the wrong pointer:** moving the TALLER wall can never help (the width shrinks and the shorter
  wall still limits the water), so always move the shorter one; moving the taller one skips the best trough.
  Forgetting to record the first trough (the two end posts) misses cases where the outer walls are best,
  such as a row of equal heights.
- **Q5 never shrinking the window:** a window that only grows reports a too-long stretch; shrink `left`
  whenever the rainy count exceeds `K`, and lower the count only when the day leaving is rainy. Recounting
  each window is O(n²) — keep the count incremental. `K = 0` and an all-rainy log (answer `0`) are hidden
  cases.
- **Q6 postponing the modulus:** reduce after every multiply and every square; computing the unreduced power
  first is infeasible at `E = 10^18`. No three-argument `pow`.
- **Q6 dropping leading zeros:** `str(answer)` alone prints `3289` for the sample; the odometer needs
  exactly `D` characters (`03289`). Also `E = 0` gives `1`, shown as `00…01`.
- **Q7 reading the queue as a stack:** the routine dequeues from the FRONT (FIFO) and appends neighbours in
  input order — trace it exactly.

## Discussion prompts

- Why does BFS (a FIFO queue) give the *fewest* steps while a stack does not? Trace both on Q2's grid.
- A grid and an adjacency-list graph look different but use the same visited-guarded walk — what is the
  "node" and the "edge" in each?
- Q4's pointers move toward each other and Q5's both move right. Why does each pointer move at most `N`
  times, making both linear?
- Q6: why is reducing after every step *necessary*, not just tidy, when the exponent is astronomically large?

## Differentiation

- **More support:** provide the four-neighbour offset list and the BFS-queue / recursive-DFS skeletons;
  pre-write the grid/graph parsing for Q1–Q3 so students focus on the traversal.
- **More challenge:** ask for the worst-case Big-O and the recursion depth of Q1/Q3, and why Q6 is O(log E)
  rather than O(E).
- **Extension:** have fast finishers argue why moving the shorter wall in Q4 never discards the best trough.

## Grading

Grade from the answer key (each reference is a display-only mirror of a stdin/stdout program in
`assets/`, judged by piping each committed input case to it and comparing the printed output). Each
question is judged as a stdin-to-stdout program against the sample plus hidden cases; award full credit for
a correct, in-budget solver, partial credit for a correct approach with a boundary slip (e.g. Q2 giving a
distance one off, Q3 missing the isolated-node case). Per-question intended complexity:

| Q | Technique | Intended complexity |
|---|-----------|---------------------|
| 1 | Flood-fill region count | O(R·C) |
| 2 | BFS fewest steps | O(R·C) |
| 3 | DFS connectivity | O(N + M) |
| 4 | Converging two pointers | O(N) |
| 5 | Sliding window | O(N) |
| 6 | Modular power (repeated squaring) + zero padding | O(log E + D) |
| 7 | BFS trace | O(N + M) |

Signature checks the hidden cases enforce: Q1 keeps diagonally-touching water separate; Q2's answer is the
true FIFO distance (a stack overshoots); Q3 reports `NO` for a disconnected graph; Q4 moves the shorter
wall's pointer; Q5 shrinks the window and handles `K = 0`; Q6 restores leading zeros, kills a dropped
odd-bit guard with an odd-exponent case, and forces reduction via the huge exponent; Q7 prints in FIFO (not stack) order.
