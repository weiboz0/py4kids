# Plan roar-001 — Foundation: registry, `racekit` core, seeded tracks, CI wiring

**Design:** `docs/designs/013-roar-book.md` (v4, gate CLOSED). **Autopilot** per AGENTS.md (the author set the whole
book to autopilot on 2026-10-25, with questions recorded as follow-ups).
This is the foundation for the advanced `roar` book: **registration, scaffolding, the `racekit` harness core, the
seeded track generator, the routed test suite and the ci-local wiring.**
It ships **no student units, projects or checkpoints** (those start in `roar-002`), and **no ROAR_Competition code,
CARLA map or waypoint data.**

## Goal
A registered, CI-green `roar` book in **buildout** state, with:
- an isolated `roar` dependency group;
- a Python 3.8-compatible `racekit` package containing:
  - the `roar_py_interface` shim with its MIT contract fixture;
  - the synchronous race runner with the real progress and respawn rule;
  - the kinematic bicycle car with a longitudinal map;
  - telemetry and `measure`;
  - `check_submission`;
- seeded, byte-stable tracks (`oval`, `test-circuit`, `monza-like`) produced by a single `generate.py` driver;
- the routed guard tests the design requires (API order, deny-list, labs-tracked, the isolated 3.8 run);
- the provenance record.

`roar-002` and later plans can then author units against a working substrate.

## Global constraints
- **Determinism:** one `numpy.random.default_rng(seed)` per generator, `PYTHONHASHSEED=0`, fixed float formatting,
  and checksummed outputs. Gates use tolerances, never exact floats (§184).
- **`racekit` targets Python ≥ 3.8 and numpy < 1.25 compatibility** (design §4): `from __future__ import annotations`
  everywhere; no 3.9+ syntax or APIs; the core imports numpy only.
- **No copied upstream code:**
  - `ROAR_Competition` has no licence, so nothing is copied from it;
  - the only `ROAR_PY`-derived artifact is the contract fixture, which carries the MIT notice;
  - CARLA maps and waypoints are never committed.
- **The repo is PUBLIC:** no student data; lab outputs are gitignored and a test enforces it.
- Never run `uv` from inside `roar/projects/racekit` (it would create a stray `uv.lock`).

## Phases

### Phase A — registry and skeleton (buildout)
- `books.yaml`:
  - `id: roar`, `number: 3`, `root: roar`;
  - title "Applied Python: Autonomous Racing", subtitle "Build a competitive ROAR agent, from waypoints to optimal
    control";
  - `depends_on: [python-projects]`, `lesson_budget: [30, 50]`;
  - **`buildout: true`**, `dependency_group: roar`;
  - no feature flags (`site` and `publication` come in `roar-014`).
