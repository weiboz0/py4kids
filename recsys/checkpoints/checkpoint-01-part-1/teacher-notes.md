# Teacher notes — Checkpoint A: the Part-1 recommender

This checkpoint closes **Part 1**. It is the one authorized **unseal of the `test` holdout** that has been sealed
since Unit 1: the student assembles the Part-1 recommender, tunes and freezes it on `val`, and scores it exactly once
on `test`. It is **strict** — every task draws only on concepts taught in Units 1–6; there are no borrowed tools and
no cold-start assessment (cold readers appear only as the `cold_readers` exclusion and a robustness note).

## Goals

Confirm the student can, unaided, assemble and *honestly evaluate* the whole Part-1 recommender:

- search the catalog and name the item universe / coverage denominator (Q1);
- build and register the four learned paths — popularity, lexical, item-item CF, MF — and produce a reader's
  recommendations through retrieve-then-rank (Q2);
- score paths with **ranking metrics** (precision@k, NDCG@k) and say why a ranking metric, not RMSE, fits implicit
  top-k (Q3);
- read a recommender **beyond accuracy** — coverage, diversity, novelty (Q4);
- build a calibrated **blend**, compare it honestly to the best single path, and **freeze** the configuration (Q5);
- run a **leave-one-path-out ablation** and interpret popularity's ≈0 marginal accuracy via the calibration pitfall
  (Q6);
- perform the **one-shot `test` evaluation** of the frozen recommender and interpret val-vs-test honestly (Q7).

## Pacing

A single assessment sitting of about **60 minutes** (it may run to 75 for students who write careful short-answers).
Questions 1–6 are all on `val`; Q7 is the short, decisive test-unseal. Students should NOT start Q7 until every
decision in Q1–Q6 is frozen.

## Common mistakes

- **Tuning against `test`.** The whole point of the freeze-then-score discipline: all path/weight/pool choices are
  made on `val` and frozen; `test` is scored once. A student who re-opens Q5 after seeing the Q7 number has turned the
  holdout into a second validation set — the single most important error to catch.
- **Expecting the blend to crush the single paths.** It beats MF modestly (≈0.306 vs 0.276) and covers far more; a
  student who reports "the blend wins big" or "every path helps" has missed the ablation (popularity's marginal
  accuracy value is ≈0).
- **Confusing coverage with accuracy.** High coverage/diversity is a different axis from hit@k — credit the student
  for keeping them separate.
- **Reading one metric.** A complete answer uses precision@k/NDCG alongside hit@k and at least one beyond-accuracy
  metric.
- **A too-shallow per-path pool.** Blending the top-k of each path starves the pool; the frozen config uses a deeper
  pool (30) than the final k (10).

## Discussion prompts

- Your `val` and `test` numbers came out close. What would it have meant if `test` were much worse — overfitting to
  `val`, or just holdout noise? How could you tell them apart *without* peeking at `test` again?
- Popularity barely moved the blend's accuracy yet you kept it. Defend that choice on grounds other than hit@k.
- If you could add one more path to the blend, what signal would it carry that the four Part-1 paths miss?

## Differentiation

- **Support:** provide the path-assembly and `run_validation_scoreboard`/`run_blended_scoreboard` calls as scaffolds
  so the assessment tests *interpretation* (metrics, ablation, test hygiene) rather than wiring.
- **Core:** Q1–Q7 unaided using the `bookrec` API.
- **Extension:** ask the student to predict the `test` hit@10 from the frozen `val` number *before* running Q7, then
  explain the gap — a concrete test of whether they trust `val` as an unbiased estimate.

## Grading

Out of **100 points**, weighted toward honest evaluation over wiring:

- **Q1 catalog search / item universe — 8.** Correct search results; names the catalog as the coverage denominator.
- **Q2 assemble + register the four paths — 12.** All four fit and register; a reader's top-10 via retrieve-then-rank
  excluding `seen`.
- **Q3 ranking metrics — 16.** Correct precision@k/NDCG@k per path; a sound why-not-RMSE answer and what NDCG rewards
  that hit@k/precision@k ignore.
- **Q4 beyond-accuracy — 14.** Correct coverage/diversity/novelty; interprets the accuracy-vs-coverage tension
  (e.g. MF high hit, low coverage).
- **Q5 build + FREEZE the blend — 16.** Calibrated weighted blend at a defensible config; honest comparison to the
  best single path; decisions crystallized into frozen constants with the frozen `val` number recorded.
- **Q6 ablation — 16.** Correct signed leave-one-path-out; identifies popularity's ≈0 marginal accuracy and explains
  the min-max calibration pitfall; justifies keeping popularity on coverage/robustness grounds.
- **Q7 one-shot `test` unseal — 18.** Evaluates the FROZEN recommender on `test` exactly once; reports test vs frozen
  val; a correct account of *why* test is scored once (no tuning). **Any evidence of tuning against `test` caps Q7 at
  half and should be flagged in feedback** — test-set hygiene is the checkpoint's central competency.

Full credit requires the honest framing throughout: the blend is a modest, well-understood win, not a blanket one.
