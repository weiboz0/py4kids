# Design 004 — Book 1b: a concept-first, story-light variant of Book 1

Status: proposed (2026-09-21).
Governs the architecture of a new book root, `book1b/`, and the tooling changes that support it.
Extends design 000 (repo/curriculum architecture) and reuses Book 1's concept catalog.

## 1. Purpose and motivation

Book 1 delivers Year-1 Python **project-first**: every unit opens with a themed build
(mad-libs, guessing game, pet simulator) and concepts arrive when the story needs them.
That framing is engaging but verbose, and the narrative can crowd out concept mastery.

**Book 1b** teaches the **same concept coverage** as Book 1, reorganized around the
**language concepts themselves**.
The story is weakened deliberately; the focus is rigorous concept mastery through
**real problem-solving** drawn from mathematics, simple (counting-style) algorithms,
turtle geometry, and puzzles.
Book 1b is an independent, self-contained root — a *variant* of Book 1, not a dependent of it —
so a teacher can run either book as a complete Year-1 course.

Book 1b is **not** a remix of Book 1's notebooks.
It is **fresh authoring** against Book 1's concept catalog.

## 2. What changes relative to Book 1 (and what does not)

| Dimension | Book 1 | Book 1b |
|---|---|---|
| Organizing principle | themed project spine | concept families |
| Concept coverage | 62 concepts | **same 62 concepts** (shared catalog) |
| Opening of each unit | project/problem hook (law) | a concrete problem that motivates the concept |
| Narrative | rich, sustained themes | minimal; problems, not stories |
| Prereq closure | strict (nothing used before taught) | **fastforward allowed** in examples/practice |
| Exercises | project-flavored | **mini-CP / LeetCode-style**, simple backgrounds |
| Exercise volume | lean early units, volume later | **no cap** — volume for mastery everywhere |
| Big builds | themed capstones (arcade night, grand adventure) | **dropped**; per-unit problem sets + one non-themed end-of-book Algorithm Challenge |
| Checkpoints | yes (themed-adjacent) | **yes** (un-themed concept-mastery) |
| Teacher notes, manifests, seeded assets | required | **required** (unchanged conventions) |
| Solutions run clean, fixed seeds; student notebooks solution-free | law | **law** (unchanged) |

Everything in AGENTS.md "Content Conventions" and "Verification" still applies to Book 1b
**except** the two laws this design explicitly relaxes for it (prereq closure → fastforward;
project-first narrative → concept-first problem framing).
The relaxations are book-scoped and enforced by configuration, so Book 1's guarantees are untouched.

## 3. Concept-family unit structure

All 62 catalog concepts are partitioned into concept-family units, each introduced **exactly once**,
in an order that keeps `requires` closure strict (a unit's core teaching never depends on an
unintroduced concept — only *examples/practice* may reach forward under fastforward).

