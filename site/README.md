# The learning-website bundle

Design 012 part A (plan 101).
The notebooks stay the source of truth: the bundle under `site/content/` is generated, never hand-edited, and never committed (`.gitignore`).
Only the id ledgers under `site/ids/` and each book's `<book>/site.yaml` are committed.

## Regenerate

```bash
uv run py4kids-tools --book <book> export                  # writes site/content/<book>/
uv run py4kids-tools --book <book> export --out DIR --release <tag>
uv run py4kids-tools --book <book> site-check              # export to build/site-check/<book>/ and check it
uv run py4kids-tools --book <book> classify [--unit ID] [--apply]
```

Only books with `site: true` in `books.yaml` export; any other book exits 2.
`--release <tag>` fills `book.json`'s `pdfs` with that GitHub Release's PDF links (`null` while `unreleased`).
The export report (probe statuses, unattributed concepts, classification, self-check reasons, derived answer formats, fixture notes, distractor fallbacks) goes to `build/site-report/<book>.json`, never into the bundle.

## Layout

| path | holds |
|---|---|
| `book.json` | `schema_version`, `book` (id, title, subtitle, flags), `release` (tag, content hash), `entries` in syllabus order, `concepts`, `glossary`, `reference_md`, `settings`, `pdfs` |
| `entries/<entry-id>.json` | one unit, checkpoint or project: `entry`, `lesson` (blocks, or `null`), `intro`, `items`, `outro`, `cards`, `files` |
| `files/<entry-id>/<path>` | every file a block or item lists (lesson assets, project data files) |
| `files/<entry-id>/fixtures/<stem>/<n>.in`, `.out` | the fixture pairs of a `fixtures` item |

The schema is `tools/export/schema/bundle.schema.json` (JSON Schema 2020-12); every written file is validated against it.
A glossary concept card sits in the `cards` of the entry of its term's first unit.
Only git-tracked files that the student editions may print are copied, plus fixture pairs.
Solution sources (`assets/exN.py`, `qN.py`, `pN.py`), `assets/verify/**` and solution notebooks never ship.

The bundle is deterministic: JSON is written with sorted keys, `indent=1` and a trailing newline, with no timestamps or absolute paths.
`release.content_hash` is sha256 over every bundle file in sorted path order (each framed as `path NUL length NUL bytes`), with `book.json` hashed without its `release` object.

## The id ledger

Every block, item and card has a global key `book/entry/notebook/cell_id` (plus `#n`, `#asset:<name>` or `#predict`; concept cards are `book/back-matter/glossary/<concept-id>`).
Progress is stored under these keys, so a key must not silently vanish.

- `site/ids/<book>.json` is the sorted key list of the last release, written by `export --update-ledger`.
  Update it at each public release.
- A key that leaves the bundle must be mapped in `site/ids/<book>-retired.yaml`, as `<old key>: <new key>` or `<old key>: retired`.
  `site-check` fails on a ledger key that is neither in the bundle nor mapped there.

## The website (plan 103)

`site/` is also the Astro 7 static site that renders every `site: true` book from its bundle.

```bash
source scripts/site-env.sh && site_node_env   # first, in each shell: Node >= 22.12 (the .nvmrc Node 24) on PATH
bash scripts/build-site.sh [--release <tag>]   # export every site book, then build site/dist/
pnpm -C site test                              # vitest
pnpm -C site e2e                               # Playwright on the built dist/ (build first)
pnpm -C site dev                               # local preview of the exported bundles
```

- **Toolchain:** Node 24 LTS (`.nvmrc`; `nvm install`), pnpm at the version in `package.json` `packageManager` (`corepack enable`).
  The tests need it too: on an older Node `test/leak.test.ts` (which builds the site) stops at once and says so.
  Dependencies are exact-pinned; `pnpm install --frozen-lockfile` is the only install path.
- **Loader:** `src/lib/bundle.ts` discovers `content/*/book.json`, validates every file against `tools/export/schema/bundle.schema.json` with Ajv, and fails the build on an invalid bundle.
  `PY4KIDS_SITE_CONTENT=<dir>` points it at another content directory.
