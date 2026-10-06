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
- **Source:** `glove-wiki-gigaword-100` (Wikipedia-2014 + Gigaword-5, uncased, 400k vocab × 100-dim). The vector
  **data** is licensed **PDDL-1.0** (gensim-data metadata; `http://opendatacommons.org/licenses/pddl/`) — distinct
  from the GloVe *software*'s Apache-2.0. A vocabulary-restricted subset (~0.12 MB) is redistributable/publish-safe —
  **unlike the ISBNdb catalog, GloVe carries no license/PII blocker** (design §6 pre-authorizes it).
- **Derivation (OFF the CI exec path, GENSIM-FREE):** `recsys/data/derive_glove_subset.py` **streams the cached
  `~/gensim-data/glove-wiki-gigaword-100/glove-wiki-gigaword-100.gz`** (plain text) with `gzip` + `str.split` — NO
  gensim needed (the probe confirmed it), removing the `uv run --with gensim` footgun. It restricts to the recsys-004
  slice vocabulary (`recsys/data/vocabulary.py` — `vocabulary`/`GENERAL_POOL`/`GENRE_WORDBANKS`), in fixed order, and
  writes a **float16 `.npy`** `(n_vocab, 100)` + a `.json` sidecar: row→token index, dim, source dataset name, the
  **upstream gensim-data artifact id + its checksum**, the derived-`.npy` **sha256**, the **PDDL-1.0 license note +
  Stanford URL**, and `missing: ["starfall"]` (the one OOV vocab word). **OOV handling (decided HERE, Phase A, so the
  artifact is final):** OOV words get a zero row, are listed in `missing`, and are skipped at pooling.
- **Committed (tracked, NOT gitignored — `.gitignore` ignores only `recsys/data/generated/`):** the `.npy` + sidecar
  live under `recsys/data/glove/` and ARE committed (the reproducible embedding artifact). A **real, executed** ci-local
  integrity check (NOT a skip) verifies the committed `.npy` matches the sidecar sha256 AND is `< 1 MB`, mirroring the
  catalog checksum discipline.

## Why this works on the data (empirical, MEASURED — [fable] probe round 1; Phase B re-confirms on shipped code)
The recsys-004 keywords are latent-correlated, so a GloVe-averaged book embedding carries real taste signal — but
**less than the sparse lexical path**. Measured (seed 0, k=10, 60 cold readers excluded, 500 val readers):
random 0.012, lexical BM25 **0.158**, **semantic (mean pooling) 0.102** (recall 0.051, NDCG 0.033), IDF-weighted
0.098 (IDF does NOT help here), max-sim-over-seen 0.142. GloVe covers **607/608** vocab words (`starfall` missing).

**Honest, binding framing:** semantic is a **content path well above the random floor (~8.5×) but BELOW lexical
(~0.102 vs 0.158, ≈65%)** — NOT "comparable within noise", and nowhere near the collaborative CF/MF paths
(0.25/0.276). Its value is **complementarity, not raw accuracy**: the lexical-vs-semantic top-10 overlap is only
**0.22**, so GloVe relates books by *word meaning* where BM25 needs *shared surface tokens* — semantic surfaces
candidates lexical misses, and adding it to the U6 blend is the quantitative complementarity test (Phase B).
**Why it underperforms lexical here (teach this):** the 32 latent-pole topics are *arbitrary contiguous slices* of
`GENERAL_POOL` (`vocabulary.py`), so GloVe's semantic geometry is uncorrelated-by-construction with the latent taste
structure; only the 12 genre banks carry GloVe-exploitable meaning. On a real catalog's prose, dense-semantic would
fare differently — the unit teaches the *method* honestly, not a staged win.
**Pooling is a documented decision:** mean pooling is the pedagogically clean default (shipped); max-sim-over-seen
(0.142) is a natural stretch exercise. Phase-B test binds `semantic_hit > 5 × floor` AND
`0.5 × lexical ≤ semantic ≤ 1.1 × lexical` (direction + band, like `test_unit03.py`), plus the overlap/blend-ablation
complementarity number — reviewers re-verify on the shipped code, not a scratch script.

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
`requires: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics, bag-of-words,
latent-factors, ranking-metrics, score-blending]`,
`practices: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics, bag-of-words]`.
(All required ids introduced by U1/U3/U5/U6. **`tf-idf` dropped** — the shipped book embedding is MEAN pooling (IDF
measured not to help), so IDF is not re-exercised; `bag-of-words` (U3) IS re-exercised as the token representation the
embedding composes. `ranking-metrics` + `score-blending` (U6) are in `requires` because the milestone reports
precision/NDCG and adds semantic to the U6 blend (the complementarity measurement); they are introduced in U6 and
practiced by Checkpoint A, so no coverage gap. `practices ∩ introduces = ∅`; no `project` entry → capstone rule inert;
closes under buildout.)

