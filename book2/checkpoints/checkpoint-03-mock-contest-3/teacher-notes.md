# Teacher Notes — Checkpoint 3: Mock Contest 3

## Goals

A timed mock contest assessing **Term 3** (Units 9–12) on the `solve(data)` contract:

- **Recursion & backtracking** (U09) — a search that marks a choice, recurses, and un-marks on return.
- **Stacks & postfix evaluation** (U10) — a `deque` used as a stack (`appendleft`/`popleft`).
- **Number systems & number theory** (U11) — base conversion by hand, bitmask subset enumeration, GCD/LCM,
  the Sieve of Eratosthenes.
- **Binary trees** (U12) — a recursive pre-order traversal over a parallel-array tree.

The seven questions map one-to-one onto those techniques (see the grading table). This is an assessment, so
there is no stretch tier and no new material.

## Pacing

A single timed sitting of about **40–50 minutes** (the 0.5-lesson checkpoint slot).

Students are **not expected to finish all seven** — the contest rewards banking the questions you are sure of.
Advise them to read all seven first, start with the ones whose technique they recognize fastest (Q3 binary,
Q5 GCD/LCM, and Q6 sieve are the quickest), and leave **Q1 (spaced-permutation count)** for last — it is the
heaviest (a full backtracking search with a correct un-mark). A student who solves five cleanly has passed.

## Common mistakes

- **Forgetting the un-mark in Q1** — after recursing, `used[i]` must be set back to `False`, or later branches
  inherit a stale "taken" flag and the count is wrong.
- **Reaching for `.pop()` in Q2** — removal from the stack is `.popleft` on a `deque`; `.pop` is untaught.
- **Postfix operand order (Q2)** — for `-`, the FIRST value popped is the right operand; popping in the wrong
  order flips the sign.
- **Binary digit order (Q3)** — repeated `% 2` produces the bits least-significant-first; reassemble them in
  the right order, and handle `0` explicitly (→ `"0"`).
- **Bit index in Q4** — item `i` is in the subset when `mask & (1 << i)` is nonzero; an off-by-one on the
  shift drops or double-counts items. Remember the empty mask (subset sum 0).
- **Sieve bound (Q6)** — cross off multiples starting at `p*p` and include the endpoint correctly; `N = 49`
  (= 7²) is the case a `<` vs `<=` slip gets wrong.
- **The `-1` child sentinel in Q7** — test `child == -1` BEFORE indexing the arrays; `arr[-1]` silently reads
  the last node and yields a wrong (not crashing) answer.

## Discussion prompts

- Q1: why does the un-mark have to happen *after* the recursive call returns, not before? Show an input where
  skipping it over-counts or under-counts.
- Q2: why is a stack the right structure for postfix evaluation, and what does the stack hold at each step?
- Q4: the bitmask enumerates all `2^N` subsets. Why must `N` stay small, and how does `mask & (1 << i)` pick
  out a subset?
- Q7: for the same tree, how do pre-order and in-order differ, and why can't you produce pre-order by sorting?

## Differentiation

- **More support:** allow a reference card of the Term-3 idioms (deque push/pop, `mask & (1<<i)`, Euclid,
  the sieve loop, the recursive-traversal skeleton); grade for technique even when an edge case is missed.
- **More challenge:** ask fast finishers to state each solution's Big-O and to identify, for Q1 and Q4, the
  input size at which the exponential search stops being fast enough.

## Grading

Total **100 points**, ~40–50 minute sitting. Partial credit per question (correct technique + most cases).
A passing result is roughly **5 of 7 clean** (≈ 70+).

| Q | Problem | Technique assessed | Points |
|---|---------|--------------------|-------:|
| 1 | Spaced Permutation Count | recursion + backtracking (U09) | 20 |
| 2 | Postfix Score | deque + postfix-eval (U10) | 15 |
| 3 | Decimal to Binary | base-conversion (U11) | 10 |
| 4 | Exact-Total Subsets | bitwise-ops + bitmask (U11) | 15 |
| 5 | GCD and LCM | gcd (U11) | 10 |
| 6 | Primes Up To N | sieve (U11) | 15 |
| 7 | Pre-order Readout | tree-traversal (U12) | 15 |

Submission wrapper (shown to students; they paste it under a finished `solve`):

```python
import sys
print(solve(sys.stdin.read()))
```

### Big-O per question

1. Spaced Permutation Count — O(N!) worst case (backtracking over orderings of N, N ≤ 9).
2. Postfix Score — O(T) over T tokens (each pushed/popped once).
3. Decimal to Binary — O(log n) (one bit per division).
4. Exact-Total Subsets — O(2ᴺ·N) (every mask, N bits each).
5. GCD and LCM — O(N·log(max value)) (Euclid per pair across the list).
6. Primes Up To N — O(N log log N) (sieve).
7. Pre-order Readout — O(N) (visit each node once).
