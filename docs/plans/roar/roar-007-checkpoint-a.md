# Plan roar-007 — Checkpoint A: a clean agent on a track it was not tuned for

**Design:** `docs/designs/013-roar-book.md` **v4.4** (§4.3 the seeded checkpoint tracks, §6 CP-A, §7.1).
**Book:** `roar`. **Autopilot** per AGENTS.md.
**Base:** branches from `main` after `roar-006` merges (#161, d14572c).
**v2.1** folds round 2's nits (probe vs gate time cap, the fixed reference settings, pinned file stems, the
cell cap 11, the length table).
**v2** folds plan-review round 1 ([sol] REJECT: B the `test-circuit` column was raced under another track name, so
with another hidden grip, S Question 6's plan, S the race counts; [fable] APPROVE WITH NITS: S1 the routed budget, S2
the notebook cell cap, S3 the weave evidence and Question 4, N1–N6). `test-circuit` is re-probed under its own name
(`q28`, matching the Unit 7 pins) and the failure mode is recorded (`q29`); every conclusion holds.

## Scope
- Checkpoint A `roar/checkpoints/checkpoint-01-part-1/`: `checkpoint.ipynb` (the brief and the questions, no
  solutions, no outputs), `solutions.ipynb`, `teacher-notes.md`, `manifest.yaml`.
  It is **strict**: no borrowed tools, every task draws only on Units 1–7 concepts, and it introduces nothing.
- **Generator:** the design's seeded checkpoint tracks (§4.3, "unseen-for-tuning checkpoint tracks from named seeds")
  become generated outputs: `test-circuit-seed1` … `test-circuit-seed4` (the **training family**) and
  `test-circuit-seed2026` (the **checkpoint track**), built by the existing `gen_tracks.seeded_track`.
  `load_track` already loads any generated track by name, so **`racekit` itself does not change**.
- Reference submission `agents/checkpoint-a.py`: `agents/unit-07.py` with `A_LAT = 4.2` (the family margin value,
  below) and a header comment saying why; nothing else differs.
- A routed premise test for the gates; registry, syllabus and design entries.

