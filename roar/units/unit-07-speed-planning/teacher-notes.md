# Teacher notes — Unit 7: Speed planning

## Goals

By the end of this unit students can:

- Build a **forward–backward speed profile**: a cornering cap at every waypoint, a backward braking pass v_i ≤ √(v_{i+1}² + 2·a_dec·Δs_i), a forward acceleration pass, both run around the lap until the wrap-around settles.
- Follow the profile with a **lead in seconds**, and explain why: the speed loop needs time to brake to the profile, so the goal must come from a little way ahead. A lead counted in waypoints does not transfer to a track with different spacing.
- Re-tune the steering lookahead for 45 m/s (Unit 5's `PP_K = 0.3` collides on every seed; 0.5 is the smallest clean value).
- Read the planned cornering rate A_LAT and braking rate A_DEC **together as a grid**, and explain its edge honestly: the car's friction circle is part of the reason, but the planner treats cornering and braking separately, and the speed loop and the driven line move the edge too (a_lat² + a_dec² along the edge is not constant).
- Tune **per-section speed knobs** one knob at a time under the clean rule, avoid the **stacking trap**, run the **sequential pass**, check the result on ten seeds, and step back by the **margin rule** when the check fails.
- Say clearly that the knobs are **not μ**: they absorb grip and everything else the planner gets wrong in that section. Unit 8 measures μ.

This unit introduces two concepts:
- `speed-profile`;
- `section-knob-sweep`.

`agents/unit-07.py` races `test-circuit` in 304.15 s (`carla_like`, ten seeds, all clean) against Unit 6's 422.65 s.
On the other tracks: 152.75 s against 216.50 s on `oval`, and 515.10 s against 880.50 s on `monza-like`.
It ships `GRIP = (1, 1, 1, 1, 1, 1)`, because a section is a sixth of *this* lap: knobs are tuned per track, in the lesson on `test-circuit` and in the lab on the real car.
On `test-circuit` the accepted knobs (1.15, 1.3, 1, 1, 1, 1) reach 299.60 s, faster beyond the noise than both the reference and the fastest global setting, 300.93 s.

## Pacing

Plan for **two to three 60–90 min sittings**, plus the lab on a CARLA machine.

1. **Sitting 1: the profile** (the hook and lesson §§1–2).
   - Hook: the Unit 6 agent is clean and slow. Plot its speed: it brakes late and never goes above 20 m/s.
   - The backward pass on the board: start at a corner's cap and walk backward with v² = v_next² + 2·a·Δs. Students who know dynamic programming recognize a relaxation.
   - Race the profile at 45 m/s: it collides. Two fixes, both "look further ahead": the steering lookahead and the speed lead.
2. **Sitting 2: two knobs** (lesson §3).
   - The (A_LAT, A_DEC) grid. Have students mark the clean cells before showing the times, and find the edge.
   - The friction-circle exercise: a_lat² + a_dec² along the edge. It is not constant; ask why. The car obeys the circle; the planner does not model it.
   - The margin rule and the reference; the gain over Unit 6.
3. **Sitting 3: per-section knobs** (lesson §4).
   - One knob at a time: every section has room. Stack them: every seed collides. This is the moment of the unit; let it land.
   - The sequential pass, and the ten-seed check that fails on seeds 5 and 8. Five seeds were not enough; the margin rule fixes it.
   - Like with like: compare the knobs with the best global setting, not with a deliberately conservative one.
4. **The lab** (lesson §5, on the CARLA machine; the full procedure can take about 3 hours, the short form fits one sitting).
   - The first run of the shipped agent is recorded as it is; tuning comes after.
   - The sequential pass on a coarse grid within a 12-run budget; the short form sweeps sections 0 and 1 only.

## The lab: what to watch for

- **Never commit results.** The recording **and** its `.sections.txt` sidecar live outside the repository. Check `git status` with the class before anyone commits.
- **One run per step is weak evidence.** The lesson needed ten seeds to catch an edge; CARLA cannot afford that, which is why the lab re-races its result twice, steps back if either run is not clean, and re-races the stepped-back setting twice too; if that also fails, the result is all knobs at 1.0, marked provisional.
- **Phantom braking.** CARLA's waypoints give a spiky curvature, so the profile can dip where the road does not bend. Point students at it in the speed plot; Unit 9 smooths the line.
- **The interim CARLA check is the author's** (design §7.3). Student CARLA results never enter the repository or the book.

## Common mistakes

- **One backward pass.** The braking pass must run around the lap more than once, or the corner just after the start line is entered too fast.
- **A lead in waypoints.** It works on one track and fails on another; the lead is a time.
- **Stacking the single-knob results.** Each knob was found with the others at 1; together they change the speeds every section is entered with.
- **Accepting on five seeds at the edge.** At the edge, one more seed can fail. Check the result on more seeds, or keep a step of margin.
- **Calling the knobs μ.** A knob of 1.3 does not mean the tyres grip 30% more there.
- **Comparing against a weak baseline.** "Better than the conservative reference" is a weaker claim than "better than the best global setting".

## Discussion prompts

- The backward pass and the forward pass each take one line. Which one makes the car fast, and which one makes it safe?
- Why does the speed lead barely change the time at the base setting but decide whether the car crashes at the edge?
- Section 1 was clean alone at 1.5 and collides at 1.5 once section 0 is raised. What physically connects the two sections?
- If you could afford only six CARLA runs, which sections would you sweep, and why?

## Differentiation

- **Support:**
  - give the two passes as code and have students explain each line, then plot the profile;
  - give the sequential-pass loop and have students write only the clean test.
- **Core:** all non-stretch exercises unaided, plus the grid's edge on one A_DEC row.
- **Stretch:**
  - a backward pass that respects the friction circle (brake less where the corner is tighter);
  - the sequential pass in the order 5→0, and whether it ends at the same knobs;
  - for strong students: prove that the backward pass converges after a bounded number of laps, and bound it.