- **Types:** `src/lib/types.ts` is hand-written to the schema.
  `test/schema-keys.test.ts` proves every key the site reads is declared there; add each new bundle-reading view model to its `CONSUMERS`.
- **No inline scripts or styles** (the strict CSP): styles are external stylesheets, client code is external modules, and the theme script is `public/scripts/theme.js`.
- **Slides:** `src/lib/slides.ts` holds the slide rules (plan 103 D6), used by both the player (`/<book>/<entry>/slides/`) and the audit.
  `pnpm -C site slide-audit` (run by `scripts/build-site.sh`) fails on a unit over `max_unit_words`, a table over `max_table_rows` or a code slide over `max_code_lines`, and reports units over the `max_words` packing budget and notice-only slides.
  Limits and reviewed exceptions live in `<book>/site.yaml` `slides:` (`tools/books.py` validates it); a lesson cell tagged `slide-break` starts a new slide, one tagged `slide-skip` stays out of the slides.
  The player dispatches a `py4kids:slide` DOM event (`{book, entry, index, key, count}`) per slide viewed; it stores nothing itself.
- `scripts/ci-local.sh` step 6 builds the site and runs its tests when the change touches it (`tools/ci_scope.py --site`).
- **Progress (Phase D):** `src/lib/progress.ts` is the on-device IndexedDB store `py4kids` (`events`, `cards`, `resume`); every event is validated against `tools/export/schema/progress-event.schema.json` before it is written.
  Without IndexedDB the site keeps working in memory and says once that nothing is saved.
  The DOM contract the islands share (`py4kids:slide`, `[data-item-key]` checklists, `[data-resume-book]` links) is in `src/lib/dom-events.ts`.
- **Cards and mastery:** `/<book>/cards/` drills the deck from `deck.json`, and the book page's mastery map reads `mastery.json`.
  Both are build-time projections (`src/lib/cards.ts`, `src/lib/mastery.ts`) with no `answer_md`, `check.*` or hash.
  `src/lib/normalise.ts` ports `tools/export/normalise.py`, checked against every vector in `tools/export/hash_vectors.json`.
- **Book pages (Phase E):** `/<book>/` lists the contents in syllabus order, with resume, quiz cards, the glossary (`/<book>/glossary/`), the quick reference (`/<book>/reference/`), the mastery map, and the release PDFs only when `book.json` `pdfs` is set (`--release`).
  Their view models are in `src/lib/book-page.ts`.
- **Search:** `pnpm -C site search-index` (run by `scripts/build-site.sh` after `astro build`) runs Pagefind over `dist/` and removes Pagefind's prebuilt UI, which the site does not use.
  Only pages with `data-pagefind-body` are indexed (reading views, practice pages, glossaries, references); the About, privacy, terms, search, catalog, book, card and slide pages are not.
  `/search/` is the site's own small UI (`src/scripts/search.ts`) on Pagefind's JS API, loaded from `/pagefind/` on the same origin.
- **Headers:** `public/_headers` (Cloudflare Pages format) sets the strict CSP, `X-Content-Type-Options`, `Referrer-Policy` and `Permissions-Policy` for every path; COOP/COEP come with part C.
- **Favicon:** `public/favicon.svg`, and `public/favicon.ico` written by `node scripts/favicon.ts`.
- **Browser tests (Phase F):** `pnpm -C site e2e` runs Playwright (`e2e/*.spec.ts`) on Chromium against `dist/`, served by `scripts/serve.mjs`, which applies `dist/_headers` with the Cloudflare Pages semantics (`test/serve.test.ts`).
  They cover a journey per book (catalog, lesson, self-check, slides by keyboard, cards, search, persistence after reload), axe on every template in both colour schemes, the no-network proofs (request recording, the build audit of absolute URLs, the headers and zero CSP violations) and, last and alone, Lighthouse budgets on the catalog, a lesson and the card deck (median of three runs).
  Playwright's own Chromium is used when downloaded (`pnpm -C site exec playwright install chromium`), else a system Chromium; `PY4KIDS_CHROMIUM` overrides both.

## The Python runner (plan 104)

Student code never runs on the site's origin. `runner/` (a sibling app: Node 24, pnpm, exact pins, its own lockfile) is the runner page that the site embeds in `<iframe sandbox="allow-scripts allow-same-origin" allow="cross-origin-isolated">` on its own origin.

