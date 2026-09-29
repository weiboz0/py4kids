# Teacher Notes — Unit 08: Boolean Algebra

## Goals

Students learn ACSL's first Contest 3 category, which every division takes.
By the end they can:

- evaluate expressions and statements with NOT, AND and OR, written in the book's notation (`~`, `*`, `+`, with `1` TRUE and `0` FALSE) and the precedence NOT, then AND, then OR;
- build truth tables, and write a truth table's result column in the book's form (rows `00, 01, 10, 11`, …);
- simplify with the laws (identity, annihilator, complement, idempotent, absorption, distributive, De Morgan, double negation) down to a sum of products;
- list or count the ordered pairs or triples that make an expression true or false, and test two expressions for equivalence;
- (Junior and above) use XOR `⊕` and XNOR `⊙` with their identities, work with three variables, and read the wiki's overbar and juxtaposition notation on real papers;
- write Python truth-table loops with `and`, `or`, `not`, `!=` (XOR) and `==` (XNOR) that list or count the solutions.

The hook is "The Clubhouse Door", with no code: the founder's rule `~(~A + B) + A * B` turns out to mean just `A`.

## Pacing

Budget: three lessons of 60–90 minutes, early in the Contest 3 window (Feb 1 – Apr 11, 2027).

- **Lesson 1, the Elementary section.** It contains no code for students to run.
  - Two variables, the symbols `~ * +`, and the order of operations.
  - Truth tables, the laws, simplifying, equivalence and tautologies; then back to the door.
  - Exercises 1–6 are the Elementary mock test: 6 questions in 30 minutes, one per skill (evaluate, truth table, simplify, count pairs, equivalence) plus a second simplify. Exercises 7–9 are extra Elementary practice.
- **Lesson 2, Junior and above.**
  - Three variables, XOR and XNOR, and the full precedence (`~`; `*`; `⊕` and `⊙`; `+`).
  - Reading a real paper: overbars and juxtaposition translated to the book's notation, with both wiki samples.
  - The full list of laws, finding every solution, and the `l1.py` self-checker.
  - The Intermediate section: nested NOTs and counting over four variables.
- **Lesson 3, Junior and above.**
  - Boolean algebra in Python: listing every solution, and reading an expression from the input.
  - A warning that Python's precedence for `!=` and `==` differs from ACSL's XOR and XNOR.
- **Exercises:** 27 items. Exercises 1–9 are Elementary; 10–19 are Junior (programs 18 and 19); 20–25 are Intermediate (program 25); and 26–27 are Senior Challenges (27 is a program).

**60-minute cut:** keep truth tables, De Morgan and simplifying; set XOR/XNOR and the Python lesson as reading plus Exercises 14 and 18.

## Common mistakes

- Doing OR before AND: `A + B * C` is `A + (B * C)`.
- Breaking De Morgan: `~(A + B)` is `~A * ~B`, not `~A + ~B`.
- Stopping before the expression is fully simplified (absorption: `A + A * B` is `A`).
- Writing a correct simplification in a different order from the book's canonical form (literals in variable order, `X` before `~X`, shorter terms first).
- Missing rows when listing solutions, or listing them out of ascending order.
- Treating `⊕` as OR: XOR is true only when exactly one side is true.
- In Python, writing `a != b or c` and expecting ACSL's precedence; bracket it.

## Discussion prompts

- Why does a truth table settle whether two expressions are equal, even when the algebra is hard?
- De Morgan's laws in words: "not (rain or snow)" means what?
- The book writes answers as sums of products, but ACSL says "the fewest operators". When would `~(A + B)` be shorter than the book's `~A * ~B`?
- How many rows does a truth table with 4 variables have? With 10?

## Differentiation

- **Elementary:** Lesson 1 and Exercises 1–9 are the whole Contest 3 path; Exercises 1–6 are the mock test.
- **Junior:** Lessons 1–3 without the Intermediate section; Exercises 1–19.
- **Intermediate and Senior:** everything, including the Challenges.
- **Classroom:** Classroom's Contest 3 includes Boolean Algebra, so do the short-answer items at Junior and Intermediate level.
- **Support:** a printed card with the laws and the precedence ladder, and blank truth-table sheets for 2 and 3 variables.
- **Extension:** design a 3-variable expression with two different minimal sums of products, and explain why the book's "unique answer" rule would reject it as a question.

## Answer forms

- Option labels in Exercises 5 and 8 are the letters `A`–`E`, the same letters as the variables. Remind students the labels are only names for the options.
- ACSL papers accept pairs in any order and simplifications in any equivalent form with the fewest operators; the book's fixed forms only make answers easy to check.
