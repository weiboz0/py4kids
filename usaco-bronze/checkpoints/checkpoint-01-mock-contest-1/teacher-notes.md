# Teacher Notes — Checkpoint 01: Mock Contest 1

## Goals

This first mock contest checks that students can, under a time limit, pick the right Term-1 tool for
each problem and implement it cleanly as a stdin-to-stdout program:

- Parse structured input, including a 2D grid (Unit 1).
- Combine Boolean flags into a correct decision (Unit 2).
- Choose an efficient shape when the constraints demand it — a single pass or a sort, not an O(n²)
  scan (Unit 3).
- Store records as tuples in a set, test membership of a reversed tuple, and sort the results with a
  named key function (Unit 4).
- Answer many nearest-neighbour queries with binary search, and enumerate every position triple with
  fixed-depth loops (Unit 5).

The point is transfer: each question is deliberately a different tool, so students practise *diagnosing*
which technique a problem wants.

## Pacing

One timed sitting of about **40 minutes** (the 0.5-lesson weight), then a review block in the next class.
Suggested flow: 5 minutes to read all six problems and plan an order, ~35 minutes to work through them —
each answer a complete program that reads the input from `sys.stdin` and prints the result. Students need
not finish all six; encourage
banking the questions they are surest of first (Q2 and Q3 are the quickest wins).

## Common mistakes

- **Q1 (grid):** confusing rows and columns, or reading `R C` in the wrong order; summing rows instead of
  columns.
- **Q3 (efficiency):** an O(n²) "compare every pair" gain calculation that times out — the intended answer
  tracks the running minimum in a single pass.
- **Q4 (sets/tuples):** counting a repeated pick twice (store picks in a set first), reporting each mutual
  pair twice (once as `Ava Ben` and once as `Ben Ava` — keep only the pair whose first name is
  alphabetically earlier), or printing the pairs in input order instead of sorted order. Scanning the whole
  pick list for each reversed pick is O(n²) and times out on the largest case.
- **Q5 (binary search):** checking only the station at or after the house (the one before may be closer),
  or indexing past either end when the house lies before the first or beyond the last station; the classic
  `lo < hi` / `mid + 1` off-by-one; forgetting to sort first. A house exactly at a station answers `0`.
- **Q6 (complete search):** comparing the values in sorted order instead of position order (`2 5 8` in the
  sample is not a valid pick), counting only increasing steps (a decreasing pick such as `9 6 3` counts),
  or reusing a position.

## Discussion prompts

- For each question, which unit did it come from, and what was the one-sentence clue in the statement that
  pointed to the technique?
- Q3 and Q6 both "look at combinations." Why does Q3 have an O(n) answer while Q6 needs three nested loops?
  What is different about what each problem asks?
- Q5 gives many queries. How much faster is "sort once, binary-search each query" than "scan the list for
  every query," and when would the simpler scan have been acceptable?
- Where did an off-by-one nearly bite you, and what test input would have caught it?

## Differentiation

- **More support:** allow the grid dimensions of Q1 and the flag order of Q2 to be walked through together
  before the timer starts; award generous partial credit for a correct-but-slow Q3/Q5.
- **More challenge:** ask early finishers to state each solution's Big-O and to name, for Q3 and Q5, the
  input size at which a naive approach would time out.
- **Retry path:** students who miss Q5 or Q6 revisit Unit 5's exercises before the next checkpoint; the
  review block re-solves Q4 and Q6 as a class.

## Grading

100 points total; a question is full credit only if its program produces the exact required output on the
hidden cases (not just the sample). Suggested split by difficulty:

- Q1 Strongest Column — 15 pts — assesses Unit 1 (grid parsing) — O(R·C).
- Q2 Practice Room Gate — 10 pts — assesses Unit 2 (boolean logic) — O(1).
- Q3 Best Trading Gain — 15 pts — assesses Unit 3 (efficiency: single pass) — O(n).
- Q4 Mutual Partner Picks — 20 pts — assesses Unit 4 (set of tuples + named-key sort) — O(n log n).
- Q5 Nearest Charging Station — 20 pts — assesses Unit 5 (binary search over queries) — O((n + q) log n).
- Q6 Evenly Spaced Picks — 20 pts — assesses Unit 5 (fixed-depth complete search) — O(n³).

Partial credit: award half a question's points for a solution that is correct but of the wrong complexity
class (it would pass small cases but time out on the largest), since diagnosing the efficient shape is the
skill being trained. Time budget: ~40 minutes.
