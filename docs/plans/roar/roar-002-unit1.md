# Plan roar-002 — Unit 1: The race and the baseline (plus `lab-check` and the first real-sim lab)

**Design:** `docs/designs/013-roar-book.md` **v4.1** (§1.2–1.3, §4, §5, §6 Unit 1, §7.2).
**Book:** `roar`. **Autopilot** per AGENTS.md.
**v2.2** folds round 3 (explicit respawn signal). **v2.1** folded plan-review round 2 ([sol] REJECT on the lab CSV producer contract). **v2** folded plan-review round 1 ([sol] REJECT, [fable] APPROVE WITH NITS with two MUSTs).
This plan ships the **first student unit** on the `roar-001` substrate, together with the real-sim lab machinery and
its first lab.

**Base:** this plan branches from `main` **after `roar-001` merges**, and Phase 0 starts only then ([fable] S7).

## Scope
- Unit 1 (`roar/units/unit-01-the-race-and-baseline/`): the hook, the race rules (including the v4.1 respawn rule),
  the submission ABI, the async step loop, telemetry, sector splits, and **repeated runs (median and range)**.
- The milestone `roar/projects/racekit/milestones/unit-01-the-race-and-baseline.ipynb` and the reference submission
  `roar/projects/racekit/agents/unit-01.py` (the starter, copied).
- `racekit` additions this unit teaches (Phase 1): seeded actuator jitter, `plots`, a telemetry-based
  `sector_splits`, an agent-variant helper, and the lab sample CSV.
- **Lab tooling** (Phase 0): the `labs` flag, the flagged `lab` manifest key, `lab-check`, and a durable exclusion
  pin.
- The lab `roar/units/unit-01-the-race-and-baseline/labs/real-sim.ipynb`.
- No project registry entry.

## Deviations from design (recorded)
- **Jitter lives on `KinematicCar`** (design §4.4 places noise on the carla-like car in `roar-004`). Unit 1 needs a
  realistic spread now. `roar-004` reuses the same `seed()` / jitter protocol on its cars ([fable] S5).
- **Content deviations** (Phases B–E): the plan's "time to first reach 19 m/s ≈ 4–5 s" is wrong; it is 11.35 s (15 m/s at 4.70 s), so Exercise 3 asks for both. `monza-like` is 5714.5 m, not 5.8 km (285.7 s per lap at 20 m/s), and the standing-start penalty is 3.55 s. The lab recorder (after the content gate) re-anchors to `start_index` on the respawn impulse, without reading the stale crash-pose sensor, and writes the 20 hold rows itself, so recordings carry the explicit respawn signal. The closed `library_methods` list was extended with the shim callables (`initialize`, `step`, `apply_action`, `get_last_gym_observation`), stdlib helpers and `update` (taught: race-telemetry).
- **Implementation deviations** (Phase 0/1, recorded at hand-back):
  - `sector_splits(..., finished=False)`: a recorded CSV never sees the finishing tick, because the agent is not
    called on it. `finished=True` closes the last sector at the last row's t + 0.05. With it, the recorded and runner
    splits match exactly. The lab passes `finished=True`.
  - The G6 saboteur steers 0.25 at t = 60 s, not full lock: on the kinematic car full lock circles on the spot and
    never leaves the track. Measured: crash at 60.60 s, total 285.10 = 223.50 + 60.60 + 1.0.
  - The recorder's tick clock adds `RESPAWN_HOLD_TICKS` when it sees the respawn impulse, because the agent is not
    stepped during the hold.
  - Additions: `race_meta(result)`; `write_variant` accepts int and float values. `labs.yaml` has exactly one key,
    `sample_csv`.
  - The lab-check simulator-mention rule matches lower-case names only.

## Buildout stays
The whole-book `lessons` total is 3, which is under 30.

## Concepts (4 introduced; 3 new to `concepts.yaml`)
All are globally unique and `kind: technique`.
- `roar-race-and-submission` (the seed concept, now introduced): the race rules, including **the pinned respawn rule:
  start pose, a 1.0 s hold, progress reset to 0, so a crash restarts the whole race with the clock running**, and
  the contrast with the published "costs a lap" wording. Also the single-file ABI, the `async initialize`/`step`
  lifecycle and the Python 3.8 target.
