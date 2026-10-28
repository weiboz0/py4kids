# Design 013 — "Applied Python: Autonomous Racing" (a new advanced book for the Berkeley ROAR series)

**Status:** APPROVED, v4.7 (2026-10-28). The design gate is CLOSED: consensus in round 4.
v2 folded the round-1 design review and a re-check of the Summer 2026 season's published reports. v3 folds round 2
([sol] REJECT on B2 only; [fable] APPROVE WITH NITS with one MUST). v3.1 made the interim CARLA checks
non-blocking. v4 folds round 3. See the Design Review section.
v4.4 (plan `roar-006`) restates the Unit 7 row (per-section speed knobs, the (A_LAT, A_DEC) grid, the clean rule)
and raises the routed pytest budget to 8 min.
v4.5 (plan `roar-007`) names the seeded checkpoint tracks and pins Checkpoint A's gate.
v4.6 (plan `roar-007`) raises the book notebook exec budget to 30 CI-minutes, after the first book-level measurement.
v4.7 (plan `roar-008`) restates the Unit 8 and Unit 9 rows from probes and raises the routed pytest budget to 10 min.

The book `roar` is tutorial material whose purpose is to let a strong student **reach a reasonable ranking in the
Berkeley ROAR Simulation Racing Series** (§1.3 defines "reasonable").
The design was agreed section by section with the author on 2026-10-25 (brainstorming). The author then set the book
to autopilot, with questions recorded as follow-ups.
Plans live under `docs/plans/roar/` (`roar-NNN`). `tools/guard.py` already guards namespaced plan directories.

## 1. Why, and what wins

### 1.1 The series
ROAR (Robot Open Autonomous Racing, UC Berkeley FHL Vive Center) runs a **Simulation Racing Series** every semester
for high-school students.
- Competitors fork `augcog/ROAR_Competition` and submit a GitHub repository URL.
- The repository contains their `submission.py` plus the **unmodified** `competition_runner.py` and
  `infrastructure.py`. Extra dependencies go in an optional `instruction.txt` (series page) or `requirements.txt`
  (gitbook); the two sources disagree, and Unit 13 checks the current season's wording.
- The stack is CARLA **0.9.12** with the **Monza map v1.1** and the `ROAR_PY` interface. The official environment is
  **Python 3.8** (`conda create -n roar_competition python=3.8`, gitbook installation page), so numpy is at most
  1.24.x there. The Monza v1.1 executable ships for **Windows AMD64** (series instructions and gitbook, checked
  2026-10-25).
- The current season's deadline is 2026-12-11.

### 1.2 Facts about the real race
Verified from `augcog/ROAR_Competition` `competition_code/competition_runner.py` at commit `ab19e1b` by two
independent readings in this design's review:
- The race is **3 laps** (the waypoint list is tripled), scored on **total elapsed sim time**. `max_seconds` is a
  sim-time timeout.
- `world.set_control_steps(0.05, 0.005)`: the control step is 0.05 s with 0.005 s physics substeps, and the world is
  synchronous. Each tick runs `await solution.step()` and then `await world.step()`.
- Progress is the furthest waypoint reached. It is found by projecting waypoints onto the car's latest motion
  segment, inside a **forward window of 15 waypoints**. The race ends when the progress index is within **5
  waypoints** of the end of the tripled list (`lap_finished(check_step=5)`).
- A **major collision** (collision impulse norm > 100) **respawns the car at the race start pose** with zero linear
  and angular velocity. The world then advances **20 control steps (1.0 s) without calling the agent**, and **the
  progress index is reset to 0** (`respawn()`, corrected in v4.1 after the roar-001 content gate re-read the pinned
  code). Because the waypoint list covers all 3 laps, a major collision at the pinned commit effectively
  **restarts the race with the clock still running**. The published Summer 2026 winner's report says "a single
  crash costs a full lap", which is milder than the pinned code; the book mirrors the pinned code and notes the
  discrepancy. **Either way, zero collisions is the dominant ranking lever.**
- The agent is a `RoarCompetitionSolution(maneuverable_waypoints, vehicle, camera_sensor, location_sensor,
  velocity_sensor, rpy_sensor, occupancy_map_sensor, collision_sensor)` with `async initialize()` and `async step()`.
  It reads sensors with `get_last_gym_observation()` and acts with `await vehicle.apply_action({"throttle", "steer",
  "brake", "hand_brake", "reverse", "target_gear"})`.
- The skeleton's starter agent steers with a P controller toward the waypoint 3 ahead, with gain ∝ 1/√v, and holds
  20 m/s with a P controller.

