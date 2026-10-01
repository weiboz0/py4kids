# Teacher notes — Unit 1: The recommendation problem and the scoreboard

## Goals

By the end of this unit students can:

- Frame recommendation as **retrieve-then-rank** and name the `RetrievalPath` contract
  (a path proposes scored candidates; a blender merges them; a ranker orders the pool).
- Load and inspect the generated book **catalog** on its real schema
  (`item_id`, `title`, `author_id`, `genres`, `year`) and run attribute/text **search and filter** over it.
- Explain why evaluation uses the generator's **per-reader temporal split** —
  train in the past, score on `val`, keep `test` sealed — and what leakage would mean here.
- Compute **hit-rate@k** and **recall@k** from scratch, distinguish the per-query value from the aggregate mean,
  and read the shared scoreboard.
- Reason about the **seeded random baseline**: derive its expected hit-rate@k (`= k/N` for one relevant item)
  and confirm the empirical number matches — the floor every later retrieval path must beat.

This unit introduces the four technique concepts `retrieve-then-rank`, `catalog-search`, `offline-evaluation`,
and `top-k-ranking-metrics`; it builds no learned/scored path yet (popularity is Unit 2).

## Pacing

Plan for **two to three sittings** (this is an advanced, applied unit; see the book's assumed baseline in
`curriculum/baseline.yaml`):

1. **Sitting 1 — the problem and the catalog.** The "what should I read next?" hook, the catalog schema and the
   dict→DataFrame view (coerce `genres` from the `;`-joined string and `year` to int), and search/filter
   (lesson §§1–2; Exercises 1–3). Have everyone regenerate the synthetic data first
   (`python -m recsys.data.gen_catalog` / `gen_interactions`, or let the project helper point at it).
2. **Sitting 2 — retrieve-then-rank and the honest scoreboard.** The architecture and `RetrievalPath`, then the
   temporal `val` split and the two metrics derived from scratch before revealing the
   `bookrec.hit_rate_at_k` and `bookrec.recall_at_k` re-exports
   (lesson §§3–4; Exercises 4–6). This is the conceptual heart — do not rush the leakage discussion.
3. **Sitting 3 — the random floor (+ Challenges).** The seeded random baseline and its analytic expectation
   (lesson §5; Exercises 7–8, both `stretch`). Strong groups can start Unit 2's popularity path informally.

## Common mistakes

- **Scoring on the training split / leaking the future.** The whole point of the temporal per-reader split is that
  you never evaluate on interactions the model could have trained on. If a student's scoreboard number looks
  suspiciously high, check they used `val` and excluded already-seen books with `rank(exclude=seen)`.
- **Touching `test`.** `test` stays sealed until Unit 6 / Checkpoint A. Using it now inflates everything and there
  is nothing left to measure honestly later.
- **hit-rate@k is not precision@k.** Hit-rate@k asks "did *any* relevant item land in the top k?" (per query, then
  averaged); precision@k and NDCG come in Unit 6. Watch for students dividing by `k` and calling it hit rate.
- **Biasing the random floor.** Readers with zero `val` positives (and cold readers, whose events are all `test`)
  must be excluded from the scoreboard mean, or the floor reads artificially low.
- **Counting re-reads as relevant.** Remove positive validation items already seen in positive training rows:
  a re-read is not a recommendation and cannot belong in the relevant denominator.
- **Random path shrinking below k.** The random baseline must sample from the *unseen* set so that
  `rank(exclude=seen)` doesn't drop it below `k` and break the empirical≈analytic comparison.
- **Confusing the `Book` attributes with its fields.** Only `item_id`/`title` are typed attributes; `author_id`,
  `genres`, `year` live as strings in `Book.fields` and need coercion.
- **Searching placeholder titles.** Generated titles are identifiers such as `Book 00000`; until later units add
  real text, useful `text=` queries target genres or author/year digits in the search haystack.

## Discussion prompts

- Why is "recommend the books this reader already loved" a useless-but-high-scoring recommender? What does that tell
  us about choosing an evaluation set?
- A per-*user* random split would be easier to code than the temporal one. What could it leak that the temporal
  split cannot?
- Our floor is a *random* path. Why is beating random a low bar — and why is it still worth measuring every time?
- Hit-rate@k rises as `k` grows. Is a recommender with higher hit-rate@20 than another's hit-rate@5 "better"?

## Differentiation

- **Support:** give the dict→DataFrame coercion and the `val`-split filter as starter snippets so the lesson stays
  on the recsys ideas rather than pandas plumbing; pair-program Exercises 5–6.
- **Core:** Exercises 1–6 unaided.
- **Stretch:** Exercises 7–8 (the analytic `= k/N` derivation and the analytic-vs-empirical comparison); ask strong
  students to predict how the floor changes with `k` and with the number of relevant items before running it, and
  to sketch what a non-random path (popularity) would need to beat it — a bridge to Unit 2.
