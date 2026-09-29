# Plan 093 — ACSL Contest 1: Number Systems, Recursive Functions, What Does This Program Do?

**Goal:** Ship the Contest 1 part of *Contest Python: ACSL*: one unit per Contest 1 category, then the Contest 1 practice checkpoint. This is the part students study before the first contest window (Oct 19, 2026 – Jan 10, 2027).

**Spec:** design 009 (D1–D5 and the roadmap row for 093). User decisions, 2026-09-29:
- "continue with plan 093 on autopilot and all other contest followed"
- the earlier decisions quoted in plan 092 (one book for every division, marked by level; organized by the contest season)

## Survey (2026-09-29, main at efb3866)

- **Existing book:** `acsl/` holds `unit-00-acsl-foundations`, which introduces `input-parse`, `str-split`, `tuple` and `complete-search`.
- **`season.yaml` Contest 1 units:**
  - Computer Number Systems — elementary, junior, intermediate, senior
  - Recursive Functions — junior, intermediate, senior
  - What Does This Program Do? – Branching — junior, intermediate, senior (the merged all-constructs unit, design 009 D3)
- **Shared concept ids** available via `peers`, with entries identical to `usaco-bronze`:
  - `base-conversion` (technique, number-theory)
  - `recursion` (feature, techniques)
  - `code-tracing` (technique, techniques)
- **Checkpoint rules:** 6–8 question headings (`tools/notebooks.py`), strict prerequisites (no borrowed tools), and a Grading section in the teacher notes. The ACSL format is short-answer questions plus exactly one programming problem.

## The entries (all under `acsl/`)

Every unit follows the Foundations conventions:
- a project-first hook cell and 3 lessons
- **at least 14 exercises**, mixing programming items (judged line-exact, with edge fixtures) and short-answer items (`**Answer:**` line and a top-level `verify` assert)
- a ladder tag plus a visible "_Division: X and above._" line on each heading
- at least 2 `stretch` Challenges

**Canonical short-answer text**, so blind solves compare cleanly:
- hex digits uppercase
- no base prefix or subscript in the answer (the base is stated in the question)
- no leading zeros
- recursion values as plain integers
- fractions in lowest terms as `a/b`
- WDTPD answers are the exact printed output; a multi-line output is written as one backticked literal with `\n` between lines, or the item is designed to print one line

Statements write bases ACSL-style with subscripts (3F₁₆).

**`source-policy` applies to lesson, solution and asset code** (`verify` cells are exempt):
- Allowed: `int(s, base)`, but only *after* the hand method.
- Never used: `bin`, `oct`, `hex`, `format`, `divmod`, `.join`, `.index`, `.find`.
- Hand-written conversion loops are the taught method.

### `unit-01-computer-number-systems` — Computer Number Systems

- **Divisions:** elementary, junior, intermediate, senior. **Introduces:** `base-conversion`. **Requires:** *Python by Projects* ids and Foundations ids only.
- **Hook: non-programming.** For example: "which is larger, 101101₂ or 55₈?" or "what colour is #7FBF3F?"
- **Lesson 1 is the Elementary section**, with no code the student runs. It follows the official Elementary study doc:
  - bases 2/8/10/16 and place value; any base → decimal by expanded notation
  - the 3-bit/4-bit grouping shortcut between 2, 8 and 16
  - addition and subtraction in another base
  - comparing values across bases
  - hex RGB colours (`#FF0000`)
  - counting the 1s in a binary number
- `assets/l1.py` is a small base-10 → base-2 self-checker, mentioned in a `no-exec` cell so the judge's per-lesson rule holds.
- **Exercises open with ≥ 6 contiguous `acsl-elementary` short-answer items**, the size of an Elementary test.
- **Lessons 2–3 (Junior+):**
  - decimal → any base by repeated division
  - larger conversions
  - multiplication by a single digit in a base (ACSL excludes division)
  - hex colours at Junior level
  - programming conversion loops, then `int(s, base)`
  - **fractional place value in bases 2, 8 and 16** (e.g. 0.101₂ = 5/8), taught by hand; items short-answer and tagged as stretch or Intermediate

### `unit-02-recursive-functions` — Recursive Functions

