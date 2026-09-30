# Plan 098 — *Python by Projects*: publication content and PDFs

**Goal:** Give *Python by Projects* its four book editions (Student Print, Student Full, Answer Key, Teacher's Edition), built and audited clean by `scripts/ci-local.sh`.

**Spec:** design 010 (D6), design 007 with its plan 089 and 090 amendments, and plan 097's tooling.
User decisions, 2026-09-30:
- "all books should have pdfs"
- the same four editions for every book, with the odd-numbered answer rule
- goals and recap panels in every lesson

Plan 097's Phase E.3 trial render is this plan's to-do list.

## Survey (2026-09-30, main at d11bad2)

- **The book:** 10 units, 4 checkpoints, 2 projects (`project-01-arcade-night`, `project-02-grand-adventure`), and 62 concept ids.
  It shares its concept registry with *Python, Concept by Concept*, whose `variant_of` is this book. It has the `patterns` flag and builds `patterns.pdf`.
- **Missing inputs:**
  - `publication.yaml`
  - front matter: `preface.md`, `how-to-use.md`, `for-teachers.md`, `answer-key-intro.md`
  - back matter: `glossary.md`, `quick-reference.md`
  - the setup chapter `docs/unit-00-getting-set-up.md` and its `docs/unit-00-teacher-notes.md`
- **Lessons:** they store no outputs (180 executable cells to fill; 53 `no-exec` cells are skipped) and have no "You will learn" / "Recap" panels (10 lessons).
  Units 02, 04, 06 and 07 head lessons `## L1:` … rather than `## Lesson N`.
- **Trial audit findings** (plan 097 E.3, `student` edition, with stub matter):
  - **every unit:** goals/recap panels missing; glossary coverage (stubbed)
  - **error-demo tags differ:** 6 `no-exec` program cells, `8a9940ed` (u01), `cff23dfd` (u06), `b9137a93` (u07), `09e1db93` (u08), `c172f647` (u09) and `d1c787cd` (u10); each needs a tag or a config entry
  - **banned phrases:**
    - "your teacher" / "with your teacher": u01, u03, u07
    - "Lesson One": u01, and the title pages through it
    - `python assets/`: u03, u05
    - "no-exec": u06, u07, u10
    - "assert" in an answer
  - **solution leak:** checkpoint-01 Question 6
  - **project scaffold code cells missing from the PDF:** `menu-loop-scaffold`, `lucky-guess-scaffold`, … (0 of 4 appear in project-01). This is a publisher gap or a tagging problem, **diagnosed first**.
  - **item titles:** stretch items authored as `## Challenge N: …` or `**Challenge:**` render untitled (u08 item 21, u09 items 24–25, u10 items 25–26)
  - **cross-references:** `Unit 5 Exercise 16: answer page 227` and `Unit 10 Exercise 22: answer page 271` unresolved
  - **possible false positive:** a `# Exercise 1 — …` Python comment inside answer code flagged as a Markdown artefact
  - **missing glyph:** 🚀 (U+1F680) in a unit-01 solution
  - **duplicate cell ids:** `u2-ex8-heading` / `u2-ex8-code` in unit-02 `solutions.ipynb`
- **Reusable material:** *Python, Concept by Concept* has the same concept ids.
  - Its glossary definitions (62) can be reused, with each `*(Unit N)*` remapped to the unit that introduces the id **in this book**.
  - Its setup chapter (245 lines: installing Python, JupyterLab and Thonny) is book-neutral except for the folder name `python-concepts` and its closing "ready for Unit 1" checklist.
  - Its quick reference covers the same language.

## Phases

### Phase A — Tooling gaps this book exposes (Opus tooling subagent; each fix with a fixture test)

1. **Project scaffolds (a publisher gap, diagnosed in review).**
   - Both briefs are `## Milestone N` sections with untagged code cells. `item_groups` recognises only `Problem N`, so every cell lands in the preface, and the preface loop emits markdown only. The scaffold code is therefore dropped, and the projects' inventories are empty.
   - Fix: a project's preface code cells render as **Starter** panels and are inventoried as `starter`, which is what the audit's expected-codes rule already expects.
   - python-concepts' project uses Problems, so its output does not change.
2. **Colon-form item titles.**
   - `## Exercise N: Title` supplies the item's own title (units 08–10: 72 items render as bare `### Exercise N` today, and the answer key inherits the loss).
   - A leading `**Challenge:**` in a stretch item's statement is removed once the title comes from the heading.
   - python-concepts has no colon-form headings.
3. **Unnumbered challenge sections.**
   - Units 01–07 end their exercises with a `## Challenge` note followed by `### Challenge N: Title` problems that are not numbered exercises. Unit 08 has `## Challenge N: Title` at level 2.
   - **Rendering contract:** each `Challenge N` becomes a titled item ("Challenge N — Title") with the Challenge marker, its Starter if any, and its **Teacher's Edition answer** from the matching `### Challenge N` solution cells.
   - Challenges print no answers in the student editions (odd-numbered *exercises* only), as checkpoints do not.
   - Exercise numbering and counts are unchanged, so no notebook is renumbered.
   - The audit counts challenge items and checks their answer coverage in the Teacher's Edition.
4. **The Markdown-artefact check** runs over each generated `.qmd` **outside code fences**, not over the PDF text. Two answer-code comments `# Exercise N — …` falsely matched it; comments in code are not artefacts.
5. **Cross-reference attribution.** The audit's exercise-heading match (`publish_audit.py`, around line 425) is anchored to a whole heading line (`^Exercise (\d+)(?: — .*)?$`). Prose that wraps to begin a line with "Exercise 16's …" no longer steals the next "Answer on page" (the 2 trial findings).

python-concepts' output is checked against its baseline. Any change there is listed in the allowed-diffs file with its reason.

### Phase B — Notebook fixes (Opus content subagent, one session)

- **Independence (design 007 plan-089 amendment):**
  - Rewrite every "your teacher" / "with your teacher" (u01, u03, u07), and unit 02's `"(teacher peek) the secret is …"` output line.
- **Lesson headings:**
  - Rename u01's "Lesson One/Two/Three" and units 02, 04, 06 and 07's `## L1:` … headings to `## Lesson N: Title` (16 headings), so every unit's outline reads "Lesson N". `lesson_heading` stays `^## Lesson\b`.
  - Update any references to the renamed headings.
- **Checkpoint title:** checkpoint-01's first cell becomes an `# Checkpoint 1 — First Steps` H1, the other checkpoints' form (today it is bold text, and would print doubled).
- **Phrases:**
  - Replace the `python assets/` run instructions in u03 and u05 with a book-appropriate form, or add a scoped exemption only if the phrase is taught there, with a reason.
  - Remove "no-exec" from student prose (u06, u07, u10).
  - Remove "assert" from the flagged answer prose.
- **The checkpoint-01 Q6 "leak":** the solution cell is the question's own given line (`secret = 42`) behind a comment. Make that answer a markdown cell rather than code; the assessed question is unchanged.
- **The 6 `no-exec` program cells** are handled by what each one is:
  - a deliberate error gets `error-demo`
  - an infinite loop gets `hang-demo`
  - a fragment printed as a program goes in `error_demo_routing_exceptions`
  - a **runnable demonstration** loses `no-exec` and gains stored output
- **Cell ids:** make the unit-02 solution cell ids unique.
- **Glyphs:** replace 🚀 in the unit-01 solution with text.

### Phase C — Lesson outputs and panels

- **Seeding:** unit 02 ("The Computer Picks and Judges") calls `random.randint` in 4 executable lesson cells with no seed. Add one visible `random.seed(…)` cell before the first use, with a sentence on why, as python-concepts does. Stored outputs are then deterministic.
- `py4kids-tools --book python-projects fill-outputs` stores the outputs of the 180 executable lesson cells (the 53 `no-exec` cells are skipped). `lesson-outputs-check` must pass.
- **Goals and recap (Opus content subagent):** each of the 10 lessons gains the exact audit form:
  - the cell immediately before the first lesson-heading cell starts `### You will learn`
  - the notebook's last cell starts `### Recap`

  The Recap summarises the core lessons, not a closing Algorithm Extension. Bullets come from that unit's `teacher-notes.md` goals and the lesson content, in student voice.

### Phase D — Front and back matter, setup chapter, config (inline + Opus)

- **`python-projects/publication.yaml`**, every value measured from the sources:
  - the setup chapter, numbered
  - `project_headers`: Arcade Night, Grand Adventure
  - `lesson_heading: '^## Lesson\b'`
  - `index_names`: this book's taught names
  - `audit`:
    - `error_demo_ids`, `hang_demo_ids`, `error_demo_routing_exceptions`
    - `print_required_starters`: this book's broken-program Starters the print edition must keep, for example u10 Exercise 8
    - `print_page_target`
    - `turtle_tryits` (unit 03) and `teacher_turtle_drawings`
    - phrase exemptions, only as Phase B justifies them
- **Front matter** (written inline; Student Book independent; edition blocks as python-concepts uses them):
  - `preface.md`
  - `how-to-use.md`: the project-first book, units opening with a thing to make, projects with milestones, challenges, checkpoints, Starters, Real version, Check lines, and self-checking with Answers to Selected Exercises
  - `for-teachers.md`
  - `answer-key-intro.md`
- **Back matter:**
  - `glossary.md`: the 62 definitions reused from *Python, Concept by Concept*, re-keyed to this book's introducing units.
    - `*(Units a–b)*` ranges are **re-derived**, not renumbered.
    - The wording is **trimmed to what this book teaches** (for example, "Break and continue" and "List changes" mention `continue`, `insert`, `pop` and `remove`; drop any this book's lessons never use).
    - It covers exactly this book's unit `introduces` ids.
  - `quick-reference.md`: adapted with its section unit keys re-keyed to this book's units (`## Lists · Unit N`), and untaught names removed.
- **Setup chapter:** `docs/unit-00-getting-set-up.md` and `docs/unit-00-teacher-notes.md`, adapted from *Python, Concept by Concept*:
  - the folder name `python-projects`
  - this book's Unit 1 checklist
  - turtle references changed from "Unit 6" to this book's Unit 3, in the chapter and its teacher notes
- **Enabling the book:**
  - `books.yaml`: `python-projects` gains `publication: true`.
  - Update the pinned expectation in `tests/test_books.py` (the `publication` set), and check `tests/test_ci_scope.py`.

### Phase E — VERIFICATION

1. `scripts/ci-local.sh` ALL GREEN in **one solo run** on the final commit; never overlap two runs.
   - Because the plan changes `tools/`, the run renders python-concepts **and** python-projects in all four editions: roughly 15 minutes of rendering each, in parallel within a book.
   - `lesson-outputs-check` passes for python-projects.
   - `publish-audit` passes all four editions: no missing glyphs, no overfull hbox over the limit, a clean leak guard, the phrase checks, and goals/recap.
2. python-concepts' output still matches its baseline, plus any allowed diffs listed in Phase A.
3. The post-execution report records each edition's page count and the audit summary.
4. **Rendered-page review in the content gate:** reviewers look at sampled page images from each edition, not only the source:
   - a unit opener, a lesson with outputs, an exercise with a colon-form title
   - **the checkpoint-01 opener**
   - **an unnumbered-challenge page**, and a project milestone page with its Starter
   - an answer page, and the glossary

## Out of scope

- *USACO Bronze* (099) and *ACSL* (100).
- The GitHub Release (after plan 100).
- New exercises or lesson content beyond the fixes, panels and outputs above.

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- The plan works through plan 097's trial to-do list, one item at a time. Tooling gaps are diagnosed before notebooks change, and content is reused from *Python, Concept by Concept*'s glossary, quick reference and setup chapter where its concept ids match.
- **N1 (superseded by [fable] 11):** the plan now renames the headings rather than configuring a second form.

### Round 1 — verdicts and fold

- `[sol]` **APPROVE WITH NITS**, 4 nits, all folded:
  1. `index_names`, `print_required_starters` and `print_page_target` are in the config list.
  2. Glossary and quick-reference wording is trimmed to what this book teaches.
  3. The setup chapter's turtle references change from Unit 6 to Unit 3, in the chapter and its teacher notes.
  4. The survey count is 180 executable cells.
- `[fable]` **REJECT**, 7 blockers and 8 nits, all folded:
  1. Unit 02's unseeded `random` gets a visible seed cell, and its "teacher peek" line is rewritten.
  2. Checkpoint-01 gets an H1.
  3. The artefact check moves to `.qmd` outside fences (tooling).
  4. Cross-references are a heading-match false positive, fixed in the audit.
  5. Colon-form `## Exercise N: Title` titles (72 items).
  6. Unnumbered challenge sections get a rendering contract, with Teacher's answers.
  7. Project scaffolds are a publisher gap, fixed as Starter panels.
  8. `tests/test_books.py` is updated.
  9. Q6's answer becomes a markdown cell.
  10. = `[sol]` 1.
  11. The lesson headings are renamed, not configured.
  12. The Recap covers the core lessons.
  13. Glossary ranges are re-derived and quick-reference keys re-keyed.
  14. A runnable demo loses `no-exec`.
  15. CI expectations are stated, and the review samples include the checkpoint-01 opener and a challenge page.

## Content Review

## Post-Execution Report
_(filled before merge.)_
