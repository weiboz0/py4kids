# Teacher notes — Checkpoint A: a clean agent on a track it was not tuned for

This checkpoint closes **Part 1**.
The student takes their Unit 7 agent, tunes **one global setting** on a family of training tracks, and races a track
it was never tuned on, **once**.
It is **strict**: every task uses only Units 1–7 (repeated runs, the clean rule, the margin rule, Menger curvature,
the speed profile, telemetry plots), with no borrowed tools, and it introduces nothing.

## Goals

The student can, unaided:

- load and compare a family of tracks (length, tightest radius from their own Menger curvature);
- plan a lap with their own forward–backward speed profile and check it against the lesson's two passes;
- find an edge on Unit 7's A_LAT grid with the clean rule on five seeds, and apply the margin rule;
- discover that a setting tuned on one track is not clean on its neighbours, and **describe** what the car did from
  telemetry;
- tune one setting on the whole training family, freeze it, and race the sealed checkpoint track once, honestly.

## The story the checkpoint tells

The Unit 7 reference ships A_LAT 4.6: one grid step inside `test-circuit`'s clean edge, 4.8.
On the training variant `test-circuit-seed1` that setting is not clean (one race of five hits the wall), and on the
checkpoint track it crashes on every run.
Tuned on the whole family, the edge is 4.4 and the margin rule gives 4.2: clean on the checkpoint track in about
311 s, against the Unit 6 agent's 420 s.

What the car does when it fails (the probe record of plan `roar-007`): on a **straight**, after a corner, it weaves
with a growing amplitude over about 4 s (about 1 m, then 2 m, off the line) until it reaches the wall.
Students should find this in their own plot in Question 4.
The variants differ in shape (every corner a little tighter or looser, every straight a little narrower or wider),
and the carla-like car does not grip the same on every track, as no two real circuits do.
**Do not tell students why the grip differs, and do not point them at the module that holds it.**

## Pacing

One sitting of **75–90 minutes**.

- Questions 1–2 (about 20 min): the tracks and the planner, no racing.
- Question 3 (about 10 min): `test-circuit`'s edge; about a minute of racing.
- Question 4 (about 20 min): the family check and the failing race's plot; this is the discussion centre.
- Question 5 (about 15 min): the family sweep, about 25 races (2 min); freeze the setting.
- Question 6 (about 15 min): the plan, the one race on the checkpoint track, and the written comparison.

**Short form** (60 min): give Question 1's table, and run Question 5 on the tracks `test-circuit` and `test-circuit-seed1`
only (the track on which 4.6 failed in Question 4).
Give the other three tracks' results as evidence: A_LAT 4.4 is clean on the tracks `test-circuit-seed2`, `-seed3` and
`-seed4` (medians 307.15, 308.15 and 308.05 s), so the student can still establish the family edge.
The student still freezes before race day and races the
checkpoint track once.

## Grading

- **The race (pass/fail):** clean on all five seeds (finished, 0 collisions, max cross-track error ≤ 2 m) and a
  median ≤ 330 s, with the setting frozen **before** the checkpoint track was raced.
- **The evidence:** the family sweep as run (which values, which tracks, which seeds), and the margin rule applied.
  The plan's results table is public, so the final number alone proves nothing; grade the sweep and the reasoning.
- **The written answers:**
  - Question 4: a clear description of the failing race (where, at what speed, what the cross-track error did), a cause
    proposed in Unit 5–6 terms (the lookahead at speed, the grip, the corner before the straight), and one race that
    would test it. **Any well-argued cause earns the marks**; there is no single right mechanism.
    A student whose own agent is clean on all four variants studies the book's reference failure instead (A_LAT 4.6 from
    `REFERENCE` on `test-circuit-seed1`, which fails on race seed 1), and says so; grade it the same way.
    The proposed race is a diagnostic and may change a fixed knob (for example `PP_K`); only the submission is limited
    to A_LAT.
  - Question 6: what speed planning bought over Unit 6, and what the margin cost against the edge.

The 330 s target is a racekit target on this one track.
It has nothing to do with the book's 329 s bar for CARLA's Monza from Unit 1; say so if students connect them.

## Common mistakes

- **Tuning on the checkpoint track.** Loading it and planning on it is allowed; racing it before the setting is
  frozen is not. A student who raced it twice reports the first race.
- **Keeping Unit 7's per-section knobs.** A student's Unit 7 file may ship a tuned `GRIP` vector; the checkpoint resets
  it to all 1.0, because a section is a sixth of a different lap on every track.
- **Stopping at the first clean track.** A value clean on `test-circuit` and three variants is not clean on the
  family; every track counts.
- **Calling 4.4 the answer.** 4.4 is the family's edge; the margin rule ships 4.2.
- **Over-reading one failing race.** One race of five failed on seed 1. That is exactly what the clean rule is for.

## Discussion prompts

- Unit 7 already used a margin of one grid step. Why was it not enough here?
- What would you need to know to set A_LAT for CARLA's Monza, which is not in the family at all? (Unit 8 measures the
  car from its logs.)
- The weave starts on a straight. What changed between the corner and the straight that a speed planner does not see?
- Would five more training variants have changed your setting? How would you know?
- The race came in **faster** than the plan (about 6 s), although the plan has no standing start. What does the car
  do that the plan does not? (The profile is followed 0.3 s early, and the car overshoots the 45 m/s top speed.)

## Differentiation

- **Support:** give Question 2's profile function and have students write only the checks; give the sweep loop and
  have them write the clean rule.
- **Core:** all six questions as written.
- **Stretch:** repeat Question 5 on A_DEC as well as A_LAT (on the family, never on the checkpoint track), and argue
  whether the extra knob is worth its races.
