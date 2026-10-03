# Plan recsys-005 — Unit 3: Lexical retrieval (TF-IDF and BM25)

> **STATUS: BLOCKED / SUPERSEDED-FOR-REVISION (renumbered 004→005 on 2026-10-03).** Plan-review round 1 ([sol] +
> [fable] empirical REJECT, self-confirmed) proved the premise is unsatisfiable on the current data: no surface
> content/lexical path beats the random floor, and even a true-affinity oracle ≈ the floor because the generator is
> popularity/exposure-dominated. The user approved a **generator redesign first** (plan **recsys-004**:
> taste-aware exposure + latent-correlated per-book text + a recoverability harness + Unit 1-2 re-validation). This
> Unit-3 plan will be **re-drafted on the redesigned data** (documents become real repeated-term text; TF-IDF/BM25
> `k1`/`b` become meaningful; the lexical/content path must beat the floor and be re-measured). The round-1 review
> record below is retained as the diagnosis that motivated recsys-004. Do NOT implement this plan as written.

---

# (original) Plan recsys-004 — Unit 3: Lexical retrieval (TF-IDF and BM25)

**Design:** `docs/designs/011-recsys-book.md` (§5, §6 "taste derived from catalog features (subjects/authors)", §8
Unit 3). **Book:** `recsys` (Book 3). **Autopilot** per AGENTS.md. Third Part-1 unit, on the recsys-001/Unit-1/Unit-2
substrate and the now-established milestone-notebook mechanism (design §10 v3). Ships the first **content/lexical**
retrieval path — the first **reader-dependent** path — scored against the Unit-1 random floor and the Unit-2
popularity baseline.

## Scope
**Unit 3 only** (`recsys/units/unit-03-lexical-retrieval/`). Teaches lexical/content retrieval over the catalog's
feature tokens: **bag-of-words**, **TF-IDF** (+ cosine), and **Okapi BM25**, and ships a `LexicalRetrievalPath`
(BM25) in `bookrec` + a Unit-3 milestone notebook. No collaborative filtering (U4), no learned embeddings (U7). No
real data; **no generator change** — the lexical "document" for each book is its existing **genre tokens + author
token** (design §6 feature-taste signal), and a reader's query is the token profile of the books they have read.

## Why this works on the existing data (empirical, binding)
The catalog generator (`gen_catalog.py`) gives each book **1–3 of 12 genres** (`genres`, `;`-joined) and one of **300
authors** (`author_id`), and builds reader taste from the genre-membership matrix + an author-follow boost
(`gen_interactions.py`). So each book's bag-of-words document = its genre tokens + an `author:<id>` token (vocabulary
≈ 312), and a reader whose positives share genres/authors will have those books surfaced by a BM25/TF-IDF match →
the path beats the random floor and captures per-reader taste the (non-personalised) popularity path cannot.
**Authors MUST empirically confirm on the committed seed** (k=10, cold excluded) that `LexicalRetrievalPath` beats
the random floor, and report its number vs the Unit-2 popularity baseline; write the measured direction into the
Phase B tests and the lesson/milestone prose (do not assert brittle exact values).

## Buildout stays
Whole-book `lessons` total becomes **9** (U1 3 + U2 3 + U3 3) < 30 → `buildout: true` retained.

## Audience & retained laws (design 011 §2)
Advanced audience; assumed baseline (incl. `vectors`, `dot-product`, `vector-norm`, `logarithms`, `probability`,
`numpy-*`). Retained: project-first; taught-before-assessed; student notebooks NO solutions / NO outputs
(`execution_count: null`); solutions + milestone run clean with fixed seeds (seed 0); teacher-notes; dual
concept∥project tracks; from-scratch→reveal-the-library (derive TF-IDF/BM25 in numpy before packaging). CPU-light
(numpy/pandas + `bookrec`; no torch/faiss) routed under `--group recsys`.

## Concepts introduced (3) — added to `concepts.yaml`; Unit 3 is their `introduces` home
- `bag-of-words` — represent a book as a bag of feature **tokens** (its genres + its `author:<id>`); the
  document–term view, vocabulary, document frequency `df`. `kind: technique`, `category: techniques`.
- `tf-idf` — term-frequency × inverse-document-frequency weighting and **cosine** similarity between a reader's
  token profile and item vectors; why IDF down-weights ubiquitous tokens. `kind: technique`, `category: techniques`.
