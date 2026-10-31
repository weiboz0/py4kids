# Design 014 — The AI Olympiad books (migrating usaaio into py4kids)

**Status:** DRAFT — v1 (2026-10-31). Awaiting the design-review gate and the author's approval.
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

  | usaaio id | py4kids id = root | number | title (unchanged) | subtitle (unchanged) | depends_on |
  |---|---|---|---|---|---|
  | `book1` | `aio-ml` | 4 | Machine Learning for the AI Olympiad | Round 1: Foundations, Models, and Practice | `[]` |
  | `book2` | `aio-dl` | 4 | Deep Learning for the AI Olympiad | Round 2: Transformers, Generative Models, and Open-Ended Modeling | `[aio-ml]` |

  - `number` is a series ordinal only (it drives no tooling); both books share 4, as the two Book-1 variants share 1.
  - The ids are new and collide with no existing id, folder or PDF stem.
    The usaaio ids cannot be kept: `book1`/`book2` are py4kids' own pre-plan-091 ids, which `tools/guard.py` `TRANSITION` still maps to `python-projects`/`usaco-bronze`,
    and a legacy `book1/` folder of py4kids run-time files exists at the repo root (untouched by this design).
  - `aio-ml` has no py4kids dependency: its baseline (Calculus AB + basic Python) is declared in its own standards (§5), not imported from `python-projects`.
- **D2 — A content-model key, not a pile of exemptions.**
  - `books.yaml` gains a value key `content_model` (absent = `py4kids`; the only other value is `aio`).
    It is read like `dependency_group`: a value, on its own line in ci-local step 1, never a boolean flag.
  - **Every py4kids content check that today runs unconditionally is routed by content model.**
    A `content_model: aio` book runs the ported aio checks (D4) instead of hygiene/structure/noexec/milestone/exec/manifest/prereq/coverage/concept-scan/stretch,
    and the aio handout/syllabus build instead of `build-pdf.sh`'s per-`exercises.ipynb` handouts.
  - The feature flags keep their meaning and apply across models: `publication` (editions, D6) and `site` (website, D7).
    `judge`, `patterns`, `acsl` and `labs` are rejected on an `aio` book by the registry check (they presuppose the py4kids unit layout).
  - Tools key on `content_model` and on flags, never on book ids — including the ported tools, whose two hard-coded `book1`/`book2` branches (schedule) are rewritten to key on registry data.
- **D3 — A snapshot import, history left in usaaio.**
  - The content is copied as a snapshot of usaaio `a20128f`; the import commit message and `aio-ml/IMPORTED.md` / `aio-dl/IMPORTED.md` record the source repo and SHA.
    Squash-merge would flatten imported history anyway, and the usaaio repo stays as the history of record.
  - **Not imported:** `book*/build/`, `output/**` PDFs, the untracked `book1/units/C10-competition-craft/` (stray practice CSV outputs), and every git-ignored path.
  - **Imported but kept git-ignored** (copied locally so the overlap check can run, never committed):
    `<book>/reference/*` except `.gitkeep` and `analysis.md` (raw past papers — copyright), `reference/cache/` (GloVe download cache),
    and the hidden test sets (`units/18-C11-competition-craft/data/heldout.csv`, `mocktests/r1-001/data/p09_heldout.csv`) plus the C11 practice output CSVs.
    The `.gitignore` rules move over verbatim with the roots renamed, and `tools/guard.py` gains them as tracked-path refusals.
  - **Renames inside the content:** qualified ids `book1:<id>` → `aio-ml:<id>` (manifests and `book2/syllabus.md` `imports:`/`evidence_imports:`),
    the 331 book2 remediation links `../../../../book1/units/...` → `../../../../aio-ml/units/...`, and `USAAIO_BOOK_ROOT` → `AIO_BOOK_ROOT`.
    Unit folder names and unit ids (`01-F1-scientific-python`, `B2-019-attention-transformers`) are unchanged.
    The rename is one scripted, reviewed substitution with a before/after count report, not hand edits.
  - The usaaio repository is not modified by this work. Archiving it on GitHub is the author's call, later.
