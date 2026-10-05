# Plan recsys-007 — Unit 5: Matrix factorization (latent factors — the embedding bridge)

**Design:** `docs/designs/011-recsys-book.md` (§5, §6, §8 Unit 5). **Book:** `recsys` (Book 3). **Autopilot** per
AGENTS.md. Fifth and final Part-1 unit, on the Units 1–4 substrate + taste-aware generator (recsys-004). Ships the
**latent-factor** path — matrix factorization trained by gradient descent — the **Part-1→Part-2 hinge**: MF's learned
reader/item factors ARE embeddings (a dot-product retriever), foreshadowing the neural two-tower of Unit 8.

## Scope
**Unit 5 only** (`recsys/units/unit-05-matrix-factorization/`). Teaches **matrix factorization**: representing the
reader×item interaction matrix as a product of low-dimensional **latent factors**, trained by **gradient descent**
with L2 regularization on implicit feedback (train positives + sampled negatives from Unit 4). Ships a
`MatrixFactorizationPath` (numpy-only — **no PyTorch**; torch begins Unit 8) in `bookrec` + a Unit-5 milestone. No
neural nets, no ANN. No generator change.

## Why this works on the data (empirical, binding)
recsys-004's committed harness already trains an implicit learned-MF (train positives + reader-complement sampled
negatives, SGD) scoring **~0.264–0.274 hit@10** on `val` (k=10, cold excluded) — ≥ item-item CF (~0.252) and > the
content/lexical path (~0.158) and ≫ popularity (~0.108). So MF is the latent generalization of co-occurrence: it
matches/edges CF and compresses the signal into compact factors. Authors re-measure on the committed seed and bind
the Phase B test to the harness gates (MF > popularity, MF ≥ content; and MF ≳ CF — at least on par, allowing a small
tolerance since MF≈CF here).

## Buildout stays
Whole-book `lessons` total becomes **15** (U1–U5, 3 each) < 30 → `buildout: true` retained. (The lesson total crosses
≥30 around U8–U10; a later plan removes buildout then.)

## Audience & retained laws
Advanced baseline (incl. `vectors`, `dot-product`, `gradients`, `linear-algebra`, `calculus`, `numpy-*`). Retained:
project-first; taught-before-assessed; student notebooks NO solutions/outputs; solutions + milestone run clean
(fixed seeds — MF training is seeded + deterministic); teacher-notes; from-scratch→reveal-the-library. CPU-light
(numpy + `bookrec`; **no torch/faiss**) routed `--group recsys`; the training loop must stay within the per-notebook
exec budget (small `d`, few epochs — design §7/§9).

## Concepts introduced (3) — `concepts.yaml`
- `matrix-factorization` — model the reader×item matrix as `P Qᵀ` (readers × factors, items × factors); the
  **latent-factor** retrieval path; score = reader-factor · item-factor. `kind: technique`, `category: techniques`.
- `latent-factors` — the learned low-dimensional factors/**embeddings** per reader and item; what they capture; the
  explicit bridge to Part-2's learned embeddings (U7/U8). `kind: technique`, `category: techniques`.
- `gradient-descent` — training the factors by (stochastic) gradient descent on an implicit-feedback loss with **L2
  regularization**; the gradient of the squared/implicit loss; learning rate, epochs, overfitting/regularization.
  `kind: technique`, `category: techniques`.
All three globally unique (confirmed: 0 hits across `*/curriculum/concepts.yaml`).

### Coverage-map entry
`unit-05-matrix-factorization`, `kind: unit`, `title: "Matrix factorization"`, `lessons: 3`,
`introduces: [matrix-factorization, latent-factors, gradient-descent]`,
`requires: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics, implicit-feedback]`,
`practices: [retrieve-then-rank, offline-evaluation, top-k-ranking-metrics, implicit-feedback]`. (All required ids are
introduced by U1 or U4; `implicit-feedback` (U4) is genuinely re-exercised — MF trains with sampled negatives — giving
that concept a practices home. `practices ∩ introduces = ∅`; no `project` map entry → capstone rule inert; closes
under buildout.)

## Phases

### Phase A — registry + syllabus
- `concepts.yaml`: add the 3 ids. `coverage-map.yaml`: add the Unit-5 entry (buildout comment → "fifteen").
- `baseline.yaml`: declare new `x.name(...)` methods (confirm against authored cells; e.g. `MatrixFactorizationPath`,
  numpy `default_rng`/`normal`/`dot`/`clip`/`einsum`/`argsort`… as used).
- `unit-05-matrix-factorization/manifest.yaml`; `syllabus.md` arc row `| 5 | \`unit-05-matrix-factorization\` | unit | 3 | <hook> |`; rebuild PDF.
**Verify:** curriculum checks green; buildout holds (15<30).

### Phase B — `bookrec` MF code (Opus subagent; numpy-only, no pandas/torch in the package)
Dispatch an **Opus subagent**. STUDY `recsys/data/_reference_recommenders.py` `_learned_mf` (the implicit MF the
harness measures — PORT its logic, not its generator-sized signature), `protocol.py`, `scoreboard.py`,
`neighborhood.py`/`popularity.py` (path conventions). Add `bookrec/factorization.py`:
- `MatrixFactorizationPath(BaseRetrievalPath)` (name `"mf"`, version `"1"`). Constructor params: `n_factors`
  (small, e.g. 32), `n_epochs`, `learning_rate`, `reg` (L2), `n_negatives`, `seed` (deterministic init + negative
  sampling). `fit(interactions, catalog=None)` — EXACT protocol signature; duck-types the row-mapping iterable
  (`reader_id,item_id,split,label`, no pandas); trains reader factors `P` (by reader_id) and item factors `Q` (by
  item_id) by SGD on implicit feedback — TRAIN positives as targets + negatives SAMPLED from each reader's unobserved
  complement (NOT the whole catalog — mirror the harness's corrected sampling), L2-regularized; leakage-safe (no
  val/test). `retrieve(reader_id, context, k)` scores items by `P[reader_id] · Qᵀ`, excludes `context["seen"]`,
  top-k via `_finish`; a reader with no learned factor (e.g. cold) → `[]`. `load`/`artifact` round-trip `{P, Q,
  reader_ids, item_ids, params}`. Deterministic under the seed. Export from `__init__`.
