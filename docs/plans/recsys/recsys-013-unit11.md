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

## Determinism & budget (per U8 pattern — binding; timing MEASURED by the probe)
Same CPU-determinism contract as U8/U9 (`torch.manual_seed` + `use_deterministic_algorithms(True)` + single-thread,
SAVED/RESTORED around `fit`; torch imported LAZILY inside `fit` only; `retrieve`/`load`/`artifact` torch-free on numpy
weights; group-free suite never imports torch/faiss — extend the import-blocked-subprocess test). Determinism GATE =
identical top-k ranking + `allclose` (design §184, never exact-float; probe: two seeded fits allclose on every weight).
**Budget (measured shape — NOT "per-fit ≲15 s"):** the MLP fit is **<1 s**, but **feature assembly ≈ 14–15 s per pass
over 540 readers** (dominated by 6×`retrieve`/reader) and the clean recipe fits the 6 paths **TWICE** per notebook
(full + profile-75% — MF + two-tower ≈ 60 s of torch/numpy fits total). So pin: **assemble the feature matrix ONCE
per notebook and cache it**; the ablation reuses the cached matrix (4 models × <1 s) with one eval pass each (~15 s);
keep assembly and ablation/eval in SEPARATE cells so each stays far under the 120 s/cell cap. Aggregate adds ~2–3 min
to the whole-book CI budget — Phase B reports the aggregate fit/assembly count.

## Why this works on the data (MEASURED — [fable] probe; Phase B re-confirms on shipped code)
The probe measured the central question and **corrected the thesis + the training recipe**. Two things matter most:
the **training-time leak** (the naive recipe tanks) and **where the lift actually comes from** (content, not score
combination).

**1. The naive recipe LEAKS and tanks — the headline teaching moment.** If the reranker's labels are the reader's
train positives and the retrieval paths are fit on that *same* train, the paths have **memorized** those positives:
"high CF / two-tower score ⇒ positive" is learned from inflated in-train scores that val candidates never exhibit
(distribution shift). Measured: mlp-all **0.278 (pool 30) / 0.288 (pool 50)** — *below* the two-tower (0.340) and even
below plain 6-way score-order (0.324/0.348). This fails the unit's own "must not tank" gate and is the best
common-mistake in the unit.

**2. The clean recipe works — a time-ordered holdout INSIDE train.** Per reader, the latest ~25% of train positives
(≥1) become the reranker's **labels**; the earlier 75% is the retrieval **`seen` profile**; the paths used to build
**training features** are fit on that 75% only (one extra fit each — MF + two-tower ≈ 24 s), and the trained reranker
is applied over the **full-fit** paths at serving/val time. Measured (val, k=10, 500 readers, SE ≈ 0.021):

| path / ranker | hit@10 | coverage |
|---|---|---|
| two-tower (U8) | 0.340 | 0.177 |
| U6 4-way blend | 0.306 | 0.333 |
| U10 hybrid | 0.362 | 0.192 |
| 6-way equal-weight score-order over the pool (pool 50) | 0.348 | 0.217 |
| **reranker, clean recipe — all-feature MLP (pool 50, seed 0)** | **0.346** | 0.195 |
| reranker, **content-only** (ablation) | **0.380** | ~0.12 |
| reranker, linear (all-feature) | 0.364 | 0.133 |

So the leakage-safe all-feature reranker **does NOT beat a careful fixed blend — it ~TIES the 6-way score-order
(0.346 vs 0.348) and ~matches the two-tower (0.340)**; coverage (0.195) edges the two-tower (0.177) but stays below
the U6 blend (0.333). The honest headline is **not** "the learned reranker wins."

