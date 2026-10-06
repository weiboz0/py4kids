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
feature-tower path reaches cold items the ID-only U8 two-tower and CF bury at ~0; (3) **hard negatives** —
sampling negatives harder than uniform (popularity-weighted) and the false-negative caveat — an **ablation** knob here,
since measured it trades warm accuracy for cold reach rather than sharpening both. **The decisive design choice is the
negative pool:** negatives are drawn from the **warm (train-positive) item universe**, NOT the full catalog — 41% of
the catalog is zero-train, so a full-catalog sampler makes cold items negatives-only and the tower learns to bury them.
Ships a `FeatureTowerRetrievalPath` in `bookrec` (torch, lazy like U8) + a Unit-9 milestone. **Honest headline:**
content paths (U7 semantic / U3 lexical) already serve cold items; the feature tower is the first **learned-taste /
collaborative** path to serve cold items while holding near the book's best warm hit — a warm/cold compromise, not
dominance. No ANN/FAISS (U10); no reranker (U11); no sequence model (U12).

## Determinism & budget (per U8 pattern — binding)
Same CPU-determinism contract as U8 (`torch.manual_seed` + `use_deterministic_algorithms(True)` + single-thread,
SAVED/RESTORED around `fit`; torch imported LAZILY inside `fit` only; `retrieve`/`load`/`artifact` torch-free on numpy
weights; the group-free suite never imports torch — reuse/extend U8's import-blocked-subprocess test). Determinism
GATE = identical top-k ranking + `allclose` (design §184, never exact-float). **Budget caution (measured):** the
feature tower is ~20–27 s/fit at 40 epochs (measured: warm 26.8 s, full 19.3 s, hard 24.5 s; ≈2× U8's ID-only 13 s,
from the extra Linear/feature embeddings); it runs in lesson + solutions + milestone + the test suite, so **Phase B
pinned `n_epochs=40`** (measured warm 0.298 ≥ gate 0.28; cold-coverage 0.138 ≫ ID-only 0) and caps full fits per
notebook (≤2–3). `test_unit09.py` runs 5 full training fits (~132 s file wall time); the AGGREGATE is reported against
the §9 whole-book budget. Each fit stays far under the 120 s/cell cap.

## Why this works on the data (empirical, MEASURED on the SHIPPED tower — Phase B, seed0/dim32/BPR+Adam wd=1e-4/40ep)
The win is **cold-item COVERAGE bought with a small, honest warm cost**, via one decisive design choice — the
**negative pool**. Cold coverage = unique zero-train ids in top-10 / 818, over ALL 540 fitted non-cold readers scored
from TRAIN histories only (validation-free). Warm hit@10 = the ordinary val scoreboard (its held-out-positive cohort);
cold hit = report-only over the 97 incidental-cold-val readers:

| path | warm hit@10 | cold coverage (/818 zero-train) | cold hit@10 (n=97) |
|------|-------------|---------------------------------|--------------------|
| U4 item-item CF | 0.252 | 0.000 (0) | 0.000 |
| U8 ID-only two-tower | 0.340 | 0.000 (0) | 0.000 |
| U7 semantic (content-only) | 0.102 | 0.322 | 0.031 |
| feature tower, **full-catalog negs** | 0.338 | 0.048 (39) | 0.010 |
| feature tower, **warm-only negs (SHIPPED)** | **0.298** | **0.138** (113) | 0.010 |
| feature tower, **hard negs (ablation)** | 0.172 | 0.226 (185) | 0.031 |

**The mechanism (THE lesson):** 41% of the catalog is zero-train, so with U8's uniform-over-the-full-catalog sampler a
cold item is only EVER a negative — the tower **buries** it (cov 0.048). Drawing negatives from the **warm
(train-positive) item universe** lifts cold coverage ~3× to **0.138** (vs 0 for ID-only/CF), at a **small warm cost**
(0.298 vs full-catalog's 0.338 ≈ U8's 0.340). So the knob is an honest **warm↔cold trade**, not a free lunch: "a cold
item that is only ever a negative gets pushed down; features can't rescue it from its own negative gradient — sample
warm-only so features can place it, and pay a few points of warm hit for ~3× cold reach." (This CORRECTS the round-1
60ep probe, which read full-catalog as *tanking* warm; on the shipped sum-composition tower at 40ep full-catalog is the
higher-warm/lower-cold end of the same trade. The cold story — warm-only required for reach, ID-only/CF = 0 — is
unchanged, and the trade-off is a cleaner teaching knob.)

