# Teacher notes — Unit 7: Semantic text embeddings (the committed GloVe subset)

This unit opens **Part 2**. It introduces *dense* representations — pretrained **GloVe** word vectors — as a contrast
to Unit 3's *sparse* lexical bag-of-words, and ships a `SemanticEmbeddingRetrievalPath` that retrieves by cosine in
embedding space. The honest result is the teaching point: on this synthetic catalog semantic retrieval is **below**
the lexical path, yet it is **complementary** — and it is the bridge from Unit 5's *learned* factors to Unit 8's
*learned neural* two-tower (all three are dot-product retrievers over embeddings).

## Goals

By the end of this unit students can:

- Explain **word embeddings**: a pretrained GloVe vector per token, where cosine distance reflects *meaning* — and
  contrast this with the sparse one-hot/bag-of-words of Unit 3.
- Compose a **document (book) embedding** = the L2-normalized mean of its keyword tokens' GloVe vectors (out-of-vocab
  tokens skipped), and a reader embedding from the books in `seen`.
- Retrieve by **brute-force cosine** over the catalog (`SemanticEmbeddingRetrievalPath`), excluding `seen`.
- Read the scoreboard honestly: semantic (~0.102 hit@10) beats the random floor ~8.5× but is **below** the lexical
  path (~0.158) and far below CF/MF — its value is **complementarity** (top-10 overlap with lexical only ~0.22; adding
  it to the Unit-6 blend lifts both hit@10 and coverage), not raw accuracy.
- Explain *why* it underperforms here: the synthetic topic vocabulary is arbitrary `GENERAL_POOL` word-slices, so
  GloVe's meaning-geometry is uncorrelated-by-construction with the latent taste (only the 12 genre banks carry
  GloVe-exploitable signal); on a real catalog's prose, dense semantics would behave differently.

This unit introduces `word-embeddings`, `document-embeddings`, and `embedding-retrieval`; it re-exercises Unit 1's
retrieve-then-rank/offline-evaluation/top-k metrics/catalog search and Unit 3's bag-of-words.

## Pacing

The unit opens with its **project hook** — *two books never share a word but mean the same thing; can we match on
meaning?* Plan **60–90 minutes across two to three sittings**; assign all exercises (1–7: 4 core + 3 Challenge):

1. **Sitting 1 (~30 min) — word & document embeddings.** GloVe vectors; cosine nearest words (vocabulary-scoped);
   build a book embedding (mean pool, L2-normalize) and a reader embedding by hand. Exercises 1–2.
2. **Sitting 2 (~35 min) — the path and the honest scoreboard.** Reveal `SemanticEmbeddingRetrievalPath`; score on
   `val`; read it honestly (below lexical, above floor) and explain why; the complementarity overlap. Exercises 3–4.
3. **Sitting 3 (~20 min, + Challenges) — pooling, the blend, the bridge.** Max-sim vs mean pooling; adding semantic
   to the Unit-6 pinned blend (both hit and coverage rise); the pretrained/learned/neural dot-product-retriever
   bridge. The stretch exercises 5–7.

## Common mistakes

- **Expecting semantic to beat lexical or the collaborative paths.** It does not here (0.102 vs lexical 0.158, CF
  0.252). Celebrate the *complementarity* (low overlap, lifts the blend), not a head-to-head win.
- **Reading "semantic < lexical" as "embeddings are worse".** It is largely a **synthetic-corpus artifact** — the
  topic vocabulary is arbitrary, so GloVe's meaning can't align with the latent taste. Say so; a real catalog differs.
- **Expecting full-GloVe analogies.** The committed subset holds only the catalog's 607 vocabulary words, so
  nearest-word demos are "nearest *among the catalog vocabulary*", not general GloVe analogies.
- **Forgetting to L2-normalize** book/reader embeddings before cosine (or dividing by a zero norm for an all-OOV
  book — guard it).
- **Mishandling out-of-vocabulary tokens.** `starfall` has no GloVe vector (a zero row in the subset); skip it in
  pooling rather than letting a zero vector drag the mean.

## Discussion prompts

- Lexical and semantic overlap only ~0.22 at top-10. Name a pair of books semantic would relate that lexical never
  would, and vice versa. Which reader is each better for?
- Semantic is the weakest single path yet it improves the blend. How can a weak path still earn its place? (tie to the
  Unit-6 ablation.)
- GloVe vectors are *pretrained* on Wikipedia; Unit 5's factors were *learned* from our log; Unit 8's two-tower will
  be *learned and neural*. All three score by a dot product — what changes, and what stays the same?
- On a *real* book catalog with full descriptions, would you expect semantic to beat lexical? Why might our synthetic
  corpus understate it?

## Differentiation

- **Support:** give `load_glove_subset` + `book_embedding` and the cosine helper as starter snippets so the lesson
  stays on the *meaning* idea; pair-program the reader-embedding aggregation.
- **Core:** Exercises 1–4 unaided, using the shipped `SemanticEmbeddingRetrievalPath`.
- **Stretch:** max-sim-over-seen pooling (0.142 > mean 0.102 — a real improvement to notice and explain), adding
  semantic to the pinned blend, and reconstructing the path's score by hand to see the dot-product-retriever bridge.
  Ask strong students why max-sim beats mean here (a reader's tastes are multi-modal; the mean blurs them).
