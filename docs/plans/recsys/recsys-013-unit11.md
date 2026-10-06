# Plan recsys-013 — Unit 11: Neural reranking (learning to rank the candidate pool)

**Design:** `docs/designs/011-recsys-book.md` (§8 row 11 "Neural ranking: candidates → learned reranker; features;
blend calibration → Learned reranker + learned path blending"; the §8 architecture diagram "ranking (learned reranker
over the merged pool + features)"; §7 libraries/determinism/ceilings — PyTorch reranker, CPU-deterministic, tolerance/
rank-based §184). **Book:** `recsys` (Book 3). **Autopilot** per AGENTS.md. Fifth Part-2 unit, on the Units 1–10
substrate. This is the **second stage of retrieve-then-rank**, finally LEARNED: the retrieval paths (U2–U10) propose a
candidate pool; a small **PyTorch reranker** re-scores each candidate from a **feature vector** (the per-path
calibrated scores + content signals) trained on implicit feedback. `rank.py` already anticipates this
("a learned reranker replaces the ordering key in a later unit without changing this signature"). No new retrieval
model; no generator change.

## Scope
**Unit 11** (`recsys/units/unit-11-neural-reranking/`). Teaches: (1) **neural reranking** — the two-stage
retrieve-then-rank split: cheap retrieval proposes a pool (U10 hybrid / U6 blend), an expensive learned model
re-scores only that pool; (2) **ranking features** — assembling a per-candidate feature vector from the retrieval
paths' **calibrated scores** (popularity, lexical, item-item, MF, semantic, two-tower) + content/behaviour signals
(genre overlap with the reader's history, author overlap, popularity count); (3) **learning to rank** — training the
reranker on implicit feedback (pointwise logistic over pool positives vs sampled pool negatives; pairwise/BPR as the
stretch), and the honest readout of whether a learned reranker beats the best single path and the linear blend. Ships
a `NeuralRerankerPath` (or `rerank`-wrapping path) in `bookrec` (torch, lazy like U8) + a Unit-11 milestone. No
sequence model (U12); no ethics/Checkpoint B (U13); no capstone (U14); no generator change.

## Determinism & budget (per U8 pattern — binding)
Same CPU-determinism contract as U8/U9 (`torch.manual_seed` + `use_deterministic_algorithms(True)` + single-thread,
SAVED/RESTORED around `fit`; torch imported LAZILY inside `fit` only; `retrieve`/`load`/`artifact` torch-free on numpy
weights; the group-free suite never imports torch — reuse/extend the import-blocked-subprocess test). Determinism
GATE = identical top-k ranking + `allclose` (design §184, never exact-float). The reranker is tiny (a small MLP over a
low-dim feature vector, few epochs) → per-fit should be ≲ U8's ~15 s; Phase B measures per-fit time + aggregate fit
count against the §9 whole-book budget and pins epochs/dims so each notebook stays ≤2–3 fits, far under the 120 s/cell
cap. Feature assembly reuses the already-fit retrieval paths (one-time cost), not a refit per candidate.

## Why this works on the data (to MEASURE in Phase B — pre-declared, honest)
The empirical question the gate reviewers must see measured on shipped code (nothing pre-bound to an unmeasured
number): **does a learned reranker over the retrieved pool beat the best single path (two-tower 0.340) and the linear
blends (U6 4-way 0.306 / U10 hybrid 0.362) on hit@10, or does it mainly help calibration/coverage?** Pre-declare the
honest outcome space — the per-path scores are correlated, so a reranker trained on the SAME implicit signal may only
modestly beat the best single path:
- **Gate (measured-safe, directional):** the reranker **must not tank** — `reranker.hit@10 ≥ two_tower.hit − 0.01`
  over its candidate pool; AND it should **beat the linear blend it reranks** on hit@10 OR match it with better
  behaviour on another axis (coverage / a beyond-accuracy metric) — Phase B pins the exact comparator from the
  measurement (e.g. `reranker.hit ≥ blend.hit`), never a number it hasn't measured.
- **Honest framing:** if the learned reranker only ties the two-tower/blend, the lesson says so — the win of a
  reranker is *combining heterogeneous signals + features a single path can't see*, and on this small synthetic log
  the ceiling may be near the two-tower; frame it as the *architecture* that production systems need (cheap recall →
  expensive precise rank), measured honestly, not a guaranteed accuracy jump.
- Report hit@10 AND coverage for: best single path, U6 blend, U10 hybrid, and the reranker; plus a feature-ablation
  (drop the path-score features vs drop the content features) as the teaching payoff.

## Audience & retained laws
Advanced baseline (design 011). Retained in full: project-first; taught-before-assessed (neural-reranking/
ranking-features/learning-to-rank introduced + practiced here); student notebooks NO solutions/outputs; solutions +
milestone run clean (fixed seeds, deterministic torch); teacher-notes; from-scratch→reveal (score-order baseline →
learned reranker); a stretch exercise. CPU-deterministic; routed `--group recsys`; within budget.

## Concepts introduced (3) — `concepts.yaml`
- `neural-reranking` — a second-stage learned model that re-scores a retrieved candidate pool (two-stage
  retrieve-then-rank). `kind: technique`, `category: techniques`.
- `ranking-features` — assembling a per-candidate feature vector from the retrieval paths' calibrated scores +
  content/behaviour signals. `kind: technique`, `category: techniques`.
- `learning-to-rank` — training the reranker on implicit feedback (pointwise logistic / pairwise over the pool).
  `kind: technique`, `category: techniques`.
All three globally unique (confirmed 0 hits across `*/curriculum/concepts.yaml`; re-confirm in Phase A).

### Coverage-map entry
`unit-11-neural-reranking`, `kind: unit`, `title: "Neural reranking"`, `lessons: 3`,
`introduces: [neural-reranking, ranking-features, learning-to-rank]`,
`requires: [retrieve-then-rank, offline-evaluation, top-k-ranking-metrics, beyond-accuracy, implicit-feedback,
score-blending, two-tower, neural-training, hybrid-retrieval]`,
`practices: [retrieve-then-rank, offline-evaluation, top-k-ranking-metrics, beyond-accuracy, implicit-feedback,
score-blending, two-tower, neural-training, hybrid-retrieval]`.
(All required ids introduced by U1/U4/U6/U8/U10. `score-blending` (U6) = the linear blend the reranker learns to beat;
`hybrid-retrieval` (U10) + `two-tower` (U8) = the candidate pool + a strong path feature; `neural-training` (U8) = the
torch training reused; `implicit-feedback` (U4) = the training signal; `beyond-accuracy` (U6) = the coverage readout.
`practices ∩ introduces = ∅`; no `project` entry → capstone rule inert. Whole-book lessons 30.5 → 33.5 ∈ [30,60].)

## Phases

### Phase A — registry + syllabus
- `concepts.yaml`: add the 3 ids. `coverage-map.yaml`: add the Unit-11 entry (lessons total 30.5 → 33.5, still ≤ 60;
  buildout already removed at U10). `baseline.yaml`: declare any new `x.name(...)` methods the authored cells use
  (torch MLP idioms — e.g. `Linear`, `ReLU`/`relu`, `Sequential`, `BCEWithLogitsLoss` if used; `NeuralRerankerPath`;
  feature-assembly accessors) — add ONLY what the cells use (trim unused at Phase G, as in recsys-011/012).
- `unit-11-neural-reranking/manifest.yaml`; `syllabus.md` arc row `| 11 | \`unit-11-neural-reranking\` | unit | 3 |
  <hook> |` after the U10 row; rebuild PDF.
**Verify:** manifest/prereq/coverage/syllabus green (lesson-budget 33.5 ∈ [30,60]; introduction completeness holds);
concepts unique.

### Phase B — `bookrec` reranker path (Opus subagent; PyTorch, lazy, CPU-deterministic)
Dispatch an **Opus subagent**. STUDY `blend.py` (the merged/calibrated/deduped pool + per-path provenance scores —
the reranker's candidate source + score features), `rank.py` (the ordering key the reranker replaces), `two_tower.py`
(the lazy-torch/determinism/torch-free-persistence pattern to mirror), `protocol.py` (`Candidate`, `calibrate_scores`,
`fit`/`retrieve`/`artifact`/`load`), `scoreboard.py`/`evaluate.py`/`diversity.py`, `catalog.py` (genre/author for
content features), the fitted paths in a milestone. Add `bookrec/rerank.py` (torch lazy in `fit`):
- `NeuralRerankerPath(BaseRetrievalPath)` (name `"reranker"`, version `"1"`) via CONSTRUCTOR (like U9/U10:
  `NeuralRerankerPath(base_registry_or_paths, catalog_books, pool=..., ...)`): `fit(interactions, catalog=None)`
  builds, per (reader, candidate) in the retrieved pool, a **feature vector** = the calibrated per-path scores +
  content/behaviour features (genre overlap with the reader's train history, author overlap, popularity), trains a
  small **MLP** (PyTorch) with a **pointwise logistic** loss over pool positives (train interactions) vs sampled pool
  negatives; `retrieve` builds the pool for the reader, scores each candidate with the learned MLP (torch-free numpy
  forward on saved weights), excludes `seen`, returns top-k; unknown reader → `[]`. BPR/pairwise = a stretch knob.
  `load`/`artifact` persist the numpy MLP weights + feature spec (torch-free). Deterministic. Export (no eager torch).
- Tests (routed, new `tests/test_unit11.py`): reranker hit@10 **≥ two_tower.hit − 0.01** (not tanked) AND the pinned
  comparator vs the linear blend from the Phase-B measurement (directional, measured-safe — do NOT assert a number
  not measured); determinism (ranking + allclose, array_equal bonus print only); feature-ablation effect recorded;
  empty-seen/unknown-reader contract; fit→artifact→load identical (torch-free); registers as `reranker-v1`. **EXTEND
  the import-blocked subprocess test** (`tests/test_unit07.py`) to cover `rerank` (group-free imports no torch/faiss).
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/ -q` green + group-free suite imports no torch/faiss;
**report reranker hit@10 + coverage vs best-single-path / U6-blend / U10-hybrid + the feature-ablation + per-fit time +
aggregate fit count** so the lesson is data-bound and in budget.

### Phase C — lesson.ipynb (Opus subagent; project-first)
Hook: "our paths each see one slice of the signal — popularity, text, behaviour. What if a model *learned* to combine
them per candidate?" From scratch → reveal: (1) the two-stage split (cheap retrieval pool → expensive precise rank)
and the score-order baseline `rank.py` already does; (2) **ranking features** — build the per-candidate feature vector
from the paths' calibrated scores + content signals; (3) **learning to rank** — train the MLP on implicit feedback
(pointwise), contrast with the linear blend (U6) which is fixed weights vs a learned non-linear combiner; reveal
`NeuralRerankerPath`; score on `val` — reranker vs two-tower / U6 blend / U10 hybrid, read hit@10 AND coverage
**honestly** (the measured Phase-B story); (4) the feature ablation (which features carry the lift). Bridge: U12 adds
sequence features; U13 revisits fairness of a learned ranker; U14 capstone wires retrieval→blend→rerank end to end.
ASCII only; `rank(exclude=seen)`; reuse `bookrec`; tiny/seeded/in-budget.
**Verify:** `exec-lessons` clean (budget); non-empty markdown first cell; `concept-scan` clean.

### Phase D — exercises.ipynb + solutions.ipynb (separate fresh Opus subagents)
≥6 `## Exercise N`; ≥2 `stretch`; exercises NO solutions/outputs; solutions mirror all, clean (fixed seeds,
deterministic), ≥3 non-vacuous asserts. Drill: build a candidate pool + per-candidate feature vector; train/register
`NeuralRerankerPath`; read the val scoreboard (reranker vs two-tower / blend / hybrid) on hit@10 AND coverage; a
feature-ablation. Stretch e.g.: pointwise vs pairwise/BPR; add/drop a feature family and measure; the pool-size knob.
Taught-before-assessed; seeded. **Verify:** `hygiene`/`structure`/`cell-lint`/`noexec`; `exec-solutions` clean
(budget); `concept-scan` clean.

### Phase E — milestone notebook (Opus subagent)
`recsys/projects/bookrec/milestones/unit-11-neural-reranking.ipynb` — fixed-seed demo: build the pool + features; train
+ register `NeuralRerankerPath`; val scoreboard vs the best single path + U6 blend + U10 hybrid (hit@10 + coverage);
the feature ablation; one reader whose ranking the reranker visibly improves. Passes `milestone-check` +
`exec-solutions` + `concept-scan`; ≤ budget; no `split="test"`.

### Phase F — teacher-notes.md (inline)
`## Goals`, `## Pacing` (60–90 min / 2–3 sittings, hook first, all exercises), `## Common mistakes` (expecting the
reranker to always beat every path — on correlated signals the lift may be small; leaking the pool's own labels /
val into training; refitting paths per candidate instead of reusing fitted ones; non-determinism; forgetting the
reranker only re-orders the POOL — recall is capped by retrieval), `## Discussion prompts` (why two-stage retrieve-
then-rank; what a learned non-linear combiner sees that a fixed linear blend cannot; which features carry the lift;
the retrieval recall ceiling), `## Differentiation`.

### Phase G — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN with Units 1–11 + Checkpoint A + the Unit-11 milestone AND
`bash scripts/pre-merge-guard.sh --pr` OK. Confirm CPU-determinism, no torch/faiss on the group-free path, lesson
budget (33.5 ∈ [30,60]), and the reranker exec stays within the whole-book CI budget.

## Out of scope
No sequence/SASRec model (U12); no ethics/beyond-accuracy deepening or Checkpoint B (U13); no capstone (U14); no new
retrieval path (the reranker reranks the EXISTING paths' pool); no generator change; no `projects/project-*` entry
(capstone = U14); no GPU.

## Verification phase declared
Phase G is this plan's named verification phase.

## Plan Review

<!-- appended after the 3-way plan-review gate -->

## Content Review

<!-- appended pre-PR -->

## Post-Execution Report

<!-- appended before ship -->
