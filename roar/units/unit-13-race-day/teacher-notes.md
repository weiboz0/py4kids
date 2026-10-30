# Teacher notes — Unit 13: Race day

## Goals

By the end of this unit students can:

- **Assemble** a race-day submission from the parts the book built: Unit 9's line, Unit 8's measured grip, Unit 10's MPC, Unit 11's fallback and Unit 12's tuning, and say which unit each constant comes from.
- Explain why section 0's grip, a **lower bound**, costs nothing on `monza-like`, from v_max = √(μg/κ) and the line's curvature, without racing.
- Re-tune on the **known track** against the **unknown car**: Unit 12's crash-aware objective on `monza-like`, Unit 1's noise-aware acceptance decided in whole ticks (the float tie), and the edges it finds.
- Apply Unit 11's **margin rule to every knob at its edge**, and keep training, validation and test cars apart (the test cars raced once).
- Decide **MPC or pursuit** honestly: time first, then margin.
- **Qualify and package:** `check_submission` on the race's own track, the timing budget, "ship the behaviour you tested" (`MPC_MIN_HORIZON = MPC_HORIZON`), the packaging checklist, and the season's rules read from the current page.
- Run a **race-day record** on CARLA: five consecutive launches, none discarded, with the host-failure rule.
- **Open the parts** (Exercises 9–11, added by plan `roar-014` so that every concept is practised before the capstone): identify the car's longitudinal map from a race and replay it with Euler and RK4; read sideslip and yaw rate against the kinematic and dynamic bicycles; check the MPC's linear error model where the car drives; see windup, Stanley's crash at speed, and where the tick's time goes.

This unit **introduces nothing**.
It practises earlier units' concepts (Units 1 and 3–12): `cornering-speed-limit`, `speed-profile`, `racing-line`, `line-retune`, `ltv-mpc`, `pure-pursuit`, `tick-budget`, `perturbation-testing`, `respawn-economics`, `repeated-run-measurement`, `black-box-search`, `held-out-track-validation`, `determinism-and-packaging`, and (Exercises 7 and 9–11) `numerical-integration`, `integrator-windup`, `stanley-steering`, `dynamic-bicycle`, `car-identification`, `error-model-linearization`, `step-profiling`.
It uses Unit 8's measured grip but identifies no grip, so it does not practise `grip-identification` (Exercise 9 identifies the longitudinal map, `car-identification`); nor does the lab, which carries the student's own CARLA grip over from an earlier lab.

`agents/unit-13.py` is `agents/unit-11.py` with six constants changed:
- `monza-like`'s line (`LINE_CONTROL`, 285 values) and measured grip (`MU_G`);
- `MU_FRACTION` 0.64, `A_DEC` 4.5 and `A_ACC` 5.0;
- `MPC_MIN_HORIZON` = 40.

On `monza-like` it races 468.55 s against `unit-07.py`'s 515.10 s, both clean on five seeds: 46.55 s faster, against spreads of 0.10 and 0.15 s.
It is clean on all 24 validation cars (24–47), all 24 further validation cars (48–71) and all 24 test cars (72–95), which were raced once.
`unit-07.py` is clean on only 12 of the 24 cars 24–47.

## Pacing

Plan for **three 60–90 min sittings** (`lessons: 4` with the lab), plus the lab on a CARLA machine.

1. **Sitting 1: assemble and re-tune** (the hook, §1–§2).
   - Hook: one file, one track, one car you have not met.
     Race `unit-07.py` against the assembled `unit-13.py` (about 15 s of racing).
     Ask: 47 s faster, but what makes it safe to submit?
   - §1: the parts table.
     Section 0's lower bound: let students compute v_max before you show the curvature plot.
   - §2: the three car sets on the board (training 0–23, validation 24–71, test 72–95).
     Then the re-tune's table and the float tie.
   - Exercises 1–3 (no races).
2. **Sitting 2: margin, steering and qualifying** (§3–§6).
   - §3: M and M2 on car 41 (about 25 s of racing).
     Unit 11's rule, read for one knob, is not enough here.
   - §4: MPC or pursuit, with pursuit's crash on car 34.
   - §5–§6: `check_submission` on its own track, the race-day timing trade, the checklist and the season's rules.
   - Exercises 4–8.
