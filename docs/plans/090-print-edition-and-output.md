# Plan 090 — Book 1b print edition, separate Answer Key, and an `output/` folder

**Goal:** Split the Book 1b student materials into a **print edition** aimed at publication (lean, about 400 pages), a **full edition** for online use (unchanged and enriched), and a separate **Answer Key** PDF for students.
Every generated PDF of the repository lands in one root `output/` folder.

**Spec:** user decisions, 2026-09-28:
- "The student book is too large. We should have a simplified version vs a full version. The simplified version aims for publication, while the full version will be available online."
- "In the simplified version, let's remove the answer key. Review any other parts can be skipped. The goal is try to keep content less than 400 pages."
- "Full version still keep the same enriched."
- On which exercises to cut: "400 is a soft guardrail, keep all exercises for now."
- "Create an output folder at the repository root to put all generated pdfs."
- "Answers keys can be in separate pdf for students reference."
- "Structure of teacher book can be kept for now until future decision."

Amends design 007 (Phase A).

## Survey (Book 1b Student Book, plan 089 build: 658 pages)

| Part | Pages |
|---|---|
| Front matter (roman) | ~12 |
| Unit 0 | 6 |
| Lessons, 13 units | 162 |
| Core exercises | 97 |
| More Practice exercises | 81 |
| Challenge exercises | 72 |
| Checkpoints (5) | 30 |
| Algorithm Challenge | 10 |
| Answers to Selected Exercises | 178 |
| Glossary, Quick Reference, Index | 14 |

Of the exercise pages:
- **Starter panels:** 376 of them, about 45 pages, mostly panel chrome. Most repeat the comment scaffold or givens from the statement. **128 carry real code, and in ≥ 13 exercises the code exists only in the Starter**, e.g. the broken program of U1 Ex 20 and the U4 repair exercises. Those Starters stay in print (D1).
- **Blank pages:** about 20 near-blank pages, forced by `open=right` chapter starts.

**Estimate for the print edition:**
- 658 − 178 (answers) − ~45 (Starters and the 175 "Answer on page" lines) − ~20 (blank pages) ≈ **~415 physical pages (~405 numbered)**, measured by [fable]'s experiment: it stripped the generated `.tex` and compiled it three times.
- Every exercise is kept; 400 is a soft target, so the audit reports a warning, not a failure.

## Editions after this plan (Book 1b)

| Edition | Output file | Content |
|---|---|---|
| `student-print` | `Book1b-Student-Print.pdf` | Full student content minus the answers appendix, the "Answer on page N" lines and every **redundant** Starter panel (rule in D1). Chapters start on any page (`open=any`). How to Use says that the starting code is in the exercises notebook, and that answers are in the separate Answer Key PDF and the full edition, both online at the course page. The edition page reads "Student Book — Print Edition". |
| `student` (full) | `Book1b-Student.pdf` | Unchanged from plan 089 — lessons, all exercises with Starters, answers appendix with page cross-references. |
| `answer-key` | `Book1b-Answer-Key.pdf` | A short book: title and edition page, a one-page "Using this Answer Key", then the answers to the odd-numbered unit exercises. It is built with the same renderer as the full edition's appendix (Check lines, real programs, drawings). One chapter per unit ("Unit U — Title"); flat headings "Unit U, Exercise N — Exercise Title", with no page numbers (pages differ between editions). No checkpoint or Algorithm Challenge answers; no teacher material. |
| `teacher` | `Book1b-Teacher.pdf` | Unchanged structure (user: "kept for now until future decision"). |

**Independence (unchanged rule):** no student edition mentions a teacher or the Teacher's Edition.

## Phase A — Design amendment (inline)

Amend design 007 D4:
- The four Book 1b editions and their content, per the table above.
- The print edition's soft 400-page target.
- The `output/` folder.

## Phase B — Content (Opus subagent, statements/front matter)

- `book1b/front-matter/how-to-use.md`: edition-specific paragraphs, marked `<!-- edition: student-print -->` … `<!-- /edition -->` and `<!-- edition: student -->` … `<!-- /edition -->`. Text outside markers is shared.
  - **Print block:**
    - The "Reading the page" list drops the **Starter** bullet.
    - Keeps the Check-lines bullet.
    - Says: "Each exercise's starting code is in your exercises notebook; a few repair exercises print the code to fix."
    - Says: "Answers to the odd-numbered exercises are in the separate Answer Key. It and the full edition are online at the course page, github.com/weiboz0/py4kids."
  - **Full block:** keeps the current answers paragraph and the Starter bullet.
  - **Teacher's Edition:** gets the full (`student`) blocks, and must not claim "Answers to Selected Exercises" are at the back — a pre-existing inaccuracy fixed here.
  - Assumption recorded: the print edition accompanies the course files. The shared "Work in the course files" section stays; standalone distribution would need a later edit.
