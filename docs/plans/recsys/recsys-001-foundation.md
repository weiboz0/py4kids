# Plan recsys-001 — Foundation: registry, baseline tooling, guard extension, data generators, `bookrec` package

**Design:** `docs/designs/009-recsys-book.md` (v2, gate CLOSED). **Autopilot** per AGENTS.md.
This is the **foundation** for the advanced `recsys` book ("Applied Python: Recommendation Systems").
It ships **tooling + book registration + scaffolding + the seeded data generators + the `bookrec` package skeleton**.
It ships **no student units/projects/checkpoints** — those land in `recsys-002+` (design 008 cadence).
Plans are namespaced under `docs/plans/recsys/` as `recsys-NNN`; this plan itself adds the guard support for that
(the one-file chicken-and-egg noted in design 009 §12 is accepted).

## Goal

A registered, CI-green `recsys` book skeleton with: the assumed-baseline tooling mechanism, a namespace-aware
pre-merge-guard, an isolated dependency group, the seeded synthetic catalog + interaction generators (with exposed
ground-truth), the license-gated real-slice script, and the importable `bookrec` package protocol/registry — so
`recsys-002+` can author units against a working substrate.

## Phases

### Phase A — pre-merge-guard: namespace-aware plan numbering
`scripts/pre-merge-guard.sh` collision check scans only `.md` files **directly** under `docs/plans` (depth-1) and
matches `^[0-9]{3}(?=-)` (`pre-merge-guard.sh:83-92`); nested `docs/plans/recsys/recsys-NNN-*.md` evade both.
- Extend the check to also collect `docs/plans/recsys/*.md` and enforce uniqueness of the `recsys-NNN` stem
  (regex `^recsys-[0-9]{3}(?=-)`), unioned across the same refs (merge-base + HEAD) it already compares.
- Keep the existing top-level `docs/plans/*.md` `[0-9]{3}` guard intact (so reserved plans 092/093 stay protected).
- **Tests:** extend `tests/` with cases proving a duplicate `recsys-001` across refs fails and distinct numbers pass.
**Verification:** `bash scripts/pre-merge-guard.sh --pr` OK; new guard tests pass.

### Phase B — assumed-baseline mechanism (`baseline.yaml`)
Advanced books assume concepts (advanced-Python, math, numerical-Python, library primitives) that `depends_on`
does not supply. Add a book-local **`<book>/curriculum/baseline.yaml`** (a list of assumed concept ids + names).
- In `tools/curriculum.py` / `tools/books.py`, union `baseline.yaml` ids into the **"known"** set used by
  prereq-closure and coverage (alongside `dependency_baseline()` at `curriculum.py:~282/425/488`), so assumed ids
  are legal to use but earn **no `introduces`/practice credit** and never count toward coverage.
- Fail closed on a malformed `baseline.yaml`; the field is **opt-in** (absent = today's behavior; other books
  unaffected).
- **Tests:** a book with a `baseline.yaml` may `require`/use an assumed id with no prereq finding and no coverage
  obligation; a non-baseline id still triggers closure findings.
**Verification:** targeted `pytest` for the new loader + prereq/coverage behavior.

### Phase C — dependency isolation + ci-local routing
- Add `[dependency-groups] recsys` to `pyproject.toml`: `numpy`, `pandas`, `matplotlib`, `scikit-learn`,
  `torch` (CPU), `faiss-cpu` (or `hnswlib`). `psycopg` + `gensim` are slice/derivation-only; `implicit` optional —
  none on the CI exec path.
- Route this book's flagged checks through `uv run --group recsys` in `scripts/ci-local.sh` (per-book), so the
  other books' checks do not install/run the heavy deps. Document the single-lock caveat (design 009 §7).
**Verification:** `uv sync` resolves; `ci-local.sh` runs the recsys book's checks under the group without pulling
torch/faiss into the other books' check invocations.

