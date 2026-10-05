# Plan recsys-009 — Unit 7: Semantic text embeddings (the committed GloVe subset; begins Part 2)

**Design:** `docs/designs/011-recsys-book.md` (§6 embedding-provenance contract, §7 generator/vocabulary, §8 row 7,
§9 budgets). **Book:** `recsys` (Book 3). **Autopilot** per AGENTS.md. First **Part-2** unit, on the Units 1–6
substrate. Ships the **semantic content-embedding** retrieval path: each book is represented by a dense vector built
from a **committed, checksum-pinned, slice-vocabulary-restricted GloVe subset**, and retrieval is brute-force cosine
in that embedding space. The pedagogical bridge: U5's MF factors were *learned* embeddings; U7 introduces *pretrained
semantic* embeddings (content), both scored by a dot/cosine — foreshadowing U8's *learned neural* two-tower.
**Still numpy — no PyTorch** (torch begins U8). No generator change.

## Scope
**Unit 7** (`recsys/units/unit-07-semantic-embeddings/`). Teaches **dense embeddings** (vs U3's sparse lexical
bag-of-words/BM25): a pretrained **GloVe** word vector per token, a book embedding = (optionally IDF-weighted) mean of
its keyword tokens' GloVe vectors, a reader embedding = aggregate of the books in `context["seen"]`, and **brute-force
cosine retrieval** over the catalog. Ships a `SemanticEmbeddingRetrievalPath` in `bookrec` + the committed GloVe
artifact + a derivation script + a Unit-7 milestone. No two-tower/neural (U8), no ANN/FAISS (U10 — retrieval is
exact brute-force here).

## Data: the committed GloVe subset (new artifact — publish-safe)
- **Source:** `glove-wiki-gigaword-100` (Wikipedia-2014 + Gigaword-5, 400k vocab × 100-dim; GloVe vectors are
  public-domain (PDDL) / Apache-2.0, redistributable). A vocabulary-restricted subset is a few MB and publish-safe —
  **unlike the ISBNdb catalog, GloVe carries no license/PII blocker** (design §6 pre-authorizes it).
- **Derivation (OFF the CI exec path):** `recsys/data/derive_glove_subset.py` loads the cached GloVe via **gensim**
  (run with `uv run --with gensim`, or a derivation-only dep — gensim stays OFF the `recsys` CI group per design §7 to
  avoid its numpy-2/py3.12 wheel fragility), restricts to the recsys-004 slice vocabulary
  (`recsys/data/vocabulary.py` — `vocabulary`/`GENERAL_POOL`/`GENRE_WORDBANKS`), and writes a **float16 `.npy`** of
  shape `(n_vocab, 100)` + a `.json` sidecar (row→token index, dim, source, **GloVe license note**, and a **sha256
  checksum**). Determinism: fixed vocabulary order; out-of-GloVe vocab words recorded + handled (zero vector or
  dropped — decide in Phase B and document).
- **Committed (tracked, NOT gitignored like `generated/`):** the `.npy` + sidecar live under
  `recsys/data/glove/` and ARE committed (they are the reproducible embedding artifact). A ci-local check verifies the
  committed `.npy` matches its recorded checksum (artifact-integrity, mirroring the catalog checksum discipline).

## Why this works on the data (empirical — MUST be measured in Phase B before the lesson claims anything)
The recsys-004 keywords are **latent-correlated** (topic vocabulary conditioned on each book's latent factors +
genres), so a GloVe-averaged book embedding should carry real taste signal. Phase B MUST measure the semantic path's
`val` hit@10 (seed 0, k=10, 60 cold readers excluded) and bind the lesson to the result, honestly:
- Expected: the semantic path beats the random floor and is a **content path comparable to / complementary with** the
  U3 lexical path (lexical ≈0.158) — it should NOT be oversold as beating the collaborative CF/MF paths (≈0.25/0.276).
  The honest story is **dense-semantic vs sparse-lexical**: GloVe relates books via *word meaning* (synonyms/related
  terms) where BM25 needs *shared surface tokens*, so semantic adds candidates lexical misses (measure a coverage /
  complementarity angle, and the U6 blend can include it).
- If semantic ≈ lexical within noise → frame as "a second, semantically-grounded content path" (its value is
  complementarity + the embedding bridge), not a raw-accuracy win. Reviewers verify the framing against a scratch
  measurement; the Phase-B test binds `semantic_hit > floor` + a stated relation to lexical.

## Buildout
Whole-book `lessons` total becomes **21.5** (U1–U7 at 3 each = 21 + Checkpoint A 0.5) < 30 → `buildout: true`
retained. (Crosses ≥30 around U10–U11; a later plan removes it.)

## Audience & retained laws
Advanced baseline (design 011; `vectors`/`dot-product`/`vector-norm`/`linear-algebra`/`numpy-*` all declared). Retained
in full: project-first; taught-before-assessed; student notebooks NO solutions/outputs; solutions + milestone run
clean (fixed seeds); teacher-notes; from-scratch→reveal; a stretch exercise per unit. CPU-light (numpy + `bookrec` +
the committed `.npy`; **no torch/faiss/gensim at CI time**) routed `--group recsys`; within the per-notebook exec
budget (design §9).

