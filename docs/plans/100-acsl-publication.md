# Plan 100 — *Contest Python: ACSL*: publication content and PDFs

**Goal:** Give *Contest Python: ACSL* its four book editions (Student Print, Student Full, Answer Key, Teacher's Edition), built and audited clean by `scripts/ci-local.sh`. This completes design 010: every book has PDFs.

**Spec:** design 010 (D6), design 007 with its amendments, and the tooling of plans 097–099. The user decisions of 2026-09-30 apply:
- the same four editions, with odd-numbered unit answers
- goals and recap panels in every lesson
- a short **unnumbered** contest "Getting Set Up" chapter; ACSL's Unit 0 stays Foundations

Rules and lessons carried over from plans 097–099:
- a probe before planning, a rendered-page review in the gate, fold sessions in isolated worktrees while CI runs, and no `git stash`
- **the strict no-copy rule for checkpoints:** no checkpoint question may reuse a unit exercise's *task*. The same computation relabelled, or a small extension of a unit exercise, counts as a copy. For short-answer items, where the instance data *is* the task, the same category with new data is allowed.

## Survey (2026-09-30, main at d263b48; read-only probe with stub matter, `student` and `teacher` rendered)

- **The book:**
  - 16 units: Unit 0 Foundations, then Contests 1–4.
  - 4 practice checkpoints, "Contest N Practice", after units 3, 7, 11 and 15, holding 35 questions.
  - No projects.
  - 324 unit exercises, 256 of them short-answer.
  - 19 `introduces` ids. 12 are shared with *USACO Bronze*, whose glossary text is book-neutral; `boolean-algebra` and `bitwise-ops` must be reworded for ACSL notation. 7 are ACSL-only.
- **Probe results:**
  - student 522 pages, teacher 646; 27 chapters, 359 items
  - 0 missing glyphs (`⊕ ⊙ ↑ λ →` and subscripts render)
  - 3 overfull boxes of 19.8pt, all from u08 cell `l-012`'s step table
- **Checks that passed:**
  - Short-answer items render correctly: the placeholder is dropped, the division tag shows, `**Answer:**` lines print in the answers appendix and the Teacher's keys (256), and `verify` cells never print.
  - Pseudocode, netlists, assembly and LISP code blocks, and the LaTeX overbars, render.
  - Inventory, cell ids and item titles are clean.
- **Tooling gaps:**
  - **Every lesson program prints twice** (48 times, 3 per unit). A `Program assets/lN.py` listing, triggered by the markdown line "It is saved as `assets/lN.py`", comes before the identical `no-exec` Try-it. ACSL programs use `input()`, and the asset is named in the cell *before*; plan 099's dedup only covers stdin Try-its whose asset is named in the cell *after*.
  - **The running head bleeds.** The "Checkpoint 4" chapter label carries onto every back-matter chapter's opening pages, because ACSL's main matter ends with a checkpoint, not a project. This also breaks `glossary_page_numbers`: "glossary pages unresolved".
  - **An audit false positive:** "Unit 13 Exercise 19: source page 363". `reference_findings` reads a sample-input line "2" at the top of a right-hand page as the page number.
  - **A nit:** `code_span_names` prints SyntaxWarnings (`ast.parse` on spans like `2d`).
- **Content findings:**
  - goals/recap missing in all 16 units
  - an error demo untagged: u02 `7be73630`
  - "your teacher" in u00 `56500fd0`
  - **a leak:** u04 Ex21 `ex21.py` is identical to the lesson's `l1.py`, and Ex21 is odd, so it prints
  - the u08 `l-012` table overflows
  - **12 lists render as running text** (no blank line before the list): u01 `l-015`, u04 `l-011`, u08 `l-010`, `l-011`, `e-038`, u12 `l-007`, `e-001`, `l-003`, `l-005`, `l-008`, `l-009`, and u00's teacher notes line 63
  - escaped `\|` inside code in tables prints its backslash (u03 `60788637`, u05 `l-017`, `l-022`)
  - 32 `_Challenge._` lines duplicate the stretch marker
  - `132_b` / `21_b` print a literal underscore (u01 lesson, exercises Ex21, solutions)
  - checkpoint openers say "check your work against the answers" (answers are Teacher's-only) and "Write each answer in the cell under its question"
  - notebook-only wording in lessons ("run the cell", "In the notebook…", "this cell is marked not to run", in u00, u01, u03 and u04)
  - "(design 009)" and "(no-exec)" in teacher notes
  - a stale syllabus line: "Planned units … arrive in later editions"
- **Lessons:** 148 executable cells with no outputs, and no randomness. `fill-outputs` fails only on u02 `07600bc9`, whose bare `f(17)` gives an `execute_result`. Headings are `## Lesson N — Title`; Lesson 1 is cell 1 in every unit.
- **Running heads:** four unit titles exceed 32 characters (u03, u06, u10, u14, all "What Does This Program Do? (…)").
- **Task-copy audit** (35 questions against 324 exercises):
  - **CP1 Q4** is u02 Ex16 relabelled (f → g).
  - **CP1 Q8** "Base Palindromes" is stitched from two printed odd solutions, u01 Ex15 and Ex17.
  - **CP2 Q9** "Deepest Stack" extends u04 Ex16.
  - **CP3 Q9** "Letter Tree" extends u09 Ex8.
  - **CP2 Q1** shares its title "Infix to Postfix" with u04 Ex3.
  - **CP4 Q9** "Friend of a Friend" stitches u12 Ex17 (odd, printed) and Ex18 (found in plan review).
  - The short-answer near-matches (CP4 Q2, Q1, Q8; CP1 Q3; CP2 Q5) are the same category with new data, which is allowed.

## Phases

### Phase A — Tooling (Opus tooling subagent; each fix with a fixture test)

0. **A continuing guard for all three published books.** Before any change, capture a committed `tests/data/usaco-bronze-publish-baseline.json` for all four editions, plus an allowed-diffs file, and add `usaco-bronze` to `BOOKS` **and to the output-comparison test's own parameter list** in `tests/test_publication_regression.py` (it keeps an explicit two-book list, around line 89), so its output is actually compared. python-concepts, python-projects and *USACO Bronze* are then all checked in Phase E and by later tooling changes; any difference is listed with its reason.

1. **Lesson programs printed once.** All 51 ACSL lesson Try-its use `input()`, so none reads stdin, and plan 099's `stdin_run_asset` never reaches them.
   - **The fix:** the dedup extends to the plain `tryit` route, and explicitly **not** to `tryit+figure`/`figure`. python-concepts' only asset-identical `input()` Try-its are unit 06's three turtle cells with `sample_input`, which keep their output, so its baseline stays byte-identical.
   - All 48 ACSL matches name the asset in **both** the preceding cell ("saved as `assets/lN.py`") and the following run-line cell. `asset_blocks` for the preceding cell must look ahead to the next code cell and suppress the listing.
   - No extra "file name" line is printed; the run line already names the file.
   - The audit mirror (`_expected_lesson_kind`, and `stdin_tryits` / "listed again in full") gains the same `tryit` case.
2. **Chapter kicker reset.** The running heads are fine. What bleeds is the chapter kicker `\pubchapterlabel` (set through `pub-label`), which the answers appendix, Glossary, Quick Reference and Index never reset; python-concepts and *USACO Bronze* escape only because a project with an empty label comes last.
   - **The fix:** the answers appendix, Glossary and Quick Reference emit `{pub-label=""}` on their level-one heading. The Index is generated as a bare `\printindex`, which `pub-label` cannot reach, so the publisher emits an explicit reset (`\renewcommand{\pubchapterlabel}{}`, or the theme's equivalent) before `\printindex`. A rendered check confirms the Index opening page carries no "Checkpoint 4".
   - `glossary_page_numbers` then finds "Glossary" at the top of the page, and it must also resolve a one-page glossary.
3. **Page-number reading.** In `reference_findings`, a top-of-page integer counts as the folio only when it equals `physical − offset`, with the offset fixed from the first unit page; otherwise the page number is `physical − offset`. The u13 Ex19 case (physical 373, folio 363, whose text begins "Exercises" / "2") is a regression test.
4. **Quiet the SyntaxWarnings** in `code_span_names`.

### Phase B — Content fixes and checkpoint replacements (Opus content subagents; the replaced problems' solutions are written by a separate blind session)

- **Replace CP1 Q4, CP1 Q8, CP2 Q9, CP3 Q9 and CP4 Q9** with new problems of the same category and level that copy no unit task (CP4 Q9 "Friend of a Friend" stitches u12 Ex17's matrix parsing, odd and printed, to u12 Ex18's M² count). Each replacement of a checkpoint's programming problem keeps the rule that exactly one programming question comes last (`acsl-check`). Each gets:
  - a statement, `assets/qN.py`, and fixtures (sample, edge cases, and one modest scale case, from a seeded generator; the whole fold's fixtures stay under about 1 MB)
  - `verify`/answer entries, and updated teacher notes
  - for short answers: a new instance with a unique canonical answer, checked with the unit's `assets/verify/*_eval.py` helper
- **Retitle CP2 Q1** to a title no unit exercise uses.
- **Revise u04 Ex21** so its solution no longer equals `l1.py`.
- **Error demo:** tag u02 `7be73630` as `error-demo`.
- **u02 `07600bc9`:** print the value (for example `print(f(17))`).
- **Independence:** remove "with your teacher or club advisor" (u00 `56500fd0`).
- **Checkpoint openers:** write your answer "on paper or in your notebook". Self-checking:
  - **Short answers** have no samples. Mark the questions you were unsure of, then re-derive them with the unit's method (redo the trace or the truth table, or check the conversion both ways) and compare with a partner or a second attempt.
  - **The programming question** is checked against its sample, and against inputs of your own made from its constraints.
- **Print wording:** make the notebook-only lines print-neutral:
  - "run the cell" (u00 `ae5e434c`, u01 `l-023`, u03 `7dc53e50`, `d1aa0ec4`, u04 `l-018`)
  - "In the notebook…" (u00 `9878c129`, u03 `2d11cfac`)
  - "this cell is marked not to run in the notebook" (u00 `b7510c30`)
  - "This cell is marked not to run" (u02, around lesson.ipynb line 633)
  - "This cell runs a script" (u09, around line 151)
  - "This cell runs" (u13, around line 561) and "the cell above" (u13, around line 712)
  - and any other such line a final grep of the student PDFs finds ("this cell", "the cell above", "run the cell", "in the notebook")
- **Markup:**
  - Add the missing blank line before each of the 12 lists.
  - Rewrite the three table cells whose code holds `\|`, so no pipe needs escaping inside a table.
  - Remove the 32 `_Challenge._` lines.
  - Write `132_b` / `21_b` as `132` in base `b` (or `132₍b₎`), consistently in the lesson, exercise and solution.
  - Make the u08 `l-012` step table's "Law" column breakable, or reword it.
- **Teacher notes and syllabus:** remove "(design 009)" and "(no-exec)" from the teacher notes, and update the stale syllabus line.

### Phase C — Lesson outputs and panels

- `fill-outputs` for the 148 executable lesson cells; `lesson-outputs-check` passes twice.
- **Goals and recap (Opus):** in all 16 lessons, a `### You will learn` cell immediately before the first `## Lesson` cell and a `### Recap` **last** cell. The Recap goes after closing asides such as u04's "Optional aside: expression trees" and u11/u15's "Back to the door/robot", but summarises the core lessons. Both are in student voice, drawn from the teacher-notes goals, and division-aware ("Elementary and above: …" where a unit has an Elementary section).

### Phase D — Front and back matter, setup chapter, config

- **`acsl/publication.yaml`:**
  - setup: `docs/getting-set-up.md` + `docs/getting-set-up-teacher-notes.md`, `numbered: false`
  - `project_headers: {}`
  - `unit_headers` for u03, u06, u10 and u14: "WDTPD – Branching", "WDTPD – Looping", "WDTPD – Arrays", "WDTPD – Strings"
  - `lesson_heading: '^## Lesson\b'`
  - `index_names` for the names this book teaches
  - `audit`: `error_demo_ids: [7be73630]`; `print_page_target: 400` (the Student Print will warn at about 440 pages, which is expected, not chased); the other lists measured from the sources; `python assets/` exemptions for `[unit]`/`units/*` and `[setup]`/`docs/getting-set-up.md`
- **Front matter** (inline; Student Book independent):
  - `preface.md`
  - `how-to-use.md`:
    - the division ladder, and doing items at your division or below
    - the paths (Elementary, Junior, Intermediate and Senior, Classroom)
    - following the contest season: it names the season the book was written for, and points to acsl.org's schedule for current dates
    - short-answer practice (pencil, exact canonical answers, 30 minutes per six-question paper)
    - programming problems (`input()`, running with a sample file using the neutral form `python my_solution.py < sample.txt`, exact output)
    - the Challenges, and the practice checkpoints as self-tests
    - Answers to Selected Exercises
  - `for-teachers.md`
  - `answer-key-intro.md`, covering short answers and programs
- **Back matter:**
  - `glossary.md`: 19 entries in the standard format, with short terms and index aliases that appear in the introducing unit's prose.
    - Reuse *USACO Bronze*'s book-neutral text for 10 of the 12 shared ids.
    - Write ACSL-notation text for `boolean-algebra` and `bitwise-ops`, and new text for the 7 ACSL-only ids.
  - `quick-reference.md`: a notation card, with sections keyed `## Topic · Unit N`. It covers:
    - the pseudocode dialect (`int` = floor, inclusive substrings and `FOR`)
    - base notation, PIP precedence, and bit-string operators and precedence
    - LISP functions, Boolean notation `~ * + ⊕ ⊙`, and data-structure conventions
    - regex syntax, graph conventions, gates, and assembly opcodes
- **Setup chapter** (unnumbered "Getting Set Up") and its teacher notes, which also cover running a program and typing its input yourself (the self-checkers in u00, u01, u04 and u08 do this):
  - installing Python is in *Python by Projects* Unit 0
  - opening a terminal in a unit folder, and running `python assets/lN.py < assets/lN/1.in` or a solution with an input file (Windows Command Prompt, not PowerShell, for `<`)
  - comparing output exactly, and how fixtures check a program
  - practising short answers on paper
- **Enabling the book:** `books.yaml` gains `publication: true` for `acsl`; update `tests/test_books.py`.

### Phase E — VERIFICATION

1. `scripts/ci-local.sh` ALL GREEN in one solo run on the final commit.
   - Because `tools/` changes, all four publication books render in all four editions (about 60 minutes). Never overlap runs.
   - `lesson-outputs-check`, `judge-check`, `acsl-check` and `publish-audit` pass for every edition.
2. The python-concepts, python-projects and USACO Bronze outputs are unchanged, or any change is listed with its reason.
3. **Blind solves:** reviewers solve the replaced CP1 Q4, CP1 Q8, CP2 Q9, CP3 Q9 and CP4 Q9, and the revised u04 Ex21, from the statement, and run the solutions against the fixtures. They re-audit all 35 questions by task.
4. **Rendered-page review, covering all four editions:**
   - a unit opener with You will learn
   - an Elementary lesson and its exercises (u01, u04, u08 **and u12**)
   - a lesson with a Try-it printed once
   - a short-answer page with division tags, and its answer
   - a programming item
   - pseudocode, netlist, assembly and LISP pages; unit 08's overbars and the fixed table
   - a checkpoint opener and a question, CP4 Q9's replacement page, and the Teacher's checkpoint key
   - the back-matter running heads, the glossary and the index
   - a WDTPD running head, and the setup chapter
5. The post-execution report records page counts and the audit summary.

6. **Release doc.** Add a "Publishing a release" section to `output/README.md` with the essentials:
   - run `scripts/ci-local.sh --all-books`
   - tag `pdfs-<date>`, and run `gh release create <tag> --target <full SHA>` with `GH_TOKEN=$(cat .gh-token)`
   - asset names prefixed with the book id, since handouts share names across books
   - the Teacher's Edition is included, by the user's choice of 2026-09-29

**After plan 100 merges:**
- run `scripts/ci-local.sh --all-books`
- publish a new GitHub Release with every book's PDFs, following the `pdf-releases` convention

## Out of scope

- New curriculum beyond the named replacements and revisions.
- Duplicate unit exercise titles across units (u03 Ex11 and u10 Ex5, and so on); these are recorded as a follow-up.

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- The plan is built from a probe that inspected rendered pages and audited every checkpoint question by task. It applies plan 099's lessons from the start: the strict no-copy rule, modest fixtures, and digests for every already-published book.
- **N1 (noted):** CP2 Q9 and CP3 Q9 are each the checkpoint's single programming problem. Their replacements must keep ACSL's exactly-one-programming-question-last rule (`acsl-check`).

### Round 1 — verdicts and fold

- `[sol]` **REJECT**, 3 findings, all folded:
  1. The checkpoint self-check guidance is split: short answers (re-derive by the unit's method) and the programming question (samples and own inputs).
  2. The print-wording list adds u02, u09 and u13, plus a final grep.
  3. A committed *USACO Bronze* baseline and regression test make it a continuing guard.
- `[fable]` **REJECT**, 2 blockers and 9 nits, all folded:
  - **B1:** the Try-it dedup covers the plain `tryit` route (not turtle figures), looks ahead from the preceding cell, prints no extra name line, and has an audit mirror.
  - **B2:** CP4 Q9 is a stitched extension of u12 Ex17/18 and is added to the replacements.
  - **Nits:**
    - The kicker reset (`pub-label`) is the real mechanism.
    - The folio rule is defined.
    - How to Use uses the neutral run form.
    - The setup chapter covers typing input.
    - The contest-season wording won't date.
    - A release doc goes in `output/README.md`.
    - The 440-page print warning is expected.
    - The Recap goes after closing asides.
    - The review list gains the u12 Elementary lesson and CP4 Q9.

### Round 2 — verdicts and fold

- `[fable]` **APPROVE WITH NITS** (r2): every fold verified. Its 3 wording nits are folded: the Phase B sentence, u13's "the cell above" at line 712, and the release-decision date 2026-09-29.
- `[sol]` **REJECT** (r2), 2 findings, both folded:
  1. *USACO Bronze* is added to the regression test's output-comparison parameters, not only to `BOOKS`.
  2. The Index gets an explicit kicker reset before `\printindex`, since `pub-label` cannot reach it, with a rendered check.

## Content Review

## Post-Execution Report
_(filled before merge.)_
