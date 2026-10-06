# Plan recsys-011 — Unit 9: Feature towers and item cold-start

**Design:** `docs/designs/011-recsys-book.md` (§7 libraries/determinism/ceilings, §8 row 9, §8 cold-start thread
U6→U9→U13, §9 CI budget). **Book:** `recsys` (Book 3). **Autopilot** per AGENTS.md. Third Part-2 unit, on the Units
1–8 substrate. Extends **U8's two-tower** (PyTorch): the item tower stops being a bare per-id `nn.Embedding` and
becomes a **feature tower** that combines an id embedding with **content features** (genre, author, and the U7 GloVe
keyword embedding), so a **cold item** (no train interactions) still gets a meaningful vector from its features —
**where the cold-start thread previewed in U6 is finally taught and assessed.** Also teaches **hard negatives**
(sampling informative negatives instead of uniform). Still PyTorch/CPU-deterministic. No ANN (U10). No generator change.

## Scope
**Unit 9** (`recsys/units/unit-09-feature-towers/`). Teaches: (1) **feature towers** — the item tower = an id
embedding ⊕ learned embeddings of the book's **genre(s)** and **author**, ⊕ its **GloVe keyword** vector (U7),
projected to the shared dim; the reader tower stays id-based; score = dot product; (2) **item cold-start** — a book
with zero train positives has a useless id embedding, but its feature embedding still places it sensibly, so the
feature-tower path can surface cold items the ID-only U8 two-tower and CF never reach; (3) **hard negatives** —
sampling negatives that are harder than uniform (e.g. popular or feature-similar items) to sharpen training. Ships a
`FeatureTowerRetrievalPath` in `bookrec` (torch, lazy like U8) + a Unit-9 milestone. No ANN/FAISS (U10); no reranker
(U11); no sequence model (U12).