- `race-telemetry`: per-tick telemetry, its columns (including `held`), and sector splits from telemetry.
- `repeated-run-measurement`: why one run lies, repeated seeded runs, the median and range, and the noise-aware rule.
- `telemetry-plotting`: matplotlib plots of telemetry and the track, via `racekit.plots` and basic `plt` / `ax`
  calls.

The entry has `requires: []` and `practices: []`.
`api-order.yaml` maps the taught callables to these concepts. `run_race`, `load_track`, `check_submission`,
`write_variant` and the shim API are `infrastructure:`.
**`library_methods` is a closed list** ([fable] N4): every `plt`/`ax` call the notebooks use (`subplots`, `plot`,
`scatter`, `set_xlabel`, `set_ylabel`, `set_title`, `legend`, `grid`, `tight_layout`, `colorbar`, …) must be listed,
or concept-scan and the API-order test fail. The content authors receive the list and may only extend it through the
plan's Phase A.

## Gates (pinned from the probe; a miss means stop, amend and re-gate)
These use `KinematicCar(jitter=0.05)` on the corrected runner (`roar-001` `35625a6`), seeds 0–4. **Per-seed times
are asserted exactly** (to 1e-9, tick-quantized; [fable] N6):

| Track | Seed times | Median | Range |
|---|---|---|---|
| oval | 220.60, 220.75, 220.75, 220.95, 220.60 | 220.75 | 0.35 |
| monza-like | 870.30, 870.50, 870.70, 870.75, 870.45 | 870.50 | 0.45 |

- **G1:** the starter finishes 3 laps of both tracks, with 0 collisions, in all 5 runs.
- **G2:** the per-seed times above, exactly; this implies the medians and ranges. With jitter = 0, `oval` gives
  **223.50 s** and range 0 (the deterministic baseline).
- **G3** ([fable] M2, non-trivial): `racekit.telemetry.sector_splits(telemetry, progress_total, laps=3, per_lap=3)`,
  computed from the `t` and `progress` columns, **equals `result.sector_splits`** to 1e-9 and sums to `total_time`.
  It does so for a racekit result and for the same race written to CSV and read back (the lab path).
- **G4** ([sol] S4, [fable] S4): the milestone asserts `check_submission("…/agents/unit-01.py").ok`. The routed
  isolated 3.8 test is **parametrized over every `agents/*.py`**, so `unit-01.py` is checked there, not in the
  milestone.
- **G5:** `lab-check` passes for Unit 1, and its negative fixtures fail.
- **G6** ([fable] S2, the crash cost): a scripted saboteur, the starter with a hard steer at t = 60 s on `oval` with
  jitter 0, finishes with `total_time == 223.50 + t_crash + 1.0` within one tick. `respawn_times` has 1 entry,
  telemetry has 20 `held` rows, and `progress` resets to 0.

## Probe evidence
- `scratchpad/probe002.py` (2026-10-26, on the corrected runner), reproduced independently by [fable] with
  `random.Random(seed)`, the throttle draw before the steer draw, gauss(0, σ), and clipping. The results are the per-seed table above, all 5/5 finished with 0
  collisions, and deterministic.
- 5 `monza-like` races take about 13.7 s; 5 `oval` races take about 3.3 s.
- **Starter facts** (monza-like, σ = 0.05, seed 0; [fable] S1):
  - mean speed 19.71 m/s, minimum after the launch 15.48 m/s;
  - 0.5% of ticks below 15 m/s (oval 2.1%);
  - max |offset| 0.61 m (oval 0.50 m);
  - 3×3 splits [99.8, 96.4, 96.55 | 96.2, 96.3, 96.45 | 96.3, 96.65, 95.65]: flat, with lap-1 sector 1 slower by
    about 3.4 s (the standing start).
  So the starter **loses time everywhere, uniformly, because it is capped at 20 m/s.** A 5.8 km lap at 20 m/s is
  about 290 s, against the podium's about 107 s per lap (320/3).

## Phases

