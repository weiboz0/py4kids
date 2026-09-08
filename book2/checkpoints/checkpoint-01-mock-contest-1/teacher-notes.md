# Teacher Notes — Checkpoint 01: Mock Contest 1

## Goals

This first mock contest checks that students can, under a time limit, pick the right Term-1 tool for
each problem and implement it cleanly on the `solve(data)` contract:

- Parse structured input, including a 2D grid (Unit 1).
- Combine Boolean flags into a correct decision (Unit 2).
- Choose an efficient shape when the constraints demand it — a single pass or a sort, not an O(n²)
  scan (Unit 3).
- Use a set for dedup/membership and sort records by a compound tuple key (Unit 4).
- Answer many queries with binary search, and enumerate all triples with a fixed-depth loop (Unit 5).

The point is transfer: each question is deliberately a different tool, so students practise *diagnosing*
which technique a problem wants.

## Pacing

One timed sitting of about **40 minutes** (the 0.5-lesson weight), then a review block in the next class.
Suggested flow: 5 minutes to read all six problems and plan an order, ~35 minutes to solve, submitting
each via the wrapper shown at the top of the contest notebook. Students need not finish all six; encourage
banking the questions they are surest of first (Q2 and Q3 are the quickest wins).

## Common mistakes

- **Q1 (grid):** confusing rows and columns, or reading `R C` in the wrong order; summing rows instead of
  columns.
- **Q3 (efficiency):** an O(n²) "compare every pair" gain calculation that times out — the intended answer
  tracks the running minimum in a single pass.
- **Q4 (sets/tuples):** forgetting the tie-break in the sort, or de-duplicating *after* sorting instead of
  before; missing that the decisive record is the last one after sorting.
- **Q5 (binary search):** the classic off-by-one — `lo <= hi` vs `lo < hi`, and `mid + 1` / `mid - 1`
  updates; forgetting to sort first.
- **Q6 (complete search):** reusing an index (a triple must use three *distinct* positions), or looping to
  the wrong depth.

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

100 points total; a question is full credit only if its `solve` produces the exact required output on the
hidden cases (not just the sample). Suggested split by difficulty:

- Q1 Strongest Column — 15 pts — assesses Unit 1 (grid parsing) — O(R·C).
- Q2 Practice Room Gate — 10 pts — assesses Unit 2 (boolean logic) — O(1).
- Q3 Best Trading Gain — 15 pts — assesses Unit 3 (efficiency: single pass) — O(n).
- Q4 Distinct Leaderboard Records — 20 pts — assesses Unit 4 (sets + tuple-key sort) — O(n log n).
- Q5 Counts at Most the Limit — 20 pts — assesses Unit 5 (binary search over queries) — O((n + q) log n).
- Q6 Target Triple Count — 20 pts — assesses Unit 5 (fixed-depth complete search) — O(n³).

Partial credit: award half a question's points for a solution that is correct but of the wrong complexity
class (it would pass small cases but time out on the largest), since diagnosing the efficient shape is the
skill being trained. Time budget: ~40 minutes.
