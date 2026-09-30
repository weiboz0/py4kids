# Design 010 — Publication for every book

Status: proposed (2026-09-30).
Extends design 007 (book publication), which has so far been applied only to *Python, Concept by Concept* (plans 085, 089 and 090).

## 1. Purpose

User, 2026-09-30: "all books should have pdfs".
Today only `python-concepts` builds book PDFs, and only the two Python books build handouts and a syllabus.
This design extends the pipeline to *Python by Projects*, *Contest Python: USACO Bronze* and *Contest Python: ACSL*.

The user's decisions (2026-09-30):
- **Editions:** every book gets the same four editions as *Python, Concept by Concept*: `student-print`, `student` (with Answers to Selected Exercises), `answer-key` (the odd-numbered unit exercises) and `teacher`.
- **Goal panels:** every lesson in every book gets a "You will learn" panel and a "Recap" panel; they are authored where missing.
- **Setup chapter:** the contest books open with a short, **unnumbered** "Getting Set Up" chapter. It covers running programs with input files and the sample-and-fixture routine, and points to *Python by Projects* for installing Python. ACSL's Unit 0 stays Foundations.

A read-only survey (2026-09-30) found that the pipeline, the audit and the theme assume *Python, Concept by Concept* content:
- `render_items` skips an item's heading cell. That drops every statement in books that put the statement there: all contest items, and most *Python by Projects* exercises.
- `verify` cells print as code noise under answers.
- Contest solution programs (`assets/exN.py`) sit inside the student source boundary.
- `publish_audit.py` hard-codes cell ids, required Starters, turtle counts and banned phrases for that book.
- The fonts lack `⊕ ⊙`, subscripts, `✓ ✗` and `⌊ ⌋`.
- nbconvert and pandoc drop missing glyphs silently in handouts and syllabi.
- The handout and syllabus build is gated off for `judge` books for historical reasons only.

## 2. Decisions