### Phase 0 — lab tooling (Opus tooling subagent)
- `books.yaml` gets a **`labs`** boolean flag (documented, set on `roar`).
  `tools/notebooks.py` gets `FLAGGED_MANIFEST_KEYS["lab"] = "labs"`.
  `tests/test_books.py` is updated: the step-1 flag tuple and the per-flag lists.
- **`tools/labs.py` → `lab-check`** (registered in `tools/checks.py`; run in `ci-local.sh` step 3 under
  `has_flag labs`). For each unit with `lab: true`:
  - `labs/real-sim.ipynb` exists. A `labs/` directory without `lab: true` is a finding.
  - It has no outputs or execution counts.
  - Its **first code cell** is tagged `parameters` and sets
    `TELEMETRY_PATH = os.environ.get("ROAR_LAB_CSV", "telemetry.csv")`.
  - **Code** cells that mention `carla`, `roar_py_carla`, `competition_runner` or `subprocess` are tagged `no-exec`.
    Markdown cells are exempt ([fable] S6).
  - No code cell other than the parameters cell contains a `.csv` string literal.
  - **Read vs write, by AST** ([sol] S3): in a `no-exec` cell, any `read_csv` / `load_csv` call is a finding, and so
    is an `open(...)` whose mode is absent or read-capable (`r`, `r+`, `rb`, `+`). `open(..., "w"/"a"/"x")` is
    allowed, which is what the CARLA recorder needs.
  - It then **executes a copy** with the `no-exec` cells removed, under the book's group, with `ROAR_LAB_CSV` set to
    the sample CSV named by `roar/curriculum/labs.yaml` (`sample_csv: roar/data/generated/lab/sample_telemetry.csv`).
- **The exclusion pin** ([fable] S6): today `publish` and `export` read only the top-level `<stem>.ipynb` files, and
  roar has neither flag. The pin is a test against the discovery helpers, using a tmp fixture book with
  `site`/`publication` on and a `labs/x.ipynb`, proving the lab is never collected. It survives `roar-014` turning
  those flags on.
- **Tests** (group-free, tiny stdlib-only fixture notebooks):
  - a passing lab, including a recorder cell with `open(TELEMETRY_PATH, "w")`;
  - each of these fails: a missing lab, a missing parameters cell, a hard-coded CSV path, an untagged CARLA code cell,
    a read-mode `open` in a `no-exec` cell, a stray `labs/` directory, and `lab: true` in a book without the flag.

### Phase 1 — `racekit` additions (Opus tooling subagent)
- **Jitter** ([fable] M1): `KinematicCar(..., jitter=0.0)` plus a **method** `seed(self, seed: int) -> None` that
  sets `self._rng = random.Random(seed)`. Each tick:
  - throttle gets `+ gauss(0, jitter)`, clipped to [0, 1], then steer gets `+ gauss(0, jitter)`, clipped to [−1, 1];
  - brake is not jittered;
  - with `jitter == 0` no RNG draws happen, and a byte-identity test against `roar-001` behaviour proves it.
  `run_race(seed=)` and `repeat_races` are the only seed sources; the lesson idiom is
  `car_factory=lambda: KinematicCar(jitter=0.05)`.
