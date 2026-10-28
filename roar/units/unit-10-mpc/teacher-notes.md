# Teacher notes — Unit 10: Model predictive control

## Goals

By the end of this unit students can:

- Write the **path-frame error model** (cross-track error e, heading error ψ), linearise it about the line, and step it in discrete time; explain why it is **time-varying** (the speed and the line's curvature change along the horizon).
- Put the **actuator lag** into the model: roll the queued command through first, then plan.
- Write the **horizon cost** and stack the whole horizon as x = G u + h, first one tick at a time, then in closed form, and solve it as **one least-squares problem per tick**; clip and apply the first command, and recede.
- Use `scipy.optimize.minimize` on one corner as the **exact reference**, and say what the linear solve gives up (under 1% of the cost) and what it buys (about 600 times the speed).
- Measure the **per-tick budget** (p50 and p99, warm-up excluded, never in a pool), and explain the shipped over-budget policy.
- Make an **honest comparison** with pure pursuit: no faster at the same fraction, but a tracking margin that moves the edge, re-tuned on the family and raced on the unseen track.

This unit introduces three concepts:
- `error-model-linearization`;
- `ltv-mpc`;
- `tick-budget`.

`agents/unit-10.py` is the Unit 9 agent with the steering law replaced by MPC (a 40-tick, 2 s horizon) and `MU_FRACTION` re-tuned from 0.54 to 0.58.
At the same fraction (0.54) it races `test-circuit` in 279.65 s against pursuit's 279.60 s: neither is noise-aware better.
MPC's gain is its tracking: its family edge is 0.60, where pursuit's was 0.56.
Frozen at 0.58, it races the unseen `test-circuit-seed2026` clean in 276.85 s, against Unit 9's 282.05 s.

## Pacing

Plan for **two to three 60–90 min sittings**, plus the lab on a CARLA machine.

1. **Sitting 1: the model** (the hook and the model sections).
   - Hook: Unit 9's agent at 0.58, one step above its edge, is not clean on `test-circuit-seed4` on any seed (on seed 0 it crashes). Pure pursuit looks at one point ahead. What if the steering planned the whole next 2 s?
   - The two error equations on the board, then the linearisation (sin ψ ≈ ψ). Ask what changes from one tick to the next (the speed, the curvature): that is "time-varying".
   - The lag: the command the car is about to apply was decided last tick. Roll it through before planning.
2. **Sitting 2: the solve** (the stacking, the exact reference and the weights).
   - Build G one tick at a time, then derive the closed form together. Students from competitive programming like spotting the running sums.
   - One `lstsq` call per tick. Clip only the first command; the rest of the plan is thrown away and re-planned.
   - The exact reference: `scipy` on one corner, the cost comparison and the timing.
   - The weights: show the first weights weaving and spinning on the dynamic car, and the same weights clean on the kinematic car. The model is kinematic; the car is not.
   - Exercises 1–5 (the model, the stacking, the solve, the lag, the timing) fit here and as homework.
3. **Sitting 3: racing it** (the comparison, the budget and the lab).
   - Same fraction first: no faster. Then the edge, the margin rule and the unseen track.
   - The lag ablation: without the lag in the model, not clean on any seed.
   - The tick budget: p50, p99, and why a pooled run lies. What a self-timed check can and cannot do.
   - Exercises 6–8 race the agent and take most of the unit's compute; Challenges 9–10 are homework.
4. **The lab** (on the CARLA machine; at most 8 races, the short form is 2).

## The lab: what to watch for

- **Start from an accepted configuration.** The lab compares MPC only against a configuration the student has already raced clean on CARLA (their Unit 8 lab's accepted setting). Students with only a PROVISIONAL Unit 7 result race it twice first; a student with no clean CARLA race at all records "no accepted configuration" and stops.
- **Timing first, off CARLA.** `check_submission` on the student's MPC file, on an idle machine. Close the browser and the other notebooks first. A file with a Monza `LINE_CONTROL` cannot race on racekit (the agent refuses a line solved for another track): time a copy with `LINE_CONTROL = None`, a proxy that passes only at p99 ≤ 4 ms (on racekit the line changed p99 by under 3%).
- **The weights were tuned on the line at 0.58.** On a centreline or `A_LAT` configuration they have never been probed; R1–R2 decide either way.
- **The procedure never ends on a value it did not race.** R3–R4 only after MPC is accepted, and only for a configuration that plans with `MU_FRACTION`.
- **Never commit results.** Check `git status` with the class before anyone commits.
- **The horizon lines.** The agent prints a line each time it shortens its horizon; ask students to note them by hand. On an idle machine there should be none.
- **The interim CARLA check of the Unit 7 reference is the author's** (design §7.3) and is still pending. Student CARLA results never enter the repository or the book.

## Common mistakes

- **Forgetting the lag.** The model plans as if this tick's command acts now; it acts next tick. Without the lag in the model the MPC is not clean on any seed.
- **Applying the whole plan.** Only the first command is applied; the plan is re-made every tick.
- **Clipping the plan before solving.** Clip the command you apply, not the least-squares problem; the box constraint is handled by clipping (design §6), and the exact reference shows what that costs.
- **Tuning the weights on the kinematic car.** They look fine there and weave on the dynamic car.
- **Timing in a pool.** Eight races sharing the machine give a p99 of 2–13 ms; the same step alone is about 1 ms.
- **Claiming MPC is faster.** At the same fraction it is not. Its tracking moves the edge; the re-tune is what buys the time.
- **Calling pursuit's `monza-like` result a crash.** At 0.64 pursuit finishes without a collision but strays 2.03–2.08 m from its line against the 2.0 m rule: a tracking-margin result at the threshold.

## Discussion prompts

- A longer horizon costs more time per tick but barely changes the lap. Why does the time saturate near 1–2 s of horizon?
- The exact `scipy` solve is under 1% better on one corner. When would that 1% be worth 600 times the compute?
- The over-budget policy shortens the horizon instead of switching to pure pursuit. Why is "the simpler controller" not automatically the safe fallback?
- MPC and pursuit drive the same speed profile. Where, exactly, does MPC's 5 s on the unseen track come from?

## Differentiation

- **Support:**
  - give the closed-form G and h and have students write only the stacked least-squares call and the clipping;
  - give the lag roll-through and have students explain it in words.
- **Core:** all non-stretch exercises unaided.
- **Stretch:**
  - a terminal cost (a larger weight on the last state), tested on the family;
  - a speed-dependent heading weight or horizon: noise-aware better or not?
  - for strong students: derive the closed form of G from the one-tick recursion by induction.