## Concepts introduced (3) — `concepts.yaml`
- `word-embeddings` — pretrained dense word vectors (GloVe): a token → a point in a semantic space where distance
  reflects meaning; contrast with U3's sparse one-hot/bag-of-words. `kind: technique`, `category: techniques`.
- `document-embeddings` — composing word vectors into a book/reader embedding (mean / IDF-weighted mean of token
  vectors; L2-normalization); a dense content representation. `kind: technique`, `category: techniques`.
- `embedding-retrieval` — brute-force nearest-neighbour retrieval by cosine similarity in embedding space; the
  dot-product retriever shared by learned (U5) and pretrained (U7) embeddings, and the exact baseline ANN (U10)
  approximates. `kind: technique`, `category: techniques`.
All three globally unique (confirm 0 hits across `*/curriculum/concepts.yaml` in Phase A).

### Coverage-map entry
`unit-07-semantic-embeddings`, `kind: unit`, `title: "Semantic text embeddings"`, `lessons: 3`,
`introduces: [word-embeddings, document-embeddings, embedding-retrieval]`,
`requires: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics, bag-of-words, tf-idf,
latent-factors]`,
`practices: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics, tf-idf]`.
(All required ids introduced by U1/U3/U5; `tf-idf` (U3) genuinely re-exercised if the book embedding uses IDF
weighting — else drop it and practice `bag-of-words`; confirm in Phase B against the shipped path. `practices ∩
introduces = ∅`; no `project` entry → capstone rule inert; closes under buildout.)

## Phases

### Phase A — registry + syllabus + GloVe derivation & artifact
- `concepts.yaml`: add the 3 ids. `coverage-map.yaml`: add the Unit-7 entry (buildout comment → "twenty-one and a
  half"). `baseline.yaml`: declare new `x.name(...)` methods used by authored cells (e.g. GloVe loader,
  `SemanticEmbeddingRetrievalPath`, numpy `linalg.norm`/`argsort`/`load`… as used).
- `recsys/data/derive_glove_subset.py` (off-CI; gensim via `uv run --with gensim`) + the committed
  `recsys/data/glove/{glove_subset.npy, glove_subset.json}` (float16, checksum, license note). Add a ci-local
  artifact-integrity check (committed `.npy` sha256 == sidecar) as a SKIP-or-real check; wire into the registry/lint
  or curriculum step.
- `unit-07-semantic-embeddings/manifest.yaml`; `syllabus.md` arc row `| 7 | \`unit-07-semantic-embeddings\` | unit |
  3 | <hook> |` after the Checkpoint-A row; rebuild PDF.
**Verify:** manifest/prereq/coverage/syllabus green; buildout holds (21.5<30); concepts unique; GloVe `.npy` loads +
checksum matches; no gensim import on the CI exec path.

### Phase B — `bookrec` semantic path + GloVe loader + measurement (Opus subagent; numpy-only, no gensim/torch)
Dispatch an **Opus subagent**. STUDY `lexical.py` (`LexicalRetrievalPath`, keyword corpus at construction),
`keywords.py` (`load_keywords`), `protocol.py` (`BaseRetrievalPath`, `fit`/`retrieve`/`artifact`/`load`, `_finish`),
`neighborhood.py`/`factorization.py` (conventions), `scoreboard.py`. Add:
- `bookrec/embeddings.py` (or extend `keywords.py`): a `load_glove_subset()` that reads the committed `.npy` + sidecar
  (numpy only, no gensim) → `{token: vector}` / matrix + index; and a `book_embedding(keywords, glove, idf=None)`
  helper (mean or IDF-weighted mean of token vectors, L2-normalized; out-of-vocab tokens skipped; zero-vector-safe).
- `SemanticEmbeddingRetrievalPath(BaseRetrievalPath)` (name `"semantic"`, version `"1"`): keyword corpus + GloVe at
  construction (like `LexicalRetrievalPath`), so `fit(interactions, catalog=None)` stays protocol-substitutable
  (fit may compute IDF over the train corpus and precompute book embeddings; leakage-safe). `retrieve(reader_id,
  context, k)` builds the reader embedding from `context["seen"]` book embeddings (mean, normalized), scores all
  catalog books by cosine, excludes `seen`, top-k via `_finish`; empty seen → `[]`. `load`/`artifact` round-trip the
  book-embedding matrix + ids + params. Deterministic. Export from `__init__`.
