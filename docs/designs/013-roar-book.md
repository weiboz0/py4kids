# Design 013 — "Applied Python: Autonomous Racing" (a new advanced book for the Berkeley ROAR series)

**Status:** DRAFT, v1 (2026-10-25).
It proposes a new, self-contained book, `roar`, whose purpose is tutorial material that lets a strong student
**reach a reasonable ranking in the Berkeley ROAR Simulation Racing Series**.
The design was agreed section by section with the author on 2026-10-25 (brainstorming).
It is the input to this design's 3-way review gate, and then to the first plan, `roar-001`.
Plans for this book live under `docs/plans/roar/` (`roar-NNN`). `tools/guard.py` already guards namespaced plan
directories, so no guard extension is needed.

## 1. Why

ROAR (Robot Open Autonomous Racing, UC Berkeley FHL Vive Center) runs a **Simulation Racing Series** every semester
for high-school students.
Competitors write a Python agent that drives a simulated Tesla Model 3 around the **Monza** map (v1.1 for Spring
2026) in the CARLA simulator, through the `ROAR_PY` interface.
The published winning solutions are **classical control engineering**, not learned policies:
- waypoint following;
- pure-pursuit or PID steering;
- speed limits from path curvature and a per-section friction estimate;
- racing-line smoothing.

No py4kids book teaches control, vehicle dynamics or optimization.
This book does, with one measurable goal: an agent that ranks well.

**Facts about the real race** (verified from `augcog/ROAR_Competition` `competition_runner.py`,
commit `ab19e1b`):
- The race is **3 laps**, scored on **total elapsed sim time**.
- The control step is **0.05 s**, with 0.005 s physics substeps, and the world is **synchronous**.
- Progress is the furthest waypoint reached.
- A **major collision** (impulse norm > 100) **respawns** the car at its last progress point. It costs time but does
  not disqualify.
- There is a timeout (`max_seconds`).
- The agent is a `RoarCompetitionSolution` with `async initialize()` and `async step()`.
  It reads sensors through `get_last_gym_observation()` and acts through
  `await vehicle.apply_action({"throttle", "steer", "brake", "hand_brake", "reverse", "target_gear"})`.
- The official starter agent steers with a P controller toward the waypoint 3 ahead, and holds a speed target of
  20 m/s with a P controller.

## 2. Audience and baseline (the per-book declared baseline, AGENTS.md "Self-containedness is law")

- **Audience:** strong high-school programmers with **competitive-programming experience** (Python or C++) who have
  **studied calculus**. Every student can run the real ROAR stack (the CARLA Monza executable plus `ROAR_PY`) on
  their own machine (author decision, 2026-10-25).
- **Assumed math:** single-variable calculus (derivatives, integrals, the chain rule, Taylor expansion to first
  order), trigonometry, and 2-D/3-D vectors with the dot product.
  **Taught in-book, because they are not assumed:** matrices as linear maps, linear least squares, linearization,
  discrete-time systems, and constrained optimization at the level `scipy.optimize` exposes.
- **Assumed programming:** Python fluency (classes, `async`/`await` *usage*, comprehensions, modules) and **numpy
  fluency** (arrays, broadcasting, vectorized math). These are declared assumed-baseline concepts in the book's
  `baseline.yaml`, and they earn no teaching credit.
- **Libraries:** numpy (assumed), and **scipy** (`optimize`, `interpolate`) and **matplotlib**, both
  **taught before assessed**.
  CARLA and `ROAR_PY` are **never** imported by CI-executed notebooks (§7).
- **Retained laws (normative):** the declared baseline overrides only the audience, the assumed math and the named
  libraries. Every other law holds:
  - prereq closure;
  - practice coverage, including the capstone rule;
  - taught-before-assessed;
  - project-first hooks;
  - student-notebook hygiene;
  - a stretch exercise per unit;
  - `teacher-notes.md` per unit;
  - checkpoints that are strict (no borrowed tools).

## 3. Book identity and registry

