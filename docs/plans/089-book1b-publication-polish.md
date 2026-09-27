# Plan 089 — Book 1b: publication polish (independent Student Book, back matter, book voice)

**Goal:** Make the two Book 1b PDFs read like finished books.
The **Student Book stands alone** — no teacher, no Teacher's Edition — and carries its own self-study answers.
Both editions gain front and back matter (edition page, preface, glossary, quick reference, index), per-unit
goals and recaps, and lose the notebook/authoring voice and internal jargon found by the reader reviews.

**Spec:** user decisions 2026-09-27:
- "Continue to polish plan", with every item in scope: builder and wording fixes, unit goals and recaps,
  glossary and quick reference, index, self-study answers;
- "We should assume independence of the student book without referencing the teacher or teacher book".

Findings come from the [sol]/[fable] reader reviews of 2026-09-27; the list is recorded in the Round 0 section below.
Design 007 (book publication) is amended in Phase A.

## Survey (current build, 2026-09-27)

- **Student Book teacher references:**
  - "The full program is in the Teacher's Edition." ×380
  - 37 "There is no real program for this …" panels
  - "your teacher / with your teacher" ×6: U00 ×2, U01 ×2, U02, U06 opener
- **Notebook/authoring voice in student pages:**
  - "tagged `no-exec` so the notebook will not ask for answers when it runs automatically"
  - "this interactive cell is not run when the notebook executes"
  - "your CELL first writes …"
  - "Put the repaired program in the empty cell"
  - "check the worked answer in solutions.ipynb"
  - `# turtle-check: open-path` in printed code (9)
  - "Run `python assets/…`" ×26 (U07–U13)
- **Naming:**
  - "Lesson One/Two/Three" in U01–U05; "Lesson 1/2/3" from U06 on
  - Unit 8 title "Randomness — Dice, …" gives a double dash in "Unit 8 — Randomness — …"
  - "(not graded)" ×39 on checkpoint Real-version lines
  - U02's "Peek ahead — not needed for the exercises" heading appears in the contents
- **Teacher's Edition:**
  - "(checked by the course's test suite)" after ~367 answers
  - Teacher-notes jargon: `no-exec` ×35, "design 006" ×19, "plan 08x" ×12, "git-ignored" ×5, `turtle-check` ×3, CI, fastforward, `practices:`
- **Answer-key bugs:**
  - The publisher drops every `assert` line. Where the call under test lives inside the assert, the printed answer loses it; e.g. Algorithm Challenge Problem 11 reads `p11_out.txt` without ever calling `running_totals_to_file`.
  - U06's key lists `solutions_ex10.py`–`solutions_ex18.py` under Exercise 1, because the glob `solutions_ex1*` matches them.
- **Missing:**
  - copyright/edition page, preface
  - glossary, quick reference, index
  - per-unit goals and recaps
  - any answers in the Student Book

## Phase A — Design amendment (inline)

Amend `docs/designs/007-book-publication.md`:
- **D4 (editions):**
  - The Student Book is **independent**. It never refers to a teacher or to the Teacher's Edition.
  - It carries **Answers to Selected Exercises**: every **odd-numbered unit exercise**. Checkpoints and the Algorithm Challenge stay without answers because they are assessments.
  - The Teacher's Edition keeps full answer keys.
- **D3 (routing):**
  - The Real-program convention is explained once in How to Use.
  - "No real program" panels are dropped.
  - `assert` lines render as **Check** lines in place: "`call` → `expected`".
  - `# turtle-check:` directive comments are stripped from printed code.
- **D5/D6:**
  - front matter: edition page, preface, How to Use
  - back matter: glossary, quick reference, index
  - "You will learn" / "Recap" panels
  - the audit rules added in Phase D

## Phase B — Content (Codex gpt-6-sol; lessons and statements)

Authoritative contract for the publisher (Phase D):
- A unit's goals are a lesson markdown cell whose first line is `### You will learn`. It sits **directly after the opening project-hook cell(s)** and **before the first lesson heading**, so the hook still comes first (project-first law).
- A unit's recap is the **last lesson cell**, whose first line is `### Recap`.

**B1 — Student-voice pass** (all Book 1b `lesson.ipynb`, `exercises.ipynb`, checkpoint and project notebooks,
`book1b/docs/unit-00-getting-set-up.md`):
- Remove every teacher reference: "your teacher", "with your teacher", "ask your teacher", "Teacher's Edition".
  - Rephrase for an independent learner; e.g. Unit 0 becomes "ask a parent or whoever manages the computer", and the chip question points to **About This Mac**.
  - Story characters who happen to be teachers ("A teacher needs the arithmetic mean…") stay.
