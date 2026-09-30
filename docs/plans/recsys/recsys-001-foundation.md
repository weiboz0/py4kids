# Plan recsys-001 — Foundation: registry, baseline tooling, guard extension, data generators, `bookrec` package

**Design:** `docs/designs/009-recsys-book.md` (v2, gate CLOSED). **Autopilot** per AGENTS.md. **v2** folds the
round-1 plan-review ([sol] REJECT + [fable] APPROVE WITH NITS).
Foundation for the advanced `recsys` book: **tooling + registration + scaffolding + seeded data generators + the
`bookrec` package skeleton**. Ships **no student units/projects/checkpoints** (→ `recsys-002+`) and commits **no
real-catalog data** (license-gated). Plans are `docs/plans/recsys/recsys-NNN`; this plan adds the guard support
(the one-file chicken-and-egg of design 009 §12 is accepted).

## Goal
A registered, CI-green `recsys` book in **buildout** state with: a namespace-aware guard, the assumed-baseline
tooling, an isolated CPU dependency group, seeded catalog+interaction generators (exposed ground-truth), the
license-gated real-slice script (no real data committed), and the importable `bookrec` protocol/registry — so
`recsys-002+` can author units against a working substrate.

## Global constraints
Determinism: one `numpy.random.default_rng(seed)` threaded through; `PYTHONHASHSEED`; fixed float precision +
normalized gzip `mtime`; reproducibility is "identical under `uv.lock`" (NEP-19: numpy streams are not frozen
across releases). CPU-only. No real catalog data in the repo. `[glm]` is skipped per the standing plan-091 user
decision (roster is otherwise 4-way).

## Phases

### Phase A — namespace-aware pre-merge-guard
The collision check scans only depth-1 `docs/plans/*.md` matching `^[0-9]{3}(?=-)` and, in `--pr` mode, unions the
live **WORKTREE** with a freshly-fetched **origin/main** (`pre-merge-guard.sh:15,33`), deduping identical pathnames.
- Extract the collision logic into an importable **`tools/guard.py`** (injectable path sets) with a thin bash
  wrapper, so it is unit-testable (today `tests/test_books.py`/`test_book_ids.py` only read the script text).
- Generalize: for each `docs/plans/<ns>/` subdir, enforce uniqueness of `^<ns>-[0-9]{3}(?=-)` (so `recsys-NNN` is
  guarded and the next namespaced book needs no further edit); keep the top-level `^[0-9]{3}` guard (protects
  reserved 092/093); preserve the WORKTREE ∪ fetched-origin/main ref model and pathname dedup.
- **Tests:** duplicate `recsys-001` within one ref fails; across WORKTREE/origin-main fails; the same pathname in
  both refs dedups (no false collision); distinct numbers pass; top-level `[0-9]{3}` still enforced.
**Verify:** `bash scripts/pre-merge-guard.sh --pr` OK; new `tools/guard.py` tests pass.

### Phase B — assumed-baseline mechanism (`baseline.yaml`)
Add `assumed_baseline(root, book)` to `tools/books.py` plus `known_baseline()` = `dependency_baseline()` ∪
`assumed_baseline()`, and **swap all four consumers** to `known_baseline()`: `tools/curriculum.py:356` (referenced),
`:499` (prereq ordering), `:562` (checkpoint), and `tools/concept_scan.py:1072` (scan allowed set — v1 AND v2).
Keep `dependency_baseline()` semantics ("introduced by dependencies") intact.
- **`<book>/curriculum/baseline.yaml` schema:** `baseline_version: 1`; `entries: [{id, name}]`; kebab id (same regex
  as `curriculum.py:283`); an assumed id MUST NOT also be in the book's own `concepts.yaml` (else "known but
  uncredited" contradicts "must be introduced"). Fail closed on malformed top level, malformed/duplicate/invalid
  entries; absent file = today's behavior (opt-in).
- **Checkpoint policy:** assumed = *legal to use, not assessable* (design §2). Emit a finding when a checkpoint
  `practices` a baseline id (dependency-book concepts stay assessable as today).
- **Tests:** assumed id usable in requires/scan with no prereq/coverage/scan finding and no coverage obligation;
  non-baseline id still flagged; checkpoint-practices-baseline flagged; malformed/dup/absent; id-in-own-concepts
  contradiction.
**Verify:** targeted `pytest` over prereq, coverage, concept-scan, checkpoint assessment.

### Phase C — CPU dependency group + ci-local routing
- `pyproject.toml` `[dependency-groups] recsys`: `numpy`, `pandas`, `matplotlib`, `scikit-learn`, `torch`,
  `faiss-cpu`. **torch pinned to the CPU wheel:** `[[tool.uv.index]] name="pytorch-cpu"
  url="https://download.pytorch.org/whl/cpu" explicit=true` + `[tool.uv.sources] torch = { index = "pytorch-cpu" }`
  (platform markers if macOS matters) — avoids the multi-GB `nvidia-*` CUDA tree. Prefer **faiss-cpu** (py3.12
  wheels) over hnswlib (sdist/compiler). `psycopg` + `gensim` slice/derivation-only; `implicit` optional — none on
  the CI exec path.