- **`racekit.telemetry.sector_splits(telemetry, progress_total, laps=3, per_lap=3) -> ndarray (laps, per_lap)`**
  ([sol] B2, [fable] M2):
  - computed from the `t` and `progress` columns, so it works on a racekit result and on a CSV;
  - `held` rows are handled (sectors restart after a respawn, as the runner does);
  - `RaceResult.sector_splits` is refactored to **call** it, so there is one implementation;
  - **The pinned CSV contract** ([sol] r2 B2):
    - `write_csv(telemetry, path, meta: Dict[str, int])`, with `meta` keys **`progress_total` (int, = laps × n),
      `laps` (int), `per_lap` (int), `waypoints_per_lap` (int, = n)**.
    - The first line is exactly `# racekit-telemetry v1 progress_total=<int> laps=<int> per_lap=<int>
      waypoints_per_lap=<int>`, then the header row, then data. The columns are `t, x, y, yaw, v, throttle, steer,
      brake, progress, offset, held`; `held` and `offset` may be all-zero in a CARLA recording.
    - `read_csv(path) -> (telemetry, meta)` validates the header and the integer types.
    - `progress` is **cumulative over the race**: 0 … `progress_total`. It is reset to 0 by a respawn.
  - **The recorder algorithm** (`racekit.telemetry.CumulativeProgress`, a ~25-line class that is also printed in the
    lab, so a student can paste it into a 3.8 submission):
    - constructed with `n` (waypoints per lap);
    - `update(lap_index, collision_impulse)` takes the agent's own one-lap index and the collision sensor's
      `impulse_normal` reading;
    - a **lap wrap** is detected when the index goes from ≥ 0.9·n to < 0.1·n, and adds n to an offset;
    - a **respawn** is detected from the **explicit collision signal** ([sol] r3): `‖impulse_normal‖ > 100`, the
      runner's own major-collision threshold. The pinned runner checks it, respawns and resets progress, and then
      the agent's next `step()` sees that impulse. racekit reports the same on the first step after the hold. A
      detected respawn resets the offset to 0, regardless of position, and sets `respawned=True` for that row;
    - it returns the cumulative progress = offset + index.
    `sector_splits` treats a cumulative-progress drop to below 0.1·n as a respawn, with or without a `held` column.
  - **Tests:**
    - a complete 3-lap CSV produced by a racekit agent that records through `CumulativeProgress` (the lab path) gives
      the same `sector_splits` as `result.sector_splits` within one tick per sector;
    - a crash/reset CSV (the saboteur, recorded the same way) gives monotone progress with exactly one reset, and
      splits that restart after it;
    - **a crash near the start line after a completed lap** (a saboteur that steers off within 15 m of the start in
      lap 2): the recorder resets to 0, and its cumulative progress matches the runner's telemetry `progress` on
      every non-held row;
    - malformed headers and non-int meta are rejected.
- **`racekit.write_variant(src_path, dst_path, replacements: Dict[str, str])`** ([fable] S3): copies a submission
  file, substituting module-level constants (`TARGET_SPEED = 20.0` → `25.0`), and checks that each replacement
  matched exactly once. It is the idiom for "try a variant" in notebooks: it mirrors the real one-file workflow, and
  the copy can be raced and checked with `check_submission`.
- **`racekit/plots.py`** (lazy matplotlib, 3.8-safe): `plot_track`, `plot_telemetry`, `plot_speed_map`.
- `roar/data/generate.py` adds the lab sample: the starter on `monza-like`, jitter 0.05, seed 0, written with the v1
  header to `roar/data/generated/lab/sample_telemetry.csv`, two-run checksummed.
- `agents/unit-01.py` is the starter, copied. The routed isolated 3.8 test is **parametrized over every
  `agents/*.py`**.
- **Carried from the `roar-001` content gate:**
  - [fable] N6: on a tick where the car both crosses the finish margin and goes off-track, check the collision
    first, as upstream does;
  - [fable] N9: a `telemetry.py` column note that `held` rows keep the pre-reset progress.
- **Tests:**
  - jitter determinism and the per-seed pins (G2);
  - the jitter = 0 identity;
  - `sector_splits` equivalence (G3), including a respawn race;
  - CSV v1 round-trip and meta;
  - `write_variant`: exactly-once matching, and failure on a missing or duplicate constant;
  - plots smoke tests (Agg backend);
  - the saboteur crash cost (G6);
  - the finish-versus-collision same-tick order.

### Phase A — registry and syllabus
- `concepts.yaml` gets the 3 new ids. `coverage-map.yaml` gets the Unit 1 entry (`lessons: 3`).
- The manifest mirrors the entry, plus `lab: true`.
- `api-order.yaml` / `library_methods` get the closed list.
- `syllabus.md` gets the row, and its crash sentence is updated to the v4.1 rule.
- `labs.yaml` is added.

### Phase B — `lesson.ipynb` (Opus content subagent)
1. **The hook** (markdown first): "Here is the official starter agent. How fast is it, and where does it lose time?"
   The goal is a reasonable ranking (§1.3: every run clean, median ≤ 329 s on CARLA Monza).
2. **The race rules (§1.2).** 3 laps, total sim time, the 0.05 s tick, progress through a forward window, and **a
   crash: back to the start, held 1.0 s, progress reset to 0. The race restarts with the clock running.** Contrast
   this with the published "a crash costs a lap": the book follows the pinned code, and either way zero collisions
   is the dominant lever.