## The idea, and why the checkpoint has one
The design's gate is "finishes within a target time, with 0 collisions" on a track the agent was not tuned for.
The probe shows this is a real test, not a formality: **the Unit 7 reference, tuned on `test-circuit` alone, crashes
on every run of the checkpoint track.**
- `agents/unit-07.py` (A_LAT 4.6, the margin value one grid step inside `test-circuit`'s edge 4.8) on
  `test-circuit-seed2026`, `carla_like(noise=True)`, seeds 0–4: 48–49 collisions per run, never finishes (`q24`).
- **What the car does (`q29`, recorded):** on a straight (|κ| = 0 at the waypoint), after a corner, the car weaves
  with a growing amplitude over about 4 s until it reaches the wall. On the checkpoint track at 4.6, race seed 0: the
  cross-track error every 0.5 s before the first collision runs −0.24, −0.95, −1.07, −0.11, +1.49, +1.94, +0.69,
  −2.40 m, at 37.5 m/s, in grip section 2 (sections 3–5 never reached). On training seed 1 at 4.6, race seed 1:
  0.01, −1.14, −1.28, −0.09, +1.78, +2.46, +1.30, −1.75 m at 45.6 m/s, in section 0. At 4.4 the same races are clean
  (max |e| by section ≤ 1.57 m and ≤ 1.40 m). The plan pins this as **observation**, not a causal story: the
  solutions describe it and name the candidate causes in Unit 5–6 terms; nothing is graded on one mechanism.
- **Why a neighbouring track differs.** A seeded variant changes every corner's radius by a factor in [0.85, 1.15]
  and every half-width by [0.9, 1.1]; and the carla-like car's grip is not the same on every track (its hidden grip
  is drawn per track, as a real circuit's would differ). A setting at the edge of one track can sit past the edge of
  a neighbour. The checkpoint says only what a student can observe: the variants differ in shape and the car may
  grip differently on each; it never reads or quotes the hidden grip.

The fix uses only taught tools: Unit 1's repeated-run measurement and Unit 7's clean and margin rules, applied to a
**family of training tracks** instead of one. The brief names the family and the checkpoint track up front
(seeds 1–4 and 2026; the checkpoint seed was fixed before it was probed). Tuning on the checkpoint track is forbidden
by the brief; the solutions race it **once**, five seeds, after every choice is frozen (the sealed-track discipline of
the recsys Checkpoint A).
This is a practice of `repeated-run-measurement` and `section-knob-sweep` (whose margin rule and "five clean seeds do
not prove the sixth" Unit 7 taught), not a new concept; held-out tracks and overfitting as named ideas stay in Unit 12.

## Probe evidence (`q22`–`q29`, scratchpad `u07cp/`; `carla_like(noise=True)`, seeds 0–4, A_DEC 5.0, PP_K 0.5, lead 0.3 s)

| A_LAT | `test-circuit` | seed 1 | seed 2 | seed 3 | seed 4 | **seed 2026** (checkpoint) |
|---|---|---|---|---|---|---|
| 3.4 | 326.75 | 324.05 | 326.20 | 327.60 | 327.30 | 326.75 |
| 3.8 | 318.45 | 316.00 | 317.85 | 319.00 | 318.85 | 318.25 |
| 4.0 | 314.65 | 312.30 | 314.20 | 315.20 | 315.15 | 314.50 |
| 4.2 | 311.10 | 308.75 | 310.55 | 311.60 | 311.55 | **310.80** (spread 0.20, max \|e\| 1.44 m) |
| 4.4 | 307.55 | 305.40 | 307.15 | 308.15 | 308.05 | 307.30 |
| 4.6 | 304.15 | ✗ (seed 1: 1 collision, max \|e\| 6.02 m) | 303.90 | 304.75 | 304.70 | ✗ (48–49 collisions every run at the 1500 s probe cap) |
| 4.8 | 300.90 | — | — | — | — | — |
| 5.0 | ✗ (17 collisions every run at the 1500 s probe cap) | — | — | — | — | — |

All cells are medians in seconds over race seeds 0–4; every cell without ✗ is clean (finished, 0 collisions, max |e|
≤ 2 m). The `test-circuit` column is `q28`, raced under the track's own name; it reproduces Unit 7's pins (4.6 →
304.15 s, 4.8 → 300.90 s, 5.0 unclean). The other columns are `q22`/`q24`/`q26`/`q27` on the generated seeded tracks
under the names the generator will write. A_LAT 3.0 on the checkpoint track: 336.45 s, clean, **outside** the target.
`agents/unit-06.py` on the checkpoint track: 420.40 s, clean. The tracks (seed: length m / waypoints / half-width
min–max m / tightest radius m): 1: 2625.6 / 1313 / 5.10–6.58 / 17.7; 2: 2662.0 / 1331 / 5.01–6.47 / 18.7; 3: 2670.4 /
1335 / 5.13–6.36 / 20.5; 4: 2675.0 / 1337 / 5.14–6.58 / 17.3; 2026: 2655.8 / 1328 / 5.15–6.56 / 19.8; all with
continuous curvature and 0 self-intersections; each builds in 0.01 s. Wall time per race 2.7–3.8 s; a crashing race
runs to its time cap (about 17 s at 1500 s, about 5 s at 450 s). **The probes used `max_seconds=1500`; the gates
and notebooks use 450** (a clean lap takes about 320 s), so a ✗ cell's collision count is a 1500 s probe figure and
is never asserted: a gate asserts only "not clean" (not finished, or a collision, or max |e| > 2 m), confirmed at 450 s
during implementation (`q29` at 450 s: 14 collisions on the checkpoint track at 4.6, race seed 0) ([sol] r2 N,
[fable] r2 N1).

Also recorded (not in the checkpoint): on `monza-like` seeds 2–4 the Unit 7 reference crashes too; A_LAT 3.4 is clean
on all four (`q23`). This is the Unit 7 agent's fragility outside its tuning track. It is a **follow-up** and a named
risk for the interim CARLA check (the CARLA map is not `monza-like` either) and for `roar-008`/`roar-010` (Unit 11,
robustness), not something this plan changes. It is registered in the run's held follow-up list and in the
post-execution report ([fable] N5).

## Gates (pinned from the probes; a miss means stop, amend and re-gate)
The grid is Unit 7's: A_LAT in steps of 0.2, A_DEC 5.0, PP_K 0.5, `PROFILE_LEAD_S` 0.3, `GRIP` all 1.0
(per-section knobs are per track; tuning them on the family is out of scope).
- **CP.1, the tracks:** the generator writes the five tracks, byte-stable (the existing checksum contract), each with
  0 self-intersections, continuous curvature, half-widths in the existing [5.0, 8.0] m bound, and the measured
  lengths, waypoint counts, half-width minima and tightest radii above (±0.1 m; ±0.01 m for the half-widths).
  The five file stems are pinned literally: `test-circuit-seed1`, `test-circuit-seed2`, `test-circuit-seed3`,
  `test-circuit-seed4`, `test-circuit-seed2026`. The routed test loads them by these literal names, with a comment
  that the carla-like car's hidden grip is keyed to the name, so a rename changes the car and invalidates every pin
  ([fable] r2 S1).
- **CP.2, one track is not enough:** on `test-circuit` alone the edge is 4.8 (clean, 300.90 s) with 5.0 unclean, so
  the margin rule gives 4.6, and 4.6 is **not clean** on training seed 1 (race seed 1: 1 collision).
- **CP.3, the family edge:** 4.4 is clean on all five training tracks on seeds 0–4 (medians as the table) and 4.6 is
  not, so the margin rule gives **4.2**, clean on all five (medians 311.10 / 308.75 / 310.55 / 311.60 / 311.55 s).
- **CP.4, the checkpoint race** (`agents/checkpoint-a.py`, `test-circuit-seed2026`, seeds 0–4, once): clean on every
  seed, median **310.80 s**, within the **target 330 s**; the Unit 6 agent's 420.40 s is not. The target sits above
  every clean grid value from 3.4 up (326.75 s at 3.4) and below 3.0's 336.45 s, so it rewards speed planning
  without demanding the edge. It is a racekit target on this track and has nothing to do with the book's 329 s CARLA
  bar on Monza (the teacher notes say so, [fable] N3).
- **CP.5:** `check_submission` passes on `agents/checkpoint-a.py`.
- **Where each gate is asserted** ([sol] S3, [fable] S1–S2). Only gate-bearing cells are raced; the rest of the table
  is probe record, labelled so wherever it is quoted.
  - CP.1 in `roar/data/tests/test_gen_tracks.py` (the driver test's output list gains the five names; generation
    budget re-measured).
  - The routed test `test_racekit_checkpoint_a.py`, cells × race seeds 0–4: `test-circuit` {4.2, 4.4, 4.6, 4.8, 5.0};
    seed 1 {4.2, 4.4, 4.6}; seeds 2–4 {4.2, 4.4} each; seed 2026 {4.2, 4.4, 4.6} plus `unit-06.py`; that is
    5 + 3 + 6 + 4 = 18 cells, **90 races** (11 of them crash: 5.0 on `test-circuit`, 4.6 on seed 2026, one race of
    4.6 on seed 1), all at `max_seconds=450`: about 79 × 3.3 s + 11 × 5 s ≈ 315 CPU-s, **about 45 s on 8 workers**.
    `agents/checkpoint-a.py` is the 4.2 cell; `check_submission` on it (CP.5).
  - The solutions notebook, one track per cell (at most 11 races, about 40 s, under the 120 s cell cap): Question 3 races
    `test-circuit` at 4.6, 4.8 and 5.0 (5 + 5 + 1, stopping a value at its first unclean race); Question 4 races 4.6 on
    seeds 1–4 (2 + 5 + 5 + 5); Question 5 races 4.4 on the five training tracks (25) and freezes 4.2 by the margin
    rule without racing it there (the routed test does); Question 6 races the checkpoint track once (5). That is
    **58 races, about 3.5 min** (an upper bound measured under 8-way load; the report records the serial time,
    [fable] r2 N4); the cell-level cap holds because no cell races more than 11.

## The checkpoint (questions; the brief opens with the project)
**Brief:** "Your Unit 7 agent is fast on `test-circuit`. Race day is on a track you have never driven: a variant of
`test-circuit`, every corner a little tighter or looser, every straight a little narrower or wider. You may tune on
four other variants of the same family. You may race the checkpoint track once." The rules: no tuning on the
checkpoint track; one global setting, A_LAT on Unit 7's grid, with A_DEC, PP_K and the lead **fixed at the Unit 7
reference's 5.0, 0.5 and 0.3 s** and `GRIP` all 1.0 (a Unit 7 file may ship its accepted per-section vector; reset
it) ([sol] r2 N, [fable] N2); the clean rule on five seeds; target median ≤ 330 s. Every numeric gate uses these
reference settings. Loading the checkpoint track and planning on it is allowed; racing it
before race day is not.
The student's submission is **their own Unit 7 submission** (the notebook points at `agents/unit-07.py` as the
stand-in and says to use theirs); variants via `write_variant` (Unit 1).
1. **Know the family.** Load the five training tracks; compute each one's length and its tightest radius from your
   own Menger curvature (Unit 2) and compare with the track's stored curvature; plot the five centrelines.