- **id / root / folder:** `roar`. The id is unused; there is no collision with the `recsys` or `acsl` namespaces.
- **number:** `3` (display ordinal only), in the "Applied Python: …" series with recsys.
- **title:** "Applied Python: Autonomous Racing".
  **subtitle:** "Build a competitive ROAR agent, from waypoints to optimal control".
- **depends_on:** `[python-projects]`, matching recsys. In practice the declared baseline (§2) supplies the
  prerequisites.
- **dependency_group:** `roar`: numpy, scipy, matplotlib, and the editable `racekit` package. There is no torch.
- **flags:** `publication` and `site`, set by the plan that first makes each one pass (not necessarily `roar-001`).
- **lesson_budget:** `[30, 50]` as a whole-book total: 13 units at 2–3 sittings each.
  The first plan sizes `lessons` with a buildout entry until the total reaches the minimum, as recsys did.

## 4. The simulator: the `racekit` package (approach 3, "own sim + calibration")

`roar/projects/racekit/racekit/` is an importable package, the analogue of recsys's `bookrec`. It is installed
editable through the `roar` group and tested by a routed pytest suite. It depends only on numpy and scipy.

### 4.1 The interface is shaped like `ROAR_PY`
- `racekit` provides objects with the **same names, signatures and semantics** as the real interface:
  - the waypoints (`.location` is an (x, y, z) array; `.roll_pitch_yaw`);
  - sensors with `get_last_gym_observation()`: location, roll-pitch-yaw, velocity and collision;
  - a vehicle with `async apply_action(dict)`, using the same keys, ranges (`throttle`/`brake` in [0, 1], `steer`
    in [−1, 1]) and **sign conventions** as the starter (a positive heading error steers negative).
- A student's `RoarCompetitionSolution` file runs **unchanged** in `racekit.run_race(...)` and in the real
  `competition_runner.py`.
- The interface is re-implemented from its documented behaviour. **No ROAR source is copied:**
  - `ROAR_PY` is MIT-licensed, so it may be referenced and linked;
  - `ROAR_Competition` carries **no licence**, so its files are neither copied nor vendored. The book's own starter
    agent re-implements the described baseline behaviour.

### 4.2 Race rules, mirrored
- `racekit.run_race(agent_cls, track, car, laps=3, max_seconds=...)` drives the asyncio loop.
- It runs a fixed control tick of 0.05 s with 10 physics substeps.
- It tracks progress by the furthest waypoint, as the real rule does.
- Leaving the track's drivable width is a **major collision**. It **respawns** the car at its last progress point,
  stationary, so it costs time as in the real series.
- It returns the total time, completion, collision and respawn counts, the time spent off the line, per-sector splits
  and the full telemetry (one row per tick).
- These are labelled as an **approximation** of the real rules wherever they are taught.

### 4.3 Tracks are generated by seeded scripts, never copied
- `roar/data/gen_tracks.py` builds closed centrelines from segment specs: straights, constant-radius arcs and
  clothoid transitions with continuous curvature, with a drivable width.
