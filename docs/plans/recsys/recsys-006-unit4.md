# Plan recsys-006 — Unit 4: Neighborhood collaborative filtering (item-item co-occurrence)

**Design:** `docs/designs/011-recsys-book.md` (§5, §6, §8 Unit 4). **Book:** `recsys` (Book 3). **Autopilot** per
AGENTS.md. Fourth Part-1 unit, on the Unit-1/2/3 substrate + the taste-aware generator (recsys-004) + the
milestone-notebook mechanism. Ships the first **collaborative** path — and the **first path to beat the popularity
baseline** on the scoreboard (the personalization payoff): item-item co-occurrence CF.

## Scope
**Unit 4 only** (`recsys/units/unit-04-neighborhood-cf/`). Teaches **neighborhood collaborative filtering**:
item-item **co-occurrence** similarity from the interaction log, **k-nearest-neighbor** retrieval, **implicit vs
explicit** feedback and **sampled negatives**. Ships an `ItemItemRetrievalPath` (co-occurrence) in `bookrec` + a
Unit-4 milestone notebook. No matrix factorization (U5), no neural (U7+). No generator change.

## Why this works on the data (empirical, binding)
recsys-004's committed recoverability harness already measures an item-item cosine co-occurrence CF at **~0.25
hit@10 ≈ 2.3–2.9× popularity (~0.108)** on `val` (k=10, cold excluded) — because taste-aware exposure imprints the
latent taste into co-occurrence. So CF is the first path to clearly **beat popularity**, the unit's headline. Authors
MUST re-measure on the committed seed and bind the Phase B test to a stable margin (CF ≥ ~1.3× popularity; the harness
gate already asserts this).

## Buildout stays
Whole-book `lessons` total becomes **12** (U1–U4, 3 each) < 30 → `buildout: true` retained.

## Audience & retained laws
Advanced baseline (incl. `vectors`, `dot-product`, `vector-norm`, `linear-algebra`, numpy). Retained: project-first;
taught-before-assessed; student notebooks NO solutions/outputs; solutions + milestone run clean (seed 0);
teacher-notes; from-scratch→reveal-the-library. CPU-light (numpy + `bookrec`; no torch/faiss) routed `--group recsys`.

## Concepts introduced (3) — `concepts.yaml`
- `item-item-cf` — item-item collaborative filtering: build an item×item **co-occurrence** similarity (cosine over
  the readers who co-engaged two items) from the **train** log; recommend items similar to what a reader has read.
  The shipped `ItemItemRetrievalPath`. `kind: technique`, `category: techniques`.
- `knn-similarity` — **k-nearest-neighbor** retrieval over the item-similarity matrix: score a candidate by the
  summed similarity to the reader's seen items (optionally capped to the top-k neighbors). `kind: technique`.
- `implicit-feedback` — **implicit vs explicit** feedback (a read/like is a positive; there are no negative ratings),
  the resulting positive-only sparsity, and why evaluation/training **sample negatives**. `kind: technique`.
All three globally unique (confirmed: 0 hits across `*/curriculum/concepts.yaml`).

### Coverage-map entry
`unit-04-neighborhood-cf`, `kind: unit`, `lessons: 3`, `introduces: [item-item-cf, knn-similarity, implicit-feedback]`,
`requires: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics]`,
`practices: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics]` (Unit-1 ids; closes
under buildout; no project map entry → capstone rule inert).

## Phases

### Phase A — registry + syllabus (CI-fidelity)
- `concepts.yaml`: add the 3 ids. `coverage-map.yaml`: add the Unit-4 entry (buildout comment → "twelve").
- `baseline.yaml`: declare any new `x.name(...)` methods the notebooks/code use (confirm against authored cells).
- `unit-04-neighborhood-cf/manifest.yaml`; `syllabus.md` arc row `| 4 | \`unit-04-neighborhood-cf\` | unit | 3 | <hook> |`; rebuild PDF.
**Verify:** curriculum checks green; buildout holds (12<30).

### Phase B — `bookrec` CF code (Opus subagent; numpy-only, no pandas in the package)
Dispatch an **Opus subagent** (`Agent`, `model: opus`). STUDY `recsys/data/_reference_recommenders.py` (its item-item
cosine co-occurrence CF reference scorer — the recoverability-harness implementation to port/mirror), `protocol.py`,
`scoreboard.py`, `popularity.py`/`lexical.py` (path conventions). Add `bookrec/neighborhood.py`:
- an item-item **co-occurrence** builder: from the train positives, build a sparse/dense item×item cosine similarity
  (reader co-engagement); row-normalize; optional top-k neighbor cap.