- Rewrite authoring voice in book voice:
  - `no-exec`, "when the notebook executes / runs automatically", "your CELL", `solutions.ipynb` → neutral phrasing.
  - "the empty cell" → "an empty cell in your exercises notebook".
  - Genuine JupyterLab teaching (running a cell in Unit 1, File ▸ Save) stays.
- Replace "Run `python assets/X.py`" with "Run `assets/X.py`", using the py/python3 convention that How to Use explains.
- Naming:
  - "Lesson One/Two/Three" → "Lesson 1/2/3" (U01–U05)
  - Unit 8 title → "Randomness: Dice, Simulations, and a Wandering Turtle"
  - drop "(not graded)" from checkpoint Real-version lines
  - U02's "Peek ahead" becomes a bold lead-in inside a Notice (no heading), so it leaves the contents
- Nothing else in specifications, samples, or code changes. All existing checks stay green.

**B2 — Unit goals and recaps** (13 lesson notebooks):
- `### You will learn`: 3–5 student-voice bullets naming the concepts the unit introduces (its manifest `introduces:`) in plain words, consistent with the teacher notes' Goals.
- `### Recap`: 4–6 bullets restating each idea with one tiny code reminder where useful, plus one "You can now…" line naming the unit project.
- Only concepts taught by that unit or earlier; no code that needs execution (markdown only).

**B3 — Front and back matter sources** (new files, student voice, semantic line breaks):
- `book1b/front-matter/preface.md` ("About This Book"):
  - what Book 1b is (concept by concept, for complete beginners)
  - how to study alone
  - what you need (a computer, Unit 0)
