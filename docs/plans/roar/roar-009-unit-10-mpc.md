# Plan roar-009 — Unit 10: model predictive control

**Design:** `docs/designs/013-roar-book.md` **v4.7** (§4.3–4.5, §6 Unit 10, §7.1–7.3); this plan amends it to
**v4.8** (budgets, below).
**Book:** `roar`. **Autopilot** per AGENTS.md.
**Base:** branches from `main` after `roar-008` merged (#163, 2bf203e).
**v2.2** folds the round-3 nits ([sol] N1; [fable] S1–S3, N4–N7); CONSENSUS.
**v2.1** folds plan-review round 2 ([sol] REJECT: B1 the non-finite fallback, B2 the lab with no accepted
configuration, B3 the stale Phase A equivalence, S4 counts and tolerance; [fable] APPROVE WITH NITS: S1–S6, N7–N10).
**v2** folds plan-review round 1 ([sol] REJECT: B1 the shipped fallback never raced, B2 the lab's fallback to an
un-raced pursuit configuration, S3 the race count; [fable] APPROVE WITH NITS: S1–S7, N8–N13; [self] N1–N2).
The over-budget policy changes: an over-budget tick now **shortens the horizon** (40 → 20 → 10) instead of handing
the next tick to pure pursuit, because pursuit at MPC's fraction is exactly what crashes (U10.3), while MPC at
N = 10 is clean in 30/30 races at the frozen fraction (r8).

## Scope
- Unit 10 `roar/units/unit-10-mpc/` (a **lab unit**, 🏁: `labs/real-sim.ipynb`, design §7.2): lesson, exercises,
  solutions, teacher notes, manifest (`lab: true`).
- Reference submission `agents/unit-10.py`; milestone `milestones/unit-10-mpc.ipynb`.
- Nothing in `racekit` changes: the model, the MPC and its solver are **student code** in the submission (numpy
  only). `scipy.optimize.minimize` appears only in notebooks, as the exact reference on one corner.
- A routed premise test for the Unit 10 gates; the registry; design 013 **v4.8**.

## Risks named for this plan (design §7.3)
- **The interim CARLA check of `agents/unit-07.py` is still PENDING (author).** Units 8–10 build on that agent;
  if the check fails, an errata/fix plan follows before Part 2 ships.
- **The MPC model is kinematic; the car is not.** On `carla_like(noise=True)` a badly weighted MPC weaves on the
  straights and spins (p1: the first weights were not clean on any of 3 seeds, 11 collisions), while it is clean on
  the kinematic car (278.25 s). The weights are therefore tuned on the dynamic car, on the training track only, and
  the lesson shows the failure.
- **The step budget is wall-clock.** `check_submission` measures p99 ≤ 5 ms; the reference measures p99 1.0 ms
  serially at load 8 (t2) but 2–13 ms when 8 pooled races share the machine (r2). The routed `check_submission` test
  runs outside any pool; probes never measure timing in a pool.
- **Budgets.** After `roar-008` the routed suite is at 8.6–9.5 of 10 min and the book's notebook exec at about 26.8
  of 30 CI-minutes; an MPC race costs about 3× a pursuit race. This plan raises both (v4.8, below), the fourth
  routed-budget raise; the follow-ups ask the author whether to keep raising or to move long gates to a slower tier.

## Probe evidence (scratchpad `u10/`, `carla_like(noise=True)`, race seeds 0–4 unless said)
The probe agent is `agents/unit-09.py` with `STEERING = "mpc"` (`make_mpc.py`, `mpc2.py`): every line, grip and
speed-profile setting is Unit 9's; only the steering law changes.
- **The model.** Path-frame errors on the agent's own line points: cross-track error e (left positive) and heading
  error ψ = yaw − segment heading. Linearised about the line (sin ψ ≈ ψ) with curvature u as the input:
  e_{t+1} = e_t + a_t ψ_t, ψ_{t+1} = ψ_t + a_t (u_t − κ_t), a_t = Δt·v_t, with v_t the profile speed at the
  distance the car will have travelled (capped by the speed reachable at 6 m/s²) and κ_t the line's curvature there.
  It is **linear time-varying**: a_t and κ_t change along the horizon.
- **The solve.** Stack the horizon (N = 40 ticks, 2 s): x = G u + h, with G and h in **closed form**
  (G_ψ[t, j] = a_j for j ≤ t; G_e[t, j] = a_j (S_t − S_j), S the running sum of a). Cost
  Σ q_e e² + q_ψ ψ² + r Σ (u_t − u_{t−1})², written as one stacked least-squares problem and solved with
  `np.linalg.lstsq`; the first u is clipped to ± tan(MAX_STEER)/L and applied as δ = atan(L u).
  The closed form races identically to the loop that builds G one tick at a time (t2: 276.85 s, max error 1.2560 m,
  both) and is faster (p50 1.31 → 0.90 ms).
- **The lag.** The car applies each command one tick late (Unit 5; Unit 8 measured lag 1 by the residual). The MPC
  first rolls its own model through the queued command, then plans from there (`MPC_LAG = 1`).
  Without that (`MPC_LAG = 0`) it is **not clean in 0/15** family races at f 0.60 (r6, max error 4.05 m); with it,
  15/15.
- **The weights** (r2, `test-circuit`, seed 0, f 0.54): 27 settings of (q_e, q_ψ, r) ∈ {0.02, 0.1, 0.3} ×
  {1, 4, 20} × {10³, 10⁴, 10⁵}; 12 clean. Two candidates went to the family: A = (0.3, 20, 10³) (279.65 s, max error
  1.04 m) and B = (0.1, 4, 10⁴) (279.95 s, 1.50 m). At the **same** f, MPC is no faster than pursuit (pursuit
  279.60 s): the speed profile, not the steering, sets the lap time. MPC's gain is the **tracking margin**.
- **The family (r3, r4; seeds 0–1, then 0–4):**

  | f | pursuit (Unit 9) family | MPC A family | MPC B family |
  |---|---|---|---|
  | 0.54 | 10/10 clean, max err 1.74 | 10/10, 1.20 | 10/10, 1.76 |
  | 0.56 | 10/10, 1.88 | 10/10, 1.22 | 10/10, 1.82 |
  | 0.58 | **8/10**, 6.11 | 10/10, 1.34 | 7/10 |
  | 0.60 | 8/10 | **25/25** (seeds 0–4), 1.50 | 5/10 |
  | 0.62 | — | 19/25 (seed1 2/5, seed2 4/5, seed4 3/5) | — |

  MPC A's family edge is **0.60**; by the margin rule (one step below the edge, as Units 7–9) it is frozen at
  **0.58**. Pursuit's edge is 0.56 (Unit 9 froze 0.54). B is discarded on the family.
  Same-f times (MPC A, 0.60, seeds 0–4): `test-circuit` 272.40, seed1 269.40, seed2 268.80, seed3 268.75, seed4
  268.85 s.
- **The transfer** (`test-circuit-seed2026`, never tuned on): MPC A at 0.58 is clean in **276.85 s** (seeds 0, 1);
  Unit 9's frozen 0.54 races 282.05 s. At 0.60 MPC A is not clean on seed 0 (the edge matches the family's).
