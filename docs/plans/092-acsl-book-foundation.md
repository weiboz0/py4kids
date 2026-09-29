# Plan 092 — The ACSL book: foundation, season map, and the Foundations unit

**Goal:** Register *Contest Python: ACSL* (`acsl/`) as a book organized by the ACSL contest season, marked by division.
This plan adds the tooling the season structure needs and ships its first unit, **ACSL Foundations**.
Contests 1–4 follow in plans 093–096; the USACO trim follows in 097 (design 009 §3).

**Spec:** designs 008 and 009. User decisions, 2026-09-28/29:
- "separate the cp book into acsl and usaco"
- "for ACSL, we will cover all levels in one book, but mark concepts by level"
- ACSL prerequisites: "New ACSL foundations unit"
- Mock contests: "Replace and move" (applied in plan 097)
- "organize them by acsl units, so that students can follow the contest schedule in a competition season"

## Survey (2026-09-29)

- **`usaco-bronze` dependencies:** the ACSL-flavoured units (02 Boolean logic, 11 number systems/bitwise, 12 binary trees) need concepts introduced only by USACO units: `input-parse` and `str-split` (U01), `tuple` (U04), `complete-search` (U05), `recursion` (U09). USACO's graphs unit needs `deque` (U10).
  - A straight move therefore breaks prerequisite closure both ways.
  - Design 009 replaces it: ACSL is written fresh by contest, shared ids use `peers`, and USACO is trimmed last (097).
- **ACSL schedule:** from the acsl.org Study Materials, retrieved 2026-09-29; the design 009 D2 table.
  - The 2026–27 contest windows open in Oct, Jan, Feb and Mar (acsl.org Schedule).
  - Junior, Intermediate and Senior each have a 6-question short-answer test plus one programming problem; Elementary has a 6-question non-programming test on one category; Classroom has 10 non-programming questions.
- **Registry:**
  - `tuple` (feature, data-structures), `str-split` (feature, io), `input-parse` (technique, io) and `complete-search` (technique, search) exist in `usaco-bronze/curriculum/concepts.yaml`.
  - `global_concept_uniqueness_findings` allows a shared id only for variant pairs.

## Phase A — Design (inline)

`docs/designs/009-acsl-book.md` (this branch). Design 008 gets a one-line pointer: "D3–D4 refined by design 009".

## Phase B — ACSL Foundations unit: lesson and statements (Opus subagent)

Unit `acsl/units/unit-00-acsl-foundations/`. The manifest's `acsl:` block is `{contest: 0, category: Foundations, divisions: [junior, intermediate, senior]}`; Elementary has no programming, so Foundations starts at Junior.

