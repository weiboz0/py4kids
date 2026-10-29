# Plan roar-012 — Unit 12: tuning against race time

**Design:** `docs/designs/013-roar-book.md` **v4.10** (§6 Unit 12, §7.1); this plan amends it to **v4.11**
(the Unit 12 gate's held-out track and objective, and the budgets, below).
**Book:** `roar`. **Autopilot** per AGENTS.md.
**Base:** branches from `main` after `roar-011` merged (#166, 1d96dd5).
**v2** folds plan-review round 1 ([sol] REJECT: B1 the held-out failure raced a rounded setting, S2 the crash-aware
acceptance ungated, S3 budget headroom, N4 the knob inventory; [fable] APPROVE WITH NITS: S1 the 20/24 cost as a
deviation, S2 budgets and notebook sizing, S3 the float repr, N1–N8). New evidence: probe `p8`.

## Scope
- Unit 12 `roar/units/unit-12-tuning/` (no 🏁: design §6 gives Unit 12 none): lesson, exercises (core + Challenges),
  solutions, teacher notes, manifest; milestone `milestones/unit-12-tuning.ipynb`.
- Reference submission `agents/unit-12.py`.
- A routed premise test for the Unit 12 gates; the registry (4 concepts, coverage entry, manifest, api-order,
  baseline, syllabus row 12); design 013 **v4.11**.
- No racekit change.

## The idea (what the probes found, and the story the unit tells)
The hook: "You have 30 knobs and 0.3 s of noise. Which changes are real?"
The probes say both halves are honest, and that the real danger is not the noise.
- **30 knobs.** `agents/unit-11.py` has 48 named module constants. The lesson classifies all 48 in one table (Phase
  B, from the file and the agent's code): 24 act in a clean race, 6 more only after a respawn (30 tunable knobs), the
  rest are mode switches, counters or settings the shipped mode never reads. In the p2 sweep (17 knobs) six move a
  clean race's time well beyond the noise, two more move it only by making the race not clean (`MPC_Q_E`,
  `MPC_Q_PSI`), and several do nothing at all (bit-identical races).
- **0.3 s of noise.** One track's 3-lap spread over race seeds is 0.05–0.25 s; the sum over the five training tracks
  spreads 0.45 s (1 lap) to 0.80 s (3 laps). Races are deterministic per seed.
- **Search works on the training family, and that is the trap.** A coordinate search over six global knobs on the
  five training tracks (3 laps, two seeds, Unit 1's acceptance rule, any not-clean race rejected) gains 48.9 s over
  15 laps. That setting is **not clean on any** of five races on the held-out track `test-circuit-seed2026`, and is
  clean on only 7 of 24 perturbed cars. Tuned on one track with per-section knobs, the gain is 14.1 s there and every
  other track crashes. **Many knobs + a family that does not contain the failure = overfitting**; the held-out track
  shows it.
- **The fix is the objective, not the search.** Adding Unit 11's three lowest-grip training cars to the objective
  (still rejecting any not-clean race) makes the same coordinate search accept **one** change, `A_DEC` 5.0 → 5.5,
  and reject every other step. That setting is 1.35 s faster on the held-out track (280.65 vs 282.00 s, both 5/5
  clean, spread 0.05 / 0.15 s): Unit 1's rule says it is real. The unit ships it as `agents/unit-12.py`.
- **What it costs.** On Unit 11's 24 held-out perturbed cars, `unit-12.py` finishes all 24 with 0 collisions (Unit
  11's design gate, N/N at 0 collisions, holds) but 4 of them (k = 24, 29, 32, 35) exceed the clean rule's 2 m line
  error (2.01–2.51 m); `unit-11.py` is clean on all 24. The 1.35 s is bought with line margin. The lesson says so,
  and Unit 13 decides which agent races (the follow-up list carries the choice to the author).

## Probe evidence (scratchpad `u12/`; `MPC_BUDGET_MS = None` in every race; nominal car is `carla_like(noise=True)`)
- **p1 noise and cost** (`unit-11.py`, seeds 0–9): 3-lap medians test-circuit 279.65, seed1 276.30, seed2 275.55,
  seed3 275.70, seed4 275.95, seed2026 281.98 s; 3-lap spreads over seeds 0–4: 0.05 / 0.10 / 0.10 / 0.15 / 0.15 /
  0.15 s. A 1-lap race costs about 2.0 CPU-s, a 3-lap race about 5.8. The same seed re-raced: bit-identical
  telemetry (12/12). 1-lap and 3-lap rankings agree (Spearman 0.96 over 46 clean settings), but 1 lap misses late
  crashes (`MPC_Q_E = 0.6`: clean on 15 one-lap races, not clean at 3 laps).
- **p2 knob map** (one knob at a time; 5 training tracks, 1 lap, seeds 0–2; Δ of the 5-track sum, noise 0.30 s):
  `MU_FRACTION` 0.50 → 0.60: +8.9 … −11.7 s; `SPEED_KP` 0.3 / 0.8 / 1.5: −9.4 / +6.1 / +11.3; `SPEED_KI` 0 / 0.2:
  +18.7 / −1.1; `A_ACC` 3 … 6: +15.3 … +0.35 (best 4.5, −2.9); `A_DEC` 4 / 4.5 / 5.5 / 6: +7.2 / +3.1 / −2.4 / −4.1;
  `TARGET_SPEED` 40 / 50 / 60: +8.2 / −1.4 / −1.4 (3 laps −10.5 / −13.4); `MPC_Q_PSI` 5: +90 (not clean);
  `MPC_Q_E` 1.5: +25 (not clean). Below the noise: `MPC_R_DU`, `MPC_HORIZON`, `REACHED_RADIUS`. Bit-identical
  (dead): `FALLBACK_SCALE` (no respawn), `CURVATURE_HORIZON` (cap mode only), `PREDICT_TICKS`, `LEAD_MIN_M = 1`.
- **p3 search on the training family** (objective: per race seed, the sum of 3-lap times on the five training
  tracks; seeds {0, 1}, 10 races per evaluation; any not-clean race rejects; acceptance `noise_aware_better` on the
  two per-seed sums; box MU_FRACTION [0.48, 0.66] step 0.02, SPEED_KP [0.1, 1] 0.1, A_DEC [4, 8] 0.5, A_ACC [3, 6]
  0.5, SPEED_KI [0, 0.3] 0.05, TARGET_SPEED [40, 60] 5; 200 races per method):
  coordinate 1383.15 → **1334.25** (MU 0.54 + 3 × 0.02 = `0.6000000000000001`, A_DEC 5.5, A_ACC 4.5); random (rng 12, batches of 6) → 1381.53;
  (1+4)-ES (σ = one grid step, ×1.5 on accept, ×0.8 on reject) → 1357.17. About 1,100 CPU-s per method. Random
  search drew two not-clean settings (0 collisions, line error 2.5 / 3.1 m) faster than anything else: counting a
  not-clean race at its time would have accepted them.
- **p4 held out** (`test-circuit-seed2026`, its Unit 9 line and measured grip, 3 laps, seeds 0–4, nominal car):

  | setting | median / spread (s) | clean | perturbed k 0–23 clean | k 24–47 clean |
  |---|---|---|---|---|
  | `unit-11.py` | 282.00 / 0.15 | 5/5 | 24/24 (mean 279.95) | 24/24 (279.96) |
  | p3 coordinate (MU 0.60, A_DEC 5.5, A_ACC 4.5) | 318.25 / 2.40 | **0/5** | 7/24 | 7/24 |
  | p3 ES | 389.0 | 0/5 | — | — |
  | crash-aware (MU 0.54, **A_DEC 5.5**, A_ACC 4.0) | **280.65 / 0.05** | 5/5 | 24/24 (278.77) | **20/24** (278.84) |

  The crash-aware objective adds `test-circuit` on training cars 16, 18, 8 (Unit 11's `grip_order[:3]`; race seed
  (k + r) mod 5 for replicate r) to each replicate: 16 races per evaluation. Its coordinate search over MU_FRACTION,
  A_DEC, A_ACC (160 races, 938 CPU-s) accepts A_DEC 5.5 only; MU 0.56, A_DEC 6.0, A_ACC 4.5 and A_ACC 3.5 each fail
  on a low-grip car. Its four held-out misses (k = 24, 29, 32, 35) finish with 0 collisions, faster than shipped
  (279.45–280.05 s), at line error 2.01–2.51 m.
- **p8 (plan review)**: the p3 coordinate setting raced with its exact `MU_FRACTION = 0.6000000000000001` and with
  the grid value 0.60: identical race times on all 15 races (training sums 1334.35 / 1334.15, 10/10 clean; seed2026
  318.25, 316.45, 318.85, 317.00, 318.85, 0/5 clean, max line error 5.25 m) but different telemetry (trap 2). The
  crash-aware objective's 16 races (per-replicate sums): `unit-11.py` 2224.90 / 2224.35, `A_DEC = 5.5` 2215.35 /
  2215.25, both 16/16 clean; Unit 1's rule accepts 5.5 (gap 9.32 s > spreads 0.55 / 0.10). `A_DEC = 6.0` crashes on
  all six low-grip races (3 collisions each). Dead knobs at `FALLBACK_SCALE = 0.5`, `CURVATURE_HORIZON = 5`,
  `PREDICT_TICKS = 1` (1 lap, `test-circuit`, seed 0): the shipped digest (96.40 s); `MU_FRACTION = 0.60` 93.95 s.
  The lesson-sized coordinate search with each step rounded to the grid (`round(x, 2)`), serial, 1 lap, seeds
  {0, 1}: 40 races, 87 CPU-s, 88 s wall at load 4; objective 476.75 → 472.62 (30 races) → 468.77 (MU 0.58).
- **p5 overfitting** (coordinate on `test-circuit` only, 3 laps, seeds {0, 1}; the six globals plus GRIP's six,
  box 0.7–1.5 step 0.05; 60 races): MU 0.64, A_DEC 5.5, GRIP[0] 1.2, GRIP[2] 1.05: test-circuit 279.65 → **265.55**
  (3/3 clean); seeds 0–2 elsewhere: seed1 0/3 clean (5 collisions), seed2 0/3, seed3 0/3, seed4 0/3 (6 collisions),
  **seed2026 0/3** (6 collisions).
- **p6 profiling and traps** (one serial 3-lap race on seed1): `step()` p50 0.914 ms, p99 0.995 ms; `mpc_command`
  63 % of `step()`, `predict()` (an instrument nothing reads) 19 %; pure pursuit p50 0.218 ms; `MPC_HORIZON = 20`
  p50 0.537 ms at +0.10 s. Traps reproduced: (1) a hand-rounded constant races differently from its `repr` (three
  digests for one value); (2) 0.54 + 3 × 0.02 is `0.6000000000000001`, which races differently from `0.6` at the
  same time; (3) race time is ticks × 0.05 (`279.65000000000003`), so a gain under one tick ties; (4) with the timing
  on at a budget near `mpc()`'s cost (0.85 ms) the same file and seed gave four different races; (5) dead knobs.
  Not reproduced (not taught): a numpy vs Python float-sum difference.
- **p7 the notebook-sized search** (serial, one worker): coordinate over MU_FRACTION, A_DEC, A_ACC at 1 lap, seeds
  {0, 1}, five training tracks: 50 races, 108 CPU-s, 109 s wall; objective 476.75 → 465.02 (MU → 0.56, 0.58, 0.60);
  that setting is clean at 3 laps on training (10/10).

## Deviations from design (recorded; design 013 v4.11)
- §6's gate "the tuned agent beats the hand-tuned one on a held-out track (noise-aware)" is met on
  `test-circuit-seed2026` (Checkpoint A's track, never in Unit 12's objective) with `noise_aware_better` over race
  seeds 0–4; the tuned agent is the **crash-aware** search's result, and the unit also gates the speed search's
  failure there (the finding, both ways).
- **Robustness: Unit 11's held-out gate as roar-010 applied it (24/24 clean by the full clean rule) does not hold for
  `unit-12.py`** (20/24: four cars over the 2 m line rule, all finished with 0 collisions; and on seed2026 its max line
  error is 1.76 m against `unit-11.py`'s 1.20 m). The literal design §6 wording for Unit 11 (N/N at 0 collisions)
  holds. The trade (1.35 s on the held-out track vs line margin on perturbed cars) is the unit's honest finding; the
  choice of race-day agent is a judgment fork for the author, held in the follow-up list for Unit 13.
- "Packaging and version pinning" is taught as a checklist on the shipped file (one file, numpy only, Python 3.8,
  `check_submission`, pinned versions written down), not probed: nothing in racekit varies with a version.
- The full searches (p3, p4) cost about 1,000 CPU-s each and are **pinned records** (this plan), not live
  notebook runs; the notebooks run one 1-lap coordinate search (p8's, in two cells) and small demonstrations. The
  evolution strategy is also practised live in a small form (Ex 3: a (1+2)-ES, 1 lap, two tracks).

## Concepts (4 new; all `kind: technique`, globally unique)
| id | taught where | practised |
|---|---|---|
| `black-box-search` | lesson §1–§3: race time as a black-box objective; coordinate, random and (1+λ) evolution-strategy search on a race budget; acceptance by Unit 1's rule; rejecting not-clean settings | Ex 1–4, 9 |
| `held-out-track-validation` | lesson §4–§5: overfitting knobs to the tracks they were tuned on; the held-out track; the crash-aware objective | Ex 5, 6, 10 |
| `step-profiling` | lesson §6: `cProfile` on one race, where `step()`'s time goes, dead work, the horizon trade | Ex 7 |
| `determinism-and-packaging` | lesson §7: same seed same race; `repr` round-trips, step accumulation, tick quantisation, timing-on is not reproducible, dead knobs; the packaging checklist and version pinning | Ex 8 |

API names (taught): `default_rng`, `uniform`, `normal` → `black-box-search`; `Profile`, `enable`, `disable`, `Stats`,
`sort_stats`, `print_stats` → `step-profiling`. No other new callables; `noise_aware_better`, `repeat_races`,
`perf_counter` are already taught; `write_variant` is infrastructure.

## The reference submission
`agents/unit-12.py` = `agents/unit-11.py` with `A_DEC = 5.5` (the crash-aware search's one accepted change) and a
header comment saying why. Every function and class body identical (an AST check, as CPB.7). Python 3.8, numpy only,
`MPC_BUDGET_MS = 5.0`, under `check_submission`.

## Gates (pinned from the probes; Phase A re-runs each with the shipped agent)
**Any failed gate assertion** (an outcome, a ranking or a tolerance) stops Phase A and amends the plan. Times are
pinned to ±1 tick (0.05 s). Every race `MPC_BUDGET_MS = None`, nominal noisy car unless said; non-`test-circuit`
tracks race their Unit 9 line and measured grip (`_line_solver`, `MEASURED_MU_G`), as in Units 9–11.
- **U12.1 determinism and noise:** one race re-raced with the same seed has identical telemetry; `unit-11.py`'s
  3-lap spread on `test-circuit-seed2026` over seeds 0–4 is ≤ 0.25 s (0.15).
- **U12.2 knob map (1 lap, `test-circuit`, seed 0; p8):** `FALLBACK_SCALE = 0.5`, `CURVATURE_HORIZON = 5` and
  `PREDICT_TICKS = 1` each race identically to the shipped file (identical telemetry, 96.40 s); `MU_FRACTION = 0.60`
  is faster by more than 0.25 s (93.95 s).
- **U12.3 overfitting:** the p5 setting is clean on `test-circuit` seeds 0, 1 and faster than `unit-11.py` there by
  more than 10 s; on `test-circuit-seed2026` seeds 0–2 it is clean on none.
- **U12.4 the speed search's result:** the p3 coordinate setting, written on the grid (`MU_FRACTION = 0.60`,
  `A_DEC = 5.5`, `A_ACC = 4.5`; p8: the same race times as the search's exact `0.6000000000000001`), is clean on all 10 training races (seeds 0, 1) with
  a per-seed 5-track sum lower than `unit-11.py`'s by more than 40 s; on `test-circuit-seed2026` seeds 0–4 it is
  clean on none.
- **U12.5 the gate (design §6):** `unit-12.py` vs `unit-11.py` on `test-circuit-seed2026`, 3 laps, seeds 0–4: both
  5/5 clean; `noise_aware_better(unit-12 times, unit-11 times)`; medians 280.65 and 282.00 s (±1 tick).
- **U12.6 the crash-aware verdict:** on the objective's 16 races (five training tracks × seeds 0, 1 plus
  `test-circuit` × cars 16, 18, 8 at race seed (k + r) mod 5, replicates r = 0, 1), `unit-12.py` and `unit-11.py` are
  both 16/16 clean and `noise_aware_better(unit-12's two per-replicate sums, unit-11's)` holds (p8: 2215.35 / 2215.25
  vs 2224.90 / 2224.35); `A_DEC = 6.0` is not clean on at least one of its six low-grip-car races (p8: all six), the
  step the search rejected.
- **U12.7 the cost (both ways):** `unit-12.py` on held-out perturbed cars k = 24–47 (`test-circuit`, race seed
  k mod 5): all 24 finish with 0 collisions; at least 20 clean; the not-clean ones are exactly k ∈ {24, 29, 32, 35},
  each with max line error ≤ 2.6 m; `unit-12.py`'s max line error on the U12.5 seed2026 races is reported (1.76 m vs
  1.20 m).
- **U12.8 equivalence:** `unit-12.py` differs from `unit-11.py` only in `A_DEC` (AST).
- `check_submission(agents/unit-12.py)` passes (outside any pool).

## Budgets
- Routed pytest: the Unit 12 job table (3-lap MPC races unless said): U12.1 1 re-race (its twin is a U12.5 race);
  U12.2 4 one-lap races; U12.3 2 + 3 (plus `unit-11.py`'s `test-circuit` seeds 0, 1: 2); U12.4 10 + 5 (and
  `unit-11.py`'s 10 training races); U12.5 10; U12.6 32 + 6; U12.7 24. About 110 races, about 600 CPU-s, about
  2 min pooled. The suite measured 927–936 s on `roar-011`, against 15.5 min: this plan raises the interim routed
  budget to **18 min** (v4.11), the seventh raise, leaving about 1 min of headroom over the estimate. The author's tiering decision (keep raising, or move the
  premise gates to a slower tier) is overdue and stays in the follow-up list.
- Notebooks: the Unit 12 lesson, solutions and milestone ≤ **5 min** serial in total, each cell ≤ 120 s (target
  ≤ 60 s). The race table, 1-lap races at about 2 CPU-s, 3-lap at about 6:

  | notebook | races | estimate |
  |---|---|---|
  | lesson | live search 40 one-lap (two cells of 20, about 45 s each); knob demos 3 one-lap; overfit on seed2026 1 three-lap; `cProfile` 1 three-lap; determinism 2 one-lap | about 115 s |
  | solutions | Ex 1 noise 5 one-lap; Ex 2 knob sweep 6 one-lap; Ex 3 (1+2)-ES 12 one-lap on 2 tracks; Ex 4 random 8 one-lap; Ex 5 held-out 4 three-lap; Ex 6 crash-aware check 6 one-lap; Ex 7 profile 1 one-lap; Ex 8 traps 3 one-lap; Challenge 9 10 one-lap; Challenge 10 policy gradient 10 one-lap | about 140 s |
  | milestone | U12.5's table: 10 three-lap; `check_submission` | about 65 s |

  About 5.3 min estimated: Phase B trims the solutions to fit 5 min (measured; a cell over 120 s splits).
  Every full-search number comes from this plan's pinned record, stated as such.
- Book exec: about 39.9 after roar-011, about 45 after this plan, against v4.10's 45 CI-minutes: no margin. This plan
  raises the interim book-exec budget to **50 CI-minutes** (v4.11), the fourth raise, so Unit 12 fits with run-to-run
  margin; Unit 13 and the capstone still need the author's tiering decision (design v4.10 named Unit 12), recorded as
  the first follow-up.

## Phases
- **Phase A — agent + premise + registry** (Opus subagent).
  - `agents/unit-12.py`; `tests/_tuning_premise.py` + `tests/test_racekit_unit12_premise.py` + a conftest fixture
    (pooled races, the existing pool runner); every gate U12.1–U12.8 confirmed and logged; `check_submission` on
    the agent, outside any pool.
  - Registry: 4 concepts, coverage-map entry `unit-12-tuning`, manifest, api-order (the 9 names above), baseline
    `library_methods`, syllabus row 12 (no emoji); design 013 v4.11 (§6 row 12's gate text, §7.1 budgets,
    changelog).
- **Phase B — content (Opus subagents).** Every coordinate step is snapped to its grid with `round(x, 2)`; §7 shows
  the unrounded `0.6000000000000001` once, on purpose (same time, different telemetry: "different race" means the
  telemetry, not the time). Lesson, project-first: the hook (the knob count from the file, the noise,
  and the p3 table: the speed search's 48.9 s, then its held-out races), then §1 the objective and the noise, §2
  the knob map (p2 as a pinned table; two live 1-lap demonstrations: a dead knob, a big one), §3 coordinate search
  live (p8's 40 races, two cells), random and ES on the pinned p3 record plus a small live random draw, §4 overfitting (p5 pinned; one
  live held-out race of the overfit setting), §5 the crash-aware objective and `unit-12.py` (p4 pinned; the cost,
  20/24), §6 profiling (`cProfile` on one race), §7 determinism, rounding traps and packaging. Exercises: 8 core + 2
  Challenges (9: search `SPEED_KP`/`SPEED_KI`/`TARGET_SPEED` on a small box and report why they are fragile; 10: an
  optional policy-gradient taste on one knob, compared honestly with coordinate search on the same race budget, per
  design §6). Milestone: the U12.5 race table (`unit-12.py` vs `unit-11.py` on seed2026) and `check_submission`.
  Solutions in a **separate fresh** Opus session.
- **Phase C — teacher notes** (inline).
- **Phase D — verification:** `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN; budgets measured.

## Out of scope
- Re-tuning for `monza-like` or choosing the race-day agent (Unit 13, roar-013); deep RL as core content (the
  policy-gradient Challenge is optional, design §9); any racekit change; Checkpoint B's track (never raced here).

## Plan Review

### Round 1 (v1 @ 1db655e)
Verdicts: [self] APPROVE WITH NITS; [sol] REJECT; [fable] APPROVE WITH NITS.
[self]: the story is honest and every number traces to a probe log; N: the 20/24 robustness cost should be a recorded deviation, and the A_DEC 6.0 rejection gate should cover both replicates (folded before the gate).
- [sol] B1 / [fable] S3: the held-out failure raced `MU_FRACTION = 0.6`, the search produced `0.6000000000000001`. p8 races both: identical race times everywhere (different telemetry); U12.4 races the grid value, the notebooks snap steps to the grid, §7 shows the unrounded value on purpose. Folded.
- [sol] S2: U12.6 now also gates that `A_DEC = 5.5` beats `unit-11.py` on the 16-race objective by Unit 1's rule (p8: gap 9.32 s). Folded.
- [sol] S3 / [fable] S2: routed 17.5 → 18 min; book exec 45 → 50 CI-minutes (interim, fourth raise); a per-notebook race table; the lesson search 40 races in two cells (p8: 88 s serial). Folded.
- [fable] S1: the 20/24 cost recorded as a deviation (and in v4.11's changelog), with the race-day agent named as a judgment fork for the author. Folded.
- [sol] N4 / [fable] N7: the inventory: 48 constants; the lesson classifies all 48 (the 30-knob split is derived there, not from p2's 17). Folded.
- [fable] N1 (six clean knobs, two that act by crashing), N2 (dead-knob values now probed, p8), N4 (`write_variant` is infrastructure), N5 (a small live ES exercise), N6 (`held-out-track-validation`), N8 (seed2026 line error 1.76 vs 1.20 m): folded. N3 ("different race" means telemetry): folded into Phase B.
