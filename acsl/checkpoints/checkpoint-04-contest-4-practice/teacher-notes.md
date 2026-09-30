# Teacher Notes — Checkpoint 04: Contest 4 Practice

## Goals

This is a timed ACSL-style practice for Contest 4, taken after units 12–15.
It introduces nothing new, and it is the book's last practice paper.
It holds two full six-question papers that share four questions, plus the programming problem:

- Q1–Q2: Graph Theory (the cycles of a directed graph, each counted once; walks of length 3 from an adjacency matrix).
- Q3–Q4: Digital Electronics (the TRUE triples of a circuit; a circuit simplified to its sum of products).
- Q5–Q6: What Does This Program Do? – Strings (Junior), one in ACSL pseudocode with ACSL's substrings and one in Python.
- Q7–Q8: Assembly Language (Intermediate and above): a `DIV` that rounds toward zero, and a `READ` loop with a branch on the boundary.
- Q9: the programming problem, "Friend of a Friend". For each vertex of an undirected graph, the program lists the vertices it is not joined to that share at least one neighbour with it, with the count of shared neighbours (an entry of `M^2`).

## Pacing

ACSL's Junior, Intermediate and Senior short-answer tests are each 6 questions in 30 minutes, and the programming problem is submitted separately within the contest window (acsl.org Divisions page).

- **Short answers: 30 minutes, pencil only.**
  - Junior: Q1–Q6.
  - Intermediate and Senior: Q1–Q4 and Q7–Q8. Q5–Q6 are optional extra string practice.
- **Programming: one session (about 60 minutes)** for Q9, on the Junior, Intermediate and Senior paths only.
- Review the next lesson, starting from the questions most students missed.

## Common mistakes

- Q1: counting a cycle twice (once from each start) or against the edge direction; at Junior level and above each cycle counts once.
- Q2: counting simple paths instead of walks, or multiplying the matrix entry by entry.
- Q3: missing a row, or listing the triples out of ascending order.
- Q4: stopping before the expression is fully simplified, or writing the terms out of canonical order.
- Q5: reading ACSL's `S[j:]` as a Python slice (it is the last j characters) or `S[j:j + 1]` as one character (it is two).
- Q6: an off-by-one in the letter shift.
- Q7: rounding `DIV` down instead of toward zero (`-23` ÷ `4` is `-5`).
- Q8: treating `BG` as "greater than or equal"; the 10 is not greater than 10.
- Q9: suggesting a vertex already joined to X, or X itself; printing nothing instead of `NONE`.

## Discussion prompts

- Which category cost you the most points, and what will you practise before Contest 4?
- In Q2, how can you check a matrix answer by listing the walks?
- In Q7, where else does "toward zero" versus "down" change an answer?
- Looking back over the season, which ACSL rule surprised you most?

## Differentiation

- **Junior:** Q1–Q6 and Q9, a full Junior paper.
- **Intermediate and Senior:** Q1–Q4, Q7–Q8 and Q9, a full Intermediate/Senior paper; Q5–Q6 optional.
- **Classroom:** Q1–Q4 and Q7–Q8 as short-answer practice, with Q5–Q6 optional. The real Classroom test is 10 questions in 50 minutes (acsl.org Divisions page), from Graph Theory, Digital Electronics and Assembly Language.
- **Elementary:** not for Elementary students. Their Contest 4 mock test is unit 12's Exercises 1–6, 6 questions in 30 minutes.
- **Support:** allow a blank matrix grid, a gate truth-table card and a trace table on a first attempt, then retake without them.
- **Extension:** write two extra Q9 test cases, one of them a graph where some vertex should print `NONE` although it has neighbours.

## Grading

- **Short answers:** 1 point each, all or nothing, exact canonical text. That means:
  - counts and location values as bare integers
  - triples as `(A,B,C)` in ascending binary order, separated by `, `
  - sums of products in the book's notation and term order
  - string outputs and printed values exactly as printed, on one line
- Each six-question paper totals 6 points: Junior Q1–Q6; Intermediate/Senior Q1–Q4 plus Q7–Q8.
- **Programming (Q9):** run the student's program on the test files in `assets/q9/` and report how many pass. ACSL scores its programming problem on its own test data, as published each season on acsl.org.
- Record points per category.

## Closing the season

This is the last practice checkpoint in the book.
Before the final contest, have each student pick their two weakest categories from the four practice papers and redo that unit's Challenges.
After the season, the book can be restarted from Foundations with the next year's category list (`acsl/curriculum/season.yaml`).
