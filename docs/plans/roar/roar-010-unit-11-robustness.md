# Plan roar-010 — Unit 11: robustness

**Design:** `docs/designs/013-roar-book.md` **v4.8** (§4.2, §4.4–4.5, §6 Unit 11, §7.1); this plan amends it to
**v4.9** (the perturbed carla-like family in §4.4; budgets, below).
**Book:** `roar`. **Autopilot** per AGENTS.md.
**Base:** branches from `main` after `roar-009` merged (#164, 6c13919).
**v2** folds plan-review round 1 ([sol] REJECT: B1 U11.3's comparison across different cars, B2 gate failures
treated as pin corrections, S3 the stale-pose re-anchor untested, S4 the warnings count ungated; [fable] APPROVE
WITH NITS: B1 U11.2 unsatisfiable at a 450 s cap, S2 re-salting, S3 no public lag-2 car, S4 level-triggered respawn
detection, S5 the warning result too narrow, S6 U11.3 vacuous, N7–N10; [self] N1 the salt).
**v2.1** folds the round-2 nits ([sol] N1; [fable] S1, N2–N4); CONSENSUS.
New evidence: q10 (a crashed race's remainder equals a fresh fallback race of the same car), q11 (β triggers at 8°
and 6° with race seeds k mod 5).

## Scope
- Unit 11 `roar/units/unit-11-robustness/` (not a lab unit: design §6 gives Unit 11 no 🏁): lesson, exercises,
  solutions, teacher notes, manifest.
- **racekit** gains a **perturbed carla-like family** (design §4.4 v4.9): `carla_like(noise=False, perturb=None)`;
  with `perturb=k` (an int) the car's mass and yaw inertia, steering gain, throttle and brake authority, drag and
  grip are each multiplied by a factor drawn, seeded by `k`, from the published `PERTURBATION_FAMILY` ranges;
  `perturbation_factors(k)` returns those factors. `perturb=None` is today's car exactly. The lag is **not**
  perturbed (below); a separate keyword `lag_ticks=None` (an int overrides the car's lag) builds the lesson's lag-2
  car through the public API. The draw is the probe's exactly: `random.Random(f"perturb:{k}")`, one `uniform` per
  factor in the order grip, steering gain, throttle, brake, mass (one factor for mass and yaw inertia), drag; the
  grip factor multiplies every section's μ. Routed racekit tests cover determinism, the ranges, `perturb=None`
  identity, the draw order (k = 0's factors pinned) and `lag_ticks`.
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
  of them crash loops that run to a 700 s cap) take it to about 14 min. This plan raises the interim routed
  budget to **15 min** (v4.9), the fifth raise, and the follow-up to the author (raise again or move gates to a
  slower tier) is re-stated.

## Probe evidence (scratchpad `u11/`, `test-circuit`, MPC budget off (`MPC_BUDGET_MS = None`) in every probe)
The probe family is `pk.py`'s `perturbed(k)`: `carla_like(noise=True)` with each factor drawn from
`random.Random(f"perturb:{k}")`; the shipped racekit function draws exactly the same factors (Scope), so the probe
outcomes carry over and Phase A re-confirms them. Every gate race uses `noise=True`.
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
  With race seeds k mod 5 (q11), a β trigger at **8°** and at 6° each still crash all 3 crashing cars once, trip
  falsely on 2 clean cars (2 and 18, 275.85 and 276.6 s instead of about 275.05) and give a mean of 298.07 / 298.03 s
  against 296.66 s for the respawn alone. The shipped agent counts warnings (an instrument) and does not act on
  them; the lesson states the result for these thresholds and this fallback, not for every possible reaction
  (Challenge 9 tries a braking reaction).
- **The restart is a fresh race (q10):** for each of the 7 races at 0.58 that crash once with the fallback, the time
  after the respawn (race time − crash time − 1.0 s) is 0.4–0.7 s shorter than a fresh race of the same car and
  race seed started in the fallback configuration (`STEERING = "pursuit"`, `MU_FRACTION = 0.58 · 0.86`); fresh
  races of one car vary by 0.15 s over race seeds 0–4. The offset is systematic (the remainder is always the
  shorter); Phase A explains it from the runner's restart accounting and records its sign in the premise, and the
  lesson states the cost as "t + 1 s, to within a second", never more precisely.
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
- the respawn handler, **edge-triggered**: a respawn is handled when the collision impulse norm exceeds
  `RESPAWN_IMPULSE` (100 N·s), the reading differs from the previous step's, and no respawn was handled in the last
  `REFRACTORY_TICKS = 40` steps (2 s; CARLA's sensor may repeat its last reading, racekit reports it on one step
  only). `fall_back()`: clear `mpc_queue`, `mpc_last` and the plan, set a re-anchor flag (the **next** step takes
  `nearest_index`, because CARLA's first post-respawn step carries the stale crash pose), switch steering to
  `FALLBACK_STEERING = "pursuit"`, multiply the lateral limit by `FALLBACK_SCALE = 0.86` and re-plan the profile;
- the instruments: sideslip β and the warnings (`WARN_BETA_DEG = 8.0`, `WARN_ERROR_M = 1.6`, computed above
  `WARN_MIN_SPEED = 5.0` m/s) counted in `self.warnings` in every mode (before and after a fallback), never acted
  on; a test-only constant `WARN_FALLBACK = False` (True: a warning also calls `fall_back()`) exists for U11.9 and
  the lesson's §5, and is False in the shipped file;
- `lateral_limit()` multiplied by `self.limit_scale` (1.0 until a respawn), so with no respawn it is Unit 10 to
  the tick.
Python 3.8, numpy only, under `check_submission` (p99 ≤ 5 ms). A respawn costs one tick of about 3 ms (the profile
re-plan and `nearest_index`); p99 is unaffected.

## Gates (pinned from the probes; Phase A re-runs each with the shipped racekit family and the shipped agent)
**Any failed gate assertion** (an outcome, a ranking or a tolerance below) stops Phase A and amends the plan.
Only descriptive figures quoted in prose (a median, a mean, an error) may be corrected in the report.
- **U11.1 family:** `perturbation_factors(k)` is deterministic and inside the published ranges for k = 0–999;
  `carla_like(perturb=None)` races identically to today's `carla_like` (to the tick); a perturbed car differs.
- **U11.2 the hook:** `agents/unit-10.py` on the training perturbations (k = 0–23, race seed k mod 5, a 700 s cap):
  at least one race not clean, at least one crash loop (≥ 3 respawns, not finished).
- **U11.3 respawn economics:** for every U11.5 race (`agents/unit-11.py` at 0.58) that crashes exactly once and
  finishes, and there must be **at least 3** such races, the time after the respawn (race time − crash time
  − 1.0 s) is within **1.0 s** of a fresh race of the same car and race seed in the fallback configuration
  (`STEERING = "pursuit"`, `MU_FRACTION = 0.58 · 0.86`): the restart is a fresh race, so a crash at time t costs
  t + 1 s plus the fallback's slower pace.
- **U11.4 robust fraction:** on the training perturbations, 0.56 is not clean on all 24 and 0.54 is; the mean race
  time (not-finished races at the cap) is lowest at 0.54 among {0.58, 0.56, 0.54, 0.52}.
- **U11.5 the fallback:** `agents/unit-11.py` at `MU_FRACTION = 0.58` finishes every training and held-out race
  with at most 1 collision; on `carla_like(noise=True, lag_ticks=2)` (700 s cap), `agents/unit-10.py` at 0.54 does
  not finish and `agents/unit-11.py` at 0.54 finishes with exactly 1 collision.
- **U11.6 the gate (design §6):** `agents/unit-11.py` is clean on **24/24 held-out** perturbations (k = 24–47).
- **U11.7 equivalence:** with no respawn, `agents/unit-11.py` races exactly as `agents/unit-10.py` at the same
  constants (the nominal car and 3 perturbed cars, to the tick).
- **U11.7a the handler, on scripted sensors** (no race; fake sensor objects feeding `step()`): (i) a step at 20 m/s with a
  β of 10° and a line error of 2 m increments `warnings` and issues exactly the action `agents/unit-10.py` issues
  from the same inputs and state; (ii) a respawn sequence as CARLA delivers it (the impulse with the stale crash
  pose, then the start pose) handles one respawn, keeps the index on the impulse step and re-anchors to the start
  on the next; (iii) the same impulse reading repeated on 10 consecutive steps is handled once; a new impulse after
  the 40-step refractory window is handled again.
- **U11.8 transfer (a finding, gated both ways):** at 0.54 on `test-circuit-seed2026` (its Unit 9 line and measured
  grip) on perturbations k = 0–11, race seed 0: at least one race not clean and at least one clean (q8: k = 6, 8, 9
  and 10 crash).
- **U11.9 warnings as a trigger (the negative result):** `agents/unit-11.py` at 0.58 with `WARN_FALLBACK = True`
  (β 8°) on the training perturbations (race seed k mod 5): every car that crashes with `WARN_FALLBACK = False`
  (U11.5) still crashes, and the mean race time is not lower than U11.5's training mean (q11: 298.07 vs 296.66 s).
- `check_submission(agents/unit-11.py)` passes (outside any pool).

## Budgets
- Routed pytest ≤ **15 min** (v4.9, interim). The Unit 11 job table (MPC races unless said): U11.2 24 (700 s cap);
  U11.3 7 pursuit races (fresh fallback twins); U11.4 72 (0.56, 0.54 and 0.52 on the training family; its 0.58 side
  is U11.2's races); U11.5 48 + 2 (700 s cap); U11.6 24; U11.7 5 (the nominal car with both agents, and 3 training
  cars with Unit 11 at 0.54; their Unit 10 twins are U11.4's 0.54 races); U11.8 12; U11.9 24. About 215 races, about 2,100 s of CPU (crash loops to 700 s count about 2.5 races each), about 4 min
  pooled on 8 workers, taking the suite from 10.0 to about 14.5 min. Measured in Phase D; over 15 min means stop and
  amend.
- Notebooks: the Unit 11 lesson, solutions and milestone ≤ **5 min** serial in total, each cell ≤ 120 s: the
  notebooks race small families (6–8 perturbations), not the gates' 24; every claim about 24 comes from the premise
  fixture's pinned numbers, stated as such.
- Book exec total reported against v4.8's 40 CI-minutes (31.3 after roar-009; about 36 after this plan, leaving
  about 4 for Checkpoint B and Units 12–13: the follow-up to the author is re-stated with the routed one).

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
  Solutions in a **separate fresh** Opus session. The lesson calls the lag-2 car "the lag Unit 8 identified, plus
  one tick", never a hidden value.
- **Phase C — teacher notes** (inline).
- **Phase D — verification:** `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN; budgets measured.

## Out of scope
- Online identification (estimating grip or lag while racing); per-track re-tuning for Checkpoint B (roar-011);
  CARLA labs (Unit 11 has none); any change to Units 1–10 content.

## Plan Review

### Round 1 (v1 @ 9ffbd10)
- [sol] REJECT.
  - B1 U11.3 compared one crashed car with other cars' clean median [FIXED v2: the same car and race seed, fresh, in
    the fallback configuration; q10: within 0.4–0.7 s on all 7; tolerance 1.0 s; at least 3 qualifying races].
  - B2 a failed tolerance or ranking could pass as a pin correction [FIXED v2: any failed assertion stops and amends;
    only prose figures are corrected].
  - S3 the stale-pose re-anchor is untestable in racekit races [FIXED v2: U11.7a (ii), scripted sensors].
  - S4 the warnings count ungated [FIXED v2: U11.7a (i), count and unchanged action on a scripted trace].
- [fable] APPROVE WITH NITS.
  - B1 U11.2's loop (≥ 3 respawns) is unreachable at the 450 s cap [FIXED v2: 700 s cap for U11.2 and the lag-2
    races; budget recomputed].
  - S2 re-salting throws away the evidence [FIXED v2: the shipped draw is the probe's, order pinned].
  - S3 no public lag-2 car [FIXED v2: `carla_like(lag_ticks=)`].
  - S4 level-triggered respawn detection [FIXED v2: edge-triggered with a 40-step refractory window; U11.7a (iii)].
  - S5 the warning result too narrow [FIXED v2: q11 β at 8° and 6° with race seeds; the lesson states its scope].
  - S6 U11.3 vacuous [FIXED v2: at least 3 races].
  - N7 U11.7's nominal Unit 10 race [FIXED v2]. N8 the family stated precisely [FIXED v2, Scope]. N9 the respawn
    tick cost [FIXED v2]. N10 the notebook exec headroom [FIXED v2, Budgets].
- [self] APPROVE WITH NITS. N1 the salt [FIXED v2 with [fable] S2].

### Round 2 (v2 @ 1550a3f): CONSENSUS
- [sol] APPROVE WITH NITS. N1 the q11 warning result has no premise gate [FIXED v2.1: U11.9, with a test-only
  `WARN_FALLBACK` constant].
- [fable] APPROVE WITH NITS (re-ran q10 for cars 8 and 16: −0.55 / −0.45 s).
  - S1 the remainder is systematically 0.45–0.7 s shorter than a fresh race, unexplained [FIXED v2.1: Phase A explains
    and records the sign; the lesson says "t + 1 s, to within a second"].
  - N2 the β instrument's speed threshold and counting after a fallback [FIXED v2.1: `WARN_MIN_SPEED`, counted in
    every mode; U11.7a (i) at 20 m/s].
  - N3 the lag-2 car is "the Unit 8-identified lag plus one", never a `_truth` value [FIXED v2.1: Phase B brief].
  - N4 pins for Phase A [FIXED v2.1: q10 sign; U11.8's crash set k = 6, 8, 9, 10].
- [self] APPROVE.
