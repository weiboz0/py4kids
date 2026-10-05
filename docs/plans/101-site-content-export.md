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
2. **A probed cell that hangs or calls `input()`**: each probe run has a timeout and stdin from `/dev/null`; the cell is reported (`probe: "timeout"` / `"error"`), and the export finishes. Test in Phase C.
3. **Canonical answers with CRLF, tabs, NBSP, trailing blank lines or mixed case**: `normalise` treats every Unicode whitespace like a space, drops leading and trailing blank lines, and folds case only when `answer_format.case` is `insensitive`. `hash_vectors.json` pins each case for the JS port. Test in Phase B.
4. **Re-export under a different `PYTHONHASHSEED`, or after only `git checkout`** (file mtimes, glob order, set order): byte-identical bundle and the same content hash. Test in Phase E.
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
- `duplicate_key_findings(keys: Iterable[str]) -> list[str]`.
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
  - `test_site_schema.py`: both schemas validate under `jsonschema.Draft202012Validator.check_schema`. A sample progress event per `kind` validates. An event with a `code` field, or with `detail: {"text": "…"}`, fails (`detail` allows only `cases: [{"n": int, "pass": bool}]`, `self_grade: "got-it"|"not-yet"`, `box: int`, `checklist: [bool]`).
- [ ] **Step 2:** run them; expected FAIL.
- [ ] **Step 3: implement.**
  - `ids.py` and `normalise.py` as above.
  - `hash_vectors.json`: a list of `{input, case, normalised, item_key, hash}` objects, generated once by the tests' helper and committed; the test also asserts the file matches the code.
  - **The bundle schema** (`$id: py4kids/bundle/1.0.0`). Top-level `book.json`:
    - `schema_version`, `book{id,title,subtitle,flags{acsl,judge}}`, `release{tag,content_hash}`
    - `entries[{id,kind,title,number,file}]` in syllabus order
    - `concepts[{id,name,category}]`, `glossary[{term,definition_md,concept,units}]`
    - `settings{lesson_heading,acsl_divisions?}`, `pdfs{edition: url}|null`
  - `entries/<entry-id>.json`: `{schema_version, entry{id,kind,title}, lesson{blocks[]}|null, items[], cards[], files[]}`.
    - A `block`: `{key, type, md?, code?, output?, route?, stdin?, sample_input?, figure?, needs_prelude, prelude[], files[], concepts[], probe}`.
    - An `item`: `{key, kind, number|null, label, title, division[], stretch, concepts[], statement_md, starter, files[], check{…}, answer_visibility, answer_md?}`.
    - `check` is a `oneOf` keyed on `kind`:
      - `fixtures{cases[{n,in,out,sample}], match:"line"|"token", over_budget[]}`
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
- **Consumes** `item_key`, `route_code(cell, stdin_note=False)`, `NOTICE`, `markdown_blocks`, `strip_turtle_directives`, `glossary_entries`, `scanner_profile`, `detect`.
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
  - a cell starting `### You will learn` → `goals`; `### Recap` → `recap`
  - a Notice paragraph plus its continuations (as `markdown_blocks` groups them) → `notice`
  - other prose splits at every `##`/`###` heading into `prose` blocks
  - block `n` of a cell gets key `…/<cell_id>#n` for n ≥ 2; the first part keeps the bare key
  - Lesson asset listings (`asset_blocks`' names) → `program` blocks keyed `…/<cell_id>#asset:<name>`, with the file copied into `files/`.
- **Probe:** runs only on executed cells that have a stored stream output.
  - Copy `entry_dir` to a temp dir, then run each cell alone under `sys.executable` with cwd at the copy, stdin `/dev/null`, `PYTHONHASHSEED=0` and the timeout.
  - Compare stdout with the stored output, with trailing whitespace stripped per line and trailing blank lines ignored.
  - On a miss, the prelude is the transitive closure of earlier executed cells that bind a name the cell loads (`ast`: Assign/AugAssign/AnnAssign targets, def, class, import, for-target, with-as). Run prelude + cell in one process, with a sentinel line printed before the cell; compare only the output after the sentinel.
  - If that still misses, use all earlier executed cells. If it still misses → `mismatch`.
  - `files`: string constants in the cell (and its prelude) that name an existing file in the entry dir or `assets/`. Solution sources and `assets/verify/**` are excluded.
- **Concepts:** `detect` on the cell's AST with the book's profile, intersected with `registered`. A heading or code cell's `metadata.concepts` list overrides the scan. An empty result goes into the report as `unattributed`.
- **Predict cards:**
  - Eligible blocks are `code` blocks with `output` and probe status `standalone` or `prelude`.
  - `mode: "typed"` when the normalised output is one line; otherwise `"flip"`.
  - `{key: block key, kind: "predict", block, mode, prelude}`. Lesson outputs are already visible on the page, so no hash is needed.
- **Concept cards:**
  - One per glossary entry: `{key: "<book>/glossary/<concept>", kind: "concept", concept, term, definition_md, distractors[3]}`.
  - Distractors are other glossary terms whose concept shares the `category`, sorted by term, taking the first 3 after the entry's own term (deterministic).
  - Fewer than 3 in the category fill from the whole glossary in term order; that case is listed in the report.

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
  - `test_probe_hang_and_input`: c5 `timeout` and c6 `error` within `2 * timeout_s` (timeout 2 s in the test) (Review Focus 2).
  - `test_blocks_types_and_keys`: m2 gives two prose blocks, `…/m2` and `…/m2#2`; c7 is `error-demo`; c8 is `turtle-figure` with 4 segments; m1 is `goals`; m3 is `notice`.
  - `test_unknown_route_fails`: monkeypatch `route_code` to return `('weird', '')` → `ValueError` naming `weird`.
  - `test_predict_cards`: c3 typed; a two-line output gives flip; c5 is not a card.
  - `test_concept_cards_deterministic`: a 4-entry fixture glossary gives the same distractors on two runs, all from the same category.
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
  - `entry_items(root, book, entry_dir, kind) -> list[Item]`. `Item` is a dataclass with `key, kind ("unit"|"challenge"|"checkpoint"|"project"), number, label, title, division, stretch, concepts, statement_md, starter, files, heading_cell, solution_group`; `solution_group` is the matching solution group, used only inside `answers.py`.
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
  - The heading cell's id is the key; a challenge split out of a note cell gets `#2`.
  - `statement_md` is `statement_text` + `markdown_blocks` per markdown cell, as `_item_body` does with `edition='student'`, minus the starter panels; `PLACEHOLDER` paragraphs are dropped.
  - `starter` is the item's code cells (non-`verify`) joined with a blank line.
  - `stretch` from the tag; `division` from `item_divisions`.
  - `concepts`:
    - from the heading cell's `metadata.concepts`, if present
    - otherwise `cell_concepts` (Phase C) over the starter and the solution code, intersected with the entry manifest's `introduces ∪ requires ∪ practices`. Only ids leave `answers.py`, never code.
    - an empty result is listed as `unattributed` in the report
    - Phase D stubs `cell_concepts` behind its Phase C signature until the merge.
- **Proposal order (first match wins):**
  1. `fixtures`: a judge book with solver `assets/<prefix>N.py` and fixture pairs.
  2. `answer`: a `short-answer` heading tag.
  3. `predict`: the statement asks what code prints (`(?i)\b(what (does|will) .* print|predict( the)? output|trace)\b`) and has a code cell.
  4. `asserts`: the solution's top-level asserts all call only functions whose names are defined in the statement's starter or named in the statement in backticks (`name(`). Otherwise reason `asserts test the solution's own choices`.
  5. `expected-output`: the solution runs twice (temp copy, stdin `/dev/null`, `PYTHONHASHSEED=0`, timeout 20 s) with identical non-empty stdout, and neither the solution nor the starter calls `input(` or imports `random` without `seed(`.
  6. Else `self-check`.

  `turtle: true` when the starter or solution imports turtle (the three-part rule is applied in part C).
- **Canonical texts (answers.py only):**
  - `answer` → the `**Answer:**` line (`ANSWER_LINE`) in the solution group. Exactly one is required; otherwise FAIL naming the item.
  - `predict` → the stdout of the statement's code cell, run as in proposal step 5.
  - `expected-output` → the solution's stdout, run the same way.
  - `asserts` ships `source` = only the top-level `assert` statements (`ast.unparse`), and `functions` = the names they call. No function body ever ships.
  - `fixtures` ships every pair as `{n, in, out, sample}`. `sample` is true for the pair whose input equals the statement's first `Sample Input` code block (whitespace-normalised); if none matches, it is pair `1`, and the report lists the item. Pairs over `fixture_budget_kb` go to `over_budget` and the report. `match` is `"line"` when the book has the `acsl` flag, else `"token"`.
  - `self-check` → `requirements` from the heading cell's `metadata.requirements` if present; else the statement's bullet and numbered list items (Markdown stripped to text); else one requirement, the statement's first sentence. The report lists `self-check` items with no list.
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
  - `test_propose_each_kind`: one fixture item per kind gives that kind, with its reason. Includes a non-portable assert example: `assert my_list == [3, 1, 2]` where `my_list` is the student's own choice → not `asserts`.
  - `test_apply_proposals_roundtrip`: the tags are written; a second apply changes nothing; cell ids and outputs are unchanged.
  - `test_tag_findings`: two `check-*` tags; a `check-*` tag on a body cell; `check-bogus`.
  - `test_odd_answer_equals_appendix`: for every odd unit exercise in **all 4 real books**, `student_answer_text` equals the matching slice of `answer_key(entry, 'unit', items, 'student', lesson_heading)` (the appendix text).
  - `test_hidden_items_ship_hash_only`: an even `answer` item's dict has `check.hash` and no canonical text anywhere in `json.dumps(item)`.
  - `test_asserts_ship_no_function_body`.
  - `test_fixture_sample_and_budget`: the sample matches the statement; a 200 KB fixture pair is `over_budget` with `fixture_budget_kb: 130`.
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
    - over-budget fixtures (`WARN:`)
    - `WARN:` per probe `mismatch`

    Only `FAIL:` lines fail.
- **CLI:**
  - `py4kids-tools --book B export [--out DIR] [--release TAG] [--update-ledger]` (default out `site/content/B`)
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
  - `test_site_check_real_books`: `site_check_findings` for each of the 4 books has no `FAIL:` line (marked `slow`, like the existing slow tests)
- [ ] **Step 2:** run; FAIL. **Step 3:** implement. **Step 4:** run; PASS.
- [ ] **Step 5:** `uv run py4kids-tools --book <b> export --update-ledger` for the 4 books. Check `git status`: only `site/ids/*.json` are new tracked files, and `site/content/` is ignored.
- [ ] **Step 6:** commit `plan 101 E: bundle writer, export/classify/site-check CLI, ci-local site step, first id ledgers`.

### Phase F — Verification (named verification phase)

**Files:** `tools/export/check.py` (answer-model findings); `tests/site_consumer.py`; `tests/test_site_consumer.py`, `tests/test_site_answer_model.py`.

- **The answer-model test (D5).** `answer_model_findings(root, book, bundle_dir) -> list[str]`:
  1. **Leak, code:** for every `none` item, each solution code cell (via `answers.py`) is tokenised. The publish audit's `solution_leak(block, sources)` (`tools/publish_audit.py:321`) is run against every code string in the bundle (starters, blocks, `asserts.source`). A hit → `FAIL: <book>: <key>: solution code leaked into <bundle key>`.
  2. **Leak, text:** every hidden canonical text whose normalised length is ≥ 4, or that has ≥ 2 tokens, must not occur in any bundle string unless it also occurs in a student-visible source (that item's statement or starter, the entry's lesson, or the glossary) (Review Focus 5).
  3. **Odd answers:** every `after-attempt` item's `answer_md` equals `student_answer_text`, and the set of `after-attempt` keys equals the odd unit exercises exactly.
  4. **Hashes:** every `answer`, `predict` and `expected-output` item's `check.hash` equals `answer_hash(key, canonical, case=answer_format.case)`.
- **The consumer test.** `tests/site_consumer.py` is ≈150 lines of plain Python, a stand-in for part B. It renders from a bundle directory **only through fields the schema marks required or declares**:
  - a lesson page (blocks → HTML)
  - an item page per check kind present
  - a checkpoint page
  - a card deck
  - the glossary

  `test_site_consumer.py`:
  - (a) renders every entry of every real book without `KeyError` and writes nothing outside `tmp_path`
  - (b) wraps the loaded JSON in a recording dict and asserts every key the consumer read is declared in the schema
  - (c) uses a fixture bundle that has one item of every check kind, checking each kind's page shows the right check control (fixture list, answer box, assert summary, expected-output box, predict box, checklist)
- **CI:** `scripts/ci-local.sh` run **solo** on the final commit. All green; `site-check` lines are recorded for the 4 books.

- [ ] **Step 1:** write the answer-model tests, including a deliberate leak fixture (an even item's canonical copied into its statement field) that must FAIL. **Step 2:** FAIL. **Step 3:** implement. **Step 4:** PASS.
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

## Plan Review

_(gate verdicts recorded here)_

## Content Review

_(gate findings recorded here)_

## Post-Execution Report

_(written before the PR)_
