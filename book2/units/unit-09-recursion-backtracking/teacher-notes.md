# Teacher Notes — Unit 09: Recursion & Backtracking

## Goals

By the end of this unit students can:

- Write a **recursive** function with a correct base case and a recursive case, and trace how the call
  stack unwinds.
- Recognize when a problem is "make a choice, then solve the smaller rest" and express it recursively.
- Use **backtracking**: extend a partial solution, recurse, and **undo** the choice on the way back —
  counting or generating all valid completions.
- Evaluate a **nested parenthesized expression** by recursion — find the operator that joins the two sides
  at depth zero, then evaluate each side the same way.

This is the first unit where a function may call itself and where "try every possibility" is done by search
rather than by nested loops — the tools for the counting/generation problems earlier units had to defer.

## Pacing

Three 60–90 minute lessons.

**Lesson 1 — Recursion.**
Open with a self-similar hook (count-the-ways).
Live-code the shape: a base case that returns directly, and a recursive case that calls the same function
on a smaller input. Warm-ups: factorial, sum-of-list, countdown. Hand-trace the call stack for a tiny input
so "what happens at the base case, then on the way back up" is concrete.
Class works Exercise 1 (subset count).

**Lesson 2 — Backtracking.**
Introduce the try → recurse → **undo** pattern: pick a choice, extend the partial path, recurse, then
restore the path before trying the next choice. Stress that the undo must be *correct* — pass a fresh
extended copy `path + [choice]` down (the caller's list is untouched), or restore in place with
`path[:] = path[:-1]`; do **not** write `path = path[:-1]` (that only rebinds the local name and leaves the
shared list mutated). Generate subsets / permutations / placements.
Class works Exercises 2, 3, 4 (spaced permutations; N-queens; coin combinations).

**Lesson 3 — Parsing by recursion + harder search.**
Work the nested-parenthesized-expression evaluator (scan at depth zero for the operator that joins the two
sides, then recurse on each side), then a partition/placement search. Discuss why these searches are
exponential and why the constraints keep N small.
Class works Exercises 5, 6, 7; assign a stretch problem (8 or 9) as an extension.

## Common mistakes

- **Missing or wrong base case** → infinite recursion (the program never stops). Every recursive function
  needs a case that returns without recursing.
- **Forgetting to undo** in backtracking → later branches inherit stale choices and the count is wrong.
- **The rebind trap:** writing `path = path[:-1]` after `path.append(x)` looks like an undo but only
  rebinds the local variable — the shared list the caller holds is still mutated. Pass `path + [choice]`
  down, or restore with `path[:] = path[:-1]`.
- **Mutating shared state across branches** (a set/list built once and never reset) → cross-contamination
  between recursive calls.
- **Not bounding the search** — exponential search only works because N is small; recognize when the
  constraints permit it.

## Discussion prompts

- For Exercise 1, what is the base case, and what are the two recursive choices at each step (take vs skip)?
- In backtracking, why must you undo a choice before trying the next one? Show an input where forgetting to
  undo gives the wrong count.
- Exercise 5 evaluates a nested expression by recursion, not a loop. What sub-problem does each recursive
  call solve, and where is the base case?
- These searches are exponential. For Exercise 3 (N-queens), roughly how many placements are examined, and
  why is that acceptable for small N?

## Differentiation

- **More support:** give the base case and the recursive-call signature for Exercises 1 and 5; provide a
  worked "take / skip" template for the subset search.
- **More challenge:** the stretch problems (8 Smallest Spaced Permutation, 9 Queens With Blocked Squares)
  add an ordering/optimization or extra constraints on top of the search; ask students to state the Big-O
  and to name where the undo happens.
- **Extension:** ask fast finishers to add a pruning check that cuts a branch early, and to measure how many
  fewer recursive calls it makes on a small input.

### Big-O per exercise

1. Target Subset Count — O(2ⁿ) (take/skip recursion over n items).
2. Spaced Permutation Count — O(n!) (permutation backtracking with a spacing check).
3. Queens Without Conflict — O(N!) worst case (place one queen per row, backtrack on conflict).
4. Coin Bag Combinations — exponential in the number of coins (combination search, order-independent).
5. Nested Expression Score — O(L) over the length-L expression (each character consumed once by the
   recursive parse).
6. Fractal Trail Count — O(bᵈ) for branching factor b and depth d (self-similar recursion).
7. Equal Team Partitions — O(2ⁿ) (assign each member to a side, backtrack).
8. Smallest Spaced Permutation *(stretch)* — O(n!) (ordered permutation search, keep the smallest valid).
9. Queens With Blocked Squares *(stretch)* — O(N!) worst case (N-queens search with extra blocked cells).
