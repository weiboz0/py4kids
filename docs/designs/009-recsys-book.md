# Design 009 — "Applied Python: Recommendation Systems" (a new advanced book)

**Status:** DRAFT — v1 (2026-09-29). Proposes a new, self-contained book `recsys` for an advanced audience.
Establishes the book's own audience baseline (it does NOT inherit design 000's middle-school laws), its two-part
structure, the dual concept∥project pedagogy, the multi-path retrieve-then-rank project architecture, the data
strategy over the local `books` PostgreSQL catalog, the tooling/library policy, and how the book plugs into the
`books.yaml` registry and `scripts/ci-local.sh`.
Plans for this book live under `docs/plans/recsys/` (namespaced, to avoid plan-number collisions with parallel work).

## 1. Why

Recommendation systems are the most visible applied-ML systems students already use every day
(what to read, watch, buy, listen to).
They are an ideal vehicle for a rigorous applied course because a single, motivating project — "build a book
recommender" — naturally demands the full modern stack: text representation, similarity, matrix factorization,
learned embeddings, approximate nearest-neighbor retrieval, and ranking.
No existing py4kids book targets this: the fundamentals books (`python-projects`, `python-concepts`) are
middle-school, library-free, and math-light; `usaco-bronze` is contest algorithms.
This book fills the advanced-applied gap.

## 2. Audience & prerequisites (a NEW baseline — this book departs from design 000 §2)

- **Audience:** high-school / university-ready students.
- **Assumed math:** calculus A/B/C and linear algebra
  (vectors, matrices, dot products, norms, gradients, partial derivatives).
  This is the explicit, deliberate departure from design 000's "typical middle-school math" baseline.
- **Assumed programming:** Python fluency.
  The book `depends_on: [python-projects]` for the concept baseline, but it does not re-teach Python syntax.
- **Consequence for verification:** reviewers hold this book to the baseline stated HERE, not to design 000's
  middle-school self-containedness laws.
  In particular, this book MAY use external libraries (see §7) and MAY assume calculus/linear-algebra fluency
  without teaching it.
  Prereq closure still applies *within the book's own concept graph* (nothing used before it is introduced,
  except an already-assumed baseline concept).

## 3. Book identity & registry

- **id / root / folder:** `recsys` (matches the `docs/plans/recsys/` namespace).
- **title:** "Applied Python: Recommendation Systems".
- **subtitle:** "Build a book recommender — from counting to neural retrieval".
- **depends_on:** `[python-projects]` (Python concept baseline, referenced by bare concept id per design 008 §3).
- **flags:** none of `patterns` / `judge` / `publication` initially
  (so schema v1: `map_version: 1`, `blueprint_version: 1`; no borrowed-tools machinery, no contest judge,
  no publication pipeline).
- **lesson_budget:** generous — the length constraint was lifted; a two-part book of ~14 units.
  (Exact budget set when the registry entry lands.)
- Registration is a `books.yaml` entry (id == root == folder) plus the standard book skeleton;
  `scripts/ci-local.sh` picks it up automatically once registered (design 008; survey of `tools/books.py`).

## 4. Pedagogical model — two tracks, side by side, one growing system

Every unit runs **two lanes that advance together**:

- **Concept track** (`lesson.ipynb` / `exercises.ipynb` / `solutions.ipynb`):
  derive the math, implement the mechanism **from scratch in numpy**, then **reveal the mature library** doing the
  same thing (scikit-learn / surprise / PyTorch / FAISS).
  The from-scratch pass earns the math; the library pass shows the professional tool.
- **Project track** (a cumulative build under `projects/`):
  apply that unit's technique to grow **one real book recommender**.
  By the capstone the theory is taught rigorously AND a working system exists.

The project is not a toy: it is built on a **real bibliographic catalog** (§6) and follows the **production
retrieve-then-rank architecture** (§5), so students finish having built the kind of system real companies run.

## 5. Project architecture — multi-path retrieval → blend → rank

Introduced in Unit 1 as the project's north star; every later unit contributes a piece:

