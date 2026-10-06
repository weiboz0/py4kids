# Plan 101 — Site content export (design 012, part A)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `py4kids-tools --book <id> export` turns each `site: true` book into a versioned, schema-checked JSON bundle under `site/content/<book>/`.
The bundle holds lesson blocks, exercise, checkpoint and project items with check data, quiz cards and the glossary.
`site-check` proves the bundle's ids, answer model and coverage in CI.

**Architecture:** A new package `tools/export/` reads the notebooks through the publisher's existing helpers (`route_code`, `item_groups`, `statement_text`, `markdown_blocks`, `student_answer_sources`), so web and print agree.
Solution material is read in one module only (`tools/export/answers.py`), which emits hashes for every hidden item.
Lesson cells are probed in a temporary copy of the entry directory.
Nothing in the bundle is hand-edited; only the id ledger and the per-book `site.yaml` are committed.

**Tech Stack:** Python 3 (the repo's `uv` environment), nbformat, PyYAML, jsonschema 4.26 (already installed through nbformat), pytest.
No Node in this plan (part B adds it).

**Spec:** `docs/designs/012-learning-website.md` (D1, D3, D4, D5, D8, D11, §3 "Export", §4 row 1).
User decisions, 2026-10-04: pedagogical gating; tag + self-check fallback; reading view primary; class sync free.
User, 2026-10-05: "Go with autopilot".

## Global Constraints

- The notebooks stay the source of truth; the bundle is generated, never hand-edited (design 012 §1).
- Tools key on the `site` flag, never on book ids (D1). First release: python-projects, python-concepts, usaco-bronze, acsl; **recsys is not flagged**.
- Global key: `book/entry/notebook/cell_id`, plus `#n` for parts split out of one cell; the export fails on a missing or duplicate id (D3).
  Cards derived from a cell use the suffix `#predict`; concept cards are `book/back-matter/glossary/<concept-id>`. Keys are unique across blocks, items and cards together.
- `answer_visibility` is `after-attempt` only for odd unit exercises, using exactly the Student Book appendix text read through `student_answer_sources`; `none` for everything else (D3, D5).
- Hidden `answer`, `predict` and `expected-output` items ship only a salted hash of the normalised canonical text: trimmed, internal whitespace collapsed to one space per line, case as `answer_format` states (D5).
- Check-kind tags are heading-cell tags: `check-fixtures`, `check-answer`, `check-asserts`, `check-expected-output`, `check-predict`, `check-self` (D4).
- Turtle rule: at least one pen-down move; fewer than 10,000 moves; closed path unless `# turtle-check: open-path` (D4).
- Fixtures: every pair is under the measured budget (start: 130 KB); the export reports any over-budget pair; skips are never silent (D7).
- The progress event is `{schema, event_id, book, item_key, kind, result, detail, duration_ms, timestamp, content_hash}`, with `kind` in `lesson-run, slide, card, exercise, checkpoint, project, self-check`; `detail` holds results only (D11).
- The repo is public: no student data, keys or payment code (design 012 §1, AGENTS.md).
- ACSL `assets/verify` helpers and solution sources (`^(ex|q|p)\d+\.py$`) are never copied into a bundle, except odd unit answers through `student_answer_sources` (D7, design 010 D3).
- Docs use semantic line breaks.

## Survey (2026-10-05, branch at f92f51a = design 012 + main 9c313d4)

| book | unit exercises | challenges | checkpoint questions | project items | lesson code cells |
|---|---|---|---|---|---|
| python-projects | 180 | 16 (unnumbered) | 31 | milestones (`## Milestone N`, 2 projects) | 234 |
| python-concepts | 345 | 0 | 35 | 11 problems | 351 |
| usaco-bronze | 127 | 0 | 26 | 8 problems | 135 |
| acsl | 324 (287 `short-answer` heading tags) | 0 | 35 | 0 | 200 |

- All 4 books: 0 cells without an id, 0 duplicate ids within a notebook.
- Existing heading tags: `stretch`, `short-answer`, `no-exec`, `acsl-<division>`. No `check-*` tag exists yet.
- Contest fixtures live in `assets/<stem>/<n>.in|.out` (`tools/judge.py::_fixture_pairs`); 314 solvers have `1.in`.
- `tools/concept_scan.detect(tree, registered_concepts=, profile=)` works on any AST with a per-book `scanner_profile(concepts)`; only `_load_k2` is gated on `patterns`.
- `tools/publish.answer_key(..., edition='student')` builds the appendix from `student_answer_sources`; `challenge_answers` is Teacher's Edition only, so challenges are `none`.
- `glossary_entries(source)` reads `**Term** — …` + `<!-- concept: id -->`; every concept in `concepts.yaml` has a `category`.

## File structure

| path | responsibility |
|---|---|
| `books.yaml`, `tools/books.py` | the `site` flag; `site_config(root, book)` loads and validates `<book>/site.yaml` |
| `<book>/site.yaml` (4 books) | `classification: proposed` (content plans flip to `confirmed`), `fixture_budget_kb: 130` |
| `tools/export/__init__.py` | `SCHEMA_VERSION = "1.0.0"` |
| `tools/export/ids.py` | global keys, uniqueness, ledger continuity |
| `tools/export/normalise.py` | `normalise`, `answer_hash`; mirrored by `tools/export/hash_vectors.json` for part C's JS port |
| `tools/export/lesson.py` | lesson → blocks (prose, notice, code, code+output, try-it, error/hang demo, turtle figure, program, goals, recap) |
| `tools/export/probe.py` | the standalone-cell probe and asset detection, in a temp copy |
| `tools/export/concepts.py` | per-cell concept attribution through `concept_scan.detect` |
| `tools/export/items.py` | items for units, challenges, checkpoints, problems and milestones; statement, starter, division, stretch |
| `tools/export/classify.py` | check-kind proposals, tag reading, `--apply`, coverage report |
| `tools/export/answers.py` | the **only** solution reader: odd answers, canonical texts, asserts, fixtures, hashes |
| `tools/export/cards.py` | predict cards and concept cards; glossary |
| `tools/export/bundle.py` | assemble, write, content hash, PDF links, determinism |
| `tools/export/check.py` | `site_check_findings(root, book)`: schema, ids, continuity, answer model, coverage, budget |
| `tools/export/schema/bundle.schema.json`, `progress-event.schema.json` | JSON Schema 2020-12, `additionalProperties: false` throughout |
| `site/ids/<book>.json`, `site/ids/<book>-retired.yaml` | committed id ledger and retirements |
| `site/README.md` | bundle layout, the regenerate command, the ledger rule |
| `tools/publish.py` | refactor only: `student_answer_text(entry, number, lesson_heading)` shared by `answer_key` and the export |
| `tools/turtle_figure.py` | add `turtle_segments(source, stdin)` (the replay `figure_tikz` already does, returned as data) |
| `tools/cli.py`, `scripts/ci-local.sh` | `export`, `classify`, `site-check`; a ci step for `site` books |
| `tests/test_site_*.py`, `tests/site_consumer.py` | the tests below |
| `.gitignore` | `site/content/` |

## Review Focus

1. **A lesson cell that writes a file** (python-projects unit 09 writes `savegame.txt`): the probe runs in a temporary copy, so the repo tree is unchanged after export. Test in Phase C.
2. **A probed cell that hangs or calls `input()`**: each probe run has a timeout and stdin from `/dev/null`; the probe returns `timeout` / `error` and finishes (in `site-check` that status is a `FAIL:` naming the cell). Test in Phase C.
3. **Canonical answers with CRLF, tabs, NBSP, trailing blank lines or mixed case**: `normalise` treats every Unicode whitespace like a space, drops leading and trailing blank lines, and folds case only when `answer_format.case` is `insensitive`. `hash_vectors.json` pins each case for the JS port. Test in Phase B.
4. **Re-export under a different `PYTHONHASHSEED`, or after only `git checkout`, or with an untracked scratch file present** (file mtimes, glob order, set order, `savegame.txt`): byte-identical bundle and the same content hash. Tests in Phases C and E.
5. **A short hidden answer that also appears in the statement** (for example `5`): the answer-model test flags only hidden canonical text that appears in the bundle **and** in no student-visible source. A real leak (a hidden canonical copied into a field) still fails. Test in Phase F.

---

## Phases

Each phase ends green on `uv run pytest -q tests/test_site_*.py` and `uv run ruff check tools tests`, and with one commit.
Never `git stash` in the shared tree; parallel phases run in worktrees.

### Phase A — The `site` flag and per-book config

**Files:** `books.yaml`; `tools/books.py`; `<book>/site.yaml` ×4; `scripts/ci-local.sh` (flag list only); `tests/test_books.py`.

**Interfaces — produces:**
- `site_config(root: Path, book: str) -> SiteConfig`, a frozen dataclass with `classification: Literal["proposed", "confirmed"]` and `fixture_budget_kb: int`.
- `site_config_errors(root, book) -> list[str]`; `SiteConfigError(ValueError)`.
- `books_with_flag(root, "site")` already exists and is reused.

- [ ] **Step 1: failing tests** in `tests/test_books.py`:

```python
def test_site_flag_books(repo_root):
    assert books_with_flag(repo_root, "site") == ["python-projects", "python-concepts", "usaco-bronze", "acsl"]

def test_site_config_validation(tmp_path):
    root = make_registry(tmp_path, books=[{"id": "b", "site": True}])   # existing helper style in test_books.py
    (tmp_path / "b" / "site.yaml").write_text("classification: maybe\nfixture_budget_kb: 130\n")
    assert site_config_errors(root, "b") == ["FAIL: b/site.yaml: classification must be one of: proposed, confirmed"]
    (tmp_path / "b" / "site.yaml").write_text("classification: proposed\nfixture_budget_kb: 130\nextra: 1\n")
    assert site_config_errors(root, "b") == ["FAIL: b/site.yaml: unknown key: extra"]

def test_site_book_needs_site_yaml(tmp_path):
    root = make_registry(tmp_path, books=[{"id": "b", "site": True}])
    with pytest.raises(SiteConfigError, match="site: true but b/site.yaml is missing"):
        site_config(root, "b")
```

  If `test_books.py` has no `make_registry` helper, write one in the test file that writes `books.yaml` (`books_version: 2`) and the book folders.
- [ ] **Step 2:** run `uv run pytest -q tests/test_books.py`. Expected: the 3 new tests FAIL (import error).
- [ ] **Step 3: implement.**
  - Add `site: true` to the 4 books in `books.yaml`, plus a header comment line: `#   site:        the learning-website export (design 012): export, classify and site-check.`
  - Add `site_config` and its validation to `tools/books.py`, following `_parse_publication_config`'s error style.
  - Write each `<book>/site.yaml`: `classification: proposed` and `fixture_budget_kb: 130`, with a comment naming design 012 D4/D7.
  - Add `site` to the flag tuple in `ci-local.sh` step 1.
- [ ] **Step 4:** run `uv run pytest -q tests/test_books.py`; expected PASS.
- [ ] **Step 5:** commit `plan 101 A: site flag and per-book site.yaml (design 012 D1)`.

### Phase B — Ids, normalisation and hashing, schemas

**Files:** `tools/export/{__init__,ids,normalise}.py`; `tools/export/hash_vectors.json`; `tools/export/schema/{bundle,progress-event}.schema.json`; `tests/test_site_ids.py`, `tests/test_site_normalise.py`, `tests/test_site_schema.py`.

**Interfaces — produces:**
- `item_key(book: str, entry: str, notebook: str, cell_id: str, part: int | None = None) -> str`. The notebook is the file stem (`lesson`, `exercises`, `checkpoint`, `brief`). A non-None `part` appends `#<part>`, so `item_key("acsl","unit-12-graph-theory","lesson","a1b2",2) == "acsl/unit-12-graph-theory/lesson/a1b2#2"`.
- `duplicate_key_findings(keys: Iterable[str]) -> list[str]`: run over the union of block, item and card keys.
- `card_key(block_key: str) -> str` returns `block_key + "#predict"`; `concept_card_key(book, concept_id) -> str` returns `f"{book}/back-matter/glossary/{concept_id}"`.
- `missing_id_findings(nb_path: Path) -> list[str]`.
- `load_ledger(root, book) -> set[str]`; `write_ledger(root, book, keys)`.
- `continuity_findings(root, book, keys) -> list[str]`: every ledger key that is neither in `keys` nor listed in `site/ids/<book>-retired.yaml` gives `FAIL: <book>: id vanished since the ledger: <key> (map it in site/ids/<book>-retired.yaml as `<key>: <new key or "retired">`)`.
- `normalise(text: str, *, case: Literal["sensitive","insensitive"]) -> str`; `answer_hash(item_key: str, canonical: str, *, case) -> str`.

```python
# tools/export/normalise.py
import hashlib, re

_WS = re.compile(r"\s+")  # str regex: every Unicode whitespace, NBSP included

def normalise(text: str, *, case: str) -> str:
    lines = [_WS.sub(" ", line).strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    out = "\n".join(lines)
    return out.casefold() if case == "insensitive" else out

def answer_hash(item_key: str, canonical: str, *, case: str) -> str:
    # The salt is the item's global key: public, per item, so equal answers hash differently (D5).
    payload = f"py4kids-answer-v1\n{item_key}\n{normalise(canonical, case=case)}"
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()
```

- [ ] **Step 1: failing tests:**
  - `test_site_normalise.py`: one test per `hash_vectors.json` vector. The vectors cover CRLF, tabs, NBSP (`" "`), leading and trailing blank lines, an internal blank line kept, `casefold` (`"Straße"` → `"strasse"`), and case sensitive vs insensitive. Plus `answer_hash("a/b/c/d", "5", case="sensitive") != answer_hash("a/b/c/e", "5", case="sensitive")`.
  - `test_site_ids.py`: `item_key` format; duplicates are reported once each; a notebook cell without `id` gives `FAIL: <path>: cell <index> has no id`; continuity with a vanished key (FAIL), a retired key (pass) and a new key (pass).
  - `test_site_schema.py`: a sample entry with `intro`, `outro` and an item `before` validates; both schemas validate under `jsonschema.Draft202012Validator.check_schema`. A sample progress event per `kind` validates. An event with a `code` field, or with `detail: {"text": "…"}`, fails (`detail` allows only `cases: [{"n": int, "pass": bool}]`, `self_grade: "got-it"|"not-yet"`, `box: int`, `checklist: [bool]`).
- [ ] **Step 2:** run them; expected FAIL.
- [ ] **Step 3: implement.**
  - `ids.py` and `normalise.py` as above.
  - `hash_vectors.json`: a list of `{input, case, normalised, item_key, hash}` objects, generated once by the tests' helper and committed; the test also asserts the file matches the code.
  - **The bundle schema** (`$id: py4kids/bundle/1.0.0`). Top-level `book.json`:
    - `schema_version`, `book{id,title,subtitle,flags{acsl,judge}}`, `release{tag,content_hash}`
    - `entries[{id,kind,title,number,file}]` in syllabus order
    - `concepts[{id,name,category}]`, `glossary[{term,definition_md,concept,units}]`, `reference_md` (the book's `back-matter/quick-reference.md`, for part B's reference page)
    - `settings{lesson_heading,acsl_divisions?}`, `pdfs{edition: url}|null`
  - `entries/<entry-id>.json`: `{schema_version, entry{id,kind,title}, lesson{blocks[]}|null, intro[], items[], outro[], cards[], files[]}`. `intro[]` and `outro[]` (and each item's `before[]`) are `block` arrays of type `prose`, `notice`, `goals`, `recap` or `starter`.
    - A `block` (types: `prose`, `opener`, `notice`, `goals`, `recap`, `code`, `tryit`, `error-demo`, `hang-demo`, `turtle-figure`, `program`, `starter`): `{key, type, md?, code?, output?, route?, stdin?, sample_input?, figure?, needs_prelude, prelude[], files[], concepts[], probe, tags[]}`; `tags` carries the cell's tags (part B's `slide-break` / `slide-skip`).
    - An `item`: `{key, kind, number|null, label, title, division[], stretch, concepts[], statement_md, starter, files[], check{…}, answer_visibility, answer_md?, before[]}`. The schema enforces, with `if`/`then`, that `answer_md` is present exactly when `answer_visibility` is `after-attempt`.
    - `check` is a `oneOf` keyed on `kind`:
      - `fixtures{cases[{n,in_file,out_file,sample}], match:"line"|"token", over_budget[]}`. Fixture text is **not** inlined: `in_file`/`out_file` are bundle paths under `files/`, so each fixture text ships exactly once
      - `answer{hash, answer_format{case,hint}}`
      - `asserts{source, functions[]}`
      - `expected-output{hash, answer_format}`
      - `predict{hash, answer_format, program}`
      - `self-check{requirements[]}`
      - plus `turtle: bool`, and `confirmed: bool` (true when a `check-*` tag is present).
  - The progress-event schema exactly per D11.
- [ ] **Step 4:** run; PASS. **Step 5:** commit `plan 101 B: ids, ledger, normalise/hash, bundle and progress-event schemas`.

### Phase C — Lessons: blocks, probe, concepts, cards

Runs in a worktree, in parallel with Phase D (no shared files except the read-only use of `tools/publish.py`).

**Files:** `tools/export/{lesson,probe,concepts,cards}.py`; `tools/turtle_figure.py` (`turtle_segments`); `tests/test_site_lesson.py`, `tests/test_site_probe.py`, `tests/test_site_cards.py`; fixture notebooks under `tests/fixtures/site/`.

**Interfaces:**
- **Consumes** `item_key`, `route_code(cell, stdin_note=False)`, `NOTICE`, `markdown_blocks`, `strip_turtle_directives`, `scanner_profile`, `detect`.
- **Produces also** `glossary_records(source: str) -> list[dict]`, each `{term, concept, definition_md, units: list[int]}`. The real `glossary_entries` returns only `(term, concept, aliases)` and `glossary_units` only the first unit, so this parser reads the whole `**Term** — definition *(Unit N)*` / `*(Units N–M)*` / `*(Units N, M)*` line plus its `<!-- concept: … -->` comment: `definition_md` is the text between ` — ` and the unit tag, kept as Markdown verbatim (inline code, italics). `units` expands ranges and comma lists (`*(Units 4, 7)*` → `[4, 7]`, `*(Units 4–6)*` → `[4, 5, 6]`). The concept comment sits on the **next** line, as `glossary_entries`' regex expects, so the parser reads the pair. `test_glossary_records_real_books`: every entry of the 4 real glossaries parses, with a non-empty definition and at least one unit; the count equals `len(glossary_entries(source))`.
- **Produces:**
  - `lesson_blocks(root, book, entry_dir) -> list[dict]`: the block dicts per the schema, in cell order.
  - `probe_cells(entry_dir, cells, timeout_s=20) -> dict[cell_id, ProbeResult]`. `ProbeResult` is a dataclass with `status: "standalone"|"prelude"|"mismatch"|"error"|"timeout"`, `prelude: list[str]` (cell ids) and `files: list[str]`.
  - `cell_concepts(profile, registered, source) -> list[str]`, sorted.
  - `predict_cards(blocks) -> list[dict]`; `concept_cards(concepts, glossary) -> list[dict]`.
  - `turtle_segments(source, stdin=None) -> list[dict]`, each `{x1,y1,x2,y2,color,width}`.

Rules:
- **Route to block type:**
  - `code+output` → `code` with `output` (stream text only)
  - `code` → `code`
  - `tryit` / `tryit-stdin` / `tryit+figure` → `tryit` (with `stdin: true` for `tryit-stdin`, and `sample_input` from metadata)
  - `errordemo` → `error-demo`; `hangdemo` → `hang-demo`
  - `figure` → `turtle-figure` with `figure` = `turtle_segments`
  - `program` → `program`

  A route value the map does not know fails the export, naming the route.
- **Markdown cells:**
  - the first cell's `# ` H1 line becomes the entry title (not a block); the whole rest of cell 0 (the hook, headings included) becomes one `opener` block, exactly as `render_chapter` builds its opener panel (`re.sub(r'^# [^\n]*\n*', '', cell0).strip()`, `tools/publish.py:1238-1241`; it is exported, so it is in the leak baseline)
  - a cell starting `### You will learn` → `goals`; `### Recap` → `recap`
  - a Notice paragraph plus its continuations (as `markdown_blocks` groups them) → `notice`
  - other prose splits at every `##`/`###` heading into `prose` blocks
  - block `n` of a cell gets key `…/<cell_id>#n` for n ≥ 2; the first part keeps the bare key
  - Lesson asset listings (`asset_blocks`' names) → `program` blocks keyed `…/<cell_id>#asset:<name>`, with the file copied into `files/`.
- **Probe:** runs on **every executed lesson cell** (every code cell without `no-exec`), including output-free setup cells such as `import random` / `random.seed(1)`. An output-free cell passes when it runs without error and prints nothing.
  - Copy **only the `git ls-files`-tracked paths** under `entry_dir` to a temp dir (never the working tree's untracked scratch such as python-concepts unit 12's `lesson_l1_one.txt` or `savegame.txt`), then run each cell alone under `sys.executable` with cwd at the copy, stdin `/dev/null`, `PYTHONHASHSEED=0` and the timeout.
  - Compare stdout with the stored output, with trailing whitespace stripped per line and trailing blank lines ignored.
  - On a miss, the prelude is the transitive closure of earlier executed cells that bind a name the cell loads (`ast`: Assign/AugAssign/AnnAssign targets, def, class, import, for-target, with-as), **plus** earlier cells that call a method on, or assign an attribute or item of, a name in that closure (so `random.seed(1)` follows `import random`; `items.append(…)` follows `items = []`), **plus** earlier executed cells that contain the same file-naming string constant (a writer before its reader: python-concepts unit 12 cell 4 writes `lesson_l1_one.txt`, cell 7 reads it). Run prelude + cell in one process, with a sentinel line printed before the cell; compare only the output after the sentinel.
  - If that still misses, use all earlier executed cells. If it still misses → `mismatch`.
  - `files`: string constants in the cell (and its prelude) that name a **git-tracked** file (`git ls-files`) in the entry dir or `assets/`, so a scratch file left by a notebook run (`savegame.txt`) never changes the bundle. Solution sources and `assets/verify/**` are excluded.
  - A real-lesson `timeout` or `error` is a `FAIL:` in `site-check`, never bundle data (lesson cells already execute in CI), so the content hash cannot flip with machine load. `mismatch` (for example `random` without `seed`) is bundle data: the block is not card-eligible, and it is reported as `WARN:`.
- **Concepts:** `detect` on the cell's AST with the book's profile, intersected with `registered`. A heading or code cell's `metadata.concepts` list overrides the scan; every id in it must be in the book's registered concept set (D11), or `site-check` gives `FAIL: <key>: unregistered concept <id>`. An empty result goes into the report as `unattributed`.
- **Predict cards:**
  - Eligible blocks are `code` blocks with `output` and probe status `standalone` or `prelude`.
  - `mode: "typed"` when the normalised output is one line; otherwise `"flip"`.
  - `{key: card_key(block key), kind: "predict", block, mode, prelude}`. Lesson outputs are already visible on the page, so no hash is needed.
- **Concept cards:**
  - One per glossary entry: `{key: concept_card_key(book, concept), kind: "concept", concept, term, definition_md, mode, distractors[0..3]}`.
  - Distractors are other glossary terms whose concept shares the `category`, sorted by term, taking the first 3 after the entry's own term (deterministic).
  - Distractors are **always category-local** (D8). With 1–2 peers, the card is multiple choice with that many distractors (`mode: "choice"`); with none, it is a term → definition flip card (`mode: "flip"`, `distractors: []`). The report lists both cases.

- [ ] **Step 1: failing tests** using a fixture lesson notebook `tests/fixtures/site/unit-01-demo/lesson.ipynb` (ids set). Its cells are:
  - c1: `x = 3`, output none
  - c2: `print(x * 2)`, output `6`
  - c3: `print('hi')`, output `hi`
  - c4: writes `open('scratch.txt','w').write('a')`, output none
  - c5: `while True: pass`, executed, stored output `x` (the hang)
  - c6: `name = input()`, stored output `x`
  - c7: a `no-exec`+`error-demo` cell
  - c8: a `no-exec` turtle square
  - m1: a markdown cell with `### You will learn` and bullets
  - m2: a markdown cell with two `###` headings
  - m3: a Notice paragraph

  Tests:
  - `test_probe_standalone_and_prelude`: c3 is `standalone`; c2 is `prelude` with `["c1"]`.
  - `test_probe_tree_unchanged`: no `scratch.txt` in the fixture dir after the probe (Review Focus 1).
  - `test_probe_setup_cells`: an output-free `import random` cell and an output-free `random.seed(1)` cell are probed (`standalone`), and a later `print(random.randint(1, 6))` cell gets both as its prelude.
  - `test_probe_file_written_by_earlier_cell`: cell A writes `x.txt` (no output), cell B reads and prints it → B is `prelude` `["A"]`, also when a stale untracked `x.txt` sits in the source dir. A cell that writes and then reads `x.txt` itself is `standalone` with an empty prelude (the common real pattern: python-concepts unit 12).
  - `test_files_tracked_only`: an untracked `scratch.txt` named by a cell is not in `files` (the fixture lives in a `git init` tmp repo).
  - `test_probe_hang_and_input`: c5 `timeout` and c6 `error` within `2 * timeout_s` (timeout 2 s in the test) (Review Focus 2).
  - `test_blocks_types_and_keys`: m2 gives two prose blocks, `…/m2` and `…/m2#2`; c7 is `error-demo`; c8 is `turtle-figure` with 4 segments; m1 is `goals`; m3 is `notice`.
  - `test_lesson_opener_real`: on python-concepts `unit-01-output-and-variables` and acsl `unit-12-graph-theory`, the entry title equals the lesson's H1 text (as `render_chapter` derives it, `tools/publish.py:1219`), no block contains that H1 line, the hook paragraphs form exactly one `opener` block keyed by cell 0, and its text equals `render_chapter`'s hook (`re.sub(r'^# [^\n]*\n*', '', cell0).strip()`, `tools/publish.py:1238-1241`). That covers acsl unit 12, whose hook opens with a `###` heading, so `markdown_blocks(first=True)` emits no opener panel there. On python-concepts unit 01, a heading-free hook, the text also equals `markdown_blocks(cell0, first=True)`'s opener panel body, as a secondary check.
  - `test_unknown_route_fails`: monkeypatch `route_code` to return `('weird', '')` → `ValueError` naming `weird`.
  - `test_predict_cards`: c3 typed; a two-line output gives flip; c5 is not a card.
  - `test_concept_cards_deterministic`: a 4-entry fixture glossary gives the same distractors on two runs, all from the same category; a category with 1 peer gives a 2-option `choice` card and a singleton category a `flip` card, deterministically.
  - `test_concept_cards_real_books`: on the 4 real books, every distractor's concept has the card's concept's `category`.
  - `test_keys_unique_across_kinds`: a predict card's key differs from its block's key, and the union of block, item and card keys has no duplicate.
  - `test_concept_override_unregistered_fails`: `metadata.concepts: [not-a-concept]` on a lesson cell and on an item heading cell each give a `FAIL:` line.
  - `test_cell_concepts`: `for i in range(3): print(i)` with python-projects' profile includes `for-range` and `print`, or whatever ids python-projects' `concepts.yaml` uses for those features (read the registry in the test, not hard-coded guesses).
- [ ] **Step 2:** run; FAIL. **Step 3:** implement. **Step 4:** run; PASS.
- [ ] **Step 5:** a smoke run over every real lesson: `uv run python -c "…lesson_blocks for all entries of the 4 books…"` prints, per book, the block counts by type and the probe counts by status. Record them for the post-execution report; design 012 expects about 61 of 718 executed cells to need a prelude.
- [ ] **Step 6:** commit `plan 101 C: lesson blocks, standalone-cell probe, concept attribution, cards`.

### Phase D — Items, classification and the answer model

Runs in a worktree, in parallel with Phase C.

**Files:** `tools/export/{items,classify,answers}.py`; `tools/publish.py` (refactor: `student_answer_text`); `tests/test_site_items.py`, `tests/test_site_classify.py`, `tests/test_site_answers.py`; fixtures under `tests/fixtures/site/`.

**Interfaces:**
- **Consumes:**
  - `item_groups`, `unit_challenges`, `group_title`, `title_heading`, `statement_text`, `markdown_blocks`, `item_divisions`, `asset_blocks`, `project_sections`, `ITEM`
  - `student_answer_sources`, `is_solution_source`
  - `judge._fixture_pairs`, `judge.outputs_match`, `judge.ANSWER_LINE`
  - `fake_turtle.imports_turtle`; `normalise`/`answer_hash`; `item_key`; `site_config`
- **Produces:**
  - `entry_content(root, book, entry_dir, kind) -> EntryContent`, a dataclass `(intro: list[dict], items: list[Item], outro: list[dict])`; `entry_items(...)` returns `entry_content(...).items`. `Item` is a dataclass with `key, kind ("unit"|"challenge"|"checkpoint"|"project"), number, label, title, division, stretch, concepts, statement_md, starter, files, heading_cell, before, solution_group`; `before` holds the item's interlude blocks (a challenge section's `unit_challenges` lead-in cells attach to the **first** challenge's `before`); `solution_group` is the matching solution group, used only inside `answers.py`.
  - `KINDS = ("fixtures","answer","asserts","expected-output","predict","self-check")`; `TAG = {k: f"check-{'self' if k == 'self-check' else k}" for k in KINDS}`.
  - `confirmed_kind(item) -> str | None` (from the heading-cell tag); `tag_findings(item) -> list[str]`, which reports more than one `check-*` tag, a `check-*` tag on a non-heading cell, or an unknown `check-*` tag.
  - `propose_kind(root, book, item) -> tuple[str, str]`, returning (kind, reason).
  - `apply_proposals(root, book, entry=None) -> list[str]`, which writes the proposed tag to heading cells without one (nbformat round-trip; ids and outputs preserved) and returns the changed keys.
  - `check_data(root, book, item, kind) -> dict` (the schema's `check`); `answer_fields(root, book, item) -> dict` (`answer_visibility`, plus `answer_md` for odd unit exercises).
  - `student_answer_text(entry: Path, number: int, lesson_heading: str | None) -> str` in `tools/publish.py`.

Rules:
- **Items:**
  - Unit: `## Exercise N` groups, plus unnumbered challenges (kind `challenge`, label `Challenge N`).
  - Checkpoint: `## Question N`.
  - Project: `Problem N` groups when present, else `## Milestone N` sections (`project_sections`).
    A milestone whose solution has no matching numbered section (`project-01-arcade-night`'s solutions use `Lucky Guess`, `Quick Quiz`, …) gets `solution_group = None` → `self-check`, no FAIL, listed in the report.
  - **Project partition (export-owned, not `item_groups`).** `item_groups(…, 'Problem')` folds every later cell into the current problem, so the export partitions a brief itself. **In Problem mode** (the brief has `Problem N` headings; in Milestone mode the `## Milestone N` cells are the items), a markdown cell whose first line is a `## ` heading (`## Milestone N…`, `## Make it yours`, `## Requirements…`) ends the current problem. If another item follows, the cell goes to that item's `before[]`; otherwise to `outro[]`. Solutions still map by `item_groups` on `solutions.ipynb`.
    `test_project_partition_real`: python-concepts `project-01-algorithm-challenge` has `p01b002` in Problem 1's `before`, `p01b007` in Problem 3's `before`, and `p01b028`, `p01b029` in `outro`; usaco-bronze `project-03-mock-contest` has `27a38ec3` in Problem 1's `before` and `219d2b81`, `ff8f4935` in `outro`; no problem's `statement_md` contains "Make it yours".
  - **Non-item content is kept, never dropped.** The entry JSON carries `intro[]` (preface cells, notebook H1 removed), each item `before[]` (interlude cells such as a `## Challenge` note), and `outro[]` (cells after the last item that belong to none; for units, a challenge section's lead-in cells from `unit_challenges` (`tools/publish.py:913-920`) go in the first challenge's `before[]`, not `intro[]`; e.g. a brief's "Make it yours" and "Requirements checklist"). These are prose and starter blocks with keys, exactly as the publisher renders them (`render_items`, `tools/publish.py:860-871`).
    `test_every_statement_cell_exported`: every cell of every statement notebook (`exercises`, `checkpoint`, `brief`) in the 4 real books lands in exactly one of `intro`, an item, a `before`, or `outro`.
  - The heading cell's id is the key; a challenge split out of a note cell gets `#2`.
  - `statement_md` is `statement_text` + `markdown_blocks` per markdown cell, as `_item_body` does with `edition='student'`, minus the starter panels; `PLACEHOLDER` paragraphs are dropped.
  - `starter` is the item's code cells (non-`verify`) joined with a blank line.
  - `stretch` from the tag; `division` from `item_divisions`.
  - `concepts`:
    - from the heading cell's `metadata.concepts`, if present (ids validated against the registry as in Phase C)
    - otherwise `cell_concepts` (Phase C) over the starter and the solution code, intersected with the entry manifest's `introduces ∪ requires ∪ practices`. Only ids leave `answers.py`, never code.
    - an empty result is listed as `unattributed` in the report
    - Phase D stubs `cell_concepts` behind its Phase C signature until the merge.
- **Proposal order (first match wins):**
  1. `fixtures`: a judge book with solver `assets/<prefix>N.py` and fixture pairs.
  2. `answer`: a `short-answer` heading tag.
  3. `predict`: the statement asks what code prints (`(?i)(what (does|will) .* print|predict( the)? output|code to trace|trace (this|the) code)`), has a code cell, **and** that cell's run (as in step 5) gives non-empty stdout. Otherwise fall through.
  4. `asserts`: the solution has **at least one** top-level assert, and every free `Name` the asserts load other than Python builtins (functions **and** variables) is bound in the starter (`def`, `class` or assignment) or named in the statement in backticks. Otherwise fall through with reason `asserts test the solution's own choices` (the common `assert total == 15` with `total` the student's own variable is not portable unless the statement names `total`).
  5. `expected-output` (amended by content review 1): every non-empty normalised output line occurs, as a whole token sequence, in the statement, the starter or a `.py` file the item ships (`output_fixed_by_statement`; otherwise `self-check`, reason `output not fixed by the statement`); and the solution runs twice (temp copy, stdin `/dev/null`, `PYTHONHASHSEED=0`, timeout 20 s) with identical non-empty stdout, and neither the solution nor the starter calls `input(` or imports `random` without `seed(`.
  6. Else `self-check`.

  `turtle: true` when the starter or solution imports turtle (the three-part rule is applied in part C).
- **Canonical texts (answers.py only):**
  - `answer` → the `**Answer:**` line (`ANSWER_LINE`) in the solution group. Exactly one is required; otherwise FAIL naming the item.
  - `predict` → the stdout of the statement's code cell, run as in proposal step 5.
  - `expected-output` → the solution's stdout, run the same way.
  - `asserts` ships `source` = only the top-level `assert` statements (`ast.unparse`), and `functions` = the names they call. No function body ever ships.
  - `fixtures` ships every pair once, as files under `files/<entry>/fixtures/<stem>/`, referenced by `{n, in_file, out_file, sample}`. `sample` is true for the pair whose input equals the statement's first `Sample Input` code block (whitespace-normalised); the Sample Input block is the first code fence anywhere in the `Sample Input` section, even after prose (as in ACSL unit 15 Exercise 17). If none matches, **no pair is a sample** (nothing is revealed), and `site-check` prints `WARN:` naming the item. Pairs over `fixture_budget_kb` go to `over_budget` and the report. `match` is `"line"` when the book has the `acsl` flag, else `"token"`.
  - `self-check` → `requirements` from the heading cell's `metadata.requirements` if present; else the statement's bullet and numbered list items (Markdown stripped to text); else (amended by content review 1) the `**Specification:**` paragraph's sentences, or the statement's prose sentences without notes, at most 6; the label only as a last resort. The report lists `self-check` items with no list.
- **`answer_format`:** the heading cell's `metadata.answer_format` (`{case, hint}`) if present; else derived:
  - `case: "sensitive"`
  - `hint`: `"a number"` when the canonical text is numeric, `"one line"` when it is a single line, `"several lines"` otherwise
  - A derived format on a canonical text containing letters is listed in the report as `answer_format: derived (letters)`: content work.
- **Visibility:**
  - `answer_visibility: "after-attempt"` and `answer_md = student_answer_text(...)` for odd unit `Exercise` items only.
  - Every other item is `"none"`, with no `answer_md`; `answer`, `predict` and `expected-output` ship only `hash` (+ `answer_format`).
- **The `student_answer_text` refactor:** move the per-item body of `answer_key`'s student branch (the `_answer_blocks(...)` call with `student=True`) into `student_answer_text`, and have `answer_key` call it. The publication regression tests (`tests/test_publication_regression.py` and the per-book baselines) must stay byte-identical.

- [ ] **Step 1: failing tests** with a fixture unit: exercises 1–6 plus one challenge, solutions, `assets/ex1.py` with `assets/ex1/{1,2}.in|.out` in a fixture judge book, and a fixture checkpoint and project.
  - `test_items_keys_and_kinds`: keys, labels, the challenge key, the milestone fallback for a project without `Problem` headings.
  - `test_statement_has_no_placeholder_or_starter_panel`.
  - `test_propose_each_kind`: one fixture item per kind gives that kind, with its reason. Includes a non-portable assert example (`assert my_list == [3, 1, 2]`, `my_list` the student's own choice → not `asserts`), a function-portable one (`assert double(3) == 6`, `double` in the starter) a variable-portable one (`assert total == 15`, the statement says "store it in `total`"), and a builtin case (`assert len(names) == 3` with `names` named in the statement is portable; `len` needs no binding).
  - `test_predict_not_trace_by_hand`: "trace their counter values by hand" with a turtle code cell is not `predict`.
  - `test_apply_proposals_roundtrip`: the tags are written; a second apply changes nothing; cell ids and outputs are unchanged.
  - `test_tag_findings`: two `check-*` tags; a `check-*` tag on a body cell; `check-bogus`.
  - `test_odd_answer_equals_appendix`: for every odd unit exercise in **all 4 real books**, `student_answer_text` equals the matching slice of `answer_key(entry, 'unit', items, 'student', lesson_heading)` (the appendix text).
  - `test_hidden_items_ship_hash_only`: an even `answer` item's dict has `check.hash` and no canonical text anywhere in `json.dumps(item)`.
  - `test_asserts_ship_no_function_body`.
  - `test_fixture_sample_and_budget`: the sample matches the statement (also with prose before the fence); an unmatched sample gives no `sample: true` pair; a 200 KB fixture pair is `over_budget` with `fixture_budget_kb: 130`.
  - `test_answer_format_override_and_derivation`.
  - Run `uv run pytest -q tests/test_publication_regression.py` before and after the refactor.
- [ ] **Step 2:** run; FAIL. **Step 3:** implement. **Step 4:** run; PASS, with the regression tests unchanged.
- [ ] **Step 5:** smoke-run proposals over all 4 real books; print a per-book table of `kind × count` and `self-check` reasons for the post-execution report. Do **not** run `--apply` on real books (that is content-plan work).
- [ ] **Step 6:** commit `plan 101 D: items, check-kind classification, answer model (odd answers via student_answer_sources)`.

### Phase E — Bundle, CLI and CI

After C and D are merged into the plan branch.

**Files:** `tools/export/{bundle,check}.py`; `tools/cli.py`; `scripts/ci-local.sh`; `site/README.md`; `site/ids/<book>.json` ×4 (generated by `--update-ledger`); `.gitignore`; `tests/test_site_bundle.py`, `tests/test_site_cli.py`.

**Interfaces:**
- **Consumes** everything above.
- **Produces:**
  - `export_book(root, book, out_dir: Path, release: str = "unreleased") -> ExportResult`. `ExportResult` is a dataclass with `out_dir, content_hash, keys: list[str], report: dict`. `report` is written to `build/site-report/<book>.json`, never into the bundle.
  - `site_check_findings(root, book) -> list[str]`. It exports to `build/site-check/<book>/`, then returns, in this order:
    - schema errors
    - missing and duplicate ids
    - continuity findings
    - `tag_findings`
    - the answer-model findings (Phase F)
    - **classification coverage**: when `site.yaml` has `classification: confirmed`, every item without a `check-*` tag → FAIL; when `proposed`, a single `INFO:` line with the confirmed/total counts
    - `FAIL:` per real-lesson probe `error` or `timeout`, naming the cell key
    - over-budget fixtures (`WARN:`)
    - `WARN:` per probe `mismatch`

    Only `FAIL:` lines fail.
- **CLI:**
  - `py4kids-tools export --book B [--out DIR] [--release TAG] [--update-ledger]` (default out `site/content/B`); argparse also accepts `--book B export`, and `test_site_cli.py` tests both orders
  - `py4kids-tools --book B classify [--apply] [--unit ID]` (prints `key<TAB>proposed<TAB>confirmed<TAB>reason`)
  - `py4kids-tools --book B site-check`
  - All three refuse a book without the `site` flag: exit 2, `usage: <book> is not a site book (books.yaml site: true)`.

Rules:
- **Layout:** `book.json`, `entries/<entry-id>.json`, `files/<entry-id>/<relative path>` (lesson assets, data files, fixtures as `files/<entry>/fixtures/<stem>/<n>.in|out`).
  - Only files `allowed_source(path, 'student')` admits, plus fixtures, are copied.
  - A solution source or `assets/verify/**` is never copied, and the test asserts it.
- **Determinism:**
  - JSON is written with `sort_keys=True, ensure_ascii=False, indent=1` and a trailing newline.
  - Lists are kept in document order; sets are sorted before writing.
  - No timestamps or absolute paths are written.
- **`content_hash`:** sha256 over the sorted `(relative path, bytes)` of every bundle file except `book.json`'s `release` object.
- **`pdfs`:** `null` when `release == "unreleased"`. Otherwise `{edition: f"https://github.com/weiboz0/py4kids/releases/download/{release}/{output_pdf_name(book, edition)}"}` for the 4 editions.
- **The ledger:** `--update-ledger` writes `site/ids/<book>.json` (the sorted key list). This plan generates the first ledger for each book and commits it. The ledger is updated at each public release (the part D plan adds that step to `output/README.md`'s release procedure).
- **ci-local:** step 4 gains, for each book with the `site` flag, `book_run "$book" site-check`. The step prints the `INFO:`/`WARN:` lines and fails on `FAIL:`.

- [ ] **Step 1: failing tests:**
  - `test_export_layout_fixture_book`
  - `test_export_deterministic_across_hashseed`: run the export in two subprocesses with `PYTHONHASHSEED=1` and `2`; the trees are byte-identical (Review Focus 4)
  - `test_no_solution_source_copied`
  - `test_pdf_links`
  - `test_cli_refuses_non_site_book`: `recsys`
  - `test_classification_confirmed_requires_tags`
  - `test_site_check_probe_error_fails`: a fixture site book whose lesson has a cell raising `ZeroDivisionError` gives a `FAIL:` line naming that cell through `site_check_findings`
  - `test_site_check_real_books`: `site_check_findings` for each of the 4 books has no `FAIL:` line (marked `slow`). To avoid running the probe twice per CI run, `site_check_findings` writes its findings to `build/site-check/<book>/findings.json` keyed by the git tree hashes of `<book>/`, `tools/`, `books.yaml` and `site/ids/<book>*`; the cache is used only when `git status --porcelain` shows those paths clean and the key matches, otherwise it recomputes. The test reuses a fresh one. The measured `site-check` time per book goes in the post-execution report.
- [ ] **Step 2:** run; FAIL. **Step 3:** implement. **Step 4:** run; PASS.
- [ ] **Step 5:** `uv run py4kids-tools --book <b> export --update-ledger` for the 4 books. Check `git status`: only `site/ids/*.json` are new tracked files, and `site/content/` is ignored.
- [ ] **Step 6:** commit `plan 101 E: bundle writer, export/classify/site-check CLI, ci-local site step, first id ledgers`.

### Phase F — Verification (named verification phase)

**Files:** `tools/export/check.py` (answer-model findings); `tests/site_consumer.py`; `tests/test_site_consumer.py`, `tests/test_site_answer_model.py`.

- **The answer-model test (D5).** `answer_model_findings(root, book, bundle_dir) -> list[str]`:
  1. **Leak, code:** the hidden corpus is **every code cell of every `solutions.ipynb`** in the book plus every hidden solution asset (`solution_assets(entry, n)` for every even exercise and `challenge_solution_assets(entry, n)` for every challenge, as the publish audit does at `tools/publish_audit.py:380`), every `is_solution_source` file and `assets/verify/**` file, independent of item mapping, minus the odd unit answers that `student_answer_sources` releases. **Only the exact assert statements emitted as some item's `asserts.source`** (compared by `ast.unparse`) are removed from the hidden cells first, because they ship as check data by design. Every other hidden assert stays in the corpus, including an even `answer` item's verify cell such as `assert str(2 * 64 + 3 * 8 + 7) == "159"`. Separately, every `asserts.source` must parse to top-level `ast.Assert` statements only, or `FAIL: <key>: asserts.source holds non-assert code`. Each remaining cell is tokenised, and the publish audit's `solution_leak(block, sources)` (`tools/publish_audit.py:321`) runs against **every string value in every bundle JSON** (code fences inside Markdown are extracted and checked too) **and every copied file's text** under `files/`. A hit → `FAIL: <book>: <key>: solution code leaked into <bundle path>`.
  2. **Leak, text:** every hidden canonical text, **of any length** (`5E`, `159`), matched as a whole token sequence (word boundaries, so `5` never matches inside `15`) and only in content fields (`md`, `code`, `output`, `statement_md`, `starter`, `answer_md`, intro/before/outro blocks, copied files), never in keys, labels or titles, is **counted**: its occurrences across all bundle strings and copied files must not exceed its occurrences across the **source text of exactly the material the export maps into the bundle**: the statement notebooks' and lessons' cells and stored outputs that it exports, the glossary and the quick reference (both exported, as `glossary` and `reference_md`), **and every file the export copies**: tracked student assets admitted by `allowed_source(…, 'student')` and the fixture pairs, which ship by design (D5), **and the odd unit answers** rendered by `student_answer_text`. ACSL answers such as `01011` recur in other items' `.out` files, and an even answer can equal an odd one (`1110`: `acsl/units/unit-03-wdtpd-branching` and `unit-08-boolean-algebra`). No source the export does not ship counts toward the allowance; a test asserts that every baseline source path is one the bundle maps. Regressions: on the real acsl bundle, injecting `A + ~B` (hidden even answer of `unit-08-boolean-algebra` Exercise 6; it also occurs once in the exported quick reference) into a statement field fails; a hidden canonical that also occurs in a shipped fixture `.out` passes; one that equals an odd item's released answer passes. A value that already appears in sources (`1024`, `True`) passes as long as the export adds no occurrence; an injected copy raises the count and fails (Review Focus 5).
  3. **Odd answers:** every `after-attempt` item's `answer_md` equals `student_answer_text`, and the set of `after-attempt` keys equals the odd unit exercises exactly.
  4. **Hashes:** every `answer`, `predict` and `expected-output` item's `check.hash` equals `answer_hash(key, canonical, case=answer_format.case)`.
  5. **Visibility:** no `none` item has `answer_md` (also enforced by the schema).
  6. **Leak, prose:** the hidden prose corpus is every Markdown paragraph (`fenced_paragraphs`) of every `solutions.ipynb` in the book whose normalised length is ≥ 40 characters, **or that contains its item's canonical text** (an answer-bearing line such as `So the answer is 5E.` in `acsl/units/unit-01-computer-number-systems` Exercise 4, whatever its length), minus the paragraphs of the odd answers `student_answer_text` releases, and minus paragraphs that also occur verbatim in a student-visible source (solutions often restate the statement). Each is counted like check 2: its occurrences across all bundle strings and copied files must not exceed its occurrences in the student-visible baseline. This covers worked explanations such as `python-projects/projects/project-01-arcade-night/solutions.ipynb`'s.
  - Regressions: `So the answer is 5E.` (an even ACSL exercise) injected into a bundle string fails; the bare canonical `5E` injected into a content field fails; an even short-answer verify cell (`assert str(2 * 64 + 3 * 8 + 7) == "159"`) injected into a starter fails, while an `asserts` item's own shipped asserts pass.
  - Regressions: a distinctive explanation paragraph from an even exercise's, a checkpoint's and a project's solution, injected into a bundle JSON string, fails; the same paragraph injected into a copied file fails; an odd exercise's released explanation passes. An even exercise's `solutions_exN.py` body injected into a bundle JSON string fails, and the same injected into a copied file fails; a challenge's `solutions_challengeN*.py` body likewise fails. A fixture's text appears once in the bundle (as its file) and passes; an extra injected copy of it in a JSON string fails the count. An `asserts` item whose solution cell holds only asserts passes; a fixture whose `asserts.source` contains `def helper(): …` fails; a hidden function body copied into a starter fails.
- **The consumer test.** `tests/site_consumer.py` is ≈150 lines of plain Python, a stand-in for part B. It renders from a bundle directory **only through fields the schema marks required or declares**:
  - a lesson page (blocks → HTML)
  - an item page per check kind present
  - a checkpoint page
  - a project page that renders its `intro`, each item's `before`, and its `outro` ("Make it yours")
  - a card deck
  - one odd turtle exercise's `answer_md`, which holds publisher Markdown (`::: {.program}` panels, a `{=latex}` TikZ block, `{.python .answer-code}` fences); the consumer strips the `{=latex}` block and renders the rest, so part B inherits a worked example
  - the glossary

  `test_site_consumer.py`:
  - (a) renders every entry of every real book without `KeyError` and writes nothing outside `tmp_path`
  - (b) wraps the loaded JSON in a recording dict and asserts every key the consumer read is declared in the schema
  - (c) uses a fixture bundle that has one item of every check kind, checking each kind's page shows the right check control (fixture list, answer box, assert summary, expected-output box, predict box, checklist)
- **CI:** `scripts/ci-local.sh` run **solo** on the final commit. All green; `site-check` lines are recorded for the 4 books.

- [ ] **Step 1:** write the answer-model tests, including a deliberate leak fixture: export a fixture book, then append an even item's canonical text to that item's `statement_md` in the written bundle; `answer_model_findings` must FAIL on it. A second fixture whose canonical (`True`) appears in another exercise's statement must PASS. **Step 2:** FAIL. **Step 3:** implement. **Step 4:** PASS.
- [ ] **Step 5:** write the consumer and its tests; PASS.
- [ ] **Step 6:** solo `bash scripts/ci-local.sh`; record the green summary.
- [ ] **Step 7:** commit `plan 101 F: answer-model checks and minimal bundle consumer`.

## Dispatch

- Phases A+B: one Opus subagent, sequential (the foundation).
- Phases C and D: two Opus subagents in parallel, each with `isolation: "worktree"` on the plan branch. After both return, merge each worktree branch into the plan branch and run the C+D tests together.
- Phases E+F: one Opus subagent.
- Phase F's answer-model checks are written by a **fresh** Opus session that has not seen `answers.py`'s internals beyond its interface, so the leak check is not shaped by the code it guards.
- The session runs CI solo, the gates, and the reports.

## Out of scope

- Parts B–F (site, runner, PWA, backend, LLM). The slide split and slide audit (D6) are part B.
- **Confirming check-kind tags, authoring `answer_format` hints, per-cell `concepts` and `requirements` metadata:** the per-book content plans (rollout step 2). This plan ships `classify --apply` for them, but tags no real notebook.
- **Tooling-only plan:** it ships no unit, project or checkpoint content, so the content-review gate reviews tooling, generated bundles and reports, not lessons.
- recsys (D1).
- `answer_format` derivation from each unit's canonical-form rule (D3): part A derives from the canonical text only and reports every letter-bearing derived format as content work.

## Plan Review

### Round 1 (bb68d05)

- `[self]` APPROVE. Verified on real content: all 287 ACSL `short-answer` solutions carry exactly one `**Answer:**` line; python-projects projects group as 6 and 7 milestones.
- `[sol]` **REJECT** (ran on gpt-6-sol; AGENTS.md now names gpt-5.6-sol, so round 2 runs on gpt-5.6-sol):
  - `[FIXED]` Card keys reused block keys: cards get `#predict` / `back-matter/glossary/<id>` keys, unique across blocks, items and cards.
  - `[FIXED]` Project and entry content outside items was undefined: `intro[]`, `before[]`, `outro[]`, with a every-cell-exported test.
  - `[FIXED]` The probe skipped output-free cells: every executed cell is probed; the prelude closure follows mutating calls (`random.seed`).
  - `[FIXED]` The leak scan covered only code strings: every JSON string and every copied file; the schema ties `answer_md` to `after-attempt`.
  - `[FIXED]` An unmatched sample fell back to pair 1: no sample is revealed, with a `WARN:`; the sample fence may follow prose.
  - `[FIXED]` (nit) The CLI accepts `export --book B` as the design writes it; both orders tested.
- `[fable]` **APPROVE WITH NITS**:
  - `[FIXED]` The assert rule was vacuous for name-only asserts: every free name must be bound in the starter or named in the statement.
  - `[FIXED]` `trace` over-fired: narrowed regex plus non-empty stdout.
  - `[FIXED]` Milestones without a numbered solution section → `self-check`, reported; the leak corpus is every solution cell, independent of mapping.
  - `[FIXED]` `files` read the working tree: tracked files only, with a test.
  - `[FIXED]` The leak-text whitelist widened to every student-source notebook of the book.
  - `[FIXED]` `answer_format` canonical-form derivation moved to Out of scope.
  - `[FIXED]` Runtime: a real-lesson timeout is a FAIL, not data; the slow test reuses fresh findings; timing goes in the report.
  - `[FIXED]` Blocks carry `tags[]`; the consumer renders one odd turtle answer; the distractor fallback is tested for determinism.
- `[glm]` skipped (user decision 2026-09-28).

### Round 2 (8d6a231)

- `[self]` APPROVE.
- `[sol]` **REJECT** (gpt-5.6-sol):
  - `[FIXED]` `intro`/`outro`/`before` were missing from the schema and interfaces: added to the entry schema, `EntryContent`, `Item.before`, the schema test and the consumer test; challenge lead-ins attach to the first challenge.
  - `[FIXED]` The probe copied ignored scratch files: the temp copy holds tracked files only, and file writers join the prelude closure (same fix as [fable] 1).
  - `[FIXED]` The leak-text rule contradicted its fixture: the rule is now count-based (bundle occurrences ≤ student-source occurrences), with an injected-copy FAIL fixture and a legitimate-collision PASS fixture.
  - `[FIXED]` `glossary_entries` returns no definition or unit list: a new `glossary_records` parser, tested on all 4 real glossaries.
  - `[FIXED]` (nit) Builtins are excluded from the assert rule, with a `len` regression case.
- `[fable]` **REJECT**:
  - `[FIXED]` The probe copy and the closure missed file dependencies (python-concepts unit 12 cell 4 → 7; `savegame.txt`): tracked-only copy, writer-before-reader closure, `test_probe_file_written_by_earlier_cell` with a stale file present.
  - `[FIXED]` (nits) Builtins exclusion; findings-cache key defined (git tree hashes of `<book>/`, `tools/`, `books.yaml`, `site/ids/<book>*`, clean paths only); answer-model checks renumbered; challenge lead-ins in the first challenge's `before[]`.

### Round 3 (0acd82f)

- `[self]` APPROVE.
- `[sol]` **REJECT** (gpt-5.6-sol):
  - `[FIXED]` The text-leak baseline missed legitimately exported text: copied assets, fixture pairs and odd `student_answer_text` join it, with `.out`-collision and odd/even (`1110`) regressions.
  - `[FIXED]` Problem-based briefs: an export-owned partition (`## ` cells end a problem → next `before[]` or `outro[]`), with exact placements asserted on both real Problem projects.
  - `[FIXED]` Probe `error`/`timeout` are `FAIL:` lines in `site_check_findings`, with an integration test.
  - `[FIXED]` The code-leak scan would reject shipped asserts: top-level asserts are removed from the hidden corpus; `asserts.source` must be assert-only (AST), with three regressions.
  - `[FIXED]` `metadata.concepts` overrides are validated against the registry, with lesson and item regressions.
- `[fable]` **APPROVE WITH NITS**:
  - `[FIXED]` Fixtures and assets join the leak baseline (acsl false positives).
  - `[FIXED]` A same-cell write-then-read case is `standalone`.
  - `[FIXED]` `definition_md` keeps Markdown; comma unit lists parse; the concept comment is on the next line.

### Round 4 (7d9a71a)

- `[self]` APPROVE.
- `[fable]` **APPROVE**: re-ran the project partition on all four real briefs (every named id lands as claimed) and the assert-stripped leak scan over every Python-book solution cell (zero false hits). `[FIXED]` (optional) "In Problem mode" added to the partition rule.
- `[sol]` **REJECT** (gpt-5.6-sol):
  - `[FIXED]` Hidden solution assets (`solutions_exN*.py`, `solutions_challengeN*.py`) join the code-leak corpus, as in the publish audit, with JSON and file injection regressions.
  - `[FIXED]` Fixture text shipped twice: fixtures are now files only, referenced by path from `check.cases`, so each text has multiplicity one; a doubled-copy regression is added.
  - `[FIXED]` The concept-card fallback broke D8: distractors are always category-local; 1–2 peers give a smaller choice card and none gives a flip card; real-book category test.

### Round 5 (73312c4)

- `[self]` APPROVE.
- `[fable]` **APPROVE**: on real content, 15 hidden solution assets add no false hit, fixture files keep the sample rule, and category-local cards give 3/2/1-distractor and flip cards in every book.
- `[sol]` **REJECT** (gpt-5.6-sol):
  - `[FIXED]` Hidden prose answers were outside the leak check: check 6 counts every distinctive solution Markdown paragraph (≥ 40 characters, minus released odd answers and restated statements), with JSON and file injection regressions.

### Round 6 (ce4174b)

- `[self]` APPROVE.
- `[fable]` **APPROVE**: check 6 measured on the 4 real books: 1,150 hidden paragraphs, no rendered-over-raw excess (no false FAIL); the 40-character cut is sound.
- `[sol]` **REJECT** (gpt-5.6-sol):
  - `[FIXED]` Short answer-bearing prose (`So the answer is 5E.`) and short canonicals escaped: check 2 now counts canonicals of any length as whole tokens in content fields only, and check 6 includes any paragraph holding its item's canonical; regressions added.
  - `[FIXED]` All top-level asserts were stripped from the code corpus: only the exact asserts shipped as an item's `asserts.source` are removed; an even verify-cell regression is added.

### Round 7 (20e66c2)

- `[self]` APPROVE.
- `[fable]` **APPROVE**: on the 4 real books, any-length whole-token canonicals give 0 false FAILs (short tokens `5`, `0`, `True` in balance), and kept verify-cell asserts give 0 `solution_leak` hits against student code.
- `[sol]` **REJECT** (gpt-5.6-sol; the exact-only assert removal confirmed):
  - `[FIXED]` The baseline counted the unexported quick reference, which could mask an injected `A + ~B`: allowances come only from material the bundle maps, the quick reference is now exported as `reference_md`, a provenance test checks baseline paths, and a real-acsl `A + ~B` injection regression must fail.

### Round 8 (2f1fd6e)

- `[self]` APPROVE.
- `[fable]` **APPROVE**: no unmapped student material exists (every statement and lesson cell is mapped; back-matter is exactly glossary + quick reference, both exported); the hook, H1 and `sample_input` hold no canonical not found elsewhere. `[FIXED]` (optional) The lesson hook's export is stated.
- `[sol]` **REJECT** (gpt-5.6-sol):
  - `[FIXED]` The publisher's first-cell handling was missing: the H1 becomes the entry title, the hook becomes one `opener` block (added to the block types), with `test_lesson_opener_real` checking parity with `markdown_blocks(first=True)` on two real lessons.

### Round 9 (aa6e284)

- `[self]` APPROVE.
- `[fable]` **APPROVE WITH NITS**: all 74 first cells start with `# `. `[FIXED]` The parity target was wrong for hooks that open with a heading (acsl unit 12): the opener is now `render_chapter`'s whole hook, with `markdown_blocks(first=True)` as a secondary check on heading-free hooks.
- `[sol]` **REJECT** (gpt-5.6-sol): `[FIXED]` the same opener-parity point as [fable]'s nit; the rule and test now use `render_chapter`'s whole-hook contract.

### Round 10 (0a1e49b) — CONSENSUS

- `[self]` APPROVE.
- `[sol]` **APPROVE** (gpt-5.6-sol).
- `[fable]` **APPROVE**: the opener fold matches `render_chapter` on both test lessons; no regression.
- `[glm]` skipped (user decision 2026-09-28).

## Content Review

Gate roster per `docs/content-review-gate.md` (3-way since 2026-10-05: [glm] removed). [sol] runs on gpt-5.6-sol as AGENTS.md names it; the gate doc's `gpt-6-sol` disagrees and is flagged to the user.

### Review 1 — [self] (2026-10-05)
- **Verdict**: REJECT
1. `[FIXED]` **`expected-output` is proposed for free-design and interactive items.** Proposal rule 5 checks only that the *solution* runs deterministically, but the books' solutions replace `input()` and randomness with scripted sample values (`random.seed(4)`, `guess = int("52")`). Measured: in python-projects, 101 of 119 `expected-output` proposals print lines that appear in neither the statement nor the starter (unit 01 Exercise 1 "Print a title and a friendly message"; unit 02 Exercise 1 the dice roller). A correct student program would fail its check. In python-concepts, 168 of 172 are fixed by the statement's worked samples. Fix: rule 5 also requires every non-empty normalised output line to occur in the statement or the starter (this keeps D4's fix-the-bug items); otherwise fall through to `self-check` with reason `output not fixed by the statement`. Add regressions for a free-design item and a fix-the-bug item. Priority: Must Fix.
   → Response: rule 5 now also requires every non-empty normalised output line of the solution to occur, as a whole token sequence, in the statement or the starter (its code cells and shipped `.py` files) (`answers.output_fixed_by_statement`); otherwise `self-check` with reason `output not fixed by the statement`. Regressions: the demo free-design list and milestone, python-projects unit-01 Exercise 1 and unit-02 Exercise 1 (self-check), unit-01 Exercise 2 (fix-the-bug, output in the starter: expected-output), python-concepts unit-01 `2f6baca29bd1` (worked sample: expected-output). Proposed kinds now: python-projects asserts 91, expected-output 18, predict 5, self-check 122; python-concepts asserts 193, expected-output 164, predict 7, self-check 27; usaco-bronze fixtures 161; acsl answer 287, fixtures 72.
2. `[FIXED]` **Self-check requirements are a single first sentence** (python-projects unit 02 Exercise 4: "This code is broken on purpose."), which is no checklist. Fix: with no list in the statement, the requirements are the statement's prose sentences (Markdown stripped, no `**No real version:**` / `**Real version:**` notes, at most 6). Priority: Should Fix.
   → Response: with no list, the requirements are the `**Specification:**` paragraph's sentences; else every prose sentence (Markdown stripped; headings, panels, tables, quotes, bold labels and the `**No real version:**` / `**Real version:**` notes left out), at most 6 (`answers.statement_sentences`); the label only as a last resort. Regressions: synthetic Specification and prose statements, python-projects unit 02 Exercise 4, python-concepts `u01e15a`'s Specification.
3. `[WONTFIX]` **Curriculum observation (from Phase F):** python-concepts checkpoint-03 Q3 `sum_to_n` and checkpoint-04 Q5 `most_common` print their answers verbatim in lessons (`u07l024`, `u11l028`). The answer model treats them as student-visible. This is not a site defect; it goes to the user as a curriculum question. Priority: Nice to Have. → Response: out of scope for this tooling plan; changing checkpoint content would expand it. The site handles it correctly (counted as student-visible), and the curriculum question is listed under Follow-ups for the user to decide (errata or a content plan).

### Review 1 — [fable] (2026-10-05)
- **Verdict**: APPROVE WITH NITS. Evidence: independent 2- and 3-line window search of every hidden solution source found none in any bundle field except released odd `answer_md` (shared idioms); 40/40 sampled odd answers are verbatim in the appendix; usaco re-export byte-identical; three lessons cover every cell in order; the turtle fix is correct.
1. `[FIXED]` `statement_program` picks a comment-only starter over the statement's ```` ```python ```` fence, so python-concepts exports 0 `predict` items (`u01e15a` "Predict the Output", `u07e20a`, `u07e21a`). Skip code cells with an empty AST body. Should Fix.
   → Response: `statement_program` skips code cells whose `ast.parse(...).body` is empty, then falls back to the ```` ```python ```` fence. `u01e15a`, `u07e20a` and `u07e21a` are now `predict` (canonical `A B\nx-y-z\nGo!Now\n` for `u01e15a`). Regression with a comment-only starter plus fence on the demo book.
2. `[FIXED]` `expected-output` proposed for items a student cannot reproduce (seeded random, "your own …", "your name"); same root cause as [self] 1. Should Fix.
   → Response: fixed with [self] 1 (same rule).
3. `[FIXED]` `PREDICT` misses "Without running …, predict the values" / "predict the exact output". Extend the regex. Should Fix.
   → Response: `PREDICT` also matches `predict (the )?(values?|result|exact)`, `without running` and `before running`; `test_predict_not_trace_by_hand` still passes. `u02e058` now matches; its fenced program is bare REPL-style expressions that print nothing, so it falls through to `expected-output` (the statement's sample fixes the output), as the regression records. New `predict` proposals: python-projects checkpoint-01 Q2, checkpoint-02 Q1 and Q5; python-concepts `u07e22a`, `u11e140`, `u12e079`, `u13e066`, all statements that ask for the output of given code.
4. `[FIXED]` The self-check fallback picks the hook sentence; prefer the `**Specification:**` paragraph's sentences (same root as [self] 2). Nice to Have.
   → Response: fixed with [self] 2: the Specification paragraph wins.
5. `[FIXED]` acsl report noise: 302 `unattributed` short-answer items; report per kind and exempt short-answer items. Nice to Have.
   → Response: the report's `unattributed.items` is now a map from check kind to keys; `answer` (short-answer) items have no code, so they are counted in `unattributed.short_answer_exempt` and get no `concepts: unattributed` note. acsl now reports 15 unattributed `fixtures` items and 287 exempt short answers; usaco-bronze 1 `fixtures` item; the Python books none.
6. `[FIXED]` `answers._run_once` keeps `PYTHON*` env vars, while the probe strips them; use one env builder. Nice to Have.
   → Response: one builder, `probe.sandbox_env()`, used by `answers._run_once` and the probe runner: every `PYTHON*` variable, `DISPLAY` and `WAYLAND_DISPLAY` stripped; `PYTHONHASHSEED=0`, `PYTHONIOENCODING=utf-8`, `PYTHONDONTWRITEBYTECODE=1`, `MPLBACKEND=Agg`. Regression `test_sandbox_env`.
7. `[FIXED]` `_odd_findings` raises `KeyError` for an entry outside the syllabus; emit a `FAIL:` line. Nice to Have.
   → Response: a bundle entry outside the syllabus gives `FAIL: <book>: <entry>: entry is not in the syllabus` and its items are skipped. Regression `test_entry_outside_the_syllabus_is_a_fail_not_a_crash`.
8. Curriculum observation, the same as [self] 3.

### Review 1 — [sol] (2026-10-05, gpt-5.6-sol)
- **Verdict**: REJECT. C, D and E deviations accepted; the Phase F hidden-stream suppression is not.
1. `[FIXED]` Check 1 drops a whole hidden stream once it occurs in any exported source, so extra copies are never detected (`answer_model.py:441-450`; `sum_to_n`, `most_common`). Count- or location-match visible streams instead, with an extra-copy regression. Must Fix.
   → Response: check 1 now counts: for each hidden stream, the bundle strings and copied files containing it (`solution_leak`) may not outnumber the exported sources that contain it; nothing is dropped. Fields tied to another by design (`check.program`, `check.functions`, a concept card's term, distractors and definition) are not counted and are tied instead. Regression on the real python-concepts bundle: an extra copy of checkpoint-03 Q3's `sum_to_n` solution in Question 1's starter FAILs; the unmodified bundle passes.
2. `[FIXED]` The minimal consumer prints the full assert source (`tests/site_consumer.py:98-101`), and its test requires it; D5 says assert source is not printed. Render only the result/function summary, and assert the raw source is absent. Must Fix.
   → Response: `tests/site_consumer.py` renders only the function summary and one pass/fail line per assert (`check n of N`); the test asserts the raw (and HTML-escaped) `check.source` is absent from the page.
3. `[FIXED]` The canonical leak scan skips student-visible fields such as self-check `requirements` (`answer_model.py:60-61, 392-395`). Count every student-visible string field, with injection regressions. Must Fix.
   → Response: check 2 now counts every string field except an exclusion list of non-content fields (keys, ids, bundle paths, hashes, enums, config: `release`, `pdfs`, `settings`, `flags`) plus titles and labels, which the plan's check 2 excludes ("never in keys, labels or titles"), and the tied fields above. Newly counted: `requirements`, `answer_format.hint`, `sample_input`, concept `name`, glossary `term`, `asserts.source`. The baseline gains the matching sources: lesson cells' `sample_input` metadata, `curriculum/concepts.yaml`, and `answers.check_texts` (each item's requirements and hint, computed from the repo, and the asserts `asserts` items ship by design). Regressions: a hidden canonical injected into a self-check requirement, into `answer_format.hint` and into a concept name each FAIL; a changed card term FAILs its tie. All 4 books still pass `site-check`.

### Review 2 — [self] (2026-10-05)
- **Verdict**: APPROVE. Sampled python-projects units 01–02: free-design items are now `self-check` with usable Specification-sentence checklists; the remaining `expected-output` items are statement-fixed.

### Review 2 — [fable] (2026-10-05)
- **Verdict**: APPROVE WITH NITS. Every round-1 fix was verified on re-exported real bundles: 0 answer-model findings; 119/164 python-concepts `expected-output` hashes equal the statement's `**Expected output:**` fence, and the rest come from worked samples; all 12 `predict` items trace the statement's program.
1. `[FIXED]` `_plain` mangles inline code in requirements (`unit-06-secret-codes` Exercise 4: `"  secret_launch  "` becomes `" secretlaunch "`). Keep code spans verbatim. Should Fix.
   → Response: `answers._plain` now strips links, emphasis and extra whitespace only outside inline code spans; a span keeps its exact text, only its backticks go (and CommonMark's one-space padding). Regressions: synthetic spans (`a  *b*  c`, a double-backtick span holding a backtick) and python-projects `unit-06-secret-codes` Exercise 4, whose first requirement is now `Store "  secret_launch  " in a variable.`
2. `[FIXED]` `PREDICT` misses "Which one message prints" (`checkpoint-01` Question 7). Nice to Have.
   → Response: `PREDICT` gains `which (one )?(message|line|branch) (prints|runs)`. The phrase is in python-projects `checkpoint-01-first-steps` **Question 4** (the `if`/`elif`/`else` trace), which is now `predict`; `test_predict_not_trace_by_hand` stays green. python-projects proposed kinds: asserts 91, expected-output 17, predict 6, self-check 122 (the other books are unchanged).
3. `[FIXED]` One-token numeric `expected-output` outputs pass `output_fixed_by_statement` trivially; flag them in the report. Nice to Have.
   → Response: an `expected-output` item whose normalised canonical is one number gets the note `expected-output: single-token output (<n>)`, and the site report lists it in `single_token_outputs` for a content plan to confirm: 6 in python-projects, 8 in python-concepts, none in the contest books. Regressions: python-concepts `u02e043` (`18`) is flagged, python-projects checkpoint-01 Question 4 is not; the report list.

### Review 2 — [sol] (2026-10-05, gpt-5.6-sol)
- **Verdict**: REJECT.
1. `[FIXED]` Hidden-code counting counts containing fields, not occurrences: two copies inside one `starter` pass. Count occurrences (or require source-location parity), with same-field and same-file regressions. Must Fix.
   → Response: check 1 now counts occurrences: per string or file, the non-overlapping occurrences of each hidden stream as `solution_leak` matches it (the whole block, or a contiguous run inside it for a stream of 30+ tokens), taking the larger of the whole-text count and the fences' summed count so a fence is never counted twice; the allowance is the same count over the exported sources. Regressions on the real python-concepts bundle, where checkpoint-03 Q3's `sum_to_n` occurs 3 times in the sources (a unit-07 lesson block, twice in an odd answer): the lesson copy moved into one starter as two copies (two containing fields, which the field count passed), an extra copy appended to the lesson block itself, and the lesson copy moved into one copied file plus an extra copy there each FAIL with `(4 occurrence(s), 3 in exported sources)`; the clean bundle passes.
2. `[FIXED]` The canonical allowance includes the whole raw `concepts.yaml`, though only `{id, name, category}` is exported. Build the baseline from the exported projection, with an unmapped-field collision regression. Must Fix.
   → Response: the baseline now takes from the registry only the exported projection (`book_registry(...).concepts`, exactly what book.json `concepts` holds), field by field: one source per concept's counted `name` (`concepts.yaml#concept:<id>/name`). `id` and `category` are not counted in the bundle, so they earn no allowance either; the new `registry` tie requires book.json `concepts` to equal the projection. Regression: `159` added to the demo registry as an unexported `kind:` value and a comment earns nothing, so `159` injected into a statement FAILs (`1 occurrence(s), 0 in exported sources`). `test_baseline_provenance` now checks the registry sources field by field against book.json `concepts`.
3. `[FIXED]` `segment.color` is student-visible but excluded and not tie-checked. Regenerate figures and compare, or count `color`; add a color-injection regression and make field coverage exhaustive. Must Fix.
   → Response: both. The `figures` tie replays every block's own (counted) `code` with `turtle_segments(code, stdin)` (stdin from `sample_input` for `tryit+figure`) and requires the `figure` to equal it. Field coverage is now exhaustive: every string field is either in `COUNTED_FIELDS` (check 2) or held by a named tie check in `TIES` (`tie_of`): `schema` (enums, consts, sha256 hashes), `keys` (a cell id of a mapped notebook, with a part, `asset:` or `predict` suffix, or a glossary card of a registered concept), `ids`, `paths` (a copied file with a repo source), `release` (`unreleased` or `pdfs-<date>`, and `pdfs` its links), `settings`, `routes`, `figures`, `tags` (tags of the source cell), `registry`, `divisions` (the season ladder), `titles` (books.yaml, the entry notebook's H1, the item's own heading text; labels `<kind> <number>`), and the existing `predict program`, `assert functions` and `glossary cards`. A check that cannot read a tampered bundle gives a FAIL instead of crashing. Tests: every schema string property is classified; every string of the demo and the 4 real bundles is counted or tied; `159` written into each uncounted field path of the demo bundle (144 paths: every uncounted field of every bundle file) FAILs; real-bundle injections of a hidden canonical into a segment `color` (python-projects: `turtle figure differs from the replay of its code`), a lesson tag, an ACSL item division and `settings.acsl_divisions` FAIL; a PDF link FAILs. Titles stay out of check 2 (Phase F: "never in keys, labels or titles"), so `test_canonical_in_title_is_not_content` became `test_canonical_in_title_is_not_counted_but_tied`.

### Review 3 — [self] (2026-10-05)
- **Verdict**: APPROVE. The round-2 fixes were verified through [fable]'s real-bundle runs and the `site-check` passes. The title-tie fix (below) is re-run on all four real books: 65/65 answer-model tests pass.

### Review 3 — [fable] (2026-10-05)
- **Verdict**: APPROVE. All four r3 bundles show 0 answer-model findings; every string field of every real bundle is counted or tied; the round-2 nits and Must Fixes are verified.
1. `[FIXED]` (Nice to Have) `_tie_titles` accepted a title whose words appear anywhere in the item's statement. → Response: fixed as [sol] 1 below.

### Review 3 — [sol] (2026-10-05, gpt-5.6-sol)
- **Verdict**: REJECT.
1. `[FIXED]` Item-title ties were not exact: `u02e043`'s title set to its hidden canonical `18` passed, because `18` occurs in its statement. Must Fix. → Response: `_tie_titles` now requires each item title to equal the exporter's own title (`entry_content(...).items[].title`, `AnswerModel._exported_titles`); the word-anywhere helper is removed. Regression `test_real_item_title_must_equal_exported_heading` (real python-concepts `u02e043` → `18` FAILs) was seen failing first.

### Review 4 — CONSENSUS (2026-10-05)
- `[self]` APPROVE.
- `[sol]` **APPROVE** (gpt-5.6-sol): no findings; the exact title tie rejects the real `u02e043` → `18` case and the clean bundle passes; the C–E deviations are accepted, and Phase F now counts visible hidden streams.
- `[fable]` **APPROVE**: the title-tie fix gives 0 findings on all four re-exported books.

## Post-Execution Report

**Shipped: design 012 part A.** `py4kids-tools export --book <id>` writes a schema-checked JSON bundle for each of the four `site: true` books, and `site-check` runs in `ci-local.sh` step 4.

| book | bundle | keys | items | proposed check kinds |
|---|---|---|---|---|
| python-projects | 0.9 MB | 1,126 | 236 | asserts 91, expected-output 17, predict 6, self-check 122 |
| python-concepts | 1.5 MB | 1,842 | 391 | asserts 193, expected-output 164, predict 7, self-check 27 |
| usaco-bronze | 3.5 MB | 803 | 161 | fixtures 161 |
| acsl | 1.7 MB | 1,370 | 359 | answer 287, fixtures 72 |

- **Lessons:**
  - 718 executed lesson cells are probed. 648 are standalone and 70 need earlier cells; none mismatches, errors or times out.
  - The probe takes about 17 s for all four books, and each book's `site-check` takes 20–90 s cold or about 2 s cached.
  - Cards: 712 predict cards (433 typed, 279 flip), and 174 concept cards whose distractors always come from the card's own category.
- **Answers:**
  - Odd unit exercises carry the Student Book appendix text verbatim (one shared `student_answer_text`; the publication regression tests are byte-identical).
  - Every other answer ships only as a salted hash.
  - The answer model (6 checks; every bundle string counted or tied to its source) finds 0 issues on all four books. Every injection regression the gates named fails as it should, including on the real bundles (`A + ~B`, `So the answer is 5E.`, a duplicate `sum_to_n`, a title of `18`).
- **Ids:** the first ledgers are in `site/ids/`. Keys are unique across blocks, items, side blocks and cards.
- **Determinism:** re-exports under other `PYTHONHASHSEED` values, and with untracked scratch files present, are byte-identical.
- **Tests:** the global suite has 1,936 passed and 2 skipped (about 300 of them are `tests/test_site_*.py`); the routed recsys suite has 152 passed. `scripts/ci-local.sh` ran ALL GREEN solo at 0824a5d, with every book rendered and audited.
- **Gates:**
  - Plan review: 10 rounds to consensus ([sol] on gpt-5.6-sol, [fable]; [glm] skipped).
  - Content review: 4 rounds. Round 1 found free-design items proposed as `expected-output` (101 of 119 in python-projects) and four leak-check gaps; all were fixed.

**Implementer deviations (accepted at the gates):**
- Concept cards are stored in the entry of the unit where their term is first taught.
- Fixtures must be tracked in git.
- The asserts rule is tightened: an assert that names nothing the student writes is not portable.
- `statement_md` leaves out asset listings, which ship as `files` instead.
- A division id is the first word of its `_Division:_` line.
- The answer model ties every uncounted field (titles, tags, figures, settings and so on) exactly to its source.

**Follow-ups:**
- **Per-book content plans (rollout step 2):** confirm the `check-*` tags; author `answer_format` hints (323 derived formats contain letters); confirm the single-token `expected-output` items (6 + 8); add per-cell `concepts` where attribution is empty (usaco-bronze 59 and acsl 128 lesson blocks); and run a `slide-break` pass.
- **Curriculum question for the user:** python-concepts checkpoint-03 Q3 (`sum_to_n`) and checkpoint-04 Q5 (`most_common`) appear verbatim in lessons `u07l024` and `u11l028`.
- **Governance mismatch for the user:** `docs/content-review-gate.md` names `gpt-6-sol` for [sol], while AGENTS.md names `gpt-5.6-sol` (used here).
- **Next plans:** part B (the Astro site core, privacy notice and terms) and part C (the isolated runner; its JS port must follow `tools/export/hash_vectors.json`, including the Python-vs-JS `\s` cases).
