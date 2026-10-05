# Teacher notes — Unit 3: Lexical retrieval (TF-IDF and BM25)

## Goals

By the end of this unit students can:

- Represent each book as a **bag of words** over its keyword text (vocabulary, document frequency
  `df`, raw term frequency), and explain why a reader's taste can be matched through the words
  their books share.
- Derive **TF-IDF** weighting and **cosine similarity** from scratch, and use them to score the
  catalog against a reader's keyword profile; explain why **IDF** down-weights ubiquitous words.
- Build **Okapi BM25** — IDF × saturating term frequency (`k1`) × document-length normalization
  (`b`) — and say precisely **what it adds over TF-IDF cosine and when it matters**: the `b`
  length-normalization effect is visible on these real variable-length documents; `k1` saturation
  is a *small* effect here because the keyword bags repeat terms only lightly.
- Ship a `LexicalRetrievalPath`, register it, and score it on the `val` scoreboard: it clears the
  random floor by ~13× and is a **strong content candidate source** — comparable to simple content
  matching, and (honestly) **below** the collaborative/latent paths still to come. The first
  **reader-dependent** path in the book.

This unit introduces `bag-of-words`, `tf-idf`, and `bm25`; it re-exercises Unit 1's
retrieve-then-rank, catalog search, offline evaluation, and top-k metrics.

## Pacing

The unit opens with its **project hook** — *you've read a handful of books; which other books use
the same words and themes?* — framing lexical/content retrieval as the first path that adapts to
the individual reader. Plan **60–90 minutes across two to three sittings** (advanced, applied):

1. **Sitting 1 (~25 min) — bag-of-words + TF-IDF.** The keyword text, the vocabulary and `df`,
   tf-idf weights and cosine similarity by hand; reveal `bookrec.tfidf_matrix`/`cosine_similarity`.
   Exercises 1–2.
2. **Sitting 2 (~35 min) — BM25 and the path.** Derive BM25; see the `b` length-norm effect on real
   docs and the (small) `k1` effect; build/register `LexicalRetrievalPath` and score it on `val`
   against the random floor and the Unit-2 popularity baseline. The honest reading — strong content
   source, comparable to simple matching, below the collaborative paths to come. Exercises 3–6.
3. **Sitting 3 (~20 min, + Challenges) — the limits.** The `k1→∞` (linear) and `k1→0` (binary)
   limits and why `k1→0` is about the best setting on these short keyword bags; rare-keyword
   dominance. Stretch exercises.

## Common mistakes

- **Skipping IDF.** Without inverse-document-frequency the most *common* words dominate every
  match, and a reader is recommended generic books. IDF is what makes a shared *rare* word
  informative.
- **No length normalization.** Without the `b` term, long keyword lists win spuriously (more tokens
  → more chances to match). BM25's `b` corrects for document length; show the top-k mean document
  length shrinking as `b` goes 0 → 1.
- **Leaking the future into the query.** A reader's query is the keyword text of the books in their
  **train** `seen` set, never their `val`/`test` books. Build the profile from `context["seen"]`.
- **Expecting BM25 to beat TF-IDF cosine on the scoreboard.** On this corpus they are about equal
  (~0.16) — BM25's advantages (term saturation) show up on long, repetitive *free text*, not on
  short keyword bags. Teach *what BM25 adds*, not that it always wins.
- **Confusing the path's two numbers.** Hit-rate@k ~0.16 (good vs the ~0.012 floor) does not mean
  "lexical is the best recommender" — popularity is ~0.11 and the collaborative paths of Units 4–5
  will go higher. Lexical is one strong *candidate source* feeding the blend.

## Discussion prompts

- A reader who loved five poetry books gets more poetry back. When is "more of the same words" a
  good recommendation, and when does it trap the reader in a narrow niche?
- **Why does `k1` (term saturation) barely change the results on our keyword bags, and when would
  it matter?** (Because books repeat a keyword only lightly — median max term-frequency is 2 — so
  there is little saturation to do; it matters on long free-text documents where a word recurs many
  times.)
- IDF rewards rare shared words. What failure mode appears if a word is *too* rare (appears in one
  or two books)? How does that relate to the cold-start problem?
- Lexical retrieval needs text. What can it recommend for a brand-new book with keywords but no
  readers yet — and what can popularity (Unit 2) not do there?

## Differentiation

- **Support:** give the tokenize + `df`/`idf` helper and the profile-building loop as starter
  snippets so the lesson stays on the retrieval ideas; pair-program the scoreboard call.
- **Core:** Exercises 1–4 unaided, using `bookrec.tfidf_matrix`/`LexicalRetrievalPath` rather than
  reimplementing the index.
- **Stretch:** the `k1→∞`/`k1→0` limit exercises and rare-keyword dominance. Ask strong students to
  predict, before running, how the top-k mean document length moves with `b`, and to sketch why a
  content path and a popularity path make *different* mistakes — a bridge to the collaborative
  filtering of Unit 4.