- `book1b/front-matter/answer-key-intro.md` (new): how to use the Answer Key honestly. Try first, compare after, and remember that a different correct program is fine when it reproduces the worked samples exactly. Also covers what the Check lines mean and why only odd-numbered exercises are included.
- No lesson or exercise notebook changes.

## Phase C — Solutions

None: the Answer Key reuses the existing solutions and the plan 089 answer renderer.

## Phase D — Tooling (Opus subagent)

- **D1 Editions.** An **edition profile** drives everything, instead of scattered `edition == 'student'` tests. The table `EDITIONS = {name: {student_family, starters, answers_appendix, answer_refs, classoption, output_name, edition_label, index}}` is consumed by the builder, the theme substitution (`@CLASSOPTION@`, `@OUTPUT@`, `@EDITION@`), `build-book.sh` and the audit.
  - `student`: `Book1b-Student`, "Student Book — Full Edition", `open=right`, starters, appendix, refs, index.
  - `student-print`: `Book1b-Student-Print`, "Student Book — Print Edition", `open=any`, redundant Starters omitted, no appendix or refs, index.
  - `answer-key`: `Book1b-Answer-Key`, "Answer Key", `open=any`, no index, no glossary or quick reference.
  - `teacher`: unchanged.
  - **Starter rule (print):** omit a Starter (units, checkpoints and the project) only when its non-comment, non-`pass` lines are empty **or every such line appears verbatim in that item's statement**. Otherwise print it. The inventory records omitted ones as `starter-omitted`.
  - **Edition blocks:** `<!-- edition: NAME -->` … `<!-- /edition -->` are filtered before heading demotion. An unknown or unclosed marker FAILs the build.
  - `tools/cli.py` `--edition` accepts `student`, `student-print`, `answer-key` and `teacher`.
  - `tools/publish.py` builds each edition into `bookN/build/publish/<edition>/`.
  - `student-print` shares the student allowlist and opens no solution sources. `answer-key` opens solutions **only** through `student_answer_sources` (odd unit exercises).
  - Edition-marked blocks in front-matter Markdown are filtered per edition.
  - `student-print`:
    - no answers chapter, no "Answer on page" lines, no `ans:` references
    - redundant Starter panels omitted per the Starter rule above (the statement, worked sample, Real version and Check yourself stay)
    - KOMA `open=any`
  - `answer-key`: front matter (title, edition page, `answer-key-intro.md`), then the answers by unit; no glossary, quick reference or index.
- **D2 Build.**
  - `scripts/build-book.sh --book book1b` builds all four editions.
  - The editions render sequentially, as now, or in parallel if it is safe; the implementer measures and states the time.
  - Each edition's draft-mode LaTeX audit pass still runs. Output names and the makeindex step come from the profile, and the key has no index.
  - Expected build-time impact: +12–15 min in ci-local.
- **D3 `output/`.**
  - `scripts/build-book.sh` and `scripts/build-pdf.sh` copy every final PDF into `output/<book>/`:
    - Book 1b: `Book1b-Student-Print.pdf`, `Book1b-Student.pdf`, `Book1b-Answer-Key.pdf`, `Book1b-Teacher.pdf`, `syllabus.pdf`, `handouts/<unit>.pdf`
    - Book 1: `syllabus.pdf`, `patterns.pdf`, `handouts/<unit>.pdf`
  - `output/<book>/` is cleared before copying, so renamed editions leave no stale PDFs. `bookN/build/` keeps intermediates.
  - `output/README.md` (committed) lists what each file is and which script makes it.
  - PDFs stay git-ignored: `*.pdf` is already ignored, and PDFs are built artifacts per AGENTS.md. `.gitignore` gains an explicit `output/**/*.pdf` line with a comment.
