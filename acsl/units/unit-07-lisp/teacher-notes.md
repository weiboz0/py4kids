# Teacher Notes — Unit 07: LISP

## Goals

Students on the Intermediate and Senior paths learn their third Contest 2 category.
By the end they can:

- read atoms and lists, `NIL` (the same as `()`), and quote `'`, and evaluate calls from the innermost brackets outward;
- evaluate ACSL's LISP functions:
  - arithmetic: variadic `ADD` and `MULT`, `SUB`, `DIV`, `SQUARE`, `EXP`, and the symbol forms `+ - * /`
  - `EQ`, `POS`, `NEG` and `ATOM`, which return `true` or `NIL`
  - list functions: `CAR`, `CDR` (`CDR` of a one-element list is `NIL`), the compositions `CAAR CADR CDAR CDDR CADDR CDDAR`, `CONS` and `REVERSE`
  - variables and evaluation: `SET` (quoted first argument), `SETQ` and `EVAL`
  - `DEF` and `DEFUN`
- trace a multi-statement LISP program with a variable table;
- write Python versions of `CAR`, `CDR`, `CONS` and `REVERSE` on lists, built with loops and `append`.

Answers follow ACSL's forms: numbers as integers when whole, otherwise a terminating decimal; lists as `(A B C)`; `NIL`; `true`.
Anything outside ACSL's set (`COND`, `IF`, `LIST`, `APPEND` and so on) is not taught.

The hook, "The Shuffled Shopping List", uses a `SETQ`, a `DEF` of `SWAP`, and a `CONS` of `CAR` and `CDR`. Its value is `(APPLE BREAD MILK JAM)`, and Lesson 3 solves it.

## Pacing

Budget: three lessons of 60–90 minutes in the Contest 2 window.

- **Lesson 1.**
  - Atoms and lists, inside-out evaluation, and the arithmetic functions.
  - `DIV` answers (a whole number when whole).
  - `EQ`, `POS` and `NEG`; the book writes `true` where some LISP systems print `T`.
- **Lesson 2.**
  - Quote, `CAR`/`CDR`, `CONS` (the second argument is a list; a list as the first argument nests), `REVERSE` at the top level only.
  - The composition table, read right to left, and `ATOM`.
  - Python list versions.
- **Lesson 3.**
  - `SETQ` versus `SET`, quote versus no quote, and `EVAL`.
  - `DEF`/`DEFUN` with functions calling functions.
  - Solve the hook.
- **Exercises:** 1–16 Intermediate (including three programs), 17–21 Senior, with 20–21 as Challenges.

**60-minute cut:** keep arithmetic, `CAR`/`CDR`/`CONS` and `SETQ`; move `EVAL`/`SET` and the composition drills to homework.

## Common mistakes

- Evaluating outside-in instead of from the innermost brackets.
- Forgetting the quote: `(CAR L)` uses the value of `L`, while `(CAR 'L)` is an error.
- Reading a composition left to right: `CADR` is `CAR` of `CDR`, applied right to left.
- `CONS` with a list first argument: it nests, `(CONS '(1 2) '(3))` is `((1 2) 3)`.
- `REVERSE` reversing inner lists too; it only turns the top level round.
- Writing `13.50` or `-2.0` instead of the canonical `13.5` and `-2`.

## Discussion prompts

- Why does LISP write the function first, inside the brackets?
- How is `CONS` the opposite of `CAR` and `CDR`?
- When does quoting matter, and what happens without it?
- How are LISP lists like Python lists, and how are they different?

## Differentiation

- **Intermediate and Senior:** the whole unit; LISP is their Contest 2 category.
- **Junior:** not part of the Junior path (Junior's Contest 2 has WDTPD – Looping instead); an optional preview for strong Juniors.
- **Classroom:** the short-answer items; LISP is one of Classroom's Contest 2 categories.
- **Elementary:** not part of the Elementary path.
- **Support:** a printed function card (each function, its arguments, and an example) and a box-and-pointer sketch of a list.
- **Extension:** use `DEFUN` to define a function that rotates a list, then compose it with itself.