- **Origins:** configured only in `deploy/origins.json` (plan 105; read through `deploy/origins.mjs`; development: site `http://127.0.0.1:4391`, runner `http://localhost:4392`); `PY4KIDS_TARGET=production` builds for the production and preview pairs, and `PY4KIDS_SITE_ORIGIN` / `PY4KIDS_RUNNER_ORIGIN` override everything with one pair. The site build fills the CSP's `frame-src` in `dist/_headers`; the runner build fills its `frame-ancestors`, and each app picks its partner origin at run time from its own `location.origin`. See `deploy/README.md` for the same-site rule.
- **Build:** `scripts/build-site.sh` also runs `pnpm -C runner build` (to `runner/dist/`): the page, a content-hashed worker with `runner/py/harness.py` and the `fake_turtle` port bundled in, and the self-hosted Pyodide 0.27.8 under `pyodide/0.27.8/`.
- **Envelopes:** `runner/schema/request.schema.json` and `reply.schema.json`; `runner/src/envelope.ts` is their hand-written twin used on both sides (`pnpm -C runner test` proves they agree with Ajv).
- **Client:** `src/lib/runner-client.ts` (`connectRunner`, `RunnerClient`: `ping`, `run`, `interrupt`, `reset`) binds replies by origin, iframe window and pending id, and times out as "runner unavailable".
- **Serve both:** `node scripts/serve-both.mjs` (the e2e config starts both servers itself). `e2e/runner.spec.ts` drives the real client, iframe and workers.
- **Harness tests:** `uv run pytest tests/test_runner_harness.py` (CPython: `outputs_match` parity with `tools/judge.py`, stdin and `EOFError`, grading, the turtle port and rule).

### Checks, Run and answers (plan 104 Phase B)

- **Projections** (`src/lib/checks.ts`; shapes and rules in `src/lib/check-model.ts`), each a small same-origin file fetched only when needed, never bundle JSON:
  - `/<book>/<entry>/practice/check/<anchor>.json` (every item, fetched on Check or Run): the salted hash and answer format (`answer`, `predict`, `expected-output`), the shipped asserts split one statement each (for the runner only, never rendered), or the fixture cases' file URLs, sample first, with `skipped` for `over_budget` cases and the per-case `budget_ms` (from `check.cpu_ms` when present, else 5 s).
  - `/<book>/<entry>/practice/answer/<anchor>.json`: only for odd unit exercises (`answer_visibility: after-attempt`): `answer_md` rendered (`{=latex}` dropped) with `answer_figures` drawn as SVG. It is fetched only after a genuine attempt: a Check run, a submitted answer, or, for a self-check item, a Run plus the checklist marked done.
  - `/<book>/<entry>/run.json`: a lesson's runnable blocks (code, prelude, stdin, files).
  - `/<book>/files/<entry>/<path>`: the bundle's files (lesson assets, fixture pairs), byte for byte.
  - The leak tests allow an item's hash and asserts only in its own check file, an odd answer only in its own answer file, and a hidden `.out` only as its served file; a predict item's program is allowed nowhere.