- **D4 Audit (`tools/publish_audit.py`), per edition via the profile, with sentinel tests.**
  - **Phrase bans are edition-specific.** Every student-family edition keeps the teacher-independence bans ("Teacher's Edition", "your teacher", …). The "Answer key" heading ban applies to `student` only (it guards the teacher-panel heading). "Answer Key" is allowed in the print edition's marked How to Use paragraph and throughout `answer-key`.
  - **Answer Key source boundary:** the edition opens only its front matter, `answer-key-intro.md` and `student_answer_sources`. A sentinel fails if any teacher note, teacher panel (`.teacher`), checkpoint/project solution or even-exercise solution enters it.
  - The leak guard scans every chapter of kind `answers`, not only the id `answers`.
  - **Print equivalence:** for every unit, the print `.qmd` equals the full-edition `.qmd` after removing the omitted Starter panels and the "Answer on page" lines. This is stronger than a heading check.
  - `answer-key` skips the index and glossary rules.
  - `student-print`:
    - no solution code at all (the leak guard with *every* solution as hidden)
    - no "Answer on page", no answers chapter, no `\pageref{ans:`
    - no Starter panels
    - independence phrase bans
    - every exercise heading of the full edition present (all tiers kept)
    - goals/recap panels
    - index and glossary rules
    - **page-count WARN** (not FAIL) above 400, printing the count
  - `answer-key`:
    - exactly the odd-numbered unit exercises
    - the leak guard for even, checkpoint and project solutions
    - independence phrase bans
    - no page cross-references
  - `student` and `teacher`: the plan 089 rules, unchanged.
  - The inventory/chapter-order check learns the two new editions.
- **D5 Tests:** edition filtering of marked blocks; print omits Starters and answer references; the answer-key contents and boundary; `output/` copy (script dry-run or a function test); CLI choices.

## Phase E — VERIFICATION

1. `scripts/build-book.sh --book book1b` builds all four editions. `publish-audit` PASS for each, with the print page count reported (target ≤ ~400, WARN only).
2. `output/` holds every expected PDF for Book 1 and Book 1b after `scripts/ci-local.sh`; `git status` shows no PDF to commit.
3. Print equivalence check PASS. Rendered-page review, including print U1 Ex 20 and a U4 repair exercise with their code kept:
   - print: How to Use, a unit's exercises without Starters, chapter starts without forced blanks, the index
   - Answer Key: intro, a Unit 6 answer with its drawing, a Check-line answer
   - full and Teacher: unchanged spot pages
4. `scripts/ci-local.sh` ALL GREEN. The post-execution report records page counts for all four editions and the build time.

## Out of scope

- Changing the Teacher's Edition structure
- Hosting the full edition or Answer Key online (publishing location is a later decision)
- Cutting exercises from print
- Book 1 and Book 2 editions (plan 086)

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- The verification phase is named; every user decision maps to a phase (editions D1, output D3, Answer Key D1/B, Teacher unchanged).
- Watch items:
  - The page estimate is ~400–410, so the soft warning may fire; that is acceptable per the user.
  - The build time grows by two renders (~+10 min in ci-local).
  - The Answer Key must not reuse full-edition page numbers.
  - The edition markers in How to Use need filtering in both student editions.

### Round 1 — verdicts

- `[sol]` **REJECT:**
  - the print edition and the key must say "Answer Key", which the current phrase ban forbids
  - the Answer Key needs a checked source allowlist and a teacher-material sentinel
- `[glm]` **APPROVE WITH NITS** (opencode-go/glm-5.3):
  - the same "Answer key" ban conflict
  - the print Starter bullet
  - the Answer Key structure
  - the survey label for index hits
  - the course-files assumption
- `[fable]` **APPROVE WITH NITS:**
  - Must Fix: a Starter rule that keeps unrepeated code (U1 Ex 20, U4 repairs); the "Answer key" ban
  - Should Fix: a real online location in the print wording; Answer Key titles and per-unit chapters; an edition profile instead of scattered literals; theme options and edition labels; build-book output names and index per edition; which blocks the Teacher's Edition gets; the Starter inventory record; a print equivalence check with rendered repair exercises
  - Measured the print edition at ~415 physical pages.

### Round 1 — fold

- `[FIXED]` all of the above:
  - the survey states ~415 and the Starter reality
  - the Starter rule
  - edition-specific bans with an allowance
  - the Answer Key source boundary and sentinel
  - an `EDITIONS` profile driving builder, theme, script and audit
  - labels "Student Book — Full Edition" / "— Print Edition" / "Answer Key"
  - Answer Key per-unit chapters with titled headings
  - print How to Use wording pointing at the course page (github.com/weiboz0/py4kids); where the PDFs are actually published is left to the user
  - Teacher's Edition blocks, fixing its false "answers at the back" line
  - `starter-omitted` records
  - the leak guard over `answers`-kind chapters
  - `output/` cleared before copy
  - the print equivalence check
  - repair exercises in the rendered review
  - build time +12–15 min

## Content Review
_(filled before PR.)_

## Post-Execution Report
_(filled before merge.)_
