# Plan roar-009 — Unit 10: model predictive control

**Design:** `docs/designs/013-roar-book.md` **v4.7** (§4.3–4.5, §6 Unit 10, §7.1–7.3); this plan amends it to
**v4.8** (budgets, below).
**Book:** `roar`. **Autopilot** per AGENTS.md.
**Base:** branches from `main` after `roar-008` merged (#163, 2bf203e).

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
- **Timing** (t1, t2, serial, load 8): p99 1.42 ms (loop G), **1.00 ms** (closed form) on seed2026; 1.45 ms on
  `monza-like`. Pursuit's step is 0.16 ms (p50).
- **Cost.** An MPC race on `test-circuit` is about 7.5 s of CPU (pursuit 2.5 s), on `monza-like` about 14 s.

## Deviations from design (recorded; design 013 v4.8)
- **The fallback is deterministic in the gates.** Design §7.1 says an over-budget tick falls back to pure pursuit and
  counts the fallbacks. The reference does exactly that with `MPC_BUDGET_MS = 5.0` (a wall-clock check, so a race
  can differ by a tick under load). The routed gate races set `MPC_BUDGET_MS = None` so the pins are deterministic,
  and a separate test sets `MPC_BUDGET_MS = 0.0` (every tick falls back) and asserts the race equals
  `agents/unit-09.py` at the same constants **to the tick**.
- **Budgets (v4.8):** routed pytest ≤ **12 min** (it was 10); book notebook exec ≤ **40 CI-minutes** (it was 30).
  Unit 10 adds about 60 MPC races to the routed suite (about 70 s pooled) and about 4 min of serial notebook exec.

## Concepts (3 new; all `kind: technique`, globally unique)
- `error-model-linearization`: the path-frame error model, linearised about the line; discrete time; why it is
  time-varying (a_t, κ_t along the horizon); the lag as part of the model.
- `ltv-mpc`: the horizon cost; stacking the horizon in closed form; one least-squares solve per tick; clipping the
  first command; receding horizon; the weights tuned on the dynamic car; the exact `scipy` reference on one corner.
- `tick-budget`: per-tick compute, p50/p99 with warm-up excluded, the fallback to pursuit and its count, and why
  timing is never measured in a pool.
Requires: `linear-least-squares` (Unit 8), `racing-line` and `line-retune` (Unit 9), `pure-pursuit`,
`kinematic-bicycle`, `numerical-integration` (actuator lag via Unit 5's `step-response`), `cross-track-error`.

## The reference submission
`agents/unit-10.py` = `agents/unit-09.py` with `STEERING = "mpc"`, `MPC_HORIZON = 40`, `MPC_Q_E = 0.3`,
`MPC_Q_PSI = 20.0`, `MPC_R_DU = 1000.0`, `MPC_LAG = 1`, `MPC_BUDGET_MS = 5.0`, and `MU_FRACTION = 0.58` (re-tuned
for MPC on the family). It counts its fallbacks in `self.fallbacks`; on a fallback tick it records the curvature
pursuit applied as the MPC's last command, so the next tick's Δu cost and lag queue stay true.
With `STEERING = "pursuit"` it races exactly like `agents/unit-09.py` at the same `MU_FRACTION`.
It imports only numpy, `math`, `time` and `roar_py_interface`; the `scipy` reference lives in the notebooks.

## Gates (pinned from the probes; Phase A re-runs every gate cell with the shipped agent and confirms each pin within
±1 tick; a miss means stop, amend and re-gate)
- **U10.1 the solve (race-free):** the closed-form G and h equal a one-tick-at-a-time build to 1e-12 on a random
  state; on c1's corner the LTV least-squares cost (nonlinear evaluation) is within **2%** of `scipy` SLSQP's
  (probe 0.94%) and the controls within 10⁻³ 1/m.
- **U10.2 same fraction:** at f 0.54 on `test-circuit` MPC is clean on seeds 0–4 with max line error ≤ 1.3 m
  (probe 1.04 m) and **not** noise-aware faster than pursuit (both about 279.6 s): the honest same-f result.
- **U10.3 the hook:** at f 0.58 on `test-circuit-seed4` pursuit (`agents/unit-09.py`) is not clean on any of seeds
  0–4, and MPC is clean on all five (271.10 s ± 2 ticks median).
- **U10.4 the edge:** MPC at 0.60 is clean on all 25 family races; at 0.62 at least one family race is not clean
  (probe: seed1 2/5).
- **U10.5 the transfer:** `agents/unit-10.py` on `test-circuit-seed2026` is clean on seeds 0–4 at 276.85 s ± 2 ticks
  median, noise-aware faster than Unit 9's 282.05 s.
- **U10.6 the lag:** with `MPC_LAG = 0` at f 0.60 on `test-circuit` MPC is not clean on any of seeds 0–4 (r7: 0/5).
- **U10.7 fallback and budget:** `MPC_BUDGET_MS = 0.0` equals `agents/unit-09.py` (same `MU_FRACTION`, seed 0) to
  the tick, with `fallbacks` equal to the step count; `check_submission(agents/unit-10.py)` passes (p99 ≤ 5 ms,
  outside any pool).
- **U10.8 `monza-like`:** MPC at 0.64 is clean on seeds 0–4 (468.75 s ± 2 ticks), where pursuit at 0.64 is not
  clean on at least one (seeds 0–1 both not clean in the probe).

## Budgets
- Routed pytest ≤ **12 min** (v4.8). The Unit 10 job table: U10.2 5; U10.3 5 MPC + 5 pursuit; U10.4 25 + 25;
  U10.5 5; U10.6 5; U10.7 1; U10.8 5 MPC (`monza-like`) + 5 pursuit; about 80 races, 66 of them MPC (about 7.5 s of
  CPU each, 14 s on `monza-like`), about 75 s pooled on 8 workers. Measured in Phase E; over 12 min means stop and
  amend. If U10.4's 0.62 cell is cut to seed1 only (5 races), it is 20 races fewer.
- Notebooks: the Unit 10 lesson, solutions and milestone **≤ 5 min** serial in total (an MPC race is about 7.5 s
  serial: each notebook races at most about 10 MPC races). The book-level exec total is reported against v4.8's 40
  CI-minutes.
- The per-cell 120 s cap holds.

## The CARLA lab (Unit 10, design §7.2)
`labs/real-sim.ipynb`, "runs on your machine with CARLA 0.9.12 and `ROAR_PY`". Starting point: the student's
accepted Unit 8 lab setting (or their Unit 7 submission when the Unit 8 lab accepted none), with their Unit 9 line if
they built one.
1. **Timing first, off CARLA:** `check_submission` on the MPC file on the same machine, idle (p99 ≤ 5 ms); if it
   fails, lower `MPC_HORIZON` to 20 and re-check; if that fails, the lab keeps pursuit and stops.
2. **R1–R2:** the MPC file at the student's accepted fraction, twice. Both clean (finished, 0 collisions,
   line-relative error ≤ 2 m) → MPC is **accepted at that fraction**; otherwise MPC is **not accepted** and the
   student keeps pursuit (no further races).
