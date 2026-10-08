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
  - a strict CSP: `default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; style-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'`
    - `'wasm-unsafe-eval'` is for Pagefind's WebAssembly.
    - There are no inline scripts or styles: Astro's `build.inlineStylesheets: 'never'`, and the theme anti-flash script is an external file.
- **The site is generated:**
  - `site/content/<book>/` comes only from `py4kids-tools export`; nothing in the site hand-copies book text.
  - The site keys on the `site` flag and `book.json`; it never hard-codes a book id. Adding a book needs no site code.
- **Hidden answers stay hidden:**
  - Part B renders no `answer_md` (gating is part C).
  - It never prints `check.source` (assert source) or a fixture `.out` other than the sample's.
  - Hashes are never shown.
- **Toolchain:** Node 24 LTS, pinned in a new `.nvmrc`. Astro 7 needs Node ≥ 22.12, and Node 20 is end-of-life; Phase A installs it with nvm and checks `engines` against the chosen Astro. pnpm, exact pinned versions and a committed `pnpm-lock.yaml`. `pnpm install --frozen-lockfile` is the only install path.
- **Accessibility:**
  - WCAG 2.2 AA
  - keyboard operable: slides, cards, menus
  - visible focus; reduced-motion respected; light and dark themes
- **Docs** use semantic line breaks.

## Architecture

- **`site/`** is an Astro 7 static project (`output: 'static'`) with TypeScript strict mode.
  - Pages come from `getStaticPaths` over the bundles. A loader (`site/src/lib/bundle.ts`) reads `site/content/*/book.json` and the entry files at build time, and validates each against `tools/export/schema/bundle.schema.json` with Ajv (2020-12). An invalid bundle fails the build.
  - Types live in `site/src/lib/types.ts`, hand-written to the schema. A test asserts that every key the components read is declared in the schema, as plan 101's consumer test does.
- **Markdown** (`site/src/lib/markdown.ts`): markdown-it with `html: false`, so a raw `<name>` token is escaped, never dropped (python-concepts has 71 such tokens in code). It adds:
  - **GFM pipe tables** with `<th scope="col">` (acsl has 113 tables).
  - **A container plugin** for the bundle's Pandoc fenced divs: `notice` and `realprog` occur in real data; `goals`, `recap`, `opener`, `program`, `datafile` and `challenge` are kept for safety. An unknown `::: {.x}` class renders as a visible plain block, never disappears, and a test pins that.
  - **Raw blocks:** `{=latex}` blocks are dropped (none occur today; answer Markdown in part C may contain them).
  - **Code:** highlighted at build time with Shiki (no client JS).
  - **Math:** present in real data (acsl unit 8 and `reference_md` use `$\overline{A}$`). It is rendered at build time with KaTeX, with self-hosted fonts, under **Pandoc's `tex_math_dollars` rule**: an opening `$` not followed by a space; a closing `$` not preceded by a space and not followed by a digit. So python-concepts unit 3's "Under 13 costs $6. Ages 13–17 cost $8" stays text. Both sentences are vitest fixtures.