**Metric (validation-safe — [sol]+[fable]):** the designated 150 cold_items have NO val positives (relevance only on
`test`, deferred to Checkpoint B); so the **GATE is cold-item COVERAGE** = `unique zero-train item ids appearing in the
top-10 / 818`, computed over **ALL fitted non-cold readers scored from their TRAIN histories only** (each reader's
train-seen items excluded; NOT the scoreboard's held-out-positive "eligible" cohort — coverage must not depend on who
has a val positive). (ID-only/CF = exactly 0 → "feature-tower cov > 0 and > ID-only" is sound.) The warm-accuracy gate
warm hit@10 ≥ 0.28 (measured 0.298; not tanked — within 0.06 of the ID-only two-tower's 0.340) is the ordinary val
scoreboard over its eligible readers — reported separately. **Report-only:** cold hit@10 on the 97 incidental readers
who DO have a cold val positive (small-n; feature tower 0.010 vs ID-only 0.000) — not a gate. The coverage cohort is
the 540 fitted non-cold readers (train-only), distinct from the val warm-cohort.

**Honest headline (NOT "first to serve cold"):** U7 semantic / U3 lexical content paths ALREADY surface cold items
freely (U7 cov 0.322) — they just ignore interactions. The feature tower is the **first LEARNED-taste/collaborative
path to serve cold items while staying near the book's best warm hit** (0.298 vs semantic's 0.102). It is a
warm/cold **compromise**, not dominance — its cold hit (0.010) is BELOW U7 semantic's (0.031).

**Hard negatives:** measured popularity-weighted hard negatives did NOT sharpen — they **traded warm for cold** harder
(warm 0.298→0.172, cov 0.138→0.226). Default = uniform-over-warm; hard-neg is the ablation/caveat knob ("trades warm accuracy for cold
reach / popularity debias", with the false-negative caveat). Pre-declare the Phase-B gate from these numbers;
reviewers re-verify on the shipped code.

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
  `Parameter` if used; `FeatureTowerRetrievalPath`; feature accessors). NOTE: `arange` is already declared
  (`baseline.yaml:68`) — only add idioms the authored cells newly use.
- `unit-09-feature-towers/manifest.yaml`; `syllabus.md` arc row `| 9 | \`unit-09-feature-towers\` | unit | 3 | <hook>
  |` after the U8 row; rebuild PDF.
**Verify:** manifest/prereq/coverage/syllabus green; buildout holds (27.5<30); concepts unique.

