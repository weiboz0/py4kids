# Teacher notes — Unit 11: Robustness

## Goals

By the end of this unit students can:

- Price a crash: a crash restarts the race from rest, so a crash at time t costs about t + 1 s, and a car that crashes at the same corner every time never finishes.
- Compare settings by **expected race time** over a family of cars (not-finished races counted at the cap), and see why one crash outweighs many small time gains.
- Build and race the **perturbed carla-like family** (`carla_like(noise=True, perturb=k)`, `perturbation_factors(k)`), keep training cars and held-out cars apart, and choose a fraction by the family edge and the margin rule.
- Detect a respawn from the collision sensor (edge-triggered, with a refractory window), and compute two warnings: sideslip from the velocity sensor and the yaw, and the line error.
- Measure what a warning is worth (its lead time, its false alarms) and report a negative result honestly.
- Write a **fallback**: reset the controller's state, re-anchor one step later, switch to pure pursuit, slow down; and explain why the fallback is a different controller, not just a slower one.

This unit introduces three concepts:
- `respawn-economics`;
- `perturbation-testing`;
- `failure-fallback`.

`agents/unit-11.py` is the Unit 10 agent with `MU_FRACTION` re-tuned from 0.58 to 0.54 by the margin rule on the perturbed training family, plus a respawn handler that falls back to pure pursuit at 0.86 of the lateral limit.
With no respawn it races exactly like Unit 10 at the same fraction.
The book's tests race all 24 held-out perturbed cars: it is clean on every one (median 279.95 s on `test-circuit`).

## Pacing

Plan for **three 60–90 min sittings**, with Exercise 7 as homework or a fourth sitting.

1. **Sitting 1: what a crash costs** (the hook, §1–§2).
   - Hook: Unit 10's agent on four perturbed cars. One is clean; one crashes once and loses more than three minutes; two crash, restart, and crash again until the time runs out (the book's tests race all 24 training cars: 21 are clean).
   - Ask before showing: if a crash sends you back to the start, how much does a crash at 3 minutes cost? (About 3 minutes.)
   - Expected race time on the board: a 2 s gain on 21 cars against one 200 s crash.
   - Exercises 1–2.
2. **Sitting 2: testing against cars you have not met** (§3–§4).
   - The family, its ranges, and why they are the book's model of model error, not a measurement of CARLA.
   - Training cars and held-out cars: the same discipline as training tracks and the unseen track.
   - The family edge, the margin rule, the held-out check, and the transfer finding on `test-circuit-seed2026`.
   - Exercises 3 and 8.
3. **Sitting 3: noticing and recovering** (§5–§7).
   - The respawn detector; the warnings and their lead times; the negative result.
   - The fallback, and the lag-2 car: the MPC trusts its lag model, so no fraction saves it; pure pursuit does not care.
   - Exercises 4–6; Exercise 7 (a fallback for Unit 10, about 45 min) as homework or a fourth sitting; Challenges 9–10 as homework.

## Common mistakes

- **Pricing a crash as "the respawn hold".** The hold is 1 s; the restart costs everything raced so far.
- **Averaging only the finished races.** A crash loop is a not-finished race; leaving it out makes the risky setting look fast. Count it at the cap, and say which cap.
- **Tuning on the held-out cars.** Once a held-out car has influenced a choice, it is a training car. Keep the two sets apart, as with tracks.
- **Treating the family as CARLA.** The ranges are the book's choice. The method transfers; the numbers do not.
- **A level-triggered respawn detector.** If the collision sensor repeats its last reading, a detector that fires on every tick with a large impulse falls back again and again and the limit collapses. Fire on a new reading, once per 2 s.
- **Re-anchoring on the respawn step.** On CARLA the first step after a respawn still reports the crash pose. Re-anchor on the next step.
- **Falling back to "the same controller, slower".** On the lag-2 car a slower MPC still crashes: the fault is in its model, not its speed. A different controller is the fallback that helps there.
- **Claiming warnings do not help.** The unit shows that falling back on a sideslip warning at 8° or 6° did not prevent these crashes. A different reaction might; that is Challenge 9.

## Discussion prompts

- A crash at 30 s and a crash at 250 s: which costs more, and what does that say about where a risky setting should be spent?
- The margin bought on `test-circuit` does not carry to `test-circuit-seed2026`. What would you need to know about a track before trusting a margin there?
- A warning that comes 1 s before a crash at 40 m/s: what can the car still do in that second?
- Why might the real competition's collision rule (no respawn for a spin that touches no wall) change how you value a fallback?

## Differentiation

- **Support:**
  - give the expected-time function and have students fill the outcome table and read off the best fraction;
  - give the respawn detector and have students explain each of its three conditions.
- **Core:** all non-stretch exercises unaided.
- **Stretch:**
  - Challenge 9, a braking reaction to the warning, compared across seeds;
  - Challenge 10, a fraction that is clean on `test-circuit-seed2026`'s perturbed cars, and what it costs on `test-circuit`;
  - for strong students: estimate the probability of a crash per car from the family and turn it into an expected time for a three-race qualifying session.
