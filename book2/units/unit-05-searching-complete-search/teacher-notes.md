# Teacher Notes — Unit 05: Searching & Complete Search

## Goals

By the end of this unit students can:

- Explain why a linear scan is O(n) per query and why that is too slow when there are many queries.
- Implement iterative **binary search** on a sorted list with a correct `lo`/`hi`/`mid` loop,
  and adapt it to *count* matches and to find a *lower-bound* (insertion position).
- Choose to **sort first**, then search — recognizing sorting as the enabling step.
- Solve pair/triple problems by **complete search**: fixed-depth nested loops over all
  pairs or triples, and reason about the O(n²)/O(n³) cost from Unit 3.
- Use **search over the answer**: binary-search the smallest feasible value when the answer is
  monotonic (feasible above a threshold, infeasible below).

They should also know the boundaries: no recursion yet (that is Unit 9), and no converging
two-pointer scan yet (that is Unit 14) — a pair is found here by a nested loop or by binary-searching
the complement.

## Pacing

Three 60–90 minute lessons.

**Lesson 1 — Linear vs binary search.**
Open with the hook: answer many "is X present?" queries over the same list.
Show the linear scan, count its work, then motivate sorting once and binary-searching each query.
Live-code the `lo <= hi` presence search, walking a concrete trace of `mid` moves.
Then adapt it twice: count how many equal a target (lower and upper bound), and find the insertion
position (lower bound alone).
Class works Exercises 1–3 (presence, count, insertion positions). Stress the four danger inputs:
target absent, target equal to the first element, target equal to the last element, empty range.

**Lesson 2 — Complete search and complement search.**
Fixed-depth enumeration: all pairs with a double loop, all triples with a triple loop; connect the
loop depth to the Big-O and to the constraint bounds that make it affordable.
Contrast the O(n²) pair loop with the O(n log n) "sort, then binary-search each element's complement"
approach for pair-sum — and name explicitly why we are *not* walking two pointers inward yet.
Class works Exercises 4–6 (pair sum by complement, closest gap, triple to target).

**Lesson 3 — Search over the answer, plus mixed practice.**
Introduce the monotonic-answer idea: if capacity C works then every capacity above C works, so
binary-search the smallest C that works.
Class works Exercises 7–9 (smallest delivery capacity, values in each range, the stretch lock),
then revisits any Lesson 1–2 problem students found hard.

## Common mistakes

- Binary-search off-by-one: mixing `lo <= hi` with `hi = mid` (infinite loop) or `hi = mid - 1`
  with a `lo < hi` guard (skips the answer). Pick one consistent convention and trace it.
- Forgetting to sort before binary-searching — the invariant only holds on sorted data.
- Enumerating with the wrong loop depth (a triple problem needs three nested loops, not two).
- The self-pair trap in pair-sum: an element is not its own partner unless it appears twice.
- Reaching for a 2ⁿ subset enumeration — defer to Unit 9 (recursion); here N is small enough for
  fixed-depth loops, or the structure allows binary search.
- Reaching for a converging two-pointer scan — defer to Unit 14; use a nested loop or complement
  binary search instead.

## Discussion prompts

- Exercise 1 has many queries. How does the total cost change between "scan the list for every query"
  and "sort once, then binary-search each query"? At what number of queries does sorting pay off?
- In Exercise 7 we binary-search the *answer*, not an array. What property of the answer makes that
  legal, and how would you check "does capacity C work?" quickly?
- Exercise 4 could be solved with a double loop or with complement search. What are the trade-offs,
  and when would the double loop be perfectly fine?
- Why is "sort then scan adjacent pairs" (Exercise 5) enough to find the closest pair, when the
  closest pair might not look adjacent before sorting?

## Differentiation

- **More support:** give a working binary-search presence function and have students *adapt* it to
  count (Exercise 2) rather than write it from scratch; provide the "does C work?" checker for
  Exercise 7 so the focus is the search loop.
- **More challenge:** the stretch problems (8 Values in Each Range, 9 Sum-and-Product Lock) combine
  two binary searches per query and constrained enumeration; ask students to state each solution's
  Big-O and justify why the constraints rule out a naive per-query linear scan.
- **Extension:** ask fast finishers to re-derive Exercise 3's insertion position as "count of values
  strictly less than the target" and confirm the two formulations agree.

### Big-O per exercise

1. Many Number Queries — O((n + q) log n) (sort once, binary-search per query).
2. Count Many Targets — O((n + q) log n) (lower/upper bound per query).
3. Many Insertion Positions — O((n + q) log n) (lower bound per query).
4. Pair Sum by Complement Search — O(n log n) (sort, binary-search each complement).
5. Closest Pair Gap — O(n log n) (sort, single adjacent scan).
6. Three Values Make the Target — O(n³) worst case (fixed-depth triple loop, small N).
7. Smallest Delivery Capacity — O(n log(Σ)) (binary search over the answer, O(n) feasibility check).
8. Values in Each Range *(stretch)* — O((n + q) log n) (two bounds per query).
9. Sum-and-Product Lock *(stretch)* — O(n²) (fixed-depth complete search over candidate pairs).