- **Hook first:** a real ACSL-style programming problem in the opening cell. For example, read a line of numbers and report something about it. The unit then builds the skills to solve it.
- **Lessons (3):**
  1. **How ACSL works:**
     - the season and the divisions
     - short-answer vs programming, exact answers
     - reading a contest problem statement
     - running a `.py` solver with input
  2. **Reading contest input:**
     - `input()` for one line and several lines
     - `split()`
     - `int` conversion (ACSL input is integers and strings; `float` is not used, which also keeps within `source-policy`'s allowlist)
     - fixed-count and "until 0" reading (a sentinel from the Python books)
  3. **Tuples and complete search:**
     - pairs and triples as tuples
     - unpacking
     - trying every candidate with nested loops
     - counting and choosing the best
- **Exercises:** at least 12, with the `stretch` Challenge tier, each exactly one kind (design 009 D4):
  - **Programming:** stdin `.py` solvers under the judge contract. Each has a sample fixture plus at least one edge fixture.
  - **Short-answer:** "given this input, what exactly does this program print?", a WDTPD warm-up. The heading cell is tagged `short-answer`.
  - Every exercise's heading cell carries exactly one ladder tag (`acsl-junior` / `acsl-intermediate` / `acsl-senior`). `stretch` goes on the heading cell too, so one convention covers all three tags.
  - Lesson 1's "run a `.py` solver with input" demo is `assets/l1.py`, so the judge's per-lesson companion rule is met naturally.
- **Concepts:**
  - introduces (shared with `usaco-bronze` via `peers`, with identical registry entries): `input-parse`, `str-split`, `tuple`, `complete-search`
  - requires: Python-book concepts only (`python-projects` ids)
  - no USACO-only ids
- **Content is ACSL-flavoured and original.** No USACO notebook is copied.
- **Teacher notes** (inline, active session): all required headings, including `## Discussion prompts` and `## Differentiation`. Differentiation covers the division paths: Elementary and Classroom skip Foundations. The notes also cover goals, pacing, using the book through a season (the contest windows) and common mistakes.

## Phase C — Solutions (Opus subagent, separate fresh session)

- **Programming items:** each gets a solver `assets/exN.py` plus fixtures under `assets/exN/`, and passes `judge-check`.
- **Short-answer items:** in `solutions.ipynb`, a markdown worked answer ending with one `**Answer:** `<text>`` line. A `verify`-tagged cell runs the program via `subprocess.run([sys.executable, "assets/<file>.py"], input=..., capture_output=True, text=True)` from the entry folder and asserts `str(<output>) == "<text>"`, with the literal equal to the markdown answer.
- **Lesson companion assets** as the judge contract requires.

## Phase D — Tooling and registration (Opus subagent)

- **D1 `peers`:**
  - `books.yaml` gets `peers:` (symmetric). An asymmetric or unknown peer is reported by `global_concept_uniqueness_findings`, under the same gate as drift.
  - `global_concept_uniqueness_findings` lets a validated symmetric peer pair each introduce a shared id when the `concepts.yaml` entries are identical, compared as dicts (name, category, `kind`, including absence), so key order and quoting are not drift. It fails on drift.
  - The variant pair's full catalogue-equality check is unchanged.
  - "Requiring a peer-only id" already fails today via `referenced_concepts_findings` (the id is unknown); a test confirms it.
  - Tests cover all of this.
- **D2 Register `acsl`:**
  - `books.yaml`: id `acsl`, `number: 2` (the contest tier), title "Contest Python: ACSL", subtitle "From Elementary to Senior, one contest at a time", `depends_on: [python-projects]`, `peers: [usaco-bronze]`, `judge: true`, and a new flag `acsl: true` with a `#   acsl:` comment line. `usaco-bronze` gets `peers: [acsl]`.
  - Update `tests/test_books.py` (ids, numbers, flag map, `FLAGS`, comment lines) and `scripts/ci-local.sh`'s flag list.
  - `pre-merge-guard` and `test_book_ids` already read roots from `books.yaml`; no change is needed, and a test confirms `acsl` is covered.
  - Folder skeleton:
    - `acsl/syllabus.md`: the whole season map, with Contest 0–4 parts and one row per unit. The shipped Foundations unit uses the syllabus-check row form (`` | `unit-00-acsl-foundations` | unit | 3 | ``). **Planned units use plain names, not backticked ids**, with *planned (plan 09N)*, so `syllabus_findings` does not flag extra rows. The syllabus also has "Following the season" (the contest windows) and "Division paths" sections (design 009 D3).
    - `acsl/curriculum/concepts.yaml`, `coverage-map.yaml`, `season.yaml` (D2 table, with source URL and retrieval date; it includes `contest 0` with `unit_order: [Foundations]` and no per-division categories, so contest 0 needs no special case in code).
    - `acsl/docs/README.md`
    - `acsl/checkpoints/` and `acsl/projects/` as the tools require (empty until 093).
  - The `test_book_ids` guard and `tests/test_books.py` learn `acsl`.
- **D3 `manifest-check` and `acsl-check`:**
  - `manifest_findings` accepts the optional `acsl` key only for books with the `acsl` flag, and rejects it elsewhere.
  - `acsl-check` is registered in `tools/checks.py` and wired into `ci-local` for `acsl`-flag books. It returns `[]` for every other book. It checks:
    - each unit manifest `acsl:` block is valid against `season.yaml` `unit_order`; each checkpoint uses the reserved `category: Practice` (contest 1–4, one per shipped contest, after its last unit); `divisions` holds ladder levels only; `Practice` on a unit or a category name on a checkpoint fails (mutations)
    - unit order follows `season.yaml` `unit_order`
    - exactly one ladder tag on each exercise or question heading, never below the entry's (unit's or checkpoint's) lowest division, and no `acsl-classroom` tag
    - a contest part with any shipped unit has its practice checkpoint
  - Tests for each failure.
- **D4 Short-answer items:** generic now, for both exercises and checkpoint questions.
  - `judge-check` maps each `## Exercise N` / `## Question N` heading. A heading cell tagged `short-answer` is exempt from needing a solver; every other heading still needs one.
  - A new rule for judge books: every short-answer item's solution has exactly one `**Answer:** `<text>`` line in markdown, and ≥ 1 `verify` cell whose `assert str(...) == "<text>"` literal (parsed with `ast`) equals that text. The assert must be non-vacuous (reuse `_is_tautology`) and executed.
  - `exec-solutions` stops skipping stdin-model entries. For judge books it executes the solutions notebook with `no-exec` cells filtered (the existing filter). This is safe for `usaco-bronze`, which has no live solution cells; a test pins that.
  - `source-policy` and `concept-scan` skip `verify` cells in judge-book solutions notebooks.
  - Execution is skipped when no code cell remains after the `no-exec` filter (USACO's display-only notebooks), with a test.
  - `judge-check` treats every `acsl`-flag entry as stdin-model even without `assets/`, so a short-answer-only unit or checkpoint cannot escape the solver rule.
  - `structure-check` and `cell-lint` accept the tags.
  - Tests and mutations:
    - an omitted solver for a programming item fails
    - a missing, tautological or `no-exec` verify assert fails
    - changing only the markdown `**Answer:**` fails (literal mismatch), and changing only the computation fails (the assert fails at execution)
    - a wrong answer fails
    - a `short-answer` tag on a heading with a solver is reported
- **D5 CI:** `ci-local` runs every per-book check for `acsl` (registry-driven) plus `acsl-check`.

## Phase E — VERIFICATION

1. `scripts/ci-local.sh` ALL GREEN, including for `acsl`: structure, hygiene, noexec, cell-lint, exec-solutions, exec-lessons, manifest, prereq, coverage, concept-scan, stretch, judge-check, source-policy and `acsl-check`.
2. `prereq-check` and `coverage-check` pass for `acsl` and for `usaco-bronze` separately; the global concept check passes with the four shared ids.
3. Mutation tests fail as designed:
   - a division tag below the unit's minimum
   - a missing tag
   - an `acsl-classroom` tag
   - an unknown category
   - out-of-season order
   - a shipped contest unit with no practice checkpoint
   - an `acsl:` manifest block on a non-`acsl` book
   - peer registry drift
   - requiring a peer-only id
   - the short-answer mutations (D4)

   Also, `acsl-check` returns `[]` for `usaco-bronze` and the Python books.
4. Blind solve in the content gate: reviewers solve Foundations exercises from the statements alone.
5. Post-execution report.

## Out of scope

- Contests 1–4 units and practice checkpoints (093–096).
- Any `usaco-bronze` change, including the trim and mock-contest replace-and-move (097).
- ACSL publication (PDF editions).
- Level badges in print (they come with publication).

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- The verification phase is named. Scope is one unit plus infrastructure, and project-first holds (hook cell first).
- Watch items:
  - Shared concept entries must be byte-identical to USACO's.
  - `acsl-check` must not block `usaco-bronze`.
  - The short-answer genre must still be machine-verified (no free-text answers without an assert).
  - The season file records its source and date, because ACSL lists change yearly.
- `[glm]` skipped: user decision 2026-09-28, "Skip GLM until further notice".

### Round 1 — verdicts

- `[sol]` **REJECT:**
  - mixed short-answer/programming solutions escape verification (judge-check, structure policy, exec-solutions all treat a judge entry wholesale)
  - the Classroom division is not representable on a single ladder
  - the Elementary categories are unassigned
- `[fable]` **APPROVE WITH NITS.** The season table was verified against acsl.org.
  - Must Fix: `manifest-check` rejects `acsl:`; `float` vs `source-policy`; the full short-answer spec (tag cell, checkpoint questions, assert rule, exec, source-policy)
  - Should Fix: a deterministic unit order; Classroom not a tag; WDTPD order across divisions; U10 postfix; 097 checkpoint caps; registry/test couplings; the peers test confirms an existing path, with dict comparison; missing mutations
  - Nice: teacher-notes headings; `l1.py`; the Foundations short-answer form; division paths; planned syllabus rows
- `[glm]` skipped (user decision 2026-09-28, until further notice).

### Round 1 — fold

- `[FIXED]` all of the above:
  - **Design 009:**
    - D2 `unit_order`
    - D3: ladder levels, Classroom as a path of short-answer Junior/Intermediate items, Elementary sections opening the matching Junior units, division paths, WDTPD Contest 1 covering all constructs for Intermediate/Senior
    - D4: per-item classification, `short-answer` heading tag, markdown worked answer plus a `verify` cell (executed, non-vacuous, source-policy exempt)
    - roadmap 097: the U10 postfix trim and the checkpoint caps
  - **Plan:**
    - no `float`
    - the Foundations short-answer form
    - `l1.py`
    - teacher-notes headings
    - peers: dict comparison, variant check unchanged, an existing-path test
    - registration couplings: number 2, the `acsl` flag, tests, ci-local
    - planned syllabus rows not backticked
    - `manifest-check` `acsl` key
    - `acsl-check` rules
    - the full short-answer tooling spec, including checkpoint questions
    - Phase E mutations

### Round 2 — verdicts and fold

- `[sol]` **REJECT** (r2): the Classroom and Elementary blockers are resolved. Remaining: the markdown worked answer is not tied to the verified value.
  - `[FIXED]` The worked answer ends with one `**Answer:** `<text>`` line, and the `verify` assert must be `str(...) == "<text>"` with the same literal. It is checked statically and executed. A mutation changes only the printed answer, and another only the computation.
- `[fable]` **APPROVE WITH NITS** (r2), every round-1 item verified. Nits:
  - `[FIXED]` `concept-scan` skips `verify` cells.
  - `[FIXED]` One `subprocess.run` mechanism for running programs in `verify` cells.
  - `[FIXED]` `season.yaml` contest 0.
  - `[FIXED]` Asymmetric `peers` is reported by the global concept check.
  - `[FIXED]` `judge-check` treats `acsl` entries as stdin-model even without `assets/`.
  - `[FIXED]` Execution is skipped when no live cells remain.
  - `[FIXED]` `stretch` goes on the heading cell.

### Round 3

- `[sol]` **REJECT** (r3): the worked-answer gap is closed. Remaining: practice checkpoints have no valid category.
  - `[FIXED]` A reserved `category: Practice` for checkpoints only: contest 1–4, one per shipped contest, after its last unit; questions may span that contest's categories. Mutations cover `Practice` on a unit and a category name on a checkpoint.

### Round 4 — CONSENSUS

- `[sol]` **APPROVE WITH NITS** (r4): the `Practice` category closes the gap.
  - `[FIXED]` Question tags are bounded by the *entry's* lowest division, and design 009's summary names the `Practice` exception.
- `[fable]` APPROVE WITH NITS (r2, folded).
- `[self]` APPROVE.
- `[glm]` skipped (user decision 2026-09-28, until further notice).

**Consensus reached; implementation starts.**

## Content Review

### Round 1

- `[sol]` **REJECT.**
  - Blind solve: short-answer Ex 6, 9 and 12 match. Programming Ex 8, 11 and 14 match the reference solvers; 15 fixtures and 7 extra edge cases pass. The season map and windows were verified against acsl.org.
  - `[FIXED]` O1: a `verify` assert nested in `if False:` or a caught `try` passed. Only top-level asserts of the verify cell count now, and none may sit inside a `try`. Mutations: `if`, `try`, an uncalled `def`, `for range(0)`, `with`, a lambda.
  - `[FIXED]` O2: the judge compared tokens, so a wrong line layout passed. `acsl` books now compare line-exact (trailing whitespace and trailing blank lines ignored); other judge books keep token comparison. Design 009 D4 records the rule, and tests cover both.
  - `[FIXED]` O3: division validation accepted Junior LISP/Assembly. `season.yaml` now has an explicit `units: [{name, divisions}]` map per contest, and a unit's divisions must be a subset. Mutations: Junior LISP, Junior Assembly, Elementary Recursive Functions, Senior WDTPD – Arrays.
- `[fable]` **APPROVE WITH NITS.**
  - Blind solve: all 5 short answers match; 10 independent programming solutions pass 46/46 fixtures; 12 plausible wrong solutions are all caught. The ACSL description and season map were verified against acsl.org. Seven tooling mutations fail as designed.
  - `[FIXED]` F1: the classroom and elementary columns (and Junior's WDTPD C1–C4) now use the official acsl.org strings; design 009 D2's table matches.
  - `[FIXED]` F2: a visible "_Division: X and above._" line under each exercise heading.
  - `[FIXED]` F3: "fall to spring".
  - `[FIXED]` F4: the teacher notes' Junior set is "1–7 and 10".
  - `[FIXED]` F5: the terminal example uses `< assets/ex4/1.in`.
- `[self]` APPROVE WITH NITS: the blind short answers (two sessions) match the author's key; the teacher notes' division paths are consistent with the syllabus.
- `[glm]` skipped (user decision 2026-09-28, until further notice).

### Round 2 — CONSENSUS

- `[sol]` **APPROVE** (r2): O1–O3 verified by direct probes; the category strings match acsl.org; the division lines and wording fixes are present.
- `[fable]` APPROVE WITH NITS (r1, all folded).
- `[self]` APPROVE.
- `[glm]` skipped (user decision 2026-09-28, until further notice).

**Consensus reached, no `[OPEN]` findings.**

## Post-Execution Report

**Shipped.**
- **Design 009:** *Contest Python: ACSL* is one book for every division, organized by the ACSL season: Foundations, then Contest 1–4 parts with one unit per category and a practice checkpoint per contest.
  - Every item carries its lowest ladder level; Classroom and Elementary have explicit paths.
  - It refines design 008 D3–D4 and sets the roadmap: 093–096 add one contest each, and 097 is the USACO trim with replace-and-move.
- **Registry:** `acsl` is registered (`number: 2`, `judge`, the new `acsl` flag), with `peers` between `acsl` and `usaco-bronze`.
  - The global concept check lets validated symmetric peers share ids when their entries are identical as dicts. The variant check is unchanged.
- **`acsl/curriculum/season.yaml`:** the 2026–27 season from acsl.org (official category strings per division; contest windows) and an explicit `units` map per contest with the ladder levels that take each unit.
  - `acsl/syllabus.md` shows the whole season map (planned units named plainly), "Following the season" and "Division paths".
- **Tooling:**
  - `acsl-check` (`tools/acsl.py`): the manifest block, the reserved `Practice` category for checkpoints, division subsets, heading ladder tags, season order, practice placement.
  - `manifest-check` accepts `acsl:` only on `acsl` books.
  - The **short-answer genre**: a `short-answer` heading tag, a `**Answer:**` line, and a top-level executed `verify` assert with the same literal. It is exempt from `source-policy` and `concept-scan`.
  - `exec-solutions` now runs judge-book notebooks with `no-exec` filtered, skipping display-only ones.
  - `judge-check` treats `acsl` entries as stdin-model and judges `acsl` output **line-exact**; USACO keeps token comparison.
- **ACSL Foundations unit:** the hook "Pairs That Make the Target"; 3 lessons (how ACSL works, reading contest input, tuples and complete search); 15 exercises, 10 programming (judged, with edge fixtures) and 5 short-answer (verified). Each exercise carries a ladder tag plus a visible division line, and 2 are Challenges. Solutions and teacher notes are included.
  - It introduces `input-parse`, `str-split`, `tuple`, `complete-search` (shared with USACO via `peers`) and requires only *Python by Projects* concepts.

**Verification.**
- `scripts/ci-local.sh` ALL GREEN at bb3dea7, all four books included.
- pytest 903 passed.
- Blind solves: the solutions session and both reviewers independently matched all short answers. [fable]'s 10 independent programs pass 46/46 fixtures, and 12 plausible wrong solutions are caught.
- Mutations: 64+ tests in `tests/test_acsl_tooling.py`, plus probes (nested asserts, line layout, Junior LISP) confirmed by [sol].

**Deviations:**
- The plan's per-contest `unit_order` became an explicit `units` map with divisions (content gate O3).
- `acsl` output is judged line-exact (O2).
- Both are recorded in design 009.

**Follow-ups:**
- Plan 093: Contest 1 (Computer Number Systems with its Elementary section, Recursive Functions, WDTPD – Branching with the Intermediate/Senior all-constructs section, Contest 1 practice).
- Level badges in print arrive with ACSL publication.
