# Teacher notes — Unit 11: Neural reranking

This unit finally *learns* the second stage of retrieve-then-rank. The paths from Units 2–10 each see
one slice of the signal (popularity, text, behaviour); a cheap retrieval step proposes a candidate
**pool**, and a small **PyTorch reranker** re-scores that pool from a per-candidate **feature vector**
(the paths' calibrated scores + content features) trained on implicit feedback. `rank.py` has
anticipated this since Unit 1 ("a learned reranker replaces the ordering key in a later unit").

The unit is built around three honest, measured results — and the first one is a **failure** that is
the best teaching moment in the book so far:

1. **The naive recipe LEAKS and tanks.** Train the reranker on a reader's train positives as labels,
   using paths fit on that *same* train, and it scores **~0.28 on val — below plain score-order and
   below the two-tower (0.340)**. The paths *memorized* those positives, so "high score ⇒ positive" is
   learned from inflated in-train scores that val candidates never show (distribution shift). The fix
   is a **time-ordered holdout inside train**.
2. **The clean reranker edges accuracy but loses coverage.** With the holdout it lands at
   **0.35–0.39** (edges the two-tower, ties the U10 hybrid 0.362) — but **coverage collapses to
   ~0.12–0.19** (vs the Unit-6 blend's 0.333). An honest win on accuracy, a real loss on coverage.
3. **The lift is from CONTENT features, not score-combining.** Ablation: content-only is the *best*
   reranker; dropping the path scores barely hurts; and **linear ≈ MLP** — the non-linear combiner adds
   nothing here. A learned ranker wins by seeing *features a single path can't* (content affinity to
   the reader's history), not by cleverly combining correlated scores.

## Goals

By the end of this unit students can:

- Explain the **two-stage retrieve-then-rank** split: cheap retrieval proposes a pool; an expensive
  learned model re-scores only that pool. Explain the **retrieval recall ceiling** — the reranker only
  re-orders the pool, so pool recall (~0.72 at pool 30, ~0.77 at pool 50) caps hit@k.
- Assemble a per-candidate **ranking-feature** vector: the pre-blend per-path calibrated scores (+
  presence flags) plus content features (genre/author affinity to the reader's history, log-popularity).
- Name and avoid the **leakage trap**: training labels must come from data the feature-producing paths
  and statistics did **not** see. Build the **time-ordered holdout inside train** (latest ~25% of a
  reader's train positives = labels; earlier 75% = the profile every training-time feature/path uses).
- Train a small reranker (PyTorch, pointwise logistic) and read the val scoreboard **honestly**:
  reranker vs two-tower vs the Unit-6 blend vs the Unit-10 hybrid, on hit@10 **and** coverage.
- Read the **feature ablation**: content features carry the lift; the path scores and the non-linearity
  do not — and explain why, given this data's feature-derived taste.

This unit introduces `neural-reranking`, `ranking-features`, and `learning-to-rank`; it re-exercises
U1's retrieve-then-rank / offline-evaluation / top-k metrics, U4's implicit feedback, U6's score
blending + beyond-accuracy coverage, U8's two-tower + neural training, and U10's hybrid.

## Pacing

The unit opens with its **project hook** — *each path sees one slice of the signal; what if a model
learned to rank a reader's candidate pool?* Plan **60–90 minutes across two to three sittings**; assign
all exercises. The reranker's MLP fit is under a second, but **feature assembly is the cost** (~15 s per
pass over the readers, and the clean recipe fits the paths twice) — so assemble the feature matrix once
and reuse it, keeping assembly and evaluation in separate cells.

1. **Sitting 1 (~30 min) — the two-stage split + features.** The pool and the recall ceiling; build the
   per-candidate feature vector; the score-order baseline `rank.py` already does.
2. **Sitting 2 (~35 min) — the leak and the fix.** Train the naive way and watch it tank to ~0.28; then
   the time-ordered holdout; train/register the reranker; read the honest scoreboard (accuracy up,
   coverage down).
3. **Sitting 3 (~20 min, + Challenges) — what carries the lift.** The feature ablation (content-only vs
   scores-only), linear vs MLP, and the pool-size/pairwise knobs.

## Common mistakes

- **The leakage trap (the headline — measured).** Training the reranker on a reader's train positives
  while the feature-producing paths and content statistics are built from that *same* train makes the
  features memorize the labels; val **tanks to ~0.28**, below score-order. Every training-time
  feature/statistic (path scores, genre/author history, popularity counts) must use only the **75%
  profile**; the held-out 25% supplies labels only. Full-train history is serving-only.
- **Expecting the win to come from combining path scores.** It doesn't — content-only is the best
  reranker, and linear ≈ MLP. The lift is content affinity the single paths' calibrated scores don't
  carry across readers.
- **Reporting the accuracy win while hiding the coverage loss.** The reranker edges hit@10 but drops
  coverage to ~0.12–0.19 (vs 0.333). Report both; it is a real trade.
- **Forgetting the recall ceiling.** The reranker only re-orders the pool — if retrieval didn't propose
  a relevant item, no reranker can surface it. Pool recall (~0.72–0.77) caps hit@k; that is why pool
  size and retrieval quality still matter.
- **Non-determinism.** Seed the trio and single-thread; two seeded fits give identical top-k ranking.
- **Leaking the holdout.** Train on `train` (the 75% profile); the scoreboard is `val`; `test` stays
  sealed for Checkpoint B.

## Discussion prompts

- Why does a two-stage retrieve-then-rank system exist at all — what does the expensive reranker buy
  over just ranking by one path's score, and what caps how much it can buy (the recall ceiling)?
- The naive recipe leaked because the features had already seen the labels. State the general rule for
  building training features in a stacked/second-stage model, and why the time-ordered holdout enforces
  it here.
- Content-only beat the score features, and linear tied the MLP. What does that tell you about where
  this data's taste signal lives, and when would a non-linear combiner of path scores actually help?
- The reranker trades coverage for accuracy. For a real bookstore, when is that trade worth it, and how
  would you claw coverage back (tie to the Unit-6 blend and Unit-13's beyond-accuracy thread)?

## Provenance

Original content. **Learning to rank** and **two-stage retrieve-then-rank** are standard IR/recsys
practice (pointwise/pairwise/listwise; Liu, *Learning to Rank for IR*, 2009) — worth a one-line framing
for an advanced audience, no single source. The **feature-leakage / train-test contamination** failure
mode in stacked models is a well-known practitioner pitfall; here it is measured on the course's own
data.

## Differentiation

- **Support:** give the feature-assembly helper and the time-ordered split as starter snippets so the
  lesson stays on the *ideas* (two-stage ranking, the leak, what carries the lift); pair-program the
  naive-vs-clean comparison.
- **Core:** assemble features, run the naive recipe and see it tank, apply the holdout fix, train/register
  the reranker, and read the honest scoreboard (hit@10 **and** coverage) + the feature ablation.
- **Stretch:** the linear-logistic → MLP ladder (show non-linearity adds nothing here); pointwise vs
  pairwise/BPR; the pool-size knob and its effect on the recall ceiling; add/drop a feature family and
  measure. Ask strong students to predict the ablation result before running it, and to explain why the
  naive recipe's val score is *below* a fixed score-order of the same pool.