### Phase B — `bookrec` feature-tower path (Opus subagent; PyTorch, lazy, CPU-deterministic)
Dispatch an **Opus subagent**. STUDY `two_tower.py` (the base to extend — lazy torch, BPR, determinism save/restore,
torch-free retrieve/load/artifact), `embeddings.py`/`load_glove_subset` (GloVe keyword vectors), `catalog.py`/
`Book` (genre/author fields), `protocol.py`, `scoreboard.py`. Add `bookrec/feature_tower.py` (torch lazy in `fit`):
- `FeatureTowerRetrievalPath(BaseRetrievalPath)` (name `"feature-tower"`, version `"1"`). **Features come through the
  CONSTRUCTOR** (like `SemanticEmbeddingRetrievalPath(keywords, glove)`): `FeatureTowerRetrievalPath(catalog_books,
  keywords, glove, embedding_dim=32, n_epochs=40, learning_rate=0.01, n_negatives=10, batch_size=256, weight_decay=1e-4,
  negative_pool="warm", seed=0)` — `fit(interactions, catalog=None)` keeps the EXACT protocol signature (`catalog` =
  item-ids iterable, NOT Book records). Item tower = id embedding ⊕ genre-embedding(s) ⊕ author-embedding ⊕ a
  `Linear` projection of the book's GloVe keyword vector, combined to the shared dim; reader tower = id embedding.
  BPR + Adam + weight_decay (reuse U8's recipe; lazy torch). **Negative pool (THE knob): default `negative_pool="warm"`
  — negatives sampled from the TRAIN-POSITIVE item universe, NOT the full catalog** (uniform-full-catalog makes the
  41% zero-train items negatives-only and buries them). `retrieve` scores ALL catalog books by `reader·item` using the
  **composed numpy item matrix stored at fit** (torch-free); a cold item still scores (feature-based); empty `seen` →
  still k recs; unknown reader → `[]`. `artifact`/`load` persist the **composed numpy item matrix + reader matrix +
  ids** (NOT the Linear/Embedding weights — so load/retrieve need no torch and no re-composition). A `negative_pool`
  knob also allows `"hard"` (popularity-weighted) as the ablation. Export (no eager torch).
- Tests (routed): **warm hit@10 ≥ 0.28** (measured 0.298 at 40ep, pinned with headroom + within-0.06-of-ID-only
  assert; never pre-bound to an unmeasured number; must not tank vs U8); **cold-item
  COVERAGE gate** — `feature_tower cold_cov > 0 AND > id_only_cold_cov` over the 818 zero-train items, coverage counted
  over **ALL fitted non-cold readers scored from TRAIN histories only** (train-seen excluded; NOT the scoreboard's
  held-out-positive eligible cohort — no val dependency); ID-only/CF are exactly 0. Report (not gate) cold hit@10 on
  the 97 incidental-cold-val readers; determinism (ranking + allclose,
  array_equal bonus print only); the warm-only-vs-uniform negative-pool effect recorded; empty-seen/unknown-reader
  contract; fit→artifact→load identical, torch-free; registers as `feature-tower-v1`. **EXTEND the import-blocked
  subprocess test** in `recsys/projects/bookrec/tests/test_unit07.py` (`:310` `test_torch_free_paths_do_not_import_torch`
  + the top-level-import scan `:283`) to cover `feature_tower` too.
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/ -q` green + group-free suite imports no torch;
**report warm hit@10 + cold coverage (feature-tower warm-only vs uniform vs ID-only/CF) + report-only cold hit@10 +
the hard-neg ablation + per-fit time + aggregate fit count at the pinned n_epochs** so the lesson is data-bound and in
budget.

### Phase C — lesson.ipynb (Opus subagent; project-first)
Hook: "our best recommender (U8) buries a book nobody has read yet — 818 of them at ~0. Can features fix that?".
From scratch → reveal: (1) the cold-item problem made concrete (ID-only two-tower / CF give zero-train items
negative-shaped id embeddings → coverage 0); (2) the **feature tower** — give the item tower genre/author/GloVe inputs
so a cold book gets a vector from what it IS; build it in PyTorch extending U8; (3) **the negative pool (THE mechanism)**
— show that a full-catalog sampler makes cold items negatives-only (cov 0.048, warm 0.338 ≈ U8) and that **warm-only
negatives** lift cold coverage ~3× to 0.138 at a small warm cost (0.298) — an honest **warm↔cold trade**, not a free
lunch; (4) **hard negatives** — uniform vs popularity negatives and the false-negative caveat, as a harder warm↔cold
trade (warm 0.172 / cov 0.226); reveal `FeatureTowerRetrievalPath`; score on `val` — warm hit stays near U8 (0.298 vs
0.340) AND cold-item **coverage** jumps from 0 (the honest Phase-B story: the first **learned-taste/collaborative**
path to serve cold items — content paths like U7 already do — a compromise, not dominance). **The bridge:** features close the cold-start gap U6 flagged; U10 makes retrieval fast (ANN), U11 reranks,
U13 revisits cold-start in the ethics/beyond-accuracy thread. ASCII only; `rank(exclude=seen)`; reuse `bookrec`;
tiny/seeded/in-budget.
**Verify:** `exec-lessons` clean (budget); non-empty markdown first cell; `concept-scan` clean.

### Phase D — exercises.ipynb + solutions.ipynb (separate fresh Opus subagents)
≥6 `## Exercise N`; ≥2 `stretch`; exercises NO solutions/outputs; solutions mirror all, clean (fixed seeds,
deterministic), ≥3 non-vacuous asserts. Drill: build an item feature vector from genre/author/GloVe; train/register
`FeatureTowerRetrievalPath`; read the val scoreboard (warm ≈ U8) AND the **cold-item COVERAGE** metric over the 818
zero-train items (feature tower > 0 vs ID-only two-tower / CF = 0); show a specific cold book the feature tower
surfaces — pick a **deterministic reader from the 97 incidental-cold-val readers** so the surfaced cold book is one the
reader actually read next. Stretch e.g.: the **negative-pool** knob (warm-only vs full-catalog — warm/cold both move);
ablate the feature inputs (id-only vs +genre vs +author vs +GloVe); uniform vs hard negatives and the warm↔cold trade.
Taught-before-assessed (cold-start IS taught here); seeded. **Verify:** `hygiene`/`structure`/`cell-lint`/`noexec`;
`exec-solutions` clean (budget); `concept-scan` clean.