- `bm25` — Okapi **BM25**: IDF × saturating term frequency (`k1`) × document-length normalization (`b`); why it
  improves on raw TF-IDF cosine for retrieval, and the `k1`/`b` roles. `kind: technique`, `category: techniques`.
All three globally unique (confirmed: 0 hits across `*/curriculum/concepts.yaml`).

### Coverage-map entry
`unit-03-lexical-retrieval`, `kind: unit`, `lessons: 3`, `introduces: [bag-of-words, tf-idf, bm25]`,
`requires: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics]`,
`practices: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics]`. (All required/practised
ids are Unit-1 introductions → `prereq_findings`/`practice_findings` close under buildout; no `project` map entry so
the capstone rule does not fire. catalog-search is genuinely practised here — the path reads the catalog's
genre/author features.)

## Phases

### Phase A — curriculum registry + syllabus (CI-fidelity)
- `concepts.yaml`: add the three ids (`kind: technique`, `category: techniques`).
- `coverage-map.yaml`: add the Unit-3 entry (map order after Unit 2); update the buildout comment to "nine".
- `baseline.yaml`: declare every NEW `x.name(...)` library method the Unit-3 notebooks/code call (confirmed against
  authored cells; e.g. numpy `log`/`log1p`/`argpartition`/`nonzero`/`unique`, `np.linalg.norm`→`norm`, and the new
  bookrec API; `Counter`/`defaultdict` are Name calls → not required).
- `recsys/units/unit-03-lexical-retrieval/manifest.yaml`: mirror the entry.
- `recsys/syllabus.md`: add the arc row `| 3 | \`unit-03-lexical-retrieval\` | unit | 3 | <hook> |`; rebuild syllabus PDF.
**Verify:** curriculum checks green; buildout holds (9 < 30).

### Phase B — `bookrec` lexical code (Opus subagent; package code)
Dispatch an **Opus subagent**. Add `bookrec/lexical.py` (numpy-only; no pandas import in the package):
- a document builder: for each catalog book, tokens = its genre names (split on `;`) + `author:<author_id>`.
- `BM25Index` (and a TF-IDF/cosine helper used by the lesson): precompute `df`, `idf`, document lengths, `avgdl`;
  BM25 score of a document vs a query-token multiset with parameters `k1` (default ~1.2) and `b` (default ~0.75);
  plus a `tfidf_matrix` / `cosine_similarity` helper for the from-scratch TF-IDF-cosine step.
- `LexicalRetrievalPath(BaseRetrievalPath)` (name `"lexical"`, version `"1"`): `fit(interactions, catalog)` builds
  the index from the **catalog** (raise if `catalog` is None/empty); `retrieve(reader_id, context, k)` forms the
  reader's **query** from the tokens of the books in `context["seen"]`, scores catalog books by BM25, excludes
  `seen`, returns top-k via `_finish`; an empty `seen` → returns `[]` (no profile). Reader-DEPENDENT. `load` restores
  the fitted index. Honour the `Candidate`/finite-score/stable-int/tie-break contract.
- Export the new public names from `bookrec/__init__.py` `__all__`.
- Tests under `recsys/projects/bookrec/tests/` (routed): index math is correct on a tiny hand-checked fixture
  (IDF monotonic in `df`; BM25 length-normalization and `k1` saturation behave); the path beats the random floor on
  the seeded val scoreboard (direction) with `cold_readers` passed; empty-`seen` → `[]`; registers with
  `artifact_name()=="lexical-v1"`, no collision.
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/ -q` green, deterministic, no real data, no pandas
import under `bookrec/`.

### Phase C — lesson.ipynb (Opus subagent; project-first)
First cell = markdown hook ("you've read three space operas and a mystery — which *other* books match your taste,
before anyone else has rated them?"). Then from scratch → reveal the library:
1. **Bag-of-words**: build each book's token document (genres + author) from the catalog; vocabulary + `df`.
2. **TF-IDF + cosine**: derive tf-idf weights and cosine similarity by hand in numpy; score books against a reader's
   token profile; reveal the `bookrec` TF-IDF helper.
3. **BM25**: motivate IDF + tf-saturation (`k1`) + length-norm (`b`); derive BM25; reveal `LexicalRetrievalPath`;
   register it and score on the val scoreboard (seed 0, k=10, `cold_readers` passed) — beats the random floor, and
   compare to the Unit-2 popularity baseline (show both numbers; interpret where content wins/loses vs popularity).
ASCII diagrams only; `rank(exclude=seen)`; reuse `bookrec`.
**Verify:** `exec-lessons` clean; non-empty markdown first cell; `concept-scan` clean.

### Phase D — exercises.ipynb + solutions.ipynb (separate fresh Opus subagents)
≥6 `## Exercise N`; ≥2 `stretch`; exercises NO solutions/NO outputs; solutions mirror all, run clean (seed 0), ≥3
non-vacuous asserts. Drill: build bag-of-words + `df`/`idf`; compute tf-idf cosine for a profile; compute BM25 and
show the effect of `k1`/`b`; register `LexicalRetrievalPath` + read the val scoreboard vs random/popularity.
Stretch e.g.: show BM25 → TF-ish as `k1→∞` and the `b=0` (no length norm) vs `b=1` contrast; derive why a rare
genre token dominates the score. Everything assessed is taught in Phase C.
**Verify:** `hygiene`/`exercise-structure` (≥6, ≥2 stretch, no outputs); `exec-solutions` clean; `concept-scan` clean.

