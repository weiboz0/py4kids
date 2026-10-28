# Plan roar-008 — Units 8–9: system identification, and the racing line

**Design:** `docs/designs/013-roar-book.md` **v4.6** (§4.3–4.5, §5, §6 Units 8–9, §7.1–7.3); this plan amends it to
**v4.7** (below).
**Book:** `roar`. **Autopilot** per AGENTS.md.
**Base:** branches from `main` after `roar-007` merged (#162, 062a11c).
**v2.1** folds plan-review round 2 ([sol] S: the squared QR identity, S: no grip estimate at all in the lab;
[fable] N1–N2).
**v2** folds plan-review round 1 ([sol] REJECT: B the lab ending on an un-raced value, S the race count; [fable]
APPROVE WITH NITS: S1 hidden truth in student material, S2 QR before it is taught, S3 the Unit 9 hook, S4 the lab's
PROVISIONAL wording and the probe's row rule, S5 a tolerance on the pin, N1–N6; [self] N1 = S2, N2 the shipped
B-spline reconstruction).

## Scope
- Unit 8 `roar/units/unit-08-system-identification/` (a **lab unit**: `labs/real-sim.ipynb`, design §7.2) and Unit 9
  `roar/units/unit-09-racing-line/`: lesson, exercises, solutions, teacher notes, manifest.
- Reference submissions `agents/unit-08.py` and `agents/unit-09.py`; milestones
  `milestones/unit-08-system-identification.ipynb` and `milestones/unit-09-racing-line.ipynb`.
- `racekit.sysid_data` (design §5: the module enters with the unit that teaches it): the names and loader of the
  committed sensor logs. Nothing else in `racekit` changes; the fits, the grip probe, the line and its solver are
  **student code**.
- A routed premise test for the Unit 8–9 gates; the registry; design 013 **v4.7** (below).

## Risks named for this plan (design §7.3)
- **The interim CARLA check of `agents/unit-07.py` is PENDING (author).** It has not run on CARLA. Units 8–9 build on
  the Unit 7 agent; if the author's check fails, an errata/fix plan follows before Part 2 ships.
- **The Unit 7 reference is fragile off its tuning track** (`roar-007`): it crashes on every seed of
  `test-circuit-seed2026` and on one seed of `test-circuit-seed1`. (The session's follow-up note that it also crashes
  on `monza-like` seeds 2–4 is **not** reproduced: at the 900 s cap a `monza-like` race needs, it is clean on seeds 0–4
  at 515.10 s (`p9`, and `roar-006`); the note came from races capped at 450 s, which cannot finish there. Corrected
  in the follow-ups.) This plan's probes give two causes, both of which
  Unit 8 measures: the per-section grip (seed2026) and the **steering gain** (the agent assumes 70° of full lock; the
  car has 66°, and on `monza-like` the mismatch is what limits the speed, below). The interim CARLA check is therefore
  more likely to fail than the racekit record suggested, and Unit 8's lab is where a student meets that on CARLA.

## Probe evidence (scratchpad `u08/`, `carla_like(noise=True)`, race seeds 0–4 unless said)
All gate pins come from these files: `p6` (the grip probe), `p7`/`p8` (the measured-μ planner at 70° / 66°), `p9`
(the Unit 7 reference at 66°), `p18`–`p26` (the line; `p10`–`p17` are its history), each with its `.pkl` or `.npy`.
The probe agents are `agents/unit-07.py` plus the constants below (`p10`'s line agent is `u9line.py`).

- **The committed logs (`roar-004` G4.6, re-used):** on `sysid/monza-like-seed0.csv` the lagged least-squares fit of
  dv/dt = a_T·throttle − a_B·brake − c·v|v| has its residual minimum at lag 1; a_B is −0.7%, a_T −4.2%, c −9.4% from
  the car; on `sysid/oval-steady-seed0.csv` the steady-row fit gives δ_max = 65.71° (the car: 66°). The routed
  `test_racekit_sysid_premise.py` already asserts these; Unit 8 teaches them.
- **Per-section grip from limit probes (`p6`).** The probe driver is the student's own Unit 7 agent:
  `A_LAT = 3.5`, and `GRIP[s] = 3.5` in **one** section s (12.25 m/s² there, above any μg), one lap, `max_seconds =
  300`, seed 0; six races per track, one per section. |a| is the second difference of the telemetry's (x, y) at
  0.05 s, over driving rows (three consecutive `held == 0` rows, no jump over 5 m, v > 5 m/s) whose waypoint
  `(progress + 1) mod n` lies in section s; the estimate μ̂_s·g is the 99th percentile.
  - On all six `test-circuit` tracks (the five training tracks and seed2026), **every section** gives μ̂g/μg in
    **[0.980, 0.999]** (36 sections; each probe crashed 3–18 times).
  - On `monza-like`, sections 1–5 give [0.971, 0.993]; **section 0 never crashed** (it is the start straight: 0
    collisions, 0.656). An estimate counts only where the probe actually lost grip; elsewhere it is a lower bound.
  - All 42 races take 19 s on 8 workers.
  - Two excitations failed and are taught as such: pushing every section at once crashes in the first corner,
    and pushing every section from s onward crashes in an earlier low-grip section and never reaches the later ones.
- **The measured-μ planner (`p7`, `p8`).** The Unit 7 agent with cap √(f·μ̂_s·g / |κ|), i.e. `A_LAT = f` and
  `GRIP = μ̂g` per track (rounded to 0.01), one global fraction f on a grid of 0.02:

  | f | `test-circuit` | seed1 | seed2 | seed3 | seed4 | seed2026 | `monza-like` |
  |---|---|---|---|---|---|---|---|
  | 0.56, MAX_STEER 70° | 302.05 | 297.80 | 297.10 | 297.55 | 298.55 | 303.40 | ✗ (0.54 already ✗ 4/5) |
  | 0.56, 66° | 301.95 | 297.65 | 297.00 | 297.45 | 298.40 | 303.30 | 506.50 |
  | 0.58, 66° | 299.30 | 295.15 | 294.35 | 294.75 | 295.80 | 300.65 | 503.45 |
  | 0.60, 66° | 296.75 | 292.65 | 291.85 | 292.20 | ✗ (4/5) | ✗ | 500.70 |
  | 0.62, 66° | — | — | — | — | — | — | 497.90 |
  | 0.64, 66° | — | — | — | — | — | — | ✗ |

  Medians in s, all clean unless ✗; spreads ≤ 0.25 s.
  - At 66° the **training family's edge is 0.58** (0.60 fails on seed4), so the margin rule (one grid step) freezes
    **0.56**; on the unseen seed2026 that races **303.30 s**, clean, against Checkpoint A's 310.80 s (7.5 s, about
    35× the spread), and 0.58 is still clean there while 0.60 is not.
  - **The steering gain is what limits `monza-like`.** At 70° the measured-μ planner fails on `monza-like` from 0.54
    (a growing weave on the long straights, as in Checkpoint A); at 66° it is clean through 0.62 (497.90 s), against
    the Unit 7 reference's 515.10 s.
  - The steering gain does **not** cure seed2026 (`p9`): the Unit 7 reference (A_LAT 4.6, GRIP 1) at 66° still
    crashes on every seed there (that one is grip), while at 66° it becomes clean on seed1 (302.05 s).
- **The racing line (`p18`–`p25`; the first attempt, `p10`/`p12`, is history below).** Offsets n_i along each
  waypoint's unit normal (left positive). The **reduced problem**: n is a periodic uniform cubic B-spline with one
  control value every 10 waypoints (133 unknowns on `test-circuit`), so each n_i is a weighted average of four control
  values (weights ≥ 0, summing to 1). The objective is the **smoothness** of the line: the sum of squared second
  differences of its points (x and y). It is linear in the control values: a bounded linear least-squares problem,
  solved with `scipy.optimize.lsq_linear(method="bvls")`. Applied to the 2n × m matrix it takes 11–16 s per
  `test-circuit` track and 110 s on `monza-like`; applied to the QR factor (A = QR: minimising ‖Ac − b‖ is minimising
  ‖Rc − Qᵀb‖, an m × m problem) it gives the same line to 1e-12 m in **3–4 s and 16 s** (`p26`). Bounds: a control value may move only as
  far as **every** waypoint in its support allows, |c_j| ≤ min(w_i − 2.5 m), so every waypoint is inside the margin by
  construction; control values whose support touches the 30 waypoints either side of the start are 0 (the car starts
  on the centreline), so n = 0 exactly there. "Local" widening fixes the offsets at 0 outside windows of 60 waypoints
  around every point tighter than 60 m radius.
  - **What the line is** (`p22`): on all seven tracks the total squared curvature Σκ²Δs falls (`test-circuit`
    0.2880 → 0.2326, −19%; `monza-like` 0.2421 → 0.1428, −41%) and the lap gets shorter (2661.7 → 2636.2 m; 5714.5 →
    5684.7 m). The single tightest point gets tighter on the `test-circuit` family (18.0 → 15.2 m) and wider on
    `monza-like` (25.0 → 28.3 m): the objective trades one corner for the whole lap.
  - A line race is **clean** when it finished, with 0 collisions, and its max |cross-track error from its own line|
    (the centreline offset minus n at the car's waypoint `(progress + 1) mod n`) is ≤ 2 m. The agent plans its profile
    on the line's own Menger curvature, with 66° and f·μ̂.

  | f (66°, μ̂) | 0.50 | 0.52 | 0.54 | 0.56 | 0.58 | 0.60 | 0.62 | 0.64 |
  |---|---|---|---|---|---|---|---|---|
  | `test-circuit` line | 285.10 | 282.25 | **279.60** | 277.10 | 274.65 | 272.30 | — | — |
  | seed1 line | 281.55 | 278.85 | 276.20 | 273.80 | 271.50 | 269.30 | — | — |
  | seed2 line | 280.60 | 278.00 | 275.50 | 273.05 | 270.80 | 268.65 | — | — |
  | seed3 line | 281.00 | 278.30 | 275.65 | 273.25 | 270.90 | 268.70 | — | — |
  | seed4 line | 281.35 | 278.55 | 275.95 | 273.45 | ✗ | ✗ | — | — |
  | seed2026 line (unseen) | 287.65 | 284.75 | **282.05** | 279.35 | ✗ (err 2.39 m) | ✗ | — | — |
  | `monza-like` line | — | — | — | 478.65 | — | 473.45 | 471.05 | ✗ (err 2.08 m) |
  | `test-circuit` centreline | — | 307.55 | 304.70 | 301.95 | 299.30 | 296.75 | ✗ | — |
  | `monza-like` centreline | — | 514.20 | — | 506.50 | 503.45 | 500.70 | 497.90 | ✗ |
  | `monza-like` local | — | — | — | 493.05 | — | 487.55 | 485.05 | — |

  Medians in s, spreads ≤ 0.20 s; ✗ = not clean on at least one seed (seed4 at 0.58: five crashes; seed2026 at 0.58:
  finished, but 2.39 m from its line).
  - **At the same f the line buys about 25 s on `test-circuit`** (0.54: 279.60 against 304.70 s) and **27 s on
    `monza-like`** (0.60: 473.45 against 500.70 s).
  - **A new line breaks the speed tuning:** the line's family edge is **0.56** (0.58 fails on seed4), one grid step
    *below* the centreline's 0.58. Carried over unchanged, Unit 8's frozen 0.56 is still clean on the five training
    tracks (the gate's claim; the probe also has seed2026 clean at 0.56, not gated), but
    its **margin is gone**: it now sits at the edge, and the value Unit 8 proved was its edge (0.58) crashes. Re-tuned by the margin rule, the line freezes **0.54**, and the unseen seed2026 races **282.05 s**
    clean (Unit 8: 303.30 s; Checkpoint A: 310.80 s), where 0.58 is not clean.
  - **Local widening, as built, loses** (`p24`, `p25`): on `test-circuit` and seed2026 it is not clean at any raced f
    (0.50, 0.54, 0.56, 0.58, 0.60) with 60-waypoint windows, nor at 0.50–0.54 with 120-waypoint windows (with 200, seed2026 is clean at
    0.50 and `test-circuit` is not); the offsets must return to 0 within a few control points of each window's edge,
    a swing the follower cannot track at speed. On `monza-like` it is clean and lies between: 487.55 s at 0.60.
  - **History (`p10`–`p17`, kept for the lesson's trap):** the first line interpolated the control values linearly.
    It raced (299.35 s at 0.56 with the start pinned, `p10-test-circuit_monza-like-2.5.pkl`; unpinned it was 2.94 m
    off its line on the first tick), and its local widening was clean at 0.56 (300.40 s), so "local widening loses"
    depends on how it is built; the lesson and notes keep the qualifier "as built". Its kinks at every control point raised the Menger curvature (Σκ²Δs 0.2880 →
    0.3023) and capped the speed there. A pure-curvature objective (κ_i ≈ κ_c + κ_c² n_i + n''_i) halves those
    kinks but swings the line across the straights, and the follower crashes at every f; its full-resolution solve is
    too ill-conditioned for `lsq_linear` or L-BFGS-B in 500 s.
- **Cost.** A race is 2–5 s of CPU (a 900 s crash race on `monza-like` about 6 s); the `p19` cells run 5 races on
  8 workers.

## Deviations from design (recorded; design 013 v4.7)
- **§6 Unit 8:** per-section μ comes from **limit probes** (one section pushed per race, the student's own agent as
  the driver) and an acceleration percentile; the logs that `roar-004` generated cannot identify it ([sol] r2 B3
  there). Unit 8 also identifies the **steering gain**, which the probes show matters as much as μ. The gate gains
  its payoff: one fraction of the measured grip, tuned on the training family, transfers to the unseen track.
- **§6 Unit 9:** the "minimum-curvature line" is the **smoothest line** (the sum of squared second differences of its
  points, the usual quadratic stand-in for curvature), on a reduced problem (a cubic B-spline of offsets), because the
  probes show it lowers the total squared curvature by 19–41% and races, while a direct curvature objective does not
  race (above). "Local late-apex widening" becomes **local widening** (windows around tight corners, symmetric), and
  the comparison is honest: it loses. A late-apex window is a Challenge exercise. The line is solved **offline** (in
  the notebook, with `scipy.optimize.lsq_linear`) and its control values are shipped in the submission as constants,
  because a submission imports only numpy (`check_submission`'s allow-list, §4.1).
- **§7.1:** the routed pytest budget rises from 8 to **10 min** (it is 7.0 min; the Unit 8–9 gates add about 1.5).

## Buildout stays
The whole-book lesson total becomes 21 + 0.5 + 3 + 3 = 27.5, under 30.

## Concepts (5 new; all `kind: technique`, globally unique)
- Unit 8 (`unit-08-system-identification`), requires Units 1–7:
  - `linear-least-squares`: a linear model as a matrix of logged columns, `np.linalg.lstsq`, residuals and their RMS,
    choosing a lag by the residual; QR (`np.linalg.qr`) as how least squares is solved well, and the identity
    ‖Ac − b‖² = ‖Rc − Qᵀb‖² + const that Unit 9 uses;
  - `car-identification`: the longitudinal fit (a_T, a_B, c, lag) and the steering gain from steady rows, against the
    agent's assumed values; validation on rows the fit did not use;
  - `grip-identification`: limit probes one section at a time, |a| from the second difference of logged positions,
    the percentile estimate, excitation and the lower bound, and planning with a fraction of the measured grip.
- Unit 9 (`unit-09-racing-line`), requires Units 1–8:
  - `racing-line`: offsets along the normals, a cubic B-spline of control values (the reduced problem), width bounds
    with a margin that hold at every waypoint, the smoothest line as bounded linear least squares
    (`scipy.optimize.lsq_linear`), the start pin, following a line;
  - `line-retune`: re-tuning the speed for a new line, the line-relative clean rule, local widening, the honest
    comparison.
- `practices:` Unit 8 practises `repeated-run-measurement`, `race-telemetry`, `telemetry-plotting`,
  `longitudinal-map`, `friction-circle`, `cornering-speed-limit`, `speed-profile` and `section-knob-sweep`; Unit 9
  practises `menger-curvature`, `pure-pursuit`, `speed-profile`, `section-knob-sweep`, `grip-identification` and
  `repeated-run-measurement`.

## The reference submissions
- **`agents/unit-08.py`** = `agents/unit-07.py` with:
  - `MAX_STEER = math.radians(66.0)`, the identified steering gain (comment: Unit 8 measured it);
  - `MU_G`, six measured μ̂·g values (m/s², per track; the shipped values are `test-circuit`'s from `p6`, rounded
    to 0.01: `(7.89, 9.72, 8.65, 7.87, 8.30, 8.14)`), and `MU_FRACTION = 0.56`;
  - the cap min(TARGET_SPEED, √(`MU_FRACTION` · `MU_G`[section] · `GRIP`[section] / |κ_i|)) when `MU_G` is not
    `None`, and Unit 7's √(`A_LAT` · `GRIP`[section] / |κ_i|) when it is `None` (then it races exactly like
    `agents/unit-07.py` with 66°; asserted).
- **`agents/unit-09.py`** = `agents/unit-08.py` with:
  - `LINE_STEP = 10` and `LINE_CONTROL`, the line's control values for its track (a tuple of n // 10 floats; the
    shipped values are `test-circuit`'s, produced by the Unit 9 solver and written at full precision), or `None` for
    the centreline;
  - `__init__` evaluates the cubic B-spline at every waypoint (numpy only), moves its path points along the normals,
    and from then on measures, plans and pursues on its own points (`advance_index` and `nearest_index` included: a
    line 3.5 m off the centreline never comes within `REACHED_RADIUS` of a centreline waypoint);
  - `MU_FRACTION = 0.54`.
  - With `LINE_CONTROL = None` it races exactly like `agents/unit-08.py` at `MU_FRACTION = 0.54` (asserted).
- Both import only the standard library and numpy, and pass `check_submission` and the isolated 3.8 test.
- Per-track constants (`MU_G`, `LINE_CONTROL`) are written into variants with `write_variant` for the family and
  `monza-like` gates, exactly as Checkpoint A's settings were.

## Gates (pinned from the probes; a miss means stop, amend and re-gate)
Every pinned time is ±1 tick (0.05 s) of the probe median; "clean" is the clean rule on seeds 0–4 (the line-relative
rule for line races); "✗" asserts not clean, never a collision count. The routed test compares μ̂ with the car's
hidden table (tests are not student material); student material never does.

- **U8.1 the committed logs:** `roar-004`'s G4.6 assertions hold, now through `racekit.sysid_data` (the loader
  returns the same arrays as `read_log_csv`).
- **U8.2 the grip probe (`p6`):** routed test only (it reads the car's hidden table): on `test-circuit` every
  section's μ̂g/μg lies in [0.97, 1.02]; on `monza-like` sections 1–5 lie in [0.95, 1.02] and section 0 has 0 probe
  collisions and μ̂g/μg < 0.8. **The milestone and the solutions assert only measured, reproducible facts:** the six
  probe races reproduce the shipped `MU_G` (`test-circuit`) to 0.01 m/s², every `test-circuit` probe crashed at least
  once, and on `monza-like` section 0's probe has 0 collisions (so its number is reported as a lower bound, not an
  estimate). A section with ≤ 20 qualifying rows gives **no estimate**.
- **U8.3 the steering gain (`p7`, `p8`, `p9`):** the measured-μ planner at f 0.54 is not clean on `monza-like` at 70°
  and is clean at 66° through 0.62 (497.90 s); the Unit 7 reference at 66° is still not clean on seed2026.
- **U8.4 the transfer (`p8`):** at 66° with each track's own μ̂, 0.58 is clean on the five training tracks and 0.60
  is not clean on seed4; 0.56 is clean on seed2026 at 303.30 s, and 303.30 + 3 × the larger spread < 310.80
  (Checkpoint A's pinned race).
- **U8.5 the reference:** `agents/unit-08.py` on `test-circuit`, clean at 301.95 s; with `MU_G = None` it races
  exactly like `agents/unit-07.py` at 66°.
- **U9.1 the line is valid** (race-free): for the six `test-circuit` tracks and `monza-like`, |n_i| ≤ w_i − 2.5 m
  + 1e-9 at every waypoint, |n_i| ≤ 1e-9 on the 30 waypoints either side of the start, Σκ²Δs below the centreline's
  (`test-circuit` 0.2326 ± 0.002 against 0.2880) and the lap shorter; the shipped `LINE_CONTROL` re-solves to within
  1e-6 m.
- **U9.2 same f:** on `test-circuit` at 0.54 the line is clean at 279.60 s against the centreline's 304.70 s; on
  `monza-like` at 0.60, the line 473.45 s, local widening 487.55 s, the centreline 500.70 s, all clean.
- **U9.3 a new line breaks the tuning (the margin):** with the line, 0.58 (Unit 8's family edge) is not clean on
  seed4, while on the centreline 0.58 is clean on all five training tracks (U8.4); Unit 8's frozen 0.56 stays clean
  with the line (U9.4), now at the edge.
- **U9.4 the family and the transfer:** with the line, 0.56 is clean on the five training tracks; 0.54 is clean on
  seed2026 at 282.05 s, and 0.58 is not clean there.
- **U9.5 local widening loses on `test-circuit`:** with 60-waypoint windows it is not clean at 0.50.
- **U9.6 the reference:** `agents/unit-09.py` on `test-circuit` clean at 279.60 s; with `LINE_CONTROL = None` it
  races exactly like `agents/unit-08.py` at 0.54.
- **U8.6 the lab (`labs/real-sim.ipynb`):** passes `lab-check`; its racekit prediction cell asserts the procedure's
  numbers on racekit (the six probe races of `test-circuit` give `MU_G` as in U8.2, and the student's fit of the
  committed logs as in U8.1).

## Budgets
- Routed pytest: **≤ 10 min** (design v4.7) on this 8-core machine. The Unit 8–9 job table, shared jobs counted once:
  U8.2 12 probe races; U8.3 15 (`monza-like` at 70° f 0.54, at 66° f 0.62, the Unit 7 reference at 66° on seed2026);
  U8.4 35 (0.58 on five tracks, 0.60 on seed4, 0.56 on seed2026); U8.5 5 + 2 single-race equivalences; U9.2 25 (the
  line and the centreline at 0.54 on `test-circuit`, the line, local and centreline at 0.60 on `monza-like`); U9.3 5;
  U9.4 35 (0.56 on five tracks, 0.54 and 0.58 on seed2026); U9.5 5; U9.6 2 equivalences: **141 races**, 31 of them
  on `monza-like` (about 6 s of CPU each), the rest 2–5 s, about 2 min pooled on 8 workers; plus U9.1's seven line
  solves (about 40 s, race-free; `monza-like` 16 s). Measured in Phase E; over 10 min means stop and amend.
- Notebooks: Units 8–9 lessons, solutions and milestones **≤ 6 min** serial in total; the book-level exec total is
  reported against design v4.6's 30 CI-minutes (it was 20.4 min).
- The per-cell 120 s cap holds; a cell races at most one gate cell (≤ 10 races) or the six probe races.

## The CARLA lab (Unit 8, design §7.2)
`labs/real-sim.ipynb`, in the house form of the Unit 5 and Unit 7 labs:
1. record one race of the student's Unit 7 agent on CARLA Monza with the Unit 5 recorder, plus one steady lap
   (`TARGET_SPEED` fixed at 15 m/s, `SPEED_MODE = "flat"`);
2. fit the longitudinal map and the steering gain on their own logs, and compare with racekit's;
3. the six grip probes on CARLA (one race each, a section pushed with `GRIP[s] = 3.5`; each run stops at its first
   respawn or after 3 minutes), and μ̂ per section with the lesson's rules: a probe with no respawn gives a lower
   bound, and a section with ≤ 20 qualifying rows gives no estimate. A section without an estimate takes the lowest
   estimate on the lap; if **no** section has an estimate, the lab records "grip not identified" and step 4 races the
   student's Unit 7 setting with only the measured steering gain changed (66° or their own), by the same
   twice-each, stop-at-the-first-failure rule;
4. predict with racekit first (the asserted cell), then decide: ship 66° or the student's measured gain, and
   `MU_FRACTION` 0.54 for the first CARLA race (one grid step inside the racekit family's frozen 0.56, since CARLA is
   a track the family never saw), racing it twice and stopping at the first race that is not clean; then 0.52 the same
   way, then 0.50. The
   result is the first value clean on both of its races. If 0.50 also fails, **no setting is accepted**: the lab
   records "not clean at 0.50" and the student keeps their Unit 7 submission for CARLA (as the Unit 7 lab's
   PROVISIONAL result is flagged, never accepted); the lab never reports a value it did not race;
5. never commit results. Run budget: 2 recording runs + 6 probes + at most 6 races = 14 (short form: the steering gain
   from the steady run and at most 6 races, 7).

## Phases

### Phase A: agents, `sysid_data`, routed test and registry (Opus subagent for the code; registry inline)
- `racekit/sysid_data.py`: `LOGS` (the committed log names), `log_path(name)` and `load_log(name)` (via
  `read_log_csv`), py3.8-safe, numpy only; a unit test.
- `agents/unit-08.py` and `agents/unit-09.py` as above, from `agents/unit-07.py` and the probe agents
  (`u9line.py`'s line logic moves to the notebook solver; the agent keeps only the interpolation); equivalences
  asserted to the tick; the shipped `LINE_CONTROL` produced by the Unit 9 solver (QR + `bvls`) and pasted at full
  precision (a test re-solves and compares to 1e-6 m). The probes raced per-waypoint offsets; the agent rebuilds them
  from the control values, which can differ in the last bits, so Phase A **re-runs every Unit 9 gate cell** with the
  shipped agent and confirms each pin within ±1 tick (a miss means stop, amend and re-gate).
- `tests/_line_premise.py` (the job table, as `_checkpoint_premise.py`) and `tests/test_racekit_unit08_09_premise.py`
  (U8.1–U8.5, U9.1–U9.6); U9.1 is a fast, race-free test.
- `concepts.yaml` (5 ids), `coverage-map.yaml` (Unit 8 and Unit 9, `lessons: 3` each), manifests (Unit 8
  `lab: true`), `labs.yaml`.
- `api-order.yaml` / `baseline.yaml`: `lstsq` and `qr` → `linear-least-squares`; `lsq_linear` → `racing-line`; `load_log`,
  `log_path` → `car-identification`; `percentile` is infrastructure. Record any others in the report.
- `syllabus.md` rows (no emoji).
- Design 013 **v4.7** (the three deviations above, the status line and the changelog; the changelog notes that this
  is the third routed-budget raise, 5 → 8 → 10 min, and why).

### Phase B: Unit 8 content (Opus subagents: lesson + exercise statements; solutions in a separate fresh session)
- **Lesson:**
  1. The hook: "Your sim-tuned agent is slow, or crashes, on CARLA. Why?" The Unit 7 agent on `monza-like` and on
     seed2026: tuned on one track, it does not know the car.
  2. Least squares: a log as a matrix, `lstsq`, residuals, the lag chosen by the residual (U8.1); QR as how it is
     solved, and ‖Ac − b‖² = ‖Rc − Qᵀb‖² + const (the squared norms; the constant is the part of b outside A's
     column space).
  3. The longitudinal map and the steering gain from the committed logs: **measured** 65.7° against the agent's
     **assumed** 70° (never "the car's 66°": student material states measured values against assumed ones only).
  4. Grip: why the race log cannot identify it, the limit probe one section at a time, |a| from positions, the
     percentile, and the lower bound where the probe did not slide (U8.2).
  5. Using what was measured: 66° and f·μ̂ (U8.3), the family sweep of f and the transfer to the unseen track
     against Checkpoint A (U8.4); the reference (U8.5).
  6. To the real car: the lab.
- **Hidden truth (both units):** the subagents are told that lessons, exercises, solutions, milestones, teacher notes and
  the lab never import, read or quote `racekit._truth` or any ratio to the true μ; the agents round the measured gain
  to 66° and say so.
- **Exercises:** at least 6 and at least 2 stretch. Stretch: (a) identify the drag from a coast-down segment alone and
  compare with the full fit; (b) a probe at `GRIP[s] = 2.0` instead of 3.5: does it still slide, and what does the
  estimate become?
- `agents/unit-08.py`, its milestone, and `labs/real-sim.ipynb` (U8.6).

### Phase C: Unit 9 content (the same dispatch rule)
- **Lesson:**
  1. The hook: "The centreline is not the fast line, but a new line breaks your speed tuning." Unit 8's frozen value
     still finishes with the line, but its margin is gone: Unit 8's edge value crashes on a training track (U9.3).
  2. The line as offsets along the normals; the reduced problem as a cubic B-spline (four weights per waypoint, a
     weighted average, so bounds on the control values bound every waypoint); the smoothness objective as bounded
     linear least squares; `lsq_linear`; the start pin (U9.1). What the line changes: total curvature, length, and
     the one corner it makes tighter.
  3. The trap, shown briefly: linear interpolation of the control values puts a kink at each one, and the Menger
     curvature (and the speed cap) sees every kink.
  4. Following a line: the agent's own points (the `REACHED_RADIUS` trap); the line-relative clean rule.
  5. The honest comparison at the same f (U9.2), the re-tune on the family by the margin rule, and the transfer
     (U9.4); local widening, which loses (U9.5); the reference (U9.6).
- **Exercises:** at least 6 and at least 2 stretch. Stretch: (a) a late-apex window (more waypoints after the tight
  point than before) against the symmetric one; (b) the margin 2.5 m against 2.0 m: is the narrower margin worth its
  risk?
- `agents/unit-09.py` and its milestone. Notebooks solve the line once per track with QR + `bvls` (3–4 s; 16 s on
  `monza-like`).

### Phase D: teacher notes for both units (active session, inline)

### Phase E: verification (named)
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN; `bash scripts/pre-merge-guard.sh --pr` OK.
- Every gate holds in the routed test and the milestones; the lab passes `lab-check`; `check_submission` passes
  both new agents on an idle machine (the 5 ms step budget is wall-clock: never measured during a pooled probe).
- The routed suite ≤ 10 min and the Units 8–9 notebooks ≤ 6 min, measured; the report records both and the
  book-level exec total.
- The report repeats the PENDING interim CARLA check and the Unit 7 fragility as risks, and lists the follow-ups.

## Out of scope
- Any `racekit` change beyond `sysid_data`; new generated logs (the probes race live); MPC (Unit 10); robustness
  (Unit 11); many-knob tuning (Unit 12); a `monza-like` reference (Unit 13 races it).
- Identifying the yaw inertia, the tyre curve or l_f (the car's other hidden parameters are not identification
  targets, `roar-004`).

## Plan Review

### Round 1 (v1 @ 4daeffa)
- [self] APPROVE WITH NITS: N1 `qr` is mapped to Unit 8 but not in its lesson [FIXED v2, = [fable] S2]; N2 the probes
  raced per-waypoint offsets, the agent rebuilds them from B-spline control values [FIXED v2: Phase A re-runs every
  Unit 9 gate cell with the shipped agent, ±1 tick].
- [sol] REJECT:
  - **B** the lab could end at a PROVISIONAL 0.50 it never raced [FIXED v2: 0.54, 0.52, 0.50 twice each; the result
    is the first value clean on both races; otherwise no setting is accepted and the Unit 7 submission is kept].
  - **S** the race count was understated [FIXED v2: the job table recounted, 141 races, 31 on `monza-like`].
- [fable] APPROVE WITH NITS (every pinned number re-read from the pickles):
  - **S1** truth-relative numbers in student material [FIXED v2: U8.2's truth comparison is routed-test only; the
    milestone asserts reproducible measured facts; Phase B/C instruct the subagents; "measured 65.7° vs assumed 70°"];
  - **S2** QR used before it is taught [FIXED v2: Unit 8 teaches QR and the identity];
  - **S3** the Unit 9 hook overstated the break [FIXED v2: the margin is gone; Unit 8's frozen 0.56 stays clean];
  - **S4** the lab's PROVISIONAL wording and the probe's row rule [FIXED v2];
  - **S5** U9.1 needs a tolerance on the pin [FIXED v2: ≤ 1e-9];
  - **N1** 3–18 collisions [FIXED v2]; **N2** "every raced f" [FIXED v2]; **N3** the history's numbers pinned to the
    start-pinned `p10` file, and the first construction's local widening was clean, so "as built" stays [FIXED v2];
    **N4** the `monza-like` fragility note reconciled (a 450 s cap; clean at 900 s) [FIXED v2, Risks]; **N5** the race
    count [FIXED v2, = [sol] S]; **N6** the budget trend in the changelog [FIXED v2, Phase A].

### Round 2 (v2 @ 9cb1bf3)
- [sol] REJECT (every round-1 finding RESOLVED): **S** the lesson outline stated the QR identity with unsquared norms
  [FIXED v2.1]; **S** the lab's fallback was undefined when no section has an estimate [FIXED v2.1: "grip not
  identified", then the Unit 7 setting with the measured steering gain, by the same rule].
- [fable] APPROVE (every round-1 finding RESOLVED; job table re-summed to 141, ≈ 1.2 min CPU-pooled): N1 the lesson
  says "the five training tracks" for 0.56 [FIXED v2.1]; N2 stop at the first failed race [FIXED v2.1].
- [self] APPROVE.
