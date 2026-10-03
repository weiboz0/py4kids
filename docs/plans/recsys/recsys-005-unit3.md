# Plan recsys-005 — Unit 3: Lexical retrieval (TF-IDF and BM25)

**Design:** `docs/designs/011-recsys-book.md` (§5, §6 keyword artifact, §8 Unit 3). **Book:** `recsys` (Book 3).
**Autopilot** per AGENTS.md. This replaces the original Unit-3 draft (preserved in git history + recsys-004's
motivation), whose premise was infeasible on the popularity-dominated data. recsys-004 (merged, `f44891d`) gave the catalog real
**keyword text** and a recoverable content signal, so a lexical path now beats the floor by ~14×. Ships the first
content/lexical **reader-dependent** path on the Unit-1/2 substrate + the milestone-notebook mechanism.

## Scope
**Unit 3 only** (`recsys/units/unit-03-lexical-retrieval/`). Teaches lexical/content retrieval over each book's
**keyword document** (`keywords.csv.gz`, real repeated-term word bags from recsys-004): **bag-of-words**, **TF-IDF**
(+cosine), **Okapi BM25**; ships `LexicalRetrievalPath` (BM25) in `bookrec` + a Unit-3 milestone notebook. A reader's
query is the keyword tokens of the books they have read. No CF (U4), no learned embeddings (U7). No generator change
(the recsys-004 keyword text + harness stand).