### Phase E — milestone notebook (Opus subagent)
`recsys/projects/bookrec/milestones/unit-03-lexical.ipynb` — runnable fixed-seed demo (cleared outputs,
`execution_count: null`, ASCII, opens with a one-line project hook): build + fit + register `LexicalRetrievalPath`,
score on val vs the random floor and the Unit-2 popularity path, and show a worked example of one reader's profile →
top recommendations with the matching genre/author tokens. Must pass `milestone-check` + `exec-solutions` +
`concept-scan`.

### Phase F — teacher-notes.md (inline)
`## Goals`, `## Pacing` (60–90 min across 2–3 sittings; project hook stated), `## Common mistakes` (forgetting IDF so
common genres dominate; no length-norm so multi-genre books win spuriously; building the query from seen vs leaking
val; cosine vs BM25 confusion), `## Discussion prompts`, `## Differentiation`.

### Phase G — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN with Units 1–3 + the Unit-3 milestone notebook AND
`bash scripts/pre-merge-guard.sh --pr` OK. buildout holds (lessons 9).

## Out of scope
No collaborative filtering (U4); no MF/neural/embeddings (U5/U7); no generator/schema change; no free-text titles
(documents are genre+author tokens); no `projects/project-*` map entry (capstone = U14); no checkpoint; no buildout
removal; no real data.

## Verification phase declared
Phase G is this plan's named verification phase.

## Plan Review

### Round 1 (on v1)

**[self] — APPROVE.** Concepts globally unique; coverage entry closes (`requires`/`practices` = Unit-1 ids, all
introduced; `practices∩introduces=∅`; no `project` map entry → capstone rule off); buildout holds (9 < 30); named
verification phase G; project-first; from-scratch→library; ≥6/≥2-stretch/≥3-asserts; teacher-notes 60–90 min;
milestone notebook via the established mechanism. Data approach is design-§6-aligned (genre+author feature tokens;
no generator change) and binds empirical floor-beating verification on the authors + the gate. No [self] blockers.
`[glm]` skipped for the weekend (volcengine-plan non-functional across three prior attempts; resume Monday).

**[sol] — REJECT** (empirical). Probed via `run_validation_scoreboard`: the specified genre+author BM25 path scores
BELOW the random floor (unique-query 0.00815, multiset 0.00543 vs random 0.01359, 368 readers). Rare author tokens
dominate IDF; author-following only applies after prior positives and doesn't generalize to `val`. Also: every
document has TF=1 (each genre/author appears once), so BM25 `k1` saturation is inert on this corpus. Plus: `load`
round-trip test unspecified. **Premise fails — the data does not support a floor-beating surface-content path.**
*(Self-confirmed: genre-only cosine 0.0054, genre×IDF 0.0082 — both below floor; all 12 genres have df≈314–358/2000,
so genre matching barely discriminates and the generator's taste is latent, captured by CF/MF not surface features.)*

**[fable]** — plan-review still running when the data-architecture fork was escalated to the user (premise already
empirically refuted by [sol] + self-probe; [fable]'s verdict does not change that a data decision is required).

### Plan-review outcome (round 1): **NOT consensus — [sol] REJECT (premise/data).** Escalated to the user: the synthetic catalog lacks the content/text signal that Units 3 (lexical) and 7 (GloVe) require. Revision blocked on the data-architecture decision below.

## Content Review

<!-- appended pre-PR -->

## Post-Execution Report

<!-- appended before ship -->
