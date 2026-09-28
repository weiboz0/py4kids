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
- **Starter panels:** 376 of them, 1,445 code lines, about 45–55 pages. They repeat the comment scaffold that the exercises notebook already gives the student.
- **Blank pages:** about 20 near-blank pages, forced by `open=right` chapter starts.

**Estimate for the print edition:**
- 658 − 178 (answers) − ~50 (Starters) − ~20 (blank pages) − ~6 (answer cross-reference lines and the answers' index hits) ≈ **400–410 pages**.
- Every exercise is kept; 400 is a soft target, so the audit reports a warning, not a failure.

## Editions after this plan (Book 1b)

| Edition | Output file | Content |
|---|---|---|
| `student-print` | `Book1b-Student-Print.pdf` | Full student content minus: the answers appendix, the "Answer on page N" lines, the Starter panels. Chapters start on any page (`open=any`). How to Use says where the Starter code lives (the exercises notebook) and where answers are (the Answer Key PDF and the full online edition). |
| `student` (full) | `Book1b-Student.pdf` | Unchanged from plan 089 — lessons, all exercises with Starters, answers appendix with page cross-references. |
| `answer-key` | `Book1b-Answer-Key.pdf` | A short book: title and edition page, a one-page "Using this Answer Key", then the answers to the odd-numbered unit exercises. It is built with the same renderer as the full edition's appendix (Check lines, real programs, drawings). Headings read "Unit U, Exercise N" with no page numbers (pages differ between editions). No checkpoint or Algorithm Challenge answers; no teacher material. |
| `teacher` | `Book1b-Teacher.pdf` | Unchanged structure (user: "kept for now until future decision"). |

**Independence (unchanged rule):** no student edition mentions a teacher or the Teacher's Edition.

## Phase A — Design amendment (inline)

Amend design 007 D4:
- The four Book 1b editions and their content, per the table above.
- The print edition's soft 400-page target.
- The `output/` folder.

## Phase B — Content (Opus subagent, statements/front matter)

- `book1b/front-matter/how-to-use.md`: edition-specific paragraphs, marked `<!-- edition: student-print -->` … `<!-- /edition -->` and `<!-- edition: student -->` … `<!-- /edition -->`. Text outside markers is shared.
  - Print: "Each exercise's starting code is in your exercises notebook."
  - Print: "Answers to the odd-numbered exercises are in the separate Answer Key; the full edition online also includes them."
  - Full: keeps the current answers paragraph.
- `book1b/front-matter/answer-key-intro.md` (new): how to use the Answer Key honestly. Try first, compare after, and remember that a different correct program is fine when it reproduces the worked samples exactly. Also covers what the Check lines mean and why only odd-numbered exercises are included.
- No lesson or exercise notebook changes.

## Phase C — Solutions

None: the Answer Key reuses the existing solutions and the plan 089 answer renderer.

## Phase D — Tooling (Opus subagent)

- **D1 Editions.**
  - `tools/cli.py` `--edition` accepts `student`, `student-print`, `answer-key` and `teacher`.
  - `tools/publish.py` builds each edition into `bookN/build/publish/<edition>/`.
  - `student-print` shares the student allowlist and opens no solution sources. `answer-key` opens solutions **only** through `student_answer_sources` (odd unit exercises).
  - Edition-marked blocks in front-matter Markdown are filtered per edition.
  - `student-print`:
    - no answers chapter, no "Answer on page" lines, no `ans:` references
    - Starter panels omitted (the exercise's statement, worked sample, Real version and Check yourself stay)
    - KOMA `open=any`
  - `answer-key`: front matter (title, edition page, `answer-key-intro.md`), then the answers by unit; no glossary, quick reference or index.
- **D2 Build.**
  - `scripts/build-book.sh --book book1b` builds all four editions.
  - The editions render sequentially, as now, or in parallel if it is safe; the implementer measures and states the time.
  - Each edition's draft-mode LaTeX audit pass still runs.
- **D3 `output/`.**
  - `scripts/build-book.sh` and `scripts/build-pdf.sh` copy every final PDF into `output/<book>/`:
    - Book 1b: `Book1b-Student-Print.pdf`, `Book1b-Student.pdf`, `Book1b-Answer-Key.pdf`, `Book1b-Teacher.pdf`, `syllabus.pdf`, `handouts/<unit>.pdf`
    - Book 1: `syllabus.pdf`, `patterns.pdf`, `handouts/<unit>.pdf`
  - `bookN/build/` keeps intermediates.
  - `output/README.md` (committed) lists what each file is and which script makes it.
  - PDFs stay git-ignored: `*.pdf` is already ignored, and PDFs are built artifacts per AGENTS.md. `.gitignore` gains an explicit `output/**/*.pdf` line with a comment.
- **D4 Audit (`tools/publish_audit.py`), per edition, with sentinel tests.**
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
3. Rendered-page review:
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

## Content Review
_(filled before PR.)_

## Post-Execution Report
_(filled before merge.)_
