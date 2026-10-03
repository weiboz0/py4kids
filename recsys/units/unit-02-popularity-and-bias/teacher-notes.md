# Teacher notes — Unit 2: Popularity and weighted baselines

## Goals

By the end of this unit students can:

- Build the **first retrieval path that learns from data**: rank catalog items by their **popularity** —
  a count of positive interactions on the **training** split — wrap it in a `PopularityRetrievalPath`, register it,
  and score it on Unit 1's frozen `val` scoreboard, where it clears the random floor by roughly an order of magnitude.
- Derive the **weighted (Bayesian-shrinkage) rating** `score = (v·R + m·C)/(v + m)` from first principles, explain
  `m` as a prior pseudo-count, and read the algebra `score = C + v·(R−C)/(v+m)` to predict the limits
  (`m→0 ⇒ R`; as `m` grows the scores contract toward the global rate `C`).
- Distinguish **popularity** (what is consumed most) from **quality** (the per-item positive rate), and explain why,
  on a holdout whose exposure is popularity-weighted (taste-aware, but still dominated by popularity), a
  quality-first ranking scores far below popularity (barely clearing the floor) — **the offline
  metric encodes popularity bias.**
- **Measure** popularity bias directly with **catalog coverage** and **head-share**, and articulate why a recommender
  that wins hit-rate by serving only the head is still a poor system — the motivation for personalisation (Unit 4)
  and the beyond-accuracy metrics of Unit 13.

This unit introduces the three technique concepts `popularity-ranking`, `bayesian-shrinkage`, and `popularity-bias`;
it re-exercises Unit 1's retrieve-then-rank architecture, catalog search, offline evaluation, and top-k metrics.

## Pacing

The unit opens with its **project hook** — *a brand-new reader with no history just signed up; what do we recommend
before we know anything about them?* — which frames popularity as the honest cold-start baseline and sets up the
sharper question *is the most-read book the best book?* Plan **60–90 minutes of core teaching across two to three
sittings** (advanced, applied; the assumed baseline is in `curriculum/baseline.yaml`):

1. **Sitting 1 (~30 min) — popularity that works.** The cold-start hook and §1: count positives on the **train**
   split, see the heavy tail, build/fit/register `PopularityRetrievalPath`, and score it on `val` against the random
   floor (≈0.11 vs ≈0.012). Exercises 1–3.
2. **Sitting 2 (~30–40 min) — popular vs good.** §2: derive the weighted/Bayesian-shrinkage rating by hand, reveal
   `bookrec.weighted_rating`, re-rank by quality, and **honestly score the quality ranking on `val`** — the near-zero
   result and the "popularity bias lives in the metric" discussion. This is the conceptual heart; do not rush it.
   Exercises 4–5.
3. **Sitting 3 (~20 min, + Challenges) — measuring the bias.** §3: catalog coverage and head-share for popularity vs
   random; name the bias and bridge to Units 4 and 13. Exercise 6 and the two stretch Challenges.

## Common mistakes

- **Counting on `val`/`test`.** Popularity must be counted on the **train** split only; counting the holdout leaks the
  answer. The shipped `PopularityRetrievalPath.fit` ignores non-train and non-positive rows — have students verify
  that adding `val`/`test` or `label==0` rows leaves the counts unchanged.
- **Forgetting to exclude already-read books.** Score with `rank(exclude=seen)` and pass the reader's `seen` set, or a
  "recommendation" is just a book they have already read.
- **Reading the quality ranking's weak score as "quality is useless."** The weighted-rating ranking is *better* by
  quality; it scores far below popularity because the `val` holdout's exposure is popularity-weighted, so the metric rewards
  recommending the already-popular. The lesson is about the **metric**, not about quality. Watch for students who
  conclude "shrinkage is broken."
- **Mis-reading `m`.** `m` is a prior strength in pseudo-counts, not a probability or a threshold. Small `m` trusts
  each item's own rate; large `m` pulls everything toward the global rate `C`. At any finite `m` the scores do not
  collapse to ties — they contract toward `C` (ties only in the infinite limit).
- **Calling popularity "personalised."** The popularity path returns the **same** ranking for every reader. It is a
  strong *non-personalised* baseline; personalisation is Unit 4.
- **Over-reading one seed.** On this synthetic seed cold readers happen to have no `val` rows, so passing
  `cold_readers` is correct hygiene but changes nothing here; it is not a per-run count of removed readers.

## Discussion prompts

- A book read 3 times out of 3 exposures has a perfect positive rate. Should it top the recommendations? What does
  your answer say about trusting an average computed from almost no data?
- Our quality-first ranking scores far below popularity on the scoreboard. Is the ranking bad, or is the scoreboard
  bad? What would a holdout have to look like for quality to win?
- Popularity gets hit-rate ≈0.11 while covering ~0.8% of the catalog. Name a real product where "recommend the
  bestsellers" is genuinely good — and one where it is harmful. What distinguishes them?
- The weighted rating is a convex combination of the item's rate `R` and the global rate `C`. As `m → ∞`, every score
  approaches `C`. Why, then, does the ranking *not* become random — what residual signal survives?

## Differentiation

- **Support:** provide the train-split filter and the `interactions.to_dict("records")` → `fit` plumbing as starter
  snippets so the lesson stays on the recsys ideas; pair-program the scoreboard call and the coverage/head-share
  helper.
- **Core:** Exercises 1–6 unaided, using `bookrec.weighted_rating` / `head_ids_from_counts` rather than reimplementing.
- **Stretch:** the two Challenges (the convex-combination argument + predicting the coverage change, and solving for
  the `m` that ties two items). Ask strong students to predict, before running, how head-share changes as `k` grows,
  and to sketch what a *personalised* path would need to beat popularity on the same scoreboard — a bridge to Unit 4.
