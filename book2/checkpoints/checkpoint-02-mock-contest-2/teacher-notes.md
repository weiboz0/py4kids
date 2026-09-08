# Teacher Notes — Checkpoint 02: Mock Contest 2

## Goals

The second mock contest checks that students can, under a time limit, diagnose which Term-2 technique a
problem wants and implement it cleanly on the `solve(data)` contract:

- Make a correct greedy choice by sorting on the right key, then sweeping (Unit 6).
- Simulate a process step by step — a grid walk and a bounded counter — watching the edges (Unit 7).
- Precompute prefix sums to answer many range queries fast, in 1D and on a 2D grid (Unit 8).

Each technique appears twice, so the skill under test is *transfer*: reading a fresh problem and reaching
for the tool that fits.

## Pacing

One timed sitting of about **40 minutes** (the 0.5-lesson weight), then a review block next class.
Suggested flow: 5 minutes to read all six and plan an order (Q2 and Q5 simulations and Q4's budget sweep
are usually the quickest to bank), ~35 minutes to solve. Students need not finish all six.

## Common mistakes

- **Q1/Q4 (greedy):** wrong sort key — sorting intervals by start instead of end, or items by value instead
  of cost; the sort key *is* the algorithm.
- **Q2 (grid simulation):** letting the robot walk off the grid or through a `#` wall instead of skipping
  that move; confusing row/column order.
- **Q3/Q6 (prefix sums):** the ±1 index convention (`pre[r+1] - pre[l]`, not `pre[r] - pre[l]`); in 2D,
  a wrong sign or a dropped term in the four-term inclusion-exclusion formula.
- **Q5 (bounded counter):** clamping to the cap/floor in the wrong order, or forgetting to clamp every tick
  (only at the end); off-by-one on the final tick.

## Discussion prompts

- For each question, name the technique and the one-sentence clue in the statement that pointed to it.
- Q3 and Q6 are the same idea in 1D and 2D. What is the "array" in each, and why does the 2D version need
  four terms where the 1D version needs two?
- Q1 and Q4 are both greedy but sort on different keys. What would go wrong if you swapped their sort keys?
- Where did an off-by-one nearly bite you (a prefix boundary, a robot at a wall, the last tick), and what
  small input would have caught it?

## Differentiation

- **More support:** give the sort key for Q1/Q4 and the prefix-array construction for Q3, so the focus is
  the sweep / the query formula; award partial credit for a correct-but-slow per-query scan on Q3/Q6.
- **More challenge:** ask early finishers to state each solution's Big-O and, for Q3/Q6, the number of
  queries at which precomputing the prefix array pays off over per-query recomputation.
- **Retry path:** a student who misses Q6 revisits Unit 8's 2D lesson; the review block re-solves Q1 and Q6
  as a class.

## Grading

100 points total; a question earns full credit only if its `solve` produces the exact required output on
the hidden cases (not just the sample). Suggested split:

- Q1 Festival Stage Schedule — 15 pts — Unit 6 greedy (interval scheduling) — O(n log n).
- Q2 Gallery Robot — 15 pts — Unit 7 simulation (grid walk) — O(M) over the M commands.
- Q3 Scoreboard Range Reports — 20 pts — Unit 8 prefix-sum 1D — O(n + Q).
- Q4 Supply Cart Budget — 15 pts — Unit 6 greedy (max items under budget) — O(n log n).
- Q5 Safety Counter — 15 pts — Unit 7 simulation (bounded counter) — O(T) over the T ticks.
- Q6 Survey Rectangle Sums — 20 pts — Unit 8 prefix-sum 2D — O(R·C + Q).

Partial credit: half a question's points for a solution that is correct but of the wrong complexity class
(passes small cases, times out on the largest) — diagnosing the efficient shape is the skill being trained.
Time budget: ~40 minutes.