- **D4 — Tooling: ported as one isolated package.**
  - usaaio's `tools/` becomes `tools/aio/` (`tools/aio/checks/`, `publish*`, `publish_theme/`, the mutation verifiers, `audit_curriculum`, the renderers),
    reached through `py4kids-tools --book <aio-id> <check>` subcommands that dispatch into it. There is no second console script.
  - Its catalog adapter reads py4kids `books.yaml` (`books_version: 2`) and sees only `content_model: aio` books; usaaio's own `books_version: 1` loader is dropped.
    Its required-root-files list (syllabus, the five curriculum YAMLs, `mocktests/blueprint.yaml`, `docs/course-structure.md`) applies only to those books.
  - Its tests become `tests/aio/` (57 files, about 1,013 tests) with ids renamed; they run in ci-local step 2 under the `aio` group.
  - **Superseded machinery not carried:** the historical-policy clock (`verify_historical_deferred_policy.py`, the `USAAIO_HISTORICAL_VERIFY`/`USAAIO_AS_OF_DATE` guard and its tests),
    and the one-off migration scripts (`renumber-book1-units.py`, `migrate-reference-layout.sh`, `verify-unit-renumbering.py`).
    `scripts/verify-register.py` is ported.
  - The shared gate scripts stay py4kids': `scripts/pre-merge-guard.sh`/`tools/guard.py` gain the aio roots' unit-id and mock-test-id collision rules;
    usaaio's own `pre-merge-guard.sh` is not carried.
  - ruff covers `tools/aio/` and `tests/aio/` with the repo's config; lint fixes are mechanical and land in the import plan.
- **D5 — The laws for an `aio` book (normative).**
  An `aio` book is bound by the usaaio laws, which are what its checks enforce:
  - **Baseline:** Calculus AB + basic Python. Nothing used before it is taught (prereq closure), nothing taught without practice (coverage),
    nothing tested that was not taught; book2 imports book1 concepts only through qualified registry contracts.
  - **Hygiene:** student notebooks carry no solutions and no executed outputs; solution notebooks run top-to-bottom clean with fixed seeds and contain executable asserts.
  - **Manifests** per unit and mock test (concepts, prerequisites, provenance, points, blueprint version and generation parameters); seeded datasets, never opaque blobs.
  - **Provenance:** original problems by default; adaptations carry `adapted-from:`; **no raw past-test papers and no verbatim past-problem text in the repo** (overlap-checked).
  - **Not applied:** project-first openings, `exercises.ipynb` with a `stretch` cell, per-unit `teacher-notes.md`, checkpoints.
    Their roles are filled by the unit overview's motivation, Set C, `front-matter/for-teachers.md`, and mock tests respectively.
  - The usaaio learner-facing standards move into the book roots: `docs/unit-standards.md` and `docs/mocktest-generation.md` → `aio-ml/docs/` (shared by both books, referenced from `aio-dl`),
    `docs/curriculum-architecture.md` → `aio-ml/docs/`. Retained usaaio designs, plans, audits and reviews are archived read-only under `docs/history/usaaio/` (outside every guard numbering rule; never edited).
- **D6 — Editions.**
  - `publication: true` on both books. The ported aio publisher builds, from each book's existing `publication.yaml` (usaaio schema, `publication_version: 1`, unchanged):
    `aio-ml`: `student-print`, `student-vol1..3`, `teacher-vol1..3`, `answer-key`; `aio-dl`: `student`, `student-print`, `teacher`, `answer-key`;
    plus `syllabus.pdf`, `handouts/<unit>.pdf`, and `mocktests/<test>-{paper,solutions}.pdf`.
  - Output lands in `output/<id>/<id>-<edition>[-vol<N>].pdf` — the py4kids layout with the new ids. ci-local step 5 routes `aio` books to the aio `build-book.sh`/`publish_audit`
    under `tools.ci_scope`'s existing render/skip logic. Answers outside the Teacher's Edition stay Set A only (`student_answers: {set: A}`).
  - Toolchain (Quarto + lualatex + makeindex) is already the py4kids one; the aio theme stays its own (`tools/aio/publish_theme/`), so the editions look as they do today.
