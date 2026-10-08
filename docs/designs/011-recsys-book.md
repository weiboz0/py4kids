# Design 011 — "Applied Python: Recommendation Systems" (a new advanced book)

> Renumbered 009 → 011 on 2026-09-30: design 009 was already owned by the ACSL book (`009-acsl-book.md`, reserved
> via design 008); `010` is the publication design. This doc is design **011**.

**Status:** DRAFT — v2 (2026-09-29). Proposes a new, self-contained book `recsys` for an advanced audience.
v2 folds the round-1 design-review findings ([sol] + [fable] REJECT; [self] APPROVE WITH NITS) — see the Design
Review section and §14 revision history.
Establishes the book's own audience baseline (a precise, user-authorized carve-out — NOT a wholesale waiver of
design 000), its two-part structure, the dual concept∥project pedagogy, the multi-path retrieve-then-rank project
architecture, the data + embedding provenance contract over the local `books` PostgreSQL catalog, the reproducible
CI/determinism budget, the tooling/library policy, and the required governance amendments + tooling.
Plans for this book live under `docs/plans/recsys/` (namespaced; requires the pre-merge-guard extension in §12).

## 1. Why

Recommendation systems are the most visible applied-ML systems students already use daily.
They are an ideal vehicle for a rigorous applied course: one motivating project — "build a book recommender" —
naturally demands the full modern stack (text representation, similarity, matrix factorization, learned embeddings,
approximate nearest-neighbor retrieval, ranking).
No existing py4kids book targets this: `python-projects`/`python-concepts` are middle-school, library-free, and
math-light; `usaco-bronze` is contest algorithms.
This book fills the advanced-applied gap.

## 2. Audience & baseline (a PRECISE carve-out from design 000, not a waiver)

- **Audience:** high-school / university-ready students.
- **Assumed math:** calculus A/B/C; linear algebra (vectors, matrices, dot products, norms, gradients);
  **probability & statistics** (distributions, sampling, expectation, log/softmax); this is the deliberate
  departure from design 000's "typical middle-school math."
- **Assumed programming:** Python fluency **plus numerical-Python competence** (`numpy` arrays/broadcasting, basic
  `pandas`). Where a specific advanced Python feature is needed (e.g. `class` inheritance / protocols for the
  `RetrievalPath` registry) it is either introduced in-book or declared as an assumed-baseline concept (§4).

**What this book overrides vs. retains (normative).**
It overrides **only three** things from design 000 §2 / AGENTS.md: the *audience*, the *assumed math*, and the
*permission to use named external libraries*.
It **retains** every other law: project-first delivery, practice coverage, **taught-before-assessed**, checkpoints
(§8), student-notebook hygiene (no solutions/outputs; solutions run clean with fixed seeds), a stretch exercise per
unit, and `teacher-notes.md` per unit.
"Assumed baseline" never means "unowned": an assumed concept is declared (§4) and earns no teaching/practice credit
but is legal to use; a library API is taught-before-assessed like any concept (§4).

## 3. Book identity & registry

- **id / root / folder:** `recsys`.
- **number:** `3` (display ordinal only). Introduces a new title series **"Applied Python: …"** alongside design
  008's "Python …" / "Contest Python: …" series.
- **title:** "Applied Python: Recommendation Systems"; **subtitle:** "Build a book recommender — from counting to
  neural retrieval".
- **depends_on:** `[python-projects]` (Python concept baseline, referenced by bare id; the cross-book
  dependency/global-namespace contract is design 008 §2 D3).
- **flags:** none of `patterns` / `judge` / `publication` (schema v1: `map_version: 1`, `blueprint_version: 1`;
  no borrowed-tools machinery, no contest judge, no publication pipeline).
- **lesson_budget:** `[30, 60]` as a **whole-book total** (the registry sums each entry's `lessons` and compares the
  sum to the range; a total below the minimum FAILS unless buildout — `tools/curriculum.py` `lesson_budget_findings`).
  With 14 units at ~2–3 sittings each (~30–48 total) this fits; the first plan sizes each entry's `lessons` so the
  sum lands in range. This is NOT a per-unit budget.

