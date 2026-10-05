# Plan recsys-006 — Unit 4: Neighborhood collaborative filtering (item-item co-occurrence)

**Design:** `docs/designs/011-recsys-book.md` (§5, §6, §8 Unit 4). **Book:** `recsys` (Book 3). **Autopilot** per
AGENTS.md. Fourth Part-1 unit, on the Unit-1/2/3 substrate + the taste-aware generator (recsys-004) + the
milestone-notebook mechanism. Ships the first **collaborative** path: item-item co-occurrence CF — the **first
decisive win over popularity** (~2.3×) and the first path to beat **both** popularity and the content/lexical path
(Unit 3's lexical already edges popularity ~1.46×; CF beats it ~1.6×).

## Scope
**Unit 4 only** (`recsys/units/unit-04-neighborhood-cf/`). Teaches **neighborhood collaborative filtering**:
item-item **co-occurrence** similarity from the interaction log, **k-nearest-neighbor** retrieval, **implicit vs
explicit** feedback and **sampled negatives**. Ships an `ItemItemRetrievalPath` (co-occurrence) in `bookrec` + a
Unit-4 milestone notebook. No matrix factorization (U5), no neural (U7+). No generator change.

## Why this works on the data (empirical, binding)
recsys-004's committed recoverability harness already measures an item-item cosine co-occurrence CF at **~0.25
hit@10 ≈ 2.3–2.9× popularity (~0.108)** on `val` (k=10, cold excluded) — because taste-aware exposure imprints the
latent taste into co-occurrence. So CF is the first path to beat **both** popularity (~0.108) **and** the
content/lexical path (~0.158) — a decisive ~2.3× popularity / ~1.6× lexical (Unit 3's lexical already modestly beat
popularity ~1.46×; CF is the first to beat both). Authors MUST re-measure on the committed seed and bind the Phase B
test to the harness's two-part margin (CF ≥ 1.3× popularity AND ≥ popularity + 0.03) **and** `CF > lexical`.

## Buildout stays
Whole-book `lessons` total becomes **12** (U1–U4, 3 each) < 30 → `buildout: true` retained.

## Audience & retained laws
Advanced baseline (incl. `vectors`, `dot-product`, `vector-norm`, `linear-algebra`, numpy). Retained: project-first;
taught-before-assessed; student notebooks NO solutions/outputs; solutions + milestone run clean (seed 0);
teacher-notes; from-scratch→reveal-the-library. CPU-light (numpy + `bookrec`; no torch/faiss) routed `--group recsys`.

## Concepts introduced (3) — `concepts.yaml`
- `item-item-cf` — item-item collaborative filtering: build an item×item **co-occurrence** similarity (cosine over
  the readers who co-engaged two items) from the **train** log; recommend items similar to what a reader has read.
  The shipped `ItemItemRetrievalPath`. `kind: technique`, `category: techniques`.
- `knn-similarity` — **k-nearest-neighbor** retrieval over the item-similarity matrix: score a candidate by the
  summed similarity to the reader's seen items, optionally capped to the top **`n_neighbors`** (named `n_neighbors`,
  NOT `k`, to avoid clashing with the protocol's `k` = candidate count). On this data an uncapped neighbourhood is
  best; a small cap *degrades* (taught honestly). `kind: technique`, `category: techniques`.
- `implicit-feedback` — **implicit vs explicit** feedback (a read/like is a positive; there are no negative *ratings*)
  and the resulting positive-only sparsity. Taught against the CONCRETE log: its `label==0` rows are
  exposure-sampled negatives (exposed-not-liked) standing in for the unobserved — the rows students have filtered to
  positives since Unit 1. The co-occurrence path uses **positives only**; **sampled negatives are USED for training
  in U5 MF / U8 two-tower**, not here — Unit 4 does no negative sampling (full-catalog ranking). `kind: technique`,
  `category: techniques`.
All three concepts carry `name`+`category`+`kind: technique`; globally unique (confirmed: 0 hits across
`*/curriculum/concepts.yaml`). `item-item-cf` → `category: techniques`.

### Coverage-map entry
`unit-04-neighborhood-cf`, `kind: unit`, **`title: "Neighborhood collaborative filtering"`** (v1 `MAP_ENTRY_KEYS`
requires `title`), `lessons: 3`, `introduces: [item-item-cf, knn-similarity, implicit-feedback]`,
`requires: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics]`,
`practices: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics]` (Unit-1 ids; closes
under buildout; no project map entry → capstone rule inert).

## Phases

### Phase A — registry + syllabus (CI-fidelity)
- `concepts.yaml`: add the 3 ids. `coverage-map.yaml`: add the Unit-4 entry (buildout comment → "twelve").
- `baseline.yaml`: declare any new `x.name(...)` methods the notebooks/code use (confirm against authored cells).
- `unit-04-neighborhood-cf/manifest.yaml`; `syllabus.md` arc row `| 4 | \`unit-04-neighborhood-cf\` | unit | 3 | <hook> |`; rebuild PDF.
**Verify:** curriculum checks green; buildout holds (12<30).

### Phase B — `bookrec` CF code (Opus subagent; numpy-only, no pandas in the package)
Dispatch an **Opus subagent** (`Agent`, `model: opus`). STUDY `recsys/data/_reference_recommenders.py` `_item_item_cf`
(the recoverability-harness CF scorer — **PORT its logic, do NOT reuse its signature**: it takes a dense reader×item
matrix sized by the generator config; `bookrec` has no generator object), `protocol.py`, `scoreboard.py`,
`popularity.py`/`lexical.py` (path conventions). Add `bookrec/neighborhood.py`:
- an item-item **co-occurrence** builder: from the train positives, build an item×item cosine similarity (reader
  co-engagement), zero diagonal; an **`n_neighbors` cap is OPTIONAL and defaults to uncapped** (capping degrades on
  this data — top-10 → 0.142 < lexical). `fit` **duck-types the row-mapping iterable** (`reader_id,item_id,split,
  label`, as `PopularityRetrievalPath.fit` does — NO pandas), indexes readers/items from the TRAIN rows themselves,
  and honours `catalog=` as the item universe.
- `ItemItemRetrievalPath(BaseRetrievalPath)` (name `"item-item"`, version `"1"`): `fit(interactions, catalog=None)` —
  EXACTLY the protocol signature; builds from the train log (implicit **positives only**, `split=="train"` &
  `label==1`; leakage-safe — no val/test). `retrieve(reader_id, context, k)` scores each candidate by the summed
  similarity to the reader's `context["seen"]` items (ignoring any `seen` item absent from the fitted index — no
  KeyError on hand-built contexts), excludes `seen`, top-k via `_finish`; empty `seen` → `[]`. `load`/`artifact`
  round-trip the fitted similarity (copy arrays). Export from `__init__`.