### Phase E — milestone notebook (Opus subagent)
`recsys/projects/bookrec/milestones/unit-09-feature-towers.ipynb` — fixed-seed demo: train + register
`FeatureTowerRetrievalPath` (warm-only negatives); val scoreboard vs the other paths (warm ≈ U8) + the **cold-item
COVERAGE** table over the 818 zero-train items (feature tower > 0 where ID-only two-tower / CF are exactly 0); one cold
book surfaced via features (deterministic reader); optionally the feature tower in the U6 blend. Passes
`milestone-check` + `exec-solutions` + `concept-scan`; ≤ budget; no `split="test"`.

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

### Round 1 (on v1)

**[self] — APPROVE.** Registry closes: `requires` ⊆ U1/U4/U5/U6/U7/U8 introductions; `practices ∩ introduces = ∅`;
buildout 27.5<30 (U10 removes it, not this plan); concepts unique (confirm Phase A). Empirical claim is conditional +
measure-first — the honest win is **cold-item reach** (the ~818 zero-train-positive items CF/ID-only-two-tower score
~0) with warm hit@10 held ≈ U8's ~0.34, plus an honest hard-negatives readout. torch isolation reuses U8's proven
pattern (lazy `fit`-only import, torch-free load, import-blocked subprocess extended to `feature_tower`), determinism
tolerance-based (§184). cold-start is now legitimately TAUGHT + assessed (U9 introduces `item-cold-start`), resolving
the U6 unassessed-preview thread. Named Phase G; project-first; ≥6/≥2-stretch/≥3-asserts; teacher-notes; milestone.
No scope creep (ANN=U10, reranker=U11, sequence=U12). Open for Phase B/gate: a well-posed **cold-item-reach metric**
([fable] is probing it + the warm-not-tanked check) and the warm-hit tolerance. No [self] blockers.

**[sol] — REJECT** (2 Must; closure/buildout/isolation/taught-before-assessed all confirmed correct):
1. `[OPEN]` **Must** — cold-item reach is ill-defined AND **unmeasurable as hit@k on val**: the generator excludes
   designated cold items from every non-test exposure (`gen_interactions.py:143-149,181-186`), so `val` has NO
   positive rows for cold items, and the scoreboard computes hit@k only from held-out positives — while Phases C–E
   demand the headline on `val` and forbid `test`. → Define ONE validation-safe metric precisely: **cold-item
   COVERAGE** = `unique cold item ids appearing in readers' top-k / cold-item denominator` (needs no cold positives);
   be explicit that cold-item *relevance* can't be scored on val (only the sealed test could, at Checkpoint B), so
   the claim is "surfaces cold items" (+ a qualitative sensible-example), NOT "cold hit@k".
