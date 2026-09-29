# Design 008 — Book series naming and the contest-book split

**Status:** accepted (user decisions, 2026-09-28).
**Supersedes:** the `book1` / `book1b` / `book2` naming in `books.yaml` and design 000 §1 (history keeps the old ids).

## 1. Purpose

py4kids now holds two introductions to Python and one beginning competitive-programming book.
The names `book1`, `book1b` and `book2` say nothing about what each book is.
Book 2 also mixes two different contests: USACO and ACSL.
This design gives every book a proper id and title, and splits the contest book in two.

## 2. Decisions

- **D1 — Level-named ids and a "Python / Contest" title series** (user: "Level-named ids", "Python / Contest series").

  | id (folder) | Title | Was |
  |---|---|---|
  | `python-projects` | Python by Projects | `book1` |
  | `python-concepts` | Python, Concept by Concept | `book1b` |
  | `usaco-bronze` | Contest Python: USACO Bronze | `book2` (USACO part) |
  | `acsl` | Contest Python: ACSL | new, seeded from `book2`'s ACSL units |

  - The USACO id names its level, so later books fit beside it (`usaco-silver`, …); the USACO book covers the beginning concepts only (user: "usaco book just covers beginning concepts, we may have more advanced books").
  - **ACSL is one book for every division** (user, 2026-09-28: "for ACSL, we will cover all levels in one book, but mark concepts by level"): Elementary, Junior, Intermediate and Senior topics live together.
    - Each concept, unit and exercise carries the lowest ACSL division that tests it (a `acsl-level:` manifest field and a printed level badge), so a student can follow one division's path through the book.
    - The folder is `acsl`, not `acsl-junior`.
  - `books.yaml` carries each book's `title` and `subtitle`.
  - Every student-facing mention of a book *as a book* (syllabi, front matter, PDF title pages) uses the title, never the id.
  - Folder paths and PDF **file names** use the id (`output/<id>/<id>-<edition>.pdf`): deterministic, lowercase, and no slugging of titles with punctuation.
  - The old "Book 1b" wording on student pages goes away.
- **D2 — Folders are renamed, not aliased** (user: "option 2 … with proper naming").
  - `git mv` keeps history. Tools, tests, scripts, CI and `output/<id>/` use the new ids.
  - Historical records (merged plans, design records, review verdicts, ERRATA entries) keep the old ids. This table is the mapping.
- **D3 — The contest book splits into USACO Bronze and ACSL, and ACSL grows** (user: "Split + grow ACSL").
  - **`usaco-bronze`** keeps the algorithm units (input, complexity, sets/tuples/sorting, searching and complete search, greedy, simulation, prefix sums, recursion and backtracking, grids and graphs, two pointers), the four mock contests and the capstone. Units are renumbered where gaps appear.
  - **`acsl`** takes Boolean logic, number systems and bitwise, stacks/queues/postfix, and binary trees, each marked with its ACSL division(s).
    - It then gains units for the ACSL categories `book2` never covered, across all divisions: bit-string flicking, recursive functions, What Does This Program Do, graph theory, data structures, prefix/infix/postfix, digital electronics, LISP, regular expressions and FSAs, assembly, and the rest of the current ACSL category list.
    - Each is marked by division. They come in later plans, one or two units per plan, with the usual gates.
  - **Each contest book is independently complete** on top of the Python fundamentals (`depends_on: [python-projects]`; `python-concepts` is a `variant_of` it and teaches the same 62 concept ids, so either intro book satisfies it).
    - A concept both contest books need is **taught in each**; duplication across the two contest books is allowed. For example, `deque` stays in USACO Bronze for BFS, stacks and queues are also taught in ACSL, and `str-split` input parsing and complete search are re-taught in ACSL where its units need them.
    - **Sharing rule.** Concept ids are one global namespace, and `global_concept_uniqueness_findings` today lets two books define the same id only when one is a `variant_of` the other. Plan 092 adds a second exemption: books declared **`peers`** in `books.yaml` (`usaco-bronze: peers: [acsl]` and the reverse, symmetric and validated) may each *introduce* a shared id.
      - Each book teaches the concept completely in its own units.
      - The registry entry (name, category, and `kind`, including whether it is absent) must be identical in both books' `concepts.yaml`; the check fails on drift.
      - Neither book may `require` an id that only its peer introduces.
      - Plan 092 implements and tests this exemption, then passes `prereq-check` and `coverage-check` for each contest book on its own. No contest book imports from the other.
- **D4 — Order of work.**
  1. Plan 091: rename ids and folders and add titles (no content moves).
  2. Plan 092: split `usaco-bronze` / `acsl` (with the level-marking scheme) (move the four ACSL units; renumber; checkpoint and mock-contest questions follow their topic's book; syllabi for both).
  3. Plan 093+: new ACSL units, marked by division.

## 3. Non-goals

- Rewriting history: merged plans, reviews and errata keep their ids.
- Changing the Python books' content beyond book naming.
- A USACO Silver book (future). ACSL has no per-division books: all divisions stay in `acsl`.
