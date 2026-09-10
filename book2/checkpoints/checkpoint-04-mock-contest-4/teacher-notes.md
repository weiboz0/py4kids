# Teacher Notes — Checkpoint 4: Mock Contest 4 (Term 4 Finale)

A timed mini mock-contest closing Term 4 and the year's technique roster before the capstone. Seven
questions: grids/graphs (flood-fill, BFS, DFS), two pointers / sliding window, and a modular-power problem
reprising Unit 11. It assesses only already-taught techniques (Units 01–14); it introduces nothing.

## Goals

By the end of this checkpoint students can, under a clock:

- Flood-fill a grid to **count 4-connected regions** with a recursive walk and a `visited` set.
- Run **BFS** with a `deque` FIFO queue for a fewest-steps shortest path (and report unreachable as `-1`).
- Build an **adjacency-list graph** (plain dict) and test **connectivity with a recursive DFS** that passes
  `visited` as an argument.
- Apply **converging two pointers** on a sorted list (exact-sum pair) and a **sliding window** with an
  incrementally maintained running sum (longest affordable run).
- Compute a **modular power** by repeated squaring, reducing `% M` after every multiplication — the
  reduce-as-you-go discipline from Unit 11.

## Pacing

One timed session of about **45–60 minutes** (`lessons: 0.5`). Suggested clock: 7 questions, roughly
6–8 minutes each. Q1–Q3 (grids/graphs) and Q4–Q5 (two pointers) are the core; Q6 (modular power) and Q7
(trace) are the shortest to code but reward careful reading. Students submit each `solve(data)` and self-check
against the stated sample; grade from the solutions notebook after the clock stops.

## Common mistakes

- **Q1/Q2 diagonals:** these are 4-neighbour problems — adding diagonal steps merges regions (Q1) or finds
  illegally short paths (Q2).
- **Q2 with a LIFO stack:** using a stack instead of a FIFO `deque` (`append` + `popleft`) returns a longer,
  wrong step count. BFS needs FIFO.
- **Q2/Q3 forgetting `visited`:** an unmarked search loops forever (BFS) or recurses without end (DFS).
- **Q3 marking too late / only direct neighbours:** mark a node when first reached; recurse through the whole
  component, not just node 1's immediate neighbours.
- **Q4 moving the wrong pointer:** on a sorted list, sum too small ⇒ advance `lo`; too big ⇒ retreat `hi`.
- **Q5 never shrinking the window:** a window that only grows reports a too-long run; shrink `left` whenever
  the running sum exceeds `K`. Recomputing the sum each step is O(n²) — keep it incremental.
- **Q6 postponing the modulus:** reduce after every multiply and every square; computing the unreduced power
  first is infeasible at `E = 10^18`. No three-argument `pow`.
- **Q7 reading the queue as a stack:** the routine dequeues from the FRONT (FIFO) and appends neighbours in
  input order — trace it exactly.

## Discussion prompts

- Why does BFS (a FIFO queue) give the *fewest* steps while a stack does not? Trace both on Q2's grid.
- A grid and an adjacency-list graph look different but use the same visited-guarded walk — what is the
  "node" and the "edge" in each?
- Q4 and Q5 both move two indices forward only. What invariant makes each linear after the sort/first pass?
- Q6: why is reducing after every step *necessary*, not just tidy, when the exponent is astronomically large?

## Differentiation

- **More support:** provide the four-neighbour offset list and the BFS-queue / recursive-DFS skeletons;
  pre-write the grid/graph parsing for Q1–Q3 so students focus on the traversal.
- **More challenge:** ask for the worst-case Big-O and the recursion depth of Q1/Q3, and why Q6 is O(log E)
  rather than O(E).
- **Extension:** have fast finishers explain why the sliding window in Q5 requires non-negative costs.

## Grading

Grade from `solutions.ipynb` (every reference runs top-to-bottom clean with the stated asserts). Each
question is judged on the `solve(data)` contract against the sample plus hidden cases; award full credit for
a correct, in-budget solver, partial credit for a correct approach with a boundary slip (e.g. Q2 returning a
distance one off, Q3 missing the isolated-node case). Per-question intended complexity:

| Q | Technique | Intended complexity |
|---|-----------|---------------------|
| 1 | Flood-fill region count | O(R·C) |
| 2 | BFS fewest steps | O(R·C) |
| 3 | DFS connectivity | O(N + M) |
| 4 | Converging two pointers | O(N log N) sort + O(N) scan |
| 5 | Sliding window | O(N) |
| 6 | Modular power (repeated squaring) | O(log E) |
| 7 | BFS trace | O(N + M) |

Signature checks the hidden asserts enforce: Q1 keeps diagonally-touching land separate; Q2's answer is the
true FIFO distance (a stack overshoots); Q3 reports `NO` for a disconnected graph; Q4 moves the correct
pointer; Q5 shrinks the window; Q6 kills a dropped odd-bit guard with an even-exponent case and forces
reduction via the huge exponent; Q7 prints in FIFO (not stack) order.
