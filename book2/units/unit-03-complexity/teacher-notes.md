# Teacher Notes — Book 2 Unit 03: Fast Enough? (Complexity)

## Goals

Students learn to treat complexity as a technique for choosing an approach before coding.
They count one important repeated operation, recognize the informal growth families O(n), O(n²), and O(log n), and use the largest stated constraint to predict whether an approach will finish.
They explain why repeatedly halving a numeric range takes O(log n) guesses without turning the lesson into a later unit's search algorithm.
They compare a direct pair-checking approach with a dictionary-based single pass on the same pair-sum problem.
Every solver follows the pure `solve(data: str) -> str` contract: parse the whole string inside the function and return output text.

The intended approach for every exercise is:

- Exercise 1, Count Scores at Least the Target: O(n), because one scan counts qualifying scores; an O(n²) approach cannot handle N up to 200000.
- Exercise 2, First Time the Total Reaches the Goal: O(n), because one running total processes each turn once; recomputing prefixes in O(n²) cannot handle N up to 200000.
- Exercise 3, Longest Winning Streak: O(n), because current and best streaks update once per score; checking every possible interval in O(n²) cannot handle N up to 200000.
- Exercise 4, Most Frequent Number: O(n), because one pass builds frequencies and one pass over dictionary pairs finds the winner; pairwise counting in O(n²) cannot handle N up to 200000.
- Exercise 5, Pair Sum Check: O(n), because a dictionary remembers earlier values during one pass; trying every pair in O(n²) cannot handle N up to 200000.
- Exercise 6, Smallest Neighbor Gap: O(n log n), because one in-place sort is followed by one scan; checking every pair in O(n²) cannot handle N up to 200000.
- Exercise 7, First Repeated Value: O(n), because a dictionary records arrivals during one pass; rescanning earlier values in O(n²) cannot handle N up to 200000.
- Exercise 8, Longest Distance Within a Limit: O(n log n), because one in-place sort is followed by one neighboring-gap scan; checking every pair in O(n²) cannot handle N up to 200000.
- Exercise 9, Most Valuable Team: O(n), because running totals update during one scan; checking every possible interval in O(n²) cannot handle N up to 200000.

## Pacing

Budget: one 60–90 minute lesson.

- Hook and operation counting, 10 minutes: show that a correct answer can still lose to a time limit, then count the work in one loop and a nested loop.
- Three growth families, 10 minutes: connect O(n) to one scan, O(n²) to a full nested scan, and O(log n) to repeatedly halving a numeric range.
- Reading constraints, 10 minutes: work through why N up to 100 can allow about 10000 checks while N up to 100000 demands an approach close to O(n).
- Naive-versus-fast pair sum, 15 minutes: trace both runnable approaches, compare their counts, and name the dictionary as the memory that removes the repeated scan.
- Independent practice, 15–45 minutes: begin with Exercises 1–3, route ready students through Exercises 4–7, and reserve Exercises 8–9 as stretch work.
- 60-MINUTE CUT: after the pair-sum comparison, assign Exercises 1–3 only and move Exercises 4–9 to a later practice block.

## Common mistakes

- Reaching for a nested loop when a single pass with a running value or dictionary is enough.
- Ignoring the stated constraints until after choosing or coding an approach.
- Treating a small sample as proof that an O(n²) approach will finish on the largest allowed input.
- Assuming Big-O is an exact operation count instead of a description of how work grows.
- Forgetting that list `.sort()` changes the same list in place and returns `None`, so `x = mylist.sort()` is a bug.
- Reusing one position twice in the pair-sum exercise instead of requiring two different input positions.
- Stopping a scan one position early and missing a decisive final value.
- Printing inside `solve` instead of returning the exact output string.

## Discussion prompts

- How can an answer be logically correct but still be rejected by a contest judge?
- If N doubles, what rough change do you expect for O(n) work and for O(n²) work?
- Why do constraints tell us more about speed than the sample input does?
- What information does the fast pair-sum approach remember that the direct approach keeps rediscovering?
- Why can repeatedly halving a range handle a surprisingly large starting range?
- When might a clear O(n²) approach still be a reasonable choice?

## Differentiation

- Strugglers: give students a two-column trace sheet labeled `operation` and `count`, and let them tally the demo loops by hand before running them.
- Visual support: draw 100 boxes, cross out half after each guess, and write the remaining range size beside every step.
- Constraint support: compare 100, 10000, 100000, and 10000000000 with place-value spacing so the growth gap is visible.
- Middle tier: complete Exercises 1–5 and explain the single piece of state each O(n) solution carries forward.
- Fast finishers: complete both stretch exercises and write a short comparison between their chosen complexity and an O(n²) alternative.
- Pair check: one student proposes an approach while the other points to the largest constraint and challenges whether the operation count fits.
