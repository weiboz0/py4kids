# Teacher Notes — Unit 11: FSAs and Regular Expressions

## Goals

Students learn the Intermediate and Senior third Contest 3 category.
By the end they can:

- read a finite state automaton as a transition table (initial state `→`, final states marked, `—` for no move) or a text diagram, and run it by hand on a string;
- say which strings an FSA accepts, including the empty string `λ`, and that a missing move rejects;
- read regular expressions built from concatenation, union (`U` or `|`) and star, with the precedence star, then concatenation, then union;
- write a regular expression for a small FSA, and test two expressions for equality with the identities or disprove it with one counterexample string;
- read ACSL's extended syntax: `?`, `+`, `.`, `[abc]`, `[^abc]` and `[a-z]`;
- write a Python FSA simulator (a dict keyed by `(state, symbol)` tuples) and a recursive matcher for simple patterns, without Python's `re` module.

The hook is "The Knock Code": an FSA with buttons `k` and `t`. Students test five codes and describe every opening code in one line. Lesson 2 writes it as `kk*t(kk*t)*`, and Lesson 3 as `(k+t)+`.

## Pacing

Budget: three lessons of 60–90 minutes in the Contest 3 window.

- **Lesson 1.**
  - FSAs as tables and diagrams; running one by hand.
  - Missing moves, and when `λ` is accepted.
  - The FSA in Python.
- **Lesson 2.**
  - The three operations and their precedence; the wiki's `00*1*1U11*0*0` sample.
  - From an FSA to an expression (students write their own).
  - The 8 identities, disproof by counterexample, and counting accepted strings in Python.
- **Lesson 3.**
  - The extended syntax, with the wiki's `[A-D]*[a-d]*[0-9]` and `Hi?g+h+[^a-ceiou]` samples.
  - The recursive matcher, and back to the door.
- **Exercises:** 18 items. Exercises 1–12 are Intermediate (including two programs, 4 and 12), and 13–18 are Senior (17–18 are Challenges; 17 is a full matcher).

**60-minute cut:** keep FSA tracing, precedence and the extended syntax; set the identities and the matcher as reading plus Exercises 8–9.

## Common mistakes

- Accepting a string because it passes through a final state; it must **end** in one.
- Forgetting that a missing move rejects the whole string.
- Reading `a|bc*` as `(a|b)c*`: star binds first, then concatenation, then union.
- Reading `ab*` as `(ab)*`.
- Treating `+` in the extended syntax as union; it means "one or more".
- Reading `[^abc]` as "not the string abc"; it is one character that is not `a`, `b` or `c`.
- Declaring two expressions equal after trying a few examples; one counterexample settles "not equal", but "equal" needs an identity or a complete argument.
- Forgetting `λ` when listing accepted strings.

## Discussion prompts

- What does each state of an FSA "remember" about the string so far?
- Why does one counterexample prove two expressions differ, while no number of examples proves them equal?
- Where do you meet patterns like `[A-Z][a-z]+` outside contests (search boxes, form checks)?
- The Exercise 13 FSA accepts binary numbers divisible by 3. Why do three states suffice?

## Differentiation

- **Intermediate and Senior:** the whole unit; this is their Contest 3 FSA category.
- **Junior:** not part of the Junior path (Junior's Contest 3 has What Does This Program Do? – Arrays instead). Keen Juniors can try Lesson 1.
- **Classroom:** Classroom's Contest 3 includes FSAs and Regular Expressions, so do the short-answer items at Intermediate level.
- **Elementary:** not part of the Elementary path.
- **Support:** a printed table with a pointer students move by hand, and a card listing the precedence and the extended-syntax symbols.
- **Extension:** design an FSA for binary numbers divisible by 5, and write it as a transition table for the Exercise 4 simulator.

## Grading and answer forms

- Short answers here are option letters in listed order (`A, C, D`), a count, or a state name (Exercise 2, written as the table names it, such as `q1`).
- The book judges regular-expression answers as option choices. Real ACSL papers also ask for a free-text expression ("write a regular expression for this FSA") and accept any correct one, so keep asking students to write their own and check them in pairs.
