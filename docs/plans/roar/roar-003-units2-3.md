# Plan roar-003 — Units 2–3: the geometry of a track, and modelling the car

**Design:** `docs/designs/013-roar-book.md` **v4.1** (§4.4 item 1, §5, §6 Units 2–3).
**Book:** `roar`. **Autopilot** per AGENTS.md.
**Base:** branches from `main` after `roar-002` merges.
**v2.1** folds round 2 ([sol] B: G3.4 checks the full state). **v2** folds plan-review round 1 ([sol] REJECT: B `polyfit`, S G2.4 tolerances, N sample count; [fable] APPROVE WITH NITS: M1 the Euler circle, M2 `polyfit`, S1–S5, N1–N8).

## Scope
- Unit 2 `roar/units/unit-02-track-geometry/` and Unit 3 `roar/units/unit-03-modelling-the-car/`: lesson, exercises,
  solutions, teacher notes, manifest. Neither unit has a lab (no 🏁 in design §6).
- Reference submissions `agents/unit-02.py` and `agents/unit-03.py`, and milestones
  `milestones/unit-02-track-geometry.ipynb` and `milestones/unit-03-modelling-the-car.ipynb`.
- A ride-along carried from the `roar-002` content gate: [fable] N1/N2 on the Unit 1 lab (prose and print fixes).
- No new `racekit` module. Both units' techniques are **student code in the submission** (design §5).

## Deviations from design (recorded, with probe evidence)
- **The Unit 2 hook is reframed.**
  The design's hook, "Why does the baseline cut corners and wobble?", is **false on racekit's kinematic car**.
  The probe (`scratchpad/probe003.py`, jitter 0) shows the starter neither wobbles nor cuts:
  - steer sign flips are ≤ 0.08 per second at every speed from 20 to 35 m/s on all three tracks;
  - max |offset| is 0.07–0.12 m on `oval`, 0.51–0.85 m on `test-circuit` and 0.37–0.63 m on `monza-like`;
  - every one of those races is clean.
  Wobble and corner-cutting are grip phenomena, which arrive with the dynamic car in Unit 6.
  The honest hook is: **"The starter steers at a point three waypoints ahead and never looks further. Where exactly
  is the car relative to the track, and what is coming?"**
  Unit 2 builds the instruments (frames, heading, wrapping, projection, cross-track error, curvature) and uses them
  to *measure* the starter. The measurement is a pinned `STEER_GAIN` sweep showing the car running wide and then
  crashing as the gain falls.
- **Units 2–3 do not change the driving.**
  A windowed nearest-waypoint search with the same 3-waypoint lookahead drives *worse* at low gain
  (`probe003b.py`: `test-circuit` at gain 2.0 fails with 32 collisions, where the starter's reached-radius search
  finishes). Its target is nearer, so the controller is effectively retuned. [superseded: the target is *farther*; see Implementation deviations]
  `agents/unit-02.py` therefore keeps the starter's control law. It adds the geometry functions and computes the
  cross-track error and the curvature ahead each tick (stored on `self`, unused for control). `agents/unit-03.py`
  adds the model and a `predict()` rollout. The windowed-search result is taught honestly in Unit 2: a sharper
  instrument is not a better controller, and Unit 4/5 build controllers that use it.

## Implementation deviations (measured while building)
- **The windowed-search explanation was backwards.** The plan said the windowed target is *nearer*. On the gain-8
  `test-circuit` telemetry the reached-radius index sits 1.99 m *behind* the car (target 4.00 m ahead), while the
  windowed-nearest index sits at the car (target 6.00 m ahead): the windowed target is *farther*, which weakens the
  correction per metre of offset, so windowed gain 2 behaves like starter gain ≈ 1.3. The lesson teaches and asserts
  the corrected explanation (windowed: gain 8 412.70 s / 0.40 m; gain 4 413.75 s / 1.93 m; gain 2 DNF, 8 crashes in a
  450 s cap, which the lesson uses instead of 1500 s for its time budget).
