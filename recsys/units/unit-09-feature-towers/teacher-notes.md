# Teacher notes — Unit 9: Feature towers and item cold-start

This unit solves the **item cold-start** problem the course has flagged since Unit 6:
our best recommender so far (Unit 8's two-tower, hit@10 ~0.340) *buries* any book nobody has read yet —
818 of the catalog have zero train-positive interactions (they appear only as sampled negatives), and
an ID-only tower gives them negative-shaped
embeddings that rank near the bottom (cold-item coverage **0**).
The fix is a **feature tower**: the item side stops being a bare per-id embedding and instead combines
an id embedding with learned embeddings of the book's **genre** and **author** and an `nn.Linear`
projection of its **GloVe keyword vector** (Unit 7), summed to the shared dimension.
Now a cold book gets a vector from *what it is*, so the path can place it.
The headline is deliberately honest: the feature tower does **not** set a new warm record — it makes a
**warm↔cold trade**, and the knob that controls that trade (the **negative pool**) is the real lesson.

## Goals

By the end of this unit students can:

- Explain **item cold-start**: why an id-only two-tower and item-item CF score a zero-interaction book at
  the bottom (its id embedding was only ever shaped by being sampled as a negative), and why *content*
  features give a cold item a usable vector.
- Build a **feature tower** in PyTorch extending Unit 8: item vector = id embedding + genre embedding +
  author embedding + `Linear`(GloVe keyword vector), summed; reader tower stays id-based; score is still
  the dot product.
- Measure cold reach with a **validation-safe metric** — **cold-item coverage** = unique zero-train item
  ids appearing in readers' top-10 / 818, counted over all fitted non-cold readers scored from their
  **train** histories only. Explain *why* hit@k on the designated cold items is **not** measurable on
  `val` (they have no held-out val positives by construction — that relevance is sealed for Checkpoint B
  on `test`).
- Read the result honestly: warm-only negatives lift cold coverage ~3× (0.048 full-catalog → **0.138**;
  vs 0 for ID-only/CF) at a small warm cost (0.338 → **0.298**, still within 0.06 of the two-tower's
  0.340). It is a **compromise, not dominance** — content paths (Unit 7 semantic, coverage 0.328)
  already serve cold freely; the feature
  tower is the first *learned-taste / collaborative* path to serve cold while staying near the best warm.
- Explain **hard negatives** (popularity-weighted sampling) and the false-negative risk, and read the
  measurement: here they trade warm for cold *harder* (warm 0.172 / coverage 0.226) — a knob, not a
  free sharpening.

This unit introduces `feature-towers`, `item-cold-start`, and `hard-negatives`; it re-exercises Unit 1's
retrieve-then-rank / offline-evaluation / top-k metrics, Unit 4's implicit feedback (sampled negatives),
Unit 5's latent factors, Unit 6's beyond-accuracy coverage, Unit 7's word embeddings, and Unit 8's
two-tower / neural training.

## Pacing

The unit opens with its **project hook** — *our best recommender can't recommend a book nobody has read
yet; 818 of them. Can features fix that?* Plan **60–90 minutes across two to three sittings**; assign all
exercises (core + Challenge). Each full-config training fit is ~20–27 s at the pinned `n_epochs=40`, so
keep to two or three fits per sitting and reuse a trained path across cells.

1. **Sitting 1 (~30 min) — the cold-item problem and the feature tower.** Make cold-start concrete:
   ID-only two-tower / CF cold coverage is 0 (Ex: confirm it). Build the feature item vector from
   genre/author/GloVe and explain the architecture extending Unit 8.
2. **Sitting 2 (~35 min) — train it, and the negative pool.** Train/register `FeatureTowerRetrievalPath`
   (warm-only), read the val scoreboard (warm near U8) and the cold-coverage table (feature tower > 0 vs
   ID-only/CF = 0). Then the mechanism: warm-only vs full-catalog negatives, and that it is a trade.
3. **Sitting 3 (~20 min, + Challenges) — hard negatives and the bridge.** The hard-negative ablation
   (warm↔cold trade, false-negative caveat) and the surfaced cold book for a specific reader; the bridge
   to U10 (fast retrieval), U11 (reranker), U13 (cold-start in the ethics thread).

## Common mistakes

- **Expecting a new warm-hit record.** The feature tower does NOT beat the two-tower on warm hit@10
  (0.298 vs 0.340). The win is **cold reach** (coverage 0 → 0.138). Grading or discussion that treats a
  lower warm number as "worse" misses the point — it is the price of serving cold items.
- **Measuring cold hit@k on `val`.** The designated cold items have no val positives by construction, so
  their relevance is unmeasurable on val — use **coverage** (does the path surface cold items at all?),
  and defer cold *relevance* to Checkpoint B on the sealed `test` split. Never pull `split="test"` here.
- **Letting the coverage cohort depend on val.** Count coverage over all fitted non-cold readers scored
  from their **train** histories — not the scoreboard's held-out-positive "eligible" readers, or the
  metric smuggles val back in.
- **Non-determinism.** Unseeded torch / multiple threads / `use_deterministic_algorithms(False)` give
  different results each run. The path seeds all three and single-threads inside `fit`; two seeded fits
  give identical top-k ranking.
- **Hard negatives sampling true positives as negatives.** Popularity-weighted negatives can draw items
  the reader actually likes (false negatives). That is a real risk, and it is part of why hard negatives
  here trade warm for cold rather than improving both.
- **Thinking a cold item needs a better id embedding.** It cannot have one — it has no interactions.
  What rescues it is the **feature** side (genre/author/GloVe), which is exactly what the feature tower
  adds.

## Discussion prompts

- An id embedding for a zero-interaction book was only ever updated by being sampled as a *negative*.
  What does that do to its vector, and why can't more training fix it without features?
- The negative pool is the whole game. Why does drawing negatives from the *warm* (train-positive)
  universe let features place cold items, when drawing from the full catalog buries them?
- The feature tower trades ~0.04 warm hit for ~3× cold coverage. When is that trade worth it for a real
  bookstore — and when would you keep the id-only two-tower instead?
- Which feature do you expect predicts taste best here — genre, author, or GloVe keywords? How would you
  measure that? (The shipped path has no knob to drop a feature input, so an actual ablation means
  subclassing `feature_tower.py` — a good extension, but beyond the two shipped Challenges.)
- Hard negatives traded warm for cold rather than sharpening both. What property of this small log makes
  "harder" negatives not obviously better, and what is the false-negative risk?
- Trace the cold-start thread: Unit 6 flagged coverage as a blind spot, Unit 9 serves cold items with
  features, Unit 13 revisits them in the ethics / beyond-accuracy thread. What is still unsolved after
  this unit?

## Provenance

Original content. The **two-tower / dual-encoder** and **content/feature towers** for cold-start are
standard retrieval practice (no single source); **hard-negative sampling** and its false-negative caveat
are a well-known training technique in the implicit-feedback literature — worth a one-line framing for a
calc/linalg audience, no attribution required.

## Differentiation

- **Support:** give the feature-vector assembly (genre/author/GloVe → summed item vector) and the
  training call as starter snippets so the lesson stays on the *ideas* (why cold items need features, why
  the negative pool controls reach); pair-program the first training/scoreboard cell.
- **Core:** train/register `FeatureTowerRetrievalPath` unaided, read the val scoreboard and the
  cold-coverage table, and surface a cold book for a specific reader.
- **Stretch:** the two shipped Challenges — the negative-pool knob (warm-only vs full-catalog — watch
  both warm and cold move) and uniform vs hard negatives (the warm↔cold trade and the false-negative
  risk). For students who want more, a feature-input ablation (id-only vs +genre vs +author vs +GloVe)
  is a natural extension, but it requires subclassing `feature_tower.py` to expose which inputs the item
  tower uses — it is not a drop-in knob. Ask strong students to predict the trade
  direction before running it, and to explain why a cold item's coverage can rise while its hit@k stays
  near zero.