- **Confirmations** (r7, seeds 0–4): pursuit at 0.58 on `test-circuit-seed4` is **not clean on any** seed (max error
  3.92–8.96 m), MPC A clean on all five (271.10 s median, ≤ 1.34 m); MPC A with `MPC_LAG = 0` at 0.60 on
  `test-circuit` not clean on any (3.33–4.05 m); MPC A at 0.58 on seed2026 clean on all five (276.75–276.85 s,
  median 276.85 s).
- **`monza-like`** (r5, seeds 0–1): MPC A is clean at 0.58–0.64 (476.00, 473.45, 471.05, **468.75 s**, max error
  ≤ 1.23 m); pursuit is clean to 0.62 and not clean at 0.64 (max error 2.06 m).
- **The horizon** (r6, family f 0.60, seeds 0–2): N = 10 15/15 (273.05 s on `test-circuit`, p50 0.44 ms), N = 20
  15/15 (272.45 s, 0.64 ms), N = 40 15/15 (272.40 s, 1.24 ms), N = 60 15/15 (272.40 s, 1.93 ms): the time saturates
  near 1–2 s.
- **The exact reference** (c1, the tightest corner of `test-circuit`'s line, |κ| 0.0658, v 18 m/s, e₀ 0.8 m,
  ψ₀ 0.05): `scipy.optimize.minimize` (SLSQP, the nonlinear path-frame model sin ψ and κ cos ψ/(1 − κe), bounds on
  u) reaches cost 3.49971 in 480 ms; the LTV least-squares u, evaluated on the nonlinear model, costs 3.53258
  (**0.94% above**) in 0.80 ms; max |u_LS − u_scipy| 3.5·10⁻⁴ 1/m.
