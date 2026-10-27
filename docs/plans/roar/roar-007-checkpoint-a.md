# Plan roar-007 — Checkpoint A: a clean agent on a track it was not tuned for

**Design:** `docs/designs/013-roar-book.md` **v4.4** (§4.3 the seeded checkpoint tracks, §6 CP-A, §7.1).
**Book:** `roar`. **Autopilot** per AGENTS.md.
**Base:** branches from `main` after `roar-006` merges (#161, d14572c).

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
  The car leaves a corner hard, starts to weave on the following straight at 27–37 m/s, and the weave grows until it
  reaches the wall (`q25`); at A_LAT ≤ 4.4 the corner exit is gentle enough that it never starts.
- The seeded variants change every corner's radius by a factor in [0.85, 1.15] and every half-width by [0.9, 1.1].
  A setting at the edge of one track sits past the edge of a neighbour.

The fix uses only taught tools: Unit 1's repeated-run measurement and Unit 7's clean and margin rules, applied to a
**family of training tracks** instead of one. The brief names the family and the checkpoint track up front
(seeds 1–4 and 2026; the checkpoint seed was fixed before it was probed). Tuning on the checkpoint track is forbidden
by the brief; the solutions race it **once**, five seeds, after every choice is frozen (the sealed-track discipline of
the recsys Checkpoint A).
This is a practice of `repeated-run-measurement` and `section-knob-sweep` (whose margin rule and "five clean seeds do
not prove the sixth" Unit 7 taught), not a new concept; held-out tracks and overfitting as named ideas stay in Unit 12.

## Probe evidence (`q22`–`q27`, scratchpad `u07cp/`; `carla_like(noise=True)`, seeds 0–4, A_DEC 5.0, PP_K 0.5, lead 0.3 s)

| A_LAT | `test-circuit` | seed 1 | seed 2 | seed 3 | seed 4 | **seed 2026** (checkpoint) |
|---|---|---|---|---|---|---|
| 3.4 | 325.45 | 324.05 | 326.20 | 327.60 | 327.30 | 326.75 |
| 3.8 | 317.20 | 316.00 | 317.85 | 319.00 | 318.85 | 318.25 |
| 4.0 | 313.40 | 312.30 | 314.20 | 315.20 | 315.15 | 314.50 |
| 4.2 | 309.85 | 308.75 | 310.55 | 311.60 | 311.55 | **310.80** (spread 0.20, max \|e\| 1.44 m) |
| 4.4 | 306.40 | 305.40 | 307.15 | 308.15 | 308.05 | 307.30 |
| 4.6 | 303.15 | ✗ (seed 1: 1 collision, max \|e\| 6.02 m) | 303.90 | 304.75 | 304.70 | ✗ (48–49 collisions every run) |
| 4.8 | 300.00 | — | — | — | — | — |
| 5.0 | ✗ (47–50 collisions) | — | — | — | — | — |

All cells are medians in seconds; every cell without ✗ is clean (finished, 0 collisions, max |e| ≤ 2 m).
`agents/unit-06.py` on the checkpoint track: 420.40 s, clean. The tracks: lengths 2625.6–2675.0 m, no self
intersections, tightest radius 17.3–20.5 m, min half-width ≥ 5.01 m. Wall time per race 2.7–3.8 s; a crashing race
runs to its time cap (about 17 s at 1500 s, so the notebooks race the training family with a 450 s cap).

Also recorded (not in the checkpoint): on `monza-like` seeds 2–4 the Unit 7 reference crashes too; A_LAT 3.4 is clean
on all four (`q23`). This is the Unit 7 agent's fragility outside its tuning track. It is a **follow-up** and a named
risk for the interim CARLA check (the CARLA map is not `monza-like` either) and for `roar-008`/`roar-010` (Unit 11,
robustness), not something this plan changes.

## Gates (pinned from the probes; a miss means stop, amend and re-gate)
The grid is Unit 7's: A_LAT in steps of 0.2, A_DEC 5.0, PP_K 0.5, `PROFILE_LEAD_S` 0.3, `GRIP` all 1.0
(per-section knobs are per track; tuning them on the family is out of scope).
- **CP.1, the tracks:** the generator writes the five tracks, byte-stable (the existing checksum contract), each with
  0 self-intersections, continuous curvature and min half-width ≥ 5.0 m; lengths and tightest radii as above
  (±0.1 m).
- **CP.2, one track is not enough:** on `test-circuit` alone the edge is 4.8 (clean, 300.00 s) with 5.0 unclean, so
  the margin rule gives 4.6, and 4.6 is **not clean** on training seed 1 (race seed 1: 1 collision).
- **CP.3, the family edge:** 4.4 is clean on all five training tracks on seeds 0–4 (medians as the table) and 4.6 is
  not, so the margin rule gives **4.2**, clean on all five (medians 309.85 / 308.75 / 310.55 / 311.60 / 311.55 s).
- **CP.4, the checkpoint race** (`agents/checkpoint-a.py`, `test-circuit-seed2026`, seeds 0–4, once): clean on every
  seed, median **310.80 s**, within the **target 330 s**; the Unit 6 agent's 420.40 s is not. The target sits above
  every clean grid value from 3.4 up (326.75 s at 3.4), so it rewards speed planning without demanding the edge.
- **CP.5:** `check_submission` passes on `agents/checkpoint-a.py`.
- **Where each gate is asserted:** CP.1 in `roar/data/tests/test_gen_tracks.py`; CP.2–CP.5 in the routed test
  `test_racekit_checkpoint_a.py` (the full table above: about 170 races, about 1.5 min on 8 workers); the solutions
  notebook asserts CP.2's 4.6 failure on training seed 1, CP.3's 4.4 and 4.2 rows and CP.4 (about 45 races,
  sweeping down from 4.6 and stopping a value at its first unclean race; about 3 min).

## The checkpoint (questions; the brief opens with the project)
**Brief:** "Your Unit 7 agent is fast on `test-circuit`. Race day is on a track you have never driven: a variant of
`test-circuit`, every corner a little tighter or looser, every straight a little narrower or wider. You may tune on
four other variants of the same family. You may race the checkpoint track once." The rules: no tuning on the
checkpoint track; one global setting (A_LAT on Unit 7's grid; A_DEC, PP_K and the lead as in the Unit 7 reference);
the clean rule on five seeds; target median ≤ 330 s.
The student's submission is **their own Unit 7 submission** (the notebook points at `agents/unit-07.py` as the
stand-in and says to use theirs); variants via `write_variant` (Unit 1).
1. **Know the family.** Load the five training tracks; compute each one's length and its tightest radius from your
   own Menger curvature (Unit 2) and compare with the track's stored curvature; plot the five centrelines.
2. **Plan a lap on paper.** Write the forward–backward speed profile (Unit 7) as a function and compute each training
   track's planned lap time at A_LAT 4.6; check it against the profile's two invariants (never above the cap; no
   step needs more than A_DEC of braking).
3. **Tune on one track.** Find `test-circuit`'s edge on the grid (clean rule, five seeds) and apply the margin rule.
4. **Check the family.** Race that value on the four variants. Where it fails, plot the cross-track error of the
   failing race against time and say what the car did (the weave) and why a tighter corner before a straight
   causes it (Units 5–6: lookahead at speed, grip).
5. **Tune on the family.** Find the highest grid value clean on all five training tracks, apply the margin rule, and
   freeze it; `check_submission` your frozen submission.
6. **Race day.** Race the checkpoint track once on five seeds; report the median and spread, the clean rule and the
   target. Then compare with Question 2's planned time for the checkpoint track and with the Unit 6 agent's time
   (given, 420.40 s): what did speed planning buy, and what did the margin cost?

## Phases

### Phase A: tracks, reference, routed test, registry (Opus subagent for the code; registry inline)
- `roar/data/gen_tracks.py`: `SEEDED_TRACKS = (("test-circuit", 1), …, ("test-circuit", 4), ("test-circuit", 2026))`
  and their names; `generate.py` step 1 writes them with the named tracks (same checksum contract);
  `test_gen_tracks.py` covers them (CP.1). `racekit`'s `TRACK_NAMES` stays the three named tracks; `conftest`'s
  missing-track check also names the seeded ones.
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
answers carry the rest), common mistakes (tuning on the checkpoint track; racing it twice; stacking a per-section
vector from Unit 7).

### Phase D: verification (named)
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN; `bash scripts/pre-merge-guard.sh --pr` OK.
- Every gate holds where listed; the checkpoint notebook passes hygiene (no outputs, no solutions); the routed roar
  suite stays ≤ 8 min; the checkpoint solutions ≤ 4 min; the post-execution report records both.

## Out of scope
- Any `racekit` library change; any change to `agents/unit-07.py` (its fragility is a follow-up, above).
- Per-section knobs on the family (the sections fall on different corners per track; Unit 12 owns many-knob tuning).
- A CARLA lab (CP-A has none in the design); system identification (Unit 8).

## Plan Review
