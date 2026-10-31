# Design 014 — The AI Olympiad books (migrating usaaio into py4kids)

**Status:** DRAFT — v2 (2026-10-31). v2 folds design-review round 1 ([self] 2 MUST + 1 NIT; [sol] REJECT, 2 BLOCKER + 4 MUST + 1 NIT;
[fable] APPROVE WITH NITS, 7 MUST + 3 NIT). Awaiting round 2 and the author's approval.
Brings the two books of the `usaaio` repository (`weiboz0/usaaio`, at commit `a20128f`) into py4kids,
publishes their editions from here, and puts them on the learning website (design 012).
Plans for these books live under `docs/plans/aio/` (`aio-NNN`); `tools/guard.py` already guards namespaced plan directories.

## 1. Purpose and agreed understanding

Author, 2026-10-31: "we will migrate the usaaio books from ../usaaio to this repo, generate version and website".
After a structural comparison of the two repositories, the author asked which unit structure suits the usaaio books better.
The answer given, and the premise of this design: **keep the usaaio content model inside the py4kids book shell**.
The author then said "go ahead with the design doc".

Why the usaaio content model is kept (recorded so reviewers can test the premise):
1. **Audience.** These books assume Calculus AB and basic Python, not zero experience.
   py4kids' project-first, one-idea-at-a-time and stretch laws protect beginners; these students need volume and rigor.
2. **Practice mirrors the contest.** About 24 practice items per unit in Sets A (fundamentals), B (exam register) and C (integration and challenge),
   typed `drill`, `mc`, `proof`, `constrained-coding`, `scenario`, `challenge`.
   One `exercises.ipynb` with a `stretch` tag would flatten the difficulty ladder that is the books' point.
3. **Mock tests are the right assessment.** Blueprinted, pointed, rubric-graded simulations of the real rounds.
   A py4kids checkpoint is a mastery check, not a timed simulation.
4. **Multi-session units.** A unit is about four lessons (`lessons/NN-*.ipynb`) over five or more hours.
5. **Tuned checks.** usaaio's answer-key, tolerance, overlap, blueprint, schedule and mutation checks enforce what this content needs;
   py4kids' checks would flag the wrong things (missing project hooks) and miss the right ones.
6. **Cost.** Converting 25 units to the py4kids model is a rewrite for a worse fit.

What py4kids contributes: the registry and its flags, descriptive book ids, the `output/<id>/` layout, the gates, and the website.

## 2. Decisions

