# Plan roar-010 — Unit 11: robustness

**Design:** `docs/designs/013-roar-book.md` **v4.8** (§4.2, §4.4–4.5, §6 Unit 11, §7.1); this plan amends it to
**v4.9** (the perturbed carla-like family in §4.4; budgets, below).
**Book:** `roar`. **Autopilot** per AGENTS.md.
**Base:** branches from `main` after `roar-009` merged (#164, 6c13919).
**v1** (draft for the plan-review gate).

## Scope
- Unit 11 `roar/units/unit-11-robustness/` (not a lab unit: design §6 gives Unit 11 no 🏁): lesson, exercises,
  solutions, teacher notes, manifest.
- **racekit** gains a **perturbed carla-like family** (design §4.4 v4.9): `carla_like(noise=False, perturb=None)`;
  with `perturb=k` (an int) the car's mass and yaw inertia, steering gain, throttle and brake authority, drag and
  grip are each multiplied by a factor drawn, seeded by `k`, from the published `PERTURBATION_FAMILY` ranges;
  `perturbation_factors(k)` returns those factors. `perturb=None` is today's car exactly. The lag is **not**
  perturbed (below). Routed racekit tests cover determinism, the ranges, and `perturb=None` identity.
- Reference submission `agents/unit-11.py`; milestone `milestones/unit-11-robustness.ipynb`.
- A routed premise test for the Unit 11 gates; the registry; design 013 **v4.9**.

## Risks named for this plan (design §7.3)
- **The interim CARLA check of `agents/unit-07.py` is still PENDING (author).** Units 8–11 build on that agent.
- **The family is a model of model error, not a measurement.** Its ranges are the book's choice (grip −8 % to 0 %,
  the rest a few per cent either way), stated as such wherever they are taught; CARLA's real error is unknown, and
  the lesson says so.
- **A margin bought on one track does not transfer** (probe q8): on `test-circuit-seed2026` the same 0.54 that is
  clean on 48/48 perturbed `test-circuit` races crashes on 7 of 24 perturbed cars. The lesson presents this as a
  finding, and Checkpoint B (roar-011) inherits it.
- **Budgets.** The routed suite is at 10.0 of 12 min after `roar-009`; this plan's races (perturbed MPC races, some
  of them crash loops that run to the time cap) take it to about 12.5–13 min. This plan raises the interim routed
  budget to **14 min** (v4.9), the fifth raise, and the follow-up to the author (raise again or move gates to a
  slower tier) is re-stated.

## Probe evidence (scratchpad `u11/`, `test-circuit`, MPC budget off (`MPC_BUDGET_MS = None`) in every probe)
The probe family is `pk.py`'s `perturbed(k)`: `carla_like(noise=True)` with each factor drawn from
`random.Random(f"perturb:{k}")` (the shipped racekit function will use its own salt; the probe numbers are re-pinned
in Phase A with it).
- **Lag is the killer, and it is not in the family** (q1–q3, q6). With a 2-tick lag drawn in 30 % of cars (the first
  family), the shipped Unit 10 agent crash-**loops** on every lag-2 car: it crashes at the same corner about every
  31 s until the time cap (q1: 5/16 cars, 18–19 respawns each). On a car that differs from the nominal one **only**
  in its 2-tick lag, `MPC_LAG = 1` crash-loops at every fraction tried (0.58, 0.50, 0.40), while `MPC_LAG = 2` is
  clean (275.10 s) and pure pursuit at 0.54 is clean (280.00 s) (q3). With lag 2, small further changes (throttle
  ×0.94, steering gain ×0.95 or ×1.05) tip even `MPC_LAG = 2` into crashes (q6): lag error makes the loop marginally
  stable for both controllers. Unit 8 identifies the lag as a whole number of ticks from logs; the family therefore
  leaves the lag alone, and the lesson shows the lag-2 car once, as model error that no fraction fixes (U11.5).
- **The family (lag fixed at 1):** grip ×U(0.92, 1.00) on every section, steering gain ×U(0.95, 1.05), throttle
  ×U(0.90, 1.10), brake ×U(0.90, 1.05), mass and yaw inertia ×U(0.95, 1.10), drag ×U(0.90, 1.10). Training
  perturbations k = 0–23, held-out k = 24–47; race seed k mod 5.
- **The hook (q9):** the shipped `agents/unit-10.py` (0.58) on the 24 training perturbations: 21/24 clean; car 8
  crashes once (471.85 s), cars 16 and 20 crash-loop (4 respawns each, not finished at the cap).
