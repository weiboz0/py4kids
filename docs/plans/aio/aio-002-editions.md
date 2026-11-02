# Plan aio-002 — Editions: `publication: true`, step-5 routing, `output/aio-*/`

**v3.1** (2026-11-01) folds round 3 ([sol] APPROVE; [fable] APPROVE WITH NITS: 1 MUST + 3 NIT). **Plan gate CLOSED (consensus).** **v3** folded plan-review round 2 ([sol] REJECT: 1 BLOCKER + 2 MUST; [fable] APPROVE WITH NITS: 1 MUST + 4 NIT). **v2** folded plan-review round 1 ([self] APPROVE WITH NITS: 1 MUST + 1 NIT; [sol] REJECT: 1 BLOCKER + 2 MUST + 1 NIT; [fable] APPROVE WITH NITS: 2 MUST + 4 NIT). **v1** was the first draft.
**Design:** `docs/designs/014-aio-books.md` (v4.2) §2 D6 and the §4 roadmap row **aio-002**.
**Precondition:** aio-001 (PR #172, `d80e76db`) merged; the publisher (`tools/aio/publish*.py`, `tools/aio/publish_theme/`), `scripts/aio/build-book.sh` and the edition router (`tools/aio/ci_scope.py` `route_books`) were ported there and are tested by the aio suite, but nothing calls them yet.
**Autopilot** per AGENTS.md.

This plan turns on the aio books' editions.
It **writes no new content** and changes no theme: the editions are the usaaio editions, built here.
The website (`site`) is aio-003.

## Goal
With `publication: true` on `aio-ml` and `aio-dl`, `TMPDIR=/dev/shm bash scripts/ci-local.sh --all-books` builds every aio edition into `output/<id>/` and passes the aio publish-audit.
Each edition's page count is within ±2% of the same edition built from usaaio `a20128f`.
An ordinary branch renders the aio editions only where `tools/aio/ci_scope.py` routes them.
The py4kids-model books' results are unchanged.

## Global constraints
- **The repo is PUBLIC.** No PDF is committed (`output/**/*.pdf` stays ignored).
  The Teacher's Edition and the answer key print Set B/C answers and the mock-test solutions; they are built artifacts only, never tracked.
  **They are also never put in a public release.** The author's 2026-09-29 choice to release the Teacher's Edition (`output/README.md` "Publishing a release") covers the py4kids-model books.
  Design 014 D7 releases only Set A answers and no mock-test solution, so an aio book's release assets are its student editions (`student`, `student-print`, `student-vol<N>`), `syllabus.pdf`, `handouts/` and the mock-test **papers** only, unless the author decides otherwise.
  This plan publishes no release; Phase B.4 records the rule in `output/README.md`.
- **Fidelity.** No content, `publication.yaml` or theme change. The only differences from usaaio's editions are the D3 renames (`book1`→`aio-ml`, `book2`→`aio-dl` in ids and file names).
- **Isolation.** Every aio edition command runs under `uv run --group aio`. The group-free `pytest -q` stays group-free.
  `tools/books.py` `_parse_publication_config` refuses an aio book's config on `content_model`, never on an id. The other py4kids `publication` readers stay off for an aio book only because no ci-local route reaches them (Phase A.4).
- **`../usaaio` is never written.** The baseline builds run in a scratch clone pinned to `a20128f` (Phase C.2), and that clone is the only build site.
- **Dispatch** (AGENTS.md): the tooling change (Phase B) by one Opus subagent with this plan and design D6 as its brief; Phase A and the verification inline.

## Phases

### Phase A — registry
1. `books.yaml`: `publication: true` on `aio-ml` and `aio-dl`. The header comment's `publication` paragraph says that an `aio` book is published by `tools/aio/` (design 014 D6) from its usaaio-schema `publication.yaml`.
2. The aio test that aio-001 dropped as deferral (d), `tools/aio/tests/test_publication_config.py::test_real_books_are_publication_books_with_valid_configs`, is restored as ported (aio-001 F.1 row −1), so the aio suite count returns to its usaaio parity.
3. The group-free registry tests that assert the publication flag:
   - `tests/test_books.py:133`: the `enabled["publication"]` list gains `aio-ml` and `aio-dl`.
   - `tests/test_books.py:404`: `assert not any(flag in book for flag in ("publication", "site"))  # not yet` becomes `publication` asserted true and `site` still absent.

   No other test in `tests/` enumerates the registry's publication books (checked by grep; the report lists the grep).
4. **The py4kids `publication` readers**, and why each stays off for an aio book once the flag is on:
   - `tools/publish.py:1582` and `scripts/build-book.sh:13`: the py4kids publisher. ci-local never calls it for an aio book, and `publication_config` refuses one.
   - `tools/notebooks.py:1372`: `lesson-outputs-check`. ci-local step 3 skips aio books (`is_aio … && continue` precedes `has_flag publication`).
   - `tools/publish_audit.py:990`: the py4kids audit, never called for an aio book.
   - `tools/export/bundle.py:165` and `tools/export/answer_model.py:392`: the site export. The site build selects `site: true` books only (`scripts/build-site.sh`), and `site` stays off until aio-003, which must route these two.

   A group-free test pins that `publication_config` refuses an aio book with the design-014 message, and that `scripts/build-book.sh --book aio-ml` fails before rendering.

### Phase B — step-5 routing (Opus subagent)
1. `scripts/ci-local.sh` step 5: the `FAIL: … aio editions are not routed yet` stub is replaced by usaaio `a20128f` step 8's edition loop (`scripts/ci-local.sh:167-189` there), ported verbatim apart from paths and the group:
   `uv run --group aio python -m tools.aio.ci_scope --root "$repo_root" [--all-books]` produces one route line per aio publication book, and each mode runs as there:
   - `full` → `uv run --group aio bash scripts/aio/build-book.sh --book <id>` then `uv run --group aio python -m tools.aio.publish_audit --root … --book <id>`;
   - `scoped` → the same two, passing the route's `--units …` / `--mocktests …` words (`"${route_scope[@]}"`) verbatim to both, as usaaio does (no re-parsing);
   - `glossary` → `publish_audit … --glossary-only`;
   - `none` → `INFO build-book: <id> unchanged (change-routed)`;
   - any other mode → FAIL.
   The router runs **once** for all aio books, after the per-book loop's `done 3<<< "$books"` and before `echo "book editions rendered: …"`. A router failure fails the step.
   The aio books join that summary: `full`/`scoped` are appended to `rendered`, and `glossary`/`none` to `skipped` with the route. No aio route is silent.
   **The loop is a shell function**, `aio_edition_routes`, defined inside step 5 before the per-book loop. It is not defined among the top-level helpers, because `tests/test_tools.py:1627-1633` orders the first `has_flag publication` before the first `build-book.sh` in the whole file.
   Its interface:
   - its arguments are the expected aio publication book ids;
   - the router command comes from an overridable array, `aio_edition_router=(uv run --group aio python -m tools.aio.ci_scope)` (default), called with `--root "$repo_root" "${scope_args[@]}"`;
   - it appends to the globals `rendered` and `skipped`.

   Its body has no bare `}` line, so the tests can extract it from `name() {` to the first `\n}\n`, as `tools/aio/tests/test_integration.py:1706-1707` does for the exec loop.
   **Exactly one route line per book:** the loop collects the routed book ids and compares them with the registered aio `publication: true` books (`MODEL` + `has_flag publication`). A missing, duplicated or unregistered book fails the step (`FAIL: aio edition routes … differ from books.yaml …`), as the step-1 adapter check does for the catalog.
   The step-5 header comment (`scripts/ci-local.sh:453-456`) states the aio rule beside the py4kids one: the book's paths, `tools/aio/` (not its tests), `scripts/aio/`, the shared CI files of B.2, or `--all-books`.
   The stub's FAIL branch inside the per-book loop becomes `is_aio "$book" && continue` before the py4kids `tools.ci_scope` call.
   `scripts/aio/build-book.sh`'s inner `py()` helper (`:50-53`) and the same nested `uv run … python` in `scripts/aio/build-pdf.sh:29` gain `--group aio`, so the publisher, `publish_output` and the PDF builder run under the group as well.
   The publisher imports only `yaml` and the stdlib, so this changes no output; it keeps the group boundary exact.
2. **The shared trigger** (design D6: py4kids' `tools/ci_scope.py` "contributes its shared-file full trigger").
   The aio router's global set becomes the aio half of the py4kids rule:
   - py4kids `SHARED_FILES` (`books.yaml`, `pyproject.toml`, `uv.lock`), already in `GLOBAL_EXACT`;
   - the shared CI and toolchain files the exec router already treats as global: `scripts/ci-local.sh` and `.python-version` (`EXEC_GLOBAL_EXACT`, `tools/aio/ci_scope.py:239-241`);
   - **every path under `tools/aio/` (except `tools/aio/tests/`) and `scripts/aio/`**: the exec router's `EXEC_GLOBAL_PREFIXES` minus `tools/aio/tests/`.

   The second item replaces the narrower usaaio `is_global_input` rule, which missed the publisher's own imports: `tools/aio/model.py` comes in through `tools/aio/books.py:13`.
   The py4kids `tools/` and `scripts/` outside the aio folders and the files above do not route the aio books, because no aio publisher file imports or calls them.
   This is a recorded deviation from usaaio parity, made in the conservative direction.
   Its cost: a change to any non-test aio tool (for example `tools/aio/checks/*` or `tools/aio/cli.py`) renders all 12 aio editions on an ordinary branch. C.7 records one full aio render's wall time, so the author can judge it.
   The module docstring (`tools/aio/ci_scope.py:12-14`) is updated to the new set.
   Tests assert the split:
   - `tools/publish.py` → `none`;
   - `tools/aio/model.py`, `scripts/aio/build-pdf.sh`, `scripts/ci-local.sh` and `.python-version` → `full`;
   - `tools/aio/tests/test_scope.py` → `none`;
   - `uv.lock` → `full`.
3. Router tests (aio suite, `tools/aio/tests/test_ci_scope.py`): the existing `test_unrelated_changes_are_unchanged_and_print_info` (`:47-49`) asserts `tools/aio/checks/scope.py` → `none`, which the wider set makes `full`; it is updated to keep its intent with paths that stay `none` (`tools/publish.py`, `tools/aio/tests/test_scope.py`), and the update is listed. Then the path cases of item 2; `--all-books` → `full` for both; one changed `aio-ml` unit → `scoped aio-ml --units <unit>` and `none aio-dl`; one changed `aio-dl` mock test → `scoped aio-dl --mocktests r2-001`.
   A ci-local text test beside aio-001's exec-route test (`tools/aio/tests/test_integration.py::test_ci_routes_aio_exec_through_the_aio_ci_scope_and_filters_both_loops`) asserts that step 5 calls the router once, handles the four modes, fails on an unknown one, and fails when the routed books differ from the registered aio publication books.
   A behavioural test runs the step-5 route loop (extracted as a shell function so it can be called alone) with a stub router that omits a book, one that repeats a book, and one that prints an unknown mode: each exits non-zero with its FAIL line.
   The test also pins the loop's position (after the per-book loop and before the summary line).
   The py4kids step-5 text tests (`tests/test_ci_scope.py:108-120`, `tests/test_tools.py:1627`) key on the first `bash scripts/build-book.sh` / `publish-audit`, so they stay green; they are re-run, and any change is listed.
4. `scripts/aio/build-book.sh` writes `output/<id>/<id>-<edition>[-vol<N>].pdf` through `tools/aio/publish_output.py` (unchanged from aio-001).
   `output/README.md`:
   - The two aio sections list their editions (replacing "not a `publication` book yet").
   - The header (`output/README.md:7`) states the aio edition rule beside the py4kids one.
   - "Publishing a release" step 2 ("Stage copies of every book's PDFs") is rewritten as an explicit allowlist:
     - every py4kids-model book's PDFs, as today;
     - for an aio book, **only** `<id>-student*.pdf`, its syllabus, its handouts and its mock-test papers (`output/<id>/mocktests/<test>-paper.pdf`, staged as `<id>-<test>-paper.pdf`).

     It names what is never staged for an aio book: `<id>-teacher*.pdf`, `<id>-answer-key.pdf` and every `mocktests/<test>-solutions.pdf`.
     The note under the procedure keeps the 2026-09-29 Teacher's Edition choice and scopes it to the py4kids-model books.

### Phase C — verification (named)
1. **Every edition builds:** `ci-local.sh --all-books` renders all of `aio-ml` (`student-print`, `student-vol1..3`, `teacher-vol1..3`, `answer-key`) and `aio-dl` (`student`, `student-print`, `teacher`, `answer-key`), and `publish_audit` passes for both (the `overfull_max_pt: 5` limit included).
   That is **12 edition PDFs**: 8 for aio-ml and 4 for aio-dl. The report lists every PDF in `output/aio-ml/` and `output/aio-dl/` with its page count.
2. **Page counts vs usaaio:** the baseline is a fresh `git clone ../usaaio /dev/shm/aio002-usaaio && git -C /dev/shm/aio002-usaaio checkout --detach a20128f`.
   The editions need no reference corpus, so the clone needs only usaaio's environment (`uv sync` via `uv run`); then `bash scripts/build-book.sh --book book1|book2` runs there.
   The report records the clone's `git rev-parse HEAD` and `git status --porcelain` (clean).
   The report tabulates edition, usaaio pages, py4kids pages and difference; every row is within ±2%.
   The on-disk `../usaaio/output/` PDFs (built 2026-10-28 after `a20128f`) are cross-checked against the fresh baseline, read only, and any difference is reported, not used.
3. **Text parity:** for each edition, `pdftotext` of both builds, diffed after applying the D3 rename map; differences are only the renames (listed counts). A non-rename difference blocks.
4. **Routing:** on a scratch clone of this branch, provisioned as in aio-001 F.2 (`scripts/aio/verify-clean-checkout.sh`'s provisioning step), a one-line comment-only change to one `aio-ml` lesson notebook is committed.
   ci-local has no step selector, so the step-5 route loop of B.1 is run on its own (the extracted shell function, with the real router).
   The evidence is its printed lines:
   - `scoped aio-ml --units <unit>`, followed by the scoped `build-book: scoped check of aio-ml …` and scoped `publish_audit` PASS lines;
   - `INFO build-book: aio-dl unchanged (change-routed)`.

   Nothing new appears in `output/`, and the render lands in `aio-ml/build/publish-check/`.
   (The change never leaves the scratch clone.)
5. **Leaks:** `git ls-files output` is only `output/README.md`; `pre-merge-guard.sh --pr` OK; `overlap-scan --require-corpus` passes in the `--all-books` run (design D4).
6. **py4kids unchanged:** step 3–6 results for the six py4kids-model books identical to `main` (same PASS lines, same counts, same editions and page counts).
7. **CI budget:** the added `--all-books` step-5 time is recorded, with the wall time of one full aio render per book (the cost of B.2's wider set). An ordinary branch with no aio publication input change adds only the router call.

## Out of scope (verification-phase exemption)
No units, mock tests or other content ship; Phase C is this plan's verification.
Also out of scope: any `publication.yaml`, content or theme change; the website and export adapter (aio-003); classification (aio-004/005); committing any PDF; any change to `../usaaio`.

## Plan Review

### Round 1 (v1)

**[self]** APPROVE WITH NITS (1 MUST, 1 NIT):
1. MUST: Phase A should name every py4kids reader of the `publication` flag, and say why each stays off for an aio book once the flag is on.
   They are: `tools/publish.py:1582` and `scripts/build-book.sh:13` (py4kids publisher; ci-local never calls it for an aio book, and `publication_config` refuses one), `tools/notebooks.py:1372` (`lesson-outputs-check`, ci-local step 3 skips aio books), `tools/publish_audit.py:990` (py4kids audit, not called for aio), and `tools/export/bundle.py:165` and `tools/export/answer_model.py:392` (site export only; `site` stays off until aio-003, which must route these).
   A group-free test should pin the refusal.
2. NIT: C.4's scratch clone needs the aio provisioning (D8) before a scoped render; say so.

**[sol]** REJECT (1 BLOCKER, 2 MUST, 1 NIT):
1. BLOCKER: `tests/test_books.py:404` asserts that no aio book has `publication`, so Phase A would leave the group-free suite failing → **[FIXED]** A.3 names it.
2. MUST: the baseline relies on an ephemeral clone (absent in its environment) → **[FIXED]** C.2 makes a fresh clone pinned to `a20128f` and records its HEAD and status.
3. MUST: the nested `uv run` in `scripts/aio/build-book.sh:50` has no `--group aio` → **[FIXED]** B.1 adds it to `py()`.
4. NIT: the blanket "py4kids tools key on `content_model`" claim is too broad (`tools/export/bundle.py:163`) → **[FIXED]** Global constraints narrowed, with the reachability list in A.4.

**[fable]** APPROVE WITH NITS (2 MUST, 4 NIT):
1. MUST: the claim that `is_global_input` names exactly the publisher's inputs is false (it misses `tools/aio/model.py`), and dropping `SHARED_DIRS` is an unstated deviation → **[FIXED]** B.2 adopts the `tools/aio/` + `scripts/aio/` prefixes (option a), recorded as a deviation in the conservative direction, with tests.
2. MUST: the public-release procedure would ship the aio Teacher's Editions, answer keys and mock-test solutions → **[FIXED]** a release rule in the Global constraints, recorded in `output/README.md` by B.4.
3. NIT: name the touched tests (`tests/test_books.py:133,404`), and pin the position of the router loop → **[FIXED]** A.3, B.1, B.3.
4. NIT: "usaaio read only" vs. building in the clone → **[FIXED]** reworded.
5. NIT: B.1 runs `build-book.sh` bare → **[FIXED]** under `uv run --group aio`.
6. NIT: state the expected count (12 edition PDFs) → **[FIXED]** C.1.

[self] 1 → **[FIXED]** A.4; [self] 2 → **[FIXED]** C.4.

### Round 2 (v2)

**[self]** APPROVE WITH NITS: no new findings beyond the reviewers'.

**[sol]** REJECT (1 BLOCKER, 2 MUST); its round-1 findings are all resolved.
1. BLOCKER: the widened set still omits `scripts/ci-local.sh`, which controls the builds → **[FIXED]** B.2 adds `scripts/ci-local.sh` and `.python-version` (the exec router's shared files), with tests.
2. MUST: the release procedure still stages "every book's PDFs" → **[FIXED]** B.4 rewrites step 2 as an explicit allowlist that names what is never staged.
3. MUST: no test or behaviour for a missing route line → **[FIXED]** B.1 checks for exactly one route per registered book; B.3 adds the stub-router tests.

**[fable]** APPROVE WITH NITS (1 MUST, 4 NIT); its round-1 findings are all resolved.
1. MUST: `tools/aio/tests/test_ci_scope.py:47-49` expects `tools/aio/checks/scope.py` → `none` → **[FIXED]** B.3 updates it, along with the module docstring (B.2).
2. NIT: "the exec prefixes" includes `tools/aio/tests/`; the budget consequence is unstated → **[FIXED]** B.2 wording and cost; C.7 records the render time.
3. NIT: stale prose in `scripts/ci-local.sh:453-456` and `output/README.md:7` → **[FIXED]** B.1, B.4.
4. NIT: ci-local has no step selector → **[FIXED]** C.4 runs the extracted route loop and names the evidence lines.
5. NIT: the baseline needs no `fetch-reference.sh` → **[FIXED]** C.2.

### Round 3 (v3): CONSENSUS

**[self]** APPROVE.
**[sol]** APPROVE: no findings; its round-2 findings are resolved.
**[fable]** APPROVE WITH NITS (1 MUST, 3 NIT); its round-2 findings are resolved.
1. MUST: specify the interface of the extracted route-loop function, so the stub tests and C.4 can call it → **[FIXED]** B.1 names `aio_edition_routes`, its arguments, the overridable `aio_edition_router` array, and the no-bare-`}` rule.
2. NIT: pin where the function is defined (`tests/test_tools.py:1627-1633`) → **[FIXED]** B.1: inside step 5.
3. NIT: `scripts/aio/build-pdf.sh:29` has the same group gap; the `py()` lines are `:50-53` → **[FIXED]** B.1.
4. NIT: say "verbatim" for the scoped words → **[FIXED]** B.1.

The round-3 fold is mechanical and adds no scope. The gate closes with all three at APPROVE or APPROVE WITH NITS and no `[OPEN]` item.

## Content Review

Duty: conventional code review of the tooling plus public-repo safety. No content ships (docs/content-review-gate.md; design 014 §3).

### Review 1 (2026-11-02, on `bbdde5c1`): CONSENSUS

**[self]** APPROVE.
The aio release allowlist in `output/README.md` stages only the student editions (which carry Set A answers only, per D7), the syllabus, the handouts and the mock-test papers.
The step-5 function's empty-argument case compares equal: both sides print one empty line.

**[sol]** APPROVE WITH NITS (1 NIT):
1. NIT: the route-loop tests cannot catch a swallowed build or audit failure, because the stub `uv` always exits 0 → **[FIXED]** `c951d182`. `test_ci_aio_edition_routes_fail_when_a_build_or_audit_fails` makes the stub fail on the build and then on the audit.
   It was mutation-checked: `|| true` on either step-5 command makes it fail.
   That check also exposed a stub bug, a trailing `[[ … ]] && exit 1` that made every unmatched call exit 1; it is fixed.

The router's global set matches B.2. The exactly-one-route check, the scoped-word forwarding and the fd-4 read are sound. No PDF is tracked, and there is no commit or release path for the restricted aio PDFs.

**[fable]** APPROVE WITH NITS (2 NIT), after checking every plan item, bash correctness and the README paths against the scripts:
1. NIT: the step-5 comment's "ported verbatim apart from paths and the aio group" omits the fd-4 read, the book-set check and the bookkeeping → **[FIXED]** the comment now names them.
2. NIT: the text test pins exact shell strings, so a reformat breaks it → **[WONTFIX]** it is the house style for the ci-local text tests (aio-001's exec-route test does the same), and the behavioural test covers command fidelity independently.

After the fixes, the suites that read `scripts/ci-local.sh` or the changed tests were re-run green:
- aio `test_integration.py`, `test_ci_scope.py` and `test_publication_config.py`: 87 passed;
- `tests/test_ci_scope.py`, `test_tools.py`, `test_books.py` and `test_book_ids.py`: 447 passed;
- ruff clean; `pre-merge-guard` OK.

The fix commits change only a test and one `ci-local.sh` comment line, so the green `--all-books` run on `331871cd` stands as the gate for every executable line.

## Post-Execution Report

Phases A–C are complete on `feature/aio-002-editions`: Phase A at `9b3ad391` (inline), and Phase B at `331871cd` (an Opus subagent with this plan as its brief).

### Phase A
- `books.yaml`: `publication: true` on both aio books, and the header's `publication` paragraph names the `tools/aio/` publisher.
- The restored aio test is `test_real_books_are_publication_books_with_valid_configs`, as at usaaio `a20128f`. The aio suite is now 1790, up from aio-001's 1783: this test plus Phase B's new router tests.
- Group-free test updates:
  - `tests/test_books.py:133` (the `publication` set);
  - `:404` (aio books now have `publication`, and still no `site`);
  - `:485`, `test_ci_local_step1_accepts_the_real_registry`. The step-1 line for an aio book is now `aio-ml publication`, not the bare id. A.3's grep missed this one, and the full suite run caught it.
- New `test_py4kids_build_book_refuses_an_aio_publication_book_before_rendering` (A.4). The existing `test_aio_books_are_not_py4kids_concept_owners_or_publications` already pinned the `publication_config` refusal.

### Phase B
- **ci-local step 5:**
  - `aio_edition_router` and `aio_edition_routes` are defined inside step 5, before the per-book loop.
  - The router runs once. Its output is read twice: first to check exactly one route per registered aio publication book, before anything renders; then on fd 4 to run each route, so the build commands cannot read the route lines from stdin.
  - The per-book loop has `is_aio "$book" && continue`. The expected-book list is built in a short loop after it.
  - A router failure prints its own FAIL line.
  - A scoped book joins `rendered` as `<id> (scoped …)`.
- **`tools/aio/ci_scope.py`:**
  - `GLOBAL_EXACT` is `books.yaml`, `pyproject.toml`, `uv.lock`, `scripts/ci-local.sh` and `.python-version`.
  - `GLOBAL_PREFIXES` is `tools/aio/` and `scripts/aio/`, with `tools/aio/tests/` excluded.
  - The docstring is updated.
- **`--group aio`** is added to `scripts/aio/build-book.sh` `py()` and to `scripts/aio/build-pdf.sh`'s uv runner.
- **Tests:**
  - `test_unrelated_changes_are_unchanged_and_print_info` now uses `tools/aio/tests/test_scope.py`.
  - Router cases are added for every B.2 path.
  - Integration tests: a text test, plus behavioural stub-router tests (all four modes; an omitted, repeated or unregistered book; an unknown mode; a failing router). They run the extracted function with a fake `uv`, so nothing renders.
  - The py4kids step-5 text tests (`tests/test_ci_scope.py`, `tests/test_tools.py:1627`) pass unchanged.
- **`output/README.md`:**
  - The header states the aio rule.
  - New `output/aio-ml/` and `output/aio-dl/` sections. The plan's "replacing 'not a `publication` book yet'" text did not exist for the aio books, so the sections are new; they are ported from usaaio's `output/README.md` with the D3 renames.
  - Release step 2 is the explicit allowlist, and names what is never staged for an aio book.
  - The 2026-09-29 Teacher's Edition note is scoped to the py4kids-model books.

### C.1 Every edition builds
`TMPDIR=/dev/shm bash scripts/ci-local.sh --all-books` on `331871cd` ended **`ci-local: ALL GREEN`**. That was the second run; see Deviations.

| Suite / check | Result |
|---|---|
| group-free suite | 2291 passed, 2 skipped |
| recsys suite | 348 passed |
| roar suite | 636 passed |
| aio suite | 1790 passed |
| register verification | 437/437 |
| mutation verifications | 5/5 ×3 |
| aio PDFs | 22 + 9 |
| aio editions | 8 PDFs for aio-ml in 676 s; 4 for aio-dl in 910 s |
| aio `publish-audit` | `OK` for both books |
| widest overfull line | 4.81 pt (aio-dl), within `overfull_max_pt: 5` |
| step-5 summary | `book editions rendered: python-projects python-concepts usaco-bronze acsl aio-ml aio-dl; skipped: none` |

### C.2 Page counts vs usaaio `a20128f`
The baseline is `git clone ../usaaio /dev/shm/aio002-usaaio`, checked out at `a20128f3a0e5455d2f78478d1ad8565ac26d9621`, with `git status --porcelain` empty.
`build-book.sh --book book1` and `--book book2` took 26 m 38 s.
The on-disk `../usaaio/output/` PDFs have the same page counts as the fresh baseline, edition for edition.

| Edition | usaaio | py4kids | Δ |
|---|---|---|---|
| aio-ml-student-print | 1023 | 1023 | 0% |
| aio-ml-student-vol1 | 560 | 560 | 0% |
| aio-ml-student-vol2 | 468 | 468 | 0% |
| aio-ml-student-vol3 | 464 | 464 | 0% |
| aio-ml-teacher-vol1 | 738 | 738 | 0% |
| aio-ml-teacher-vol2 | 600 | 600 | 0% |
| aio-ml-teacher-vol3 | 718 | 718 | 0% |
| aio-ml-answer-key | 125 | 125 | 0% |
| aio-dl-student | 552 | 552 | 0% |
| aio-dl-student-print | 444 | 444 | 0% |
| aio-dl-teacher | 936 | 936 | 0% |
| aio-dl-answer-key | 46 | 46 | 0% |

### C.3 Text parity
Each edition was compared with `pdftotext` on both builds, after applying the D3 rename map to the usaaio text: `book1`→`aio-ml`, `book2`→`aio-dl`, and `USAAIO_BOOK_ROOT`→`AIO_BOOK_ROOT`.
The comparison ignores whitespace and hyphenation breaks.
- **All 8 aio-ml editions and the aio-dl answer key are character-identical**, from 139,809 to 1,681,002 characters each.
- **The other aio-dl editions** (`student`, `student-print`, `teacher`) have the same text, re-wrapped. Their many qualified ids (`aio-ml:` is two characters longer than `book1:`) re-wrap lines and move a few lines across page breaks inside unit B2-019 and later.
  Page counts are unchanged.
  Leaving out each page's running head and page numbers, the character multisets differ by 3, 3 and 1 digits (page references in moved text) and by nothing else.
  The aio-dl `teacher` edition's full-text character multiset is identical.

There is no non-rename content difference.

### C.4 Routing
The scratch clone `/dev/shm/aio002-route` holds this branch plus one committed comment line in `aio-ml/units/01-F1-scientific-python/lessons/01-arrays-and-indexing.ipynb`.
Its `origin/main` was set to the branch tip, so the probe is the whole change set.
The extracted `aio_edition_routes aio-ml aio-dl` printed:
- `build-book: scoped check of aio-ml (units: F1-scientific-python; mock tests: none) in 164s`, then `publish-audit aio-ml: OK`;
- `INFO build-book: aio-dl unchanged (change-routed)`;
- `rendered: aio-ml (scoped --units F1-scientific-python); skipped: aio-dl (change-routed)`.

The render landed in `aio-ml/build/publish-check/`, and `output/` held only `README.md`.
A first attempt left `origin/main` at `main`. It correctly routed both books `full`, because the branch changes global inputs. That attempt is not evidence for C.4.

### C.5 Leaks
- `git ls-files output` lists only `output/README.md`.
- `pre-merge-guard: OK`.
- `overlap-scan --require-corpus` passed for both books: aio-ml had 1/1 PDF parts and 37 index text parts; aio-dl had 3/3 and 26; neither had an extraction failure.
- The provisioned corpus is git-ignored (`!!`).

### C.6 py4kids unchanged
Every py4kids-book line of this run's steps 3–6 matches aio-001's final gate run (`d80e76db` lineage): every PASS, FAIL and SKIP line, every `book editions:` and `publish-audit:` line, and every render page count (69 lines).
The only added lines are the 12 aio edition renders.

### C.7 CI budget
`--all-books` step 5 adds the two aio edition builds: about 26.4 min of wall time (676 s + 910 s) plus the audits.
That is also the cost of one full aio render on an ordinary branch that touches a B.2 global input.
A scoped one-unit render took 164 s.
An ordinary branch that touches no aio publication input adds only the router call.

### Deviations (recorded)
- **First `--all-books` run failed, fail-closed:** `overlap-scan --require-corpus` reported `reference corpus absent`.
  The main checkout had never been step-B provisioned; aio-001 ran in a worktree.
  It was provisioned with `bash scripts/aio/fetch-reference.sh --all` and `aio-provision-cache.sh`, plus the two local `index.yaml` files copied from `../usaaio` (read only, per `scripts/aio/verify-clean-checkout.sh`'s note that they come only from a local corpus).
  All of these are ignored files. The second run was green. Log: `ci-all-1-nocorpus.log`.
- A.3's missed `:485` assertion (above).
- B.4's new README sections (above).
- B.1's fd-4 read and pre-check pass, the scoped `rendered` text, and the router FAIL line are additions within B.1's contract.
