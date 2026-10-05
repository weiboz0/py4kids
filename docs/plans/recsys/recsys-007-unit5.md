# Plan recsys-007 — Unit 5: Matrix factorization (latent factors — the embedding bridge)

**Design:** `docs/designs/011-recsys-book.md` (§5, §6, §8 Unit 5). **Book:** `recsys` (Book 3). **Autopilot** per
AGENTS.md. Fifth and final Part-1 unit, on the Units 1–4 substrate + taste-aware generator (recsys-004). Ships the
**latent-factor** path — matrix factorization trained by gradient descent — the **Part-1→Part-2 hinge**: MF's learned
reader/item factors ARE embeddings (a dot-product retriever), foreshadowing the neural two-tower of Unit 8.

## Scope
**Unit 5 only** (`recsys/units/unit-05-matrix-factorization/`). Teaches **matrix factorization**: representing the
reader×item interaction matrix as a product of low-dimensional **latent factors**, trained by **full-batch gradient
descent** (logistic implicit-feedback loss, L2 regularization) on train positives + **negatives sampled from each
reader's unobserved complement** (the sampled-negative technique from Unit 4 — but NOT the log's `label==0` exposure
negatives, which carry taste signal; see Phase C). Ships a
`MatrixFactorizationPath` (numpy-only — **no PyTorch**; torch begins Unit 8) in `bookrec` + a Unit-5 milestone. No
neural nets, no ANN. No generator change.

## Why this works on the data (empirical, binding — measured on the SHIPPED data, [fable] round 1)
A port of recsys-004's implicit learned-MF as a `BaseRetrievalPath` (train positives + **reader-complement** sampled
negatives, **logistic loss, full-batch per-entity-averaged gradient descent**, L2) was measured on the committed `val`
scoreboard (k=10, 60 cold readers excluded, 500 eligible). At the pinned config `n_factors=32, n_epochs=300,
learning_rate=0.5, reg=0.05, n_negatives=10` (~16–21 s/fit):

| path | hit@10 |
|------|--------|
| random | 0.012 |
| popularity | 0.108 |
| content/lexical | 0.158 |
| item-item CF | 0.252 |
| **MF (this unit)** | **0.254 mean** (seeds 0.262/0.258/0.246/0.270/0.232; seed 0 = 0.262) |

So MF is the latent generalization of co-occurrence: it is **on par with CF** (≈0.26 vs 0.25) and compresses the
signal into compact factors, while beating lexical (×1.6) and popularity (×2.3) by wide margins. MF−CF is **within
one paired SE** (≈0.019) — "edges CF" is seed luck; the honest story is parity, with MF pulling ahead only at more
epochs (e500 → 0.267) at a time cost (a teaching point about compact factors). **Two measured cliffs bind the plan:**
(a) epochs matter — e200 → 0.241 (< CF), e100 → 0.153 (**< lexical**), so defaults are pinned, NOT "small/few"; (b)
training on the log's `label==0` **exposure** negatives instead of the complement collapses MF to the random floor
(0.016–0.028) because those negatives carry the taste signal — this is a Phase-C lesson, not a bug. The Phase-B test
binds to these numbers (seed 0: `mf ≥ cf − 0.03`, `mf ≥ 1.2×pop`, `mf ≥ pop + 0.03`, `mf ≥ lexical`).

## Buildout stays
Whole-book `lessons` total becomes **15** (U1–U5, 3 each) < 30 → `buildout: true` retained. (The lesson total crosses
≥30 around U8–U10; a later plan removes buildout then.)

