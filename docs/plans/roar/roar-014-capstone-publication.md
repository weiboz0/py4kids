# Plan roar-014 — Capstone: your competition agent (and the book's completion)

**Design:** `docs/designs/013-roar-book.md` **v4.12** (§3 flags, §6 the capstone row and row 13, §7.1, §7.3); this
plan amends it to **v4.13** (the capstone gate made precise, Unit 13's practice list, the flags' timing, below).
**Book:** `roar`. **Autopilot** per AGENTS.md. This is the book's **last** plan.
**Base:** branches from `main` after `roar-013` merged (#168, 44f9753).
**v1.**

## Scope
- The capstone project `roar/projects/project-14-competition-agent/` (`brief.ipynb`, `solutions.ipynb`,
  `teacher-notes.md`, `manifest.yaml`, `lessons: 3`): "Your competition agent: build, tune and justify the agent
  you submit", with an engineering report around an **ablation table** (race time bought by each stage, with spread).
- Unit 13 gains **two core exercises** that practise the six concepts the capstone rule needs (below); its manifest,
  coverage entry, solutions and teacher notes follow.
- A routed premise test for the capstone gate; the registry (the project's coverage entry, syllabus row; **no new
  concepts and no new API names**); `books.yaml`: `buildout: true` **removed** (the book is concept-complete and its
  lessons total 43, inside `[30, 50]`); design 013 **v4.13**.
- **Not** the `site` and `publication` flags (see "The flags").
- No racekit code change; no new agent file (the capstone's reference is `agents/unit-13.py`).

## The flags: why this plan does not set them
Design §3 and §7.3: `publication` is set only after the author's **final qualification** on the pinned CARLA stack
(5 consecutive official-runner launches, every run clean, median ≤ 329 s, recorded in `roar/docs/qualification.md`),
and `site` is set together with it.
That run needs the author's Windows machine; autopilot cannot run it.
So this plan ships the capstone with both flags **unset**, leaves the final-qualification table "not yet run", and
records the flags as the first follow-up: after the author's run, a short plan records the launches and sets both
flags (or, if the proxy fails, a re-tune plan follows, design §7.3).
This is a narrowing of the design's `roar-014` row, recorded in v4.13; it relaxes no rule.

**Named risk (design §7.3):** the `roar-013` interim **timed** CARLA check of `agents/unit-13.py` is `PENDING
(author)`. The capstone's reference is that same file, so a failing CARLA check would also question the capstone's
reference numbers on CARLA. On CARLA, "the Unit 13 reference" means the lab-assembled file with the author's own Monza
line and grip (`monza-like` is racekit's model of the track).

## The capstone rule (tool-forced)
`tools/curriculum.py practice_findings`: once `projects/<capstone>/` exists, every concept must already be practised
by a **non-capstone** entry. Seven concepts are introduced but practised by no later entry:

| introduced in | concept | where it is practised after this plan |
|---|---|---|
| Unit 3 | `numerical-integration` | Unit 13, Exercise 9 (Euler vs RK4 replay of the race) |
| Unit 4 | `integrator-windup` | Unit 13, Exercise 10 (the speed PID's launch, with and without its limits) |
| Unit 5 | `stanley-steering` | Unit 13, Exercise 10 (one capped Stanley race on `monza-like`) |
| Unit 6 | `dynamic-bicycle` | Unit 13, Exercise 10 (sideslip and yaw rate from the race; a `DynamicCar` twin) |
| Unit 8 | `car-identification` | Unit 13, Exercise 9 (the longitudinal map fitted from the race) |
| Unit 10 | `error-model-linearization` | Unit 13, Exercise 10 (the linear error model against the nonlinear step) |
| Unit 12 | `step-profiling` | Unit 13, Exercise 7 (already: `step_ms` p50/p99, timing on and off); listed now |

Design §6 already makes Unit 13 the integration unit that carries the capstone rule (013 review B1/M4); `roar-013`
listed only the Unit 8–12 concepts its exercises named. This plan adds the practice, not a new unit.

## The idea (what the probes found, and the story the capstone tells)
The hook: "You have one file. Show what every stage of it bought."

**The starter cannot finish `monza-like`** (`u14/p1.log`): `agents/starter.py` (byte-identical to `unit-01.py`)
crash-loops in the first few hundred waypoints on all five seeds (85 collisions in 900 s; still not a lap at 1800 s).
Made clean by its own one knob, `TARGET_SPEED`: 8 → 2033.65 s, 10 → 1650.50, 12 → 1390.55, **14 → 1203.55 s
(spread 0.70, 5/5 clean)**, 16 → finishes with 0 collisions but 2.695 m from the centreline (not clean).
So the design's gate ("the reference beats the starter at 0 collisions") is read as: **the starter made clean by its
own knob, `TARGET_SPEED = 14.0`** (the fastest clean grid point).

**The build-up ablation** (`u14/p2.log`, `p3.log`; one file, `agents/unit-13.py` with constants changed by
`write_variant`; `monza-like`, nominal noisy car, seeds 0–4, 3 laps, timing off; S1–S7 with the respawn fallback
off, `RESPAWN_IMPULSE = 1e300`, and the pre-re-tune knobs `MU_FRACTION` 0.54, `A_DEC` 5.0, `A_ACC` 4.0):

| stage | the unit's idea (constants) | clean | median / spread (s) | time bought (s) | noise-aware vs previous | max error (m) |
|---|---|---|---|---|---|---|
| S1 | Unit 4: `STEERING "pid"`, `SPEED_MODE "flat"`, 14 m/s, centreline, `MU_G None` | 5/5 | 1219.75 / 0.60 | — | — | 0.434 (c) |
| S2 | Unit 5: `"pursuit"`, flat 15 m/s | 5/5 | 1138.85 / 0.45 | 80.90 | True | 1.042 (c) |
| S3 | Unit 6: `SPEED_MODE "cap"`, `A_LAT` 4.6, `TARGET_SPEED` 32.5 | 5/5 | 617.05 / 0.15 | 521.80 | True | 0.753 (c) |
| S4 | Unit 7: `"profile"`, `TARGET_SPEED` 45 | 5/5 | 514.95 / 0.20 | 102.10 | True | 1.575 (c) |
| S5 | Unit 8: `MU_G` measured, `MU_FRACTION` 0.54 | 5/5 | 510.20 / 0.15 | 4.75 | True | 1.734 (c) |
| S6 | Unit 9: the line | 5/5 | 482.00 / 0.10 | 28.20 | True | 1.529 |
| S7 | Unit 10: `"mpc"` | 5/5 | 482.00 / 0.05 | 0.00 | False | 0.976 |
| S8 | Unit 11: the respawn fallback on | 5/5 | 482.00 / 0.05 | 0.00 | False | 0.976 (telemetry identical to S7) |
| S9 | Unit 13: the re-tune = `agents/unit-13.py` as shipped | 5/5 | 468.55 / 0.10 | 13.45 | True | 1.009 |

(c): from the centreline (no line raced). The story the table tells:
- Most of the time is bought early: S1 → S4 is about 705 s of the 751 s; Unit 6's cap alone 522 s.
- Each stage's constants have a reason the table shows: pursuit is worth one more clean m/s of flat speed (pid at
  15 m/s crashes); Unit 6's cap cannot run at 45 m/s (every `A_LAT` 4.0–6.0 crashes at the first chicane: the 50 m
  curvature lookahead cannot brake from about 39 m/s, Unit 7's motivation), so S3 runs at 32.5 (35 crashes).
- **MPC buys 0.00 s** on the nominal car and the fallback buys nothing there (identical telemetry): they buy
  **margin** (max line error 1.53 → 0.98 m; Unit 11's held-out cars), which a time-only ablation cannot show. The
  report must say so.
- **Leave-one-out from S9** (468.55 s; `u14/p3.log`): no line 495.40 (+26.85), no grip 486.25 (+17.70), no MPC
  (pursuit) 468.60 (+0.05, not noise-aware better), no tune 482.00 (+13.45). The grip buys 4.75 s in the build-up
  and 17.70 s in the leave-one-out: **stages are not additive**, and the order of an ablation is a choice the report
  states.

**The gate** (seeds 0–4 pinned; seed 0 in the premise): `unit-13.py` 468.55 s against the starter at
`TARGET_SPEED = 14.0`, 1203.55 s: **735.00 s**, spreads 0.10 and 0.70, both 5/5 clean at 0 collisions,
`noise_aware_better` holds. Seed 0: 468.55 vs 1203.45.

**Unit 13's two exercises** (`u14/p5.log`–`p7.log`; one 1-lap race of `unit-13.py`, seed 0, timing off, 159.15 s,
clean: Exercise 7's `untimed` race, so no new race; telemetry `u14/r_tel.pkl`):
- R1 `car-identification` (Unit 8's least squares): lag RMS 0.625 / **0.448** / 0.602 / 0.707 m/s² for lags 0–3;
  at lag 1, `A_THROTTLE` 5.075, `A_BRAKE` 8.533, `C_DRAG` 3.137e-4 against the agent's assumed 6.0 / 8.0 / 4.0e-4
  (RMS 0.607); fitted on the first half, RMS 0.453 on the second (assumed 0.604).
- R2 `numerical-integration` (Unit 3): a 1 s replay from 31 start rows; on the agent's own model Euler is 0.123 m
  (median) from a fine RK4 and RK4 5e-9 m; against the real car model error dominates (Euler 0.520, RK4 0.558; RK4
  with R1's map 0.472).
- R3 `dynamic-bicycle` (Unit 6): sideslip from positions above 5 m/s, max 4.38°, median 0.59°; peak lateral
  acceleration 8.71 m/s² at 19.56 m/s; measured over kinematic yaw rate median 0.976 (p10 0.657, p90 1.473); a
  `DynamicCar()` twin at the peak point (kinematic r 0.510, dynamic 0.397).
- R4 `error-model-linearization` (Unit 10): the tightest line point (κ 0.0353, 12.75 m/s); linear vs nonlinear over
  2 s, 0.35 vs 0.29 m at (0.1 m, 0.01 rad) up to 25.40 vs 20.97 at (5 m, 0.8 rad); in the race's own range
  (|ψ| ≤ 0.118 rad) one tick differs by ≤ 2.3e-4 m.
- R5 `stanley-steering` (Unit 5): Stanley never races `monza-like` clean (fallback off, 1 lap, seed 0: the first
  crash at about 44.5 m/s, sooner the higher `ST_K`: 1 → progress 1057, 3 → 413, 8 → 237); a 70 s cap shows it.
- R6 `integrator-windup` (Unit 4): `unit-13.py`'s `PID(0.5, 0.1)` launching `KinematicCar()` from 0 to 45 m/s: with
  limits (0, 1) 0% overshoot, settles 7.75 s, peak integral 1.35; with no limits 50.0% overshoot, 28.40 s, 173.89.
  No race (the limits are not a module constant).
Phase A re-measures every pinned value with the shipped code; a miss stops the plan and amends it.

## Deviations from design (recorded; design 013 v4.13)
- §6 capstone gate: "the starter" is the starter made clean by its own knob (`TARGET_SPEED = 14.0`); the shipped
  starter never finishes `monza-like`. Gate: `unit-13.py` beats it by **≥ 700 s** (735.00 s measured), both clean at
  0 collisions, by Unit 1's rule.
- §6 row 13: Unit 13 also practises the seven concepts above (the capstone rule).
- §3: `site` and `publication` wait on the author's final qualification (a follow-up plan sets them); `buildout`
  is removed here.

## Concepts
Introduces nothing. The capstone practises every concept of Units 1–13 that the brief's milestones exercise
(listed in its manifest; no assumed-baseline concept); Unit 13 adds `numerical-integration`, `integrator-windup`,
`stanley-steering`, `dynamic-bicycle`, `car-identification`, `error-model-linearization`, `step-profiling` to its
practices.

## The capstone
`roar/projects/project-14-competition-agent/` (the id matches `^project-[0-9]{2}-…$`).
- **Brief** (project-first; student-facing, no solutions or outputs; 5 milestone headings, `## Make it yours`,
  `## Requirements checklist`; project-strict: no borrowed tools, every call taught):
  1. **The bar.** Race the starter on `monza-like` (seed 0, capped): it never finishes. Make it clean with its one
     knob (a coarse `TARGET_SPEED` grid); that is the bar your agent must beat.
  2. **Build it up.** Rebuild your stack from one file, one unit's idea per stage (S1–S9: the constants given),
     racing each stage on seeds 0–4: the ablation table (median, spread, time bought, Unit 1's verdict against the
     previous stage, max error, clean).
  3. **Take one out.** The leave-one-out cross-check (line, grip, MPC, tune): what each costs when removed, and
     why stages are not additive.
  4. **Qualify.** Your agent against the bar (Unit 1's rule, 0 collisions) and against your Unit 7 agent;
     `check_submission` on `monza-like`; the packaging checklist (Unit 13).
  5. **The engineering report.** A memo: the ablation table, what each stage bought with its spread, what MPC and
     the fallback buy that time does not show (margin; Unit 11's held-out cars, from Unit 13's record), the order
     of the ablation, what you would do next, and the CARLA caveat (racekit is a model; CARLA is the test).
  The student races on their own machine (about 45 races, a few CPU-minutes).
- **Solutions** (a separate fresh session): race seed 0 of every stage S1–S9 live (about 63 CPU-s) and check each
  against the pinned record (±1 tick); the five-seed tables are the probe record of plan `roar-014`, given as data;
  the bar (the shipped starter capped at 120 s: collisions, not finished; `TARGET_SPEED` 14 seed 0); the gate
  (seed 0: 468.55 vs 1203.45, margin ≥ 700, both clean); `check_submission(UNIT_13, track="monza-like")` PASS with
  p99 printed (≤ 5 ms asserted; the one timed run); a model report.
- **Teacher notes** (inline): goals, the sittings (3 lessons), the hook, the rubric, mistakes (an ablation with one
  seed; reading 0.00 s as "MPC is useless"; additive thinking; the order), prompts, differentiation.

## Unit 13's two exercises
Inserted before the Challenge (which becomes Exercise 11, still tagged `stretch`):
- **Exercise 9, "Measure the car you race"** (`car-identification`, `numerical-integration`): from Exercise 7's
  `untimed` telemetry, fit the longitudinal map at lags 0–3 (Unit 8's least squares; pick the lag by RMS), compare
  with the agent's assumed constants, and check the fit on the race's second half; then a 1 s replay from fixed
  start rows, Euler against RK4 (written by the student, Unit 3), on the agent's model and against the car. No race.
- **Exercise 10, "Why the stack is built this way"** (`dynamic-bicycle`, `error-model-linearization`,
  `integrator-windup`, `stanley-steering`): sideslip and yaw rate from the same telemetry against the kinematic
  model, with a `DynamicCar()` twin; the linear error model against the nonlinear step at the tightest line point;
  the speed PID's launch with and without its limits on `KinematicCar()`; one Stanley race on `monza-like` capped at
  70 s (about 1 CPU-s). One race.
Every value the solutions assert is a deterministic pin from Phase A; anything else is printed.

## Gates (pinned from the probes; Phase A re-runs each with the shipped code)
- **C14.0** the shipped starter on `monza-like`, seed 0, cap 120 s: not finished, collisions ≥ 1.
- **C14.1** the gate: `unit-13.py` and the starter at `TARGET_SPEED = 14.0`, seed 0, 3 laps, timing off, cap 1300 s:
  both clean at 0 collisions; times 468.55 and 1203.45 (±1 tick); margin ≥ 700 s.
- **C14.2** (solutions, not routed) every stage's seed-0 time, clean flag and max error equal the record (±1 tick,
  ±0.01 m).
- **C14.3** Unit 13's new exercises: R1's lag-1 fit to 1e-3 relative, R1's lag choice, R6's overshoots and peak
  integrals, R4's one-tick bound, Stanley not clean in 70 s (asserted in the solutions; deterministic).
- **C14.4** the registry: `coverage-check` (with the capstone directory present: the capstone rule) and every
  `py4kids-tools --book roar` check PASS with `buildout` removed.

## Budgets
- **Routed pytest:** C14.0 (under 1 CPU-s) + C14.1 (2 races, about 16 CPU-s, pooled): about +12 s wall, about 1,130
  s of the interim 1,170 s. **No raise.**
- **Notebooks:** capstone solutions about 90 s serial (S1–S9 seed 0 about 63 CPU-s, the bar about 7 s, the gate
  reuses S9's race, `check_submission` about 10 s); Unit 13 solutions +about 3 s (one 70 s-capped race; the rest
  reuses Exercise 7). Each cell ≤ 120 s. Book exec about 49.3 → **about 51 of 55 CI-min. No raise.**

## Phases
- **Phase A — premise + registry** (Opus subagent).
  - `tests/_capstone_premise.py` + `tests/test_racekit_capstone_premise.py` (C14.0, C14.1; the existing pool runner);
    re-measure C14.2's nine seed-0 races and C14.3's values and log them (`scratchpad/u14/phaseA-gates.log`).
  - Registry: coverage-map entry `project-14-competition-agent` (`kind: project`, `lessons: 3`, introduces nothing,
    requires everything, practises the brief's concepts); Unit 13's entry and manifest gain the seven concepts;
    syllabus capstone row (no emoji) and the "added by the plans that follow" line updated; `books.yaml` drops
    `buildout` (and its comment), the coverage map's header comment updated; design 013 v4.13 (§3, §6 capstone row and
    row 13, §7.1 measured budgets, changelog). `qualification.md` unchanged except a note under the final
    qualification that the flags wait on it.
- **Phase B — content** (Opus subagents): the capstone brief (statements) and Unit 13's two new exercise statements
  in one session; the capstone solutions and Unit 13's two new solutions in a **separate fresh** session. Every race
  timing off except the capstone solutions' `check_submission`. Never race `test-circuit-seed2027/2028`, cars
  72–95, or k ≥ 1000; nothing from `racekit._truth`.
- **Phase C — teacher notes** (inline): the capstone's; Unit 13's pacing and mistakes for Exercises 9–10.
- **Phase D — verification:** `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN; budgets measured.

## Out of scope
- The `site` and `publication` flags and the final qualification (the author's CARLA run; a follow-up plan).
- Any racekit or agent change; any new concept or API name.
- The routed / book-exec tiering decision (a follow-up; no raise is needed here).

## Plan Review