- **"3 clamped rows" (G2.2) is qualified:** the naive version differs by more than 1e-9 on exactly 3 rows, all
  clamped (1.05e-6, 6.9e-7 and 4.875e-4 m); only 2 exceed 1e-6. The lesson asserts the > 1e-9 form.
- `monza-like` runs clockwise (total turning −2π; 65% of corner rows are right-handers); the lesson says so.
- `predict` is added to the closed callable list, taught under `numerical-integration` (it is called on the loaded
  submission in the Unit 3 lesson and milestone).
- The Unit 3 text numbers MPC as Unit 10 (the design §6 table), correcting a stray "Unit 9".

## Buildout stays
The whole-book lesson total becomes 3 + 3 + 3 = 9, under 30.

## Concepts (7 new; all `kind: technique`, globally unique)
- Unit 2 (`unit-02-track-geometry`), requires Unit 1's four concepts:
  - `frames-and-heading`: world and car frames, the rotation into the car frame, `atan2` heading, and angle wrapping
    to [−π, π);
  - `waypoint-projection`: projecting a point onto a polyline segment, and windowed nearest-waypoint search with a
    cyclic index;
  - `cross-track-error`: the signed lateral offset (left positive), with the track half-width as the constraint;
  - `menger-curvature`: the curvature from three points (4·area / product of the sides), signed; radius = 1/κ.
- Unit 3 (`unit-03-modelling-the-car`), requires Units 1–2:
  - `kinematic-bicycle`: the state (x, y, ψ, v); the steer → wheel angle δ = −steer·δ_max; yaw rate v·tan δ / L;
    the steady-state circle R = L / tan δ;
  - `longitudinal-map`: throttle → acceleration, brake against the motion, quadratic drag; the terminal speed;
  - `numerical-integration`: explicit Euler vs RK4 over a tick with the action held, the local and global error
    orders, and timestep error.
- `practices:` each unit practises the earlier units' measurement concepts (`race-telemetry`,
  `repeated-run-measurement`, `telemetry-plotting`), and Unit 3 also practises Unit 2's concepts.
- The model parameters are **the kinematic car's** (`KinematicCar` defaults: L = 2.875 m, δ_max = 70°, a_throttle 6,
  a_brake 8, c_drag 4e-4). These are a *model*, not the truth: Unit 8 re-identifies them from data. That is said in
  both units.

## Gates (pinned from the probes; a miss means stop, amend and re-gate)
**Unit 2** (`probe003.py`, `probe003b.py`; jitter 0):
- **G2.1, functions vs analytic circles:**
  - Menger curvature of three points on a circle of radius R equals 1/R to 1e-9, with the sign matching the turn
    direction;
  - for a **counter-clockwise** circle polyline (left positive), the cross-track error of a point at radius r
    from the centre equals R − r within the chord sagitta bound R(1 − cos(Δθ/2)); a clockwise test flips the sign
    ([fable] N4);
  - `wrap_angle` maps ±π, ±3π and 0 correctly and is idempotent;
  - the `atan2` heading of a chord equals the analytic tangent at the chord's **midpoint** angle, to 1e-12
    ([fable] N3);
  - **Menger vs the generator** ([fable] S5): the signed Menger curvature of consecutive waypoint triples matches
    `track.curvature` with max |diff| < 1e-3 on all three tracks (measured 6.9e-5 / 9.2e-4 / 6.9e-4). Left turns
    are positive, and R_min is 120.00 / 18.00 / 25.00 m (oval / test-circuit / monza-like).