**3. Two leak modes — the real payoff — and where the (small) lift actually lives.** The unit teaches TWO distinct
leaks: (i) **path-memorization** — the naive recipe (labels = train positives, feature-paths fit on the same train)
tanks to **0.288** (§1); (ii) **held-out-event inflation of `log_pop`** — before the fix, a repeat-read item's
held-out (label-period) event was counted into the GLOBAL popularity feature — never that reader's own positive (the
pool excludes their profile), but a book that is a held-out positive for OTHER readers (cross-reader leak) — inflating the
all-feature reranker by **+0.018 (0.364 → 0.346)** — a *phantom* win the content gate caught. With both leaks closed:
the only genuine lift is from **CONTENT features** — **content-only 0.380 > score-order 0.348** (and > two-tower
0.340), while the **all-feature MLP (0.346) DILUTES** it (the correlated path scores add noise, not signal), and
**linear ≈ MLP**. 17 features = 6 calibrated per-path scores + 6 presence flags + n_paths + content (genre_frac,
genre_cos vs the reader's history, author_frac, log_pop); at TRAINING time the feature-paths AND the popularity count
come from the **profile rows** that exclude every occurrence of a held-out label item, and the per-reader genre/author
history comes from the reader's profile item set (a repeat-read keeps its earlier read) — no held-out event enters any
training input; serving uses full train. The lesson: "a learned ranker's value is the *content features a single path can't see*, not combining
correlated path scores — and a naive reranker leaks in more than one way."

**4. Pool recall ceiling (retrieval caps reranking).** Any-relevant-in-pool recall: **0.716 @ pool 30, 0.772 @ pool
50** — hit@10 of *any* reranker is capped there; motivates pool=50. **Pin pool=50.**

**Gate (an honest regression gate, re-pinned after the user-approved post-leak-fix reframe — NOT predeclared):** (a) `reranker.hit@10 ≥
two_tower.hit − 0.01` (not tanked — 0.346 ≥ 0.330); (b) **the lift is content:** `content_only.hit ≥
six_way_score_order.hit` (0.380 ≥ 0.348) AND the all-feature reranker ~ties the fixed order within noise
(`reranker.hit ≥ six_way − 0.01` → 0.346 ≥ 0.338); (c) **RECORD, do not gate:** the all-feature MLP ≤ content-only
(dilution), `linear ≈ MLP`, the hybrid comparison, and coverage; (d) **two negative tests:** the naive same-train
recipe tanks below the clean recipe (path-memorization leak), AND no held-out repeat-read event enters the training
`log_pop` (the event-inflation leak). Determinism: two seeded fits `allclose` on every weight (§184).

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
  buildout already removed at U10). `baseline.yaml`: declare the new `x.name(...)` idioms the authored cells use —
  torch MLP idioms the shipped reranker uses (`Linear`, `relu`/`ReLU`, `Sequential`, `BCEWithLogitsLoss`,
  `sigmoid` if used) + `NeuralRerankerPath` + any numpy/feature accessors (`calibrate` is already an accessor on
  paths). Add ONLY what the authored cells actually call (verify + trim unused at Phase G concept-scan, as in
  recsys-011/012).
- `unit-11-neural-reranking/manifest.yaml`; `syllabus.md` arc row `| 11 | \`unit-11-neural-reranking\` | unit | 3 |
  <hook> |` after the U10 row; rebuild PDF.
**Verify:** manifest/prereq/coverage/syllabus green (lesson-budget 33.5 ∈ [30,60]; introduction completeness holds);
concepts unique.

