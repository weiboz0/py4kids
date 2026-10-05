# Teacher notes — Unit 4: Neighborhood collaborative filtering (item-item co-occurrence)

## Goals

By the end of this unit students can:

- Explain **collaborative filtering**: recommend from *who read what*, not from item content — "readers who liked
  the books you liked also read…".
- Build an item-item **co-occurrence** similarity (cosine over the readers who co-engaged two items) from the
  **train** log, and use **k-nearest-neighbor** retrieval: score a candidate by the summed similarity to a reader's
  history (`ItemItemRetrievalPath`).
- Distinguish **implicit vs explicit** feedback against the real log — a read/like is a positive; there are no
  negative *ratings*; the log's `label==0` rows are exposure-sampled negatives (exposed-not-liked). The co-occurrence
  path uses **positives only**; Unit 4 does **no** negative sampling (it ranks the full catalog); sampled negatives
  are *used for training* in Unit 5 (MF) and Unit 8 (two-tower).
- Read the scoreboard honestly: item-item CF (~0.25 hit@10) is the **first path to beat both** the popularity
  baseline (~0.11) **and** the content/lexical path (~0.16) — the decisive personalization win of Part 1 — while
  acknowledging it cannot reach ~41% of the catalog (items with no train positives have no neighbors).

This unit introduces `item-item-cf`, `knn-similarity`, and `implicit-feedback`; it re-exercises Unit 1's
retrieve-then-rank, catalog search, offline evaluation, and top-k metrics.

## Pacing

The unit opens with its **project hook** — *readers who liked the books you liked also read…* — which motivates
collaborative filtering before any mechanics. Plan **60–90 minutes across two to three sittings**; assign all
exercises (1–8: 6 core + 2 Challenge) across the sittings:

1. **Sitting 1 (~25 min) — co-occurrence + implicit feedback.** The collaborative idea; implicit vs explicit against
   the real log's positives and `label==0` rows; build the item-item cosine similarity by hand. Exercises 1–2.
2. **Sitting 2 (~35 min) — k-NN retrieval and the win.** Score by summed similarity to a reader's history; the
   `n_neighbors` cap (and its honest *degradation* here); reveal `ItemItemRetrievalPath`; score on `val` — CF beats
   both popularity and lexical (~0.25 vs ~0.11 / ~0.16). Exercises 3–6.
3. **Sitting 3 (~20 min, + Challenges) — limits and bridges.** The coverage ceiling (no-neighbor items), cold items,
   and why MF (Unit 5) is a **low-rank (rank-reduced) approximation** of this full pairwise co-occurrence. The stretch exercises.

## Common mistakes

- **Leaking the holdout into the similarity.** Building co-occurrence from `val`/`test` rows (not just `train`) makes
  the scoreboard jump to ~**0.96** — a "too good to be true" number that signals leakage. The similarity must be
  bit-identical whether or not `val`/`test` rows are present; only `train` positives count.
- **Recommending already-read books.** A reader's own history is the *query*, not a recommendation — exclude `seen`
  with `rank(exclude=seen)`.
- **Assuming a bigger/smaller neighbor cap helps.** On this data an **uncapped** neighborhood is best; a small
  `n_neighbors` cap (e.g. 10) *lowers* the score below lexical. Don't present capping as a free win.
- **Expecting CF to cover the whole catalog.** ~41% of items have no train positives, so CF can *never* surface them
  (no co-occurrence) — unlike the content/lexical path. This is the cold-item problem that blending and Unit 6
  address, not a bug.
- **Confusing item-item with user-user CF.** We ship item-item (similar *items* to what you read). User-user (similar
  *readers*) is a mention, not the path.
- **Treating `label==0` as "never expose".** They are *exposed-not-liked* events — the implicit-feedback negatives —
  not items to avoid; the point is that implicit data has no explicit negative ratings.

## Discussion prompts

- Content (Unit 3) and collaborative (this unit) make *different* mistakes. Name a book each would recommend that the
  other never would. Which reader is each better for?
- CF beats content here, but content can recommend a brand-new book with no readers. When would you *want* the weaker
  path? (bridge to cold-start and blending, Unit 6.)
- Our co-occurrence similarity is item×item. What changes if we build reader×reader instead — what does each scale
  with, and which is cheaper when there are far more readers than books?
- Co-occurrence is a big, sparse similarity matrix. Unit 5 replaces it with a handful of latent factors per
  item/reader. What would that buy us (coverage? cold items? memory?) and what might it cost?

## Differentiation

- **Support:** give the train-positive filter and the incidence→cosine construction as starter snippets so the
  lesson stays on the CF ideas; pair-program the scoreboard call and the neighbor lookup.
- **Core:** Exercises 1–6 unaided, using `bookrec.item_item_cosine` / `ItemItemRetrievalPath` rather than
  reimplementing the matrix.
- **Stretch:** the `n_neighbors`-cap degradation, the no-neighbor coverage ceiling, and the "MF is a low-rank
  (rank-reduced) approximation of the full co-occurrence" argument bridging to MF. Ask strong students to predict, before running, how CF and content
  rank a book that is popular-but-off-taste vs niche-but-on-taste.