- **D7 — The website.** Both books get `site: true` and a `site.yaml`, in a dedicated plan (aio-003) after the import and editions are green.
  This extends design 012, whose D1 excludes books whose code Pyodide cannot run; the extension is:
  - **An aio export adapter** (`tools/export/aio.py`) produces the existing bundle schema from the aio layout:
    a unit's lesson is its overview `lesson.ipynb` followed by `lessons/NN-*.ipynb` as **lesson parts** (a schema minor bump: `lesson.parts[]`, each with its own title and blocks, slides split at part boundaries);
    items are the manifest `practice:` rows, carrying `set`, `type` and `difficulty`; `review.ipynb` exports as a review page.
  - **Mock tests** become a new entry kind `mocktest` (schema minor bump): a read-and-attempt view of `test.md` and `problems/`, rubric visible, solutions never shipped
    (matching the PDFs, which print them only in the Teacher's Edition).
  - **Answer gating** follows the editions: Set A solutions `after-attempt`, Sets B and C `none` — the same leak guard (`student_answer_sources`) reading the same selector.
  - **Runnable vs. read-only code.** Pyodide runs numpy, pandas, scikit-learn, scipy and matplotlib (seaborn via micropip); it cannot run torch, torchvision or gensim.
    A code block whose cumulative namespace imports an unsupported package is exported `runnable: false`;
    such lessons show **stored outputs captured at export time** by executing the notebook in the `aio` group (the notebooks in the repo stay output-free, as the hygiene law requires).
    Measured today: aio-ml lessons hold 693 code cells (78 touch torch); aio-dl lessons hold 84 (68 touch torch) — aio-dl is mostly a read-and-attempt book on the web.
  - **Checking.** The classification tool proposes `check-asserts` for portable assert-checked practice, `check-answer` for `mc`/`mc-normal-form`, `check-self` for `proof` and any torch-bound item.
    `site.yaml` starts `classification: proposed`; per-book content plans confirm the tags.
  - Concepts come from the manifests' `concepts_taught`, the glossary from `back-matter/glossary.md`, plus `back-matter/notation.md` as a reference page.
  - The site deploys with the other books from the same release tags (design 012 D1); no aio-specific site code beyond rendering the two new schema parts.
- **D8 — Dependencies.** A new `aio` dependency group: gensim, ipykernel, jupyter, matplotlib, nbclient, nbformat, numpy, pandas, pyyaml, scikit-learn, seaborn, torch, torchvision
  (torch/torchvision through the existing `pytorch-cpu` explicit index). ci-local runs every `aio` book command through `uv run --group aio`.
  usaaio's lower bounds (numpy ≥2.5.1, pandas ≥3.0.5, torch ≥2.13, …) are kept; the import plan proves `uv lock` resolves them together with the `recsys` and `roar` groups,
  and declares a `[tool.uv] conflicts` entry if it cannot.
  **Network:** the aio-ml C5 notebooks download GloVe through `gensim.downloader` into the git-ignored `reference/cache/`.
  That stays as is in the import (a warm cache is a precondition of exec, as it is in usaaio today); replacing it with a committed, integrity-checked subset like recsys's is a follow-up, not a blocker.
- **D9 — CI budget.** The aio books' notebook execution (about 1,346 notebooks across lessons, practice solutions and mock tests) is the largest cost.
  The import plan measures it. If the full run exceeds 60 CI-minutes, `tools.ci_scope` scopes aio exec to changed aio paths on ordinary branches,
  and `ci-local.sh --all-books` (required before any aio content merge and for release) runs it in full. The 20 s per-notebook timeouts usaaio applies to aio-dl practice solutions are kept.

## 3. Governance amendments (precondition — needs the author's explicit authorization)

These edit governance files, so they ship as **one small governance PR before any aio content merges**, and only on the author's explicit approval:
- **AGENTS.md:**
  - The "Self-containedness is law" and "Project-first is law" bullets gain: *a book registered `content_model: aio` is bound instead by the aio laws of design 014 §2 D5;
    every gate, the hygiene law, prereq closure, coverage and taught-before-assessed still apply to it.*
  - Hard safeguards gain: *committing raw past-test papers or verbatim past-problem text, or a hidden test set*.
  - Project Structure lists `aio-ml/` and `aio-dl/`.
- **`docs/architecture/decisions.md`:** append **D-006 — Content models.** D-001 (project-first), D-002 (checkpoints replace mock tests) and D-004 (no usaaio machinery)
  govern `py4kids`-model books; `aio`-model books keep mock tests and the usaaio checks, isolated in `tools/aio/`.
- **`docs/content-review-gate.md`:** the reviewer duties gain an `aio` column: project-first and stretch duties are replaced by
  Set-ladder integrity (A/B/C difficulty is honest), mock-test blueprint fidelity, and the no-past-paper overlap duty.

The gate roster is unchanged (3-way, [self]/[sol]/[fable]).

## 4. Roadmap

| Plan | Delivers | Verification |
|---|---|---|
| governance PR | §3 amendments | docs-only |
| **aio-001** Import | registry entries + `content_model`; snapshot copy with renames (D3); `tools/aio/` + `tests/aio/` (D4); `aio` group (D8); ci-local routing (D2); guard rules; CI budget measured (D9) | ci-local green: every aio check, all aio tests, full aio notebook exec; py4kids books' results unchanged; a rename-count report; `git ls-files` proves no ignored path is tracked |
| **aio-002** Editions | `publication: true`; step-5 routing; `output/aio-*/` | every edition builds; publish-audit passes; page counts within ±2% of the usaaio `a20128f` PDFs (same content, same theme) |
| **aio-003** Site export + render | aio adapter, `lesson.parts[]`, `mocktest` kind, `runnable: false` + export-time outputs, schema bump, `site: true` with `classification: proposed` | export schema + consumer tests; site-check; e2e: read a lesson part, step slides, attempt a Set A item, open a mock test, see torch cells read-only |
| **aio-004 / aio-005** Classification | per-book check-tag confirmation, `classification: confirmed` | site-check in confirmed mode |
| follow-up | committed GloVe subset (D8) | glove-integrity-style check |

Each plan passes the 3-way plan-review and content-review gates. aio-001 is a migration, not new content:
its content-review duty is fidelity (the imported books are byte-identical to usaaio `a20128f` apart from the listed renames), not re-review of the pedagogy.

## 5. Risks

- **Dependency resolution** across `aio`, `recsys` and `roar` (D8). Mitigation: proved in aio-001 Phase 1, before any content copy.
- **CI time** (D9). Mitigation: measured, then scoped; the full run stays mandatory before aio merges.
- **A leaked hidden set or past paper.** Mitigation: the copy is driven by usaaio's `git ls-files`, not a directory copy; guard refusals; a tracked-path assertion in the verification phase.
- **Rename misses** (a stray `book1/` path or `book1:` id). Mitigation: a post-rename grep that must return zero hits outside `docs/history/usaaio/`, plus the full aio test and exec suite.
- **Theme drift** between the aio and py4kids editions. Accepted: the aio books keep their own look; unifying themes is out of scope.

## 6. Out of scope

- Converting any aio unit to the py4kids content model, or py4kids content to the aio model.
- New aio content (units, mock tests) — later plans under the same namespace, once the import is green.
- Editing or archiving the usaaio repository.
- Per-unit teacher notes for aio books (additive later work if the books are taught to a class).
- Running torch in the browser.

## Design Review

(pending)

## Revision history

- v1 (2026-10-31): first draft.
