# Teacher Notes — Unit 08: Prefix Sums

## Goals

By the end of this unit students can:

- Build a 1D prefix-sum array (`pre[0] = 0`, `pre[i] = pre[i-1] + a[i-1]`) in O(n) and answer any
  range-sum query `sum of a[l..r] = pre[r+1] - pre[l]` in O(1).
- State and defend the **±1 index convention** — why `pre` has one extra entry and where the `+1`/`-1`
  land — and avoid the classic off-by-one.
- Build a 2D grid prefix sum and use the four-term **inclusion-exclusion** formula to sum any
  sub-rectangle in O(1).
- Recognize when a problem "asks the same kind of sum many times" and reach for prefix sums instead of
  recomputing.

Prefix sums are the first unit where a cheap precomputation turns a slow repeated query into an instant
one — the payoff of "think before you loop."

## Pacing

Two 60–90 minute lessons. Each concept is a short **worked-example ladder**: the core idea on a tiny array
you can trace by hand → one step up → the full program that reads the real input from **stdin**. The early
rungs run live in the notebook (literal data); the full solver is shown `no-exec` and **run from a terminal**
(`python assets/l1.py < assets/l1/1.in`) — that is the real contest shape, now that Book 2 reads stdin and
prints stdout (no `solve()` wrapper). Reference solvers live as runnable `.py` in `assets/`, judged against
committed `.in`/`.out` fixtures.

**Lesson 1 — 1D prefix sums.**
Open with the hook: answer many range-sum queries over a big array.
Live-code the naive per-query loop, count its cost (O(n) per query → too slow for many queries), then walk
the 1D ladder: build `pre` on a tiny array (`pre[0] = 0`) → one range query `pre[r+1] - pre[l]` → loop
several queries → the full stdin solver (`assets/l1.py`).
Hand-trace the index convention on a tiny array so the `pre[r+1] - pre[l]` boundary is concrete.
Extend to prefix *counts* (how many 1s / how many values in a range) — same idea on a 0/1 or indicator array.
Class works Exercises 1–4 (range totals, lit-tile counts, target-sum reports, strongest range).

**Lesson 2 — 2D grid prefix sums.**
Walk the 2D ladder: build the prefix grid on a tiny grid (one extra zero row and column) → one rectangle
query via the four-term formula → the full stdin solver (`assets/l2.py`). Derive inclusion-exclusion by
drawing the four overlapping regions.
Hand-trace one sub-rectangle so the signs are concrete: add the big corner, subtract the two strips, add
back the doubly-subtracted corner.
Class works Exercises 5–9 (map rectangle totals, region beacon counts, best survey zone, and the two
stretch window problems — 8 Best Bounded Candidate Window and 9 Longest Low-Total Streak).

Note on house style: the prefix grid is pre-sized with an **append loop** (the `[0] * n` list-repetition
idiom is banned book-wide, so the 2D rungs look a little longer — that is expected).

## Common mistakes

- **Off-by-one on the ±1 convention** — mixing 0-based array indices with the 1-shifted prefix array; using
  `pre[r] - pre[l]` (drops `a[r]` or includes `a[l-1]`) instead of `pre[r+1] - pre[l]`.
- **Wrong inclusion-exclusion signs (2D)** — subtracting one strip twice, or forgetting to add back the
  double-subtracted corner. Draw the rectangles.
- **Querying before building** — reading the prefix array before it is fully filled, or rebuilding it per
  query (defeats the whole point).
- **Indexing the last row/column** — the prefix grid is `(R+1)×(C+1)`; the final real cell is at
  `pre[R][C]`, not `pre[R+1][C+1]` on the *values*.

## Discussion prompts

- Why does the prefix array have `n + 1` entries instead of `n`? What would break if it had `n`?
- Exercise 5 sums a sub-rectangle with four terms. Draw the four regions and explain why the corner is
  *added back* — what was subtracted twice?
- For Exercise 1, at how many queries does building the prefix array pay off versus scanning per query?
- Prefix counts (Exercise 2) and prefix sums (Exercise 1) use the same trick on different arrays. What is
  the array in each case?

## Differentiation

- **More support:** give the built prefix array for Exercises 1 and 5 and have students write only the
  query formula; provide a labeled diagram of the 2D four-term rectangle.
- **More challenge:** the stretch problems (8 Best Bounded Candidate Window, 9 Longest Low-Total Streak)
  combine prefix sums with a scan or search; ask students to state the Big-O and where the ±1 lives.
- **Extension:** ask fast finishers to answer Exercise 4's *reported* ranges two ways — by loop-summing
  each reported range directly (O(Q·n)) and via the prefix-sum O(1)-per-query version — and confirm they
  agree on small inputs. (Note this is the max over the *given* ranges, not the max over all possible
  subranges.)

### Big-O per exercise

1. Arena Range Totals — O(n + Q) (build prefix O(n), each of Q queries O(1)).
2. Lit Tiles in a Range — O(n + Q) (prefix counts of the 1s).
3. Target-Sum Reports — O(n + Q) (prefix sums, one O(1) test per report).
4. Strongest Reported Range — O(n + Q) (prefix sums, one O(1) range sum per query).
5. Map Rectangle Totals — O(R·C + Q) (build the 2D prefix grid, each query O(1) inclusion-exclusion).
6. Beacons in a Region — O(R·C + Q) (2D prefix counts over the beacon indicator grid).
7. Most Valuable Survey Zone — O(R·C + Q) (2D prefix sums; one O(1) rectangle sum per candidate zone).
8. Best Bounded Candidate Window *(stretch)* — O(n + Q) (prefix sums, O(1) per candidate window).
9. Longest Low-Total Streak *(stretch)* — O(n²) after an O(n) prefix build (enumerate all O(n²) windows,
   each total checked in O(1) via the prefix array — negatives rule out a linear sliding window here).
