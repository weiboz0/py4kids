# Plan roar-006 — Units 6–7: grip and the speed limit, and speed planning

**Design:** `docs/designs/013-roar-book.md` **v4.3** (§4.4 items 2–3, §5, §6 Units 6–7, §7.1, §7.2, §7.3).
**Book:** `roar`. **Autopilot** per AGENTS.md.
**Base:** branches from `main` after `roar-005` merges (#160).
**v2** folds plan-review round 1 ([sol] REJECT: B the like-with-like comparison, B `qualification.md`, S the
friction-circle attribution; [fable] REJECT: S1 the profile lead, S2 one clean rule, S3 like with like, S4 the lab
budget, N1–N7; [self] the lab's 2 m rule). Unit 7 is re-probed (`q18`–`q21`) with the lead in seconds and one clean
rule; the reference and every Unit 7 pin change.
**v2.3** folds plan-review round 4 ([sol] B: the sidecar in progress order, tested on a shifted start; S: ignore it).
**v2.2** folds plan-review round 3 ([sol] B: the lab's section map by a recorder sidecar; S: the lab grid).
**v2.1** folds plan-review round 2 ([sol] REJECT: B the lab's run budget, B the interim check vs the lab's
fallback, S section 3's seed list, S U7.2's evidence class; [fable] APPROVE WITH NITS: S1–S2 the same two, N1–N7).

## Scope
- Unit 6 `roar/units/unit-06-grip-and-speed-limit/` and Unit 7 `roar/units/unit-07-speed-planning/`: lesson,
  exercises, solutions, teacher notes, manifest.
  Unit 7 is a lab unit: it ships `labs/real-sim.ipynb` (design §7.2).
- Reference submissions `agents/unit-06.py` and `agents/unit-07.py`; milestones
  `milestones/unit-06-grip-and-speed-limit.ipynb` and `milestones/unit-07-speed-planning.ipynb`.
- **No `racekit` library change.** Both units race the dynamic car and `carla_like`, which `roar-004` shipped
  (`DynamicCar`, `carla_like(noise)`, spin-out respawns, `grip_sections`). The test helper `_agent_premise.py` gains a
  car spec and a spin count (Phase A).
- A routed premise test for the Unit 6–7 gates, and a design 013 **v4.4** amendment (below).
- `roar/docs/qualification.md` is created with its interim-check section, and the Unit 7 reference's interim CARLA
  check (design §7.3) is recorded there and in the post-execution report as **PENDING (author)**.

## Probe evidence
All probes are in the session scratchpad `u06/`: `probe6.py` is `agents/unit-05.py` plus a `SPEED_MODE` switch
(`"flat"` = Unit 5 exactly, `"cap"`, `"profile"`) and the constants below (`probe6_v1.py` is the v1 prototype with a
waypoint-count lead); `harness.py` races it through `write_variant` and `run_race` in a process pool. The pin record
is `q8.txt`, `q11.txt` (Unit 6) and `q18.txt`–`q21.txt` (Unit 7 v2), unfiltered `summarize` output with each race's
max |offset|, and their `.pkl`. `q13.txt`–`q17.txt` are the v1 Unit 7 record (2-waypoint lead), kept as history.
Each race costs about 3–5 s of CPU (a 1500 s crash race about 11 s).

- **The hook (`q8`):** the Unit 5 agent at its flat 20 m/s **spins** on the dynamic car. On `DynamicCar()` (μ = 1)
  `test-circuit` gives 40 spin-outs and no finish in 1500 s; on `carla_like(noise=False)` 39. On `monza-like` it runs
  wide (23 collisions, 0 spins). Only `oval` is clean (216.50 s).
- **The curvature cap (`q8`, `q11`):** goal = min(TARGET_SPEED, √(A_LAT / κ_ahead)), with κ_ahead Unit 2's
  `curvature_ahead` (the largest |κ| over the next 25 waypoints, about 50 m). On `DynamicCar()` every A_LAT from 5
  to 9.5 is clean on `test-circuit` and 9.75 spins (36 spins); on `monza-like` 9.25 is clean and 9.5 spins. The edge
  sits just under μg = 9.81 m/s².
  On `carla_like(noise=False)` the edge moves down: `test-circuit` is clean to 7 and spins at 8 (19 spins);
  `monza-like` is clean to 8 and spins at 9. The car has less grip than μ = 1, and Unit 7 goes looking for it.
- **Speed planning (`q18`, `q19`):** a forward–backward profile (per-waypoint cap √(A_LAT·GRIP[section]/|κ|),
  a backward braking pass at A_DEC, a forward pass at A_ACC = 4) with TARGET_SPEED 45 m/s. The goal is the profile
  speed **a lead ahead of the car, measured in seconds of travel**: the first waypoint at least
  max(`PROFILE_LEAD_S`·v, 2 m) of path ahead of `current_index`. The lead pays for the speed loop's lag (the PI needs
  time to brake to the profile). At the base the lead barely changes the time (0.1–0.35 s in `q18` and 0.4–0.6 s in `q19`: 309.70–310.05 s), but at
  the grid's edge a short lead crashes: (A_DEC 4.0, A_LAT 5.0) collides on every seed at 0.1 and 0.15 s and is clean
  from 0.2 s; (6.0, 4.0) collides at 0.1 and 0.15 s, passes 2 m only from 0.25 s. `PROFILE_LEAD_S = 0.3` is inside the
  clean range everywhere probed.
- **The (A_LAT, A_DEC) trade (`q19`):** the clean A_LAT edge falls as the planned braking rate rises (5.2, 5.0, 4.8,
  4.8, 4.4 at A_DEC 3.0, 4.0, 4.5, 5.0, 6.0). The *car's* friction circle is part of the reason (braking hard into a
  corner leaves less grip for cornering), but the **planner** does not model it: its cornering cap and its braking
  pass are separate approximations, and a_lat² + a_dec² along the edge is not constant (36.0, 41.0, 43.3, 48.0,
  55.4). The speed loop arriving above the profile and the line pure pursuit drives also move the edge.
- **The lookahead must grow with speed (`q21`):** at 45 m/s pure pursuit with Unit 5's `PP_K = 0.3` collides on every
  seed, 0.4 on every seed; 0.5 is the smallest clean value, and 0.6 and 0.7 are no faster.
- **Per-section knobs (`q20`):** one multiplier per grip section on top of the global A_LAT. Swept one at a time from
  the base, sections 0–5 are clean up to 1.2, 1.5, 1.1, 1.1, 1.05, 1.1; **stacked, that vector collides on all 10
  seeds**. A **sequential pass** (sweep section 0 and keep its knob, then sweep section 1 on top, and so on) keeps
  (1.2, 1.4, 1.0, 1.0, 1.0, 1.0): sections 2–5 fail their first step on seed 4. That vector is clean on seeds 0–4 but
  only on 8 of seeds 0–9 (seeds 5 and 8 collide): it sits on the edge. One grid step back on every raised knob, (1.15, 1.3, 1.0, 1.0, 1.0,
  1.0), is clean on 10/10.
- **The agent's section map** (cumulative waypoint distance / lap length × 6, as `grip_sections`) equals
  `racekit.tracks.grip_sections` on every waypoint of all three tracks (checked in the probe; asserted in Phase A).

## Deviations from design (recorded)
- **"Per-section μ" is taught as per-section speed knobs.** The knob multiplies the planner's A_LAT in one section.
  It absorbs the grip and everything else the planner gets wrong there (the waypoints' curvature noise, the line pure
  pursuit actually drives, braking and cornering combined, the speed loop's lag behind the lead), so the tuned knobs
  are **not** μ estimates: `test-circuit`'s accepted knobs are (1.15, 1.3, 1.0, 1.0, 1.0, 1.0). The lesson says so in
  one paragraph and hands μ itself to Unit 8 (identification from logs). The design's gate is kept: per-section knobs
  beat the best global setting beyond the noise.
- **A_DEC is a planning knob in Unit 7.** The design names one global knob (μ) plus per-section knobs; the probe
  shows that the planned braking rate decides how much cornering speed is safe (`q19`). Unit 7 sweeps the
  (A_LAT, A_DEC) grid once, as two global knobs read together, and keeps the per-section sweep one-knob. Unit 12
  still owns many-knob tuning. The lead (`PROFILE_LEAD_S`) is fixed at 0.3 s from `q18`, shown in the lesson, and
  not swept by students beyond one exercise.
- **One clean rule for both units and the lab:** a race is *clean* when it finishes with 0 collisions **and** its
  max |cross-track error| on driving rows (`held == 0`) is at most 2 m. On a track 11–12 m wide a car 2 m off the
  line at 45 m/s is near the wall; CARLA's walls are not racekit's. Every Unit 6 clean row is under 1.2 m; every
  Unit 7 clean row under 1.9 m.
- **The margin rule.** Both units ship a global setting **one grid step inside the clean edge** (Unit 6: A_LAT 6
  where 7 is the last clean value on `carla_like`; Unit 7: A_LAT 4.6 at A_DEC 5.0, where 4.8 is the fastest clean
  edge), because five clean seeds do not prove the sixth and CARLA's grip is not racekit's. The per-section pass
  keeps the last clean step on five seeds, then checks the vector on ten; if that fails, every raised knob steps back
  once and the check repeats. `q20` shows why: the five-seed edge vector fails on seeds 5–9.
- **The reference `agents/unit-07.py` ships `GRIP = (1, 1, 1, 1, 1, 1)`.** A section is a fraction of *this* lap,
  so the knobs are per track; the lesson and milestone tune `test-circuit`, and the lab tunes the real car.
- **Routed budget: design §7.1 "Routed pytest ≤ 5 min" becomes ≤ 8 min (design v4.4).** The roar routed suite is
  4.5 min after `roar-005` on this 8-core machine; this plan's gates add about 270 races (about 17 CPU-minutes,
  about 2.2 min on 8 workers, [fable] r2 N6). Every multi-seed gate is asserted in full in the routed pool, which is cheaper than any
  notebook. The budget is stated for an 8-core CI machine and the report records the measured time; recorded as a
  user follow-up.

## Buildout stays
The whole-book lesson total becomes 15 + 3 + 3 = 21, under 30.

## Concepts (5 new; all `kind: technique`, globally unique)
- Unit 6 (`unit-06-grip-and-speed-limit`), requires Units 1–5:
  - `dynamic-bicycle`: slip angles at each axle, lateral tyre forces, the yaw equation; how it reduces to the
    kinematic bicycle at low speed;
  - `friction-circle`: the saturating tyre curve, the friction circle a_lat² + a_long² ≤ (μg)², the spin-out;
  - `cornering-speed-limit`: v_max = √(a_lat / |κ|), a curvature-limited speed goal from the curvature ahead.
- Unit 7 (`unit-07-speed-planning`), requires Units 1–6:
  - `speed-profile`: the forward–backward speed profile (per-waypoint cap, a backward braking pass
    v_i ≤ √(v_{i+1}² + 2·a_dec·Δs_i), a forward acceleration pass), and following it with a lead in seconds;
  - `section-knob-sweep`: per-section knobs by one-knob sweeps with Unit 1's median-and-spread rule; the clean rule;
    the stacking trap, the sequential pass, the ten-seed check and the margin rule.
- `practices:` both units practise `repeated-run-measurement`, `race-telemetry`, `menger-curvature`,
  `pid-control` and `pure-pursuit`; Unit 6 practises `kinematic-bicycle` (the low-speed limit) and
  `longitudinal-map`; Unit 7 practises `lookahead-tuning` (the 45 m/s re-tune), `friction-circle` and
  `cornering-speed-limit`.

## The reference submissions
- **`agents/unit-06.py`** = `agents/unit-05.py` (pure pursuit, `PP_K = 0.3`) with a `SPEED_MODE` switch:
  - `"cap"` (default): goal = min(`TARGET_SPEED`, √(`A_LAT` / κ_ahead)) when κ_ahead > 1e-9, with
    `A_LAT = 6.0` m/s² and `TARGET_SPEED = 20.0` m/s, fed to Unit 4's speed PI;
  - `"flat"`: races exactly like `agents/unit-05.py` (to the tick; asserted).
- **`agents/unit-07.py`** = `agents/unit-06.py` plus `SPEED_MODE = "profile"` (default) and the constants
  `TARGET_SPEED = 45.0`, `PP_K = 0.5`, `A_LAT = 4.6`, `A_DEC = 5.0`, `A_ACC = 4.0`, `PROFILE_LEAD_S = 0.3`,
  `LEAD_MIN_M = 2.0`, `GRIP = (1.0,) * 6`:
  - `__init__` keeps each segment's length, builds the section of every waypoint (cumulative distance / lap length
    × 6, clipped to 5), the per-waypoint cap min(TARGET_SPEED, √(A_LAT·GRIP[section] / |κ_i|)) with κ_i Unit 2's
    Menger curvature, one backward pass at A_DEC and one forward pass at A_ACC, each run twice around the lap so the
    wrap-around settles;
  - `step()` walks forward from `current_index` until the summed segment lengths reach
    max(PROFILE_LEAD_S·speed, LEAD_MIN_M) and sets the goal to the profile there;
  - `"cap"` races exactly like `agents/unit-06.py` when `TARGET_SPEED = 20.0`, `PP_K = 0.3` and `A_LAT = 6.0`
    (asserted).