- **Routing (the key fix):** `ci-local.sh:44` runs the whole `tests/` suite with plain `uv run pytest` BEFORE any
  `--group recsys` step, and `uv run` is an inexact sync — so recsys tests that import numpy/torch/`bookrec` would
  ImportError. Therefore **recsys tests live OUTSIDE `tests/`** (under `recsys/projects/bookrec/tests/` and
  `recsys/data/tests/`) and run in a **routed per-book step** `uv run --group recsys pytest <those paths>`; the
  global `tests/` run stays group-free. Notebook/exec commands for `recsys` also run under `uv run --group recsys`.
- Isolation is honest: one lock + one `.venv`, so the group is *selected/installed* but torch/faiss are not
  *required by* or *imported in* the other books' commands (design §7 single-lock caveat).
**Verify:** `uv sync --group recsys` resolves to CPU torch; the group-free `uv run pytest -q` over `tests/` does NOT
require the group; the routed recsys test step passes.

### Phase D — book registration + skeleton (buildout state)
- `books.yaml`: `id: recsys`, `number: 3`, `root: recsys`, title "Applied Python: Recommendation Systems",
  subtitle "Build a book recommender — from counting to neural retrieval", `depends_on: [python-projects]`,
  `lesson_budget: [30, 60]`, **`buildout: true`** (no `patterns`/`judge`/`publication`). `buildout` is required:
  a `depends_on` book gets `concept_minimum = 1` (`books.py:105`) so an empty `concepts.yaml` fails
  (`curriculum.py:263`), a non-empty map-less `concepts.yaml` fails "never introduced" (`curriculum.py:384`), and
  the lesson-budget minimum fails until units land (`curriculum.py:345`) — all waived by buildout (python-concepts
  used this, removed in plan 078). Name the future plan that removes `buildout` once Part 1 units land.
- Create `recsys/`: `syllabus.md` (two-part arc prose — do NOT backtick future `unit-NN` ids, or
  `syllabus_findings` treats them as stale rows, `curriculum.py:598`); `curriculum/concepts.yaml` with **≥1
  concept** (the retrieve-then-rank framing concept) so `concept_minimum` is met; `curriculum/coverage-map.yaml`
  (`map_version: 1`, entries added as units land); `curriculum/baseline.yaml` (assumed advanced-Python / math /
  numerical-Python ids); `reference/`, learner-facing `docs/`; and `units/` `projects/` `checkpoints/` each with a
  **`.gitkeep`** (dirs must exist — `notebooks.py:126/143/160` fail closed on a missing dir; no stub unit needed).
- Update `tests/test_books.py` (id list +`recsys`; title/subtitle assertions; per-flag book lists — recsys has no
  flags) and add the `## output/recsys/` section to `output/README.md`.
**Verify:** `ci-local.sh` registry/structure/curriculum steps pass for `recsys` in buildout; `build-pdf.sh` builds
`output/recsys/syllabus.pdf` over zero units.

### Phase E — seeded generators + license-gated real-slice script
- Location: **`recsys/data/`** with seeded `gen_catalog.py` + `gen_interactions.py` ("seeded generation scripts,
  never opaque blobs"). Decide committed-vs-regenerated: **regenerate in CI** under a required check (preferred);
  if any artifact is committed, add a required regenerate-and-checksum check (design §9). Default sizes within
  §7 ceilings (5–20k books / 5k readers / ~200k interactions) with a generation-time budget.
- Interaction generator implements the design §6 signal table (feature-derived taste, popularity bias,
  timestamps/ordered sessions/drift, exposure process + implicit positives + sampled negatives, cold-item/
  cold-reader partitions, leakage-safe temporal splits) and **exposes ground-truth**.
- **Real-slice script `recsys/data/slice_books.py`** (`psycopg`/`gensim`, derivation-only): **fails closed** unless
  given an explicit recorded permissive source/license attestation, or fed a local Open Library fallback input;
  records source/version, query params, deterministic ordering, normalization/dedup, row counts, schema/data-
  dictionary, checksums (§6). Default output is **gitignored / non-promotable**; commits no real catalog.
- **Tests (invariants, model-free):** observed positives enriched vs. the exposed true-score matrix
  (AUC / rank-correlation above threshold); measurable popularity skew; per-reader leakage-free splits
  (max train ts < min val ts < min test ts); cold partitions disjoint from train; sessions ordered; determinism
  under `uv.lock`.
**Verify:** seeded generation reproduces identically under the lock; invariant tests green; a tracked-file check
proves no real catalog artifact is in the branch.

### Phase F — the `bookrec` package
- `recsys/projects/bookrec/` with `pyproject.toml` (hatchling), a `bookrec` entry in the `recsys` group, and
  `[tool.uv.sources] bookrec = { path = "recsys/projects/bookrec", editable = true }` so notebooks `import bookrec`
  even with the unit dir as cwd. (`project_dirs` globs only `project-*` (`notebooks.py:167`), so `bookrec/` is
  ignored by the content checks — state it.)
- `RetrievalPath` protocol: stable int item ids, `fit`/`load`, `retrieve(q, ctx, k) -> [(item_id, score,
  provenance)]`, deterministic tie-break (id order), candidate limit `k`, **calibrated/normalized score semantics
  before blending**, and **per-path artifact ownership/versioning**; a path **registry**; `blend`; `rank`;
  `evaluate`; catalog loading. The popularity path is a **test fixture only** (a real popularity impl is Unit 2).
- Add `recsys/projects/bookrec` + `recsys/data` to the `ruff check` scope.
- **Tests:** stable ids, `k`, tie-break, provenance, score normalization/calibration, registry duplicate handling,
  catalog load, blend, rank, hit-rate@k evaluate.
**Verify:** routed `uv run --group recsys pytest recsys/...` green; deterministic.

### Phase G — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN with `recsys` registered (buildout, `.gitkeep` dirs, routed
recsys tests under `--group recsys`, group-free `tests/` unaffected); `tools/guard.py` + baseline + generator-
invariant + `bookrec` tests pass; determinism (seeds/threads/lock) confirmed; `bash scripts/pre-merge-guard.sh
--pr` OK; tracked-file assertion: no real catalog artifact on the branch. **Precondition:** resolve the untracked
`book1/` leftover first (see Blockers) — the guard's WORKTREE scan normalizes `book1/`→`python-projects/` and would
report duplicate unit numbers.

