# Plan roar-011 — Checkpoint B: a full agent on a track and a car it has never met

**Design:** `docs/designs/013-roar-book.md` **v4.9** (§4.3 the seeded tracks, §6 CP-B, §7.1).
**Book:** `roar`. **Autopilot** per AGENTS.md.
**Base:** branches from `main` after `roar-010` merges (#165, f62130c).
**v5.1** (CONSENSUS) folds round 5's nits (`p7` is proxy evidence; the CPU arithmetic; CPB.7 in Phase A).
**v5** folds round 4 ([sol] B and [fable] S1 the endpoints do not bound a mid-race horizon switch: CPB.4c races the frozen file as shipped, serially (`p7`); CPB.4b reworded as the budget policy's end state; N the race-count arithmetic; [fable] N2).
**v4** folds round 3 ([sol] B the pinned races ran a timing-off copy, not the frozen file: a worst-case-budget gate CPB.4b (`p6`) covers the shipped file; S `check_submission` races the default kinematic car; N five scored races; [fable] N1–N4).
**v3** folds round 2 ([sol] B and [fable] S1 the submission check raced the race-day track before race day; [fable] S2 the seal check's mechanics, S3 timing off for the pinned races, N1–N3).
**v2** folds plan-review round 1 ([sol] REJECT: B the student's own agent may find another edge, S the sealed-car loophole, S every probe's outcome, N Question 3 a lookup; [fable] APPROVE WITH NITS: S1 Question 2 named 0.48, S2 = [sol] N, S3 the race-day record must not be in the notebook, S4 = [sol] S, S5 CPB.4 a bound not a pin, S6 the book-exec raise, N1–N6).

## Scope
- Checkpoint B `roar/checkpoints/checkpoint-02-part-2/`: `checkpoint.ipynb` (the brief and the questions, no
  solutions, no outputs), `solutions.ipynb`, `teacher-notes.md`, `manifest.yaml`.
  It is **strict**: no borrowed tools, every task draws only on Units 1–11 concepts, and it introduces nothing.
- **Generator:** one more seeded variant, `test-circuit-seed2027`, the **race-day track** (the seed was fixed
  before it was probed, as 2026 was for Checkpoint A). `load_track` already loads it by name; `racekit` does not
  change.
- Reference submission `agents/checkpoint-b.py`: `agents/unit-11.py` with the race-day track's line
  (`LINE_CONTROL`, solved by Unit 9's method), its measured grip (`MU_G`, Unit 8's probes) and
  `MU_FRACTION = 0.48` (the margin rule on the track × car family, below), and a header comment saying why.
- A routed premise test for the gates; registry, syllabus and design entries.

## The idea, and why the checkpoint has one
Design §6: "a full agent under parameter uncertainty; completes hidden perturbed races, timed".
Unit 11 left two findings open: a margin bought on one track did not carry to another (`test-circuit-seed2026`),
and the fraction it shipped was the one with the shortest **expected race time** on its training family.
Checkpoint B puts both to the test on a track and on cars the student has never raced:
- **The race-day track** `test-circuit-seed2027`: the student measures it (Unit 8's grip probes, with the
  nominal carla-like car) and solves its line (Unit 9). Racing it is allowed once, on race day.
- **The race-day cars** are five members of the perturbed family whose factors are **sealed**: `perturb=k` for
  k = 1000–1004 (race seed k mod 5). The seal is an **honour rule**, stated as such: the sealed cars are built only
  in the race-day cell and never inspected by any route (no `perturbation_factors`, no attribute of a built car, no
  re-deriving the seeded draw from the published algorithm, no race before race day). The solutions keep it, and
  the routed test checks that `perturb=` with k ≥ 1000 appears in exactly one code cell of `solutions.ipynb` and
  of `checkpoint.ipynb` (the race-day cell) ([sol] S, [fable] S4).
- **Tuning** uses the track × car family: the five training tracks (`test-circuit`, `-seed1` … `-seed4`, each with
  its own line and measured grip) × the training cars (k = 0–23).

The probe shows the two Unit 11 rules **disagree here**, and race day settles it:
- **Expected race time** over the 120 family races is lowest at **0.54** (279.95 s; every race finishes, thanks to
  the fallback), as in Unit 11.
- **The clean rule and the margin rule** (Units 7 and 11): 0.52 is not clean on the family (`test-circuit-seed2`
  crashes two cars), 0.50 is clean on all 120, so the margin rule gives **0.48**.
- **Race day:** at 0.48 all five hidden cars are clean (median 283.90 s); at 0.54 four of five crash once (each
  finishes, after the fallback, in 384.65–477.00 s; mean 382.82 s); Unit 10's agent at 0.54, with no fallback,
  never finishes three of the five.
The lesson: the expected-time rule trusts the family's crash rate, and a new track is not in the family.
The margin is the insurance against what the family did not show; the fallback turns a crash into a slow finish
instead of a DNF. Both are Unit 11 ideas; the checkpoint makes the student choose between them before the race and
justify the choice with evidence. Graded on the evidence and the reasoning; the race is pass/fail.

## Probe evidence (`p1`–`p5`, scratchpad `cpb/`; `carla_like(noise=True, perturb=k)`, MPC budget off (`MPC_BUDGET_MS = None`) in every probe, 700 s cap)
- **`p1` the track** (`gen_tracks.seeded_track(2027)`): length 2631.2 m, 1316 waypoints, half-width 5.41–6.56 m,
  tightest radius 19.3 m, continuous curvature, 0 self-intersections; builds in 0.01 s. Its smoothest line
  (QR + `lsq_linear`, Unit 9) solves in 0.1 s (131 control values).
- **`p2` the grip probes** (Unit 8's rule: `agents/unit-07.py`, A_LAT 3.5, one section's knob at 3.5, one lap, race
  seed 0, 300 s cap, the 99th percentile of |a|): on `test-circuit-seed2026` the rule reproduces the pinned
  `MEASURED_MU_G` exactly. On `test-circuit-seed2027`: **(9.10, 9.55, 7.79, 9.35, 9.00, 7.76)** m/s².
  Section 0's probe finished the lap clean (109.40 s, 0 collisions): it never slid, so 9.10 is a **lower bound**,
  the case Unit 8 taught (`monza-like`'s section 0), and the planner uses it as measured.
- **`p3` the family sweep** (`agents/unit-11.py`, each track's line and measured grip, `test-circuit` as shipped;
  24 training cars × 5 training tracks, race seed k mod 5; 480 races, 2,907 CPU-s, 427 s on 8 workers):

  | fraction | clean / 120 | not clean | mean (all finish) | median |
  |---|---|---|---|---|
  | 0.56 | 110 | `test-circuit` cars 8, 9; `-seed2` cars 1, 8, 9, 10, 13, 16, 17, 20 | 286.95 | 273.95 |
  | 0.54 | 118 | `-seed2` cars 13, 16 | **279.95** | 276.30 |
  | 0.52 | 118 | `-seed2` cars 9, 16 | 282.57 | 278.90 |
  | 0.50 | **120** | — | 282.21 | 281.60 |
  | 0.48 (`p5`) | 120 | — | 285.11 | 284.48 |

  Every not-clean race crashes once and finishes after the fallback. Max line error on clean races ≤ 1.77 m.
- **`p4` race day** (`test-circuit-seed2027`, its `p1` line and `p2` grip; hidden cars k = 1000–1004, race seed
  k mod 5; and, as record only, k = 1005–1023):

  | agent, fraction | hidden: clean | hidden: race times (s) | mean | k = 1000–1023: clean |
  |---|---|---|---|---|
  | Unit 11, 0.58 | 0/5 | 316.75, 378.70, 381.00, 379.65, 379.45 | 367.11 | 9/24 |
  | Unit 11, 0.56 | 1/5 | 382.05, 273.10, 381.45, 381.80, 381.50 | 359.98 | 11/24 |
  | Unit 11, 0.54 | 1/5 | 390.35, 275.45, 386.65, 384.65, 477.00 | 382.82 | 14/24 |
  | Unit 11, 0.52 | 1/5 | 480.40, 278.10, 389.90, 390.40, 486.50 | 405.06 | 17/24 |
  | Unit 11, 0.50 | 3/5 | 281.10, 280.80, 280.55, 486.40, 394.95 | 344.76 | 20/24 |
  | **Unit 11, 0.48** | **5/5** | 283.95, 283.90, 283.60, 283.75, 283.95 (median **283.90**) | 283.83 | 23/24 |
  | Unit 10, 0.54 | 1/5 | 379.85, 275.45, DNF, DNF, DNF (5–6 collisions each) | — | 14/24 (6 DNF) |
  | Unit 10, 0.48 | 5/5 | as Unit 11 at 0.48 (no respawn) | 283.83 | 23/24 |

  Every Unit 11 race finishes. The nominal car (no perturbation) at 0.54 is clean on seeds 0–4 (275.00–275.25 s):
  the race-day risk comes from the cars, not from the track alone. One wide-record car (k = 1005) crashes once even
  at 0.48: the margin makes crashes rarer, not impossible (said in the solutions).
- **`p5` the small protocol** (what the checkpoint asks a student to race): the three lowest-grip training cars
  (16, 18, 8, Unit 11's `grip_order[:3]`) × the five training tracks, race seed **0**: 0.56 not clean (`-seed2` cars
  16, 18), 0.54 not clean (`-seed2` cars 16, 8), 0.52 not clean (`-seed2` car 16), 0.50 and 0.48 clean on all 15.
  It finds the same edge (0.50) and the same margin value (0.48) as the full family.

## Gates (pinned from the probes; any failed assertion stops Phase A and amends the plan)
Only descriptive figures quoted in prose (a median, a mean) may be corrected in the report.
- **CPB.1 the track:** the generator writes `test-circuit-seed2027`, byte-stable (the existing checksum contract),
  with the stats above (length 2631.2 ± 0.1 m, 1316 waypoints, minimum half-width 5.41 ± 0.01 m, tightest radius
  19.3 ± 0.1 m), continuous curvature, 0 self-intersections, half-widths in [5.0, 8.0] m. The stem is pinned
  literally (the hidden grip is keyed to the name).
- **CPB.2 the measurement:** the six Unit 8 probes on `test-circuit-seed2027` give (9.10, 9.55, 7.79, 9.35, 9.00,
  7.76), equal after rounding to 0.01 (as `_line_premise` rounds); each probe's outcome is asserted: section 0's
  finishes the lap with 0 collisions (it never slid: a lower bound), sections 1–5 do not finish and have at least
  one collision (probe: 12, 7, 5, 3, 3), so their estimates come from a car that slid ([sol] S).
- **CPB.3 the family edge** (the small protocol, race seed 0, `agents/unit-11.py` with each track's line and
  measured grip): the protocol's car order, the three lowest-grip training cars by `perturbation_factors` ascending,
  is asserted to be (16, 18, 8); at 0.54 and at 0.52 the first 7 races in protocol order are raced and the 7th
  (`test-circuit-seed2`, car 16) is the first that is not clean; at 0.50 and 0.48 all 15 are clean. So the margin
  rule gives 0.48. At 0.52 the edge rests on that single race (the full-family record shows two); the teacher notes
  say so ([fable] N1, N2).
- **CPB.4 race day** (`agents/checkpoint-b.py`, hidden cars k = 1000–1004, race seed k mod 5, 700 s cap): all five
  **clean**, median ≤ the **target 300 s**; pinned to the probe: the five times 283.95, 283.90, 283.60, 283.75,
  283.95 s to a tick (0.05 s), median 283.90 s, max line error ≤ 1.5 m (probe 1.33 m) ([fable] S5). These races use
  the timing-off copy (reproducibility).
- **CPB.4b the budget policy's end state** (supporting evidence, [sol] r3 B, [fable] r4 S1): the frozen file with
  `MPC_BUDGET_MS = 0.0` (every `mpc()` call over budget, so the horizon is 10 ticks from the third tick on, as
  U10.7), the same five sealed cars, pooled: all five clean, median ≤ 300 s; pinned to the probe `p6`: 284.35, 284.35,
  284.00, 284.20, 284.55 s to a tick, median 284.35 s, max line error ≤ 1.7 m (probe 1.52 m). It shows the
  policy's other end state is clean too; it does **not** bound a race that switches horizon part-way.
- **CPB.4c the frozen file as shipped** ([sol] r4 B): `agents/checkpoint-b.py` itself (`MPC_BUDGET_MS = 5.0`),
  the five sealed cars, raced **serially in the test process** after the pool has finished (as `check_submission`
  is): all five clean, median ≤ 300 s, and the number of horizon cuts (the agent's printed lines) recorded. With no
  cut the race is the timing-off race, so the five times must equal CPB.4's to a tick; with a cut the bar alone is
  asserted and the cut count is reported. Probe `p7` (proxy evidence: the Unit 11 stand-in with the three constants, `MPC_BUDGET_MS` untouched; load average 2.8): 0 cuts, 283.95, 283.90, 283.60, 283.75,
  283.95 s, identical to CPB.4. About 33 CPU-s serial.
- **CPB.5 the contrast** (same five races): `agents/unit-11.py` at 0.54 with the race-day line and grip finishes all
  five and is not clean on at least three; `agents/unit-10.py` at 0.54 with the same constants does not finish at
  least one.
- **CPB.6:** `check_submission(agents/checkpoint-b.py, track="test-circuit-seed2027")` passes (outside any pool).
- **CPB.7 the reference is Unit 11 plus three constants:** the module-level assignments of `agents/checkpoint-b.py`
  and `agents/unit-11.py` (parsed with `ast`) differ only in `MU_FRACTION`, `MU_G` and `LINE_CONTROL` (131 values
  against 133), and the bodies of every function and class are identical ([fable] N3).
- **CPB.8 the seal:** the race-day cell of both `checkpoint.ipynb` and `solutions.ipynb` is cell-tagged `race-day`
  and carries the scaffold line `SEALED_CARS = range(1000, 1005)`; in each notebook that tagged cell exists exactly
  once, and no other code cell contains an integer literal from 1000 to 1005 or `SEALED_CARS` (each code cell parsed with
  `ast`, walking `ast.Constant` ints and `ast.Name` ids; a cell that does not parse fails the test; a float, string or computed 1000 is a known gap, named in the
  test's docstring) ([fable] r3 N4, r4 N2); no cell calls
  `perturbation_factors` with `SEALED_CARS`, one of its members or such a literal ([fable] r2 S2).
- **Timing off for the pinned races:** every CPB.3–CPB.5 race runs a `MPC_BUDGET_MS = None` variant (as
  `_robust_premise` does), and so do the solutions' Question 4 and 5 sealed races, so the tick-level pins reproduce
  on a loaded machine; CPB.4b runs the worst budget; CPB.4c, CPB.6 and Question 5's `check_submission` run the file
  as shipped
  ([fable] r2 S3, r3 N3).
- **Where each gate is asserted.**
  - CPB.1 in `roar/data/tests/test_gen_tracks.py` (the driver test's output list, the length-bounds dict and
    `SEEDED_STATS` gain the name; `gen_tracks.py`'s docstring names the track) ([fable] N4).
  - CPB.2–CPB.8 in the routed `tests/test_racekit_checkpoint_b.py` (helper `tests/_checkpoint_b_premise.py`,
    a conftest fixture `checkpoint_b_premise`). Jobs: 6 probes; CPB.3 15 + 15 (0.50, 0.48) + 7 + 7 (0.54 and 0.52,
    the first 7 in protocol order: `test-circuit`, `-seed1`, then `-seed2`'s first car, enough to include the
    not-clean race) = 44; CPB.4 5; CPB.4b 5; CPB.5 10. **70 pooled races** plus CPB.4c's 5 serial, about 70 × 6.1 s + the Unit 10 DNFs (3 × 700 s races,
    about 2.5 races each) + CPB.4c's 33 s ≈ 8.5 CPU-min (8 pooled + 0.5 serial), about 1 min pooled on 8 workers plus
    33 s serial, plus the six line solves (under 1 s).
  - The **target 300 s** sits above the clean race-day value (283.90 s) and below every fraction that is not clean
    on race day (their means 344.76–405.06 s); it is a racekit target on this track and has nothing to do with the
    book's 329 s CARLA bar on Monza (the teacher notes say so).
  - The expected-time table (`p3`) is **probe record** (480 races are too many for the suite); wherever it is
    quoted it is labelled "the probe record of plan `roar-011`". The checkpoint gives it as data.

## The checkpoint (questions; the brief opens with the project)
**Brief:** "Race day. A track you have never driven, `test-circuit-seed2027`, and a car you have never met: five
cars of the perturbed family, sealed (`perturb=1000` … `1004`). You may measure the track with the carla-like car you
know, solve its line, and tune on the five training tracks with the training cars. You may race the race-day track
once: the submission check, then five scored races, after every choice is frozen." ([sol] r3 N) The rules: the submission is **your own Unit 11 submission**
(`agents/unit-11.py` is the stand-in; the solutions use it); only `MU_FRACTION`, `LINE_CONTROL` and `MU_G` change;
the seal is an honour rule (above); no race on `test-circuit-seed2027` except the six probes and race day, and race
day starts with the frozen file's `check_submission` (racekit's default kinematic car) before the five sealed races.
Races in the notebook use a timing-off copy of the file (`write_variant(..., MPC_BUDGET_MS=None)`, as Unit 11's
solutions do), so the numbers reproduce on any machine; the frozen file itself keeps `MPC_BUDGET_MS = 5.0` and is
what `check_submission` validates ([fable] r3 N1).
**The bar:** all five race-day races clean (finished, 0 collisions, max line error ≤ 2 m), median ≤ 300 s.
1. **Measure the track.** Run Unit 8's six grip probes on `test-circuit-seed2027` (the given probe settings); from
   each probe's outcome (finished or not, collisions) and its telemetry compute each section's μg, and say which
   estimate is a lower bound and why.
2. **Solve its line and plan the lap.** The smoothest line (Unit 9); the planned lap time with the speed profile
   (Unit 7) at Unit 11's shipped 0.54 on the race-day track, compared with `test-circuit`'s. (Question 5 plans it
   again at the fraction you freeze.) ([fable] S1)
3. **Two rules, one record.** The given table is the **reference agent's** record on the track × car family (the
   probe record of plan `roar-011`; `agents/unit-11.py`, 24 cars × 5 tracks per fraction): per fraction, the clean
   count, the clean races' mean and the time of every not-clean race (each crashed once and finished after the
   fallback). Compute each fraction's expected race time (Unit 11 §2) and find the fraction it picks; apply the
   clean rule and the margin rule to the same table. Then, before racing anything: given the bar, which rule fits,
   and why? ([sol] N, [fable] S2) The student data:

   | fraction | clean / 120 | clean mean (s) | not-clean races (track, car, time s) |
   |---|---|---|---|
   | 0.56 | 110 | 274.50 | `test-circuit` 8 484.45, 9 391.90; `-seed2` 1 498.60, 8 407.25, 9 319.00, 10 496.30, 13 499.30, 16 316.95, 17 500.10, 20 324.75 |
   | 0.54 | 118 | 276.94 | `-seed2` 13 501.00, 16 413.40 |
   | 0.52 | 118 | 279.52 | `-seed2` 9 508.35, 16 416.60 |
   | 0.50 | 120 | 282.21 | — |
   | 0.48 | 120 | 285.11 | — |

   (Expected times 286.95, **279.95**, 282.57, 282.21, 285.11 s: computed in the solutions, never printed in the
   checkpoint.)
4. **Tune your agent on the family.** The small protocol, on **your** agent: the three lowest-grip training cars
   (from `perturbation_factors`) × the five training tracks (each with its line and measured grip), race seed 0,
   each fraction stopped at its first race that is not clean. Start at 0.54. **Every outcome has a defined path**
   ([sol] B):
   - 0.54 not clean: go down by 0.02 until a fraction is clean on all 15 (the edge); ship one step below it.
   - 0.54 clean on all 15: go up by 0.02 until a fraction is not clean; the edge is the highest clean one; ship
     one step below it. Clean on all 15 at 0.60: the edge is 0.60, ship 0.58 ([fable] N3).
   - nothing clean down to 0.40: ship 0.40 and say so; the race is still raced and the write-up carries the grade.

   Report the edge and the shipped value, and freeze it. The stand-in finds
   0.50 and ships 0.48; a student's agent may not, and that is not an error.
5. **Race day.** Plan the lap at your frozen fraction (Question 2's function); run `check_submission` on the frozen
   file on the race-day track (racekit's default kinematic car, with the timing check; it must pass before any
   sealed car races there) ([sol] r3 S, [fable] r3 N2) ([sol] r2 B,
   [fable] r2 S1); then race the five sealed cars once.
   Report clean, the median and the mean against the bar, and compare with the plan.
6. **What bought what.** With the race-day record your teacher hands out after Question 5 (the `p4` table, kept in
   the teacher notes and the solutions, **never in `checkpoint.ipynb`**) ([fable] S3): what the margin bought on race
   day; what the fallback bought at 0.54 (Unit 10 against Unit 11), and why it did not make 0.54 a good choice; and
   why the expected time over the family misjudged race day.

**Grading** (teacher notes): the race is pass/fail on the bar; the written answers to Questions 1, 3 and 6 and the
evidence of Question 4 carry the rest. A student whose own agent misses the bar after following Question 4 honestly
can still earn full marks on the write-up, which must say what their record showed; the reference's numbers are
public in this plan, so the grade never rests on the final number alone.

## Budgets
- Routed pytest: measured 13.7 min after `roar-010`; this plan adds about 1.5–2 min (1 min pooled, 33 s serial, the line solves). **≤ 15.5 min** (v4.10, interim;
  over means stop and amend). The follow-up on the routed-suite budget (a slow tier) is re-stated.
- Checkpoint notebooks: the solutions ≤ **5 min** serial, each cell ≤ 120 s: 6 probes (about 20 s), the line solve,
  Question 4's protocol (7 + 7 + 15 = 29 races, about 180 s, split one fraction per cell and 0.50 in two cells), race
  day (`check_submission`, about 6 s, then 5 races, about 35 s). The checkpoint notebook itself has no outputs and no races.
- Book exec total: about 35.8 CI-min after `roar-010` + about 4.5 = about 40.3, **over** v4.8's 40.
  Design v4.10 raises the interim book-exec target to **45 CI-min** (the third book-exec raise, after 15 → 30 → 40),
  enough for this plan with headroom; Units 12–13 and the capstone (about 3–4.5 CI-min each) cannot all fit, so the
  author's tiering decision is due at Unit 12 and stays in the held follow-up list ([fable] S6).

## Phases
- **Phase A — track, reference, premise, registry.** (Opus subagent for code; registry inline.)
  - `roar/data/gen_tracks.py` `SEEDED_TRACKS` gains `("test-circuit", 2027)`; `generate.py` writes it (checksums);
    `test_gen_tracks.py` covers it (CPB.1); `conftest`'s missing-track check names it.
  - `agents/checkpoint-b.py`; `tests/_checkpoint_b_premise.py`, `tests/test_racekit_checkpoint_b.py`, the conftest
    fixture; CPB.2–CPB.7 confirmed and logged (CPB.8 in Phase B with the notebooks).
  - `coverage-map.yaml`: `checkpoint-02-part-2`, `kind: checkpoint`, `introduces: []`, `requires` all Unit 1–11
    concepts, `practices` the ones the questions use (grip-identification, racing-line, speed-profile,
    perturbation-testing, respawn-economics, failure-fallback, repeated-run-measurement); manifest mirrors it;
    `syllabus.md` row (no emoji).
  - Design 013 **v4.10**: §4.3 names `test-circuit-seed2027` as Checkpoint B's race-day track; §6 CP-B's gate gets the
    bar (five sealed cars, clean, median ≤ 300 s, tuned on the track × car family only); §7.1 the budgets; changelog.
- **Phase B — statements (Opus) and solutions (Opus, a separate fresh session).** The statements never quote a
  `_truth` value; the sealed cars' factors are never computed in either notebook; the race-day record (`p4`) and
  the expected times of Question 3 are never in `checkpoint.ipynb` (the teacher notes carry the `p4` handout).
- **Phase C — teacher notes** (inline): goals, a 60–90 min sitting plan (Question 4 is the long part; the short form
  races only `-seed2`, the family's hardest track, reports those races and does not claim the protocol's edge,
  [fable] r2 N2), grading (the race is pass/fail; the written answers to 1, 3 and 6
  and the evidence of 4 carry the rest ([fable] r2 N1); since this plan's table is public, the grade rests on the evidence and the reasoning, never on
  the final number alone), the 300 s target vs the 329 s CARLA bar, common mistakes (shipping the expected-time
  minimum against a clean bar; racing the race-day track before freezing; inspecting the sealed cars; reading a
  lower bound as a measurement); the race-day record (`p4`) as the Question 6 handout; the 0.52 edge resting on one
  race; `agents/checkpoint-b.py` answers Questions 1–2 and 4 for anyone who opens it (a known give-away, as
  `checkpoint-a.py` was) ([fable] N2, N5).
- **Phase D — verification:** `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN; budgets measured.

## Out of scope
- Any `racekit` library change; any change to Units 1–11 content or agents.
- Per-section knobs on the family; online identification; a CARLA lab (CP-B has none in the design).
- Unit 12's held-out-track and overfitting vocabulary (the checkpoint uses Unit 7's and Unit 11's rules only).

## Plan Review

### Round 1 (v1 @ 5a9f456)
Verdicts: [self] APPROVE WITH NITS (CPB.4 is not knife-edge on the line error: 1.10–1.33 m against 2 m); [sol] REJECT; [fable] APPROVE WITH NITS.
- [sol] B (the student's own agent): Question 4 gives every protocol outcome a defined path (down, up to 0.60, or no edge down to 0.40); Question 3 is about the reference's record; grading for a student whose agent misses the bar. Folded.
- [sol] S / [fable] S4 (the seal): an honour rule over every route; CPB.8 checks the race-day cell is the only one that builds a sealed car. Folded.
- [sol] S (probe outcomes): CPB.2 asserts every probe's outcome. Folded.
- [sol] N / [fable] S2 (Question 3 a lookup): the table gives clean means and not-clean times. Folded.
- [fable] S1 (Question 2 named 0.48): it plans at 0.54; Question 5 plans the frozen value. Folded.
- [fable] S3 (the race-day record in the notebook): teacher-notes handout only. Folded.
- [fable] S5 (CPB.4 a bound): the five times pinned to a tick. Folded.
- [fable] S6 (the book-exec raise): 45 CI-min, the third book-exec raise; the tiering decision due at Unit 12, held in the follow-up list (the autopilot directive holds questions to the end). Folded.
- [fable] N1–N6: CPB.3 wording and car order; the one-race edge; CPB.7 (AST comparison); the generator test's bounds dict and docstring; the known give-away; rounding. Folded.

### Round 2 (v2 @ d856cd4)
Verdicts: [self] APPROVE WITH NITS; [sol] REJECT (one B); [fable] APPROVE WITH NITS (re-derived every pin from the probe pickles and re-ran the six grip probes: all match).
- [sol] B / [fable] S1: Question 4's `check_submission` raced the race-day track before race day. It moves to Question 5, the first step of race day after the freeze (the nominal car); the rules say so. (A training track cannot host the check: the frozen file's line is solved for `test-circuit-seed2027`, and the agent refuses another track's line.) Folded.
- [fable] S2: CPB.8's mechanics pinned (a `race-day` cell tag, the `SEALED_CARS = range(1000, 1005)` scaffold, the literal scan on both notebooks). Folded.
- [fable] S3: the pinned races and the solutions' races run with `MPC_BUDGET_MS = None`; CPB.6 runs the shipped file. Folded.
- [fable] N1–N3: grading text aligned; the short form does not claim the edge; the upward path's cap outcome. Folded.

### Round 3 (v3 @ 07a2073)
Verdicts: [self] APPROVE WITH NITS; [sol] REJECT (one B); [fable] APPROVE WITH NITS.
- [sol] B: the pinned race-day races ran a timing-off copy, not the frozen file. Probe `p6`: the frozen file with every `mpc()` call over budget (`MPC_BUDGET_MS = 0.0`, the horizon drops to 10) is clean on all five sealed cars, median 284.35 s. New gate CPB.4b; since the policy only shortens the horizon, the shipped file's race is bracketed by CPB.4 and CPB.4b. Folded.
- [sol] S: `check_submission` races racekit's default kinematic car, not a nominal carla-like car; the wording says so. Folded.
- [sol] N: "five races" now "the submission check, then five scored races". Folded.
- [fable] N1–N4: the timing-off copy named in the rules; "before any sealed car races there"; the gate names which runs keep timing; CPB.8 scans with `ast`. Folded.

### Round 4 (v4 @ 24a1bbc)
Verdicts: [self] APPROVE WITH NITS; [sol] REJECT (one B); [fable] APPROVE WITH NITS.
- [sol] B / [fable] S1: the two end states (CPB.4, CPB.4b) do not bound a race whose horizon switches part-way. New gate CPB.4c races the frozen file as shipped (5.0 ms), serially after the pool, on the five sealed cars; probe `p7`: 0 horizon cuts, identical to CPB.4 to the tick. CPB.4b is reworded as supporting evidence about the policy's end state, with no bracketing claim. Folded.
- [sol] N / [fable] N1: the race count's arithmetic (70 pooled, 5 serial). Folded.
- [fable] N2: the CPB.8 scan's known gap named in the test docstring. Folded.

### Round 5 (v5 @ f3a5b0d): CONSENSUS
Verdicts: [self] APPROVE; [sol] APPROVE WITH NITS; [fable] APPROVE WITH NITS (checked CPB.4c's mechanics against the agent and the runner: 0 printed cuts means the timing-off race, and `ci-local` runs pytest without xdist, so "after the pool" holds).
- [sol] N1 / [fable] N3: `p7` is proxy evidence (the stand-in with the three constants); CPB.4c is the direct test. Folded.
- [sol] N2 / [fable] N1: the routed estimate and the CPU arithmetic include CPB.4c. Folded.
- [fable] N2: Phase A confirms CPB.2–CPB.7; CPB.8 lands with the notebooks. Folded.
