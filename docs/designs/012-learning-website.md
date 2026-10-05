# Design 012 — A learning website for every book

Status: proposed (2026-10-04).
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
- **Accounts:** owned by a parent or teacher, who adds child profiles. The free core needs no account at all.
- **Architecture:** static-first, with a backend added later.
- **Design sections:** sections 1–4 below were reviewed and approved in conversation.

**Assumptions, kept as constraints:**
- The notebooks stay the single source of truth. The site, like the PDFs, is a generated view.
- The books' verification machinery (lesson outputs, judge fixtures, `**Answer:**` lines, `verify` helpers) is the site's evaluation engine.
- The repository is public: it holds no student data, keys or payment code.

**Essential components added** (user request): navigation and resume, a lesson reading view, an in-browser code runner, answer gating, the glossary, quick reference and search, accessibility, children's-privacy compliance, a teacher and classroom view, report-a-problem, privacy-respecting aggregate analytics, content versioning, offline use, light motivation (streaks and a mastery map), legal pages, payments, and LLM cost and safety controls.

## 2. Decisions

- **D1 — One framework, books as data.**
  - The site lives in this repo under `site/` and renders any book listed in `books.yaml` from that book's content bundle. Adding a book needs no site code.
  - The static build deploys from the same release tags (the host, GitHub Pages or Cloudflare Pages, is chosen in part D's plan) as the PDFs, so the site and the PDFs always match.
- **D2 — Roadmap in parts**, each with its own plan and gates:

  | Part | Delivers | Depends on | Tier |
  |---|---|---|---|
  | **A** Content export | versioned JSON content bundles per book | — | free |
  | **B** Static site core | catalog, slides, reading view, quiz cards, glossary/reference/search, report-a-problem, accessibility, device-local progress | A | free |
  | **C** In-browser runner and judge | Pyodide runs and checks lesson code, programs, short answers and turtle drawings | A, B | free |
  | **D** App experience | installable PWA, offline books, resume | B, C | free |
  | **E** Accounts, classes, sync, subscriptions | private backend: adult-owned accounts, child profiles, consent, classes, teacher dashboard, synced progress, Stripe, legal pages | B–D | teacher view free; synced personal progress paid |
  | **F** LLM orchestrator | mastery-driven next step and hint dialogue for subscribers | E | paid |

  This design specifies A–D in detail. E and F are outlined here (§2 D8–D9) and get their own designs before any plan, because they need privacy, legal and vendor decisions.
- **D3 — Content export (part A).** `py4kids-tools export --book <id>` writes `site/content/<book>/` as JSON, with a JSON Schema checked in CI. The bundle is generated, never hand-edited.
  - **Book manifest:**
    - id, title and subtitle from `books.yaml`
    - the release tag and a content hash
    - the syllabus order (units, checkpoints, projects) and the concepts (`concepts.yaml`)
    - the per-book publication settings that apply on the web (division ladder for ACSL, lesson heading)
  - **Slides, from `lesson.ipynb`:**
    - Each `## Lesson` heading starts a section, and each `###` heading starts a slide.
    - A code cell with its stored output becomes a Program/Output slide; a `**Notice:**` becomes a callout slide.
    - "You will learn" opens the unit and "Recap" closes it.
    - Over-long content splits by a size budget.
    - Optional cell tags `slide-break` and `slide-skip` override the rules.
    - Routing reuses the publisher's (try-it, error demo, turtle figure), so the web and print agree.
  - **Reading view:** the same cells as the book chapter, minus print furniture.
  - **Quiz cards**, each carrying concept ids (from the unit manifest's `introduces` and `practices`, or the card's own tag):
    1. **predict-the-output:** a lesson code cell plus its stored output. The answer is already verified by `lesson-outputs-check`. Cells tagged `no-exec`, or whose output is empty or nondeterministic, are excluded.
    2. **concept:** from the glossary, term → definition and definition → term.
    3. **authored mastery:** new `quiz`-tagged lesson cells, multiple choice or a short exact answer, with a one-line explanation and a concept tag. They are authored by Opus sessions and verified like exercises (a tool checks the answer key's format and uniqueness), and they arrive per book in later content plans.
  - **Exercises:** the books' exercise sets unchanged. Each item has:
    - statement, Starter, division tag, stretch flag, concept ids, and kind (program, short answer, Check-line function, turtle)
    - check data:
      - programs: sample and fixture inputs, plus expected outputs
      - short answers: canonical answer text and a normalisation rule
      - functions: the top-level asserts
    - `answer_visibility`:
      - `after-attempt` for odd-numbered unit exercises, carrying the worked answer exactly as the Student Book's appendix prints it
      - `none` for even-numbered exercises, checkpoints and projects, which ship **no** answer text, only check data
  - **Stable ids:** every slide, card and item is keyed by its notebook cell id, so progress survives releases. A tool fails the export if an id is missing or duplicated.
- **D4 — Static site core (part B).**
  - **Stack:** **Astro**, a static generator built for content, with small interactive islands for the slide player, quiz deck and exercise runner.
  - **Pages:** a catalog of all books; a book home with its contents and mastery map; a unit page; the slide player (keyboard and swipe, a "run this code" button on code slides); the reading view; a quiz deck per unit plus a mixed review deck; exercise pages; checkpoint self-tests (timed, no answers); glossary, quick reference and search (**Pagefind**, static).
  - **Progress:** stored on the device in **IndexedDB** as a log of progress events (D7). From it the site derives:
    - "continue where you left off"
    - per-unit completion
    - a **per-concept mastery level**: card results and exercise results combined; recent results weigh more
  - **Quiz scheduling:** quiz cards are scheduled by simple **spaced repetition** (Leitner boxes per card).
  - **Report a problem:** each slide, card and item has a "report a problem" link that opens a prefilled GitHub issue (no account data) for the errata flow.
  - **Accessibility:** WCAG 2.2 AA is the target (keyboard paths, labels, contrast, alt text for figures, reduced motion).
  - **Analytics:** aggregate and cookieless only (page and item counts, failure rates per item), or none, until part E's privacy policy exists.
  - **Motivation:** a streak counter and a mastery map. No leaderboards.
- **D5 — In-browser runner and judge (part C).**
  - **Runtime:** **Pyodide** in a Web Worker, so code never blocks the page. Each run has a time limit, and the worker is restarted if it hangs (infinite loops). **CodeMirror** is the editor.
  - **Checking:**
    - **Lesson code:** "run" on a code slide executes it and compares with the stored output.
    - **Programs:** **Run** uses the sample input; **Check** runs every fixture and shows which pass. Matching is per book: line-exact for ACSL, token-based for USACO, as in `tools/judge.py`. Fixtures that are too large for the browser are marked by the export and skipped with a note.
    - **Function exercises:** Check runs the item's asserts and shows each result as a Check line.
    - **Short answers:** the input is normalised and compared with the canonical text. The format hint comes from the book's canonical rules.
    - **Turtle:** a turtle shim draws on a canvas. Checking is "runs without error"; drawings are not compared.
  - **Answer gating:** an odd exercise's answer appears after a genuine attempt: one Check run, or one submitted short answer. Even-numbered, checkpoint and project items never show answers.
  - **Server:** none is involved. The judge's matching rules are ported to the worker and tested against the Python implementation on every book's fixtures.
- **D6 — App experience (part D).**
  - **Installable PWA:** a web manifest and a service worker (Workbox). "Download this book" caches its pages, content bundle and the Pyodide runtime for offline study; resume works offline, and progress syncs in part E.
  - **Native store wrappers** (for example Capacitor) are deferred to a later design.
- **D7 — Interfaces fixed now** (E and F build on these without changing A–D):
  - **The content bundle schema** (D3), versioned. A breaking change bumps its major version.
  - **The progress event:** `{book, item_id, kind, result, detail, timestamp, content_hash}`, where `kind` is one of slide, card, exercise or checkpoint. Events are append-only; mastery and completion are derived from them.
  - **Concept ids:** the registries' ids (`concepts.yaml`).
- **D8 — Part E outline** (a separate design before any plan):
  - **Repo:** a private backend repo and service. This public repo never holds student data or secrets.
  - **Accounts:**
    - An adult (a parent or teacher) owns the account.
    - Child profiles carry a display name only: no child email and no free text.
    - Verifiable parental consent comes before any child data is stored (COPPA and equivalents).
    - Data export and deletion; minimal retention; no ads or third-party trackers.
  - **Classes:** a teacher creates a class with a join code. The free teacher view shows per-unit and per-concept progress and lets the teacher assign units.
  - **Sync and payments:** on sign-in, device events upload into the profile. Synced personal progress across devices is paid, through Stripe, with the adult as payer.
  - **Legal pages:** terms, privacy policy, contact.
- **D9 — Part F outline** (a separate design before any plan):
  - **Mastery-driven next step:** from the mastery map and recent attempts, choose what comes next (review cards, a weak concept's slides, the next exercise) and explain the choice in one sentence.
  - **Hint dialogue on exercises:** it never reveals the full solution of an even exercise.
  - **Child safety:**
    - a system prompt scoped to the course
    - input and output filtering
    - only progress data and the current item are sent; no personal data
    - per-subscriber rate limits and cost caps
    - an audit log visible to parents and teachers
  - **Keys:** a current Claude model, called only from the backend; the static site never holds keys.

## 3. Verification (for the plans implementing A–D)

- **Export:** schema validation in CI; stable-id and uniqueness checks; and a test that every odd exercise's web answer equals the Student Book's appendix text while no even, checkpoint or project answer text appears in any bundle.
- **Judge parity:** the browser checker and `tools/judge.py` agree on every fixture of every book (run headless in CI).
- **Site:**
  - **Playwright** end-to-end tests per book: navigate, play slides, run lesson code, check an exercise, answer a card, resume.
  - **axe** accessibility checks on every page template.
  - a **Lighthouse** budget (performance, accessibility, PWA)
  - an offline test with a downloaded book
- **CI:**
  - A `site` step in `scripts/ci-local.sh` builds the content and site for the books a change touches (the design 010 D7 scoping) and runs the tests above.
  - A release builds every book.

## 4. Rollout

| plan | scope |
|---|---|
| next | **Part A:** the export command, schema, bundles for all books, and tests. |
| then | **Part B:** the static site core for all books. |
| then | **Part C:** the Pyodide runner, judge parity, and answer gating. |
| then | **Part D:** the PWA and offline mode; first public deploy of the free site. |
| later | Authored `quiz` cells per book (content plans). |
| later | A design for part E (accounts, classes, sync, subscriptions, privacy), taking the next free design number. |
| later | A design for part F (the LLM orchestrator). |

## 5. Non-goals (this design)

- Server-side code running, native app-store apps, discussion forums or chat between students, ads.
- Any student data, secret or payment code in this public repository.
- Changing the books' content rules: the site follows the odd-answer rule and the independence rules exactly as the Student Book does.
