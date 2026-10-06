# Plan recsys-012 — Unit 10: Approximate nearest neighbours (ANN) and hybrid retrieval

**Design:** `docs/designs/011-recsys-book.md` (§7 libraries/determinism/ceilings — ANN verified by **recall@k +
latency**, never exact neighbour identity; `faiss.omp_set_num_threads(1)`; "the reveal is an exact brute-force numpy
baseline → library, compared on recall-vs-speed"; §8 row 10). **Book:** `recsys` (Book 3). **Autopilot** per AGENTS.md.
Fourth Part-2 unit. Shared **retrieval infrastructure**: every dense path so far (U7 semantic, U8 two-tower, U9 feature
tower) retrieves by scoring *all* 2,000 items by brute force. This unit teaches the **exact brute-force baseline vs an
approximate index** (FAISS **HNSW**) — the **recall/speed trade** — and a **hybrid** path that fuses the sparse
lexical scores (U3 BM25) with the dense embedding scores (U8 two-tower). No new model; no generator change.

## Scope
**Unit 10** (`recsys/units/unit-10-ann-and-hybrid/`). Teaches: (1) **ANN retrieval** — exact top-k (numpy argsort over
the full score vector, what every dense path already does) vs an **approximate** index; the recall-vs-speed trade
(ANN trades a little recall for sublinear query time at scale); (2) **HNSW** — the Hierarchical Navigable Small World
graph index (FAISS-cpu), its `efConstruction`/`efSearch` knobs, deterministic single-thread build; (3)
**hybrid retrieval** — fusing sparse (BM25, U3) + dense (two-tower, U8) candidate scores (score-normalised weighted
sum and reciprocal-rank fusion), and when fusion helps. Ships `bookrec/ann.py` (an `HnswIndex` wrapper + an
`AnnRetrievalPath` that approximates an existing dense path) and `bookrec/hybrid.py` (`HybridRetrievalPath`), plus a
Unit-10 milestone. **This plan REMOVES `buildout`** (whole-book lessons 27.5 → 30.5 ≥ 30). No learned reranker (U11);
no sequence model (U12); no generator change.

## Determinism & budget (binding — numbers from the [fable] probe, Phase B re-confirms)
- **ANN is approximate — the gate is NOT identical neighbour ids.** Gate on **recall@10 of ANN vs exact brute force
  `≥ 0.98`** (measured 0.9991 at the pinned `M=32 / efConstruction=200 / efSearch=64`; the loose `≥0.9` floor
  doesn't bite — 0.98 does) and **determinism** = two seeded, single-thread index builds give the **same** approximate
  neighbours (rank overlap + `allclose` on returned distances, design §184 — never exact-float, never the brute-force
  identity). **Score geometry:** the index is **`IndexHNSWFlat(d, M, faiss.METRIC_INNER_PRODUCT)`** so it ranks the
  SAME `reader·item` dot product U8's exact comparator uses (default L2 would rank differently → recall meaningless).
- **Latency bound (design §7 requires recall@k + latency):** gate a **generous ABSOLUTE ceiling**, not a 2k-item
  speedup — e.g. ANN batched query over the ~540-reader cohort **< 1 s** (measured 18 ms; per-query ~34 µs). At 2,000
  items there is **no meaningful speedup** (exact numpy argpartition ~27 µs ≈ HNSW ~34 µs) — the plan must NOT assert
  one; the speed win is **asymptotic** (measured: 20k items → 90× faster, recall 0.993, build 2.5 s). The scaling demo
  uses **20k** (not 200k: 49 s build threatens the CI budget).
- `faiss.omp_set_num_threads(1)` is process-global like `torch.set_num_threads` → **save/restore in a `finally`**
  (`faiss.omp_get_max_threads()`), mirroring `two_tower.fit`.
- Budget: the two-tower fit it reuses is ~13–15 s (U8) → ≤2 torch fits per notebook; HNSW build at 2k ~0.16 s, 20k
  ~2.5 s. Each cell far under 120 s. Everything CPU-deterministic; routed `--group recsys`; `faiss-cpu` in the dep
  group (recsys-001).

## Why this works on the data (MEASURED — [fable] probe; Phase B re-confirms on shipped code)
**ANN (the speed technique that preserves accuracy):** FAISS HNSW over the 2,000 two-tower item vectors (dim 32,
`METRIC_INNER_PRODUCT`) recovers the exact top-10 at high recall, and its hit@10 is identical to the exact two-tower:

| efSearch (M=32, efC=200) | 8 | 16 | 32 | 64 | 128 |
|---|---|---|---|---|---|
| recall@10 vs exact | 0.981 | 0.996 | 0.998 | **0.9991** | 1.000 |

ANN path **hit@10 = 0.340 at every efSearch ≥ 16 — identical to the exact two-tower (Δ +0.000).** ANN is a *speed*
technique, not an accuracy one. At 2,000 items there is **no speedup** (numpy argpartition ~27 µs ≈ HNSW ~34 µs); the
win is **asymptotic** — 20k items → recall 0.993 at **90×** (build 2.5 s), 200k → recall 0.912 (build 49 s, CI-unsafe).
Teaching point: at fixed `efSearch`, recall *falls* as the catalog grows (1.000 @2k → 0.912 @200k) — the knob must
scale with the catalog. Determinism: two single-thread builds give identical neighbour ids + `allclose` distances.

**Hybrid (dense dominates; a small, weight-sensitive lift — NOT a free win):** fusing BM25 (U3, 0.158/cov 0.278) +
two-tower (U8, 0.340/cov 0.177) by min-max-normalised weighted sum over the union of their top pools. Measured
(hit@10 / coverage, 500 val readers):

| fusion | hit@10 | coverage |
|---|---|---|
| two-tower alone | 0.340 | 0.177 |
| hybrid **pool 50, w_dense 0.7 (PINNED)** | **0.362** | 0.192 |
| hybrid pool 100, w_dense 0.6 | 0.366 | 0.201 |
| hybrid equal weights (w 0.5) | 0.296–0.328 | — |
| reciprocal-rank fusion (RRF) | 0.310–0.330 | ≤0.241 |
| U6 4-way blend (recorded) | 0.306 | 0.333 |

The honest story: **dense dominates; a dense-heavy hybrid gives a small lift on BOTH hit@10 (0.362, stable 0.362/
0.362/0.362 across two-tower seeds 0/1/2) and coverage (0.192 > 0.177)** — but the gain is **small and not
statistically secure** (paired bootstrap 95% CI touches 0 every seed), **weight-sensitive** (equal weights HURT; RRF
loses to the two-tower alone), and coverage stays well below lexical-alone (0.278) and the U6 blend (0.333). So the
lesson frames hybrid as "sparse recovers a few lexically-matched items the dense tower ranks low — a *modest,
tuning-dependent* complement, not a new best." **Gate (directional, measured-safe):** `hybrid(pool=50,w=0.7).hit ≥
two_tower.hit − 0.01` AND `hybrid.coverage > two_tower.coverage` — NOT a strict `hybrid > two-tower`. The milestone
contrasts hybrid vs the U6 blend on BOTH axes (hybrid wins hit 0.362>0.306, loses coverage 0.192<0.333).

## Buildout — REMOVED by this plan
Whole-book `lessons` total becomes **30.5** (U1–U10 at 3 each = 30 + Checkpoint A 0.5) ≥ 30 = the `recsys`
lesson-budget minimum (`books.yaml lesson_budget: [30, 60]`). **Phase A removes `buildout: true` from the `recsys`
entry in `books.yaml`** and updates the coverage-map header comment. Removing buildout re-enables two full checks
(`tools/curriculum.py`): the **lesson-budget minimum** (30.5 ≥ 30 ✓) and **introduction completeness** (every concept
in `concepts.yaml` must be introduced by a coverage entry — holds: `concepts.yaml` lists only U1–U10 concepts, each
introduced by its unit's entry). Phase A/G verify both pass with the flag off.

## Audience & retained laws
Advanced baseline (design 011). Retained in full: project-first; taught-before-assessed (ann-retrieval/hnsw/
hybrid-retrieval introduced + practiced here); student notebooks NO solutions/outputs; solutions + milestone run clean
(fixed seeds, deterministic torch + `faiss.omp_set_num_threads(1)`); teacher-notes; from-scratch→reveal (exact
brute-force numpy baseline → FAISS); a stretch exercise. CPU-deterministic; routed `--group recsys`; within budget.

## Concepts introduced (3) — `concepts.yaml`
- `ann-retrieval` — approximate nearest-neighbour retrieval: exact brute force vs approximate; the recall/speed trade.
  `kind: technique`, `category: techniques`.
- `hnsw` — the Hierarchical Navigable Small World graph index (FAISS/HNSW) and its `efConstruction`/`efSearch` knobs.
  `kind: technique`, `category: techniques`.
- `hybrid-retrieval` — fusing sparse (BM25) + dense (embedding) candidate scores (normalised weighted sum / RRF).
  `kind: technique`, `category: techniques`.
All three globally unique (confirmed 0 hits across `*/curriculum/concepts.yaml`; re-confirm in Phase A).

### Coverage-map entry
`unit-10-ann-and-hybrid`, `kind: unit`, `title: "Approximate nearest neighbours and hybrid retrieval"`, `lessons: 3`,
`introduces: [ann-retrieval, hnsw, hybrid-retrieval]`,
`requires: [retrieve-then-rank, offline-evaluation, top-k-ranking-metrics, beyond-accuracy, embedding-retrieval,
two-tower, bm25, score-blending]`,
`practices: [retrieve-then-rank, offline-evaluation, top-k-ranking-metrics, beyond-accuracy, embedding-retrieval,
two-tower, bm25, score-blending]`.
(All required ids introduced by U1/U3/U6/U7/U8. `embedding-retrieval` (U7) + `two-tower` (U8) = the dense source ANN
indexes; `bm25` (U3) = the sparse half of the hybrid; `score-blending` (U6) = the fusion precedent; `beyond-accuracy`
(U6) = the coverage lens for the hybrid readout. `practices ∩ introduces = ∅`; no `project` entry → capstone rule
inert.)

## Phases

### Phase A — registry + syllabus + buildout removal
- `concepts.yaml`: add the 3 ids. `coverage-map.yaml`: add the Unit-10 entry; update the header comment (buildout
  removed, total 30.5 = "thirty and a half" meets the 30 minimum). `baseline.yaml`: declare the new `x.name(...)`
  idioms the authored cells use — faiss `IndexHNSWFlat`, `add`, `search`, `omp_set_num_threads`, `omp_get_max_threads`,
  the `hnsw.efSearch`/`hnsw.efConstruction` attribute access on the index, `AnnRetrievalPath`/`HybridRetrievalPath`,
  and any numpy idiom (`argpartition`?) not yet listed. Add ONLY what the cells actually use (trim unused at Phase G
  concept-scan, as in recsys-011).
- **`books.yaml`: remove `buildout: true` from the `recsys` entry.**
- `unit-10-ann-and-hybrid/manifest.yaml`; `syllabus.md` arc row `| 10 | \`unit-10-ann-and-hybrid\` | unit | 3 |
  <hook> |` after the U9 row; rebuild PDF.
**Verify:** manifest/prereq/coverage/syllabus green **with buildout OFF** (lesson-budget 30.5 ∈ [30,60];
introduction completeness holds); concepts unique.

### Phase B — `bookrec` ANN + hybrid (Opus subagent; FAISS-cpu, CPU-deterministic)
Dispatch an **Opus subagent**. STUDY `two_tower.py` (the dense source — reader+item numpy matrices in one space;
torch-free `retrieve`), `embeddings.py`/`feature_tower.py` (other dense sources), `lexical.py`/`BM25Index` (the sparse
half), `protocol.py` (`fit`/`retrieve`/`artifact`/`load`), `scoreboard.py`, `blend.py` (the U6 fusion precedent).
- `bookrec/ann.py`:
  - `HnswIndex` — a thin FAISS HNSW wrapper over a dense item matrix: build
    **`faiss.IndexHNSWFlat(d, M=32, faiss.METRIC_INNER_PRODUCT)`** (inner product so it ranks the SAME `reader·item`
    dot product U8 uses — NOT default L2), `efConstruction=200`; `faiss.omp_set_num_threads(1)` **saved/restored in a
    `finally`** (`faiss.omp_get_max_threads()`, mirroring `two_tower.fit`); `search(query, k, efSearch=64)` sets
    `index.hnsw.efSearch` then searches → approximate top-k ids + scores. Import `faiss` **lazily inside build/search/
    load** (like torch in `two_tower.py`) so the group-free suite never imports faiss; `artifact`/`load` persist the
    item matrix + pinned params so `load` rebuilds identically single-threaded (torch/faiss-free on the path's numpy
    retrieve surface).
  - `AnnRetrievalPath(BaseRetrievalPath)` (name `"ann"`, version `"1"`) wrapping a dense source via the CONSTRUCTOR
    (`AnnRetrievalPath(dense_path, efSearch=64, ...)` — like U9's feature-constructor pattern): `fit` builds the HNSW
    index over the dense source's item matrix; `retrieve` queries by the reader vector and **over-fetches
    `min(n_items, k + len(seen))`** from the index BEFORE excluding `seen` (else parity with exact breaks for heavy
    readers); unknown reader → `[]`. EXACT protocol signature. The **exact-brute-force reference** is just the dense
    source's own numpy `retrieve` (argsort/argpartition over the same item·reader scores) — used for recall/latency.
- `bookrec/hybrid.py`: `HybridRetrievalPath(sparse_path, dense_path, weight=0.7, pool=50, method="weighted"|"rrf")` —
  fuse BM25 (U3) + two-tower (U8) by **min-max-normalised weighted sum** (`w_dense=0.7`) over the union of each path's
  **top-`pool=50`** candidates (each path over-fetches its pool); `rrf` offered as the alternative. EXACT protocol;
  empty/unknown contracts; deterministic. Default pinned `pool=50, weight=0.7` (the probe's sweet spot).
- Tests (routed, new `tests/test_unit10.py`): **ANN recall@10 vs exact `≥ 0.98`** at pinned `M=32/efC=200/efSearch=64`
  (measured 0.9991; the 0.9 floor doesn't bite); **ANN hit@10 == exact two-tower within ±0.005** (measured Δ0.000 —
  ANN is a speed technique, not accuracy); **determinism** — two single-thread builds give the same neighbours (rank
  overlap + `allclose` distances; no exact-float gate); **recall endpoints** `recall(efSearch=8) ≤ recall(128)` (NOT
  strict per-step monotonicity — ties at ~1.0 are possible); **latency** — ANN batched query over the val cohort
  `< 1 s` (generous absolute ceiling, measured ~18 ms; NOT a 2k speedup); **hybrid** `hybrid(pool=50,w=0.7).hit ≥
  two_tower.hit − 0.01` AND `hybrid.coverage > two_tower.coverage` (directional, measured-safe — NOT strict
  `hybrid > two-tower`); equal-weights/RRF recorded as not-better; empty-seen/unknown contracts; fit→artifact→load
  identical; both register (`ann-v1`, `hybrid-v1`). **EXTEND the import-blocked subprocess test** (`tests/
  test_unit07.py`) to plant `sys.modules["faiss"]=None` alongside torch and assert the group-free path imports
  neither (`sys.modules.get("faiss") is None`).
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/ -q` green + group-free suite imports no torch/faiss;
**report ANN recall@10 vs exact across the efSearch sweep, ANN vs exact hit@10 + batched/ per-query latency, the 20k
scaling point (recall + speedup + build time), and hybrid hit@10 + coverage vs BM25/two-tower + the pinned weight** so
the lesson is data-bound.

### Phase C — lesson.ipynb (Opus subagent; project-first)
Hook: "our two-tower scores all 2,000 books for every reader — fine here, hopeless at a million. Can we retrieve the
same books without looking at all of them?" From scratch → reveal: (1) the exact brute-force baseline (numpy argsort
over the item scores — what every dense path already does) and why it is linear in the catalog; (2) **HNSW** — a
navigable graph that visits a few neighbours instead of all items; build it with FAISS single-threaded; the
`efSearch` recall/speed knob; (3) **ANN recall vs exact** — measure recall@10 (~0.999 at efSearch 64) and show hit@10
== the exact two-tower (0.340); latency framed honestly — **no speedup at 2k**, demonstrate the asymptotic win on a
**20k synthetic index** (jittered item-matrix copies: recall 0.993, ~90×, build ~2.5 s — NOT 200k, CI-unsafe), and
that recall falls with catalog size at fixed `efSearch`; (4) **hybrid** — fuse BM25 + the two-tower (pinned `pool=50,
w_dense=0.7`) and read hit@10 (0.362) AND coverage (0.192) honestly: a small, weight-sensitive lift on both (equal
weights hurt; RRF loses), coverage still below lexical/U6. Bridge: U11 reranks the retrieved pool; U12 adds sequence
models. ASCII only; reuse `bookrec`; tiny/seeded/in-budget.
**Verify:** `exec-lessons` clean (budget); non-empty markdown first cell; `concept-scan` clean.

### Phase D — exercises.ipynb + solutions.ipynb (separate fresh Opus subagents)
≥6 `## Exercise N`; ≥2 `stretch`; exercises NO solutions/outputs; solutions mirror all, clean (fixed seeds,
deterministic + `faiss.omp_set_num_threads(1)`), ≥3 non-vacuous asserts. Drill: build an HNSW index over the
two-tower item matrix; measure recall@10 vs exact and watch it rise with `efSearch`; confirm ANN hit@10 ≈ exact; build
and score a `HybridRetrievalPath` and read hit@10 + coverage vs the singles. Stretch e.g.: the `efSearch` recall/speed
curve; weighted-sum vs reciprocal-rank fusion; the fusion-weight sweep. Taught-before-assessed; seeded.
**Verify:** `hygiene`/`structure`/`cell-lint`/`noexec`; `exec-solutions` clean (budget); `concept-scan` clean.

### Phase E — milestone notebook (Opus subagent)
`recsys/projects/bookrec/milestones/unit-10-ann-and-hybrid.ipynb` — fixed-seed demo: build the HNSW index over the
two-tower vectors; recall@10-vs-exact + latency table (+ the 20k scaling point); register `AnnRetrievalPath` +
`HybridRetrievalPath` (pinned `pool=50, w_dense=0.7`); val scoreboard (ANN == exact two-tower 0.340; hybrid 0.362/cov
0.192 vs BM25 0.158 / two-tower 0.340 / the U6 blend 0.306/cov 0.333 — hybrid wins hit@10, loses coverage; frame
BOTH). Passes
`milestone-check` + `exec-solutions` + `concept-scan`; ≤ budget; no `split="test"`.

### Phase F — teacher-notes.md (inline)
`## Goals`, `## Pacing` (60–90 min / 2–3 sittings, hook first, all exercises), `## Common mistakes` (expecting ANN to
*improve* accuracy — it preserves it; expecting a speedup at 2,000 items — the win is asymptotic (20k → ~90×);
non-determinism from multi-thread HNSW builds; using default L2 when the scores are inner products; forgetting to
over-fetch past `seen`; **assuming any fusion / equal weights helps — equal weights HURT and RRF loses here; only a
tuned dense-heavy hybrid gives a small lift**; leaking val),
`## Discussion prompts` (why graph traversal beats scanning at scale; the `efSearch` recall/speed trade; when sparse
complements dense; the retrieve→rerank split ahead), `## Differentiation`.

### Phase G — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN with Units 1–10 + Checkpoint A + the Unit-10 milestone AND
`bash scripts/pre-merge-guard.sh --pr` OK. **`buildout` is OFF** — confirm lesson-budget (30.5 ∈ [30,60]) and
introduction-completeness both pass. Confirm CPU-determinism, the group-free path imports neither torch nor faiss, and
the ANN/hybrid exec stays within the whole-book CI budget.

## Out of scope
No learned reranker (U11); no sequence/SASRec model (U12); no generator change; no new embedding model (ANN indexes
the EXISTING U8 two-tower vectors); no `projects/project-*` entry (capstone = U14); no Checkpoint B (U13); no GPU; no
hnswlib (FAISS-cpu is the shipped index; hnswlib named-not-shipped at most).

## Verification phase declared
Phase G is this plan's named verification phase.

## Plan Review

### Round 1

**[self] — APPROVE.** Registry closes: `requires` ⊆ introductions of U1 (retrieve-then-rank/offline-evaluation/
top-k-ranking-metrics), U3 (bm25), U6 (beyond-accuracy/score-blending), U7 (embedding-retrieval), U8 (two-tower);
`practices ∩ introduces = ∅`; 3 new ids globally unique (0 hits). **Buildout removal verified safe:** `buildout` gates
exactly two `tools/curriculum.py` checks — lesson-budget minimum (30.5 ∈ recsys `[30,60]` ✓) and introduction
completeness (`concepts.yaml` lists only U1–U10 concepts, each introduced by its unit entry → `introduced == known`
with the flag off ✓). ANN verification paradigm matches design §7: gate on **recall@k-vs-exact + determinism**
(single-thread `faiss.omp_set_num_threads(1)`, rank-overlap + `allclose` distances, §184 tolerance), NOT exact
neighbour identity, NOT a hard small-scale speedup — the plan frames ANN as a *speed* technique that *preserves*
accuracy, and latency as asymptotic. faiss isolated lazily (mirrors U8's proven torch isolation; group-free suite
imports neither torch nor faiss; subprocess test extended). Hybrid is honestly conditional (measure hit@10 AND
coverage; do not assume it beats the two-tower). Named Phase G; project-first; ≥6/≥2-stretch; teacher-notes; milestone;
no scope creep (reranker=U11, SASRec=U12). Open for Phase B/gate (both [fable]-probed): the ANN recall@efSearch +
hit@10≈exact + latency numbers, and the hybrid hit@10/coverage/weight. No [self] blockers.

**[sol] — REJECT (round 1)** (closure/buildout-removal/faiss-isolation/hybrid-honesty/scope all confirmed correct):
1. `[OPEN]→[FIXED v2]` **Must** — latency bound missing (design §7 requires recall@k + latency). → v2 adds a generous
   ABSOLUTE ceiling (ANN batched query over the cohort < 1 s; measured ~18 ms), NOT a 2k speedup.
2. `[OPEN]→[FIXED v2]` **Must** — ANN scoring geometry unspecified: U8 ranks raw inner products, `IndexHNSWFlat`
   defaults to L2. → v2 pins **`faiss.METRIC_INNER_PRODUCT`** + consistent polarity + over-fetch past `seen`.
3. `[OPEN]→[FIXED v2]` **Should** — "recall RISES with efSearch" too strong (can plateau/tie). → v2 gates endpoints
   `recall(8) ≤ recall(128)` (non-strict), not per-step monotonicity; pinned recall gate tightened **0.9 → 0.98**.

**[fable] — APPROVE WITH NITS (round 1, full seeded probe; faiss-cpu 1.15.1).** Measured and folded:
- ANN recall@10 vs exact: 0.981/0.996/0.998/**0.9991**/1.000 at efSearch 8/16/32/64/128 (M=32,efC=200); ANN hit@10
  **0.340 == exact** (Δ0.000); deterministic single-thread; latency 2k ~34 µs ≈ exact (no speedup); 20k → 90×/recall
  0.993/build 2.5 s; 200k → recall 0.912/build 49 s (CI-unsafe).
- Hybrid: pool 50/w_dense 0.7 → **0.362/cov 0.192** (stable 0.362 across two-tower seeds 0/1/2); pool 100/w 0.6 →
  0.366/0.201; equal weights HURT (0.296–0.328); RRF loses (0.310–0.330); gain small + CI touches 0 + weight-sensitive;
  coverage < lexical 0.278 < U6 blend 0.333.
1. `[OPEN]→[FIXED v2]` **Must** — hybrid thesis: a tuned dense-heavy hybrid DOES edge the two-tower on hit@10 (0.362)
   and coverage, but small/insecure/weight-sensitive. → v2 Why-table + Phase B gate (`hit ≥ tt−0.01` ∧ `cov > tt`,
   not strict `>`) + Phase F ("assuming equal weights / any fusion helps").
2. `[OPEN]→[FIXED v2]` **Must** — ANN `retrieve` must over-fetch `k+len(seen)` before excluding `seen`; index must be
   `METRIC_INNER_PRODUCT`. → v2 Phase B (also applies to hybrid pools).
3–7. `[OPEN]→[FIXED v2]` **Should** — pin M=32/efC=200/efSearch=64 + gate ≥0.98 (#3); 20k not 200k scaling demo (#4);
   `faiss.omp` save/restore in `finally` (#5); pin hybrid `pool=50,w=0.7` + milestone-vs-U6 framing (#6); plant
   `sys.modules["faiss"]=None` in the import-blocked test (#7). **Nice** — baseline.yaml lists `hnsw.efSearch`/
   `efConstruction` attribute access + faiss methods (folded into Phase A).

### v2 changelog
Folded ALL of the above into: Determinism&budget (latency ceiling + metric + omp save/restore + 20k scaling + pinned
knobs), Why-this-works (full measured tables + honest hybrid reframe), Phase A (baseline idioms), Phase B (metric,
over-fetch, ≥0.98 recall gate, endpoint-not-monotonic, latency<1s gate, pinned hybrid, faiss import-block), Phase C
(20k scaling, honest hybrid), Phase E (hybrid vs U6 both-axes), Phase F (fusion mistakes).

**[self] — APPROVE (round 2).** v2 binds every gate to the [fable] measurements and resolves both [sol] Musts
(absolute latency ceiling; inner-product metric + over-fetch) and the [fable] Must (honest hybrid reframe). No
remaining blocker; dispatching [sol] round-2 re-review.

**[sol] — APPROVE (round 2).** All 3 findings resolved (absolute latency bound < 1 s separated from any 2k speedup;
FAISS inner-product metric matches U8's dot product + over-fetch before seen-removal; recall trend gated on non-strict
endpoints). Hybrid reframe appropriately cautious + directionally gated. No new blocker.

### Plan-review outcome (FINAL): **CONSENSUS — [self] APPROVE (r2) · [fable] APPROVE WITH NITS (all folded) · [sol] APPROVE (r2).**
Cleared for implementation (Phases A→G).

## Content Review

<!-- appended pre-PR -->

## Post-Execution Report

<!-- appended before ship -->