- **The degraded horizon at the frozen fraction** (r8, f 0.58, seeds 0–4): N = 10 is clean on all 30 races of the
  family and seed2026 (max error ≤ 1.59 m; `test-circuit` 275.35 s, seed2026 277.30 s, seed4 271.55 s medians);
  N = 20 also 30/30 (≤ 1.35 m; seed2026 276.85 s).
- **Logs.** r3–r5 and r8 are saved as logs; r6, r7, t1, t2 and c1 were read from the terminal (c1 reproduces, [fable]).
  Phase A saves every gate re-run's output in the scratchpad.
- **Timing** (t1, t2, serial, load 8): p99 1.42 ms (loop G), **1.00 ms** (closed form) on seed2026; 1.45 ms on
  `monza-like`. Pursuit's step is 0.16 ms (p50).
- **Cost.** An MPC race on `test-circuit` is about 7.5 s of CPU (pursuit 2.5 s), on `monza-like` about 14 s.

## Deviations from design (recorded; design 013 v4.8)
- **The over-budget policy (design §7.1 says: fall back to pure pursuit for that tick).** A self-timed check can only
  measure a solve after it has run, so it cannot recover the time of the tick that overran; it can only make the
  next ticks cheaper. Pursuit ticks would also break the Δu cost's and the lag queue's continuity, and pursuit
  *throughout* at MPC's frozen fraction is what crashes (U10.3; a single pursuit tick would not). What is timed: the
  `mpc()` call (the model, the stack and the solve), from `time.perf_counter()` before it to after it. So the reference applies the
  command it has already computed, counts the tick in `self.over_budget`, and **halves the horizon** for the rest of
  the race (40 → 20 → 10, never below 10), printing one line each time it does. In MPC mode pure pursuit is **never**
  used: a solve whose result is not finite (possible only from non-finite inputs, such as a bad sensor reading;
  `lstsq` on finite inputs returns finite values) applies the **next command of the last finite plan** (the plan
  shifted by one tick; the last applied command once the plan is used up), counted in `self.fallbacks`.
  Design v4.8 restates §7.1 this way.
- **Deterministic races.** `MPC_BUDGET_MS = 5.0` ships; because it reads a wall clock, a loaded machine can shorten
  the horizon at a different tick. The routed gates **and the notebooks' pinned race cells** race the variant
  `MPC_BUDGET_MS = None` (no timing; the lesson says why). The two extremes of the shipped policy are both gated:
  `None` (always N = 40) and `MPC_BUDGET_MS = 0.0` (every tick over budget, so N = 40, 20, then 10 for the rest of
  the race, deterministically), U10.7; the non-finite path is tested race-free (U10.7).