- **G2.2, instrument equivalence** ([fable] S2): the student's cross-track error, computed from telemetry `x, y`,
  equals racekit's `offset` column within 1e-6 on every row of the deterministic `monza-like` race. The lesson pins
  the formula so this is achievable:
  - per segment i → i+1, the foot parameter t = ((p − a)·d)/|d|² is **clamped to [0, 1] for selecting** the
    segment (the smallest clamped-foot distance wins, with ties going to the first k by strict `<`);
  - the offset is the scalar cross product (dx·e_y − dy·e_x)/|d|, with e = p − a. That is the signed distance to
    the segment's line, left positive;
  - the window is segments hint − 8 … hint + 8 (cyclic), with `hint` carried as the chosen segment index and
    starting at 0.
  racekit writes e = p − foot. That is the same value, because the cross product is invariant to shifts along d, and the lesson says so ([fable] r2 N2). A naive sign × foot-distance differs on 3 clamped rows (max 4.9e-4 m); the lesson shows this as the reason the
  formula matters.
- **G2.3, the reference submission:** `agents/unit-02.py` races exactly like the starter: oval 223.50 s,
  test-circuit 412.75 s, monza-like 882.55 s, all clean, at jitter 0. `check_submission(...).ok` holds, and so does
  the isolated 3.8 test (parametrized over `agents/*.py`).
- **G2.4, the `STEER_GAIN` sweep** (`test-circuit`, 20 m/s, jitter 0):

  | gain | outcome | max \|offset\| |
  |---|---|---|
  | 8 | finishes 412.75 s, clean | 0.51 m |
  | 4 | finishes 413.55 s, clean | 1.76 m |
  | 2 | finishes 415.35 s, clean | 4.40 m |
  | 1 | does **not** finish in 1500 s (16 collisions) | 5.64 m |

  On `monza-like` the same sweep gives 0.37 / 1.27 / 3.63 m, and gain 1 does not finish (22 collisions).
  The lesson asserts the `test-circuit` table and relates the offset peaks to the curvature peaks.
  **Tolerances** ([sol] S): times are exact (to 1e-9, tick-quantized); max |offset| is within ±0.005 m of the
  table; gains 8, 4 and 2 give `finished` and 0 collisions; gain 1 gives `finished == False` and exactly 16
  collisions at `max_seconds=1500`. The gain-1 DNF runs once per notebook at most ([fable] N7).
- **G2.5, the cross-track scorecard** ([fable] S1): the starter's numbers that Units 4–5 are scored against, at
  `TARGET_SPEED` 20.
  - Jitter 0, max / RMS |offset|: oval 0.07 / 0.050, test-circuit 0.51 / 0.088, monza-like 0.37 / 0.056 m.
  - Jitter 0.05, seeds 0–4 (`probe003e.py`), median and range:

    | track | max \|offset\| | RMS \|offset\| |
    |---|---|---|
    | oval | 0.499 (range 0.164) | 0.1397 (range 0.0099) |
    | test-circuit | 0.689 (range 0.132) | 0.1586 (range 0.0055) |
    | monza-like | 0.611 (range 0.106) | 0.1416 (range 0.0040) |

  They are computed on `held == 0` rows, as the probe does (none are held today), and asserted in the Unit 2 milestone to ±0.001 for max and ±0.0005 for RMS ([fable] r2 N3, N4).
  The RMS is the steadier statistic, so Units 4–5 are scored on it. Jitter shows here too: a noisy car sits further
  off the line.

**Unit 3** (`probe003c.py`):
- **G3.1, the circle radius** ([fable] M1): hold steer s at the drag-balancing throttle with v = 10 m/s for 2000
  steps of h = 0.05.
  - The RK4 rollout stays on R = L / tan(s·δ_max) within 1e-6 m (measured 2.8e-8).
  - Euler's trajectory is an exact regular polygon (side h·v, exterior angle h·v·κ). Its distance from the true
    centre differs from R by about **h·v/2 = 0.25 m, bounded and independent of R**: the same in the first and the
    last 200 steps, so it does **not** grow.
  - The polygon's circumradius exceeds R by only about R·(hv/2R)²/6.
  - It is taught as "first-order error = a half-step lag of the whole circle", and halving h halves the shift.
  - The pinned R values are 47.006 m (s = 0.05), 23.415 m (s = 0.1) and 11.531 m (s = 0.2). The Euler shift is
    asserted as **max |dist − R| over each 200-step window** in [0.245, 0.255] for each R, and equal (±1e-3) in the first and last windows. The signed deviation oscillates between ±hv/2 once per lap, so never assert the mean or the signed value ([fable] r2 N1).
