# Teacher notes — Unit 14: The full system

Thirteen units built thirteen pieces. This unit puts them together into one recommender and asks the question a real
team has to answer: **what does each stage actually buy, and at what cost?**
It is the integration unit before the capstone. It introduces no new concepts. Instead it **uses** the heavy pieces
from Units 9–12 inside one pipeline:
- the two-tower served through an HNSW index;
- the feature tower for cold books (and its hard-negative variant);
- a learned reranker over the full candidate pool;
- the self-attention sequence model on the session log.

Everything is measured on the main log's val split, except the sequence path, which is scored on the session log.
The sealed test split stays sealed; it was opened once at each checkpoint.

**Fitted models come from a cache.** The expensive models are fitted once per CI run by a seeded script
(`recsys/projects/bookrec/scripts/build_models.py`) and loaded by the notebooks. A required test regenerates and
checks them.
- The lesson fits MF, the two-tower and the HNSW index **on screen**, and shows that the cached versions are the
  same models.
- The feature tower, the rerankers and SASRec are loaded with their training curves. Students already fitted those
  in Units 9, 11 and 12.
- If a student asks "isn't loading a cache cheating?", the answer is no: the cache is rebuilt from the same seeded
  code on every CI run, and a test checks it against independently measured numbers.

The unit's honest result (committed seed, val, k = 10, 500 readers):

| System | hit@10 | coverage | What it shows |
|---|---|---|---|
| Part-1 build (U6 blend) | 0.306 | 0.333 | the widest reach of any system |
| U10 hybrid (best single path) | 0.362 | 0.192 | |
| Fixed 8-path blend (two-tower via HNSW) | 0.362 | 0.206 | ties the hybrid's hit, reaches a little further |
| Full stack: 8-path pool + learned reranker | **0.356** | 0.203 | the reranker *dilutes*, as in U11 |
| Dense-heavy weights | 0.376 | 0.184 | buys hit with reach |
| Content-only reranker | 0.384 | 0.137 | the book's best hit, and its most concentrated system (head-share 0.96) |

**No system dominates.** More machinery did not automatically win. The best-hit systems are the narrowest, and the
widest is the oldest. The deliverable here, and in the capstone, is the **hit ↔ reach ↔ exposure frontier** and a
defended choice on it.

## Goals

By the end of this unit students can:

- Assemble a **multi-stage recommender**: several retrieval paths, then a calibrated blend into a candidate pool,
  then a learned reranker. Explain what each stage is for.
- Serve a dense path through an **approximate nearest-neighbour index (HNSW)**. Check its recall against exact
  search (about 0.999 here), and explain why ANN is a speed tool, not an accuracy tool.
- Use the **feature tower** to serve cold books, and read the **hard-negative** trade: harder negatives raise
  cold-item coverage but cost warm accuracy (warm 0.298 → 0.172; cold coverage 0.138 → 0.226).
- Train a **learning-to-rank** model over **ranking features** from the full pool, and explain why it does not beat
  the fixed blend here.
- Read the **self-attention** sequence model's result on the session log, and say why its numbers are not
  comparable to the main log.
- Build and read an **ablation table** and a **beyond-accuracy table**, and compare the full system with the Part-1
  build.

## Pacing

The unit opens with its **project hook**: *"You have built twelve kinds of recommender. Now build one system, and
decide what earns its place."*
Plan **60–90 minutes across two to three sittings**, and assign all exercises.
The lesson fits MF and the two-tower on screen (about 35 s); everything else loads in under a second.

1. **Sitting 1 (~30 min) — assembly.** The paths, served through the cache (MF, the two-tower and HNSW fitted on
   screen); the 8-path blend; the HNSW recall check; the feature tower for cold books.
2. **Sitting 2 (~30 min) — the learned stage.** The reranker over the full pool, and the honest result (0.356 <
   0.362). The sequence path on the session log.
3. **Sitting 3 (~25 min, plus Challenges) — what earns its place.** The ablation table, the beyond-accuracy table,
   the frontier, and the bridge to the capstone.

## Common mistakes

- **"More stages means better."** The full stack with a learned reranker scores *below* the fixed blend. Every
  stage has to earn its place with a measurement.
- **Reading the ablation baseline wrong.** Stage rows compare with the full stack. Path rows are leave-one-out of
  the **fixed** blend, not of the reranked stack. Under the reranker, the same path removals can change sign (for
  example, dropping popularity *helps* the fixed blend but *hurts* the reranked stack).
- **Treating ANN as an accuracy improvement.** HNSW reproduces exact search's results almost perfectly (recall
  about 0.999). Its value is speed at large catalogs, not hit.
- **Comparing session-log numbers with main-log numbers.** The sequence path runs on a different reader population.
- **Quoting only hit@10.** The most accurate systems here are also the most concentrated. Always put coverage,
  head-share and the exposure Gini next to hit.
- **Thinking the cache hides the work.** The cached models are rebuilt from seeded code every CI run and checked by
  a required test. Fitting on screen once is enough to see that they are the same models.

## Discussion prompts

- If you ran a library's recommender, where on the frontier would you put it: the Part-1 build's reach, the
  hybrid's accuracy, or the content reranker's precision? Who should make that choice?
- The learned reranker underperformed the fixed blend twice now (U11 and here). When *would* you expect a learned
  ranker to win?
- Cold books only reach readers through content paths and the feature tower. What does that mean for a new
  author's first book?
- Which stage would you remove first to save cost, and what would the ablation table tell you about the price?

## Provenance

Original content.
The multi-stage retrieve-blend-rerank architecture is standard industry practice. HNSW is from Malkov and
Yashunin (2018) and SASRec from Kang and McAuley (2018). They are named for an advanced audience; no material is
adapted from a single source.
All numbers are measured on the course's own seeded synthetic data.

## Differentiation

- **Support:** give the pool-assembly and readout helpers as starter code, so the sittings stay on *what each stage
  buys*. Pair-program the ablation table.
- **Core:**
  - the HNSW efSearch/M sweep (recall vs time; Exercise 1);
  - the feature tower's cold slice (Exercise 2) and the hard-negative trade (Exercise 3);
  - a reranker feature-family refit on the cached training matrix (Exercise 4);
  - the SASRec readout (Exercise 5);
  - the ablation and beyond-accuracy tables and the frontier (Exercises 6–7).
- **Stretch:**
  - your own weighting of the 8-path blend, placed on the frontier (Exercise 8);
  - the `log_pop` ablation of the reranker (Exercise 9).
  Ask strong students to predict, *before* running it, whether adding the learned reranker will raise hit, and why.
