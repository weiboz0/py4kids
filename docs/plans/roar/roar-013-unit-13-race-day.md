# Plan roar-013 — Unit 13: race day

**Design:** `docs/designs/013-roar-book.md` **v4.11** (§6 Unit 13, §7.1, §7.3); this plan amends it to **v4.12**
(Unit 13's gate pinned on `monza-like`, and the budgets, below).
**Book:** `roar`. **Autopilot** per AGENTS.md.
**Base:** branches from `main` after `roar-012` merged (#167, d8cf80b).
**v1**; **v2** folds plan-review round 1 ([sol] REJECT: B1 the N/N gate never raced the shipped timing policy, B2 the
lab's five-launch record and acceptance paths, S3 Exercise 6's data; [fable] APPROVE WITH NITS: S1 the isolated
3.8 check's track, S2–S5, S6 the lab under lab-check, S7, N1–N6; [self] the held-out cars as validation). New
evidence: probes `p8` (fresh test cars 48–71, pre-registered), `p9` (the timing policy bracketed) and `p10` (both
edges confirmed at the shipped `A_ACC` 5.0).
**v3** folds plan-review round 2 ([sol] REJECT: B1 a mid-race horizon cut is not covered by any gate, B2 the test cars
were reused, S3 the solver call; [fable] APPROVE WITH NITS: S1 = [sol] B2, S2–S5, N1–N4). The shipped file now sets
`MPC_MIN_HORIZON = 40`, so its budget policy never changes the horizon (the gates race exactly what ships); cars
48–71 become validation cars, and fresh pre-registered test cars 72–95 were raced once with the literal shipped file
(`p11`).

## Scope
- Unit 13 `roar/units/unit-13-race-day/` (🏁: design §6 gives Unit 13 a real-sim lab): lesson, exercises (core +
  Challenge), solutions, teacher notes, manifest (`lab: true`), `labs/real-sim.ipynb`; milestone
  `milestones/unit-13-race-day.ipynb`.
- Reference submission `agents/unit-13.py`: the book's race-day agent for `monza-like`.
- A routed premise test for the Unit 13 gates; the registry (coverage entry, manifest, syllabus row 13; **no new
  concepts and no new API names**: Unit 13 introduces nothing); `roar/docs/qualification.md`'s `roar-013` row
  (the interim timed CARLA check, `PENDING (author)`, design §7.3); design 013 **v4.12**.
- No racekit code change.

## The idea (what the probes found, and the story the unit tells)
The hook: "Assemble, qualify and submit."
The real competition races **one known track** (CARLA's Monza). So the honest race-day story is: **the track is known;
the car is not.** Tuning on `monza-like` itself is legitimate; what must be held out is the **car** (Unit 11's
perturbed family: training cars k = 0–23, held-out cars k = 24–47, race seed k mod 5).
- **Assemble.** `agents/unit-13.py` is `agents/unit-11.py` (Unit 10's MPC on Unit 9's line with Unit 8's grip, Unit
  11's respawn fallback) with `monza-like`'s line (`LINE_CONTROL`, 285 values, Unit 9's solver), its measured grip
  (`MU_G`, Unit 8's probes, as `tests/_line_premise.MEASURED_MU_G` pins it) three re-tuned speed constants, and `MPC_MIN_HORIZON = 40` (below).
  Section 0's grip is a **lower bound** (its probe never slid). It costs nothing: on the solved line section 0's
  largest curvature is 2e-5 1/m (a radius of about 45 km), and the races give identical times and line errors with `MU_G[0]` at
  5.38, 7.97, 9.12 or 12.0 (p5: nominal seeds 0–4 and cars 16, 18, 8). A student can see why from v_max = √(μg/κ) without racing.
- **Re-tune on the known track, crash-aware (Unit 12's objective).** Each evaluation races the nominal car on seeds
  0 and 1 plus the three lowest-grip **training** cars (k = 16, 18, 8: grip factors 0.930, 0.934, 0.936), 3 laps;
  any not-clean race rejects the setting; Unit 1's rule on the two per-replicate sums accepts a step. A coordinate
  search from `unit-11.py`'s (0.54, 5.0, 4.0) over `MU_FRACTION` (grid 0.02), `A_DEC` (0.5) and `A_ACC` (0.5), 100
  races (p2): `MU_FRACTION` climbs clean to 0.66 (0.68 is not clean: at `A_ACC` 4.0 car 8 collides and car 16 runs 2.01 m from
  its line; at the shipped `A_ACC` 5.0, p10, cars 16 and 8 collide and car 18 runs 2.01 m); `A_DEC` 5.5 is not
  clean on all three low-grip cars at `A_ACC` 4.0, 5.5 and (p10) 5.0 (4.5 is clean but slower); `A_ACC` 4.0 → 4.5 → 5.0 is accepted, and 5.0, 5.5, 6.0
  are a plateau (per-replicate sums [1861.95, 1861.90], [1861.90, 1861.85] and [1862.05, 1861.95] s).
  The lesson's and Exercise 3's table pins every evaluated setting with its two per-replicate sums and, for a
  not-clean one, each failing race's reason (collision, or line error over 2 m), from `u13/p2.pkl`.
  **A determinism trap, live:** the search's literal last step, `A_ACC` 5.0 → 5.5, was accepted on a floating-point
  tie (the pairs [1861.95, 1861.90] and [1861.90, 1861.85]: gain 0.0500000000001819 s against a spread of
  0.049999999999954525 s, exactly one tick each, so the float comparison says "beats"). Unit 12's traps apply: compare in whole ticks
  (or with a half-tick tolerance), and the step is a tie, not a gain. The incumbent is **(0.66, 5.0, 5.0)**: the
  **edge** on two knobs, `MU_FRACTION` (0.68 not clean) and `A_DEC` (5.5 not clean). The search found no edge for `A_ACC`
  (6.0 is clean; 6.5 and 7.0, inside its box of 2.0–7.0, were not raced).
- **The margin rule, on every knob at its edge.** Unit 11's rule (one grid step inside the edge) was stated for
  its one knob. On held-out cars 24–47 (3 laps, p3):

  | setting (`MU_FRACTION`, `A_DEC`, `A_ACC`) | held-out clean | median (s) | max line error (m) | not clean |
  |---|---|---|---|---|
  | the edge E (0.66, 5.0, 5.0) | 22/24 | 465.05 | 9.53 | car 24 (2 collisions, 737 s), car 41 (2 collisions, 889 s) |
  | the search's literal output E′ (0.66, 5.0, 5.5) | 22/24 | 465.00 | 2.64 | cars 41 and 46 (1 collision each) |
  | margin on `MU_FRACTION` only, M (0.64, 5.0, 5.0) | 23/24 | 467.02 | 5.42 | car 41 (1 collision, 685 s) |
  | **margin on both edged knobs, M2 (0.64, 4.5, 5.0)** | **24/24** | 468.83 | 1.34 | none |
  | margin on `A_DEC` only, P (0.66, 4.5, 5.0) | 24/24 | 466.73 | 1.44 | none |
  | `unit-11.py` as shipped (0.54, 5.0, 4.0) | 24/24 | 482.23 | 1.31 | none |
  | `unit-12.py` as shipped (0.54, 5.5, 4.0) | 24/24 | 480.48 | 1.87 | none |
  | `unit-07.py` as shipped | 12/24 | 708.17 | 6.73 | 12 cars, 144 collisions, each cut at 900 s |

  The rule applied only to Unit 11's knob (M) is **not** N/N; applied to **every knob at its edge** (M2) it is.
  M2 is the rule's answer, fixed before any held-out result: p3 raced E, E′, M and M2 in one pre-declared job, and P
  was raced afterwards (p3b). M is the cautionary row (Unit 11's rule read too narrowly). P (margin only on the knob that failed) is also 24/24 and about 2 s faster: Challenge 9
  asks whether that is a finding or a fit to the held-out cars. **The unit ships M2.** M2 is also 24/24 clean on
  the training cars (median 468.35 s, max line error 1.30 m).
  **A test set, raced once.** The held-out cars 24–47 showed which reading of the rule to ship and P's 2 s, so (as
  Unit 12 taught for tracks) they have become a **validation** set. Cars 48–71 were pre-registered as a test set
  (p8: M2 24/24 clean, median 469.65 s, max line error 1.37 m), then raced twice more with M2 under other timing
  settings (p9) and informed the timing decision below, so they are validation cars too (the pre-registration's
  one deviation, recorded). With the shipped file fixed first, fresh cars **k = 72–95** were pre-registered
  (`u13/p11-preregistration.txt`) and raced **once** with the literal shipped file, timing on (p11): **24/24
  clean**, median 468.65 s, max line error 1.37 m. The lesson keeps the sets apart: training cars 0–23 (in the
  objective: 16, 18, 8), validation cars 24–71, test cars 72–95. A knob never pushed to a not-clean setting gets
  no margin: `A_ACC`'s search stopped at 6.0 by Unit 1's rule, so M2 keeps its 5.0. Honesty: all three are racekit's stand-in for
  "a car you have not met"; **the real test is CARLA**, raced in the lab.
- **MPC or pursuit (falsifiable, Unit 10's question again).** At M2 on the nominal car, seeds 0–4: MPC 468.55 s
  (spread 0.10, max line error 1.01 m), pursuit (`STEERING = "pursuit"`) 468.60 s (spread 0.10, 1.66 m): Unit 1's
  rule says neither is faster. On the held-out cars pursuit is **13/24 clean (11 collisions)**, MPC 24/24. MPC
  costs about 2.7× the CPU (step p99 about 1.0 ms, inside the 5 ms budget). The submission keeps MPC: the
  comparison is time first, then margin, as Unit 10 taught.
- **The gate (design §6: `check_submission`, the timing budget, N/N clean races, beats the Unit 7 agent
  noise-aware).** `unit-13.py` vs `unit-07.py` on `monza-like`, nominal car, 3 laps, seeds 0–4: 468.55 s (spread
  0.10, 5/5 clean) against 515.10 s (spread 0.15, 5/5 clean): 46.55 s, Unit 1's rule holds by a wide margin.
  N/N: 5/5 nominal, 24/24 on each validation set and 24/24 test cars.
  **The shipped timing policy (ship the behaviour you tested).** The races above switch timing off; the submitted file keeps `MPC_BUDGET_MS = 5.0`,
  and under load a slow `mpc()` call halves the horizon for the rest of the race (40 → 20 → 10, never restored).
  Timing-on races are not reproducible (Unit 12), so the plan brackets the policy deterministically (p9): M2 with
  the horizon fixed at 20, and with `MPC_BUDGET_MS = 0.0` (every call over budget: the horizon is 10 from the
  third tick to the end, the policy's worst case), is clean on nominal seeds 0–4, cars 24–47 and cars 48–71 at
  both (106 races, max line error 1.38 m at 20 and 1.58 m at 10). That shows each regime is clean, but no finite
  set of races covers every time a load spike could cut the horizon mid-race. So the race-day file sets
  `MPC_MIN_HORIZON = 40`: the policy can no longer cut (a slow call is still counted in `over_budget`), every race
  is the race the gates ran, and the timing check is made **before** the race, by `check_submission` on the race
  machine (p99 about 1.0 ms against the 5 ms budget). The lesson presents this as a race-day trade: Unit 10's
  adaptive policy protects a machine you cannot check; on race day you check the machine, and ship the behaviour
  you tested. `check_submission(agents/unit-13.py, track="monza-like")` passes,
  step p99 about 1.0 ms (p6, under a load of 7.7). On its **default** track (`test-circuit`) it fails at
  construction (`LINE_CONTROL has 285 values, this track needs 133`): a race-day submission is checked on its
  own track, as the Unit 10 lab found.
- **Qualify and submit (the packaging checklist, Unit 12).** One file, numpy and math only, Python 3.8 syntax
  (`check_submission` parses it at `feature_version=(3, 8)`), constants written with `repr`, `MPC_BUDGET_MS = 5.0`
  for the race (timing off only for comparing), the season's submission rules re-checked (the unmodified
  `competition_runner.py` and `infrastructure.py`; `instruction.txt` vs `requirements.txt`, design §1.1: the two
  sources disagree, so the student reads the current season's page), and what to re-check if the season's runner,
  map or CARLA version changes (design §7.3). The interim timed CARLA check of the Unit 13 reference is
  `PENDING (author)`.

## Probe evidence (scratchpad `u13/`; `MPC_BUDGET_MS = None` unless said; 3 laps; cap 900 s; the nominal car is `carla_like(noise=True)`)
- **p1 baselines** (seeds 0–4, median / spread, all 5/5 clean): `unit-07.py` 515.10 / 0.15 (1.67 m; it needs no
  line or grip: it plans with `A_LAT` on the centreline); `unit-10.py` 476.00 / 0.05 at 0.58, 468.75 / 0.10 at
  0.64; `unit-11.py` 482.00 / 0.05; `unit-12.py` 480.25 / 0.05; `checkpoint-b.py` 493.50 / 0.10. One lap ranks all
  six as three laps do. CPU per 3-lap race: MPC about 10 s, `unit-07.py` 3.8 s, pursuit 3.6 s; 1-lap MPC about 3.5 s.
- **p2 the crash-aware re-tune** (100 races, 935 CPU-s): the trajectory and every evaluated setting are in
  `u13/p2.log` (the plan's table above; the incumbent 1861.88 at the literal (0.66, 5.0, 5.5), 1861.93 at
  (0.66, 5.0, 5.0)).
- **p3 / p3b / p3c held-out and training cars:** the table above (`u13/p3*.log`).
- **p4 MPC vs pursuit at M2:** above (`u13/p4.log`, `u13/p3c.log`).
- **p5 section 0's lower bound:** identical times and max line errors (telemetry not compared) at `MU_G[0]` ∈ {5.38, 7.97, 9.12, 12.0} (`u13/p5.log`).
- **p6 the submission:** `check_submission(..., track="monza-like")` PASS, 464.35 s on its own default car, p99
  0.997 ms; on `test-circuit` it fails at construction (`u13/p6.log`).
- **p7 the gate vs Unit 7:** above; with timing on (5.0 ms, a 5-worker pool) M2 is 468.60 / 0.25, still clean, and
  some races halve the horizon under load (`u13/p7.log`): timing-on races are not reproducible (Unit 12).
- **p8 cars 48–71** (pre-registered as test cars in `u13/p8-preregistration.txt`; validation cars since p9): M2 on k = 48–71,
  24/24 clean, median 469.65 s, max line error 1.37 m (`u13/p8.log`).
- **p9 the timing policy, bracketed:** M2 at `MPC_HORIZON = 20` (timing off) and at `MPC_BUDGET_MS = 0.0`, on
  nominal seeds 0–4, cars 24–47 and cars 48–71: 106/106 clean (`u13/p9.log`).
- **p11 the test cars** (pre-registered in `u13/p11-preregistration.txt`, the shipped file fixed first): the literal
  shipped configuration, timing on, on k = 72–95: 24/24 clean, median 468.65 s, max line error 1.37 m, no horizon
  cut (`u13/p11.log`).
- **p10 the edges at the shipped `A_ACC` 5.0:** (0.68, 5.0, 5.0) and (0.66, 5.5, 5.0) are each not clean on cars
  16, 18 and 8 (`u13/p10.log`).
- **Expected time over the validation cars** (per-car times in `u13/p3.pkl`, `p3c.pkl`; a race cut at 900 s counts
  at 900 s): E 494.11 s, M 476.24 s, M2 468.98 s, `unit-07.py` 707.62 s. Here expected time also picks M2: E's two
  crashes cost more than its 3.9 s a clean race saves (unlike Checkpoint B's race day, where the expected-time rule
  picked the edge).

## Deviations from design (recorded; design 013 v4.12)
- §6's Unit 13 gate "N/N clean races" is pinned as **5/5 nominal (seeds 0–4), 24/24 validation cars (k = 24–47)
  and 24/24 test cars (k = 72–95)** on `monza-like`; "the timing budget" is `check_submission`'s p99 ≤ 5 ms on
  `monza-like`. Cars 48–95 are new Unit 13 validation (48–71) and test (72–95) sets of the same family; design
  §4.4 named only 0–23 and 24–47, and v4.12 amends it. The sealed range k ≥ 1000 stays untouched.
- The race-day file sets `MPC_MIN_HORIZON = 40` (Unit 10 taught a horizon-halving budget policy): the policy
  becomes a counter, so the shipped behaviour is the gated behaviour.
- Unit 11's margin rule is applied to **every knob at its edge** (Unit 11 stated it for its one knob); the unit
  shows the one-knob reading failing (M, 23/24).
- The race-day agent is a **re-tune of `unit-11.py`** on `monza-like`; `unit-12.py`'s `A_DEC = 5.5` is not carried
  (on `monza-like` at `MU_FRACTION` 0.66 it is not clean on all three low-grip cars). This resolves the roar-012
  follow-up "which agent races" by the book's own rules; the follow-up list keeps it for the author.
  `checkpoint-b.py` (`MU_FRACTION` 0.48, Checkpoint B's margin answer on its own track) is the slowest tuned agent on
  `monza-like` (493.50 s, p1) and was not raced on the perturbed cars there: a re-tune on the known track replaces it.
- `check_submission` is called with `track="monza-like"` everywhere (its default track refuses a Monza line).

## Concepts
**Introduces nothing** (design §6). Practises (each exercised in Unit 13's exercises, by name):
`cornering-speed-limit`, `speed-profile`, `racing-line`, `line-retune`, `ltv-mpc`, `pure-pursuit`,
`tick-budget`, `perturbation-testing`, `respawn-economics`, `repeated-run-measurement`, `black-box-search`,
`held-out-track-validation`, `determinism-and-packaging`. No new API names: every callable is in
`baseline.yaml` `library_methods` and taught by Unit 12 or earlier (`concept-scan` enforces it).

## The reference submission
`agents/unit-13.py` = `agents/unit-11.py` with exactly these module constants changed: `LINE_CONTROL` (the 285
values of `monza-like`'s line, written with `repr`), `MU_G` = (5.38, 8.96, 9.12, 9.14, 9.70, 7.97),
`MU_FRACTION` = 0.64, `A_DEC` = 4.5, `A_ACC` = 5.0, `MPC_MIN_HORIZON` = 40; and a `#` header above the module
docstring (the docstring stays verbatim, as Unit 12's file did). `STEERING = "mpc"`, `MPC_HORIZON = 40`,
`MPC_BUDGET_MS = 5.0` as shipped.

## Gates (pinned from the probes; Phase A re-runs each with the shipped agent)
**Any failed gate assertion** stops Phase A and amends the plan. Times ±1 tick (0.05 s). Every race
`MPC_BUDGET_MS = None`, `monza-like`, 3 laps, cap 900 s, nominal noisy car unless said.
- **U13.0 the file:** `unit-13.py` differs from `unit-11.py` only in the six constants above (AST, docstring and
  imports equal); its `LINE_CONTROL` equals `_line_solver.solve_track(("monza-like", "global"))` to 1e-9 and has 285
  values; `MU_G` equals `MEASURED_MU_G["monza-like"]`; `MPC_MIN_HORIZON == MPC_HORIZON`.
- **U13.0b the policy cannot cut (race-free):** an agent loaded from `unit-13.py` with `MPC_BUDGET_MS = 0.0`
  written in: three `mpc_command` calls each count in `over_budget` and leave `horizon` at 40.
- **U13.1 the gate:** `unit-13.py` vs `unit-07.py`, seeds 0–4: both 5/5 clean; `noise_aware_better(unit-13,
  unit-07)`; medians 468.55 and 515.10 s.
- **U13.2 N/N on the test cars:** `unit-13.py` on k = 72–95 (race seed k mod 5): 24/24 clean (finished, 0
  collisions, max line error ≤ 2 m; p11: max 1.37 m, median 468.65 s). The validation sets (24–47, 48–71) are the
  pinned record, not re-raced.
- **U13.3 the margin was needed:** the one-knob margin M (0.64, 5.0, 5.0) on car 41 (race seed 1) is not clean
  (p3: 1 collision).
- **U13.4 pursuit loses the margin:** `unit-13.py` with `STEERING = "pursuit"` on car 34 (race seed 4) is not
  clean (p4: 1 collision, 5.34 m).
- **U13.5 section 0 is not grip-limited:** `unit-13.py` with `MU_G[0] = 12.0` on seed 0 has the same race
  time and max line error as `unit-13.py` (the U13.1 race); Phase A also compares the telemetry and reports it.
- **U13.6** `check_submission(agents/unit-13.py, track="monza-like")` passes (outside any pool; p99 ≤ 5 ms).

## Budgets
- **Routed pytest:** U13.1 10 races (5 MPC, 5 `unit-07.py`); U13.2 24 MPC; U13.3 1 (a crash race, about 15 s);
  U13.4 1 pursuit; U13.5 1; the line solve (about 2 s); U13.6 serial, about 10 s; the isolated Python 3.8 `check_submission` of `unit-13.py` (`AGENT_TRACKS`), about
  15 s. About 37 races, about 340 CPU-s, about 50–60 s pooled, plus about 25 s serial: about 1,115 s in all. The suite measured 1036–1038 s on `roar-012` against 18.5 min (1,110 s): **this plan
  raises the interim routed budget to 19.5 min (1,170 s; v4.12), the eighth raise**; over 1,170 s in Phase D stops
  and amends the plan. The tiering decision stays the first follow-up.
- **Notebooks** (lesson + solutions + milestone; the lab's analysis cells are seconds): ≤ **4 min** serial in total,
  each cell ≤ 120 s (target ≤ 60 s). Live races only where a race carries the story; every other number is the
  pinned record, stated as such:

  | notebook | live races | estimate |
  |---|---|---|
  | lesson | the hook: `unit-07.py` and `unit-13.py`, seed 0 (14 s); M and M2 on car 41 (about 25 s); pursuit on car 34 (4 s); the line solve (2 s) | about 50 s |
  | solutions | see the exercises (about 8 races) | about 90 s |
  | milestone | U13.1's 10 races; `check_submission` on `monza-like` | about 85 s |

  About 3.8 min. Book exec was about 45.9 of 50 CI-min after `roar-012`: **this plan raises the interim book-exec
  budget to 55 CI-min (v4.12), the fifth raise**, so Unit 13 fits with run-to-run margin and the capstone has room;
  the tiering decision stays the first follow-up.

## Phases
- **Phase A — agent + premise + registry** (Opus subagent).
  - `agents/unit-13.py` (written with `write_variant` from `unit-11.py`; constants with `repr`; header comment
    naming the unit, the five constants and why; the comments on `MU_G` and `LINE_CONTROL` rewritten for
    `monza-like`: the AST compare ignores comments, so Phase A reads them).
  - `tests/test_racekit_check_submission.py`: `AGENT_TRACKS` gains `"unit-13.py": "monza-like"` (the isolated
    Python 3.8 run of every agent would otherwise race it on `test-circuit` and fail at construction).
  - `tests/_race_day_premise.py` + `tests/test_racekit_unit13_premise.py` + a conftest fixture (pooled races, the
    existing pool runner); every gate U13.0–U13.6 (with U13.0b) confirmed and logged.
  - Registry: coverage-map entry `unit-13-race-day` (introduces nothing; practises the list above), manifest
    (`lab: true`), syllabus row 13 (no emoji); `qualification.md`'s `roar-013` row: `agents/unit-13.py`, timed,
    its SHA-256 at the Phase A commit (re-recorded if the file changes before merge), `PENDING (author)`; design
    013 v4.12 (§4.4 the family's validation and test cars, §6 row 13's gate text, §7.1 budgets, changelog).
    The `qualification.md` SHA-256 is computed with the shell's `sha256sum`, never in a notebook.
- **Phase B — content (Opus subagents).** Every notebook race uses a timing-off copy (`NO_TIMING`); the one timed
  run is the milestone's `check_submission`. Never race `test-circuit-seed2027` or `test-circuit-seed2028`; no
  `perturbation_factors` on k ≥ 1000; nothing from `racekit._truth`.
  - **Lesson, project-first:** the hook (race day: one file, one track, one car you have not met; the checklist;
    `unit-07.py` against the assembled `unit-13.py` live, seed 0); §1 assemble (each part and the unit that built
    it; section 0's lower bound and why it costs nothing: v_max from the line's curvature); §2 the known track and
    the unknown car (p2's crash-aware re-tune as a pinned table; the float tie as Unit 12's trap, caught); §3 the
    margin on every knob at its edge (M and M2 on car 41 live; p3's held-out table pinned; `unit-07.py` 12/24);
    §4 MPC or pursuit (p4 pinned; pursuit on car 34 live); §5 qualify (`check_submission` on its own track; the
    default track's refusal shown; the timing budget, timing off vs on); §6 package and submit (the checklist,
    the season's rules re-checked, what to re-check if the season changes; the interim CARLA check `PENDING`).
  - **Exercises (8 core + 1 Challenge),** each naming the concepts it practises:
    1. Section 0's lower bound (`cornering-speed-limit`, `speed-profile`): each section's largest curvature
       on the solved line and v_max = √(μg/κ) at the measured grip; which sections can the lower bound limit? No
       races. (It uses the measured μg; it identifies nothing, so it claims no `grip-identification` credit.)
    2. The line (`racing-line`, `line-retune`): solve `monza-like`'s line with the setup's Unit 9 solver; check the
       width constraint; compare with `unit-13.py`'s `LINE_CONTROL`. No races.
    3. The re-tune's record (`black-box-search`, `repeated-run-measurement`, `determinism-and-packaging`): replay
       p2's table (every setting's two per-replicate sums, pinned, and each not-clean race's reason) step by step
       with Unit 1's rule; find the float tie; decide it in whole ticks; name the incumbent and its edges. No races.
    4. The margin (`perturbation-testing`, `held-out-track-validation`, on held-out **cars**: the statement says the
       training/validation/test idea carries from tracks to cars): from the table, the margin setting under the
       one-knob reading (M) and the every-edge reading (M2); race both on car 41 (2 races); clean counts from p3's
       pinned table; which set is spent, and which is the test.
    5. MPC or pursuit (`ltv-mpc`, `pure-pursuit`): race `unit-13.py` and its pursuit copy on car 34 (2 races, about
       14 s); with p4's pinned nominal table, decide by Unit 10's order (time, then margin).
    6. Respawn economics (`respawn-economics`): the 24 per-car times of E, M, M2 and `unit-07.py` on cars 24–47
       are given (pinned from `u13/p3.pkl` and `p3c.pkl`; a race cut at 900 s counts at 900 s, the stated crash
       cost). Compute each expected race time (494.11, 476.24, 468.98, 707.62 s); here expected time also picks
       M2; find the crash rate at which E's per-race saving would pay for its crashes, and compare with Checkpoint
       B, where expected time picked the edge. No races.
    7. Timing (`tick-budget`): one `run_race` of `unit-13.py` with timing **on** and one with it off on seed 0
       (with `MPC_MIN_HORIZON = 40` the two are the same race; the exercise asks why),
       printing `step_ms` p50/p99 and whether the times match; nothing load-dependent is asserted or printed as a
       fixed claim (the solutions brief says so; 2 races, about 20 s; 1 lap if the budget is tight); then, from
       p9's pinned record, what Unit 10's halving policy would have done under load, and why the race-day file
       turns it into a counter.
    8. The packaging checklist (`determinism-and-packaging`): read `unit-13.py`'s text; check its constants
       against the pinned ones; `check_submission` on the default track (the refusal, shown) and the reasons a
       race-day file is checked on its own track; write the checklist as a list of strings. The timed
       `check_submission` run is the milestone's.
    9. **Challenge** (`stretch`): P, the margin only on the knob that failed: race it on car 41 and on seed 0 (2
       races); is P a finding or a fit to the held-out cars, and what would you need to race to tell?
  - **Milestone:** U13.0's file checks (constants, line, grip), U13.1's 10 races and the noise-aware verdict, and
    `check_submission(UNIT_13, track="monza-like")` PASS with p99 printed and ≤ 5 ms asserted.
  - **Lab** `labs/real-sim.ipynb` (lab-check rules: one parameters cell holds the only `.csv` path; analysis cells
    run on the sample CSV): race day on CARLA.
    - **The starting file.** The latest configuration that has raced clean on CARLA in an earlier lab, in this
      order: the Unit 10 lab's accepted configuration, else the Unit 8 lab's, else the Unit 7 lab's, else the
      Unit 5 or Unit 1 lab file. Nothing that has not raced clean on CARLA is ever the race-day file.
    - **Assemble** that file's own constants (line, `MU_G`, `MAX_STEER`, fraction, steering choice) and put one grid
      step of margin on **every knob that reached an edge on CARLA** (a knob never pushed to a not-clean setting
      gets none). If the assembled file differs from the starting file, it must be **accepted** first: clean on
      two practice launches (the earlier labs' rule); if either is not clean, the starting file is the race-day
      file. The timing step runs off CARLA first (the Unit 10 lab's timing copy for a file with a Monza line).
    - **The checklist** (one file, numpy only, Python 3.8, the unmodified runner files, the season's
      `instruction.txt` / `requirements.txt` wording read from the current page, the file's SHA-256 from the
      operating system's tool, `certutil -hashfile submission.py SHA256` in a `no-exec` cell as the Unit 10 lab
      does, written down; no hashing in an executed cell).
    - **The race-day record: five consecutive official-runner launches of that one file, none discarded or
      restarted.** A host failure (the CARLA server exits, or the agent never receives its first tick) is not an
      agent failure: it is recorded, the five-launch block restarts, and both blocks stay in the record (design
      §7.3).
    - **Analysis, per launch.** Point `ROAR_LAB_CSV` at each launch's recording in turn and run the analysis cell
      (the clean rule on that recording, as the Unit 10 lab); type each launch's result into `LAUNCHES`, a hand-typed
      list of (time, runner collisions, finished, max error, clean, host failure) in a plain cell, as the Unit 10
      lab's run log does. A summary cell computes the clean count, the median and spread of the clean launches,
      and Unit 1's comparison with the student's Unit 7 lab record (`UNIT_7_TIMES`, typed in); with a host
      failure it groups `LAUNCHES` into five-launch blocks, reports the last complete block and keeps both; it
      executes clean on empty lists against the fixture. The lab and the teacher notes say not to commit the
      edited lab notebook: the typed-in results are the student's data. Results stay on the student's machine (the public-repo warning).
  - Solutions in a **separate fresh** Opus session.
- **Phase C — teacher notes** (inline): goals, two or three sittings, the lab sitting, common mistakes, prompts,
  differentiation.
- **Phase D — verification:** `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN; budgets measured (the routed
  time from the log; the notebooks with nbclient serially).

## Out of scope
- The capstone, the site flag, the final qualification and the publication flag (`roar-014`).
- Any racekit change; any new concept or API name.
- The author's CARLA runs (the interim check is recorded `PENDING (author)`; it is a named risk in `roar-014`'s
  `## Plan Review`, design §7.3, and in the follow-up list).

## Plan Review

### Round 1 (v1 @ 554c035)

Verdicts: [self] APPROVE WITH NITS (S1 below); [sol] REJECT (B1, B2, S3); [fable] APPROVE WITH NITS (S1–S7, N1–N6).

- [FIXED v2] [sol] B1: the N/N gate raced timing off only, while the file ships `MPC_BUDGET_MS = 5.0`, whose load-driven horizon cuts change the steering. The policy only halves the horizon (40 → 20 → 10) and never restores it, so p9 brackets it deterministically: horizon 20, and `MPC_BUDGET_MS = 0.0` (10 from the third tick), 106/106 clean on nominal, validation and test cars. New gate U13.2b: the test cars at budget 0. The lesson says the bracket covers each regime, not every switching time.
- [FIXED v2] [sol] B2 / [fable] S6: the lab now names the starting file (the latest configuration that raced clean on CARLA, in a fixed order down to the Unit 1 lab), the acceptance of an assembled file (two clean practice launches, else the starting file races), per-launch analysis (each recording through the clean-rule cell, results typed into `LAUNCHES`), the summary cell under lab-check's one-CSV rule, and design §7.3's host-failure rule.
- [FIXED v2] [sol] S3: Exercise 6 is given the 24 per-car times of E, M, M2 and `unit-07.py` (a race cut at 900 s counts at 900 s, stated); the expected times are pinned (494.11, 476.24, 468.98, 707.62 s), and here expected time also picks M2, which the exercise contrasts with Checkpoint B.
- [FIXED v2] [self] S1: the held-out cars 24–47 decided between readings of the rule and showed P's 2 s, so they are now a validation set; p8 raced M2 once on fresh, pre-registered family cars 48–71 (24/24 clean), the unit's test cars.
- [FIXED v2] [fable] S1: Phase A adds `"unit-13.py": "monza-like"` to `AGENT_TRACKS` in `test_racekit_check_submission.py`.
- [FIXED v2] [fable] S2: 0.68's failures are stated per car (car 8 collides, car 16 2.01 m at `A_ACC` 4.0; p10 at 5.0); the pinned table carries each not-clean race's reason.
- [FIXED v2] [fable] S3: "no edge in the box" is now "no edge found (6.0 clean; 6.5 and 7.0 not raced)"; p10 confirms both edges at the shipped `A_ACC` 5.0.
- [FIXED v2] [fable] S4: the per-replicate pair sums are pinned (the tie's exact float gain and spread in the plan).
- [FIXED v2] [fable] S5: Exercise 1 no longer claims `grip-identification`; the unit practises `cornering-speed-limit` and `speed-profile` there, and Exercise 4 states the tracks-to-cars reframe.
- [FIXED v2] [fable] S7: Deviations say why `checkpoint-b.py` is not the race-day agent.
- [FIXED v2] [fable] N1 (E′ row), N2 (p3's pre-declared job), N3 (comments rewritten in Phase A), N5 (the PENDING check as a named risk for `roar-014`), N6 (print-only timing in Exercise 7).
- [WONTFIX] [fable] N4: budgets confirmed as stated (now about 1,115 s against 1,170 s with U13.2b).

### Round 2 (v2 @ e3a190b)

Verdicts: [self] APPROVE; [sol] REJECT (B1, B2, S3); [fable] APPROVE WITH NITS (S1–S5, N1–N4). [fable] verified every round-1 fold and recomputed the expected times from the pickles.

- [FIXED v3] [sol] B1: a load spike can cut the horizon at any tick, and no finite bracket covers every switching time. The race-day file now sets `MPC_MIN_HORIZON = 40`, so the policy only counts slow calls (U13.0b proves it race-free) and every gated race is the shipped race; the timing check is `check_submission` on the race machine before the race. U13.2b (budget 0) is dropped; p9 stays as recorded evidence of what the halving policy would have done.
- [FIXED v3] [sol] B2 / [fable] S1: cars 48–71 were raced again in p9, so they are validation cars (the pre-registration's one deviation, recorded). Fresh cars 72–95, pre-registered after the shipped file was fixed, were raced once with the literal shipped file, timing on (p11: 24/24 clean); U13.2 gates them. The validation sets are the pinned record.
- [FIXED v3] [sol] S3: U13.0 compares with `_line_solver.solve_track(("monza-like", "global"))`.
- [FIXED v3] [fable] S2: the routed estimate includes the isolated Python 3.8 run (about 15 s): about 1,115 s with U13.2b gone.
- [FIXED v3] [fable] S3: v4.12 amends design §4.4 (the family's validation and test cars).
- [FIXED v3] [fable] S4: SHA-256 comes from the operating system's tool (`certutil`, `sha256sum`), in a `no-exec` cell or the shell, never in an executed cell.
- [FIXED v3] [fable] S5: moot (U13.2b dropped); U13.0b reads `horizon` and `over_budget` from the agent directly.
- [FIXED v3] [fable] N1 (docstring verbatim, `#` header), N2 (no margin for a knob never pushed to a not-clean setting, stated), N3 (five-launch blocks in the lab summary), N4 (do not commit the edited lab notebook).
