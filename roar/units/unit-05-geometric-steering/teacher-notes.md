# Teacher notes — Unit 5: Geometric steering 🏁

## Goals

By the end of this unit students can:

- Derive **pure pursuit**: the arc through a lookahead point at distance d and bearing α has curvature κ = 2 sin α / d, so δ = atan(L·κ). They check that on a circle it gives exactly 1/R.
- Use a **speed-scaled lookahead** L_d = clip(k·v, L_min, L_max) and explain the trade: a longer lookahead is more stable and cuts more corners.
- Explain **actuator delay**, why every real car has some, and race with `KinematicCar(lag_ticks=N)`.
- Write the **Stanley** law at the front axle, δ = ψ_e + atan(k·e / v), and say why a law with no lookahead is delay-sensitive.
- Read an honest, conditional result.
  - On a car with **no delay**, pure pursuit does **not** beat Unit 4's controller; it cuts corners (RMS 0.14–0.15 m against about 0.10 m at 20 m/s).
  - At **30 m/s with a 2-tick delay**, pure pursuit is clean on every seed, while Unit 4's gains and Stanley crash on every seed.
  - A detuned PD survives too, but sits further off the line (0.51 against 0.45 m).
  - The best lookahead grows with the delay.
- Run both agents on **CARLA** in the lab, and keep the one the real car prefers.

This unit introduces three concepts:
- `pure-pursuit`;
- `lookahead-tuning`;
- `stanley-steering`.

`agents/unit-05.py` keeps pure pursuit (k = 0.3 s) because it is the robust choice while CARLA's delay is unknown; Unit 8 measures it.
`STEERING = "pid"` turns it back into the Unit 4 agent exactly, so the lab comparison is one constant away.

## Pacing

Plan for **two to three 60–90 min sittings**, plus the lab on a CARLA machine.

1. **Sitting 1: the geometry** (lesson §§1–3).
   - Hook: *steer like a driver looks ahead*. Ask students where they look when they drive a bend.
   - Derive κ = 2 sin α / d from the isosceles triangle (car, target, centre of the arc). The circle check is exact; make students predict it before running it.
   - Race pure pursuit at 20 m/s and show the honest result: it does not beat Unit 4 on this car. Let the class sit with the puzzle: why would anyone use it?
2. **Sitting 2: delay** (lesson §§4–6).
   - Actuator delay: the command applied now takes effect N ticks later. Racing with `lag_ticks` shows what a real car does with a controller tuned on a perfect model.
   - Lag 2 is the smallest delay that separates the controllers on the kinematic car; it stands in for the real car's lag, its steering-rate limit and its tyres.
   - The delay study at 30 m/s: Unit 4's controller goes from the best at lag 0 to crashing at lag 2. Connect it to Unit 4's K_HEAD = K_D·v: at 30 m/s the damping is a third lower.
   - The lookahead sweep: draw the RMS against k at lag 0 and at lag 2 on the same axes. The minimum moves right as the delay grows.
3. **Sitting 3: Stanley and the decision** (lesson §§7–8).
   - Stanley is excellent with no delay and crashes at lag 2. A detuned PD survives, but pure pursuit gets its detuning for free from the lookahead.
   - Choosing under uncertainty: the reference keeps pure pursuit until CARLA says otherwise. Set up the lab.
4. **The lab** (on the CARLA machine; about 60 min once the set-up from Unit 1 works).
   - Students add the one-line recorder change (the offset becomes the agent's own cross-track error), run `unit-04.py` and `unit-05.py`, and analyse each recording.
   - The analysis excludes the first row after each respawn hold, because CARLA's first post-hold observation is still the crash pose.
   - Compare with racekit's prediction table. If CARLA's Unit 4 RMS is below Unit 5's, the real car behaves like a small delay, and Unit 4's controller is the better choice there.

## The lab: what to watch for

- **Never commit results.** Recordings live outside the repository (the Unit 1 lab sets this up). Check `git status` with the class before anyone commits.
- **One recording at a time.** `ROAR_LAB_CSV` points at one file; students run the analysis twice and write the two RMS values down.
- **Both agents run at 20 m/s.** On `carla_like`, the Unit 6 car, Unit 4's controller is clean at 20 m/s but crashes at 25 m/s while pure pursuit is clean (a preview, not shown to students yet). Do not let students raise `TARGET_SPEED` for the lab.
- **The interim CARLA checks are the author's** (design §7.3). Student CARLA results never enter the repository or the book.

## Common mistakes

- **Bearing in the wrong frame.** α must be the bearing of the target in the **car** frame (Unit 2's `to_car_frame`), not the world-frame angle to the target.
- **Lookahead by index, not distance.** The target is the first waypoint at a straight-line distance ≥ L_d. Counting waypoints ties the lookahead to the waypoint spacing.
- **Stanley's reference point.** Stanley uses the **front axle**; projecting the rear axle gives a different, worse law.
- **"Pure pursuit is better."** It is better under delay and worse without it. Every claim in this unit is conditional, and the evidence says which condition you are in.
- **Reading one seed of a crash study.** At lag 3 pure pursuit is clean but weaves (time spread 3.75 s). Clean is not the same as good.

## Discussion prompts

- Why does a longer lookahead make the car more stable under delay? (Hint: what does the controller do with an error it sees early?)
- Unit 4's controller has the lowest RMS at lag 0 and crashes at lag 2. What would you measure on the real car before trusting either result?
- A detuned PD and pure pursuit both survive lag 2. Which knob does each one turn, and which is easier to retune when the speed changes?
- In the lab, what result would make you switch the reference back to Unit 4's controller?

## Differentiation

- **Support:**
  - give the target-search loop and have students write only the curvature and the wheel angle;
  - give the delay-study table with the lag-0 row filled in.
- **Core:** all non-stretch exercises unaided, plus the lab analysis on the sample recording.
- **Stretch:**
  - the lookahead that minimizes RMS at lag 1;
  - a lookahead point interpolated on the polyline (exact distance) against the first-waypoint rule;
  - for strong students: linearize pure pursuit about the line and show that its effective proportional gain is about 2L / L_d², so a longer lookahead is a softer controller.
