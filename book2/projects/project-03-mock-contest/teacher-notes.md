# Teacher Notes — Capstone: Grand Mock Contest

The Year-2 finale: a full timed mock contest of eight problems across five rounds, integrating the whole
year's technique roster (prefix sums, simulation, binary search, greedy, two pointers, graphs/BFS,
flood-fill, recursion/backtracking, tree traversal). It introduces nothing new — it is where students prove
they can pick and apply the right technique under a clock.

## Goals

By the end of the capstone students can, unaided and under time pressure:

- **Read the problem, pick the technique, and pin the data structure** — recognizing a prefix-sum, a
  binary-search-on-the-answer, a two-pointer scan, a BFS, a flood-fill, a backtracking search, or a tree
  traversal from the problem's shape.
- Implement each cleanly against the `solve(data) -> str` contract, and defend its Big-O against the stated
  constraints ("will it finish in time?").
- Debug against a sample and reason about the boundary cases that a mock-contest grader will probe.

## Pacing

Three lessons: **(1)** a timed contest sitting (~60–90 min; students attempt as many of the eight as they
can), **(2)** a review of the reference solutions and the technique each rewards, **(3)** a retry/extension
session — resubmit fixed solvers and try the "Make it yours" extensions. Suggested weighting: Problems 1–4
are the accessible core; 5–8 stretch across the harder techniques.

## Common mistakes

- **P1 prefix off-by-one:** the inclusive range `[l, r]` is `pre[r] - pre[l-1]`, not `pre[r] - pre[l]`.
- **P2 dropping the bounds guard:** a move off the grid must be ignored, not wrapped (`grid[-1]` is a real
  index in Python).
- **P3 searching the wrong range / wrong comparison:** binary-search the cap in `[max(w), sum(w)]`; a
  feasible cap needs `groups_needed(cap) <= K` (not `< K`).
- **P4 two-pointer pitfalls:** advance `lo` when the sum is too small, `hi` when too big; stop at `lo < hi`
  so a player is never paired with themselves; sort by the right key.
- **P5 BFS with a stack:** a LIFO stack instead of a `deque` FIFO queue returns a longer, wrong hop count;
  mark a node visited when you enqueue it.
- **P6 diagonals:** flood-fill is 4-neighbour — counting diagonals merges regions that should stay separate.
- **P7 forgetting to un-mark:** backtracking must restore `used[p] = 0` after the recursive call, or the
  shared state leaks and the count collapses.
- **P8 the `-1` sentinel:** base-case `child == -1` BEFORE indexing; `arr[-1]` silently reads the last node.

## Discussion prompts

- For each problem, what in its wording tips you off to the technique? Which two problems look similar but
  need different techniques?
- P3 "binary-searches the answer" rather than the data. Why is the feasibility check monotone, and why does
  that make binary search valid?
- P5 and P6 both explore a structure with a visited set. What is the "node" and the "edge" in each, and why
  does one use a queue and the other recursion?
- P7's backtracking and P8's traversal are both recursion. What makes one "backtracking" and the other a
  plain traversal?

## Differentiation

- **More support:** hand out the technique-per-problem mapping and the BFS-queue / recursive-DFS / prefix-sum
  skeletons; let students focus on the problem-specific logic. Pre-parse the input for P5/P8.
- **More challenge:** require a stated Big-O and a worst-case argument for every solved problem; assign all of
  the "Make it yours" extensions.
- **Extension:** ask fast finishers to write an additional original problem in the year's style with a
  reference solver and crafted tests (the first "Make it yours" option).

## Rubric

Grade from `solutions.ipynb` (every reference runs top-to-bottom clean with its asserts). Each problem is
judged on the `solve(data)` contract against the sample plus hidden cases: full credit for a correct,
in-budget solver; partial credit for a correct approach with a boundary slip. Per-problem intended
complexity and the signature bug each problem's hidden asserts catch:

| # | Technique | Intended complexity | Signature bug caught |
|---|-----------|---------------------|----------------------|
| 1 | Prefix-sum range queries | O(N + Q) | inclusive off-by-one (`pre[r]-pre[l]`) |
| 2 | Grid simulation | O(len(moves)) | missing off-grid bounds guard |
| 3 | Binary search on the answer + greedy | O(N · log(sum)) | wrong feasibility comparison / range |
| 4 | Converging two pointers | O(N log N) | wrong pointer move / self-pairing |
| 5 | Graph BFS (adjacency list) | O(N + M) | LIFO stack instead of FIFO queue |
| 6 | Flood fill | O(R·C), R·C ≤ 400 | 8-neighbour merge |
| 7 | Recursion + backtracking | O(N!), N ≤ 9 | forgetting to restore shared state |
| 8 | Tree pre-order traversal | O(N), N ≤ 300 | pre- vs post-order / `-1` sentinel |

A completed contest solves all eight within budget; a strong pass solves the core (1–4) plus at least two of
5–8 with correct techniques.