3. The ABI: read `agents/unit-01.py`; the Python 3.8 note.
4. `run_race` on `oval`, **deterministic first** (jitter 0: 223.50 s, range 0). "racekit is repeatable; CARLA is
   not."
5. `monza-like`: telemetry columns, the speed trace, the speed map.
6. **Where the time goes** ([fable] S1):
   - the 20 m/s budget: 5.8 km per lap at 20 m/s is about 290 s per lap, against about 107 s per lap on the podium;
   - flat 3×3 splits are the symptom of a speed cap;
   - lap-1 sector 1 is about 3.4 s slower (the standing start), which shows what splits are for;
   - the max offset (0.61 m) shows it is **not** cutting corners on this car.
7. **One run lies:** turn on jitter (σ = 0.05, chosen to match the series' *absolute* spread of about 0.3 s, not the
   relative one; [fable] N3); 5 runs; the median and range; `noise_aware_better`. Times are quantized to the 0.05 s
   tick ([fable] N7).
8. The crash cost, shown with the saboteur on `oval`: `respawn_times`, the `held` rows, the progress reset, and
   total ≈ clean + t_crash + 1.0.
9. `check_submission` (an AST deny-list plus a race; only the isolated 3.8 run proves 3.8).
10. The bridge: what the lab will do on CARLA.

Repeated-run drills use `oval`; one `monza-like` set only ([fable] N2).

### Phase C — `exercises.ipynb` + `solutions.ipynb` (separate fresh Opus subagents)
- At least 6 `## Exercise N` headings and at least 2 `stretch` cells (statement plus answer cell).
- No solutions or outputs in the exercises. The solutions run clean with at least 3 non-vacuous asserts.
- The exercises drill:
  - the ABI;
  - running races;
  - telemetry queries, for example **"time to first reach 19 m/s"** (non-degenerate, about 4–5 s; [fable] S1);
  - sector splits from a CSV round-trip;
  - repeated runs on `oval`, and the noise-aware rule;
  - a plot;
  - spotting a 3.9+ construct that `check_submission` rejects.
- Stretch:
  1. **predict, then measure**, the crash cost of a saboteur crashing at t = 120 s, using the v4.1 rule ([sol] B1);
  2. a `write_variant` with `TARGET_SPEED = 22`: is it better, noise-aware, on `oval`, and does it still finish
     clean?

### Phase D — the milestone (Opus content subagent)
- It runs 5 jittered races per track and asserts G1–G3, G4 (`check_submission(...).ok`) and G6.
- Cleared outputs. It runs under `exec-solutions`.

### Phase E — the lab (Opus content subagent)
`labs/real-sim.ipynb` contains:
- the parameters cell;
- no-exec setup: CARLA 0.9.12 plus the Monza v1.1 Windows executable; the Python 3.8 conda env; the pinned
  `ROAR_PY`; the `ROAR_Competition` fork at the pinned commit; `agents/unit-01.py` as `submission.py`; run
  `competition_runner.py`;
- a **recorder** the student adds to their `step()`: it uses `CumulativeProgress` (pasted, 3.8-safe), writes the v1
  header once in `initialize()` with `open(TELEMETRY_PATH, "w")`, and appends rows with `open(TELEMETRY_PATH, "a")`;
- analysis cells that run in CI against the sample: `read_csv` → `(telemetry, meta)`, `sector_splits`, the plots,
  and a comparison with racekit;
- a "never commit your results" note.

### Phase F — `teacher-notes.md` (active session, inline)
`## Goals`, `## Pacing` (two or three 60–90 min sittings plus the lab session), `## Common mistakes` (including
"a crash costs a lap": no, it restarts the race), `## Discussion prompts`, `## Differentiation`, and "Lab logistics".

### Phase G — verification (named)
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN;
- `bash scripts/pre-merge-guard.sh --pr` OK;
- G1–G6 hold;
- Unit 1 notebook exec ≤ 2 min in total, recorded.

## Out of scope
- Geometry and controllers (Unit 2 onward), and the dynamic car (`roar-004`).
- Changes to the starter's behaviour.
- A project entry.
- Running CARLA.

