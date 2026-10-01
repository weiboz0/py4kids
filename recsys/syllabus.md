# Applied Python: Recommendation Systems

*Build a book recommender — from counting to neural retrieval.*

This is an advanced, applied book.
It assumes Python fluency (the ground covered in *Python by Projects*),
comfort with numerical Python (NumPy arrays and broadcasting, basic pandas),
and high-school / university-ready mathematics:
linear algebra, single-variable calculus, and probability and statistics.
Those assumptions are declared in `curriculum/baseline.yaml`;
everything the book itself teaches is still introduced before it is used
and practiced before it is assessed.

## The through-line

One project runs the length of the book: **build a book recommender.**
Every unit contributes a working piece to a single, growing system,
organised around one architecture — **retrieve then rank.**
Parallel *retrieval paths* each propose candidate books;
their scores are calibrated, merged, and de-duplicated into one pool;
a ranker orders that pool into the final recommendations.
From the first unit there is an evaluation scoreboard —
a frozen holdout and a hit-rate@k metric —
so every addition can answer the only question that matters: *did it help?*

## Arc at a glance

| # | Entry | Kind | Lessons | The hook |
|---|-------|------|---------|----------|
| 1 | `unit-01-problem-and-scoreboard` | unit | 3 | Turn “what should I read next?” into a recommender you can measure. |

## How the book is organised

**Part 1 — Foundational Recommenders.**
The problem framing and the catalog; popularity and weighted baselines;
lexical retrieval (TF-IDF and BM25); neighbourhood collaborative filtering;
matrix factorisation as the bridge to embeddings;
and evaluation deepened (ranking metrics, coverage, diversity, cold-start),
closing with the first blended system and Checkpoint A.

**Part 2 — Neural Recommenders.**
Learned and semantic-text embeddings; matrix factorisation re-expressed as a two-tower model in PyTorch;
feature towers and item cold-start; approximate nearest-neighbour retrieval and hybrid sparse-plus-dense search;
a learned reranker; a small sequence-aware model over reading history;
and a system-wide evaluation with an ethics and beyond-accuracy thread,
closing with Checkpoint B and the capstone.

## Working method

The concept track derives each mechanism from scratch in NumPy — cosine similarity, BM25,
gradient-descent matrix factorisation, a from-scratch two-tower forward and backward pass —
and only then reveals the mature library that does it at scale.
Everything runs on CPU and is deterministic:
a single seeded generator, fixed thread counts, and tolerance-based (never exact-float) checks.
The recommender itself lives in an importable package that grows unit by unit,
so the system is one coherent build rather than scattered notebook cells.

## Data

The synthetic reader-and-book interaction log is produced by seeded generation scripts
with exposed ground-truth, never an opaque blob.
No real catalog or reader data is committed to this public repository;
the real-slice tooling is license-gated and fails closed.

*Units, projects, and checkpoints are authored in the plans that follow this foundation.*
