# Plan roar-006 — Units 6–7: grip and the speed limit, and speed planning

**Design:** `docs/designs/013-roar-book.md` **v4.3** (§4.4 items 2–3, §5, §6 Units 6–7, §7.1, §7.2, §7.3).
**Book:** `roar`. **Autopilot** per AGENTS.md.
**Base:** branches from `main` after `roar-005` merges (#160).

## Scope
- Unit 6 `roar/units/unit-06-grip-and-speed-limit/` and Unit 7 `roar/units/unit-07-speed-planning/`: lesson,
  exercises, solutions, teacher notes, manifest.
  Unit 7 is a lab unit: it ships `labs/real-sim.ipynb` (design §7.2).
- Reference submissions `agents/unit-06.py` and `agents/unit-07.py`; milestones
  `milestones/unit-06-grip-and-speed-limit.ipynb` and `milestones/unit-07-speed-planning.ipynb`.
- **No `racekit` change.** Both units race the dynamic car and `carla_like`, which `roar-004` shipped
  (`DynamicCar`, `carla_like(noise)`, spin-out respawns, `grip_sections`).
- A routed premise test for the Unit 6–7 gates, and a design 013 **v4.4** amendment (below).
- The interim CARLA check of design §7.3 for the Unit 7 reference is recorded as **PENDING (author)**.

## Probe evidence
All probes are in the session scratchpad `u06/`: `probe6.py` is `agents/unit-05.py` plus a `SPEED_MODE` switch
(`"flat"` = Unit 5 exactly, `"cap"`, `"profile"`) and the constants below; `harness.py` races it through
`write_variant` and `run_race` in a process pool. The pin record is the files `q8.txt`, `q11.txt`, `q13.txt`–`q17.txt`
(unfiltered `summarize` output, each with its `.pkl`). Each race costs about 3–5 s of CPU (a 1500 s crash race about
11 s).

- **The hook (`q8`):** the Unit 5 agent at its flat 20 m/s **spins** on the dynamic car. On `DynamicCar()` (μ = 1)
  `test-circuit` gives 40 spin-outs and no finish in 1500 s; on `carla_like(noise=False)` 39. On `monza-like` it runs
  wide (23 collisions, 0 spins). Only `oval` is clean (216.50 s).
- **The curvature cap (`q8`, `q11`):** goal = min(TARGET_SPEED, √(A_LAT / κ_ahead)), with κ_ahead Unit 2's
  `curvature_ahead` (the largest |κ| over the next 25 waypoints, about 50 m). On `DynamicCar()` every A_LAT from 5
  to 9.5 is clean on `test-circuit` and 9.75 spins (36 spins); on `monza-like` 9.25 is clean and 9.5 spins. The edge
  sits just under μg = 9.81 m/s², where the friction circle says it must.
  On `carla_like(noise=False)` the edge moves down: `test-circuit` is clean to 7 and spins at 8 (19 spins);
  `monza-like` is clean to 8 and spins at 9. The car has less grip than μ = 1, and Unit 7 goes looking for it.
- **Speed planning (`q13`, `q14`):** a forward–backward profile (per-waypoint cap √(A_LAT·GRIP[section]/|κ|),
  a backward braking pass at A_DEC, a forward pass at A_ACC = 4, target = profile[current_index + 2]) with
  TARGET_SPEED 45 m/s. The planner's A_LAT and A_DEC **share the friction circle**: planning to brake hard into a
  corner leaves less grip for cornering. On `carla_like(noise=True)` the clean A_LAT edge falls as A_DEC rises
  (`q14`, five seeds each).
- **The lookahead must grow with speed (`q8`, `q16`):** at 45 m/s pure pursuit with Unit 5's `PP_K = 0.3` spins on
  every seed, 0.4 on four of five; 0.5 is the smallest clean value, and 0.6 and 0.7 are no faster.
- **Per-section knobs (`q15`–`q17`):** one multiplier per grip section on top of the global A_LAT. Swept one at a
  time from the base, every section has a clean knob above 1; **stacked, those knobs crash on every seed**, even one
  grid step back. A **sequential pass** (sweep section 0, keep its knob, then sweep section 1 on top, and so on)
  ends clean on 10/10 seeds and 8.0 s faster than the base.
- **The agent's section map** (cumulative waypoint distance / lap length × 6, as `grip_sections`) equals
  `racekit.tracks.grip_sections` on every waypoint of all three tracks (checked in the probe; asserted in Phase A).

## Deviations from design (recorded)
- **"Per-section μ" is taught as per-section speed knobs.** The knob multiplies the planner's A_LAT in one section.
  It absorbs the grip and everything else the planner gets wrong there (the waypoints' curvature noise, the line pure
  pursuit actually drives, the braking and cornering it combines), so the tuned knobs are **not** μ estimates:
  `test-circuit`'s sequential knobs are (1.5, 1.0, 1.15, 1.1, 1.05, 1.1). The lesson says so in one paragraph and
  hands μ itself to Unit 8 (identification from logs). The design's gate is unchanged: per-section knobs beat the
  best global setting beyond the noise.
- **A_DEC is a planning knob in Unit 7.** The design names one global knob (μ) plus per-section knobs; the probe
  shows that the braking rate the planner assumes decides how much cornering grip is left (`q13`, `q14`). Unit 7
  therefore sweeps the (A_LAT, A_DEC) grid once, as two global knobs read together through the friction circle, and
  keeps the per-section sweep one-knob. Unit 12 still owns many-knob tuning.
- **The margin rule.** Both units pick a global setting **one grid step inside the clean edge** (Unit 6: A_LAT 6
  where 7 is the last clean value on `carla_like`; Unit 7: A_LAT 4.6 where 4.8 is the last clean value at
  A_DEC 4.0), because five clean seeds do not prove the sixth, and CARLA's grip is not racekit's. The per-section
  pass keeps the last clean step and then checks the whole vector on 10 seeds.
- **The reference `agents/unit-07.py` ships `GRIP = (1, 1, 1, 1, 1, 1)`.** The knobs are tuned per track (a
  section is a fraction of *this* lap), so the shipped default is track-free; the lesson and milestone tune
  `test-circuit`, and the lab tunes the real car.
- **Routed budget: design §7.1 "Routed pytest ≤ 5 min" becomes ≤ 8 min (design v4.4).** The roar routed suite is
  4.5 min after `roar-005`; this plan's gates add about 17 CPU-minutes of races (about 130 s on 8 workers). Every
  multi-seed gate is asserted in full in the routed pool, which is cheaper than any notebook. Recorded as a user
  follow-up.

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
    v_i ≤ √(v_{i+1}² + 2·a_dec·Δs_i), a forward acceleration pass), and following it with a small lead;
  - `section-knob-sweep`: per-section knobs by one-knob sweeps with Unit 1's median-and-spread rule; the stacking
    trap and the sequential pass; the margin rule.
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
  `TARGET_SPEED = 45.0`, `PP_K = 0.5`, `A_LAT = 4.6`, `A_DEC = 4.0`, `A_ACC = 4.0`, `PROFILE_LEAD = 2`,
  `GRIP = (1.0,) * 6`:
  - `__init__` builds the section of every waypoint (cumulative distance / lap length × 6, clipped to 5), the
    per-waypoint cap min(TARGET_SPEED, √(A_LAT·GRIP[section] / |κ_i|)) with κ_i Unit 2's Menger curvature, one
    backward pass at A_DEC and one forward pass at A_ACC, each run twice around the lap so the wrap-around settles;
  - `step()` sets goal = profile[(current_index + PROFILE_LEAD) mod n];
  - `"cap"` races exactly like `agents/unit-06.py` when `TARGET_SPEED = 20.0`, `PP_K = 0.3` and `A_LAT = 6.0`
    (asserted).