- `book1b/front-matter/how-to-use.md` (rewrite; no teacher references):
  - legend matching the panels actually printed: Program/Output, Notice, Try it yourself, Read the error, Pictures from code, Starter, Data file, Check lines, Real version
  - how to run a program file (`py` / `python3` from the unit folder, pointing to Unit 0)
  - where to write exercises (the unit's `exercises.ipynb` in the course files)
  - the Real-version convention, stated once
  - the answers at the back (odd-numbered exercises) and how to use them honestly
  - a course-files folder map (`book1b/units/unit-NN-…/lesson.ipynb`, `exercises.ipynb`, `assets/`)
- `book1b/back-matter/glossary.md`:
  - one entry per concept id introduced by a Book 1b unit manifest (`book1b/curriculum/concepts.yaml` names), in the form `**term** — definition. *(Unit N)*`, alphabetical
  - each definition is one or two sentences for a beginner and uses only earlier terms
  - an optional `<!-- index: key1; key2 -->` comment lists extra index keys
- `book1b/back-matter/quick-reference.md`:
  - 2–3 printed pages of the syntax Book 1b teaches, grouped by topic (output, variables, numbers, decisions, loops, turtle, functions, random, strings, lists, dictionaries, files, classes)
  - each group names its unit
  - only constructs a Book 1b unit teaches

**B4 — Teacher-notes jargon** (inline, active session): rewrite the listed jargon in all Book 1b teacher notes (units, checkpoints, project, Unit 0, `for-teachers.md`) in classroom voice.
- `no-exec` → "not run automatically".
- Drop design and plan citations.
- "git-ignored scratch files" → "scratch files the program creates".
- Checker names are replaced by what the teacher should do.
- Pedagogy stays unchanged.

## Phase C — Solutions

No new solutions: the self-study answers reuse the existing, CI-executed solutions notebooks.
The Problem 11 fix is a publisher change (D3 below); its solution code is correct and unchanged.

## Phase D — Tooling (Codex gpt-6-sol)

- **D1 Student independence (`tools/publish.py`):**
  - Student Book: drop the "The full program is in the Teacher's Edition." sentence and any "no real program" note.
  - Real-version statement lines render as written, minus a trailing "— see the solution".
  - Both editions drop "There is no real program …" panels.
- **D2 Answers to Selected Exercises:**
  - The Student Book gains a back-matter chapter with, per unit, the answers to odd-numbered exercises. It is built with the existing answer-key renderer in student mode: solution cells and the real program; turtle drawings included; no teacher panels.
  - Cross-references: each exercise heading gets a LaTeX `\label`. An odd exercise in the Student Book ends with "Answer on page N". Each answer heading reads "Exercise N (page M)". The Teacher's Edition answer keys also show "(page M)".
- **D3 Check lines:**
  - Parse solution code with `ast`. Split the code block at each top-level `assert` and render it in place as a **Check** line: `assert A == B` → "Check: `A` → `B`"; other asserts → "Check: `expr` is true" (source text via `ast.get_source_segment`). Code before and after stays in order.
  - Remove "(checked by the course's test suite)".
  - Test: the Problem 11 answer shows the `running_totals_to_file(...)` call before reading `p11_out.txt`.
- **D4 Answer-key grouping:** match `solutions_ex{N}` followed by a non-digit, so Exercise 1 no longer lists Exercise 10–18 assets. Test on U06.
- **D5 Front matter:**
  - edition page after the title: title, "Book 1b — Year 1", "First edition, 2026", "Copyright © 2026 Weibo Zhou", "Written for Python 3.12 or newer" (per Unit 0), course files `https://github.com/weiboz0/py4kids` (folder `book1b/`)
  - then Preface, then How to Use
  - the Teacher's Edition additionally keeps For Teachers
- **D6 Panels:** new `goals` and `recap` panel kinds (tcolorbox in `theme.tex` / `panels.lua`), routed from the B contract headings.
- **D7 Back matter (both editions):**
  - order: Answers to Selected Exercises (Student only), Glossary, Quick Reference, Index
  - Index:
    - `imakeidx`; the publisher inserts `\index{…}` at the **first prose occurrence** (not in code or LaTeX) of each glossary term and its extra keys in each unit, plus a `\index{…}` at the glossary entry
    - Python names such as `print`, `input`, `range` are indexed as `\texttt` subentries
    - `scripts/build-book.sh` guarantees the makeindex pass: a Quarto run, if it runs makeindex itself (verified by a spike), otherwise an explicit `lualatex`/`makeindex` rerun on the kept `.tex`
- **D8 Printed code:** strip lines that are only a `# turtle-check:` directive.
- **D9 `tools/publish_audit.py` rules:**
  - Student Book: no `Teacher's Edition`, `your teacher`, `with your teacher`, `ask your teacher`, `no-exec`, `solutions.ipynb`, `python assets/`, `Lesson One`, "checked by the course's test suite", "There is no real program"
  - both editions: every unit has one goals and one recap panel, in the contract positions
  - the Student answers chapter covers exactly the odd-numbered exercises of every unit
  - every Book 1b-introduced concept id has a glossary entry
  - the index is non-empty and every glossary term appears in it
  - chapter count updated
  - sentinel tests for each rule
- **D10 Checks:**
  - `structure-check` / `cell-lint` accept the two new markdown cells
  - the concept scan applies its normal rules to them: a goals cell names only the unit's own introduced concepts, and a recap uses only concepts taught by then
  - pytest for D1–D9

## Phase E — VERIFICATION

1. All existing checks PASS: `lesson-outputs-check`, `turtle-real-check`, `turtle-check`, structure, hygiene, noexec, concept-scan, cell-lint, prereq and coverage.
2. Both books build, and `publish-audit` PASS with the new rules.
3. A grep of the Student Book PDF text finds no teacher/Teacher's-Edition reference except story characters, and none of the banned authoring phrases.
4. Rendered-page review:
   - edition page, preface, How to Use
   - a unit opener with its hook, then goals; a recap
   - an odd exercise's "Answer on page N" and the page it points to
   - Problem 11 in the Teacher's Edition
   - U06 answer key Exercise 1
   - glossary, quick reference, index
5. `scripts/ci-local.sh` ALL GREEN; post-execution report.

## Out of scope

- figure numbering and cross-referenced figures
- blank-page and page-break tuning
- renaming "Starter"
- an edition-specific release tag or QR code (the edition page names the repository and folder)
- Book 1 and Book 2 editions (reserved plan 086)
- Book 1 (non-b) content

## Plan Review

### Round 0 — reader-review findings (2026-09-27, [sol]/[fable]) addressed

- Front and back matter missing; unit objectives and recaps missing; no self-study answers.
- "Real program … Teacher's Edition" boilerplate; notebook and repository voice; teacher-facing text on student pages.
- Teacher's Edition jargon; Lesson One vs Lesson 1; U06 answer-key ordering; the Problem 11 answer key.

### Round 1 — `[self]` APPROVE WITH NITS

- Verification phase named (Phase E); every surveyed finding maps to a phase (B1 voice/naming, B2 goals/recaps,
  B3 front/back matter, B4 teacher jargon, D1–D10 builder/audit); Phase C exemption stated.
- Watch items for reviewers: the answers appendix size (odd exercises only, roughly +150–200 pages); whether
  Check lines read well for multi-line asserts; the index automation (first prose occurrence per unit) may
  over- or under-index; the goals cell must not precede the project hook.
- `[glm]` skipped for this gate by user decision (2026-09-26: "skip glm reviewer for 1 day, then use
  volcengine-plan/glm-5.3"); from 2026-09-28 the seat returns.


## Content Review
_(filled before PR.)_

## Post-Execution Report
_(filled before merge.)_
