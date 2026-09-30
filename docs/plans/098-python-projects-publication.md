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
- **Lessons:** they store no outputs (179 cells to fill) and have no "You will learn" / "Recap" panels (10 lessons).
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

### Phase A — Diagnose, then fix the tooling gaps this book exposes (Opus tooling subagent)

1. **Project scaffold cells.** Find why project-01's and project-02's scaffold code cells are absent from the generated `.qmd`, and fix the cause:
   - a **publisher gap** (for example, untagged brief code cells being dropped) is fixed in `tools/publish.py`, with a test
   - a **tagging problem** is fixed in the notebooks, in Phase B
2. **The `# Exercise` artefact check.** If it fires on text inside a code block, it is a false positive: fix the audit rule to ignore code blocks, with a test.
3. **Challenge titles.** Stretch items headed `## Challenge N: Title` (or with a `**Challenge:**` lead) get their title from that heading. A fixture test covers this. The notebooks are not reworded for this.

Both the tooling changes and python-concepts' regression digest are checked. Its generated output must not change; if it does, the change is listed in the allowed-diffs file with its reason.

### Phase B — Notebook fixes (Opus content subagent, one session)

- **Independence (design 007 plan-089 amendment):**
  - Rewrite every "your teacher" / "with your teacher" (u01, u03, u07) so the Student Book stands alone.
  - Rename u01's "Lesson One/Two/Three" headings to the book's lesson-heading form.
- **Phrases:**
  - Replace the `python assets/` run instructions in u03 and u05 with a book-appropriate form, or add a scoped exemption **only if** the phrase is taught there (a `phrase_exemptions` entry with a reason).
  - Remove "no-exec" from student prose (u06, u07, u10).
  - Remove "assert" from the flagged answer prose.
- **Leak:** change checkpoint-01 Question 6 so its answer no longer contains a whole solution the Student Book hides.
- **Error demos:** give each of the 6 `no-exec` program cells its correct tag (`error-demo` for deliberate errors) or its config entry, as the cell's purpose requires.
- **Cell ids:** make the unit-02 solution cell ids unique.
- **Glyphs:** replace 🚀 in the unit-01 solution with text.
- **Cross-references:** fix the 2 unresolved ones at their cause, whether a heading or a label.
- **Scaffolds:** any tagging fix Phase A's diagnosis calls for.

### Phase C — Lesson outputs and panels

- `py4kids-tools --book python-projects fill-outputs` stores every lesson's outputs; `lesson-outputs-check` must pass.
- **Goals and recap (Opus content subagent):** each of the 10 lessons gains one "You will learn" cell (just before its first lesson, after the hook) and one "Recap" cell (its last lesson cell), in the form python-concepts uses. The bullets come from that unit's `teacher-notes.md` goals and the lesson content, in student voice.

### Phase D — Front and back matter, setup chapter, config (inline + Opus)

- **`python-projects/publication.yaml`:**
  - setup numbered: "Unit 0 — Getting Set Up"
  - `project_headers`: Arcade Night, Grand Adventure (their titles)
  - `lesson_heading: '^## (Lesson\b|L\d+:)'`
  - audit expectations: this book's error and hang demo ids, turtle try-it counts per unit (unit 03), and the Teacher's Edition drawing count, all measured from the sources
  - phrase exemptions only as Phase B justifies
- **Front matter** (written inline; Student Book independent; edition blocks as python-concepts uses them):
  - `preface.md`
  - `how-to-use.md`: the project-first book, units opening with a thing to make, projects, checkpoints, Starters, Real version, Check lines, self-checking with Answers to Selected Exercises
  - `for-teachers.md`
  - `answer-key-intro.md`
- **Back matter:**
  - `glossary.md`: the 62 definitions reused from *Python, Concept by Concept*, re-keyed to this book's introducing units, with the wording checked against this book's lessons. It must cover exactly this book's unit `introduces` ids.
  - `quick-reference.md`: adapted from *Python, Concept by Concept*, with any name or feature this book does not teach removed.
- **Setup chapter:** `docs/unit-00-getting-set-up.md` and `docs/unit-00-teacher-notes.md`, adapted from *Python, Concept by Concept* (the folder `python-projects`; this book's Unit 1 checklist).
- **`books.yaml`:** `python-projects` gains `publication: true`.

### Phase E — VERIFICATION

1. `scripts/ci-local.sh` ALL GREEN in a solo run on the final commit. Because this plan changes `tools/` and python-projects, it renders both python-concepts and python-projects in all four editions:
   - `lesson-outputs-check` passes for python-projects
   - `publish-audit` passes all four editions: no missing glyphs, no overfull hbox over the limit, a clean leak guard, all phrase checks, and goals/recap
2. python-concepts' output still matches its baseline (plus any allowed diffs listed in Phase A).
3. The post-execution report records each edition's page count and the audit summary.
4. The content gate includes a rendered-page review: reviewers look at sampled page images from each edition (a unit opener, a lesson with outputs, an exercise, a project page, an answer page, the glossary), not only the source.

## Out of scope

- *USACO Bronze* (099) and *ACSL* (100).
- The GitHub Release (after plan 100).
- New exercises or lesson content beyond the fixes, panels and outputs above.

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- The plan works through plan 097's trial to-do list, one item at a time. Tooling gaps are diagnosed before notebooks change, and content is reused from *Python, Concept by Concept*'s glossary, quick reference and setup chapter where its concept ids match.
- **N1 (noted, not folded):** the "Lesson One" rename and the `## L1:` headings could be unified to a single lesson-heading form. The plan configures `lesson_heading` rather than renaming 4 units, to keep the notebooks' structure (and their tests) unchanged.

## Content Review

## Post-Execution Report
_(filled before merge.)_