## Audience & retained laws
Advanced baseline (incl. `vectors`, `dot-product`, `gradients`, `linear-algebra`, `calculus`, `numpy-*`). Retained:
project-first; taught-before-assessed; student notebooks NO solutions/outputs; solutions + milestone run clean
(fixed seeds — MF training is seeded + deterministic); teacher-notes; from-scratch→reveal-the-library. CPU-light
(numpy + `bookrec`; **no torch/faiss**) routed `--group recsys`. **Exec budget (numeric, binding):** each MF fit at
the pinned config is ~16–21 s (well under the 120 s per-cell cap); each notebook does ≤3–4 fits (Phase-D sweep split
≤4 fits/cell); whole-book adds ~1.5–2 CI-min (design §9). Defaults are **pinned** (d32/e300) — NOT "small/few epochs"
(measured: <300 epochs fails the CF/lexical gate).

## Concepts introduced (3) — `concepts.yaml`
- `matrix-factorization` — model the reader×item matrix as `P Qᵀ` (readers × factors, items × factors); the
  **latent-factor** retrieval path; score = reader-factor · item-factor. `kind: technique`, `category: techniques`.
- `latent-factors` — the learned low-dimensional factors/**embeddings** per reader and item; what they capture; the
  explicit bridge to Part-2's learned embeddings (U7/U8). `kind: technique`, `category: techniques`.
- `gradient-descent` — training the factors by **full-batch (per-entity-averaged) gradient descent** on a **logistic
  implicit-feedback loss** with **L2 regularization**; the gradient of the logistic loss over positives + sampled
  negatives; learning rate, epochs, overfitting/regularization. `kind: technique`, `category: techniques`.
All three globally unique (confirmed: 0 hits across `*/curriculum/concepts.yaml`).

### Coverage-map entry
`unit-05-matrix-factorization`, `kind: unit`, `title: "Matrix factorization"`, `lessons: 3`,
`introduces: [matrix-factorization, latent-factors, gradient-descent]`,
`requires: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics, implicit-feedback]`,
`practices: [retrieve-then-rank, offline-evaluation, top-k-ranking-metrics, implicit-feedback]`. (All required ids are
introduced by U1 or U4; `implicit-feedback` (U4) is genuinely re-exercised — MF trains with sampled negatives — giving
that concept a practices home. **`catalog-search` is intentionally dropped from `practices`** (MF scores `P·Qᵀ` over
the latent factors — it does no lexical/catalog search; the concept stays practiced in U2–U4, so this is legal).
`practices ∩ introduces = ∅`; no `project` map entry → capstone rule inert; closes under buildout.)

## Phases

### Phase A — registry + syllabus
- `concepts.yaml`: add the 3 ids. `coverage-map.yaml`: add the Unit-5 entry (buildout comment → "fifteen").
- `baseline.yaml`: declare new `x.name(...)` methods (confirm against authored cells; e.g. `MatrixFactorizationPath`,
  numpy `default_rng`/`normal`/`integers`/`dot`/`clip`/`exp`/`bincount`/`concatenate`/`repeat`/`argsort`/`einsum`… as
  used). (Note: `bincount`-per-column is the fast per-entity gradient path — prefer over `np.add.at`.)
- `unit-05-matrix-factorization/manifest.yaml`; `syllabus.md` arc row `| 5 | \`unit-05-matrix-factorization\` | unit | 3 | <hook> |`; rebuild PDF.
**Verify:** curriculum checks green; buildout holds (15<30).

