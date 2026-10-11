# Teacher notes — Checkpoint B: the Part-2 recommender

This checkpoint closes **Part 2** (Units 7–13).
It is the book's **second and last authorized unseal of the main-log `test` holdout**.
The student scores the Part-2 paths on `val`, reads the cold-start and ethics readouts, then builds, measures and
**freezes** one pinned Part-2 blend, and finally scores it exactly once on `test`.
It is **strict**: every task draws only on concepts taught in Units 3–13 (the manifest's `practices` list), with no
borrowed tools.
Two deliberate scope choices keep it honest and fast:

- **Cold start (Q4) needs no feature-tower fit.** It reuses the paths already fit (semantic, lexical, item-item,
  two-tower), so it assesses `item-cold-start` itself, not the Unit-9 feature-tower recipe.
- **The sequence question (Q5) runs on the session log's `val` split only.** There is no session-log `test`
  unseal; the session log's numbers are not comparable with the main log's.

The checkpoint's central lesson is uncomfortable on purpose.
The pinned Part-2 blend (equal weights over item-item, two-tower, semantic and lexical, pool 30) **loses on hit@10**
to its own two-tower member and to the Unit-10 hybrid, and **wins on catalog reach**.
A student who reports "the blend wins" has not read their own numbers.

## Measured reference values

All on the committed seed, `K = 10`, cold readers excluded (main log unless marked).
Use them to check student work; small differences across machines are rounding, not errors.

| Readout | Value |
|---|---|
| Q1 book embedding norm | 1.000 |
| Q1 semantic / lexical val hit@10 | 0.102 / 0.158 |
| Q2 two-tower BPR loss, first → last epoch | about 0.370 → 0.111 |
| Q2 two-tower val hit@10 | 0.340 |
| Q3 two-tower hit / coverage | 0.340 / 0.177 |
| Q3 hybrid (lexical + two-tower, w 0.7, pool 50) hit / coverage | 0.362 / 0.192 |
| Q4 zero-train books surfaced (of 818): semantic, lexical, item-item, two-tower | 268, 128, 0, 0 |
| Q4 cold hit@10 (97 cold-target readers): semantic, lexical, item-item, two-tower | 0.031, 0.021, 0, 0 |
| Q5 session log hit@10: bag item-item, last-3, transition, transition (shuffled) | 0.480, 0.551, 0.516, 0.333 |
| Q5 paired lifts (± paired SE): last-3 − bag; transition − shuffled | +0.071 (0.014); +0.183 (0.014) |
| Q6(a) exposure Gini: Part-2 blend vs two-tower (540 warm readers) | 0.857 vs 0.929 |
| Q6(a) long-tail share: Part-2 blend vs two-tower | 0.429 vs 0.100 |
| Q6(b) mean genre entropy: recommended vs history; share narrower | 0.81 vs 1.55 bits; 76% |
| Q6(c) item-item loop, round 0 → 3, no mitigation (cov / Gini / genre H / clean hit) | 0.490 → 0.412 / 0.773 → 0.835 / 1.64 → 1.18 / 0.252 → 0.206 |
| Q6(c) the same with the exploration slot | 0.514 → 0.455 / 0.751 → 0.812 / 1.91 → 1.53 / 0.252 → 0.216 |
| Q7 Part-2 blend val hit / coverage | 0.298 / 0.383 |
| Q7 leave-one-out hit (coverage): −item-item, −two-tower, −semantic, −lexical | 0.246 (0.320), 0.198 (0.436), 0.310 (0.365), 0.312 (0.419) |
| Q8 Checkpoint A reference (frozen Part-1 blend on `test`) | 0.306 hit / 0.338 coverage |

The Q8 `test` numbers for the Part-2 blend are deliberately not listed here.
Read them from the solutions notebook's executed run, so the number reaches the teacher through the same one-shot
path the student uses.

## Goals

Confirm the student can, unaided, evaluate the Part-2 system on more than one axis and keep the holdout honest:

- explain and use **word and document embeddings** for semantic retrieval, and say why a weaker single path can still
  earn a place (Q1);
- fit a **two-tower** model with the **BPR loss** and read its training curve without confusing it with held-out
  accuracy (Q2);
- build a **sparse + dense hybrid** from fitted paths and treat fusion as something to measure (Q3);
- measure **item cold start** and explain which kinds of path can serve a never-read book, and why (Q4);
- read **sequence-aware** paths with a paired comparison and an order-destroying control (Q5);
- measure **exposure fairness**, **filter-bubble** narrowing and a **feedback loop** with and without a mitigation,
  and explain the loop's **leakage guard** (Q6);
- build a pinned blend on `val`, run a **leave-one-path-out ablation**, describe a **hit ↔ coverage trade**, and
  **freeze** (Q7);
- perform the **one-shot `test` evaluation** of the frozen blend and interpret it against `val` and Checkpoint A
  (Q8).

## Pacing

A single assessment sitting of about **75 minutes** (up to 90 for careful short answers).
The setup cell and the two-tower fit take about 30 seconds together; the two feedback loops take about 10 seconds
each.
Everything else runs in a few seconds.
Questions 1–7 are all on `val`, and Q8 is the short, decisive unseal.
Students must not start Q8 until the `# FREEZE` cell in Q7 has run.
If time is short, Q5 (session log) can be split into a second short sitting: it does not feed the frozen blend.

## Common mistakes

- **Expecting the blend to win.** The pinned blend scores 0.298 hit@10, below the two-tower (0.340) and the hybrid
  (0.362). Dropping either content path *raises* its hit@10. What it buys is reach: coverage 0.383, about twice the
  two-tower's 0.177 and the hybrid's 0.192. Full credit needs that sentence in both directions; "the blend is best"
  or "the blend is useless" both miss the trade.
- **Freezing a different recommender than the one specified.** Some students will swap in the two-tower or drop a
  content path in Q7 because it scores higher on `val`. That is a tuning decision the checkpoint pinned on purpose,
  so the ablation and the honest comparison stay about *this* blend. The right move is to report the better single
  path, not to replace the frozen one.
- **Touching `test` before freezing.** Any `split="test"` call before the `# FREEZE` cell, a second call after it, or
  a call inside a loop or a function, breaks the checkpoint's central discipline. So does going back to Q7 after
  reading Q8. This is the error to catch first.
- **Treating one fairness metric as "the" fairness.** The exposure Gini, the long-tail share, coverage and the genre
  spread each measure one kind of inequality. The blend is less concentrated than the two-tower on Gini (0.857 vs
  0.929) and far more on long-tail share (0.43 vs 0.10), yet it still narrows most readers' genres. A complete answer
  names what each number measures and does not crown one.
- **Missing the leakage guard in the loop.** If a simulated reader may "accept" one of their own held-out books, the
  refit model is handed the answer and clean hit *rises* for the wrong reason. Students who write "the loop improves
  accuracy" have either read the table wrongly or reasoned about an unguarded loop. Here clean hit falls
  (0.252 → 0.206).
- **Fitting extra models.** Q3 and Q4 reuse fitted paths. A student who fits a second two-tower or a feature tower is
  not wrong, but loses time and should be told why reuse was the point.
- **Comparing session-log and main-log numbers.** The session log's hit@10 values (about 0.48–0.55) are on a
  different reader population. They are not "better" than the main log's.
- **Reading Q8's Gini as a new measurement.** The blend's lists depend only on train history, so its exposure Gini is
  the Q6(a) value; unsealing `test` cannot change it. A student who recomputes a "test Gini" by selecting test
  readers has added a second test touch.

## Discussion prompts

- The two-tower is more accurate; the Part-2 blend reaches twice as much of the catalog. You run a library's
  recommender. Which would you ship, and what would you want to measure next before deciding?
- The exploration slot lowered the loop's concentration but did not stop it. What would a stronger mitigation cost,
  and who pays that cost: readers, authors, or the library?
- Your recommendations are narrower in genre than most readers' own histories. Is that a filter bubble, or is it
  the recommender doing its job of focusing? What evidence would tell the two apart?
- Content paths can serve brand-new books; collaborative ones cannot. How would you design a system that lets a new
  book earn interactions without flooding readers with untested titles?
- Checkpoint A's Part-1 blend scored about 0.306 on `test`. Did Part 2's extra machinery make the *frozen*
  recommender better? If not, was Part 2 wasted?

## Differentiation

- **Support:** provide the `blend_top_k`, `cold_reach` and `paired` helpers filled in, so the assessment tests
  interpretation (trade-offs, controls, the leakage guard, test hygiene) rather than wiring. Keep Q7 and Q8 unaided.
- **Core:** Q1–Q8 unaided using the `bookrec` API, with every short answer backed by a number.
- **Extension:** before running Q8, ask the student to predict the `test` hit@10 and coverage from the frozen `val`
  numbers and to say which of the two they trust more. After Q8, ask them to explain any gap without touching `test`
  again. A second extension: argue, with the Q7 ablation, which single member you would drop *in a future checkpoint*,
  and what it would cost on coverage.

## Grading

Out of **100 points**, weighted toward honest evaluation over wiring:

- **Q1 semantic retrieval — 8.** A unit-norm book embedding; semantic and lexical val hit@10; a sound account of why
  a weaker path can still be complementary.
- **Q2 the two-tower — 10.** One seeded fit; first and last BPR loss; val hit@10 about 0.340; separates training loss
  from held-out accuracy.
- **Q3 hybrid retrieval — 10.** Built from fitted paths (no new fit); hit and coverage for the two-tower and the
  hybrid; says the lift is small and weight-sensitive, not free.
- **Q4 cold start — 10.** Correct cold reach and cold hit for all four paths; content paths serve cold books,
  warm-only collaborative paths surface exactly 0; explains *why* (keywords vs interactions).
- **Q5 sequence-aware paths — 12.** Session log, `val` only; the four paths scored on the same cohort; both paired
  differences with paired SEs; explains why the shuffled control isolates order.
- **Q6 ethics — 18.** Gini and long-tail share for the blend and the two-tower (6); genre spread vs history with the
  narrower share (4); both R = 3 loops read correctly, with exploration partly restoring exposure (4); names the
  limits of any single fairness metric and explains the leakage guard (4). Every claim needs a number; deduct for
  verdicts without measurements.
- **Q7 build, ablate and FREEZE — 16.** The pinned blend measured on `val`; signed leave-one-out over the four
  members; the hybrid reported as a separate path; the honest hit ↔ coverage reading; decisions crystallized in the
  `# FREEZE` cell with the frozen `val` numbers recorded. **Claiming the blend wins on hit@10 caps Q7 at half.**
- **Q8 one-shot `test` unseal — 16.** Exactly one top-level `split="test"` call after the freeze; test hit, coverage
  and readers; the Gini carried from Q6(a) with the reason it cannot change; an honest comparison with `val` and with
  Checkpoint A; explains why swapping in the two-tower now would be tuning on the holdout. **Any evidence of tuning
  against `test`, or of more than one `test` evaluation, caps Q8 at half and should be flagged in feedback.**

Full credit requires the honest framing throughout: the Part-2 blend is a measured trade, not a win, and every
ethics claim is a number on our data, not a verdict.
