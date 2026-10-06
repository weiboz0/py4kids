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

## Determinism & budget (binding)
- **ANN is approximate — the gate is NOT identical neighbour ids.** Gate on **recall@k of ANN vs exact brute force**
  (unique-id overlap of ANN top-k with exact top-k, `≥` a measured threshold) and **determinism** = two seeded,
  single-thread (`faiss.omp_set_num_threads(1)`) index builds give the **same** approximate neighbours (rank overlap
  + `allclose` on the returned distances, design §184 — never exact-float, and never the brute-force identity).
- **Latency:** measure exact-vs-ANN query time and REPORT it; do NOT hard-assert a speedup at 2,000 items (brute force
  over 2k×32 is already sub-millisecond — the ANN win is asymptotic). Phase B measures both and the lesson frames the
  speed story honestly (recall preserved here; speed is the *scaling* argument, optionally shown on a larger synthetic
  index built from the committed item matrix). Each cell far under the 120 s/cell cap; the two-tower fit it reuses is
  ~13–15 s (U8), so ≤2 torch fits per notebook.
- Everything CPU-deterministic; routed `--group recsys`; `faiss-cpu` already in the dep group (recsys-001).

## Why this works on the data (to MEASURE in Phase B — pre-declared, honest)
Two empirical questions the gate reviewers must see measured on the shipped code (no claim is pre-bound to an
unmeasured number):
1. **ANN recall:** does FAISS HNSW over the 2,000 two-tower item vectors (dim 32) recover the exact top-10 at high
   recall for a reasonable `efSearch`? Expect recall@10 → ~1.0 as `efSearch` grows (the honest knob story: low
   `efSearch` trades recall for speed). The gate: ANN recall@10 vs exact `≥ 0.9` at the pinned `efSearch`, and the
   ANN path's hit@10 within a small tolerance of the exact two-tower's 0.340 (ANN ≈ exact on accuracy; it is a
   *speed* technique, not an accuracy technique).
2. **Hybrid value:** does fusing BM25 (U3, 0.158) + two-tower (U8, 0.340) beat either single on hit@10, or does it
   help **coverage**/robustness instead? Do NOT assume hybrid wins hit@10 (dense dominates here). Pre-declare the
   honest outcome space: hybrid is reported on hit@10 AND coverage; if it does not beat the two-tower on hit@10, the
   lesson frames it as a **coverage/robustness** tool (sparse reaches lexically-matching items the dense tower ranks
   low) and names the measured fusion weight. The milestone compares hybrid against the U6 blend.

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
  removed, total 30.5 = "thirty and a half" meets the 30 minimum). `baseline.yaml`: declare any new `x.name(...)`
  methods the authored cells use (e.g. `faiss` constructors/methods — `IndexHNSWFlat`, `add`, `search`,
  `omp_set_num_threads`; `AnnRetrievalPath`/`HybridRetrievalPath`; any numpy idioms not yet listed).
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
  - `HnswIndex` — a thin FAISS HNSW wrapper over a dense item matrix: build (`faiss.omp_set_num_threads(1)`,
    deterministic, pinned `M`/`efConstruction`), `search(query_vectors, k, efSearch)` → approximate top-k item ids +
    distances. Import `faiss` **lazily inside the build/search methods** (like torch in `two_tower.py`) so the
    group-free suite never imports faiss; `artifact`/`load` persist the index deterministically (or the item matrix +
    pinned params so load rebuilds identically single-threaded).
  - `AnnRetrievalPath(BaseRetrievalPath)` (name `"ann"`, version `"1"`) wrapping a dense source via the CONSTRUCTOR
    (`AnnRetrievalPath(dense_path, efSearch=..., ...)` — like U9's feature-constructor pattern): `fit` builds the HNSW
    index over the dense source's item matrix; `retrieve` queries by the reader vector, excludes `seen`; unknown
    reader → `[]`. EXACT protocol signature. An **exact-brute-force reference** (numpy argsort over the same item
    matrix) is provided for the recall/latency comparison (it is just the dense source's own `retrieve`).
- `bookrec/hybrid.py`: `HybridRetrievalPath(sparse_path, dense_path, weight=..., method="weighted"|"rrf")` — fuse
  BM25 (U3) + two-tower (U8) candidate scores by min-max-normalised weighted sum or reciprocal-rank fusion over the
  union of each path's top-pool; EXACT protocol; empty/unknown contracts; deterministic.
- Tests (routed, new `tests/test_unit10.py`): **ANN recall@10 vs exact `≥ 0.9`** at the pinned `efSearch`; ANN hit@10
  within tolerance of the exact two-tower's ~0.340 (ANN is a speed technique, not accuracy); **determinism** — two
  seeded single-thread builds give the same approximate neighbours (rank overlap + `allclose` distances; no
  exact-float gate); recall RISES with `efSearch` (the knob); **hybrid** hit@10 + coverage recorded vs BM25-alone and
  two-tower-alone (directional asserts only — do NOT assert hybrid > two-tower on hit@10 unless measured); empty-seen /
  unknown-reader contracts; fit→artifact→load identical; both register (`ann-v1`, `hybrid-v1`). **EXTEND the
  import-blocked subprocess test** (`tests/test_unit07.py`) so the group-free path imports neither torch NOR faiss.
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/ -q` green + group-free suite imports no torch/faiss;
**report ANN recall@10 (vs exact) at a small `efSearch` sweep, ANN vs exact hit@10 + query latency, and hybrid hit@10 +
coverage vs the two singles + the fusion weight** so the lesson is data-bound.

### Phase C — lesson.ipynb (Opus subagent; project-first)
Hook: "our two-tower scores all 2,000 books for every reader — fine here, hopeless at a million. Can we retrieve the
same books without looking at all of them?" From scratch → reveal: (1) the exact brute-force baseline (numpy argsort
over the item scores — what every dense path already does) and why it is linear in the catalog; (2) **HNSW** — a
navigable graph that visits a few neighbours instead of all items; build it with FAISS single-threaded; the
`efSearch` recall/speed knob; (3) **ANN recall vs exact** — measure recall@10 and show hit@10 ≈ the exact two-tower
(ANN preserves accuracy at adequate `efSearch`); latency framed honestly (the speed win is asymptotic; optionally a
larger synthetic index); (4) **hybrid** — fuse BM25 + the two-tower and read hit@10 AND coverage honestly (the
measured Phase-B story). Bridge: U11 reranks the retrieved pool; U12 adds sequence models. ASCII only; reuse
`bookrec`; tiny/seeded/in-budget.
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
two-tower vectors; recall@10-vs-exact + latency table; register `AnnRetrievalPath` + `HybridRetrievalPath`; val
scoreboard (ANN ≈ exact two-tower; hybrid hit@10 + coverage vs BM25 / two-tower / the U6 blend). Passes
`milestone-check` + `exec-solutions` + `concept-scan`; ≤ budget; no `split="test"`.

### Phase F — teacher-notes.md (inline)
`## Goals`, `## Pacing` (60–90 min / 2–3 sittings, hook first, all exercises), `## Common mistakes` (expecting ANN to
*improve* accuracy — it preserves it; expecting a speedup at 2,000 items — the win is asymptotic; non-determinism from
multi-thread HNSW builds; expecting hybrid to always beat dense — it may help coverage not hit@10; leaking val),
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

<!-- appended after the 3-way plan-review gate -->

## Content Review

<!-- appended pre-PR -->

## Post-Execution Report

<!-- appended before ship -->
