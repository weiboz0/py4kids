# Teacher notes — Unit 5: Matrix factorization (latent factors — the embedding bridge)

## Goals

By the end of this unit students can:

- Explain **matrix factorization**: represent the reader x item interaction matrix as a product of two low-rank
  factor matrices `P Q^T` (readers x factors, items x factors), so a recommendation score is a single dot product
  `P_u . Q_i` of a reader factor and a book factor.
- Read the factors as **latent factors / embeddings**: a handful of learned "taste dials" per reader and per book,
  fitted from who-engaged-what rather than hand-labeled — and see that a dot-product retriever over these factors is
  exactly the shape Unit 8 will learn with a neural two-tower.
- Train the factors by **full-batch, per-entity-averaged gradient descent** on a **logistic implicit-feedback loss**
  with **L2 regularization**: positives are the train engagements, negatives are sampled (per train-positive) from
  each reader's unobserved complement; `error = label - sigmoid(P_u . Q_i)`, per-entity gradients accumulated with
  `bincount` and divided by each entity's interaction count.
- Read the scoreboard honestly: MF (~0.25-0.28 hit@10, here **0.276**) is **on par with item-item CF** (~0.252) —
  within noise over 500 readers, not a reliable win — while beating lexical (~0.158) and popularity (~0.108) by wide
  margins. MF is the **latent generalization** of co-occurrence: it compresses the pairwise similarity table into
  compact factors that fill in plausible similarities for warm books.

This unit introduces `matrix-factorization`, `latent-factors`, and `gradient-descent`; it re-exercises Unit 1's
retrieve-then-rank, offline evaluation, and top-k metrics, and Unit 4's implicit feedback (MF trains with sampled
negatives). It does **not** re-exercise catalog search — MF scores latent factors, it does no lexical lookup.

## Pacing

The unit opens with its **project hook** — *what if we could describe every reader and book by a handful of hidden
"taste dials"?* — which motivates latent factors before any mechanics. Plan **60-90 minutes across two to three
sittings**; assign all exercises (1-8: 6 core + 2 Challenge) across the sittings:

1. **Sitting 1 (~30 min) — the model and the loss, from scratch.** The latent-factor model and the dot-product score;
   the logistic implicit-feedback loss over positives + complement negatives; one full-batch, per-entity-averaged
   gradient-descent step by hand (watch the loss drop); train the toy factors over the pinned epochs and record the
   loss curve. Exercises 1-4.
2. **Sitting 2 (~35 min) — reveal the path, the negatives beat, the win.** Reveal `MatrixFactorizationPath` at the
   pinned config; the retrieve contract (a known reader with empty `seen` still gets recs; an unknown reader -> `[]`);
   the **negatives beat** — complement negatives vs the log's `label==0` exposure negatives (the exposure ones
   collapse MF to the floor); register all paths and read the val scoreboard — MF on par with CF, beating lexical and
   popularity. Exercises 5-6.
3. **Sitting 3 (~20 min, + Challenges) — capacity, the bridge, the limits.** `n_factors` capacity and
   under/overfitting; the score **is** an embedding dot product (the two-tower bridge to Unit 8); the cold story
   (cold reader -> `[]`, cold item scored low). The stretch exercises 7-8.

## Common mistakes

- **Leaking the holdout into training.** Fitting on `val`/`test` rows (not just `train` positives) inflates the
  scoreboard — the factors must be bit-identical whether or not `val`/`test` rows are present.
- **Not seeding.** MF init and negative sampling are random; without a fixed seed the factors (and the printed
  hit@10) change run to run. Everything here is seeded and deterministic.
- **Shrinking the epochs to "save time".** This is the mistake the data actually punishes: below ~300 epochs at
  d=32 MF silently drops below CF, and at ~100 epochs it drops **below the lexical path** — a worse recommender that
  still "runs fine". Keep the pinned `n_epochs=300`; the fit is only ~15 s.
- **Training on the log's `label==0` exposure negatives.** They look like ready-made negatives, but they are
  *exposure-biased* (a reader was shown the book and did not engage), so they carry taste signal; pushing them down
  destroys the factors and collapses MF to the random floor. Sample negatives from each reader's **unobserved
  complement** instead. (This is the unit's bridge to exposure bias, Unit 13.)
- **Forgetting regularization.** Without the L2 term the factors overfit the train positives and the val score sags.
- **Reading the factors as interpretable axes.** A single dial is not "how much sci-fi"; the factors are only
  meaningful as a whole, up to rotation. Resist naming individual dimensions.
- **Conflating a cold reader with a cold book.** A cold *reader* (0 train positives) has no learned factor, so
  `retrieve` returns `[]`. A cold *book* does get an initialized factor, but with no positive signal it is shaped
  only by negative gradient and scored near the bottom — MF scores the whole catalog (unlike CF's hard zeros) but
  still cannot meaningfully recommend cold books. The real fix is Unit 9's item features.
- **Expecting MF to "beat" CF.** On this data MF is **on par** with CF, within noise. Celebrate the parity (and the
  compression into compact factors), not a seed-lucky win.

## Discussion prompts

- MF ends up on par with item-item CF but stores a handful of factors per book instead of a similarity to every other
  book. What does the compression buy (memory? generalization to unread pairs?) and what might it cost?
- The MF score is literally `reader_factor . book_factor`. If a neural network learned those two factor vectors
  instead of gradient descent on a fixed table, what would change and what would stay the same? (bridge to the Unit 8
  two-tower.)
- Why are the log's `label==0` rows the *wrong* negatives for training here, when they were a perfectly good way to
  *describe* implicit feedback in Unit 4? What does that tell you about where a recommender's "negatives" should come
  from? (exposure bias, Unit 13.)
- Why does regularization help a recommender that has far more parameters than it has strong signal?

## Differentiation

- **Support:** give the per-entity `bincount` gradient accumulation and the sigmoid as starter snippets so the lesson
  stays on the latent-factor idea; pair-program the scoreboard call and the retrieve contract.
- **Core:** Exercises 1-6 unaided, using `MatrixFactorizationPath` rather than reimplementing the full training loop
  after the by-hand step in Exercise 3.
- **Stretch:** the `n_factors` capacity sweep, the embedding dot-product identity, and the MF-vs-CF top-k
  overlap. Ask strong students to predict, before running, whether more factors or more epochs would pull MF clearly
  ahead of CF — and at what cost — then check against the measured numbers.
