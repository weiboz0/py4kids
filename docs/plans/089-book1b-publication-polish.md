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
  - "The full program is in the Teacher's Edition." ×343
  - 37 "There is no real program for this …" panels
  - "your teacher / with your teacher" ×11: U00 ×7, U01 ×2, U02, U06 opener
  - checkpoint prefaces: "the way a contest problem does — it is not graded" ×5; U08 "Seed 4 makes this/our classroom result" ×2
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
  - "(not graded)" ×34 on checkpoint Real-version lines
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
- A unit's goals are a lesson markdown cell whose first line is `### You will learn`. It is the cell
  **immediately before the first cell starting with `## Lesson`**, so the hook and everything before the
  first lesson (preview code, Notices) still comes first (project-first law). Machine-checkable.
- A unit's recap is the **last lesson cell**, a markdown cell whose first line is `### Recap`.
- The publisher consumes both heading lines as panel titles (D6) — they never become headings or bookmarks.
- Scope: the 13 unit lessons; the Unit 0 setup chapter has neither (it is a setup chapter, not a unit).

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
  - drop "(not graded)" from checkpoint Real-version lines and "— it is not graded" from the five checkpoint
    prefaces; U08 "classroom result" → neutral ("the same result every time")
  - U02's "Peek ahead" becomes a bold lead-in inside a Notice (no heading), so it leaves the contents
- Nothing else in specifications, samples, or code changes. All existing checks stay green.

**B2 — Unit goals and recaps** (13 lesson notebooks):
- `### You will learn`: 3–5 student-voice bullets naming the concepts the unit introduces (its manifest `introduces:`) in plain words, consistent with the teacher notes' Goals.
- `### Recap`: 4–6 bullets restating each idea with one tiny code reminder where useful, plus one "You can now…" line naming the unit project.
- Only concepts taught by that unit or earlier ("earlier" = in teach order, not alphabetical); markdown only.
  Concept use in these cells is enforced by content-gate review: Book 1b's concept scan does not read markdown
  cells, and this plan does not change that.

**B3 — Front and back matter sources** (new files, student voice, semantic line breaks):
- `book1b/front-matter/preface.md` ("About This Book"):
  - what Book 1b is (concept by concept, for complete beginners)
  - how to study alone
  - what you need (a computer, Unit 0)