## Blockers / preconditions
- **Untracked `book1/` stray** (present since session start; a stale pre-rename leftover, not in `books.yaml`).
  The guard's WORKTREE scan + `test_book_ids.py` filesystem scan may choke on it (duplicate unit numbers). Per
  AGENTS.md ("ask before discarding leftovers") this is surfaced to the user before Phase G.
- **Data license** (design §6): no real slice commits until the author confirms the `books` DB origin/license or
  the Open Library fallback is used; CI/committed data stays synthetic.

## Out of scope (verification-phase exemption)
No student units/projects/checkpoints ship (→ `recsys-002+`, each with its own verification phase), so the
unit-shipping verification rule is satisfied by shipping none; Phase G is this plan's verification. No real-catalog
slice commit (license-gated); no GPU; no served API; no neural model (Part 2); no GloVe subset (lands with U7).
**No stub unit** is added — `buildout: true` is the mechanism for the not-yet-populated state.
Design 009's closing line still lists "Unit 1" under `recsys-001`; this plan records the **no-unit override**, and a
one-line design-009 reconciliation is a separate follow-up.

## Plan Review

4-way gate ([glm] skipped, standing plan-091 user decision).

### Round 1 (on v1)
- **[sol]:** REJECT — 8 Must: (A) guard ref model is WORKTREE∪fetched-origin/main + needs a test harness; (B)
  baseline must union into concept-scan + checkpoint too (4th site `concept_scan.py:1072`), define schema; (C) the
  global `uv run pytest` runs before the group so recsys tests ImportError — route them; verification uses `uv sync
  --group recsys`; (C/F) real packaging contract for `bookrec`; (D) use `buildout: true` (+ update
  `tests/test_books.py`), no stub, no general relaxation; (E) license gate must be fail-closed in the script +
  Phase-G tracked-file assertion; (F) add per-path artifact ownership/versioning + calibrated scores, popularity as
  fixture; (review) `Content Review: N/A` is wrong — tooling gets a roster code review. + Nice: reconcile the stale
  design-009 Unit-1 line.
- **[fable]:** APPROVE WITH NITS — 5 Must (ci-local pytest ordering; `buildout:true` + `.gitkeep` + `concept_minimum`
  ≥1 concept; `tests/test_books.py`/`output/README.md` updates; **torch CPU index source** or CUDA multi-GB;
  faiss-cpu over hnswlib) + Should (single `known_baseline()` swapping all 4 sites; baseline schema + checkpoint
  policy; guard test harness via importable `tools/guard.py`; concrete generator-invariant tests + NEP-19/mtime
  determinism; `bookrec` packaging + tests + ruff scope; Content-Review not N/A) + Nice (isolation wording;
  syllabus backtick caveat; sequencing; the `book1/` stray).
- **[self]:** APPROVE WITH NITS — flagged the empty-book ci-local viability (now resolved via `buildout`) and the
  dependency-isolation reality; both folded.
- **[glm]:** skipped.
- **Round-1 outcome:** NOT consensus (1 REJECT). v2 folds all Must + Should items (this revision).

### Round 2 (on v2)
- **[self]:** _(pending)_ · **[sol]:** _(pending)_ · **[fable]:** _(pending)_ · **[glm]:** skipped.

## Content Review
Pre-PR round is a **conventional code review of `tools/`, `scripts/`, the generators, and the `bookrec` package by
the gate roster** (`docs/content-review-gate.md` — tooling changes get code review in the same round). NOT N/A.

## Post-Execution Report
_(pending)_