- It emits waypoints at about 2 m spacing (like ROAR's `maneuverable_waypoints`).
- It writes generated outputs with sha256 entries in `checksums.json`. The outputs are gitignored, regenerated in CI
  and byte-stable.
- It ships these tracks:
  - `oval` (Units 1–4);
  - `test-circuit` (mixed corners and a chicane);
  - `monza-like`, built from public facts about the circuit: about 5.8 km, long straights, the Rettifilo and Roggia
    chicanes, the two Lesmo corners, Ascari, and the Parabolica (Alboreto) corner. It is labelled **"inspired by
    Monza"**, not a copy of the CARLA map.
  - **hidden checkpoint tracks** (§6), generated from fixed seeds that the checkpoints name.
- The real CARLA map and its waypoints are **never** committed or redistributed.

### 4.4 Car models, each taught before it is used
1. **Kinematic bicycle** (Unit 3): position, heading and speed. The steering angle sets the yaw rate through the
   wheelbase.
2. **Dynamic bicycle** (Unit 6 onward):
   - lateral tyre forces with a saturating tyre curve and a **friction circle**, so the car slides if it demands
     more grip than μ allows;
   - longitudinal force from a throttle map;
   - brake force and aerodynamic drag;
   - a steering-rate limit and one to two ticks of actuator lag.
3. **The "carla-like" ground-truth car:** a dynamic-bicycle parameter set with **section-varying friction**, used as
   the stand-in for CARLA. Its parameters live in a `racekit._truth` module that students are told not to read.
   Exercises access the car only through `racekit.cars.carla_like()`. A seeded script records **telemetry logs**
   from it. In Unit 8 students **identify** its parameters from those logs. In the real-sim lab they repeat the
   identification on **their own CARLA logs**.

### 4.5 Determinism and honesty
- Pure numpy, fixed tick, fixed seeds; there is no wall-clock dependence (`step()` timing is measured but never
  affects the simulation).
- Lap times are gated with **tolerances** (`allclose`). Comparisons ("A beats B") require a margin larger than the
  measured seed-to-seed spread over at least 3 perturbed-car seeds. This is the §184 tolerance/rank rule from recsys,
  never an exact float.
- Every unit that reports a racekit number says that it is a **model** number. Gains, μ and lap times must be
  **re-measured on CARLA**. Unit 8 teaches how.

## 5. Project architecture: one agent, upgraded unit by unit

- The student builds **one agent** across the book.
- `racekit` holds the infrastructure plus a library of reusable, tested building blocks, so later units can import
  earlier units' work:
  - `geometry` (frames, nearest waypoint, cross-track error, curvature);
  - `control` (PID, pure pursuit, Stanley);
  - `planning` (speed profile, racing line);
  - `sysid` (fits);
  - `mpc`;
  - `tuning`.
- A module enters `racekit` **in the plan of the unit that teaches it**, never before. Notebooks use only modules
  whose concepts are taught (prereq closure).
- Each unit's project milestone is a **milestone notebook** at `roar/projects/racekit/milestones/unit-NN-<slug>.ipynb`.
  It integrates the unit's upgrade into the agent, runs a race, and **asserts the unit's measured gate** (§6).
  Milestones run under `exec-solutions`, exactly as recsys's do.
- The single `projects/` registry entry is the **capstone** (§6). The tooling treats a `projects/` entry as the
  capstone (every concept must be practised by a non-capstone entry), so it is authored **last**.

## 6. Structure: three parts, two checkpoints, a capstone

Every unit ships these files:
- `lesson.ipynb` (opens with its racing **project hook**);
- `exercises.ipynb` (with at least one `stretch` Challenge);
- `solutions.ipynb`;
- `teacher-notes.md`;
- `manifest.yaml`.

🏁 marks a unit with a **real-sim lab** (§7.2).
**Gates** are directional here. Each unit plan pins exact numbers from a pre-implementation probe; a miss means stop,
amend the plan and re-gate.

### Part 1: A car that finishes laps

| # | Unit | Project hook | Teaches | Gate (direction) |
|---|---|---|---|---|
| 1 | The race and the baseline 🏁 | "Here is the starter agent. How fast is it, and where does it lose time?" | Race rules; the agent interface; the async step loop; telemetry; sector splits | The baseline completes `oval` and `monza-like`; its time is reported |
| 2 | Geometry of a track | "Why does the baseline cut corners and wobble?" | Frames, heading, `atan2`, angle wrapping; windowed nearest-waypoint search; cross-track error; Menger curvature | Functions match analytic circles within tolerance |
| 3 | Modelling the car | "Predict where the car is in 1 s." | Kinematic bicycle; Euler vs RK integration; timestep error | Circle radius matches the analytic one; RK error < Euler error |
| 4 | PID control | "Hold 20 m/s, then follow the line." | P/I/D; discrete PID; windup; step-response tuning; steering from heading error | Overshoot and settling time in bounds; cross-track error < baseline |
| 5 | Geometric steering 🏁 | "Steer like a driver looks ahead." | Pure pursuit; speed-scaled lookahead; Stanley; the stability vs corner-cutting trade | Pure pursuit beats PID-heading on cross-track error at speed |
| 6 | Grip and the speed limit | "Why does the car spin at Parabolica?" | Dynamic bicycle; tyre saturation; the friction circle; v_max = √(μg/κ) | Curvature-limited speed eliminates collisions on `test-circuit` |
| 7 | Speed profiles 🏁 | "Brake *before* the corner." | Forward–backward pass under acceleration and braking limits; lookahead speed planning | A large race-time gain over Unit 6 with zero collisions |
| CP-A | **Checkpoint A** | A complete classical agent on an unseen seeded track | strict | Finishes a hidden track within a target time |

### Part 2: Measuring the real car

| # | Unit | Project hook | Teaches | Gate |
|---|---|---|---|---|
| 8 | System identification 🏁 | "Your sim-tuned agent is slow, or crashes, on CARLA. Why?" | Logging; matrices and linear least squares (taught here); fitting steering gain, drag and grip; residuals; per-section μ | The carla-like car's parameters are recovered within tolerance |
| 9 | The racing line | "The centreline is not the fast line." | Width constraints; minimum-curvature line as an optimization (`scipy.optimize`); spline smoothing | Lower Σκ² and a faster race than the centreline |
| 10 | Model predictive control 🏁 | "Plan the next 2 s, every tick." | Linearization; discrete-time model; horizon cost; constrained optimization; receding horizon; the compute budget per tick | Tracks the racing line with lower error than pure pursuit at higher speed |
| 11 | Robustness | "One bad tick ends your race." | Recovery after a respawn; fallback controller; testing across seeds and perturbed parameters | Completes N/N perturbed-parameter races |
| CP-B | **Checkpoint B** | A full agent under parameter uncertainty | strict | Completes and times hidden perturbed races |

### Part 3: Going fast

| # | Unit | Project hook | Teaches | Gate |
|---|---|---|---|---|
| 12 | Tuning against race time | "You have 12 knobs. Which ones matter?" | Race time as a black-box objective; grid, random and coordinate search; a simple evolution strategy; overfitting to one track; held-out tracks | A tuned agent beats the hand-tuned one on a **held-out** track |
| 13 | Race-day engineering 🏁 | "Make it work on the organisers' machine." | Packaging the submission; profiling `step()` against the tick; determinism; a pre-submission checklist; version pinning | The submission passes `racekit.check_submission` and the timing budget |
| Capstone | **Your competition agent** (`project-14-…`) | Build, tune and justify the agent you submit | Integrates everything; an engineering report with an **ablation table** (race time bought by each stage) | The reference solution beats the starter baseline by a pinned margin on `monza-like` with zero collisions |

Unit 12's Challenge may include an **optional** reinforcement-learning taste: a policy-gradient tune of one
parameter, compared honestly with search. Deep RL is not core, because it is not what wins this series.

## 7. Verification and the bridge to CARLA

### 7.1 What CI proves (`scripts/ci-local.sh`, plus the routed `uv run --group roar` suite)
- **`racekit` tests:**
  - the **interface contract** against `ROAR_PY`: names, async signatures, action keys, ranges and signs;
  - analytic car-model checks: circle radius, friction-circle bounds, integrator order;
  - generator **byte-stability** (`checksums.json`);
  - runner timing, respawn and progress accounting, on scripted agents.
- **Notebooks:** every lesson, solution, milestone, checkpoint and capstone notebook executes clean. Each unit's gate
  is an `assert` in its milestone notebook, pinned from a pre-implementation probe.
- **The standard laws:** manifest, prereq, coverage (including the capstone rule), hygiene, stretch, cell-lint and
  concept-scan. The `racekit`, scipy and matplotlib APIs that students call are declared in `baseline.yaml`
  `library_methods`.
- **Budgets** (measured targets; an overrun means stop and amend):
  - book notebook exec ≤ **15 CI-minutes** (`exec-lessons` + `exec-solutions` wall time, with the load recorded);
  - routed pytest ≤ **5 min**;
  - the per-cell 120 s cap is retained.
  A 3-lap race on `monza-like` is about 3,500 ticks, and the target is ≤ 3 s per race in pure numpy. MPC (Unit 10)
  is the budget risk: its plan must pin the horizon and solver iterations from a probe.

### 7.2 What CI cannot prove: the real-sim labs
- 🏁 units ship `labs/real-sim.ipynb`, labelled "runs on your machine with CARLA and `ROAR_PY`".
  - CI does not execute it: `exec-lessons` and `exec-solutions` discover only lessons, solutions, milestones,
    checkpoints and projects.
  - Every cell that needs CARLA also carries the existing `no-exec` cell tag.
  - `roar-002` adds a lab check: the lab exists for each 🏁 unit, it is clean (no outputs), its CARLA cells are
    tagged, and its analysis cells run on a seeded **sample CSV** that racekit generates. This keeps the analysis code
    under CI even though the CARLA run is not.
- Each lab gives exact steps:
  1. start the Monza executable;
  2. put the agent file in the competition folder;
  3. run `competition_runner.py`;
  4. export telemetry to CSV;
  5. analyse it in the lab notebook.
- **`racekit.check_submission(path)`** checks a student's agent file statically (imports only what the competition
  environment provides) and dynamically (one racekit race). It catches the code that works in the sim but not on
  CARLA.
