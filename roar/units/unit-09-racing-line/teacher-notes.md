# Teacher notes — Unit 9: The racing line

## Goals

By the end of this unit students can:

- Describe a line as **offsets along the track's normals**, and keep it inside a **margin** of the edges.
- Explain the **reduced problem**: offsets as a periodic cubic B-spline of a few control values, where each waypoint's offset is a weighted average of four control values, so a bound on the control values bounds every waypoint.
- Solve the **smoothest line** (the sum of squared second differences of its points) as bounded linear least squares: QR, then `scipy.optimize.lsq_linear` on the small problem, with the start pinned to the centreline.
- Say what the line changes, with numbers: total squared curvature, lap length, and the one corner it makes tighter.
- **Follow** a line (the agent works on its own points) and judge it with the **line-relative clean rule**.
- Re-tune the speed for the new line, freeze it by the margin rule on the training family, and make an **honest comparison**: centreline, global line and local widening at the same fraction and at each one's own edge.

This unit introduces two concepts:
- `racing-line`;
- `line-retune`.

`agents/unit-09.py` is the Unit 8 agent with the smoothest line for `test-circuit` (shipped as 133 control values; a submission imports only numpy, so the line is solved in the notebook and pasted into the file) and `MU_FRACTION = 0.54`.
On `test-circuit` it races 279.60 s, against 304.70 s for the centreline at the same fraction.
On the unseen `test-circuit-seed2026` it races 282.05 s (Unit 8: 303.30 s; Checkpoint A: 310.80 s).
On `monza-like` the line buys about 27 s at the same fraction.

## Pacing

Plan for **two to three 60–90 min sittings**.

1. **Sitting 1: the hook and the line** (the hook and the line sections).
   - Hook: put Unit 8's frozen fraction on the line. It still finishes, but the value Unit 8 proved was its edge now crashes on a training track. The line moved the edge; the margin is gone.
   - Offsets along the normals; the margin; why the start must sit on the centreline.
   - The B-spline basis on the board: four weights, all non-negative, summing to one. Students should derive "bound the control values, and every waypoint is bounded" themselves.
2. **Sitting 2: solving it** (the solve and comparison sections).
   - The smoothness objective is linear in the control values; QR shrinks it to a square problem; `lsq_linear` handles the bounds.
   - What the line changes: about 19% less total squared curvature, a shorter lap, and one corner that gets *tighter*. The objective trades one corner for the whole lap.
   - The trap: interpolate the control values linearly and every control value becomes a kink the speed planner brakes for.
3. **Sitting 3: racing it** (the last sections).
   - Following a line: the agent's own points, and the `REACHED_RADIUS` trap (a line 3.5 m off the centreline never comes within 3 m of a centreline waypoint).
   - The same-fraction comparison, then the re-tune on the family and the race on the unseen track.
   - Local widening: it loses, as built. Discuss why rather than hiding it.

## Common mistakes

- **Bounding only the control values' own waypoints.** Use the whole support of each control value, or a waypoint between control values can cross the margin.
- **Forgetting the start pin.** The car starts on the centreline; a line that starts 3 m away puts the first tick 3 m off its own line.
- **Following the centreline's waypoints.** The agent must measure, plan and pursue on its own points.
- **Keeping the old speed tuning.** The line moves the edge; re-tune on the family before trusting a fraction.
- **Judging a line by the centreline's clean rule.** A line is meant to be off the centreline; the clean rule is measured from the line.
- **Calling it the minimum-curvature line.** It is the smoothest line, the usual stand-in; say what it minimises and measure what it changes.

## Discussion prompts

- The line lowers the total curvature but tightens one corner. When would that trade be a bad one?
- Why does a pure curvature objective swing across the straights, and why does the follower care?
- Local widening only moves the line near tight corners. Why does it crash here, when the global line, which moves more, does not?
- `monza-like` is mostly long straights at the 45 m/s top speed, yet the line buys about 27 s there. Where does the time come from?

## Differentiation

- **Support:**
  - give the B-spline basis and the matrix, and have students write only the bounds and the `lsq_linear` call;
  - give the follower change and have students write the line-relative clean rule.
- **Core:** all non-stretch exercises unaided, and the re-tune on at least three training tracks.
- **Stretch:**
  - a late-apex window (more waypoints after the tight point than before) against the symmetric one;
  - a 2.0 m margin against 2.5 m: is the narrower margin worth its risk?
  - for strong students: write the linearised curvature of an offset line and explain why the direct curvature objective is badly conditioned.
