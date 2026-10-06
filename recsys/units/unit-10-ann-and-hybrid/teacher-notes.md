# Teacher notes — Unit 10: Approximate nearest neighbours and hybrid retrieval

Every dense path the course has built — U7 semantic, U8 two-tower, U9 feature tower — retrieves the
same way: score *all* 2,000 books for a reader and sort. That is fine at this scale and hopeless at a
million. This unit is about the **retrieval infrastructure**, not a new model: an **exact brute-force
baseline** vs an **approximate** index (**FAISS HNSW**), the **recall/speed trade**, and a **hybrid**
path that fuses the sparse lexical scores (U3 BM25) with the dense two-tower scores. Two honest
headlines the unit is built around: **ANN preserves accuracy** (it is a speed technique, not an
accuracy one), and **hybrid gives only a small, tuning-dependent lift** (dense dominates; naive fusion
can hurt).

## Goals

By the end of this unit students can:

- Explain the **exact brute-force baseline**: the two-tower (and every dense path) scores every item by
  the `reader · item` dot product and sorts — O(catalog) per query.
- Build an **HNSW** index (FAISS) over the two-tower item vectors, ranking the **same inner product**
  (`METRIC_INNER_PRODUCT` — not the default L2), and explain the `efSearch` recall/speed knob.
- Measure **recall@10 of ANN vs exact** and read it honestly: ≈0.999 at `efSearch=64`, and the ANN
  path's **hit@10 is identical to the exact two-tower (0.340)** — ANN recovers the same recommendations,
  it does not change them.
- Reason about **speed**: at 2,000 items there is **no speedup** (brute force is already microseconds);
  the win is **asymptotic** — a 20k synthetic index is ~10× faster at recall 0.993 — and at fixed
  `efSearch`, recall *falls* as the catalog grows, so the knob must scale with the catalog.
- Build a **hybrid** path (min-max-normalised weighted sum of BM25 + two-tower over the union of their
  top pools) and read hit@10 AND coverage honestly: the tuned `pool=50, w_dense=0.7` hybrid edges the
  two-tower (0.362 vs 0.340) and lifts coverage a little (0.192 vs 0.177), but the gain is small and
  weight-sensitive — equal weights *hurt* and reciprocal-rank fusion loses here.

This unit introduces `ann-retrieval`, `hnsw`, and `hybrid-retrieval`; it re-exercises U1's
retrieve-then-rank / offline-evaluation / top-k metrics, U3's BM25, U6's beyond-accuracy coverage and
score-blending, U7's embedding retrieval, and U8's two-tower.

## Pacing

The unit opens with its **project hook** — *our two-tower scores all 2,000 books for every reader; fine
here, hopeless at a million — can we retrieve the same books without looking at all of them?* Plan
**60–90 minutes across two to three sittings**; assign all exercises. The two-tower fit it reuses is
~13–15 s; HNSW build at 2k is ~0.16 s and at 20k ~2.5 s, so sittings stay well within budget.

1. **Sitting 1 (~30 min) — exact vs approximate.** The brute-force baseline and why it is linear in the
   catalog; build the HNSW index single-threaded; the `efSearch` knob.
2. **Sitting 2 (~35 min) — recall, accuracy, speed.** Measure recall@10 vs exact across an `efSearch`
   sweep; confirm ANN hit@10 == exact; the latency story (no 2k speedup; the 20k scaling demo).
3. **Sitting 3 (~20 min, + Challenges) — hybrid.** Fuse BM25 + two-tower; read hit@10 AND coverage;
   the weight sweep and why equal weights / RRF do not help.

## Common mistakes

- **Expecting ANN to *improve* accuracy.** It does not — it recovers (approximately) the same top-k the
  exact search would. hit@10 is identical to the exact two-tower (0.340). ANN buys *speed at scale*,
  not better recommendations. Grading that rewards a higher hit@10 from "adding ANN" misreads the unit.
- **Expecting a speedup at 2,000 items.** Brute force over 2k×32 is already microseconds; HNSW is no
  faster here. The win is **asymptotic** — show it on the 20k synthetic index (~10×). Do not assert a
  small-catalog speedup.
- **Using the default L2 metric.** FAISS `IndexHNSWFlat` defaults to L2, but the two-tower ranks by
  inner product; a mismatched metric makes recall meaningless. Use `METRIC_INNER_PRODUCT`.
- **Forgetting to over-fetch past `seen`.** The index must return `k + len(seen)` neighbours *before*
  excluding the reader's already-seen items, or heavy readers lose recommendations relative to exact.
- **Non-determinism from multi-threaded HNSW builds.** HNSW construction is thread-order dependent;
  `faiss.omp_set_num_threads(1)` (saved/restored) makes two builds identical.
- **Assuming any fusion helps / equal weights are safe.** They are not: equal weights (`w=0.5`) *hurt*
  (hit drops to ~0.30) and reciprocal-rank fusion loses to the two-tower alone. Only a tuned, dense-heavy
  weight (`w_dense≈0.7`) gives the small lift — and even then the gain is not statistically secure.
- **Leaking the holdout.** Train/index on `train`; the scoreboard is `val`; `test` stays sealed.

## Discussion prompts

- Why does a navigable graph visit only a handful of nodes to find good neighbours, while brute force
  must touch every item? What does `efSearch` control, and why does it trade recall for speed?
- ANN recovers the same top-k the exact search would. So what, exactly, has it bought us — and at what
  catalog size does that matter? (Tie to the 20k scaling demo and the recall-falls-with-size point.)
- The hybrid's best weight is dense-heavy (0.7) and the gain is small. When *would* sparse matter more —
  what kind of reader or query would BM25 rescue that the dense tower buries?
- Equal weights and RRF both failed here. What does that tell you about fusing two score distributions
  on very different scales, and why does min-max normalisation plus a tuned weight help?
- Retrieval is only the first stage. What would a second-stage **reranker** (U11) add on top of the
  pool the ANN index returns?

## Provenance

Original content. **HNSW** is Malkov & Yashunin, *Efficient and robust approximate nearest neighbor
search using Hierarchical Navigable Small World graphs* (2016) — worth a one-line attribution for an
advanced audience; **FAISS** is the standard library (Johnson, Douze & Jégou). **Hybrid sparse+dense
retrieval** and **reciprocal-rank fusion** (Cormack et al., 2009) are standard IR practice, no single
source.

## Differentiation

- **Support:** give the `HnswIndex` build + search call and the exact-vs-ANN recall helper as starter
  snippets so the lesson stays on the *ideas* (graph traversal, the recall/speed knob, why ANN preserves
  accuracy); pair-program the recall measurement.
- **Core:** build the index, measure recall@10 vs exact across an `efSearch` sweep, confirm ANN hit@10
  == exact, and build + score a `HybridRetrievalPath`.
- **Stretch:** the full `efSearch` recall/speed curve (and the 20k scaling point); weighted-sum vs
  reciprocal-rank fusion; the fusion-weight sweep (find where dense-heavy fusion helps and where equal
  weights hurt). Ask strong students to predict the recall curve's shape and the best fusion weight
  before running them, and to explain why recall falls as the catalog grows at fixed `efSearch`.