### Phase B — `bookrec` reranker path (Opus subagent; PyTorch, lazy, CPU-deterministic)
Dispatch an **Opus subagent**. STUDY `blend.py` (calibration semantics — but note its `Candidate` keeps only the
SUMMED score + a provenance string, so per-path scores are NOT recoverable from blend output), `protocol.py`
(`Candidate`, `calibrate_scores`, `fit`/`retrieve`/`artifact`/`load`, `order_candidates`), `rank.py` (the ordering
key — see API note), `two_tower.py` (lazy-torch/determinism/torch-free-persistence to mirror), `scoreboard.py`
(`_seen_and_relevant`), `evaluate.py`/`diversity.py`, `catalog.py` (genre/author), and the probe reference at
`scratchpad/probe_rerank.py`. Add `bookrec/rerank.py` (torch lazy in `fit`):
- **Features (from the PRE-BLEND per-path lists — NOT blend's Candidate):** per reader, take each path's top-`pool=50`
  `retrieve` list, `calibrate` each list to [0,1], union by item id. For each pooled candidate build a **17-dim**
  vector: 6 calibrated per-path scores (absent path → 0.0) + 6 presence flags + n_paths + content (genre_frac,
  genre_cos of candidate genres vs the reader's **history** genre vector, author_frac, log_pop from interaction
  counts). Persist the feature ordering/spec in the artifact. **CRITICAL (leakage) — every feature uses the reader's
  PROFILE history, which differs by phase:** at TRAINING time the "history" / counts are the **75% profile only** (see
  below) so no held-out *event* enters any feature or statistic (a repeat-read item can stay in the profile item set
  via its earlier read; paths + popularity use the label-item-excluded `profile_rows`); at SERVING/val the history is
  the full train. Same code, phase-dependent profile. (`log_pop` / popularity counts too — compute from the 75% at train, full
  train at serve.)
- **Training recipe (THE fix — time-ordered holdout INSIDE train; the naive recipe LEAKS + tanks, see §Why):** per
  reader, split train positives time-ordered — latest ~25% (≥1) = reranker **labels**; earlier 75% = the retrieval
  **`seen` profile**. Build ALL TRAINING-time inputs from the **75% profile only** — both the retrieval paths used for
  the per-path-score features (one extra fit per path; MF+two-tower ≈ 24 s) AND the content/popularity statistics
  (genre-history vector, author history, log_pop counts). The held-out 25% supplies ONLY the positive labels — no held-out
  event enters a feature. Train a small MLP (17→32 ReLU→1, BCEWithLogits, Adam, ~30 epochs, ~10 sampled pool negatives per positive).
  At serving/val, score the pool from the **full-fit** paths + full-train content/popularity with the learned numpy
  MLP. TRAIN-ONLY throughout; a regression must prove val/test rows cannot change the fitted artifact.
- `NeuralRerankerPath(BaseRetrievalPath)` (name `"reranker"`, version `"1"`). **API (reconcile `rank.py`):** the
  learned per-candidate **ordering key** is authoritative (honours `rank.py`'s "a learned reranker replaces the
  ordering key"); expose it as a `rerank(...)` scoring fn and wrap it in the thin `NeuralRerankerPath` for the
  scoreboard/registry (scored like every other path). The constructor carries the train-time split + the profile-refit
  mechanism (a `path_factory`/refit callback, or two registries — subagent picks + documents; the lesson is honest
  that this IS one refit on the profile split, not "reuse fitted paths"). `retrieve` builds the pool (full-fit paths),
  scores via the numpy MLP, excludes `seen`, top-k; unknown reader → `[]`. `load`/`artifact` persist numpy MLP weights
  + feature spec (torch-free). Deterministic. Export (no eager torch). A linear-logistic variant + pairwise/BPR =
  stretch knobs (linear ≈ MLP measured).
- Tests (routed, new `tests/test_unit11.py`): **(gate)** `reranker.hit ≥ two_tower.hit − 0.01` (not tanked) AND
  `content_only.hit ≥ six_way_score_order.hit` (the content lift) AND all-feature `reranker.hit ≥ six_way − 0.01`
  (ties within noise); **(two negative tests — codify the TWO leaks)** the naive same-train-label recipe tanks BELOW
  the clean recipe (path-memorization), AND no held-out repeat-read event enters the training `log_pop`
  (event-inflation); **(record, not gate)** all-feature MLP ≤ content-only (dilution), `linear ≈ MLP`, the hybrid
  comparison, and coverage; determinism (ranking + allclose; array_equal bonus print only); feature-ablation recorded
  (content-only ≥ scores-only); empty-seen/unknown-reader contract; fit→artifact→load identical (torch-free);
  val/test-invariance of the fitted artifact; registers as `reranker-v1`. **EXTEND the import-blocked subprocess test**
  (`tests/test_unit07.py`)
  to cover `rerank` (group-free imports no torch/faiss).
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/ -q` green + group-free suite imports no torch/faiss;
**report reranker hit@10 + coverage vs two-tower / 6-way score-order / U6-blend / U10-hybrid, the feature-ablation
(content-only vs scores-only), the leak-recipe number, linear-vs-MLP, the pool recall ceiling, and per-fit/assembly
time + aggregate count** so the lesson is data-bound and in budget.

### Phase C — lesson.ipynb (Opus subagent; project-first)
Hook: "our paths each see one slice of the signal — popularity, text, behaviour. What if a model *learned* to rank a
reader's candidate pool?" From scratch → reveal: (1) the two-stage split (cheap retrieval pool → expensive precise
rank) + the score-order baseline `rank.py` already does, and the **pool recall ceiling** (0.716@pool30 / 0.772@pool50
— the reranker only re-orders the pool, so retrieval caps hit@k; pin pool=50); (2) **ranking features** — build the
17-dim per-candidate vector from the pre-blend per-path calibrated scores + content signals (genre/author affinity vs
the reader's TRAIN history, log-popularity); (3) **the leakage trap (headline)** — train the reranker the *naive* way
(labels = train positives, paths fit on the same train) and WATCH IT TANK to ~0.28 (below score-order), because the
paths memorized those positives; then fix it with a **time-ordered holdout inside train** (latest 25% = labels, earlier
75% = profile the feature-paths are fit on); (4) **learning to rank + reveal** `NeuralRerankerPath`: a **linear**
logistic combiner first (the U6 blend's fixed weights, now *learned*) → the MLP, and show **linear ≈ MLP** here; score
on `val` — the all-feature reranker (**0.346**) **~ties** the 6-way score-order (0.348) and ~matches the two-tower
(0.340): a leakage-safe learned reranker does NOT beat a careful fixed blend here; (5) **the second leak + the feature
ablation** — closing the `log_pop` held-out-event leak removes a **+0.018 phantom** win (0.364→0.346), and the only
genuine lift is **content** (content-only **0.380** > score-order 0.348; the all-feature MLP *dilutes* it with the
correlated path scores; linear ≈ MLP). Honest headline: the reranker's value is the two-stage architecture + the
content features, and the unit's payoff is the **two leak modes**. Bridge: U12 adds sequence features; U13 revisits
fairness of a learned ranker + coverage; U14 capstone wires retrieval→blend→rerank end to end. ASCII only;
`rank(exclude=seen)`; reuse `bookrec`; tiny/seeded/in-budget.
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
`## Goals`, `## Pacing` (60–90 min / 2–3 sittings, hook first, all exercises), `## Common mistakes` — lead with the
**MEASURED leakage trap** (training the reranker on labels = train positives while the feature-paths are fit on that
same train → the paths memorized them → the reranker learns inflated in-train scores → val **tanks to ~0.28**, below
score-order; fix = time-ordered holdout inside train); then the **second, subtler leak** (a repeat-read item's
held-out event counted into the global `log_pop` → a **+0.018 phantom** win, 0.364→0.346; fix = count training
popularity from the label-item-excluded profile rows); then: **expecting a learned reranker to beat a careful fixed
blend** (it does NOT here — the all-feature MLP ~ties the 6-way score-order 0.346≈0.348); expecting the lift from
combining path scores (it comes from CONTENT — content-only 0.380 > 0.348; the all-feature MLP *dilutes*; linear ≈
MLP); forgetting the reranker only re-orders the POOL (recall ceiling 0.72–0.77 caps hit@k); non-determinism.
`## Discussion prompts` (why two-stage retrieve-then-rank; the two leak modes and their fixes; why content features
beat combining correlated scores here; when a learned reranker WOULD beat a fixed blend; the recall ceiling).
`## Differentiation`.

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

### Round 1

**[self] — APPROVE.** Registry closes: `requires` ⊆ introductions of U1 (retrieve-then-rank/offline-evaluation/
top-k-ranking-metrics), U4 (implicit-feedback), U6 (beyond-accuracy/score-blending), U8 (two-tower/neural-training),
U10 (hybrid-retrieval); `practices ∩ introduces = ∅`; 3 new ids globally unique (0 hits); lesson-budget 30.5→33.5 ∈
[30,60] (buildout already removed at U10). Architecture reuses the EXISTING infra as designed — `blend.py`'s merged/
calibrated/deduped pool + per-path provenance scores are the reranker's features; `rank.py` already says "a learned
reranker replaces the ordering key in a later unit"; `fit(interactions, catalog=None)`/`retrieve` protocol intact;
torch isolation mirrors U8 (lazy fit-only import, torch-free retrieve/load/artifact, import-blocked subprocess
extended), §184 tolerance/rank-based determinism. **Honest framing:** the plan does NOT pre-assume the reranker beats
the two-tower (0.340) or the blends (U6 0.306 / U10 hybrid 0.362) — per-path signals are correlated, so a learned
combiner may only tie; the gate is directional (reranker ≥ two_tower − 0.01 AND a Phase-B-pinned comparator vs the
blend), and the lesson frames the reranker as the two-stage *architecture* production needs, measured honestly. The
retrieval **recall ceiling** (the reranker only re-orders the pool) is acknowledged (Phase F + Out of scope). Leakage
guarded (train-only features/labels, val scoreboard, test sealed). Named Phase G; project-first; ≥6/≥2-stretch;
teacher-notes; milestone; no scope creep (sequence=U12, ethics/ChkptB=U13, capstone=U14). Open for Phase B/gate
([fable]-probed): whether the reranker beats/ties the two-tower + blends on hit@10, the feature-ablation, per-fit time.
No [self] blockers.

**[sol] — REJECT (round 1)** (closure/budget/determinism/scope confirmed; 2 Must + 2 Should, all folded to v2):
1. `[OPEN]→[FIXED v2]` **Must** — per-path score features don't exist in `blend.py` output (`Candidate` keeps only
   the summed score + provenance string). → v2 extracts features from the **pre-blend per-path lists** (6 calibrated
   scores + 6 presence flags + n_paths + content), absent-path = 0.0, persisted feature ordering.
2. `[OPEN]→[FIXED v2]` **Must** — training-pool trap: retrieval excludes `seen` = the reader's train positives, so the
   pool has no positives to train on. → v2 **time-ordered holdout inside train** (latest 25% = labels, earlier 75% =
   `seen` profile; feature-paths fit on 75%); + a val/test-invariance regression on the fitted artifact.
3. `[OPEN]→[FIXED v2]` **Should** — reconcile `rank.py` (ordering key) vs a `RetrievalPath.retrieve` wrapper. → v2: the
   learned ordering key is authoritative; a thin `NeuralRerankerPath` wraps it for the scoreboard; both documented.
4. `[OPEN]→[FIXED v2]` **Should** — predeclare the exact comparator (no post-hoc "OR another axis"). → v2 pins
   `reranker ≥ two_tower − 0.01` AND `reranker ≥ six_way_score_order`; hybrid + coverage RECORDED (coverage is a loss),
   not gated.

**[fable] — APPROVE WITH NITS (round 1, full seeded probe).** Measured and folded (2 Must + 4 Should + 2 Nice):
- Must — the naive recipe (labels=train-positives, paths fit on same train) **LEAKS by memorization → tanks to
  0.278/0.288** (< two-tower 0.340−0.01, < score-order 0.324/0.348). Clean time-ordered-holdout recipe → **0.35–0.39**
  (edges two-tower, ties hybrid 0.362) but **coverage collapses to 0.12–0.19**. → v2 §Why + Phase B/C/F.
- Must — re-frame the thesis: the lift is from **CONTENT features** (content-only 0.384–0.390 ≥ scores-only ≈
  score-order), **linear ≈ MLP** (non-linearity adds nothing). → v2 §Why/#3 + Phase C/D ablation + Phase F.
- Should — ship the **pool recall ceiling** (0.716@30 / 0.772@50; pin pool=50) + the real **budget shape** (MLP fit
  <1 s but feature assembly ~14–15 s/pass + paths fit TWICE ~60 s → cache features once, split cells) + the API
  split (path refit expressed as a factory/two-registries) + a **negative test** codifying the leak. → v2 Determinism
  & budget, Phase B/E.
- Nice — linear-logistic→MLP from-scratch→reveal ladder; pin pool=50. → v2 Phase B/C.

### v2 changelog
Rewrote §Why (measured leak + clean-recipe table + content-carries-lift + coverage loss + recall ceiling + predeclared
gate), §Determinism&budget (real timing + feature caching), Phase A (MLP baseline idioms), Phase B (pre-blend
features, time-ordered-holdout training recipe, rank.py API reconciliation, predeclared comparator + negative/leak +
val-test-invariance tests, pool=50), Phase C (leak as headline, linear→MLP ladder, content-carries-lift, recall
ceiling), Phase F (leak-trap headline mistake + coverage-loss honesty).

**[self] — APPROVE (round 2).** v2 binds every gate to the [fable] probe and resolves both [sol] Musts (pre-blend
feature source; time-ordered-holdout training that avoids the memorization leak) + the Shoulds (rank.py API; pinned
comparator). The thesis is now honest and richer: a learned reranker edges accuracy via content features (not score
combination; linear ≈ MLP), at a real coverage cost, and the naive recipe's leak is the headline lesson. No remaining
[self] blocker; dispatching [sol] round-2 re-review.

### Round 2
**[sol] — REJECT (round 2)** — all 4 round-1 findings confirmed resolved; 1 NEW Must:
1. `[OPEN]→[FIXED v3]` **Must** — training-time CONTENT features can still leak the holdout labels: the 75% restriction
   covered only the fitted retrieval paths, but the content stats (genre-history vector, author history, `log_pop`
   counts) were still computed from the FULL train history — which includes the held-out 25% label items. → **v3:**
   every TRAINING-time feature/statistic (content + popularity + path scores) uses the **75% profile only**; full-train
   history is serving-only (same code, phase-dependent profile). Folded into §Why/#3 + Phase B features & training
   bullets. ([sol] confirmed the split is feasible — 540 warm readers, ≥2 train positives each.)

**[self] — APPROVE (round 3).** v3 closes the content-feature leak: at training time ALL inputs (paths + content +
popularity) are the 75% profile; the 25% supplies only labels; serving uses full train. Leakage-safe and symmetric.
No remaining [self] blocker; dispatching [sol] round-3.

**[sol] — APPROVE (round 3).** Leak fully closed — every training-time feature/statistic (path scores + genre/author
history + `log_pop`) uses the 75% profile only; the 25% supplies only labels; full-train is serving/val-only. No
contradictory requirement, no new blocker.

### Plan-review outcome (FINAL): **CONSENSUS — [self] APPROVE (r3) · [fable] APPROVE WITH NITS (all folded) · [sol] APPROVE (r3).**
Three would-be-fatal design issues caught + fixed before any content: (1) naive training recipe leaks by memorization
→ tanks 0.28 (time-ordered holdout fix); (2) per-path features not in blend's Candidate (extract from pre-blend
lists); (3) training-time content features leaked the 25% labels (all training inputs = 75% profile). Cleared for
implementation (Phases A→G).