- Both import only the standard library and numpy, and pass `check_submission` and the isolated 3.8 test.

## Gates (pinned from the probes; a miss means stop, amend and re-gate)
Deterministic races (no jitter: `DynamicCar()`, `carla_like(noise=False)`) are within ±0.05 s of the pins;
jittered (`carla_like(noise=True)`) medians within ±0.05 s; clean/crash outcomes, spin counts and the per-seed
collision lists exact; noise-aware comparisons strict (`racekit.measure.noise_aware_better`, or a median gap larger
than both spreads). "Clean" means finished with 0 collisions. Every race uses seed `s` for `run_race`'s seed and
`max_seconds` as stated. All jittered gates use seeds 0–4 unless stated.

**Unit 6** (`q8`, `q11`):
- **U6.1, the hook:** the Unit 5 agent (`agents/unit-06.py` with `SPEED_MODE = "flat"`), `max_seconds=1500`:
  `DynamicCar()` `test-circuit` 40 spins and 40 collisions, not finished; `carla_like(noise=False)` `test-circuit`
  39 / 39; `DynamicCar()` `monza-like` 23 collisions, 0 spins, not finished; `DynamicCar()` `oval` clean 216.50 s.
- **U6.2, the cap against μg** on `DynamicCar()`, `max_seconds=1500`:

  | A_LAT | 5 | 6 | 7 | 8 | 9 | 9.25 | 9.5 | 9.75 | 10 |
  |---|---|---|---|---|---|---|---|---|---|
  | `test-circuit` | 433.95 | 423.70 | 417.65 | 413.55 | 411.05 | 410.50 | 410.05 | 36 spins | 37 spins |
  | `monza-like` | 891.85 | 881.80 | 875.70 | 871.55 | 868.75 | 868.15 | 11 spins | 21 spins | 21 spins |

  Every number is a clean time unless it says spins (then the spin count, not finished). `oval` is 216.50 s at every
  A_LAT (the cap never binds below 20 m/s there).
