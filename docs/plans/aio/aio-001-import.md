# Plan aio-001 — Import: registry, snapshot, `tools/aio/`, CI routing

**v2.6** (2026-10-31) folds round 6 ([sol] APPROVE; [fable] APPROVE WITH NITS, 5 NIT) — **plan gate CLOSED (consensus)**. **v2.5** folded round 5 ([sol] REJECT: 3 MUST; [fable] APPROVE WITH NITS: 3 MUST + 2 NIT); the rename is now outcome-gated. **v2.4** folded round 4 ([sol] REJECT: 2 MUST; [fable] APPROVE WITH NITS: 2 MUST + 2 NIT). **v2.3** folded round 3 ([sol] REJECT: 1 BLOCKER + 2 MUST; [fable] APPROVE WITH NITS: 2 MUST + 3 NIT). **v2.2** folded round 2 ([sol] REJECT: 1 BLOCKER + 1 MUST; [fable] APPROVE WITH NITS: 3 MUST + 6 NIT). **v2** folded plan-review round 1 ([self] 1 MUST; [sol] REJECT, 1 BLOCKER + 2 MUST + 1 NIT; [fable] APPROVE WITH NITS, 6 MUST + 5 NIT).
**Design:** `docs/designs/014-aio-books.md` (v4.2, APPROVED by the author 2026-10-31, "Do it autopilot").
**Governance precondition:** the design-014 governance amendments (AGENTS.md content-models law, D-006, aio reviewer duties) merge first, on `feature/design-014-aio-books`.
**Autopilot** per AGENTS.md.

This plan moves the two books of `weiboz0/usaaio` at `a20128f` into py4kids as `aio-ml` and `aio-dl` (`content_model: aio`),
ports usaaio's verification into `tools/aio/`, and routes `scripts/ci-local.sh` so the books are verified here exactly as they were there.
It **writes no new content**. Editions (`publication`) are aio-002; the website (`site`) is aio-003.

## Goal
`TMPDIR=/dev/shm bash scripts/ci-local.sh` is green with both aio books registered, and the D4 parity table shows that every usaaio CI gate
has a py4kids destination with the same PASS/SKIP outcome as at usaaio `a20128f` (or a listed, justified difference).
The py4kids-model books' results are unchanged.

## Global constraints
- **The repo is PUBLIC.** The snapshot is driven by usaaio `git ls-files` (design D3 step A). Raw past papers, hidden test sets and the download cache are provisioned locally (step B) and are never tracked.
  The guard and a verification assertion enforce it.
- **Fidelity.** Imported files change only by the D3 renames and the D4 tooling dispositions. No notebook output is cleared.
- **Isolation.** Every aio command runs under `uv run --group aio`. The group-free `pytest -q` never collects aio tests.
  py4kids tools key on `content_model`, `aio_round` and flags, never on ids.
- **The usaaio repository is read only.** No command writes to `../usaaio`.
- **Dispatch** (AGENTS.md): tooling code (`tools/aio/`, `scripts/aio/`, `tools/`, `scripts/`) by Opus subagents, one phase each, with the phase brief and the design as context; the import itself (Phase C) is a scripted copy, run inline and reviewed.

## Phases

### Phase A — dependencies and external artifacts
- `pyproject.toml`: an `aio` dependency group (design D8 list; torch/torchvision through the existing `pytorch-cpu` index), and `[tool.hatch.build.targets.wheel]` excludes `tools/aio/tests/`.
  `uv lock` must resolve `aio` with `recsys` and `roar`; if it cannot, add a `[tool.uv] conflicts` entry and record why.
