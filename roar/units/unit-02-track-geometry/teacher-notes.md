# Teacher notes — Unit 2: The geometry of a track

## Goals

By the end of this unit students can:

- Move between the world frame and the car frame. They compute a heading with `atan2` and wrap angles to [−π, π),
  and they know the edge cases (±π, ±3π, 0) and why wrapping must be idempotent.
- Project a point onto a segment and onto a closed polyline. They use a windowed, cyclic nearest-segment search
  carried from tick to tick instead of a full scan.
- Compute the signed **cross-track error** (left positive) with the scalar cross product, and reproduce racekit's
  `offset` column to 1e-6 on every row of a race.
- Compute the signed **Menger curvature** from three points and read a track's curvature profile (R_min 18 m on
  `test-circuit`, 25 m on `monza-like`).
- Use these instruments to *measure* the starter: the offset against the curvature, the `STEER_GAIN` sweep, and
  the RMS cross-track scorecard that Units 4–5 are scored against.

This unit introduces four concepts:
- `frames-and-heading`;
- `waypoint-projection`;
- `cross-track-error`;
- `menger-curvature`.

It does **not** change the car's behaviour. `agents/unit-02.py` races exactly like the starter (oval 223.50 s,
test-circuit 412.75 s, monza-like 882.55 s at jitter 0). It only adds the instruments.

## Pacing

Plan for **two to three 60–90 min sittings**. There is no lab.

1. **Sitting 1: frames, heading, wrapping** (lesson §§1–2).
   - Open with the hook: *the starter steers at a point three waypoints ahead and never looks further. Where
     exactly is the car relative to the track, and what is coming?*
   - Derive the rotation into the car frame on the board.
   - Make students predict `wrap_angle(math.pi)` before running it. The half-open interval surprises people.
2. **Sitting 2: projection and the cross-track error** (lesson §§3–4).
   - Derive the foot parameter t = ((p − a)·d)/|d|², and *why* the clamp is used only to choose the segment.
   - The G2.2 check is the payoff: the student's offset equals racekit's on every row to 1e-6.
   - Show the naive "sign × distance to the clamped foot" version failing on 3 rows (max 4.9e-4 m). Students who
     write that version first learn more from the discrepancy than from being told.
3. **Sitting 3: curvature, and measuring the starter** (lesson §§5–8).
   - Menger curvature on a circle first (exact to 1e-9), then the generator's profile.
   - The `STEER_GAIN` sweep: gain 8, 4, 2 finish clean while the car runs ever wider (0.51 → 1.76 → 4.40 m); gain 1
     does not finish (16 collisions). Have students predict, before running, *where* on the track the offset
     peaks. The answer is the tight corners.
   - Close with the windowed-search experiment and the bridge to Unit 3.

## Common mistakes

- **Expecting the starter to wobble or cut corners.** The original design hook assumed it did. On racekit's
  kinematic car it does neither: it stays within about 0.5 m of the line and never oscillates. Wobble and
  corner-cutting come from grip, which arrives with the dynamic car in Unit 6. Be honest about this. It is a good
  lesson in measuring before believing.
- **Wrapping with `%` and getting [0, 2π).** Subtract π after shifting, as `wrap_angle` does, and test ±π.
- **Using the clamped-foot distance as the offset.** It is the right *selector* but the wrong *offset* past a
  segment's ends. The offset is the distance to the segment's line: the cross product divided by |d|.
- **Reaching for `np.cross`.** It is deprecated for 2-vectors and raises in numpy 2. Write dx·e_y − dy·e_x, which a
  Python 3.8 submission needs anyway.
- **Full scans every tick.** They are O(n) per tick and they jump to the wrong part of a track that passes close to
  itself. A window around a carried hint is O(1) and stays on the right part.
- **Sign conventions.** Left-positive offset and left-turn-positive curvature, but a *positive steer turns right*.
  Students will get one sign wrong. The stretch exercise on the steer sign is there for this reason.
- **"A better instrument should drive better."** The windowed-search agent with the same lookahead drives *worse*
  at low gain. Its index sits at the car rather than about 2 m behind it, so its target is about 6 m ahead
  instead of 4 m. A farther target weakens the correction per metre of offset: windowed gain 2 behaves like starter
  gain ≈ 1.3. Instruments measure;
  controllers (Units 4–5) use them.

## Discussion prompts

- The offset peaks line up with the curvature peaks. Is that cause or correlation? What experiment separates them?
- Gain 2 finishes clean but 4.4 m off the line. Is that a problem if the race only counts time? (Think of the track
  half-width, and of the next unit's prediction.)
- Why do we score Units 4–5 on the RMS offset rather than the max? (Hint: compare the ranges in the jittered
  scorecard.)
- The car's index comes from a "reached radius" test, and the instrument's from a projection. When could they
  disagree, and which one would you trust after a respawn?

## Differentiation

- **Support:**
  - give the segment-projection formula and have students implement only the window logic;
  - provide a two-track plot template for the curvature profile.
- **Core:** all non-stretch exercises unaided, plus the G2.2 equivalence.
- **Stretch:**
  - the sign convention of the signed curvature against the steer sign;
  - the curvature–offset correlation on `monza-like` at 30 m/s;
  - for strong students: why is the Menger curvature of a chord-sampled circle exact, and when does it stop being
    a good estimate of the generator's curvature?
