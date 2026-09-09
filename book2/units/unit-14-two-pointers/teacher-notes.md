# Teacher Notes — Unit 14: Two Pointers & Sliding Window

## Goals

By the end of this unit students can:

- Use **converging two pointers** on a SORTED list — `lo` and `hi` moving inward by comparison — to find a
  pair summing to a target, count pairs under a threshold, or find the closest pair, in O(n) after sorting.
- Use a **sliding window** — `left`/`right` indices over a contiguous run with a running sum/count updated
  INCREMENTALLY — to find the longest or shortest window meeting a condition, in O(n).
- Explain why both patterns are linear (each pointer only ever moves forward) and why the window
  sum/count is maintained incrementally rather than recomputed.
- Recognize that the sliding-window grow/shrink logic requires **non-negative values** (with negatives the
  monotonicity breaks and the window answer is wrong).

This is the last Book-2 technique: it turns an O(n²) nested-loop scan into a single O(n) (or O(n log n)) pass.

## Pacing

Two 60–90 minute lessons, core exercises assigned per lesson (stretches optional homework):

**Lesson 1 — Converging two pointers.** On a sorted list, `lo`/`hi` move inward: sum too small → advance
`lo`; too big → retreat `hi`. Hand-trace a pair search; cover closest-pair and one-way decisions; argue O(n)
after the O(n log n) sort. Class works **Exercises 1, 2, 3, 4** (Exact Budget Pair; Pairs Below the Alarm;
Closest Combined Score; Teammates by Finish Time).

**Lesson 2 — Sliding windows.** Grow `right`, shrink `left` when the window violates its bound, maintaining
the running sum incrementally; stress that non-negative values make shrinking safe, and that the
shortest-window goal reverses the shrink condition. Argue O(n). Class works **Exercises 5, 6, 7** (Longest
Affordable Streak; Shortest Training Burst; Badge Variety Limit). Assign the stretch problems (8 Count
Affordable Windows, 9 Minimum Rescue Boats) as extension.

## Common mistakes

- **Advancing the wrong pointer** — in a converging search, if the sum is too small you must move `lo` up
  (the only way to increase it on a sorted list), and vice versa; moving the wrong one misses pairs.
- **Forgetting to shrink the window** — a solver that only grows `right` and never advances `left` reports a
  window that is too long (or never finds the shortest); always shrink when the bound is violated.
- **Re-summing the window each step** — recomputing `sum(window)` inside the loop is O(n²); keep a running
  sum and add/subtract the entering/leaving element.
- **Sliding window on negative values** — the grow/shrink logic only works when values are non-negative; the
  exercises state this, and students should know why.
- **Forgetting to sort** — converging two pointers require a sorted list; running them on unsorted data is
  wrong. Sort first (by the key the problem needs).
- **Off-by-one on window bounds** — be precise whether the window is `[left, right]` inclusive and when
  `right` has moved past the end.

## Discussion prompts

- Why do converging two pointers find the answer in O(n) after sorting, when the brute force is O(n²)? What
  invariant lets you discard a whole row/column of pairs at each step?
- In the sliding window, why is it safe to never move `left` backward? What would break if values could be
  negative?
- "Longest window with sum ≤ K" and "shortest window with sum ≥ K" shrink under opposite conditions — state
  each shrink rule.

## Differentiation

- **More support:** give the `lo`/`hi` converging template and the grow/shrink window skeleton; pre-write the
  parsing and sorting so students focus on the pointer logic.
- **More challenge:** the stretch problems (8 Count Affordable Windows — count rather than find; 9 Minimum
  Rescue Boats — the classic pair-greedy) need the technique applied in a new shape; ask for the Big-O and
  the sort key.
- **Extension:** ask fast finishers to prove each pointer moves at most n times, giving the O(n) bound.

### Concept → core-exercise coverage

- **two-pointers** → Ex 1–4 (converging pointers on a sorted list) and Ex 5–7 (sliding window) — every core
  exercise exercises the technique.

(Stretch: Ex 8 Count Affordable Windows; Ex 9 Minimum Rescue Boats.)

### Big-O per exercise

1. Exact Budget Pair — O(n) after an O(n log n) sort (converging pointers).
2. Pairs Below the Alarm — O(n) after sort (count pairs as `hi` retreats).
3. Closest Combined Score — O(n) after sort (track the closest sum).
4. Teammates by Finish Time — O(n log n) (sort by the finish-time key, then pointers).
5. Longest Affordable Streak — O(n) (sliding window, sum ≤ K).
6. Shortest Training Burst — O(n) (sliding window, sum ≥ K).
7. Badge Variety Limit — O(n) (window with a bounded variety/count).
8. Count Affordable Windows *(stretch)* — O(n) (count windows as the right edge advances).
9. Minimum Rescue Boats *(stretch)* — O(n) after sort (converging greedy pairing).
