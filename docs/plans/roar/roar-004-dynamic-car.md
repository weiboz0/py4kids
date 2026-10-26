# Plan roar-004: the dynamic car, the carla-like truth car, noise and the telemetry generator

**Design:** `docs/designs/013-roar-book.md` **v4.2** (§4.2 the spin-out rule, §4.3 the generator driver step 2, §4.4 items 2–3, §4.5, §5, §7.1).
**Book:** `roar`. **Autopilot** per AGENTS.md.
**Base:** branches from `main` after `roar-003` merges (#158).
**v3** folds plan-review round 2. [sol] found three blockers: the low-speed regime broke μg; the comparison was not against the best global setting; the Unit 8 μ premise was unstated. [fable] found that the low-speed gates did not match the prototype. The prototype is now **frozen** at `scratchpad/u04/dyn.py` md5 `94808dd3a5d0a2a9c49817536a67fcb1`, and every number below was measured on it.
**v2** folds plan-review round 1. Both [sol] and [fable] rejected. The decisive finding was [fable] B1: the v1 probes never attached the section grip, so every truth-car number was measured at μ = 1.0. Every probe below was re-run with the grip attached, with the prototype's low-speed and brake-stop physics fixed.

## Scope
This plan is **infrastructure plus probes** (design §8).
It ships no unit, no checkpoint and no student-facing notebook.
- `racekit.cars.DynamicCar`: the public dynamic bicycle that Unit 6 teaches. It has:
  - saturating tyres and a per-axle friction circle;
  - longitudinal force, brake and drag;
  - a steering-rate limit and 0–2 ticks of actuator lag;
  - an exact brake stop and a low-speed kinematic blend;
  - a spin-out predicate;
  - optional section-varying grip.
- `racekit._truth` plus `racekit.cars.carla_like(noise=False)`: the stand-in for CARLA.
  It has its own parameters and per-section grip, and an optional seeded throttle jitter.
- `racekit.tracks.GRIP_SECTIONS = 6` and `grip_sections(track)`: the **public** section rule.
  It divides each lap into six equal arc-length sections from the start waypoint.
- Runner:
  - it calls `car.attach_track(track)` once per race when the car has it;
  - it adds the **spin-out major collision** (design §4.2), with the same respawn as the wall;
  - it adds `RaceResult.respawn_causes`.
- `roar/data/drivers.py`: **one** data-side pure-pursuit driver module.
  It is used by the generator and imported by the premise tests ([fable] S4), and is never student-facing.
- Telemetry generator (`roar/data/generate.py` step 2, `roar/data/gen_sysid.py`).
  It writes **sensor-observable** logs of the carla-like car.
  A driver records its own sensor observations and commanded actions every step, as a CARLA recorder would.
  The logs go to `generated/sysid/`, written by `racekit.telemetry.write_log_csv` and read by `read_log_csv`.
- Routed tests for all of it.
  The premise facts that roar-005 to roar-008 build on are pinned as tests.

## Probe evidence
The prototype lives in `scratchpad/u04/`: `dyn.py`, `truthcar.py`, `pp*.py` and `probe1–9.py`.
Every truth-car number below has μ **attached** per section.
All numbers are re-pinned on the shipped code.

- **The truth μ tables.** They are drawn with `random.Random`, seeded from sha256, uniform in [0.78, 1.05] and rounded to 3 decimals:

  | Track | Section μ |
  |---|---|
  | `oval` | [0.930, 1.001, 0.802, 0.975, 1.024, 0.880] |
  | `test-circuit` | [0.817, 1.002, 0.886, 0.816, 0.849, 0.838] |
  | `monza-like` | [0.836, 0.941, 0.951, 0.940, 0.996, 0.819] |
- **Unit 6 premise, on `DynamicCar()` defaults (μ = 1, no sections).**
  A pure-pursuit driver (lookahead max(6, 0.5·v) m) at a flat 20 m/s finishes `oval` (224.65 s).
  It fails both `test-circuit` (DNF, 16 collisions in 1500 s) and `monza-like` (DNF, 21 collisions) by running wide at the tight corners.
  With a **curvature-limited speed** it finishes all three clean: 217.65 / 413.70 / 873.00 s.
  The limit is v ≤ √(a_lat/κ) with a_lat = 0.7g, braking at 5 m/s² towards each cap within 120 m.
  On `KinematicCar` the flat agent is clean everywhere.
  The starter's own steering (gain 8/√v with δ_max = 70°) **spins** the dynamic car on `test-circuit`: one spin location at about 15 m/s, about 42 s into each restart, repeated after every respawn (34 times in 1500 s). It never completes a lap.
  Pure pursuit spins only at 60 m/s.
- **Unit 7 premise (late braking).**
  Pure pursuit with a 45 m/s cap and only 120 m of look-ahead braking fails `test-circuit` (18 collisions).
- **Unit 7 premise (per-section grip, noise-aware).**
  The setup is `carla_like` with throttle noise σ = 0.1, seeds 0–4, on `test-circuit`, with a 45 m/s cap and look-ahead braking over 300 m at 6 m/s².
  - **Global a_lat sweep on a 0.1 grid** ([sol] r2 B2):
    - 3.5: median 327.40 s (spread 0.30 s);
    - 3.6: median 325.05 s (spread 0.35 s);
    - **3.7: median 323.05 s (spread 0.40 s), the fastest clean global**;
    - 3.8: collisions on 1 of 5 seeds;
    - 3.9 and 4.0: DNF on every seed.
  - **One knob per section on top of global 3.5 (5 seeds each):**

    | Section (μ) | Clean up to | Median at that knob | Crashes at |
    |---|---|---|---|
    | 0 (0.817) | ×1.5 | 325.35 s | — |
    | 1 (1.002, the highest) | ×1.5 | 321.30 s | — |
    | 2 (0.886) | ×1.3 | 323.60 s | ×1.5 |
    | 3 (0.816) | ×1.15 | 324.95 s | ×1.3 |
    | 4 (0.849) | — | — | ×1.15 |
    | 5 (0.838) | ×1.15 | 325.25 s | ×1.3 |

    The knob a section accepts follows its μ, modulated by the section's corners.
  - **One knob per section on top of the best global 3.7:**
    - sections 0 and 1 are clean to ×1.35 (321.80 s and 318.70 s);
    - section 2 is clean to ×1.2 (320.60 s);
    - section 5 is clean at ×1.1 (321.80 s);
    - sections 3 (μ 0.816) and 4 (μ 0.849) crash already at ×1.1.
  - **Combined on 3.7:** [1.35, 1.35, 1.2, 1, 1, 1.1] is clean in 5/5 runs, median **313.50 s** (spread 0.45 s). That is **9.55 s faster than the best clean global**, about 20× either spread.
    The milder [1.2, 1.35, 1.2, 1, 1, 1] gives 315.35 s (spread 0.35 s).
  - **Stacking knobs that are each clean alone can crash:**
    - on 3.7, adding ×1.1 on section 3, which is clean alone at 3.5 but not at 3.7, gives [1.35, 1.35, 1.2, 1.1, 1, 1.1], with collisions on 1 of 5 seeds;
    - on 3.5, [1.5, 1.5, 1.3, 1.15, 1, 1.15] has collisions on 2 of 5 seeds.
    
    Knobs interact, which is a Unit 7 lesson.
  - (On global 3.5, [1.3, 1.5, 1.3, 1, 1, 1] gave 316.35 s, 11.05 s faster than 3.5 but measured against a non-optimal base.)
  - At μ = 1 (the v1 mistake) the same fixture runs clean at global 5.25. The grip is what binds.
- **Noise.**
  White **steer** jitter is unrealistic at speed: σ = 0.01 is about 0.7° of wheel angle per tick and crashes most runs at 45 m/s.
  Throttle-only jitter σ = 0.1 gives these spreads with every run clean:
  - `monza-like` at global 3.5: median 542.00 s, spread 0.25 s;
  - `test-circuit` at global 3.5: spread 0.30 s.
- **Unit 8 premise (identification from logs, attached).**
  - **Longitudinal fit.** One noisy `monza-like` race (a_lat 3.5, 10,840 rows) fitted to dv/dt = a_T·throttle − a_B·brake − c·v|v|, with the action lagged L ticks.
    - The residual is smallest at **L = 1**: RMS 0.436, against 0.569 at L = 0 and 0.537 at L = 2.
    - a_B = 8.56 (truth 8.6, −0.4%).
    - c = 3.15e-4 (truth 3.4e-4, −7%).
    - a_T = 5.17 (truth 5.4, −4.3%). The throttle jitter clipping and traction limits bias it low.
  - **Steering gain.** From a **steady oval log** at 10, 15 or 20 m/s, using rows where the lagged steer is steady (rolling σ < 0.002 over 10 ticks), atan(r·L/v) against the steer gives δ_max = 66.16° / 65.72° / 65.94° (truth 66°) from 186 to 1,051 rows.
    The same fit on race logs is unstable: 45° on `test-circuit` from 13 rows. The yaw rate lags fast steering, so the steady log is the one to use.
  - **Per-section μ is not yet identifiable from these logs.**
    Peak |a_y| per section gives 0.91–0.99 of μ·g, a correct lower bound, but only for the sections a driver actually pushes to the limit. Single-lap limit runs reached three of six.
    Designing the excitation that identifies every section's μ is **roar-008's** probe ([sol] B3, [fable] S1).
    roar-008 may extend `generate.py` step 2 (new logs, new driver settings). G4.7's checksums are byte-stability checks, not a frozen contract.
- **Friction circle.** Over a limit-probing `test-circuit` lap, the per-tick |a|/(μg) has p99 0.990 and max 0.999.
  v1's post-step low-speed projection gave non-physical spikes of 24× and 36×; the fix is below.
- **Cost.** About 0.30 ms per tick for `carla_like` with `track.nearest` included ([fable] measurement), against 0.15 ms for `KinematicCar`.

## Deviations from design (recorded)
- **The Unit 6 hook.**
  The design asks "Why does the car spin at Parabolica?".
  On this model the 20 m/s failure is **running wide at the tight corners** (the `test-circuit` hairpin and chicane, the Rettifilo).
  Spins come from aggressive steering (the starter's gain) or very high speed.
  The Parabolica (R = 140 m) is safe at 20 m/s.
  roar-006 reframes the hook from this evidence; this plan only records it.
- **The spin-out rule uses sideslip only** ([fable] S3).
  Design §4.2 says "|β| or |r| beyond a pinned threshold".
  A yaw-rate threshold cannot tell a legitimate full-lock turn at low speed (r ≈ 4.8 rad/s at 5 m/s) from a spin, and β can.
  The rule is |β| > 25° at a speed above 5 m/s.
  At 5–10 m/s and full lock the probe's max |β| is 18.8°, so the rule does not trip.
- **The noise is throttle-only** (see Probe evidence).
  Design §4.4 says "a seeded actuator jitter", and this satisfies it.
  `KinematicCar` keeps its two-channel jitter, because Unit 1's pins depend on it.
- **Grip sections are equal arc-length sixths**, a public rule.
  The design says "section-varying grip" without fixing the sections.
  Equal sections are reproducible on any generated track, seeded checkpoint tracks included.
- **A spin-out is a respawn although CARLA would not respawn a spin that touches no wall.**
  This is the design's approximation (most spins end in the wall), labelled in the runner docstring.

## Design of the dynamic car (`DynamicCar`, the public defaults)
- **State.**
  - x, y (the centre of gravity, ROAR frame), ψ, v_x and v_y (body frame), r (yaw rate), δ (the actual wheel angle), and the lag FIFO.
  - `v` is the signed speed ±‖(v_x, v_y)‖, with the sign of v_x.
  - `velocity()` is world-frame.
- **Parameters (defaults).**
  - mass 1845 kg, I_z 2900 kg·m², l_f 1.40 m, L 2.875 m;
  - δ_max 70°: steer s gives the target δ = −s·δ_max, as in `KinematicCar`;
  - steering rate 360°/s;
  - a_throttle 6, a_brake 8 and c_drag 4e-4, which is `KinematicCar`'s longitudinal map;
  - μ = 1.0, tyre B = 10 and C = 1.6;
  - lag 1 tick;
  - kinematic blend between **1 and 2 m/s**, where even full lock (R ≈ 1.05 m) needs at most v²/R ≈ 3.8 m/s², within μg;
  - spin-out at |β| > 25° with ‖v‖ > `SPIN_MIN_SPEED` = 5 m/s, a constant separate from the blend band ([fable] r2).
- **Forces.**
  - Static axle loads. There is no load transfer, a labelled model limit.
  - The longitudinal force is m·(drive − brake against the motion − drag), split between the axles in proportion to load: an **all-wheel-drive model choice**, labelled ([self] N2). Each axle's force is clipped to ±μF_z.
  - Lateral: F_y = −√((μF_z)² − F_x²) · sin(C·atan(B·α)), with α_f = atan2(v_y + l_f·r, u) − δ, α_r = atan2(v_y − l_r·r, u) and u = max(|v_x|, 3 m/s).
  - Reversing at speed is not modelled: the slip-angle sign assumes forward motion ([self] N1). The runner's agents never reverse; the kinematic blend covers manoeuvres below 3 m/s.
- **Low speed** ([fable] r1 B2, [sol] r2 B1).
  - Below 2 m/s the **derivatives** blend towards a kinematic bicycle whose **acceleration vector is capped at μg**, with weight w = clip((|v_x| − 1)/(2 − 1), 0, 1).
  - The kinematic lateral acceleration is a_y,k = v_x·r_k + clip((l_r·r_k − v_y)/0.1 s, ±μg), itself clipped to ±μg, with r_k = v_x·tan δ / L.
  - The longitudinal part is a_x,k = the longitudinal map, clipped to ±√((μg)² − a_y,k²). The friction circle binds at low speed too, so neither the drive nor the brake exceeds the grip that turning leaves.
  - The blended derivatives are:
    - dv_x → a_x,k + v_y·r;
    - dv_y → a_y,k − v_x·r;
    - dr → (r_k − r)/0.1 s.
  - No state is projected after a step; projection was the source of v1's non-physical spikes.
  - **Measured:**
    - over μ ∈ {0.78, 1}, v₀ ∈ {0 … 5} m/s and 7 throttle, brake and steer combinations, the worst per-tick |a|/(μg) is **1.000**;
    - from rest under throttle 0.3 at steer 0, 0.5 and 1, v_x never goes negative and is non-decreasing while below 1 m/s.
  - **Spin rule against legitimate turns** (frozen prototype, defaults and truth parameters): full lock at throttle 0.3 from 5, 6, 8 and 10 m/s peaks at |β| = 4.5–11.7°, with no trip.
    The true spins trip:
    - 40 m/s full lock with full brake (|β| 27–34°);
    - full throttle at full lock from rest, power oversteer (40–68°);
    - the starter's whip on `test-circuit`.
    A held full lock or a half-lock L/R/L at 40 m/s understeers (|β| ≤ 11°) and does not trip ([fable] r2 S1).
- **Integration.** RK4 per substep (10 per tick). The steering moves towards its target at the rate limit once per substep, before the stages.
- **Brake stop** ([sol] B1, [fable] N1). The car stops (v_x = v_y = r = 0) when, at the start of a substep, all three hold:
  - the brake is on;
  - the brake is at least the drive (braking ≥ |drive|, [fable] r2 N2);
  - ‖v‖ ≤ (braking − drive·sign(v_x) + c·v_x²)·h, which is the direction-aware net deceleration.
  Under braking, a sign change of v_x also clamps to 0, but only below 0.5 m/s, so a spinning car's v_x may cross zero.
  This is deliberately unlike `KinematicCar`, whose RK4 substeps creep (see Out of scope).
- **Section grip.** `mu` takes a scalar, or a length-6 sequence applied per grip section.
  A per-section μ requires `attach_track(track)`.
  The car locates its section with `track.nearest` and a carried hint, which resets on `reset()`. μ is read once per tick, at the start of `advance`.
  A per-section car that is raced without a track raises a clear error rather than silently using μ = 1 (the v1 probe bug, now impossible).
- **Noise.** `jitter` (throttle) and `steer_jitter` are separate, both drawn from `random.Random(seed)`; `seed()` behaves as in `KinematicCar`.

## The carla-like car
- `racekit/_truth.py` holds its parameters. Its module docstring says "do not read this in teaching material".
- **Parameters that Unit 8 identifies differ from `DynamicCar`'s defaults** ([sol] S, [fable] N4):

  | Parameter | `DynamicCar` default | `_truth` | Difference |
  |---|---|---|---|
  | δ_max | 70° | 66° | 5.7% |
  | a_throttle | 6 | 5.4 | 10% |
  | a_brake | 8 | 8.6 | 7.5% |
  | c_drag | 4e-4 | 3.4e-4 | 15% |

  μ is per section, in [0.78, 1.05] against 1.0.
- **Intentionally shared:** mass 1845, L 2.875 and lag 1. Unit 8 *finds* the lag rather than recovering a changed one.
- **Other differences, not identification targets:** I_z 3100, l_f 1.45, tyre B 9 and C 1.45.
- **The μ table** is `random.Random(int(sha256("racekit-grip:" + name)[:16], 16))`, uniform in [0.78, 1.05], rounded to 3 decimals ([fable] S2). The three named tracks' tables are also **hard-pinned in a test**.
- `carla_like(noise=False)` returns a configured `DynamicCar`. With `noise=True` it adds throttle jitter `_truth.NOISE_SIGMA` (0.1 from the probe, confirmed in Phase A against G4.4).
- **The `_truth` rule.**
  - A routed test fails if the string `_truth` appears in any student-facing source: `roar/units/`, `roar/checkpoints/`, `roar/projects/` notebooks and agents, `roar/labs/`, `roar/docs/`, `roar/reference/` and `roar/syllabus.md` ([sol] S).
  - It excludes `roar/projects/racekit/racekit/` (where `cars.py` imports it) and the racekit tests.
  - The object `carla_like()` returns exposes its parameters as attributes, so introspection (`carla_like().a_brake`) is a **reviewer-enforced** rule in the content gates ([fable] N3).

## Gates (pinned from the probes; a miss means stop, amend and re-gate)
All are routed tests under `roar/projects/racekit/tests/`, plus the existing suite.

### G4.1, analytic car checks (design §7.1)
- **Circle radius:** at 8 m/s with steer 0.02, the steady radius is within 3% of L/tan δ ([fable] measured 0.1%).
- **Friction circle** (a regression guard, true by construction, [fable] N2): in a seeded random-action fuzz of 500 cases, every substep has √(F_x² + F_y²) ≤ μF_z + 1e-9 per axle. In addition, the per-tick |a|/(μg) stays ≤ 1.02 over a limit lap.
- **Integrator order** ([sol] S, [fable] N2): halving the substep size shrinks the end-state error of a 2 s smooth manoeuvre at 15 m/s by a ratio ≥ 12 (RK4), checked over two halvings. The wheel angle starts at its target, so the piecewise-constant steering update does not limit the order, and no tyre is saturated.
- **Longitudinal:** a straight full-throttle run below the traction limit matches the map to 1e-3 m/s over 2 s.
- **Brake stop:**
  - from every v₀ in {0.005, 0.01, 0.03, 0.2, 1, 5} m/s, 1 s of full brake leaves v == 0.0 and never reverses;
  - with full throttle **and** full brake from 0.05 m/s, the car takes at least 3 substeps to stop, so it is not an early snap ([sol] B1);
  - with throttle 0.75 and full brake from 5 m/s, the car reaches v == 0.0 within 2 s.
- **Low speed:**
  - **Friction bound:** over μ ∈ {0.78, 1}, v₀ ∈ {0, 0.5, 1, 1.5, 2, 3, 5} m/s and the action set {(1, 1, 0), (1, 0.5, 0), (0.3, 1, 0), (0, 1, 1), (0, 0, 1), (0, 0.5, 1), (0.5, −1, 0.3)} for 3 s each, every tick has |Δv|/(0.05·μg) ≤ 1.02 (probe 1.000).
  - From rest under throttle 0.3 at steer ∈ {0, 0.5, 1}, for 4 s:
    - v_x ≥ 0 throughout;
    - v_x is non-decreasing while |v_x| < 1 m/s;
    - `spun_out()` never trips.

    Above the blend band, v_x is a body-frame component, and v_y·r coupling may legitimately move it ([fable] r2 N3).
  - While |v_x| < 1 m/s and after 0.5 s, |v_y − l_r·v_x·tan δ / L| ≤ 0.1 m/s at half lock and ≤ 0.4 m/s at full lock (probe 0.062 and 0.308).
    That bound is the relaxation lag, an absolute bound: at walking pace a small lag is a large angle.
- **Lag:** with `lag_ticks = k`, a throttle step first changes v_x on tick k + 1.
- **Steering rate:** the rate limit is respected.
- **Spin-out:**
  - 40 m/s with full lock and full brake for 1 s triggers `spun_out()` (probe |β| 27.3°, truth car 34°);
  - full throttle at full lock from rest for 4 s triggers it (power oversteer);
  - a steady 15 m/s, 0.3g circle never does;
  - full lock at throttle 0.3 from 5, 6, 8 and 10 m/s for 4 s never does (max |β| 11.7°);
  - the tests call the car's own `spun_out()`, never a re-implementation of the threshold.
- **Grip:** a per-section `DynamicCar` raced without `attach_track` raises.

### G4.2, the runner
- A spin-out triggers the same respawn as the wall: start pose, 20-tick hold, progress reset to 0, `respawn_causes == ["spin"]`.
- If the wall and a spin coincide in one tick, the cause is `"wall"`.
- A spin reports `CRASH_IMPULSE` on the collision sensor, as the wall does ([fable] N5).
- `attach_track` is called once per race.
- `KinematicCar` races are unchanged: the existing Unit 1–3 pins (223.50 / 412.75 / 882.55 s and Unit 1's per-seed times) still pass, and the default car is still `KinematicCar`.

### G4.3, the Unit 6 premise
These use `drivers.py` on `DynamicCar()` defaults.
- At a flat 20 m/s the driver fails `test-circuit` with at least 5 collisions within a 600 s cap.
- With the curvature-limited speed (0.7g) it finishes `test-circuit` with 0 collisions and 0 spins.
- On `KinematicCar` the flat 20 m/s driver finishes `test-circuit` cleanly.

### G4.4, noise
- `carla_like(noise=True)` with `drivers.py` at global a_lat 3.5 and a 45 m/s cap, on `monza-like`, seeds 0–4: all 5 runs clean, with a spread in **[0.15, 0.6] s** (probe 0.25 s = 5 ticks; the band is 3–12 ticks, so a last-bit difference from the unrolled RK4 cannot fail it, [fable] r2 N1).
- `noise=False` is exactly deterministic, and the same seed gives identical times.

### G4.5, the Unit 7 premise
On `carla_like(noise=True)` on `test-circuit`, seeds 0–4, with a 45 m/s cap and look-ahead braking over 300 m at 6 m/s²:
- global a_lat **3.7** is clean in 5/5 runs, and global 3.8 is not: 3.7 is the fastest clean global on the 0.1 grid;
- section grip **[1.35, 1.35, 1.2, 1, 1, 1.1]** on top of 3.7 is clean in 5/5 runs;
- **noise-aware:** its median beats global 3.7 by more than both spreads **and** by at least **5 s** (probe: 9.55 s);
- the stacked vector [1.35, 1.35, 1.2, 1.1, 1, 1.1] on 3.7 is **not** clean on all 5 seeds (the interaction premise).

A miss on the shipped code means stop, amend and re-gate, never a silent re-pin.

### G4.6, the Unit 8 premise (on the generated logs)
On `monza-like-seed0` (race):
- lagged least squares has its residual minimum at lag 1;
- a_B is within 5%, c within 10% and a_T within 10%.

On `oval-steady-seed0`:
- the steady-row fit gives δ_max within 3% of 66°.

Per-section μ, a consistency check only:
- The estimator is the probe's. Per respawn-free segment, drop the first and last 10 rows and keep rows with body speed > 5 m/s.
- Take the 98th percentile of |a_y| from central differences of the world velocity, projected on the body y axis.
- On the race log that value is ≤ 1.02·μ·g in every section that has at least 20 such rows ([fable] r2 S3).

**This plan does not establish the Unit 8 per-section μ identification premise** ([sol] r2 B3).
That premise (design §6 Unit 8, "per-section μ from data") is roar-008's to probe and gate, with a designed excitation.
If roar-008 finds it infeasible, roar-008 amends the design.

### G4.7, the generator
- `generate.py` step 2 writes `generated/sysid/monza-like-seed0.csv` (a noisy race at global 3.5) and `generated/sysid/oval-steady-seed0.csv` (a noisy steady 15 m/s oval lap), via `drivers.py`.
- Both are byte-stable under the existing checksum contract.
- The log reader round-trips.
- Total generation (tracks, logs and lab sample) is **≤ 1 min** (design §7.1).

### G4.8, cost
- The median `carla_like` cost per tick, `track.nearest` included, is **≤ 0.6 ms** on the CI machine, measured and recorded.
- The routed pytest stays within its 5-min budget, measured.

### G4.9, Python 3.8
- The new modules pass the AST deny-list test and use `from __future__ import annotations`.
- The isolated 3.8 run gains a **smoke race** through `carla_like(noise=True)` on `oval` for 1 lap. It exercises `DynamicCar`, `_truth`, the section grip, `attach_track` and the spin-out check ([sol] S).

## Phases
### Phase A: `racekit` cars and runner (Opus subagent, tooling)
- `cars.py`: `DynamicCar` and `carla_like`.
- `_truth.py`.
- `tracks.py`: `GRIP_SECTIONS` and `grip_sections`.
- `runner.py`: `attach_track`, spin-out and `respawn_causes`. The "Known differences" docstring gains the spin-out approximation and the spin-without-wall caveat.
- `KinematicCar`'s docstring gains the brake-creep note ([fable] point 5).
- Tests for G4.1, G4.2, G4.4 and G4.9.
- `_truth.NOISE_SIGMA` is confirmed against G4.4.

The prototype `scratchpad/u04/dyn.py` is the reference for the physics. The implementation unrolls its RK4 stage tuples for speed ([fable] note).

### Phase B: the driver and the telemetry generator (Opus subagent, tooling)
- `roar/data/drivers.py`: one pure-pursuit driver class. It takes the cap, a_lat, section grips, look-ahead braking and recording on or off, and records sensor rows when recording is on.
- `roar/data/gen_sysid.py`.
- `generate.py` step 2 and its docstring.
- `racekit.telemetry`: `LOG_COLUMNS = (t, x, y, yaw, vx, vy, throttle, steer, brake)` with `write_log_csv` / `read_log_csv`, following the v1 CSV conventions with a meta header (track, seed, noise, kind).
- Tests for G4.7.

### Phase C: the premise tests (Opus subagent, tooling)
- Tests for G4.3, G4.5 and G4.6, importing `drivers.py`.
- The `_truth` scan test.
- The hard-pinned μ tables.

### Phase D: verification (named)
- `uv run --group roar pytest -q roar/projects/racekit/tests roar/tests`, timed.
- `PYTHONHASHSEED=0 uv run --group roar python roar/data/generate.py`, timed.
- `py4kids-tools --book roar`: all checks.
- `TMPDIR=/dev/shm bash scripts/ci-local.sh`: ALL GREEN.
- The 3-way content gate, which for this plan reviews the code, the physics and the pinned premises.

## Out of scope
- **No unit content** (no lessons, exercises, milestones or teacher notes).
  This is a tooling-only plan.
  The content laws are exercised from roar-005 onward; the verification phase above is the named verification.
- **`KinematicCar`'s brake creep** (the roar-003 follow-up).
  - It stays unchanged, documented in the car's docstring.
  - Changing it would change Unit 3's taught parity: `agents/unit-03.py`'s `stopping_tick`, the Unit 3 milestone and lesson §8. That is errata scope.
  - No race brakes to rest, so no race time is affected.
  - `DynamicCar` stops exactly.
  - roar-006's Unit 6 lesson labels the difference where the two cars are compared.
  - The follow-up is listed for the user.
- **Per-section μ identification** (excitation design): roar-008.
- **Model limits, labelled:** load transfer, gears, power limits, tyre temperature and reversing at speed.
- `racekit.sysid_data` and the analysis helpers, which enter with Unit 8 (roar-008, design §5).
- Any change to `KinematicCar`'s behaviour, to the telemetry v1 format or to the lab-check format.

## Plan Review

### Round 1 (v1 @ 298feb5)
- [self] APPROVE WITH NITS.
  - N1 [FIXED]: reverse slip-angle sign, now stated as a model limit.
  - N2 [FIXED]: the load-split drive is all-wheel drive, now labelled.
- [sol] REJECT.
  - **B1** [FIXED] The brake-stop threshold was not direction-aware, so the stop rule snapped a car with opposing throttle to rest early. It now uses the net deceleration, and a G4.1 case covers throttle plus brake.
  - **B2** [FIXED] The Unit 7 advantage had not been probed as a combined, noise-aware comparison. Both are now probed (5 seeds, combined vector) and pinned in G4.5 with no silent re-pin.
  - **B3** [FIXED] G4.6 covered only the longitudinal fit. Added: lag, steering gain from a steady log (probed at 66 ± 0.3°), and a μ lower bound. Per-section μ identification is explicitly roar-008's.
  - **S** [FIXED] The parameter-separation claim was wrong; the table now lists which parameters differ and which are shared.
  - **S** [FIXED] The isolated 3.8 run did not exercise the new car; it gains a smoke race.
  - **S** [FIXED] Added the integrator-order check, and widened the `_truth` scan to all student-facing sources.
- [fable] REJECT.
  - **B1** [FIXED] The v1 truth-car probes ran at μ = 1.0 because nothing called `attach_track`. All probes were re-run attached and every pin was rewritten: global 3.5, not 5.5; the combined grip vector; the noise band; the fits. The car now raises if a per-section car is raced without a track.
  - **B2** [FIXED] A steered car from rest drove backwards. The low-speed blend now acts on the derivatives (v_x, v_y and r), with gates for monotone v_x ≥ 0 from rest, kinematic β and no spin trip at full lock from 5 to 10 m/s. The same fix removed the friction-bound spikes.
  - **S1** [FIXED] μ identification was not probed. Recorded as a lower bound now, with excitation in roar-008 and a note that generator checksums are not a frozen contract.
  - **S2** [FIXED] μ now comes from `random.Random`, and the named tables are hard-pinned.
  - **S3** [FIXED] The β-only spin rule is recorded as a deviation, with the reason.
  - **S4** [FIXED] There is now one `drivers.py` shared by the generator and the tests.
  - **N1** [FIXED] Net-deceleration stop threshold.
  - **N2** [FIXED] Friction-circle fuzz labelled a regression guard; convergence check added.
  - **N3** [FIXED] Introspection is reviewer-enforced, and the scan exclusions are stated.
  - **N4** [FIXED] Mass dropped from the "differs" list.
  - **N5** [FIXED] Spin impulse and precedence specified.
  - **N6** noted.

### Round 2 (v2 @ f31a0f3)
- [self] APPROVE (spot-checked the convergence order: ratios 16.5, 16.2 and 16.1 per halving).
- [sol] REJECT:
  - **B1** [FIXED] The low-speed blend broke μg in combined turning with throttle or brake (1.30 μg and 1.12 μg). The blend band is now 1–2 m/s, where the kinematic path is feasible, and the kinematic acceleration vector is capped at μg. The probe's worst case is 1.000, gated in G4.1 over the same cases.
  - **B2** [FIXED] The comparison was not against the best clean global. A 0.1-grid sweep finds 3.7 (323.05 s). The per-section sweep and the combined vector were redone on 3.7 (313.50 s, 9.55 s faster), and G4.5 is re-pinned.
  - **B3** [FIXED] The Unit 8 μ premise is now stated explicitly as not established here and assigned to roar-008, with the lower-bound check kept as a consistency gate.
  - **S** [FIXED] The monotonicity gate is restricted to |v_x| < 1 m/s.
- [fable] REJECT:
  - **B1** [FIXED] The low-speed gates did not match the prototype.
    - The prototype is frozen (md5 recorded), and the low-speed section and gates were rewritten to match it.
    - `SPIN_MIN_SPEED` is separate from the blend band. [fable]'s 5–8 m/s trips came from a gate script that used `v_hi` (now 2 m/s) as the speed threshold; the car's own `spun_out()` peaks at |β| 11.7° there.
    - An "excess over kinematic β" rule was tried and rejected, because it trips on a legitimately understeering full lock.
    - All probes through the low-speed regime were re-run on the frozen prototype: the Unit 6 races (unchanged: 16 and 21 collisions, and clean when limited), the starter spins, the stacked vectors and the friction lap (max 0.992).
  - **S1** [FIXED] The spin scripts are now spelled out.
  - **S2** [FIXED] The starter's spins are one repeated event.
  - **S3** [FIXED] The μ estimator is pinned.
  - **N1** [FIXED] The spread band is stated in ticks.
  - **N2** [FIXED] The stop condition reads braking ≥ |drive|.
  - **N3** [FIXED] The monotonicity is restricted to the blend band.