- Both import only the standard library and numpy, and pass `check_submission` and the isolated 3.8 test.

## Gates (pinned from the probes; a miss means stop, amend and re-gate)
Deterministic races (no jitter: `DynamicCar()`, `carla_like(noise=False)`) are within ±0.05 s of the pins;
jittered (`carla_like(noise=True)`) medians within ±0.05 s and quoted spreads within ±0.05 s; clean/crash outcomes,
spin counts and the per-seed collision lists exact; max |offset| within ±0.01 m where quoted; noise-aware
comparisons strict (`racekit.measure.noise_aware_better`, or a median gap larger than both spreads). "Clean" is the
rule above. Every race uses seed `s` for `run_race`'s seed and `max_seconds` as stated. All jittered gates use
seeds 0–4 unless stated.

**Unit 6** (`q8`, `q11`):
- **U6.1, the hook:** the Unit 5 agent (`agents/unit-06.py` with `SPEED_MODE = "flat"`), `max_seconds=1500`:
  `DynamicCar()` `test-circuit` 40 spins and 40 collisions, not finished; `carla_like(noise=False)` `test-circuit`
  39 / 39; `DynamicCar()` `monza-like` 23 collisions, 0 spins, not finished; `DynamicCar()` `oval` clean 216.50 s.
  The lesson opens with both facts ([fable] N1): the car spins on `test-circuit` and runs wide on `monza-like`'s
  Parabolica-like bends; one cause, too much speed for the grip.