- **Divisions:** junior, intermediate, senior. **Introduces:** `recursion`. **Requires:** *Python by Projects* and Foundations ids, including `def-function`, `parameters` and `return-value`.
- **ACSL notation:** piecewise "cases" definitions in ACSL's bracket layout. **Call-table method:** expand top-down to the base case, then substitute back up. Conditions may use `abs`, floor and `mod`.
- **Forms taught and assessed:**
  - single recursion
  - two-variable functions
  - **multiple recursion** (`f(x-1) + f(x-2)`; at least one Junior exercise)
  - **indirect recursion** (f calls g calls f; at least one Intermediate exercise)
- Nested calls `f(f(x))` are not tested by ACSL and not used.
- **Python:** a function that calls itself, base cases, tracing calls, the call stack. Programming items implement a given definition.
- `concept-scan` has no recursion detector, so taught-before-used is enforced by review.

### `unit-03-wdtpd-branching` — What Does This Program Do? – Branching

- **Divisions:** junior, intermediate, senior. **Introduces:** `code-tracing`. **Requires:** *Python by Projects* and Foundations ids, plus `recursion` and `base-conversion` if traced.
- **Lesson 1 opens with an ACSL pseudocode ↔ Python dialect table.** Operators and forms in scope:
  - `+ - * %`
  - `/` (real division: used only on exactly-divisible operands, so it equals `//`)
  - `^` exponent (small whole-number powers, traced as repeated multiplication)
  - `!`, `&&`, `||` (Python `not`, `and`, `or`)
  - `abs` and `int` (greatest integer, on whole-number results only)
  - `S[a:b]` substrings (Python slicing semantics stated)
  - arrays from index 0 or 1, as the program states
- **At least one third of short-answer items are presented in ACSL pseudocode**, with a Python transliteration in the trace asset.
- **Junior:** `if`/`elif`/`else` chains, nested conditions, logical operators, integer arithmetic, exact output.
- **Intermediate+ section** (tagged `acsl-intermediate`): Contest 1 covers all constructs for these divisions. It traces `while` and `for` loops (including stepped loops), 1D lists, and strings (indexing, slicing, methods from *Python by Projects*).
- **Excluded in 093, with the gap noted in the unit and the teacher notes:**
  - 2D arrays (coming in plan 095, WDTPD – Arrays and Data Structures)
  - `sqrt`
  - non-integer real division
- Mostly short-answer, plus a few "predict, then verify" programming items.

### `checkpoint-01-contest-1-practice` — Practice (contest 1)

- **Divisions:** junior, intermediate, senior.
- **8 questions:**
  - Q1–Q6: `acsl-junior` short-answer, 2 per category (a full Junior paper)
  - Q7: one `acsl-intermediate` short-answer tracing question across all constructs
  - Q8: the single `acsl-junior` **programming problem**, last as on the contest, with the sample plus ≥ 4 hidden-style fixtures
- Strict: `requires`/`practices` only ids from *Python by Projects* and units 00–03; no introductions; no auxiliary concepts.
- **Teacher notes:**
  - Grading uses ACSL's published scoring (1 point per short answer; the programming problem scored on its test cases) and time limits, quoted from acsl.org rather than invented.
  - Division paths: Classroom takes Q1–Q7; the Elementary path uses unit 01's Elementary items as its mock test.

## Phase A1 — Registry, before authoring (inline)

`acsl/curriculum/concepts.yaml`: add `base-conversion` (technique, number-theory), `recursion` (feature, techniques) and `code-tracing` (technique, techniques), byte-identical to USACO's, so the manifests validate.

## Phase B — Lessons and statements (Opus subagents, one per entry, in parallel; each owns only its folder)

Four authors: three units and the checkpoint.
- Each unit author writes `manifest.yaml` (with the `acsl:` block), `lesson.ipynb`, `exercises.ipynb`, and the lesson assets `lN.py` with fixtures.
- The checkpoint author writes `manifest.yaml` and `checkpoint.ipynb`.
- Each reports its concept lists.

## Phase C — Solutions (Opus subagents, separate fresh sessions, one per entry)

- Programming items: `assets/exN.py` or `qN.py` with fixtures, and no-exec mirrors in the notebook.
- Short-answer items: a trace asset where a program is involved, a worked answer, and a `verify` cell, using the canonical answer text.
- Solved from the statements only.

## Phase A2 — Coverage and syllabus, after authoring (inline)