- **U6.3, the cap on the carla-like car** (`carla_like(noise=False)`, `max_seconds=1500`): `test-circuit` 434.70 /
  424.30 / 418.40 s at A_LAT 5 / 6 / 7, and 19 spins at 8; `monza-like` 892.60 / 882.45 / 876.30 / 872.15 s at
  5–8, and 21 spins at 9. The edge is lower than U6.2's: less grip.
- **U6.4, the reference** (`agents/unit-06.py`, `carla_like(noise=True)`, seeds 0–4, `max_seconds=1500`): `oval`
  216.50 s (spread 0.10), `test-circuit` 422.65 s (0.30), `monza-like` 880.50 s (0.15), all 15 clean, 0 spins.
  With `SPEED_MODE = "flat"` it races exactly like `agents/unit-05.py` on `KinematicCar()` (`roar-005`'s U5.2 times
  and RMS).

**Unit 7** (`q14`–`q17`; all on `carla_like(noise=True)`, `test-circuit`, `max_seconds=600`):
- **U7.1, the lookahead at speed** (the reference with `PP_K` varied): 0.3 collides on every seed [7, 6, 7, 7, 7];
  0.4 collides on seeds 1–4 [0, 1, 2, 2, 1]; 0.5 is clean, 309.70 s (spread 0.05); 0.6 309.70 (0.10) and 0.7
  309.75 (0.05) are clean and not faster beyond the noise. The reference keeps the smallest clean value.
- **U7.2, the (A_LAT, A_DEC) grid** (`GRIP` all 1): median times; ✗ = collides on every seed.

  | A_DEC \ A_LAT | 3.7 | 4.0 | 4.2 | 4.4 | 4.6 | 4.8 | 5.0 |
  |---|---|---|---|---|---|---|---|
  | 3.0 | 335.85 | 329.55 | 325.70 | 321.90 | 318.35 | 314.90 | 311.55 |
  | 4.0 | 326.45 | 320.40 | 316.70 | 313.20 | 309.70 | 306.40 | ✗ |
  | 4.5 | 323.00 | 317.25 | 313.60 | 310.00 | 306.60 | ✗ | ✗ |
  | 5.0 | 320.55 | 314.80 | 311.10 | 307.60 | ✗ | ✗ | ✗ |
  | 6.0 | 318.15 | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

  **Asserted in the routed test:** the edge cells and their clean neighbours: (6.0, 3.7) clean and (6.0, 4.0) ✗;
  (5.0, 4.4) clean and (5.0, 4.6) ✗; (4.5, 4.6) clean and (4.5, 4.8) ✗; (4.0, 4.6) and (4.0, 4.8) clean and
  (4.0, 5.0) ✗; (3.0, 5.0) clean. The other cells are probe record, shown in the lesson as a table labelled so.
  The gate: the clean edge in A_LAT falls as A_DEC rises (the friction circle), and the reference's (4.0, 4.6) is one
  step inside the edge.
- **U7.3, the reference** (`agents/unit-07.py`): `test-circuit` 309.68 s (spread 0.25) over seeds 0–9, all clean;
  `oval` 153.80 s (0.10) and `monza-like` 520.55 s (0.10) over seeds 0–4, clean, `max_seconds=1500`. Deterministic
  (seed 0): `carla_like(noise=False)` 153.85 / 310.30 / 520.95 s; `DynamicCar()` 153.30 / 309.15 / 519.65 s.
- **U7.4, the gain over Unit 6:** on every track the Unit 7 median beats U6.4's beyond the noise
  (153.80 vs 216.50, 309.70 vs 422.65 on seeds 0–4, 520.55 vs 880.50 s), all clean: a large median gain at 0
  collisions (design gate).
