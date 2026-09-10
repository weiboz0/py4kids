# Teacher Notes — Unit 06: Greedy

## Goals

By the end of this unit students can:

- Recognize a greedy problem: one where repeatedly taking the locally-best choice builds a globally-best
  answer.
- Pick the **right sort key** and sweep once — the heart of most greedy solutions.
- Give an informal, plain-words reason *why* a particular greedy choice is safe (an exchange argument:
  "swapping toward the greedy choice never makes the answer worse").
- Recognize when greedy is *not* valid, and reach for a different tool instead of trusting a hunch.

Greedy is the first unit where "which order do I process things in?" is the whole problem, so the sort key
is where their attention should go.

## Pacing

Two 60–90 minute lessons. Each greedy pattern is a short **worked-example ladder** — the local choice on a tiny hand-traceable case (executable in the notebook on literal data), then the full **stdin** solver shown `no-exec` and run from a terminal (`python assets/l1.py < assets/l1/1.in`; Book 2 now reads stdin/prints stdout — no `solve()` wrapper). BOTH counterexamples are executable rungs (greedy-by-start attends fewer than greedy-by-end; greedy coins `1,3,4` for `6` uses 3 vs the optimal 2), and the pairing (`l3`) and cheapest-first (`l4`) patterns each get an executable mastery rung (crossed-vs-sorted distance; a budget sweep). Reference solvers live as runnable `.py` in `assets/`, judged against committed `.in`/`.out` fixtures.

**Lesson 1 — The greedy pattern.**
Open with the project hook (fit the most non-overlapping events into a day).
Live-code the classic: sort the intervals by END time, then sweep, taking each event whose start is after
the last one taken.
Walk the exchange argument out loud: if the optimal answer didn't take the earliest-ending compatible
event, we could swap it in without losing anything.
Introduce a second pattern — fewest coins with canonical denominations (take as many of the largest as
fit, then the next) — and the deadline/shortest-job orderings.
Class works Exercises 1–5.

**Lesson 2 — Choosing the key, and when greedy fails.**
Compare sort keys on the same problem to show a wrong key gives a wrong answer.
Present ONE counter-example where greedy is tempting but wrong (e.g. coins `1, 3, 4` making `6`: greedy
gives `4+1+1`, optimal is `3+3`) — the takeaway is "justify the choice, don't assume."
Class works Exercises 6–9 (budget items, shortest-job checkout, and the two stretch problems).

## Common mistakes

- **Wrong sort key** — sorting by start instead of end for interval scheduling, or by value instead of
  value-per-cost. The sort key IS the algorithm; get it wrong and everything downstream is wrong.
- **Assuming greedy always works** — for problems where it doesn't (non-canonical coins, some knapsacks),
  greedy silently gives a wrong-but-plausible answer. Always be able to say why the choice is safe.
- **Sorting in place and losing the original indices** when the answer needs the original position.
- **Off-by-one on the final swept item** — a sweep that stops one element early misses the last decisive
  choice (several exercises place the decisive element last after sorting to catch this).
- **Comparing tuples the wrong way** — when sorting `(key, tie-breaker)` records, make the tie-breaker
  explicit rather than relying on incidental order.

## Discussion prompts

- For Exercise 1, why does sorting by END time work but sorting by START time or by DURATION fail? Find an
  input where each wrong key gives a wrong answer.
- What is the one-sentence "exchange argument" for the sort key you chose in Exercise 5?
- Exercise 3 (fewest coins) is greedy-safe for the given denominations. Invent a denomination set where
  greedy would fail, and say how you'd know.
- When you finish a greedy solution, what's the quickest test that would reveal a wrong sort key?

## Differentiation

- **More support:** give the sort key for Exercises 1 and 2 and let students focus on writing the sweep;
  provide a worked exchange argument they can adapt.
- **More challenge:** the stretch problems (8 Fewest Checkpoints, 9 Prize Jobs) need a less obvious key or a
  small secondary structure; ask students to state and defend the key, and to give the Big-O.
- **Extension:** for any exercise, ask fast finishers to construct the smallest input on which a named wrong
  greedy key fails — a concrete counter-example is the best evidence a key is right.

### Big-O per exercise

1. Festival Marathon — O(n log n) (sort intervals by end, single sweep).
2. Smallest Worst Lateness — O(n log n) (sort by deadline, sweep accumulating time).
3. Fewest Coins — O(k) over the k denominations (take the largest that fits, repeat).
4. Robot Charging Match — O(n log n) (sort both lists, pair in order).
5. One-Minute Job Deadlines — O(n log n) (sort by deadline / value, sweep).
6. Most Supplies on Budget — O(n log n) (sort by cost ascending, take cheapest until budget runs out).
7. Fast Checkout Order — O(n log n) (shortest-job-first: sort ascending, sum completion times).
8. Fewest Checkpoints *(stretch)* — O(n log n) (sort by end, cover greedily).
9. Prize Jobs *(stretch)* — O(n²) worst case (sort by profit O(n log n), then for each job scan backward for the latest free slot — the scan is O(n) per job).