- Tests (routed): MF clears the harness gates on the seeded `val` scoreboard — **MF > popularity AND MF ≥ content
  (lexical) AND MF ≳ item-item CF** (within a small tolerance; measured ~0.264–0.274 vs CF ~0.252, cold excluded,
  k=10); deterministic (two fits identical); a tiny hand-checkable training step reduces the loss; leakage (val/test
  rows don't affect the factors); empty-seen / no-factor reader → `[]`; fit→artifact→load identical recs; registers
  as `mf-v1`, no collision. Keep training FAST (small `d`/epochs) — within exec budget.
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/ -q` green, deterministic, numpy-only (no pandas/
torch import under `bookrec/`); the MF training notebook/test stays well under the 120 s per-cell budget.

### Phase C — lesson.ipynb (Opus subagent; project-first)
Hook: "what if we could describe every reader and book by a handful of hidden 'taste dials'?". From scratch →
reveal: (1) the latent-factor model `P Qᵀ` and what the factors mean; (2) the implicit-feedback loss + its gradient;
train P,Q by gradient descent with L2 regularization BY HAND in numpy (small toy), watch the loss fall; reveal
`MatrixFactorizationPath`; (3) score on `val` (seed 0, k=10, cold excluded) — MF matches/edges item-item CF
(~0.26 vs ~0.25), beating content and popularity: the latent generalization of co-occurrence. **The hinge:** these
learned factors ARE embeddings — a dot-product retriever — which Unit 8 will learn with a neural two-tower; and MF
shares CF's cold-item limit (no interactions → no learned factor), addressed by U9 features. ASCII only;
`rank(exclude=seen)`; reuse `bookrec`.
**Verify:** `exec-lessons` clean (within budget); non-empty markdown first cell; `concept-scan` clean.

### Phase D — exercises.ipynb + solutions.ipynb (separate fresh Opus subagents)
≥6 `## Exercise N`; ≥2 `stretch`; exercises NO solutions/outputs; solutions mirror all, clean (fixed seeds), ≥3
non-vacuous asserts. Drill: implement the factor model + a gradient-descent step; show the loss decreasing;
train/register `MatrixFactorizationPath` + read the val scoreboard vs CF/lexical/popularity/random (MF on par with/
edging CF). Stretch e.g.: the effect of `n_factors` and `reg` (under/overfitting); show MF's score is a dot product
of embeddings (the two-tower bridge); MF vs CF on a reader (same/different top picks). Taught-before-assessed; keep
all training small/seeded.
**Verify:** `hygiene`/`structure`/`cell-lint`/`noexec`; `exec-solutions` clean (budget); `concept-scan` clean.

### Phase E — milestone notebook (Opus subagent)
`recsys/projects/bookrec/milestones/unit-05-matrix-factorization.ipynb` — runnable fixed-seed demo (cleared outputs,
ASCII, one-line hook): train + register `MatrixFactorizationPath`, score on `val` vs random/popularity/lexical/CF
(MF on par with/edging CF), and show one reader's learned factor → top MF recs (and that the score is an
embedding dot product — the Part-2 bridge). Passes `milestone-check` + `exec-solutions` + `concept-scan`; stays in budget.

### Phase F — teacher-notes.md (inline)
`## Goals`, `## Pacing` (60–90 min / 2–3 sittings, hook stated; assign all exercises), `## Common mistakes` (leaking
val into training; not seeding → non-deterministic; too-large `d`/epochs → overfit or slow; forgetting regularization;
reading factors as interpretable axes; MF still can't cold-start the no-interaction items), `## Discussion prompts`
(MF vs CF; factors as embeddings → U8; why regularize), `## Differentiation`.

### Phase G — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN with Units 1–5 + the Unit-5 milestone AND
`bash scripts/pre-merge-guard.sh --pr` OK. buildout holds (15). Confirm the MF exec stays within the whole-book CI
budget (design §9).

## Out of scope
No PyTorch/neural (two-tower = U8); no ANN/FAISS (U10); no feature/cold-start factors (U9); no generator change; no
`projects/project-*` map entry (capstone=U14); no checkpoint (Checkpoint A ends Part 1 at U6); no buildout removal.

## Verification phase declared
Phase G is this plan's named verification phase.

## Plan Review

### Round 1 (on v1)

**[self] — APPROVE.** Concepts globally unique; coverage entry closes (requires = U1+U4 ids, all introduced;
`implicit-feedback` re-practiced; `practices∩introduces=∅`; no project entry → capstone rule inert); buildout holds
(15<30); named Phase G; project-first; from-scratch→library; ≥6/≥2-stretch/≥3-asserts; teacher-notes; milestone.
Feasibility from recsys-004's harness (implicit MF ~0.264–0.274 ≥ CF ~0.252); binds the harness gates + a CF tolerance
on the authors/gate. numpy-only (torch is U8); training kept small/seeded/in-budget. MatrixFactorizationPath ports
`_learned_mf` via the row-mapping fit. The embedding-bridge framing is the correct Part-1→2 hinge. No [self] blockers.

## Content Review

<!-- appended pre-PR -->

## Post-Execution Report

<!-- appended before ship -->
