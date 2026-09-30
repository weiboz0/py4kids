# Teacher Notes — Checkpoint 02: Mock Contest 2

## Goals

The second mock contest checks that students can, under a time limit, diagnose which Term-2 technique a
problem wants and implement it cleanly as a stdin-to-stdout program:

- Make a correct greedy choice by sorting, then sweeping — matching two sorted lists, and always driving to
  the farthest reachable stop (Unit 6).
- Simulate a process step by step — two jugs with capped pours, and a running lead that survives ties —
  applying every rule in order (Unit 7).
- Precompute prefix sums: cumulative totals searched with binary search (Units 5 and 8), and every
  fixed-size square of a 2D grid (Unit 8).

Each technique appears twice, so the skill under test is *transfer*: reading a fresh problem and reaching
for the tool that fits.

## Pacing

One timed sitting of about **40 minutes** (the 0.5-lesson weight), then a review block next class.
Suggested flow: 5 minutes to read all six and plan an order (the Q2 and Q5 simulations and Q1's snack
sweep are usually the quickest to bank), ~35 minutes to work through them (each answer a complete program that reads `sys.stdin` and prints the result). Students need not finish all six.

## Common mistakes

- **Q1 (greedy matching):** giving each snack to the *neediest* kid it fits, or sorting only one list;
  moving to the next kid when a snack is skipped (only the snack pointer advances then). Trying every
  assignment is exponential.
- **Q4 (greedy refuels):** stopping at the *first* reachable station instead of the farthest one; missing
  the `-1` case when the next station is more than `D` beyond the current stop; forgetting that the second
  line is absent when `N = 0` (read by tokens, not by lines); stopping once more when the destination is
  already within reach.
- **Q2 (jug simulation):** pouring the whole source jug without capping at the room left in the target
  (`min(source, capacity - target)`), or updating one jug before computing the amount moved.
- **Q3 (prefix sums + binary search):** an off-by-one between day numbers and prefix indices (day `d` is
  `pre[d]`); searching for "greater than" instead of "at least" the goal; forgetting `-1` when the final
  total is still short. Scanning the days for every goal is O(n·q) and times out.
- **Q6 (prefix sums):** the ±1 index convention (`pre[r+1] - pre[l]`, not `pre[r] - pre[l]`); in 2D,
  a wrong sign or a dropped term in the four-term inclusion-exclusion formula.
- **Q6 (square placements):** a placement loop that stops one short (`top + K < R` instead of
  `top + K <= R`) misses the bottom row or right column of placements, which the sample's bottom-right answer
  catches; starting the best total at `0` prints `0` when every placement total is negative (a hidden case
  is all shadow).
- **Q5 (lead tracking):** resetting the last leader on a tie (so `A` leading again after a tie is wrongly
  counted as a change), counting the very first lead as a change, or comparing with the previous *event*
  instead of the previous *leader*.

## Discussion prompts

- For each question, name the technique and the one-sentence clue in the statement that pointed to it.
- Q3 and Q6 both build cumulative sums. Why may Q3 binary-search its prefix array (what makes it sorted?),
  and why does the 2D version in Q6 need four terms where 1D needs two? What would re-adding every
  `K`-by-`K` square cost?
- Q1 and Q4 are both greedy. For each, what is the greedy choice, and what small input shows that a
  different choice (the neediest kid first, the nearest station first) loses?
- Where did an off-by-one nearly bite you (a prefix boundary, a pour that overflows, a tie in the score),
  and what small input would have caught it?

## Differentiation

- **More support:** give the greedy rule for Q1/Q4 and the prefix-array construction for Q3, so the focus
  is the sweep / the search; award partial credit for a correct-but-slow per-goal scan on Q3 or a
  cell-by-cell re-add of every placement on Q6.
- **More challenge:** ask early finishers to state each solution's Big-O and to argue why the greedy choice
  in Q1 or Q4 can never do worse than any other choice.
- **Retry path:** a student who misses Q6 revisits Unit 8's 2D lesson; the review block re-solves Q1 and Q6
  as a class.

## Grading

100 points total; a question earns full credit only if its program produces the exact required output on
the hidden cases (not just the sample). Suggested split:

- Q1 Snack Sizes — 15 pts — Unit 6 greedy (matching two sorted lists) — O(n log n + m log m).
- Q2 Water Jug Log — 15 pts — Unit 7 simulation (capped pours) — O(N) over the N commands.
- Q3 Savings Goal Days — 20 pts — Unit 8 prefix sums + Unit 5 binary search — O(n + q log n).
- Q4 Road Trip Refuels — 15 pts — Unit 6 greedy (farthest reachable stop) — O(n log n).
- Q5 Lead Changes — 15 pts — Unit 7 simulation (running lead through ties) — O(N) over the N events.
- Q6 Solar Panel Placement — 20 pts — Unit 8 prefix-sum 2D (best `K`×`K` square) — O(R·C).

Partial credit: half a question's points for a solution that is correct but of the wrong complexity class
(passes small cases, times out on the largest) — diagnosing the efficient shape is the skill being trained.
Time budget: ~40 minutes.
