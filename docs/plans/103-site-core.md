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
  - a strict CSP: `default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; style-src 'self'; img-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'`
    - `'wasm-unsafe-eval'` is for Pagefind's WebAssembly.
    - There are no inline scripts or styles: Astro's `build.inlineStylesheets: 'never'`, and the theme anti-flash script is an external file.
    - No `data:` images: Shiki and KaTeX emit none, and turtle figures are inline SVG. The CSP test confirms that no `data:` URL appears in `dist/`.
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
  - **Code:** highlighted at build time with Shiki (no client JS), using `@shikijs/transformers`' `transformerStyleToClass`. Shiki's default output puts inline `style` attributes on tokens, which the CSP forbids; this transformer gives tokens classes and generates one stylesheet, which also serves the light and dark themes.
  - **Math:** present in real data (acsl unit 8 and `reference_md` use `$\overline{A}$`). It is rendered at build time with KaTeX in **MathML-only output** (`output: 'mathml'`). KaTeX's HTML output uses inline `style` attributes, which the CSP forbids; MathML has none and is rendered natively by current browsers, so no KaTeX CSS or fonts ship. Dollar signs follow **Pandoc's `tex_math_dollars` rule**: an opening `$` not followed by a space; a closing `$` not preceded by a space and not followed by a digit. So python-concepts unit 3's "Under 13 costs $6. Ages 13–17 cost $8" stays text. Both sentences are vitest fixtures.
- **No bundle JSON reaches the client.** Pages are rendered at build time. No `site/content/**/entries/*.json` (or `book.json`) is copied into `dist/`. Islands receive only a build-time **projection** as a small inline-free JSON data file per page: a card deck gets card keys, prompts, outputs or terms, modes and concept ids, never `answer_md`, `check.*` or hashes. The leak test also asserts that no `*.json` under `dist/` contains the keys `answer_md`, `source` or `hash`. (`program` is also a block type name, so `check.program` is covered by the sentinel test instead.)
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
    - A list item's indented continuation lines stay with their item, and a nested list is never split from its parent item. The slide-rules test pins usaco-bronze unit 1's 110-word, 6-bullet recap.
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

  **Expected after in-block splitting** (re-measured by [fable], round 3):
  - no paragraph over 150 words in any book
  - 12 acsl units and 1 usaco-bronze unit between 90 and 150 words
  - 1 acsl table over 12 rows (the one expected `slides.allow` entry)

  Phase C **asserts** these counts in a test, not just records them.
- **Two limits, stated plainly:**
  - `max_words` (90) is the **packing budget**.
  - `max_unit_words` (150) and `max_table_rows` (12) are the **failure limits**.
  - A unit between 90 and 150 words becomes one slide over the packing budget. The audit **reports** each such slide (expected: 13) and does not fail on it. Only units over the failure limits fail CI.
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
  - **`ci-local.sh`** gains a step: it resolves scope first (`tools/ci_scope.py --site`). When the site is in scope, it requires `node` (≥ 22.12), `pnpm` and Chromium, and **fails** if any is missing (content review, round 2: a site change must never pass unverified), then runs `scripts/build-site.sh` and the site tests. An out-of-scope change prints `SKIP: site (<reason>)`. This is stricter than design 012 §3's local `SKIP (Node missing)`.
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
    - A test copies each real bundle and writes a unique sentinel into every forbidden field: `answer_md`, `check.source`, `check.hash`, `check.program` of a hidden item, and every non-sample fixture `.out` file.
      - Sentinels respect the schema so the loader accepts the poisoned bundle: `check.hash` gets `sha256:` plus 64 hex characters derived from its sentinel, and the search looks for that hex. The other fields take free text.
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
  - **Accessibility:** axe (`@axe-core/playwright`) on every page template, plus acsl unit 08's math lesson (MathML is in the accessibility tree), with 0 violations carrying a WCAG 2.2 A or AA tag, whatever their impact (content review 1, [sol] 3).
  - **Lighthouse** (CLI, headless Chromium, the built site served locally): on the catalog, a lesson and the card deck, performance ≥ 0.9, accessibility ≥ 0.95, best practices ≥ 0.95.
  - **No network, proven three ways:**
    - **Request recording:** Playwright records every request (`page.on('request')`) across the end-to-end paths, and any request whose origin is not the local server fails the test. Requests are recorded, not merely blocked, so a page that silently recovers from a blocked call still fails.
    - **Same-origin requests carry nothing:** after the card, checklist and progress interactions, every recorded same-origin request must be:
      - a `GET` (or a `HEAD`) with no body, no `sendBeacon` and no WebSocket
      - for a path that exists in `dist/`
      - free of any query string other than Pagefind's own fragment and index paths
      - free of the test's typed answers, checklist state and card results (the test types unique sentinel strings and asserts that none appears in any request URL or header)
    - **Build audit:** a scan of `dist/` finds no `http(s)://` URL in any `src`, `srcset`, CSS `url()`, `@import`, `fetch`, `import` or `<link>` (other than a hyperlink). The only absolute URLs allowed are plain `<a href>` hyperlinks on an allowlist: the GitHub issue link, the release PDF links and the CC license deed. These are user-initiated navigations, not loads.
    - **Headers:** the test server (`site/scripts/serve.mjs`) applies `dist/_headers` with the Cloudflare Pages `_headers` semantics.
      - It asserts that every HTML response carries the CSP and the other headers.
      - It records `securitypolicyviolation` events on every template, `/search/` included (Pagefind's WebAssembly), plus a real math lesson (acsl unit 08's `$\overline{A}$`) and the acsl reference page, and requires zero.
      - It also asserts that no element in `dist/` HTML carries a `style` attribute.
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