- Tests (routed): CF clears the harness two-part gate on the seeded `val` scoreboard — **hit@10 ≥ 1.3× popularity
  AND ≥ popularity + 0.03 AND > lexical** (cold excluded, k=10; measured 0.252 vs pop 0.108 / lexical 0.158); a tiny
  hand-checked co-occurrence/cosine fixture; **leakage: the similarity is bit-identical with vs without val/test rows**
  (and, as a vivid check, a val-folded "leaky" fit scores wildly higher ~0.96); empty-seen → `[]`; a `seen` item not
  in the index is skipped; fit→artifact→load round-trip returns identical recs; registers as `item-item-v1`, no
  collision; a small `n_neighbors` cap *lowers* the score (documents the degradation).
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/ -q` green, deterministic, numpy-only.

### Phase C — lesson.ipynb (Opus subagent; project-first)
Hook: "readers who liked the books you liked also read…". From scratch → reveal: (1) the co-occurrence idea +
implicit vs explicit feedback taught against the real log (count its `label==1` positives vs `label==0`
exposure-sampled negatives; co-occurrence uses positives only; U5 is where sampled negatives get USED to train);
(2) build the item-item cosine similarity by hand in numpy; (3) k-NN retrieval — score candidates by summed
similarity to the reader's history, and show the **`n_neighbors` cap** (if any exercise assesses it) with its honest
*degradation* on this data; note the coverage ceiling (41% of the catalog has no train positives → unreachable by
CF, unlike lexical — a bridge to U6 cold-start/blending);
reveal `ItemItemRetrievalPath`, register + score on `val` (seed 0, k=10, cold excluded) — it **beats popularity**
(~0.25 vs ~0.108) AND the content/lexical path (~0.158): the first DECISIVE personalization win (acknowledge U3's
lexical already modestly beat popularity ~1.46× — CF is the first to beat both, by the widest margin so far). Honest: this
is collaborative (uses who-read-what), complementary to the content/lexical path; MF (U5) generalizes it.
ASCII only; `rank(exclude=seen)`; reuse `bookrec`.
**Verify:** `exec-lessons` clean; non-empty markdown first cell; `concept-scan` clean.

### Phase D — exercises.ipynb + solutions.ipynb (separate fresh Opus subagents)
≥6 `## Exercise N`; ≥2 `stretch`; exercises NO solutions/outputs; solutions mirror all, clean (seed 0), ≥3
non-vacuous asserts. Drill: build the co-occurrence matrix + cosine similarity; k-NN retrieval; register
`ItemItemRetrievalPath` + read the val scoreboard vs popularity/lexical/random (CF wins both); implicit-feedback as
reasoning/counting over the log's positives vs `label==0` rows (NOT asserted path behaviour). Stretch e.g.: the
`n_neighbors` cap *degrades* the score here (expect it); cold-item behavior (no co-occurrence → no neighbors → the
coverage ceiling); why co-occurrence ≈ a rank-reduced signal (bridge to MF). Taught-before-assessed.
**Verify:** `hygiene`/`structure`/`cell-lint`/`noexec` (≥6, ≥2 stretch, no outputs); `exec-solutions` clean;
`concept-scan` clean.