### Phase B — `bookrec` MF code (Opus subagent; numpy-only, no pandas/torch in the package)
Dispatch an **Opus subagent**. STUDY `recsys/data/_reference_recommenders.py` `_learned_mf` (the implicit MF the
harness measures — PORT its logic, not its generator-sized signature), `protocol.py`, `scoreboard.py`,
`neighborhood.py`/`popularity.py` (path conventions). Add `bookrec/factorization.py`:
- `MatrixFactorizationPath(BaseRetrievalPath)` (name `"mf"`, version `"1"`). Constructor params with **PINNED
  defaults** (measured — do NOT shrink): `n_factors=32`, `n_epochs=300`, `learning_rate=0.5`, `reg=0.05` (L2),
  `n_negatives=10`, `seed` (deterministic init + negative sampling). `fit(interactions, catalog=None)` — EXACT
  protocol signature; duck-types the row-mapping iterable (`reader_id,item_id,split,label`, no pandas). **Item
  universe = the full catalog** (every catalog item id gets an initialized `Q` row), so retrieval can score any item;
  **readers = those with ≥1 TRAIN positive** (only they get a learned `P` row). Trains `P`/`Q` by **full-batch,
  per-entity-averaged gradient descent on a logistic implicit-feedback loss** (NOT SGD, NOT squared loss) — TRAIN
  positives as label-1 + **`n_negatives` per reader sampled from that reader's unobserved complement** (NOT the log's
  `label==0` exposure negatives — those collapse MF to the floor; NOT the whole catalog), L2-regularized; leakage-safe
  (val/test rows never touch `P`/`Q`). PORT `_reference_recommenders._learned_mf`'s exact objective (the 0.254 depends
  on it); use `bincount`-per-column for the per-entity gradient (fast path). `retrieve(reader_id, context, k)` scores
  **all catalog items** by `P[reader_id] · Qᵀ`, excludes `context["seen"]` (empty `seen` → excludes nothing), top-k
  via `_finish`. **Retrieve contract:** a reader WITH a learned factor is scored by its `P·Qᵀ` row **regardless of
  whether `seen` is empty** (MF does not build its query from `seen`); only a reader with **no learned factor**
  (unknown / cold — 0 train positives) → `[]`. `load`/`artifact` round-trip `{P, Q, reader_ids, item_ids, params}`.
  Deterministic under the seed. Export from `__init__`.
