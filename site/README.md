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
