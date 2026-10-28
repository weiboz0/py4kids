# Teacher notes — Unit 8: System identification

## Goals

By the end of this unit students can:

- Write a model that is linear in its unknowns as a **matrix of logged columns**, solve it with `np.linalg.lstsq`, read the **residual**, and choose an unknown such as the actuator lag by the residual.
- Explain how least squares is solved well (QR), and why ‖Ac − b‖² = ‖Rc − Qᵀb‖² + const turns a tall problem into a small one (Unit 9 uses this).
- **Identify the car** from logs: the longitudinal map (throttle, brake, drag, lag) and the **steering gain**, and compare each with the value the agent *assumed*.
- Design an **excitation**: explain why a clean race log cannot identify grip, push one section at a time with their own agent, estimate μg from a percentile of the measured acceleration, and say when the number is only a **lower bound** (the probe never slid) or **no estimate** (too few rows).
- Plan with a **fraction of the measured grip**, tune that one fraction on the training family, freeze it by the margin rule, and show that it transfers to a track it was never tuned on.

This unit introduces three concepts:
- `linear-least-squares`;
- `car-identification`;
- `grip-identification`.

`agents/unit-08.py` is the Unit 7 agent with two measured things changed: the steering gain (66°, rounded from the measured 65.7°, where Unit 7 assumed 70°) and a per-section grip table `MU_G` measured on `test-circuit`, planned at `MU_FRACTION = 0.56`.
On `test-circuit` it races 301.95 s.
The headline is the transfer: tuned on the five training tracks, it races the unseen `test-circuit-seed2026` clean in 303.30 s, where Checkpoint A's single setting took 310.80 s and the Unit 7 reference crashes on every seed there.
On `monza-like`, the steering gain alone decides how hard the agent can plan: at 70° the measured-grip planner fails from f = 0.54; at 66° it is clean up to 0.62.

## Pacing

Plan for **two to three 60–90 min sittings**, plus the lab on a CARLA machine.

1. **Sitting 1: least squares on logs** (the hook and the lesson's least-squares and car sections).
   - Hook: the Unit 7 agent, tuned on one track, crashes on a track it never saw. It does not know the car; it knows one track.
   - Build the longitudinal matrix column by column from the committed race log, solve, and plot the residual against the lag. Students from competitive programming like the "pick the lag by the smallest residual" search.
   - QR on the board: why `lstsq` does not form AᵀA.
   - The steering gain from the steady lap: 65.7° measured against 70° assumed. Ask what a 6% gain error does to every steering command.
2. **Sitting 2: grip** (the grip section).
   - Why the race log is useless for grip: a clean race never reaches the limit, so it only bounds μ from below.
   - The probe: push one section, let the car slide, and look at the top of the acceleration. Show the two excitations that fail (all sections at once, every section from s onward) before the one that works.
   - The lower-bound case on `monza-like` section 0: a straight cannot be pushed sideways. That is not a failure of the method; it is what the method can honestly say.
3. **Sitting 3: using what was measured** (the last section).
   - The fraction sweep on the family, the margin rule, and the race on the unseen track. Put Checkpoint A's 310.80 s on the board first.
   - The steering gain on `monza-like`: the same planner, the same grip, only the gain changed.
4. **The lab** (on the CARLA machine; about 3 hours in full, the short form fits one sitting).

## The lab: what to watch for

- **Never commit results.** The recordings, the probe logs and any fitted numbers stay outside the repository. Check `git status` with the class before anyone commits.
- **Probes crash on purpose.** Each grip probe is meant to slide; on CARLA it ends at its first respawn or after 3 minutes. Warn students before the first probe, or they will "fix" it.
- **A probe that never slid is a lower bound.** If a section's probe finished without a respawn, its number is not an estimate. If a section has too few rows, it has no estimate at all.
- **The decision procedure never ends on a value it did not race.** 0.54, then 0.52, then 0.50, each raced twice and abandoned at the first unclean race; if 0.50 also fails, no setting is accepted and the student keeps their Unit 7 submission.
- **Grip may not be identified at all on CARLA.** Then the lab races the Unit 7 submission with only the measured steering gain changed. That is still a measured improvement, and the most likely one to transfer.
- **The interim CARLA check of the Unit 7 reference is the author's** (design §7.3) and is still pending. Student CARLA results never enter the repository or the book.

## Common mistakes

- **Fitting without the lag.** The residual is visibly worse at lag 0; a fit that ignores the actuator delay biases every coefficient.
- **Reading a clean race's peak acceleration as μg.** It is a lower bound: the car never reached the limit.
- **Pushing every section at once.** The car crashes in the first corner and never reaches the others; one probe per section is the excitation.
- **Treating a lower bound as an estimate.** Planning at f·(lower bound) is safe but slow; planning at a made-up number is neither.
- **Calling the fitted numbers "the car's".** They are measurements, with errors; say "measured", and compare them with what the agent assumed.
- **Tuning the fraction on the unseen track.** The transfer claim only holds if the fraction was frozen on the family first, as in Checkpoint A.

## Discussion prompts

- The longitudinal fit uses three columns and a lag. What would a fourth column have to be for the fit to find the road's slope?
- Why does a 6% steering-gain error hurt more at 45 m/s than at 20 m/s?
- A percentile of what the car did can only read at or below the limit. Is a biased-low estimate a problem for planning, or a feature?
- On CARLA you get six probe runs, not sixty. Which sections would you probe first, and why?

## Differentiation

- **Support:**
  - give the matrix for the longitudinal fit and have students write only the `lstsq` call and the residual;
  - give the probe driver and have students write the acceleration and the percentile.
- **Core:** all non-stretch exercises unaided, and the fraction sweep on at least three training tracks.
- **Stretch:**
  - the drag from a coast-down segment alone, against the full fit;
  - a weaker probe (`GRIP[s] = 2.0`): does it still slide, and what does the estimate become?
  - for strong students: derive the normal equations, and show why QR avoids squaring the condition number.