- **U6.2, the cap against μg** on `DynamicCar()`, `max_seconds=1500`:

  | A_LAT | 5 | 6 | 7 | 8 | 9 | 9.25 | 9.5 | 9.75 | 10 |
  |---|---|---|---|---|---|---|---|---|---|
  | `test-circuit` | 433.95 | 423.70 | 417.65 | 413.55 | 411.05 | 410.50 | 410.05 | 36 spins | 37 spins |
  | `monza-like` | 891.85 | 881.80 | 875.70 | 871.55 | 868.75 | 868.15 | 11 spins | 21 spins | 21 spins |

  Every number is a clean time unless it says spins (then the spin count, not finished). `oval` is 216.50 s at every
  A_LAT (the cap never binds below 20 m/s there; probe record, asserted at A_LAT 6 only, in U6.4).
- **U6.3, the cap on the carla-like car** (`carla_like(noise=False)`, `max_seconds=1500`): `test-circuit` 434.70 /
  424.30 / 418.40 s at A_LAT 5 / 6 / 7, and 19 spins at 8; `monza-like` 892.60 / 882.45 / 876.30 / 872.15 s at
  5–8, and 21 spins at 9. The edge is lower than U6.2's: less grip.
- **U6.4, the reference** (`agents/unit-06.py`, `carla_like(noise=True)`, seeds 0–4, `max_seconds=1500`): `oval`
  216.50 s (spread 0.10), `test-circuit` 422.65 s (0.30), `monza-like` 880.50 s (0.15), all 15 clean, 0 spins.
  With `SPEED_MODE = "flat"` it races exactly like `agents/unit-05.py` on `KinematicCar()` (`roar-005`'s U5.2 times
  and RMS).

**Unit 7** (`q18`–`q21`; all on `carla_like(noise=True)`, `test-circuit`, `max_seconds=600`, the reference's
constants unless stated):
- **U7.1, the lookahead at speed** (`q21`, `PP_K` varied): 0.3 collides on every seed [10, 9, 8, 9, 10]; 0.4 on
  every seed [6, 6, 6, 6, 6]; 0.5 is clean (U7.3); 0.6 and 0.7 are clean at 304.20 s (0.15), not faster than 0.5
  beyond the noise. The reference keeps the smallest clean value.
