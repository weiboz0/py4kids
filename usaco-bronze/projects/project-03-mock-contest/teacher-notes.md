# Teacher Notes — Capstone: Grand Mock Contest

The finale of *Contest Python: USACO Bronze*: a full timed mock contest of eight problems in five milestones, integrating the whole
book's technique roster (prefix sums, simulation, binary search, greedy, two pointers, graphs/BFS,
flood-fill, recursion/backtracking, tree traversal). It introduces nothing new — it is where students prove
they can pick and apply the right technique under a clock.

## Goals

By the end of the capstone students can, unaided and under time pressure:

- **Read the problem, pick the technique, and pin the data structure** — recognizing a prefix-sum, a
  binary-search-on-the-answer, a two-pointer scan, a BFS, a flood-fill, a backtracking search, or a tree
  traversal from the problem's shape.
- Implement each cleanly as a stdin-to-stdout program, and defend its Big-O against the stated
  constraints ("will it finish in time?").
- Debug against a sample and reason about the boundary cases that a mock-contest grader will probe.

## Pacing

Three lessons: **(1)** a timed contest sitting (~60–90 min; students attempt as many of the eight as they
can), **(2)** a review of the reference solutions and the technique each rewards, **(3)** a retry/extension
session — resubmit fixed solvers and try the "Make it yours" extensions. Suggested weighting: Problems 1–4
are the accessible core; 5–8 stretch across the harder techniques.

## Common mistakes

- **P1 cut positions:** a cut must leave at least one box on each side, so the cuts run over prefix indices
  `1` through `N - 1`; starting the best at `0` (instead of the first real difference) prints `0` for every
  row. Re-adding both parts for each cut is O(N²).
- **P2 mirror directions:** swapping the `/` and `\` rules, or turning before moving into the next cell in the
  wrong order (each entered cell turns the beam, then it moves); stopping at the first repeated cell (a cell
  may be entered twice, and both entries count).
- **P3 the wrong search direction:** a distance that works makes every smaller distance work too, so keep
  the *largest* working distance (`lo = mid` with `mid = (lo + hi + 1) // 2`, or an equivalent form); a
  greedy check that does not start at the first sorted position undercounts.
- **P4 two-pointer pitfalls:** forgetting to sort first; moving `hi` back to `lo` for each new `lo` (O(N²));
  counting a pair twice. Both pointers only move forward.
- **P5 route counts:** giving a node the count of only the first node that reached it (every node one road
  closer that has a road to it must add its count); adding counts from nodes at the *same* distance; missing
  the modulus, or the `-1 0` and `0 1` cases. A LIFO stack instead of a `deque` FIFO queue breaks the
  distances.
- **P6 the edge test:** checking only the cell where the fill started, instead of every cell of the pond;
  treating diagonal water as connected (flood-fill is 4-neighbour).
- **P7 forgetting to un-mark:** backtracking must restore `used[p] = 0` after the recursive call, or the
  shared state leaks and the count collapses.
- **P8 the `-1` sentinel:** base-case `child == -1` BEFORE indexing; `arr[-1]` silently reads the last node.
  Choosing the deepest (instead of the shallowest) of several equally wide depths is the tie slip.

## Discussion prompts

- For each problem, what in its wording tips you off to the technique? Which two problems look similar but
  need different techniques?
- P3 "binary-searches the answer" rather than the data. Why is the feasibility check monotone, and why does
  that make binary search valid?
- P5 and P6 both explore a structure with a visited set. What is the "node" and the "edge" in each, and why
  does one use a queue and the other recursion? In P5, why must a node's route count be final before it
  leaves the queue?
- P7's backtracking and P8's traversal are both recursion. What makes one "backtracking" and the other a
  plain traversal?

## Differentiation

- **More support:** hand out the technique-per-problem mapping and the BFS-queue / recursive-DFS / prefix-sum
  skeletons; let students focus on the problem-specific logic. Pre-parse the input for P5/P8.
- **More challenge:** require a stated Big-O and a worst-case argument for every solved problem; assign all of
  the "Make it yours" extensions.
- **Extension:** ask fast finishers to write an additional original problem in the book's style with a
  reference solver and crafted tests (the first "Make it yours" option).

## Rubric

Grade from the answer key (each reference is a display-only mirror of a stdin/stdout program in
`assets/`, judged by piping each committed input case to it and comparing the printed output). Each problem
is judged as a stdin-to-stdout program against the sample plus hidden cases: full credit for a correct,
in-budget solver; partial credit for a correct approach with a boundary slip. Per-problem intended
complexity and the signature bug each problem's hidden cases catch:

| # | Technique | Intended complexity | Signature bug caught |
|---|-----------|---------------------|----------------------|
| 1 | Prefix sums over every cut | O(N) | a cut leaving one side empty / O(N²) re-adding |
| 2 | Grid simulation (mirror beam) | O(R·C) | swapped mirror rules / stopping at a revisit |
| 3 | Binary search on the answer + greedy | O(N log N + N · log(range)) | searching toward the smallest distance |
| 4 | Same-direction two pointers | O(N log N) | resetting `hi` for each `lo` (O(N²)) |
| 5 | Graph BFS with route counts | O(N + M) | counting only the first predecessor / missing modulus |
| 6 | Flood fill with an edge test | O(R·C), R·C ≤ 400 | testing only the starting cell of a pond |
| 7 | Recursion + backtracking | O(N!), N ≤ 9 | forgetting to restore shared state |
| 8 | Tree traversal with depths | O(N), height ≤ 500 | `-1` sentinel / tie to the deeper level |

A completed contest solves all eight within budget; a strong pass solves the core (1–4) plus at least two of
5–8 with correct techniques.