- **G3.2, prediction from telemetry:** replay the recorded actions over 1 s (20 ticks) from **180 start rows**
  (rows 200, 297, … at stride 97) of the deterministic `monza-like` race ([sol] N, [fable] N1):
  - RK4 at one step per tick reproduces racekit's position within 1e-6 m (measured 1.7e-8). racekit is RK4 with
    the action held, in 10 substeps of 0.005 s; one 0.05 s step agrees to about 1.7e-8, and ten substeps to
    about 1e-13 ([fable] N2);
  - Euler at one step per tick has a max error of about 0.378 m, and Euler at 10 substeps about 0.038 m.
  The tenfold drop is **first-order convergence**, which the lesson names.
  Euler's *median* error is tiny (about 2e-6 m) because on the straights the car sits at its 19.49 m/s drag
  equilibrium. That links back to Unit 1.
- **G3.3, convergence order** (`probe003d.py`): the case is throttle 0.6, steer 0.15, v₀ = 5 m/s, T = 4 s, against
  a reference RK4 at h = 1e-4. Over h = 0.4, 0.2, 0.1 and 0.05:
  - the Euler position errors are 8.25, 4.18, 2.10 and 1.05 m, ratios about 1.97–1.99;
  - the RK4 errors are 3.1e-4, 1.9e-5, 1.2e-6 and 7.5e-8 m, ratios about 16.0–16.1.
  The asserts allow ratios in [1.8, 2.2] for Euler and [14, 18] for RK4.
- **G3.4, the reference submission** ([fable] S4): `agents/unit-03.py` races exactly like the starter, with the
  same pins as G2.3.
  - Its `predict(state, actions, dt=0.05)` takes the state (x, y, ψ, v) and a sequence of (throttle, steer, brake)
    actions, applies one RK4 step per action and returns the final state.
  - Checked in the milestone on the recorded 20-action sequences of G3.2, **all four components** are compared
    ([sol] r2 B, `probe003f.py`):
    - x and y within 1e-6 m (measured 1.3e-8);
    - ψ within 1e-9 rad, compared wrapped (measured 1.7e-14);
    - v within 1e-9 m/s (measured 4.3e-14).
  - A held-current-action prediction is shown in the lesson only, with its error *measured, not gated*.

## Phases

### Phase 0: the ride-along (inline)
- Unit 1 lab, [fable] N1: on CARLA the hold rows (and the first row after them) carry the crash pose. Update the lab
  prose and the `telemetry.py` module docstring to say so.
- Unit 1 lab, [fable] N2: exclude `held == 1` rows from the "min after the first 10 s" print.
- Re-run `lab-check`.

### Phase A: registry
- `concepts.yaml` gets the 7 ids. `coverage-map.yaml` gets the Unit 2 and Unit 3 entries (`lessons: 3` each). The
  manifests mirror the entries.
- `library_methods` and `api-order` are extended with the closed list the notebooks use. At least: `atan2`, `cos`,
  `sin`, `tan`, `hypot`, `radians`, `degrees`, `linspace`, `cumsum`, `arange`, `dot`, `norm`, `percentile`, `log2`,
  `loglog`, `semilogy`, `set_xscale`, `set_yscale`, `fill_between`.
  - **No `polyfit`** ([sol] B, [fable] M2): design §7.1 reserves it for Unit 8's least squares. The orders are
    `log2(e_h / e_{h/2})` ratios.
  - **No `np.cross`** ([fable] S3): it raises on 2-vectors in numpy 2.x. The scalar dx·e_y − dy·e_x is taught; a 3.8
    submission needs it anyway.
  - The plotting names map to `telemetry-plotting` and are listed in the Unit 3 manifest's `practices`
    ([fable] N8).
  Map them to infrastructure (assumed numpy, trigonometry and math names) or to `telemetry-plotting`. No taught
  callable precedes its unit.
