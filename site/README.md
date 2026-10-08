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
bash scripts/build-site.sh [--release <tag>]   # export every site book, then build site/dist/
pnpm -C site test                              # vitest
pnpm -C site dev                               # local preview of the exported bundles
```

- **Toolchain:** Node 24 LTS (`.nvmrc`; `nvm install`), pnpm at the version in `package.json` `packageManager` (`corepack enable`).
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
