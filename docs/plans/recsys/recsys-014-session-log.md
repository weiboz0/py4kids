# Plan recsys-014 — Session-log generator: genuine order signal for the sequence unit (data foundation for U12)

**Design:** `docs/designs/011-recsys-book.md` (§6 data contract — **amended here**; §8 row 12; §7 ceilings).
**Book:** `recsys` (Book 3). **Autopilot** per AGENTS.md. **User-approved 2026-10-07** (option "separate session log
for U12"). This is a **data/tooling foundation slice, not a unit** (like recsys-004): it adds a seeded, separate
**session log** with real order structure so Unit 12 (sequence-aware retrieval, **recsys-015**) has something true to
teach, while the main interaction log stays **byte-identical** so no number in Units 1–11 or Checkpoint A moves.

## Motivation (empirically established — U12 pre-plan probe, 2026-10-07)
On the current log (`interactions.csv.gz`; val, k=10, 500 eligible readers, cold excluded, SE ≈ 0.021):
- A tiny **SASRec** (1 block, dim 32, the design §7 ceiling) scores **0.17–0.21** in every config — *below* plain
  item-item CF (0.252) — and a **shuffled-history control scores the same** (mean 0.194 vs ordered 0.203 over seeds
  0–3). Removing the positional embedding *helps* (0.248): position is noise on this log.
- **Recency** weighting of bag paths gives < 2 SE (CF decay γ=0.9 +0.014; two-tower last-3 +0.020).
- **Author-following is null-level** (author-match of the next read vs last/first reads 0.003–0.005 ≈ random 0.005):
  `author_exposure_recur=0.3` is tiny next to β·z-affinity (2.5/SD), never decays, and `liked_authors` is an
  order-free set. **Drift** is small and only touches acceptance (latent cosine session-0→val 0.974).
- Histories are short (median 8 train positives; ~4.3k next-item transitions) — `max_len=50` is never reached.

⇒ Design 011 §6 promises "timestamps + ordered sessions; series/author-following; taste drift → U12", but the shipped
log's sequential signal is **order-insensitive**. Redesigning the main generator would move every pinned number in
U2–U11 + Checkpoint A (a multi-plan rework); the user chose a **separate session log** instead.

## Goals (committed acceptance criteria — the named verification)
1. **Byte-stability (hard gate).** `catalog.csv.gz`, `interactions.csv.gz`, `keywords.csv.gz`, and
   `cold_partitions.json` are **byte-identical** to the current committed-seed output (sha256-pinned in a test), so
   every U1–U11 + Checkpoint A number and assert is untouched. The new artifacts draw only from **independent
   `SeedSequence(seed).spawn(...)` sub-streams** (the recsys-004 keyword trick) and never advance the threaded RNG.
2. **New artifacts** (gitignored, regenerated-only, gzip'd CSV, seeded):
   - `series.csv.gz` — `item_id, series_id, volume`: ~25–30% of the 2,000 catalog books grouped into series of 3–5
     volumes (other books: no row). Series membership is a *catalog-side observable*; it does **not** change the
     catalog CSV.
   - `sessions.csv.gz` — the **U12 session log**, same 6-column schema as `interactions.csv.gz`
     (`reader_id, item_id, session_id, timestamp, split, label`), its own synthetic reader population over the same
     catalog, per-reader time-ordered sessions, and a per-reader `train < val < test` split **by session**. Longer
     histories than the main log (target median ≥ 20 train positives) so a capped sequence model has transitions to
     learn from (still within design §7's seq-len ≤ 50).
3. **Order signal is real and recoverable** — a committed **session recoverability harness** (numpy, routed with the
   recsys group) with ratio + absolute-margin + min-eligible-reader gates on the session log's `val` (k=10):
   - an **order-aware reference** (a first-order **transition** recommender: next-item counts from the reader's LAST
     train item, learned from train transitions; plus a **last-k** CF variant) beats the **bag** item-item CF (all
     seen) by a clear margin;
   - an **order-shuffled control** of the transition recommender (each reader's train sequence permuted before
     learning/querying) drops **well below** the ordered one — order, not the item set, carries the lift;
   - **next-in-series**: for val positives that are volume v+1 of a series whose volume v the reader read last, the
     transition reference ranks them in the top-10 far more often than bag CF;
   - sanity: popularity is a strong-but-beatable baseline and bag CF still beats popularity on the session log (the
     book's earlier lessons still hold on it).
   Thresholds are pinned from the Phase-B measurement (not pre-bound to unmeasured numbers) and re-checked on ≥3
   seeds; the harness enforces a minimum eligible-reader count.
4. **SASRec feasibility (measured, reported — not a CI gate here).** Phase B measures, on the session log, a tiny
   SASRec at the design §7 ceiling (1 block, dim 32, seq-len ≤ 50, ≤ 40 epochs, CPU-deterministic) vs its
   **shuffled-order control** and vs bag CF / the transition reference, and reports per-fit time. The plan's U12
   premise holds only if **ordered SASRec ≫ shuffled SASRec** and **ordered SASRec > bag CF** by > 2 SE; if not,
   tune the generator (series strength, decay, mood persistence, history length) before shipping. The torch gate
   itself belongs to recsys-015 (U12), where the path ships.

## Phase 0 — Design 011 amendment (active session inline; reviewed by this plan's gate)
- **§6** "Synthetic interactions — per-unit signal spec": the U12 row now reads "**separate session log**
  (`sessions.csv.gz` + `series.csv.gz`): series with next-volume pull, decaying author-follow, short-term genre mood,
  longer histories → U12 sequence model". Add a short paragraph: *why a separate log* (the probe numbers above; the
  main log's sequential signal is order-insensitive; a main-generator change would move every pinned U2–U11 +
  Checkpoint A number), *what is shared* (the catalog + series observable; the taste-aware exposure form), *what is
  not* (U12 is scored on `sessions.csv.gz`, a different reader population — every U12 number must say so), and the
  byte-stability guarantee for the main artifacts.
- **§8 row 12**: note "scored on the session log (§6)".
- **§14 revision history**: **v5 (2026-10-07, via recsys-014)** entry.
(Design docs are not governance-protected files; this amendment is reviewed by the gate below.)

## Phase A — `series.csv.gz` (Opus subagent; numpy, seeded sub-stream)
In `recsys/data/gen_catalog.py` (or a new `gen_series.py`): `generate_series(catalog, config)` drawing from
`SeedSequence(config.seed).spawn(k)[i]` (an index NOT used by the keyword stream), grouping ~25–30% of books into
series of 3–5 volumes. Prefer **same-author, genre-coherent** series (pick an author's books and order them) so series
structure is consistent with the catalog. Config knobs in `DatasetConfig` with defaults (series_fraction,
series_len_min/max). Written by the generator CLI next to the other artifacts; added to the data dictionary
(`recsys/data/README` or wherever the artifacts are documented).

## Phase B — `sessions.csv.gz` generator + measurement (Opus subagent; numpy, seeded sub-stream)
New `recsys/data/gen_sessions.py`: `generate_sessions(catalog, series, config)` on its own sub-stream. Per synthetic
session reader: latent taste + genre prefs (fresh draws from the sub-stream, same distributions as the main readers);
taste-aware exposure base (`popularity^α · exp(β · z-affinity)`, same form as §6) plus **order mechanisms**:
1. **Series next-volume pull** — after a positive on volume v, volume v+1 gets a large exposure + acceptance boost in
   the next 1–2 sessions, decaying after.
2. **Decaying author-follow** — `author_bonus *= author_decay` each session; per-positive bump large enough to matter
   against β·z-affinity (the probe suggests ~1.5–2.0 with decay ~0.5).
3. **Short-term genre mood** — a per-session genre state persisting with probability `mood_persist`, boosting
   exposure to that genre.
4. Longer histories (`session_mean_sessions_per_reader`, `session_max_items_per_session` tuned for median ≥ 20 train
   positives) and the standard temporal split by session (val = the next session block, test sealed).
Every knob in `DatasetConfig` (prefixed `session_`), defaults chosen by measurement. Sized within budget (target
≤ ~60k events; generation ≪ 10 s).
**Measure + report (binding):** byte-identity of the 4 main artifacts (sha256 before/after); session-log stats
(readers, events, positives, median history length, transitions); the Goal-3 harness numbers on 3 seeds (bag CF,
last-k CF, transition reference, shuffled transition, next-in-series hit, popularity, analytic floor); and the
Goal-4 SASRec feasibility numbers (ordered vs shuffled vs bag CF, per-fit time, 3 seeds). Iterate the knobs until
Goal 3 holds with margin AND Goal 4's premise holds; report the final knobs and numbers.

## Phase C — session recoverability harness + byte-stability test (Opus subagent)
- `recsys/data/tests/test_session_recoverability.py` — the Goal-3 gates (ratio + absolute margin + min readers),
  thresholds pinned from Phase B with headroom; reference recommenders in `recsys/data/_reference_recommenders.py`
  (bag CF, last-k CF, first-order transition, shuffled control) — numpy only.
- `recsys/data/tests/test_main_artifacts_byte_stable.py` (or extend an existing invariants test) — sha256 of
  `catalog.csv.gz`, `interactions.csv.gz`, `keywords.csv.gz`, `cold_partitions.json` generated at the committed seed
  equal pinned values captured BEFORE this plan's changes.
- Invariants for the new artifacts: schema, split ordering (train < val < test per reader by time), series
  well-formedness (contiguous volumes, one series per book), determinism (two generations identical).

## Phase D — `bookrec` loaders (Opus subagent; tiny)
`bookrec.load_series(path) -> {item_id: (series_id, volume)}` and a `bookrec.sessions_path()`/data-dir convention so
U12 can call `run_validation_scoreboard(path, sessions_path, ...)` unchanged (same schema). Export without new heavy
deps; unit tests. No retrieval path here (the SASRec path is recsys-015).

## Phase G — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN (the new harness + byte-stability + invariants run in the routed
recsys step) AND `bash scripts/pre-merge-guard.sh --pr` OK. Confirm U1–U11 + Checkpoint A notebooks/tests are
untouched and still green (byte-stable inputs ⇒ identical outputs), and the generator + harness stay within the
whole-book CI budget.

## Out of scope
No student unit, lesson, exercises, or checkpoint (U12 content = **recsys-015**); no torch/SASRec retrieval path in
`bookrec` (recsys-015); no change to the main interaction generator or any shipped number; no registry/coverage-map
change (no concept is introduced — `lessons` total unchanged at 33.5). This is a data/tooling foundation slice:
there are no new units/projects/checkpoints, so the "named verification phase" rule is satisfied by Phase G.

## Verification phase declared
Phase G is this plan's named verification phase.

## Plan Review

<!-- appended after the 3-way plan-review gate -->

## Content Review

<!-- N/A content (no student-facing content); the content gate reviews the generator + harness + design amendment -->

## Post-Execution Report

<!-- appended before ship -->