- **U7.2, the lead** (`q18`, `PROFILE_LEAD_S` ∈ {0.1, 0.15, 0.2, 0.25, 0.3, 0.35}, at A_DEC 4.0 with A_LAT 4.6 and
  5.0, and at A_DEC 6.0 with A_LAT 4.0): at (4.0, 4.6) every lead is clean (309.70–309.95 s, max |offset| falling
  from 1.53 to 1.25 m); at (4.0, 5.0) leads 0.1 and 0.15 collide on every seed and 0.2–0.35 are clean (303.25–303.35
  s); at (6.0, 4.0) 0.1 and 0.15 collide, 0.2 finishes without a collision but exceeds 2 m (max 2.03–2.36 m), and
  0.25–0.35 are clean. **Asserted:** the (4.0, 5.0) and (6.0, 4.0) rows at 0.15 and 0.3 (outcomes, collision lists,
  and the clean cells' medians and max |offset|); every other figure in U7.2 is probe record, labelled so in the lesson
  ([sol] r2 S2).
- **U7.3, the (A_LAT, A_DEC) grid** (`q19`, lead 0.3 s, `GRIP` all 1): median times; ✗ = not clean on any seed.

  | A_DEC \ A_LAT | 4.0 | 4.4 | 4.6 | 4.8 | 5.0 | 5.2 | 5.4 | 5.6 |
  |---|---|---|---|---|---|---|---|---|
  | 3.0 | 329.75 | 322.05 | 318.60 | 315.05 | 311.70 | 308.45 | ✗ | ✗ |
  | 4.0 | 320.50 | 313.25 | 309.80 | 306.55 | 303.25 | ✗ | ✗ | ✗ |
  | 4.5 | 317.30 | 310.05 | 306.70 | 303.40 | 4/5 | ✗ | ✗ | ✗ |
  | 5.0 | 314.65 | 307.55 | 304.15 | 300.90 | ✗ | ✗ | ✗ | ✗ |
  | 6.0 | 311.40 | 304.15 | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

  (4.5, 5.0) is clean on 4/5 seeds (seed 1: 1 collision). **Asserted:** each row's last clean cell (median and every
  seed's max |offset| ≤ 2 m) and first unclean cell (the unanimous ones on seeds 0–1 by their collision lists,
  (4.5, 5.0) by seed 1's single collision). The other cells are probe record, labelled so in the lesson.
  The gate: the clean edge in A_LAT falls as A_DEC rises; the fastest clean cell is (5.0, 4.8), and the reference's
  (5.0, 4.6) is one step inside it. An exercise computes a_lat² + a_dec² along the edge and asks why it is not
  constant (the planner's separate approximations, the speed loop, the driven line).
- **U7.4, the reference** (`agents/unit-07.py`): `test-circuit` 304.15 s (spread 0.20) over seeds 0–9, all clean;
  `oval` 152.75 s (0.10) and `monza-like` 515.10 s (0.15) over seeds 0–4, clean, `max_seconds=1500`, max |offset|
  0.81 / 1.67 m. Deterministic (seed 0): `carla_like(noise=False)` 152.75 / 304.80 / 515.45 s; `DynamicCar()`
  152.15 / 303.45 / 514.10 s.
- **U7.5, the gain over Unit 6:** on every track the Unit 7 median beats U6.4's beyond the noise (152.75 vs 216.50,
  304.15 (seeds 0–4: 304.15) vs 422.65, 515.10 vs 880.50 s), all clean: a large median gain at 0 collisions (design
  gate).
- **U7.6, one knob at a time, and the stacking trap** (`q20`): each section alone, swept up the grid (1.05, 1.1,
  1.15, 1.2, 1.3, 1.4, 1.5) on seeds 0–4 until the first unclean step, keeps (1.2, 1.5, 1.1, 1.1, 1.05, 1.1)
  (probe record, `q20.txt`; section 1's 1.5 is the grid's top, never an unclean step, [fable] r2 N5); **stacked, that vector collides 23 times on every one of seeds 0–9**. **Asserted:** each single
  knob's kept step clean on seeds 0–4, and the stack unclean on seeds 0–9.
- **U7.7, the sequential pass** (`q20`), sections 0→5, each step on seeds 0–4, stop at the first unclean step, keep
  the last clean one:

  | section | kept | the first unclean step |
  |---|---|---|
  | 0 | 1.2, 303.10 s | 1.3: collisions [9, 0, 0, 4, 13] |
  | 1 | 1.4, 298.35 s | 1.5: [23, 23, 23, 23, 23] |
  | 2, 4, 5 | 1.0 | 1.05: seed 4 collides 18 times, seeds 0–3 clean |
  | 3 | 1.0 | 1.05: seeds 1 and 4 collide 18 times each, [0, 18, 0, 0, 18] |

  The ten-seed check of the five-seed result (1.2, 1.4, 1.0, 1.0, 1.0, 1.0) fails: seeds 5 and 8 collide 18 times
  each (max 6.48 / 6.38 m), the other eight are clean. The vector sits on the edge: seeds 0–4 were not enough, and
  raising any later section by one step tipped seed 4 over (and seed 1 too in section 3). Section 1
  was clean alone at 1.5 (U7.6) and fails at 1.5 on top of section 0's 1.2: the lesson's concrete interaction. One step back on the raised
  knobs, **(1.15, 1.3, 1.0, 1.0, 1.0, 1.0): clean on seeds 0–9, 299.60 s (spread 0.15)**.
  **Asserted:** sections 0 and 1's kept and first-unclean steps, each of sections 2–5's per-seed collision list at 1.05 (from `q20`), the ten-seed
  failure of the edge vector (which seeds), and the accepted vector's ten-seed result.
- **U7.8, per-section knobs beat the best global setting** (design gate), like with like:
  - with margin: the accepted vector, 299.60 s (0.15), beats the reference (one step inside the global edge),
    304.15 s (0.20), beyond the noise;
  - against the edge: it also beats the **fastest clean global setting**, (A_DEC 5.0, A_LAT 4.8) on seeds 0–9,
    300.93 s (0.20), beyond the noise, although that global setting has no margin and the vector does.
  **Asserted:** all three ten-seed results and both comparisons.
- **U7.9, the section map:** the agent's section of every waypoint equals `grip_sections(load_track(name))` on all
  three tracks.
- **U7.10, the lab** (design §7.2): `labs/real-sim.ipynb` passes `lab-check` against the sample CSV. It races
  `agents/unit-07.py` on CARLA and splits the recording into the six sections **by the agent's own section map**
  ([sol] r3 B1). The telemetry CSV's columns are fixed (`racekit.telemetry.COLUMNS`), so the lab's recorder change
  (on top of Unit 5's) writes a **sidecar** once, at `initialize`: `<the CSV path>.sections.txt`, one integer per
  waypoint **in progress order** (line k is the section of waypoint (start_index + k) mod n, where `start_index` is
  the recorder's progress origin, the same one Unit 1's recorder uses), derived from `TELEMETRY_PATH` (the parameters
  cell stays the only place a file name appears). The analysis maps each driving row to
  `sections[progress % waypoints_per_lap]`, which is then the right waypoint for any start ([sol] r4 B1). Without the
  sidecar (the sample fixture has none) it falls back to equal progress slices and prints that they match the agent's
  sections only on evenly spaced waypoints. A routed test splices the recorder into `agents/unit-07.py`, races `oval`
  and asserts the sidecar equals `grip_sections(load_track("oval"))` and that the analysis maps every driving row to
  the sidecar's section of its waypoint; a second, direct test calls the recorder's sidecar writer with a shifted
  start (start_index 10 and n − 3) and checks the rotation, a row on the lap wrap and a row in lap 2. `.gitignore`
  gains `roar/**/labs/**/*.sections.txt` and `*.csv.sections.txt` beside the existing CSV rules, and the lab's "never
  commit results" note names the sidecar ([sol] r4 S2). Six sections by arc length are racekit's
  convention, not a property of Monza ([fable] r2 N4). It reports per section the
  time, the median and peak speed, the max |cross-track error| and the collisions (Unit 5's recorder change supplies
  the error). Its racekit-prediction cell races the reference on `monza-like` (`carla_like(noise=True)`, seed 0) and
  **asserts** that race's per-section times, peak errors and 0 collisions (pinned in Phase C from the shipped agent,
  ±0.05 s / ±0.01 m; the race is U7.4's seed 0).
  **The decision procedure** uses the unit's clean rule (finished, 0 collisions, every section's peak error ≤ 2 m):
  1. **Race `agents/unit-07.py` exactly as shipped, three laps** (its SHA-256 printed). For the author this first run
     *is* the design §7.3 interim check, recorded PASS or FAIL in `qualification.md`; a FAIL is surfaced as the §7.3
     follow-up (an errata/fix plan), never replaced by a later run ([sol] r2 B2, [fable] r2 S2).
  2. **Not clean:** the student's path to a usable lab (lab tuning, not the check): lower A_LAT one grid step (4.4,
     then 4.0) and race again, at most 2 runs.
  3. **Clean:** the sequential pass on CARLA on a coarse grid (1.1, 1.2, 1.3), one 3-lap run per step (so at most
     3 steps per section, [sol] r3 S1), sections in order, a section stopping at its first unclean step, and a **sweep budget of 12
     runs**: when it is spent the pass stops, the sections not yet tried stay at 1.0, and the printout names them
     ([sol] r2 B1, [fable] r2 N1). The short form sweeps sections 0–1 only.
  4. Re-race the result twice; if either run is not clean, step every raised knob back once (the margin rule) and
     re-race the stepped-back setting twice; if that fails too, the result is all knobs at 1.0, marked provisional
     (content gate [sol] r1 B).
  The worst case is 1 + 2 + 12 + 4 = 19 runs, about 3 hours at about 10 min per run; the short form fits one sitting
  ([fable] r2 N2). A host failure (the server exits, or the agent gets no first tick) is repeated, not counted. The
  lab prints the runs used. It says plainly that one run per step is weaker evidence than the lesson's five seeds,
  which is why step 4 exists ([fable] r2 N3). It names CARLA's spiky waypoint curvature (phantom braking in the profile, smoothed only downward by the
  backward pass) as a thing to look for, and points at Unit 9 for a smoothed line ([fable] N6).
  **Where each gate is asserted:** U6.1–U6.4 and U7.1–U7.9 in the routed test
  `tests/test_racekit_unit06_07_premise.py` as stated, in the session's parallel pool (`_premise.py`'s `race_all`);
  the milestones assert a trimmed subset (below); the lessons show the rest as the probe record, labelled so.