| # | Unit (slug) | Introduces | Problem backgrounds |
|---|---|---|---|
| 01 | `unit-01-output-and-variables` | run-program, print, comment, string-literal, variable, naming, input, string-concat, f-string, error-messages | print math facts, labels, simple I/O |
| 02 | `unit-02-numbers-and-arithmetic` | int-type, float-type, arithmetic, type-conversion, boolean, comparison | digit math, even/odd (`n % 2 == 0`), averages, unit conversion, rounding |
| 03 | `unit-03-decisions` | logical-ops, if-statement, elif-else, conditional-nesting | classify (leap year, triangle type, grade), sign, logic puzzles |
| 04 | `unit-04-loops-and-counting` | while-loop, break-statement, loop-counter, accumulator, sentinel-loop, running-total, count-by-condition | digit sum, factorial, GCD-by-subtraction, Collatz steps, powers |
| 05 | `unit-05-for-and-range` | for-loop, range-function, nested-loops | series sums, times tables, primality by trial, number/star triangles |
| 06 | `unit-06-turtle-geometry` | import-statement, turtle-basics, turtle-drawing | polygons, stars, spirals — angles as math (`import turtle` is the natural motivation for `import-statement`) |
| 07 | `unit-07-functions` | def-function, parameters, return-value, scope, builtin-functions | is_prime, gcd, fib, packaging counting algorithms, `draw_polygon(n, side)` (turtle practice site) |
| 08 | `unit-08-randomness` | random-module | dice/coin simulation, Monte-Carlo estimate, turtle random walk (turtle practice site) — `requires: [import-statement]` |
| 09 | `unit-09-strings` | string-index, string-slice, string-methods, in-operator, transform-each, linear-search | palindrome, vowel count, Caesar cipher (mod), char frequency |
| 10 | `unit-10-lists` | list-literal, list-index, list-append, list-loop, list-sort, find-extreme, filter-into-list | min/max/sum, filtering, prefix sums, sorting |
| 11 | `unit-11-dictionaries` | dict-literal, dict-access, dict-loop | frequency maps, tallies, lookup tables, group-by-first-letter (backgrounds avoid untaught methods like `join`) |
| 12 | `unit-12-files` | file-read, file-write, with-statement | read numbers → stats, save/load records |
| 13 | `unit-13-objects` | class-def, init-method, attributes, methods | a `Fraction` / `Point` / `Counter` class with methods |

Checkpoints (un-themed concept-mastery) are interleaved after U03, U05, U08, and U11; a **mandatory**
checkpoint follows U13 (final numbering fixed as units land). The post-U13 checkpoint is not optional:
U12's file concepts (`file-read`, `file-write`, `with-statement`) and U13's four OOP introductions
(`class-def`, `init-method`, `attributes`, `methods`) have no later *unit*, so the post-U13 checkpoint
must practice **both** U12 and U13 — it is their only practice site before the end-of-book challenge (see
§6). U13's backgrounds accordingly include a `Counter`/`Point` that **saves and loads itself to a file**,
giving file I/O a natural reuse inside U13 as well.
The single `project` entry is a **non-themed** end-of-book **Algorithm Challenge**
(`project-01-algorithm-challenge`): an integrative problem set that doubles as the CI anchor for
full practice-coverage (see §6). It is not a narrative capstone; it appears in the syllabus roadmap
prose as the visible year-end goal students work toward.

This is a roadmap: the **coverage-map grows incrementally** as units are authored
(one content plan per unit or small batch). The catalog (§4) ships in full up front.

## 4. Registry model — a *variant* book

Book 1b registers in `books.yaml` as:

```yaml
- id: book1b
  number: 1            # same year as Book 1 (a parallel edition)
  root: book1b
  depends_on: []       # self-contained; does NOT import Book 1
  variant_of: book1    # shares Book 1's concept catalog
  prereq_policy: fastforward
  buildout: true       # EXPLICIT lifecycle flag — relaxes completeness/lesson-lower ONLY
  concept_minimum: 40  # full catalog ships up front (same 62 as Book 1)
  lesson_budget: [30, 60]
```

`buildout: true` is an **explicit, book-scoped** state, not a value derived from "is everything
introduced?" — a derived predicate would be self-referential (a missing introduction makes the
predicate false, which would silently disable the very check that catches it) and would regress Book 1
/ Book 2. Book 1 and Book 2 carry **no** `buildout` flag and are therefore strict by default. When
Book 1b is finished, the flag is removed and the completeness + lesson-lower-bound checks apply to it too.

`book1b/curriculum/concepts.yaml` is the **full 62-concept catalog, identical to Book 1's**.
`book1b/curriculum/coverage-map.yaml` is **independent** and grows unit-by-unit.
Book 1b introduces every concept itself (no dependency baseline) — it re-teaches from zero,
so it is independently complete.

## 5. Fastforward policy

Under `prereq_policy: fastforward`, a Book 1b unit may **use concepts before they are formally
taught**, to make examples and exercises real (e.g. an f-string or a small loop inside a
numbers-unit problem).

