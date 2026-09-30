# Plan 099 — *Contest Python: USACO Bronze*: publication content and PDFs

**Goal:** Give *Contest Python: USACO Bronze* its four book editions (Student Print, Student Full, Answer Key, Teacher's Edition), built and audited clean by `scripts/ci-local.sh`.

**Spec:** design 010 (D6), design 007 with its plan 089 and 090 amendments, and the tooling of plans 097 and 098.
User decisions, 2026-09-30:
- "all books should have pdfs"
- the same four editions, with the odd-numbered answer rule
- goals and recap panels in every lesson
- a short **unnumbered** contest "Getting Set Up" chapter that points to *Python by Projects* for installing Python

Plan 098's lessons apply:
- a probe before planning, and a rendered-page review in the gate
- fold sessions in isolated worktrees while CI runs
- no `git stash` in the shared tree

## Survey (2026-09-30, main at 0f23c00; read-only probe with stub matter, `student` and `teacher` rendered)

- **The book:**
  - 14 units: 127 exercises, 2 stretch items per unit.
  - 4 checkpoints, "Mock Contest 1–4", after units 5, 8, 12 and 14.
  - 1 project: `project-03-mock-contest`, "Grand Mock Contest", with 8 problems in 5 milestones.
  - 31 `introduces` ids, 11 of them shared with the peer *Contest Python: ACSL*: input-parse, str-split, grid-2d, boolean-algebra, code-tracing, tuple, complete-search, recursion, postfix-eval, base-conversion, tree-traversal.
  - Every problem reads stdin (`sys.stdin.read()`). Lessons run full solvers as `python assets/lN.py < assets/lN/1.in` from the unit folder (33 times, always "Run the full solver from this unit folder:").
- **Probe results:** student 270 pages, teacher 388; 26 chapters, 161 items; 0 overfull boxes and 0 missing glyphs.
- **Audit findings:**
  - Goals/recap are missing in all 14 units.
  - "no-exec" appears in u08 lesson cell `0f35cbe0`.
  - **Leaks** (byte-identical solutions):
    - CP2 Q6 `q6.py` = u08 Ex5 `ex5.py` (odd, printed)
    - CP3 Q7 `q7.py` = u12 Ex1 (odd, printed)
    - u13 Ex6 `ex6.py` = Ex7 (odd, printed), so the hidden even answer leaks
    - u02 Ex1 `ex1.py` = the lesson's `l1.py` gate program (cell `f970f6d3`)
  - The typed-code inventory fails for u02 and u04: their `exercises.ipynb` cells have **no ids** (19/19 each), so nbformat invents ids on every read.
  - An index term wrapped across two `.ind` lines (a long glossary term) is missed by the audit.
- **Found only on rendered pages:**
  - **Every lesson stdin solver prints twice:** as a Try-it with a generic "save it as a `.py` file…" note, then again as a `Program assets/lN.py` listing (the 33 `lN.py` files are identical to their cells).
  - `_Challenge (stretch)._` lines duplicate the stretch marker (28 items).
  - Checkpoints:
    - Three opener cells (CP1–3) mention "the teacher grading guide", which breaks independence.
    - "in the empty code cell below" (checkpoints and the project) is notebook-only wording.
    - They use bold inline `**Constraints.**` / `**Constraints:**` (7 places), not the units' `### Constraints`.
  - Project:
    - `Constraints:` and "Sample Input" are plain lines, not run-in subheads.
    - Its Teacher's answer key prints untitled "Problem 1…8".
  - `**O(R*C)**` in u01 `teacher-notes.md` (lines 20, 21, 24) prints literal asterisks.
  - "Book-2" (u01 notes line 5, u14 line 16) and "Year-2" (the project) are wrong names.
  - Inline code containing `..` breaks as "1. / .n" (about 20 spans, for example u01 `302b3447`).
  - The unit-11 running header is truncated ("…Bitwise & Number").
- **Near-duplicate checkpoint questions** (the audit cannot see them; token similarity to a unit exercise):
  - CP3 Q2 ≈ u10 Ex2: 0.97
  - CP4 Q4 ≈ u14 Ex1: 0.78
  - CP4 Q6 ≈ u11 Ex8: 0.76
  - CP4 Q5 ≈ u14 Ex5: 0.69
  - CP3 Q1 ≈ u09 Ex2: 0.64
  - CP4 Q1 ≈ u13 Ex3: 0.37
- **Lessons:**
  - 102 executable cells have no outputs; `exec-lessons` passes, and there is no randomness.
  - The 33 `no-exec` cells are all stdin solvers routed to Try-it.
  - Headings are `## Lesson N — Title`.
  - **Unit 03 has no `## Lesson` heading.**
  - Unit 01 opens with `## The Real Program Reads stdin` before Lesson 1.
- **Reuse:** no other book's glossary covers these ids. The 11 shared definitions are written book-neutrally, so plan 100 (*ACSL*) can reuse them.

## Phases

### Phase A — Tooling gaps (Opus tooling subagent; each fix with a fixture test; python-concepts and python-projects outputs checked against their baselines)

1. **Stdin solver printed once.** When a lesson's stdin Try-it cell is identical (by code tokens) to the `assets/lN.py` the next cell tells students to run, it prints once:
   - the Try-it panel ends with the book's run line for that file (`python assets/lN.py < assets/lN/1.in`), instead of the generic "save it as a `.py` file…" note
   - the following `Program assets/lN.py` listing is not repeated
   - the audit's inventory and "listed again in full" checks agree
2. **Project answer titles.** A project answer section headed `## Problem N` takes its title from the brief's `### Problem N — Title` heading, as checkpoint answers do.
3. **Inline code with `..`.** Find why inline code containing `..` renders as "1. / .n" (the `Code` filter's break points, or a TeX ligature), and fix it so the code prints exactly.
4. **Running-header length.** Long unit titles get a short running head, taken from a new optional manifest key `short_title`, or from a rule applied by the publisher. The unit-11 header is the test case.
5. **Index audit.** Index entries that makeindex wraps across `.ind` lines are matched.

### Phase B — Notebook fixes and content (Opus content subagents; blind solves for every changed problem)

- **Duplicates and leaks:**
  - Replace **CP2 Q6** and **CP3 Q7** (identical to odd unit exercises) and **CP3 Q2** (0.97 similar to u10 Ex2) with new problems of the same topic and level. Each gets a statement, `qN.py` with fixtures, a `solutions.ipynb` mirror and teacher notes. Solutions are written in a separate session, blind to the statement's intended answer.
  - Revise **u13 Ex6** so its solution no longer equals Ex7's.
  - Revise **u02 Ex1** so it no longer equals the lesson's gate program `l1.py`.
  - The reviewers judge CP4 Q4/Q5/Q6 and CP3 Q1 (0.64–0.78, same technique with a different task) in the gate; any judged a copy is replaced the same way.
- **Independence and print wording:**
  - Remove "the teacher grading guide" from the checkpoint openers.
  - Reword "in the empty code cell below" to "in your notebook" (checkpoints and the project).
  - Remove "no-exec" from u08 `0f35cbe0`.
  - Fix "Book-2" / "Year-2" to the book's name.
- **Markup:**
  - Remove the `_Challenge (stretch)._` lines (the stretch marker already prints).
  - Checkpoint inline `**Constraints.**` becomes `### Constraints`.
  - The project's `Constraints:` / "Sample Input" / "Sample Output" become `###` subsections.
  - Write `O(R*C)` in u01's teacher notes as code.
- **Cell ids:** give u02's and u04's `exercises.ipynb` cells stable ids.
- **Lesson structure:** unit 03 gains a `## Lesson 1 — …` heading. Unit 01's opening `## The Real Program Reads stdin` section moves inside Lesson 1, so the goals panel sits before Lesson 1.

### Phase C — Lesson outputs and panels

- `fill-outputs` for the 102 executable lesson cells; `lesson-outputs-check` passes twice (deterministic).
- **Goals and recap (Opus):** in all 14 lessons, a `### You will learn` cell immediately before the first `## Lesson` cell and a `### Recap` last cell. They are in student voice, covering the core lessons, and drawn from each unit's teacher-notes goals.

### Phase D — Front and back matter, setup chapter, config

- **`usaco-bronze/publication.yaml`:**
  - setup: `docs/getting-set-up.md` + `docs/getting-set-up-teacher-notes.md`, `numbered: false`
  - `project_headers: {project-03-mock-contest: Mock Contest}`
  - `lesson_heading: '^## Lesson\b'`
  - `index_names`: this book's taught names
  - `audit`: empty demo lists, and `print_required_starters` measured from the sources
  - `phrase_exemptions`: `python assets/`, kinds `[unit]`, chapters `[units/*]`, because the lessons teach running solvers this way
- **Front matter** (inline; Student Book independent; contest-specific), measured from the sources:
  - `preface.md`
  - `how-to-use.md`, which covers:
    - stdin programs, samples and constraints, and running a program with an input file
    - the fixture routine, and the stretch Challenges
    - the Mock Contest checkpoints (timed, self-checked against their samples) and the Grand Mock Contest
    - Answers to Selected Exercises
  - `for-teachers.md`
  - `answer-key-intro.md`
- **Back matter:**
  - `glossary.md`: 31 entries with **short** terms (for example "Set operations"), covering exactly the book's `introduces` ids. The 11 ids shared with *ACSL* get book-neutral definitions.
  - `quick-reference.md`: contest idioms by unit (reading input, splitting, sorting with a key, sets, prefix sums, deque, bit operations, grid and graph traversal, two pointers).
- **Setup chapter** (unnumbered "Getting Set Up") and its teacher notes: installing Python is covered in *Python by Projects* Unit 0. It covers:
  - opening a terminal in a unit folder
  - running `python assets/lN.py < assets/lN/1.in`, or a solution with an input file
  - comparing with the sample output
  - how the fixtures check a program
- **Enabling the book:** `books.yaml` gains `publication: true` for `usaco-bronze`; update `tests/test_books.py`.

### Phase E — VERIFICATION

1. `scripts/ci-local.sh` ALL GREEN in one solo run on the final commit.
   - Because `tools/` changes, all three publication books render in all four editions, about 45 minutes of rendering. Never overlap runs.
   - `lesson-outputs-check`, `judge-check` (including the new and revised problems) and `publish-audit` pass for every edition.
2. python-concepts and python-projects outputs are unchanged, or any change is listed with its reason. python-concepts is checked against its baseline and allowed-diffs; python-projects against a digest captured before Phase A.
3. **Blind solves:** reviewers solve every new or revised problem (CP2 Q6, CP3 Q2, CP3 Q7, u13 Ex6, u02 Ex1, and any replaced in the gate) from the statement, and run the solutions against the fixtures.
4. **Rendered-page review in the content gate:**
   - a unit opener with You will learn
   - a lesson with a stdin Try-it (printed once, with its run line)
   - a judge exercise with its sections
   - a stretch Challenge
   - a checkpoint opener and a question
   - the Grand Mock Contest problem and its Teacher's answer
   - Answers to Selected Exercises, the Answer Key, and the glossary and index
   - the unit-11 running head and a `..` code span
5. The post-execution report records page counts and the audit summary.

## Out of scope

- *ACSL* (plan 100) and the GitHub Release (after plan 100).
- New exercises beyond the named replacements and revisions.

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- The plan is built from a fresh probe that looked at rendered pages. It separates tooling from content, and it treats duplicate checkpoint questions as content errors (replaced and blind-solved), not audit noise.
- **N1 (noted):** the python-projects regression digest is new here. Plan 098 had no baseline for that book, so Phase A captures one before its first change.

## Content Review

## Post-Execution Report
_(filled before merge.)_