- The `syllabus.md` rows for Units 2–3, including the reframed Unit 2 question.
- A one-line design 013 **v4.2** amendment of the §6 Unit 2 hook (to the reframed question, citing the probe), so
  the design and the syllabus agree ([fable] N6).

### Phase B: Unit 2 content (Opus subagents: lesson + exercise statements; solutions in a separate fresh session)
- **Lesson:**
  1. The hook.
  2. Frames, and the heading from `atan2`.
  3. Wrapping, with the `wrap_angle` edge cases.
  4. Projection onto a segment, then onto a polyline with a cyclic window.
  5. The cross-track error, checked against racekit's `offset` (G2.2).
  6. Menger curvature, checked on a circle (G2.1), and the curvature profile of `monza-like` (R_min 25 m) and
     `test-circuit` (R_min 18 m).
  7. Measuring the starter: the offset vs the curvature, and the `STEER_GAIN` sweep (G2.4).
  8. The windowed-search experiment: a better instrument is not a better controller.
  9. The bridge to Unit 3.
- **Exercises:** at least 6 `## Exercise N` and at least 2 stretch, drilling each concept. Stretch:
  - the signed curvature's sign convention vs the steer sign;
  - the curvature-offset correlation on `monza-like` at 30 m/s.
- `agents/unit-02.py` (G2.3): the measurement window is anchored at `self.current_index`, the reached-radius index,
  not at a second carried hint. That avoids desync and handles a respawn for free ([fable] N5). The milestone
  covers G2.1–G2.5.