- **U7.5, one knob at a time** (on the reference, `GRIP` one section raised, seeds 0–4): each section alone is
  clean up to a knob above 1 (probe record, `q15`: sections 0–5 clean up to 1.5, 1.5, 1.15, 1.1, 1.05, 1.1);
  **stacked, `GRIP = (1.5, 1.5, 1.15, 1.1, 1.05, 1.1)` collides on every one of seeds 0–9 (29 collisions each), and
  so does one step back, (1.4, 1.4, 1.1, 1.05, 1.0, 1.05).** Asserted: both stacks collide on seeds 0–9.
- **U7.6, the sequential pass** (`q17`), grid (1.05, 1.1, 1.15, 1.2, 1.3, 1.4, 1.5), sections 0→5, each step on
  seeds 0–4, stop at the first step that is not clean on all five, keep the last clean step:

  | section | kept | the first unclean step (collisions per seed) |
  |---|---|---|
  | 0 | 1.5 (grid top), 307.40 s | — |
  | 1 | 1.0 | 1.05: [21, 0, 0, 0, 0] |
  | 2 | 1.15, 305.30 s | 1.2: [13, 14, 13, 12, 15] |
  | 3 | 1.1, 303.55 s | 1.15: [0, 0, 3, 0, 0] |
  | 4 | 1.05, 303.15 s | 1.1: [10, 9, 11, 9, 9] |
  | 5 | 1.1, 301.70 s | 1.15: [6, 6, 8, 8, 8] |

  Section 1 is clean alone up to 1.5 (U7.5) and fails at 1.05 once section 0 is at 1.5: the braking zone into
  section 1 starts in section 0. **Asserted:** each section's kept step (clean, with its median) and its first
  unclean step (its collision list), in the context of the earlier sections' kept knobs: 10 steps on five seeds.
  The intermediate clean steps are probe record. Then the final vector
  `(1.5, 1.0, 1.15, 1.1, 1.05, 1.1)` clean on seeds 0–9 with median 301.68 s (spread 0.20), beating the reference's
  309.68 s (0.25) beyond the noise: **per-section knobs beat the best global setting** (design gate).
- **U7.7, the section map:** the agent's section of every waypoint equals `grip_sections(load_track(name))` on all
  three tracks.
- **U7.8, the lab** (design §7.2): `labs/real-sim.ipynb` passes `lab-check` against the sample CSV. It races
  `agents/unit-07.py` on CARLA (the design §7.3 interim check: 3 laps, 0 collisions, untimed), splits the recording
  into the six sections by progress, and reports per section the time, the median and peak speed, the max
  |cross-track error| and the collisions (Unit 5's recorder change supplies the error). Its racekit-prediction cell
  races the reference on `monza-like` (`carla_like(noise=True)`, seed 0) and **asserts** that race's per-section
  times and collisions (pinned in Phase C from the shipped agent, ±0.05 s; it is a deterministic function of the
  U7.3 race). The decision procedure: a section with a collision or a peak error over 2 m gets its knob lowered by
  one step, then the sequential pass on CARLA within a stated run budget; the margin rule applies.
  **Where each gate is asserted:** U6.1–U6.4 and U7.1–U7.7 in full in the routed test
  `tests/test_racekit_unit06_07_premise.py`, in the session's parallel pool (`_premise.py`'s `race_all`); the
  milestones assert a trimmed subset (below); the lessons show the rest as the probe record, labelled so.

**Runtime.** The routed module races about 230 jobs (about 17 CPU-minutes, about 130 s on 8 workers). The milestones
race seed 0 of U6.1 (`test-circuit` only), U6.2 at A_LAT 9.5 and 9.75, U6.4 on seed 0, U7.1 at 0.3 and 0.5, U7.3 on
seeds 0–4 of `test-circuit`, U7.5's first stack on seed 0 and U7.6's final vector on seeds 0–4 (about 3 min in all,
sequential). Units 6–7 notebooks ≤ 6 min in total; the post-execution report records the book-level exec total
against the 15 CI-minute cap.

## Phases

### Phase A: agents, routed test and registry (Opus subagent for the code; registry inline)
- `agents/unit-06.py` and `agents/unit-07.py` as above, built from `agents/unit-05.py` with the probe's logic
  (`probe6.py`), the comments in the book's voice. `"flat"` and `"cap"` equivalences asserted to the tick.
- `tests/test_racekit_unit06_07_premise.py` and its jobs in `_premise.py` (U6.1–U6.4, U7.1–U7.7), reusing the
  `agent_premise` fixture pattern; the U7.7 section-map test is a fast separate test.
