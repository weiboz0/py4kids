# Plan recsys-004 — Generator redesign: taste-aware exposure + latent-correlated text (data foundation for the personalization arc)

**Design:** `docs/designs/011-recsys-book.md` (§6 data contract — **amended here**). **Book:** `recsys` (Book 3).
**Autopilot** per AGENTS.md. **User-approved 2026-10-03.** This is a **data/tooling foundation slice, not a unit**:
it re-architects the synthetic generator so each personalization technique in Part 1 (and Part 2) is *recoverable* and
demonstrably beats the popularity baseline, and gives the catalog the real **text** that lexical (U3) and GloVe (U7)
need. It unblocks the whole personalization arc; Unit 3 (lexical) is re-drafted afterward as **recsys-005**.

## Motivation (empirically established at the recsys-005/Unit-3 plan gate)
Both [sol] and [fable] (self-confirmed) measured, on the committed seed (`run_validation_scoreboard`, k=10, cold
excluded, 368 readers): the generator's `val` positives are **exposure-gated and exposure ∝ lognormal popularity**,
so even an **oracle ranking by the generator's own true affinity scores 0.0163 ≈ the random floor 0.0136**, while
true popularity scores **0.1304**. No content path beats the floor (genre cosine 0.0054; genre×IDF 0.0082; BM25
genre+author 0.0054–0.0082). ⇒ On this data **no personalization path — content (U3), item-item CF (U4), or MF
(U5) — can demonstrate value**, because the affinity signal is swamped by popularity-driven exposure. Separately,
the catalog has **no text** (titles are placeholders; 12 genres each in ~1/6 of books; 300 author tokens too rare),
so U3 lexical (BM25 `k1` is inert on TF=1 tag docs) and U7 GloVe content embeddings are infeasible as designed.