## Content Review

### Review 1 — [self] (2026-10-06)
- **Verdict**: APPROVE.
Reviewed lesson/exercises/solutions/milestone/teacher-notes + `rerank.py` + tests against the 8 gate duties.
1. **Project-first** ✓ — lesson cell 0 opens with the "each path sees one slice — can a model LEARN to rank the
   pool?" hook (not drill).
2. **Correctness / honest thesis** ✓ — the leakage trap is the headline (naive recipe tanks ~0.288; clean
   time-ordered 75/25 holdout → 0.364); ALL training-time features/paths/stats use the 75% profile, 25% = labels only
   (leakage-safe); reranker edges two-tower (0.340)/ties hybrid (0.362) but coverage is an honest LOSS (0.186 vs U6
   0.333); content-only (0.384) ≥ scores-only (0.346), linear ≈ MLP; retrieval recall ceiling (0.772) caps hit@k.
   Determinism tolerance/rank-based (§184). No overclaim.
3. **Ex3 invariant** ✓ (self-caught, fixed) — leakage-safety is the training pool EXCLUDING the profile, NOT set
   disjointness (re-read books sit in both sets, ~33% of readers); exercises Ex3 reframed to match the solution; no
   residual "disjoint" claim in shipped content; lesson/teacher-notes carry none.