3. **R3–R4 (only after acceptance):** the fraction + 0.02, twice; both clean → accepted at the higher fraction,
   otherwise the accepted value stays the one already raced. The procedure never ends on a value it did not race.
4. Analysis cells: the clean rule, the median time against the accepted pursuit record, the fallback count printed
   by the agent (`fallbacks` / steps).
Run budget: 4 races (short form: R1–R2, 2). No results committed; `.gitignore` already covers the lab outputs.
`lab-check` executes the analysis against the generated sample CSV.

## Phases

### Phase A: agent, routed test and registry (Opus subagent for the code; registry inline)
- `agents/unit-10.py` from `agents/unit-09.py` and `u10/mpc2.py` as above, with the fallback; the equivalences
  (pursuit mode = Unit 9; budget 0 = Unit 9) asserted to the tick.
- `tests/_mpc_premise.py` (the job table, as `_line_premise.py`, lines from `_line_solver.solve_track`) and
  `tests/test_racekit_unit10_premise.py` (U10.1–U10.8); U10.1 is race-free and imports `scipy`.
- **Re-run every gate cell** with the shipped agent and confirm the pins (±1 tick).
- `concepts.yaml` (3 ids), `coverage-map.yaml` (Unit 10, `lessons: 3`), the manifest (`lab: true`), `labs.yaml`.
- `api-order.yaml` / `baseline.yaml`: `np.tril`, `np.cumsum` if not already present, and `scipy.optimize.minimize`
  → `ltv-mpc`; `time.perf_counter` → `tick-budget`. Record any others in the report.
- `syllabus.md` row 10 (no emoji).
- Design 013 **v4.8** (the budget raises and the deterministic-fallback deviation; status line; changelog).

### Phase B: Unit 10 content (Opus subagents: lesson + exercise statements; solutions in a separate fresh session)
- **Lesson:**
  1. The hook: "Plan the next 2 s, every tick." Unit 9's agent at 0.58, one step above its frozen fraction, crashes
     on a training track (U10.3); pure pursuit looks at one point. What if the steering planned the whole next 2 s?
  2. The model: the path-frame errors, linearised; discrete time; time-varying a_t and κ_t; the queued (lagged)
     command.
  3. The horizon cost and the stacked least-squares solve: G and h built one tick at a time, then in closed form
     (U10.1); clip and apply the first command; recede.
  4. The exact reference on one corner: `scipy.optimize.minimize` on the nonlinear model, 0.94% better at 600× the
     time (U10.1). This is why the submission solves the linear problem.
  5. Weights tuned on the **dynamic** car: the first weights weave and spin (p1), on the kinematic car they are fine.
     The lag ablation (U10.6).
  6. The honest comparison: at the same f, no faster (U10.2); the tracking margin; the re-tune on the family by the
     margin rule (U10.4) and the transfer (U10.5); `monza-like` (U10.8).
  7. The tick budget: p50/p99, warm-up, the fallback, and why timing in a pool lies (U10.7).
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