## Goals (committed acceptance criteria — the named verification)
Regenerate the synthetic data (seeded, reproducible, publish-safe — still NO real catalog) so that on `val`
(k=10, cold excluded) the signal hierarchy is **recoverable** and matches the curriculum. **Denominators use the
ANALYTIC expected random floor** (U1's `1−C(N_u−r,k)/C(N_u,k)` averaged over scored readers) or a ≥50-seed random
average — never a single noisy draw ([fable]#2). Targets (met by the empirically-confirmed regime **α=0.75, β=2.5**
on per-reader z-scored affinity, default density, on 3 seeds):
- **random floor** low (analytic ≈ 0.011–0.012);
- **popularity** a strong, beatable baseline (**≥ 5× analytic floor** — preserving U2's `test_unit02` `>5×` contract
  and its "popularity is hard to beat" lesson; measured ~10×);
- **content** (keyword BM25 over the new text, and genre cosine) clearly beats the floor (**≥ 2× floor**; measured
  ~14×), and **content < CF** ([fable]#7);
- **item-item co-occurrence CF** (U4) beats popularity (**≥ 1.3× popularity**; measured ~2.6×);
- a **learned MF** trained on the OBSERVED interaction log (not the oracle) beats popularity, and **MF ≥ content**
  ([sol]#1, [fable]#7);
- the **true-affinity oracle ≥ 2× popularity** (holds at α=0.75); the generator's **observation-propensity oracle**
  (α·log pop + β·z-affinity) is the sanity ceiling (≫ everything). **Do NOT assert "oracle ≥ CF"** — CF legitimately
  learns the exposure pattern the pure-affinity oracle ignores ([fable]#1);
- **pure positive-RATE "quality"** (U2's weighted-rating lens) stays *weak* (**< popularity**; measured ~1–2× the
  floor — NO longer below it), because taste is driven by **latent affinity**, which `rate` does not capture.
- **keywords encode finer latent structure beyond genre**: latent-neighbour keyword overlap exceeds a
  genre-controlled baseline ([sol]#1).
These become a committed **recoverability harness** (Phase C) that fails CI if a future generator change breaks the
pedagogy (rank/ratio + absolute-margin based, per the `_common.py` numpy-robustness convention; min eligible-reader
counts enforced).

## Why this preserves Units 1–2 (regeneration impact)
`recsys/data/generated/` is **gitignored / regenerated-only** (`.gitignore:56`) — no committed data files change;
CI regenerates from the seeded scripts, and U1/U2 notebooks execute against the new data. U1/U2 **tests are
direction/rank-based** (not exact values), so they should still pass; the **prose numbers** in U1/U2 lessons/
solutions/milestones change and are re-verified + updated here with ERRATA notes (Phase E). The redesign is tuned to
**keep U1's random-floor story** (floor non-zero, popularity ≫ floor) and **U2's popularity-bias story** (popularity
strong; pure-rate quality weak) intact.

## Phases

### Phase 0 — Design 011 §6 amendment (active session inline; reviewed by this plan's gate)
Amend §6 "Synthetic interactions — per-unit signal spec":
- replace the pure popularity-exposure process with a **taste-aware exposure** contract: a reader is exposed to item
  `i` with probability ∝ `popularity(i)^α · exp(β · z_u(affinity(reader, i)))`, where `affinity` combines a
  **latent** component (reader×item latent dot product) and a **content** component (reader feature-prefs · item
  genre/keyword features), and **`z_u` is the reader's per-reader standardisation (z-score) of affinity** so `β` is
  well-conditioned regardless of `latent_scale`/`feature_weight` ([fable]#5, [sol]#3); positives arise among exposed
  items by a calibrated rate; **author-follow recurs across sessions**. State the design intent: popularity remains a
  strong baseline, but content/collaborative/latent signals are each **recoverable** and beat popularity (acceptance
  hierarchy above).
- add a **per-book keyword text artifact** (a SEPARATE gitignored file, e.g. `keywords.csv.gz`, NOT a new catalog
  column — so U1's five-column catalog teaching/assert `(5,5)` is untouched; [sol]#2): per book, a variable-length
  bag of **real-English-word** tokens (with repetition → TF varies; lengths vary → BM25 `b` matters) sampled from a
  committed topic **vocabulary** conditioned on the book's latent factors + genres; this is the slice vocabulary the
  **U7 GloVe subset** is later derived from (design §6 embeddings clause now has a concrete source). A separate
  `load_keywords` loader exposes it; `load_catalog` and the 5-column CSV are unchanged.
- note the regeneration + the U1/U2 re-validation/errata and the committed recoverability harness.
- Revision history v4.

### Phase A — keyword text artifact (`gen_catalog.py` + a new `keywords.csv.gz` + `bookrec` loader; Opus subagent)
- Add a committed **vocabulary module** (`recsys/data/vocabulary.py`): a curated list of common **real-English**
  words grouped into ~`latent_dim`+`n_genres` topics (so the U7 GloVe subset has near-total coverage); seeded, no
  network.
- `gen_catalog.py`: emit a SEPARATE `keywords.csv.gz` (`item_id,keywords` with keywords a space-joined token bag),
  NOT a new column in `catalog.csv.gz` — the 5-column catalog (`item_id,title,author_id,genres,year`) is UNCHANGED.
  For each book sample `T_i` tokens (T varying, e.g. 12–40) with repetition from a per-book distribution built from
  its latent factors + genres. **Draw keyword tokens from an rng sub-stream created AFTER the existing
  author/year/genre/latent/popularity draws** (or a derived `SeedSequence.spawn`) so the catalog's existing rng
  stream — and thus U1's pinned `search_catalog` ids (`solutions.ipynb` cell 7) — are byte-identical ([fable]#6).
- **Raise `latent_noise`** (independent latent component beyond the genre image) enough that the latent signal
  exceeds the genre signal, so U5 MF can later visibly beat U3 content ([fable]#7) — re-tune with the generator in
  Phase B against the harness.
- `bookrec/catalog.py` (or a new `bookrec/keywords.py`): a `load_keywords(path)` loader returning
  `dict[int, str]` (or token lists); numpy-only, no pandas. `load_catalog`/`Book` unchanged.
- Tests: `keywords.csv.gz` present; vocabulary ⊆ the committed vocabulary; deterministic; books sharing latent/genre
  have higher keyword overlap than random pairs; **latent-neighbour overlap exceeds a genre-controlled baseline**
  ([sol]#1); the catalog CSV is byte-identical to before (U1 search ids preserved).
**Verify:** `gen_catalog` regenerates deterministically incl. `keywords.csv.gz`; `load_keywords` works; the
`catalog.csv.gz` and `load_catalog` output are unchanged in schema/values U1 depends on.

### Phase B — taste-aware exposure (`gen_interactions.py` + `_common.py`; Opus subagent)
- Implement the taste-aware exposure process (Phase 0 contract): exposure sampling ∝
  `popularity^α · exp(β · z_u(affinity))` with **per-reader z-scored affinity**; `affinity` = `latent_scale`-weighted
  reader·item latent + `feature_weight`-weighted content (genre + keyword) term; positives among exposed by the
  calibrated rate; preserve the per-reader **temporal train/val/test** split, cold items/readers, sampled negatives,
  timestamps/sessions, and **make author-follow recur across sessions** (a read raises the exposure of the same
  author's other books in later sessions).
- **Starting regime α=0.75, β=2.5, default density** (empirically confirmed by both reviewers). If the CF gate
  (≥1.3× popularity) is not met, Phase B is EXPLICITLY permitted to tune **interaction density /
  reader-community recurrence** — e.g. raise `mean_sessions_per_reader` to 10–15, or draw readers from latent
  clusters so co-occurrence is informative ([sol]#4, [fable] regime notes) — keeping α≥0.75 (so pop≥5×floor) and the
  rest of the hierarchy.
- Expose the ground-truth (latent factors, per-pair affinity, observation propensity) so the harness runs oracle
  checks. Standardise affinity before `exp` (numerically stable; [sol]#3).
- Add/document config knobs in `_common.py` (`exposure_affinity_weight` β on z-scored affinity; keep
  `popularity_exposure_weight` α; raised `latent_noise`); **tune** to hit the Goals hierarchy (iterate with Phase C).
- **Preserve the existing interaction rng draw order where possible; where the new process necessarily changes it,
  that is expected — U1/U2 interaction-derived pins are updated in Phase E.**
**Verify:** deterministic regeneration; existing generator invariant tests updated and green; split/cold/negative
structure intact.

### Phase C — recoverability validation harness (Opus subagent; the named verification)
`recsys/data/tests/test_signal_recoverability.py` (routed `--group recsys`) + a `recsys/data/_reference_recommenders.py`
helper with small reference scorers (popularity count; keyword BM25; genre cosine; item-item cosine co-occurrence CF;
a **few-epoch learned MF trained on the observed TRAIN interactions**; the exposed true-affinity oracle; the
exposed observation-propensity oracle; U2's positive-rate quality). Evaluate on `val` (k=10, cold excluded) with the
**analytic expected floor** as the random denominator (or a ≥50-seed average), each assertion carrying a ratio
threshold **plus an absolute margin and a minimum eligible-reader count** ([fable]#2, [sol]#3). Separate gates
([sol]#1, [fable]#1/#7):
- popularity ≥ 5× analytic floor;
- keyword-only BM25 ≥ 2× floor; genre cosine ≥ 2× floor; **content < CF**;
- item-item CF ≥ 1.3× popularity;
- **learned MF (from the interaction log) > popularity and ≥ content**;
- **true-affinity oracle ≥ 2× popularity** (NO "oracle ≥ CF" assertion); observation-propensity oracle ≫ all (ceiling sanity);
- positive-rate "quality" < popularity (U2 guard);
- **keyword latent-neighbour overlap > genre-controlled baseline** (keywords encode finer-than-genre structure);
- U2 coverage guards (popularity coverage < 0.05 and < 0.1× random; head-share 1.0).
This harness is the durable guard AND this plan's named verification.
**Verify:** harness green on the tuned generator; **"guard has teeth"**: it FAILs both when α is raised (popularity
swamps affinity) AND when β→0 (no taste signal) ([fable]#8).

### Phase D — regenerate + checksums
Regenerate `recsys/data/generated/` (gitignored) via the seeded scripts; update `checksums.json` generation; confirm
CI's regenerate-then-check path is deterministic (byte-stable across two runs). No data committed.

### Phase E — Unit 1–2 re-validation + ERRATA (Opus subagents; content, asserts AND prose)
This is NOT prose-only. Re-run U1 and U2 lessons/exercises/solutions/milestones/**teacher-notes** against the
regenerated data and authorize these specific edits (inventory from [sol]#2 + [fable]#3/#4):
- **U1 interaction-derived pins** (certain break): `unit-01.../solutions.ipynb` cell 11 `seen=={309,419,…}` /
  `relevant=={400}` (reader-0) → update to the new values. U1 **catalog-search** pins (cell 7 `[377,489,903,1052,
  1542]`/`[2,7,21,40,45]`) and the `(5,5)` shape (cell 11/`:91`) are PRESERVED by Phase A (separate keywords file +
  draw-order) — verify, don't edit.
- **U2 `readers_scored`** (certain break): `unit-02.../solutions.ipynb` cell 7 `readers_scored==368` → the new count
  (~500–520, positive rate 0.23→0.33); likewise all "368 readers" prose: U1 lesson md19, U2 lesson md10/md12,
  `unit-02.../teacher-notes.md:32,65`, `projects/bookrec/milestones/unit-02-popularity.ipynb:99,237`.
- **U2 quality-vs-floor narrative BREAKS** (per [fable]#3): drop `solutions.ipynb` cell 11
  `assert quality_hit < random_board.hit_rate_at_k`; rewrite the lesson md22 "below even the random floor (~0.005)"
  claim and its causal explanation — quality now lands ~1–2× the floor (NOT below) but **5–10× below popularity**;
  the point becomes "ranking by positive-RATE ignores BOTH popularity AND the reader, so it barely clears random and
  loses badly to popularity" — the popularity-bias LESSON is preserved, the "below the floor" detail is corrected.
  Update the matching exercise (Ex5) + its solution + the milestone prose. Keep `quality < popularity` (an assert).
- **U2 value-pinned test contracts** (`projects/bookrec/tests/test_unit02.py:82-85` pop `>0.05` and `>5×` random; the
  coverage asserts): re-verify they PASS on regenerated data (they do in the α=0.75 regime — pop ~0.10–0.12, ~10×);
  do not weaken unless a measured value forces it (then relax to direction + record why).
- Update U2 lesson md25 "~0.007 / 14 of 2000" coverage figures to the new seed.
Add an `ERRATA.md` entry in `unit-01-problem-and-scoreboard/` and `unit-02-popularity-and-bias/` noting the
recsys-004 regeneration, the figure updates, and the U2 quality-vs-floor correction. Re-run U1/U2 notebooks to the
new values; keep `execution_count: null`/cleared outputs.
**Verify:** `exec-lessons`/`exec-solutions`/`hygiene`/`exercise-structure`/`concept-scan`/`milestone-check` green for
U1+U2; `test_unit01.py`/`test_unit02.py` green.

### Phase F — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN (lint; the new recoverability harness + updated generator tests
+ routed recsys suite; U1/U2 regenerated exec; PDFs) AND `bash scripts/pre-merge-guard.sh --pr` OK.

## Out of scope
No new concepts/coverage-map/unit (this is data+tooling; `concepts.yaml`/`coverage-map.yaml` unchanged); Unit 3
lexical is re-drafted as **recsys-005** on this data; no real-catalog data (still synthetic/seeded); the committed
**GloVe subset** still lands with U7 (this plan only establishes the vocabulary it derives from); `buildout` unchanged
(no lesson-count change). No change to the `RetrievalPath`/scoreboard contracts.

## Verification phase & unit-exemption note
This plan ships **no unit/project/checkpoint**, so the plan-review "named verification phase for shipped units" rule
is satisfied by exemption here; nonetheless its substantive verification is the **Phase C recoverability harness**
(+ Phase F `ci-local`), which the reviewers should treat as the acceptance gate.

## Plan Review

### Round 1 (on v1)

**[self] — APPROVE.** The slice is the correct, user-approved response to the empirically-established premise
failure (oracle ≈ floor). The taste-aware exposure contract + latent-correlated text address both the recoverability
gap (all personalization units) and the text gap (U3/U7). The committed recoverability harness (Phase C) makes the
pedagogy a durable CI invariant and is the real acceptance gate. Regeneration risk to U1/U2 is bounded (gitignored
data; direction/rank-based tests; prose re-verified + errata in Phase E) and the tuning explicitly preserves U1's
floor story and U2's popularity-bias story (taste via latent affinity ⇒ pure-rate "quality" stays weak). Design §6
amendment is in-scope (design doc, not a governance file) and gate-reviewed. No `concepts.yaml`/coverage changes, so
no curriculum-closure risk. No [self] blockers. `[glm]` skipped (weekend; volcengine non-functional; resume Monday).

**[sol] — REJECT** (approach empirically sound; plan needs tightening). In-memory prototype (α=0.5, β=0.15, 507
readers): random 0.0158, popularity 0.0730, genre-content 0.1460, true-affinity oracle 0.1834, item-item CF 0.0789,
quality 0.0158 → content/oracle clearly beat popularity and quality stays weak (**mechanism confirmed**), BUT CF only
1.08× popularity (target 1.3×).
1. `[OPEN]` **Must Fix** — Phase C harness is too loose ("keyword BM25 / genre cosine", "factorization or oracle"):
   require SEPARATE gates for (i) keyword-only lexical, (ii) a **learned MF trained on the observed interaction log**
   (not just the oracle), (iii) the true-affinity oracle, and (iv) **keywords encode finer latent structure beyond
   genre** (latent-neighbour keyword overlap controlling for genre) — else inert keywords or an unlearnable log pass.
2. `[OPEN]` **Must Fix** — U1/U2 regeneration impact understated; there are **value-pinned contracts**, not just
   prose: U1 `exercises.ipynb:62` teaches five columns + `solutions.ipynb:91` asserts `(5,5)` + seed-pinned
   search IDs / seen-relevant sets (116-117, 184-185); U2 `solutions.ipynb:136-137` + `tests/test_unit02.py:82-85`
   require popularity `>0.05` and `>5×` random (plan promises only ≥3×) and **quality < random** (new goal only
   quality < popularity). Phase E must inventory + authorize edits to lessons/exercises/solutions/milestones/
   teacher-notes/**tests**, preserving or explicitly revising each contract, and qualify U2's "exposure is
   popularity-driven" prose now that exposure is taste-aware.
3. `[OPEN]` **Should Fix** — pin numerics: raw affinity std≈11 (range −44…63); specify normalization before
   `exp(β·affinity)`; near the floor one hit ≈ 0.002–0.0027 over ~368–500 readers, so combine ratio thresholds with
   absolute margins + minimum eligible-reader counts, and/or average several deterministic seeds.
4. `[OPEN]` **Should Fix** — CF is not automatically recovered by α/β alone (1.08× popularity); Phase B must
   explicitly permit tuning **interaction density / reader-community recurrence** (e.g. readers drawn from latent
   clusters so co-occurrence is informative) to meet the CF gate.
(Otherwise the foundational-slice framing, latent-driven taste, §6 amendment, and no-concept/coverage exemption are
sound.)

**[fable] — APPROVE WITH NITS** (feasibility EMPIRICALLY CONFIRMED). Prototype (`scratchpad/taste_proto.py`,
exposure ∝ popularity^α · exp(β · per-reader-z-scored affinity), 3 seeds) found a working regime **α=0.75, β=2.5,
default density**: random ~0.011, popularity ~0.10–0.12 (~10×), genre cosine ~0.14–0.18, keyword BM25 ~0.17–0.22,
item-item CF ~0.24–0.33 (**2.6× pop**), true-affinity oracle ~0.26–0.31 (2.5× pop), exposure-aware-propensity oracle
~0.45–0.51, quality(m=10) 0.012–0.035 (5–10× below pop), pop coverage ~0.007 — every plan target met on all 3 seeds
(incl. U2's `>5×` and coverage asserts). α≥0.75 needed (α=0.5 risks pop<5×random); β≥2.0 needed (β≤1.5 fails CF at
default density unless sessions raised to 10–15).
1. `[OPEN]` **Must Fix** — "MF/latent-oracle ≥ CF" is NOT reliably true: val positives stay exposure-gated, so
   co-occurrence CF can beat the pure true-affinity oracle (coin-flip at α=0.75). Define the harness ceiling as the
   generator's **observation-propensity oracle** (α·log pop + β·z-affinity, ~0.45–0.51) and/or **drop "oracle ≥ CF",
   keeping only "true-affinity oracle ≥ 2× popularity"** (holds at α=0.75).
2. `[OPEN]` **Must Fix** — ratio thresholds vs a **single-draw** random floor are ±50% noisy at ~370–520 readers
   (floor ranged 0.0077–0.0173 same config). Use the **analytic expected floor** (U1's `1−C(N_u−r,k)/C(N_u,k)`
   averaged over scored readers) or a ≥50-seed average as the denominator; numerator paths (0.1–0.3) are fine.
3. `[OPEN]` **Should Fix** — Phase E: U2's `assert quality_hit < random_board.hit_rate_at_k` + the "below even the
   random floor (~0.005)" prose + its causal explanation **BREAK** (quality is now ~1–2× the floor, never below).
   Drop the floor comparison, rewrite the explanation (quality loses because it ignores BOTH popularity AND the
   reader; exposure now tracks taste too), keep the popularity-bias point and `quality < popularity`.
4. `[OPEN]` **Should Fix** — enumerate certain U1/U2 breaks in Phase E: U1 `solutions.ipynb` cell 11
   `seen=={309,419,…}`/`relevant=={400}` (reader-0 interaction pins); U2 `solutions.ipynb` cell 7
   `readers_scored==368` → ~500–520 (positive rate 0.23→0.33); all "368 readers" prose (U1 lesson md19, U2 lesson
   md10/12, **teacher-notes.md:32,65**, milestone:99,237), U2 lesson md25 "~0.007 / 14 of 2000". Direction-based
   `test_unit01/02.py` pass in the regime. Add teacher-notes.md to Phase E's list.
5. `[OPEN]` **Should Fix** — specify β acts on **per-reader z-scored** affinity (raw per-reader std ≈12) in the
   Phase 0 contract + `_common.py` knob docstring, else `exp(β·affinity)` is ill-conditioned.
6. `[OPEN]` **Should Fix** — Phase A must draw keyword tokens **after** the existing author/year/genre/latent/
   popularity rng draws (or from a derived sub-stream) so U1's pinned catalog-search ids (`solutions.ipynb` cell 7
   `[377,489,903,1052,1542]`/`[2,7,21,40,45]`) survive (search haystack excludes keywords — `bookrec/search.py:28-35`).
7. `[OPEN]` **Nice to Have** — latent text barely beats genre-only text (latent ≈ linear image of genres;
   `latent_noise 0.2` vs `genre_latent_scale 1.8`). If U5 MF should visibly beat U3 content, raise `latent_noise`
   (independent latent component) and add explicit harness orderings **content < CF** and **learned-MF > content**.
8. `[OPEN]` **Nice to Have** — record the tuned (α,β) + 3-seed table in the Post-Execution Report; the
   "guard has teeth" check flips **β→0 AND α↑** (both must turn the harness red).

### Plan-review outcome (round 1): **NOT consensus — [sol] REJECT + [fable] APPROVE WITH NITS.** Mechanism empirically confirmed (working regime α=0.75,β=2.5); all findings fold into v2. Re-review round 2.

### Round 2 (on v2 — all round-1 findings folded)
**[self] — APPROVE.** v2 folds every [sol] + [fable] finding: analytic-floor denominators + absolute margins + min
reader counts ([fable]#2/[sol]#3); observation-propensity oracle ceiling and dropped "oracle≥CF", kept
"true-affinity≥2×pop" ([fable]#1); keyword text as a SEPARATE `keywords.csv.gz` (U1 5-column catalog + `(5,5)`
preserved) with keyword draws after the existing rng stream (U1 search ids preserved) ([sol]#2/[fable]#6); z-scored
affinity ([fable]#5/[sol]#3); per-technique harness gates incl. a learned-MF-from-interactions and
keywords-encode-latent-beyond-genre ([sol]#1); content<CF, MF>content, raised latent_noise ([fable]#7); α=0.75/β=2.5
regime + explicit CF-tuning latitude ([sol]#4); full U1/U2 re-validation inventory incl. the U2 quality-vs-floor
narrative correction and teacher-notes ([fable]#3/#4); guard-has-teeth flips β→0 AND α↑ ([fable]#8). Mechanism
empirically confirmed on 3 seeds. No [self] blockers.

<!-- [sol] / [fable] round 2 appended -->

## Content Review

<!-- appended pre-PR (code/data review: no student content ships; reviewers verify recoverability + U1/U2 re-validation) -->

## Post-Execution Report

<!-- appended before ship -->
