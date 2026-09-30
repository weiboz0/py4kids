# Teacher Notes — Checkpoint 02: Contest 2 Practice

## Goals

This is a timed ACSL-style practice for Contest 2, taken after units 04–07.
It introduces nothing new.
It holds two full six-question papers that share four questions, plus the programming problem:

- Q1–Q2: Prefix/Infix/Postfix (an infix→postfix conversion; a prefix evaluation).
- Q3–Q4: Bit-String Flicking (a precedence evaluation; a solve-for-x).
- Q5–Q6: What Does This Program Do? – Looping (Junior), one in ACSL pseudocode.
- Q7–Q8: LISP (Intermediate and above): one `DEFUN`/`SETQ` item and one `CAR`/`CDR` composition item.
- Q9: the programming problem, "Brackets Away". The program reads a fully bracketed infix expression and prints it in postfix and in prefix: each operator is written out when its closing bracket is reached, and a stack of pieces builds the prefix.

## Pacing

ACSL's Junior, Intermediate and Senior short-answer tests are each 6 questions in 30 minutes, and the programming problem is submitted separately within the contest window (acsl.org Divisions page).

- **Short answers: 30 minutes, pencil only.**
  - Junior: Q1–Q6.
  - Intermediate and Senior: Q1–Q4 and Q7–Q8. Q5–Q6 are optional extra loop practice.
- **Programming: one session (about 60 minutes)** for Q9.
- Review the next lesson, starting from the questions most students missed.

## Common mistakes

- Q1: reordering operands or grouping `D / (E - F)` wrongly in the postfix.
- Q2: taking the two operands of a prefix operator in the wrong order.
- Q3: ignoring precedence (`NOT`, then shifts, then `AND`, then `OR`) or padding on the wrong side.
- Q4: listing the solutions out of ascending order, or missing a free bit.
- Q5–Q6: stopping a `FOR` loop early (ACSL includes the end value); using Python `int()` for ACSL `int`.
- Q7: forgetting that `DIV` can give a decimal (write `14.5`, not `14`).
- Q8: reading `CADDR` left to right, or nesting wrongly in `CONS`.
- Q9: writing an operator when its bracket opens instead of when it closes; building the prefix by reversing the postfix, which reverses the operands too (`(9-4)` would give `- 4 9`); forgetting that a single operand has no brackets.

## Discussion prompts

- Which category cost you the most points, and what will you practise before Contest 2?
- In Q4, how did you decide which bits were free?
- In Q9, at which character is each operator written into the postfix, and why does that give the right order?
- If you had five more minutes, which question would you check first, and why?

## Differentiation

- **Junior:** Q1–Q6 and Q9, a full Junior paper.
- **Intermediate and Senior:** Q1–Q4, Q7–Q8 and Q9, a full Intermediate/Senior paper; Q5–Q6 optional.
- **Classroom:** Q1–Q4 and Q7–Q8 as short-answer practice, with Q5–Q6 optional. The real Classroom test is 10 questions in 50 minutes, from Prefix/Infix/Postfix, Bit-String Flicking and LISP.
- **Elementary:** not for Elementary students. Their Contest 2 mock test is unit 04's Elementary items (Exercises 1–9), 6 questions in 30 minutes.
- **Support:** allow the precedence ladders (PIP and bit strings) and a LISP function card on a first attempt, then retake without them.
- **Extension:** write two extra Q9 test cases, one of them a case where writing each operator at its opening bracket would fail.

## Grading

- **Short answers:** 1 point each, all or nothing, exact canonical text. That means:
  - single-space tokens with `↑`
  - bit strings at full width
  - solutions in ascending order separated by `, `
  - LISP numbers integer when whole, lists `(A B C)`, `NIL`/`true`
- Each six-question paper totals 6 points: Junior Q1–Q6; Intermediate/Senior Q1–Q4 plus Q7–Q8.
- **Programming (Q9):** run the student's program on the test files in `assets/q9/` and report how many pass. ACSL scores its programming problem on its own test data, as published each season on acsl.org.
- Record points per category so students know what to review before Contest 2.