- `concepts.yaml` gets the 5 ids; `coverage-map.yaml` the Unit 6 and Unit 7 entries (`lessons: 3` each);
  manifests mirror them; Unit 7's manifest declares `lab: true`.
- `api-order.yaml`: any new callables the notebooks use, each mapped (expected: none beyond `DynamicCar`,
  `carla_like` and `grip_sections`, mapped to `dynamic-bicycle`, `friction-circle` and `section-knob-sweep`; record
  any others in the report).
- `syllabus.md` rows for Units 6–7 (**no emoji**: the PDF font has no glyph for it; the Unit 7 row names the CARLA
  lab in words).
- Design 013 **v4.4**: the routed budget (≤ 8 min), the per-section knob wording in the §6 Unit 7 row, and the
  (A_LAT, A_DEC) grid, citing this plan.

### Phase B: Unit 6 content (Opus subagents: lesson + exercise statements; solutions in a separate fresh session)
- **Lesson:**
  1. The hook: "Why does the car spin at Parabolica?" The Unit 5 agent on the dynamic car (U6.1).
  2. The dynamic bicycle: slip angles, lateral forces, the yaw equation; at low speed it agrees with Unit 3's
     kinematic bicycle (a short `DynamicCar` vs `KinematicCar` run at 5 m/s).
  3. Tyre saturation and the friction circle; a skidpad experiment on `DynamicCar` (speed ramped on a fixed steer
     until the lateral acceleration saturates near μg and the car spins).
  4. v_max = √(a_lat/|κ|), and the curvature cap built from Unit 2's `curvature_ahead`.
  5. The cap against μg (U6.2): the edge sits just under 9.81 m/s².
  6. The carla-like car (U6.3): the edge moves down, so the real grip is lower than the model's. The margin rule
     and the reference (U6.4).
  7. The bridge: the cap is safe and slow (it never goes above 20 m/s, and it brakes only when the corner is
     already close).
- **Exercises:** at least 6 `## Exercise N` and at least 2 stretch. Stretch: (a) the friction circle under combined
  braking and cornering on the skidpad (brake while turning, find where it spins); (b) the effect of κ_ahead's
  horizon (25 vs 10 waypoints) on the clean edge.
- `agents/unit-06.py` and its milestone.

### Phase C: Unit 7 content (the same dispatch rule)
- **Lesson:**
  1. The hook: "Brake *before* the corner, and find the grip that is really there." The Unit 6 agent is clean and
     slow (422.65 s on `test-circuit`).
  2. The forward–backward profile: the braking pass, the acceleration pass, the wrap-around; plot the profile
     against the Unit 6 goal.
  3. Racing the profile at 45 m/s: the lookahead must grow (U7.1).
  4. Two knobs and one friction circle: the (A_LAT, A_DEC) grid (U7.2) and the margin rule; the reference
     (U7.3) and its gain over Unit 6 (U7.4).
  5. Per-section knobs: one at a time (U7.5), the stacking trap, and the sequential pass (U7.6). The knobs are not
     μ; Unit 8 measures μ.
  6. To the real car: the lab.
- **Exercises:** at least 6 and at least 2 stretch. Stretch: (a) a backward pass that also respects the friction
  circle (brake less where the corner is tighter); (b) the order of the sequential pass (5→0 instead of 0→5) and
  whether it ends at the same knobs.
- `agents/unit-07.py`, its milestone, and `labs/real-sim.ipynb` (U7.8): the five design §7.2 steps briefly, with a
  pointer to the Unit 1 lab; the Unit 5 recorder change reused; the per-section analysis; the asserted racekit
  prediction; the decision procedure; "never commit results".

### Phase D: teacher notes for both units (active session, inline)

### Phase E: verification (named)
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN.
- `bash scripts/pre-merge-guard.sh --pr` OK.
- All the gates hold in the routed test and the milestones; the lab passes `lab-check`.
- The routed roar pytest ≤ 8 min; Units 6–7 notebooks ≤ 6 min; the report records both and the book-level exec
  total.
- The post-execution report records the interim CARLA check (design §7.3) as **PENDING (author)** and surfaces it
  as a follow-up; `roar-008`'s plan review names it as a risk.

## Out of scope
- Any `racekit` change; system identification (Unit 8); racing lines (Unit 9); many-knob tuning (Unit 12).
- Tuning `A_ACC`, `PROFILE_LEAD` or the speed PI gains (fixed at the probe's values; the lesson names them as
  knobs left for Unit 12).
- Shipping tuned `GRIP` values in the reference (they are per track).

## Plan Review
