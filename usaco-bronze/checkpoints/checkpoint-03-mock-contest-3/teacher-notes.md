# Teacher Notes — Checkpoint 3: Mock Contest 3

## Goals

A timed mock contest assessing **Term 3** (Units 9–12) as stdin-to-stdout programs:

- **Recursion & backtracking** (U09) — a search that marks a choice, recurses, and un-marks on the way back.
- **Stacks & postfix evaluation** (U10) — a `deque` used as a stack (`appendleft`/`popleft`) to evaluate a
  postfix logic circuit with one- and two-operand gates.
- **Number systems & number theory** (U11) — base-`B` conversion by hand (with a palindrome test on the
  digits), bitmask subset enumeration, GCD/LCM, and a Sieve of Eratosthenes reused to count twin primes.
- **Binary trees** (U12) — a recursive traversal over a parallel-array tree that gives back the best
  root-to-leaf path total.

The seven questions map one-to-one onto those techniques (see the grading table). This is an assessment, so
there is no stretch tier and no new material.

## Pacing

A single timed sitting of about **40–50 minutes** (the 0.5-lesson checkpoint slot).

Students are **not expected to finish all seven** — the contest rewards banking the questions you are sure of.
Advise them to read all seven first, start with the ones whose technique they recognize fastest (Q3 base
conversion, Q5 GCD/LCM, and Q6 sieve are the quickest), and leave **Q1 (gap-respecting orders)** for last — it is the
heaviest (a full backtracking search with a correct un-mark). A student who solves five cleanly has passed.

## Common mistakes

- **Forgetting the un-mark in Q1** — after recursing, `used[i]` must be set back to `False`, or later branches
  inherit a stale "taken" flag and the count is wrong.
- **Reaching for `.pop()` in Q2** — removal from the stack is `.popleft` on a `deque`; `.pop` is untaught.
- **Postfix operand order (Q2)** — for `IMP`, the FIRST value removed is the right operand; removing in the
  wrong order turns `1 IMP 0` (= `0`) into `0 IMP 1` (= `1`). `AND` and `OR` hide this slip because they are
  symmetric, so only the `IMP` cases catch it.
- **`NOT` arity (Q2)** — `NOT` removes ONE operand; treating every gate as two-operand empties the stack
  early (an error on a `deque` with nothing left) or combines the wrong bits.
- **Digit order (Q3)** — repeated `% B` produces the digits least-significant-first; reassemble them in the
  right order (the sample prints `21211` instead of `11212` if not). A palindrome hides this slip, so the
  first output line is what catches it. Handle `0` explicitly (→ `0` and `YES`).
- **Hard-coding base 2 (Q3)** — the base is an input; `% 2` and `// 2` pass only the base-2 cases.
- **Bit index in Q4** — item `i` is in the subset when `mask & (1 << i)` is nonzero; an off-by-one on the
  shift drops or double-counts items. Remember the empty mask (subset sum 0).
- **Sieve bound (Q6)** — cross off multiples starting at `p*p` and include the endpoint correctly; `N = 169`
  (= 13², with `167` prime) is the case a `<` vs `<=` slip gets wrong (13 pairs instead of 12).
- **Pair range (Q6)** — both members must be at most `N`: check `p + 2 <= N` so the last index stays in the
  sieve list, and count each pair once (from its smaller prime). Small `N` such as `2` or `4` has no pairs.
- **A missing child is not a leaf (Q7)** — a node with only one child must continue into that child. Giving
  back `0` for a missing child and taking the larger side lets a path stop early at a one-child node; with
  negative values that over-counts (the sample's `9` instead of `8`).
- **The `-1` child sentinel in Q7** — never recurse on child `-1`: it silently indexes the LAST node
  (`values[-1]`), re-enters that node's children, and typically recurses forever (`RecursionError`) or
  yields a wrong total.
- **Starting the best at `0` (Q7)** — when every path total is negative, the answer is negative; the leaf
  base case, not `0`, must seed the comparison.

## Discussion prompts

- Q1: why does the un-mark have to happen *after* the recursive call comes back, not before? Show an input where
  skipping it over-counts or under-counts.
- Q2: why is a stack the right structure for postfix evaluation, and what does the stack hold at each step?
- Q4: the bitmask enumerates all `2^N` subsets. Why must `N` stay small, and how does `mask & (1 << i)` pick
  out a subset?
- Q7: why does a one-child node need a different rule from a two-child node? Draw a tree where treating the
  missing child as `0` gives the wrong path total.

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
| 1 | Gap-Respecting Orders | recursion + backtracking (U09) | 20 |
| 2 | Postfix Logic Circuit | deque + postfix-eval (U10) | 15 |
| 3 | Mirror Number in Base B | base-conversion (U11) | 10 |
| 4 | Exact-Total Subsets | bitwise-ops + bitmask (U11) | 15 |
| 5 | GCD and LCM | gcd (U11) | 10 |
| 6 | Twin Prime Pairs | sieve (U11) | 15 |
| 7 | Heaviest Root-to-Leaf Path | tree-traversal (U12) | 15 |

Each answer is a complete stdin-to-stdout program; students read the whole input with:

```python
import sys
data = sys.stdin.read()
```

### Big-O per question

1. Gap-Respecting Orders — O(N!) worst case (backtracking over orderings of N, N ≤ 9).
2. Postfix Logic Circuit — O(T) over T tokens (each pushed/removed once).
3. Mirror Number in Base B — O(log n) (one digit per division).
4. Exact-Total Subsets — O(2ᴺ·N) (every mask, N bits each).
5. GCD and LCM — O(N·log(max value)) (Euclid per pair across the list).
6. Twin Prime Pairs — O(N log log N) (sieve) + O(N) pair scan.
7. Heaviest Root-to-Leaf Path — O(N) (visit each node once).