- **Islands:** `src/scripts/practice.ts` (editors, Run, Check, Stop, answer boxes, gating), `src/scripts/lesson-run.ts` (Run, Reset and input boxes in the reading view; one session per lesson, prelude replay), `src/scripts/run-support.ts` (the page's one runner connection, opened on the first Run or Check).
- **Editor:** CodeMirror 6 (`src/scripts/editor.ts`), loaded by dynamic import when an editor nears the screen and mounted in a shadow root, so `style-mod` uses constructable stylesheets (zero CSP violations: `e2e/checks.spec.ts`). The page's `<textarea>` holding the starter is the fallback.
- **Progress:** each Check writes an `exercise`, `checkpoint` or `project` event with `detail.cases`, and each lesson Run a `lesson-run` event; code and typed answers go only to the on-device `attempts` store (database version 2).
- `test/schema-keys.test.ts` lists the optional keys the site reads before their schema change lands here (`PENDING_KEYS`: plan 102's `also_check`, `aliases` and `whitespace`; Phase C's `cpu_ms` and `answer_figures`); drop each once it is declared.

### Verification (plan 104 Phase D)

`pnpm -C site e2e` runs the browser suites below (with part B's journeys, axe, headers and Lighthouse); `pnpm -C site e2e:solvers` runs the slow reference-solver parity on its own.
`scripts/ci-local.sh` runs both in its site step.

- **Design 012 §3 runner acceptance**, one named test per row:
  - stdin, including `input()` at end of input: `runner.spec.ts` "input() reads stdin, and at the end of input raises EOFError as in CPython"; in the reading view, `checks.spec.ts` "the reading view: …input() reads the box".
  - interrupt on a hang: `runner.spec.ts` "a hang is stopped by the SharedArrayBuffer interrupt…" (`interrupts: "sab"`) and "a loop that swallows the interrupt is stopped by the grace restart"; the restart path with isolation disabled: `runner-unisolated.spec.ts` (`interrupts: "restart"`).
  - recursion depth and float formatting: `runner.spec.ts` "§3 recursion depth and float formatting match CPython" (20 expressions; CPython's output is computed at test time with `uv run python`).
  - function-assert isolation: `acceptance.spec.ts` "§3 function-assert isolation…" (six asserts, mixed verdicts, no source in the DOM or the stores); also `runner.spec.ts` "checks grade fixtures…, asserts…" and `checks.spec.ts` "asserts: a verdict per test, never the source".
  - short-answer hashing and normalisation: `acceptance.spec.ts` "§3 short-answer hashing and normalisation: every hash_vectors.json vector…" (each pinned vector typed into a real answer box under the vector's own item key and hash; blank vectors are refused).
  - turtle directives: `acceptance.spec.ts` "§3 turtle directives…" (closed, open path with and without `# turtle-check: open-path`, no pen-down move, 10,000 moves).
  - mounted asset files: `acceptance.spec.ts` "§3 mounted asset files…" (a real asset block runs and draws; a cell reads the mounted file).
  - cumulative lesson state: `acceptance.spec.ts` "§3 cumulative lesson state: … again after a forced worker restart".
- **Reference solvers:** `solvers.setup.ts` gets `tools/judge.py`'s verdict on every case (`e2e/helpers/solver_verdicts.py`, the judge's own walk and `_run_case`); `solvers.spec.ts` runs every `assets/{l,ex,q,p}N.py` of usaco-bronze and acsl in Pyodide through the runner (one fresh worker per case, the book's matching mode, the site's budget rule) in four parallel shards and requires the same verdict for every case. Solvers and fixtures are read from the repo, never shipped.
- **Isolation** (`isolation.spec.ts`): the runner iframe cannot read the site's IndexedDB or localStorage; the runner ignores a wrong-origin message and a valid-looking one from a popup on the site origin; the site drops a reply from a wrong origin, from a second runner-origin iframe, with an unknown id, and an invalid envelope; COEP and `crossOriginIsolated` in the site, runner page and worker: `runner.spec.ts` first test.
- **Sessions:** reset (`runner.spec.ts` "reset clears a lesson session"); the prelude replay after a forced restart (`acceptance.spec.ts`, above); two checks share nothing (`runner.spec.ts` "two checks share no process state…"); two fixture cases of one item share nothing (`acceptance.spec.ts` "§3 process state…").
- **Grading UI and gating:** `checks.spec.ts` (both matching modes with `outputs_match` parity, the skipped case, the sample-only reveal, `expected-output`, `predict`, `aliases`, `whitespace: exact`, `self-check`, `also_check` (skipped until plan 102 merges), the turtle rule, odd and even answers, the odd self-check attempt).
- **Navigation, CSP, network:** `isolation.spec.ts` "navigation…" (twice: with the site CSP, which blocks the navigation, and with the CSP bypassed, so the other page loads and still receives nothing); "zero CSP violations on the runner page…"; "no network…" (only the two local origins, files of `dist/` and `runner/dist/`, no code or answers in any request).
- **Workers and boot:** at most three workers (`runner.spec.ts`); cold and warm boot under Chromium CPU throttling ×4, with the unthrottled numbers beside them, are printed and attached as test annotations (`runner.spec.ts` "cold and warm Pyodide boot…").
