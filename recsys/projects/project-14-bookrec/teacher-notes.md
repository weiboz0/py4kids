# Teacher notes — Capstone: Your book recommender (`project-14-bookrec`)

The capstone closes Book 3.
Each student builds **their own** recommender from the pieces assembled in Unit 14, measures it on accuracy, reach
and exposure, and defends one choice on the **hit ↔ reach ↔ exposure frontier** in a short design memo.
It introduces no new concepts and uses no borrowed tools: every call in the brief was taught in Units 2–14.

**The thesis is the frontier, not "the full stack wins".**
On this data the most machinery does not win.
Students who expect the learned reranker to top the table will find it below the fixed blend, as in Unit 11.
That is the lesson, not a bug, and the rubric rewards students who report it honestly.

Reference numbers (committed seed, main-log val, k = 10, 500 readers; the solution's measurements):

| System | hit@10 | coverage | head-share | exposure Gini | zero-train books shown |
|---|---|---|---|---|---|
| Part-1 build (Unit 6 blend) | 0.306 | 0.333 | 0.793 | 0.908 | 4 |
| Best single path (U10 hybrid, exact two-tower) | 0.362 | 0.192 | 0.862 | 0.922 | 17 |
| Fixed 8-path blend (two-tower via HNSW) | 0.362 | 0.206 | 0.846 | 0.923 | 23 |
| Full stack: 8-path pool + learned reranker | 0.356 | 0.203 | 0.847 | 0.913 | **0** |
| Dense-heavy weights (Unit 14 reference) | 0.376 | 0.184 | 0.885 | — | — |
| Content-only reranker (Unit 14 reference) | 0.384 | 0.137 | 0.960 | — | — |

Single paths alone (Milestone 1; one-path blends, pool 50):

| Path | hit@10 | coverage | zero-train books shown |
|---|---|---|---|
| popularity | 0.108 | 0.008 | 0 |
| lexical | 0.158 | 0.278 | 128 |
| item-item | 0.252 | 0.490 | 0 |
| MF | 0.276 | 0.074 | 0 |
| semantic | 0.102 | 0.354 | 263 |
| two-tower (HNSW) | 0.340 | 0.177 | 0 |
| feature tower | 0.298 | 0.306 | 109 |
| hybrid (HNSW) | 0.360 | 0.192 | 17 |

818 of the 2,000 books have no train positive.
The full stack shows **none** of them: the reranker learned from warm reading histories and pushes every cold book
out of the top 10.
The fixed blend keeps 23.
This is the cold-start finding most students will not expect, and the memo should name it.

An example student blend, for calibration only: an equal-weight blend of item-item, MF, two-tower, feature tower,
semantic and hybrid scores about 0.370 / 0.198 and shows 10 zero-train books.
It beats the 8-path blend on hit and loses on reach.
That is a trade, not a win, and a strong memo says so.

The whole solution runs in under a minute on the cache.
The cache must be built first (`uv run --group recsys python recsys/projects/bookrec/scripts/build_models.py`,
about 5 minutes); CI builds it on every run.

## Goals

By the end of the capstone students can:

- **Choose retrieval paths with evidence:** score each path alone and justify each choice by hit, by reach, or by
  cold-book service.
- **Build and tune a calibrated blend** over a candidate pool, and compare it with the 8-path reference.
- **Measure a learned reranker as a stage** and decide, from their own numbers, whether it earns its place.
- **Build an ablation table** where every row names its baseline, and read the reference 10-row table.
- **Build a beyond-accuracy table** (coverage, head-share, exposure Gini, novelty, diversity) with the Part-1 build
  as the benchmark.
- **Write a design memo** that defends a point on the frontier, covering accuracy vs reach, exposure, cold start
  and cost, with every claim tied to a measured number.

## Pacing

Three lessons of 60–90 minutes, run as **build → measure → defend**.
The project hook opens lesson 1: *the library wants ten suggestions per reader on its front page, one system, with
a reason behind every piece.*
Check before lesson 1 that every machine has built the model cache; a missing cache fails the setup cell with the
build command.

- **Lesson 1 — build (Milestones 1–2).**
  10 min: the hook; recall the Unit 14 frontier table and ask "which system would you ship?" before anyone computes.
  30 min: Milestone 1, scoring all eight paths alone and choosing at least three with a reason each.
  30 min: Milestone 2, the blend and at least one weight change, compared with the 8-path blend.
  Minimum bar by the end of lesson 1: a scored blend of three or more paths.
- **Lesson 2 — measure (Milestones 3–5).**
  20 min: Milestone 3, the reranker as a stage, and the keep-or-drop decision.
  25 min: Milestone 4, the student's own leave-one-out ablation plus the reference table.
  25 min: Milestone 5, the beyond-accuracy table with the Part-1 build.
- **Lesson 3 — defend (Milestone 6 and showcase).**
  30 min: the design memo.
  15 min: `## Make it yours` for students who finish early.
  30 min: showcase. Each student states their frontier choice in one sentence and shows the one number that
  justifies it; the class challenges with a system that beats theirs on some column.

## Common mistakes

- **Ranking systems by hit@10 alone.** The highest-hit systems here are the narrowest. A memo that never cites
  coverage, head-share or the Gini has not done the capstone.
- **Expecting the reranker to win, and hiding that it did not.** The full stack scores 0.356, below the fixed
  blend's 0.362. Students who "fix" this by not reporting it lose credit; students who explain it gain credit.
- **Ablation deltas with no baseline.** A row that says "−0.008" without saying "compared with what" cannot be read.
  The student's path rows compare with *their* blend; the reranker stage row compares the full stack with the 8-path
  fixed blend; the reference table's two families have different baselines.
- **Changing weights in the ablation.** Leave-one-out must keep the other weights fixed, or the row measures two
  changes at once.
- **Comparing session-log numbers with main-log numbers.** Only relevant if a student takes the SASRec extension;
  the session log has a different reader population.
- **Reading the sealed final split.** Everything is val. A student who scores on the sealed split has broken the
  book's evaluation protocol; send them back to val and discuss why the split was sealed.
- **Overclaiming small differences.** Many ablation deltas are ±0.002–0.010 on 500 readers, about one to five
  readers. Students should call these "small" rather than build a story on them.

## Discussion prompts

- The full stack shows no zero-train books at all. Who is harmed by that, and would you accept 0.006 more hit for it?
- The Part-1 build reaches a third of the catalog; nothing newer comes close. Why might a library prefer it, and
  why might it not?
- Dropping popularity from the fixed blend *raises* hit. Why could a path that is "in every recommender" hurt here?
- If the reranker cost nothing to run, would you keep it? What does the cache's build-time record say it costs?
- Who should choose the point on the frontier: the engineers, the librarians, the readers, or the authors?

## Differentiation

- **Support:** pair students for Milestones 1 and 4, which are loop-shaped and benefit from talking through the
  baseline. Give the `show(...)` print pattern as a model for every table. A three-path blend with an honest memo
  is a complete, celebrated result at the Developing level.
- **Core:** the six milestones as written, with at least three paths and one weight change.
- **Stretch:** the `## Make it yours` extensions: a weight sweep listing dominated settings, an explicit
  cold-book weighting with its hit cost, the SASRec readout on the session log, or a reranker feature-family refit
  on the cached training matrix. Ask strong students to predict each result *before* running it and to record
  whether they were right.

## Rubric

Assess each student's **own** system. There is no single correct answer: different path choices and weights land
on different points of the frontier, and any point is acceptable if it is measured and defended.
Judge the evidence and the reasoning, not a match to the reference numbers.

**Meets the brief (full credit):**
- All eight paths scored alone with hit, coverage and cold-book count; at least three chosen, each with a reason
  that cites a measured number.
- A calibrated blend of the chosen paths with stated weights, scored and compared with the 8-path fixed blend on
  hit **and** coverage, with at least one weight change reported.
- The learned reranker scored, its training record read from the cache, and a keep-or-drop decision consistent
  with the student's own numbers.
- An ablation table with one leave-one-out row per chosen path and the reranker stage row, every delta computed
  against a named baseline; the reference table printed and read.
- A beyond-accuracy table with the student's system, the full stack, the best single path and the Part-1 build, all
  six columns.
- A design memo answering frontier choice, accuracy vs reach, cold start, cost and next step, each answer citing
  the student's own numbers, and naming at least one system that beats theirs on some column.
- Every number on val; the notebook runs top to bottom.

**Developing (a valid result, below the full bar):**
- A scored blend of three or more paths, the reranker comparison, and a memo that defends the choice with numbers,
  but with an incomplete ablation or beyond-accuracy table. Name the missing table as the next step.

**Milestone by milestone, "what done looks like":**
1. **Paths:** eight rows; reasons say *which* axis earned each path its place (hit, reach or cold books).
2. **Blend:** the student's blend next to the 8-path blend on both hit and coverage; one weight change and its effect.
3. **Reranker:** first and last training loss, 21 features, the full stack's hit, coverage and cold-book count
   (about 0.356 / 0.203 / 0), and a decision that follows from them.
4. **Ablation:** each row's baseline named; signs read correctly; small deltas called small.
5. **Beyond accuracy:** four rows, six columns; the Part-1 comparison stated on hit, reach and exposure.
6. **Memo:** a defended frontier point; cold start and cost addressed with numbers.

**Stretch (recognise, do not require):** a weight sweep with dominated settings identified; a cold-book weighting
with its measured hit cost; the SASRec session-log readout correctly kept separate; a reranker feature-family refit.

**Re-teach signal:** if a third of the class or more ranks systems by hit@10 alone, or presents ablation deltas
without baselines, revisit the Unit 6 and Unit 13 beyond-accuracy readouts before the end-of-course review. Those
are the two habits the whole book was built to teach.

## Provenance

Original content.
All numbers are measured on the course's own seeded synthetic data and the regenerated model cache.