- Create `roar/`:
  - `syllabus.md`: the three-part arc in prose. It does **not** backtick future `unit-NN` ids, because
    `syllabus_findings` would treat them as stale rows.
  - `curriculum/concepts.yaml`: **one seed concept**, `roar-race-and-submission` ("The ROAR race and its submission
    interface"), globally unique, so `concept_minimum` is met.
  - `curriculum/coverage-map.yaml`: `map_version: 1`, `entries: []`.
  - `curriculum/baseline.yaml`: the assumed ids (advanced Python: classes, modules, comprehensions, async usage,
    exceptions, type hints; numpy fluency; calculus, trigonometry, vectors), plus `library_methods` with only the
    infrastructure names `roar-002` needs, starting empty except for what this plan's tests require.
  - `curriculum/api-order.yaml`: `api_order_version: 1`, `infrastructure: []`, `taught: {}`.
  - `reference/upstream.md`: design §7.4.
  - `docs/` (with a README), plus `units/`, `projects/` and `checkpoints/`, each with a `.gitkeep`.
- `tests/test_books.py`:
  - the id list gains `roar`;
  - the title and subtitle are asserted;
  - the `number` list becomes `[1, 1, 2, 2, 3, 3]`;
  - the dependency-group assertion becomes `{"recsys", "roar"}`, with `roar`'s value asserted;
  - buildout is asserted on `roar`.
- `output/README.md` gains an `## output/roar/` section.
- **Naming:** the roar docs name other books by their titles, never "Book 1/2" (`tests/test_book_ids.py`).

**Verify:** ci-local's registry, structure and curriculum steps pass for `roar` in buildout; `build-pdf.sh` builds
`output/roar/syllabus.pdf` over zero units.

### Phase B — dependency group and CI wiring
- `pyproject.toml`:
  - a `[dependency-groups] roar` entry with `numpy`, `scipy`, `matplotlib` and `racekit`;
  - `[tool.uv.sources] racekit = { path = "roar/projects/racekit", editable = true }`;
  - a regenerated `uv.lock`, from the repo root only.
- `scripts/ci-local.sh`:
  - add `roar/projects/racekit roar/data` to the ruff paths;
  - in the routed loop, **if `$book/data/generate.py` exists**, run `PYTHONHASHSEED=0 uv run --group "$grp" python
    "$book/data/generate.py"`, else keep recsys's `gen_catalog`/`gen_interactions` branch unchanged;
  - recsys's behaviour must be byte-identical.
- `.gitignore`:
  - `roar/data/generated/`;
  - `roar/**/labs/**/*.csv`, `*.json`, `*.npz`, `*.parquet`, `*.log`, `*.png`.

**Verify:** the exact `uv sync` (no group) followed by the group-free `tests/` run still passes; the routed roar step
runs; recsys's routed step is unchanged.

### Phase C — seeded tracks (`roar/data/`)
- `roar/data/tracks.py` (library) and `roar/data/generate.py` (driver):
  - segment specs: straight, constant-radius arc, and clothoid (linear curvature) transitions;
  - integrate the centreline by curvature;
  - a **closure correction** that distributes the endpoint error so the track closes with continuous heading;
  - resample at 2.0 m spacing;
  - a per-waypoint drivable half-width;
  - write `roar/data/generated/tracks/<name>.npz` (x, y, z = 0, yaw, half-width, s, curvature) plus `checksums.json`.
- Tracks:
  - `oval`: two 300 m straights and two 120 m-radius arcs;
  - `test-circuit`: mixed radii, a chicane and a hairpin, about 2.5 km;
  - `monza-like`: about 5.8 km, built from public layout facts (main straight, Rettifilo chicane, Curva Grande,
    Roggia chicane, the two Lesmo corners, Serraglio, the Ascari chicane, the back straight, Parabolica). The module
    docstring says it is **"inspired by Monza"** and not the CARLA map.
- The driver verifies byte-stability by generating twice and comparing sha256. It supports `--check` (the CI mode),
  which fails on any mismatch with the committed expectations in `roar/data/expected-checksums.json`. That file is
  tracked and small: hashes only, no data. It lets CI detect accidental generator drift.
- **Tests (`roar/data/tests/`):**
  - closure: the last-to-first gap is under 2.5 m, and the heading is continuous within 1°;
  - spacing within 2.0 ± 0.05 m;
  - curvature matches the specs on arcs (±2%);
  - lengths in the stated windows;
  - determinism: two runs are byte-identical;
  - no self-intersection: segment-pair checks on a downsampled line.

**Verify:** routed tests green; generation takes ≤ 10 s.

### Phase D — the `racekit` core (`roar/projects/racekit/`)
The package `pyproject.toml` (hatchling) declares `requires-python = ">=3.8"` and `dependencies = ["numpy"]`, with
`scipy` and `matplotlib` as an optional `analysis` extra. Modules:

- **`racekit/roar_py_interface.py` (the shim):**
  - `RoarPyWaypoint`;
  - sensor classes with `get_last_gym_observation()` (location, roll-pitch-yaw, velocity, collision with
    `.impulse_normal`), plus the camera and occupancy stubs;
  - `RoarPyActor` with `async apply_action(dict)` that **validates** keys, types and ranges and raises
    `ValueError`;
  - all of it per design §4.1, written from the gitbook documentation and the observed behaviour (clean room).
- **`racekit/contract/roar_py_contract.json` plus `LICENSE-ROAR_PY` (MIT):** the class and method names, the async
  flags and parameter names from `ROAR_PY` at commit `3cbb087` that the competition surface uses. The fixture
  records the commit, the file paths and the licence. Generate it with a throwaway script that reads a local
  checkout in the scratchpad. The script is not committed; the fixture's header records the procedure.
- **`racekit/tracks.py`:** loads a generated track as waypoints (`RoarPyWaypoint` list); provides track-relative
  queries (offset from the centreline, progress s) for the runner.
- **`racekit/cars.py`:** the `KinematicCar` (kinematic bicycle with wheelbase L; steer `[-1, 1]` mapped to `δ =
  -steer·δ_max`, so the sign convention matches the starter; throttle → acceleration through a simple map; brake →
  deceleration; quadratic drag; RK4 substep integration) and a `Car` protocol, so `roar-004` adds the dynamic and
  carla-like cars.
- **`racekit/runner.py`:**
  - `run_race(submission, track, car=None, laps=3, max_seconds=..., seed=0) -> RaceResult`, **synchronous**:
    - a fresh event loop when none is running, otherwise a worker thread with its own loop;
    - a 0.05 s control tick with 10 substeps;
    - each tick runs `await agent.step()`, then advances the car (the official order);
  - **progress** follows the real rule: segment projection inside a forward window of 15 waypoints over the
    tripled waypoint list;
  - **major collision:** `|offset| > half-width`, which **respawns at the start pose** with zero velocity and
    retains progress;
  - `RaceResult` holds: `finished`, `total_time`, `collisions`, `time_lost_respawn`, `sector_splits`, `telemetry`
    (a structured numpy array: t, x, y, yaw, v, throttle, steer, brake, progress, offset) and `step_ms` (per-tick
    compute).
  - **The shim lifetime:**
    - install `racekit.roar_py_interface` in `sys.modules["roar_py_interface"]` for the whole call;
    - refuse when a different real module is already importable or installed;
    - restore afterwards;
    - load the submission with `spec_from_file_location` under a unique module name.
  - `run_race` also accepts an agent **class** for in-notebook agents (the lesson path).
- **`racekit/measure.py`:** `repeat_races(submission, track, n, seeds)` → median, spread (IQR and max−min) and
  per-run results; `noise_aware_better(a_times, b_times)`, the documented rule (median difference > max(spread_a,
  spread_b)).
- **`racekit/telemetry.py`:** a CSV export and import with a fixed column schema. The same format is used for the
  real-sim lab sample later.
- **`racekit/check_submission.py`** (also `python -m racekit.check_submission <file>`):
  1. a 3.8 AST parse plus the deny-list (design §4.1, including the annotation-position checks);
  2. the import allow-list (stdlib, `numpy`, `roar_py_interface`, `typing`) and the official class and constructor
     signature;
  3. one `test-circuit` race with no exception or validation error, and `step()` p99 ≤ 5 ms after 50 warm-up ticks.
  It returns a structured report, and exits non-zero on failure.
- **`racekit/agents/starter.py`:** re-implements the **described** starter behaviour, not the code: a P controller
  toward the waypoint 3 ahead with gain ∝ 1/√v, and a 20 m/s P speed controller. It is 3.8-compatible and passes
  `check_submission`. It is the `roar-002` Unit 1 baseline; that plan copies it to `agents/unit-01.py`.

**Tests (`roar/projects/racekit/tests/`):**
- the shim against the contract fixture (names, async-ness, parameters), and action validation (good and bad
  dicts);
- the kinematic car: the steady-state circle radius equals `L / tan δ` within 1%; RK4 error < Euler error at
  equal dt; drag decelerates monotonically;
- the runner:
  - a scripted perfect follower finishes `oval` in the expected time band;
  - a scripted "drive off" agent triggers respawn at the start pose with progress retained;
  - the forward window ignores far-ahead waypoints;
  - the 3-lap finish detection;
  - both sync paths (no running loop; inside a running loop in a thread);
  - a function-local `import roar_py_interface` inside `step()` works;
  - two submissions load in one process without a module collision;
  - the refusal to shadow a real module;
- `measure`: deterministic with seeds; the noise-aware rule on synthetic data;
- `check_submission`: the starter passes; negative files fail with the right reason (a `match` statement,
  `removeprefix`, an `X | Y` annotation, `import scipy`, a wrong constructor, an invalid action, a slow step);
- **the isolated 3.8 run** (marked `slow`, but run in CI): `uv run --no-project --python 3.8 --with "numpy<1.25"
  --with-editable roar/projects/racekit python -m racekit.check_submission racekit/agents/starter.py`, asserting
  `(3, 8)` and numpy < 1.25 inside the run. If the uv-managed 3.8 interpreter cannot be fetched (offline CI), it
  **fails, not skips**;
- every `racekit` module passes `ast.parse(feature_version=(3, 8))` plus the deny-list.

**Verify:** routed `uv run --group roar pytest roar` green; the 3.8 run green.

### Phase E — guard tests (routed, `roar/tests/`)
- **API order (design §7.1):**
  - the loader for `api-order.yaml` (schema: `infrastructure: [names]`, `taught: {name-or-module:name: concept-id}`);
  - call resolution: qualified calls, `import m as a`, `from m import f`, `from m import f as g`, and attribute
    calls;
  - each entry's position is derived from `coverage-map.yaml` entry order and `introduces`;
  - the scan scope: lessons, exercises, solutions, milestones, `agents/unit-NN.py`, labs, checkpoints and the
    capstone, with verify cells excluded.
  The test runs over the real book (empty now, so it passes trivially). **Negative fixtures**, built in a temp tree
  of the same shape, must fail for:
  - a premature use in each of the four call forms;
  - an unmapped `library_methods` name;
  - an `api-order` key missing from `library_methods`;
  - an unknown concept id.
- **Deny-list:** fails if any tracked path matches `*.umap`, `*.xodr`, `*.uasset`, `**/competition_runner.py`,
  `**/infrastructure.py`, or a `waypoints*` dump outside `roar/data/generated/`. Negative test included.
- **Labs-tracked:** fails if a tracked file under any `roar/**/labs/` is not `*.ipynb` or `README.md`.

### Phase F — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` must be ALL GREEN with `roar` registered. That covers:
- buildout;
- the `.gitkeep` dirs;
- the routed roar suite under `--group roar`, including the isolated 3.8 run;
- the group-free `tests/` run unaffected;
- recsys unchanged.

Also:
- `bash scripts/pre-merge-guard.sh --pr` OK;
- the tracked-file assertions (no upstream code, maps or lab data);
- timing: generation ≤ 10 s, routed roar pytest ≤ 2 min.

## Out of scope (verification-phase exemption)
No student units, projects or checkpoints ship (they start in `roar-002`, each with its own verification phase).
Phase F is this plan's verification. The following are also out of scope:
- the dynamic car, the carla-like truth car and telemetry generation (`roar-004`);
- `lab-check` and labs (`roar-002`);
- `site` and `publication` (`roar-014`);
- any CARLA run.

No stub unit is added; `buildout: true` covers the empty state.

## Plan Review

## Content Review
N/A as a content gate: this plan ships no student content. The gate is still run on the shipped code and docs per
`docs/content-review-gate.md` (tooling duties).

## Post-Execution Report
