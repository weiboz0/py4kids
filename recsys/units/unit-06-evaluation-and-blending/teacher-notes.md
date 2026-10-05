# Teacher notes — Unit 6: Evaluation deepened and the first blend (end of Part 1)

## Goals

By the end of this unit students can:

- Measure a recommender with **ranking metrics** beyond hit-rate/recall: **precision@k** and **NDCG@k** (gain
  discounted by log rank), and explain why a *ranking* metric — not ratings RMSE — is the right target for implicit
  top-k.
- Read a recommender **beyond accuracy**: **catalog coverage**, **intra-list diversity**, and **novelty** — and see
  that two paths with equal hit@k can serve very different catalogs (MF's 0.07 coverage vs item-item's 0.49).
- Build the **first blended recommender**: calibrate each Part-1 path to a common scale, take a **weighted union**
  (`blend.blend`), and order the pool with the classical ranker (`rank.rank(exclude=seen)`). At the pinned config
  (per-path pool 30, weights {popularity 0.25, lexical 0.5, item-item 1.0, MF 1.0}) the blend scores **~0.306 hit@10**
  — above the best single path (MF 0.276) — with **~0.333 coverage**, about 4.5× MF's.
- Run and read a **leave-one-path-out ablation**, and draw the honest conclusion: the three *reader-dependent* paths
  each contribute (dropping MF −0.046, item-item −0.026, lexical −0.014), but **popularity's marginal accuracy value
  is ≈0** (dropping it does not lower hit@10). "Every path contributes" is **false** here.

This unit introduces `ranking-metrics`, `beyond-accuracy`, and `score-blending`; it re-exercises Unit 1's
retrieve-then-rank/offline-evaluation/top-k metrics and Unit 2's popularity bias. It closes **Part 1**; Checkpoint A
assesses the whole Part-1 recommender on the sealed `test` holdout.

## Pacing

The unit opens with its **project hook** — *we have five paths and a scoreboard, but which recommender is best, and
best at what?* — before any new metric. Plan **60–90 minutes across two to three sittings**; assign all exercises
(1–7: 5 core + 2 Challenge):

1. **Sitting 1 (~30 min) — ranking + beyond-accuracy.** Precision@k and NDCG by hand then via `bookrec`; why NDCG
   rewards placement that hit@k ignores; coverage/diversity/novelty of a path's recs. Exercises 1–3.
2. **Sitting 2 (~35 min) — the first blend and the ablation.** Calibrate + weighted-union + rank; the pinned-config
   blended scoreboard (beats the best single path AND covers more); the leave-one-path-out ablation and why dropping
   popularity does not hurt. Exercises 4–5.
3. **Sitting 3 (~20 min, + Challenges) — the mechanisms.** The per-path pool sweep (and why we pin 30, not the
   val-max); the calibration pitfall; the cold-reader robustness demo and a forward look at cold-start (Unit 9). The
   stretch exercises 6–7.

## Common mistakes

- **Reading hit@k as the only metric.** A path can win hit@k and still serve almost none of the catalog (MF: 0.276
  hit, 0.07 coverage). Precision@k/NDCG and coverage/diversity tell different, complementary stories.
- **Tuning against the test holdout.** `test` is sealed until Checkpoint A, and even there it is evaluated **once**.
  Choosing weights or a pool by watching a test number is the cardinal sin of offline evaluation — do all selection on
  `val`, freeze, then score `test` once.
- **Assuming a blend always beats the best path — or that "every path contributes".** The measured ablation refutes
  both: the blend wins here only with a sensible pool (30) and down-weighted popularity, and **dropping popularity
  raises hit@10**. A path earns its place by *reader-dependence*, not by existing.
- **The calibration pitfall.** Min-max calibration maps every path's top candidate to 1.0, so a flat,
  reader-independent popularity path ties its head books with every reader's true top pick — which is exactly why
  popularity's marginal accuracy value is ≈0. Calibration makes paths comparable but can also let a weak path tie a
  strong one at the top.
- **Leaving the per-path pool at k.** A pool of only k candidates per path (= the top-k) starves the blend (0.278 at
  pool 10 vs 0.306 at pool 30). The blend needs a deeper pool than the final k.
- **Equating coverage with accuracy.** High coverage is a *beyond-accuracy* virtue (serving more of the catalog,
  robustness to cold readers), not a hit@k win; keep the two axes separate.

## Discussion prompts

- When does blending help, and why did *popularity* hurt? What property must a path have to add accuracy, not just
  candidates?
- What does NDCG reward that hit@k and precision@k ignore? Construct two rankings with equal hit@5 and precision@5 but
  different NDCG.
- Two recommenders tie on hit@10 but one covers 5% of the catalog and the other 49%. Which would you ship, and for
  whom?
- The 60 cold readers get `[]` from every personalized path but real recs from popularity/blend. That is graceful
  degradation, not cold-*start*. What is the harder cold-start problem a Part-1 blend still cannot solve, and why?
  (forward to Unit 9.)

## Differentiation

- **Support:** give the metric calls (`precision_at_k`/`ndcg_at_k`/`catalog_coverage`) and the `blend`/`rank`
  wiring as starter snippets so the lesson stays on *interpreting* the numbers; pair-program the ablation loop.
- **Core:** Exercises 1–5 unaided, using `run_blended_scoreboard` + the metric functions rather than reimplementing
  the blend.
- **Stretch:** the per-path pool sweep (and the anti-tuning argument for pinning 30), and reproducing the calibration
  pitfall by hand. Ask strong students to predict, before running, which single path the ablation will show is
  *least* valuable — and to explain the calibration mechanism behind the answer.
