# Teacher notes — Unit 6: Grip and the speed limit

## Goals

By the end of this unit students can:

- Explain why a car that holds the line perfectly on the kinematic car **spins** on a car with tyres.
  The Unit 5 agent at its flat 20 m/s spins 40 times on `DynamicCar()` `test-circuit` and runs wide on `monza-like`: one cause, too much speed for the grip.
- Describe the **dynamic bicycle**: slip angles at each axle, lateral tyre forces, and the yaw equation.
  At low speed it agrees with Unit 3's kinematic bicycle, which is why the earlier units were not wrong, only incomplete.
- Explain **tyre saturation** and the **friction circle** a_lat² + a_long² ≤ (μg)², and recognize a spin-out in telemetry.
- Derive the **cornering speed limit** v_max = √(a_lat / |κ|) and build a curvature-limited speed goal from Unit 2's `curvature_ahead`.
- Read an edge honestly.
  On `DynamicCar()` (μ = 1) the cap is clean up to 9.5 m/s² on `test-circuit` and spins at 9.75, just under μg = 9.81.
  On the carla-like car the edge moves down (clean at 7, spins at 8): the car has less grip than the model's default, and Unit 7 goes looking for it.
- Apply the **clean rule** (finished, 0 collisions, max cross-track error ≤ 2 m) and the **margin rule** (ship one grid step inside the last clean value).

This unit introduces three concepts:
- `dynamic-bicycle`;
- `friction-circle`;
- `cornering-speed-limit`.

`agents/unit-06.py` is Unit 5's agent with a speed cap, A_LAT = 6 m/s², and `TARGET_SPEED` still 20 m/s.
It is **safe and slow on purpose**: it removes every spin and collision (`carla_like` medians 216.50 / 422.65 / 880.50 s, all clean) without going any faster on the straights.
`SPEED_MODE = "flat"` turns it back into the Unit 5 agent exactly.

## Pacing

Plan for **two to three 60–90 min sittings**. There is no lab in this unit.

1. **Sitting 1: why it spins** (lesson §§1–3).
   - Hook: race the Unit 5 agent on the dynamic car. Let students watch the spin-outs in the telemetry before any theory: what changed between Unit 5 and now? Only the car.
   - The dynamic bicycle on the board. Keep the algebra to slip angles and the two lateral forces; the yaw equation is one line.
   - The low-speed comparison: at 5 m/s the two models agree, so the earlier units were right where they were used.
2. **Sitting 2: the friction circle** (lesson §§3–4).
   - The skidpad: a fixed steer, speed ramped, lateral acceleration plotted against speed. It rises as v²/R and flattens near μg, then the car spins. This is the single most useful plot in the unit.
   - v_max = √(a_lat/|κ|): connect it to the skidpad plot (the flat part is the a_lat the formula needs).
   - Build the cap from `curvature_ahead`, and race it.
3. **Sitting 3: edges and margins** (lesson §§5–7).
   - The A_LAT sweep on `DynamicCar()` and on the carla-like car. Ask students to predict the edge from μg before showing the table.
   - The clean rule and the margin rule: five clean seeds do not prove the sixth, and CARLA is not racekit.
   - The bridge: the cap only brakes when the corner is already close, and it never goes above 20 m/s. Unit 7 plans the whole lap.

## Common mistakes

- **Curvature sign.** The cap needs |κ|; a signed curvature makes left-hand corners unlimited.
- **Dividing by a zero curvature.** On a straight κ_ahead is 0; the cap must fall back to `TARGET_SPEED` (the agent uses κ > 1e-9).
- **Reading μ off the edge.** The edge is a little under μg because steering, tracking and the speed loop use some of the grip; "the edge is 9.5, so μ = 0.97" over-reads one sweep. Unit 8 measures μ properly.
- **Calling a run clean because it finished.** A car 2 m off the line at speed is near the wall on CARLA; the clean rule checks the cross-track error too.
- **Reading the hidden car.** The carla-like car's parameters are deliberately hidden. Students identify them from logs in Unit 8; nobody reads the module that holds them.

## Discussion prompts

- The kinematic car never spins. Which assumption of the kinematic bicycle fails first as the speed rises?
- The cap is clean at 9.5 m/s² on `test-circuit` but spins at 9.5 on `monza-like`. What is different about the corners?
- Why ship A_LAT = 6 when 7 is clean on the carla-like car without noise? (Exercise 6 races 7 with the actuator noise on.)
- The cap looks only 50 m ahead. What goes wrong if the car arrives at a hairpin at 45 m/s?

## Differentiation

- **Support:**
  - give the skidpad loop and have students write only the lateral-acceleration calculation and the plot;
  - give the cap function's skeleton (the `min`, the `sqrt`, the zero-curvature guard) and have them fill in the formula.
- **Core:** all non-stretch exercises unaided, plus the A_LAT sweep on one track.
- **Stretch:**
  - the friction circle under combined braking and cornering on the skidpad (brake while turning, find where it spins);
  - the effect of the curvature horizon (25 vs 10 waypoints) on the clean edge, in at most three races;
  - for strong students: from the lesson's model, show why the car is neutral-steer (the same cornering stiffness per unit load at both axles), and argue what load transfer under braking would change (Exercise 7 asks why braking in a corner does not spin this car).