### 1.3 What wins, and what "reasonable ranking" means
Published Summer 2026 reports ([first place](https://roar.berkeley.edu/opening-the-corner-late-apex-line-widening-and-per-sectiongrip-tuning-for-the-roar-monza-simulation-race/),
[third place](https://roar.berkeley.edu/third-place-solution-in-summer-2026-simulation-racing-series/)):
- **Results:** 22 entries. The winner took **319.65 s** for 3 laps with 0 collisions. Third place took 320.15 s. The
  previous season's winning controller ran about 320.4–321.25 s. **Places are separated by tenths of a second, and
  run-to-run noise is about 0.3 s**, so single-run comparisons partly rank noise.
- **What won:** pure-pursuit steering; a **corner-radius speed controller** with **per-section grip constants tuned
  empirically**; local **late-apex line widening** at a few corners; offline tools and **systematic tuning**
  (coordinate search over about 30 parameters); and **measurement infrastructure** (repeated runs, crash maps).
- **What failed for a podium team:** a global racing-line optimization (it caused crashes, because "the line and the
  speed controller are effectively one artifact"); a speed profile derived purely from physics (about 10 s per lap
  slower than the tuned constants); and throttle smoothing.

**"Reasonable ranking" (the book's acceptance proxy, pinned to the Summer 2026 season):** a reference agent that,
on CARLA 0.9.12 with Monza v1.1 and the pinned runner, completes 3 laps with **0 major collisions** in **every one of
at least 5 runs**, with a **median ≤ 329 s** (within 3% of the published winning time). It is measured by the author
outside CI (§7.3). The book teaches toward the frontier but promises only this proxy.

## 2. Audience and baseline (a per-book declared baseline, AGENTS.md "Self-containedness is law")

- **Audience:** strong high-school programmers with **competitive-programming experience** (Python or C++) who have
  **studied calculus**. Every student can run the real stack on their own machine (author decision, 2026-10-25).
- **Assumed math:** single-variable calculus (derivatives, integrals, the chain rule, first-order Taylor),
  trigonometry, and 2-D/3-D vectors with the dot product.
  **Taught in-book:** matrices as linear maps, linear least squares, linearization, discrete-time systems, simple
  constrained optimization, and repeated-measurement statistics (median, spread, noise-aware comparison).
- **Assumed programming:** Python fluency (classes, modules, comprehensions, `async def` / `await` *usage*) and
  numpy fluency. These are declared assumed-baseline concepts in `roar/curriculum/baseline.yaml`, earning no teaching
  credit.
- **Submission target: Python 3.8 with numpy < 1.25** ([fable] r2 F1). Notebooks run on the repo's Python 3.12+,
  but every **submission file** must be 3.8-compatible:
  - no `match`;
  - no runtime `X | Y` types or `list[int]` subscripts;
  - no `str.removeprefix`, `functools.cache` or `np.trapezoid`.
  Unit 1 states this, and Unit 13's packaging checklist re-checks it.
- **Libraries:** numpy (assumed). **scipy** (`optimize`, `interpolate`) and **matplotlib** are **taught before
  assessed**, as ordered concepts (§7.1).
- **Retained laws (normative):** the declared baseline overrides only the audience, the assumed math and the named
  libraries. Every other law holds:
  - prereq closure;
  - practice coverage, including the capstone rule;
  - taught-before-assessed;
  - project-first hooks;
  - student-notebook hygiene;
  - a stretch exercise per unit;
  - `teacher-notes.md` per unit;
  - strict checkpoints.

## 3. Book identity and registry

- **id / root / folder:** `roar` (unused).
- **number:** `3` (display ordinal), in the "Applied Python: …" series with recsys.
- **title:** "Applied Python: Autonomous Racing".
  **subtitle:** "Build a competitive ROAR agent, from waypoints to optimal control".
- **depends_on:** `[python-projects]` (matching recsys). In practice the declared baseline supplies the
  prerequisites.
- **dependency_group:** `roar` (numpy, scipy, matplotlib, and the editable `racekit` package via
  `[tool.uv.sources] racekit = { path = "roar/projects/racekit", editable = true }`). No torch, CARLA or `ROAR_PY`.
- **flags:**
  - `site` is set in `roar-014` together with publication. The book is not shown on the public site before its
    CARLA qualification.
  - `publication` is set only after the §7.3 qualification, in `roar-014`.
- **lesson_budget:** `[30, 50]`, a whole-book total over 13 units at 2–3 sittings each.
  `roar-001` sets **`buildout: true`** on the book's `books.yaml` entry (as recsys did) and removes it once the
  authored total reaches 30 and the concept catalog is fully introduced. There are no placeholder curriculum entries.

## 4. The simulator: the `racekit` package (approach 3, "own sim + calibration")

`roar/projects/racekit/racekit/` is an importable harness package, the analogue of recsys's `bookrec`. It depends
only on numpy and scipy, and is tested by the routed suite.

**`racekit` is itself Python 3.8-compatible** ([sol] r3 B1, [fable] r3 M1):
- its own `pyproject.toml` declares `requires-python = ">=3.8"`;
- every module starts with `from __future__ import annotations` and avoids 3.9+ syntax and APIs (the §4.1 deny-list);
- scipy usage stays within 1.10.x, and scipy is imported lazily, only inside the analysis modules that need it.

The core (the shim, the runner, track loading, cars, `check_submission`) imports numpy only. A routed test parses
every `racekit` module with `ast.parse(feature_version=(3, 8))` and the deny-list.
**It is a harness, never a dependency of a submission** (§4.1).

### 4.1 The submission ABI: one self-contained file
- The unit of work is the **season's official submission shape**: a single `submission.py` defining
  `RoarCompetitionSolution` with exactly the constructor, lifecycle and action dict of §1.2.
- It may import **only** the standard library, `numpy` and `roar_py_interface`. That is what the official runner's
  environment provides without an `instruction.txt`.
- All of a student's control code lives **in that file**. The book's units teach techniques in notebooks, and each
  unit's milestone grows a **reference submission file**: `roar/projects/racekit/agents/unit-NN.py`, each one a
  complete official-shape submission.
- **`racekit.roar_py_interface`** is a **shim module**. `run_race` and `check_submission` install it in
  `sys.modules` under the name `roar_py_interface` **for the whole call**, covering loading and every tick, so
  function-local imports work. They restore the previous entry afterwards. They **refuse** to overwrite a real
  `roar_py_interface` that is already importable.
  - Submissions are loaded with `importlib.util.spec_from_file_location` under a **unique module name per load**, so
    two milestones in one kernel never collide.
  - The file's `import roar_py_interface` line therefore works unchanged.
  - The shim provides:
  - `RoarPyWaypoint` (`.location` (3,) float64 in metres, `.roll_pitch_yaw` (3,) radians, `.lane_width` metres);
  - sensor objects with `get_last_gym_observation()`:
    - location (3,) in metres, world frame;
    - roll-pitch-yaw (3,) in radians;
    - velocity (3,) in m/s, world frame;
    - collision: `.impulse_normal` (3,);
  - `vehicle.apply_action(dict)`, which **validates** the action keys, types and ranges (`throttle`/`brake`
    ∈ [0, 1], `steer` ∈ [−1, 1], `reverse` ∈ {0, 1}, `target_gear` an int, `hand_brake` ∈ [0, 1]), and raises on
    violation;
  - the camera and occupancy-map sensors as `None`-compatible stubs (they are not taught).
- **The contract test:** the shim's names, signatures, shapes and units are tested against a **contract fixture**
  derived from the MIT-licensed `ROAR_PY` at the pinned commit. The fixture is recorded with provenance: commit,
  file, licence. It is the only `ROAR_PY`-derived artifact in the repo, and it carries the MIT notice.
- **`racekit.check_submission(path)`** proves exactly the following, and nothing more:
  1. the file parses with `ast.parse(src, feature_version=(3, 8))`, and an AST deny-list catches the 3.9+ runtime
     APIs:
     - `str.removeprefix` / `removesuffix`;
     - `functools.cache`, `math.lcm`, `itertools.pairwise`, `int.bit_count`;
     - `zip(..., strict=)`;
     - `dict | dict` and `|=` on dicts;
     - `np.trapezoid`.
     It also catches `X | Y` and builtin-generic subscripts (`list[int]`) in annotation positions, which
     `from __future__ import annotations` would hide from the 3.8 run. It defines `RoarCompetitionSolution` with the official constructor signature.
  2. its imports are within the allowed set;
  3. it completes a racekit race on `test-circuit` without an action-validation error or an exception, and with
     `step()` compute **p99 ≤ 5 ms**, the universal per-submission budget, with the first 50 warm-up ticks excluded. The official sim is
     synchronous, so compute time never changes the scored time; the budget protects CI wall time and flags a
     controller too slow to be practical.
  - A routed test runs every `agents/unit-NN.py` through `check_submission` in an **isolated** 3.8 environment:
    `uv run --no-project --python 3.8 --with "numpy<1.25" --with "scipy<1.11" --with-editable roar/projects/racekit
    python -m racekit.check_submission <file>`. It asserts, inside the run, that `sys.version_info[:2] == (3, 8)`
    and `numpy.__version__ < "1.25"`. The [fable] r3 probe measured it at about 3 s warm. It is the one deliberately
    slow test, and it stays within the routed 5-minute budget.
  It does **not** prove CARLA performance. That is what the real-sim labs and §7.3 are for.

### 4.2 The race runner mirrors the real rules
- `racekit.run_race(submission, track, car, laps=3, max_seconds=...)` is a **plain synchronous function**. It runs
  the agent's `async initialize()` / `step()` on a **private event loop**: a fresh loop when none is running, or
  otherwise a worker thread with its own loop. Notebooks therefore never use top-level `await`, which `cell-lint`
  rejects, and never call `asyncio.run` inside ipykernel's running loop. `roar-001` tests both paths.
- It uses a fixed 0.05 s control tick with 10 physics substeps.
- **Progress** is the real rule: segment projection inside a forward window of 15 waypoints. (Unit 2 teaches the
  student's own *windowed nearest-waypoint search* as a separate tool, and says how it differs from the runner's
  rule.)
- **Major collision** (both are labelled as approximations wherever they are taught):
  - leaving the drivable width (the wall approximation);
  - or, on the dynamic car, a **spin-out** (sideslip |β| or yaw rate |r| beyond a pinned threshold).
  Either one **respawns the car at the start pose** with zero velocity, holds it for 20 ticks without calling the
  agent, and **resets progress to 0**, as the pinned runner does (§1.2). The finish rule is the runner's
  5-waypoint margin.
- It returns:
  - total time and completion;
  - collision count and the sim times of each respawn (`respawn_times`);
  - per-sector splits;
  - per-tick telemetry (time, pose, velocity, actions, progress, track-relative offset, and a `held` flag for the
    20 respawn-hold ticks).
- **Ticks:** at the real winning pace (320 s) a race is about **6,400 ticks**. The 20 m/s starter baseline needs
  about 17,000 ticks on `monza-like`.

### 4.3 Tracks are generated by seeded scripts, never copied
- `roar/data/gen_tracks.py` builds closed centrelines from segment specs: straights, constant-radius arcs, and
  clothoid transitions with continuous curvature, plus a per-segment drivable width.
- It emits waypoints at about 2 m spacing (like `maneuverable_waypoints`) into **`roar/data/generated/`**
  (gitignored), with sha256 entries in `roar/data/generated/checksums.json`, regenerated in CI and byte-stable.
- **One generator driver** ([sol] r2 S2, [fable] r2 F3): `roar/data/generate.py` runs, in a declared order:
  1. tracks;
  2. the carla-like telemetry logs (from `roar-004`);
  3. the `lab-check` sample CSV.
  It runs in `ci-local.sh` step 2, before step 3's `lab-check` reads the CSV.
- It ships these tracks:
  - `oval` (Units 1–4);
  - `test-circuit` (mixed corners and a chicane);
  - `monza-like`, built from public facts about the circuit: about 5.8 km, long straights, the Rettifilo and Roggia
    chicanes, the two Lesmo corners, Ascari and the Parabolica. It is labelled **"inspired by Monza"**, not a copy of
    the CARLA map.
  - **unseen-for-tuning** checkpoint tracks from named seeds (v4.5, plan `roar-007`: `test-circuit-seed1` …
    `test-circuit-seed4` are Checkpoint A's training family and `test-circuit-seed2026` its checkpoint track; the
    carla-like car's hidden grip is drawn per track name, so a variant differs in grip as well as shape). They are
    reproducible and not secret; the checkpoint
    briefs forbid per-track tuning, and the content gate's blind solve tests that.
- The real CARLA map and its waypoints are **never** committed or redistributed.

### 4.4 Car models, each taught before it is used
1. **Kinematic bicycle** (Unit 3): position, heading and speed, with steering angle → yaw rate through the wheelbase.
   It includes a **simple longitudinal map** (throttle → acceleration, brake → deceleration, quadratic drag), so Unit
   4's speed PID has a plant to control.
2. **Dynamic bicycle** (Unit 6 onward): lateral tyre forces with a saturating tyre curve and a **friction circle**;
   longitudinal force; brake and drag; a steering-rate limit; one to two ticks of actuator lag. It produces real
   slides and spin-outs.
3. **The "carla-like" ground-truth car:** dynamic-bicycle parameters with **section-varying grip**, the stand-in for
   CARLA.
   - Its parameters live in `racekit._truth`. That module is public in a public repo; teaching material says "do not
     read it" and never uses it.
   - Exercises access the car only through `racekit.cars.carla_like()`.
   - A seeded script records telemetry logs from it. Unit 8 identifies its parameters from those logs. The real-sim
     lab repeats the identification on the student's own CARLA logs.
   - Optional per-run **noise** (a seeded actuator jitter) reproduces the about-0.3 s run-to-run spread, so
     noise-aware comparison is taught on realistic data.

### 4.5 Determinism and honesty
- Pure numpy, fixed tick, fixed seeds, no wall-clock effect on the simulation. The per-tick compute time of `step()`
  is measured but never fed back into the simulation.
- Times are gated with **tolerances** (`allclose`). "A beats B" requires a margin larger than the measured spread over
  at least 5 noisy runs. This is the §184 tolerance/rank rule from recsys, never an exact float.
- Every racekit number is called a **model** number. Students must re-measure gains, μ and times on CARLA, and Unit 8
  teaches how.

## 5. Project architecture: one submission, upgraded unit by unit

- The student grows **one `submission.py`**. Each unit adds or replaces techniques **inside that file**.
- The book's reference versions are `roar/projects/racekit/agents/unit-NN.py`, each passing `check_submission`.
- `racekit` modules are **harness and analysis tools only**:
  - `run_race`, `tracks`, `cars`, `telemetry`, `plots`;
  - `measure`: repeated runs, median and spread, noise-aware comparison;
  - `sysid_data`;
  - `check_submission`.
  A module enters `racekit` **in the plan of the unit that teaches it**. Techniques that students write (geometry,
  PID, pure pursuit, speed planning, the line, MPC, tuning) are **student code in the submission**, not racekit
  imports.
- Each unit's **milestone notebook**, `roar/projects/racekit/milestones/unit-NN-<slug>.ipynb`:
  - loads that unit's reference submission;
  - races it;
  - **asserts the unit's gate** (§6).
  It runs under `exec-solutions`, exactly as recsys's milestones do.
- The single `projects/` registry entry is the **capstone**, authored last (§6).

## 6. Structure: three parts, two checkpoints, an integration unit, a capstone

Every unit ships `lesson.ipynb` (opening with its racing **project hook**), `exercises.ipynb` (at least one `stretch`
Challenge), `solutions.ipynb`, `teacher-notes.md` and `manifest.yaml`.
🏁 marks a unit with a **real-sim lab** (§7.2).

**Gate policy:**
- Each gate has **validity, safety and timing** parts (0 collisions where stated; `check_submission` passes) plus a
  **measured result**.
- Gates on *optional* sophistication (the racing line, MPC) are **falsifiable experiments**. The gate requires an
  honest, noise-aware comparison against the simpler fallback, and **either outcome is acceptable** if the evidence
  supports it. The submission keeps whichever wins.
- Exact numbers are pinned in each unit's plan from a pre-implementation probe. A miss means stop, amend the plan and
  re-gate.

### Part 1: A car that finishes clean laps

| # | Unit | Project hook | Introduces | Gate |
|---|---|---|---|---|
| 1 | The race and the baseline 🏁 | "Here is the starter agent. How fast is it, and where does it lose time?" | Race rules; the submission ABI; the step loop; telemetry; sector splits; **repeated runs, median and spread** | The starter completes `oval` and `monza-like` with 0 collisions in all of N noisy runs; the median and spread lie in pinned intervals |
| 2 | Geometry of a track | "The starter steers at a point three waypoints ahead and never looks further: where exactly is the car relative to the track, and what is coming?" (v4.2) | Frames, heading, `atan2`, angle wrapping; windowed nearest-waypoint search; cross-track error; Menger curvature | Functions match analytic circles within tolerance |
| 3 | Modelling the car | "Predict where the car is in 1 s." | Kinematic bicycle and longitudinal map; Euler vs RK; timestep error | Circle radius matches the analytic value; RK error < Euler error |
| 4 | PID control | "Hold 20 m/s, then follow the line." | P/I/D; discrete PID; windup; step-response tuning; steering from heading error | Overshoot and settling in bounds; cross-track error below the starter's |
| 5 | Geometric steering 🏁 | "Steer like a driver looks ahead." | Pure pursuit; speed-scaled lookahead; Stanley; stability vs corner-cutting | Under actuator delay at speed, speed-scaled pure pursuit stays clean where the tighter controllers crash, and beats a detuned PD (noise-aware); with no delay it pays in corner-cutting (v4.3) |
| 6 | Grip and the speed limit | "Why does the car spin at Parabolica?" | Dynamic bicycle; tyre saturation; friction circle; v_max = √(μg/κ); the spin-out failure | A curvature-limited speed controller removes spin-outs and collisions on `test-circuit` |
| 7 | Speed planning 🏁 | "Brake *before* the corner, and find the grip that is really there." | Forward–backward speed profile; lookahead planning (a speed lead in seconds); the planned cornering and braking rates read together as a grid (v4.4); **per-section speed knobs by one-knob sweeps** (one multiplier per section, accepted by Unit 1's median-and-spread rule and a clean rule: finished, 0 collisions, max cross-track error ≤ 2 m; the knobs absorb μ and the planner's other errors, so they are not μ estimates, and Unit 8 measures μ; Unit 12 generalizes to many knobs) | A large median race-time gain over Unit 6 at 0 collisions; per-section knobs beat the best single global setting (noise-aware, v4.4) |
| CP-A | **Checkpoint A** | A complete clean agent on an unseen-for-tuning seeded track | — (strict) | One global setting, tuned on the training family only, finishes the checkpoint track clean on five seeds within a median of 330 s (v4.5) |

### Part 2: Measuring the real car

| # | Unit | Project hook | Introduces | Gate |
|---|---|---|---|---|
| 8 | System identification 🏁 | "Your sim-tuned agent is slow, or crashes, on CARLA. Why?" | Logging; matrices; linear least squares (and QR); fitting the longitudinal map and the **steering gain**; residuals; **per-section μ from limit probes** (one section pushed per race, the student's own agent as the driver, a percentile of \|a\|, a lower bound where it did not slide) and planning with a fraction of it (v4.7) | The carla-like car's parameters are recovered within tolerance; one fraction of the measured grip, tuned on the training family, transfers to the unseen track faster than Checkpoint A (v4.7) |
| 9 | The racing line | "The centreline is not the fast line, but a new line breaks your speed tuning." | Width constraints; the **smoothest line** (squared second differences of its points, the usual stand-in for minimum curvature) as bounded least squares (`scipy.optimize.lsq_linear`) on a reduced problem, a cubic B-spline of offsets, solved offline and shipped as constants (a submission imports only numpy); **local widening**; re-tuning speed with the line (v4.7) | Valid, collision-free line(s); an honest comparison: global line vs local widening vs centreline (falsifiable) |
| 10 | Model predictive control 🏁 | "Plan the next 2 s, every tick." | Linearization; discrete-time model; horizon cost; **LTV least-squares MPC** (linearize → stack → solve, box constraints by clipping); the compute budget per tick; `scipy.optimize` on a single corner as the exact reference | MPC meets the tick budget and is collision-free; an honest comparison with pure pursuit (falsifiable) |
| 11 | Robustness | "One crash costs you a lap." | Respawn economics; fallback controller; off-track and spin detection; testing across seeds and perturbed parameters | Completes N/N perturbed-parameter races at 0 collisions |
| CP-B | **Checkpoint B** | A full agent under parameter uncertainty | — (strict) | Completes hidden perturbed races, timed |

### Part 3: Going fast

| # | Unit | Project hook | Introduces | Gate |
|---|---|---|---|---|
| 12 | Tuning against race time | "You have 30 knobs and 0.3 s of noise. Which changes are real?" | Race time as a black-box objective; coordinate, random and evolution-strategy search; noise-aware acceptance; overfitting and held-out tracks; profiling `step()`; determinism and rounding traps; packaging and version pinning | The tuned agent beats the hand-tuned one on a **held-out** track (noise-aware) |
| 13 | Race day (integration; **introduces nothing**) 🏁 | "Assemble, qualify and submit." | — It practises the Unit 8–12 concepts on `monza-like`: sysid-informed μ, line plus speed re-tune, MPC-or-pursuit choice, robustness, noise-aware tuning, the packaging checklist | The assembled submission passes `check_submission`, the timing budget and N/N clean races; it beats the Unit 7 agent (noise-aware) |
| Capstone | **Your competition agent** (`project-14-…`) | Build, tune and justify the agent you submit | — An engineering report with an **ablation table** (race time bought by each stage, with spread) | The reference beats the starter by a pinned margin on `monza-like` at 0 collisions |

Unit 12's Challenge may include an **optional** reinforcement-learning taste (a policy-gradient tune of one
parameter, compared honestly with search). Deep RL is not core.

## 7. Verification

### 7.1 What CI proves
This covers `scripts/ci-local.sh` and the routed `uv run --group roar` suite.
- **`racekit` tests:**
  - shim vs the `ROAR_PY` contract fixture;
  - action validation;
  - analytic car checks: circle radius, friction-circle bound, integrator order, spin-out trigger;
  - generator **byte-stability**;
  - runner progress, respawn and timing on scripted agents;
  - `run_race` sync paths (with and without a running loop);
  - `check_submission` positive and negative cases.
- **Reference submissions:** every `agents/unit-NN.py` passes `check_submission`.
- **Notebooks:** every lesson, solution, milestone, checkpoint and capstone notebook executes clean. Each unit's gate
  is an `assert` in its milestone notebook.
- **The standard laws:** manifest, prereq, coverage (including the capstone rule), hygiene, stretch, cell-lint and
  concept-scan.
- **API ordering ([sol] r1 B2, r2 B2; [fable] r2 F5).** It works in two layers, and `concept-scan` is unchanged:
  1. Every callable a student may call is listed in `baseline.yaml` `library_methods`, so `concept-scan` (whose
     library exemption is global, `tools/concept_scan.py`) accepts it. This includes the shim API, `racekit`
     harness calls, numpy names, and the **taught** scipy, matplotlib and `racekit` analysis calls.
  2. `roar/curriculum/api-order.yaml` maps each **taught** callable to the **concept id** that teaches it. Keys are
     bare names with an optional `module:` qualifier for collisions (`fit`, `solve`, `plot`). numpy names that belong
     to **in-book-taught math** (`np.linalg.lstsq`, `solve`, `inv`, `polyfit`) are mapped to their teaching concept
     (Unit 8), **not** listed as infrastructure. Otherwise "numpy is assumed" would let least squares leak into Unit 4. That
     concept is introduced by exactly one entry in `concepts.yaml` and `coverage-map.yaml`. There is no second copy
     of the order: a routed test **derives** each concept's introducing position from the coverage map's entry order
     and `introduces` lists.
  **Call resolution ([sol] r3 S2, [fable] r3 S2):** the test resolves calls to canonical names. It follows `import m`
  and `import m as a` (so `a.f(...)` → `m.f`), `from m import f` and `from m import f as g` (so `g(...)` → `m.f`),
  and attribute calls (`x.f(...)` → `f`). A negative test covers each form.
  **Scan scope ([fable] r3 S3):** each unit's lesson, exercises and solutions; its milestone; its
  `agents/unit-NN.py`; and its lab are all positioned at that unit. Checkpoints and the capstone sit at their map
  position. Verify cells are excluded, mirroring `concept-scan`.
  The test fails when:
  - a taught callable appears in an entry (or entry-positioned file) that comes before its introducing entry;
  - an `api-order.yaml` key is **not** in `library_methods` (the reverse direction);
  - a callable in `library_methods` is in **neither** `api-order.yaml` **nor** the explicit `infrastructure:` list at
    the top of `api-order.yaml`;
  - an `api-order.yaml` concept id is unknown.
  Negative cases prove a premature use fails and an unmapped name fails.
- **Budgets** (measured targets; an overrun means stop and amend):
  - **Book notebook exec ≤ 30 CI-minutes** (v4.6; it was 15): `exec-lessons` + `exec-solutions` wall time, with the
    1-minute load average recorded at start and end. Every plan's report records the book-level total. It **excludes** track and telemetry generation, which are reported
    separately and must stay ≤ 1 min.
  - **Routed pytest ≤ 10 min** on an 8-core CI machine (v4.7, plan `roar-008`; it was 8 min from v4.4, plan `roar-006`, and 5 min before that; the Unit 8–9 gates add 141 races). From v4.4: the Unit 6–7 gates
    add about 2 min of pooled races).
  - The per-cell 120 s cap is retained.
  - **Per-tick (a measured target from the [fable] probe, not a cap the runner enforces):** the simulation costs
    about 0.2 ms per tick, and a 17,000-tick starter-baseline race takes ≤ 4 s. A student's `step()` adds to that.
  - **MPC:** the Unit 10 agent's `step()` has **p99 ≤ 5 ms** on the CI machine, warm-up excluded. Over budget, it falls back to pure
    pursuit for that tick, and counts and reports the fallbacks. scipy's constrained solvers (about 90–300 ms per
    tick in the probe) are used only on a single-corner segment of a few hundred ticks.
  - Notebooks size their runs to a few full races per cell.
- **`ci-local.sh` wiring (`roar-001`):**
  - add `roar/projects/racekit roar/data` to the ruff path list;
  - extend the data-regeneration hook: when `$book/data/generate.py` exists, run it with
    `PYTHONHASHSEED=0 uv run --group "$grp"`. The driver verifies `checksums.json` byte-stability for every output
    (tracks, telemetry, lab CSV). Otherwise keep recsys's
    existing `gen_catalog.py` / `gen_interactions.py` branch unchanged. Run it before the routed pytest;
  - add the `roar` group and the `racekit` source to `pyproject.toml`.
  - ruff targets `py312` with the default E/F rules, so it never rewrites `racekit` to 3.9+ syntax. If `UP` rules are
    ever enabled, add `[tool.ruff.per-file-target-version] "roar/projects/racekit/**" = "py38"`.

### 7.2 Real-sim labs (CI checks their analysis, not CARLA)
- 🏁 units ship `labs/real-sim.ipynb`, labelled "runs on your machine with CARLA 0.9.12 and `ROAR_PY`".
- The exec tools do not discover it; they discover only lessons, solutions, checkpoints, projects and milestones.
- Each lab gives exact steps:
  1. start the Monza v1.1 executable;
  2. put the submission in the forked competition folder;
  3. run `competition_runner.py`;
  4. export telemetry to CSV;
  5. analyse it.
- Every cell that needs CARLA carries the `no-exec` tag.
- **The `lab-check` command** (a new `py4kids-tools` check, added by `roar-002` and wired into `ci-local.sh` step 3)
  checks, for each unit whose manifest declares `lab: true`:
  - the lab exists;
  - it has no outputs;
  - its CARLA cells are tagged;
  - it is excluded from `publish` and the site export.
  Then it **executes a copy** of the lab with the `no-exec` cells removed, against a seeded **sample telemetry CSV**
  that `roar/data/generate.py` writes into `roar/data/generated/`. So the analysis code is under CI even though the
  CARLA run is not.
- **Data path ([sol] r2 S3, [fable] r2 F8):**
  - Every lab's first cell, tagged `parameters`, sets `TELEMETRY_PATH = os.environ.get("ROAR_LAB_CSV",
    "telemetry.csv")`. Every analysis cell reads only through `TELEMETRY_PATH`.
  - `lab-check` sets `ROAR_LAB_CSV` to the fixture.
  - Negative tests: a lab that hard-codes a CSV path elsewhere, lacks the parameters cell, or reads data inside a
    `no-exec` cell fails `lab-check`.
- **No student data in the repo (the repo is PUBLIC):** lab outputs stay on the student's machine. `.gitignore`
  covers `roar/**/labs/**/*.csv`, `*.json`, `*.npz`, `*.parquet`, `*.log` and `*.png`. The sample fixture lives
  only in the gitignored generated directory. A routed test fails if any file under a `labs/` directory other than
  `*.ipynb` and `README.md` is tracked. Teacher notes say so.

### 7.3 Author qualification (outside CI): the "reasonable ranking" proxy
- **Early warnings ([fable] r2 F6):** the author runs two interim CARLA checks, recorded in the same file:
  - `roar-006`: the Unit 7 reference, untimed, must complete 3 laps with 0 collisions;
  - `roar-013`: the Unit 13 reference, timed.
  These checks need the author's Windows machine, so the shipping plan **does not block** on them. Each plan records
  its check as `PENDING (author)` in `qualification.md` and in its post-execution report, and surfaces it as a
  follow-up. A PENDING check is also a **named risk** in the `## Plan Review` of the next part's first plan
  (`roar-008` for the Unit 7 check, `roar-014` for the Unit 13 check), so gate reviewers see it. When the author runs a check and it fails, an errata/fix plan follows before the next part ships. Only
  the final qualification hard-gates the `publication` flag.
- Before `roar-014` sets the `publication` flag, the author runs the **final reference submission** on the pinned
  stack:
  - CARLA 0.9.12;
  - Monza v1.1;
  - `ROAR_Competition` at the pinned commit;
  - `ROAR_PY` at the pinned commit.
  The run is **exactly 5 consecutive official-runner launches** ([sol] r2 S1), all recorded in
  `roar/docs/qualification.md`: hardware, OS, GPU, versions, the submission file's **SHA-256** and repository commit,
  and **every** launch's outcome (time, collisions, timeout or crash). No launch is discarded or restarted.
  A **host failure** (the CARLA server exits, or the agent never receives its first tick) is not an agent failure. It
  is recorded, the 5-launch block restarts, and both blocks stay in the record.
- The §1.3 proxy (every run clean, median ≤ 329 s) must hold. **Otherwise stop and amend.** The fix is a plan that
  re-tunes, not a relaxed proxy without author sign-off.
- The record contains only the author's reference agent, never student results.
- If the season's runner, map or CARLA version changes, Unit 13 says what to re-check, and the qualification is
  re-run.

### 7.4 Provenance and licensing (`roar-001`)
- `roar/reference/upstream.md` records:
  - the pinned `ROAR_PY` commit and its MIT licence (the contract fixture carries the notice);
  - the `ROAR_Competition` commit, and the fact that it has **no LICENSE file** (checked 2026-10-25), so nothing
    from it is copied;
  - a **clean-room note:** the shim and the starter re-implementation are written from documented behaviour (the
    gitbook docs at `roar.gitbook.io/roar-competition-documentation` and the published reports);
  - the season reports cited in §1.3.
- A routed deny-list test fails on any tracked CARLA map, waypoint dump, `.umap`/`.xodr` file or vendored
  `ROAR_Competition` file.

## 8. Build sequence (one plan each, full lifecycle)

| Plan | Ships |
|---|---|
| design 013 (this doc) | The design, through the 3-way gate (docs-only) |
| `roar-001` foundation | the `books.yaml` entry (`buildout: true`, `dependency_group: roar`); the `roar/` skeleton (syllabus, curriculum, baseline, concepts, `api-order.yaml`); pyproject group and source; the `racekit` core (shim plus contract fixture, the sync runner with the real progress/respawn rule, the kinematic car with its longitudinal map, telemetry, `measure`, `check_submission`); `gen_tracks.py` and the `generate.py` driver; the ci-local generalizations (§7.1); the routed tests (API-order with its exhaustiveness check, deny-list, labs-tracked, the Python 3.8 `check_submission` run); `upstream.md`; `.gitignore`. No units. |
| `roar-002` | Unit 1; `lab-check`; the first lab; the starter re-implementation as `agents/unit-01.py` |
| `roar-003` | Units 2–3 |
| `roar-004` | `racekit` dynamic car, spin-out, the carla-like truth car, noise, the telemetry generator (infrastructure plus probes) |
| `roar-005` / `roar-006` | Units 4–5 / Units 6–7 (records the interim untimed CARLA check as PENDING (author), §7.3) |
| `roar-007` | Checkpoint A |
| `roar-008` / `roar-009` / `roar-010` | Units 8–9 / Unit 10 / Unit 11 |
| `roar-011` | Checkpoint B |
| `roar-012` / `roar-013` | Unit 12 / Unit 13 (integration; records the interim timed CARLA check as PENDING (author)) |
| `roar-014` | Capstone; site flag; §7.3 qualification; publication flag |

Pairings may be adjusted by each plan's gate without a design change.

## 9. Out of scope
- The **physical-car** ROAR series.
- Camera perception and computer vision. The camera and occupancy sensors are stubs, mentioned but not taught.
- Deep RL as core content (Unit 12 has an optional Challenge only).
- Copying ROAR_Competition code, or redistributing CARLA maps or waypoints.
- Student results in the repo.
- Governance edits: none are needed. AGENTS.md already permits a per-book declared baseline, and the content gate's
  audience duty already reads "per the book's declared baseline".

## Design Review

### Round 1 (v1 @ ed7f846)
- **[self]** APPROVE WITH NITS:
  - the ci-local data-gen hook is recsys-specific;
  - the ruff path list is hard-coded;
  - "hidden" tracks and `_truth` are visible in a public repo;
  - the `[tool.uv.sources]` entry is unstated.
  All [FIXED v2, §4.3, §4.4, §7.1].
- **[sol]** REJECT:
  - B1, the capstone rule: [FIXED v2, U13 is an integration unit that introduces nothing].
  - B2, `library_methods` vs taught APIs: [FIXED v2, §7.1 API-order test].
  - B3, the submission ABI: [FIXED v2, §4.1 single-file ABI, shim plus contract fixture, a precise
    `check_submission` scope].
  - B4, no real-race acceptance: [FIXED v2, §1.3 proxy plus §7.3 author qualification].
  - S5, the respawn rule and season pin: [FIXED v2, §1.1–§1.2 Summer 2026 / Fall 2026 season, respawn at start].
  - S6, falsifiable gates: [FIXED v2, §6 gate policy, U9/U10, measurement in U1, empirical μ in U7].
  - S7, lab and budget definitions: [FIXED v2, §7.1 budgets, §7.2 `lab-check`].
  - N8, buildout is a flag: [FIXED v2, §3].
  - N9, auditable licensing: [FIXED v2, §7.4].
- **[fable]** APPROVE WITH NITS:
  - M1, respawn: [FIXED v2, §1.2, §4.2].
  - M2, tick counts: [FIXED v2, §4.2, §7.1].
  - M3, MPC cost: [FIXED v2, U10 LTV least squares, p99 budget].
  - M4, the capstone rule: [FIXED v2, U13].
  - M5, sync `run_race`: [FIXED v2, §4.2].
  - S6, ci-local specifics: [FIXED v2, §7.1].
  - S7, buildout: [FIXED v2].
  - S8, longitudinal map: [FIXED v2, §4.4].
  - S9, spin-out: [FIXED v2, §4.2, U6].
  - S10, gitignore: [FIXED v2, §7.2].
  - S11, "unseen for tuning": [FIXED v2, §4.3].
  - N12, provenance: [FIXED v2, §7.4].
  - N13, the API list grows per plan: [FIXED v2, §7.1].
  - N14, `lab-check` is load-bearing and excluded from publish and site: [FIXED v2, §7.2].
  - N15, the U1 gate is concrete: [FIXED v2, §6].
  - Probe evidence: 0.17–0.18 ms/tick; monza-like profile ≈ 2× faster than fixed 20 m/s; scipy MPC 91–293 ms/tick
    vs LTV least squares 0.167 ms/tick.

### Round 2 (v2 @ f6fc342)
- **[sol]** REJECT on r1 B2 only. B1, B3, B4, S5, S6, S7, N8 and N9 were verified RESOLVED.
  - B2, the API-order test is disjoint from `concept-scan`: [FIXED v3, §7.1, the two-layer scheme].
  - S1, the qualification stopping rule: [FIXED v3, §7.3].
  - S2, generator ordering: [FIXED v3, §4.3 single driver].
  - S3, the lab data path: [FIXED v3, §7.2 `ROAR_LAB_CSV`].
- **[fable]** APPROVE WITH NITS. All round-1 items were verified RESOLVED; its shim probe confirmed both sync
  `run_race` paths.
  - F1 MUST, the Python 3.8 runtime: [FIXED v3, §1.1, §2, §4.1].
  - F2, shim lifetime and loading: [FIXED v3, §4.1].
  - F3, generator order: [FIXED v3, §4.3].
  - F4, the p99 tick check: [FIXED v3, §4.1].
  - F5, `api-order.yaml` as a map with derived order: [FIXED v3, §7.1].
  - F6, interim CARLA checks and Windows-only Monza: [FIXED v3, §1.1, §7.3].
  - F7, the U7 one-knob sweep: [FIXED v3, §6].
  - F8, the lab path: [FIXED v3, §7.2].
  - F9, the number is not unique: no change.
  - F10, the per-tick target: [FIXED v3, §7.1].
- **[self]** APPROVE.

### Round 3 (v3.1 @ e40b9cf)
- **[sol]** REJECT. B2, S1, S2 and S3 were verified RESOLVED.
  - New B1, the 3.8 run is impossible under the repo's `requires-python`: [FIXED v4, §4 racekit is 3.8-compatible,
    plus the isolated `--no-project` command with version asserts].
  - S2, alias and `from`-import resolution plus the reverse check: [FIXED v4, §7.1].
  - N3, version labels: [FIXED v4].
- **[fable]** APPROVE WITH NITS. All round-2 items were verified RESOLVED; it judged the v3.1 non-blocking interim
  policy acceptable. uv feasibility was confirmed: Python 3.8.20 with numpy 1.24.4 and scipy 1.10.1, about 3 s warm.
  - M1, 3.8 executability: [FIXED v4, option (a)].
  - S2, call granularity and taught numpy math: [FIXED v4].
  - S3, scan scope: [FIXED v4].
  - S4, PENDING as a named risk, §8 wording, the site flag: [FIXED v4, §3, §7.3, §8].
  - N5, the universal 5 ms p99: [FIXED v4].
  - N6, the hook seed and checksums: [FIXED v4].
  - N7, host failure: [FIXED v4, §7.3].
  - N8, deny-list breadth: [FIXED v4, §4.1].
  - N9, ruff: [FIXED v4, §7.1].
- **[self]** APPROVE.

### Round 4 (v4 @ b4db74c): CONSENSUS
- **[sol]** APPROVE. B1, S2 and N3 were RESOLVED, with no new findings.
- **[fable]** APPROVE WITH NITS in round 3. All of its nits were folded in v4.
- **[self]** APPROVE.

## 10. Revision history
- v1 (2026-10-25): the initial draft from the author-agreed brainstorming sections 1–5.
- v2 (2026-10-25): folds round 1, and re-grounds the race in the Summer 2026 reports. Changes:
  - respawn at the start;
  - the single-file submission ABI with a shim;
  - the reasonable-ranking proxy and author qualification;
  - U13 becomes an integration unit;
  - falsifiable line and MPC gates;
  - measurement in U1 and empirical μ in U7;
  - LTV MPC;
  - the API-order test;
  - `lab-check`;
  - the budgets made precise;
  - the provenance record.
- v3 / v3.1 (2026-10-25): folds round 2; v3.1 makes the interim CARLA checks non-blocking. Changes:
  - two-layer API ordering;
  - the Python 3.8 / numpy < 1.25 submission target;
  - the shim's lifetime and loading;
  - a single generator driver;
  - the p99 tick check;
  - interim CARLA checks;
  - the qualification stopping rule;
  - `ROAR_LAB_CSV`;
  - the U7 one-knob sweep.
- v4 (2026-10-25): folds round 3. Changes:
  - `racekit` is Python 3.8-compatible, with an isolated `--no-project` 3.8 run;
  - alias-aware API-order resolution, the reverse check, and the full scan scope;
  - interim checks become named risks;
  - the site flag moves to `roar-014`;
  - the universal p99 budget, host-failure handling and a wider deny-list.
- v4.1 (2026-10-26): factual correction from the roar-001 content gate ([fable] M1, verified against
  `ab19e1b`). Respawn resets progress to 0 after a 20-step hold, and the finish uses a 5-waypoint margin.
- v4.2 (2026-10-26): the §6 Unit 2 hook is reframed (plan `roar-003`, [fable] N6). On racekit's kinematic car the
  starter neither wobbles nor cuts corners (probe: steer sign flips ≤ 0.08/s, max |offset| ≤ 0.85 m, all clean), so
  the hook asks where the car is and what is coming; wobble and corner-cutting arrive with grip in Unit 6.
- v4.3 (2026-10-26): the §6 Unit 5 gate is restated (plan `roar-005`). On racekit's lag-free kinematic car pure pursuit
  does not beat Unit 4's PD-plus-feedforward (it cuts corners); with a 2-tick actuator delay at 30 m/s it is clean where
  Unit 4's gains and Stanley crash, and it beats a detuned PD that also survives. The gate pins both halves, and the
  Unit 5 lab lets CARLA decide.
- v4.4 (2026-10-27): the §6 Unit 7 row and the §7.1 routed budget (plan `roar-006`). Probes show that the planned
  braking rate decides how much cornering speed is safe, and that a waypoint-count lead does not transfer; Unit 7 reads
  A_LAT and A_DEC together as a grid and follows the profile with a lead in seconds. Per-section "μ" is taught as
  per-section speed knobs (they absorb the planner's other errors; Unit 8 measures μ), accepted under a clean rule
  (finished, 0 collisions, max cross-track error ≤ 2 m). The routed pytest budget is 8 min on an 8-core CI machine.
- v4.5 (2026-10-27): §4.3 and the §6 CP-A row (plan `roar-007`). The Unit 7 reference, tuned on `test-circuit` alone,
  crashes on every run of a seeded variant; one setting tuned on a family of four variants and `test-circuit` under
  the clean and margin rules is clean there. Checkpoint A pins the training family (seeds 1–4), the checkpoint track
  (seed 2026, named before it was probed) and a 330 s racekit target.
- v4.6 (2026-10-27): the §7.1 notebook exec budget (plan `roar-007`). The first book-level measurement, at the end of
  Part 1, is 20.4 min serial (load 3.1–3.8 on a shared 8-core machine): 17.7 min for Units 1–7, measured by no earlier
  plan, and 2.6 min for Checkpoint A's solutions. The Unit 5 and Unit 4 milestones (3.8 and 2.1 min) are the largest
  items. The budget is raised to 30 CI-minutes for Part 2 and the capstone, rather than cutting merged units' gates.
- v4.7 (2026-10-28): the §6 Unit 8 and Unit 9 rows and the §7.1 routed budget (plan `roar-008`).
  - Unit 8: the generated logs cannot identify per-section μ; limit probes (one section pushed per race, the student's
    own agent as the driver) estimate it within 3% where the probe slid. The steering gain (70° assumed, 65.7° measured)
    matters as much as μ: it is what limited `monza-like`. One fraction of the measured grip, tuned on the training
    family, races the unseen track 7.5 s faster than Checkpoint A.
  - Unit 9: a direct curvature objective does not race (its line swings across the straights), so the line is the
    smoothest one, on a cubic B-spline of offsets; it lowers the total squared curvature by 19–41% and buys about 25 s
    on `test-circuit`. Local widening, as built, loses. Submissions import only numpy, so the line is solved offline
    and shipped as control values.
  - The routed pytest budget rises to 10 min: the third raise (5 → 8 → 10 min), each for a part's gates.
