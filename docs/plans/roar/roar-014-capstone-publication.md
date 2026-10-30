# Plan roar-014 — Capstone: your competition agent (and the book's completion)

**Design:** `docs/designs/013-roar-book.md` **v4.12** (§3 flags, §6 the capstone row and row 13, §7.1, §7.3); this
plan amends it to **v4.13** (the capstone gate made precise, Unit 13's practice list, the flags' timing, below).
**Book:** `roar`. **Autopilot** per AGENTS.md. This is the book's **last** plan.
**Base:** branches from `main` after `roar-013` merged (#168, 44f9753).
**v1**; **v2** folds plan-review round 1 ([sol] REJECT: B1 S1→S2 changed steering and speed together, B2 the gate's
five-seed claim was checked on seed 0 only, B3 the student made no choice of their own, S4 Unit 13's pacing, S5 the
student's race count; [fable] APPROVE WITH NITS: F1 the car, F2 = B3, F3 the bar as row 0, F4 `step-profiling` needs a
real profile, F5 split Exercise 10, F6 = S5, F7–F10; [self] = B3). New evidence: `p8` (one knob tuned by Unit 13's
protocol: `TARGET_SPEED`), `p8v` (its validation cars), `p9` (per-seed lists; pursuit at the same speed).
**Pre-registration (v2, before any race of it):** the capstone reference `agents/capstone.py` is `agents/unit-13.py`
with `TARGET_SPEED = 50.0` and nothing else changed. Its **test cars are k = 96–119** (race seed k mod 5, 3 laps,
`monza-like`, timing off), never raced before; they are raced **once**, by probe `p10` after this commit, and the
result is reported as it comes: no choice in this plan may change after it.
**v2.1** records `p10` (raced once after dc170c9): nominal 5/5 clean, median 447.90 s; the test cars **23/24** clean
(car 117 collides twice, 590.05 s, 4.485 m); `check_submission` PASS. The choice stands, as pre-registered.
**v3.1 CONSENSUS** folds the round-3 findings (below). **v3** folds plan-review round 2 ([sol] REJECT: B1 a file not clean on every fresh car is not submitted, by Unit 13's
own rule, B2 the routed fallback dropped gate seeds, S3 the expected-time claim compared different cars; [fable]
APPROVE WITH NITS: S1 the shipped file's timing behaviour, S2 the student's test cars, S3 the author's choice
informed, N1–N4). **The capstone's reference is `agents/unit-13.py`**: the worked choice (`TARGET_SPEED` 50.0)
passed training and validation and **failed its pre-registered test** (23/24), and Unit 13's submission rule
(clean on every fresh car, a pass/fail rule fixed before `p10` ran) vetoes it. A test can veto a choice; it never
selects a new one: the incumbent submitted is the file that passed its own test (cars 72–95, 24/24) before any of
this. No `agents/capstone.py` is shipped; nothing is re-tuned; car 117 is not re-raced.
The pre-registered choice and its result stay as recorded above (dc170c9, `p10`): the pre-registration fixed the
choice and its test, not the fallback. Submitting the incumbent is a **later safety decision** (v3), taken by
Unit 13's existing rule after the test failed; it is not described as pre-registered. dc170c9's pre-registration
omitted the pass/fail rule; the rule applied is design §6 row 13 and Unit 13's N/N on every set of cars it has never
been tuned on, merged in 44f9753 (#168) before dc170c9, and the reference changed as a consequence the
pre-registration's last sentence did not foresee. The teacher notes carry this as a mistake to avoid: a
pre-registration that names no rule (the brief's Milestone 2 states the rule before the race).

## Scope
- The capstone project `roar/projects/project-14-competition-agent/` (`brief.ipynb`, `solutions.ipynb`,
  `teacher-notes.md`, `manifest.yaml`, `lessons: 3`): "Your competition agent: build, tune and justify the agent
  you submit", with an engineering report around an **ablation table** (race time bought by each stage, with spread).
- The capstone's reference submission is `agents/unit-13.py`, unchanged; the solution's worked choice
  (`TARGET_SPEED` 50.0) is reported as a choice that failed its test (no new agent file).
- Unit 13 gains **three core exercises** that practise the seven concepts the capstone rule needs (below); the
  Challenge becomes Exercise 12; Unit 13's `lessons` 3 → **4**; its manifest, coverage entry, solutions and teacher
  notes follow.
- A routed premise test for the capstone gate; the registry (the project's coverage entry, syllabus rows; **no new
  concepts and no new API names**); `books.yaml`: `buildout: true` **removed** (the book is concept-complete and its
  lessons total 44, inside `[30, 50]`); design 013 **v4.13**.
- **Not** the `site` and `publication` flags (see "The flags").
- No racekit code change.

## The flags: why this plan does not set them
Design §3 and §7.3: `publication` is set only after the author's **final qualification** on the pinned CARLA stack
(5 consecutive official-runner launches, every run clean, median ≤ 329 s, recorded in `roar/docs/qualification.md`),
and `site` is set together with it.
That run needs the author's Windows machine; autopilot cannot run it.
So this plan ships the capstone with both flags **unset**, leaves the final-qualification table "not yet run", and
records the flags as the first follow-up: after the author's run, a short plan records the launches and sets both
flags (or, if the proxy fails, a re-tune plan follows, design §7.3).
The final qualification races the capstone's reference, `agents/unit-13.py` (on CARLA, the lab-assembled file with the
author's own Monza line and grip), unless a follow-up plan records an author override of design §6 row 13's rule and why.
This is a narrowing of the design's `roar-014` row, recorded in v4.13; it relaxes no rule.

**Named risk (design §7.3):** the `roar-013` interim **timed** CARLA check of `agents/unit-13.py` is `PENDING
(author)`. The capstone's reference is that same file, so a failing CARLA check is a failing check of the capstone's
reference. On CARLA, "the Unit 13 reference" means the lab-assembled file with the author's own
Monza line and grip (`monza-like` is racekit's model of the track). Recorded again in `## Plan Review`.

## The capstone rule (tool-forced)
`tools/curriculum.py practice_findings`: once `projects/<capstone>/` exists, every concept must already be practised
by a **non-capstone** entry. Seven concepts are introduced but practised by no later entry:

| introduced in | concept | where it is practised after this plan |
|---|---|---|
| Unit 3 | `numerical-integration` | Unit 13, Exercise 9 (Euler vs RK4 replay of the race) |
| Unit 8 | `car-identification` | Unit 13, Exercise 9 (the longitudinal map fitted from the race) |
| Unit 6 | `dynamic-bicycle` | Unit 13, Exercise 10 (sideslip and yaw rate from the race; a `DynamicCar` twin) |
| Unit 10 | `error-model-linearization` | Unit 13, Exercise 10 (the linear error model against the nonlinear step) |
| Unit 4 | `integrator-windup` | Unit 13, Exercise 11 (the speed PID's launch, with and without its limits) |
| Unit 5 | `stanley-steering` | Unit 13, Exercise 11 (one capped Stanley race on `monza-like`) |
| Unit 12 | `step-profiling` | Unit 13, Exercise 11 (`cProfile` over Exercise 7's race: where the tick's time goes) |

Design §6 already makes Unit 13 the integration unit that carries the capstone rule (013 review B1/M4); `roar-013`
listed only the concepts its exercises named. This plan adds the practice, not a new unit.

## The idea (what the probes found, and the story the capstone tells)
The hook: "You have one file. Tune it once more, then show what every stage of it bought."
Every race here is on **`carla_like(noise=True)`**, the book's CARLA stand-in since Unit 6, on `monza-like`.

**The starter cannot finish `monza-like` on this car** (`u14/p1.log`): `agents/starter.py` (byte-identical to
`unit-01.py`) crash-loops in the first few hundred waypoints on all five seeds (85 collisions in 900 s; still not a
lap at 1800 s). Unit 1 measured the same file clean (870 s on `KinematicCar`); Unit 6's hook showed it spinning the
grip car. The file is the same; the car changed. Made clean by its own one knob, `TARGET_SPEED`: 8 → 2033.65 s,
10 → 1650.50, 12 → 1390.55, **14 → 1203.55 s (spread 0.70, 5/5 clean; seeds 0–4: 1203.45, 1203.55, 1203.90, 1203.85,
1203.20)**, 16 → finishes with 0 collisions but 2.695 m from the centreline (not clean).
So the design's gate ("the reference beats the starter at 0 collisions") reads: **the starter made clean by its
own knob, `TARGET_SPEED = 14.0`** (the fastest clean grid point), on `carla_like(noise=True)`.

**The student's own choice (the worked example; `u14/p8a.log`, `p8b.log`, `p8v.log`).** From `agents/unit-13.py`,
one knob Unit 13 never touched, by Unit 13's protocol (the crash-aware objective: nominal seeds 0 and 1 plus training
cars 16, 18, 8; a setting not clean is rejected; Unit 1's rule on the per-replicate sums in whole ticks):

| `TARGET_SPEED` | clean | pair (ticks) | nominal s0, s1 (s) | result |
|---|---|---|---|---|
| 45 (shipped) | yes | [37556, 37556] | 468.55, 468.55 | incumbent |
| 47.5 | yes | [36624, 36625] | 456.85, 456.90 | accepted |
| 50.0 | yes | [35911, 35913] | 447.80, 447.90 | accepted |
| 52.5 | yes | [35346, 35345] | 440.75, 440.70 | accepted |
| 55.0 | **no** (car 8: 1 collision, 5.273 m, 508.50 s) | — | 434.75, 434.55 | the edge |

Unit 11's margin rule ships one step inside the edge: **50.0**. On the validation cars 24–47: 50.0 is **24/24** clean
(median 448.12 s, max error 1.341 m); 52.5 without the margin is 21/24 (cars 24, 43, 46 collide). The other knobs
tried: `PROFILE_LEAD_S` 0.2 is accepted by 0.85 s (a plateau; not pursued), 0.4 slower; `MPC_Q_E` 0.2 slower, 0.5 not
clean. Why it works: `TARGET_SPEED` was set in Unit 4 and never re-tuned after the grip, the line and MPC raised the
corner speeds.

**The test cars, raced once (`u14/p10.log`, pre-registered at dc170c9; `p10.py` refuses a second run):** cars 96–119,
race seed k mod 5: **23/24 clean**, median 448.48 s; **car 117** (seed 2) finishes with 2 collisions, 590.05 s, max
line error 4.485 m (its CPU time, 4.47 s against about 9.3, fits the fallback's switch to pursuit). The other 23:
445.30–451.15 s, max error ≤ 1.323 m. `agents/unit-13.py` was 24/24 on its test cars (72–95).
**The verdict, by the book's own rule:** Unit 13's submission rule is a file clean on every fresh car (N/N), fixed
before `p10` ran; 23/24 fails it. So the worked choice is **not submitted**: the capstone submits the incumbent,
`agents/unit-13.py` (468.55 s; 24/24 on its own test cars 72–95). The report states the two facts separately, as
measured: 20.65 s faster on the nominal car, and one crash in 24 fresh cars; it does not net them into an expected
time (the two files' test results are on different cars). The margin rule thinned the risk (52.5, without it, was
21/24 on the validation cars); it did not remove it, and only a test the file could fail showed that.
A next choice would need a fresh pre-registered set. The 50.0 file is **informational, not a submission candidate**
under design §6 row 13; the author may race it on CARLA as an extra row, and the final qualification races
`unit-13.py` unless a follow-up plan records an override.

**The build-up ablation** (`u14/p2.log`, `p3.log`, `p9`; one file, `agents/unit-13.py` with constants changed by
`write_variant`; seeds 0–4, 3 laps, timing off; S1–S7 with the respawn fallback off, `RESPAWN_IMPULSE = 1e300`, and
the pre-re-tune knobs `MU_FRACTION` 0.54, `A_DEC` 5.0, `A_ACC` 4.0):

| stage | the idea (constants) | clean | median / spread (s) | time bought (s) | Unit 1's rule vs previous | max error (m) |
|---|---|---|---|---|---|---|
| S0 | the bar: `starter.py`, `TARGET_SPEED` 14 | 5/5 | 1203.55 / 0.70 | — | — | 0.706 (c) |
| S1 | Unit 4: `STEERING "pid"`, `SPEED_MODE "flat"` 14 m/s, centreline, `MU_G None` | 5/5 | 1219.75 / 0.60 | **−16.20** | False | 0.434 (c) |
| S2a | Unit 5: `"pursuit"`, same 14 m/s | 5/5 | 1219.90 / 0.55 | −0.15 | False | 0.429 (c) |
| S2b | Unit 5's speed: pursuit at 15 m/s (pid at 15 crashes on every seed) | 5/5 | 1138.85 / 0.45 | 81.05 | True | 1.042 (c) |
| S3 | Unit 6: `SPEED_MODE "cap"`, `A_LAT` 4.6, `TARGET_SPEED` 32.5 | 5/5 | 617.05 / 0.15 | 521.80 | True | 0.753 (c) |
| S4 | Unit 7: `"profile"`, `TARGET_SPEED` 45 | 5/5 | 514.95 / 0.20 | 102.10 | True | 1.575 (c) |
| S5 | Unit 8: `MU_G` measured, `MU_FRACTION` 0.54 | 5/5 | 510.20 / 0.15 | 4.75 | True | 1.734 (c) |
| S6 | Unit 9: the line | 5/5 | 482.00 / 0.10 | 28.20 | True | 1.529 |
| S7 | Unit 10: `"mpc"` | 5/5 | 482.00 / 0.05 | 0.00 | False | 0.976 |
| S8 | Unit 11: the respawn fallback on | 5/5 | 482.00 / 0.05 | 0.00 | False | 0.976 (telemetry identical to S7) |
| S9 | Unit 13: the re-tune = `agents/unit-13.py` | 5/5 | 468.55 / 0.10 | 13.45 | True | 1.009 |
| S10 | the worked choice, `TARGET_SPEED` 50.0 (**not submitted**: test cars 23/24) | 5/5 | 447.90 / 0.20 | 20.65 | True | 1.141 |

(c): from the centreline (no line raced). The story:
- **A stage can cost time.** Unit 4's PID at the bar's speed is 16 s *slower* than the starter (it buys precision:
  0.434 m against 0.706 m), and pursuit at the same speed buys nothing (−0.15 s); what pursuit buys is the next clean
  m/s (S2b). Time bought depends on what the stage lets you change next.
- Most of the time is bought early (the bar → S4 is about 689 s of the 735 s; Unit 6's cap alone 522 s). Unit 6's
  cap cannot run at 45 m/s (every `A_LAT` 4.0–6.0 crashes at the first chicane: the 50 m curvature lookahead cannot
  brake from about 39 m/s, Unit 7's motivation), so S3 runs at 32.5 (35 crashes).
- **MPC buys 0.00 s** on the nominal car and the fallback buys nothing there (identical telemetry): they buy
  **margin** (max line error 1.53 → 0.98 m; Unit 13's held-out cars, where pursuit is clean on 13 of 24), which a
  time-only ablation cannot show. The report must say so.
- **Leave-one-out from S9** (468.55 s; `u14/p3.log`): no line 495.40 (+26.85), no grip 486.25 (+17.70), no MPC
  (pursuit) 468.60 (+0.05, not better by Unit 1's rule), no tune 482.00 (+13.45). The grip buys 4.75 s in the
  build-up and 17.70 s in the leave-one-out: **stages are not additive**, and the order of an ablation is a choice
  the report states.

**The gate** (seeds 0–4, all in the premise): the capstone reference `agents/unit-13.py` against the bar, both clean at
0 collisions, Unit 1's rule, margin **≥ 700 s** on the medians: **735.00 s** (468.55, 468.55, 468.55, 468.65, 468.60
against 1203.45, 1203.55, 1203.90, 1203.85, 1203.20; `noise_aware_better` True). `unit-13.py`'s five races are U13.1's
(already routed; the premise reuses the `race_day_premise` session fixture), so the gate adds only the bar's five.

**Unit 13's three exercises** (`u14/p5.log`–`p7.log`; one 1-lap race of `unit-13.py`, seed 0, timing off, 159.15 s,
clean: Exercise 7's `untimed` race, so no new race; telemetry `u14/r_tel.pkl`):
- R1 `car-identification` (Unit 8's least squares): lag RMS 0.625 / **0.448** / 0.602 / 0.707 m/s² for lags 0–3;
  at lag 1, `A_THROTTLE` 5.075, `A_BRAKE` 8.533, `C_DRAG` 3.137e-4 against the agent's assumed 6.0 / 8.0 / 4.0e-4
  (RMS 0.607); fitted on the first half, RMS 0.453 on the second (assumed 0.604).
- R2 `numerical-integration` (Unit 3): a 1 s replay from 31 start rows; on the agent's own model Euler is 0.123 m
  (median) from a fine RK4 and RK4 at most 5e-9 m; against the real car model error dominates (Euler 0.520, RK4 0.558; RK4
  with R1's map 0.472).
- R3 `dynamic-bicycle` (Unit 6): sideslip from positions above 5 m/s, max 4.38°, median 0.59°; peak lateral
  acceleration 8.71 m/s² at 19.56 m/s; measured over kinematic yaw rate median 0.976 (p10 0.657, p90 1.473); a
  `DynamicCar()` twin at the peak point (kinematic r 0.510, dynamic 0.397).
- R4 `error-model-linearization` (Unit 10): the tightest line point (κ 0.0353, 12.75 m/s); linear vs nonlinear over
  2 s, 0.35 vs 0.29 m at (0.1 m, 0.01 rad) up to 25.40 vs 20.97 at (5 m, 0.8 rad); in the race's own range
  (|ψ| ≤ 0.118 rad) one tick differs by at most 2.31e-4 m (measured 2.314e-4).
- R5 `stanley-steering` (Unit 5): Stanley never races `monza-like` clean (fallback off, 1 lap, seed 0: the first
  crash at about 44.5 m/s, sooner the higher `ST_K`: 1 → progress 1057, 3 → 413, 8 → 237); a 70 s cap shows it.
- R6 `integrator-windup` (Unit 4): `unit-13.py`'s `PID(0.5, 0.1)` launching `KinematicCar()` from 0 to 45 m/s: with
  limits (0, 1) 0% overshoot, settles 7.80 s, peak integral 1.35; with no limits 50.0% overshoot, 28.45 s, 173.89
  (settling by Unit 4's `step_metrics`, the first tick after the last one outside ±2%; the probe log's 7.75 / 28.40
  took the last tick outside, one tick earlier: corrected in Phase B).
  No race (the limits are not a module constant).
- R7 `step-profiling` (Unit 12): `cProfile` over Exercise 7's untimed race replayed (about 4 CPU-s, re-racing the same
  1 lap under the profiler); the student reads where the tick's time goes (the MPC solve); nothing load-dependent is
  asserted (only that the MPC function appears among the top entries). Phase A measures it.
Phase A re-measures every pinned value with the shipped code; a miss stops the plan and amends it.

## Deviations from design (recorded; design 013 v4.13)
- §6 capstone gate: "the starter" is the starter made clean by its own knob (`TARGET_SPEED = 14.0`) on
  `carla_like(noise=True)`; the shipped starter never finishes `monza-like` on that car. Gate: the capstone reference
  beats it by **≥ 700 s**, both clean at 0 collisions, by Unit 1's rule on seeds 0–4.
- §6 capstone: the reference is `agents/unit-13.py`; the solution's worked choice (`TARGET_SPEED` 50.0) failed its
  pre-registered test cars 96–119, raced once (23/24), and is not submitted. §4.4 gains cars 96–119 (spent) and
  **120–143, a student's own pre-registered test cars** (raced once, after the file is frozen).
- §6 row 13: Unit 13 also practises the seven concepts above (the capstone rule), with `lessons: 4`.
- §3: `site` and `publication` wait on the author's final qualification (a follow-up plan sets them); `buildout`
  is removed here; "13 units at 2–3 sittings each" notes Unit 13's four.

## Concepts
Introduces nothing. The capstone practises the concepts its milestones exercise (listed in its manifest; no
assumed-baseline concept). Unit 13 adds `numerical-integration`, `integrator-windup`, `stanley-steering`,
`dynamic-bicycle`, `car-identification`, `error-model-linearization`, `step-profiling` to its practices.

## The capstone
`roar/projects/project-14-competition-agent/` (the id matches `^project-[0-9]{2}-…$`).
- **Brief** (project-first; student-facing, no solutions or outputs; 5 milestone headings, `## Make it yours`,
  `## Requirements checklist`; project-strict: no borrowed tools, every call taught). The student's file: their own
  race-day file from Unit 13 if it has the book's mode switches, else `agents/unit-13.py` (the brief says so).
  Three files are named throughout: the **incumbent** (the file you start from), the **candidate** (the incumbent
  with your one choice, frozen before its test) and the **submitted file** (the candidate if it passes its test, else
  the incumbent, whose own evidence is Unit 13's record or your earlier labs').
  1. **The bar.** Race the starter on `monza-like` on `carla_like(noise=True)` (seed 0, capped): it never finishes,
     although Unit 1 measured it clean on the kinematic car (why: the car changed). Make it clean with its one knob
     (`TARGET_SPEED` 10, 12, 14, 16 at seed 0; then the chosen one on seeds 0–4): the bar.
  2. **Your choice.** Tune **one** knob your file has not been tuned on (candidates listed: `TARGET_SPEED`,
     `PROFILE_LEAD_S`, `MPC_Q_E`, `MPC_R_DU`, `CURVATURE_HORIZON`; the report justifies the knob, and a student who
     picks `TARGET_SPEED`, the solution's, also reports a second knob's evidence), by Unit 13's protocol (the
     crash-aware objective on the nominal car and training cars 16, 18, 8; whole ticks; the edge and the margin),
     judge it on validation cars (24–47), and **freeze** the result (or keep the value, with the evidence). Then
     the test, stated before any race of it: write down the frozen file and the rule (clean on every car), race
     **your own test cars 120–143 once**, record the result as it comes, and submit the frozen file only if it
     passes; otherwise submit the incumbent. Cars 120–143 test only the one frozen candidate (a second knob's evidence
     stops at validation), so no student spends them twice. Never revise the choice on the test, never race the test cars
     72–119, `test-circuit-seed2027/2028`, or cars ≥ 1000 (a test set raced to make a choice is spent).
  3. **Build it up.** The ablation of **the submitted file**: the bar, then one unit's idea per stage (the reference
     grid S1–S10 given as a starting point; a stage whose given constants are not clean for your file needs its own
     fastest clean value, as S2b and S3 did), on seeds 0–4: median, spread, time bought, Unit 1's verdict against
     the previous stage, max error, clean; and the leave-one-out cross-check (line, grip, MPC, your choice). The candidate is its last row,
     marked submitted or not (the solution's S10); if your choice kept the value, there is no candidate row.
  4. **Qualify.** The submitted file against the bar (Unit 1's rule, 0 collisions, seeds 0–4) and against
     `agents/unit-07.py`; `check_submission` on `monza-like`; the packaging checklist (Unit 13).
  5. **The engineering report.** A memo: the ablation table, what each stage bought with its spread, the stage that
     cost time and why, what MPC and the fallback buy that time does not show (margin), the order of the ablation,
     your choice's evidence (training, validation, your test) and which file you submit and why, what you would
     do next, and the CARLA caveat (racekit is a model; CARLA is the test).
  **The student's race count** (stated in the brief): the bar 10, the choice about 30 plus 24 validation and
  24 test, the build-up 55, the leave-one-out 20, qualify 10: about 175 races, about 24 CPU-minutes serial, run across the three
  sittings and at home (the brief says which can run while you write). A student may cut the build-up and the
  leave-one-out to seeds 0–2 and say so in the report.
- **Solutions** (a separate fresh session; the submitted file `agents/unit-13.py`): the worked choice's test record
  (`p10`, 23/24, car 117) given as data, the veto applied, never raced; the bar (the shipped starter capped
  at 120 s: collisions ≥ 1, not finished; `TARGET_SPEED` 14 at seed 0 live: 1203.45); the choice (`p8`'s table and
  `p8v`'s validation counts as the probe record of plan `roar-014`, given as data; the whole-tick replay of the
  acceptance; seed 0 of 50.0 live: 447.80); the build-up (seed 0 of S1–S10 live, each checked against the record
  ±1 tick; the five-seed tables given as data); the gate on the given five-seed lists by Unit 1's rule;
  `check_submission(UNIT_13, track="monza-like")` PASS with p99 printed (not asserted: Unit 13's milestone holds the
  timing gate); a model report.
- **Teacher notes** (inline): goals, the three sittings, the hook, the rubric, mistakes (an ablation with one seed;
  reading 0.00 s as "MPC is useless"; additive thinking; the order; tuning on test cars; netting a crash into an
  expected time across different cars; a pre-registration that names no rule), prompts, differentiation; the rubric
  states the reference's own trade; the solutions never race cars 120–143, and a student who re-runs Milestone 2 after
  racing them has spent them.

## Unit 13's three exercises
Inserted before the Challenge (which becomes Exercise 12, still tagged `stretch`):
- **Exercise 9, "Measure the car you race"** (`car-identification`, `numerical-integration`): R1, R2 from Exercise
  7's `untimed` telemetry. No race.
- **Exercise 10, "The models under the MPC"** (`dynamic-bicycle`, `error-model-linearization`): R3 (with a
  `DynamicCar()` twin) and R4. No race.
- **Exercise 11, "The parts you did not ship"** (`integrator-windup`, `stanley-steering`, `step-profiling`): R6 on
  `KinematicCar()`, R5 (one Stanley race capped at 70 s), R7 (one profiled 1-lap race).
Phase C rewrites Unit 13's pacing: **three sittings plus the lab** (`lessons: 4`): sitting 1 the hook and §1–§2,
Exercises 1–3; sitting 2 §3–§6, Exercises 4–8; sitting 3 Exercises 9–11 (the car, the models, the parts); the
Challenge as homework. Every reference to "Challenge 9" (lesson, teacher notes, solutions) becomes "Challenge 12".
Every value the solutions assert is a deterministic pin from Phase A; anything else is printed.

## Gates (pinned from the probes; Phase A re-runs each with the shipped code)
- **C14.0** the shipped starter on `monza-like`, `carla_like(noise=True)`, seed 0, cap 120 s: not finished,
  collisions ≥ 1.
- **C14.1** the gate: the starter at `TARGET_SPEED = 14.0`, seeds 0–4, 3 laps, timing off, cap 1300 s (five races),
  with `agents/unit-13.py`'s five U13.1 races from the session fixture: all ten clean at 0 collisions; the bar's
  per-seed times equal the record (±1 tick); `noise_aware_better(unit-13, bar)`; median margin ≥ 700 s.
- **C14.2** (solutions, not routed) every stage's seed-0 time, clean flag and max error equal the record (±1 tick,
  ±0.01 m); the choice's seed-0 time.
- **C14.3** Unit 13's new exercises: R1's lag-1 fit to 1e-3 relative and its lag choice, R6's overshoots and peak
  integrals, R4's one-tick bound, Stanley not clean in 70 s (asserted in the solutions; deterministic); R7 only that
  the MPC function is among the profile's top entries.
- **C14.4** the registry: `coverage-check` (with the capstone directory present: the capstone rule) and every
  `py4kids-tools --book roar` check PASS with `buildout` removed.

## Budgets
- **Routed pytest:** C14.0 (under 1 CPU-s) + C14.1 (five bar races, about 6 CPU-s each, pooled; `unit-13.py`'s are
  U13.1's): about +10 s wall, about 1,130 s of the interim 1,170 s. **No raise.** Over 1,170 s in Phase D stops the
  plan and amends it (no gate race is ever dropped to fit).
- **Notebooks:** capstone solutions about 110 s serial (S1–S10 seed 0 about 70 CPU-s, the bar about 7 s, the choice's
  seed 0 is S10, `check_submission` about 10 s); Unit 13 solutions +about 8 s (a 70 s-capped Stanley race and
  the profiled lap). Each cell ≤ 120 s. Book exec about 49.3 → **about 51.5 of 55 CI-min. No raise.**

## Phases
- **Probe p10 (done, after dc170c9; recorded above):** nominal 5/5, test cars 23/24, `check_submission` PASS
  (p99 0.998 ms, load 2.46). The test cars are **not** in the routed premise (24 races would not fit the headroom);
  their record is `p10`'s, quoted with its log.
- **Phase A — premise + registry** (Opus subagent).
  - `roar/projects/racekit/tests/_capstone_premise.py` + `roar/projects/racekit/tests/test_racekit_capstone_premise.py`
    (the routed roar suite; C14.0, C14.1: the five `unit-13.py` races are read from the `race_day_premise` fixture's
    `monza-like` seeds 0–4 keys, no re-race; the bar's five run in the new pool, `car="carla"`, constants
    `(("TARGET_SPEED", 14.0),)`, `max_seconds=1300`; the never-raced assertion covers cars 72–143; the existing pool
    runner and the `race_day_premise` fixture); re-measure C14.2's seed-0 races and C14.3's values and log them
    (`scratchpad/u14/phaseA-gates.log`).
  - Registry: coverage-map entry `project-14-competition-agent` (`kind: project`, `lessons: 3`, introduces nothing,
    requires everything, practises the brief's concepts); Unit 13's entry and manifest gain the seven concepts and
    `lessons: 4`; syllabus: Unit 13's lessons, the capstone row (no emoji), the "added by the plans that follow"
    line deleted; `books.yaml` drops `buildout` (and its comment), the coverage map's header comment updated; design
    013 v4.13 (§3, §4.4 cars 96–119 and 120–143, §6 capstone row and row 13, §7.1 measured budgets, changelog).
    `qualification.md`: a note under the final qualification that the flags wait on it, that it races `unit-13.py`
    (468.55 s, 24/24 on cars 72–95; its SHA-256) unless a follow-up plan records an author override, and an
    informational row: `unit-13.py` with `TARGET_SPEED` 50.0, 447.90 s, failed N/N (23/24 on cars 96–119, car 117),
    not a submission candidate under design §6 row 13.
- **Phase B — content** (Opus subagents): the capstone brief (statements) and Unit 13's three new exercise
  statements in one session; the capstone solutions and Unit 13's three new solutions in a **separate fresh**
  session. Every race timing off except the capstone solutions' `check_submission`. Never race
  `test-circuit-seed2027/2028`, cars 72–143, or k ≥ 1000; nothing from `racekit._truth`.
- **Phase C — teacher notes** (inline): the capstone's; Unit 13's pacing (three sittings plus the lab), mistakes for
  Exercises 9–11, the Challenge renumbered.
- **Phase D — verification:** `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN; budgets measured.
- **Content gate scope for blind solving:** reviewers solve Unit 13's Exercises 9–11 and the capstone's Milestones
  1–2 on the given data (including the veto) plus seed 0 of S1, S3 and S10 (they cannot run 175 races).

## Out of scope
- The `site` and `publication` flags and the final qualification (the author's CARLA run; a follow-up plan).
- Any racekit change; any change to `agents/unit-13.py`; any new concept or API name.
- The routed / book-exec tiering decision (a follow-up; no raise is needed here).

## Plan Review

### Named risk (design §7.3)
The `roar-013` interim timed CARLA check of `agents/unit-13.py` is `PENDING (author)` in `roar/docs/qualification.md`.
It is also the capstone's submitted reference, so a failed CARLA check questions the capstone's reference on CARLA.

### Round 1 (v1 @ 05babe1)
Verdicts: [self] REJECT (B3 below); [sol] REJECT; [fable] APPROVE WITH NITS.
- [FIXED v2] [sol] B1: S1→S2 changed the steering and the speed together; the table now has S2a (pursuit at the same
  14 m/s: −0.15 s, not better) and S2b (pursuit's next clean m/s: pid at 15 crashes on every seed).
- [FIXED v2] [sol] B2: the gate's five-seed claim now runs five seeds in the premise (C14.1: ten races, all clean,
  per-seed pins, Unit 1's rule, margin ≥ 700 s).
- [FIXED v2] [sol] B3 / [fable] F2 / [self]: the student now makes and freezes a choice of their own (Milestone 2, Unit
  13's protocol, validation cars) and ablates their frozen file; the solution's worked choice is `TARGET_SPEED` 50.0
  (`p8`, `p8v`), shipped as `agents/capstone.py` with pre-registered test cars 96–119 raced once (`p10`).
- [FIXED v2] [sol] S4 / [fable] F5: Unit 13 gets three exercises (Exercise 10 split), `lessons: 4`, three sittings
  plus the lab, the Challenge renumbered to 12 everywhere.
- [FIXED v2] [sol] S5 / [fable] F6: the brief states about 150 races (about 20 CPU-minutes) and which seeds a student
  may cut.
- [FIXED v2] [fable] F1: every race names `carla_like(noise=True)`; Milestone 1 says why Unit 1's clean starter
  crash-loops here.
- [FIXED v2] [fable] F3: the bar is row S0, and S1's −16.20 s is a required point of the report.
- [FIXED v2] [fable] F4: `step-profiling` is practised by a `cProfile` pass (Exercise 11, R7), not by Exercise 7.
- [FIXED v2] [fable] F7: the syllabus's "added by the plans that follow" line is deleted; Unit 13's lessons updated.
- [FIXED v2] [fable] F8: the capstone solutions print p99 and assert only PASS.
- [FIXED v2] [fable] F9: the named risk is recorded here; the brief names the never-race list and why; the content
  gate's blind-solve scope is named.
- [FIXED v2] [fable] F10: the routed fallback is pre-declared in Budgets.

### Round 2 (v2.1 @ 140516d)
Verdicts: [self] APPROVE WITH NITS (sides with [sol] B1); [sol] REJECT; [fable] APPROVE WITH NITS.
[fable] verified the pre-registration from the artefacts: dc170c9 committed 22:25:06 and pushed 22:25:08; `p10.py`
22:25:49; `p10.log` 22:26:37; every v2.1 number matches the logs.
- [FIXED v3] [sol] B1: Unit 13's rule (clean on every fresh car) vetoes the worked choice at 23/24; the capstone
  submits `agents/unit-13.py`, and no `agents/capstone.py` ships. [fable] argued that reverting is a post-hoc choice;
  [self]: the pass/fail rule was fixed before `p10`, and the incumbent's own test (72–95) is independent of it, so
  the veto selects nothing from cars 96–119.
- [FIXED v3] [sol] B2: no gate race is dropped to fit the budget; over 1,170 s stops and amends. The gate now adds only
  the bar's five races (U13.1 races `unit-13.py`'s).
- [FIXED v3] [sol] S3: the expected-time netting across different cars is removed; the two facts are stated apart.
- [FIXED v3] [fable] S1: moot for the submitted file (`unit-13.py` sets `MPC_MIN_HORIZON = 40`, bracketed in
  roar-013); `p10c`'s 443.05 s is `check_submission`'s default `KinematicCar` race, not comparable with 447.90.
- [FIXED v3] [fable] S2: students get their own pre-registered test cars 120–143 (design §4.4) and Milestone 2 states
  the rule before the race.
- [FIXED v3] [fable] S3: `qualification.md` records both candidates side by side with SHA-256s; the teacher notes'
  rubric states the trade.
- [FIXED v3] [fable] N1 (the candidate knobs, and a second knob if the student picks the solution's), N2 (no empty
  S10 row), N3 (design §3's sittings phrase), N4 (the bar is 10 races).

### Round 3 (v3 @ a20283f): CONSENSUS at v3.1
Verdicts: [self] APPROVE WITH NITS; [sol] REJECT (one blocker, folded in v3.1); [fable] APPROVE WITH NITS (withdraws
its round-2 objection: Unit 13's N/N rule was merged in 44f9753 before dc170c9, and the incumbent's test is
independent of cars 96–119, so the veto selects nothing from them).
- [FIXED v3.1] [sol] B1 / [fable] S2: three files named throughout (incumbent, candidate, submitted file);
  Milestones 3–4 ablate and qualify the submitted file; the candidate is the ablation's last row, marked.
- [FIXED v3.1] [sol] S2 / [fable] S1: the pre-registered choice and its result stay as recorded; the incumbent
  submission is labelled a later safety decision; the plan says the pre-registration named no rule, which rule was
  applied and when it was merged.
- [FIXED v3.1] [sol] S3: the premise files are under `roar/projects/racekit/tests/` (the routed roar suite).
- [FIXED v3.1] [fable] S3: the Flags section's leftover v2 sentence corrected.
- [FIXED v3.1] [fable] S4: the 50.0 row is informational, not a submission candidate; the final qualification races
  `unit-13.py` unless a follow-up plan records an author override.
- [FIXED v3.1] [fable] N5 (175 races), N6 (one test, one file; the never-raced assertion covers 72–143), N7 (C14.1's
  race keys and the bar's job spelled out), N8 (the teacher notes on cars 120–143).
Consensus: [sol]'s only blocker is resolved by a text change that names the file each milestone evaluates; no
number, gate or phase changed; [self] and [fable] approve. Implementation proceeds at v3.1.

## Content Review

### Round 1 (@ 1d569a1)
Verdicts: [self] APPROVE WITH NITS (one S); [sol] REJECT (three B, one S); [fable] APPROVE WITH NITS (one S, six N).
Blind solves ([sol] and [fable], from the statements before the solutions): Exercise 9 lag 1, fit 5.075 / 8.533 /
3.137e-4, Euler 0.123 m, against the car 0.520 / 0.558 / 0.472; Exercise 10 the one-tick gap 2.314e-4 m; Exercise 11
overshoot 0% / 50.0%, settling 7.80 / 28.45 s by Unit 4's rule, peak integral 1.35 / 173.89, Stanley not clean in 70 s
(first crash 23.00 s); Milestone 2 accepts 47.5, 50.0 and 52.5 on whole ticks, 55.0 not clean, edge 52.5, margin 50.0,
validation 24/24, test 23/24, the incumbent submitted; Milestone 3 seed 0 S1 1219.90, S3 617.05, S10 447.80 s.
All match the solutions.
- [FIXED] [sol] B1: the brief requires a `TARGET_SPEED` student's second knob through training **and validation**;
  the solution stopped `PROFILE_LEAD_S` at training. Probes p11, p11b, p11c (scratchpad `u14/`, validation cars
  24–47 only) completed it: 0.2, 0.1 and 0.0 each beat the value before on training (sums 1876.9 / 1874.95 / 1872.55
  s), all clean; a lead below 0 is floored at `LEAD_MIN_M`, so 0.0 ends the walk with no edge and is kept by the
  brief's rule; on the validation cars 0.0 is clean on **22 of 24** (car 24: 2 collisions, 707.25 s, 3.975 m; car 35:
  2.009 m). No second candidate; the solution's cell 7 and answer 6 give it as data with asserts.
  (Recorded, not used by the solution: 0.1 on the same validation cars is clean 24/24, median 468.10 s, p11b.)
- [FIXED] [sol] B2: the brief promised the tested file is the submitted file "byte for byte", but `race()` adds
  `NO_TIMING`. The brief (Milestone 2 step 3 and the `race()` comment) now says so: the test races the frozen file with
  only its timing switched off, as every race in the notebook, and Milestone 4's `check_submission` races it exactly as
  submitted, timing on.
- [FIXED] [sol] B3 = [fable] N2: `assert check_passed` used `report.ok`, which includes the load-dependent p99 budget.
  The solution now asserts the parse and shape stages empty and the race finished, and prints `report.ok`; checklist
  item 6 prints it too.
- [FIXED] [self] S = [sol] S4 = [fable] S1: the brief wrote `candidate.py` beside the notebook, inside the public
  repository clone. It now writes it to `RUNS`, a folder of the student's own outside the repository (the labs'
  `roar-runs`), with the labs' "This repository is public" warning; the teacher notes gain the mistake.
- [FIXED] [fable] N4: "steps 1 to 3" → "steps 1 and 2" (step 3 is the freeze).
- [FIXED] [fable] N7: the plan's "RK4 5e-9 m" is the maximum ("at most 5e-9 m").
- [WONTFIX] [fable] N3: `np.atan2` in Unit 13's solutions. `arctan2` is not on the book's closed name list
  (`baseline.yaml` `library_methods`); `atan2` is, and numpy 2.5.3 is pinned.
- [WONTFIX] [fable] N5: the capstone's `practices` list `grip-identification` and `pid-control`: the ablation races
  those stages (S5, S1) and reads what they bought; capstone practice earns no coverage credit, so the capstone rule is
  unaffected. Plan Phase A listed them; changing the map is out of this round's scope.
- [WONTFIX] [fable] N6: the one-race guard is per kernel; the brief calls it "a seat belt, not a record" and the
  pre-registration with its timestamp is the record.
