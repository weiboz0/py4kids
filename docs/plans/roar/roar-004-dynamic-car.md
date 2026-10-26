# Plan roar-004: the dynamic car, the carla-like truth car, noise and the telemetry generator

**Design:** `docs/designs/013-roar-book.md` **v4.2** (§4.2 the spin-out rule, §4.3 the generator driver step 2, §4.4 items 2–3, §4.5, §5, §7.1).
**Book:** `roar`. **Autopilot** per AGENTS.md.
**Base:** branches from `main` after `roar-003` merges (#158).

## Scope
This plan is **infrastructure plus probes** (design §8).
It ships no unit, no checkpoint and no student-facing notebook.
- `racekit.cars.DynamicCar`: the public dynamic bicycle that Unit 6 teaches. It has:
  - saturating tyres and a per-axle friction circle;
  - longitudinal force, brake and drag;
  - a steering-rate limit and 0–2 ticks of actuator lag;
  - an exact brake stop;
  - a low-speed kinematic blend;
  - a spin-out predicate;
  - optional section-varying grip.
- `racekit._truth` plus `racekit.cars.carla_like(noise=False)`: the stand-in for CARLA.
  It has its own parameters and per-section grip, and an optional seeded throttle jitter.
- `racekit.tracks.GRIP_SECTIONS` and `grip_sections(track)`: the **public** section rule. It is six equal arc-length sections per lap, counted from the start waypoint. Units 7 and 8 tune and identify one μ per section.
- Runner: it calls `car.attach_track(track)` when the car has one. It adds the **spin-out major collision** (design §4.2) with the same respawn rule as the wall, and `RaceResult.respawn_causes`.
- Telemetry generator (`roar/data/generate.py` step 2, `roar/data/gen_sysid.py`).
  It writes **sensor-observable** logs of the carla-like car, recorded by an agent from its own sensors as a CARLA recorder would.
  The logs go to `generated/sysid/`, in a new `racekit` log format (`write_log_csv` / `read_log_csv`).
- Routed tests for all of it, and the probe facts that roar-005 to roar-008 build on, pinned as tests.

## Probe evidence (`scratchpad/u04/`, prototype `dyn.py` / `truthcar.py`; numbers re-pinned on the shipped code)
- **The dynamic car reproduces the Unit 6 premise.**
  A pure-pursuit agent (lookahead max(6, 0.5·v) m) at a flat 20 m/s finishes `oval` (224.65 s).
  It fails `test-circuit` (DNF, 16 collisions in 1500 s) and `monza-like` (DNF, 21 collisions) by running wide at the tight corners.
  The same agent with a **curvature-limited speed** (v ≤ √(a_lat/κ), a_lat = 0.7g, braking at 5 m/s² towards each cap 120 m ahead) finishes all three cleanly: 217.65 / 413.70 / 873.00 s.
  On the kinematic car the 20 m/s pure-pursuit agent is clean everywhere.
- **Spin-outs are real, not universal.**
  The starter's steering (gain 8/√v with δ_max = 70°) whips the wheel by ±0.3 at 18 m/s and **spins** the dynamic car on `test-circuit` (37 spins in 1500 s).
  Pure pursuit at 20 to 45 m/s never spins.
  At 60 m/s pure pursuit spins on `oval` (18 spins).
- **Unit 7 premise (late braking).**
  Pure pursuit with a 45 m/s cap and only 120 m of look-ahead braking fails `test-circuit` (18 collisions).
  It finishes `monza-like` (476.70 s) and `oval` (132.50 s).
- **Unit 7 premise (per-section grip).**
  On `carla_like()` on `test-circuit`, with a 45 m/s cap and 300 m of look-ahead at 6 m/s², a global a_lat sweep runs clean at 5.0 (294.75 s), 5.25 and 5.5 (287.95 s), and crashes at 6.0.
  One knob per section on top of global 5.5:
  - section 0 stays clean up to ×1.45 (286.2 s);
  - section 3 stays clean up to ×1.3 (284.45 s), crashing at ×1.45;
  - section 5 stays clean at ×1.1 (286.7 s);
  - sections 1, 2 and 4 crash already at ×1.1.

  Per-section tuning therefore beats the best global value by more than 1 s per section, well above the noise spread.
  The sections that accept more grip are not simply the highest-μ ones: corner geometry and the controller matter too.
  That is the honest framing of "find the grip that is really there".
- **Noise.**
  White **steer** jitter is unrealistic at speed: σ = 0.01 is about 0.7° of wheel angle per tick, roughly 8 m/s² of lateral transient at 45 m/s, and crashes most runs.
  Throttle-only jitter σ = 0.1 over seeds 0–4 gives a spread of 0.25 s on `monza-like` (median 502.15 s) and 0.10 s on `test-circuit`, all runs clean.
  The carla-like noise is therefore **throttle-only**, with σ pinned in Phase A to give a `monza-like` spread in the band of G4.4.
- **Unit 8 premise (identification).**
  Least squares on one noisy `monza-like` race (10,046 non-held rows) of dv/dt = a_T·throttle − a_B·brake − c·v|v|, with the action lagged by L ticks:
  - the residual RMS is smallest at **L = 1** (0.482 against 0.601 at L = 0 and 0.546 at L = 2), the truth lag;
  - a_B = 8.64 (truth 8.6) and c = 3.32e-4 (truth 3.4e-4);
  - a_T = 5.16 (truth 5.4): about 4% low, from the clipped throttle jitter and rear-axle traction limits.
- **Cost.** The prototype costs 0.40–0.50 ms per tick against 0.15 for the kinematic car, which is about 3–4.5 s for a 6,400-tick race.

## Deviations from design (recorded)
- **The Unit 6 hook.**
  The design's hook is "Why does the car spin at Parabolica?".
  On this model the 20 m/s failure is **running wide at the tight corners** (the `test-circuit` hairpin and chicane, the Rettifilo).
  Spins come from aggressive steering (the starter's gain) or very high speed, and the Parabolica (R = 140 m) is safe at 20 m/s.
  roar-006 reframes the hook from this evidence. This plan only records it.
- **The noise is throttle-only** (see Probe evidence). Design §4.4 says "a seeded actuator jitter", which this satisfies.
  `KinematicCar` keeps its two-channel jitter: Unit 1's pins depend on it.
- **Grip sections are equal arc-length sixths**, a public rule. The design says "section-varying grip" without fixing the sections.
  Equal sections are reproducible on any generated track, seeded checkpoint tracks included, and students can compute them.

## Design of the dynamic car (`DynamicCar`, the public defaults)
- **State:** x, y (the centre of gravity, ROAR frame), ψ, v_x and v_y (body frame), r (yaw rate), δ (the actual wheel angle), and the lag FIFO of past actions.
  `v` is the signed speed, ±‖(v_x, v_y)‖ with the sign of v_x, so telemetry's `v` keeps its meaning.
  `velocity()` returns the world-frame vector.
- **Parameters (defaults):**
  - mass 1845 kg, I_z 2900 kg·m², l_f 1.40 m, L 2.875 m (l_r = L − l_f);
  - δ_max 70° (steer s → target δ = −s·δ_max, as in `KinematicCar`), steering rate 360°/s;
  - a_throttle 6, a_brake 8, c_drag 4e-4 (the kinematic car's longitudinal map, so Units 1–5 numbers carry over);
  - μ = 1.0, tyre B = 10, C = 1.6, lag 1 tick;
  - kinematic blend between 3 and 5 m/s;
  - spin-out at |β| > 25° above 5 m/s.
- **Forces:**
  - static axle loads F_z,f = m·g·l_r/L and F_z,r = m·g·l_f/L (no load transfer, a labelled model limit);
  - longitudinal force m·(drive − brake against the motion − drag), split between the axles in proportion to their load, each clipped to ±μF_z;
  - lateral force F_y = −√((μF_z)² − F_x²) · sin(C·atan(B·α)), a saturating curve with fall-off past its peak (about 8.6° at B = 10) under the friction circle;
  - slip angles α_f = atan2(v_y + l_f·r, u) − δ and α_r = atan2(v_y − l_r·r, u), with u = max(|v_x|, 3 m/s).
- **Integration:** RK4 per substep (10 per tick, as the runner passes).
  The steering moves towards its target at the rate limit once per substep, before the RK4 stages.
- **Brake stop (no creep):** if the brake is on and |v_x| ≤ (braking + |drive|)·h at the start of a substep, and the brake beats the drive, the car stops: v_x = v_y = r = 0.
  A sign change of v_x under braking also clamps to 0.
  This is deliberately unlike `KinematicCar`, whose RK4 substeps creep at a few cm/s (roar-003 content gate). See Out of scope.
- **Low speed:** after each substep, with weight w = clip((|v_x| − 3)/(5 − 3), 0, 1), v_y and r blend towards the kinematic values: r_k = v_x·tan δ / L and v_y,k = l_r·r_k.
- **Section grip:**
  - `DynamicCar(mu=...)` takes a scalar, or a length-6 sequence that is applied per grip section;
  - a per-section μ requires `attach_track(track)`, which the runner calls;
  - the car finds its section with `track.nearest` and a carried hint, which resets on `reset()`;
  - μ is read once per tick, at the start of `advance`.
- **Noise:** `jitter` (throttle) and `steer_jitter` are separate, both drawn from `random.Random(seed)`. `seed()` follows `KinematicCar`.

## The carla-like car
- `racekit/_truth.py` holds its parameters. Its module docstring says: "do not read this in teaching material".
  - The values are chosen so that each parameter Unit 8 identifies differs from `DynamicCar`'s defaults by at least 5%: mass 1845, I_z 3100, l_f 1.45, δ_max 66°, a_throttle 5.4, a_brake 8.6, c_drag 3.4e-4, B 9, C 1.45, lag 1.
  - μ per section comes from `numpy.random.default_rng(seed)` with the seed taken from sha256("racekit-grip:" + track name), uniform in [0.78, 1.05] and rounded to 3 decimals.
  - This gives a reproducible μ for any track name, including seeded checkpoint tracks.
- `carla_like(noise=False)` returns a configured `DynamicCar`. With `noise=True`, its throttle jitter is `_truth.NOISE_SIGMA`, pinned in Phase A.
- **The rule that content never reads `_truth`:** a routed test fails if any file under `roar/units/`, `roar/checkpoints/`, `roar/projects/racekit/agents/`, `roar/projects/racekit/milestones/`, `roar/projects/*/` notebooks or `roar/labs/` contains `_truth`.

## Gates (pinned from the probes; a miss means stop, amend and re-gate)
All gates are routed tests under `roar/projects/racekit/tests/`, plus the existing suite.
- **G4.1, the analytic car checks** (design §7.1):
  - circle radius: at 8 m/s with steer 0.02 the steady radius is within 3% of L/tan δ (low lateral acceleration);
  - friction circle: in a seeded 500-case random-action fuzz, every substep's tyre forces satisfy √(F_x² + F_y²) ≤ μF_z + 1e-9 per axle;
  - longitudinal: a straight full-throttle run below the traction limit matches the longitudinal map to 1e-3 m/s over 2 s;
  - brake stop: from every v₀ in {0.005, 0.01, 0.03, 0.2, 1, 5} m/s, 1 s of full brake leaves v == 0.0 exactly, and the car never reverses;
  - lag: with `lag_ticks = k`, a throttle step first changes v_x on tick k + 1;
  - the steering rate is respected;
  - from rest at full lock and 0.3 throttle, |v_y| stays ≤ 0.5 m/s (no sideways slide at low speed);
  - spin-out: a scripted 40 m/s full-lock flick triggers `spun_out()`, and a steady 15 m/s, 0.3g circle never does.
- **G4.2, the runner:**
  - a spin-out triggers the same respawn as the wall: start pose, a 20-tick hold, progress reset to 0 and `respawn_causes == ["spin"]`;
  - `attach_track` is called once per race;
  - `KinematicCar` races are unchanged: the existing Unit 1–3 pins (223.50 / 412.75 / 882.55 s and Unit 1's per-seed times) still pass;
  - the default car is still `KinematicCar`.
- **G4.3, the Unit 6 premise:**
  - the test-fixture pure-pursuit agent at a flat 20 m/s on `DynamicCar()` fails `test-circuit` with at least 5 collisions within a 600 s cap;
  - the same agent with the curvature-limited speed finishes `test-circuit` with 0 collisions and 0 spins;
  - on `KinematicCar` the flat 20 m/s agent finishes `test-circuit` with 0 collisions, so the failure belongs to the dynamic model.
- **G4.4, noise:**
  - `carla_like(noise=True)` gives a `monza-like` spread over seeds 0–4 in **[0.15, 0.6] s** with the fixture's limited agent at a 45 m/s cap (clean in all 5);
  - `noise=False` is exactly deterministic, and the same seed gives identical times.
- **G4.5, the Unit 7 premise:**
  - on `carla_like()` on `test-circuit`, the fixture with global a_lat 5.5 is clean;
  - the per-section vector found by the probe's one-knob sweep, combined, is clean and faster than global 5.5 by more than 1.0 s;
  - if the combined vector is not clean, the plan records the best clean combination that the sweep finds and pins that.
- **G4.6, the Unit 8 premise:**
  - on one generated noisy `monza-like` log, lagged least squares has its residual minimum at lag 1;
  - a_B and c_drag are recovered within 5%, and a_T within 10%.
- **G4.7, the generator:**
  - `generate.py` step 2 writes `generated/sysid/test-circuit-seed0.csv` and `monza-like-seed0.csv`;
  - it is byte-stable under the existing checksum contract (two in-process runs, rounded hashes, re-read and re-hash);
  - the log reader round-trips;
  - total generation (tracks, logs and lab sample) is **≤ 1 min** (design §7.1).
- **G4.8, cost:** the median `DynamicCar` cost per tick is **≤ 0.6 ms** on the CI machine, measured and recorded. The racekit pytest stays within the 5-min routed budget.
- **G4.9, Python 3.8:** the new modules pass the existing AST deny-list test and `from __future__ import annotations`. The isolated 3.8 run is unchanged.

## Phases
### Phase A: `racekit` cars and runner (Opus subagent, tooling)
`cars.py` (`DynamicCar`, `carla_like`), `_truth.py`, `tracks.py` (`GRIP_SECTIONS`, `grip_sections`), `runner.py` (`attach_track`, spin-out, `respawn_causes`).
The runner docstring's "Known differences" adds the spin-out approximation.
Tests for G4.1, G4.2, G4.4 and G4.9.
`_truth.NOISE_SIGMA` is pinned here from a σ sweep on the shipped code.

### Phase B: the telemetry generator (Opus subagent, tooling)
- `roar/data/sysid_driver.py`: a recording agent, data-side and never student-facing. It is pure pursuit with a curvature-limited speed, and it logs its own sensor observations and commanded actions every step.
- `roar/data/gen_sysid.py`.
- `generate.py` step 2 and its docstring.
- `racekit.telemetry` gains `LOG_COLUMNS = (t, x, y, yaw, vx, vy, throttle, steer, brake)` with `write_log_csv` / `read_log_csv`, in the v1 CSV conventions with a meta header (track, seed, noise).
- Tests for G4.7.

### Phase C: the premise probes as tests (Opus subagent, tooling)
- `roar/projects/racekit/tests/fixtures/`: the pure-pursuit fixture agent, parametrised by cap, a_lat and section grips (a test fixture, not a reference submission).
- Tests for G4.3, G4.5 and G4.6. The G4.5 vector is re-derived on the shipped code and pinned.
- The test that content never reads `_truth`.

### Phase D: verification (named)
- `uv run --group roar pytest -q roar/projects/racekit/tests roar/tests`.
- `PYTHONHASHSEED=0 uv run --group roar python roar/data/generate.py`, timed.
- `py4kids-tools --book roar` all checks.
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN.
- Then the 3-way content gate, which for this plan reviews the code, the physics and the pinned premises.

## Out of scope
- **No unit content.** There are no lessons, exercises, milestones or teacher notes. This is a tooling-only plan, and the content laws are exercised by roar-005 onwards. The verification phase above is the named verification.
- **`KinematicCar`'s brake creep** (the roar-003 follow-up). It is left unchanged and documented in its docstring as a known model artefact.
  - Changing it would change Unit 3's taught parity (`agents/unit-03.py`'s `stopping_tick`, the Unit 3 milestone and lesson §8), which is errata scope.
  - The races never brake to rest, so no race time is affected.
  - `DynamicCar` stops exactly.
  - The follow-up is listed for the user.
- Load transfer, gears, power limits and tyre temperature are labelled model limits.
- `racekit.sysid_data` and the analysis helpers enter with Unit 8 (roar-008, design §5).
- Any change to `KinematicCar`, the telemetry v1 format or the lab-check format.

## Plan Review