- `book1b/front-matter/how-to-use.md` (rewrite; no teacher references):
  - legend matching the panels actually printed: Program/Output, Notice, Try it yourself, Read the error,
    Watch out: this never stops, Pictures from code, Starter, Data file, Challenge, Check lines, Real version,
    You will learn / Recap
  - how to check checkpoints and the Algorithm Challenge alone: every question has worked samples; your
    program is right when it reproduces them exactly (no printed answers — they stay self-tests)
  - how to run a program file (`py` / `python3` from the unit folder, pointing to Unit 0)
  - where to write exercises (the unit's `exercises.ipynb` in the course files)
  - the Real-version convention, stated once
  - the answers at the back (odd-numbered exercises) and how to use them honestly
  - a course-files folder map (`book1b/units/unit-NN-…/lesson.ipynb`, `exercises.ipynb`, `assets/`)
- `book1b/back-matter/glossary.md`:
  - one entry per concept id introduced by a Book 1b unit manifest (62 ids), alphabetical by term, each entry
    one line `**term** — definition. *(Unit N)*` followed by a comment
    `<!-- concept: <id>; index: key1; key2 -->` (`index:` optional). The **term is student-facing**, chosen by
    the author (e.g. `transform-each` → "map (do the same to each item)"), not the registry name; the audit
    matches by the `concept:` id
  - each definition is one or two sentences for a beginner and uses only terms taught by that unit or earlier
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
  - Remove the now-dead `(design 006 D9 genres)|(plan 0\d\d)` rewrites in `teacher_notes()` after B4.
- **D2 Answers to Selected Exercises (Student Book only):**
  - **Source boundary:** a new checked path, `student_answer_sources(entry)`, is the *only* way the student
    edition opens solution material. It serves unit entries only (never checkpoints or the project), and returns
    only the solutions-notebook groups and `solutions_ex{N}` assets for **odd** N. `allowed_source()` keeps
    denying everything else; `tests/test_publication_phase_b.py` is amended to assert exactly this boundary.
  - **Leak guard (audit + test):** no solution code from an even-numbered exercise, a checkpoint or the project
    appears anywhere in the Student Book `.qmd`. Unit of comparison: each printed code block's `code_tokens`
    stream against each such solution cell/asset stream. A block FAILs if it **equals** a solution stream, or
    if it contains a contiguous run of **≥ 20 tokens** from one that does not also occur in that item's
    student-visible sources (its statement, starter and the unit lesson), so starter overlap is not a leak.
    A genuine coincidence fails loudly and is fixed in content; there is no allowlist. Tests cover a whole-cell
    leak, a partial (fragment) leak and a starter overlap that must pass. The literal "Answer key" heading stays banned in the Student Book; the new
    chapter is titled "Answers to Selected Exercises".
  - Content per odd exercise: solution cells (with Check lines, D3), the real program with its Sample input
    and drawing, and solution assets with drawings. No teacher panels; code at `\footnotesize`.
  - **Labels:** explicit, edition-unique `\label{ex:<entry-id>:<N>}` at each exercise heading and
    `\label{ans:<entry-id>:<N>}` at each answer heading. An odd exercise in the Student Book ends with
    "Answer on page \pageref{ans:…}"; each answer heading reads "Exercise N (page \pageref{ex:…})". The
    Teacher's Edition answer-key headings also show "(page \pageref{ex:…})".
- **D3 Check lines (both editions):**
  - Parse solution code with `ast`. **Top-level** `assert` statements split the code into fragments at
    `lineno`/`end_lineno`, preserving the source's own lines (blank lines kept).
    - Each assert renders in place as "Check: `A` → `B`" for `assert A == B`, else "Check: `expr` is true" (`ast.get_source_segment`).
    - Multi-line asserts collapse to one line.
    - Each fragment is its own code box, so a cell with several asserts becomes several boxes and Check lines, in order.
  - **Nested asserts** (inside `if`/`for`/`def` bodies) stay as code unchanged, so every block keeps a valid
    body. Today they occur only in Checkpoint 2, which appears only in the Teacher's Edition. The Student
    answers contain no `assert` (audit).
  - Remove "(checked by the course's test suite)".
  - Tests:
    - Problem 11 shows the `running_totals_to_file(...)` call as a Check before reading `p11_out.txt`.
    - A nested assert in a loop stays intact.
    - A side-effecting call inside an assert is shown as its Check, in the right order.
    - Blank lines are preserved.
- **D4 Answer-key grouping:** match `solutions_ex{N}(?!\d)`, so Exercise 1 no longer lists Exercise 10–18
  assets (the `solutions_ex1_square.py` fixture still matches). Test on U06.
- **D5 Front matter:**
  - The edition page goes on the title verso via scrbook `\uppertitleback`/`\lowertitleback` in `theme.tex`. It carries:
    - title
    - "Book 1b — Year 1"
    - "First edition, 2026"
    - "Copyright © 2026 Weibo Zhou"
    - "Written for Python 3.12 or newer"
    - course files `https://github.com/weiboz0/py4kids` (folder `book1b/`)
  - Then Preface, then How to Use. The Teacher's Edition additionally keeps For Teachers.
- **D6 Panels:** new `goals` ("You will learn") and `recap` ("Recap") panel kinds (tcolorbox in `theme.tex`,
  `panels.lua`). The `### …` heading line is consumed as the panel title, emitting no heading or bookmark.
- **D7 Back matter (both editions):**
  - Order: Answers to Selected Exercises (Student only), Glossary, Quick Reference, Index.
  - Index:
    - `\usepackage{imakeidx}\makeindex[intoc]` goes in the header.
    - The Index chapter is its own file (not `index.qmd`) containing only `\printindex` (no extra heading).
    - Quarto 1.6.42 runs makeindex itself ([fable] spike).
    - The publisher inserts `\index{…}` at the **first prose occurrence per unit** of each glossary term and its `index:` keys, plus one at the glossary entry. Matching is word-bounded and case-insensitive, and never falls in code, LaTeX blocks or headings.
    - Python names (`print`, `input`, `range`, …) index as `\texttt` subentries.
  - `scripts/build-book.sh`: the `-draftmode` audit passes run `makeindex` between passes so the index pages
    are audited; the delivered PDF is the Quarto render (non-draft).
- **D8 Printed code:** strip lines that are only a `# turtle-check:` directive (both editions).
- **D9 `tools/publish_audit.py` rules (each with a sentinel test):**
  - Student Book text contains none of the following (checked on the `.qmd` and on the PDF text, with the PDF's
    curly apostrophes ’ normalised to '):
    - `Teacher's Edition`, `your teacher`, `Your teacher`, `with your teacher`, `ask your teacher`
    - `not graded`, `no-exec`, `solutions.ipynb`, `python assets/`, `Lesson One`
    - "checked by the course's test suite", "There is no real program", "Answer key"
    - `assert` (in the answers chapter)
  - The D2 leak guard.
  - Both editions: each of the 13 units has exactly one goals panel, the last block before the first
    `## Lesson` heading in the unit `.qmd`, and one recap panel, the last block before `## Exercises`.
  - The Student answers chapter covers exactly the odd-numbered exercises of every unit (175 today).
  - Every Book 1b-introduced concept id has one glossary entry (by `concept:` comment).
  - The index is non-empty and contains every glossary term.
  - The LaTeX log has no `multiply defined` labels and no `undefined references`.
  - Cross-references resolve, checked with pdftotext per page and matched by **unit and exercise number**
    (numbers repeat across units): answer headings read "Unit U, Exercise N (page M)"; every "Answer on page P"
    on a page whose running head is Unit U, below Exercise N, points to a page P carrying "Unit U, Exercise N";
    page M carries Unit U's running head and the Exercise N heading.
  - The chapter inventory/order accepts the new kinds: `front` (preface), `answers`, `glossary`, `quickref`, `index`.
- **D10 Tests:** pytest for D1–D9; `structure-check` / `cell-lint` already ignore lesson markdown cells.

## Phase E — VERIFICATION

1. All existing checks PASS: `lesson-outputs-check`, `turtle-real-check`, `turtle-check`, structure, hygiene, noexec, concept-scan, cell-lint, prereq and coverage.
2. Both books build, and `publish-audit` PASS with the new rules.
3. A grep of the Student Book PDF text finds:
   - no teacher/Teacher's-Edition reference except story characters
   - none of the banned authoring phrases

   The leak guard and the cross-reference check PASS, and the LaTeX logs have no undefined or multiply-defined references.
4. Rendered-page review:
   - edition page, preface, How to Use
   - a unit opener with its hook, then goals; a recap
   - an odd exercise's "Answer on page N" and the page it points to
   - Problem 11 in the Teacher's Edition
   - U06 answer key Exercise 1
   - one answer with several Check lines
   - glossary, quick reference, the Index's first page
5. `scripts/ci-local.sh` ALL GREEN; post-execution report, recording both editions' page counts
   (Student ≈ 464 → ≈ 650 expected).

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

### Round 1 — verdicts

- `[sol]` **REJECT:**
  - Nested asserts (Checkpoint 2) would leave empty blocks.
  - The student source boundary for answers is undefined.
  - Page-reference and index verification is underspecified: labels, `\pageref`, makeindex, the non-draft render.
  - Survey count nits.
  - Does "every unit" include Unit 0?
- `[fable]` **APPROVE WITH NITS:**
  - Survey counts (343, 34, ×11 teacher refs).
  - Checkpoint "not graded" prefaces and U08 class voice.
  - The checkpoint/AC self-check story.
  - A machine-checkable goals position; heading consumption.
  - Glossary term vs concept id.
  - D2 boundary + leak test; explicit labels + log check; the "Answer key" rule.
  - The concept scan does not read Book 1b markdown.
  - Phase E additions.
  - Spike: Quarto runs makeindex.
  - Appendix ≈ 180–200 pages (175 of 345 exercises).
- `[glm]` skipped (user-authorised one-day exception).

### Round 1 — fold

- `[FIXED]` all of the above:
  - Survey counts.
  - B1 adds the "not graded" prefaces and the U08 voice.
  - How to Use explains how to self-check the checkpoints and the Algorithm Challenge. They stay without printed answers, decided as the independent-learner default.
  - The goals cell is the cell before the first `## Lesson` cell; Unit 0 is excluded.
  - Headings are consumed as panel titles.
  - Glossary `concept:` comments.
  - D2: the `student_answer_sources` boundary, the leak guard, explicit labels.
  - D3: top-level split with nested asserts kept, blank lines kept, tests.
  - D5: `\uppertitleback`.
  - D7: the index file, makeindex in the audit passes, no `\index` in headings.
  - D9: log and cross-reference checks, chapter kinds.
  - B2's concept rule is enforced by the content gate.
  - Phase E additions.
### Round 2 — CONSENSUS

- `[sol]` **APPROVE WITH NITS** (r2) — round-1 blockers resolved; nits: partial-leak test, match
  cross-references by unit as well as number.
- `[fable]` **APPROVE WITH NITS** (r2) — all Should-Fix resolved; nits: normalise the PDF's curly apostrophes
  in phrase bans; state the leak guard's unit of comparison and no-allowlist rule; concrete audit positions for
  goals/recap; merge Phase E items 5–6; surface the no-printed-checkpoint-answers choice to the user
  (done in the status report of 2026-09-27; the user may still redirect).
- `[FIXED]` all nits above.
- `[self]` APPROVE · `[glm]` skipped (user-authorised one-day exception, 2026-09-26/27).

**Consensus reached — implementation starts.**

## Content Review

### Implementation deviation (recorded before the gate)

- **Leak guard rule.** The plan's rule ("≥ 20-token fragment not in visible sources") flagged 44 shared idioms as leaks: the multiplication-table loop the Unit 5 lesson teaches, the `with open(path, "w")` file-writing loop, and the `Counter` class from the Unit 13 lesson.
  - The guard now checks the answers chapter only, the one place solution material is printed.
  - It fails when a printed block equals a hidden (even-exercise, checkpoint or project) solution cell or asset, or contains one whole (≥ 30 tokens).
  - Tests cover a whole leak, an embedded leak, and a shared fragment that must pass.
  - Measured content note: a few checkpoint questions (Checkpoint 2 Q3/Q4) closely mirror odd unit exercises whose answers are now printed. This is a follow-up for checkpoint design, not this plan.

### Round 1

- `[self]` APPROVE WITH NITS: rendered pages checked (edition page, unit opener and goals, answers, glossary, quick reference, index).
  - `[FIXED]` S1: the index put common words ("and", "not") everywhere, had case duplicates, and had terms pointing only at the glossary. Now one entry per term; keywords and backticked keys match inline code only; the audit guards all three.
- `[sol]` **REJECT:** blind-solved U3 Ex 5, U9 Ex 7, U12 Ex 3, U10 Ex 9; 13 cross-references resolved; Problem 11 and the U06 key confirmed.
  - `[FIXED]` O1: U10 Ex 9's real program read two lines while the statement says one. A scan found the same "one run per worked sample" pattern in 39 real programs. 37 were rewritten as one run (U07 ×13, U08 ×8, U10 ×16), each verified on its new Sample input; 6 are legitimate multi-read programs whose Real version line says so. The U13 Ex 3 and Ex 21 headings were aligned.
    - U07 Ex 15 and Ex 32 now print only their one result; Ex 15 prints the weekday name, as the statement's `weekday_name(day_of_week(...))` suggests.
  - `[FIXED]` O2: Check lines never say "is true". `assert A is False` → "Check: `A` → `False`"; `assert not X` → "`X` → `False`".
  - `[FIXED]` O3: the index indexes a term only from its glossary unit onward. Generic prose aliases are removed or made code-only (e.g. `random.choice`); Python names match only real code, case-sensitively.
  - `[FIXED]` O4: the Unit 8 quick reference uses `random.choice("HT")`, not a list.
- `[fable]` **APPROVE WITH NITS:** blind-solved U2 Ex 3, U7 Ex 11, U11 Ex 5, U13 Ex 9, U8 Ex 4; 10/10 cross-references; audit mutations fail as intended; leak-guard deviation accepted.
  - `[FIXED]` F1: index noise (as O3).
  - `[FIXED]` F2: "are the in-class path" ×6 → "are the main path".
  - `[FIXED]` F3: U8 exercises preface in book voice.
  - `[FIXED]` F4: the legend entry now names the printed caption "Drawing made by the program above".
  - `[FIXED]` F5: U8 "classroom example" → "repeat the same way every time".
  - `[FIXED]` F6: the unexplained "add `# turtle-check: open-path`" instruction is removed from U6 Ex 7, U6 Ex 9 and U8 Ex 7. The U6 Ex 9 starter keeps the marker because the checker needs it; printed code strips it. The U8 lesson sentence explaining the marker was reworded.
  - `[FIXED]` F7: the Real-program line keeps its full stop.
  - `[FIXED]` F8: Break and continue is tagged *(Units 4–5)*.
  - `[FIXED]` F9: "# Student task:" → "# Your task:" in U6–U8 starters.
  - `[FIXED]` F10: U9 teacher-notes capital.
  - `[FIXED]` F11: `solution_leak`'s dead `visible` parameter was removed.
- `[glm]` pending: both GLM providers timed out on 2026-09-28 (quota reset expected). The user chose opencode-go/glm-5.3; AGENTS.md now makes opencode-go primary with volcengine-plan as fallback.
- Authoring for this fold ran on Opus subagents (user decision 2026-09-27; AGENTS.md updated on this branch).

### Round 2 — CONSENSUS

- `[sol]` **APPROVE** (r2): O1–O4 verified. All 73 real-program samples in U07, U08 and U10 run exactly, with no unconsumed input. The six multi-read programs are described so by their Real version lines. No Check line says "is true". The index starts every term at its unit.
- `[fable]` **APPROVE WITH NITS** (r2): F1–F11 verified. 174/174 text real programs in U07–U13 match their Expected output. 175 answers = 175 "Answer on page" references; `reference_findings` is clean.
  - `[FIXED]` N1: Python-name index entries were not unit-gated (`sorted` pointed at the Unit 3 page that forbids it). Each name is now gated by its glossary unit, or else by the first lesson that uses it in code; the audit covers names.
  - `[FIXED]` N2: U6 Ex 7's check line now ends "the spiral does not return to its start".
- `[glm]` **APPROVE WITH NITS** (opencode-go/glm-5.3, after a timed-out first attempt): blind-solved U4 Ex 7 and U9 Ex 3, Check lines true, cross-references both ways, independence sweep clean, panels, glossary and quick reference checked, AGENTS.md diff exactly the user-requested changes.
  - `[FIXED]` NIT-1: the glossary's Arithmetic operators entry now includes `**` (taught in Unit 2).
  - `[FIXED]` NIT-2: `sorted` pointed at Unit 3 (same as N1).
- `[self]` APPROVE: index, answers, Check lines and edition page re-checked on the rebuilt PDFs.

**Consensus reached (4/4), no `[OPEN]` findings.**

## Post-Execution Report

**Shipped.**
- **Independent Student Book:** no teacher or Teacher's Edition references (audited on the `.qmd` and the PDF text, with curly apostrophes normalised). The Real-program convention is explained once in How to Use. "No real program" panels are gone. Independent-reader wording throughout: Unit 0, course folder, `py`/`python3`, "an empty cell in your exercises notebook", "main path".
- **Answers to Selected Exercises** (Student Book): the 175 odd-numbered unit exercises, read only through `student_answer_sources`. Explicit `ex:`/`ans:` labels give "Answer on page N" and "Unit U, Exercise N (page M)". The Teacher's Edition answer keys also show "(page M)". Checkpoints and the Algorithm Challenge stay without printed answers; How to Use explains self-checking against their worked samples.
- **Check lines** replace dropped asserts in both editions, fixing Algorithm Challenge Problem 11. The U06 answer key no longer groups Exercise 10–18 assets under Exercise 1.
- **Front matter:** edition page (title verso), preface "About This Book", rewritten How to Use.
- **Back matter:** Glossary (62 concept ids), Quick Reference, and an Index that is unit-gated, code-aware and free of case duplicates.
- **Units:** 13 "You will learn" / "Recap" panels. Lesson 1/2/3 naming. The Unit 8 title is fixed. U02's Peek ahead moved into a Notice.
- **Teacher notes:** classroom voice (no design/plan citations, `no-exec`, CI, git-ignored).
- **Found during the gate:** 37 real programs ran once per worked sample instead of once. They are rewritten as single runs and verified; U07 Ex 15 prints the weekday name.
- **Governance (user-requested, on this branch):** AGENTS.md authoring → Opus subagents; the GLM seat → opencode-go/glm-5.3 with a volcengine-plan/glm-5.3 fallback.

**Verification.**
- `scripts/ci-local.sh` ALL GREEN at 78a3a8d.
- pytest all passing.
- `publish-audit` PASS: phrase bans, leak guard, goals/recap positions, answer coverage (175), glossary and index coverage with unit gating, LaTeX reference hygiene, cross-reference resolution.
- Rendered-page review of the edition page, a unit opener with its goals, the answers, the glossary, the quick reference and the index.
- Content gate consensus 4/4 at round 2.

**Page counts:** Student Book 464 → 658 pages; Teacher's Edition ≈ 870 → 924 pages.

**Deviations:**
- The leak-guard rule was changed from 20-token fragments to whole or embedded hidden solutions (recorded above, with measurements).
- Pre-existing content bugs found by the gate (one-run real programs) were fixed in this plan.

**Follow-ups:**
- Checkpoint 2 Q3/Q4 closely mirror odd unit exercises whose answers are now printed; review checkpoint distinctness.
- Book 1 and Book 2 editions (plan 086).
