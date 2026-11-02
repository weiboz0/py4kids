# Plan aio-002 — Editions: `publication: true`, step-5 routing, `output/aio-*/`

**v2** (2026-11-01) folds plan-review round 1 ([self] APPROVE WITH NITS: 1 MUST + 1 NIT; [sol] REJECT: 1 BLOCKER + 2 MUST + 1 NIT; [fable] APPROVE WITH NITS: 2 MUST + 4 NIT). **v1** was the first draft.
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
   - `scoped` → the same two with `--units …` / `--mocktests …`;
   - `glossary` → `publish_audit … --glossary-only`;
   - `none` → `INFO build-book: <id> unchanged (change-routed)`;
   - any other mode → FAIL.
   The router runs **once** for all aio books, after the per-book loop's `done 3<<< "$books"` and before `echo "book editions rendered: …"`. A router failure fails the step.
   The aio books join that summary: `full`/`scoped` are appended to `rendered`, and `glossary`/`none` to `skipped` with the route. No aio route is silent.
   The stub's FAIL branch inside the per-book loop becomes `is_aio "$book" && continue` before the py4kids `tools.ci_scope` call.
   `scripts/aio/build-book.sh`'s inner `py()` helper (`:49-52`) gains `--group aio`, so the publisher and `publish_output` run under the group as well.
   The publisher imports only `yaml` and the stdlib, so this changes no output; it keeps the group boundary exact.
2. **The shared trigger** (design D6: py4kids' `tools/ci_scope.py` "contributes its shared-file full trigger").
   The aio router's global set becomes the aio half of the py4kids rule:
   - py4kids `SHARED_FILES` (`books.yaml`, `pyproject.toml`, `uv.lock`), already in `GLOBAL_EXACT`;
   - **every path under `tools/aio/` (except `tools/aio/tests/`) and `scripts/aio/`**, the prefixes the exec router already uses (`EXEC_GLOBAL_PREFIXES`).

   The second item replaces the narrower usaaio `is_global_input` rule, which missed the publisher's own imports: `tools/aio/model.py` comes in through `tools/aio/books.py:13`.
   The py4kids `tools/` and `scripts/` outside the aio folders do not route the aio books, because no aio publisher file imports or calls them.
   This is a recorded deviation from usaaio parity, made in the conservative direction.
   Tests assert the split:
   - `tools/publish.py` → `none`;
   - `tools/aio/model.py` and `scripts/aio/build-pdf.sh` → `full`;
   - `tools/aio/tests/test_scope.py` → `none`;
   - `uv.lock` → `full`.
3. Router tests (aio suite, `tools/aio/tests/test_ci_scope.py`): the py4kids-path cases of item 2; `--all-books` → `full` for both; one changed `aio-ml` unit → `scoped aio-ml --units <unit>` and `none aio-dl`; one changed `aio-dl` mock test → `scoped aio-dl --mocktests r2-001`.
   A ci-local text test beside aio-001's exec-route test (`tools/aio/tests/test_integration.py::test_ci_routes_aio_exec_through_the_aio_ci_scope_and_filters_both_loops`) asserts that step 5 calls the router once, handles the four modes and fails on an unknown one.
   The test also pins the loop's position (after the per-book loop and before the summary line).
   The py4kids step-5 text tests (`tests/test_ci_scope.py:108-120`, `tests/test_tools.py:1627`) key on the first `bash scripts/build-book.sh` / `publish-audit`, so they stay green; they are re-run, and any change is listed.
4. `scripts/aio/build-book.sh` writes `output/<id>/<id>-<edition>[-vol<N>].pdf` through `tools/aio/publish_output.py` (unchanged from aio-001).
   `output/README.md`:
   - The two aio sections list their editions (replacing "not a `publication` book yet").
   - "Publishing a release" gains the aio release rule from the Global constraints: the Teacher's Edition, the answer key and the mock-test solutions are excluded unless the author decides otherwise.

### Phase C — verification (named)
1. **Every edition builds:** `ci-local.sh --all-books` renders all of `aio-ml` (`student-print`, `student-vol1..3`, `teacher-vol1..3`, `answer-key`) and `aio-dl` (`student`, `student-print`, `teacher`, `answer-key`), and `publish_audit` passes for both (the `overfull_max_pt: 5` limit included).
   That is **12 edition PDFs**: 8 for aio-ml and 4 for aio-dl. The report lists every PDF in `output/aio-ml/` and `output/aio-dl/` with its page count.
2. **Page counts vs usaaio:** the baseline is a fresh `git clone ../usaaio /dev/shm/aio002-usaaio && git -C /dev/shm/aio002-usaaio checkout --detach a20128f`.
   The clone is provisioned per usaaio's own instructions, as in aio-001 F.1 (`uv sync` via `uv run`; `scripts/fetch-reference.sh --all`), then `bash scripts/build-book.sh --book book1|book2` runs there.
   The report records the clone's `git rev-parse HEAD` and `git status --porcelain` (clean).
   The report tabulates edition, usaaio pages, py4kids pages and difference; every row is within ±2%.
   The on-disk `../usaaio/output/` PDFs (built 2026-10-28 after `a20128f`) are cross-checked against the fresh baseline, read only, and any difference is reported, not used.
3. **Text parity:** for each edition, `pdftotext` of both builds, diffed after applying the D3 rename map; differences are only the renames (listed counts). A non-rename difference blocks.
4. **Routing:** on a scratch clone of this branch, provisioned as in aio-001 F.2 (`scripts/aio/verify-clean-checkout.sh`'s provisioning step), a one-line comment-only change to one `aio-ml` lesson notebook is committed, and ci-local step 5 is run: it prints `scoped aio-ml --units <unit>`, renders the scoped check into `aio-ml/build/publish-check/`, copies nothing to `output/`, and routes `aio-dl` `none`.
   (The change never leaves the scratch clone.)
5. **Leaks:** `git ls-files output` is only `output/README.md`; `pre-merge-guard.sh --pr` OK; `overlap-scan --require-corpus` passes in the `--all-books` run (design D4).
6. **py4kids unchanged:** step 3–6 results for the six py4kids-model books identical to `main` (same PASS lines, same counts, same editions and page counts).
7. **CI budget:** the added `--all-books` step-5 time is recorded; an ordinary branch with no aio publication input change adds only the router call.

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

## Content Review

## Post-Execution Report