## 4. Baseline & library-API tooling mechanism

`depends_on: [python-projects]` supplies only Book-1's concept ids (no inheritance/protocols, exceptions,
comprehensions, generators, `*args`, type hints, and no `numpy`/`pandas`).
The book must be able to *use* those without teaching them, and must still enforce taught-before-assessed for what
it *does* teach (including library APIs).

- **Assumed concepts:** a book-local **`curriculum/baseline.yaml`** lists assumed-baseline concept ids
  (advanced-Python + math + numerical-Python + assumed library primitives).
  Prereq-closure and coverage checks treat these as *known but uncredited* (no `introduces`, no practice
  requirement).
  This is named tooling work in the first plan (extend `tools/curriculum.py` prereq/coverage to union
  `baseline.yaml` into the "known" set for this book).
- **Library APIs are taught-before-assessed:** each library API a student must *write* is introduced before use and
  practiced if assessed; the "numpy from-scratch → reveal the library" pattern satisfies this (the mechanism is
  taught from scratch, then the library call is introduced explicitly).
  A library call the student only *consumes* via an **instructor-provided adapter** is marked as given and earns no
  credit (analogous in spirit to a borrowed tool, but implemented as an assumed/adapter concept since this book is
  schema v1).
- **Check applicability (confirmed):** `stretch-check` applies (every unit ships a stretch exercise);
  `concept-scan` applies within the book's own graph + baseline; `turtle-check`/`turtle-real-check` are inert (no
  turtle); `patterns`/`judge`/`publication` families are off (no flags).

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

**`RetrievalPath` contract (forward-designed for both parts).**
A path exposes a small, stable protocol: `fit(...)` / `load(artifact)` and
`retrieve(query_or_user, context, k) -> [(item_id, score, provenance)]`, over **stable integer item ids**, with
**deterministic tie-breaking** (id order), an explicit **candidate limit** `k`, documented **score semantics**
(each path's scores are calibrated/normalized before blending), and per-path **artifact ownership/versioning** (a
path owns its fitted artifact under the project package).
The student-facing interface is kept minimal in U1 and grows only when a later unit (embedding, ANN, session) needs
a new capability — designed from the start to admit those, so no rewrite is forced.

## 6. Data & embedding provenance contract

- **Catalog source & license (blocker gate on the U1 slice-commit, not merely an open question):**
  the committed slice must come from a **known-permissive** source.
  Default/fallback: **Open Library** dumps (public domain) for title/author/subjects/ISBN;
  if real ratings are wanted, **goodbooks-10k** (CC-licensed, includes ratings) is the fallback.
  The local `books` PostgreSQL DB (~100M rows) may be the source **only once its origin/license is confirmed
  permissive**; otherwise the slice is regenerated from the fallback.
  No slice is committed until the license is confirmed.
- **Extraction contract (so a committed artifact is reproducible from an evolving DB):** the slice script records
  source + snapshot date/version, the exact query parameters, deterministic total ordering, normalization +
  dedup rules, a schema/data-dictionary, row counts, and content **checksums**.
- **Slice format:** **gzip'd CSV** (no parquet, to avoid a `pyarrow` dependency), with a stated size ceiling
  (target ≤ a few MB).
- **Embeddings:** a **committed, checksum-pinned, slice-vocabulary-restricted GloVe subset** (derived
  deterministically from the slice vocabulary; float16 `.npy`, a few MB) with a license note.
  **Default CI requires neither the database nor any network/model download.**
  `sentence-transformers` is an explicit opt-in for local experimentation only and **must never be on the CI path**.