## Determinism & budget (per U8 pattern — binding)
Same CPU-determinism contract as U8 (`torch.manual_seed` + `use_deterministic_algorithms(True)` + single-thread,
SAVED/RESTORED around `fit`; torch imported LAZILY inside `fit` only; `retrieve`/`load`/`artifact` torch-free on numpy
weights; the group-free suite never imports torch — reuse/extend U8's import-blocked-subprocess test). Determinism
GATE = identical top-k ranking + `allclose` (design §184, never exact-float). Tiny/fast: a feature tower is only
modestly larger than U8's; pin dims/epochs so each fit stays well under the 120 s/cell cap and the ≥2×/CI budget holds
— Phase B reports the measured per-fit time + aggregate fit count (as U8 did; ~15–30 s/fit expected).

## Why this works on the data (empirical — MUST be measured in Phase B before the lesson claims anything)
The win is **cold-item reach**, not necessarily a warm-hit record. The committed data has **~818 cold items** (zero
train positives) that CF and the ID-only two-tower can NEVER surface (no learned signal). A feature tower gives each
cold item a vector from its genre/author/GloVe features, so it CAN be recommended. Phase B MUST measure and bind the
lesson honestly to BOTH:
- **Warm hit@10** (seed, k=10, 60 cold readers excluded): should stay in the neighbourhood of U8's two-tower (~0.34)
  — feature towers must NOT materially tank warm accuracy to count as a win.
- **Cold-item reach** — a cold-item metric (e.g. cold-item catalog coverage in top-k, or hit@k restricted to readers
  whose relevant set includes cold items) that the feature tower IMPROVES over the ID-only two-tower / CF (which score
  ~0 there). This is the unit's headline — the first path that meaningfully serves cold items.
- **Hard negatives**: measure whether hard-negative sampling helps/hurts vs uniform (honest either way — it may be a
  "sharpens but risks false negatives" lesson). Pre-declare the Phase-B gate from the measurement; reviewers verify
  empirically. If the feature tower can't beat the ID-only path on a cold metric, that is a plan-changing finding.

## Buildout
Whole-book `lessons` total becomes **27.5** (U1–U9 at 3 each = 27 + Checkpoint A 0.5) < 30 → `buildout: true`
retained. (The NEXT unit, U10, pushes it to 30.5 ≥ 30 — **recsys-012/U10 removes `buildout`**, not this plan.)

## Audience & retained laws
Advanced baseline (design 011). Retained in full: project-first; taught-before-assessed (feature-towers/
item-cold-start/hard-negatives introduced + practiced here; cold-start is now legitimately assessed — it is taught in
THIS unit); student notebooks NO solutions/outputs; solutions + milestone run clean (fixed seeds, deterministic
torch); teacher-notes; from-scratch→reveal; a stretch exercise. CPU-deterministic; routed `--group recsys`; within
budget.

## Concepts introduced (3) — `concepts.yaml`
- `feature-towers` — a two-tower whose item side combines an id embedding with learned **content-feature** embeddings
  (genre, author, GloVe keyword vector) projected to the shared space. `kind: technique`, `category: techniques`.
- `item-cold-start` — recommending items with zero interaction history via their features (the ID-only towers +
  CF cannot); the cold-start thread from U6, now solved for items. `kind: technique`, `category: techniques`.
- `hard-negatives` — sampling informative (popular / feature-similar) negatives instead of uniform, and the
  false-negative risk it introduces. `kind: technique`, `category: techniques`.
All three globally unique (confirm 0 hits across `*/curriculum/concepts.yaml` in Phase A).

### Coverage-map entry
`unit-09-feature-towers`, `kind: unit`, `title: "Feature towers and item cold-start"`, `lessons: 3`,
`introduces: [feature-towers, item-cold-start, hard-negatives]`,
`requires: [retrieve-then-rank, offline-evaluation, top-k-ranking-metrics, beyond-accuracy, implicit-feedback,
latent-factors, embedding-retrieval, two-tower, bpr-loss, neural-training, word-embeddings]`,
`practices: [retrieve-then-rank, offline-evaluation, top-k-ranking-metrics, beyond-accuracy, implicit-feedback,
two-tower, neural-training, word-embeddings]`.
(All required ids introduced by U1/U4/U5/U6/U7/U8. `beyond-accuracy` (U6 coverage) re-exercised for the cold-item
reach metric; `two-tower`/`neural-training`/`word-embeddings` re-exercised (feature tower extends the two-tower and
uses GloVe). `practices ∩ introduces = ∅`; no `project` entry → capstone rule inert; closes under buildout.)

## Phases

### Phase A — registry + syllabus
- `concepts.yaml`: add the 3 ids. `coverage-map.yaml`: add the Unit-9 entry (buildout comment → "twenty-seven and a
  half"). `baseline.yaml`: declare any new `x.name(...)` methods the authored cells use (e.g. torch `cat`/`Linear`/
  `Parameter` if used; `FeatureTowerRetrievalPath`; feature accessors).
- `unit-09-feature-towers/manifest.yaml`; `syllabus.md` arc row `| 9 | \`unit-09-feature-towers\` | unit | 3 | <hook>
  |` after the U8 row; rebuild PDF.
**Verify:** manifest/prereq/coverage/syllabus green; buildout holds (27.5<30); concepts unique.

### Phase B — `bookrec` feature-tower path (Opus subagent; PyTorch, lazy, CPU-deterministic)
Dispatch an **Opus subagent**. STUDY `two_tower.py` (the base to extend — lazy torch, BPR, determinism save/restore,
torch-free retrieve/load/artifact), `embeddings.py`/`load_glove_subset` (GloVe keyword vectors), `catalog.py`/
`Book` (genre/author fields), `protocol.py`, `scoreboard.py`. Add `bookrec/feature_tower.py` (torch lazy in `fit`):
- `FeatureTowerRetrievalPath(BaseRetrievalPath)` (name `"feature-tower"`, version `"1"`). Item tower = id embedding ⊕
  genre-embedding(s) ⊕ author-embedding ⊕ a projection of the book's GloVe keyword vector, combined (concat→Linear, or
  sum) to the shared dim; reader tower = id embedding. BPR + Adam + weight_decay (reuse U8's recipe). `fit(interactions,
  catalog=None)` — EXACT protocol; builds the feature maps from the catalog (so EVERY catalog item, incl. cold ones,
  has a feature vector); leakage-safe. `retrieve` scores all catalog books by the reader·item dot product using numpy
  weights (torch-free), excludes seen; a **cold item still scores** (feature-based); a reader with no learned embedding
  → `[]`. **Hard negatives**: a `hard_negatives`/`negative_strategy` knob (uniform vs popular/feature-similar);
  default from the Phase-B measurement. `load`/`artifact` torch-free. Deterministic. Export (no eager torch).
- Tests (routed): warm hit@10 bound to the measured number (≈ U8's ~0.34 within a stated tolerance — must not tank);
  a **cold-item-reach** assertion (feature tower surfaces cold items / improves a cold metric vs the ID-only two-tower
  which scores them ~0); determinism (ranking + allclose); hard-negative effect recorded; empty-seen/unknown-reader
  contract; fit→artifact→load identical (torch-free); registers as `feature-tower-v1`. EXTEND U8's import-blocked
  subprocess test to cover `feature_tower` too.
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/ -q` green + group-free suite imports no torch;
**report warm hit@10, the cold-item-reach numbers (feature-tower vs ID-only two-tower / CF), the hard-negative effect,
and per-fit time + aggregate fit count** so the lesson is data-bound and in budget.