**Runtime.** The routed module races about 270 jobs (about 17 CPU-minutes, about 2.2 min on 8 workers; the roar suite then
about 6.5 min). The milestones
race seed 0 of U6.1 (`test-circuit` only), U6.2 at A_LAT 9.5 and 9.75, U6.4 on seed 0, U7.1 at 0.3 and 0.5, U7.2's
(4.0, 5.0) row at 0.15 and 0.3 on seed 0, U7.4 on seeds 0–4 of `test-circuit`, U7.6's stack on seed 0 and U7.7's
accepted vector on seeds 0–4 (about 3 min in all, sequential). Units 6–7 notebooks ≤ 6 min in total; the
post-execution report records the book-level exec total against the 15 CI-minute cap.

## Phases

### Phase A: agents, routed test and registry (Opus subagent for the code; registry inline)
- `agents/unit-06.py` and `agents/unit-07.py` as above, built from `agents/unit-05.py` with the probe's logic
  (`probe6.py`), the comments in the book's voice. `"flat"` and `"cap"` equivalences asserted to the tick.
- `_agent_premise.py` ([fable] N4): `AgentJob` gains a car spec (`"kinematic"` (today's `KinematicCar(jitter,
  lag_ticks)`), `"dynamic"` = `DynamicCar()`, `"carla0"` = `carla_like(noise=False)`, `"carla"` =
  `carla_like(noise=True)`) and `AgentOutcome` gains `spins` (`result.respawn_causes.count("spin")`) and the max
  |offset| on driving rows. Existing jobs keep the `"kinematic"` default, so `roar-005`'s routed test is unchanged.
- `tests/test_racekit_unit06_07_premise.py` and its jobs (U6.1–U6.4, U7.1–U7.8); the U7.9 section-map test is a fast
  separate test.
- `concepts.yaml` gets the 5 ids; `coverage-map.yaml` the Unit 6 and Unit 7 entries (`lessons: 3` each);
  manifests mirror them; Unit 7's manifest declares `lab: true`.
- `api-order.yaml`: every new callable the notebooks use, each mapped. Expected: `DynamicCar`, its `reset`,
  `advance`, `sideslip` and `spun_out` (the skidpad, [fable] N4; `mu_now` is an attribute, read in the lesson only,
  [fable] r2 N7) → `dynamic-bicycle` / `friction-circle`;
  `carla_like` → `cornering-speed-limit`; `grip_sections` → `section-knob-sweep`. Record any others in the report.
- `syllabus.md` rows for Units 6–7 (**no emoji**: the PDF font has no glyph for it; the Unit 7 row names the CARLA
  lab in words).
- `roar/docs/qualification.md` ([sol] B2): the design §7.3 record's skeleton (the final-qualification table, empty,
  and an **Interim checks** section with the `roar-006` row: `agents/unit-07.py` **as shipped**, untimed, 3 laps,
  0 collisions, PASS/FAIL on its first run,
  `PENDING (author)`, the submission's SHA-256 and the repository commit). It holds only the author's reference agent.
- Design 013 **v4.4**: the routed budget (≤ 8 min on an 8-core CI machine), the §6 Unit 7 row's per-section knob
  wording and the (A_LAT, A_DEC) grid, and the clean rule, citing this plan.

### Phase B: Unit 6 content (Opus subagents: lesson + exercise statements; solutions in a separate fresh session)
- **Lesson:**
  1. The hook: "Why does the car spin at Parabolica?" The Unit 5 agent on the dynamic car (U6.1): it spins on
     `test-circuit` and runs wide on `monza-like`.
  2. The dynamic bicycle: slip angles, lateral forces, the yaw equation; at low speed it agrees with Unit 3's
     kinematic bicycle (a short `DynamicCar` vs `KinematicCar` run at 5 m/s).
  3. Tyre saturation and the friction circle; a skidpad experiment on `DynamicCar` (speed ramped on a fixed steer
     until the lateral acceleration saturates near μg and the car spins).
  4. v_max = √(a_lat/|κ|), and the curvature cap built from Unit 2's `curvature_ahead`.
  5. The cap against μg (U6.2): the edge sits just under 9.81 m/s².
  6. The carla-like car (U6.3): the edge moves down, so the real grip is lower than the model's. The clean rule,
     the margin rule and the reference (U6.4).
  7. The bridge: the cap is safe and slow (it never goes above 20 m/s, and it brakes only when the corner is
     already close).
- **Exercises:** at least 6 `## Exercise N` and at least 2 stretch. Stretch: (a) the friction circle under combined
  braking and cornering on the skidpad (brake while turning, find where it spins); (b) the effect of κ_ahead's
  horizon (25 vs 10 waypoints) on the clean edge, in at most three races ([fable] r2 N6).
- `agents/unit-06.py` and its milestone.

### Phase C: Unit 7 content (the same dispatch rule)
- **Lesson:**
  1. The hook: "Brake *before* the corner, and find the grip that is really there." The Unit 6 agent is clean and
     slow (422.65 s on `test-circuit`).
  2. The forward–backward profile: the braking pass, the acceleration pass, the wrap-around; plot the profile
     against the Unit 6 goal.
  3. Racing the profile at 45 m/s: the steering lookahead must grow (U7.1), and the speed goal needs a lead in
     seconds (U7.2).
  4. Two knobs: the (A_LAT, A_DEC) grid (U7.3). The car's friction circle is part of the story, the planner's
     separate approximations and the speed loop the rest; the margin rule; the reference (U7.4) and its gain over
     Unit 6 (U7.5).
  5. Per-section knobs: one at a time and the stacking trap (U7.6), the sequential pass and the ten-seed check
     (U7.7), like with like (U7.8). The knobs are not μ; Unit 8 measures μ.
  6. To the real car: the lab.
- **Exercises:** at least 6 and at least 2 stretch, including a_lat² + a_dec² along the U7.3 edge. Stretch: (a) a
  backward pass that also respects the friction circle (brake less where the corner is tighter); (b) the order of
  the sequential pass (5→0 instead of 0→5) and whether it ends at the same knobs.
- `agents/unit-07.py`, its milestone, and `labs/real-sim.ipynb` (U7.10): the five design §7.2 steps briefly, with a
  pointer to the Unit 1 lab; the Unit 5 recorder change reused; the per-section analysis; the asserted racekit
  prediction; the decision procedure and its run budget; "never commit results".

### Phase D: teacher notes for both units (active session, inline)

### Phase E: verification (named)
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN.
- `bash scripts/pre-merge-guard.sh --pr` OK.
- All the gates hold in the routed test and the milestones; the lab passes `lab-check`.
- The routed roar pytest ≤ 8 min (measured on this 8-core machine); Units 6–7 notebooks ≤ 6 min; the report records
  both and the book-level exec total.
- `roar/docs/qualification.md` and the post-execution report both record the interim CARLA check (design §7.3) as
  **PENDING (author)**; it is surfaced as a follow-up, and `roar-008`'s plan review names it as a risk.

## Out of scope
- Any `racekit` library change; system identification (Unit 8); racing lines (Unit 9); many-knob tuning (Unit 12).
- Tuning `A_ACC`, `LEAD_MIN_M` or the speed PI gains (fixed at the probe's values; the lesson names them as knobs
  left for Unit 12).
- Shipping tuned `GRIP` values in the reference (they are per track).

## Plan Review

### Round 1 (v1 @ 5b3b7c4)
- [self] APPROVE WITH NITS: the lab's "peak error over 2 m" rule would flag sections where the reference itself
  exceeds 2 m on racekit; one rule must serve the sweep and the lab. [FIXED v2: the clean rule.]
- [sol] REJECT:
  - **B1** "Per-section knobs beat the best global" compared against the margin reference, not the best clean
    global (306.40 s at v1). [FIXED v2: U7.8 compares like with like, both ways.]
  - **B2** design §7.3 also requires the `qualification.md` record. [FIXED v2: Phase A creates it; Phase E checks it.]
  - **S** the planner does not implement the friction circle; the car does. [FIXED v2: Probe evidence, U7.3 and
    lesson §4 attribute the edge to the car's circle plus the planner's separate approximations.]
- [fable] REJECT:
  - **S1** the fixed 2-waypoint lead is a large, unexamined part of the grid edge, and a waypoint count does not
    transfer to CARLA. [FIXED v2: the lead is `PROFILE_LEAD_S` seconds of travel, swept in `q18` (U7.2), and the
    grid re-probed at 0.3 s.]
  - **S2** the sweep's clean rule (0 collisions) and the lab's (also peak error ≤ 2 m) disagree. [FIXED v2: one
    clean rule everywhere; the sequential pass re-run under it (`q20`).]
  - **S3** like with like. [FIXED v2: U7.8.]
  - **S4** the lab has no run budget. [FIXED v2: at most 12 runs, the procedure in U7.10.]
  - **N1** the hook's Parabolica wording. [FIXED v2: U6.1.] **N2** spreads' tolerance. [FIXED v2: ±0.05 s.]
    **N3** a one-seed cascade count is fragile. [FIXED v2: the v2 table has no such row; sections 2–5 assert seed 4's
    collision count, measured on the shipped agent.] **N4** the test helper's car spec, spins and the skidpad
    callables. [FIXED v2: Phase A.] **N5** the budget assumes 8 cores, and trims. [FIXED v2: stated for 8 cores;
    unclean grid cells asserted on seeds 0–1.] **N6** CARLA's spiky curvature and the section convention.
    [FIXED v2: U7.10.] **N7** the knobs absorb the lead's effect too. [FIXED v2: the deviation lists it.]

### Round 2 (v2 @ 742397a)
- [self] APPROVE WITH NITS: the reviewers' points below are right; nothing further.
- [sol] REJECT: its round-1 B1, B2 and S are resolved.
  - **B1** the 12-run lab cap cannot hold the sequential pass as specified. [FIXED v2.1: a coarse lab grid, at most
    3 steps per section, a 12-run sweep budget that stops the pass and names the untried sections.]
  - **B2** a lower-A_LAT run could be recorded as the reference's interim check. [FIXED v2.1: the check is the
    shipped agent's first run, PASS/FAIL; the fallback is lab tuning.]
  - **S1** section 3's seed list is [0, 18, 0, 0, 18], not seed 4 only. [FIXED v2.1: its own row; per-section lists
    asserted.]
  - **S2** U7.2's other figures had no evidence class. [FIXED v2.1: probe record, labelled.]