- **No bundle JSON reaches the client.** Pages are rendered at build time. No `site/content/**/entries/*.json` (or `book.json`) is copied into `dist/`. Islands receive only a build-time **projection** as a small inline-free JSON data file per page: a card deck gets card keys, prompts, outputs or terms, modes and concept ids, never `answer_md`, `check.*` or hashes. The leak test also asserts that no `*.json` under `dist/` contains the keys `answer_md`, `source`, `hash` or `program`.
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
  - **Event kinds written in part B:**
    - `slide` (each slide viewed)
    - `card` (`detail.box`, `detail.self_grade`)
    - `self-check` (the practice page's checklist, `detail.checklist`)
  - Reading position lives only in the `resume` store. Part B writes no `lesson-run` event, so the D11 stream that part E will sync stays truthful.
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
| `/<book>/<entry>/` | reading view: blocks in order. Code blocks show their stored output under "Output". Try-it, error-demo and hang-demo blocks are labelled as in the PDFs. Turtle figures are drawn as inline SVG (see below). Prev/next navigation; a "Slides" button |
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

**Turtle SVG:** 22 figures, 1–144 segments each.
- Turtle space has y pointing up, so it is flipped with `scale(1,-1)`.
- `viewBox` is the segments' bounding box, padded by 10 units plus the largest stroke width.
- A fixed white background `rect` keeps black strokes visible in dark mode.
- Colours are the turtle's colour names, passed through as SVG colour keywords.
- Each figure has `role="img"` and an `aria-label` taken from its nearest heading ("Drawing for <heading>").

## Slide mode and the slide audit (D6)

- **Slide rules** (`site/src/lib/slides.ts`, one function shared by the player and the audit):
  - opener, goals, recap and each code(+output) block start a slide
  - a notice attaches to the adjacent code slide when the pair stays within budget; otherwise it is its own slide (python-projects has 210 notices, many under 20 words). The audit reports notice-only slides as a count, not a failure
  - **Every prose-like block splits inside itself** (prose, opener, goals, recap, notice). Its `md` is cut at paragraph boundaries and at top-level list-item boundaries (blank lines outside code fences; a fenced block is never cut) into *units*.
    - A **pipe table is one atomic unit**, measured by rows (`max_table_rows`, default 12), and its words do not count toward `max_words`.
    - Units of consecutive prose blocks are packed into slides of up to `max_words` (default 90).
    - A heading always starts a new slide.
    - A unit longer than `max_words` becomes one slide on its own.
    - Real case: acsl `unit-12-graph-theory/lesson/l-009#2` is 518 words in one block and splits into its paragraphs.
  - try-it, demo and figure blocks are one slide each
  - a block tagged `slide-break` starts a new slide; one tagged `slide-skip` is left out of slides (it still shows in the reading view)
- **Player:**
  - full-viewport, arrow keys and swipe, a progress bar, the slide number in the URL hash
  - Escape returns to the reading view
  - each slide viewed writes a `slide` event
- **Measured before the rule change (real bundles, 2026-10-07, [fable]), with blocks indivisible:**

  | book | oversized slides | mostly |
  |---|---|---|
  | usaco-bronze | 13 | 12 recaps of 93–117 words, 1 opener |
  | python-projects | 3 | prose of 99 and 95 words, a recap of 91 |
  | python-concepts | 5 | one prose block of 129 words |
  | acsl | 192 | 173 prose blocks over 90 words (max 518), 98 of them containing tables, and 29 single paragraphs over 90 words |

  **Expected after in-block splitting:** recaps, goals and lists split at items; tables are atomic. What can remain is single paragraphs over `max_unit_words` (about 29 in acsl, about 0 elsewhere) and tables over `max_table_rows`. Phase C records the measured result.
- **Slide audit:** `pnpm -C site slide-audit` reports, per book, every **indivisible unit** over `max_unit_words` (default 150: one paragraph too long for a slide), every table over `max_table_rows`, and every code slide over `max_code_lines`.
  - A remaining oversized unit is either split by a `slide-break` (where it spans blocks) or listed by key in `<book>/site.yaml` `slides.allow: [{key, reason}]`: an explicit, reviewed list, like `[WONTFIX]`. A ceiling is never raised to make the audit pass.
  - The content gate reviews the allow list.
  - Packed slides cannot exceed `max_words` by construction, apart from single oversized units, which the audit catches.
  - Phase C runs the audit on all four real bundles before and after the tag pass, and records the counts. The thresholds come from a new optional `slides:` block in `<book>/site.yaml` (`max_words`, `max_unit_words`, `max_table_rows`, `max_code_lines`, `allow`), validated by `tools/books.py`. Any slide over the limit fails CI.
- **Slide-break pass (moved here from plan 102):**
  - python-projects and usaco-bronze lessons get `slide-break` (and, rarely, `slide-skip`) cell tags where packing gives poor slides: splits a reader would not choose, or a figure separated from its explanation.
  - An oversized paragraph that only a text edit could fix goes into `slides.allow` with its reason (no notebook text changes in this plan).
  - This data shows python-projects does not split "poorly"; its tag pass is expected to be small.
  - These are cell-tag-only notebook edits: no source text changes, and the PDFs are unchanged (the publication regression digests stay byte-identical, which a test asserts).
  - python-concepts and acsl must pass the audit as they are, or get the same pass.

## Mastery map and cards (D8)

- **Concept mastery:**
  - **Where concepts come from:**
    - a predict card's concepts are its block's `concepts` (looked up by `block` key)
    - a concept card's concept is its `concept`
    - an item's concepts are its `concepts`
  - **Weighting:** a card attributed to k concepts adds 1/k to each, so one python-concepts card that carries 17 concept ids cannot move 17 concepts at full weight. A concept's mastery is the weighted share of its cards in Leitner box ≥ 3.
  - The map shows a concept only when it has at least **N = 3** attributed cards or items.
  - A concept that meets N with items but has no cards shows "practice in exercises" instead of a percentage (part C will add item results).
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
  - **`ci-local.sh`** gains a step: if `node` (≥ 22.12), `pnpm` and Chromium exist, run `scripts/build-site.sh` and the site tests; otherwise print `SKIP (Node missing)`. The step is scoped like design 010 D7.
    - `tools/ci_scope.py` gains a `--site` mode: an interface change, because it requires `--book` today, so the CLI accepts exactly one of `--book` or `--site`.
    - `--site` returns `render` when `site/`, `tools/`, `scripts/`, `books.yaml` or any site book's root changed, and `skip` with the reason otherwise.
  - **Done when:** `pnpm -C site build` builds all four books; a vitest unit test runs.
- **Phase B: reading view and practice pages.**
  - Contents: the Markdown pipeline with containers, Shiki and latex stripping; all block types; turtle SVG; the practice page; prev/next navigation; report-a-problem links.
  - **Tests (vitest):**
    - every container class renders
    - `{=latex}` is dropped
  - **Markdown tests:**
    - a GFM table with `<th scope>`
    - an unknown container class renders visibly
    - a `<name>` token is escaped
    - the two dollar-sign fixtures
  - **The structural leak test (poisoned bundle).** The site must never render a field that may hold hidden material. The bundle's own content is already proven by plan 101's answer model.
    - A test copies each real bundle and writes a unique sentinel string into every forbidden field: `answer_md`, `check.source`, `check.hash`, `check.program` of a hidden item, and every non-sample fixture `.out` file.
    - It builds the site from the poisoned bundles and searches all of `dist/` for any sentinel: HTML, JS, CSS, JSON, and Pagefind's index and fragment files (decompressed).
    - Zero hits is required. A regression deliberately renders one forbidden field and must be caught.
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
  - **No network, proven three ways:**
    - **Request recording:** Playwright records every request (`page.on('request')`) across the end-to-end paths, and any request whose origin is not the local server fails the test. Requests are recorded, not merely blocked, so a page that silently recovers from a blocked call still fails.
    - **Build audit:** a scan of `dist/` finds no `http(s)://` URL in any `src`, `srcset`, CSS `url()`, `@import`, `fetch`, `import` or `<link>` (other than a hyperlink). The only absolute URLs allowed are plain `<a href>` hyperlinks on an allowlist: the GitHub issue link, the release PDF links and the CC license deed. These are user-initiated navigations, not loads.
    - **Headers:** the test server (`site/scripts/serve.mjs`) applies `dist/_headers` with the Cloudflare Pages `_headers` semantics.
      - It asserts that every HTML response carries the CSP and the other headers.
      - It records `securitypolicyviolation` events on every template, `/search/` included (Pagefind's WebAssembly), and requires zero.
      - A deliberately injected inline script is reported as a violation.
      - Part D re-verifies the headers on the real host.
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

### Round 1 (369a818)

- `[sol]` **REJECT** (gpt-6-sol):
  - `[FIXED]` Prose blocks were indivisible (acsl `l-009#2` is 518 words): paragraph-level units, an audit on indivisible units (`max_unit_words`), run on all four real bundles.
  - `[FIXED]` A plain grep of `dist/` would flag legitimate shared values: replaced by the poisoned-bundle sentinel test, which is structural and occurrence-free and also covers JS and the Pagefind index.
  - `[FIXED]` Blocking does not prove no request: requests are recorded, external URLs are audited in the build, and headers are asserted through a local server that applies `_headers`; the adult GitHub link and PDF links are allowlisted hyperlinks.
  - `[FIXED]` (nit) Predict-card concepts come from their block; concepts with only items show "practice in exercises".

- `[fable]` **REJECT** (round 1, 369a818):
  - `[FIXED]` The slide audit could not pass with blocks indivisible (usaco 12 recap slides, acsl 192). Every prose-like block now splits at paragraphs and list items; tables are atomic with `max_table_rows`; measured targets are recorded; remaining units need a reviewed `slides.allow` entry, never a raised ceiling.
  - `[FIXED]` (nits)
    - a CSP with `'wasm-unsafe-eval'`, no inline styles or scripts, and a zero-violation test
    - Pandoc dollar math, with KaTeX fixtures
    - `html: false`, GFM tables, unknown containers rendered visibly
    - a build-time projection, so no bundle JSON reaches the client, plus a JSON key scan
    - no `lesson-run` in part B, and `self-check` events
    - Node 24 LTS
    - 1/k concept weighting
    - the turtle SVG spec
    - notices attached to their code slide
    - the `ci_scope --site` interface change

## Content Review

## Post-Execution Report