### Phase E — milestone notebook (Opus subagent)
`recsys/projects/bookrec/milestones/unit-04-neighborhood-cf.ipynb` — runnable fixed-seed demo (cleared outputs,
ASCII, one-line hook): build + fit + register `ItemItemRetrievalPath`, score on `val` vs random/popularity/lexical
(CF wins), and show one reader's history → top CF recommendations with the co-occurring neighbors. Passes
`milestone-check` + `exec-solutions` + `concept-scan`.

### Phase F — teacher-notes.md (inline)
`## Goals`, `## Pacing` (60–90 min / 2–3 sittings, hook stated; assign ALL exercises), `## Common mistakes`
(leaking val into the similarity — folding val into `fit` jumps hit@10 to ~0.96, a vivid "too good to be true"
number; recommending already-seen items; cold items with no neighbors and the ~41% coverage ceiling; confusing
item-item with user-user; assuming a bigger `n_neighbors` cap helps — it doesn't here), `## Discussion prompts`,
`## Differentiation`.

### Phase G — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN with Units 1–4 + the Unit-4 milestone AND
`bash scripts/pre-merge-guard.sh --pr` OK. buildout holds (12).

## Out of scope
No matrix factorization (U5); no neural/embeddings (U7+); no generator change; no user-user CF beyond a mention
(item-item is the shipped path); no `projects/project-*` map entry (capstone=U14); no checkpoint; no buildout removal.

## Verification phase declared
Phase G is this plan's named verification phase.

## Plan Review

### Round 1 (on v1)

**[self] — APPROVE.** Concepts globally unique; coverage entry closes (Unit-1 ids; `practices∩introduces=∅`; no
project map entry → capstone rule inert); buildout holds (12<30); named verification Phase G; project-first;
from-scratch→library; ≥6/≥2-stretch/≥3-asserts; teacher-notes; milestone. Feasibility established by recsys-004's
committed harness (item-item CF ~0.25 ≈ 2.3–2.9× popularity) — CF is the first path to beat popularity, the Part-1
headline; binds empirical re-measure + the ≥1.3×-popularity margin on the authors + gate. `ItemItemRetrievalPath`
mirrors the harness's reference CF scorer, keyword/construction pattern not needed (fit builds from the train log).
No [self] blockers. Monday: full 4-way incl. [glm]; [sol] retried on Codex.

**[sol] — INCOMPLETE** (Codex `gpt-5.6-sol` immediately "at capacity"; persistent infra outage, weekend+Monday).
Infra-unavailable for this gate.

**[fable] — APPROVE WITH NITS** (empirically verified: CF 0.252 = 2.33× popularity, 1.6× lexical, 21× floor;
fit→artifact→load identical; leakage val-fold → 0.964; 818/2000 items have no train positives; coverage/prereq pass;
ids unique).
1. `[OPEN]` **Must Fix** — "first path to beat popularity" is FALSE and contradicts shipped Unit 3 (lexical already
   beats popularity 1.46×, and `unit-03`'s lesson/milestone say so). Reframe (plan lines 5–6,17,74–75,118 + Phase C
   hook): CF is the **first collaborative path** and the **first to beat BOTH popularity AND the content path**, by
   the widest margin so far (2.33× pop, 1.6× lexical). Add `> lexical` to the Phase B assert (mirrors the harness's
   content-below-collaborative gate).
2. `[OPEN]` **Should Fix** — neighbor-cap default must be **uncapped** (or ≥100); capping HURTS on this data
   (top-10 → 0.142, below lexical, ~1.31× pop — one wobble from failing the gate). Bind headline/test to the
   uncapped default; the Phase-D stretch "cap effect" must expect **degradation**, not improvement; name the param
   `n_neighbors` (NOT `k` — clashes with the protocol's `k` = candidate count).
3. `[OPEN]` **Should Fix** — taught-before-assessed: if any exercise assesses the neighbor cap, teach it in Phase C
   (the lesson outline currently only teaches summed similarity).
4. `[OPEN]` **Should Fix** — implicit-feedback honesty: the shipped path + the scoreboard use **no** negative
   sampling (full-catalog ranking), so do NOT present "sampling negatives" as something Unit 4 DOES. Teach implicit
   feedback against the concrete log (10457 train `label==0` exposed-not-liked vs 5303 positives; positives-only
   enter the co-occurrence; label-0 + the unobserved complement are the two "negatives"), and point to U5 MF as where
   sampled negatives are actually used. Exercises on this concept = reasoning/counting over the log, not asserted
   `ItemItemRetrievalPath` behaviour.
5. `[OPEN]` **Should Fix** — Phase B must say "fit duck-types the row-mapping iterable (`reader_id,item_id,split,
   label`) like `PopularityRetrievalPath.fit`, index readers/items from the train rows, honour `catalog=` as the
   item universe, no pandas" — the harness `_item_item_cf` takes a dense generator-sized matrix; PORT the logic,
   don't reuse the signature.
6. `[OPEN]` **Should Fix** — leakage test: assert the similarity is bit-identical with/without val/test rows (+ the
   0.964 leaky number as a teacher-notes "common mistake").
7. `[OPEN]` **Nice** — `retrieve` ignores `seen` items absent from the fitted index (no KeyError on hand-built ctx).
8. `[OPEN]` **Nice** — 41% of the catalog has no train positives → CF coverage ceiling; one honest lesson sentence +
   bridge to U6 cold-start/blending.
9. `[OPEN]` **Nice** — `baseline.yaml` new numpy idioms (fill_diagonal/outer/sqrt/argsort/ItemItemRetrievalPath/
   artifact/...); Phase A covers it.

**[glm] — REJECT** (corroborates the headline Must-Fix; otherwise verified sound — coverage closes, ids unique,
design matches protocol/lexical, numbers match committed records).
1. `[OPEN]` **Must Fix** — (same as [fable]#1) "first path to beat popularity" contradicts shipped U3 (lexical
   1.46× pop). Reframe all four sites + Phase C/E/F: first **collaborative** path, first **decisive** win over
   popularity (~2.3× vs lexical's ~1.5×), acknowledging U3's modest win.
2. `[OPEN]` **Should Fix** — schema fields: the coverage-map entry needs `title` (v1 `MAP_ENTRY_KEYS` exact-set),
   and all three concepts need `name`+`category` (not just `item-item-cf`). (concepts.yaml/coverage-map will carry
   them; stated for the authors.)
3. `[OPEN]` **Should Fix** — (refines [fable]#4) implicit-feedback honesty: the log's `label==0` rows
   (`gen_interactions.py:226`) ARE exposure-sampled negatives standing in for the unobserved — the rows students have
   filtered since U1. Teach "no negative ratings" against that concrete log; co-occurrence uses positives only; U5 MF
   is where sampled negatives are USED for training (design §6 designates U4 for this framing).
4. `[OPEN]` **Nice** — Phase B test: mirror the harness two-part gate (`≥1.3× popularity` AND `≥ pop+0.03`), not the
   ratio alone.

### Plan-review outcome (round 1): **NOT consensus — [glm] REJECT + [fable] APPROVE WITH NITS ([sol] infra-down).** Headline empirical error (CF beats BOTH popularity and content, not "first to beat popularity") + solid refinements. Fold → v2 → re-review.

### Round 2 (on v2)
**[self] — APPROVE.** v2 folds all findings: headline reframed everywhere in the body — CF is the first
**collaborative** path and the first to beat **both** popularity (~2.3×) and the content/lexical path (~1.6×),
acknowledging U3's modest ~1.46× win (fable#1/glm#1); `n_neighbors` (not `k`) default **uncapped**, cap *degrades*
(fable#2); lesson teaches the cap if assessed (fable#3); implicit-feedback taught against the real `label==0`
exposure-sampled-negative rows, no negative sampling in U4, sampled negatives USED in U5 (fable#4/glm#3); Phase B
PORTs `_item_item_cf` via the row-mapping duck-typed `fit`, no pandas (fable#5); leakage bit-identical test + the
~0.96 leaky number (fable#6); `retrieve` skips absent `seen` (fable#7); coverage-ceiling sentence (fable#8);
coverage-map `title` + all 3 concepts `name`+`category` (glm#2); Phase B test = two-part gate `≥1.3× pop AND
≥ pop+0.03 AND > lexical` (glm#4/fable#1). No [self] blockers.

**[fable] — APPROVE** (round 2): all 8 resolved; one non-blocking implementer note (fit precedence: `catalog=` when
given, else train items — baked into the Phase-B dispatch).
**[glm] — APPROVE** (round 2): all findings resolved + verified against `gen_interactions.py` (`label==0` = exposed-
not-liked; per-positive sampled negatives), shipped U3 (~1.46×), and the committed harness/`_learned_mf`. No new blockers.

### Plan-review outcome: **CONSENSUS (3-of-4; [sol] infra-down — Codex at capacity)** — [self]/[fable]/[glm] APPROVE. CF headline corrected (beats BOTH popularity and lexical). Cleared to implement (Phase A → G).

## Content Review

ci-local ALL GREEN (97 bookrec tests incl. test_unit04; lesson/solutions/milestone exec; concept-scan; recsys PDFs;
pre-merge-guard OK). Ruff step-1 caught an unused `Counter` import in the milestone (fixed, commit `fa6bb98`). 4-way
gate (Opus back Monday; [sol] retried on Codex).

### Review 1 — self (2026-10-05)
- **Verdict**: APPROVE. All phases verified: lesson (project-first; co-occurrence→cosine→kNN from scratch then
  reveal), 8 exercises (6 core + 2 stretch) + mirrored solutions (8 asserts), milestone, teacher-notes. Numbers
  reproduced (CF 0.252 = 2.33× popularity, 1.60× lexical, 21× floor; cap=10 → 0.142 degrades; 818/2000 unreachable).
  Honest framing confirmed (CF first COLLABORATIVE path + first to beat BOTH popularity AND lexical, acknowledging
  U3's ~1.46×; implicit feedback vs the real label==0 rows, no negative sampling in U4). Code tested (neighborhood.py
  97 tests incl. leakage bit-identical + leaky-0.964 + fit→artifact→load + cap degradation). No [self] blockers;
  deferred to [fable]/[glm]/[sol] blind-solve.

### Review 2 — fable (2026-10-05)
- **Verdict**: APPROVE WITH NITS. Blind-solved all 8 (every answer matches solutions); empirically verified (CF
  0.252 = 2.33× pop / 1.60× lexical; two-part gate clears; bit-identical leakage + leaky 0.964; round-trip identical;
  cap sweep monotone-degrading); code sound; honest framing confirmed everywhere; 15 test_unit04 pass. No Must.
1. `[OPEN]` **Should Fix** — `teacher-notes.md` has literal placeholder "Exercises (1–N)"/"1–N" (lines ~27,69) → use
   1–8 (6 core + 2 Challenge).
2. `[OPEN]` **Should Fix** — `teacher-notes.md` Pacing leaves **Exercise 6 (the scoreboard) unassigned** (sittings
   list 1–2, 3–5, stretch); fold Ex6 into Sitting 2.
3. `[OPEN]` **Should Fix** — "rank-reduced" is INVERTED + untaught: co-occurrence `RᵀR` is the full Gram matrix; **MF
   is the low-rank (rank-reduced) approximation** of it. Fix Ex8 statement+solution + teacher-notes to
   "MF is the low-rank (rank-reduced) approximation of this pairwise co-occurrence" (lesson never uses the term).
4. `[OPEN]` **Nice** — `test_unit04.py::test_fit_signature_is_protocol_substitutable` asserts non-None on item 5,
   which has no train positives → `[]` (vacuous); use an item with positives (e.g. 307) and assert non-empty.
5. `[OPEN]` **Nice** — lesson cell 14 genre-overlap hedge: name item 976 (fantasy;romance) as the clean off-genre
   example rather than a list that partly overlaps reader 3.
6. `[OPEN]` **Nice** — milestone cell 9 redundant `rank(exclude=seen)` on already-ranked/filtered output.
7. `[OPEN]` **Nice** — `ItemItemRetrievalPath.load` accepts `n_neighbors` without the constructor's validation.

### Review 3 — glm (2026-10-05)
- **Verdict**: APPROVE WITH NITS. Independent blind-solve matches all 8; claims verified empirically (CF 0.252 beats
  both; cap 0.142; 818 unreachable; leaky 0.964; implicit-feedback vs real label==0); project-first/audience/hygiene/
  code all ✓; ran the suite 97/97. No Must.
1. `[OPEN]` **Should Fix** — (= fable#1) `teacher-notes.md:27,69` placeholders "1–N" → 1–8.
2. `[OPEN]` **Nice** — reconcile 5303 positive ROWS vs 4694 distinct PAIRS (609 dup reader-item positives) with one
   sentence in lesson §1/§2 (also explains why popularity counts rows, CF counts pairs).
3. `[WONTFIX]` **Nice** — `_cap_neighbors` `np.argsort` not stable; deterministic under the pinned numpy lockfile
   (CI-safe) and changing tie-break would shift the pinned cap numbers (0.142) in notebooks/tests — leave.
4. `[OPEN]` **Nice** — (= fable#4) vacuous test assert; + `load` doesn't validate `similarity` shape vs `len(item_ids)`.

### Content-review outcome (pending [sol]): [self]/[fable]/[glm] APPROVE / APPROVE WITH NITS — no Must; fold nits → re-verify → merge (3-of-4 if [sol] Codex stays at capacity).

### Review 4 — sol (2026-10-05, Codex completed)
- **Verdict**: REJECT. Blind-solve matched E1–7 (and E8 numerics); 15 test_unit04 pass; cosine/fit/leakage/
  round-trip/numpy-only all check out. But three substantive Must + Shoulds:
1. `[OPEN]` **Must Fix** — the 818-item **coverage ceiling is NOT enforced**: `retrieve()` ranks every unseen item
   incl. ZERO-score ones (`neighborhood.py:197`), so a thin-history reader (e.g. reader 350) gets zero-score recs
   from the "unreachable" 818 — contradicting lesson:151 / milestone:165 / teacher-notes:44. Drop non-positive-score
   candidates (making the "never recommend" claim true) + a regression for an all-zero-score history. (Verify the
   val hit@10 0.252 is unchanged — zero-score filler never holds the positive.)
2. `[OPEN]` **Must Fix** — (= fable#3) Ex8 assesses "rank reduction" but the lesson only says "memorized, pairwise"
   and the solution explains sparsity, not rank. TEACH the real relation (normalized `RᵀR` has rank ≤ rank(R); MF
   chooses a smaller latent rank) in the lesson and align Ex8 statement+solution — or drop the term.
3. `[OPEN]` **Must Fix** — milestone (`:165,:240`) overclaims: it says U5 MF "generalizes" to the 818 zero-positive
   items; ID-only MF CANNOT infer factors for truly cold items — it fills WARM-item gaps. Cold-start is U6 (blend) /
   U9 (features) per design §8. Fix the bridge.
4. `[OPEN]` **Should Fix** — `label==0` rows called "leakage" (milestone:70, neighborhood.py:103 comment); they are
   valid TRAIN exposure-sampled negatives the algorithm intentionally ignores — only val/test is leakage. Reword.
5. `[FIXED 9247438]` **Should** — pacing/placeholders ([sol] reviewed the pre-fix commit; teacher-notes now 1–8 +
   Ex6 in Sitting 2).

### Plan-review—wait, content-review outcome (round 1): **NOT consensus — [sol] REJECT (3 Must) + [fable]/[glm] APPROVE WITH NITS.** [sol]'s deeper pass caught a real code/teaching mismatch (coverage ceiling), an untaught/inverted Ex8, and an MF cold-item overclaim. Fold all (incl. the [fable]/[glm] nits) → v2 → re-review.

<!-- round 2 appended -->

## Post-Execution Report

<!-- appended before ship -->
