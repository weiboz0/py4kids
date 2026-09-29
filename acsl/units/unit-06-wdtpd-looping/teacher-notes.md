# Teacher Notes — Unit 06: What Does This Program Do? – Looping

## Goals

Students learn Junior's third Contest 2 category: tracing programs with loops and writing their exact one-line output.
By the end they can:

- translate ACSL `FOR … TO … STEP` loops, which include their end value, to Python `range`, including negative steps ("one past the end in the direction of travel");
- count the passes of a loop before tracing it, and spot loops that run zero times;
- trace `WHILE` loops, which test only at the top, and see why a variable can overshoot the limit;
- trace nested loops whose inner bounds depend on the outer counter;
- follow counters, accumulators and a running maximum, including `>` versus `>=` ties;
- use `%`, `int` (the greatest integer, i.e. floor) and `abs` inside loops, and keep ACSL `int` distinct from Python's `int()` for negative numbers.

The hook is a bouncing ball: a `WHILE` loop shrinks the bounce height and adds up the distance. The answer for h = 100 is `5 372`. Lesson 1 checks it in Python and Lesson 2 traces it by hand.

Strings and arrays are deliberately left out: Junior meets them in Contests 4 and 3.

## Pacing

Budget: three lessons of 60–90 minutes in the Contest 2 window.

- **Lesson 1.**
  - `FOR` loops and their pass count, and the negative-`STEP` translation.
  - `WHILE` loops.
  - The `int`-below-zero warning, then the hook in Python.
- **Lesson 2.**
  - Trace tables for the hook.
  - Counters, accumulators and running maxima, digit loops with `%` and `int`, and `abs`.
- **Lesson 3.**
  - Nested loops that grow, shrink or never start.
  - A `WHILE` inside a `FOR`, with variables reset each pass.
- **Exercises:** 19 items, all Junior (16 short answers, 3 predict-then-verify programs); 18–19 are Challenges.

**60-minute cut:** keep `FOR`/`WHILE` tracing and trace tables; move the nested-loop lesson to homework reading plus Exercises 12–13.

## Common mistakes

- Stopping a `FOR` loop one pass early; ACSL includes the end value.
- Translating a negative `STEP` with the wrong `range` end: `FOR i = 10 TO 1 STEP -3` is `range(10, 0, -3)`.
- Testing a `WHILE` condition in the middle of the body instead of only at the top.
- Using Python's `int()` for ACSL `int` on a negative value (use floor).
- `>` versus `>=` in a running maximum: which of two equal values wins?
- Not resetting an inner accumulator when the outer loop repeats.

## Discussion prompts

- How can you know how many times a loop runs before tracing it?
- Why is a trace table safer than tracing "in your head"?
- When is a `WHILE` loop more natural than a `FOR` loop?
- What changes in a running maximum if you use `>=` instead of `>`?

## Differentiation

- **Junior:** the whole unit; this is Junior's Contest 2 WDTPD category.
- **Intermediate and Senior:** extra loop drill only. Their Contest 2 has LISP instead, and they met every construct in Contest 1's WDTPD unit.
- **Classroom:** optional practice (Classroom's Contest 2 categories are Prefix/Infix/Postfix, Bit-String Flicking and LISP).
- **Elementary:** not part of the Elementary path.
- **Support:** a blank trace-table sheet with one column per variable, and a "passes" box to fill in before tracing.
- **Extension:** write a loop whose output changes if `>` is swapped for `>=`, and swap it with a partner.