Rules:
- **`requires` stays strict.** A unit's *core teaching* may not structurally depend on an
  unintroduced concept — prereq closure over `requires` is enforced exactly as in Book 1.
- **`practices` may reach forward.** A unit may list (and its content may use) any concept in the
  catalog, regardless of introduction order — these are incidental, fastforwarded uses.
- **Checkpoint alignment stays strict.** Checkpoints assess only concepts already *introduced* by
  an earlier entry (fastforward does not apply to assessment).
- **Referenced concepts must exist in the catalog.** Fastforward relaxes *ordering*, never
  *existence*: every referenced id is still validated against `concepts.yaml`.
- **Content scan follows suit — for UNITS only.** `concept_scan.py` treats the whole catalog as the
  allowed set for a Book 1b **unit's** content (a fastforwarded concept in a cell is not
  "used-but-unlisted"). **Checkpoints and the project keep the strict per-entry allowed set**, so a
  checkpoint cannot silently use an unintroduced concept — assessment alignment holds at the content
  level, not just the declared-tag level.

Book 1's closure traps (no `+=` before it's taught, min/argmin seeding, etc.) are *pedagogical*
choices, not fastforward concerns; Book 1b authors still write age-appropriate code, but they are
free to introduce a helper concept early when a real problem calls for it.