## Framing (honest, per recsys-004 [fable] follow-up)
Keyword BM25 beats the random floor massively (~0.158 vs ~0.012 ≈ 14×) and is a strong **content candidate source**;
it is **comparable to** a simple genre-matching baseline and sits below collaborative/latent paths (U4/U5) — the
lesson frames lexical as "retrieve books whose words match what you've read", NOT as "beats everything". (The
`keyword_genre_scale` signal-independence question is noted but NOT re-tuned here — lexical is a valid floor-beating
path as shipped; re-tuning would re-open the merged generator for marginal benefit.) Empirical floor-beating is
BINDING on authors + the gate (reuse recsys-004's harness/probes).

## Buildout stays
Whole-book `lessons` total becomes **12** (U1 3 + U2 3 + U3 3) < 30 → `buildout: true` retained.

## Audience & retained laws
Advanced baseline (incl. `vectors`, `dot-product`, `vector-norm`, `logarithms`, numpy). Retained: project-first;
taught-before-assessed; student notebooks NO solutions/outputs (`execution_count: null`); solutions + milestone run
clean (seed 0); teacher-notes; from-scratch→reveal-the-library (derive TF-IDF/BM25 in numpy before packaging).
CPU-light (numpy/pandas + `bookrec`; no torch/faiss) routed `--group recsys`.

## Concepts introduced (3) — `concepts.yaml`
- `bag-of-words` — a book as a bag of **keyword tokens**; document–term view, vocabulary, document frequency `df`,
  raw term frequency (real repetition in the keyword text). `kind: technique`, `category: techniques`.
- `tf-idf` — tf × idf weighting + **cosine** similarity between a reader's keyword profile and item vectors; why IDF
  down-weights ubiquitous words. `kind: technique`, `category: techniques`.
- `bm25` — Okapi BM25: IDF × saturating tf (`k1`) × document-length normalization (`b`); why it improves on raw
  TF-IDF cosine for retrieval — now demonstrable on real variable-length, repeated-term keyword docs.
  `kind: technique`, `category: techniques`.
All three globally unique (0 hits in any `*/curriculum/concepts.yaml`).

### Coverage-map entry
`unit-03-lexical-retrieval`, `kind: unit`, `lessons: 3`, `introduces: [bag-of-words, tf-idf, bm25]`,
`requires: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics]`,
`practices: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics]` (Unit-1 ids; closes
under buildout; no project map entry → capstone rule inert). catalog-search genuinely practised (reads the catalog +
keyword artifact).

## Phases

### Phase A — registry + syllabus
- `concepts.yaml`: add the 3 ids. `coverage-map.yaml`: add the Unit-3 entry (buildout comment → "twelve").
- `baseline.yaml`: declare new `x.name(...)` methods the notebooks/code use (e.g. `load_keywords`, numpy
  `log`/`log1p`/`argpartition`/`nonzero`, `np.linalg.norm`→`norm`, bookrec lexical API; `Counter`/`defaultdict` are
  Name calls, not required).
- `unit-03-lexical-retrieval/manifest.yaml`; `syllabus.md` arc row `| 3 | ... | unit | 3 | <hook> |`; rebuild PDF.
**Verify:** curriculum checks green; buildout holds (12<30).

### Phase B — `bookrec` lexical code (Opus subagent; numpy-only, no pandas in the package)
`bookrec/lexical.py`: a document builder from `load_keywords` (tokenize the keyword bag per book); `BM25Index`
(precompute `df`/`idf`/doc-lengths/`avgdl`; BM25 score vs a query-token multiset; `k1`~1.2, `b`~0.75) + a
`tfidf_matrix`/`cosine_similarity` helper for the from-scratch step; `LexicalRetrievalPath(BaseRetrievalPath)`
(name `"lexical"`, version `"1"`): `fit(interactions, catalog, keywords)` builds the index from the keyword text
(raise if keywords missing/empty); `retrieve(reader_id, context, k)` forms the query from the keyword tokens of
`context["seen"]` books, scores by BM25, excludes `seen`, top-k via `_finish`; empty `seen` → `[]`. `load` restores
the index. Export from `__init__`. Tests (routed): hand-checked index math (IDF monotone in `df`; BM25 `k1`
saturation + `b` length-norm behave on a tiny fixture); path beats the random floor on the seeded `val` scoreboard
(direction + margin, `cold_readers` passed); empty-seen → `[]`; `artifact_name()=="lexical-v1"` no collision.
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/ -q` green, deterministic.

### Phase C — lesson.ipynb (Opus subagent; project-first)
Hook: "you've read a handful of books — which *other* books use the same words/themes?" From scratch → reveal:
(1) bag-of-words over the keyword text (vocabulary, `df`, real tf); (2) TF-IDF + cosine by hand → reveal the helper;
(3) BM25 (`k1` saturation, `b` length-norm — show the effect on the real variable-length docs), reveal
`LexicalRetrievalPath`, register + score on `val` (seed 0, k=10, `cold_readers`) — beats the floor ~14×; compare to
the random floor and the U2 popularity baseline (honest: strong vs floor, comparable to simple matching, below the
collaborative paths to come). ASCII only; `rank(exclude=seen)`; reuse `bookrec`.
**Verify:** `exec-lessons` clean; non-empty markdown first cell; `concept-scan` clean.

### Phase D — exercises.ipynb + solutions.ipynb (separate fresh Opus subagents)
≥6 `## Exercise N`; ≥2 `stretch`; exercises NO solutions/outputs; solutions mirror all, clean (seed 0), ≥3
non-vacuous asserts. Drill: build bag-of-words + `df`/`idf` from keyword text; tf-idf cosine for a profile; BM25 +
the `k1`/`b` effect (now visible on real repeated-term docs); register `LexicalRetrievalPath` + read the val
scoreboard vs floor/popularity. Stretch e.g.: BM25→tf-ish as `k1→∞`; `b=0` vs `b=1` on a long vs short doc; why a
rare keyword dominates. Taught-before-assessed.
**Verify:** `hygiene`/`structure`/`cell-lint`/`noexec` (≥6, ≥2 stretch, no outputs); `exec-solutions` clean;
`concept-scan` clean.

### Phase E — milestone notebook (Opus subagent)
`recsys/projects/bookrec/milestones/unit-03-lexical.ipynb` — runnable fixed-seed demo (cleared outputs, ASCII, opens
with a hook): build+fit+register `LexicalRetrievalPath`, score on val vs the random floor + U2 popularity, and show
one reader's keyword profile → top recommendations with the matching words. Passes `milestone-check` +
`exec-solutions` + `concept-scan`.

### Phase F — teacher-notes.md (inline)
`## Goals`, `## Pacing` (60–90 min / 2–3 sittings, hook stated), `## Common mistakes` (no IDF → common words
dominate; no length-norm → long keyword lists win spuriously; query from seen vs leaking val; cosine vs BM25),
`## Discussion prompts`, `## Differentiation`.

### Phase G — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN with Units 1–3 + the Unit-3 milestone AND
`bash scripts/pre-merge-guard.sh --pr` OK. buildout holds (12).

## Out of scope
No CF (U4); no MF/neural/embeddings (U5/U7); no generator/`keyword_genre_scale` change (recorded, deferred); no
`projects/project-*` map entry (capstone=U14); no checkpoint; no buildout removal; no real data.

## Verification phase declared
Phase G is this plan's named verification phase.

## Plan Review

### Round 1 (on v1)

**[self] — APPROVE.** Concepts globally unique; coverage entry closes (Unit-1 ids; `practices∩introduces=∅`; no
project map entry → capstone rule inert); buildout holds (12<30); named verification Phase G; project-first;
from-scratch→library; ≥6/≥2-stretch/≥3-asserts; teacher-notes; milestone. Feasibility is now real (recsys-004
keyword text: BM25 ~0.158 ≈ 14× floor, with genuine tf repetition + length variation so `k1`/`b` are meaningful);
framing is honest per the recsys-004 follow-up (lexical beats the floor + is a content candidate source, NOT "beats
genre"). No generator re-opening. No [self] blockers. `[glm]` weekend-skip (resume Monday).

<!-- [sol] / [fable] appended -->

## Content Review

<!-- appended pre-PR -->

## Post-Execution Report

<!-- appended before ship -->