- `ItemItemRetrievalPath(BaseRetrievalPath)` (name `"item-item"`, version `"1"`): `fit(interactions, catalog=None)` —
  EXACTLY the protocol signature; builds the similarity from the train log (implicit positives only; leakage-safe —
  no val/test). `retrieve(reader_id, context, k)` scores each candidate by the summed similarity to the reader's
  `context["seen"]` items, excludes `seen`, top-k via `_finish`; empty `seen` → `[]`. `load`/`artifact` round-trip the
  fitted similarity. Export from `__init__`.
- Tests (routed): CF beats popularity on the seeded `val` scoreboard with a stable margin (≥1.3× popularity, cold
  excluded, k=10); a tiny hand-checked co-occurrence/cosine fixture; leakage (val/test rows don't affect the
  similarity); empty-seen → `[]`; fit→artifact→load round-trip returns identical recs; registers as `item-item-v1`,
  no collision.
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/ -q` green, deterministic, numpy-only.

### Phase C — lesson.ipynb (Opus subagent; project-first)
Hook: "readers who liked the books you liked also read…". From scratch → reveal: (1) the co-occurrence idea +
implicit vs explicit feedback (why there are no negatives, sparsity, sampled negatives); (2) build the item-item
cosine similarity by hand in numpy; (3) k-NN retrieval — score candidates by similarity to the reader's history;
reveal `ItemItemRetrievalPath`, register + score on `val` (seed 0, k=10, cold excluded) — it **beats popularity**
(~0.25 vs ~0.108) and the content path (~0.158): the first personalization win, the headline of Part 1. Honest: this
is collaborative (uses who-read-what), complementary to the content/lexical path; MF (U5) generalizes it.
ASCII only; `rank(exclude=seen)`; reuse `bookrec`.
**Verify:** `exec-lessons` clean; non-empty markdown first cell; `concept-scan` clean.

### Phase D — exercises.ipynb + solutions.ipynb (separate fresh Opus subagents)
≥6 `## Exercise N`; ≥2 `stretch`; exercises NO solutions/outputs; solutions mirror all, clean (seed 0), ≥3
non-vacuous asserts. Drill: build the co-occurrence matrix + cosine similarity; k-NN retrieval; register
`ItemItemRetrievalPath` + read the val scoreboard vs popularity/lexical/random (CF wins); implicit-feedback +
sampled-negative reasoning. Stretch e.g.: effect of the top-k neighbor cap; cold-item behavior (an item with no
co-occurrence → no neighbors); why co-occurrence ≈ a rank-reduced signal (bridge to MF). Taught-before-assessed.
**Verify:** `hygiene`/`structure`/`cell-lint`/`noexec` (≥6, ≥2 stretch, no outputs); `exec-solutions` clean;
`concept-scan` clean.

### Phase E — milestone notebook (Opus subagent)
`recsys/projects/bookrec/milestones/unit-04-neighborhood-cf.ipynb` — runnable fixed-seed demo (cleared outputs,
ASCII, one-line hook): build + fit + register `ItemItemRetrievalPath`, score on `val` vs random/popularity/lexical
(CF wins), and show one reader's history → top CF recommendations with the co-occurring neighbors. Passes
`milestone-check` + `exec-solutions` + `concept-scan`.

### Phase F — teacher-notes.md (inline)
`## Goals`, `## Pacing` (60–90 min / 2–3 sittings, hook stated; assign all exercises), `## Common mistakes`
(leaking val into the similarity; recommending already-seen items; cold items with no neighbors; confusing item-item
with user-user), `## Discussion prompts`, `## Differentiation`.

### Phase G — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN with Units 1–4 + the Unit-4 milestone AND
`bash scripts/pre-merge-guard.sh --pr` OK. buildout holds (12).

## Out of scope
No matrix factorization (U5); no neural/embeddings (U7+); no generator change; no user-user CF beyond a mention
(item-item is the shipped path); no `projects/project-*` map entry (capstone=U14); no checkpoint; no buildout removal.

## Verification phase declared
Phase G is this plan's named verification phase.

## Plan Review

### Round 1 (on v1)

**[self] — APPROVE.** Concepts globally unique; coverage entry closes (Unit-1 ids; `practices∩introduces=∅`; no
project map entry → capstone rule inert); buildout holds (12<30); named verification Phase G; project-first;
from-scratch→library; ≥6/≥2-stretch/≥3-asserts; teacher-notes; milestone. Feasibility established by recsys-004's
committed harness (item-item CF ~0.25 ≈ 2.3–2.9× popularity) — CF is the first path to beat popularity, the Part-1
headline; binds empirical re-measure + the ≥1.3×-popularity margin on the authors + gate. `ItemItemRetrievalPath`
mirrors the harness's reference CF scorer, keyword/construction pattern not needed (fit builds from the train log).
No [self] blockers. Monday: full 4-way incl. [glm]; [sol] retried on Codex.

## Content Review

<!-- appended pre-PR -->

## Post-Execution Report

<!-- appended before ship -->