- **Respawn economics (q9):** a crash restarts the race (design §4.2); the restart is from rest, exactly like the
  start, so a crash at time t costs t + 1.0 s (the hold), as measured: car 8 crashes at 195.9 s and finishes 196.8 s
  after its clean twin's time. Mean race time over the 24 training perturbations (a not-finished race counted at the
  700 s cap): 0.58 → 318.66 s; 0.56 → 294.35 s (2 crash); **0.54 → 279.95 s (24/24 clean)**; 0.52 → 282.57 s (24/24
  clean). The fraction that minimizes the expected race time is 0.54.
- **The family edge and the margin rule (q7–q9):** the highest fraction clean on all 24 training perturbations with
  race seed 0 is 0.56 (q7; with race seeds k mod 5, 0.56 crashes twice, q9); the margin rule (one step inside)
  gives **0.54**. On the 24 **held-out** perturbations (q9): 0.54 is clean 24/24 (median 279.95 s, max line error
  1.35 m); 0.56 crashes on 4/24 (q8, race seed 0); 0.58 on 4/24.
- **The fallback (q5, q9):** on a detected respawn (the collision sensor's impulse > 100 N·s, the CARLA signal), the
  probe agent re-anchors its waypoint index (one tick later, because CARLA's first post-respawn step carries the
  stale crash pose), clears the MPC's queue and plan, switches to pure pursuit and multiplies its lateral limit by
  0.86 (again at every further respawn). At 0.58, every one of the 7 crashing races (3 training, 4 held-out)
  finishes with exactly **1** collision (385.05–502.45 s) where Unit 10 crash-loops on 2 of them; on the lag-2 car,
  Unit 10 at 0.54 crash-loops (23 respawns, not finished) and the fallback agent finishes in 321.65 s with 1.
- **Early warning (q4, q5):** sideslip β (from the velocity sensor and the yaw) peaks at 4.5–5.4° in clean MPC races
  and passes 8° 0.9–2.4 s before a crash; |line error| > 1.6 m comes 0.15–0.9 s before. Falling back on a β > 6°
  warning (W6) is **worse** than falling back on the respawn alone (W0): mean 302.1 vs 293.7 s at 0.58 over the
  training family (q7): the warning trips in races that would have stayed clean, or too late to save the car.
  The shipped agent counts warnings (an instrument) and does not act on them; the lesson shows why.
- **Equivalence (q9):** with no respawn the probe agent races exactly as Unit 10 at the same constants (nominal car,
  0.54: 279.65 s both; 48/48 perturbed races at 0.54 identical).
- **Transfer (q8):** at 0.54 on `test-circuit-seed2026` (its line and measured grip) 17/24 perturbed cars are clean;
  the 7 that crash have grip ≤ 0.954.

## Deviations from design (recorded; design 013 v4.9)
- §4.4 gains the perturbed family; the lag is not perturbed (probe evidence above). Design §6's "testing across
  seeds and perturbed parameters" is taught on it.
- §6's gate "Completes N/N perturbed-parameter races at 0 collisions" is met with the book's full clean rule
  (finished, 0 collisions, line-relative error ≤ 2 m) on N = 24 held-out perturbations.
- "Spin and off-track detection" is taught and measured, but the shipped agent only **counts** warnings; it acts on
  the respawn alone (the W6 negative result).

## Concepts (3 new; all `kind: technique`, globally unique)
| id | taught where | practised |
|---|---|---|
| `respawn-economics` | lesson §1–§2: crash cost t + 1 s; expected race time over a family | Ex 1, 2, 8 |
| `perturbation-testing` | lesson §3–§4: `carla_like(perturb=k)`, `perturbation_factors`, training vs held-out perturbations, the family edge and the margin rule | Ex 3, 8, 10 |
| `failure-fallback` | lesson §5–§6: respawn detection (impulse), β and off-track warnings with lead times, re-anchor, reset, degrade | Ex 4–7, 9 |

API names: `perturbation_factors` → `perturbation-testing` (taught); `carla_like` is already taught
(`cornering-speed-limit`; the `perturb` keyword is new and taught in §3). No other new callables.

## The reference submission
`agents/unit-11.py` = `agents/unit-10.py` with:
- `MU_FRACTION = 0.54` (re-tuned by the margin rule on the perturbed training family);
- the respawn handler: impulse norm > `RESPAWN_IMPULSE` (100 N·s) → `fall_back()`: clear `mpc_queue`, `mpc_last`
  and the plan, set a re-anchor flag (the next step takes `nearest_index`), switch steering to
  `FALLBACK_STEERING = "pursuit"`, multiply the lateral limit by `FALLBACK_SCALE = 0.86` and re-plan the profile;
- the instruments: sideslip β and the warnings (`WARN_BETA_DEG = 8.0`, `WARN_ERROR_M = 1.6`) counted in
  `self.warnings`, never acted on;
- `lateral_limit()` multiplied by `self.limit_scale` (1.0 until a respawn), so with no respawn it is Unit 10 to
  the tick.
Python 3.8, numpy only, under `check_submission` (p99 ≤ 5 ms; the handler adds nothing to the MPC tick).

## Gates (pinned from the probes; Phase A re-runs each with the shipped racekit family and the shipped agent and
confirms each pin; a miss of a pinned *number* is a pin correction in the report, a miss of a clean/crash
*outcome* stops and amends the plan)
- **U11.1 family:** `perturbation_factors(k)` is deterministic and inside the published ranges for k = 0–999;
  `carla_like(perturb=None)` races identically to today's `carla_like` (to the tick); a perturbed car differs.