```
        user / query + context
                 │
   ┌─────────────┴──── candidate generation: parallel retrieval paths ─────────────┐
   │  popularity/trending   lexical/BM25   content-similarity   item-item co-occ.    │  (Part 1 paths)
   │  semantic text (GloVe) two-tower behavioral embeddings   session/sequence       │  (Part 2 paths)
   └─────────────┬──────────────────────────────────────────────────────────────┘
          merge / dedup / blend  (union candidates + per-path scores)
                 │
          ranking  (learned reranker over the merged pool + features)
                 │
          top-N recommendations
```

A small **`RetrievalPath` interface** (given a query/user + context → scored candidate items) is the software
backbone: every technique becomes a pluggable path in a registry.
This teaches sound design (polymorphism, a path registry, ablation, blending) alongside the ML, and makes the
"add a new retrieval path per unit" progression literal.
The blend layer unions and de-duplicates candidates and combines per-path scores;
the rank layer scores the merged pool (a simple weighted blend in Part 1, a learned reranker in Part 2).

## 6. Data strategy

- **Real catalog:** the local PostgreSQL database `books` (~100M rows: `isbn`/`isbn13`, `title`, `authors[]`,
  `subjects[]`, `language`, `date_published`, `pages`, `publisher`; plus `authors`/`subjects` tables with
  `book_count` popularity signals).
  A committed **slice script** deterministically carves a manageable, clean, subject-rich subset
  (e.g., English, `array_length(subjects,1) >= k`, sane page counts), plus the related authors/subjects.
  Notebooks read the **committed slice artifact** (CSV/parquet), NOT the live 100M-row DB —
  so the book is portable, CI-runnable, and reproducible without the database present.
  The live DB is the source of truth; the slice script + artifact are what ship.
- **Interactions:** the catalog has **no ratings / no per-user data**.
  A **seeded synthetic reader×book interaction generator with known latent structure** provides collaborative /
  matrix-factorization / two-tower training data.
  Known ground-truth latent factors let students *verify* their models recover the truth — a teaching feature,
  not a compromise.
- **Semantic embeddings:** the local **GloVe** vectors (`glove-wiki-gigaword-100`), offline and reproducible.
  (Optional `sentence-transformers` — better semantic quality but a one-time model download — is a documented
  opt-in, not the default.)
- **Provenance & privacy:** this book takes a deliberate, documented exception to design 000 §3
  ("datasets from seeded generation scripts, never opaque blobs"):
  the catalog is a *real* source, but only a small **reproducible slice** (script + artifact) is committed, which
  preserves the norm's spirit (inspectable, regenerable, not an opaque blob).
  No personal data is committed: synthetic readers carry no PII, and the bibliographic slice contains no user data.
  The `books` DB's own origin/license is to be confirmed with the author and recorded here before first merge.

## 7. Tooling & reproducibility

