# Teacher Notes — Checkpoint 03: Contest 3 Practice

## Goals

This is a timed ACSL-style practice for Contest 3, taken after units 08–11.
It introduces nothing new.
It holds two full six-question papers that share four questions, plus the programming problem:

- Q1–Q2: Boolean Algebra (a simplification to a sum of products; the triples that make an expression true, with XOR).
- Q3–Q4: Data Structures (a queue script of pushes and pops; the internal path length of a BST with duplicates).
- Q5–Q6: What Does This Program Do? – Arrays (Junior), one in Python and one in ACSL pseudocode on a 4×4 grid.
- Q7–Q8: FSAs and Regular Expressions (Intermediate and above): one FSA table item and one regular-expression equivalence item, both as option choices.
- Q9: the programming problem, "The Counting Line". The program keeps the players in a queue (a list and a `head` index, as in Unit 9), moves `K − 1` players from the front to the back each round, and prints the order in which the players leave.

## Pacing

ACSL's Junior, Intermediate and Senior short-answer tests are each 6 questions in 30 minutes, and the programming problem is submitted separately within the contest window (acsl.org Divisions page).

- **Short answers: 30 minutes, pencil only.**
  - Junior: Q1–Q6.
  - Intermediate and Senior: Q1–Q4 and Q7–Q8. Q5–Q6 are optional extra array practice.
- **Programming: one session (about 60 minutes)** for Q9, on the Junior, Intermediate and Senior paths only.
- Review the next lesson, starting from the questions most students missed.

## Common mistakes

- Q1: keeping the term `A * ~B`, which the other two terms already cover, or writing the terms out of the book's canonical order.
- Q2: reading `⊕` with the wrong precedence (it binds after `*` and before `+`), or missing a row of the truth table.
- Q3: treating the queue as a stack (last in, first out). The same script run as a stack gives a different value.
- Q4: sending a duplicate letter to the right, or starting the depth count at 1 instead of 0.
- Q5–Q6: tracing a pass with the array as it was at the start; mixing up the main diagonal and the anti-diagonal.
- Q7: forgetting that a string must end in a final state, not just pass through one.
- Q8: accepting an expression that matches the examples tried but not every string (test short strings, including `λ`).
- Q9: moving `K` players to the back instead of `K − 1`; starting each round again from player 1 instead of from the front of the queue; a program that breaks when `K` is larger than the number of players left.

## Discussion prompts

- Which category cost you the most points, and what will you practise before Contest 3?
- In Q3, how did you keep track of the front of the queue?
- In Q8, what is the quickest string that proves two expressions are different?
- In Q9, what happens when `K` is larger than the number of players left, and which test case checks it?

## Differentiation

- **Junior:** Q1–Q6 and Q9, a full Junior paper.
- **Intermediate and Senior:** Q1–Q4, Q7–Q8 and Q9, a full Intermediate/Senior paper; Q5–Q6 optional.
- **Classroom:** Q1–Q4 and Q7–Q8 as short-answer practice, with Q5–Q6 optional. The real Classroom test is 10 questions in 50 minutes (acsl.org Divisions page), from Boolean Algebra, FSAs and Regular Expressions, and Data Structures.
- **Elementary:** not for Elementary students. Their Contest 3 mock test is unit 08's Exercises 1–6, 6 questions in 30 minutes.
- **Support:** allow the precedence ladder, a blank truth-table sheet and a blank tree sheet on a first attempt, then retake without them.
- **Extension:** write two extra Q9 test cases, one of them a case where moving `K` players to the back instead of `K − 1` gives a different answer.

## Grading

- **Short answers:** 1 point each, all or nothing, exact canonical text. That means:
  - sums of products in the book's notation and term order
  - triples as `(A,B,C)` in ascending binary order, separated by `, `
  - values and path lengths as bare integers
  - option letters in listed order, separated by `, `
  - array outputs exactly as printed, on one line
- Each six-question paper totals 6 points: Junior Q1–Q6; Intermediate/Senior Q1–Q4 plus Q7–Q8.
- On a real paper, a simplification may be accepted in any equivalent form with the fewest operators; the book's canonical form only makes the practice easy to mark.
- **Programming (Q9):** run the student's program on the test files in `assets/q9/` and report how many pass. ACSL scores its programming problem on its own test data, as published each season on acsl.org.
- Record points per category so students know what to review before Contest 3.