- Tests (routed), binding to the measured numbers (seed 0, k=10, 60 cold readers excluded):
  **`mf_hit >= 1.2*pop` AND `mf_hit >= pop + 0.03` AND `mf_hit >= lexical` AND `mf_hit >= cf_hit − 0.03`**
  (seed-0 measured MF 0.262 vs CF 0.252, +0.010; tolerance 0.03 covers the worst-seed −0.020) — NOT "MF > popularity"
  / "small tolerance"; deterministic (two fits bit-identical); a tiny hand-checkable step reduces the logistic loss;
  leakage (val/test rows don't change `P`/`Q`); **a known reader with empty `seen` still returns k recs**, an
  **unknown reader → `[]`**; fit→artifact→load identical recs; registers as `mf-v1`, no collision. Run at the PINNED
  config (~16–21 s/fit) — do NOT shrink epochs to save time (measured: e100 → 0.153 < lexical, fails the gate).
**Seed honesty ([fable] round-2 Nice3):** the Opus port will consume `default_rng(0)` differently from the harness,
so its seed-0 draw is a fresh sample of the measured 0.232–0.270 spread (tolerance 0.03 covers the worst-of-5). If
the shipped port's seed 0 lands below `cf − 0.03`, do NOT loosen the gate or silently shop seeds — report the draw in
the Post-Execution Report and pin the test seed explicitly (the number stays traceable either way).
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/ -q` green, deterministic, numpy-only (no pandas/
torch import under `bookrec/`); each fit ~16–21 s, well under the 120 s per-cell budget.

### Phase C — lesson.ipynb (Opus subagent; project-first)
Hook: "what if we could describe every reader and book by a handful of hidden 'taste dials'?". From scratch →
reveal: (1) the latent-factor model `P Qᵀ` and what the factors mean; **a short "why not plain SVD?" aside** —
classical low-rank factorization (truncated SVD) decomposes a *dense, explicit-rating* matrix, but our feedback is
*implicit and sparse* (reads/likes, no ratings; the unobserved entries are not true zeros), so we optimize an
implicit **logistic** loss by gradient descent instead of SVD (design §8's "SVD" named here, not shipped). (2) the
logistic implicit-feedback loss + its gradient; train P,Q by **full-batch gradient descent** with L2 regularization
BY HAND in numpy (small toy), watch the loss fall; reveal `MatrixFactorizationPath`. **(2b) the negatives beat
(reconciles U4):** Unit 4 pointed forward to these sampled negatives feeding U5's training — so try it both ways and
measure: training on the log's `label==0` **exposure** negatives collapses MF to the random floor (~0.02), because
exposed-not-engaged books are an *exposure-biased* negative (the generator exposes by popularity+taste), so pushing
them down destroys the very signal; sampling negatives from each reader's **unobserved complement** is what works
(a first, concrete encounter with exposure bias → Unit 13). (3) score on `val` (seed 0, k=10, 60 cold readers
excluded) — MF is **on par with item-item CF** (about 0.25–0.26, within noise of CF's ~0.25 over 500 readers; more
epochs pull slightly ahead at a time cost), beating content (0.158) and popularity (0.108): the latent generalization of
co-occurrence. **The hinge:** these learned factors ARE embeddings — a dot-product retriever — which Unit 8 will learn
with a neural two-tower. **Honest cold story (two distinct cases):** a cold *reader* (0 train positives) has no
learned factor → `[]`; a cold *item* DOES get an initialized `Q` row, but with no positive signal it is shaped only
by negative sampling (gradient pushes its score down) → MF *scores* the whole catalog (broader candidate reach than
CF's hard-zero) yet still can't meaningfully *recommend* cold items — the real fix is U9 features. ASCII only;
`rank(exclude=seen)`; reuse `bookrec`.
**Verify:** `exec-lessons` clean (within budget; ≤4 fits/cell); non-empty markdown first cell; `concept-scan` clean.

### Phase D — exercises.ipynb + solutions.ipynb (separate fresh Opus subagents)
≥6 `## Exercise N`; ≥2 `stretch`; exercises NO solutions/outputs; solutions mirror all, clean (fixed seeds), ≥3
non-vacuous asserts. Drill: implement the factor model + a full-batch gradient-descent step on the logistic loss;
show the loss decreasing; train/register `MatrixFactorizationPath` (pinned config) + read the val scoreboard vs
CF/lexical/popularity/random (**MF on par with CF**, within noise — not "beats"). Stretch e.g.: the effect of
`n_factors` and `reg` (under/overfitting) — **split the sweep ≤4 fits per cell** (6 fits × ~18 s in one cell brushes
the 120 s cap); show MF's score is a dot product of embeddings (the two-tower bridge); MF vs CF on a reader
(same/different top picks). Taught-before-assessed; seed everything; keep each cell ≤4 fits at the pinned config.
**Verify:** `hygiene`/`structure`/`cell-lint`/`noexec`; `exec-solutions` clean (budget); `concept-scan` clean.

### Phase E — milestone notebook (Opus subagent)
`recsys/projects/bookrec/milestones/unit-05-matrix-factorization.ipynb` — runnable fixed-seed demo (cleared outputs,
ASCII, one-line hook): train + register `MatrixFactorizationPath` (pinned config), score on `val` vs
random/popularity/lexical/CF (**MF on par with CF**, about 0.25–0.26 vs CF's ~0.25, within noise), show one reader's learned factor → top MF recs
(the score is an embedding dot product — the Part-2 bridge), and illustrate the cold-item limit (a no-train-positive
item's factor is shaped only by negative gradient → pushed to a low score). Passes `milestone-check` +
`exec-solutions` + `concept-scan`; ≤4 fits total, stays in budget.

### Phase F — teacher-notes.md (inline)
`## Goals`, `## Pacing` (60–90 min / 2–3 sittings, hook stated; assign all exercises), `## Common mistakes` (leaking
val into training; not seeding → non-deterministic; **shrinking epochs below ~300 → MF silently drops below lexical**
(the gate-failing mistake the data actually punishes); **training on the log's exposure `label==0` negatives → MF
collapses to the floor** — use complement sampling; forgetting regularization; reading factors as interpretable axes;
conflating a cold *reader* (→ `[]`) with a cold *item* (gets a negative-shaped factor, scored low); expecting MF to
beat CF — it is on par, within noise), `## Discussion prompts` (MF vs CF; factors as embeddings → U8; why regularize;
why are exposure negatives the *wrong* negatives? → exposure bias, U13), `## Differentiation`.
- **In-scope U4 consistency touch (markdown-only, [fable] round-2 Should1/Nice2):** U5 proves the log's `label==0`
  exposure negatives are *harmful* for training (MF → ~0.02), so U4's forward pointers that say those negatives are
  "used as training signal in Unit 5" become misleading once U5 ships. Apply a ≤3-line markdown-only correction to
  `recsys/units/unit-04-neighborhood-cf/{teacher-notes.md (≈:13-15), lesson.ipynb (cells 5, 24)}`: reword to "Unit 5
  trains a model to tell positives from *sampled* negatives — and discovers *which* negatives are the right ones (the
  reader's unobserved complement, not these exposure-biased `label==0` rows)"; and cell 24's "no factors to learn for
  the 818 cold books" → "no positive signal to learn from". Markdown-only → no re-exec of U4; `hygiene`/`noexec` still
  pass. This ships atomically with U5 (the unit that makes the correction true), NOT a separate errata.

### Phase G — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN with Units 1–5 + the Unit-5 milestone AND
`bash scripts/pre-merge-guard.sh --pr` OK. buildout holds (15). Confirm the MF exec stays within the whole-book CI
budget (design §9).

## Out of scope
No PyTorch/neural (two-tower = U8); no ANN/FAISS (U10); no feature/cold-start factors (U9); no generator change; no
`projects/project-*` map entry (capstone=U14); no checkpoint (Checkpoint A ends Part 1 at U6); no buildout removal.
**SVD:** design §8/§7 names SVD/`TruncatedSVD` for this unit; we mention it in a Phase-C aside (why plain SVD doesn't
fit sparse implicit feedback) but **ship gradient-descent MF, not an SVD path** — a deliberate omission, no concept
id, no `TruncatedSVD` code. **Unit 4 touch is IN-scope (markdown-only, ≤3 lines — Phase F):** U4's forward pointers
become misleading once U5 ships, so this plan corrects them atomically (see Phase F); this is the only cross-unit
change and it is markdown-only (no U4 re-exec). The Phase-C negatives beat remains the pedagogical reconciliation.

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

**[glm] — APPROVE WITH NITS** (empirical: MF 0.274 ≥ CF 0.252 ~9% margin; coverage/prereq/practice/syllabus close;
ids unique; design + protocol consistent). No Must.
1. `[OPEN]` **Should Fix** — "SGD" mislabels the ported training: `_reference_recommenders._learned_mf` is
   **vectorized FULL-BATCH gradient descent** (per-entity-averaged gradients), NOT per-pair SGD; literal SGD (58k
   pairs × 300 epochs Python loop) would blow the exec budget. Reword the concept + Phase B to "full-batch
   vectorized gradient descent on sampled implicit pairs".
2. `[OPEN]` **Should Fix** — SVD silently dropped: design §8 U5 names "latent factors, **SVD**, gradient descent +
   regularization" (§7 lists `TruncatedSVD`). Either fold a short low-rank/SVD aside into the lesson (no concept id)
   OR record the deliberate omission in `## Out of scope` — make it a decision, not a silent deviation.
3. `[OPEN]` **Nice** — name the shipped MF sizing (`n_factors`/`n_epochs`/`n_negatives`); measured dim=32/epochs=300/
   10-neg ≈ 33 s/fit, run ≥3× in CI (lesson+solutions+milestone) — in budget but state it (the CF-tolerance gate
   depends on the shipped config).
4. `[OPEN]` **Nice** — pre-declare likely `baseline.yaml` methods (`exp`, `bincount`, `concatenate`, `repeat`,
   `integers`) in Phase A to avoid a red Phase-G iteration.
5. `[OPEN]` **Nice** — `practices` drops `catalog-search` vs U2–U4; legal (practiced elsewhere) — confirm intentional
   (MF does no catalog search).

**[sol] — REJECT** (6 Must + 1 Should; premise verified MF 0.274 > CF 0.252). Corroborates [glm] + adds correctness:
1. `[OPEN]` **Must** — retrieve contract: a FITTED reader with empty `seen` must still receive `P[reader]·Qᵀ` recs
   (MF does not build its query from `seen`); only an UNKNOWN/no-factor reader → `[]`. (`seen` is for exclusion only.)
2. `[OPEN]` **Must** — objective/optimizer: `_learned_mf` uses **logistic** loss + **full-batch vectorized,
   per-entity-averaged gradient descent** with L2 — NOT squared loss, NOT SGD. PORT exactly (the 0.274 depends on it).
3. `[OPEN]` **Must** — numeric gate matching the harness (`test_signal_recoverability.py:89-93`): `MF ≥ 1.2×
   popularity AND MF ≥ content AND MF ≥ CF − fixed_tol` — not "small tolerance"/"MF > popularity".
4. `[OPEN]` **Must** — cold-item claim is FALSE as written: `_learned_mf` initializes a factor for EVERY catalog item
   and updates zero-train items when sampled as negatives, so "no interactions → no factor" is wrong. MF scores the
   WHOLE catalog (broader candidate coverage than CF's hard-zero), but cold items get weak negative-shaped factors →
   ranked low → real cold-start fix is U9. Define the item universe + cold behavior precisely.
5. `[OPEN]` **Must** — (= glm#2) SVD omitted vs design §8/§7: teach/mention it or record the omission in Out of scope.
6. `[OPEN]` **Must** — (= glm#3, elevated) state concrete `n_factors`/`n_epochs`/`n_negatives` + a NUMERIC
   per-notebook exec budget (design §9; ≤3 executions; benchmark ~27–33 s/fit).
7. `[OPEN]` **Should** — (= glm#5) `practices` omits `catalog-search`; confirm intentional (MF does no catalog search).

**[fable] — REJECT** (3 Must + 3 Should; **ran the port on the shipped data** — authoritative empirical findings).
Measured val (k=10, 60 cold readers excluded, 500 eligible, committed seed): random 0.012, pop 0.108, lexical 0.158,
item-item CF 0.252; MF port (complement negatives, lr0.5, reg0.05, 10-neg, catalog universe) d32/e300 = seeds
0.262/0.258/0.246/0.270/0.232 (**mean 0.254**, 16–21 s/fit), e500 → 0.267, e200 → 0.241, e100 → 0.153 (< lexical),
d16/e300 → 0.243. Paired MF−CF ≈ +0.010/+0.006/−0.006/+0.018/−0.020, SE ≈ 0.019 → **not significant**. Determinism,
leakage-safety, unknown-reader→[] all confirmed; all 60 cold readers have 0 train positives.
1. `[OPEN]` **Must** — Phase B's "keep training FAST (small `d`/epochs)" (:31/:67/:79) **contradicts its own gate**:
   <300 epochs at d32 drops MF below CF; e100 → 0.153 **< lexical** (fails `MF ≥ content`); d16 needs 300 epochs just
   to reach 0.243. PIN the shipped defaults to the harness config (`n_factors=32, n_epochs=300, learning_rate=0.5,
   reg=0.05, n_negatives=10`) + state the measured ~16–21 s/fit budget; Phase-D sweep split ≤4 fits/cell.
2. `[OPEN]` **Must** — **cross-unit contradiction**: U4 lesson + `unit-04-neighborhood-cf/teacher-notes.md:15`
   promise the log's `label==0` sampled negatives "are used for training in Unit 5 (MF)". The plan mandates
   complement sampling and ignores label-0 — and training on the log negatives **collapses MF to the random floor
   (0.016–0.028)** (exposure negatives carry the taste signal: generator exposes by `α·log pop + β·z_u`). Resolve:
   keep complement sampling AND add a Phase-C "why not the exposure negatives?" beat (measure both; teach
   exposed-not-engaged = exposure-biased negative → U13) that explicitly reconciles U4's forward pointer.
3. `[OPEN]` **Must** — (= sol#3) bind the CF comparison at a fixed seed with a stated tolerance: at `seed=0`
   `mf_hit >= cf_hit − 0.03` (margin +0.010; worst seed −0.020), plus hard gates `mf >= 1.2*pop`, `mf >= pop + 0.03`,
   `mf >= lexical`. Reword "matches/edges CF" → "on par with CF (≈0.26 vs 0.25, within noise over 500 readers)".
4. `[OPEN]` **Should** — (= glm#1/sol#2) full-batch per-entity-averaged GD (+ logistic loss), not SGD/"(stochastic)".
5. `[OPEN]` **Should** — (= glm#2/sol#5) SVD aside in Phase C or an Out-of-scope note.
6. `[OPEN]` **Should** — record the measured numbers in "Why this works" so the gate values are traceable to the
   shipped data (not the generator-sized harness).
7. `[OPEN]` **Nice** — `bincount`-per-column is the fast gradient path (not `np.add.at`); milestone/lesson could show
   the ~818 cold ITEMS get only negative gradient (scores pushed down) — concretizing the cold-item limit.

### Plan-review outcome (round 1): **NOT consensus — [sol] + [fable] REJECT, [glm] APPROVE WITH NITS, [self] APPROVE.** Both rejects converge on: pin defaults to d32/e300 (small-epochs fails the gate), logistic full-batch GD (not SGD), numeric seed-0 gate `mf ≥ cf − 0.03` + hard pop/lexical gates, complement negatives + reconcile U4's exposure-negative forward pointer (log negs collapse MF to the floor), honest "on par with CF ≈0.26 vs 0.25" (not "edges"), fix retrieve contract (known reader+empty-seen still recommends; only unknown→[]), define item universe/cold-item behavior, SVD aside, record measured numbers. Folding all → **v2** below, then round-2 re-review (all four; glm back Monday).

### Round 2 (on v2)

**v2 changelog** (folds all round-1 findings): (a) objective reworded everywhere to **logistic loss + full-batch
per-entity-averaged gradient descent** (not SGD/squared) [glm#1/sol#2/fable#4]; (b) retrieve contract fixed — a
**known** reader with empty `seen` still returns recs; only an **unknown/no-factor** reader → `[]` [sol#1]; (c)
Phase-B gate made numeric at seed 0: `mf ≥ cf − 0.03 AND mf ≥ 1.2×pop AND mf ≥ pop+0.03 AND mf ≥ lexical`
[sol#3/fable#3]; (d) **defaults PINNED** `d32/e300/lr0.5/reg0.05/10-neg` + ~16–21 s/fit budget — removed the
gate-failing "small/few epochs" language [fable#1/sol#6/glm#3]; (e) **item universe = full catalog, readers = ≥1
train positive**; cold *reader* → `[]` vs cold *item* → negative-shaped low-scored factor; honest coverage [sol#4];
(f) **cross-unit reconciliation** — Phase-C negatives beat honors U4's forward pointer (complement vs exposure
negatives; log negs collapse MF to floor) [fable#2]; (g) "edges CF" → **"on par with CF"** everywhere + measured
table in "Why this works" [fable#3/#6]; (h) **SVD** aside in Phase C + Out-of-scope note [glm#2/sol#5/fable#5]; (i)
`baseline.yaml` methods pre-declared incl. `bincount` fast path [glm#4/fable#7]; (j) `catalog-search` practice-drop
confirmed intentional [glm#5/sol#7]; (k) cold-item illustration added to milestone [fable#8].

**[self] — APPROVE (round 2).** All 6+6 round-1 findings folded and internally consistent: objective is logistic
full-batch GD throughout (Scope/concept/Phase B/C/D agree); retrieve contract correct for MF (known reader scored by
`P·Qᵀ` independent of `seen`; unknown → `[]`); Phase-B gate numeric and satisfied at the measured seed-0 values
(MF 0.262 ≥ CF 0.252 − 0.03, ≥ 1.2×0.108, ≥ 0.108+0.03, ≥ 0.158); defaults pinned to the only config that clears the
gate (measured cliffs recorded); item universe/cold-reader-vs-cold-item defined honestly; U4 forward pointer honored
in-scope via the Phase-C negatives beat (no cross-unit edit); SVD mentioned-not-shipped (design §8 reconciled);
`catalog-search` drop justified. Named Phase G retained; project-first; ≥6/≥2-stretch/≥3-asserts; buildout holds (15).
No [self] blockers.

**[glm] — round-2 UNAVAILABLE (tooling).** The opencode companion failed at the invocation layer: both
`opencode-go/glm-5.3` and the `volcengine-plan/glm-5.3` fallback exited 1 with the identical opencode-CLI `--help`
dump (an invocation-layer problem with the companion, not model selection). No round-2 content. **Standing position:**
[glm] returned APPROVE WITH NITS in round 1 with NO Must; all 5 nits are folded into v2 (changelog items a/h/c/i/j),
so its substantive review is satisfied — only a confirmation pass is missing. If [sol]+[fable] APPROVE on round 2,
this becomes a 3-of-4 consensus (glm round-1 APPROVE-WITH-NITS, all nits resolved) → surface the 3-of-4 trust fork to
the user before merge (per memory: 3-of-4 needs user OK).

**[fable] — APPROVE WITH NITS (round 2).** All 3 Must + 3 Should from round 1 correctly folded; no new blocker.
Resolution confirmed: pinned defaults + cliffs + ≤4-fits/cell (Must1); Phase-C (2b) negatives beat honest (Must2);
numeric seed-0 CF gate + "on par" wording (Must3); logistic full-batch GD (Should4); SVD aside + Out-of-scope
(Should5); measured table (Should6). New nits:
1. `[OPEN→FIXED v2.1]` **Should** — U4 as a STANDALONE artifact still states two now-false claims that the Phase-C
   beat doesn't touch: `unit-04-neighborhood-cf/teacher-notes.md:13-15` and `lesson.ipynb` cells 5 + 24
   ("the `label==0` negatives are *used as training signal* in Unit 5") — v2 proves they're *harmful* for that job.
   Fix in-scope: a ≤3-line markdown-only U4 touch added to **Phase F** (reversing the earlier "no edit to Unit 4").
2. `[OPEN→FIXED v2.1]` **Nice** — related U4 drift (cell 24: "no factors to learn for the 818 cold books") →
   reword to "no positive signal to learn from" for consistency with U5's two-case cold story. Same Phase-F touch.
3. `[OPEN→FIXED v2.1]` **Nice** — Phase B: the Opus port will consume `default_rng(0)` differently, so its seed-0 draw
   is a fresh sample of the 0.232–0.270 spread, not 0.262. If the shipped port's seed 0 lands below `cf − 0.03`, do
   NOT loosen the gate or shop seeds silently — report it and state the chosen seed in the plan. Added to Phase B.
4. `[OPEN→FIXED v2.1]` **Nice** — word lesson/milestone prose "about 0.25–0.26, within noise of CF" so a 0.24x draw
   isn't read as contradicting a printed number. Added to Phase C/E.
5. `[NOTED]` **Nice** — Phase B test docstring should cite the shipped-data table (:23-29), not the generator-sized
   harness numbers in historical round-1 text. (Phase B already binds the :23-29 table.)

_([sol] round-2 verdict appended on hand-back. v2.1 amendments below fold [fable]'s round-2 Shoulds/Nices — additive, [sol]-neutral.)_

## Content Review

<!-- appended pre-PR -->

## Post-Execution Report

<!-- appended before ship -->