- **D1 — Book identity.**

  | usaaio id | py4kids id = root | number | aio_round | title (unchanged) | subtitle (unchanged) | depends_on |
  |---|---|---|---|---|---|---|
  | `book1` | `aio-ml` | 4 | 1 | Machine Learning for the AI Olympiad | Round 1: Foundations, Models, and Practice | `[]` |
  | `book2` | `aio-dl` | 4 | 2 | Deep Learning for the AI Olympiad | Round 2: Transformers, Generative Models, and Open-Ended Modeling | `[aio-ml]` |

  - `number` stays a py4kids series ordinal that drives no tooling; both books share 4, as the two Book-1 variants share 1.
  - **`aio_round` (1 or 2, required on every `aio` book, rejected elsewhere) carries the role that usaaio's `number` played.**
    usaaio tooling routes on that number (mock-test glob `mocktests/r{number}-*`, `books.py:557`; dependency ordering `books.py:250`;
    `unit_order.py:42` book-1-only; `schedule.py:89-103,134,164-166`; `prereq.py:106`; `cli.py:131,151` passing `book_number` to answerkey/overlap),
    and on manifest `book: 2` (`model.py:431,570`), plus id-literal branches (`audit_curriculum.py:329` `statement_only_book2`, `scope.py:1259` `book1:C5-embeddings`,
    `render_curriculum_roadmap.py:405-408,517`, the three mutation verifiers' `--root` selection, usaaio `ci-local.sh` step 7 `BOOK_NUMBERS`).
    The catalog adapter (D4) sets the ported `BookSpec.number := aio_round`, so number-keyed code is unchanged;
    every id-literal branch is rewritten to resolve the book from `aio_round`. aio-001 ships the full consumer inventory (`grep` for `number`, `book1`, `book2`, `book: 2`) with each site's disposition.
  - The ids are new and collide with no existing id, folder or PDF stem.
    The usaaio ids cannot be kept: `book1`/`book2` are py4kids' own pre-plan-091 ids, which `tools/guard.py` `TRANSITION` still maps to `python-projects`/`usaco-bronze`,
    `tests/test_book_ids.py` forbids their spellings in `tests/` and every book root, and a legacy `book1/` folder of py4kids run-time files exists at the repo root (untouched).
  - `aio-ml` has no py4kids dependency: its baseline (Calculus AB + basic Python) is declared in its own standards (D5), not imported from `python-projects`.
- **D2 — A content-model key, and a complete routing table.**
  - `books.yaml` gains a value key `content_model` (absent = `py4kids`; the only other value is `aio`).
    It is read like `dependency_group`: a value, on its own line in ci-local step 1, never a boolean flag.
    An `aio` book also sets `dependency_group: aio` (D8), so every routed command runs under `uv run --group aio`.
  - The registry check rejects `judge`, `patterns`, `acsl` and `labs` on an `aio` book (they presuppose the py4kids layout); `publication` and `site` keep their meaning.
  - **Every ci-local command, and its route for an `aio` book** (the plan pins each to a line number):

    | Step | py4kids-model command | `aio` route |
    |---|---|---|
    | 1 | registry assertions (`books_version`, root = id, flag tuple) | same, plus `content_model`/`aio_round` validation |
    | 2 | group-free `pytest -q` (`testpaths = ["tests"]`) | unchanged: the aio suite lives **outside** `tests/` (D4) |
    | 2 | routed per-book data generators and `pytest -q <book>` | one routed `pytest -q tools/aio/tests` for the aio content model (not per book: the suite covers both books) |
    | 3 | hygiene, structure, noexec, cell-lint, milestone, exec-solutions, exec-lessons; `lesson-outputs-check` (publication); `lab-check` (labs) | aio notebook exec (usaaio step 3, incl. the 20 s aio-dl timeouts) + aio hygiene; none of the py4kids step-3 commands |
    | 4 | manifest, prereq, coverage, concept-scan, stretch; patterns/judge/acsl branches; **`turtle-check`/`turtle-real-check` for every non-`judge` book**; `site-check` (site) | the aio per-book checks (prereq, coverage, scope, schedule, tolerance, hygiene, blueprint, overlap, answerkey, layer-boundary, unit-order, api-comments), the aio all-books checks (prereq, scope, schedule) and `verify-register`; **no turtle checks**; `site-check` unchanged (site books) |
    | 4b | — | usaaio step 7: `audit_curriculum --check` and `render_course_structure --check` per book, `render_curriculum_roadmap --check`, the three mutation verifiers |
    | 5 | `build-pdf.sh` (handouts from `units/unit-*/exercises.ipynb`, FAILs if absent); `build-book.sh` + `py4kids-tools publish-audit` (called **without** `book_run`) | aio `build-pdf.sh` (syllabus, unit handouts, mock-test papers/solutions) and aio `build-book.sh` + aio `publish_audit`, both through the `aio` group |
    | 6 | site build + tests | unchanged; `build-site.sh` runs `export` routed through each book's group (D7) |
    | 7 | pre-merge-guard | unchanged, with the aio guard rules (D4) |

  - **All-book iterations filter to the py4kids model.** Cross-book concept uniqueness, peers and variants (`tools/curriculum.py:122`),
    `known_baseline` walks, `publication_config` and every loop over `books.yaml` in `tools/` skip `aio` books, so a missing `concepts.yaml` or a usaaio-schema `publication.yaml` never reaches py4kids code.
  - **py4kids registry tests** (`tests/test_books.py:17,28-31,109-138,181-186,220-231`) are updated: the new ids and flag sets, `content_model`/`aio_round` documented and read,
    the `projects/`/`checkpoints/` root-layout assertion and the `classification == "confirmed"` site assertion keyed on `content_model` (an aio book may be `proposed` until aio-004/005).
  - Tools key on `content_model`, `aio_round` and flags, never on book ids.
- **D3 — A snapshot import in two separate steps, history left in usaaio.**
  - **Step A, tracked snapshot:** exactly usaaio `git ls-files` at `a20128f` under `book1/`, `book2/`, `tools/`, `tests/`, `scripts/` and `docs/`, minus the exclusions below, copied to their new paths.
    The import commit and `aio-ml/IMPORTED.md` / `aio-dl/IMPORTED.md` record the source repo and SHA (prose names the "usaaio `book1` id", never a `book1/` path spelling, so `test_book_ids` stays clean).
    Squash-merge would flatten imported history anyway; the usaaio repo stays the history of record.
  - **Step B, local-only provisioning** (never committed, all git-ignored): the raw past papers via the ported `scripts/fetch-reference.sh` (public usaaio.org links; the 2025 forum papers stay manual),
    the hidden test sets copied from the author's usaaio checkout, and the external-artifact cache (D8).
  - **Not imported:** `book*/build/`, `output/**` PDFs, the untracked `book1/units/C10-competition-craft/` (stray practice CSV outputs),
    and the superseded machinery listed in D4.
  - **Ignore rules** move over verbatim with the roots renamed: `<book>/reference/*` except `.gitkeep`/`analysis.md` (raw past papers — copyright), `reference/cache/`,
    `units/18-C11-competition-craft/data/heldout.csv`, `mocktests/r1-001/data/p09_heldout.csv`, and the five C11 practice-output CSV rules (py4kids has no `*.csv` rule, so each is ported explicitly).
    `tools/guard.py` gains them as tracked-path refusals.
  - **Renames:** qualified ids `book1:<id>` → `aio-ml:<id>` (manifests, `book2/syllabus.md` `imports:`/`evidence_imports:`, tests, `scope.py`);
    the `../../../../book1/units/...` remediation links in 309 aio-dl notebooks → `../../../../aio-ml/units/...`; test fixtures (`tests/fixtures/two-books-valid/book1/` and kin) and their 364 literals;
    `USAAIO_BOOK_ROOT` → `AIO_BOOK_ROOT`. Unit folder names and unit ids are unchanged.
    The rename is one scripted substitution with a before/after count report. **Acceptance proof:** `tests/test_book_ids.py` (extended to `tools/aio/`) passes, and a grep for `book1`/`book2` spellings returns zero hits outside `docs/history/usaaio/`.
  - **Archive:** retained usaaio designs, plans, audits and reviews go read-only under `docs/history/usaaio/` (outside every guard numbering rule; never edited).
    Because audits may quote problem text, the overlap scan runs over `docs/history/usaaio/` once at import, with the corpus present; any hit is redacted before commit.
  - The usaaio repository is not modified by this work. Archiving it on GitHub is the author's call, later.
- **D4 — Tooling: ported as one isolated package.**
  - usaaio's `tools/` becomes `tools/aio/` (`checks/`, `publish*`, `publish_theme/`, the mutation verifiers, `audit_curriculum`, the renderers),
    reached through `py4kids-tools --book <aio-id> <command>` and `py4kids-tools --content-model aio <all-books-command>` subcommands that dispatch into it. There is no second console script.
  - Its catalog adapter reads py4kids `books.yaml` (`books_version: 2`) and sees only `content_model: aio` books (D1 maps `number := aio_round`); usaaio's `books_version: 1` loader is dropped.
    Its required-root-files list applies only to those books.
  - **Its tests move to `tools/aio/tests/`** (57 files, about 1,013 tests, plus fixtures), outside the group-free `testpaths`, run by the routed step-2 command. The six content tests usaaio runs in step 7 join that run.
  - **SKIP semantics.** usaaio's exit code 3 is mapped by the dispatcher to a printed `SKIP (<reason>)`. Only one aio skip is permanent, and it is declared (§3): the overlap scan without a local corpus.
    It is **fail-closed where it matters**: `py4kids-tools --book <aio-id> overlap --require-corpus` fails when the corpus is absent,
    and it is required (a) once at import, (b) by `ci-local.sh --all-books`, and (c) before merging any plan that changes aio content, recorded in the plan's verification phase.
    Ordinary branches print the skip; a skip in a plan that touches aio statements is gate-blocking.
  - **Superseded machinery not carried:** the historical-policy clock (`verify_historical_deferred_policy.py`, the `USAAIO_HISTORICAL_VERIFY`/`USAAIO_AS_OF_DATE` guard and its tests),
    and the one-off migration scripts (`renumber-book1-units.py`, `migrate-reference-layout.sh`, `verify-unit-renumbering.py`).
    `scripts/verify-register.py` and `scripts/fetch-reference.sh` are ported.
  - The shared gate scripts stay py4kids': `tools/guard.py` gains the aio roots' unit-id (`NN-<id>`, `B2-0NN-<id>`) and mock-test-id (`rN-NNN`) collision rules; usaaio's own `pre-merge-guard.sh` is not carried.
  - ruff covers `tools/aio/` with the repo's config; lint fixes are mechanical and land in the import plan.
  - **Parity is the acceptance test.** aio-001 records a table mapping every usaaio `ci-local.sh` gate (steps 1–9) to its py4kids destination command,
    and the PASS/SKIP outcome of each on usaaio `a20128f` beside its outcome after import. Every row must match, or differ only by a listed, justified change.
- **D5 — The laws for an `aio` book (normative).**
  An `aio` book is bound by the usaaio laws, which are what its checks enforce:
  - **Baseline:** Calculus AB + basic Python. Nothing used before it is taught (prereq closure), nothing taught without practice (coverage),
    nothing tested that was not taught; aio-dl imports aio-ml concepts only through qualified registry contracts.
  - **Hygiene:** student notebooks carry no solutions and no executed outputs; solution notebooks run top-to-bottom clean with fixed seeds and contain executable asserts.
  - **Manifests** per unit and mock test (concepts, prerequisites, provenance, points, blueprint version and generation parameters); seeded datasets, never opaque blobs.
  - **Provenance:** original problems by default; adaptations carry `adapted-from:`; **no raw past-test papers, no verbatim past-problem text and no hidden test set in the repo** (overlap-checked, guard-refused).
  - **Not applied:** project-first openings, `exercises.ipynb` with a `stretch` cell, per-unit `teacher-notes.md`, checkpoints, the 60–90 min unit budget.
    Their roles are filled by the unit overview's motivation, Set C, `front-matter/for-teachers.md`, mock tests, and the manifests' `estimated_minutes` respectively.
  - The usaaio learner-facing standards move into the book roots: `docs/unit-standards.md`, `docs/mocktest-generation.md` and `docs/curriculum-architecture.md` → `aio-ml/docs/` (shared by both books, referenced from `aio-dl`).
- **D6 — Editions.**
  - `publication: true` on both books. The ported aio publisher builds, from each book's existing `publication.yaml` (usaaio schema, `publication_version: 1`, unchanged):
    `aio-ml`: `student-print`, `student-vol1..3`, `teacher-vol1..3`, `answer-key`; `aio-dl`: `student`, `student-print`, `teacher`, `answer-key`;
    plus `syllabus.pdf`, `handouts/<unit>.pdf`, and `mocktests/<test>-{paper,solutions}.pdf`.
  - Output lands in `output/<id>/<id>-<edition>[-vol<N>].pdf`. Step 5 routes `aio` books to the aio scripts under `tools.ci_scope`'s render/skip logic, through the group (D2).
    Answers outside the Teacher's Edition stay Set A only (`student_answers: {set: A}`).
  - Toolchain (Quarto + lualatex + makeindex) is shared with py4kids; the aio theme stays its own (`tools/aio/publish_theme/`), so the editions look as they do today.
- **D7 — The website: an explicit contract extension of design 012.**
  Both books get `site: true` and a `site.yaml`, in aio-003, after the import and editions are green.
  Design 012 D1 excluded books whose code Pyodide cannot run; this is the extension, and it is a **bundle schema major version** (closed enums change), with consumers updated in the same plan:
  - **Ids and kinds.** The schema's entry-id patterns (`bundle.schema.json:38-47`) and the exporter's prefix parsing (`bundle.py:70,219-221`) gain the aio unit patterns (`NN-<id>`, `B2-0NN-<id>`) and a new kind `mocktest` (`rN-NNN`), gated by `content_model`;
    `site/src/lib/types.ts:16,147` unions widen to match; the global key stays `book/entry/notebook/cell_id`.
  - **Lesson parts.** An aio unit's lesson is its overview `lesson.ipynb` followed by `lessons/NN-*.ipynb`, exported as `lesson.parts[]` (title + blocks each); py4kids books export one part.
    Reading view, navigation, resume/progress keys and slide splitting (slides break at part boundaries) iterate parts (`site/src/lib/entry.ts:163-180`). `review.ipynb` exports as a review page.
  - **Items** are the manifest `practice:` rows, carrying `set`, `type`, `difficulty`.
  - **Answer gating** uses an aio-specific release rule read from `publication.yaml` `student_answers: {set: A}` (Set A `after-attempt`; Sets B and C `none`),
    replacing py4kids' `is_released` for `aio` books (`tools/export/answers.py:820-827`) and enforced by the same `student_answer_sources` leak guard.
  - **Mock tests** are a read-and-attempt view of `test.md` and `problems/` with the rubric; solutions are never shipped (the PDFs print them only in the Teacher's Edition).
  - **Runnable vs. read-only code.** Pyodide runs numpy, pandas, scikit-learn, scipy and matplotlib (seaborn via micropip); it cannot run torch, torchvision or gensim.
    A block gains `runnable: bool` (new field); a block whose cumulative namespace imports an unsupported package is `runnable: false`.
  - **Export-time outputs (new machinery).** Lesson outputs today come from stored `cell.outputs` (`tools/export/lesson.py:131`), and aio notebooks store none (the hygiene law).
    The aio adapter executes each lesson notebook under the `aio` group at export, caches the outputs under `build/aio-outputs/` keyed by the notebook's content hash, and embeds them in the bundle;
    the repo's notebooks stay output-free. `build-site.sh` therefore routes `export` through each book's group, and the export inherits the exec preconditions (D8).
    Measured: aio-ml lessons hold about 680–690 code cells (about 75 touch torch); aio-dl lessons hold 84 (68 touch torch) — aio-dl is mostly read-and-attempt on the web.
  - **Checking.** The classification tool proposes `check-asserts` for portable assert-checked practice, `check-answer` for `mc`/`mc-normal-form`, `check-self` for `proof` and any torch-bound item.
    `site.yaml` starts `classification: proposed`; aio-004/005 confirm the tags.
  - Concepts come from the manifests' `concepts_taught`; the glossary from `back-matter/glossary.md`, plus `back-matter/notation.md` as a reference page.
- **D8 — Dependencies and external artifacts.**
  - A new `aio` dependency group: gensim, ipykernel, jupyter, matplotlib, nbclient, nbformat, numpy, pandas, pyyaml, scikit-learn, seaborn, torch, torchvision
    (torch/torchvision through the existing `pytorch-cpu` explicit index). usaaio's lower bounds (numpy ≥2.5.1, pandas ≥3.0.5, torch ≥2.13, …) are kept;
    aio-001 Phase 1 proves `uv lock` resolves them with the `recsys` and `roar` groups, and declares a `[tool.uv] conflicts` entry if it cannot.
  - **External artifacts.** Known: the GloVe vectors (`gensim.downloader`, aio-ml C5 and C9) and the pretrained ResNet weights (aio-ml C10 `lessons/02-resnet-reading.ipynb`), both into the git-ignored `reference/cache/`;
    aio-dl B2-022…B2-024 also fetch. aio-001 Phase 1 inventories every download in notebooks and tools (artifact, source URL, size, consumers)
    and ships `scripts/aio-provision-cache.sh`, which fills the cache from those public sources and verifies a recorded SHA-256 per artifact.
    **A clean checkout + `aio-provision-cache.sh` + `ci-local.sh` must pass**; that sequence is the aio-001 verification. Replacing downloads with committed, integrity-checked subsets (as recsys did) is a follow-up.
- **D9 — CI budget.** The aio books' notebook execution (about 1,346 notebooks across lessons, practice solutions and mock tests) is the largest cost.
  aio-001 measures it. If the full run exceeds 60 CI-minutes, `tools.ci_scope` scopes aio exec to changed aio paths on ordinary branches,
  and `ci-local.sh --all-books` (required before any aio content merge and for release) runs it in full.

## 3. Governance amendments (precondition — needs the author's explicit authorization)

These edit governance files, so they ship as **one small governance PR before any aio content merges**, and only on the author's explicit approval:
- **AGENTS.md:**
  - "Self-containedness is law" and "Project-first is law" gain: *a book registered `content_model: aio` is bound instead by the aio laws of design 014 §2 D5;
    every gate, the hygiene law, prereq closure, coverage and taught-before-assessed still apply to it.*
  - Hard safeguards gain: *committing raw past-test papers, verbatim past-problem text, or a hidden test set*.
  - Verification gains: *the aio overlap scan's skip without a local corpus is a declared standing skip (design 014 D4); it is fail-closed (`--require-corpus`) for `--all-books` and for any plan changing aio content.*
  - Project Structure lists `aio-ml/` and `aio-dl/`.
- **`docs/architecture/decisions.md`:** append **D-006 — Content models.** D-001 (project-first), D-002 (checkpoints replace mock tests) and D-004 (fresh minimal tooling; usaaio scope inventories, mutation checks and legacy handling deliberately absent)
  govern `py4kids`-model books. For `aio`-model books D-006 **supersedes D-002 and D-004**: they keep mock tests and the usaaio checks, including the mutation verifiers, isolated in `tools/aio/`.
- **`docs/content-review-gate.md`:** the reviewer duties gain an `aio` reading:
  project-first and stretch duties are replaced by Set-ladder integrity (A/B/C difficulty is honest) and mock-test blueprint fidelity;
  the 60–90 min budget duty (6) reads against the manifest's `estimated_minutes`; the baseline duty (7) reads "Calculus AB + basic Python";
  and a no-past-paper duty (the overlap scan ran with `--require-corpus`) is added.

The gate roster is unchanged (3-way, [self]/[sol]/[fable]).

## 4. Roadmap

| Plan | Delivers | Verification |
|---|---|---|
| governance PR | §3 amendments | docs-only |
| **aio-001** Import | Phase 1: dependency resolution (D8) + external-artifact inventory and `aio-provision-cache.sh`. Then registry entries (`content_model`, `aio_round`); snapshot + provisioning (D3); `tools/aio/` and its tests (D4); ci-local routing table (D2); guard rules; CI budget measured (D9) | the D4 parity table, every row matching; clean checkout + provision + `ci-local.sh` green; py4kids books' results unchanged; rename-count report + `test_book_ids` + zero-hit grep; `git ls-files` proves no ignored path is tracked; fidelity diff: imported files byte-identical to usaaio `a20128f` apart from the listed renames; `overlap --require-corpus` over the books and `docs/history/usaaio/` |
| **aio-002** Editions | `publication: true`; step-5 routing; `output/aio-*/` | every edition builds; aio publish-audit passes; page counts within ±2% of the usaaio `a20128f` PDFs (same content, same theme) |
| **aio-003** Site | the D7 contract: schema major bump, id patterns + `mocktest` kind, `lesson.parts[]`, `runnable`, export-time output cache, aio answer-release rule, `build-site.sh` group routing, site types/views; `site: true`, `classification: proposed` | schema + consumer tests for each new part (ids, kinds, parts, runnable, mocktest); leak-guard test (no Set B/C or mock-test solution in any bundle); site-check; py4kids bundles regenerate unchanged apart from the schema version; e2e: read a lesson part, step slides across a part boundary, resume, attempt a Set A item, see a torch block read-only with its output, open a mock test |
| **aio-004 / aio-005** Classification | per-book check-tag confirmation, `classification: confirmed` | site-check in confirmed mode |
| follow-up | committed artifact subsets (D8) | integrity checks |

Each plan passes the 3-way plan-review and content-review gates. aio-001 is a migration, not new content:
its content-review duty is fidelity (the fidelity diff and parity table above), not re-review of the pedagogy.

## 5. Risks

- **Dependency resolution** across `aio`, `recsys` and `roar` (D8). Mitigation: aio-001 Phase 1, before any content copy.
- **CI time** (D9). Mitigation: measured, then scoped; the full run stays mandatory before aio merges.
- **A leaked hidden set or past paper.** Mitigation: the snapshot is `git ls-files`-driven (D3 step A) and provisioning is separate (step B); guard refusals; the tracked-path assertion; the overlap scan over the archive.
- **An overlap scan that silently passes.** Mitigation: `--require-corpus` is fail-closed at import, on `--all-books`, and for every aio-content plan (D4).
- **Rename misses.** Mitigation: `test_book_ids`, the zero-hit grep, the parity table and the full aio exec.
- **Unreachable external artifacts** (a moved URL). Mitigation: recorded checksums fail loudly; the follow-up commits subsets.
- **Theme drift** between the aio and py4kids editions. Accepted: the aio books keep their own look.

## 6. Out of scope

- Converting any aio unit to the py4kids content model, or py4kids content to the aio model.
- New aio content (units, mock tests) — later plans under the same namespace, once the import is green.
- Editing or archiving the usaaio repository.
- Per-unit teacher notes for aio books (additive later work if the books are taught to a class).
- Running torch in the browser.

## Design Review

### Round 1 (on v1, commit 21b7e3e)

- **[self] MUST** — group-free step-2 pytest would collect the aio suite → **[FIXED]** D4 (tests in `tools/aio/tests/`), D2 table.
- **[self] MUST** — all-book iterations would hit aio books → **[FIXED]** D2 "All-book iterations filter".
- **[self] NIT** — export-time execution needs caching → **[FIXED]** D7 output cache.
- **[sol] REJECT.**
  1. BLOCKER overlap scan passes without corpus → **[FIXED]** D4 SKIP semantics, `--require-corpus`, §3 amendment.
  2. BLOCKER `number: 4` breaks usaaio routing → **[FIXED]** D1 `aio_round` + consumer inventory.
  3. MUST test location vs isolation → **[FIXED]** D4.
  4. MUST usaaio gates beyond per-book checks → **[FIXED]** D2 step 4b, D4 parity table.
  5. MUST external artifacts beyond GloVe (ResNet weights) → **[FIXED]** D8 inventory + provisioning + clean-checkout verification.
  6. MUST site contract larger than stated → **[FIXED]** D7 rewritten as an explicit schema-major contract; aio-003 row.
  7. NIT two-step import inventory → **[FIXED]** D3 steps A/B.
- **[fable] APPROVE WITH NITS.**
  1. MUST incomplete routing (cell-lint, lesson-outputs, turtle checks, build-pdf, publish-audit without group) → **[FIXED]** D2 table.
  2. MUST step 2 collection / per-book pytest exit 5 → **[FIXED]** D2, D4.
  3. MUST `number` drives usaaio tooling → **[FIXED]** D1.
  4. MUST py4kids registry tests pin layout/classification → **[FIXED]** D2 registry-tests bullet.
  5. MUST old-id guard vs imported tests → **[FIXED]** D3 renames + acceptance proof.
  6. MUST overlap skip semantics + `fetch-reference.sh` → **[FIXED]** D3 step B, D4.
  7. MUST website gaps (closed unions, `runnable`, export-time execution, group-free export, answer gating) → **[FIXED]** D7.
  8. NIT governance duties 6/7, D-006 supersedes D-004 → **[FIXED]** §3.
  9. NIT counts → **[FIXED]** 309 notebooks; cell counts stated as approximate.
  10. NIT overlap over the archive; explicit CSV rules → **[FIXED]** D3.

## Revision history

- v1 (2026-10-31): first draft.
- v2 (2026-10-31): folds round 1 (above).
