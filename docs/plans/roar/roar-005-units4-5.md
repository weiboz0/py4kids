# Plan roar-005 — Units 4–5: PID control, and geometric steering

**Design:** `docs/designs/013-roar-book.md` **v4.2** (§4.4 item 1, §5, §6 Units 4–5, §7.2).
**Book:** `roar`. **Autopilot** per AGENTS.md.
**Base:** branches from `main` after `roar-004` merges (#159).
**v2.1** folds round 2 ([sol] B: every stated multi-seed gate is asserted somewhere; [fable] N7–N11).
**v2** folds plan-review round 1 ([sol] REJECT: B the pin record, S tolerances, S the lab's stale row; [fable] APPROVE WITH NITS: S1 the detuned PD, S2 runtime, S3 lab and starter pins, N1–N6).

## Scope
- Unit 4 `roar/units/unit-04-pid-control/` and Unit 5 `roar/units/unit-05-geometric-steering/`: lesson, exercises,
  solutions, teacher notes, manifest.
  Unit 5 is a 🏁 unit: it ships `labs/real-sim.ipynb` (design §7.2).
- Reference submissions `agents/unit-04.py` and `agents/unit-05.py`; milestones
  `milestones/unit-04-pid-control.ipynb` and `milestones/unit-05-geometric-steering.ipynb`.
- One `racekit` change: `KinematicCar(lag_ticks=0)`, an actuator-delay option (default 0, so every existing pin is
  unchanged), the same FIFO semantics as `DynamicCar`'s.
- Both units race on racekit's **kinematic** car (design §4.4 item 1); the dynamic car arrives in Unit 6.

## Probe evidence
All probes are in `scratchpad/u05/`. The pin record is `p6_full.txt` (unfiltered: every controller's full settings, regenerated from `p6.pkl`; the v1 `p6.txt` had `"SPEED_MODE": "pi"` stripped by a display filter, [sol] B), `p6_seed0_lag13.txt` (per-seed lags 1 and 3) and `p7.txt` (the detuned PD and the lab table). Every Unit 4, Unit 5 and Stanley row uses `SPEED_MODE = "pi"`; only the starter rows use the P loop (`probe_agent.py` is a parametrized copy of `agents/unit-03.py`;
`lagcar.py` prototypes `lag_ticks` as a subclass that applies jitter first, then the FIFO, exactly as `DynamicCar`).
`LagKinematicCar(lag_ticks=0)` reproduces `KinematicCar` to the tick on all three tracks (the starter's
223.50 / 412.75 / 882.55 s, and every candidate's time and RMS).

- **Speed (`p5.py`, a straight, jitter 0, the car's own `advance`):**
  the starter's P-only speed loop (gain 0.05) settles 0.508 m/s short of 20 m/s (drag needs a throttle, and a P loop
  needs an error to make it). A higher P gain shrinks the error but never removes it (gain 0.5: 0.053; gain 2: 0.013).
  PI removes it, but from rest the integrator winds up while the throttle sits at 1: 28.71% overshoot, 17.70 s to
  settle. Conditional-integration anti-windup gives 0.26% and 3.55 s.
- **Steering at 20 m/s (`p1.py`, `p6.py`, jitter 0.05, seeds 0–4):**
  a PD law on the cross-track error with the **heading error as its derivative** and a **curvature feedforward**
  (Unit 2's instrument) beats the starter's RMS on every track by more than either range.
  Without the feedforward the controller needs an error to hold a corner (RMS worse on `test-circuit` than the
  starter's); without the D term it oscillates and crashes.
- **Pure pursuit vs delay (`p2.py`–`p4.py`, `p6.py`):** on the lag-free kinematic car, pure pursuit (and a longer
  lookahead in particular) does **not** beat Unit 4's controller: it cuts corners. With a 2-tick actuator delay at
  30 m/s, speed-scaled pure pursuit finishes clean while **the Unit 4 gains** and Stanley (k = 3) crash on every seed
  and the starter does not finish inside the cap. A reactive law survives only when detuned ([fable] S1):
  PD with K_E 0.05, K_HEAD 0.5 is clean at lag 2 but sits further off the line than pure pursuit (`p7.txt`).
  Pure pursuit gets that detuning for free from its speed-scaled lookahead, which is why it is the robust choice
  when the delay is unknown.
  A preview on `carla_like` (`p4.py`, `oval`, not shown to students before Unit 6) agrees: at 25 m/s Unit 4's PD
  crashes on 3/3 seeds and pure pursuit (k = 0.3) is clean.

## Deviations from design (recorded)
- **The Unit 5 gate is restated** (design §6: "pure pursuit lowers cross-track error at speed (noise-aware)").
  On racekit's lag-free kinematic car this is **false against Unit 4** (the probe above), and only a tie with the
  starter at 20 m/s.
  The honest, pinned claim is the design's own "stability vs corner-cutting": **under actuator delay, a speed-scaled
  lookahead keeps the car stable where the tighter controllers go unstable, and it pays for that with corner-cutting
  when there is no delay.** Gate U5.4 pins both halves, and pins a detuned PD that also survives lag 2 but loses to pure pursuit beyond noise.
  Lag 2 is the smallest delay that discriminates on the kinematic car (at lag 1 all four controllers are clean); it stands in for `carla_like`'s 1-tick lag plus its steering-rate limit and tyre dynamics, which the `p4.py` preview agrees with ([fable] N3). The lesson says so in one sentence. CARLA's delay is unknown until Unit 8 measures it, so the
  Unit 5 lab runs both agents on CARLA and lets the real car decide which the student keeps (design §6 gate policy:
  a falsifiable experiment, either outcome acceptable on the evidence).
  `agents/unit-05.py` ships pure pursuit, because it is the robust choice when the delay is unknown.
  A one-line design 013 **v4.3** amendment of the §6 Unit 5 gate cell records this, so the design and the syllabus agree.
- **Actuator delay is a Unit 5 concept**, so `KinematicCar` gains `lag_ticks` here (design §4.4 lists "one to two
  ticks of actuator lag" under the dynamic car; the kinematic car needs it now to show the trade-off).
  The Unit 3 teacher notes already list actuator delay among the sources of model error.
- **Units 4–5 change the driving.** Both agents hold 20 m/s with a PI loop (the starter holds 19.49 m/s), so race
  times fall by about 1.4–1.7%; both keep `TARGET_SPEED = 20.0` (speed planning is Units 6–7).

## Buildout stays
The whole-book lesson total becomes 9 + 3 + 3 = 15, under 30.

## Concepts (7 new; all `kind: technique`, globally unique)
- Unit 4 (`unit-04-pid-control`), requires Units 1–3:
  - `pid-control`: the P, I and D terms; the discrete form at the 0.05 s tick; a derivative taken from a measured
    rate instead of a finite difference;
  - `integrator-windup`: actuator saturation; conditional integration (integrate only when unsaturated, or when the
    error drives the output back out of saturation);
  - `step-response`: overshoot, settling time (2% band), steady-state error, and tuning by step response;
  - `cross-track-steering`: steering from the cross-track error with the heading error as its derivative, plus a
    curvature feedforward δ_ff = atan(L·κ).
- Unit 5 (`unit-05-geometric-steering`), requires Units 1–4:
  - `pure-pursuit`: the arc through a lookahead point, κ = 2 sin α / L_d, δ = atan(L·κ);
  - `lookahead-tuning`: speed-scaled lookahead L_d = clip(k·v, L_min, L_max); actuator delay; stability vs
    corner-cutting;
  - `stanley-steering`: the front-axle heading-plus-cross-track law δ = ψ_e + atan(k·e / v).
- `practices:` both units practise the measurement concepts (`race-telemetry`, `repeated-run-measurement`,
  `telemetry-plotting`) and the Unit 2 instruments (`cross-track-error`, `menger-curvature`, `frames-and-heading`);
  Unit 4 practises `longitudinal-map` (the steady-state error is a drag balance); Unit 5 practises Unit 4's
  `pid-control` and `cross-track-steering`. Unit 4 also practises `kinematic-bicycle` (δ_ff = atan(L·κ) is its
  steady-state circle) ([fable] N5).

## The reference submissions
- **`agents/unit-04.py`** = `agents/unit-03.py` (its instruments and `predict` kept) with:
  - a small `PID` class: `update(error, dt, rate=None)` returns `kp·e + ki·∫e + kd·(rate or Δe/dt)`, with output
    limits and conditional-integration anti-windup; `reset()`;
  - speed: `PID(kp=0.5, ki=0.1)` on `TARGET_SPEED − speed`, output clipped to [−1, 1] and split into throttle and brake;
  - steering: wheel angle δ = atan(L·κ_i) − K_E·e + K_HEAD·ψ_e with `K_E = 0.2` rad/m and `K_HEAD = 1.0`, where e is
    Unit 2's cross-track error, ψ_e = wrap(segment heading − yaw) on Unit 2's `segment_index`, and κ_i the Menger
    curvature at that index; steer = −δ / δ_max, clipped. (The heading term is the D term:
    ė = −v·sin ψ_e, which the lesson derives. So K_HEAD = K_D·v: the effective damping K_D falls as 1/v, a third
    less at 30 m/s than at 20, which is part of why fixed gains fail at speed with delay; the lesson says so,
    [fable] N2.)
  - The P-only, no-feedforward and no-D variants are reachable by `write_variant` (`FEEDFORWARD = False`,
    `K_HEAD = 0.0`).
- **`agents/unit-05.py`** = `agents/unit-04.py` with `STEERING = "pursuit"` (also `"pid"` = Unit 4's law exactly, and
  `"stanley"`), so every comparison is one `write_variant` away:
  - pure pursuit: L_d = clip(`PP_K`·v, `PP_MIN`, `PP_MAX`) with `PP_K = 0.3` s, `PP_MIN = 3.0` m, `PP_MAX = 40.0` m;
    the target is the first waypoint after `segment_index` whose straight-line distance from the car is ≥ L_d;
    α is its bearing in the car frame (Unit 2's `to_car_frame`); δ = atan2(2L·sin α, d) with d the distance to it;
  - Stanley (`ST_K = 3.0`): the front-axle point (x + L cos ψ, y + L sin ψ) is projected onto the segments
    `segment_index − 4 … segment_index + 11` (wider than needed: the front axle lands on segment i + 1 or i + 2; a
    code comment says so, [fable] N6); δ = wrap(segment heading − ψ) + atan2(−ST_K·e_f, max(v, 1)).
  - With `STEERING = "pid"` the file races exactly like `agents/unit-04.py` (to the tick; asserted).

## Gates (pinned from the probes; a miss means stop, amend and re-gate)
Deterministic (jitter 0) race times are within one tick (±0.05 s) of the pins, U4.1's settling times are exact to the tick (a deterministic straight-line run), and
jittered median times within ±0.05 s ([sol] S, design §4.5); clean/crash outcomes and the per-seed collision lists
are exact, and every noise-aware comparison is strict. RMS / max |offset| on driving rows (`held == 0`) within ±0.0005 / ±0.005 m
of the pins unless stated; "noise-aware" means `racekit.measure.noise_aware_better` or a median gap larger than both
ranges, as stated.

**Unit 4** (`p5.py`, `p6.py`):
- **U4.1, the speed step response** on `KinematicCar()` (jitter 0, a straight, 10 substeps, 30 s), from rest to
  20 m/s unless stated:

  | controller | overshoot | settling (2% band) | error at 30 s |
  |---|---|---|---|
  | P 0.05 (the starter) | 0 | never | 0.5081 |
  | P 0.5 | 0 | 3.60 s | 0.0531 |
  | P 2.0 | 0 | 3.30 s | 0.0133 |
  | PI (0.5, 0.1), no anti-windup | 28.71% | 17.70 s | −0.0290 |
  | PI (0.5, 0.1), anti-windup | 0.26% | 3.55 s | −0.0003 |

  From 15 m/s: PI without anti-windup 7.19% / 8.40 s; with it 0.98% / 1.35 s.
  Tolerances: overshoot ±0.01 percentage points, settling exact to the tick, error ±1e-4 m/s.
  The steady-state error of a P loop is derived from the drag balance K_p·e·a_T = c·(v* − e)² (0.506 for the starter,
  the 30 s figure still settling); the lesson links it to Unit 1's 19.49 m/s and Unit 3's terminal speed.
- **U4.2, the reference submission** (jitter 0): oval 216.35 s, test-circuit 400.55 s, monza-like 858.45 s, all clean;
  RMS 0.0034 / 0.0139 / 0.0112 m and max 0.009 / 0.136 / 0.153 m. `check_submission(...).ok`, and the isolated 3.8
  test (parametrized over `agents/*.py`) passes.
- **U4.3, the scorecard** (jitter 0.05, seeds 0–4), against G2.5's starter numbers:

  | track | RMS median (range), Unit 4 | starter | time median (spread), Unit 4 | starter |
  |---|---|---|---|---|
  | oval | 0.1041 (0.0062) | 0.1397 (0.0099) | 216.40 (0.05) | 220.75 (0.35) |
  | test-circuit | 0.1048 (0.0050) | 0.1586 (0.0055) | 400.60 (0.10) | 407.50 (0.65) |
  | monza-like | 0.1029 (0.0042) | 0.1416 (0.0040) | 858.55 (0.00) | 870.50 (0.45) |

  On every track the RMS median gap exceeds the larger range, and `noise_aware_better(unit_04_times, starter_times)`
  holds. All 15 races are clean. The starter's five-seed times are raced in the Unit 4 milestone (the `test-circuit`
  starter times 407.50 s, spread 0.65, come from `p1.py` and have no earlier shipped pin, [fable] S3).
- **U4.4, the ablations** (jitter 0.05, seeds 0–4): without the feedforward the RMS medians are
  0.1327 / 0.1794 / 0.1374 m (worse than with it on all three; worse than the starter on `test-circuit`), all clean;
  without the D term (`K_HEAD = 0`) on `test-circuit` with `max_seconds=400` every seed crashes, with
  [30, 32, 31, 29, 30] collisions.

**Unit 5** (`p6.py`):
- **U5.1, pure pursuit on a circle** (analytic): for a car on a circle of radius R, tangent to it, and a target on the
  circle at chord distance d, sin α = d / 2R, so κ = 2 sin α / d = 1/R. Checked for R ∈ {18, 25, 120} m and
  d ∈ {3, 6, 9, 12} m with the submission's function, to 1e-12; and δ = atan(L/R).
- **U5.2, the reference submission** (jitter 0, lag 0): oval 216.35 s, test-circuit 400.50 s, monza-like 858.45 s,
  all clean; RMS 0.0035 / 0.0193 / 0.0157 m. `check_submission(...).ok`. With `STEERING = "pid"` it races exactly
  like `agents/unit-04.py` (U4.2's times and RMS).
- **U5.3, the 20 m/s scorecard** (jitter 0.05, seeds 0–4, lag 0): RMS medians 0.1422 / 0.1481 / 0.1445 m (ranges
  0.0107 / 0.0050 / 0.0022) for pure pursuit and 0.0987 / 0.1043 / 0.0981 m for Stanley, all clean.
  Pure pursuit does **not** beat Unit 4 here (U4.3), and the lesson says so.
- **U5.4, the delay study** (the gate): `test-circuit`, `TARGET_SPEED = 30.0`, jitter 0.05, seeds 0–4,
  `max_seconds=400`, on `KinematicCar(jitter=0.05, lag_ticks=N)`:

  | lag | Unit 4 PD | Stanley | pure pursuit k = 0.3 | starter |
  |---|---|---|---|---|
  | 0 | clean, RMS 0.1295 (0.0060) | clean, 0.1582 (0.0139) | clean, 0.3097 (0.0153) | clean, 0.2346 (0.0167) |
  | 1 | clean, 0.2136 (0.0077) | clean, 0.1939 (0.0129) | clean, 0.3469 (0.0198) | clean, 0.3233 (0.0154) |
  | 2 | **crashes** [41, 42, 43, 43, 40] | **crashes** [20, 16, 16, 17, 20] | **clean**, 0.4526 (0.0234), 269.70 s | does not finish in 400 s ([0, 1, 0, 0, 0] collisions) |
  | 2, detuned PD (K_E 0.05, K_HEAD 0.5) | clean, RMS 0.5149 (0.0376), 269.70 s; at lag 0: 0.3538 (0.0280) | | | |
  | 3 | crashes, 60 each | crashes [53, 53, 53, 53, 50] | clean, 1.4305 (0.1659), 282.00 s (spread 3.75) | crashes [41, 41, 41, 41, 44] |

  (The starter here keeps its P speed loop; the other three use Unit 4's PI.)
  **The gate:** at lag 2, pure pursuit is clean 5/5 and Unit 4's PD and Stanley collide on every seed (the exact
  per-seed collision lists above); the detuned PD is also clean at lag 2, and pure pursuit's RMS median beats it by
  more than both ranges (0.4526 vs 0.5149); at lag 0, Unit 4's RMS median beats pure pursuit's by more than both
  ranges.
  **Where each gate is asserted ([sol] r2 B, [fable] N7, N9):** every multi-seed claim in U4.3, U4.4, U5.3, U5.4 and
  U5.5 is asserted in full by a routed racekit test, `tests/test_racekit_unit04_05_premise.py`, which races the
  reference submissions (via `write_variant`) in the session's parallel process pool (`_premise.py`'s `race_all`
  pattern): the exact per-seed collision lists of Unit 4's PD, Stanley and the starter at lag 2, the detuned PD at
  lags 0 and 2, all four controllers at lag 0, and the U5.5 sweep medians on five seeds. The milestones assert the
  trimmed subset below, and the lesson shows the rest as the probe record. Added routed cost: about 4 CPU-minutes,
  about 35 s on 8 workers.
  **Runtime trim ([fable] S2):** the milestone races lag 0 for all four controllers (5 seeds), and at lag 2 pure
  pursuit, Unit 4's PD and the detuned PD on 5 seeds, Stanley and the starter on seed 0 only (their crash rows cost
  about 11–13 s each). Lags 1 and 3 appear in the lesson for seed 0 only, pinned from `p6_seed0_lag13.txt`:
  lag 1 starter 280.25 s / 0.3335, PD 269.40 / 0.2150, pursuit 269.05 / 0.3498, Stanley 269.00 / 0.1904, all clean;
  lag 3 starter 41 collisions, PD 60, Stanley 53, pursuit clean 282.00 s / 1.4305.
- **U5.5, the lookahead sweep** (the same setting, `PP_K` ∈ {0.2, 0.3, 0.4, 0.5}): RMS medians at lag 0
  0.1800 / 0.3097 / 0.4656 / 0.6477 m (a longer lookahead cuts corners), at lag 2 1.2972 (time 292.35 s, spread 5.75:
  it weaves) / 0.4526 / 0.5625 / 0.7203 m, all clean. The best lookahead grows with the delay. The milestone races
  the sweep on seed 0 only (per-seed pins from `p6.pkl`); the lesson shows the medians.
- **U5.6, the lab** (design §7.2): `labs/real-sim.ipynb` passes `lab-check` against the sample CSV. Its recorder is
  the Unit 1 recorder with one change, `offset` = the agent's own `self.cross_track_error`; a routed racekit test
  splices it into `agents/unit-05.py`, races `oval` (jitter 0) and checks the recorded `offset` against racekit's
  telemetry `offset` one row earlier (the alignment the Unit 2 milestone uses) within 1e-4 m (the Unit 1 recorder
  writes 0 there today; the test asserts the new column, [fable] N4). A second, respawning race exercises the
  stale-row rule deterministically ([fable] N10): `STEERING = "pid"`, `TARGET_SPEED = 30.0`, `test-circuit`,
  `KinematicCar(jitter=0.05, lag_ticks=2)`, seed 0, `max_seconds=400` (41 collisions); the analysis's exclusion
  drops exactly the first row after each hold run.
  **The stale row ([sol] S):** on CARLA the first observation after a respawn hold is still the crash pose (the Unit 1
  lab says so), so that row's cross-track error is meaningless although `held == 0`. The analysis excludes the first
  row after every hold run (and, in a file without held rows, the row where progress drops) from the RMS and max,
  and says why; the routed test covers a respawning race.
  **The lab table ([fable] S3)**, racekit's predictions on `monza-like` at 20 m/s, jitter 0.05, seed 0, all clean
  (`p7.txt`): Unit 4 RMS 0.1054 / 0.1288 / 0.2420 m (858.55 / 858.95 / 861.85 s) and Unit 5 0.1450 / 0.1655 /
  0.2142 m (858.60 / 858.90 / 859.75 s) at lag 0 / 1 / 2. They cross at lag 2; the lab names the crossover: if
  CARLA's Unit 4 RMS is below Unit 5's, the real car behaves like a small delay.

## Phases

### Phase A: racekit and registry (Opus subagent for the racekit change; registry inline)
- `KinematicCar(lag_ticks: int = 0)`: validated (an int ≥ 0); a FIFO of (throttle, steer, brake), refilled with zeros
  by `reset()` (a respawn resets it, as `DynamicCar`); jitter is drawn first, then the FIFO, as `DynamicCar`.
  Docstring updated: the FIFO holds (throttle, steer, brake) only, `hand_brake` and `reverse` act immediately (as
  `DynamicCar`), jitter is drawn at command time and queued, and `reset`/respawn discards queued commands
  ([fable] N1). Tests: lag 0 is bit-identical to the old car over a fuzz of actions; with lag k an action first
  changes the state on tick k + 1; `reset` refills the queue; a respawn mid-race drains it; the jitter draw order is
  unchanged; the U5.4 lag-2 row reproduces for seed 0 (one race per controller).
- `concepts.yaml` gets the 7 ids; `coverage-map.yaml` gets the Unit 4 and Unit 5 entries (`lessons: 3` each); the
  manifests mirror them; Unit 5's manifest declares `lab: true`.
- `library_methods` / `api-order.yaml`: the closed list of new callables the notebooks use, each mapped to
  infrastructure or a teaching concept (no taught callable before its unit). Expected: none beyond those already
  listed plus `to_car_frame`-style student functions (student code is not a library call); add any the content needs
  and record them in the post-execution report. `append`, `deque` and `popleft` (a FIFO or history cell) are added to
  infrastructure if used ([fable] N5).
- `syllabus.md` rows for Units 4–5; design 013 **v4.3** (the restated Unit 5 gate, citing this plan).

### Phase B: Unit 4 content (Opus subagents: lesson + exercise statements; solutions in a separate fresh session)
- **Lesson:**
  1. The hook: "Hold 20 m/s, then follow the line." The starter holds 19.49 m/s, not 20 (Unit 1's telemetry).
  2. P control, and why a P loop needs an error: the drag balance (U4.1 row 1–3).
  3. I, and windup from a standing start; conditional integration (U4.1 rows 4–5).
  4. Step-response tuning: overshoot, settling, steady-state error; a small gain grid.
  5. D, taken from a measured rate.
  6. Steering: the cross-track error, the heading error as its derivative (ė = −v sin ψ_e), and the curvature
     feedforward; the ablations (U4.4).
  7. The Unit 4 agent vs the starter: the scorecard (U4.3) and the race-time gain.
  8. The bridge to Unit 5: what a controller that only reacts cannot do.
- **Exercises:** at least 6 `## Exercise N` and at least 2 stretch, drilling each concept. Stretch: (a) derivative
  kick: a set-point change through a finite-difference D term vs a measured-rate D term; (b) the I term on steering
  (a steady corner bias without feedforward) vs the feedforward.
- `agents/unit-04.py` and its milestone (U4.1–U4.4).

### Phase C: Unit 5 content (the same dispatch rule)
- **Lesson:**
  1. The hook: "Steer like a driver looks ahead."
  2. The pure-pursuit geometry, checked on a circle (U5.1).
  3. Pure pursuit on the track at 20 m/s, and why it does not beat Unit 4 on a car with no delay (U5.3).
  4. Actuator delay: what it is, why every real car has some, and `KinematicCar(lag_ticks=...)`.
  5. The delay study at 30 m/s (U5.4): stability vs corner-cutting.
  6. Speed-scaled lookahead, swept (U5.5).
  7. Stanley, and why a law with no lookahead is delay-sensitive; a detuned PD survives the delay too, but pure
     pursuit gets the detuning for free from its lookahead and stays closer to the line.
  8. Choosing under uncertainty: the reference keeps pure pursuit until CARLA says otherwise (the lab).
- **Exercises:** at least 6 and at least 2 stretch. Stretch: (a) the lookahead that minimizes RMS at lag 1;
  (b) a lookahead point interpolated on the polyline (exact arc distance) vs the first-waypoint rule.
- `agents/unit-05.py`, its milestone (U5.1–U5.5), and `labs/real-sim.ipynb` (U5.6): the five design §7.2 steps
  listed briefly, with a pointer to the Unit 1 lab for the details ([fable] N4); the stale post-respawn row excluded; the one-line recorder change, the analysis (RMS and max |offset|, time, collisions), and a
  comparison table against racekit's predictions for `unit-04.py` and `unit-05.py` on `monza-like` at 20 m/s with
  lag 0, 1 and 2 (seed 0, jitter 0.05). The student runs both agents on CARLA and keeps the one the real car prefers.
- The routed lab-recorder test (U5.6).

### Phase D: teacher notes for both units (active session, inline)

### Phase E: verification (named)
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN.
- `bash scripts/pre-merge-guard.sh --pr` OK.
- All the gates hold in the milestones; the lab passes `lab-check`.
- Units 4–5 notebook execution totals ≤ 8 min ([fable] S2 measured about 9–11 min for the v1 scope; the trims above
  bring the milestone to about 3 min), and the post-execution report records the book-level exec-lessons +
  exec-solutions total against design §7.1's 15 CI-minute cap. Over budget means trim, not raise.

## Out of scope
- The dynamic car and `carla_like` in content (Unit 6); speed planning (Units 6–7); MPC (Unit 10).
- Changing `TARGET_SPEED` in the reference submissions.
- Any change to `KinematicCar` other than `lag_ticks` (the brake creep stays a documented property; it is a user
  follow-up).

## Plan Review

### Round 1 (v1 @ d05bb12)
- [self] APPROVE WITH NITS: the K_HEAD = K_D·v scaling must be stated; the lesson's lag-1/lag-3 rows need per-seed pins. Both [FIXED v2].
- [sol] REJECT (it could not run uv in its read-only sandbox, so it reviewed from the probe record):
  - **B** [FIXED v2] The pin record did not match the probe inputs: the v1 `p6.txt` was produced through a display filter that stripped `"SPEED_MODE": "pi"`. The races did use PI. The unfiltered record `p6_full.txt` was regenerated from the pickle and is cited; the stray `p6.pkl` was moved out of the repository and `p6.py` now writes beside itself.
  - **S** [FIXED v2] Tolerances: deterministic times and settling within one tick, jittered medians ±0.05 s; outcomes and noise-aware comparisons stay strict.
  - **S** [FIXED v2] The lab excludes CARLA's stale first row after a respawn from the RMS.
  - Confirmed: the restated Unit 5 gate is a defensible conditional claim; lag 2 is within the design's actuator-lag range; the lag semantics match `DynamicCar`; the D-term sign is right.
- [fable] APPROVE WITH NITS (reproduced U4.1, the lag-0 equivalence, U5.1 to 5.5e-15, U4.2/U5.2, and samples of U4.3, U5.3, U5.4, U4.4; checked the lap wrap, the Stanley window, respawn with a queue and the derivative sign):
  - **S1** [FIXED v2] "the only controller that finishes clean" was false for a detuned PD; restated, and the detuned PD (0.05 / 0.5) is pinned and beaten by pure pursuit beyond noise.
  - **S2** [FIXED v2] Runtime: the milestone is trimmed; the budget is 8 min with the book total reported.
  - **S3** [FIXED v2] The lab table and the starter's `test-circuit` times are pinned or raced.
  - **N1–N6** [FIXED v2].

### Round 2 (v2 @ e3f5122)
- [self] APPROVE.
- [sol] REJECT:
  - **B** [FIXED v2.1] The milestone's runtime trim left the five-seed Stanley/starter lag-2 lists and the U5.5 medians unasserted. A routed premise test now asserts every stated multi-seed gate in a parallel pool; the milestone keeps the trimmed subset.
  - **N** [FIXED v2.1] Settling: U4.1 is exact to the tick, and the shared rule now says so.
  - Round 1 verified resolved; U4.2, lag-2 seed 0 (pursuit, PD, detuned PD) and a lab row reproduced with the venv interpreter.
- [fable] APPROVE WITH NITS (every round-1 finding verified resolved; the detuned PD five-seed row, two lab rows and the starter's `test-circuit` times reproduced digit for digit; the milestone runtime arithmetic checked at about 3 min):
  - **N7** [FIXED v2.1] (with [sol] B): gates asserted where stated.
  - **N8** [FIXED v2.1] Settling wording.
  - **N9** [FIXED v2.1] The detuned PD at lag 0 is raced in the routed test.
  - **N10** [FIXED v2.1] The respawning lab-recorder race is named.
  - **N11** [FIXED] The filtered v1 record is renamed `p6_FILTERED_DO_NOT_CITE.txt`.