2. `[OPEN]` **Must** — the "ID-only two-tower can NEVER surface cold items / scores ~0" premise is FALSE: U8 embeds
   EVERY catalog item and scores every row; zero-train items get **negative-shaped** embeddings (sampled as
   negatives) → ranked low, NOT hard-excluded. → Replace the categorical claim with the MEASURED baseline cold
   coverage (the honest story: ID-only buries cold items with negative-shaped id embeddings; the feature tower lifts
   their coverage via feature-based embeddings).

**[fable] — REJECT** (3 Must + 4 Should + 2 Nice; **ran a thorough seeded torch probe** — premise survives but under
an unspecified design choice; closure/isolation/taught-before/scope all confirmed). Measured (60ep, dim32, BPR+Adam
wd=1e-4; warm 500 readers, k=10): cold universe = **150 designated** cold_items (0 val positives by construction;
54/150 have a TEST positive → Checkpoint B only) **+ 668 incidental** zero-train items (101 val positives across 97
readers). Paths: U4 CF warm 0.252 / cold-cov 0; U8 ID-only warm **0.340** / cold-cov 0; U7 semantic warm 0.102 /
cold-cov **0.322** (content already serves cold!); feature tower **uniform-full-catalog negs** 0.298 / cold-cov 0.040
(buries cold + tanks warm); feature tower **warm-only negs** warm **0.320** / cold-cov **0.131** / cold share 0.085;
hard-neg popularity: warm 0.28→0.23 (trades warm for cold, doesn't "sharpen"). Two seeded fits allclose + bit-identical.
1. `[OPEN]` **Must** — the plan silently inherits U8's **uniform-over-full-catalog** negative sampler; since 41% of
   the catalog is zero-train, cold items become **negatives-only** → the tower learns to BURY them (cov 0.04) and
   tanks warm. **Negatives must be drawn from the WARM (train-positive) item universe** (the primary design knob +
   the mechanism lesson: "a cold item that is only ever a negative gets pushed down; features can't rescue it from
   its own negative gradient"). Warm-only → warm 0.320, cold-cov 0.131.
2. `[OPEN]` **Must** (= [sol]#1) — define the cold metric precisely: **GATE = cold-item coverage of top-10 (and cold
   share of slots) over the 818 zero-train items** (deterministic, well-populated; ID-only/CF are exactly 0 so
   "feature-tower cold-cov > 0 and > ID-only" is a sound bound); **report-only** cold hit@10 on the 97 incidental
   readers (state small-n); relevance for the 150 designated cold items is measurable only on `test` at Checkpoint B.
3. `[OPEN]` **Must** — "the first path that serves cold items" is FALSE (U7 semantic/U3 lexical content paths already
   cover cold freely — U7 cold-cov 0.322). Honest headline: **the first LEARNED-taste/collaborative path to serve
   cold items while staying near the best warm hit** (0.320 vs semantic's 0.102) — a warm/cold COMPROMISE, not
   dominance (its cold hit 0.021 is BELOW U7's 0.031).
4. `[OPEN]` **Should** — hard negatives: popularity-weighted did NOT sharpen — it traded warm for cold. Default =
   **uniform-over-warm**; hard-neg is the ablation/caveat knob framed as "trades warm accuracy for cold reach /
   popularity debias" (not "sharpens").
5. `[OPEN]` **Should** — ~28–35 s/fit at 60 epochs (≈2× U8); feature-tower exec adds ~3–5 CI-min. Pin n_epochs (try
   **40**) + cap fits/notebook; count the aggregate against the §9 budget.
6. `[OPEN]` **Should** — `fit(interactions, catalog=None)`'s `catalog` is an iterable of item IDS, not `Book`s.
   Features (catalog `Book`s + keywords + `GloveSubset`) come through the **constructor**, like
   `SemanticEmbeddingRetrievalPath(keywords, glove)` → `FeatureTowerRetrievalPath(catalog_books, keywords, glove, …)`.
7. `[OPEN]` **Should** — name the subprocess test (`tests/test_unit07.py:310` + the top-level scan at `:283`);
   `artifact()` must persist the **composed numpy item matrix** (not Linear/Embedding weights) so `load`/`retrieve`
   stay torch-free without re-composition.
8. `[OPEN]` **Nice** — baseline.yaml likely needs `Linear`, `no_grad`, `cat`, `zeros_`, `arange` beyond U8's list.
9. `[OPEN]` **Nice** — Phase-D "specific cold book" drill: pick a deterministic reader from the 97 incidental-cold-val
   readers so the surfaced cold book is one the reader actually read next.

### Plan-review outcome (round 1): **NOT consensus — [sol] REJECT (2 Must) + [fable] REJECT (3 Must, probe) + [self] APPROVE.** The premise HOLDS under warm-only negatives (warm 0.320 ≈ U8, cold-cov 0.131 vs 0). Fold both → **v2**: warm-only negative pool (THE mechanism); cold-COVERAGE gate over 818 (+ report-only cold-hit on 97, designated→ChkptB); honest "first collaborative/learned path to serve cold at near-best warm, a compromise not dominance"; hard-neg = ablation (trades warm↔cold); features via constructor; artifact persists composed numpy matrix; pin n_epochs≈40 + fit budget; baseline torch idioms. Then round-2 re-review (both rejecters).

### Round 2 (v2 changelog — all round-1 Must/Should folded)
- **[sol]#1 / [fable]#2 (cold metric unmeasurable on val):** GATE redefined as **cold-item COVERAGE** = unique
  zero-train ids in readers' top-10 / 818 (needs no cold val positives; ID-only/CF = 0). Cold *hit@10* is report-only
  on the 97 incidental-cold-val readers (small-n); designated-150 relevance deferred to Checkpoint B on sealed `test`.
  Folded into **Why this works** (metric para), **Phase B** (gate), C/D/E (coverage framing).
- **[sol]#2 (ID-only "never surfaces cold" is false):** replaced with the MEASURED baseline — ID-only/CF give cold
  items negative-shaped id embeddings → coverage exactly 0, not hard-excluded. Phase C point (1) + table reframed.
- **[fable]#1 (negative pool — THE mechanism):** default `negative_pool="warm"` (train-positive universe) added to
  Scope, Determinism&budget-adjacent, Why-this-works table, and **Phase B** as the primary knob; full-catalog shown as
  the failure mode (cov 0.04 / warm tanks).
- **[fable]#3 ("first to serve cold" false):** honest headline = first **learned-taste/collaborative** path to serve
  cold at near-best warm, a compromise not dominance (U7 content already serves cold). Scope + Why + Phase C.
- **[fable]#4 (hard negatives):** reframed as the warm↔cold-trade **ablation** knob, not "sharpens". Scope, Why,
  Phase C/D.
- **[fable]#5 (budget):** Phase B pins `n_epochs=40`, caps ≤2–3 fits/notebook, reports aggregate fit count + wall time
  vs §9 budget. Determinism&budget bullet.
- **[fable]#6 (features via constructor):** `FeatureTowerRetrievalPath(catalog_books, keywords, glove, …)`; `fit`'s
  `catalog` stays an item-ids iterable. Phase B signature.
- **[fable]#7 (named subprocess test + artifact):** Phase B names `tests/test_unit07.py:310` + `:283`; `artifact`
  persists the **composed numpy item matrix** (+ reader matrix + ids), not Linear/Embedding weights.
- **[fable]#8 (baseline torch idioms):** Phase A baseline.yaml note to add torch idioms beyond U8's list as the
  authored cells require. **As built:** only `Linear` was actually used by the authored cells (the lesson's feature
  skeleton); the shipped tower SUMS (no `torch.cat`) and no notebook uses `no_grad`/`zeros_`, so those were NOT added
  (`arange`/`from_numpy` already declared). `FeatureTowerRetrievalPath` listed alongside the U7/U8 path-class precedent.
- **[fable]#9 (deterministic cold-book example):** Phase D/E pick the surfaced-cold-book reader from the 97
  incidental-cold-val readers deterministically.

**[self] — APPROVE (round 2).** v2 resolves every round-1 Must/Should on the measured numbers: warm-only negatives is
the mechanism (warm 0.320 ≈ U8 0.340, cold-cov 0.131 vs 0); the gate is the validation-safe cold COVERAGE over 818
(cold hit report-only); the headline is honest (learned/collaborative-first, compromise not dominance); hard-neg is an
ablation; budget pinned at 40 epochs; features via constructor; artifact persists the composed numpy matrix; subprocess
test extended. No [self] blockers; dispatching [sol]+[fable] round-2 re-review.

**[fable] — APPROVE WITH NITS (round 2).** Verified all nine round-1 findings genuinely folded into the v2 text (not
merely claimed), honest-headline framing consistent across Scope/Why/Phase C/D/E/F, registry unique + closure sound
(24.5→27.5 buildout arithmetic correct), subprocess test line numbers exact (`:310`/`:283`), constructor signature
matches `protocol.py`/`embeddings.py`. No new blocker. Two **Nice** nits — BOTH FOLDED: (1) Phase B warm-gate was
pre-bound to an unmeasured "≈0.32 at 40ep" (all measurements were 60ep) → reworded to re-measure at 40ep and pin with
headroom (≥0.28 if lower); (2) `arange` already declared (`baseline.yaml:68`) → dropped from the Phase-A add list.

**[sol] — REJECT (round 2) → fixed in round 3.** Confirmed round-1 Must #2 resolved (U8 embeds/scores every catalog
item, cold items get negative-shaped embeddings not exclusion — `two_tower.py:148,231,376`) and no sealed-test leak
(`gen_interactions.py:183`), closure/buildout/isolation/taught-before all sound. One remaining Must:
- `[OPEN]→[FIXED r3]` **Must** — the cold-COVERAGE gate still had a hidden val dependency: the plan's measured cohort
  was the "500 eligible readers", but the scoreboard derives eligibility from readers who HAVE a held-out positive
  (`scoreboard.py:141,147`), so *which* readers count toward coverage would depend on val. → **v3 fold:** coverage is
  now counted over **ALL fitted non-cold readers scored from TRAIN histories only** (train-seen excluded), explicitly
  NOT the held-out-positive cohort; the 500-reader val cohort is kept only for warm hit@10 + report-only cold hit, and
  Phase B re-measures the coverage bound on the train-only cohort. Folded into the **Why/metric** para + **Phase B**.

**[self] — APPROVE (round 3).** v3 removes the last val dependency: the coverage denominator (818) and the reader
cohort (all fitted non-cold readers, train-only scoring) are both validation-free; warm hit and report-only cold hit
stay on the val scoreboard, clearly separated. No remaining [self] blocker. Re-dispatching [sol] round-3 (sole
rejecter; [fable] already APPROVE WITH NITS).

**[sol] — APPROVE (round 3).** Round-2 Must resolved: numerator, denominator (818 zero-train), reader cohort,
histories, and exclusions are all train-only; the validation-eligible cohort is explicitly separate (verified against
`scoreboard.py`, `two_tower.py`, `gen_interactions.py`). No remaining or new blocker.

### Plan-review outcome (FINAL): **CONSENSUS — [self] APPROVE (r3) · [sol] APPROVE (r3) · [fable] APPROVE WITH NITS (r2).**
All blockers resolved; both [fable] Nice nits and both [sol] Musts folded. Cleared for implementation (Phases A→G).

## Content Review

### Pre-gate self-caught fixes (during the build)
- `[FIXED]` **Ex1 degenerate warm/cold contrast** — the exercises scaffold set `warm_book = catalog_ids[0]`, but
  `catalog_ids[0]` == book 0 == `min(zero_train)` on seed 0, so the "warm" and "cold" demonstration books were the
  SAME zero-train book (identical genres/author printed). Surfaced by the independent solutions solver. Fixed in BOTH
  `exercises.ipynb` and `solutions.ipynb`: `warm_book = min(train_pos_items)` (smallest id with a train positive,
  guaranteed warm); added a contrast-guard assert in the solution (`warm_book in train_pos_items and warm_book !=
  cold_book`). Solutions re-executed clean.

<!-- appended pre-PR -->

## Post-Execution Report

<!-- appended before ship -->