- **Concept track:** **numpy** to derive core mechanics (cosine/BM25 scoring, MF by gradient descent, a tiny
  two-tower's forward/backward, the contrastive-loss gradient) → then the mature library.
- **Libraries (isolated to THIS book; the fundamentals books stay library-free):**
  `numpy`, `pandas`, `matplotlib`; `scikit-learn` and `surprise`/`implicit` for the Part-1 "reveal";
  **PyTorch** for the Part-2 neural models; **FAISS** (or `hnswlib`) for approximate nearest-neighbor retrieval;
  `gensim`/GloVe for content embeddings; `psycopg`/`sqlalchemy` used ONLY in the slice script.
- **Reproducibility:** every model is kept **small enough to train deterministically on CPU in minutes**
  with fixed seeds — notebooks and CI run with no GPU.
  Solutions notebooks run top-to-bottom clean with fixed seeds (design 000 §3 convention, retained).

## 8. Structure — two parts, ~14 units (dual-track throughout)

### Part 1 — Foundational Recommenders

| # | Concept track (numpy → library) | Contributes to the project |
|---|---|---|
| 1 | The recsys problem; catalog data; the retrieve-then-rank architecture; the `RetrievalPath` interface | System skeleton (paths + blend + rank stubs); search/filter |
| 2 | Popularity & baselines; Bayesian / weighted averages | **Path: popularity/trending** |
| 3 | Lexical retrieval: bag-of-words, **TF-IDF**, **BM25**; cosine/BM25 scoring | **Path: lexical (BM25)** + **Path: content-similarity** |
| 4 | Neighborhood collaborative filtering: user/item **k-NN**; implicit vs explicit | **Path: item-item co-occurrence** |
| 5 | **Matrix factorization**: latent factors, SVD, gradient descent + regularization (the embedding bridge) | **Path: latent-factor** |
| 6 | Evaluation: train/test, **RMSE, precision@k / recall@k, NDCG**, cold-start | **Blend v1** + classical ranker; per-path contribution measured; the **Part-1 recommender** assembled |

### Part 2 — Neural Recommenders

| # | Concept track (numpy → PyTorch/FAISS) | Contributes to the project |
|---|---|---|
| 7 | Factors → **learned embeddings**; content embeddings (GloVe); brute-force embedding retrieval | **Path: semantic text embeddings** |
| 8 | **Two-tower / dual encoders**: query & item towers, shared space (tiny case in numpy → PyTorch) | **Path: two-tower behavioral embeddings** |
| 9 | **Training embeddings**: contrastive loss, **negative sampling / sampled softmax**, gradients; hard negatives | Strengthens the two-tower path |
| 10 | **Approximate nearest-neighbor retrieval**: exact vs ANN, recall/speed trade-off; **FAISS/HNSW**; **hybrid sparse (BM25) + dense** | Shared retrieval infra; scales all embedding paths; hybrid retrieval |
| 11 | **Neural ranking**: candidate generation → learned reranker; features | **Learned reranker + learned path blending** over the merged pool |
| 12 | **Sequence-aware** recommenders: self-attention, SASRec-style over reading history | **Path: session/sequence** |
| 13 | Evaluating the full system: per-path **ablations**, diversity, cold-start via content, neural vs classical | System-wide evaluation |
| 14 | Capstone | The complete **multi-path retrieval + blend + neural rerank** recommender, served and benchmarked against the Part-1 classical build |

BM25 is introduced in Part 1 (Unit 3) as the lexical retrieval path and revisited in Part 2 (Unit 10) as the
sparse half of hybrid sparse+dense retrieval.

## 9. Verification — how it plugs into `scripts/ci-local.sh`

`ci-local.sh` is book-agnostic and per-book routed (design 008; survey of the script).
For `recsys` (no flags), the applicable checks are the base family:
book/structure validation, manifest validation, prereq closure (within the book's own concept graph + the
`python-projects` dependency baseline), practice coverage, stretch-cell presence, notebook execution
(solutions run clean with fixed seeds), student-notebook hygiene (exercises carry no solutions/outputs), and the
PDF build.
Flag-gated families (`patterns` technique-spiral / markdown-scan, `judge` contest harness, `publication` pipeline)
do NOT apply.
A concern to resolve during implementation: notebook-execution checks must tolerate this book's heavier
dependencies (PyTorch/FAISS) and keep within a sane CPU time budget;
if the standard exec check is too strict on runtime, the plan will define how (small models, fixed seeds, a
capped slice) rather than weakening the gate.

## 10. Governance & relationship to design 000

- Design 000 remains the master repo/process design.
  This book is an **advanced-track exception** to design 000's middle-school audience baseline;
  design 000 §2 gets a one-line pointer noting the advanced `recsys` book sets its own baseline (a small,
  reviewable amendment, not a governance-file change).
- Plans live under **`docs/plans/recsys/`** (namespaced for parallel-agent collision safety).
- The lifecycle is the standard gated one (design 000 §5): this design → plan-review gate → per-unit plans →
  `ci-local.sh` → content-review gate → PR → `pre-merge-guard.sh --pr` → squash-merge.
  Note: the review gate is currently 3-way ([self]/[sol]/[fable]); [glm] is skipped per the author's 2026-09-28
  decision.
- Namespace safety: book id `recsys` is unused; plan numbers `092`/`093` and book ids `acsl`/`usaco-silver` are
  reserved for a separate contest-book split and are avoided here.

## 11. Out of scope (for now)

- A live serving API / web front-end (the capstone "serves" via a notebook/CLI query interface, not a deployed
  service).
- GPU training (everything is CPU-deterministic).
- Real per-user data of any kind (interactions are synthetic; no real ratings enter the repo).
- Distributed / big-data infrastructure (the committed slice is notebook-scale).

## 12. Open questions

- Confirm the `books` DB origin/license before first merge (record in §6).
- Final slice parameters (target row counts for books and synthetic readers) — set in the Part-1 Unit-1 plan.
- Whether the neural units may opt into `sentence-transformers` (network download) or stay GloVe-only.

## Design Review

Design-review gate on this doc. Roster: `[self]` (inline), `[sol]` (codex `--model gpt-6-sol`, read-only),
`[fable]` (Fable 5, read-only). `[glm]` is skipped by standing user decision (2026-09-28, "Skip GLM until further
notice"; recorded in plan 091). Consensus target: all active reviewers APPROVE / APPROVE WITH NITS, no open blockers.

### Review 1 — [self] (2026-09-29)
- **Verdict:** APPROVE WITH NITS
The two-part arc, dual-track pedagogy, and multi-path retrieve-then-rank architecture are coherent and genuinely
production-shaped; the data strategy and audience carve-out are sound. Design-level items to resolve (mostly in the
per-unit plans, a couple in this doc):
1. `[OPEN]` Should Fix (§7/§9) — **CPU-deterministic feasibility guardrail is under-specified.** "Small enough to
   train in minutes on CPU with fixed seeds" is asserted but not bounded. PyTorch determinism needs explicit setup
   (seed + `torch.use_deterministic_algorithms`); FAISS determinism means the graded path uses an exact index
   (`IndexFlat`), not approximate HNSW; heavy-training cells may need a cached-artifact + `no-exec` pattern so the
   exec gate stays in budget. The design should state these guardrails, not just defer them.
2. `[OPEN]` Should Fix (§8 U12) — **the self-attention / SASRec sequence unit is the least CPU-friendly.** Training
   even a tiny transformer deterministically in minutes is the shakiest claim; consider scoping U12 explicitly as a
   small "taste" with a capped model + short sequences, or note it may become a conceptual + tiny-demo unit.
3. `[OPEN]` Should Fix (§7) — **dependency weight vs. the shared environment.** PyTorch + FAISS are heavy in an
   otherwise library-light repo; they load into the shared `uv` env and slow every book's CI. The design says
   libraries are "isolated to this book" pedagogically, but the ENVIRONMENT is shared. Decide whether they go in an
   optional extras group and how `ci-local` handles a book whose exec needs them.
4. `[OPEN]` Should Fix (§5/§8 U1) — **the `RetrievalPath` interface must be forward-designed for Part 2.** If U1's
   interface is shaped only around classical paths, the neural/ANN paths in Part 2 will force a redesign. State that
   U1 designs the interface with embedding/ANN paths in mind.
5. `[OPEN]` Should Fix (§6/§12) — **the `books` DB origin/license is a merge blocker, not just an open question.**
   Committing a slice to a PUBLIC repo requires a known-permissive license; resolve before the first content merge.
6. `[OPEN]` Nice to Have (§8) — **add an explicit recommender-ethics beat** (filter bubbles, feedback loops,
   popularity bias) — appropriate and valuable for this audience; currently only diversity-in-ablation is mentioned.

### Review 2 — [sol] (2026-09-29)
_(pending)_

### Review 3 — [fable] (2026-09-29)
_(pending)_

## 13. Revision history

- **v1 (2026-09-29):** created. Two-part book (Foundational / Neural Recommenders), dual concept∥project tracks,
  multi-path retrieve-then-rank project over the real `books` catalog slice + synthetic interactions, numpy→library
  tooling with PyTorch/FAISS, advanced-audience baseline, plans namespaced under `docs/plans/recsys/`.