- **U11.2 the hook:** `agents/unit-10.py` on the training perturbations (k = 0–23, race seed k mod 5): at least one
  race not clean, at least one crash loop (≥ 3 respawns, not finished).
- **U11.3 respawn economics:** for every U11.2 race that crashes exactly once and finishes, the race time minus
  (the crash time + 1.0 s) is within 1.0 s of the median clean time of the same agent over the training family
  (q9: car 8, 471.85 − 196.9 = 274.95 s against the 275.05 s median): the restart is a fresh race.
- **U11.4 robust fraction:** on the training perturbations, 0.56 is not clean on all 24 and 0.54 is; the mean race
  time (not-finished races at the cap) is lowest at 0.54 among {0.58, 0.56, 0.54, 0.52}.
- **U11.5 the fallback:** `agents/unit-11.py` at `MU_FRACTION = 0.58` finishes every training and held-out race
  with at most 1 collision; on the nominal car with a 2-tick lag (a test-only car), `agents/unit-10.py` at 0.54 does
  not finish and `agents/unit-11.py` at 0.54 finishes with exactly 1 collision.
- **U11.6 the gate (design §6):** `agents/unit-11.py` is clean on **24/24 held-out** perturbations (k = 24–47).
- **U11.7 equivalence:** with no respawn, `agents/unit-11.py` races exactly as `agents/unit-10.py` at the same
  constants (nominal car and 3 perturbed cars, to the tick); its `warnings` count is reported, not gated.
- **U11.8 transfer (a finding, gated both ways):** at 0.54 on `test-circuit-seed2026` (its Unit 9 line and measured
  grip) on perturbations k = 0–11: at least one race not clean and at least one clean.
- `check_submission(agents/unit-11.py)` passes (outside any pool).

## Budgets
- Routed pytest ≤ **14 min** (v4.9, interim). The Unit 11 job table (MPC races): U11.2 24; U11.4 72 (0.56, 0.54
  and 0.52 on the training family; its 0.58 side is U11.2's races); U11.5 48 + 2; U11.6 24; U11.7 4 (the nominal
  car and 3 perturbed cars, both agents: the Unit 10 sides come from U11.4); U11.8 12. About 186 races; races that
  crash-loop are capped at 450 s. About 1,600 s of CPU, about 3.4 min pooled on 8 workers. Measured in Phase D;
  over 14 min means stop and amend.
- Notebooks: the Unit 11 lesson, solutions and milestone ≤ **5 min** serial in total, each cell ≤ 120 s: the
  notebooks race small families (6–8 perturbations), not the gates' 24; every claim about 24 comes from the premise
  fixture's pinned numbers, stated as such.
- Book exec total reported against v4.8's 40 CI-minutes.

## Phases
- **Phase A — racekit family + agent + premise.** (Opus subagent for racekit code and tests; agent and premise
  inline or Opus.)
  - racekit: `PERTURBATION_FAMILY`, `perturbation_factors(k)`, `carla_like(perturb=)`; routed tests (U11.1).
  - `agents/unit-11.py`; `tests/_robust_premise.py` + `tests/test_racekit_unit11_premise.py` + a conftest fixture;
    every gate U11.2–U11.8 confirmed and logged; `check_submission` on the agent.
  - Registry: 3 concepts, coverage-map entry `unit-11-robustness`, manifest, api-order (`perturbation_factors`),
    baseline `library_methods`, syllabus row 11; design 013 v4.9.
- **Phase B — content (Opus subagents).** Lesson (project-first: the hook race table, then §1 crash cost, §2
  expected time, §3 the family, §4 edge and margin on the family + the held-out check + the seed2026 transfer
  finding, §5 detection and lead times + the W6 negative result, §6 the fallback + the lag-2 car, §7 the shipped
  agent); exercises (8 core + Challenges 9 β-triggered braking, noise-aware; 10 the seed2026 margin); milestone.
  Solutions in a **separate fresh** Opus session.
- **Phase C — teacher notes** (inline).
- **Phase D — verification:** `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN; budgets measured.

## Out of scope
- Online identification (estimating grip or lag while racing); per-track re-tuning for Checkpoint B (roar-011);
  CARLA labs (Unit 11 has none); any change to Units 1–10 content.

## Plan Review