- **Budgets (v4.8):** routed pytest ≤ **12 min** (it was 10); book notebook exec ≤ **40 CI-minutes** (it was 30).
  Unit 10 adds 76 races, 65 of them MPC (about 72 s pooled, below), and about 4–5 min of serial notebook exec, which
  takes the book to about 31 of 30. 40, not 35, because Units 11–13, Checkpoint B and the capstone remain and each
  has added 3–6 min. v4.8's levels are **interim** (the changelog says so): by these numbers both will need raising
  again by `roar-011`/`roar-012`. The follow-ups ask the author whether to keep raising or to move the long gates to a slower tier
  (the question is held to the end of the run by the author's autopilot directive).

## Concepts (3 new; all `kind: technique`, globally unique)
- `error-model-linearization`: the path-frame error model, linearised about the line; discrete time; why it is
  time-varying (a_t, κ_t along the horizon); the lag as part of the model.
- `ltv-mpc`: the horizon cost; stacking the horizon in closed form; one least-squares solve per tick; clipping the
  first command; receding horizon; the weights tuned on the dynamic car; the exact `scipy` reference on one corner.
- `tick-budget`: per-tick compute, p50/p99 with warm-up excluded, why timing is never measured in a pool, and the
  shipped policy: an over-budget solve shortens the horizon (`over_budget`); a non-finite solve applies the shifted
  last finite plan (`fallbacks`).
Requires: `linear-least-squares` (Unit 8), `racing-line` and `line-retune` (Unit 9), `pure-pursuit`,
`kinematic-bicycle`, `numerical-integration` (actuator lag via Unit 5's `step-response`), `cross-track-error`.

## The reference submission
`agents/unit-10.py` = `agents/unit-09.py` with `STEERING = "mpc"`, `MPC_HORIZON = 40`, `MPC_Q_E = 0.3`,
`MPC_Q_PSI = 20.0`, `MPC_R_DU = 1000.0`, `MPC_LAG = 1`, `MPC_BUDGET_MS = 5.0`, `MPC_MIN_HORIZON = 10`, and
`MU_FRACTION = 0.58` (re-tuned for MPC on the family). It keeps `self.horizon`, `self.over_budget` and
`self.fallbacks` and the last finite plan (the over-budget policy above); whatever command it applies goes into the
lag queue and becomes the last command, so the next tick's Δu cost and lag stay true.
Hygiene, each commented: the reference speed is capped by `A_THROTTLE` (not a literal); the distance along the line
starts at the car's segment, ignoring its position within it (under 2 m); the braking side of the profile is taken
as given (the model assumes the speed loop follows it); `v_ref[t]`, `k_ref[t]` are the line's values after t + 1 ticks
but drive the transition t → t + 1 (a half-step forward reference, inherited by the loop build and the `scipy`
reference alike).
With `STEERING = "pursuit"` it races exactly like `agents/unit-09.py` at the same `MU_FRACTION`.
It imports only numpy, `math`, `time` and `roar_py_interface`; the `scipy` reference lives in the notebooks.

## Gates (pinned from the probes; Phase A re-runs every gate cell with the shipped agent and confirms each pin within
±2 ticks of the median; a miss means stop, amend and re-gate)
- **U10.1 the solve (race-free):** the closed-form G and h equal a one-tick-at-a-time build (`np.allclose`,
  rtol 1e-12, atol 1e-12) on a random state; on c1's corner the LTV least-squares cost (nonlinear evaluation) is within **2%** of `scipy` SLSQP's
  (probe 0.94%) and the controls within 10⁻³ 1/m.
- **U10.2 same fraction:** at f 0.54 on `test-circuit` MPC is clean on seeds 0–4 with max line error ≤ 1.3 m
  (probe 1.04 m, seed 0 only; seeds 0–1 for the family) and **neither** is noise-aware better than the other:
  `racekit.measure.noise_aware_better(mpc_times, pursuit_times)` and `noise_aware_better(pursuit_times, mpc_times)`
  are both False on the five seeds (Unit 1's rule; MPC 279.65 s, pursuit 279.60 s on seed 0): the honest same-f
  result.
- **U10.3 the hook:** at f 0.58 on `test-circuit-seed4` pursuit (`agents/unit-09.py`) is not clean on any of seeds
  0–4, and MPC is clean on all five (271.10 s ± 2 ticks median).
- **U10.4 the edge:** MPC at 0.60 is clean on all 25 family races; at 0.62 on `test-circuit-seed1` at least one of
  seeds 0–4 is not clean (probe 2/5 clean).
- **U10.5 the transfer:** `agents/unit-10.py` on `test-circuit-seed2026` is clean on seeds 0–4 at 276.85 s ± 2 ticks
  median, noise-aware faster than `agents/unit-09.py` raced on the same five seeds (282.05 s in `roar-008`).
- **U10.6 the lag:** with `MPC_LAG = 0` at f 0.60 on `test-circuit` MPC is not clean on any of seeds 0–4 (r7: 0/5).
- **U10.7 the over-budget policy and the budget:** with `MPC_BUDGET_MS = 0.0` (every tick over, so N = 10 after
  two ticks) `agents/unit-10.py` is clean on seeds 0–4 of `test-circuit-seed4` and `test-circuit-seed2026` (r8, at
  N = 10: 10/10; soft expectations under the Pins rule: medians near 271.55 s and 277.30 s), with `over_budget` equal to the number of `mpc()` calls (one per telemetry row, warm-up included) and `fallbacks`
  0; with `STEERING = "pursuit"` it
  equals U10.3's `agents/unit-09.py` race (`test-circuit-seed4`, 0.58, seed 0) to the tick;
  a race-free test gives `mpc()` a non-finite curvature and asserts that it applies the shifted last finite plan and
  counts one fallback, with no call to pursuit;
  `check_submission(agents/unit-10.py)` passes (p99 ≤ 5 ms; the routed suite runs tests serially, so it is outside
  any pool).
- **U10.8 `monza-like`:** MPC at 0.64 is clean on seeds 0–4 (468.75 s ± 2 ticks median; probed on seeds 0–1),
  where pursuit at 0.64 is not clean on at least one. Pursuit's failure there is at the threshold (max error
  2.03–2.06 m against the 2.0 m rule, no collision): the lesson and notes present it as a tracking-margin result, not
  as pursuit crashing.
- **Pins.** Where a gate rests on a 2-seed probe (U10.2, U10.8), a Phase-A miss of the pinned number is a pin
  correction recorded in the report, not a regression; the clean/not-clean outcomes are the gates. Times are
  pinned as the median ± 2 ticks throughout (Phase A confirms each).

## Budgets
- Routed pytest ≤ **12 min** (v4.8). The Unit 10 job table (MPC + pursuit): U10.2 5 + 5; U10.3 5 + 5; U10.4
  30 MPC (25 at 0.60, 5 at 0.62 on seed1); U10.5 5 + 5; U10.6 5; U10.7 10 + 1; U10.8 5 + 5 (`monza-like`); the pursuit sides of U10.2 and
  U10.5 are read from roar-008's `line_premise` fixture (`U9_REFERENCE`, `line_key(CHECKPOINT, 0.54)`), not re-raced:
  **76 races, 65 of them MPC** (about 7.5 s of CPU each, 14 s on `monza-like`; pursuit 2.5 s, 6 s), about 565 s of CPU, about 72 s pooled on
  8 workers, taking the suite from 9.5 to about 11 min. Measured in Phase D; over 12 min means stop and amend.
- Notebooks: the Unit 10 lesson, solutions and milestone **≤ 5 min** serial in total (an MPC race is about 7.5 s
  serial: each notebook races at most about 10 MPC races, with `MPC_BUDGET_MS = None` in pinned cells). The book-level exec total is reported against v4.8's 40
  CI-minutes.
- The per-cell 120 s cap holds.

## The CARLA lab (Unit 10, design §7.2)
`labs/real-sim.ipynb`, "runs on your machine with CARLA 0.9.12 and `ROAR_PY`".
**Starting point: the accepted configuration**, the exact submission the student's Unit 8 lab accepted. It has been
raced clean on CARLA; nothing un-raced is ever the fallback.
**When Unit 8 accepted none** (the student holds only a PROVISIONAL Unit 7 result): R00a–R00b race that Unit 7
submission as-is, twice. Both clean → it becomes the accepted configuration and the lab continues; otherwise the lab
records "no accepted configuration" and stops: MPC is never compared against a configuration that has not raced
clean. A student with no clean CARLA race at all (the Unit 7 lab not run or not clean) also records "no accepted
configuration" and stops.
0. **R0a–R0b (optional, only to add a Unit 9 line):** the accepted configuration with the student's line, pursuit,
   twice. Both clean → it becomes the accepted configuration; otherwise the line is dropped and the accepted
   configuration is unchanged.
1. **Timing first, off CARLA:** `check_submission` on the MPC file on the same machine, idle (p99 ≤ 5 ms); if it
   fails, lower `MPC_HORIZON` to 20 and re-check; if that fails, the lab keeps the accepted configuration and stops.
2. **R1–R2:** the MPC file, twice: `agents/unit-10.py`-style (the student's Unit 10 file) with the accepted
   configuration's constants copied in (`LINE_CONTROL` or `None`, `MU_G` or `None` with `A_LAT`, `MU_FRACTION`,
   `MAX_STEER`, …); step 1's `check_submission` runs on exactly that file. The weights were tuned on the line at 0.58
   and are un-probed on a centreline or `A_LAT` configuration; R1–R2 gate it either way, and the lab says so. Both clean (finished, 0
   collisions, line-relative error ≤ 2 m) → MPC is **accepted at that fraction**; otherwise the student keeps the
   accepted configuration (no further races).
3. **R3–R4 (only after MPC is accepted, and only when the accepted configuration plans with `MU_FRACTION`; a Unit 7
   configuration on the `A_LAT` path skips them):** the fraction + 0.02, twice; both clean → accepted at the higher fraction,
   otherwise the accepted value stays the one already raced. The procedure never ends on a value it did not race.
4. Analysis cells: the clean rule and the median time against the accepted configuration's record, from
   `TELEMETRY_PATH` only. The agent prints one line each time it shortens its horizon (the runner's console shows
   it); the lab asks the student to note those lines by hand, and the analysis does not read them.
Run budget: at most 8 races (R00a–R00b, R0a–R0b, R1–R4); short form R1–R2, 2. No results committed; `.gitignore` already covers the lab
outputs. `lab-check` executes the analysis against the generated sample CSV.

## Phases

### Phase A: agent, routed test and registry (Opus subagent for the code; registry inline)
- `agents/unit-10.py` from `agents/unit-09.py` and `u10/mpc2.py` as above, with the fallback; the equivalences
  (`STEERING = "pursuit"` = Unit 9 to the tick; budget 0 → N = 40, 20, then 10, asserted on `self.horizon`; a
  race-free test feeds a non-finite input and asserts the shifted last finite plan is applied and counted).
- `tests/_mpc_premise.py` (the job table, as `_line_premise.py`, lines from `_line_solver.solve_track`) and
  `tests/test_racekit_unit10_premise.py` (U10.1–U10.8); U10.1 is race-free and imports `scipy`.
- **One serial, timed race** of the shipped agent (`MPC_BUDGET_MS = 5.0`) on `test-circuit-seed2026`, seed 0, on an
  idle machine: record `over_budget`, the final horizon and the per-tick max, so any lesson statement about how often
  the policy fires rests on evidence.
- **Re-run every gate cell** with the shipped agent and confirm the pins (median ± 2 ticks, the one tolerance throughout).
- `concepts.yaml` (3 ids), `coverage-map.yaml` (Unit 10, `lessons: 3`), the manifest (`lab: true`), `labs.yaml`.
- `api-order.yaml` / `baseline.yaml`, decided up front: `tril`, `cumsum`, `tile`, `eye` (with `k`) and `minimize` →
  `ltv-mpc`; `perf_counter` → `tick-budget`; `empty`, `atan`, `allclose` and `isfinite` as infrastructure if not already present. Record any
  others in the report.
- `syllabus.md` row 10 (no emoji).
- Design 013 **v4.8** (the budget raises and the deterministic-fallback deviation; status line; changelog).

### Phase B: Unit 10 content (Opus subagents: lesson + exercise statements; solutions in a separate fresh session)
- **Lesson:**
  1. The hook: "Plan the next 2 s, every tick." Unit 9's agent at 0.58, one step above its edge (0.56) and two above its
     frozen 0.54, crashes on a training track (U10.3); pure pursuit looks at one point. What if the steering planned the whole next 2 s?
  2. The model: the path-frame errors, linearised; discrete time; time-varying a_t and κ_t; the queued (lagged)
     command.
  3. The horizon cost and the stacked least-squares solve: G and h built one tick at a time, then in closed form
     (U10.1); clip and apply the first command; recede.
  4. The exact reference on one corner: `scipy.optimize.minimize` on the nonlinear model, 0.94% better at 600× the
     time (U10.1). This is why the submission solves the linear problem.
  5. The speed reference is a heuristic (the profile speed, capped by what the throttle can reach); say so.
     Weights tuned on the **dynamic** car: the first weights weave and spin (p1), on the kinematic car they are fine.
     The lag ablation (U10.6).
  6. The honest comparison: at the same f, no faster (U10.2); the tracking margin; the re-tune on the family by the
     margin rule (U10.4) and the transfer (U10.5); `monza-like` (U10.8).
  7. The tick budget: p50/p99, warm-up, why timing in a pool lies, and what a self-timed check can and cannot do
     (it cannot recover the tick that overran; it can shorten the horizon for the next ones) (U10.7).
  8. To the real car: the lab.
- **Hidden truth:** student material never imports, reads or quotes `racekit._truth`; the lag is "measured lag 1
  tick (Unit 8)", the steering gain "measured, 66°".
- **Exercises:** at least 6 and at least 2 stretch. Stretch: (a) add a terminal cost (a larger weight on the last
  state) and test it on the family; (b) add a speed-dependent q_ψ or horizon and say whether it is noise-aware
  better.
- `agents/unit-10.py`, its milestone, and `labs/real-sim.ipynb`.

### Phase C: teacher notes (active session, inline)

### Phase D: verification (named)
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN; `bash scripts/pre-merge-guard.sh --pr` OK.
- Every gate holds in the routed test and the milestone; the lab passes `lab-check`; `check_submission` passes the
  new agent on an idle machine.
- The routed suite ≤ 12 min and the Unit 10 notebooks ≤ 5 min, measured; the report records both and the book-level
  exec total.
- The report repeats the PENDING interim CARLA check as a risk, and lists the follow-ups.

## Out of scope
- A nonlinear MPC in the submission (the `scipy` solve stays a notebook reference); a speed (longitudinal) MPC — the
  speed profile and its PI loop are Unit 7's and unchanged.
- Robustness, perturbed parameters and respawn handling (Unit 11); Checkpoint B (`roar-011`).
- Any change to `racekit`.

## Plan Review

### Round 1 (v1, 1a0a6da)
- [sol] REJECT.
  - B1 the routed pins disable the fallback the agent ships with, so no gate races the shipped policy
    [FIXED v2: the policy is now "shorten the horizon"; both extremes are gated (U10.7 budget 0 on seed4 and seed2026,
    r8 evidence 30/30 at N = 10)].
  - B2 the lab could fall back to a pursuit configuration with a new line that never raced [FIXED v2: the starting
    point is the Unit 8 lab's accepted configuration; a line enters only through R0a–R0b].
  - S3 the job table summed to 86 races, 76 MPC, not 80/66 [FIXED v2: recounted after the changes, 91/70, about
    85 s pooled].
- [fable] APPROVE WITH NITS (re-derived G and h, reproduced c1).
  - S1 "Phase E" [FIXED: Phase D].
  - S2 the fallback semantics [FIXED v2: post-solve check, horizon halving; lesson §7 says what a self-timed check
    cannot do].
  - S3 notebooks would race the timed variant [FIXED: pinned cells race `MPC_BUDGET_MS = None`].
  - S4 cut U10.4's 0.62 cell to seed1 [FIXED]; ask the author about the 4th raise now [WONTFIX: the author's
    autopilot directive holds questions to the end of the run; recorded in the follow-ups]; justify 40 [FIXED].
  - S5 U10.8's pursuit failure is at the threshold [FIXED: gate text and lesson framing].
  - S6 2-seed probes and ±1 vs ±2 ticks [FIXED: the Pins rule; ±2 ticks throughout].
  - S7 U10.5 needs Unit 9's five times [FIXED: 5 pursuit races in the job table].
  - N8 neither noise-aware better [FIXED]. N9 allclose with rtol [FIXED]. N10 hygiene comments [FIXED: the reference
    submission]. N11 api-order up front [FIXED]. N12 logs [FIXED: recorded; Phase A saves its outputs].
    N13 the lab's fallback count [FIXED: printed lines, noted by hand, not analysed].
- [self] APPROVE WITH NITS. N1 the literal 6 m/s² cap [FIXED: `A_THROTTLE`]. N2 the speed reference is a heuristic
  [FIXED: lesson §5].

### Round 2 (v2, a46af45)
- [sol] REJECT.
  - B1 a non-finite solve still went to pursuit at 0.58, untested [FIXED v2.1: pursuit is never used in MPC mode; the
    shifted last finite plan is applied and counted; a race-free U10.7 test].
  - B2 the lab called a PROVISIONAL Unit 7 result "accepted" [FIXED v2.1: R00a–R00b race it twice first, otherwise
    the lab stops with "no accepted configuration"].
  - B3 Phase A still asserted "budget 0 = Unit 9" [FIXED v2.1: horizon checks and the pursuit-mode equivalence].
  - S4 counts (86/65) and ±1 vs ±2 ticks [FIXED v2.1: recounted, now 76/65 after [fable] N7; one tolerance].
- [fable] APPROVE WITH NITS.
  - S1 the count [FIXED]. S2 the Phase A leftovers [FIXED, = [sol] B3/S4]. S3 `tick-budget`'s text [FIXED].
  - S4 how often the policy fires on an idle machine, and what is timed [FIXED: a serial timed race in Phase A; the
    `mpc()` call is timed].
  - S5 R3–R4 meaningless for an `A_LAT` configuration [FIXED: skipped].
  - S6 v4.8 levels will be exceeded again [FIXED: labelled interim in the changelog; the question stays a follow-up].
  - N7 reuse roar-008's pursuit races [FIXED]. N8 `allclose`, `isfinite` [FIXED]. N9 soft medians for U10.7 [FIXED].
    N10 the over-claimed rationale [FIXED: softened].
- [self] APPROVE.

### Round 3 (v2.1, ca4043d) — CONSENSUS
- [sol] APPROVE WITH NITS: rounds 1–2 resolved. N1 U10.2's "neither better" needs a rule [FIXED v2.2:
  `noise_aware_better` False both ways on the five seeds].
- [fable] APPROVE WITH NITS (re-derived G, h and the Δu row against an independent build; checked r7/r8 and the
  fixture keys). S1 the lab's MPC file [FIXED: the Unit 10 file with the accepted constants; weights un-probed off the
  line]. S2 no clean CARLA race at all [FIXED: stop]. S3 the hook's "one step" [FIXED]. N4 the pursuit-mode race
  [FIXED: U10.3's seed-0 race]. N5 the job-table notation [FIXED]. N6 the half-step reference [FIXED: commented].
  N7 the step count [FIXED].
- [self] APPROVE.