- [fable] APPROVE WITH NITS (all round-1 findings resolved; numbers re-raced and reproduced):
  - **S1** = [sol] S1. [FIXED v2.1.] **S2** = [sol] B2. [FIXED v2.1.]
  - **N1** = [sol] B1. [FIXED v2.1.] **N2** the lab's wall-clock cost and a short form. [FIXED v2.1.] **N3** one run
    per step is weaker evidence; say so. [FIXED v2.1.] **N4** split the recording with the agent's section formula.
    [FIXED v2.1.] **N5** section 1's 1.5 is the grid top. [FIXED v2.1.] **N6** recount (about 270 races, 17 CPU-min,
    2.2 min); the oval row's class; keep the horizon stretch to three races. [FIXED v2.1.] **N7** cite `q19` for
    leads 0.4–0.6; `mu_now` is an attribute. [FIXED v2.1.]

### Round 3 (v2.1 @ 7b58c69)
- [sol] REJECT: round-2 B1, B2, S1, S2 resolved.
  - **B1** the CSV schema cannot carry the agent's section boundaries, so the lab cannot reproduce them. [FIXED v2.2:
    the recorder writes a `.sections.txt` sidecar of the agent's section map; the analysis uses it, with a stated
    equal-slice fallback; a routed test checks the sidecar.]
  - **S1** the 1.5 grid value was unreachable within three steps. [FIXED v2.2: the lab grid is (1.1, 1.2, 1.3).]

