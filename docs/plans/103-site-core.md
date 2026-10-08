# Plan 103 — Learning website, part B: the static site core

**Goal:** One Astro site in `site/` renders every `site: true` book from its plan-101 bundle. A student can, with no account and no data leaving the device:
- browse the catalog
- read every lesson in the reading view
- step through slides
- read every exercise, checkpoint and project item
- drill quiz cards with spaced repetition
- use the glossary, the quick reference and search
- see their progress and resume

The privacy notice, the terms and the About page ship with it.
Running code and checking answers are part C; installable offline use and the public deploy are part D.

**Spec:** design 012 D1, D2 (part B row), D5 (About page honesty statement), D6, D8, D9, D11, §3 "Site" and "Toolchain".
Part A is merged (plan 101, PR #139).
User decisions:
- 2026-10-06: "non stop until full working learning website"
- 2026-10-07: content license **CC BY-NC-SA 4.0**; contact **GitHub issues** (no email published)

## Global constraints

- **No personal data by construction (D9):**
  - progress lives only in on-device IndexedDB, with no identifiers
  - no analytics, no cookies
  - no third-party scripts, fonts, images or trackers: every asset is self-hosted, the font stack is system fonts
  - a strict `Content-Security-Policy: default-src 'self'`
- **The site is generated:**
  - `site/content/<book>/` comes only from `py4kids-tools export`; nothing in the site hand-copies book text.
  - The site keys on the `site` flag and `book.json`; it never hard-codes a book id. Adding a book needs no site code.
- **Hidden answers stay hidden:**
  - Part B renders no `answer_md` (gating is part C).
  - It never prints `check.source` (assert source) or a fixture `.out` other than the sample's.
  - Hashes are never shown.
- **Toolchain:** Node 20 (the repo's `.nvmrc`), pnpm, with exact pinned versions and a committed `pnpm-lock.yaml`. `pnpm install --frozen-lockfile` is the only install path.
- **Accessibility:**
  - WCAG 2.2 AA
  - keyboard operable: slides, cards, menus
  - visible focus; reduced-motion respected; light and dark themes
- **Docs** use semantic line breaks.

## Architecture

- **`site/`** is an Astro 7 static project (`output: 'static'`) with TypeScript strict mode.
  - Pages come from `getStaticPaths` over the bundles. A loader (`site/src/lib/bundle.ts`) reads `site/content/*/book.json` and the entry files at build time, and validates each against `tools/export/schema/bundle.schema.json` with Ajv (2020-12). An invalid bundle fails the build.
  - Types live in `site/src/lib/types.ts`, hand-written to the schema. A test asserts that every key the components read is declared in the schema, as plan 101's consumer test does.
- **Markdown** (`site/src/lib/markdown.ts`): markdown-it plus a container plugin for the bundle's Pandoc fenced divs (`::: {.notice}`, `{.goals}`, `{.recap}`, `{.opener}`, `{.program}`, `{.realprog}`, `{.datafile}`, `{.challenge}`).
  - `{=latex}` raw blocks are dropped.
  - Code is highlighted at build time with Shiki (no client JS).
  - Math, if present, is rendered at build time with KaTeX, with its fonts self-hosted.
- **Client islands are the only JS:**
  - the slide player
  - the card deck
  - the progress store and "resume"
  - the search box
  - the theme toggle

  Each is a small vanilla-TS module; no UI framework.
- **Progress** (`site/src/lib/progress.ts`): IndexedDB database `py4kids`.
  - **Stores:**
    - `events`: D11 progress events validated against `tools/export/schema/progress-event.schema.json`
    - `cards`: Leitner box and due date per card key
    - `resume`: last position per book
  - **Event kinds written in part B:** `slide`, `card` and `lesson-run` (the last as "read" until part C).
  - **Fallback:** if IndexedDB is unavailable (private window), the site works without saving and says so once.
- **Normalisation** (`site/src/lib/normalise.ts`): a port of `tools/export/normalise.py`, including `case` and `aliases`. It is tested against every vector in `tools/export/hash_vectors.json`, including the Python-vs-JS `\s` cases. `answerHash` uses WebCrypto SHA-256. Part B uses it for typed predict cards; part C for checks.
- **Search:** Pagefind runs after `astro build` over the built HTML.
  - It indexes lesson text, item statements, the glossary and the reference.
  - It does not index the About, privacy or terms pages.
  - It is self-hosted, with no network calls.
- **Build:** `scripts/build-site.sh`
  1. exports every `site` book to `site/content/<book>/` (the release tag is passed through for PDF links)
  2. runs `pnpm -C site build`
  3. runs Pagefind
  4. runs the slide audit

## Pages

| route | page |
|---|---|
| `/` | catalog: each book's title, subtitle, unit count, "continue" link |
| `/<book>/` | contents in syllabus order (units, checkpoints, projects); resume; PDF links (when the bundle has a release); mastery map |
| `/<book>/<entry>/` | reading view: blocks in order. Code blocks show their stored output under "Output". Try-it, error-demo and hang-demo blocks are labelled as in the PDFs. Turtle figures are drawn as inline SVG from `figure` segments. Prev/next navigation; a "Slides" button |
| `/<book>/<entry>/slides/` | slide mode (below) |
| `/<book>/<entry>/practice/` | the entry's items, intro, `before` blocks and outro. Each item shows its statement, Starter (read-only code), division tags and stretch marker, and a "How this is checked" line from its check kind. Self-check items show their requirements as a checklist that saves locally. Every other kind shows "Checking arrives soon" in part B |
| `/<book>/cards/` | the book's quiz deck: due cards first (Leitner, 5 boxes), filterable by unit |
| `/<book>/glossary/`, `/<book>/reference/` | `glossary` and `reference_md` |
| `/search/` | the Pagefind UI |
| `/about/` | what the site is; the D5 honesty statement (answer gating is a study aid, not security); the license |
| `/privacy/` | the D9 notice in plain language: nothing collected, what stays on the device and how to clear it, no analytics, no third parties; contact through GitHub issues |
| `/terms/` | free educational use under **CC BY-NC-SA 4.0**, with attribution "py4kids"; provided as is; adults supervise children's use; GitHub issues for problems |

- **Report a problem:** each lesson, item and card links to a prefilled GitHub new-issue URL (`github.com/weiboz0/py4kids/issues/new?title=…&body=…`) carrying only the item key and the bundle content hash. The link is labelled "For parents and teachers: report a problem", and is a plain link, not a script.
- **Footer:** the license, privacy, terms, about, and the book's release tag.

## Slide mode and the slide audit (D6)

- **Slide rules** (`site/src/lib/slides.ts`, one function shared by the player and the audit):
  - opener, goals, recap, each notice and each code(+output) block is one slide
  - consecutive prose blocks group up to `max_words` (default 90), splitting at headings
  - try-it, demo and figure blocks are one slide each
  - a block tagged `slide-break` starts a new slide; one tagged `slide-skip` is left out of slides (it still shows in the reading view)
- **Player:**
  - full-viewport, arrow keys and swipe, a progress bar, the slide number in the URL hash
  - Escape returns to the reading view
  - each slide viewed writes a `slide` event
- **Slide audit:** `pnpm -C site slide-audit` reports, per book, every slide over `max_words` prose words or `max_code_lines` code lines. The thresholds come from a new optional `slides:` block in `<book>/site.yaml` (`max_words`, `max_code_lines`), validated by `tools/books.py`. Any slide over the limit fails CI.
- **Slide-break pass (moved here from plan 102):**
  - python-projects and usaco-bronze lessons get `slide-break` (and, rarely, `slide-skip`) cell tags until the audit passes.
  - These are cell-tag-only notebook edits: no source text changes, and the PDFs are unchanged (the publication regression digests stay byte-identical, which a test asserts).
  - python-concepts and acsl must pass the audit as they are, or get the same pass.

## Mastery map and cards (D8)

- **Concept mastery:**
  - Each card and item carries concept ids. A concept's mastery is the share of its attributed cards in Leitner box ≥ 3.
  - The map shows a concept only when it has at least **N = 3** attributed cards or items.
  - Concepts are grouped by registry `category`.
- **Predict cards:** a `typed` card compares the student's line with the stored output through `normalise` (case-sensitive). A `flip` card reveals the output for self-grading ("Got it" / "Not yet").
- **Concept cards:** a `choice` card shuffles the term with its 1–3 distractors, seeded by the card key so the order is stable. A `flip` card shows the definition.
- **Prelude cards** show the probe's prelude code above the card's code.

## Phases

Each phase ends green on its own tests and one commit.
Never `git stash` in the shared tree.
`ci-local` runs are never overlapped.

- **Phase A: toolchain and skeleton.**
  - Contents:
    - `site/` scaffold, `.nvmrc`, pinned `package.json`, `pnpm-lock.yaml`
    - the bundle loader with Ajv validation, the types and the schema-key test
    - `scripts/build-site.sh`
    - the layout shell (header, footer, theme), and a catalog page that builds from real bundles
    - `LICENSE.md` at the repo root (course content under CC BY-NC-SA 4.0, as the user chose)
  - **`ci-local.sh`** gains a step: if `node`, `pnpm` and Chromium exist, run `scripts/build-site.sh` and the site tests; otherwise print `SKIP (Node missing)`. The step is scoped like design 010 D7: `tools/ci_scope.py --site` returns `render` when `site/`, `tools/`, `scripts/`, `books.yaml` or any site book's root changed, and `skip` with the reason otherwise.
  - **Done when:** `pnpm -C site build` builds all four books; a vitest unit test runs.
- **Phase B: reading view and practice pages.**
  - Contents: the Markdown pipeline with containers, Shiki and latex stripping; all block types; turtle SVG; the practice page; prev/next navigation; report-a-problem links.
  - Tests (vitest): every container class renders; `{=latex}` is dropped; no `answer_md`, `check.source`, `hash` or non-sample `.out` text appears in any built page. That last test greps the whole `dist/` for every hidden canonical and solution stream, reusing plan 101's `answer_model` corpora through a small `uv run` helper that writes them to a temp JSON file.
- **Phase C: slides, the slide audit and the slide-break pass.**
  - Contents: `slides.ts`, the player, the audit, `site.yaml` `slides:` validation, then the tag pass on python-projects and usaco-bronze.
  - Tests:
    - slide rules on fixture blocks
    - the audit fails over the limit
    - all four books pass the audit
    - the publication digests are unchanged
- **Phase D: progress, cards, mastery, resume.**
  - Contents: `progress.ts` (IndexedDB, D11 events, schema-validated), Leitner, the card deck, the mastery map, resume on the book page.
  - Tests:
    - `normalise.ts` against all `hash_vectors.json` vectors
    - Leitner transitions
    - mastery thresholds
    - the no-IndexedDB fallback
- **Phase E: glossary, reference, search, About, privacy and terms, book pages.**
  - Contents: Pagefind, the static pages with their D5/D9 text, PDF links when released, and a `_headers` file with the strict CSP plus `X-Content-Type-Options`, `Referrer-Policy: no-referrer` and `Permissions-Policy`.
  - COOP/COEP are part C; part B's `_headers` must not set them yet.
- **Phase F: verification (named verification phase).**
  - **Playwright end-to-end, per book:**
    - open the catalog
    - read a lesson (blocks visible, a turtle SVG where the book has one)
    - step through its slides by keyboard
    - answer a typed predict card and a choice concept card
    - check a self-check box
    - reload: resume and progress persist
    - search for a glossary term
  - **Accessibility:** axe (`@axe-core/playwright`) on every page template, with 0 serious or critical violations.
  - **Lighthouse** (CLI, headless Chromium, the built site served locally): on the catalog, a lesson and the card deck, performance ≥ 0.9, accessibility ≥ 0.95, best practices ≥ 0.95.
  - **No network:** a Playwright test with every non-localhost request blocked: the pages render and work, and no request leaves the origin.
  - **The leak test** from Phase B, run over the full four-book `dist/`.
  - **`scripts/ci-local.sh`** runs solo on the final commit.

## Dispatch

- Phase A runs first (one Opus agent).
- Then B, C and D run in parallel worktrees (three Opus agents; disjoint files: the markdown and pages, the slides, and progress and cards).
- Then E (one agent). Then F, run by a fresh agent that writes the end-to-end, axe, Lighthouse and no-network tests against the built site.
- The slide-break notebook pass in Phase C is content work, done by the Phase C agent and checked at the content gate.

## Out of scope

- The runner, checks and answer gating (part C).
- COOP/COEP headers (part C).
- The PWA, offline caching and the public deploy (part D).
- Accounts and sync (part E); the LLM (part F).
- Authored `quiz` cells.
- recsys.

## Plan Review

## Content Review

## Post-Execution Report