- **Pre-import overlap scan.** In a fresh clone of usaaio at `a20128f` under `/dev/shm` (the same clone F.1 uses; `../usaaio` is never written), fetch the corpus with its `scripts/fetch-reference.sh --all`
  and run usaaio's own `usaaio-tools --book book1 overlap-scan` and `--book book2 overlap-scan` (the pinned CLI's command name, `tools/cli.py:26-30`), requiring a non-skipped PASS **with zero corpus extraction failures**: the scanner logs a failed `pdftotext` extraction only as a warning (`overlap.py:169-187,242-243,304` at `a20128f`), so the run must also report the expected corpus parts and the extracted ones, and any shortfall fails it. The whole-import-set scan applies the same rule.
  Because that scanner reads only mock-test statements and practice notebooks (`overlap.py:245,296`), a **whole-import-set scan** follows: a scratch script (in the scratchpad, not committed) imports the clone's `tools.checks.overlap` scoring and thresholds and scores
  **every file in the import set** (every Phase B destination: book roots, `tools/`, `tests/`, the ported scripts, the six live docs, and the archive) by its text: `.md`, `.yaml`/`.yml`, `.py`, `.sh`, `.txt`, `.csv`, `.json`, `.toml`, `.lua`, `.tex`, `.gitignore`, `.gitkeep` as plain text (at `a20128f` that covers every extension in the tree: 1,348 `.ipynb`, 115 `.py`, 93 `.md`, 64 YAML, 8 `.sh`, and the rest), `.ipynb` by markdown and code sources.
  Any other extension (images, binaries) is listed in its report and must be justified as non-text; an unlisted unscanned file fails the scan.
  Any hit is resolved (redacted at the source path in the import script's rename table) **before the first import commit**, so no commit ever carries flagged text.
- **Artifact inventory.** `git -C ../usaaio grep -n -E 'gensim\.downloader|torchvision\.(models|datasets)|weights=|download=True|torch\.hub|load_state_dict_from_url|urlretrieve|urlopen|requests\.get|hf_hub' a20128f --`
  (the SHA passed as the tree argument), plus a manual read of each hit's cell for the artifact it fetches.
  Record each artifact in `aio-ml/curriculum/artifacts.yaml` (one file for both books): name, source URL, cache path under `<book>/reference/cache/`, size, SHA-256, consuming notebooks.
- `scripts/aio/aio-provision-cache.sh`: fills each book's `reference/cache/` from the recorded sources and verifies every SHA-256. It is idempotent and fails loudly on a mismatch.
- `[tool.uv.sources]` adds `torchvision = { index = "pytorch-cpu" }` beside torch.
- **Verify:** `uv lock` clean; `uv sync --group aio` succeeds; the provision script fills an empty cache and a second run is a no-op; the inventory grep finds no download missing from `artifacts.yaml`.

### Phase B — snapshot import (inline, scripted)
- `docs/history/aio-import/import-usaaio.py` (self-authored provenance, **outside** the usaaio archive and its inventory; `docs/` is not in `test_book_ids`' live set) performs design D3:
  1. **Step A:** for each path in `git -C ../usaaio ls-tree -r --name-only a20128f` (1,659 paths), write `git -C ../usaaio show a20128f:<path>` to its new home (the pinned tree, not the checkout's index or working files):
     - `book1/` → `aio-ml/`, `book2/` → `aio-dl/`;
     - `tools/` → `tools/aio/` (tests handled in Phase D), `tests/` → `tools/aio/tests/`;
     - `scripts/{verify-register.py,fetch-reference.sh,verify-clean-checkout.sh,verify-comment-only.py,build-pdf.sh,build-book.sh}` → `scripts/aio/`;
     - the live docs (design D3), with these exact destinations:
       `docs/unit-standards.md` → `aio-ml/docs/unit-standards.md`, `docs/mocktest-generation.md` → `aio-ml/docs/mocktest-generation.md`, `docs/curriculum-architecture.md` → `aio-ml/docs/curriculum-architecture.md`,
       `docs/curriculum-roadmap.md` → `aio-ml/docs/curriculum-roadmap.md`, `docs/audits/015-coverage-audit.md` → **`aio-ml/docs/coverage-audit.md`** (renamed, listed in the import report and admitted by the fidelity diff),
       `docs/audits/015-plan014-reconciliation.md` → `aio-ml/docs/015-plan014-reconciliation.md`;
     - every other `docs/` file → `docs/history/usaaio/` (read only), **except** `docs/proposals/.gitkeep` and `docs/reviews/.gitkeep` (dropped: empty placeholders with no content to archive or scan);
     - dropped, each listed in the import report: the D4 drops (historical-policy clock `.py`/`.sh` and tests, the one-off migration scripts and their tests, `verify-staged-scope.py`, `tests/fixtures/plan019-path-inventory.yaml`, `tests/test_plan031_guard.py`), `scripts/pre-merge-guard.sh`, `scripts/ci-local.sh`, `output/README.md` (py4kids has its own), and the root `AGENTS.md`/`CLAUDE.md`/`TODO.md`/`books.yaml`/`pyproject.toml`/`uv.lock`/`.gitignore`.
  2. **Renames** (D3), one pass over the **live destinations only** (book roots, `tools/aio/`, `scripts/aio/`, the six live docs; **never the archive**, which stays byte-identical to `a20128f` apart from recorded overlap redactions), counted per rule.
     **The rules are the script's, refined by a dry run; the plan fixes the acceptance outcomes, not the regexes.** The starting rule set (from the round-5 simulation, `scratchpad/r4sim/sim24.py`):
     qualified ids `(?<![\w-])book([12]):(?=\S)` (so `book2: Path` annotations are untouched); path segments `(?<![\w-])book([12])/`; output-name forms `(?<!\w)book([12])-` (so `wrong-book2-owner` is renamed);
     bare-value forms (YAML `book: book1`, the `imports.book` / `evidence_imports.book` keys in `aio-dl/syllabus.md`, table cells `| book1 |`, `**Book:** book1`); quoted literals (`'`, `"` and backtick, so "the `book1` folder" and the `reference/analysis.md` mentions rename); `--book book1`; the bridge file; `USAAIO_*`.
     **Step 0, dry run** (in the scratchpad, before anything is written to the repo), then the commit is allowed only when **all** of these hold on the transformed live set:
     (a) `tests/test_book_ids.py`'s patterns (book-name rule exempted per Phase C) give **zero hits**;
     (b) every rewritten `.py` parses (`ast.parse`) and no `\w+aio-(ml|dl)[:/-]` was produced;
     (c) every remaining `\bbook[12]\b` token is listed in the import report with its disposition (e.g. `lambda book2:`, a fixture unit id such as `C1-book1`, or the inline test registries `{id: book1, number: 1, root: book1, …}` / `depends_on: [book1]` in the 8 files Phase D rewrites to the v2 schema, kept here pending that rewrite), and none is an id, path, output name or registry value;
     (d) every rule's hit count is in the report (dropped paths excluded from the dry run, so their counts do not pollute it).
     The full aio suite and checks (Phase D/E) then prove the renamed tree runs. Prose that names the old folder as a path (`front-matter/how-to-use.md`, "the `book1` folder") is renamed with the path rule and listed as an allowed fidelity edit. The rules include: `book1:` → `aio-ml:`, `book2:` → `aio-dl:` (qualified ids); **every `book1/` → `aio-ml/` and `book2/` → `aio-dl/` path segment, whatever follows** (`book1/units` in 321 aio-dl notebooks, `book1/front-matter`, `book1/reference`, `book2/mocktests` in r2-001 and `blueprint.yaml`, `book2/reference`, and the live docs), so `test_book_ids`' path-segment rule holds;
     `book1-` → `aio-ml-` and `book2-` → `aio-dl-` (output and fixture names such as `book2-student.pdf`, `book1-teacher-vol2`, `wrong-book2-owner`, `book2-unit`; `test_book_ids`' case-insensitive "old output name" rule);
     `--book book1` → `--book aio-ml` and `--book book2` → `--book aio-dl` (incl. both `reference/analysis.md` files; the "CLI value" rule);
     `00-book1-bridge.ipynb` → `00-aio-ml-bridge.ipynb` (file renamed in all six units B2-019…B2-024, ~105 references);
     `"book1"`/`"book2"` and `book1/`/`book2/` literals in tools, tests and fixtures (incl. `tests/fixtures/two-books-valid/book1/` → `aio-ml/`); `USAAIO_*` → `AIO_*`. "Book 1"/"Book 2" prose is not renamed.
  3. Writes `docs/history/aio-import/import-report.md`: per-rule before/after counts, every dropped path with its reason, every renamed path, and the list of every changed file.
     It also writes the **archive inventory** (every file under `docs/history/usaaio/` and its extension), which the archive scan must cover in full.
- `aio-ml/IMPORTED.md`, `aio-dl/IMPORTED.md`: source repo, SHA, date, and a pointer to the report (prose says "usaaio `book1` id", never the path spelling).
- `.gitignore`: usaaio's rules with the roots renamed (`reference/*` except `.gitkeep`/`analysis.md`, `reference/cache/`, the two hidden sets, the five C11 CSV rules, `build/` dirs).
- **Step B (local only):** `scripts/aio/fetch-reference.sh --all` for the past papers, and `aio-provision-cache.sh` for the artifacts.
  The two hidden sets are **not provisioned**: they exist in no checkout and are regenerated by their seeded scripts (`18-C11-competition-craft/data/make_dataset.py --with-test`, `mocktests/r1-001/data/gen_p09.py`) only when grading; usaaio CI passes without them, and so does this one. They stay git-ignored.
- **Every overlap gate in this plan** (Phase A pre-import and whole-import-set scans, the Phase D archive scan, the Phase F scans) requires a non-skipped PASS **and** zero corpus extraction failures, with expected-versus-extracted corpus parts reconciled in its report; the ported `overlap-scan --require-corpus` enforces the same (any extraction warning fails it), with a test.
- **Archive overlap scan:** the archive is staged **outside the repository** (`/dev/shm/aio-archive/`; volatile, so `import-usaaio.py --archive-only` regenerates it from `a20128f` and Phase D scans a fresh regeneration) in Phase B and copied into `docs/history/usaaio/` only after Phase D's archive-mode scan has passed over the staged copy with the corpus present (Phase D's last step); a hit is redacted in the staged copy, and the redaction is listed in the import report.
  The book roots and tools are committed in Phase B only because the pre-import scan (Phase A) already passed over both books.
- The import script and report are committed **with** Phase B's import commit (they are its provenance); only the staged archive waits for Phase D.
- **Verify:** the import report's counts; zero `book1`/`book2` id or path-segment spellings in the **contents** of `test_book_ids`' live set (aio roots, `tools/`, `tests/`, `scripts/`; the repo-root legacy `book1/` runtime folder and the `docs/history/` trees are out of scope); every archive-inventory file has a scannable extension; `git status --ignored` shows the step-B files ignored; `git ls-files` contains none of them.

### Phase C — registry
- `books.yaml`: `aio-ml` (number 4, `aio_round: 1`, `depends_on: []`) and `aio-dl` (number 4, `aio_round: 2`, `depends_on: [aio-ml]`), both `content_model: aio` and `dependency_group: aio`, titles and subtitles unchanged (design D1).
  The header comment documents `content_model` and `aio_round`. No `publication` and no `site` yet.
- `tools/books.py`: `content_model(id)` (default `py4kids`), `aio_round(id)`, `books_with_content_model(model)`.
  Registry validation (ci-local step 1): `content_model` ∈ {py4kids, aio}; `aio_round` required on aio books and rejected elsewhere; `judge`/`patterns`/`acsl`/`labs` rejected on aio books.
- **All-book iterations filter to the py4kids model:** `tools/curriculum.py` cross-book uniqueness, peers and variants (~line 122), `known_baseline` walks, `publication_config` callers, `tools/guard.py` per-root layout rules, and every other `books.yaml` loop in `tools/`
  (the phase lists each site it changes).
- `tests/test_books.py`: the new ids, flag sets, `content_model`/`aio_round` documented and read; the `projects/`+`checkpoints/` layout assertion and the site `classification == "confirmed"` assertion keyed on `content_model`.
- `tests/test_book_ids.py`: the `"book name"` rule exempts aio roots, `tools/aio/` and `scripts/aio/`; the id rules stay in force everywhere; `tools/aio/` and `scripts/aio/` are added to its scan.
- **Verify** (the roots exist from Phase B, so ci-local step 1's `root` check and `test_book_ids`' live-files check hold): `uv run pytest -q tests/test_books.py tests/test_book_ids.py` passes; step 1 of ci-local passes and rejects a hand-made bad entry (each rejection rule tested).
  Until Phase E routes the steps, the branch's later ci-local steps are expected to fail on aio books; Phases C–D verify with targeted commands only.

### Phase D — `tools/aio/` port (Opus subagent)
- Make `tools/aio/` an importable subpackage (`from tools.aio.checks import …`); rewrite usaaio's absolute imports (`tools.X` → `tools.aio.X`).
- **Catalog adapter:** usaaio `tools/books.py` loads py4kids `books.yaml` v2 and keeps only `content_model: aio` books, mapping `BookSpec.number := aio_round`; the v1 loader is removed. Its required-root-files list is unchanged.
- **Id-literal branches → registry data** (design D1 inventory): `schedule.py:164-166`, `model.py:431,570` (`book: 2` stays a manifest field, compared against `aio_round`), `audit_curriculum.py:329`, `scope.py:1259`, `render_curriculum_roadmap.py:405-408,517`, the three mutation verifiers' `--root` selection.
  The phase ships the full grep (`number`, `book1`, `book2`, `book: 2`) with each hit's disposition in its commit message.
- **Paths:** `render_curriculum_roadmap.py` targets become `aio-ml/docs/curriculum-roadmap.md` and `aio-ml/docs/coverage-audit.md`; `scope.py`'s reconciliation read points at `aio-ml/docs/015-plan014-reconciliation.md`, and its usaaio-history ancestry probe (`git merge-base --is-ancestor b486d72`) is removed (D3).
  Notebooks find their root by `AIO_BOOK_ROOT` or the `syllabus.md` + `curriculum/` walk-up (unchanged); `uv run --project ..` in exec becomes the py4kids root.
- **CLI:** `py4kids-tools aio …` delegates to `tools.aio.cli.main` (usaaio's own `--book <id>` / `--all` grammar, unchanged), so there is one console script.
  It is a **pre-argparse intercept** in `tools/cli.py` `main` (`argv = sys.argv[1:] if argv is None else argv`, then `if argv[:1] == ["aio"]: return tools.aio.cli.main(argv[1:])`) with a **lazy import**, because the py4kids parser requires `--book` and constrains `check`, and the group-free test run imports `tools.cli` without the `aio` group. A test covers the delegate and the lazy import.
  The delegate **passes exit codes through unchanged** (3 stays 3). Phase E's ci-local tolerates 3, printing `SKIP (<reason>)`, exactly where usaaio's ci-local does (the per-book checks of its step 5 and `build-pdf.sh` in its step 8) and nowhere else,
  so `verify-register`, the `--all` aggregates and step-4b tools fail on 3, and every SKIP is visible to the F.1 table. `--require-corpus` turns the overlap scan's missing-corpus skip into a failure.
- **Overlap:** the ported command keeps its name, `overlap-scan`. `overlap-scan --require-corpus` fails on a missing corpus; `overlap-scan --require-corpus --paths <dir>` is the archive mode (the permanent, tested version of Phase A's scratch scan) (`.md`, `.yaml`/`.yml`, `.ipynb` markdown and code; fail closed on any other extension or parse error; usaaio thresholds), with a test that plants corpus text in an archived document.
- **Ported scripts in `scripts/aio/`:** their repo-root resolution moves one level up (`$(dirname "$0")/../..` in `build-pdf.sh:23`, `build-book.sh:47`, `fetch-reference.sh:9`; the same in `verify-register.py`, `verify-comment-only.py`, `verify-clean-checkout.sh`), and their `tools.X` imports become `tools.aio.X` (`build-pdf.sh:35`, `fetch-reference.sh:31,47`, `verify-register.py:25`, `verify-comment-only.py:40`). Each edit is listed for the fidelity diff.
- **`scripts/aio/verify-clean-checkout.sh` is rewritten** for py4kids: it `git clone`s the current branch into a fresh `/dev/shm` directory, runs step-B provisioning **into the clone** from sources outside it (`fetch-reference.sh --root <clone> --all` and `aio-provision-cache.sh --root <clone>`; nothing copied from the working tree),
  runs `ci-local.sh` there, and finally asserts `git -C <clone> status --porcelain --ignored` shows the provisioned files as ignored and none as tracked or untracked-unignored. `tests/test_clean_checkout.py` is rewritten to test that sequence (with stub provisioning).
- **Tests:** the 16 test and fixture files under `tests/` that build `books_version` registries (`fixtures/two-books-valid/books.yaml`, `publication_fixture.py`, `test_answerkey.py`, `test_api_comments.py`, `test_book_isolation.py`, `test_books.py`, `test_clean_checkout.py`, `test_integration.py`, `test_layer_boundary.py`, `test_model.py`, `test_plan031_guard.py`, `test_prereq_coverage.py`, `test_publication_config.py`, `test_schedule.py`, `test_tolerance.py`, `test_verify_register.py`):
  `test_plan031_guard.py` is dropped (D4); the other 15 are rewritten to the v2 schema + `content_model`/`aio_round` (each assertion kept).
- **ci-local- and dropped-script-coupled tests**, each dispositioned:

  | Test | Coupling | Disposition |
  |---|---|---|
  | `test_integration.py` (~24 refs) | reads and runs usaaio `scripts/ci-local.sh`, incl. `--registry-probe` / `--solution-probe` | the usaaio-ci-local assertions are rewritten against the py4kids `scripts/ci-local.sh` aio routing (Phase E), and `--registry-probe` / `--solution-probe` are ported as py4kids ci-local options for aio books; tests that only assert usaaio-ci-local text are dropped and listed |
  | `test_clean_checkout.py` (~22 refs) | imports `renumber-book1-units.py`, `verify-staged-scope.py`, `plan019-path-inventory.yaml` | those references are dropped with their targets; the clean-checkout sequence test is rewritten (above) |
  | any other test importing a dropped script or fixture | — | dropped with its target, listed |
  | `test_integration.py` module import of the dropped `renumber-book1-units.py` (`test_integration.py:32-45`) | the helper load and every test that uses it | dropped, each listed and counted in the parity table; the module's other tests stay |
  | `test_publication_config.py:79` | expects the `f"{book.id}: …"` label `"book1: not a publication book…"` | expectation follows the renamed id, counted |
  | `test_ci_scope.py:38,43,53` | expects `"full book1"`-style route strings built from `book.id` | expectations follow the renamed ids (a D3 rename of the expected strings), counted |
  | the six step-7 content tests that read `scripts/ci-local.sh` text (`test_latent_model_checks.py:34`, `test_capstone_checks.py:37`, `test_generative_model_checks.py:39`, `test_language_transformer_checks.py:14`, `test_vision_transformer_checks.py:17`, `test_b2_024_statements.py:549`) | assert usaaio ci-local wiring | rewritten against the py4kids ci-local aio routing (Phase E), or dropped and listed where they assert only usaaio text |

- **Mechanical path dispositions** (listed for the fidelity diff): the 46 tests that set `ROOT = Path(__file__).resolve().parents[1]` use a shared `ROOT` from `tools/aio/tests/conftest.py` (the py4kids repo root, `parents[3]`);
  `tools/aio/publish.py:1294` and `tools/aio/publish_output.py:75` default `--root` to `parents[2]`; `ROOT/"scripts"/…` references (`test_book_isolation.py` running `build-pdf.sh` and `fetch-reference.sh`) become `scripts/aio/…`;
  `overlap.py`'s skip hint names `scripts/aio/fetch-reference.sh`, with `test_overlap.py:101,352` updated.
  Every other test moves unchanged apart from the D3 renames.
  usaaio `tests/conftest.py` is **retained** as `tools/aio/tests/conftest.py` (its `deferred_policy_window` clock fixture is still used by the kept `test_b2_019_statements.py` / `test_b2_020_statements.py`; D4 drops only `verify_historical_deferred_policy` and its tests), and gains the root setting. The six step-7 content tests are part of the suite.
- **Guard:** `tools/guard.py` gains the aio unit-id (`NN-<code>-…`, `B2-0NN-…`) and mock-test-id (`rN-NNN`) collision rules and the D3 ignored paths as tracked-path refusals, with tests in `tests/`.
- ruff passes on `tools/aio/` and `scripts/aio/` with the repo config (mechanical fixes only, listed).
- **Verify:** `uv run --group aio pytest -q tools/aio/tests` passes with the source test count minus the D4 drops minus the listed coupled-test drops (the phase reports every number); the group-free `uv run pytest -q` collects no aio test; ruff clean.

### Phase E — ci-local routing (Opus subagent)
Route `scripts/ci-local.sh` per design D2's table, each row pinned to a line:
- step 1: `content_model`/`aio_round` read on their own line, like `dependency_group`; validation per Phase C;
- step 2: one routed `uv run --group aio pytest -q tools/aio/tests` when any aio book exists; the per-book `pytest -q <book>` loop skips aio books;
- step 3: aio books skip every py4kids step-3 command and run aio notebook exec and aio hygiene. Exec is usaaio step 3 ported verbatim (solutions, practice solutions, mock-test solutions, then lessons; the per-unit 20 s `timeout` list for aio-dl practice and r2-001 solutions),
  with the command `cd <book root> && AIO_BOOK_ROOT=… uv run --project .. --group aio jupyter execute …` (`..` already resolves to the py4kids root);
- step 4: aio books skip manifest/prereq/coverage/concept-scan/stretch and the turtle checks, and run the aio per-book checks, the aio all-books checks, `verify-register` (the `aio_round: 1` book; its `book.number != 1` guard, `verify-register.py:314`, works through the adapter's `number := aio_round`, and its test asserts that mapping since py4kids `number` is 4 for both books), and step 4b (`audit_curriculum --check`, `render_course_structure --check` per book, `render_curriculum_roadmap --check`, the three mutation verifiers);
- step 5: aio books skip `build-pdf.sh` and run `scripts/aio/build-pdf.sh` (syllabus, handouts, mock-test papers and solutions) through the group, exit 3 → SKIP when the toolchain is absent (as in usaaio);
- `--all-books` additionally runs `overlap-scan --require-corpus` for each aio book.
- **CI budget (D9):** time each aio stage. If the full aio run exceeds 60 CI-minutes, aio exec on ordinary branches is scoped by `tools/aio/ci_scope.py` to changed aio paths, and `--all-books` runs it in full; otherwise no scoping is added. The measurement is recorded in the post-execution report.
- **Verify:** ci-local green; a branch touching only a py4kids book runs no aio exec only if scoping was added (else full); a deliberately broken aio practice solution fails step 3 (reverted).

### Phase F — verification (named)
1. **Parity table** (in this plan's post-execution report): every usaaio `ci-local.sh` gate (steps 1–9, each check and test file) → its py4kids command, with the outcome at usaaio `a20128f` beside the outcome here.
   The usaaio side runs in a **fresh clone of usaaio at `a20128f` under `/dev/shm`** with its own provisioning (never in `../usaaio`, which stays untouched).
   Every row matches or carries one of these listed justification classes: (a) a D4 drop (historical-policy clock, one-off migration scripts, `verify-staged-scope`, `test_plan031_guard`); (b) the removed usaaio-history ancestry probe;
   (c) a listed coupled-test drop (Phase D); (d) **deferred to aio-002**: usaaio step 8's edition builds (`build-book.sh` + `publish_audit`), since `publication` is not yet set; (e) **replaced**: usaaio step 9 `pre-merge-guard.sh` by the py4kids guard with the aio rules.
2. **Clean checkout:** `git clone` of this branch into `/dev/shm`, step B provisioning, then `TMPDIR=/dev/shm bash scripts/ci-local.sh` green. (`scripts/aio/verify-clean-checkout.sh` drives it.)
3. **Fidelity diff:** every imported file compared with its usaaio source after reversing the recorded renames; the only differences allowed are the D3 renames and the Phase D tool edits (listed per file).
4. **Leak assertions:** `git ls-files aio-ml aio-dl tools/aio` contains no path under `*/reference/` other than `.gitkeep`/`analysis.md` (the fixture's `.gitkeep` included), no hidden set and no cache file (the py4kids books' own `reference/` files are out of scope); `pre-merge-guard.sh --pr` OK; `overlap-scan --require-corpus` over both books and over `docs/history/usaaio/` passes.
5. **py4kids unchanged:** step 3–6 results for the six existing books identical to `main` (same PASS lines, same counts).
6. **Rename proof:** `tests/test_book_ids.py` passes; the zero-hit id grep.

## Deviations from design names (recorded)
- The CLI shape: design D4 named `py4kids-tools --book <aio-id> <command>` and `--content-model aio <all-books-command>`. Because `--book` is required by the py4kids parser and usaaio's CLI already has `--book`/`--all`,
  the plan uses one delegate, `py4kids-tools aio --book <id> <check>` / `py4kids-tools aio --all <check>`. Same dispatch point, no second console script.
- The artifact inventory lives at `aio-ml/curriculum/artifacts.yaml` (design D8 named only the provisioning script).

## Out of scope (verification-phase exemption)
No new units, mock tests or other content ship: this is a migration, and Phase F is its verification (fidelity and parity, per design §4).
Also out of scope: `publication` and editions (aio-002), `site` and the export adapter (aio-003), classification (aio-004/005), committed artifact subsets (follow-up), any change to `../usaaio`.

## Plan Review

### Round 1 (v1, scratch draft)

- **[self]** MUST — F.1 ran usaaio CI "there", which writes into `../usaaio` → **[FIXED]** F.1 runs it in a fresh `/dev/shm` clone.
- **[sol] REJECT.**
  1. BLOCKER archive scan fails on `docs/proposals/.gitkeep`, `docs/reviews/.gitkeep` → **[FIXED]** Phase B drops both placeholders; archive inventory must be fully scannable.
  2. MUST clean-checkout driver unspecified → **[FIXED]** Phase D rewrite of `verify-clean-checkout.sh` + its test.
  3. MUST coverage-audit destination contradictory → **[FIXED]** Phase B names `aio-ml/docs/coverage-audit.md`.
  4. NIT pin the snapshot; test count → **[FIXED]** `ls-tree`/`git show` at `a20128f`; the 16 files are listed (both reviewers undercounted: `git grep -c books_version a20128f -- tests` gives 16), one dropped, 15 rewritten.
- **[fable] APPROVE WITH NITS.**
  1. MUST ci-local-coupled tests → **[FIXED]** Phase D disposition table; probes ported.
  2. MUST path-segment rename too narrow → **[FIXED]** every `book1/`/`book2/` segment renamed.
  3. MUST hidden sets not in any checkout → **[FIXED]** Phase B: not provisioned; regenerated only for grading.
  4. MUST `scripts/aio/` root resolution and imports → **[FIXED]** Phase D edits listed.
  5. MUST Phase B verification before import → **[FIXED]** import is now Phase B, registry Phase C.
  6. MUST parity justification classes → **[FIXED]** F.1 classes (a)–(e).
  7. NIT count → see sol 4.
  8. NIT CLI intercept + lazy import → **[FIXED]** Phase D.
  9. NIT `output/README.md` → **[FIXED]** dropped, listed.
  10. NIT exec command → **[FIXED]** Phase E.
  11. NIT `torchvision` source → **[FIXED]** Phase A.

### Round 2 (v2, scratch draft)

- **[sol] REJECT.** Round-1 items verified resolved.
  1. BLOCKER book content committed before its overlap scan → **[FIXED]** Phase A pre-import scan of both books in the `/dev/shm` usaaio clone; the archive is staged outside the repo until Phase D's scan passes.
  2. MUST artifact grep searched the SHA as text → **[FIXED]** Phase A pattern with `a20128f` as the tree argument.
- **[fable] APPROVE WITH NITS.** All round-1 dispositions and counts verified.
  1. MUST archive scan fails on the import script's `.py` → **[FIXED]** script and report live in `docs/history/aio-import/`, outside the archive inventory.
  2. MUST F.4 `reference/` assertion hits py4kids books' own files → **[FIXED]** scoped to aio roots and `tools/aio`.
  3. MUST global exit-3 → SKIP relaxes parity → **[FIXED]** delegate passes codes through; ci-local tolerates 3 only where usaaio does.
  4. NIT bridge units B2-019…B2-024 → **[FIXED]**.
  5. NIT Phase reference → **[FIXED]**.
  6. NIT `conftest.py` retained → **[FIXED]**.
  7. NIT zero-hit grep vs legacy `book1/` folder → **[FIXED]** contents of the live set only.
  8. NIT `argv is None` → **[FIXED]**.
  9. NIT provenance commit timing → **[FIXED]** committed with Phase B.

### Round 3 (v2.2, scratch draft)

- **[sol] REJECT.** Round-2 items verified resolved.
  1. BLOCKER the six live docs escaped every pre-commit scan → **[FIXED]** Phase A whole-import-set scan (every destination file, fail closed on unlisted unscanned files).
  2. MUST command is `overlap-scan`, not `overlap` → **[FIXED]** everywhere; the ported flags attach to `overlap-scan`.
  3. MUST `git show` needs `-C ../usaaio` → **[FIXED]**.
- **[fable] APPROVE WITH NITS.** Round-2 dispositions verified.
  1. MUST `Book[12]-` and `--book book[12]` patterns trip in the live set → **[FIXED]** Phase B rename rules `book1-`/`book2-` and `--book book1`/`book2`.
  2. MUST live docs never scanned → **[FIXED]** by the v2.3 whole-import-set scan (sol 1).
  3. NIT command name → **[FIXED]** (sol 2).
  4. NIT volatile staging → **[FIXED]** `--archive-only` regeneration.
  5. NIT `verify-register` number guard → **[FIXED]** Phase E note + test assertion.

### Round 4 (v2.3, scratch draft)

- **[sol] REJECT.** Round-3 items verified resolved.
  1. MUST renames would rewrite the read-only archive → **[FIXED]** Phase B: renames on live destinations only; archive byte-identical apart from recorded redactions.
  2. MUST scanner tolerates corpus extraction failures → **[FIXED]** Phase A: zero extraction failures, expected vs extracted parts reported, for both scans.
- **[fable] APPROVE WITH NITS.** Rename simulation over the pinned tree: 0 `test_book_ids` hits in the live set.
  1. MUST substring `book2:` rename corrupts identifiers → **[FIXED]** left-boundary rules, produced-pattern assertion, `ast.parse` of every rewritten `.py`.
  2. MUST test root depth and script paths → **[FIXED]** Phase D mechanical path dispositions; the six ci-local-text tests join the coupled-test table.
  3. NIT overlap skip hint path → **[FIXED]**.
  4. NIT cite rule by name → **[FIXED]**.

### Round 5 (v2.4, scratch draft)

- **[sol] REJECT.**
  1. MUST later overlap gates could pass with extraction failures → **[FIXED]** one rule for every overlap gate, enforced by `--require-corpus`.
  2. MUST `wrong-book2-owner` unmatched → **[FIXED]** output-name rule `(?<!\w)`; outcome (a).
  3. MUST `test_integration.py` loads the dropped renumber script at import → **[FIXED]** coupled-test row.
- **[fable] APPROVE WITH NITS.** Simulation: 0 produced `\w+aio-` patterns; round-4 items resolved.
  1. MUST `book2: Path` annotations → **[FIXED]** qualified-id rule requires a non-space after the colon; outcome (b).
  2. MUST hyphen lookbehind → **[FIXED]** (sol 2).
  3. MUST bare `book: book1` values and table cells → **[FIXED]** bare-value rules; outcome (c).
  4. NIT `test_ci_scope.py` → **[FIXED]** coupled-test row.
  5. NIT `how-to-use.md` folder prose → **[FIXED]** allowed fidelity edit.
- **[self]** The regex list kept growing round by round; v2.5 makes the rename **outcome-gated** (dry run + acceptance (a)–(d)), so a missed form fails before commit instead of needing another review round.

### Round 6 (v2.5): CONSENSUS

- **[sol] APPROVE.** Round-5 items verified resolved; no new plan-level defects.
- **[fable] APPROVE WITH NITS.** Simulation (`scratchpad/r4sim/sim25.py`) over `a20128f`: 1,605 live files, 493 changed; 0 `test_book_ids` hits, 0 produced `\w+aio-` patterns, 0 parse failures.
  1. NIT inline test registries vs outcome (c) → **[FIXED]** kept pending Phase D's rewrite.
  2. NIT backtick literals → **[FIXED]** quoted-literal rule names backticks.
  3. NIT `test_publication_config.py:79` label → **[FIXED]** coupled-test row.
  4. NIT (c)'s example → **[FIXED]**.
  5. NIT dropped paths in the dry run → **[FIXED]** excluded.
- **[self] APPROVE.**

**Plan-review outcome: CONSENSUS on v2.6** — [self] APPROVE · [sol] APPROVE · [fable] APPROVE WITH NITS (folded). The gate is approval to implement.

## Content Review

Duty: fidelity (design §4) plus conventional review of the tooling changes, with the aio reading of `docs/content-review-gate.md` (duty 9: no past papers).

### Review 1 — [self] (2026-11-01)
- **Verdict**: APPROVE
- Checked: the aio per-book and all-books check lists in `scripts/ci-local.sh` match usaaio `a20128f` lines 123–133 verbatim, and exit 3 is tolerated only where usaaio tolerated it (per-book checks, hygiene, PDFs).
  `tools/guard.py` refuses tracked aio `reference/*` and the seven local-only grading files, keyed on `content_model: aio`.
  `route_exec` sends a book `full` on any change outside `units/<x>/` and `mocktests/<x>/`; a code-cell scan of both books found no reference to another unit, mock test or book, so `scoped` is sound.
  The only `git ls-files` hits on token/secret names are lesson titles (`01-train-token-embeddings`, `unit-06-secret-codes`).
  The report records both environment caveats (the usaaio branch mirror, the roar sync).
  No findings.

### Review 1 — [sol] (2026-11-01)
- **Verdict**: APPROVE (GPT-6, `--model gpt-6-sol`)
- No findings.

### Review 1 — [fable] (2026-11-01)
- **Verdict**: APPROVE WITH NITS
- Independently re-ran the import dry-run (report byte-identical; 1,501 identical / 91 differing = `classify.tsv`; 0 notebooks differ), the archive comparison (44/44), the leak and guard checks, the junit per-file recount, and read-only aio and group-free test subsets.
1. `[FIXED]` `tools/aio/ci_scope.py:261`: the exec-scoping invariant (no aio code cell reads another unit's, mock test's or book's files) holds but is unenforced. Priority: Nice to Have.
   → Response: added `tools/aio/tests/test_exec_isolation.py`, which scans every code cell of every registered aio book and fails on any such reference.
2. `[WONTFIX]` `docs/history/aio-import/import-usaaio.py:240`: the "Renamed paths" list is sliced `[:0]`, so `import-report.md` records per-root move counts and the special renames, not every renamed path as Phase B worded it. Priority: Nice to Have.
   → Response: the script is the recorded import tool whose byte-for-byte reproducibility is fidelity evidence; it stays as run. The per-root counts plus the full "Changed files" list make every rename auditable; the wording difference is recorded under Deviations below.
3. `[FIXED]` `.gitignore:117`: `build/aio-outputs/` is already covered by `build/` and belongs to aio-003's export cache. Priority: Nice to Have.
   → Response: removed; aio-003 adds what its cache needs.

Consensus: all three APPROVE / APPROVE WITH NITS; no `[OPEN]` items.

## Post-Execution Report

**Draft (Phase F).** Branch `feature/aio-001-import`, rebased onto `main` 927d5f51.
Phase F ran against b752070f (tree-identical to 1554c100, whose full ci-local run 4 was ALL GREEN) and added one port fix, 025f499d (F.1 below).
Evidence lives in the session scratchpad (`aio001/`): `usaaio-ci.log`, `usaaio-junit.xml`, `py4kids-aio-junit.xml`, `junit-parity.md`, `ci-full-run4.log`, `clean-checkout.log`, `fid/`, `F5/`, `F4-overlap-*.txt`, `F6-id-grep.txt`.

### F.1 Parity table

The usaaio side ran in a fresh clone of usaaio at `a20128f` under `/dev/shm/usaaio-a20128f` (`../usaaio` was only read).
It was provisioned per usaaio's own instructions: `uv sync` by `uv run`, and `scripts/fetch-reference.sh --all` for the 2026 papers.
Then `TMPDIR=/dev/shm bash scripts/ci-local.sh` ran: **`ci-local: ALL GREEN`, 139 min** (`usaaio-ci.log`).
The first attempt (`usaaio-ci-attempt1.log`) failed one test, `test_integration.py::test_plan019_cutover_ignores_exact_plan022_three_blob_worktree_change`.
That test `git clone --no-local`s the repository and needs commit `4cc3894`.
The commit is on the local branch `feature/plan-019-attention-transformers` in `../usaaio`, but a plain clone carries it only as a remote-tracking ref.
So the clone's local branches were mirrored from `../usaaio`'s `refs/heads` (19 refs, HEAD still detached at `a20128f`, tree clean), and the test passed.
This is a usaaio fresh-clone hazard; the test is a D4 drop here (class a).
The py4kids side is ci-local run 4 (`ci-full-run4.log`, tree-identical to b752070f), plus a junit run of the aio suite at b752070f.

| usaaio ci-local gate (a20128f) | usaaio outcome | py4kids command | py4kids outcome | Match / class |
|---|---|---|---|---|
| 1 registry (`load_book_catalog`, `validate_book_root`) | PASS `registry: book1 -> book2` | step 1 aio catalog adapter + root validation; `content_model`/`aio_round` validation | PASS `aio registry: aio-ml (aio_round 1) -> aio-dl (aio_round 2)` | match |
| 1 `ruff check tools/ tests/` | PASS | step 1 `uv run ruff check tools/ tests/ scripts/ …` (covers `tools/aio/`, `scripts/aio/`) | PASS | match |
| 2 `uv run pytest -q` | 1856 passed | step 2 `uv run --group aio pytest -q tools/aio/tests` | 1781 passed, 1 skipped (b752070f); 1782 passed after 025f499d | per-file table below |
| 3 solution, practice-solution, mock-test-solution and lesson exec (20 s list) | PASS, 751 notebooks | step 3 aio exec, `cd <root> && AIO_BOOK_ROOT=… uv run --project .. --group aio jupyter execute` (route `full` on this branch) | PASS, 751 notebooks | match |
| (no usaaio gate) | — | step 3 aio `hygiene-check` per book | PASS ×2 | moved from usaaio step 5 (deviation below) |
| 4 `verify-register.py --book book1` | PASS 437/437 | step 4 `scripts/aio/verify-register.py --book aio-ml` | PASS 437/437 | match |
| 5 per-book checks ×12 × 2 books (prereq, coverage, scope, schedule, tolerance, hygiene, blueprint, overlap-scan, answerkey, layer-boundary, unit-order, api-comments) | 24 PASS, 0 SKIP | step 4 `py4kids-tools aio --book <id> <check>` (11 checks; hygiene in step 3) | 22 PASS + hygiene 2 PASS, 0 SKIP | match |
| 6 `--all` prereq, scope, schedule | 6 PASS | step 4 `py4kids-tools aio --all <check>` | 6 PASS | match |
| 7 `audit_curriculum --check` ×2 | PASS ×2 | step 4b same | PASS ×2 | match |
| 7 `render_curriculum_roadmap --check`, `render_course_structure --check` ×2 | PASS (silent) | step 4b same (targets `aio-ml/docs/…`) | PASS (silent) | match |
| 7 training / classical / attention mutation verifiers | 5/5, 5/5, 5/5 (+ untouched 5/5) | step 4b same via `--repo-root` | 5/5, 5/5, 5/5 (+ untouched 5/5) | match |
| 7 `pytest -q` language-transformer, latent, generative, capstone, vision-transformer, r2-001 checks | 20, 34, 46, 50, 52, 13 passed | step 2 aio suite (same files; no second run) | 20, 34, 46, 50, 52, 13 passed | match (run once, in step 2) |
| 8 `build-pdf.sh` per book | 22 + 9 PDFs | step 5 `scripts/aio/build-pdf.sh --book <id>` | 22 + 9 PDFs | match |
| 8 `build-book.sh` + `publish_audit` (ci_scope edition routes) | INFO unchanged (change-routed) ×2 | — | not run | (d) deferred to aio-002 |
| 9 `pre-merge-guard.sh` | OK | step 7 py4kids `scripts/pre-merge-guard.sh` with the aio rules | OK | (e) replaced |
| `--all-books` overlap (usaaio: in step 5) | PASS | `--all-books` `overlap-scan --require-corpus` per aio book | PASS ×2, 0 extraction failures (F.4) | match |

**Step 2 per test file** (junit, usaaio clone at a20128f vs py4kids `tools/aio/tests` at b752070f):

| test file | usaaio a20128f | py4kids | Δ |
|---|---|---|---|
| `test_answerkey.py` | 9 passed | 9 passed | +0 |
| `test_api_comments.py` | 40 passed | 40 passed | +0 |
| `test_attention_mutations.py` | 10 passed | 10 passed | +0 |
| `test_audit_curriculum.py` | 36 passed | 35 passed | -1 |
| `test_b2_019_statements.py` | 134 passed | 134 passed | +0 |
| `test_b2_020_statements.py` | 22 passed | 22 passed | +0 |
| `test_b2_021_plan.py` | 4 passed | 4 passed | +0 |
| `test_b2_021_statements.py` | 19 passed | 19 passed | +0 |
| `test_b2_022_plan.py` | 13 passed | 13 passed | +0 |
| `test_b2_022_statements.py` | 17 passed | 17 passed | +0 |
| `test_b2_023_plan.py` | 13 passed | 13 passed | +0 |
| `test_b2_023_statements.py` | 17 passed | 17 passed | +0 |
| `test_b2_024_plan.py` | 13 passed | 13 passed | +0 |
| `test_b2_024_statements.py` | 18 passed | 18 passed | +0 |
| `test_blueprint.py` | 21 passed | 21 passed | +0 |
| `test_blueprint_book2.py` | 40 passed | 40 passed | +0 |
| `test_book2_schedule.py` | 79 passed | 79 passed | +0 |
| `test_book_isolation.py` | 14 passed | 14 passed | +0 |
| `test_books.py` | 41 passed | 41 passed | +0 |
| `test_c12_solution_regressions.py` | 123 passed | 123 passed | +0 |
| `test_c12_statement_contracts.py` | 12 passed | 12 passed | +0 |
| `test_c8_solution_regressions.py` | 18 passed | 18 passed | +0 |
| `test_capstone_checks.py` | 50 passed | 50 passed | +0 |
| `test_ci_scope.py` | 11 passed | 16 passed | +5 |
| `test_classical_mutations.py` | 9 passed | 9 passed | +0 |
| `test_clean_checkout.py` | 136 passed | 109 passed | -27 |
| `test_cli.py` | 7 passed | 7 passed | +0 |
| `test_compute_policy.py` | 16 passed | 16 passed | +0 |
| `test_generative_model_checks.py` | 46 passed | 46 passed | +0 |
| `test_historical_deferred_policy.py` | 2 passed | — | -2 |
| `test_hygiene.py` | 8 passed | 8 passed | +0 |
| `test_integration.py` | 61 passed | 34 passed | -27 |
| `test_language_transformer_checks.py` | 20 passed | 20 passed | +0 |
| `test_latent_model_checks.py` | 34 passed | 34 passed | +0 |
| `test_layer_boundary.py` | 22 passed | 22 passed | +0 |
| `test_model.py` | 53 passed | 53 passed | +0 |
| `test_mutation_repo_root.py` | — | 9 passed | +9 |
| `test_new_mocktest.py` | 8 passed | 8 passed | +0 |
| `test_new_mocktest_book2.py` | 7 passed | 7 passed | +0 |
| `test_overlap.py` | 22 passed | 22 passed | +0 |
| `test_overlap_modes.py` | — | 12 passed | +12 |
| `test_plan031_guard.py` | 3 passed | — | -3 |
| `test_prereq_coverage.py` | 35 passed | 35 passed | +0 |
| `test_publication_config.py` | 30 passed | 29 passed | -1 |
| `test_publish.py` | 35 passed | 35 passed | +0 |
| `test_publish_audit.py` | 30 passed | 30 passed | +0 |
| `test_publish_theme_tables.py` | 10 passed | 9 passed 1 skipped | +0 |
| `test_r2_001.py` | 22 passed | 22 passed | +0 |
| `test_r2_001_checks.py` | 13 passed | 13 passed | +0 |
| `test_reference_migration.py` | 9 passed | — | -9 |
| `test_renumber_book1_units.py` | 26 passed | — | -26 |
| `test_schedule.py` | 60 passed | 60 passed | +0 |
| `test_scope.py` | 170 passed | 165 passed | -5 |
| `test_tolerance.py` | 30 passed | 30 passed | +0 |
| `test_training_mutations.py` | 13 passed | 13 passed | +0 |
| `test_unit_order.py` | 20 passed | 20 passed | +0 |
| `test_verify_comment_only.py` | 22 passed | 22 passed | +0 |
| `test_verify_register.py` | 51 passed | 52 passed | +1 |
| `test_vision_transformer_checks.py` | 52 passed | 52 passed | +0 |
| **total** | 1856 passed | 1781 passed 1 skipped | -74 |

Every difference carries a class:
- `test_historical_deferred_policy.py` (−2), `test_reference_migration.py` (−9), `test_renumber_book1_units.py` (−26), `test_plan031_guard.py` (−3): **(a)** D4 drops.
- `test_scope.py` (−5 net: 6 ancestry-probe tests removed, 1 `test_plan014_merged_reconciliation_needs_no_git_history` added): **(b)** the removed usaaio-history ancestry probe.
- `test_integration.py` (−27 net: 29 cases of 18 test functions removed, which are the plan019/plan022 history tests and the usaaio `pre-merge-guard.sh` tests; 2 py4kids exec-routing tests added; the module's other Phase D drops were restored in Phase E): **(c)** listed coupled-test drops (Phase D), with the guard tests also **(e)**.
- `test_clean_checkout.py` (−27 net: 32 cases of 27 test functions removed, covering `verify-staged-scope.py`, `renumber-book1-units.py`, `plan019-path-inventory.yaml`, plan031 rename rules and usaaio ci-local's guard wiring; 5 added for the rewritten verifier): **(a)**/**(c)**.
- `test_audit_curriculum.py` (−1, `test_plan019_task3_scope_allows_both_shared_generated_outputs`, which asserts `verify-staged-scope` scope): **(a)**.
- `test_publication_config.py` (−1, `test_real_books_are_publication_books_with_valid_configs`; the aio books carry no `publication` yet): **(d)**.
- Added: `test_ci_scope.py` +5 (exec routing), `test_verify_register.py` +1 (`aio_round` mapping), `test_mutation_repo_root.py` +9, `test_overlap_modes.py` +12 (Phase D/E additions, no usaaio counterpart).
- `test_publish_theme_tables.py`: usaaio 10 PASS, py4kids at b752070f 9 PASS + **1 SKIP**.
  `test_outside_tables_only_the_global_dot_rule_changes` read the pre-Plan-033 filter from usaaio's git history (`git show 60b1247:tools/publish_theme/panels.lua`), which py4kids does not import.
  It fit none of (a)–(e) and silently dropped an assertion, so it was treated as a port bug and fixed in **025f499d**:
  the blob is pinned byte for byte as `tools/aio/tests/fixtures/panels-pre-plan033.lua` (sha256 `f33cd7e3…`) and the test reads it.
  After the fix the module is 10 PASS, and the suite has 0 skips.

### F.2 Clean checkout

`AIO_CLEAN_CHECKOUT_KEEP=1 TMPDIR=/dev/shm bash scripts/aio/verify-clean-checkout.sh` at b752070f: **`ci-local: ALL GREEN`, then `PASS verify-clean-checkout: b752070f…`**, 358 min (`clean-checkout.log`).
- The clone was `git clone`d into `/dev/shm/aio-clean-checkout.*`.
  `uv run --frozen` created a fresh `.venv` from `uv.lock`: this is the real `--frozen` path, run for real for the first time.
- Step B ran into the clone. `fetch-reference.sh --root <clone> --all` fetched the 4 2026 PDFs.
  `aio-provision-cache.sh --root <clone>` fetched 4 artifacts, each with its sha256 verified. That is 8 provisioned files.
- Results: group-free 2290 passed / 2 skipped; recsys 348; roar 636; aio suite 1781 passed / 1 skipped; aio exec `full` ×2, 751 notebooks; verify-register 437/437; mutation verifiers 5/5 ×3; aio PDFs 22 + 9; the four editions rendered; site built and tested; guard OK.
- After the run, `git status --porcelain --ignored` shows no tracked change and no untracked-unignored file.
  The provisioned trees are `!!` (ignored): `aio-ml/reference/r1-2026/`, `aio-ml/reference/cache/`, `aio-dl/reference/r2-2026/`.
- **Needed: `uv sync --frozen --group roar --inexact` before ci-local**, passed as `AIO_CLEAN_CHECKOUT_PROVISION='bash scripts/aio/aio-provision-cache.sh --root "$CLONE" && uv sync --frozen --group roar --inexact'`.
  The first attempt (`clean-checkout-attempt1.log`) failed step 2.
  `tests/test_labs.py::test_racekit_carla_like_is_not_the_simulator` runs a roar notebook that imports `racekit`.
  In a fresh venv, step 2's group-free `pytest -q` runs before the roar routed suite installs `racekit`, so the import fails.
  This is **pre-existing on `main`**: a fresh clone of 927d5f51 fails the same test the same way, and it is not aio-related.
  It is a follow-up for py4kids `main`, out of this plan's scope.
- 025f499d (one test file and one fixture, after this run) was verified separately: aio suite **1782 passed, 0 skipped**; `tests/test_book_ids.py` + `tests/test_guard.py` 18 passed; ruff clean.

### F.3 Fidelity diff

`import-usaaio.py --dry-run` regenerated the D3 transform of `a20128f` (`/dev/shm/aio-fid`).
Its import report is byte-identical to the committed `docs/history/aio-import/import-report.md`.
Each regenerated file was then compared with `git show HEAD:<path>` (`fid/fidelity.py`, `fid/fidelity.json`, `fid/classify.tsv`).
This applies the recorded renames forward, which is equivalent to reversing them.
- **Archive:** 44/44 files in `docs/history/usaaio/` byte-identical to `a20128f` (no redaction was needed).
- **Live set:** 1,592 files; **1,501 byte-identical** to the renamed source, every `.ipynb` among them (no notebook output changed).
  91 differ, all Phase D/E edits:
  - Book content (2): `aio-ml/curriculum/material-inventory.yaml`, `aio-dl/curriculum/material-inventory.yaml`.
    They differ only in regenerated `semantic_sha256` values (67 of 1,013 and 338 of 364), because the D3 renames changed the hashed text.
    With those values removed, the parsed YAML is equal, and `audit_curriculum --check` passes on both (Phase D part 1).
  - `tools.X` → `tools.aio.X` imports only (16): `checks/{answerkey,api_comments,blueprint,hygiene,layer_boundary,new_mocktest,tolerance,unit_order}.py`, `publish_audit.py`, `publish_pdf.py`, `render_course_structure.py`, `tests/test_{cli,hygiene,overlap,publish,publish_audit}.py`.
  - Ported scripts, repo root one level up (+ imports): `scripts/aio/{build-book.sh,build-pdf.sh,fetch-reference.sh,verify-register.py}`; `verify-comment-only.py` also takes its book roots from the registry.
    `verify-clean-checkout.sh` is rewritten (Phase D).
  - Id-literal branches → registry data (D1): `audit_curriculum.py`, `checks/coverage.py`, `model.py` (`ROUND2_AIO_ROUND`; `Report.notes` for the corpus reconciliation), `checks/schedule.py` (dispatch on `aio_round`), `verify_{training,classical,attention}_mutations.py` (`--repo-root` selects the book by `aio_round`).
  - Catalog adapter `books.py` (v2 registry, `content_model: aio`, `number := aio_round`); CLI `cli.py` (delegate, `--require-corpus`, `--paths`); `checks/overlap.py` (`--require-corpus`, corpus reconciliation, archive mode); `checks/scope.py` (reconciliation path `aio-ml/docs/`, ancestry probe removed, duplicate-evidence fix); `render_curriculum_roadmap.py` (targets `aio-ml/docs/curriculum-roadmap.md`, `aio-ml/docs/coverage-audit.md`); `ci_scope.py` (aio publisher's global inputs, exec routing `route_exec`); `publish.py`, `publish_output.py` (`--root` default `parents[2]`); `checks/prereq.py` (ruff import re-wrap).
  - Tests (61 files): shared `ROOT` from `conftest.py` (`parents[3]`) in place of `parents[1]`; v2 registries with `content_model`/`aio_round` (the 15 listed files); fixture and doc paths (`tools/aio/tests/fixtures/…`, `aio-ml/docs/…`); ci-local wiring assertions rewritten against the py4kids script (`ci_local_text.py`); the listed coupled-test drops; and two digests re-pinned to the renamed bytes (`test_attention_mutations.py`, `test_book2_schedule.py`).
    The book bytes these digests cover are the identical transform shown above.
- **Added with no usaaio source (7 + 1):** `aio-ml/IMPORTED.md`, `aio-dl/IMPORTED.md`, `aio-ml/curriculum/artifacts.yaml`, `scripts/aio/aio-provision-cache.sh`, `tools/aio/tests/{ci_local_text.py,test_mutation_repo_root.py,test_overlap_modes.py}`, and the 025f499d fixture `tools/aio/tests/fixtures/panels-pre-plan033.lua` (a usaaio blob from `60b1247`, verbatim).

### F.4 Leak assertions

- `git ls-files aio-ml aio-dl tools/aio` lists 6 `reference/` paths: `aio-{ml,dl}/reference/{.gitkeep,analysis.md}` and the fixture's two `.gitkeep`s. Nothing else.
- No hidden set is tracked: `git ls-files | grep heldout` is empty.
  The C11 `heldout.csv`, `r1-001/data/p09_heldout.csv` and the five C11 CSV rules are in `.gitignore`.
- No cache file is tracked: 0 paths match `cache/`, `__pycache__` or `*.pyc`.
  No tracked aio path is matched by an ignore rule.
- `bash scripts/pre-merge-guard.sh --pr` (with `GH_TOKEN`): `pre-merge-guard: OK`.
- `py4kids-tools aio --book aio-ml overlap-scan --require-corpus`: PASS.
  Corpus: PDF parts expected 1, extracted 1, index text parts 37, extraction failures 0.
  6 below-threshold similarity WARNINGs, the same scanner behaviour as usaaio.
- `--book aio-dl`: PASS. Corpus: expected 3, extracted 3, index text parts 26, extraction failures 0.
- `py4kids-tools aio --all overlap-scan --require-corpus --paths docs/history/usaaio`: PASS, files 44, scanned 44, corpus parts 67, 0 warnings.

### F.5 py4kids unchanged

Steps 3–6 of the `main`-tree run (`ci-gov.log`, 927d5f51) were compared with run 4, after normalizing paths and timings (`F5/full.diff`).
Every py4kids line of step 3, step 4 and step 5's `build-pdf` is identical: the same PASS lines, the same counts and the same PDFs.
The diff has two kinds of hunk only:
1. **Pure insertions of aio output:** the step-3 aio hygiene and exec block, the step-4 aio checks and 4b, and the step-5 aio `build-pdf` (22 + 9 PDFs).
   No py4kids line is removed or changed.
2. **Change-routed steps that flip from skip to run**, as expected, because the branch changes `tools/`, `scripts/`, `books.yaml`, `pyproject.toml` and `uv.lock`:
   - book editions for python-projects, python-concepts, usaco-bronze and acsl (`main`: skip; branch: rendered, `publish-audit: PASS`, 0 overfull hboxes);
   - step 6 site (`main`: skip; branch: built, exported, and its e2e and solver-parity suites passed, e.g. 314 solvers / 1409 cases with 0 mismatches).
   These are routing effects of `tools/ci_scope.py`, not result changes.

### F.6 Rename proof

- `uv run pytest -q tests/test_book_ids.py`: 7 passed.
- Zero-hit grep: `git grep -I -E` over `aio-ml aio-dl tools/aio scripts/aio` covers the path segment, `--book book[12]`, quoted id, qualified id, `book[12]-`/`book1b-` output names and `USAAIO_`. **0 hits** (`F6-id-grep.txt`).

### CI budget (D9, Phase E)

The full aio run measured **111.7 CI-minutes**: suite 32.2, hygiene 0.1, exec 72.1, checks 3.0, 4b 1.6, PDFs 2.7.
That is more than 60, so **exec scoping was added**: `tools/aio/ci_scope.py --exec` routes each book `full`, `scoped` or `none` on ordinary branches, and `--all-books` runs it in full.
An ordinary branch costs about 40 aio minutes when no aio exec input changed.
This branch routes `full`. Run 4 took 349.7 min end to end.

### Deviations (recorded)

- **Overlap archive mode:** an inline code span holding an import statement (`` `import numpy as np` ``) counts as boilerplate, as usaaio's `_without_boilerplate` already treats `import`/`from` lines.
  The staged archive's only hit was `plans/006-units-tranche-2.md:166`. The rule is archive-mode only and is tested.
- **`PYTHONDONTWRITEBYTECODE=1` around the aio exec loop:** without it, exec left `units/B2-02x-*/data/__pycache__` behind, and that failed the four cache-free inventory tests on a re-run.
  usaaio's CI only ever ran on a fresh tree.
- **Hygiene once, in step 3:** usaaio ran `hygiene-check` among the step-5 per-book checks. Here it runs before exec in step 3 and is not repeated in step 4.
- **Step 4b echo heading:** `--- 4b: aio generated evidence + mutation checks ---` stands in for usaaio's step-7 heading, so the gate keeps seven steps.
- **Registry top-level key fix:** `tools/aio/books.py` again requires the exact top level (`books_version`, `books`), as usaaio did; Phase D part 1 had loosened it.
- **`ci_scope` paths:** the aio publisher's global inputs are `tools/aio/publish*.py`, `tools/aio/publish_theme/`, `tools/aio/books.py` and `scripts/aio/build-book.sh`.
  The py4kids `tools/publish.py` no longer routes the aio books full.
- **Scope duplicate-evidence fix:** `checks/scope.py` lets a modality cite each lesson anchor, practice and assessment only once.
  usaaio's test passed only because its fixture lacked the repository-root reconciliation.
- **Phase F, 025f499d:** the pinned pre-Plan-033 `panels.lua` fixture (F.1).
- **Clean-checkout provisioning** (F.2): `uv sync --frozen --group roar --inexact` before ci-local, for a pre-existing `main` test-environment gap.
- **Import report "Renamed paths"** (Phase B item 3): the report lists per-root move counts and the special renames rather than every renamed path; every rename is still recoverable from those counts and the full changed-file list ([fable] nit 2).
- **Content gate, after the verification runs:** `tools/aio/tests/test_exec_isolation.py` (aio suite 1783) and the removal of the premature `build/aio-outputs/` ignore rule; the final `ci-local.sh --all-books` run below covers both.
