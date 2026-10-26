# Teacher notes — Unit 3: Modelling the car

## Goals

By the end of this unit students can:

- Write the **kinematic bicycle**: the state (x, y, ψ, v), the wheel angle δ = −steer·δ_max, the yaw rate
  v·tan δ / L, and the steady-state circle R = L / tan δ.
- Write the **longitudinal map**: throttle → acceleration, brake against the motion, quadratic drag. They derive
  the terminal speed and connect it to Unit 1's 19.49 m/s drag equilibrium on the straights.
- Integrate the model over a tick with the action held, with explicit **Euler** and with **RK4**. They measure the
  error orders from a convergence experiment with `log2` ratios (Euler about 2× per halving, RK4 about 16×).
- **Predict** where the car will be in one second from recorded telemetry. RK4 at one step per tick reproduces
  racekit to about 1e-8 m; Euler is off by up to about 0.38 m.
- Say clearly that these are **the model car's** parameters (L = 2.875 m, δ_max = 70°, a_throttle 6, a_brake 8,
  c_drag 4e-4). They are not CARLA's; Unit 8 re-identifies them from data.

This unit introduces three concepts:
- `kinematic-bicycle`;
- `longitudinal-map`;
- `numerical-integration`.

It does **not** change the car's behaviour. `agents/unit-03.py` races exactly like the starter and adds
`predict(state, actions, dt=0.05)`, which Units 4–5 and the model-predictive unit build on.

## Pacing

Plan for **two to three 60–90 min sittings**. There is no lab.

1. **Sitting 1: the model** (lesson §§1–3).
   - Hook: *predict where the car is in 1 s.* Have students guess before any maths, using a straight line at the
     current speed.
   - Derive R = L / tan δ from the geometry of the two wheels. Then check it numerically (47.006 m at steer 0.05).
   - Terminal speed: set dv/dt = 0. The starter's 19.49 m/s on the straights is this equilibrium, not the
     20 m/s target, because the P speed controller's throttle falls as the error shrinks.
2. **Sitting 2: integration** (lesson §§4–6).
   - Euler step by step, then RK4.
   - The Euler circle is the key picture. The trajectory is a regular polygon whose distance from the centre is off
     by about h·v/2 = 0.25 m, **bounded and independent of R**, the same in the first and the last lap: a
     half-step lag of the whole circle. Halving h halves it. Do not let students conclude that "Euler spirals out"
     here. For this model it does not.
   - The convergence experiment: the error ratios per halving give the orders 1 and 4 without any curve fitting.
3. **Sitting 3: prediction from telemetry and the reality check** (lesson §§7–8).
   - Replay recorded actions from 180 starting rows: RK4 reproduces racekit to about 1e-8 m; Euler's *median* error
     is tiny (about 2e-6 m) because the straights sit at equilibrium, but its max is about 0.38 m in the corners.
   - Close with "this is the *model* car": what changes on CARLA (grip, load transfer, actuator lag), pointing to
     Units 6 and 8.

## Common mistakes

- **Steer sign.** δ = −steer·δ_max: a positive steer turns right, so it gives a negative yaw rate. A sign slip here
  produces a car that circles the wrong way, which is easy to spot on a plot, so plot early.
- **Updating the state in place inside RK4.** Each stage must start from the step's initial state. Students who
  write `x += k1 * h / 2` before computing k2 have written something that is neither Euler nor RK4.
- **Reading the order from one pair of step sizes.** Ratios are noisy at large h (RK4's first ratio is about 16.0,
  the last about 16.1). Look at the trend over four halvings.
- **Comparing against the wrong reference.** racekit integrates with RK4 in 10 substeps of 0.005 s. One RK4 step of
  0.05 s agrees with it to about 1.7e-8 m, close enough to be a perfect predictor at this scale; ten substeps agree
  to about 1e-13.
- **Brake past zero.** The brake acts against the motion and must not drive v negative. Check the model's clamp.
- **Treating the model as the car.** Every number here is the kinematic car. A prediction that is perfect in
  racekit is only as good as the model on CARLA.

## Discussion prompts

- Euler's error on a circle is bounded here, but Euler is famous for drifting. Which property of this model keeps
  it bounded, and what kind of model would make it drift?
- RK4 costs four model evaluations per step. When is that worth it inside a 50 ms control tick?
- The median Euler prediction error is 2e-6 m but the max is 0.38 m. Which one matters for not crashing?
- If CARLA's real wheelbase were 5% longer than our L, what would the predicted circle do, and how would you
  measure it?

## Differentiation

- **Support:**
  - give the RK4 stage template and have students write only `derivatives(state, action)`;
  - pre-build the convergence table and have students fill in the ratio column.
- **Core:** all non-stretch exercises unaided, plus the prediction check against telemetry.
- **Stretch:**
  - the step size at which Euler's 1 s prediction error falls below 1 cm;
  - semi-implicit (symplectic) Euler and its order;
  - for strong students: derive the h·v/2 Euler circle shift analytically from the polygon's geometry.