3. **Sitting 3: open the parts** (Exercises 9–11; one 70 s Stanley race and one profiled lap, the rest reuses Exercise 7's race).
   - Exercise 9: the car's longitudinal map at lags 0–3, and Euler against RK4 against the car. Ask why RK4 is not closer to the car than Euler (the model error dominates).
   - Exercise 10: sideslip and yaw rate; the linear error model at the tightest point, and why it is safe where the car drives.
   - Exercise 11: windup with and without the PID's limits; Stanley's crash; the profile.
   - Challenge 12 as homework.
4. **The lab** (on the CARLA machine): two counted practice launches (a host failure is relaunched, not counted) plus the 5-launch record; a host failure adds a block.

## The lab: what to watch for

- **The starting file must have raced clean on CARLA.**
  The order is the Unit 10 lab's accepted configuration, else Unit 8's, else Unit 7's, else the Unit 5 or Unit 1 lab file.
  A file that has never raced clean on CARLA is never the race-day file.
- **Margin only where an edge was found on CARLA.**
  A knob the student never pushed to a not-clean setting gets no margin.
  An assembled file that differs from the starting file needs two clean practice launches; otherwise the starting file races.
- **Fix the horizon.** The race-day file sets `MPC_MIN_HORIZON` to its own `MPC_HORIZON`, so the race is the behaviour its practice launches tested.
  Timing is checked first, before the practice launches, off CARLA, on an idle machine (the Unit 10 lab's timing copy for a file with a Monza line, at 4 ms; the cell checks at 4 ms unless told the file has no line).
  If the assembled file fails, the starting file races, with no practice launches.
- **Five consecutive launches, none discarded.**
  A host failure (the server exits, or the agent never gets its first tick) is recorded and the block restarts; both blocks stay in the record.
  Students are tempted to "just run it again" after a bad launch: that is exactly what the record forbids.
- **Analyse every launch**, not one: point `ROAR_LAB_CSV` at each recording in turn and type each result into `LAUNCHES`.
- **Never commit results, and never commit the edited lab notebook.** The typed-in `LAUNCHES` and `UNIT_7_TIMES` are the student's data, and the repository is public.
  Check `git status` with the class.
- **The season's rules.** The series page says `instruction.txt` and the gitbook says `requirements.txt`. Have students read the current season's page, not the book.
- **The interim timed CARLA check of the Unit 13 reference is the author's** (design §7.3) and is still pending.
  Student CARLA results never enter the repository or the book.

## Common mistakes

- **Tuning on the test cars.** Cars 72–95 were raced once, after the file was fixed.
  Any choice made from them would spend them; Challenge 12 asks what to race instead (a fresh, pre-registered set).
- **Reading the margin rule for one knob.** The margin on `MU_FRACTION` alone (M) crashes on car 41.
  Every knob at its edge gets one grid step of margin; a knob with no edge gets none.
- **Accepting a float tie.** A gain of exactly one tick against a spread of exactly one tick is a tie.
  Compare race times in whole ticks.
- **Choosing pursuit because it ties MPC on the nominal car.** It is clean on only 13 of 24 validation cars.
  Time first, then margin.
- **Checking the submission on the default track.** `check_submission` races `test-circuit` unless told otherwise.
  A Monza line refuses to run there, so a race-day file is checked on its own track.
- **Trusting the time-budget policy on race day.** The halving policy protects a machine you cannot check.
  On race day you check the machine before the race and ship the behaviour you tested.
- **Calling the stand-in "the car".** Every racekit number is a model number.
  CARLA is the test, and the lab's record is what counts.
- **Fitting the map at lag 0** (Exercise 9). The command acts a tick late; the lag with the smallest RMS (1) is the one Unit 8 measured.
- **Expecting RK4 to match the car** (Exercise 9). RK4 beats Euler on the model's own equations; against the car, the model's error is larger than either integrator's.
- **Calling the agent's own `PID` or `rk4_step`** (Exercises 9 and 11). Students write Unit 3's integrators and Unit 4's PID themselves; the file's helpers are not taught names.
- **Trusting the linear error model everywhere** (Exercise 10). It is safe where the car drives (one tick differs by at most about 2.3e-4 m); at a 5 m error it overshoots by metres.
- **Reading the profile's numbers as a timing claim** (Exercise 11). The profile shows *where* the time goes (the MPC solve); its seconds depend on the machine.

## Discussion prompts

- The track is known and the car is not. Which of the book's tools exist because of the car, and which because of the track?
- On `monza-like`, expected time and the margin rule both pick M2; at Checkpoint B they disagreed. What was different?
- Pursuit ties MPC on five seeds and loses on eleven perturbed cars. What would you have shipped after Unit 10, and why?
- Why is a test set raced once? What would you do if `unit-13.py` had failed on car 80?
- Unit 10 taught a horizon that shrinks when the machine is slow. Why does the race-day file turn that off, and when would you keep it?

## Differentiation

- **Support:**
  - give Exercise 3's whole-tick comparison helper and have students replay the table;
  - give Exercise 6's expected-time sums and have students write only the comparison.
- **Core:** all non-stretch exercises unaided.
- **Stretch:**
  - Challenge 12: P, the margin only on the knob that failed; is it a finding or a fit, and what would you race to tell?
  - For strong students: design the race-day protocol for a second track (which car sets, how many races, what is raced once) and estimate its cost before racing anything.