## Phases

### Phase A — registry + syllabus + GloVe derivation & artifact
- `concepts.yaml`: add the 3 ids. `coverage-map.yaml`: add the Unit-7 entry (buildout comment → "twenty-one and a
  half"). `baseline.yaml`: declare new `x.name(...)` methods used by authored cells (e.g. GloVe loader,
  `SemanticEmbeddingRetrievalPath`, numpy `linalg.norm`/`argsort`/`load`… as used).
- `recsys/data/derive_glove_subset.py` (off-CI, **gensim-free**: stream the cached `.gz` with `gzip`+`str.split`) +
  the committed `recsys/data/glove/{glove_subset.npy, glove_subset.json}` (float16; sidecar carries row→token index,
  dim, upstream gensim-data artifact id + checksum, derived-`.npy` sha256, **PDDL-1.0** license note + Stanford URL,
  and `missing: ["starfall"]`). **OOV decided here:** zero row, listed in `missing`, skipped at pooling (so the
  artifact/checksum are final before Phase B). Add a **real, executed** ci-local integrity check (committed `.npy`
  sha256 == sidecar AND size `< 1 MB`) — NOT a skip — wired into the registry/lint step.
- `unit-07-semantic-embeddings/manifest.yaml`; `syllabus.md` arc row `| 7 | \`unit-07-semantic-embeddings\` | unit |
  3 | <hook> |` after the Checkpoint-A row; rebuild PDF.
**Verify:** manifest/prereq/coverage/syllabus green; buildout holds (21.5<30); concepts unique; GloVe `.npy` loads +
checksum matches + `< 1 MB`; no gensim import anywhere (derivation included).

### Phase B — `bookrec` semantic path + GloVe loader + measurement (Opus subagent; numpy-only, no gensim/torch)
Dispatch an **Opus subagent**. STUDY `lexical.py` (`LexicalRetrievalPath`, keyword corpus at construction),
`keywords.py` (`load_keywords`), `protocol.py` (`BaseRetrievalPath`, `fit`/`retrieve`/`artifact`/`load`, `_finish`),
`neighborhood.py`/`factorization.py` (conventions), `scoreboard.py`. Add:
- `bookrec/embeddings.py` (or extend `keywords.py`): a `load_glove_subset()` that reads the committed `.npy` + sidecar
  (numpy only, no gensim) → `{token: vector}` / matrix + index; and a `book_embedding(keywords, glove)` helper
  (**MEAN of token vectors, L2-normalized** — the shipped default; IDF measured not to help; OOV tokens skipped;
  zero-vector-safe).