4. **Taught-before-assessed / heavy-dep isolation** ✓ — the 3 concepts introduced in the lesson, assessed in
   exercises; torch+faiss lazy, group-free import pulls neither (extended test_unit07), val-only (test sealed).
5. **Pacing / stretch** ✓ — assemble-once/reuse budget; 8 exercises (6 core + 2 Challenge); teacher-notes 60–90 min.
No [self] blockers. Awaiting [sol] + [fable] blind-solve reviews.

### Review 2 — [fable] (2026-10-06)
- **Verdict**: APPROVE WITH NITS (no Must). Full blind solve reproduced every number (0.772/0.716, 0.288, 0.364/0.186,
  content-only 0.384 ≥ scores-only 0.346, linear 0.366 ≈ MLP 0.364); leakage story sound; no residual "disjoint"
  claim; heavy-dep isolation confirmed.
1. `[OPEN]→[FIXED]` **Should** — lesson "a real, if modest, win... within a standard error or two" is
   self-contradictory (+0.024 ≈ 1 SE) → "a directional, within-noise edge (~1 SE)".
2. `[OPEN]→[FIXED]` **Should** — teacher-notes Pacing names "pairwise" as if an exercise → relabel as a differentiation
   stretch (done inline).
3. `[OPEN]→[FIXED]` **Nice** — lesson/docstring "25% never enters a feature" imprecise given repeat reads → precise
   wording (subsumed by [sol] Must fix below).