### Phase D — book registration + skeleton
- `books.yaml`: add `id: recsys`, `number: 3`, `root: recsys`, title "Applied Python: Recommendation Systems",
  subtitle "Build a book recommender — from counting to neural retrieval", `depends_on: [python-projects]`,
  `lesson_budget: [30, 60]` (whole-book total), **no** `patterns`/`judge`/`publication` flags.
- Create `recsys/`: `syllabus.md` (the two-part arc), `curriculum/concepts.yaml` (v1, the book's own concept ids),
  `curriculum/coverage-map.yaml` (`map_version: 1`, entries added as units land), `curriculum/baseline.yaml`
  (the assumed advanced-Python/math/numerical-Python ids), `reference/`, learner-facing `docs/`, and empty
  `units/` `projects/` `checkpoints/` (populated by `recsys-002+`).
- If `ci-local`/structure requires ≥1 unit or ≥1 coverage entry for a registered book, make the base checks
  tolerate a not-yet-populated book (a foundation state), rather than shipping a throwaway unit.
**Verification:** `ci-local.sh` registry/structure steps pass for `recsys` in its empty-book foundation state.

### Phase E — seeded data generators + license-gated real-slice script
- **Synthetic catalog generator** (`recsys/.../assets` or a book-level `data/` gen script): seeded, realistic book
  catalog (title/author(s)/subjects/year/etc.) — SAFE for the public repo.
- **Synthetic interaction generator:** implements design 009 §6 per-unit signal table (feature-derived taste,
  popularity bias, timestamps/ordered sessions/drift, exposure process + implicit positives + sampled negatives,
  cold-start partitions, leakage-safe temporal splits) with **exposed ground-truth**; verification targets
  recovered scores/rankings/subspaces (non-identifiability).
- **Real-slice script** (`psycopg`/`gensim`, derivation-only): reads the local `books` PostgreSQL catalog and emits
  a gzip'd-CSV slice + checksums + a data-dictionary per the §6 extraction contract. **It does NOT commit any real
  slice** — the committed artifact is **gated on the author confirming the DB's origin/license** (or switching to
  the Open Library public-domain fallback). Until then, committed/CI data is the **synthetic** catalog.
- **Tests:** generators are deterministic under fixed seeds; ground-truth is recoverable to tolerance.
**Verification:** seeded generation reproduces byte-identically; unit tests green; no real data committed.

### Phase F — the `bookrec` package skeleton
- Create `recsys/projects/bookrec/bookrec/`: the `RetrievalPath` protocol (`fit`/`load`, `retrieve(q, ctx, k) ->
  [(item_id, score, provenance)]` over stable int ids, deterministic tie-break, candidate limit, score semantics),
  a path **registry**, `blend`, `rank`, and `evaluate` stubs, plus catalog loading. Installed editable via the
  `recsys` dependency group so notebooks `import bookrec`.
- **Tests:** the registry + a trivial popularity path + blend + a hit-rate@k evaluator round-trip on the synthetic
  data (proves the substrate before any unit uses it).
**Verification:** `pytest` for the package; deterministic.

### Phase G — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN (with `recsys` registered, empty-book foundation state,
routed through `--group recsys`); all new `pytest` (guard, baseline.yaml, generators, bookrec) pass; determinism
(seeds/threads) confirmed; `bash scripts/pre-merge-guard.sh --pr` OK.

## Out of scope (verification-phase exemption)
This plan ships **no student units/projects/checkpoints**, so the "a plan shipping units needs a named verification
phase" rule is satisfied by shipping none (units land in `recsys-002+`, each with its own verification phase).
It is a **tooling + scaffolding** plan; its verification phase is Phase G.
Also out of scope: committing any real-catalog slice (license-gated); GPU; a served API; any neural model (Part 2);
the GloVe subset (lands with U7).

## Plan Review
_(4-way gate — [glm] skipped per standing decision; pending)_

## Content Review
_(N/A — no student content ships in this plan; tooling + scaffolding only.)_

## Post-Execution Report
_(pending)_