- **Synthetic interactions — per-unit signal spec.**
  A seeded generator produces a reader×book interaction log rich enough to drive every unit, with **exposed
  ground-truth**:

  | Signal built into the generator | Consumed by |
  |---|---|
  | low-rank latent taste factors | U5 MF, U8 two-tower |
  | taste derived from catalog features (subjects/authors/keywords) | U3/U7 content & hybrid, U9 feature towers, cold start |
  | popularity bias | U2 popularity, exposure-bias discussion (U13) |
  | **separate session log** (`sessions.csv.gz` + `series.csv.gz`, amended v5): forced next-volume exposure, decaying author-follow, persistent genre mood, longer histories | U12 sequence model |
  | implicit positives + a defined exposure/observation process + sampled negatives | U4, U8–U9 training |
  | held-out cold items & cold readers; leakage-safe temporal train/val/test splits | U6 eval, U9, U13 |

  **Taste-aware exposure (amended 2026-10-03, recsys-004).** The observation process is NOT popularity-only: a reader
  is exposed to item `i` with probability ∝ `popularity(i)^α · exp(β · z_u(affinity(reader, i)))`, where `affinity`
  combines the latent taste dot-product and a **genre** content term, and `z_u` is per-reader standardisation of
  affinity (so `β` is scale-free). The per-book **keywords** are a *latent-correlated observable* (generated from the
  book's latent factors + genres), consumed by the lexical/content retrieval paths (U3/U7) — they are NOT an input to
  the exposure affinity (keeping content retrieval strictly below collaborative/latent on the scoreboard). Positives arise among exposed items; author-following recurs
  across sessions. **Design invariant:** popularity remains a strong baseline, but content (U3), collaborative (U4),
  and latent (U5) signals are each **recoverable** and beat popularity on the `val` scoreboard — enforced by a
  committed **recoverability harness** (per-technique ratio+margin gates against the analytic random floor). A pure
  positive-RATE estimate stays weak (preserving U2's popularity-bias lesson), because taste is driven by latent
  affinity, not by per-item rate. The earlier popularity-only exposure made even a true-affinity oracle ≈ the random
  floor, so no personalization unit could demonstrate value — this amendment fixes that.
  **Catalog keyword text.** Alongside the 5-column catalog CSV, the generator emits a separate, gitignored per-book
  **keyword artifact** (`keywords.csv.gz`): variable-length real-English-word token bags (repetition + length
  variation, so TF-IDF/BM25 `k1`/`b` are meaningful) drawn from a committed topic vocabulary conditioned on each
  book's latent factors + genres. This is the slice vocabulary the **U7 GloVe subset** derives from, and the
  document corpus the **U3 lexical** path scores.

  Because latent factors are **not identifiable** (rotations give equivalent predictions), students verify
  **recovered scores / rankings / latent subspaces**, not literal factor coordinates.
  No PII: readers are synthetic.
  **First-plan deliverables:** the slice script AND the synthetic generator ship in `recsys-001` (U1's scoreboard
  needs interactions); **the taste-aware exposure + keyword artifact + recoverability harness land in `recsys-004`**;
  the committed GloVe subset lands with U7.

  **Session log for U12 (amended 2026-10-07, recsys-014).** The main log's timestamps and sessions are real, but its
  sequential signal turned out to be **order-insensitive**: on `interactions.csv.gz` a capped SASRec (0.17–0.21 hit@10)
  scored below plain item-item CF (0.252) and the same as a shuffled-history control; author-following was at the
  random level, drift was small, and the median history was 8 positives. Strengthening the main generator would move
  every pinned number in U2–U11 and Checkpoint A, so U12 gets a **separate seeded session log** instead.
  - *What it is:* `sessions.csv.gz` (the same 6-column schema as `interactions.csv.gz`) over its own synthetic reader
    population, plus `series.csv.gz` (`item_id, series_id, volume`; same-author series of 3–5 volumes). Order
    mechanisms: a **forced next-volume exposure** slot after a series read, a **decaying author-follow** bump, a
    **persistent per-session genre mood**, and longer histories (median ≥ 20 train positives). Splits are per reader
    by session (`train < val < test`, test sealed).
  - *What is shared:* the catalog and the taste-aware exposure form above. *What is not:* the readers — every U12
    number must say "on the session log", and it is not comparable to main-log numbers.
  - **Cold items are excluded** from the session log, so U12 needs no cold-start machinery.
  - `series.csv.gz` is a catalog-side observable. U12 uses it for **diagnostics only** (for example, next-in-series
    hit rate), not as a model input unless it is taught.
  - A sequence model has no reader ids, so it *could* run on main-log histories, but there it behaves like a bag model.
    **U13/U14 score the sequence path on the session log only.**
  - **Byte-stability guarantee:** the new artifacts draw only from named, independent `SeedSequence` sub-streams
    (`SUBSTREAM_KEYWORDS = 1`, `SUBSTREAM_SERIES = 2`, `SUBSTREAM_SESSIONS = 3`) and never touch the threaded rng.
    `catalog.csv.gz`, `interactions.csv.gz`, `keywords.csv.gz` and `cold_partitions.json` stay byte-identical
    (sha256-pinned by a test).
  - **SASRec is a measured near-tie, not the winner (user decision 2026-10-08).** At the §7 ceiling, a tiny SASRec
    learns order (ordered beats an order-shuffled copy) but stays about 1.5–2 SE short of bag item-item CF. The
    cheap order-aware paths (last-k CF, transition) carry U12's lift. The unit reports this honestly, as U11 did.
  - A committed **session recoverability harness** gates the order signal. Last-k CF must beat bag CF; a last-k
    transition reference must drop clearly under an order-shuffled control; and next-in-series must beat bag CF.

## 7. Tooling, dependency isolation & reproducibility

- **Concept track:** numpy to derive core mechanics (cosine/BM25, MF by gradient descent, an ID-only two-tower's
  forward/backward, the contrastive-loss gradient) → then the mature library.
  Honest scope: from-scratch is realistic for U2–U5 and U8's ID-only two-tower + single-step contrastive gradient;
  it is **not** realistic for FAISS/HNSW (U10) or SASRec (U12) — there the "reveal" is an **exact brute-force numpy
  baseline → library**, compared on **recall-vs-speed**, not a from-scratch reimplementation.
- **Libraries (isolated via a dependency group):** `numpy`, `pandas`, `matplotlib`, `scikit-learn`
  (`NearestNeighbors`, `TruncatedSVD`), **PyTorch** (MF, two-tower, reranker, SASRec taste), **FAISS-cpu**
  (or `hnswlib`). `psycopg` and **`gensim`** are used ONLY in the slice / GloVe-subset derivation scripts (off the
  CI exec path — avoids gensim's wheel/numpy-2 fragility on py≥3.12); notebooks load the committed GloVe `.npy`
  subset (§6), never `gensim`. **`implicit`** is optional for an ALS reveal and never on the CI path.
  **`surprise` is dropped** (unmaintained; compiles; numpy-2 / py3.12 breakage).
  These go in `[dependency-groups] recsys` in `pyproject.toml`; `ci-local.sh` routes this book's checks through
  `uv run --group recsys`, so the install/exec cost of the heavy deps is routed away from the other books' checks.
  Caveat: `uv` keeps a single lockfile/venv, so `--group recsys` still adds torch/faiss to the shared `.venv` and
  shares resolution constraints — the *cost* is isolated, the *lock* is not; if version conflicts with the other
  books appear, promote `recsys` to a `uv` workspace member.
- **Determinism (mandatory):** `PYTHONHASHSEED`, `numpy` seed, `torch.manual_seed` +
  `torch.use_deterministic_algorithms(True)` + single-thread; `faiss.omp_set_num_threads(1)` (HNSW build is
  thread-order dependent).
  Assertions are **tolerance/rank-based**, never exact-float; ANN is verified by **recall@k + latency bounds**, not
  exact neighbor identity.
- **Scale ceilings (committed, not "small enough"):** ~5–20k books, ~5k synthetic readers, ~200k interactions,
  embedding dim ~32, a **tiny 1-block SASRec** at seq-len ≤50, few epochs.

## 8. Structure — two parts, dual-track, with checkpoints and an ethics thread

Pacing: classroom-taught; a "unit" may span 2–3 sittings (hence the wider `lesson_budget`).
Every unit ships `lesson.ipynb` / `exercises.ipynb` / `solutions.ipynb` / `teacher-notes.md`; the project track
grows an **importable package** (§10).
Evaluation starts early: **U1/U2 introduce a frozen holdout + hit-rate@k / recall@k scoreboard** (also the natural
project hook, "how would we know it works?"); U6 deepens it (RMSE vs. ranking metrics, NDCG, calibration, path
ablations).
**Cold-start is a cross-unit thread (U6 → U9 → U13).**

### Part 1 — Foundational Recommenders

| # | Concept track (numpy → library) | Contributes |
|---|---|---|
| 1 | The recsys problem; catalog data; retrieve-then-rank; the `RetrievalPath` interface; **the evaluation scoreboard** | Skeleton (paths + blend + rank) + search/filter + holdout/hit-rate@k |
| 2 | Popularity & baselines; Bayesian/weighted average; **popularity bias** | **Path: popularity/trending** |
| 3 | Lexical retrieval: bag-of-words, **TF-IDF**, **BM25**, cosine/BM25 scoring | **Path: lexical (BM25)** (+ content-similarity, lighter) |
| 4 | Neighborhood CF: user/item **k-NN**; implicit vs explicit; sampled negatives | **Path: item-item co-occurrence** |
| 5 | **Matrix factorization**: latent factors, SVD, gradient descent + regularization | **Path: latent-factor** (the embedding bridge) |
| 6 | Evaluation deepened: RMSE, precision@k/recall@k, **NDCG**; **coverage/diversity/novelty**; cold-start; ablations | **Blend v1** + classical ranker; **Checkpoint A** (end of Part 1) |

### Part 2 — Neural Recommenders

| # | Concept track (numpy → PyTorch/FAISS) | Contributes |
|---|---|---|
| 7 | Factors → **learned embeddings**; content embeddings (committed GloVe subset); brute-force embedding retrieval | **Path: semantic text embeddings** |
| 8 | **MF re-expressed as an ID-only two-tower** in PyTorch, trained with BPR / sampled softmax (bridges U5) | **Path: two-tower (behavioral)** |
| 9 | **Feature towers** (subjects/author/GloVe + id) → **item cold start**; hard negatives | Strengthens the two-tower path |
| 10 | **ANN retrieval**: exact vs approximate, recall/speed; **FAISS/HNSW**; **hybrid sparse (BM25) + dense** | Shared retrieval infra (exact brute-force baseline → library) |
| 11 | **Neural ranking**: candidates → learned reranker; features; blend calibration | Learned reranker + learned path blending |
| 12 | **Sequence-aware** (tiny capped SASRec-style self-attention over reading history), scored on the **session log** (§6) | **Path: session/sequence** |
| 13 | Evaluating the whole system; **ethics & beyond-accuracy**: exposure/popularity bias, feedback loops, filter bubbles, fairness, offline-metric limits; per-path ablations | System-wide eval; **Checkpoint B** |
| 14 | Capstone | The full **multi-path retrieval + blend + neural rerank** recommender, consuming **bounded/cached** models (regenerated by seeded scripts and validated by a required check, within a total budget), benchmarked vs. the Part-1 build, with an **ablation table AND a beyond-accuracy table** |

## 9. Verification — how it plugs into `scripts/ci-local.sh`

Base per-book checks apply (structure, manifest, prereq closure over the book's graph + `baseline.yaml` +
the `python-projects` dependency baseline, coverage, stretch presence, notebook execution, hygiene, PDF build);
flag-gated families do not.
Concrete execution budget (the exec gate is the authority, not a bypass):
- `NotebookClient` enforces a **120 s per-cell** cap, and `exec-lessons` runs `lesson.ipynb` in addition to
  `solutions.ipynb`, so **every training loop runs ≥ twice per CI pass** — models/epochs are sized so no cell
  exceeds 120 s and each notebook stays within a stated per-notebook budget, with a whole-book CI-minutes target.
- Expensive artifacts (fitted embeddings/models) may be **cached under `assets/`**, but caching is NOT a `no-exec`
  escape: a **required check regenerates the cached artifacts from their seeded scripts and validates them**, so the
  expensive behavior stays under the authoritative gate.
- Every unit-shipping plan MUST name its verification phase (the standard gate rule).
- **Whole-book exec target:** ≤ ~15 CI-minutes (a first-plan-validated target the per-unit plans divide against).
  Note `exec-solutions` also executes the `projects/` milestone/solutions notebooks, so a heavy path can run a
  *third* time (lesson + solution + project/capstone regeneration) — model/epoch sizing accounts for all three.

## 10. Project packaging

The cumulative system cannot live in scattered notebook cells across 14 units.
It is an **importable package** at `recsys/projects/bookrec/bookrec/` (the `bookrec` package: catalog loading,
the `RetrievalPath` registry, blend, rank, evaluation), installed via the `recsys` dependency group as an editable
local package so unit notebooks `import bookrec` under CI (the exec checks run from the unit dir; the package is on
the path via the group install).
Each unit's project milestone **adds or extends a `bookrec` module and ships a milestone notebook** at
`recsys/projects/bookrec/milestones/unit-NN-<slug>.ipynb` — a runnable, fixed-seed demonstration that integrates the
unit's deliverable into the growing system. Milestone notebooks are under the authoritative gate (discovered + run by
`exec-solutions`, hygiene/seed/concept-scan checked by dedicated tooling) **without being `projects/project-*` map
entries**: the single `projects/` *registry* entry is treated by the tooling as the **capstone**
(`practice_findings` requires every concept practised by a non-capstone entry), so it is CI-feasible only once the
book is concept-complete and is therefore **authored only at the Unit-14 capstone**. (The growing project is thus the
`bookrec` package + its per-unit milestone notebooks; the one `projects/` map entry is the capstone. Resolved
2026-10-02 per recsys-003 — supersedes the earlier "single `projects/` entry's manifest grows per unit" wording,
which collided with the capstone rule. Unit 1 is grandfathered: its milestone shipped as package code before this
convention.)

## 11. Governance amendments (user-authorized precondition — 2026-09-29)

The middle-school baseline is hard-coded in two governance files; without amendment every recsys gate reviewer is
formally obliged to reject the book.
The author authorized (2026-09-29) a **precise per-book-baseline carve-out**, to ship as a small governance PR
BEFORE recsys content merges:

- **AGENTS.md — "Self-containedness is law"** gains a clause: a book MAY declare its own audience, assumed
  mathematics, and permission to use named libraries in its design doc; **all other laws
  (project-first, coverage, taught-before-assessed, hygiene, stretch, teacher-notes, checkpoints) are retained for
  every book.**
- **`docs/content-review-gate.md` — the "age-appropriateness" duty** is generalized to
  **"audience-appropriateness per the book's declared baseline."**

This design doc does **not** itself declare any gate/roster change (e.g. it does not establish a "3-way" gate;
the current [glm] skip is a separate standing user decision recorded in plan 091).
The amendment ships as its **own governance PR** (it edits root governance files, not recsys content) — not as a
`recsys-NNN` plan — and merges before any recsys content.

## 12. Namespace & collision safety

Plans live under **`docs/plans/recsys/`** (author's choice), numbered **`recsys-NNN`**.
`scripts/pre-merge-guard.sh` today guards only Markdown directly under `docs/plans/` (a path-depth condition), so
nested files evade the collision check that protects the reserved plans 092/093.
The first plan therefore **extends pre-merge-guard with a tested namespace-aware uniqueness rule** (guarding nested
plan files too, and matching the `recsys-NNN` stem — the current `^[0-9]{3}(?=-)` regex would not).
Chicken-and-egg: that first guard-extending plan file is itself unguarded under the current depth rule, which is
acceptable because only that single file is exposed before the rule lands.
Book id `recsys` is unused; `acsl` / `usaco-silver` are avoided.

## 13. Out of scope (for now)

- A deployed serving API / web front-end (the capstone "serves" via a notebook/CLI query interface).
- GPU training (everything is CPU-deterministic).
- Real per-user data (interactions are synthetic; no real ratings enter the repo, unless the goodbooks-10k fallback
  is chosen and its license/PII posture is confirmed acceptable for a public repo).
- Distributed / big-data infrastructure (the committed slice is notebook-scale).
- An optional out-of-repo stretch on real interaction data (goodbooks-10k / Book-Crossing) may be referenced but is
  not committed.

## Design Review

Design-review gate. Roster: `[self]` (inline), `[sol]` (codex `--model gpt-5.6-sol`, read-only), `[fable]`
(Fable 5, read-only). `[glm]` skipped by standing user decision (2026-09-28; recorded in plan 091).

### Round 1 (on v1) — verdicts
- **[self]:** APPROVE WITH NITS — 6 items (CPU-determinism guardrail, U12 transformer feasibility,
  dependency-weight/shared-env, `RetrievalPath` forward-design, DB-license-as-blocker, ethics beat).
- **[sol]:** REJECT — 5 Must (heavy-dep CI determinism/budgets; data+embedding provenance contract + license
  blocker; plan-namespace guard hole; over-broad baseline override + missing prob/stats & numerical-Python + no
  design-doc gate change; synthetic generator can't drive the curriculum + non-identifiability) + Should (eval
  earlier; from-scratch not for FAISS/SASRec; library-API closure; `RetrievalPath` contract; ethics core; U12/U14
  ceilings) + Nice (number:3; §-ref fix; lesson_budget).
- **[fable]:** REJECT (revise to v2) — 4 Must (synthetic generator per-unit signals; offline reproducibility /
  GloVe-network / slice-format / per-cell-timeout; governance-amendment precondition + drop the "3-way" claim;
  assumed-baseline tooling mechanism) + 8 Should (eval earlier; U8/U9 reorder; U3 overload + U7 motivation trap;
  drop `surprise` + dependency-group isolation + determinism; license fallback; project packaging; missing
  checkpoints/teacher-notes/pacing; ethics core + cold-start thread) + 4 Nice.
- **[glm]:** skipped.
- **Round-1 outcome:** NOT consensus (2 REJECT). Full findings are preserved in git history (commit `a76b054`) and
  on PR #119.

### v2 disposition
v2 folds all Must-Fix and Should-Fix items: precise baseline carve-out + retained laws (§2), governance-amendment
precondition (§11, authorized), assumed-baseline + library-API tooling (§4), data/embedding provenance contract +
license-blocker + gzip'd-CSV + committed GloVe subset (§6), per-unit synthetic-signal spec with exposed
ground-truth + non-identifiability handling (§6), dependency-group isolation + determinism + committed scale
ceilings + dropped `surprise` (§7), forward-designed `RetrievalPath` contract (§5), early evaluation scoreboard +
U8/U9 reorder + tiny SASRec + cached-with-required-regen capstone + checkpoints + core ethics/beyond-accuracy
thread + cold-start cross-unit thread (§8), concrete exec budgets (§9), importable project package (§10),
namespace-aware guard extension (§12), and the Nice items (number:3, "Applied Python" series, §-ref fix,
lesson_budget). Ready for round-2 review.

### Round 2 (on v2, commit 04f5dba)
- **[self]:** APPROVE — verified every round-1 Must/Should item maps to a v2 section; no new issues.
- **[sol]:** APPROVE — all 5 Must-Fixes RESOLVED (with §s), all Should-Fixes handled, no new findings.
- **[fable]:** APPROVE WITH NITS — all 4 Must + 8 Should + Nice RESOLVED; scope right-sized, no new blocker; 6 NIT
  findings, all folded into v2:
  1. §3 `lesson_budget` is a whole-book TOTAL (not per-unit) — reworded + the min/buildout caveat noted. **[FIXED]**
  2. §7 `gensim` (and `implicit`) moved to slice/derivation-only / never-on-CI; notebooks load the committed GloVe
     `.npy`. **[FIXED]**
  3. §6 pinned the slice script + synthetic generator as `recsys-001` deliverables; GloVe subset with U7. **[FIXED]**
  4. §11/§12 governance PR ships as its own governance PR (not a `recsys-NNN` plan); §12 notes the guard must match
     the `recsys-NNN` stem and the one-file chicken-and-egg. **[FIXED]**
  5. §7 softened the CI-isolation claim (uv single lock/venv; cost isolated, lock shared; workspace-member escape
     hatch). **[FIXED]**
  6. §9 pinned a whole-book exec target (~≤15 CI-min) + noted the third heavy execution via `projects/`. **[FIXED]**
- **[glm]:** skipped (standing user decision, plan 091).

### Design-review outcome: **FULL CONSENSUS on v2** — [self] APPROVE · [sol] APPROVE · [fable] APPROVE WITH NITS (all folded) · [glm] skipped
No open blockers. Gate CLOSED. The design is approved. Implementation preconditions (each named above): the
user-authorized **governance-amendment PR** (§11) ships first; then `recsys-001` (§12) extends pre-merge-guard,
scaffolds the book + `baseline.yaml` + slice script + synthetic generator + the `bookrec` package (a
**foundation** plan — NO student units; `buildout: true`) through the plan-review gate. Units land in
`recsys-002+`, per design 008's one-design-then-1–2-units cadence.

## 14. Revision history

- **v5 (2026-10-07, via recsys-014):** §6 amended with a **separate seeded session log** for U12 (`sessions.csv.gz` +
  `series.csv.gz`; forced next-volume exposure, decaying author-follow, genre mood, longer histories; cold items
  excluded; named independent sub-streams). The main artifacts stay byte-identical, and a session recoverability
  harness gates the order signal. §8 row 12 now notes that U12 is scored on the session log. Prompted by the U12
  pre-plan probe, which found the main log's sequence signal order-insensitive (capped SASRec ≤ bag CF and equal to a
  shuffled control). User-approved option; reviewed under recsys-014's gates.
- **v4 (2026-10-03, via recsys-004):** §6 amended — **taste-aware exposure** (exposure ∝ popularity^α · exp(β·z-affinity))
  replaces popularity-only exposure so content/collaborative/latent signals are each recoverable and beat popularity
  (enforced by a committed recoverability harness), while a positive-rate estimate stays weak (preserving U2's
  popularity-bias lesson); added a seeded **keyword text artifact** (`keywords.csv.gz`, latent-correlated real-word
  token bags) as the U3 lexical corpus + U7 GloVe vocabulary source. Prompted by the recsys-003/005 finding that the
  original generator was popularity-dominated (true-affinity oracle ≈ random floor). Reviewed under recsys-004's
  plan-review gate.
- **v3 (2026-10-02, via recsys-003):** §10 project-packaging amended — the growing project is the `bookrec` package
  + per-unit milestone notebooks (gated via dedicated tooling, not as `projects/project-*` map entries); the single
  `projects/` registry entry is the Unit-14 capstone. Supersedes the "single `projects/` entry's manifest grows per
  unit" wording, which collided with the tooling capstone rule. Reviewed under recsys-003's 4-way plan-review gate.

- **v1 (2026-09-29):** created. Two-part book, dual concept∥project tracks, multi-path retrieve-then-rank project
  over the real `books` catalog slice + synthetic interactions, numpy→library tooling with PyTorch/FAISS.
- **v2 (2026-09-29):** folded round-1 review ([sol]+[fable] REJECT). Added: precise baseline carve-out + retained
  laws; user-authorized governance-amendment precondition; assumed-baseline + library-API tooling mechanism
  (`baseline.yaml`); full data/embedding provenance contract (license blocker, gzip'd CSV, committed GloVe subset,
  DB/network-free CI); per-unit synthetic-signal spec + non-identifiability; dependency-group isolation +
  determinism + committed scale ceilings + dropped `surprise`; forward-designed `RetrievalPath` contract; early
  evaluation scoreboard, U8/U9 reorder, tiny-SASRec ceiling, cached-with-required-regeneration capstone;
  checkpoints; core ethics/beyond-accuracy + cold-start threads; concrete CI exec budgets; importable project
  package; `recsys-NNN` namespacing + pre-merge-guard extension; registry `number:3` + "Applied Python" series.
