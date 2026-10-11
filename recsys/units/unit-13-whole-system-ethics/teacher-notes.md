# Teacher notes — Unit 13: Evaluating the whole system (ethics and beyond-accuracy)

Twelve units have chased one number, hit@10.
This unit asks what that number hides: **who** the recommender is good for, **which books it never shows**, and
**what happens when readers start reading what it suggests**.
Everything runs on the main interaction log, using paths students already built.
Every claim in the unit is a **measurement on our data**, not an opinion.
Keep it that way in discussion: the unit presents trade-offs, and the class decides what they think about them.

The unit is built around four measured results (committed seed, val, k = 10, a 500-reader cohort):

1. **The most accurate paths are the most concentrated.** The U10 hybrid (hit 0.362) and the two-tower (0.340)
   send most of their exposure to a few popular books (exposure Gini 0.922 / 0.929, head-share 0.86 / 0.90).
   Item-item CF is the least concentrated collaborative path: Gini 0.773, coverage 0.49, but hit 0.252.
   Popularity is the extreme case (Gini 0.995, coverage 0.008).
   A popularity-penalty re-rank traces the **trade-off curve**. On item-item, raising the penalty λ from 0 to 1
   lowers the Gini from 0.773 to 0.713 and lowers hit from 0.252 to 0.112. There is no free lunch, only a choice of
   point on the curve.
2. **Feedback loops concentrate exposure.** In the *stylized* loop, simulated readers take each shown book with
   probability 0.3, and the path is retrained on the result six times. Under that loop item-item CF's catalog
   coverage falls from 0.490 to 0.358 and its Gini rises from 0.773 to 0.832. Its clean accuracy on the original
   val set falls from 0.252 to 0.09, because the model learns *the recommender*, not the readers.
   An **exploration slot** (one random unseen book in slot 10) partially restores exposure: coverage 0.421, Gini
   0.812.
3. **Filter bubbles are measurable, and here they are transient.** The genre spread of item-item's lists drops from
   1.64 bits to a minimum of about 1.18 bits by round 3–4. It then partly rebounds as readers exhaust their
   neighbourhood.
4. **Offline scores reflect the logging policy.** 44% of val positives are head books, and every collaborative path
   hits head targets at least 5× as often as tail targets (item-item 0.356 vs 0.032; MF 0.427 vs 0.000).
   That is a *measured association* in data that an earlier system's exposure shaped. It is not proof that the
   scores are "inflated", and students should say exactly that.

The **cold-start thread** (Units 6 → 9 → 13) closes here. The warm-only collaborative paths (popularity, item-item,
MF, two-tower) surface **zero** never-read books. The feature tower is the only *learned/collaborative* path that
serves them (109 of 818). The content paths surface even more (lexical 128, semantic 263).

## Goals

By the end of this unit students can:

- Read a **whole-system scoreboard**: hit@10 alongside coverage, head-share, the exposure Gini (computed over the
  **full catalog**, zeros included) and genre spread. Explain why the most accurate path is not automatically the
  best one.
- Compute a **Gini coefficient** by hand and with `exposure_gini`. Compute author-level exposure, and put it next to
  each author's **catalog share** (unequal exposure partly reflects unequal numbers of books).
- Trace an **accuracy ↔ exposure trade-off curve** with a popularity-penalty re-rank, and describe a point on it in
  numbers.
- Run and read a **feedback-loop simulation**. Explain the **leakage guard**: the simulation must never let a
  reader "accept" their own held-out val/test book. Without the guard, clean accuracy *rises*, which is a leak, not
  a result. Explain why one exploration slot partly helps.
- Measure **filter-bubble** narrowing of genre spread across rounds.
- State what offline metrics can and cannot tell us, and close the cold-start thread with numbers.

## Pacing

The unit opens with its **project hook**: *"Your recommender scores well. Who is it good for?"*
Plan **60–90 minutes across two to three sittings**; assign all exercises.
The model fits (MF, two-tower, feature tower) each take about 15–35 s depending on machine load. Each feedback
loop takes about 10–15 s. Run every loop in its own cell.

1. **Sitting 1 (~30 min) — exposure fairness.** The whole-system scoreboard; the Gini by hand, then the helper;
   author exposure against catalog share; the penalty trade-off curve.
2. **Sitting 2 (~35 min) — feedback loops and filter bubbles.** One round by hand (and why the leakage guard
   matters); the full simulation for item-item and popularity; the exploration slot; genre spread across rounds.
3. **Sitting 3 (~20 min, plus Challenges) — the limits of offline evaluation and cold start.** The head/tail split
   and the cold-item readout. Preview Checkpoint B.

## Common mistakes

- **Treating one fairness metric as "fairness".** The Gini, long-tail share, coverage and author exposure each
  measure *one* kind of inequality. These are descriptive proxies; a fairness judgement needs a stated goal
  ("fair to whom, measured how?").
- **Comparing a Gini across different catalog sizes or item sets.** Always compute over the same full catalog,
  zeros included; otherwise the numbers are not comparable.
- **Forgetting the logging policy.** Offline hit@k is measured on data an earlier system's exposure shaped.
  Report the head/tail split; do not claim a causal "inflation" the data cannot show.
- **A feedback loop that leaks val into the train log.** If simulated readers may "accept" their own held-out book,
  the retrained model recovers the answer and clean accuracy *rises* (measured: 0.252 → 0.27–0.29). The guard
  removes every reader's val/test books from what they can accept.
- **Measuring loop accuracy on the grown history.** Clean hit must use the *original* train history and val set.
  Otherwise accepted books vanish from the relevant set, and the score changes for a bookkeeping reason.
- **Reading the loop as a prediction about real people.** It is stylized: readers take what they are shown with a
  fixed probability. It shows the *mechanism* of concentration, not its real-world size.
- **Preaching instead of measuring.** Every claim in this unit comes with a number on our data. Hold the
  discussion to that standard.

## Discussion prompts

- The hybrid is the most accurate path *and* among the most concentrated. If you ran a bookshop's recommender,
  which point on the trade-off curve would you choose, and who should decide that?
- What would change if authors, not readers, were the ones you had to be fair to? Would the author Gini be the
  right measure? (Look at the catalog-share context.)
- Our loop assumes readers take what they are shown 30% of the time. How would a pickier or a more trusting
  audience change the concentration?
- Why does the filter bubble partly *rebound* here? Would it in a real system with new books arriving?
- Offline metrics reward predicting what an old system already showed people. How could a team learn whether an
  unshown tail book would have been liked?

## Provenance

Original content.
Exposure inequality (the Gini coefficient), popularity bias, feedback loops and filter bubbles are standard topics
in the recommender-systems and fairness literature. Examples include work on popularity bias in recommendation and
simulation studies of feedback loops. They are named here for an advanced audience; no material is adapted from a
single source.
All numbers are measured on the course's own seeded synthetic data.

## Differentiation

- **Support:** give the Gini formula and the one-round loop skeleton as starter snippets, so the sittings stay on
  the *ideas* (concentration, trade-offs, the leakage guard). Pair-program the loop round by hand.
- **Core:**
  - the whole-system scoreboard;
  - the Gini by hand and with the helper;
  - author exposure with catalog share;
  - the penalty curve;
  - a short feedback loop with the guard;
  - genre spread;
  - the head/tail and cold readouts.
- **Stretch:**
  - a different mitigation (for example, a genre-calibrated re-rank) compared with the exploration slot;
  - a reader-group fairness slice (heavy vs light readers);
  - a longer loop.
  Ask strong students to predict *before* running it whether the exploration slot will cost accuracy at round 0
  (measured: essentially none), and why.