### Phase C — lesson.ipynb (Opus subagent; project-first)
Hook: "our best recommender (U8) can't recommend a book nobody has read yet — 818 of them. Can features fix that?".
From scratch → reveal: (1) the cold-item problem made concrete (ID-only two-tower / CF score cold items ~0); (2) the
**feature tower** — give the item tower genre/author/GloVe inputs so a cold book gets a vector from what it IS; build
it in PyTorch extending U8; (3) **hard negatives** — uniform vs harder negatives and the false-negative caveat; reveal
`FeatureTowerRetrievalPath`; score on `val` — warm hit stays ≈ U8 (~0.34) AND cold-item reach jumps (the honest
Phase-B story: the first path that serves cold items). **The bridge:** features close the cold-start gap U6 flagged;
U10 makes retrieval fast (ANN), U11 reranks, U13 revisits cold-start in the ethics/beyond-accuracy thread. ASCII only;
`rank(exclude=seen)`; reuse `bookrec`; tiny/seeded/in-budget.
**Verify:** `exec-lessons` clean (budget); non-empty markdown first cell; `concept-scan` clean.

### Phase D — exercises.ipynb + solutions.ipynb (separate fresh Opus subagents)
≥6 `## Exercise N`; ≥2 `stretch`; exercises NO solutions/outputs; solutions mirror all, clean (fixed seeds,
deterministic), ≥3 non-vacuous asserts. Drill: build an item feature vector from genre/author/GloVe; train/register
`FeatureTowerRetrievalPath`; read the val scoreboard (warm ≈ U8) AND a cold-item-reach metric (feature tower vs ID-only
two-tower / CF); show a specific cold book the feature tower surfaces that U8/CF cannot. Stretch e.g.: ablate the
feature inputs (id-only vs +genre vs +author vs +GloVe); uniform vs hard negatives; the warm-vs-cold trade. Taught-
before-assessed (cold-start IS taught here); seeded. **Verify:** `hygiene`/`structure`/`cell-lint`/`noexec`;
`exec-solutions` clean (budget); `concept-scan` clean.

### Phase E — milestone notebook (Opus subagent)
`recsys/projects/bookrec/milestones/unit-09-feature-towers.ipynb` — fixed-seed demo: train + register
`FeatureTowerRetrievalPath`; val scoreboard vs the other paths (warm ≈ U8) + the **cold-item-reach** table (feature
tower lifts cold coverage/hit where ID-only two-tower / CF are ~0); one cold book surfaced via features; optionally the
feature tower in the U6 blend. Passes `milestone-check` + `exec-solutions` + `concept-scan`; ≤ budget; no `split="test"`.

### Phase F — teacher-notes.md (inline)
`## Goals`, `## Pacing` (60–90 min / 2–3 sittings, hook first, all exercises), `## Common mistakes` (expecting a warm
hit@10 record — the win is cold reach; non-determinism; hard negatives sampling true positives as negatives;
leaking val; forgetting cold items need features not an id embedding), `## Discussion prompts` (why id embeddings fail
cold items; what features best predict taste here; hard-negative trade-offs; cold-start thread U6→U9→U13),
`## Differentiation`.

### Phase G — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN with Units 1–9 + Checkpoint A + the Unit-9 milestone AND
`bash scripts/pre-merge-guard.sh --pr` OK. buildout holds (27.5<30). Confirm CPU-determinism, no torch on the
group-free path, and the feature-tower exec (≥2×/CI) stays within the whole-book CI budget.

## Out of scope
No ANN/FAISS (U10 — exact brute-force retrieval here; U10 removes `buildout`); no learned reranker (U11); no sequence
model (U12); no generator change; no `projects/project-*` entry (capstone=U14); no Checkpoint B (U13); no GPU.

## Verification phase declared
Phase G is this plan's named verification phase.

## Plan Review

<!-- round 1 appended -->

## Content Review

<!-- appended pre-PR -->

## Post-Execution Report

<!-- appended before ship -->
