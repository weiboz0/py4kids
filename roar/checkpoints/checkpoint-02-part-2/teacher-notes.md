# Teacher notes — Checkpoint B: a full agent on a track and a car it has never met

This checkpoint closes **Part 2**.
The student takes their Unit 11 agent, measures a new track, solves its line, tunes one fraction on a family of
training tracks × training cars, and races five **sealed** perturbed cars on the new track, **once**.
It is **strict**: every task uses only Units 1–11 (grip probes, the smoothest line, the speed profile, expected race
time, the perturbed family, the clean and margin rules, the fallback), with no borrowed tools, and it introduces
nothing.

## Goals

The student can, unaided:

- measure a track's grip with Unit 8's probes and tell a measurement from a lower bound;
- solve the track's smoothest line and plan a lap on it;
- compute expected race time from a family's record, and see where it and the clean-plus-margin rule disagree;
- tune a fraction on a track × car family with a stated protocol, freeze it, and race sealed cars honestly;
- explain what the margin and the fallback each bought, with numbers.

## The story the checkpoint tells

Unit 11 shipped 0.54, chosen both by the margin rule on `test-circuit`'s perturbed cars and by the shortest expected
race time.
On the five training tracks with the training cars the two rules **disagree**: expected time is still lowest at 0.54
(the fallback turns every crash into a slow finish), but 0.54 and 0.52 are not clean on `test-circuit-seed2`, so the
family edge is 0.50 and the margin rule ships **0.48**.
Race day settles it: at 0.48 all five sealed cars are clean (median 283.90 s); at 0.54 four of five crash once.
The expected-time rule trusts the family's crash rate, and a new track with new cars is not in the family.
The margin is insurance against what the family did not show.

The race-day track's section 0 probe never slides: its estimate (9.10 m/s²) is a **lower bound**, the case Unit 8
taught on `monza-like`. The planner uses it as measured, which is the conservative choice.

## The race-day record (the Question 6 handout)

Hand this out **after** Question 5, never before. It is the probe record of plan `roar-011`, the reference agent on
the five sealed cars (`test-circuit-seed2027`, race seed k mod 5), and is also printed in the solutions.

| agent, fraction | clean | race times (s) | mean |
|---|---|---|---|
| Unit 11, 0.58 | 0/5 | 316.75, 378.70, 381.00, 379.65, 379.45 | 367.11 |
| Unit 11, 0.56 | 1/5 | 382.05, 273.10, 381.45, 381.80, 381.50 | 359.98 |
| Unit 11, 0.54 | 1/5 | 390.35, 275.45, 386.65, 384.65, 477.00 | 382.82 |
| Unit 11, 0.52 | 1/5 | 480.40, 278.10, 389.90, 390.40, 486.50 | 405.06 |
| Unit 11, 0.50 | 3/5 | 281.10, 280.80, 280.55, 486.40, 394.95 | 344.76 |
| Unit 11, 0.48 | 5/5 | 283.95, 283.90, 283.60, 283.75, 283.95 | 283.83 |
| Unit 10, 0.54 (no fallback) | 1/5 | 379.85, 275.45, did not finish × 3 | — |

Every Unit 11 race finishes; every not-clean one crashed once and finished after the fallback.
With no perturbation the same track at 0.54 is clean (about 275 s): the risk comes from the cars on this track, not
from the track alone.
Over 19 further cars of the family (record only) 0.48 is clean on 18: the margin makes crashes rarer, not impossible.

## Pacing

One long sitting of **90 minutes**, or two of 60.

- Questions 1–2 (about 20 min): six short probe races and the line solve; no tuning.
- Question 3 (about 15 min): the table, expected time, the two rules; the first written decision.
- Question 4 (about 30 min): the protocol, about 29 races (3 min of racing on the reference); the long part.
- Question 5 (about 10 min): the plan, the submission check, five races.
- Question 6 (about 15 min): the handout and the written answer.

**Short form** (60 min): give Question 1's six estimates and Question 2's line, and run Question 4 on
`test-circuit-seed2` only (the family's hardest track, where 0.54 and 0.52 fail).
That short run reports the `-seed2` races and does **not** claim the protocol's edge; give the other four tracks'
record (clean at 0.54 and below on the three cars) so the student can still argue for a value.

## Grading

- **The race (pass/fail):** all five race-day races clean (finished, 0 collisions, max line error ≤ 2 m) and a median
  ≤ 300 s, with the fraction frozen and `check_submission` passed **before** any sealed car raced.
- **The evidence (Question 4):** the protocol as run (which fractions, which races, where each stopped), the edge and
  the shipped value. A student's own agent may find another edge; every outcome path in Question 4 is legitimate.
- **The written answers:** Question 1 (which estimate is a lower bound, and why), Question 3 (the expected times and
  the decision, argued before racing), Question 6 (what the margin bought, what the fallback bought, why expected
  time misjudged race day).
- A student whose own agent misses the bar after following Question 4 honestly can still earn full marks on the
  write-up, which must say what their record showed.
- This plan's tables are public and `agents/checkpoint-b.py` ships the race-day line, grip and fraction (a known
  give-away, as `checkpoint-a.py` was); the grade never rests on the final number alone.

The 300 s target is a racekit target on this one track.
It has nothing to do with the book's 329 s bar for CARLA's Monza from Unit 1; say so if students connect them.

## Common mistakes

- **Shipping the expected-time minimum against a clean bar.** 0.54 has the best family mean, but the bar is clean
  races; a crash that the fallback rescues still fails it.
- **Racing the race-day track before freezing.** The six probes and race day are the only races allowed there.
- **Inspecting the sealed cars.** Any route counts: `perturbation_factors`, a built car's attributes, or re-deriving
  the seeded draw. The seal is an honour rule; a student who looked reports it.
- **Reading a lower bound as a measurement.** Section 0's probe finished the lap: the car never slid, so the true grip
  is at least 9.10 m/s², maybe more.
- **Over-reading one race.** At 0.52 the protocol's edge rests on a single race (`-seed2`, car 16); the full family
  record shows two. One crash is enough to call a fraction not clean, which is the clean rule's point.
- **Timing a pooled race.** The notebook races a timing-off copy; the frozen file keeps its 5 ms budget, and
  `check_submission` is the one run that times it.

## Discussion prompts

- The fallback made every 0.54 race finish. Why is that not enough to ship 0.54?
- Expected time would be right if the race-day crash rate matched the family's. What would you need to know to trust
  it on a new track?
- 0.48 crashed one of 24 wide-record cars. What would you do on a real race day with that knowledge?
- The section 0 estimate is a lower bound. Would a higher true grip there make 0.48 more or less safe?

## Differentiation

- **Support:** give the expected-time function from Unit 11 and the protocol loop; students fill in the stopping rule
  and write the answers.
- **Core:** all six questions as written.
- **Stretch:** run the protocol with all 24 training cars on `-seed2` only and compare the edge with the three-car
  protocol's; argue whether the extra races change the shipped value.