### Round 4 (v2.2 @ ee5af8c)
- [sol] REJECT: round-3 B1 and S1 resolved in principle.
  - **B1** progress counts from the recorder's start index, so `sections[progress % n]` misreads a shifted start.
    [FIXED v2.3: the sidecar is written in progress order; a direct test covers a shifted start, the wrap and lap 2.]
  - **S2** the sidecar is not ignored by `.gitignore`. [FIXED v2.3: ignore rules and the lab's note.]

### Round 5 (v2.3 @ 789b51b): CONSENSUS
- [sol] APPROVE: round-4 B1 and S2 resolved; no findings.
- [fable] APPROVE WITH NITS (round 2); every nit folded in v2.1, and the v2.2–v2.3 changes touch only the lab's
  section map and ignore rules that [sol] reviewed.
- [self] APPROVE.

## Content Review

### Round 1 (implementation @ 5317c99, CI ALL GREEN)
- [self] APPROVE pending the fixes below. Both units open with their hook and a race before any theory; no student material reads or quotes `racekit/_truth.py`; `agents/unit-07.py`'s SHA-256 is unchanged since Phase A and matches `qualification.md`. The blind solvers' statement fixes were folded before the gate (Unit 6 Ex 6, 7; Unit 7 Ex 3, 6, 9).
- [sol] REJECT (blind-solved Unit 6 Ex 2, 4, 7 and Unit 7 Ex 2, 3, 6, all agreeing with the solutions; races not rerun, `uv` unavailable in its sandbox):
  - **B** [FIXED] The lab's step 4 stepped the knobs back after a failed re-race and ended without racing the new setting, so a student could finish on a setting never clean on CARLA. The stepped-back setting is now re-raced twice; if that fails too, the result is all knobs at 1.0, printed as PROVISIONAL. The worst case becomes 1 + 2 + 12 + 4 = 19 runs (short form 13); the plan's lab procedure is amended to match, and the replay cell asserts the step-back path.
  - **S** [FIXED] The replay accepted runs logged after the procedure ended. It now raises on any leftover run, asserted in the cell.
- [fable] APPROVE WITH NITS (blind-solved Unit 6 Ex 2, 4, 7 and Unit 7 Ex 2, 3, 6 to the printed values, all agreeing; spot-checked lesson numbers; hygiene, provenance, the hidden truth, the sidecar and its ignore rules, the registry and the `tools/labs.py` carve-out all checked):
  - **S1** [FIXED] Both teacher notes cited the plan's outline section numbers; the Pacing citations now match the shipped lessons (Unit 6: hook and §1, §§2–3, §§4–6; Unit 7: hook and §§1–2, §3, §4, the lab §5).
  - **N2** [FIXED] Unit 7 solutions Ex 3's prediction now gives the walk's waypoints 2, 2, 2, 4, 5, 7 (segments just under 2 m).
  - **N3** [FIXED] Unit 6 Exercise 6's run time reads "about a minute" in both notebooks.
  - **N4** [FIXED] Unit 6 solutions Ex 5's diagnosis prints the computed excess instead of a hard-coded 22%.
  - **N5** [WONTFIX] The Probe-evidence range 309.70–310.05 s covers both `q18` and `q19` (the lead in `q19` at 0.4–0.6 s); U7.2's 309.70–309.95 s is `q18` alone. Both are right.

### Round 2 (fixes @ 51e41be, CI ALL GREEN): CONSENSUS
- [sol] APPROVE: B and S verified fixed (cell 12 executed with its asserts and focused checks of every terminal path); the plan's 19-run maximum matches the code; no regressions.
- [fable] APPROVE WITH NITS: S1 and N2–N4 verified fixed, N5's WONTFIX accepted; the lab fix verified on five further scenarios.
  - **N1** [FIXED] Unit 7 teacher notes' lab bullet now describes the re-raced step-back and the provisional result.
  - **N2** [FIXED] The lab's "runs used … of at most" line prints 13 in the short form.
- [self] APPROVE.

## Post-Execution Report

**Status: SHIPPED.** Units 6–7 are complete:
- Unit 6 puts the car on tyres: the dynamic bicycle, the friction circle and a curvature speed cap (`agents/unit-06.py`, safe and slow: `carla_like` medians 216.50 / 422.65 / 880.50 s, all clean);
- Unit 7 plans the lap with a forward–backward speed profile and tunes per-section knobs (`agents/unit-07.py`: `test-circuit` 304.15 s on ten seeds, spread 0.20, all clean; `oval` 152.75 s; `monza-like` 515.10 s), with the CARLA lab.

**Verification.**
- `TMPDIR=/dev/shm bash scripts/ci-local.sh`: ALL GREEN at 5317c99, at 51e41be (the content-gate fixes; routed roar suite 406 passed in 376.3 s) and at the final commit (round-2 nits and this report).
- Every gate U6.1–U6.4 and U7.1–U7.10 is asserted, in the routed test (`test_racekit_unit06_07_premise.py`, 24 tests; `test_racekit_unit07_lab.py`, 4 tests) and in the milestones.
- The routed roar suite: 406 passed in 378.6 s (6.3 min, under the 8-min cap of design v4.4, on this 8-core machine).
- Units 6–7 notebooks, measured by their authors: Unit 6 lesson 45 s, solutions 79 s, milestone 72 s; Unit 7 lesson 37 s, solutions 58 s, milestone 49 s; about 340 s in total, under the plan's 6 min.
- The lab passes `lab-check`; the lesson buildout total is 21, under 30.
- `agents/unit-07.py` SHA-256 `4d56c05b…eb9f` is unchanged since Phase A; `qualification.md` records it.

**Deviations from the plan (recorded).**
1. **Tooling: `tools/labs.py`'s simulator-mention regex** flagged `racekit.carla_like` as a CARLA call in the lab's racekit prediction cell. It is now `carla(?!_like)|competition_runner|subprocess`, with a test (`tests/test_labs.py`: `carla_like` alone passes; `carla_like` with `import carla` still fails). A tooling change outside the phases' file list, made to let the planned lab pass the planned check.
2. **U6.4's seed-0 times are probe record** (`q8`: 216.50 / 422.55 / 880.40 s), not plan text: the plan quotes only the five-seed medians. The lesson and the milestone assert them, labelled "seed 0 of the probe record".
3. **One extra U7.2 job:** the (A_DEC 6.0, A_LAT 4.0) cell at the reference lead 0.3 s on seeds 0–4. It is not a U7.3 edge cell; the (4.0, 5.0) cell is, and is reused.
4. **Interpretation choices in the routed test:**
   - U7.4's max |offset| (0.81 / 1.67 m) is read as the median of the per-seed maxima, ±0.01;
   - U7.2's clean cells assert q18's per-seed max |offset| lists, ±0.01; U7.7 asserts seeds 5 and 8 at 6.48 / 6.38 m;
   - U7.7 also asserts that section 1 at 1.5 *alone* is clean (the plan's "concrete interaction");
   - the job table lives in a new helper, `_speed_premise.py`, rather than inside `_agent_premise.py`.
   The milestone checks the accepted vector on seeds 0–4 (median 299.60 s); the ten-seed check is in the routed test.
5. **The lab's racekit prediction is pinned** on `monza-like`, `carla_like` (noisy), seed 0: 515.10 s; per-section time / max |error|: 67.85 / 0.265, 93.50 / 1.624, 102.90 / 1.554, 73.10 / 1.672, 92.70 / 0.444, 85.05 / 1.594.
6. **Exercise statements** were clarified after the blind solves (Unit 6 Ex 6, 7; Unit 7 Ex 3, 6, 9), before the content gate.
7. **The lab's step 4 was tightened by the content gate** ([sol] r1 B): a stepped-back setting is re-raced twice, and a further failure gives a provisional all-1.0 result; the worst case is 19 runs (short form 13) where the gated plan said 17, and the plan's procedure is amended to match.

**Interim CARLA check (design §7.3): PENDING (author).** The first run of `agents/unit-07.py` as shipped, untimed, 3 laps, 0 collisions, on the pinned stack. It is recorded in `roar/docs/qualification.md`, surfaced as a user follow-up, and `roar-008`'s plan review names it as a risk.

**Follow-ups (held for the end of the run):** the routed budget raise to 8 min (design v4.4); the knobs-are-not-μ and A_DEC-as-planning-knob deviations; the interim CARLA check.