2. **Plan a lap on paper.** Write the forward–backward speed profile (Unit 7) as a function and compute each training
   track's planned lap time at A_LAT 4.6; check the result against the lesson's two passes: no waypoint above its
   cornering cap (the cap pass), and no step braking harder than A_DEC (the backward pass).
3. **Tune on one track.** Find `test-circuit`'s edge on the grid (clean rule, five seeds) and apply the margin rule.
4. **Check the family.** Race that value on the four variants. Where it fails, plot the failing race's cross-track
   error and speed against time for the 10 s before the first collision, **describe** what the car did, and
   **propose** a cause in Unit 5–6 terms (the lookahead at speed, the grip, the corner before) and one race that
   would test it. Graded on the description and the reasoning, not on one mechanism ([fable] S3).
5. **Tune on the family.** Find the highest grid value clean on all five training tracks, apply the margin rule, and
   freeze it; `check_submission` your frozen submission.
6. **Race day.** First, with the setting frozen, compute the planned lap time on the checkpoint track with
   Question 2's function ([sol] S2; planning on it is allowed). Then race it once on five seeds; report the median
   and spread, the clean rule and the target. Compare the race with the plan and with the Unit 6 agent's time (given,
   420.40 s): what did speed planning buy, and what did the margin cost?

## Phases

