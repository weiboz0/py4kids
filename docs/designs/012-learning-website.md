# Design 012 — A learning website for every book

Status: approved, revision 3 (2026-10-04). Round 1: [sol] REJECT, [fable] REJECT. Round 2: [sol] REJECT (3 findings), [fable] APPROVE WITH NITS. Round 3: [sol] APPROVE WITH NITS. All findings are folded. Review consensus reached. **Approved by the user on 2026-10-05 ("Go with autopilot").** Part A: plan 101.
Extends design 000 ("notebooks are the source of truth"), design 007 (publication), and design 010 (every book publishes).

## 1. Purpose and agreed understanding

User, 2026-10-04: "start making a learning website for these books. the website should share the single framework for all books". The requested content:

1. slides for self-paced learning
2. quiz cards for self-evaluation of concept mastery, from the lesson notebooks
3. question evaluation on the same exercise set as the books
4. a web and app experience
5. personalized learning progress, with an LLM as orchestrator: a stretch feature for subscribers

The user also asked to "add any components missing from the list but essential for a learning website".

**Decisions** (user, 2026-10-04):
- **Audience:** a public site with a free core and a paid tier. Success for the first release is that a student can self-study a whole book online.
- **Accounts:** owned by a parent or teacher, who adds child profiles. The free core needs no account.
- **Architecture:** static-first, with a backend later.
- **Answers:** pedagogical gating; check data is public by nature (D5).
- **Python-book exercises:** tagged by check kind, with a self-check fallback (D4).
- **Lessons:** the reading view is primary; slides are a step-through and review mode (D6).
- **Sync:** class sync is free (a child in a teacher's class syncs results to that class); personal cross-device sync and the LLM orchestrator are paid; student code stays on the device unless a parent opts in (D11).

**Constraints:**
- The notebooks stay the source of truth, and the site is a generated view, like the PDFs.
- The books' verification machinery is reused, not reinvented.
- This repository is public: it holds no student data, keys or payment code.

**Essential components added:**
- navigation, contents and resume
- the reading view with an inline runner
- checking in the browser
- answer gating
- glossary, quick reference and search
- accessibility
- children's privacy from day one
- a teacher and classroom view
- report-a-problem
- content versioning, and links to the release PDFs
- offline use
- light motivation (a streak and a mastery map)
- legal pages
- payments
- LLM cost and safety controls

## 2. Decisions

- **D1 — One framework, books opted in by a flag.**
  - The site lives in `site/` in this repo and renders every book that `books.yaml` marks `site: true`. The tools key on that flag, never on ids. Adding a book needs no site code.
  - The first release covers python-projects, python-concepts, usaco-bronze and acsl. **recsys** is out of scope: it stores no lesson outputs and depends on packages Pyodide cannot load (`bookrec`, torch, faiss). It can opt in once it has outputs and a browser-feasible subset.
  - The site deploys to **Cloudflare Pages**, chosen because it can set the COOP/COEP headers the runner needs (D7), from the same release tags as the PDFs. Each unit page links to that release's PDFs.
- **D2 — Roadmap in parts**, each with its own plan and gates:

  | Part | Delivers | Depends on |
  |---|---|---|
  | **A** Content export and classification | JSON bundles; the exercise-classification tool; the standalone-cell probe; the id/hash scheme; schema with a minimal consumer test | — |
  | **B** Static site core | catalog; reading view (primary); slide mode; quiz cards; glossary, reference and search; privacy notice and terms; accessibility; device-local progress | A |
  | **C** Isolated runner and checking | the Pyodide runner on its own origin; program, function, short-answer and turtle checks; answer gating; browser acceptance tests | A, B |
  | **D** App experience | installable PWA, offline books, persistent storage; first public deploy of the free site | B, C |
  | **E** Accounts, classes, sync, subscriptions | private backend (its own design) | B–D |
  | **F** LLM orchestrator | subscribers (its own design) | E |

  - **Free:** A–D, teacher classes and class sync.
  - **Paid:** personal cross-device sync and F.
- **D3 — Content export (part A).**
  - **The command:** `py4kids-tools export --book <id>` writes `site/content/<book>/` as JSON against a versioned JSON Schema. A minimal consumer test renders one page of each kind from the bundle, so the schema is proven before it freezes. The bundle is generated, never hand-edited.
  - **Reuse:** the export **imports** the publisher's routing (`route_code`, the try-it, figure and demo routes, structural subheads), so web and print agree.
  - **Book manifest:** id, title and subtitle; release tag and content hash; syllabus order; concepts (`concepts.yaml`); the publication settings the web uses (`acsl` division ladder, `lesson_heading`); and the release PDF links.
  - **Lessons:** each lesson is a sequence of **blocks**:
    - prose
    - Notice
    - code with stored output
    - try-it
    - error demo
    - turtle figure
    - goals and recap
  - **Lesson code:**
    - **The standalone-cell probe:** the export runs every executable lesson cell **on its own**, from the unit directory. A cell that fails or whose output differs gets `needs_prelude: true`, with the ids of the earlier cells it depends on. In review, 61 of 718 lesson cells (8.5%) needed their earlier cells.
    - **The asset list:** cells that read data files list the unit's `assets/` files they need, so the runner can mount them.
  - **Exercises:** the books' sets unchanged. Each item carries:
    - statement, Starter, division tag, stretch flag, and its concept ids
    - its **check kind** (D4) and check data (D5)
    - `answer_visibility`: `after-attempt` for odd unit exercises, using exactly the Student Book appendix text, read only through `student_answer_sources`, which is the export's leak guard; `none` for everything else
  - **Answer formats:** short-answer items carry an `answer_format` hint, derived from the item's statement and the unit's canonical-form rule, or authored where the derivation is ambiguous. The derivation is listed as content work.
  - **Ids:** every block, card and item has a global key `book/entry/notebook/cell_id`, plus `#n` for parts split out of one cell.
    - The export fails on a missing or duplicate id.
    - A **continuity check** compares with the previous release's bundle and lists vanished ids, so content plans can map them. Progress for a vanished id is kept but marked stale.
- **D4 — Exercise check kinds and classification** (user decision: tag, with a self-check fallback).
  - **The classification tool** proposes a kind for every checkable item: unit exercises, **checkpoint questions and project problems or milestones**. A content plan per book confirms the tags as **heading-cell tags** (`check-fixtures`, `check-answer`, `check-asserts`, `check-expected-output`, `check-predict`, `check-self`), the same form as `short-answer` and `stretch`, so the tag readers and hygiene checks in `tools/notebooks.py` apply unchanged.
  - **The kinds:**
    - `fixtures`: contest programs (stdin to stdout, judged on the test cases).
    - `answer`: short answers (ACSL `short-answer`).
    - `asserts`: Python items whose statement fixes the inputs, so the solution's top-level asserts are portable. Asserts that test the solution's own choices are not portable, and the tool flags them.
    - `expected-output`: an item with fixed inputs, checked against its worked output.
    - `predict`: trace items, where the student enters the predicted output.
    - `self-check`: open-ended items (random results, free design, interactive input). The student runs their code and marks the item done against a short **requirements checklist taken from the statement**, never from the solution. Odd unit items may also show the worked answer after the attempt (D5); `none` items show no answer. The site states plainly that it cannot check these.
  - **Fixed-answer items** (for example "fix the bug" items, whose fixed program's output is determined) are classified `expected-output` with a **hashed** expected output (D5), not `self-check`, so no solution ships.
  - **Turtle items** use a browser port of `tools/fake_turtle.py`: its tracked API, plus `bgcolor`. They are checked by the same three-part rule:
    - at least one pen-down move
    - fewer than 10,000 moves
    - a closed path by default, with `# turtle-check: open-path` as the opt-out

    The rule applies to exercise cells as well as assets. "Runs without error" is not a check.
  - Turning `self-check` items into checked ones is later content work, book by book.
- **D5 — The answer model** (user decision: pedagogical gating).
  - **Honest premise:** everything the browser checks against is public, as the repo's `solutions.ipynb` files and the Teacher's Edition PDFs already are. Gating is a study aid, not a security boundary; the About page says so.
  - **Odd unit exercises:** the worked answer is shown after a genuine attempt (one Check run, or one submitted answer).
  - **Even exercises, checkpoints and projects:**
    - **Short answers, `predict` items and `expected-output` items:** only a **salted hash** of the normalised canonical answer or output ships, never the plain text. Normalisation: trimmed, internal whitespace collapsed to one space per line, case as `answer_format` states. The student's input is compared by hash.
    - **Programs:** the fixtures ship, because expected output is not the program. Check shows pass or fail for each test case, and reveals input and expected output for the **sample** only.
    - **Asserts:** Check runs the asserts and shows each result as pass or fail. The assert source is not printed.
  - **The export test** checks three things:
    - no plain answer text of any `none` item appears in any bundle
    - every odd answer equals the Student Book appendix text
    - every `answer`, `predict` and `expected-output` item's hash matches its canonical text
- **D6 — Lesson experience** (user decision: the reading view is primary).
  - **Reading view:**
    - The lesson reads as a page with the book's blocks.
    - Code blocks are **runnable inline with cumulative state**: one namespace per lesson, like the notebook, re-running the earlier cells the probe lists when needed.
    - Stored outputs show beside "Run" so the student can compare.
    - Interactive `input()` demos take input from a box filled before the run (live prompts are an enhancement where the headers allow it, D7).
  - **Slide mode** (step-through and review) comes from cell-level rules:
    - each code+output pair is one slide
    - each Notice is one slide
    - prose is grouped up to a word budget, splitting at headings
    - goals and recap get their own slides
    - optional `slide-break` / `slide-skip` tags adjust the split
    - a **per-book slide audit** (the maximum words or lines per slide) runs in CI like `publish-audit`
  - Books whose lessons split poorly (python-projects, usaco-bronze) get a `slide-break` authoring pass in their content plans.
- **D7 — The isolated runner (part C).**
  - **Origin:** Python runs in Pyodide on a **separate runner origin** (for example `run.<site>`), inside a sandboxed iframe that holds a Web Worker. It has no access to the site's storage or, later, its session.
  - **Isolation headers:** **both** origins send COOP `same-origin` and COEP, the iframe carries `allow="cross-origin-isolated"`, and every asset is self-hosted (D9), so `SharedArrayBuffer` interrupts work. The worker-restart path is the fallback, not the default.
  - **Message boundary:** the site sends `{code, stdin, files, check spec, time budget}` and receives `{stdout, stderr, results, timing}`. Nothing else crosses.
  - **Time limits:** a per-test-case budget (set by measurement in part C, starting at 10× the CPython time and capped). The runner interrupts with `SharedArrayBuffer` interrupts where the COOP/COEP headers allow; otherwise it terminates and restarts the worker, and the reload cost is shown honestly.
  - **Fixtures:** contest fixtures run in the browser. Every pair is under 130 KB (usaco-bronze totals 1.9 MB, ACSL 40 KB). The export reports any fixture over a measured budget, and the site lists any skipped case. Skips are never silent.
  - **Matching:** keyed on book flags, not names: line-exact for `acsl` books, token-based otherwise, as in `tools/judge.py`.
  - **ACSL `assets/verify` helpers** are not shipped. Short answers are checked by hash (D5), and the helpers stay solution sources (design 010 D3).
- **D8 — Quiz cards and mastery.**
  - **Card kinds:**
    - **Predict-the-output:** only cells that pass the standalone probe, or that show their prelude on the card. Single-token or one-line outputs are typed and compared after D5's normalisation (trimmed, internal whitespace collapsed), case-sensitive. Multi-line outputs are flip-and-self-grade.
    - **Concept cards:** from the glossary. Multiple-choice distractors come from concepts in the same `category`.
    - **Authored `quiz` cells:** added in later content plans.
  - **Concept attribution is per item, not per unit.** It uses an explicit concept tag on authored cards and the glossary term for concept cards. For code cells, part A extends `tools/concept_scan.py`'s cell-level scan, which today runs only for `patterns` books, to every `site` book. Where the scan cannot attribute a cell, per-cell `concepts` metadata is listed as content work.
  - **The mastery map** shows a concept only when at least N attributed items exist (N set in part B), so it never pretends.
  - **Scheduling:** Leitner spaced repetition per card.
- **D9 — Children's privacy in the free site (B–D).** The site is directed at children, so it collects **no personal data by construction**:
  - progress only in on-device IndexedDB, with no identifiers
  - **no analytics**
  - no third-party scripts, fonts or trackers, and self-hosted assets
  - a privacy notice and terms **ship with part B**
  - **report a problem** is labelled for adults and prefills only the item id and content hash, never an attempt
- **D10 — App experience (part D).**
  - **Installable PWA:** "download this book" caches the book's pages and bundle with the **site** origin's service worker. It also asks the runner iframe, through its message channel, to precache the runner page, worker, Pyodide runtime (+10–20 MB) and the book's fixtures and assets with the **runner** origin's own service worker. A service worker controls only its own origin, so each origin caches its own files. Both request `navigator.storage.persist()`.
  - **Offline status:** the site shows "available offline" only after both caches confirm.
  - **Storage limits:** the site states that some browsers (Safari) can clear storage after long disuse, with an "export my progress" file as the backup.
  - **Native wrappers** are deferred.
- **D11 — Interfaces fixed now** (E and F build on these).
  - **The bundle schema** (D3), with a semantic version.
  - **The progress event:**

    ```
    {schema, event_id, book, item_key, kind, result, detail, duration_ms, timestamp, content_hash}
    ```

    - `kind` is one of `lesson-run`, `slide`, `card`, `exercise`, `checkpoint`, `project`, `self-check`.
    - `event_id` makes sync idempotent.
    - `detail` holds **results only** (pass/fail per test case, self-grade, card box). It never holds student code or free text.
  - **The attempt store** keeps code and answers **on the device only**. Uploading them requires parental opt-in in E, and F uses them only with that opt-in.
  - **Concept ids** come from the registries.
- **D12 — Part E outline** (its own design):
  - **Repo:** a private backend repo and service.
  - **Accounts:** an adult (parent or teacher) owns the account. Child profiles carry a display name only. Verifiable parental consent comes before any child data is stored.
  - **Classes:** a teacher creates a class with a join code. A child joins under a consenting adult. **Class sync of results is free**, and the teacher dashboard shows unit and concept progress and lets the teacher assign units.
  - **Paid:** personal cross-device sync, through Stripe with the adult as payer.
  - **Policies:** data export and deletion, minimal retention, no ads or trackers.
- **D13 — Part F outline** (its own design):
  - **Mastery-driven next step:** chooses what to do next and says why in one sentence.
  - **Hint dialogue:** never reveals an even item's solution.
  - **Child safety:**
    - a system prompt scoped to the course
    - input and output filtering
    - only results, the current item and opted-in attempts are sent
    - per-subscriber rate limits and cost caps
    - an audit log visible to parents and teachers
  - **Keys:** a current Claude model, called only from the backend.

## 3. Verification (for the plans implementing A–D)

- **Export:**
  - the schema check, plus the minimal consumer test
  - the id uniqueness and continuity checks
  - the standalone-cell probe report
  - the classification coverage report (every unit exercise, checkpoint question and project item has a confirmed check kind)
  - the D5 answer-model test
- **Runner acceptance** (in a headless browser, in CI):
  - stdin programs, including `input()` at end of input
  - worker interrupt or restart on a hang
  - recursion depth and float formatting against CPython
  - function-assert isolation; short-answer hashing and normalisation
  - turtle directives; mounted asset files; cumulative lesson state
- **Reference solvers:** every reference solver (`assets/{l,ex,q,p}N.py`) runs in Pyodide against all its fixtures, with results equal to `tools/judge.py`.
- **Site:**
  - Playwright end-to-end tests per book: read a lesson and run code, step through slides, answer a card, check one exercise of each kind, resume
  - axe on every template
  - a Lighthouse budget
  - an offline test that **runs code and checks an exercise** with the network off, not only reads a lesson
- **Toolchain:** the site adds a Node toolchain with pinned versions and a lockfile. `ci-local.sh` gains a `site` step, scoped like design 010 D7. Without Node it prints `SKIP (Node missing)` locally, and it is required before a release.

## 4. Rollout

| order | plan scope |
|---|---|
| 1 | **Part A:** export, classification tool, standalone-cell probe, id/hash scheme, schema + consumer test, `site:` flag. |
| 2 | **Content plans**, one per book, which can run alongside part B (only part C consumes the tags): confirm the check-kind tags; `answer_format` hints; per-cell `concepts` where the scan cannot attribute; slide-break pass (python-projects, usaco-bronze). |
| 3 | **Part B:** static site core, privacy notice and terms. |
| 4 | **Part C:** isolated runner, checks, answer gating, acceptance tests. |
| 5 | **Part D:** PWA and offline; first public deploy of the free site. |
| later | Authored `quiz` cards per book; designs for part E and part F (the next free design numbers). |

## 5. Non-goals (this design)

- Server-side code running; native app-store apps; forums or student-to-student chat; ads.
- Any student data, secret or payment code in this public repository.
- Treating gating as security (D5); changing the books' content rules.
