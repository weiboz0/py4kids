# Contest Python: ACSL — Syllabus

*From Elementary to Senior, one contest at a time.*

This book prepares you for the American Computer Science League (ACSL), in every division.
It follows the ACSL season: one part per contest, in the order the contests happen.
Study each part in the weeks before its contest, and you are ready when the contest window opens.
Python comes from *Python by Projects* (or *Python, Concept by Concept*); everything else is taught here.

## How the book is organized

- **Contest 0 — Foundations** comes first.
  It teaches what every programming problem needs: how ACSL works, reading contest input, tuples, and complete search.
- **Contests 1–4** each have one unit per ACSL category of that contest, in the official order.
  Each part ends with a **Contest N practice** checkpoint in the ACSL format: short-answer questions plus one programming problem.
- Every exercise and question is one of two kinds:
  - **short-answer:** one exact answer, worked out by hand (like the ACSL written test);
  - **programming:** a Python program that reads the input and prints the exact output.
- Every item carries a **division mark**: the lowest division that is tested on it.

## Following the season

The 2026–27 contest windows (acsl.org Schedule):

| Contest | Window | Study in the book |
|---|---|---|
| Contest 1 | Oct 19, 2026 – Jan 10, 2027 | Foundations, then Contest 1 |
| Contest 2 | Jan 4 – Feb 28, 2027 | Contest 2 |
| Contest 3 | Feb 1 – Apr 11, 2027 | Contest 3 |
| Contest 4 | Mar 1 – May 23, 2027 | Contest 4 |

Start Foundations as soon as the school year begins, so Contest 1 has the whole autumn.
Finish each part a week or two before you plan to sit its contest, and do the practice checkpoint last.

## Division paths

The divisions form a ladder: Elementary, then Junior, then Intermediate, then Senior.
Follow your division's path, and do every item marked at your division **or below**.

- **Elementary:** no programming. Skip Foundations and start at Contest 1's Computer Number Systems unit.
  In each contest, study the opening Elementary section of that contest's Elementary category unit
  (Number Systems, Prefix/Infix/Postfix, Boolean Algebra, Graph Theory).
- **Junior:** Foundations, then every unit of each contest part except the Intermediate/Senior-only units
  (LISP, FSAs and Regular Expressions, Assembly Language).
  Each contest's practice checkpoint includes a programming problem.
- **Intermediate and Senior:** Foundations, then every unit, including the Intermediate/Senior-only units.
  Contest 1's What Does This Program Do? unit has an Intermediate section on loops, arrays and strings, because Intermediate and Senior Contest 1 tests every construct.
- **Classroom:** no programming. Do every short-answer item marked Junior or Intermediate in the contest's categories.

## Season map

The whole season is in this book: the Foundations unit, then each contest's units followed by its practice checkpoint.

### Contest 0 — Foundations

| entry | kind | lessons | focus |
|-------|------|---------|-------|
| `unit-00-acsl-foundations` | unit | 3 | how ACSL works; reading contest input; tuples and complete search |

### Contest 1

| entry | kind | lessons | focus |
|-------|------|---------|-------|
| `unit-01-computer-number-systems` | unit | 3 | bases 2/8/10/16, conversions, arithmetic in a base, hex colours, fractions; opens with the Elementary section |
| `unit-02-recursive-functions` | unit | 3 | evaluating recursive definitions (call tables), multiple and indirect recursion, recursion in Python |
| `unit-03-wdtpd-branching` | unit | 3 | ACSL pseudocode, tracing branches; Intermediate section on loops, arrays, 2D grids and strings |
| `checkpoint-01-contest-1-practice` | checkpoint | 0.5 | timed Contest 1 practice: 6 short answers + 1 Intermediate trace + 1 programming problem |

### Contest 2

| entry | kind | lessons | focus |
|-------|------|---------|-------|
| `unit-04-prefix-infix-postfix` | unit | 3 | evaluating and converting prefix/infix/postfix, stack evaluation; opens with the Elementary section |
| `unit-05-bit-string-flicking` | unit | 3 | NOT/AND/OR/XOR, shifts and circulates, ACSL precedence, solving for x |
| `unit-06-wdtpd-looping` | unit | 3 | tracing FOR/WHILE and nested loops (Junior) |
| `unit-07-lisp` | unit | 3 | ACSL LISP: lists, CAR/CDR/CONS, arithmetic, SETQ/EVAL, DEFUN (Intermediate and Senior) |
| `checkpoint-02-contest-2-practice` | checkpoint | 0.5 | timed Contest 2 practice: Junior and Intermediate/Senior six-question papers + 1 programming problem |

### Contest 3

| entry | kind | lessons | focus |
|-------|------|---------|-------|
| `unit-08-boolean-algebra` | unit | 3 | NOT/AND/OR/XOR/XNOR, the laws, simplifying to a sum of products, truth tables and satisfying tuples; opens with the Elementary section |
| `unit-09-data-structures` | unit | 3 | stacks and queues, binary search trees (depths, path lengths, traversals, deletion), min- and max-heaps |
| `unit-10-wdtpd-arrays` | unit | 3 | tracing 1D arrays and 2D grids in ACSL pseudocode and Python (Junior) |
| `unit-11-fsas-regular-expressions` | unit | 3 | finite state automata, regular expressions and their identities, extended syntax (Intermediate and Senior) |
| `checkpoint-03-contest-3-practice` | checkpoint | 0.5 | timed Contest 3 practice: Junior and Intermediate/Senior six-question papers + 1 programming problem |

### Contest 4

| entry | kind | lessons | focus |
|-------|------|---------|-------|
| `unit-12-graph-theory` | unit | 3 | vertices and edges, paths and cycles, traversability, adjacency matrices and M^p, components and trees; opens with the Elementary section |
| `unit-13-digital-electronics` | unit | 3 | the eight gates, circuits as netlists and expressions, tuples and counts, simplifying, NAND/NOR |
| `unit-14-wdtpd-strings` | unit | 3 | tracing string programs with ACSL's substring rules (Junior) |
| `unit-15-assembly-language` | unit | 3 | ACSL assembly: the accumulator, memory, branches and loops, READ/PRINT (Intermediate and Senior) |
| `checkpoint-04-contest-4-practice` | checkpoint | 0.5 | timed Contest 4 practice: Junior and Intermediate/Senior six-question papers + 1 programming problem |

The category lists come from the acsl.org Study Materials page (retrieved 2026-09-29).
ACSL revises them from year to year; the book follows the current list.
