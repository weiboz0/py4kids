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
(k=10, cold excluded) the signal hierarchy is **recoverable** and matches the curriculum:
- **random floor** low (target ≈ 0.01–0.05);
- **popularity** a strong, beatable baseline (target ≥ 3× random) — **preserving Unit 2's "popularity is hard to
  beat / popularity-bias-in-the-metric" lesson**;
- **content** (genre/keyword BM25 or TF-IDF cosine over the new text) clearly beats random (target ≥ 2× random);
- **item-item co-occurrence CF** (U4) beats popularity (target ≥ ~1.3× popularity);
- **latent/MF** and the **true-affinity oracle** beat CF (oracle target ≫ popularity, e.g. ≥ 2× popularity);
- **pure positive-RATE "quality"** (Unit 2's weighted-rating lens) stays *weak* (below popularity), so Unit 2's
  lesson survives — achieved by driving taste through **latent affinity**, which `rate` does not capture.
These become a committed **recoverability harness** (Phase C) that fails CI if a future generator change breaks the
pedagogy. Exact thresholds are set from the tuned measurements and written into the harness (rank/ratio based, per
the `_common.py` numpy-version-robustness convention).

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
  `i` with probability ∝ `popularity(i)^α · exp(β · affinity(reader, i))`, where `affinity` combines a **latent**
  component (reader×item latent dot product) and a **content** component (reader feature-prefs · item genre/keyword
  features); positives arise among exposed items by a calibrated rate; **author-follow recurs across sessions**.
  State the design intent: popularity remains a strong baseline, but content/collaborative/latent signals are each
  **recoverable** and beat popularity (with the acceptance hierarchy above).
- add a **catalog text field** (`keywords`/`description`): per book, a variable-length bag of **real-English-word**
  tokens (with repetition → TF varies; lengths vary → BM25 `b` matters) sampled from a committed topic **vocabulary**
  conditioned on the book's latent factors + genres; this vocabulary is the slice vocabulary the **U7 GloVe subset**
  is later derived from (design §6 embeddings clause now has a concrete source).
- note the regeneration + the U1/U2 re-validation/errata and the committed recoverability harness.
- Revision history v4.

### Phase A — catalog text (`gen_catalog.py` + `bookrec/catalog.py`; Opus subagent)
- Add a committed **vocabulary module** (`recsys/data/vocabulary.py` or similar): a curated list of common
  real-English words grouped into ~`latent_dim`+`n_genres` topics (so GloVe coverage is near-total); seeded, no
  network.
- `gen_catalog.py`: add a `keywords` column — for each book, sample `T_i` tokens (T varying, e.g. 12–40) with
  repetition from a per-book word distribution built from its latent factors + genre membership (so books with
  similar latent/genre have similar text). Update `CATALOG_COLUMNS`, `Catalog`, and the catalog CSV writer; keep
  `item_id,title,author_id,genres,year` and append `keywords`.
- `bookrec/catalog.py`: `load_catalog` surfaces `keywords` in `Book.fields` (string); numpy-only, no pandas.
- Tests: catalog has the new column; keywords vocabulary ⊆ the committed vocabulary; deterministic under the seed;
  books sharing latent/genre have measurably higher keyword overlap than random pairs.
**Verify:** `gen_catalog` regenerates deterministically; `load_catalog` exposes `keywords`; U1/U2 notebooks (which
ignore `keywords`) still load the catalog unchanged in shape they use.

### Phase B — taste-aware exposure (`gen_interactions.py` + `_common.py`; Opus subagent)
- Implement the taste-aware exposure process (Phase 0 contract): exposure sampling ∝ `popularity^α · exp(β·affinity)`;
  `affinity` = `latent_scale`-weighted reader·item latent + `feature_weight`-weighted content (genre + keyword) term;
  positives among exposed by the calibrated rate; preserve the per-reader **temporal train/val/test** split, cold
  items/readers, sampled negatives, timestamps/sessions, and **make author-follow recur across sessions** (a read
  raises the exposure of the same author's other books in later sessions).
- Expose the ground-truth (latent factors, per-pair affinity) so the harness can run oracle checks.
- Add/rename config knobs in `_common.py` (`exposure_affinity_weight` β, keep `popularity_exposure_weight` α, etc.);
  **tune** α/β/weights to hit the Goals hierarchy (iterate with the Phase C harness).
**Verify:** deterministic regeneration; existing generator invariant tests updated and green; split/cold/negative
structure intact.

### Phase C — recoverability validation harness (Opus subagent; the named verification)
`recsys/data/tests/test_signal_recoverability.py` (routed `--group recsys`): regenerate (or load the regenerated)
data and assert the Goals hierarchy on `val` (k=10, cold excluded), each as a **ratio/rank** threshold with a margin:
random floor < bound; popularity ≥ 3× random; content(keyword BM25 / genre cosine) ≥ 2× random; item-item CF ≥
1.3× popularity; MF/latent-oracle ≥ CF; true-affinity oracle ≥ 2× popularity; pure positive-rate "quality" <
popularity (Unit-2 guard). Implement small reference scorers (popularity, content, co-occurrence CF, a few-epoch
latent factorization or the exposed-latent oracle) inside the test or a `recsys/data/_reference_recommenders.py`
helper. This harness is the durable guard against generator regressions AND this plan's named verification phase.
**Verify:** harness green on the tuned generator; it FAILs if α is raised so popularity swamps affinity again
(sanity check the guard has teeth).

### Phase D — regenerate + checksums
Regenerate `recsys/data/generated/` (gitignored) via the seeded scripts; update `checksums.json` generation; confirm
CI's regenerate-then-check path is deterministic (byte-stable across two runs). No data committed.

### Phase E — Unit 1–2 re-validation + ERRATA (Opus subagents per notebook; prose only)
Re-run U1 and U2 lessons/solutions/milestones against the regenerated data. Update the **prose numbers** to the new
seed values; confirm the **narratives hold** (U1: non-zero random floor beaten by later paths; U2: popularity ≫
floor, the weighted-rating *quality* lens still scores below popularity = popularity-bias-in-the-metric, coverage/
head-share directions). Confirm **direction/rank-based asserts still pass**; if any U2 assert was value-pinned,
relax to direction. Add an `ERRATA.md` entry in `unit-01-*/` and `unit-02-*/` noting the recsys-004 data
regeneration and the updated figures. If a narrative genuinely breaks (e.g. quality no longer < popularity), fix the
generator tuning (Phase B) rather than rewrite the lesson's point.
**Verify:** `exec-lessons`/`exec-solutions`/`exercise-structure`/`concept-scan`/`milestone-check` green for U1+U2.

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

<!-- verdicts appended -->

## Content Review

<!-- appended pre-PR (code/data review: no student content ships; reviewers verify recoverability + U1/U2 re-validation) -->

## Post-Execution Report

<!-- appended before ship -->