### Phase A: tracks, reference, routed test, registry (Opus subagent for the code; registry inline)
- `roar/data/gen_tracks.py`: `SEEDED_TRACKS = (("test-circuit", 1), …, ("test-circuit", 4), ("test-circuit", 2026))`
  and their names; `generate.py` step 1 writes them with the named tracks (same checksum contract);
  `test_gen_tracks.py` covers them (CP.1): the driver test's exact output list gains the five names, the per-track
  fixture covers them (the [5.0, 8.0] half-width bound holds: 5.01–6.58; the name-keyed length table gains the five
  names with `test-circuit`'s (2300, 2800) range, [fable] r2 N3), and the 60 s generation budget is
  re-measured ([fable] N1). `racekit`'s `TRACK_NAMES` stays the three named tracks; `conftest`'s missing-track check
  also names the seeded ones.
- `agents/checkpoint-a.py` and `tests/test_racekit_checkpoint_a.py` (CP.2–CP.5), reusing `_agent_premise.py`'s
  job runner with a track path.
- `coverage-map.yaml`: `checkpoint-01-part-1`, `kind: checkpoint`, `lessons: 0.5`, `introduces: []`, `requires` all
  23 Unit 1–7 concepts, `practices` those the questions use; the manifest mirrors it; `syllabus.md` row (no emoji).
- Design 013 **v4.5**: §4.3 names the seeded tracks and the checkpoint seed 2026; §6 CP-A's gate gets the target
  330 s and "tuned on the training family only"; changelog.

### Phase B: checkpoint statements (Opus subagent) and solutions (Opus subagent, a separate fresh session)
- `checkpoint.ipynb` per the questions above; TODO cells, no outputs, nothing that answers a question.
- `solutions.ipynb` asserting the gates as listed; races capped at 450 s on the training family.

### Phase C: teacher notes (active session, inline)
Goals, a 60–90 min sitting plan (the training sweep is the long part; the short form gives Question 3's edge), the
weave as the discussion centre, grading (the race is pass/fail on the clean rule and the target; the written
answers carry the rest; since this plan's table is public, the grade rests on the family-sweep evidence and the
written answers, never on the final number alone, [fable] N6), the 330 s target vs the 329 s CARLA bar, common
mistakes (tuning on the checkpoint track; racing it twice; stacking a per-section
vector from Unit 7).

### Phase D: verification (named)
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN; `bash scripts/pre-merge-guard.sh --pr` OK.
- Every gate holds where listed; the checkpoint notebook passes hygiene (no outputs, no solutions); the routed roar
  suite **≤ 7.5 min** measured (6.3 min before this plan; headroom kept for `roar-008`); the checkpoint solutions
  ≤ 4 min; the post-execution report records both, the generation time, and the book-level executed-notebook total
  against the 15 CI-minute cap ([fable] N4).

## Out of scope
- Any `racekit` library change; any change to `agents/unit-07.py` (its fragility is a follow-up, above).
- Per-section knobs on the family (the sections fall on different corners per track; Unit 12 owns many-knob tuning).
- A CARLA lab (CP-A has none in the design); system identification (Unit 8).

## Plan Review

### Round 1 (v1 @ 7b1da85)
- [self] APPROVE WITH NITS: the solutions notebook's race count sits at the 4-min budget; drop re-racing the frozen
  value on the family (the routed test asserts it). [FOLDED v2]
- [sol] REJECT:
  - **B** The `test-circuit` column was raced under the name `test-circuit-base`, and the carla-like car draws its
    hidden grip from the track name, so those pins came from another car. [FIXED v2: re-probed under the real name
    (`q28`); it reproduces Unit 7's 304.15 / 300.90 s and 5.0 unclean; every gate and conclusion holds, and the plan
    now says the hidden grip differs per track without reading it.]
  - **S** Question 6 compared with a plan Question 2 never computed. [FIXED v2: Question 6 computes it first.]
  - **S** The race counts were understated. [FIXED v2: exact job lists, 90 routed races, 58 notebook races.]
- [fable] APPROVE WITH NITS:
  - **S1** routed budget and race count [FIXED v2: gate-bearing cells only, 450 s cap, ≤ 7.5 min measured target];
  - **S2** the 120 s cell cap [FIXED v2: one track per cell, ≤ 10 races];
  - **S3** the weave was unrecorded and Question 4 graded one mechanism [FIXED v2: `q29` pinned as observation;
    Question 4 asks for a description and a proposed, testable cause; Question 2 uses the lesson's two passes];
  - **N1** generator test fallout [FIXED v2]; **N2** brief precision (GRIP reset, own A_DEC/PP_K/lead, planning on the
    checkpoint track allowed) [FIXED v2]; **N3** the target's floor (3.0 → 336.45 s) and 330 vs 329 [FIXED v2];
    **N4** book-level exec total and generation time in the report [FIXED v2]; **N5** the follow-up is registered
    [FIXED v2]; **N6** grading not on the public final number [FIXED v2].

### Round 2 (v2 @ 3eadc61): CONSENSUS
- [sol] APPROVE WITH NITS: B fixed (`q28` supports every revised cell), Question 6 fixed, 90 routed and 58 notebook
  races recounted. N: label the probe cap vs the gate cap [FIXED v2.1]; N: one rule for A_DEC/PP_K/lead [FIXED v2.1:
  fixed at the reference's values].
- [fable] APPROVE WITH NITS: every cell and `q29` verified against the pickles; name consistency verified. S1 pin the
  five file stems [FIXED v2.1]; N1 assert "not clean", never a cap-dependent count [FIXED v2.1]; N2 the cell cap is 11
  [FIXED v2.1]; N3 the name-keyed length table [FIXED v2.1]; N4 record the serial notebook time [FIXED v2.1, in Phase D's
  report].
- [self] APPROVE.