### Phase C: Unit 3 content (the same dispatch rule)
- **Lesson:**
  1. The hook: "Predict where the car is in 1 s."
  2. The kinematic bicycle and its circle.
  3. The longitudinal map and the terminal speed (it links back to Unit 1's 19.49 m/s).
  4. Euler, step by step.
  5. RK4.
  6. The error orders from a convergence plot (G3.3).
  7. Prediction from telemetry (G3.2).
  8. "This is the *model* car": what changes on CARLA, as a pointer to Units 6 and 8.
- **Exercises:** at least 6 and at least 2 stretch. Stretch:
  - the step size at which Euler's 1 s error falls below 1 cm;
  - a semi-implicit Euler variant, and its order.
- `agents/unit-03.py` (G3.4) and the milestone (G3.1–G3.4).

### Phase D: teacher notes for both units (active session, inline)

### Phase E: verification (named)
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN.
- `bash scripts/pre-merge-guard.sh --pr` OK.
- All the gates hold in the milestones.
- Units 2–3 notebook execution totals ≤ 3 min.

## Out of scope
- New racekit modules; the dynamic car (`roar-004`); PID (Unit 4).
- Changes to the driving behaviour of the reference submissions.
- Labs.

## Plan Review

### Round 1 (v1)
- **[sol]** REJECT:
  - B, `polyfit` too early: [FIXED v2, dropped; it stays a Unit 8 name].
  - S, the G2.4 tolerances: [FIXED v2].
  - N, the G3.2 sample count: [FIXED v2, 180 rows].
  - It confirmed the reframing and the no-driving-change deviation are honest, and that G2.2 is achievable.
- **[fable]** APPROVE WITH NITS (it reproduced every pinned number independently):
  - M1, Euler's circle error is a bounded half-step shift, not growth: [FIXED v2].
  - M2, `polyfit`: [FIXED v2].
  - S1, the cross-track scorecard: [FIXED v2, G2.5 with the jittered medians and ranges].
  - S2, the exact `offset` formula, window and ties: [FIXED v2].
  - S3, no `np.cross`: [FIXED v2].
  - S4, the `predict` signature: [FIXED v2].
  - S5, Menger vs the generator: [FIXED v2, in G2.1].
  - N1–N8: [FIXED v2].
- **[self]** APPROVE, with the same window concern as [fable] S2.

### Round 2 (v2)
- **[sol]** REJECT. Round 1 was verified resolved, and G2.1, G2.2, G2.4, G2.5 and G3.1 were checked by probe. B: G3.4
  checked only the position: [FIXED v2.1, all four components with wrapped ψ and pinned tolerances].
- **[fable]** APPROVE WITH NITS. Every round-1 item was verified as intended, including the G2.2 formula to 2.3e-13 over 17651 rows and the G2.5 table digit for digit. N1–N4 (the Euler window statistic, e = p − foot, the held filter, the RMS tolerance): [FIXED v2.1].

### Round 3 (v2.1): CONSENSUS
- **[sol]** APPROVE. G3.4's full-state check was reproduced over 180 rows, and there are no new issues.
- **[fable]** APPROVE WITH NITS (round 2; all its nits are folded in v2.1).
- **[self]** APPROVE.

## Content Review

### Round 1

- [self] APPROVE pending the fixes below; ruled B1 a real defect and confirmed it with the prototype (`scratchpad/proto_stop.py`, 24 cases, worst error 2.95e-8 m after the fix).
- [sol] REJECT:
  - **B1** [FIXED] Near a braking stop, `predict` disagrees with racekit: from v = 0.01 under full brake it predicts x −0.0028 m against racekit's +0.000167 m, because a single RK4 step crosses zero without the stop clamp.
    `unit-03.py` now detects up front, with `|v| ≤ a_B·brake·dt`, when a tick can reach a stop.
    It then integrates that tick with `stopping_tick`: 10 RK4 substeps with racekit's clamp (crossed zero, or held at rest when the throttle cannot beat the brake).
    A new milestone cell checks braking to a stop against `KinematicCar.advance` (v0 ∈ {0, 0.01, 0.2, 1, 3, 8} × 4 actions, max error < 1e-6, v ≥ 0).
    The lesson notes the stop exception.
  - **S2** [FIXED] The lesson stated the integrator conclusion as universal.
    It now limits the claim to smooth ODEs and the windows measured.
    It names the half-step lag as the circle's picture, and says a jump (the stop) must be stepped to or across.
  - **S3** [FIXED] The lesson stated Σκ·ds = ±2π as an identity.
    It is now an approximation: the unit square gives 4√2 ≈ 5.66.
    The exact turning of a polygon is the sum of its exterior angles.
- [fable] APPROVE WITH NITS:
  - **S1** [FIXED] The Unit 2 teacher-notes sitting section refs are now §§1–2 / 3–4 / 5–8.
  - **N1** [FIXED] Corrected the Dκ/2 wording.
  - **N2** [FIXED] Added the high-gain clause.
  - **N3** [FIXED] Exercise 10 now says "(a track may have none)".
  - **N4** [FIXED] The Unit 3 teacher notes now list the sources of model error: tyre slip, guessed parameters, actuator delay and the asynchronous tick.
  - **N5** [FIXED] The plan's "nearer target" line is now marked superseded.
  - **N6** [FIXED] Dropped the unused `cumsum`, `dot`, `set_xscale` and `set_yscale` from the closed list. `advance` and `reset` are now listed as infrastructure, for the milestone's racekit check.

The checks re-run after the fixes all pass:
- every static book check;
- exec-lessons, exec-solutions and milestone-check;
- racekit pytest (187 passed);
- ruff over the CI scope;
- `check_submission` on `unit-03.py`;
- G3.4 (180 rows, RK4 max error 1.35e-8 m).

The race times are unchanged: 223.50 / 412.75 / 882.55 s.