- `SemanticEmbeddingRetrievalPath(BaseRetrievalPath)` (name `"semantic"`, version `"1"`): keyword corpus + GloVe at
  construction (like `LexicalRetrievalPath`), so `fit(interactions, catalog=None)` stays protocol-substitutable
  (fit may compute IDF over the train corpus and precompute book embeddings; leakage-safe). `retrieve(reader_id,
  context, k)` builds the reader embedding from `context["seen"]` book embeddings (mean, normalized), scores all
  catalog books by cosine, excludes `seen`, top-k via `_finish`; empty seen → `[]`. `load`/`artifact` round-trip the
  book-embedding matrix + ids + params. Deterministic. Export from `__init__`.
- Tests (routed): loads the committed GloVe subset + verifies its sidecar sha256; a hand-checkable cosine/embedding
  fixture; the path clears the floor and sits in the measured band — **`semantic_hit > 5 × floor` AND
  `0.5 × lexical ≤ semantic_hit ≤ 1.1 × lexical`** (measured ≈0.102 vs lexical 0.158); determinism; empty-seen → `[]`;
  fit→artifact→load identical; registers as `semantic-v1`. numpy-only (no gensim/torch import under `bookrec/`).
- **Complementarity measurement (binds [sol]#3 / [fable]#1,#3):** compute the lexical-vs-semantic top-10 overlap
  (measured ≈0.22) AND a blend-ablation — the U6 blend WITH vs WITHOUT the semantic path (hit@10 + coverage) — so the
  lesson's "complementary" claim is quantitative, not a single example. Report both.
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/ -q` green, deterministic, numpy-only; **report the
measured semantic val hit@10, the lexical overlap, and the blend-with-semantic ablation so the lesson/milestone
framing is bound to the shipped data (not [fable]'s scratch probe).**

### Phase C — lesson.ipynb (Opus subagent; project-first)
Hook: "two books never share a word but mean the same thing — can we match on *meaning*, not spelling?". From
scratch → reveal: (1) sparse lexical (U3 recap) vs **dense word embeddings** — GloVe vectors, cosine as semantic
similarity (show a few nearest-word examples, **labelled "nearest among the catalog's 607-word vocabulary"** — not
full-GloVe analogies, which the committed subset can't produce); (2) compose a **book embedding** = MEAN of its
keyword tokens' GloVe vectors (L2-normalized), a reader embedding from `seen`, and **brute-force cosine retrieval**;
reveal `SemanticEmbeddingRetrievalPath`; (3) score on `val` — the HONEST Phase-B story: semantic (~0.102) beats the
floor ~8.5× but is **below** lexical (0.158), far below CF/MF — its value is **complementarity** (lexical overlap
only ~0.22; semantic surfaces books lexical misses; adding it to the U6 blend is the quantitative demo). **Teach WHY
it's below lexical:** our synthetic topic vocabulary is arbitrary `GENERAL_POOL` slices, so GloVe's meaning-geometry
is uncorrelated-by-construction with the latent taste (only the 12 genre banks help); on a real catalog's prose dense
semantics would fare differently — we teach the *method* honestly. **The bridge:** pretrained GloVe here, MF's
*learned* factors (U5), U8's *learned neural* two-tower next — all dot-product retrievers over embeddings. ASCII only;
`rank(exclude=seen)`; reuse `bookrec`. **Verify:** `exec-lessons` clean (budget); non-empty markdown first cell;
`concept-scan` clean.

### Phase D — exercises.ipynb + solutions.ipynb (separate fresh Opus subagents)
≥6 `## Exercise N`; ≥2 `stretch`; exercises NO solutions/outputs; solutions mirror all, clean (fixed seeds), ≥3
non-vacuous asserts. Drill: cosine nearest words; build a book/reader embedding; register the path + read the val
scoreboard honestly vs lexical/CF/MF/random; a semantic-vs-lexical complementarity case. Stretch e.g.: IDF-weighted vs
mean pooling; semantic ∪ lexical candidate overlap; the dot-product-retriever bridge to MF/U8. Taught-before-assessed;
seeded. **Verify:** `hygiene`/`structure`/`cell-lint`/`noexec`; `exec-solutions` clean; `concept-scan` clean.

### Phase E — milestone notebook (Opus subagent)
`recsys/projects/bookrec/milestones/unit-07-semantic-embeddings.ipynb` — fixed-seed demo: load GloVe + build the
semantic path, val scoreboard (hit/precision/NDCG/coverage) vs the other paths with the honest "below lexical,
complementary" framing, one reader's semantic recs + a nearest-words illustration (vocabulary-scoped), the
lexical-overlap number (~0.22), AND the semantic path added to the U6 blend (the complementarity ablation — this is
why `ranking-metrics`+`score-blending` are in `requires`). Passes `milestone-check` + `exec-solutions` +
`concept-scan`; ≤ budget; no `split="test"`.

### Phase F — teacher-notes.md (inline)
`## Goals`, `## Pacing` (60–90 min / 2–3 sittings, hook first, all exercises assigned), `## Common mistakes`
(expecting semantic to beat lexical/collaborative — it is BELOW lexical here; **reading that as "embeddings are
worse" rather than a synthetic-corpus artifact** — the arbitrary topic vocabulary means GloVe meaning is
uncorrelated-by-construction with latent taste, a real catalog differs; treating GloVe cosine as exact; out-of-vocab
tokens; forgetting L2-normalization), `## Discussion prompts` (semantic vs lexical, and why overlap is only ~0.22;
pretrained vs learned embeddings → U8; when would meaning-match help on a REAL corpus?), `## Differentiation` (stretch:
max-sim pooling 0.142 > mean 0.102).

### Phase G — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN with Units 1–7 + Checkpoint A + the Unit-7 milestone + the GloVe
artifact-integrity check (real, executed: sha256 matches sidecar AND `.npy` `< 1 MB`) AND `bash
scripts/pre-merge-guard.sh --pr` OK. buildout holds (21.5). Confirm no gensim import anywhere (derivation included)
and the committed `.npy` is ~0.1–0.2 MB.

## Out of scope
No PyTorch/neural two-tower (U8); no ANN/FAISS (U10 — retrieval is exact brute-force here); no feature/cold-start
towers (U9); no generator change; no `projects/project-*` entry (capstone=U14); no Checkpoint B (U13); no buildout
removal; **gensim is not used at all** (the derivation streams the `.gz` gensim-free; notebooks load the committed
`.npy` with numpy).

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

**[sol] — APPROVE WITH NITS** (3 nits, no Must). Registry/governance/empirical-discipline sound.
1. `[OPEN]` **Should** — sidecar must pin the UPSTREAM gensim artifact version + checksum (not only the derived
   `.npy` checksum); and distinguish the vector DATA's PDDL license from the GloVe SOFTWARE's Apache-2.0 (still
   publish-safe). (Phase A.)
2. `[OPEN]` **Should** — remove the "SKIP-or-real" ambiguity: this plan SHIPS the committed artifact, so its
   checksum/integrity check must be implemented + executed (real), never skipped. (Phase A/G.)
3. `[OPEN]` **Nice** — bind the "complementary to lexical" claim to a QUANTITATIVE overlap/unique-hit or
   blend-ablation measurement in Phase B (not a single lesson example). (Phase B/C.)

**[fable] — APPROVE WITH NITS** (8 nits, no Must; **ran a real GloVe probe**). Measured (seed 0, k=10, 500 val):
random 0.012, lexical 0.158, **semantic mean-pooling 0.102** (recall 0.051, NDCG 0.033), IDF-weighted 0.098 (does
NOT help), **max-sim-over-seen 0.142**. GloVe covers **607/608** vocab words (only `starfall` missing); subset
**~0.12 MB**; lexical-vs-semantic top-10 overlap **0.22** (complementarity real). Premise HOLDS but semantic is
**below lexical** (~65%), far above floor (8.5×). Derivation needs NO gensim (stream the `.gz` with `gzip`+`str.split`).
1. `[OPEN]` **Should** — pre-bind the MEASURED branch in "Why this works": ~0.102 (65% of lexical, 8.5× floor), below
   lexical (not "comparable within noise"); Phase-B test = `semantic_hit > 5×floor` AND `0.5×lexical ≤ semantic ≤
   1.1×lexical` (direction+band); document pooling (mean = clean default; max-sim 0.142 = stretch).
2. `[OPEN]` **Should** — synthetic-vocabulary honesty: the 32 latent-pole topics are arbitrary contiguous
   `GENERAL_POOL` slices, so GloVe "meaning" is UNCORRELATED with the latent structure by construction; only the 12
   genre banks carry GloVe-exploitable semantics → semantic underperforms lexical here partly as a synthetic artifact,
   a real catalog would differ. Lesson + teacher-notes MUST say this.
3. `[OPEN]` **Should** — requires closure: the milestone prints precision/NDCG (`ranking-metrics`) and adds semantic
   to the U6 blend (`score-blending`); add both to the coverage-map `requires` (both U6-introduced, closure holds).
4. `[OPEN]` **Should** — decide OOV handling in Phase A (zero vector, recorded in sidecar `missing: ["starfall"]`,
   skipped at pooling) so the committed artifact/checksum isn't re-cut after Phase B.
5. `[OPEN]` **Nice** (+[sol]#1) — license is **PDDL-1.0** (gensim-data metadata), NOT Apache-2.0; sidecar `license`
   = PDDL-1.0 + Stanford URL + "Wikipedia 2014 + Gigaword 5, uncased, 100-d".
6. `[OPEN]` **Nice** — size ~0.1–0.2 MB (not "a few MB"); Phase G integrity check adds a hard cap `< 1 MB`.
7. `[OPEN]` **Nice** — nearest-word demo must be labelled "nearest among the catalog's vocabulary" (607-word subset),
   not full-GloVe analogies.
8. `[OPEN]` **Nice** — make `derive_glove_subset.py` **gensim-free** (stream the `.gz`), removing the `uv run --with
   gensim` footgun entirely (the probe proved it works).

### Plan-review outcome (round 1): **CONSENSUS — [self] APPROVE · [sol] APPROVE WITH NITS · [fable] APPROVE WITH NITS; no Must/REJECT.** [fable]'s probe grounds the empirics (semantic 0.102, below lexical, complementary at 0.22 overlap). Folding all 11 nits → **v2** (measured "below-lexical" branch + band test; synthetic-vocab honesty; +ranking-metrics/score-blending requires; gensim-free derivation; PDDL license; OOV in Phase A; <1 MB cap; nearest-word scoping), then build — no round-2 needed (nits only).

### v2 (nits folded — plan-review CONSENSUS, no round-2 needed)
All 11 nits applied: "Why this works" now states the MEASURED below-lexical result (0.102 vs 0.158, 8.5× floor) + the
`0.5×lexical ≤ semantic ≤ 1.1×lexical` band test [fable#1]; synthetic-vocabulary honesty added to Why/Phase C/F
[fable#2]; `ranking-metrics`+`score-blending` added to `requires`, `tf-idf`→`bag-of-words` (mean pooling, no IDF)
[fable#3]; OOV decided in Phase A (zero row, `missing:["starfall"]`, skip at pooling) [fable#4]; PDDL-1.0 license +
upstream checksum in sidecar [fable#5/sol#1]; ~0.12 MB + `<1 MB` hard cap [fable#6]; nearest-word demo
vocabulary-scoped [fable#7]; **derivation gensim-free** (stream the `.gz`) [fable#8]; integrity check REAL+executed,
not skipped [sol#2]; complementarity bound to overlap (~0.22) + blend-ablation [sol#3]. Plan-review consensus stands
([self] APPROVE + [sol]/[fable] APPROVE WITH NITS, all nits resolved). Proceed to build (Phase A → G).

## Content Review

### Round 1 — [self] (2026-10-05)
- **Verdict**: APPROVE WITH NITS. Project-first (all notebooks open with the meaning-vs-spelling hook); honest framing
  consistent everywhere (semantic 0.102 BELOW lexical 0.158, 8.5× floor, value = complementarity with overlap 0.216 +
  blend lift, synthetic-vocab caveat — nothing overclaims); blend-ablation config unified to the Unit-6 PINNED blend
  (pool 30; WITHOUT 0.306/0.333 → WITH semantic@0.5 0.316/0.353) across lesson/exercises/solutions/milestone after
  reconciling the milestone off its equal-weight pool-50 draft; taught-before-assessed (word-embeddings/
  document-embeddings/embedding-retrieval introduced; no borrowed tools); NO `split="test"` in any Unit-7 notebook;
  nearest-word demos vocabulary-scoped; GloVe artifact gensim-free, PDDL-1.0 note, 0.122 MB, real integrity check.
  Nit already caught + fixed in-build: a milestone `FURB192`/import-order class of ruff issue (ruff lints milestones).
No open [self] blockers.

### Round 1 — [fable] (2026-10-05)
- **Verdict**: APPROVE WITH NITS (no Must). Blind-solved Ex1/2/4/5/6/7; solutions match; honest framing + pinned-blend
  config + no-`split=test` + GloVe governance all confirmed consistent.
1. `[OPEN]` **Should** — milestone §5 (cell 10) OVERCLAIMS: says reader 3's recs "share *meaning*" with seen books,
   but the output shows grab-bag keyword sets sharing 6–10 SURFACE tokens and uniformly high cosines (mean pairwise
   book-embedding cosine ~0.66 vs ~0.12 for words — mean-pooling collapses toward a centroid). Reword to the honest
   "grab-bags + uniformly high cosines = the uncorrelated-by-construction point; genre-bank words are where GloVe
   meaning shows" (or pick a genre-heavy reader and show shared-token counts honestly).
2. `[FIXED-pending]` **Should** — max-sim hit@10 is **0.146** (I re-measured + confirmed), not the stated "~0.142"
   in exercises/solutions (`maxsim_explanation`), teacher-notes, and the plan. Update to ~0.146.
3. `[OPEN]` **Should (minor)** — nearest-word prose skips the actual #1 neighbor (dragon→`lantern` 0.682 is top;
   `magic` is wizard's not dragon's) in lesson cell 5 / exercises cell 2 / milestone cell 5. Add one honest sentence
   that nearest-word lists are noisy (100-d, Wikipedia co-occurrence, 607-word restricted field).
4. `[OPEN]` **Nice** — unused `blend` import in exercises/solutions cell 1 (no CI effect; units aren't ruff'd).
5. `[OPEN]` **Nice** — add the GloVe license (PDDL-1.0) + citation (Pennington, Socher & Manning 2014) to the
   student lesson + teacher-notes (sidecar has it); a short `recsys/data/glove/README.md` would help.
6. `[OPEN]` **Nice** — `embeddings.py` `load()` ignores the artifact `"dim"`; check `embeddings.shape[1]==glove.dim`.
7. `[OPEN]` **Nice** — Ex2 uses `keywords[id].split()`; the lesson/library use `tokenize` (identical here) — prefer
   `tokenize` for robustness-by-construction.
8. `[OPEN]` **Nice** — teacher-notes discussion prompt: the anisotropy number (book-embedding mean cosine ~0.66 vs
   ~0.12 for words) explains why every cosine looks "high" and why max-sim beats mean.

_([sol] content verdict pending — its codex-rescue forwarder launched a background Codex task; re-dispatch if it
doesn't hand back. Then fold [fable]+[sol] nits in one coordinated pass + re-verify.)_

<!-- appended pre-PR -->

## Post-Execution Report

<!-- appended before ship -->