- `acsl/curriculum/coverage-map.yaml`: entries in season order (units 01, 02, 03, then the checkpoint), reconciled exactly against each manifest.
- `acsl/syllabus.md`: the Contest 1 rows in the syllabus-check form (`` | `id` | kind | lessons | ``), with the checkpoint's lessons value as in USACO's syllabus.

## Phase D — Teacher notes (inline) and one tooling rule (Opus subagent)

- **Four `teacher-notes.md` files:** the required headings, plus Grading for the checkpoint. They cover:
  - division paths
  - pacing against the Contest 1 window
  - common mistakes (place value vs digit value, a missing base case, tracing `elif` after a true branch)
  - the excluded constructs
- **`acsl-check`:** a practice checkpoint has exactly one question heading without the `short-answer` tag, and it is the last question. Mutation tests: zero programming questions, two, and not last.

## Phase E — VERIFICATION

1. `scripts/ci-local.sh` ALL GREEN. For `acsl` this covers structure, hygiene, noexec, cell-lint, exec-solutions, exec-lessons, manifest, prereq, coverage, concept-scan, stretch, judge-check, source-policy and `acsl-check`, including season order, practice placement, division subsets and the new one-programming-question rule.
2. The global concept check passes with the three new shared ids.
3. **Division paths are checked:**
   - the Junior path through the checkpoint is exactly 6 short-answer questions plus 1 programming question
   - unit 01 has ≥ 6 contiguous `acsl-elementary` items before any other tag
4. **Blind solves** in the content gate: every reviewer solves all 7 short-answer checkpoint questions and at least 3 short-answer items per unit, using the canonical answer text, plus a sample of programming items.
5. Post-execution report.

## Out of scope

- Contests 2–4 (094–096).
- The USACO trim (097).
- ACSL publication.

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- The verification phase is named. The scope is 3 units and a checkpoint, as in earlier content plans.
- Watch items:
  - the Elementary section must be fully non-programming and usable alone
  - the Intermediate+ tracing section must not use concepts beyond *Python by Projects*
  - `int(s, base)` must come after the hand method
  - the checkpoint must have exactly one programming question
- `[glm]` skipped: user decision 2026-09-28, until further notice.

### Round 1 — verdicts

- `[sol]` **REJECT:**
  - the Junior checkpoint path has fewer than 6 short answers
  - "all constructs" is too narrow and unspecified (2D arrays, stepped loops, slicing, real division, exponent, `abs`/`sqrt`/`int`)
  - Number Systems omits fractions
  - registry timing contradicts the author handoff
- `[fable]` **APPROVE WITH NITS** (conditional), checked against acsl.org category pages and the Elementary study doc:
  - Must fix: ACSL pseudocode dialect; multiple and indirect recursion; Elementary aligned with the official doc (grouping, add/subtract, compare, RGB, counting 1s, ≥ 6 items); the checkpoint Junior path
  - Should fix: per-entry `requires` boundaries; A1/A2 ordering; the Elementary hook and `l1.py` mechanics; canonical answer text; the 2D-array exclusion; `source-policy` gotchas
  - Nice: official scoring and timing, Classroom/Elementary paths, blind-solve sample definition, a one-programming-question check, subscripted bases, hex colours at Junior
- `[glm]` skipped (user decision 2026-09-28, until further notice).

### Round 1 — fold

- `[FIXED]` all of the above.
  - **Entries rewritten** with explicit per-entry scope, divisions, `requires` boundaries and canonical answer text:
    - Elementary is Lesson 1 of unit 01, with a non-programming hook and ≥ 6 contiguous items.
    - Fractions in bases 2/8/16 are taught by hand.
    - Recursion covers multiple and indirect recursion, with the call-table method.
    - WDTPD has a pseudocode dialect table, at least one third of items in pseudocode, and an explicit construct list with its semantics.
    - 2D arrays, `sqrt` and non-integer division are excluded in 093, with the gap stated (plan 095 covers 2D arrays).
    - The checkpoint has 8 questions: 6 Junior short answers, 1 Intermediate, and the programming problem last (≥ 4 hidden-style fixtures).
  - **Phases A1/A2** split (registry before authoring; coverage and syllabus after, reconciled).
  - **Tooling:** `acsl-check` enforces exactly one programming question, last.
  - **Phase E:** division-path checks and the blind-solve sample.

## Content Review
_(filled before PR.)_

## Post-Execution Report
_(filled before merge.)_