- Tests (routed): loads the committed GloVe subset + checksum; a hand-checkable cosine/embedding fixture; the path
  clears the harness floor on `val` and the **measured relation to lexical** (bind to Phase-B numbers, e.g.
  `semantic_hit > floor` AND the stated lexical relation ± tolerance); determinism; empty-seen → `[]`;
  fit→artifact→load identical; registers as `semantic-v1`. numpy-only (no gensim/torch import under `bookrec/`).
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/ -q` green, deterministic, numpy-only; **report the
measured semantic val hit@10 + its relation to lexical/CF so the lesson framing is bound to the shipped data.**

### Phase C — lesson.ipynb (Opus subagent; project-first)
Hook: "two books never share a word but mean the same thing — can we match on *meaning*, not spelling?". From
scratch → reveal: (1) sparse lexical (U3 recap) vs **dense word embeddings** — GloVe vectors, cosine as semantic
similarity (show a few nearest-word examples); (2) compose a **book embedding** from its keyword tokens, a reader
embedding from `seen`, and **brute-force cosine retrieval**; reveal `SemanticEmbeddingRetrievalPath`; (3) score on
`val` — the honest Phase-B story (semantic is a content path comparable to/complementary with lexical, below CF/MF;
show a book semantic finds that lexical misses). **The bridge:** pretrained GloVe here, MF's *learned* factors in U5,
and U8's *learned neural* two-tower next — all dot-product retrievers over embeddings. ASCII only; `rank(exclude=seen)`;
reuse `bookrec`. **Verify:** `exec-lessons` clean (budget); non-empty markdown first cell; `concept-scan` clean.

### Phase D — exercises.ipynb + solutions.ipynb (separate fresh Opus subagents)
≥6 `## Exercise N`; ≥2 `stretch`; exercises NO solutions/outputs; solutions mirror all, clean (fixed seeds), ≥3
non-vacuous asserts. Drill: cosine nearest words; build a book/reader embedding; register the path + read the val
scoreboard honestly vs lexical/CF/MF/random; a semantic-vs-lexical complementarity case. Stretch e.g.: IDF-weighted vs
mean pooling; semantic ∪ lexical candidate overlap; the dot-product-retriever bridge to MF/U8. Taught-before-assessed;
seeded. **Verify:** `hygiene`/`structure`/`cell-lint`/`noexec`; `exec-solutions` clean; `concept-scan` clean.

### Phase E — milestone notebook (Opus subagent)
`recsys/projects/bookrec/milestones/unit-07-semantic-embeddings.ipynb` — fixed-seed demo: load GloVe + build the
semantic path, val scoreboard (hit/precision/NDCG/coverage) vs the other paths with the honest framing, one reader's
semantic recs + a nearest-words illustration, and (optionally) the semantic path added to the U6 blend. Passes
`milestone-check` + `exec-solutions` + `concept-scan`; ≤ budget.

### Phase F — teacher-notes.md (inline)
`## Goals`, `## Pacing` (60–90 min / 2–3 sittings, hook first, all exercises assigned), `## Common mistakes`
(expecting semantic to beat collaborative; treating GloVe cosine as exact; out-of-vocab tokens; forgetting
normalization; leaking val into IDF), `## Discussion prompts` (semantic vs lexical; pretrained vs learned embeddings →
U8; when does meaning-match help?), `## Differentiation`.

### Phase G — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN with Units 1–7 + Checkpoint A + the Unit-7 milestone + the GloVe
artifact-integrity check AND `bash scripts/pre-merge-guard.sh --pr` OK. buildout holds (21.5). Confirm no gensim on
the CI exec path and the committed `.npy` stays a few MB.

## Out of scope
No PyTorch/neural two-tower (U8); no ANN/FAISS (U10 — retrieval is exact brute-force here); no feature/cold-start
towers (U9); no generator change; no `projects/project-*` entry (capstone=U14); no Checkpoint B (U13); no buildout
removal; gensim is derivation-only (never on the CI exec path).

## Verification phase declared
Phase G is this plan's named verification phase.

## Plan Review

### Round 1 (on v1)

**[self] — APPROVE.** Registry closes: `requires` ⊆ U1 (retrieve-then-rank/catalog-search/offline-evaluation/
top-k-ranking-metrics) + U3 (bag-of-words/tf-idf) + U5 (latent-factors), all introduced; `practices ∩ introduces = ∅`;
buildout 21.5<30 (Checkpoint A 0.5 counted). GloVe artifact is publish-safe (PDDL/Apache, vocab-restricted float16
.npy, checksum, committed-not-gitignored; gensim derivation OFF the CI exec path — design §6/§7 pre-authorize it).
The semantic-path accuracy claim is **conditional + measure-first** (the U3/U5/U6 discipline), framed as a content
path complementary to lexical, not beating collaborative CF/MF. Phase B is protocol-substitutable
(keyword+GloVe at construction, like `LexicalRetrievalPath`). Named Phase G; project-first; ≥6/≥2-stretch/≥3-asserts;
teacher-notes; milestone. numpy-only (torch is U8; ANN is U10 — no scope creep). Open items for the gate/Phase B: (a)
the empirical strength of GloVe-averaged embeddings (the premise — [fable] is probing it); (b) `tf-idf` in
requires/practices is legitimate only if the book embedding uses IDF weighting (else swap to `bag-of-words`); (c) the
GloVe checksum/artifact-integrity ci-local check is small new tooling (confirm it piggybacks cleanly). No [self]
blockers.

_([sol] + [fable] round-1 verdicts appended on hand-back.)_

## Content Review

<!-- appended pre-PR -->

## Post-Execution Report

<!-- appended before ship -->
