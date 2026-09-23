# Book 1b — Year 1 Syllabus (concept-first edition)

A concept-organized, story-light edition of Year 1 Python for middle-school students with zero
programming experience.
It covers the **same 62 concepts as Book 1**, but organized around the language concepts themselves
rather than themed projects, with rigorous mastery built through **real problem-solving** — mathematics,
simple (counting-style) algorithms, turtle geometry, and puzzles.
Exercises are **mini-CP / LeetCode-style** (a precise spec, worked sample input→output, testable
solutions) with simple, accessible backgrounds, and there is no cap on how many a unit may carry.
Full design: `../docs/designs/005-book1b-concept-first.md`.

Book 1b is an independent, self-contained root — a *variant* of Book 1, not a dependent of it —
so a teacher can run either book as a complete Year-1 course.
Every unit still opens with a concrete problem that motivates the concept (a genuine puzzle with a
visible payoff, never concept drill), ships `stretch` ("Challenge") exercises, and carries teacher
notes with a 60–90 min pacing plan.

## How Book 1b differs from Book 1

- Organized around **concept families**, not themed projects; the verbose narrative is deliberately weakened.
- **Fastforward is allowed:** examples and practice may use a concept before it is formally taught, to keep
  problems real. Core teaching (`requires`) and checkpoint assessment stay strict.
- **Checkpoints are kept**; the themed capstones are dropped in favour of per-unit problem sets and one
  non-themed end-of-book **Algorithm Challenge** — the visible year-end goal students work toward.

## Roadmap (concept-family units)

This edition is in buildout; the shipped-entries table appears below as units land (Unit 01 first).
The planned progression, each unit introducing its concept family exactly once in an order that keeps
`requires` closure strict:

1. **Unit 01 — Output & Variables:** printing, comments, variables, naming, input, string joining, f-strings, reading errors.
2. **Unit 02 — Numbers & Arithmetic:** integers, floats, arithmetic (`+ - * / // %`), type conversion, booleans, comparison.
3. **Unit 03 — Decisions:** logical operators, `if`/`elif`/`else`, nested conditionals.
4. **Unit 04 — Loops & Counting:** `while`, `break`, counters, accumulators, and the counting techniques (sentinel loop, running total, count-by-condition).
5. **Unit 05 — For & Range:** `for` loops, `range`, nested loops.
6. **Unit 06 — Turtle Geometry:** importing modules (`import turtle`), turtle movement and drawing — angles as math.
7. **Unit 07 — Functions:** defining functions, parameters, return values, scope, built-in functions.
8. **Unit 08 — Randomness:** the `random` module — dice, coins, and simulation.
9. **Unit 09 — Strings:** indexing, slicing, string methods, membership, transform-each, linear search.
10. **Unit 10 — Lists:** creating/indexing/appending/looping/sorting lists, find-the-best, filter.
11. **Unit 11 — Dictionaries:** creating, looking up, and looping over dictionaries.
12. **Unit 12 — Files:** reading, writing, and the `with` statement.
13. **Unit 13 — Objects:** classes, `__init__`, attributes, and methods.

Checkpoints follow Units 03, 05, 08, and 11, with a mandatory checkpoint after Unit 13.
The **Algorithm Challenge** (a non-themed integrative problem set) closes the year.

## Shipped so far

| entry | kind | lessons | the hook |
|---|---|---|---|
| `unit-01-output-and-variables` | unit | 3 | Fill a club "fact card" from a few saved values — output, variables, and your first programs. |
| `unit-02-numbers-and-arithmetic` | unit | 3 | Make the computer do the math — integers, floats, `//`/`%`, conversions, and True/False comparisons. |
| `unit-03-decisions` | unit | 3 | Teach the computer to choose — `if`/`elif`/`else` and `and`/`or`/`not` on leap years, grades, and more. |
| `checkpoint-01-foundations` | checkpoint | 0.5 | Prove output, numbers, and decisions on a mixed problem set. |
| `unit-04-loops-and-counting` | unit | 3 | Teach the computer to repeat and count — `while`, counters, accumulators, and stop-when-done. |
| `unit-05-for-and-range` | unit | 3 | Count with `for`/`range` and stack loops for tables and triangles. |
| `checkpoint-02-loops` | checkpoint | 0.5 | Prove `while`, `for`/`range`, and counting on a mixed loop problem set. |
| `unit-06-turtle-geometry` | unit | 3 | Draw with code — `import turtle`, movement, and polygons as angles (`360 / n`) with loops. |
| `unit-07-functions` | unit | 3 | Package logic into functions — `def`, parameters, `return`, scope, and Python's built-in tools. |
| `unit-08-randomness` | unit | 3 | Roll dice and simulate — the `random` module, seeding, and Monte-Carlo estimates. |
| `checkpoint-03-functions-and-randomness` | checkpoint | 0.5 | Prove functions and randomness on a mixed problem set. |

## Rules this syllabus is bound by

- Prereq closure over `requires` (strict): a unit's core teaching never depends on a concept introduced later.
- Fastforward (relaxed): examples/practice may reach forward to any catalog concept.
- Checkpoints assess only concepts already introduced; they introduce nothing.
- Stretch exercises may preview, but core paths never depend on stretch content.
- Docs use semantic line breaks (one sentence per line).