U01 needs almost no fastforward, so **U02 is the first unit to demonstrate the forward-reaching
`practices:` tagging convention** (declaring a not-yet-introduced concept a unit's content uses) that
later units copy; U01's teacher-notes carry a one-line pointer to it.

## 6. Coverage and verification model

Book 1b runs the same `scripts/ci-local.sh` gate. **Four curriculum checks are made book-aware**, plus
build/registry **integration** so the gate reaches Book 1b at all.

1. **Concept uniqueness** (`global_concept_uniqueness_findings`): exempt id collisions between a
   book and its `variant_of` target (both directions). Additionally assert a variant's catalog is
   **content-identical** to its parent's (keeps the two catalogs in sync — a new finding if they diverge).
2. **Introduction completeness** (`introduction_findings`): keep "each concept introduced at most
   once" **always**; enforce "every catalog concept introduced" only when the book is **not** flagged
   `buildout: true`. This is gated on the explicit config flag, **not** a derived predicate (see §4),
   so Book 1 / Book 2 (no flag) stay strict and a mutation test proves that deleting an introduction
   from a strict book still fails.
3. **Prereq closure** (`prereq_findings`): under `prereq_policy: fastforward`, validate `requires`
   strictly and **skip `practices`** for ordering (existence still checked in `referenced_concepts`).
   Checkpoint alignment (`checkpoint_findings`) is untouched — still strict.
4. **Lesson budget** (`lesson_budget_findings`): enforce the configured *upper* bound always; enforce
   the *lower* bound only when the book is **not** `buildout: true` (same explicit gate; a mutation
   test proves deleting enough lessons from a strict book still fails).

**Content scan** (`concept_scan.py`): for a fastforward book, the whole-catalog allowance
(`union |= registered`) applies to **unit entries only**. **Checkpoints and the project keep the strict
per-entry allowed set**, so a checkpoint's *content* cannot use an unintroduced detectable concept
(assessment alignment holds at the content level, not just declared tags). The untaught-*method* safety
net runs for every entry.

**Pattern checks are inert for Book 1b** — `pattern_marker_findings` / `technique_spiral_findings`
(`tools/patterns.py`) and `patterns_doc_findings` (`tools/patterns_doc.py`) are hard-gated
`if book != "book1": return []`, consistent with §7 (Book 1b does not inherit design 002). No change,
but the roster is stated so nothing is expected of Book 1b there.

**Build & registry integration** (folded from plan review — these are the reason a partial Book 1b
would otherwise fail immediately; exact CLI check names + phase sequencing live in the plan):
- `scripts/ci-local.sh`: the registry assertion (currently `== ["book1","book2"]`) accepts the
  three-book registry; an **existence-guarded** (`[ -d book1b ]`) Book 1b block mirrors the Book 1
  curriculum + notebook + **turtle-check** + hygiene + manifest steps (minus the Book-1-only pattern
  checks). `scripts/build-pdf.sh` is already `--book`-generic (only its pattern-doc probe is book1-gated),
  so it is invoked for `book1b` unchanged.
- `scripts/pre-merge-guard.sh`: the collision loop iterates `book1b` too.
- `tests/test_books.py` + `tests/test_tools.py`: the registry assertion and the CI-contract test are
  updated for the three-book registry (all of ids/numbers/roots/positional deps, pinned order).
- All curriculum invocations use `python -m tools.cli --book book1b <check>` (both `--book` and a check
  name are required); `coverage-check`/`prereq-check` are the composites that exercise the curriculum rules.

**Syllabus** (`syllabus_findings`): matches only pipe-delimited table rows, so Book 1b's `syllabus.md`
lists shipped entries as a table and the **roadmap of planned units as prose** (never a
`| ` + backtick-slug + ` |` row) — no tooling change, an authoring rule.

**Practice coverage** (every concept practiced beyond its introduction) is anchored by the end-of-book
`project-01-algorithm-challenge`: the existing capstone check (`practice_findings`) fires once a
`project` entry is the last entry and its directory is authored, guaranteeing every concept is
practiced somewhere before the final challenge. **This anchor is dormant until the last plan**, so each
per-unit content plan's gate must **manually verify every earlier introduction is practiced at least
once** (an authoring rule) to avoid a backfill scramble at the end.

**Per-exercise assertion rigor is a content-gate rule, not an existing CI guarantee.** `notebooks.py`
`_solution_policy_findings` only requires **three assert-bearing cells across the whole notebook**, not
three cases per exercise. Book 1b's "every exercise's solution asserts several cases" is therefore
enforced by reviewers at the content gate (a future per-exercise check could be added, out of scope here).

**Engagement criterion for Book 1b.** `docs/content-review-gate.md` is governance-locked and carries
Book 1's "no unit opens with concept drill" wording. For Book 1b, that criterion reads: **each unit's
opening cell poses a genuine problem with a visible payoff** ("which of these years are leap years?",
"how many steps does 27 take to reach 1?") — *not* "here is what `if` does". Dropping the narrative is
allowed; opening on concept exposition is still a gate-blocking finding.

Per-unit notebook checks (execution, hygiene, manifest, stretch) run on **authored** units only;
roadmap entries not yet in the coverage-map are simply absent, so nothing is skipped or faked.

## 7. Exercise design — mini-CP / LeetCode style

Every exercise is a **self-contained problem** with:
- a one-paragraph **simple background** (math / counting / turtle / puzzle — never a sustained story);
- a precise **specification** (inputs, outputs, constraints);
- **worked sample(s)**: sample input → expected output, so the task is unambiguous and blind-solvable;
- a **testable solution** whose form depends on whether functions have been taught yet:
  - **Before U07 (`def-function`)** — the *pre-function* form: the exercise is stated as "given these
    values, produce this exact output"; `input()` is replaced by **fixed sample values** in
    `solutions.ipynb`. The solution **mirrors the student's visible form** (the same separate `print`
    calls a student writes — never an untaught `"\n"`-joined string or multi-line join as the shown
    answer), and **asserts the produced output line by line** against the expected text (a 4-line card
    → 4 line asserts; a 1-line answer → 1). **House form** (locked at U01 so U02–U13 clone one shape):
    capture each output line in a named variable, print it, then assert that variable
    (`line_1 = f"…"; print(line_1); assert line_1 == "…"`) — one source of truth, so the asserted text
    is exactly the printed text. A "repair the error" exercise is the one exception: it shows the
    *directly repaired instruction* verbatim (the point is seeing the fix), with the assert on a
    separately built copy — the reference answer must model the operation the student was asked to do.
  - **From U07 on** — the *function* form: the solution defines the function and asserts it against
    **several distinct input cases**, fixed seeds where random.