- `[sol]` **REJECT** (round 2, a968ea1): `[FIXED]` Same-origin requests were unaudited. Now every same-origin request must be a body-less GET for an existing `dist/` path, with no unexpected query string and no typed sentinel in any URL or header.

- `[fable]` **APPROVE WITH NITS** (round 3, bb6528b): re-measured, in-block splitting brings every book under the audit with one expected allow entry.
  - `[FIXED]` (nits)
    - expected counts asserted
    - the 90–150-word gap named
    - list-item continuation rule, with the usaco recap fixture
    - schema-shaped hash sentinels
    - `data:` dropped from `img-src`
    - the JSON key scan without `program`

- `[sol]` **REJECT** (round 3, bb6528b):
  - `[FIXED]` KaTeX's HTML output uses inline styles, which the CSP forbids. Math is now MathML-only, and the zero-violation test names a real math lesson and checks that no element carries a `style` attribute.
  - `[FIXED]` (nits) The two slide limits are stated, and slides between them are reported; schema-shaped hash sentinels (already folded from [fable]).

- `[fable]` **APPROVE WITH NITS** (round 4, 7ff1940): MathML Core renders `\overline` natively. `[FIXED]` Shiki uses `transformerStyleToClass` (no inline styles); axe also runs on the math lesson.

### Round 4 (7ff1940 / 77da698) — CONSENSUS

- `[self]` APPROVE.
- `[sol]` **APPROVE WITH NITS** (gpt-6-sol): the MathML fix resolves the round-3 blocker. `[FIXED]` Its Shiki inline-style nit was already folded in 77da698 (`transformerStyleToClass`).
- `[fable]` **APPROVE WITH NITS**: all folds confirmed; its nit was folded in 77da698.
- `[glm]` removed from the roster (user directive 2026-10-05).

## Content Review

Gate roster per `docs/content-review-gate.md`: [self], [sol], [fable] ([glm] removed by the user on 2026-10-05). [sol] runs gpt-6-sol, falling back to gpt-5.6-sol.

### Review 1 — [fable] (2026-10-08)
- **Verdict**: APPROVE WITH NITS. Built and browsed a copy:
  - **Privacy:** 173 requests, 0 off-origin, 0 non-GET. The IndexedDB contents match the D11 schema, and no typed sentinel is stored. The privacy, terms and about text is accurate.
  - **Hidden answers:** 12 hidden items across all six kinds checked, with 0 leaks in HTML, JS, JSON or the Pagefind index; 889 hidden fixture outputs scanned.
  - **Lighthouse:** 1.0, 0.99 and 0.99. axe reports 0 serious violations.
1. `[OPEN]` The plan's Content Review and Post-Execution Report sections are empty. Should Fix (done in the ship step).
2. `[FIXED]` Long allow-listed code slides show no scroll cue. Nice to Have.
   → Response: the slide player adds `.is-overflowing` to a code panel while `scrollHeight - scrollTop > clientHeight` (checked on show, scroll and resize); `slides.css` then fades the panel's bottom edge and shows a "Scroll the code for more ↓" label (a class, no inline style), removed once the code is scrolled to the end. Test: `e2e/review-fixes.spec.ts` (the 53-line `l1_cards.py` slide shows the cue and loses it at the end; a short code slide shows none).
3. `[FIXED]` The mastery map dominates a fresh book page (40 rows at 0%). Nice to Have.
   → Response: the concept rows now sit in a `<details>` ("All N concepts"), collapsed by default; the mastery island opens it once the reader has reviewed at least one card of the book. Test: `e2e/review-fixes.spec.ts` (collapsed on a fresh page, open after one card review).
4. `[FIXED]` The leak test fails confusingly on Node 20: add a clear version guard and a README note. Nice to Have.
   → Response: `test/leak.test.ts` now stops at import on Node < 22.12 with a message naming the version and the fix (`source scripts/site-env.sh && site_node_env`), from `test/helpers/node-version.ts` (unit-tested in `test/node-version.test.ts`); `site/README.md` puts that command first in its commands and notes the guard.
5. `[FIXED]` Resume can land on a practice page while the catalog label implies reading. Nice to Have.
   → Response: chose labelling over restricting. `pageContext` adds `resumeTitle`, the entry title plus the page kind — `(lesson)`/`(reading)`, `(slides)`, or the practice heading `(exercises)`/`(questions)`/`(problems)` — rendered as `data-resume-title` and stored with the resume position, so the link reads e.g. "Continue: Turtle Art Studio (exercises)". The practice heading moved to `practiceHeading` so the page and the label share it. Tests: `test/cards.test.ts` (every page kind), `e2e/review-fixes.spec.ts` (practice resume) and `e2e/journey.spec.ts` (slides resume).