4. `[OPEN]→[FIXED]` **Nice** — solutions Ex7/Ex8 markdown lack the `stretch` tag their code cells carry → add.
5. `[OPEN]→[FIXED]` **Nice** — coverage "~0.12–0.19" is a seed range → note it's across seeds 0/1/2 (seed-0 ~0.186).

### Review 3 — [sol] (2026-10-06)
- **Verdict**: REJECT (blind solve matched all numbers; targeted tests 11/11 pass incl. determinism + torch/faiss
  isolation; project-first/audience/pacing/coverage-honesty all pass). One Must:
1. `[OPEN]→[FIXED]` **Must** — the clean recipe is NOT event-level leakage-safe for **repeat reads**:
   `split_profile_labels` collapses timestamped events into item SETS, so a repeat-read item in BOTH the profile and
   label sets still has its held-out event counted into the global `log_pop` (`_train_positive_counts(rows,
   keep=profile)` filters by item-membership), while the path refit excludes every occurrence. The claim "every
   training-time input comes only from the 75% profile" is therefore false at the event level — unacceptable in a
   leakage-teaching unit. → **Fix:** compute the training popularity count from the SAME label-item-excluded
   `profile_rows` the paths use (`train_counts = _train_positive_counts(profile_rows)`), so NO held-out event enters
   the paths OR log_pop (a repeat-read's earlier events are conservatively dropped too); + a repeat-read regression
   test; + precise prose (plan §3 + lesson + docstring). Result is unaffected (log_pop is a minor global feature;
   Phase B re-measures to confirm reranker ≈ 0.364). The public set-based `split_profile_labels` API (Ex3's overlap
   teaching) is unchanged.

### Round 2 (re-review after the fold + user-approved reframe)
- **[fable] — APPROVE WITH NITS (r2).** Re-ran test_unit11 (10 passed) + an independent blind solve of Ex3/Ex4/Ex6
  (+Ex5/Ex7): every number matches code, solutions and lesson outputs; leak fix verified correct (no held-out event
  of any reader enters any training input); second-leak sections accurate; exercises↔solutions matched; hygiene,
  project-first, 2 Challenges OK. Nits, all `[FIXED]`: (Should) `rerank.py` docstring still said "edges the
  two-tower / ties the hybrid" → tie-with-score-order + content-only lift; (Should) teacher-notes "accuracy up" /
  "trades coverage for accuracy" → tie on accuracy / coverage given up without an all-feature win; (Nice) lesson
  notes linear's 0.364 is within one SE of 0.348; (Nice) teacher-notes Common mistakes gains a leak-#2 bullet.

- **[sol] — REJECT (r2).** Code fix confirmed correct (paths + `log_pop` from label-item-excluded `profile_rows`;
  serving counts full-train; tests 10/10, numbers reproduced). Residuals, all `[FIXED]` in r3:
  1. **Must** — the leak explanation + regression test modelled the wrong causal path: the pool excludes each
     reader's profile, so a repeat-read item is never *that reader's* positive; the real defect is a **cross-reader**
     leak (a held-out, label-period read inflates the GLOBAL `log_pop` of a book that is a held-out positive for
     OTHER readers). → reworded lesson cell 18, exercises/solutions Ex3 (cell 6), milestone cell 9, `rerank.py`
     docstring, plan §3, teacher-notes leak #2; regression test rewritten with a `seen`-respecting fake path and two
     readers (reader 1's held-out A read leaks via the old `keep=profile` count onto reader 2's held-out A positive;
     the fix leaves that row's `log_pop` at 0).
  2. **Should** — wording: genre/author history comes from the profile ITEM SET (not `profile_rows`); the gate was
     re-pinned after the reframe, so it is an honest regression gate, not "predeclared". → both reworded.

- **[sol] — APPROVE WITH NITS (r3).** Cross-reader causal story correct; simulated the old `keep=profile` count
  (count 3 → reader 2's positive `log_pop`=1.0 vs 0.0 now), so the regression fails against the pre-fix code. Nits
  `[FIXED]`: provenance wording in exercises/solutions cell 6, teacher-notes and plan Phase B now says no held-out
  *event* enters a feature (paths + popularity from `profile_rows`; genre/author from the profile item set); plan MLP
  input 18→17.

### Content-review outcome (FINAL): **CONSENSUS — [self] APPROVE · [fable] APPROVE WITH NITS (r2, folded) · [sol] APPROVE WITH NITS (r3, folded).**

### Author response (fold) — 2026-10-06
Folding all. Docs (plan §3 precise prose; teacher-notes pacing) done INLINE. Code + notebooks folded by a focused
subagent: event-safe log_pop count + repeat-read regression test in `rerank.py`/`test_unit11.py`; lesson
within-noise wording + precise leakage note + seed-range note; solutions Ex7/Ex8 stretch tags; re-measured +
re-executed clean. Re-run ci-local + re-review [sol] (rejecter) after.

### Pre-gate self-caught fixes (during the build)
- `[FIXED]` **Ex3 "disjoint" framing wrong** — the exercises Ex3 statement said "confirm labels disjoint from its
  profile" with a `prof.isdisjoint(lab)` TODO, but `split_profile_labels` builds SETS and a re-read book lands in both
  the 75% profile and the 25% labels, so disjoint is False for ~33.5% of readers (reader 0: profile∩labels={296,651}).
  The leakage guarantee does NOT depend on set-disjointness — it depends on the training **pool excluding the profile**
  (`seen`), so an overlapping re-read is never a training candidate and the positive rows are exactly `labels −
  profile`. Surfaced by the independent solutions solver (which already asserted the real invariant). Fixed the
  exercises Ex3 markdown + scaffold to match (measure the repeat-read overlap; confirm ≥1 genuinely-held-out label;
  pool-excludes-profile is the invariant). Lesson + teacher-notes carry no disjointness claim (verified). Exercises
  static checks (hygiene/cell-lint/stretch/concept-scan) re-pass.
- `[FIXED]` **baseline.yaml** — added the two genuine Phase-B reranker-API idioms the notebooks call
  (`assemble_training_matrix`, `set_model`); all other candidate idioms rewritten to baseline-safe alternatives
  (pandas data-load, public API). concept-scan PASS book-wide.

<!-- appended pre-PR -->

## Post-Execution Report

**Status:** COMPLETE — plan gate CONSENSUS (3 rounds), content gate CONSENSUS (3 rounds incl. a user-approved reframe);
`ci-local.sh` ALL GREEN on the final code (see below); ready to merge.

**What shipped (Unit 11 — neural reranking):**
- **Registry (Phase A):** `neural-reranking`, `ranking-features`, `learning-to-rank`; coverage entry; manifest; syllabus
  row 11; whole-book lessons 30.5 → 33.5 ∈ [30, 60]. Baseline gains the MLP idioms + `assemble_training_matrix`/`set_model`.
- **`bookrec` (Phase B):** `rerank.py` — `NeuralRerankerPath` (`reranker` v1) + authoritative `rerank()` ordering key +
  `RerankerModel` (torch lazy in `fit`, numpy serve/load/artifact). 17-dim features from the PRE-blend per-path lists
  (6 calibrated scores + 6 presence flags + n_paths + 4 content). Leakage-safe time-ordered 75/25 holdout inside train:
  feature-paths refit + training popularity from the label-item-excluded `profile_rows` (via a `path_factory`),
  genre/author history from the profile item set; serving uses full-fit paths + full train. `test_unit11.py` (10 tests
  incl. two leak negatives + val/test invariance); `test_unit07` torch+faiss isolation extended.
- **Notebooks (C/D/E) + teacher-notes (F):** lesson (project-first; leak #1 → holdout fix → leak #2 → tie → content
  lift), exercises (8: 6 core + 2 Challenge), solutions, milestone (cleared).

**Measured (seed 0, pool 50, val):** all-feature reranker **0.346 / cov 0.195** — **~ties** the 6-way score-order
(0.348) and ~matches the two-tower (0.340); content-only **0.380** (the genuine lift); linear 0.364 ≈ MLP; scores-only
0.346; leaky (naive same-train) **0.288**; pool recall ceiling 0.772 @50 / 0.716 @30; coverage below the U6 blend (0.333).

**Thesis corrections (all caught by the gates before ship):**
1. Plan probe: the naive training recipe LEAKS by path memorization and tanks (0.288) → time-ordered holdout.
2. Plan review: per-path features aren't in `blend.py`'s `Candidate` (extract pre-blend); training-time content stats
   must use the 75% profile.
3. Content review ([sol]): a **second, cross-reader leak** — repeat-read held-out (label-period) reads were counted into
   the GLOBAL `log_pop`, inflating books that are other readers' held-out positives. Fixing it removed a **+0.018
   phantom** (0.364 → 0.346), so the all-feature reranker no longer beats the fixed order. **User-approved reframe:**
   the unit now teaches that a leakage-safe learned reranker ~ties a careful fixed blend, the lift is content features
   (all-feature dilutes; linear ≈ MLP), and naive reranking leaks in two distinct ways.
4. Self-caught: Ex3 originally claimed profile/label sets are disjoint (false for ~1/3 of readers) → the real invariant
   (pool excludes profile); ruff FURB192 in the milestone; plan's 18→17 feature off-by-one.

**Gates:** plan — [self]/[sol] APPROVE, [fable] APPROVE WITH NITS. Content — [self] APPROVE, [fable] APPROVE WITH
NITS (r2), [sol] APPROVE WITH NITS (r3); all `[OPEN]` resolved.

**Verification:** `TMPDIR=/dev/shm bash scripts/ci-local.sh` on the final code commit — ALL GREEN (unit tests,
notebook exec + hygiene, curriculum, PDF, `pre-merge-guard: OK`). Later commits are prose/markdown only (no
executable change).

**Follow-ups:** none blocking. `docs/content-review-gate.md:11` still names `gpt-6-sol` (gates ran on `gpt-5.6-sol`);
reconcile pending user OK. Next: U12 SASRec (recsys-014).