- **Assertion rigor is a content-gate authoring rule** (reviewers verify it; `notebooks.py` only
  enforces ≥3 assert-bearing cells notebook-wide, see §6). Its meaning is form-dependent: the
  **pre-function** form asserts every line of the one deterministic expected output (there is a single
  fixed-input case, so per-line asserts ARE the "several" — not several distinct inputs); the
  **function** form asserts several distinct inputs. Turtle exercises are exempt (verified by execution
  + `turtle-check`).
- **Turtle exercises are exempt from the assert rule.** A drawing cannot be asserted; turtle `.py`
  assets (U06, and the turtle practice sites in U07/U08) are verified by execution + `turtle-check`
  (the `fake_turtle` harness), exactly as in Book 1 — not by output assertions.

Exercises favor **volume and variety** — no per-unit cap — and ladder from a minimal case to a
realistic one. To protect the fragile early-lesson pacing, U01–U02 teacher-notes **partition** the
exercise bank into a *core set* (the minimum every student does, keeping a lesson at 60–90 min) and
*extra practice*; the bank itself stays large. Student notebooks remain solution-free with no executed
outputs; solutions run top-to-bottom clean. Each unit still ships ≥2 `stretch` ("Challenge") exercises,
and core content never depends on them. Datasets come from seeded generators, never opaque blobs.

Because Book 1b is concept-first, it does **not** inherit Book 1's algorithm-pattern-thread
authority (design 002); the seven technique concepts are taught within their natural units
(counting in U04, search/transform in U09, find-extreme/filter in U10) as ordinary concepts.

## 8. Notebook and directory conventions

`book1b/` mirrors Book 1's layout (design 000 §1): `syllabus.md`, `curriculum/`, `units/`,
`checkpoints/`, `projects/` (the single Algorithm Challenge), `reference/`, `docs/`, `build/`.
Each unit ships `manifest.yaml`, `lesson.ipynb` (opens with a motivating problem), `exercises.ipynb`
(solution-free), `solutions.ipynb` (clean, seeded), `teacher-notes.md`, and `assets/`.
Turtle work — U06 and the turtle practice sites in U07/U08 — runs as `.py` scripts from the terminal,
exactly as Book 1's turtle units do (verified by `turtle-check`). Empty `checkpoints/` and `projects/`
directories carry a `.gitkeep` (git does not track empty dirs; Book 1/Book 2 use the same convention).

## 9. Governance and decision record

Adding a book root and relaxing two Book-1 laws (for Book 1b only) is an architectural decision.
This design is the record; an ADR stub in `docs/architecture/decisions.md` (governance-locked,
human-reviewed) should note "Book 1b — concept-first variant; fastforward + concept-first framing
are book-scoped relaxations." Two other governance-locked edits are likewise **deferred to human
review** (per AGENTS.md, unless the user asks inline): AGENTS.md's "two independently complete roots"
sentence (now three) and any content-review-gate wording for the Book 1b engagement criterion (§6). The
tooling and content this plan ships do not touch those files.

## 10. Out of scope

- Any Book 2 changes.
- Retro-fitting Book 1 (it remains project-first and strict).
- A narrative capstone (deliberately dropped).
- New concepts beyond Book 1's catalog.

## 11. Rollout

- **Plan 069 — Foundation:** registry entry, `book1b/` skeleton, full catalog, syllabus, a valid
  U01-only coverage-map, the book-aware tooling changes (plan Tooling A–D + tests), ci-local/registry
  integration, and **U01 authored end-to-end** as the template all later units follow. Verification
  phase required.
- **Plans 070+ — per-unit content:** one plan per unit (or small batch), each adding the unit's
  coverage-map entry + notebooks + teacher notes + checkpoint where due, through the 4-way content
  gate. The Algorithm Challenge project lands last.

## Design Review

_(4-way plan-review verdicts recorded in the plan file, per AGENTS.md.)_
