# Teacher notes — Unit 12: Sequence-aware retrieval

Every path so far has treated a reader's history as a **bag** of books.
This unit asks whether the *order* matters: does the book a reader finished **last** tell us more about the next
one than a book from months ago?
The unit runs on a **separate session log** (`sessions.csv.gz`).
It is a different synthetic reader population with real order effects: finished volume 2 pulls volume 3, an author
streak, a genre mood.
The main interaction log turned out to have no usable order signal (design 011 §6, recsys-014).
**Every number in this unit is "on the session log" and is not comparable to the numbers in Units 2–11.**
Say this out loud at the start.

The unit is built around three measured results (committed seed, val, k = 10, 1,419 readers):

1. **Recency wins.** Plain item-item CF over the whole history (Unit 4's path) scores **0.480**.
   Querying with only the reader's **last 3 distinct** books scores **0.551** (+0.071), and the last 5 score
   **0.572**.
   Using *all* books again (`k_last=None`) gives back exactly Unit 4's 0.480: the old path is the
   "remember everything" end of the same dial.
2. **Order, not the item set, carries the lift.** A first-order **transition** model ("what do people read
   *right after* this book") over the last 5 books scores **0.516**.
   Shuffle every reader's history (same books, random order), refit, and it falls to **0.333**, i.e. 1.55×.
   That **control** is the evidence that order matters; a raw score alone proves nothing.
3. **A tiny self-attention model learns order, but does not win.** The SASRec-style model (1 block, dim 32, the
   unit's fast 30-epoch recipe) scores **0.423**.
   This unit's milestone measures it against its own shuffled copy at 0.383 (+0.040, 3.8 paired standard errors),
   so it *does* learn order.
   But it **trails** plain item-item CF by about **0.06** (−0.057 ± 0.012) and the simple order paths by more.
   The longer recipe measured when the data was built (recsys-014) came within 0.04 of item-item CF on held-out
   seeds. That is *its* result, not this unit's, and even it missed by 0.046 on this seed.
   Do not let students leave thinking "attention wins". On this data a counting model captures the short-range,
   item-to-item order effects, and a tiny attention model at our size budget cannot use its extra flexibility.

## Goals

By the end of this unit students can:

- Explain why a reading history is a **sequence**, and turn a bag recommender into a **recency** recommender by
  querying with the last *k* distinct books (`LastKItemItemPath`). Show that `k = all` recovers the bag model.
- Build a first-order **item transition** table by hand from consecutive train reads, and explain why only
  *consecutive train pairs* may be counted: a val or test read must never enter the table.
- Use an **order-shuffled control** correctly. It shuffles both the history the model learns from **and** the
  history it queries with, and the drop in score is the evidence that order matters.
- Explain **causal self-attention**: each position may look only at earlier positions (the causal mask). Train
  the `SasrecRetrievalPath` deterministically, and read its result honestly: it learns order but trails the
  simple paths here.
- Read next-item hit@10 alongside any-item hit@10, and coverage alongside accuracy.

## Pacing

The unit opens with its **project hook**: *you just finished volume 2 of a series; should the recommender care that
you read it last?*
Plan **60–90 minutes across two to three sittings**, and assign all exercises.
The numpy paths fit in under a second.
The SASRec fit takes about **45–70 s**, depending on machine load, so run it once, in its own cell, and reuse the fitted path.

1. **Sitting 1 (~30 min) — sequences and recency.** Meet the session log and one reader's ordered history, with the
   series volumes visible. Run the bag baseline, then the last-k query by hand and the `LastKItemItemPath` reveal.
   Finish with the k sweep (1, 3, 5, all).
2. **Sitting 2 (~30 min) — transitions and the control.** Count consecutive pairs by hand, reveal the
   `TransitionRetrievalPath`, then shuffle and refit. The collapse is the evidence.
3. **Sitting 3 (~25 min, plus Challenges) — self-attention.** Build the causal mask and one attention step by hand
   on a toy sequence. Train SASRec, then give the honest readout and the "why".

## Common mistakes

- **Comparing session-log numbers to main-log numbers.** "0.55 beats Unit 8's 0.34!" is meaningless: the readers,
  history lengths and order effects all differ. Compare paths only *within* the session log.
- **Letting val or test reads into the transition counts.** A transition table counted over all rows has seen the
  answer. Count consecutive pairs of **train positives only**; the last-train → first-val step is exactly what we
  are trying to predict. The shipped path is tested against this leak.
- **A half-shuffled control.** Shuffling only the training histories, or only the query, is a weaker and misleading
  control. The shuffle must apply to both, so the model learns and queries from the same scrambled order.
- **Querying from the `seen` set.** `context["seen"]` is an unordered *set*: fine for excluding books already
  read, useless for "the last 3". The order lives in the stored history.
- **Re-reads in last-k.** About 28% of train reads in the session log are re-reads. "Last 3" means the last 3
  **distinct** books; counting a re-read twice gives a different model, and `k = all` no longer matches
  Unit 4.
- **Claiming SASRec wins, or ties.** At this unit's recipe it trails item-item CF by about 0.06. Give the measured
  gap.
- **Using the series table as a model input.** `series.csv.gz` is a *diagnostic lens* (for example, "did the
  next volume make the top 10?"). The paths learn series effects from reading order alone.
- **Non-determinism.** SASRec must be seeded and single-threaded. Two fits with the same seed give the same
  top-10 lists.

## Discussion prompts

- When would self-attention beat counting? Think about longer-range patterns, much more data, a bigger model, and
  rich item features.
- Why is order evidence a *control*, not a raw number? What would a 0.52 transition score mean without the 0.33
  shuffled baseline?
- Which real-world sequences have strong order effects (series, playlists, courses, shopping baskets)? Which have
  almost none?
- Recency improved hit@10 *and* coverage here. Why would looking at fewer books surface a wider range of
  recommendations?
- The data generator *put* order effects into this log. What does that tell us about reading too much into a
  synthetic win?

## Provenance

Original content.
**Sequential recommendation**, first-order **Markov / transition** models, and **SASRec** (Kang & McAuley,
*Self-Attentive Sequential Recommendation*, 2018) are standard recsys methods. They are named here for an advanced
audience; no material is adapted from a single source.
The session log is the course's own seeded synthetic data (`recsys/data/gen_sessions.py`, recsys-014).

## Differentiation

- **Support:** give the hand-written last-k query and transition-counting loops as starter snippets, so the
  sittings stay on the *ideas* (recency, order evidence, the honest readout). Pair-program the shuffled control.
- **Core:**
  - the last-k sweep;
  - the transition table by hand, then the path;
  - the shuffled control;
  - one SASRec fit and its honest comparison;
  - next-item vs any-item hit;
  - coverage per path.
- **Stretch:**
  - a second-order transition (pairs of previous books) or a time-decayed recency CF;
  - a next-in-series diagnostic, with the series table used *only* as an evaluation lens;
  - a blend of last-k CF and transition.
  Ask strong students to predict, *before* running it, whether shuffling will hurt last-k CF as much as the
  transition model, and why.