## Plan Review

### Round 1 (v1, scratch draft)
- **[sol]** REJECT:
  - B1, "a crash costs a lap": [FIXED v2, the v4.1 rule taught, plus G6 and stretch 1].
  - B2, the lab sector-split contract: [FIXED v2, `sector_splits(telemetry, …)` plus the CSV v1 meta].
  - S3, read vs write: [FIXED v2, AST mode check].
  - S4, the 3.8 test parametrized: [FIXED v2, G4].
  - N5, v4.1: [FIXED v2].
- **[fable]** APPROVE WITH NITS:
  - M1, the jitter seed must be a method: [FIXED v2].
  - M2, sector splits clash and a vacuous G3: [FIXED v2].
  - S1, probe facts and step 6: [FIXED v2].
  - S2, the falsifiable crash cost: [FIXED v2, G6].
  - S3, the variant idiom: [FIXED v2, `write_variant`].
  - S4, the milestone 3.8: [FIXED v2].
  - S5, deviation and a deterministic run first: [FIXED v2].
  - S6, the durable exclusion pin and markdown exemption: [FIXED v2].
  - S7, the base branch: [FIXED v2].
  - N1, the lab already in API-order scope: noted.
  - N2, `oval` for drills: [FIXED v2].
  - N3, absolute spread: [FIXED v2].
  - N4, the closed list: [FIXED v2].
  - N5, the concept count: [FIXED v2].
  - N6, per-seed pins: [FIXED v2].
  - N7, quantization: [FIXED v2].
- **[self]** APPROVE.

### Round 2 (v2)
- **[sol]** REJECT. B1, S3, S4, N5, [fable] M1 and all [fable] S/N items were verified RESOLVED; it reproduced the
  per-seed tables and 223.50 s exactly.
  - B2/M2 remained: the CSV producer contract (writer meta, cumulative progress over one-lap indices, crash reset).
    [FIXED v2.1, the pinned writer, header and meta schema, the `CumulativeProgress` algorithm, and 3-lap and crash
    CSV tests].

### Round 3 (v2.1)
- **[sol]** REJECT. The header and meta contract was resolved. The jump-based respawn detection misses crashes near
  the start. [FIXED v2.2: an explicit collision-impulse signal (> 100, the runner's threshold) plus a near-start,
  after-lap crash test].

### Round 4 (v2.2): CONSENSUS
- **[sol]** APPROVE. It verified the upstream impulse timing (the observation is not refreshed during the hold) and
  racekit's mirror of it.
- **[fable]** APPROVE WITH NITS in round 1. Both MUSTs and every S/N item were folded in v2.
- **[self]** APPROVE.

## Content Review

### Round 1
- **[sol]** REJECT:
  - B1, a respawn at progress 0 is invisible in a recording: [FIXED ba36989; the recorder writes 20 `held` rows at the runner's hold times, and a test covers a CSV crash at progress 0].
  - S2, the parameters cell could reassign `TELEMETRY_PATH`: [FIXED ba36989; exactly one assignment, none in other cells, with tests].
  - N, the Exercise 5 "but one" prose: [FIXED].
  - Blind solve: all 9 exercises match.
- **[fable]** APPROVE WITH NITS:
  - M1, a stale crash-pose observation after a CARLA respawn (a false lap wrap): [FIXED ba36989; re-anchor to `start_index` after `advance_index`, the prose explains it, and the runner's "Known differences" list records it].
  - S1, the lab recorder was never executed: [FIXED; `test_racekit_lab_recorder.py` splices the marked cell into the starter and covers the clean, saboteur and stale-pose cases, plus a teeth check].
  - S2, the ROAR_PY install path and the numpy pin: [FIXED; `requirements.txt` plus `roar_py_core` / `roar_py_carla`, and `numpy<1.25`].
  - S3, the Exercise 5 prose: [FIXED].
  - S4, 285.7 vs 290 s: [FIXED].
  - N1–N5: [FIXED; including a `write_variant` → `check_submission` demo in §8].
  - Blind solve: all 9 exercises match.
- **[self]** APPROVE: hook first, the crash rule correct, pins asserted.

## Post-Execution Report