### Review 1 — [sol] (2026-10-08, gpt-6-sol)
- **Verdict**: REJECT.
1. `[FIXED]` Leitner promotes cards that are not yet due ("Start again" can reach mastery box 3 immediately). Practice on a card that is not due must not advance its box or its mastery. Must Fix.
   → Response: `leitner.review` now leaves a card that is not due unchanged on a correct answer (box and due date kept, only `updated_at` moves); the deck still writes its `card` event (`pass`, the unchanged box). Decision, documented in `leitner.ts`: a miss still sends a card to box 1 at any time, since a wrong answer is real evidence and can only lower mastery, never raise it. The mastery-map text now reads "answered right twice, at least a day apart" and the deck's end screen says an early card stays in its box. Tests (`test/leitner.test.ts`, `test/progress.test.ts`): an early correct review does not promote; the same card promotes once due; an early miss resets; ten "Start again" rounds stay in box 2 (below box 3); mastery is unchanged by early reviews; `recordCardReview` records the early event without promoting.
2. `[FIXED]` Slide events cannot identify each slide: one block split across slides shares one key (acsl graph-theory, `l-001` ×4). Use a schema-valid per-slide identifier, and test slides split from one block. Must Fix.
   → Response: `slides.ts` `slideKeys` names each slide by its first block's key, and the k-th (k ≥ 2) slide starting with the same block `<block key>#slide-<k>` (so `l-001`, `l-001#slide-2`, `#slide-3`, `#slide-4`); an unsplit block's slide keeps exactly its block key. The schema's `item_key` pattern already accepts any `#…` suffix (block keys such as `…/l-018#2` become `…/l-018#2#slide-2`), so the schema is unchanged. The deck's `data-key`, the `py4kids:slide` event and the stored `slide` event all carry it; resume reads the URL hash and mastery reads only card states, so neither changes. Tests: `test/slides.test.ts` (a split-block fixture, a `#2` block key, and the real acsl unit 12 deck plus every deck of every book: distinct keys, each event valid under the hand-written validator and Ajv) and `e2e/review-fixes.spec.ts` (acsl unit 12 stepped through: distinct `data-key`s and one stored slide event key per slide).
3. `[FIXED]` The a11y gate fails only on serious and critical results; it must fail on every violation carrying a WCAG 2.2 AA tag. Must Fix.
   → Response: `e2e/a11y.spec.ts` now fails on every violation carrying `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa` or `wcag22aa`, whatever its impact, and prints only best-practice-only ones; a predicate test proves the filter ignores impact. The stricter gate surfaced no site defect: all 32 template × scheme runs report zero violations of any kind.
4. `[FIXED]` Normalisation parity for `exact` and `aliases` is unverified on this branch: the Python producer and the 41 vectors come with plan 102. Should Fix: plan 102 merges first, then main is merged into 103 so the vector test covers all 41 vectors.
   → Response: the TS `normalise` is unchanged. `test/normalise.test.ts` adds "parity with Python: every hash_vectors.json vector, all fields": it runs every vector with its `case` and, when present, `whitespace` and `aliases`, checking both the normalised text and the hash, and fails on any vector field it does not know. This branch carries 28 vectors (none with `whitespace`/`aliases`). Parity is complete when plan 102 merges first and main is merged into this branch: the same test then covers all 41 vectors with no change.

### Review 2 — [sol] (2026-10-08, gpt-6-sol)
- **Verdict**: REJECT. Confirms that the Leitner, per-slide-key and WCAG-gate fixes are present.
1. `[FIXED]` The site step could print SKIP for missing tools and still reach ALL GREEN. Must Fix. → Response: `ci-local.sh` now resolves scope first. An in-scope site change fails if Node ≥ 22.12, pnpm or Chromium is missing; only an out-of-scope change skips, and the skip is printed. `tests/test_ci_scope.py::test_ci_local_site_step` pins this.
2. `[OPEN]` Normalisation parity: the same point as round 1 [sol] 4. It closes when plan 102 (the Python producer and its 41 vectors) merges first and main is merged into this branch; the parity test then runs on all vectors. Should Fix.

### Review 2 — [fable] (2026-10-08)
- **Verdict**: APPROVE. Rebuilt a fresh copy: 267/267 vitest and 68/68 e2e pass, Lighthouse 1.0, 0.99 and 0.97, zero WCAG A/AA violations. Every fix was verified in its own browser run (scroll cue, collapsed map, Node guard, resume label, no early promotion, 75 distinct slide keys on acsl unit 12).
1. `[WONTFIX]` (Nice to Have) A split sub-block gets a double suffix (`l-018#2#slide-2`). → Response: schema-valid and distinct. Recorded as a key-format note for part E's sync design, which must treat everything after the first `#` as one opaque fragment.

## Post-Execution Report
