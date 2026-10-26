# Teacher notes — Unit 1: The race and the baseline

## Goals

By the end of this unit students can:

- State the ROAR race rules as the **pinned code** applies them: 3 laps, total simulated time, the 0.05 s control
  tick, progress through a 15-waypoint forward window, and the **crash rule**:
  - a major collision (impulse > 100) sends the car back to the start pose;
  - the car is held for 20 ticks (1.0 s);
  - progress resets to 0, so the race restarts with the clock still running.
- Read and explain the one-file submission ABI. That means `RoarCompetitionSolution`, with `async initialize()` and
  `async step()`, written for the Python 3.8 target.
- Run the starter in racekit, deterministically and with seeded jitter, and read its telemetry columns, including
  `held`.
- Compute 3×3 **sector splits** from telemetry, for a racekit result and for a CSV round-trip, and use them to say
  *where* time goes.
- Explain why one run lies. Measure **repeated seeded runs** (median and range), and apply the noise-aware
  comparison rule.
- Plot telemetry and the speed map with `racekit.plots` and plain matplotlib.
- Run the starter on real CARLA in the lab, record telemetry with `CumulativeProgress`, and analyse it with the same
  code.

This unit introduces four concepts:
- `roar-race-and-submission`;
- `race-telemetry`;
- `repeated-run-measurement`;
- `telemetry-plotting`.

It does **not** change the car's behaviour. Controllers start in Unit 2.

## Pacing

Plan for **two to three 60–90 min sittings plus one lab session**. The audience has calculus and solid
competitive-programming experience, so move briskly through Python mechanics and slowly through the measurement
ideas.

1. **Sitting 1: the race and the ABI** (lesson §§1–4; Exercises 1–2).
   - Open with the hook: *how fast is the official starter, and where does it lose time?*
   - Cover the rules, especially the crash rule, then read `agents/unit-01.py` line by line.
   - Do the deterministic `oval` run first (223.50 s, every time).
2. **Sitting 2: where the time goes** (lesson §§5–6; Exercises 3–5).
   - Move to `monza-like` telemetry, the speed trace, the speed map and the sector splits.
   - Derive the 20 m/s budget on the board: about 5.8 km per lap at 20 m/s is about 290 s per lap, against about
     107 s per lap on the podium.
   - Flat splits are the fingerprint of a speed cap. The slow lap-1 sector 1 is the standing start.
3. **Sitting 3: one run lies; the price of a crash; checking a submission** (lesson §§7–9; Exercises 6 onward, and
   the stretch exercises).
   - Turn on jitter, take 5 runs, and report the median and range.
   - Show the saboteur crash: total ≈ clean + t_crash + 1.0.
   - Finish with `check_submission`.
4. **Lab session** (`labs/real-sim.ipynb`): install, run `agents/unit-01.py` as `submission.py` on CARLA Monza, add
   the recorder, and analyse your own CSV.
   - Budget a full session for the first install. CARLA plus the Monza executable is Windows-only and needs a GPU.
   - Have students verify the environment *before* the session if at all possible.

## Common mistakes

- **"A crash costs a lap."** Not in the code we race against. The published rules say so, but the pinned runner
  resets progress to 0 after a 1.0 s hold. A crash on lap 3 therefore costs nearly the whole race. Zero collisions
  is the dominant lever, so a clean slower agent beats a fast crashing one.
- **Trusting one run.** On CARLA the same agent spreads by about 0.3 s from run to run, and racekit with jitter
  reproduces that. A "0.2 s improvement" from a single run is noise. Insist on medians and the noise-aware rule.
- **Comparing jittered and deterministic numbers.** Jitter 0 gives 223.50 s on `oval`; jittered seeds give
  220.60–220.95 s. Neither is "the" time: compare like with like, the same car factory and the same seeds.
- **Forgetting that times are tick-quantized.** Every total is a multiple of 0.05 s, so differences smaller than a
  tick are meaningless.
- **Writing 3.9+ Python in a submission.** Students with modern habits reach for `list[int]` annotations, `|`
  unions, dict `|`, `match` or `str.removeprefix`, and the official environment is Python 3.8.
  `check_submission` catches the common ones, but only the isolated 3.8 run *proves* compatibility.
- **Reading the lab CSV per lap.** The recorder's `progress` is cumulative over the race (0 … laps × n). If a
  student writes the one-lap waypoint index instead, the sector splits come out wrong.
- **Hard-coding a CSV path in the lab.** The parameters cell owns `TELEMETRY_PATH`. CI swaps in the sample through
  `ROAR_LAB_CSV`.
- **Committing lab results.** Students' recorded telemetry is their work and never goes into the public repo.

## Discussion prompts

- The pinned code and the published rules disagree about crashes. Which should we optimise for, and what would you
  check before race day?
- The starter is never more than about 0.6 m off the line. It is not losing time by cutting or missing corners, so
  where *is* it losing time? What single number would you change first, and what could go wrong if you do?
- Why is the median a better summary than the mean for 5 race times? When might the *worst* run matter more than
  the median? (Hint: think about the qualification bar: every run clean.)
- racekit is repeatable and CARLA is not. What does repeatability buy us while developing, and what does it hide?

## Differentiation

- **Support:**
  - give the telemetry column list and a two-line `plt.subplots` template;
  - pair students for the CSV round-trip exercise;
  - in the lab, let a pair share one working CARLA machine.
- **Core:** all non-stretch exercises unaided, plus the lab on their own machine.
- **Stretch:**
  - Challenge 1: predict the crash cost at t = 120 s *before* measuring, from the v4.1 rule alone.
  - Challenge 2: use `write_variant` to try `TARGET_SPEED = 22` and decide, noise-aware, whether it is better *and*
    still clean.
  - Ask strong students what they expect when the cap rises further, as a bridge to Unit 4/5 control and Unit 7
    speed planning.

## Lab logistics

- Pins:
  - CARLA 0.9.12 with the **Monza v1.1** Windows AMD64 executable;
  - a Python 3.8 conda environment (numpy ≤ 1.24);
  - `ROAR_PY` at the pinned commit;
  - the `ROAR_Competition` runner at the pinned commit, unmodified apart from `submission.py`.
  See `roar/reference/upstream.md`.
- Students copy `agents/unit-01.py` to `submission.py` and run `competition_runner.py`.
- The recorder adds a `CumulativeProgress` and writes a v1-header CSV, which the analysis cells read with the same
  `read_csv` / `sector_splits` code used in racekit.
- Expect the first CARLA lap time to differ from racekit. racekit's kinematic car is a *model*, and calibration
  comes in Units 3 and 8. The point of this lab is the workflow and the measurement, not matching numbers.
- **Never commit results**: CSVs, screenshots and times stay on the student's machine.