- **D1 — A per-book publication config.**
  Each publication book gets a `publication.yaml` at its root, validated by `tools/books.py`. It holds every setting that is book-specific today:
  - **setup chapter:** its source file, whether it is numbered (python-concepts: "Unit 0 — Getting Set Up"; contest books: unnumbered "Getting Set Up"), and its teacher-notes file
  - **project running headers**, per project id (python-concepts: "Algorithm Challenge"; usaco-bronze: "Mock Contest"; python-projects: each project's own title)
  - **audit expectations:**
    - error-demo and hang-demo cell ids
    - print-required Starters
    - turtle try-it counts per unit and the Teacher's Edition drawing count
    - the per-book exemptions to the phrase bans, each scoped to the source files where the book teaches the phrase (for example `python assets/` in contest lessons, which is how students run their programs). The phrase stays banned everywhere else.
  - **index:** the set of Python names the index recognises

  The *Python, Concept by Concept* values move there **unchanged**. A regression guard proves that its four generated Quarto projects and its audit results are byte-identical before and after the move.
- **D2 — Item rendering for every book.**
  - An item's statement is read from its heading cell as well as from the cells after it.
  - The title is the first `###` heading that is not a structural subsection (`Input`, `Output`, `Constraints`, `Sample Input`, `Sample Output`, `Example`).
  - **Judge-book items:**
    - The `_Division: X and above._` line prints as a small division tag beside the title.
    - `### Input` / `### Output` / `### Constraints` / `### Sample …` become unnumbered run-in subheads, with the samples set as code blocks.
    - The `**Your answer:**` placeholder prints nothing. As design 007 decided, the book has no answer lines; students work in their notebooks or on paper.
- **D3 — Answers for every book.**
  - A short-answer item's answer is its worked markdown plus its `**Answer:**` line. `verify`-tagged cells are **never** printed in any edition.
  - A judge programming item's answer is its solution notebook's mirror cell, which `judge-check` enforces to be identical (apart from trailing whitespace) to `assets/exN.py` (units), `qN.py` (checkpoints, Teacher's Edition only) or `pN.py` (projects). It prints once.
  - Files matching `^(ex|q|p)\d+\.py$` under `assets/`, and `assets/verify/`, are **solution sources**. They are outside every student edition's source allowlist, except through `student_answer_sources` (odd-numbered unit exercises only).
  - The leak guard still applies.
  - The odd-number rule holds for every book. Where an odd answer's code repeats an even item's full solution, the item is changed (content plans), never the rule.
- **D4 — Glyphs.**
  - The theme uses luaotfload font fallback to DejaVu Sans and DejaVu Sans Mono, for any glyph the primary fonts lack, everywhere (prose, code blocks, headings, running heads). The ranges it must cover include: arrows, mathematical operators U+2200–22FF (`⊕ ⊙ ≤ ≥ ≠ −`), miscellaneous technical U+2300–23FF (`⌊ ⌋`), sub- and superscripts U+2070–209F, box drawing U+2500–257F, and dingbats U+2700–27BF (`✓ ✗`).
  - Handouts (nbconvert) and syllabi (pandoc) build with a template that uses the same body, mono and fallback fonts.
  - A **missing-glyph check** fails any PDF build whose LaTeX log reports a missing character. The book audit already fails; handouts and syllabi now fail too.
- **D5 — Handouts and syllabi for every book.**
  `scripts/ci-local.sh` builds handouts and the syllabus for every book, `judge` books included. The gate existed only because the contest book was never added.
- **D6 — Per-book content** (one content plan per book). Each book gets:
  - `front-matter/preface.md`, `how-to-use.md`, `for-teachers.md` and `answer-key-intro.md`
  - `back-matter/glossary.md`, covering exactly the book's unit `introduces` ids, and `back-matter/quick-reference.md`
  - its setup chapter and its teacher notes
  - stored lesson outputs (`fill-outputs`, `lesson-outputs-check`)
  - "You will learn" and "Recap" panels in every lesson
  - fixes for banned phrases and leaks

  The Student Book independence rule (design 007, plan 089 amendment) applies to every book.
  - The contest books' How to Use explains stdin programs, samples and fixtures, and the short-answer format.
  - ACSL's How to Use also explains divisions, the contest windows and paths.
  - ACSL's quick reference is a notation card: the pseudocode dialect, `⊕ ⊙ ↑ λ`, bit-string, LISP and assembly.
- **D7 — Build cost.**
  A book's four editions render in parallel in about 14 minutes (python-concepts recorded 187, 422, 639 and 847 seconds). Four publication books would add roughly 30–45 minutes to every `ci-local.sh` run.
  So `ci-local.sh` builds a book's editions only when the change touches that book; any change under `tools/`, `scripts/` or `books.yaml` builds every book. The user chose this on 2026-09-30 ("Only changed books"). `ci-local.sh --all-books` builds every book, and it is required before each GitHub Release.
  Handouts and syllabi are cheap and always build for every book. The `ci-local serial` rule (never two runs at once) stands.

## 3. Rollout

| plan | scope |
|---|---|
| 097 | **Tooling.** D1–D5. `publication.yaml` for python-concepts, with its regression guard (an immutable baseline and a reasoned allowed-diffs list). D2/D3 rendering and the solution-source boundary, tested on fixture books. The D4 glyph fallback and missing-glyph check. D5 handouts and syllabi for every book. No new book is flagged `publication: true` yet. A trial render of each other book in a scratch copy is reported, not gated. |
| 098 | ***Python by Projects*** content (D6), then `publication: true`. |
| 099 | ***Contest Python: USACO Bronze*** content (D6, with its contest setup chapter and leak fixes), then `publication: true`. |
| 100 | ***Contest Python: ACSL*** content (D6, with its setup chapter, notation quick reference and leak fix), then `publication: true`. |
| after 100 | A new GitHub Release with every book's PDFs (see the `pdf-releases` convention). |

## 4. Non-goals

- No change to design 007's decisions for *Python, Concept by Concept*. Plan 097's per-book config changes none of its output; D2/D3 fixes may change its output only in files listed with a reason against an immutable pre-change baseline.
- No per-contest split of the ACSL book (one book, as design 009 decided).
- No e-book or HTML edition.
