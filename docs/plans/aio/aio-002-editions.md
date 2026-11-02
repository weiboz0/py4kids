# Plan aio-002 — Editions: `publication: true`, step-5 routing, `output/aio-*/`

**v1** (2026-11-01), draft for the plan-review gate.
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
- **Fidelity.** No content, `publication.yaml` or theme change. The only differences from usaaio's editions are the D3 renames (`book1`→`aio-ml`, `book2`→`aio-dl` in ids and file names).
- **Isolation.** Every aio edition command runs under `uv run --group aio`. The group-free `pytest -q` stays group-free.
  py4kids publication tools keep refusing an aio book (`tools/books.py` `_parse_publication_config`); they key on `content_model`, never on ids.
- **The usaaio repository is read only.** The baseline builds run in the existing fresh clone `/dev/shm/usaaio-a20128f` (aio-001 F.1), never in `../usaaio`.
- **Dispatch** (AGENTS.md): the tooling change (Phase B) by one Opus subagent with this plan and design D6 as its brief; Phase A and the verification inline.

## Phases

### Phase A — registry
1. `books.yaml`: `publication: true` on `aio-ml` and `aio-dl`. The header comment's `publication` paragraph says that an `aio` book is published by `tools/aio/` (design 014 D6) from its usaaio-schema `publication.yaml`.
2. The aio test that aio-001 dropped as deferral (d), `tools/aio/tests/test_publication_config.py::test_real_books_are_publication_books_with_valid_configs`, is restored as ported (aio-001 F.1 row −1), so the aio suite count returns to its usaaio parity.
3. Any group-free test that asserts the set of `publication: true` books (`tests/`) is updated to include the two aio books **only** where it asserts the registry flag; tests of py4kids publishing keep excluding them through `content_model`. Each change is listed in the report.

### Phase B — step-5 routing (Opus subagent)
1. `scripts/ci-local.sh` step 5: the `FAIL: … aio editions are not routed yet` stub is replaced by usaaio `a20128f` step 8's edition loop (`scripts/ci-local.sh:167-189` there), ported verbatim apart from paths and the group:
   `uv run --group aio python -m tools.aio.ci_scope --root "$repo_root" [--all-books]` produces one route line per aio publication book, and each mode runs as there:
   - `full` → `scripts/aio/build-book.sh --book <id>` then `python -m tools.aio.publish_audit --root … --book <id>`;
   - `scoped` → the same two with `--units …` / `--mocktests …`;
   - `glossary` → `publish_audit … --glossary-only`;
   - `none` → `INFO build-book: <id> unchanged (change-routed)`;
   - any other mode → FAIL.
   The router runs **once** for all aio books (not inside the per-book loop), after the per-book `build-pdf` loop; a router failure fails the step.
   The aio books join the step's `book editions rendered: …; skipped: …` summary (`full`/`scoped` → rendered, `glossary`/`none` → skipped with the route), so no aio route is silent.
2. **The py4kids shared trigger** (design D6: py4kids' `tools/ci_scope.py` "only contributes its shared-file full trigger"). The trigger is py4kids `SHARED_FILES` (`books.yaml`, `pyproject.toml`, `uv.lock`), already in the aio router's `GLOBAL_EXACT`.
   py4kids' `SHARED_DIRS` (`tools/`, `scripts/`) is **not** applied to the aio books: the aio publisher's code inputs are exactly the ones `is_global_input` names (`tools/aio/publish*.py`, `tools/aio/publish_theme/`, `tools/aio/books.py`, `scripts/aio/build-book.sh`), and the py4kids publisher shares no file with it.
   A test asserts this split: a change to `tools/publish.py` routes the aio books `none`, and to `uv.lock` routes them `full`.
3. Router tests (aio suite, `tools/aio/tests/test_ci_scope.py`): the py4kids-path cases of item 2; `--all-books` → `full` for both; one changed `aio-ml` unit → `scoped aio-ml --units <unit>` and `none aio-dl`; one changed `aio-dl` mock test → `scoped aio-dl --mocktests r2-001`.
   A ci-local text test beside aio-001's exec-route test (`tools/aio/tests/test_integration.py::test_ci_routes_aio_exec_through_the_aio_ci_scope_and_filters_both_loops`) asserts that step 5 calls the router once, handles the four modes and fails on an unknown one.
   The py4kids step-5 text tests (`tests/test_ci_scope.py`) still pass; the stub's FAIL line, if any of them asserts it, is updated and listed.
4. `scripts/aio/build-book.sh` writes `output/<id>/<id>-<edition>[-vol<N>].pdf` through `tools/aio/publish_output.py` (unchanged from aio-001); `output/README.md` gains one line naming the aio editions.

### Phase C — verification (named)
1. **Every edition builds:** `ci-local.sh --all-books` renders all of `aio-ml` (`student-print`, `student-vol1..3`, `teacher-vol1..3`, `answer-key`) and `aio-dl` (`student`, `student-print`, `teacher`, `answer-key`), and `publish_audit` passes for both (the `overfull_max_pt: 5` limit included).
   The report lists every PDF in `output/aio-ml/` and `output/aio-dl/` with its page count.
2. **Page counts vs usaaio:** the same editions built in `/dev/shm/usaaio-a20128f` (`bash scripts/build-book.sh --book book1|book2`) are the baseline.
   The report tabulates edition, usaaio pages, py4kids pages and difference; every row is within ±2%.
   The on-disk `../usaaio/output/` PDFs (built 2026-10-28 after `a20128f`) are cross-checked against the fresh baseline, read only, and any difference is reported, not used.
3. **Text parity:** for each edition, `pdftotext` of both builds, diffed after applying the D3 rename map; differences are only the renames (listed counts). A non-rename difference blocks.
4. **Routing:** on a scratch clone of this branch, a one-line comment-only change to one `aio-ml` lesson notebook is committed, and ci-local step 5 is run: it prints `scoped aio-ml --units <unit>`, renders the scoped check into `aio-ml/build/publish-check/`, copies nothing to `output/`, and routes `aio-dl` `none`.
   (The change never leaves the scratch clone.)
5. **Leaks:** `git ls-files output` is only `output/README.md`; `pre-merge-guard.sh --pr` OK; `overlap-scan --require-corpus` passes in the `--all-books` run (design D4).
6. **py4kids unchanged:** step 3–6 results for the six py4kids-model books identical to `main` (same PASS lines, same counts, same editions and page counts).
7. **CI budget:** the added `--all-books` step-5 time is recorded; an ordinary branch with no aio publication input change adds only the router call.

## Out of scope (verification-phase exemption)
No units, mock tests or other content ship; Phase C is this plan's verification.
Also out of scope: any `publication.yaml`, content or theme change; the website and export adapter (aio-003); classification (aio-004/005); committing any PDF; any change to `../usaaio`.

## Plan Review

## Content Review

## Post-Execution Report
