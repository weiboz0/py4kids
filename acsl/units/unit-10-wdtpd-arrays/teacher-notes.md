# Teacher Notes — Unit 10: What Does This Program Do? – Arrays

## Goals

Students learn Junior's third Contest 3 category: tracing programs that use arrays and grids, and writing their exact one-line output.
By the end they can:

- read ACSL array notation, `A(i)` and `A(r, c)`, and check where the positions start (1 or 0) before tracing;
- translate an array that starts at 1 to Python with an unused slot at position 0;
- trace arrays filled by a formula, positions computed from a counter (`A(i + 1)`, `A(n + 1 - i)`), and a value used as a position (a tally);
- trace in-place changes box by box: sums, counts, extremes, swaps, reversal to the middle, shifts, rotations and running totals;
- trace grids row by row or column by column, including both diagonals, triangles, a swap across the diagonal, and neighbour checks.

The hook is a row of lockers: the program reverses the row by swapping to the middle and then takes a weighted sum. Its answer is `5 67`. Lesson 1 checks it in Python and Lesson 2 traces it by hand.

String traversal is deliberately left out: Junior meets it in Contest 4.

## Pacing

Budget: three lessons of 60–90 minutes in the Contest 3 window.

- **Lesson 1.**
  - ACSL array notation, and where positions start.
  - Filling with a formula, computed positions, and reading an array from the input.
  - A value used as a position, then the hook in Python.
- **Lesson 2.**
  - Sum, count and extremes, with `>` versus `>=` ties.
  - Swapping with a temporary box; reversing to `int(n / 2)` and the full-loop trap.
  - Shifting (the loop direction matters), rotating, and a pass that uses its own changes.
- **Lesson 3.**
  - Grids: filling, rows versus columns, both diagonals and the triangles.
  - Swapping across the diagonal, and neighbours.
- **Exercises:** 19 items, all Junior (16 short answers, 3 predict-then-verify programs: 8, 14 and 17); 18–19 are Challenges. 14 of the 19 are in ACSL pseudocode.

**60-minute cut:** keep Lesson 1's notation and Lesson 2's in-place changes; set the grid lesson as reading plus Exercises 12–13.

## Common mistakes

- Starting at position 0 when the program's array starts at 1, or the other way round.
- Reversing by swapping over the whole array, which swaps every pair twice and changes nothing.
- Shifting in the wrong loop direction, so one value is copied into every box.
- Tracing a pass with the array as it was at the start, when each step sees the changes made before it.
- Swapping without a temporary box, which loses a value.
- Mixing up `A(r, c)` (row first) with column-first order, and the two diagonals (`r = c` and `r + c = n + 1`).
- Using Python's `int()` for ACSL `int` on a negative value (use floor).

## Discussion prompts

- Why does reversing stop at the middle? What happens if it goes all the way?
- How does the direction of a shift loop decide whether values are copied or lost?
- For a grid, when does it matter whether the row loop or the column loop is outside?
- A tally uses a value as a position. What goes wrong if a value is bigger than the array?

## Differentiation

- **Junior:** the whole unit; this is Junior's Contest 3 WDTPD category.
- **Intermediate and Senior:** extra array drill only. Their Contest 3 has FSAs and Regular Expressions instead, and they met arrays in Contest 1's WDTPD unit.
- **Classroom:** optional practice (Classroom's Contest 3 categories are Boolean Algebra, FSAs and Regular Expressions, and Data Structures).
- **Elementary:** not part of the Elementary path.
- **Support:** printed rows of boxes, and a grid sheet, so students change one box at a time in pencil.
- **Extension:** write a four-line program that reverses only the even positions, then swap with a partner and trace each other's.