- **No student data in the repo (the repo is PUBLIC):** lab outputs (times, telemetry, fitted parameters) stay on the
  student's machine. `.gitignore` covers `roar/**/labs/**/telemetry*.csv` and `roar/**/labs/**/results*`. Teacher
  notes say so.
- **Version pinning:** the book names the `ROAR_PY` commit (`3cbb087`), the `ROAR_Competition` commit (`ab19e1b`)
  and the Monza map version (v1.1) it was written against. Unit 13 says what to re-check when the series updates them.
- **No predictive claims:** student-facing text never claims that a racekit time predicts a CARLA ranking. The claim
  is structural: the same pipeline, then re-measured and re-tuned on CARLA.

## 8. Build sequence (one plan each, full lifecycle)

| Plan | Ships |
|---|---|
| design 013 (this doc) | The design, through the 3-way gate (docs-only) |
| `roar-001` foundation | `books.yaml` entry; `roar/` skeleton (syllabus, curriculum, baseline, concepts); the `roar` dependency group; `racekit` core (interface, kinematic car, runner, telemetry, `check_submission`); `gen_tracks.py` (oval, test-circuit, monza-like) with checksums; routed pytest; ci-local wiring; `.gitignore` for labs. No units. |
| `roar-002` | Unit 1, the real-sim lab mechanism and the first lab |
| `roar-003` | Units 2–3 |
| `roar-004` | `racekit` dynamic car, the carla-like truth car and the telemetry generator (infrastructure plus probes) |
| `roar-005` / `roar-006` | Units 4–5 / Units 6–7 |
| `roar-007` | Checkpoint A |
| `roar-008` … `roar-010` | Units 8–9 / Unit 10 / Unit 11 |
| `roar-011` | Checkpoint B |
| `roar-012` / `roar-013` | Unit 12 / Unit 13 |
| `roar-014` | Capstone, publication and site flags |

Unit pairings may be adjusted by each plan's gate. A pairing change is not a design change.

## 9. Out of scope
- The **physical-car** ROAR series.
- Camera perception and computer vision: the competition supplies waypoints and pose sensors. The camera sensor is
  mentioned, not taught.
- Deep RL as core content (Unit 12 has an optional Challenge only).
- Copying or redistributing ROAR or CARLA code, maps or waypoints.
- Real student results in the repo.
- Governance edits: none are needed. AGENTS.md already permits a per-book declared baseline, and the content gate's
  audience duty already reads "per the book's declared baseline".

## Design Review

(Pending: 3-way gate [self] / [sol] / [fable].)

## 10. Revision history
- v1 (2026-10-25): the initial draft from the author-agreed brainstorming sections 1–5.
