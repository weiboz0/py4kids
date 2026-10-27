# Teacher notes — Unit 4: PID control

## Goals

By the end of this unit students can:

- Explain why a **P loop needs an error** to hold a set point against a load.
  The starter's speed loop (gain 0.05) settles 0.51 m/s short of 20 m/s, because drag needs a throttle and a P loop only makes a throttle from an error.
  They derive it from the drag balance K_p·e·a_T = c·(v* − e)², which is Unit 3's terminal-speed algebra again.
- Add an **integral** term, watch it **wind up** from a standing start (28.7% overshoot, 17.7 s to settle), and cure it with **conditional integration** (0.26% and 3.55 s).
- Read and tune a **step response**: overshoot, settling time in a 2% band, steady-state error.
- Write a discrete **PID** at the 0.05 s tick, with the D term taken from a **measured rate** rather than a finite difference.
- **Steer from the cross-track error**: P on the error, the **heading error as the derivative** (ė = −v·sin ψ_e), and a **curvature feedforward** δ_ff = atan(L·κ) from Unit 2's instrument.
- Show with the scorecard that the Unit 4 agent follows the line better than the starter **beyond the noise** (RMS about 0.10 m against 0.14–0.16 m on all three tracks), and that it is faster, because it holds 20 m/s instead of 19.49.

This unit introduces four concepts:
- `pid-control`;
- `integrator-windup`;
- `step-response`;
- `cross-track-steering`.

`agents/unit-04.py` is the first agent that **changes the driving**.
Its race times fall by about 1.4–2.0% (five-seed medians; for example 870.50 → 858.55 s on `monza-like`), and its run-to-run spread nearly vanishes, because the I term corrects the throttle jitter.

## Pacing

Plan for **two to three 60–90 min sittings**. There is no lab.

1. **Sitting 1: speed** (lesson §§1–4).
   - Hook: *hold 20 m/s*. Show Unit 1's telemetry: the starter sits at 19.49 m/s on every straight. Ask why before any theory.
   - P control, and the steady-state error from the drag balance. Raise the gain: the error shrinks (0.053 at gain 0.5, 0.013 at gain 2) but never reaches 0. This is the point of the I term.
   - PI from rest: the overshoot is spectacular. Let students find the cause themselves: plot the integral while the throttle sits at 1.
   - Conditional integration, and the step-response vocabulary. A small gain grid makes tuning concrete.
2. **Sitting 2: steering** (lesson §§5–6).
   - D from a measured rate. Derive ė = −v·sin ψ_e on the board with the sign conventions (offset left positive, ψ_e = path heading − yaw). Students should see that the heading error *is* the derivative, measured without differencing noise.
   - Make the consequence explicit: K_HEAD = K_D·v, so the true damping K_D falls as 1/v. At 30 m/s the car has a third less damping than at 20 m/s with the same constant. Unit 5 needs this.
   - Feedforward: in a steady corner a P/PD law needs an error to hold the steer. The feedforward supplies the steer the corner needs, so the error can stay near 0.
   - The ablations: without the feedforward the controller is worse than the starter on `test-circuit`; without the D term it oscillates and crashes.
3. **Sitting 3: the scorecard** (lesson §§7–8).
   - The Unit 4 agent against Unit 2's scorecard, five seeds, noise-aware. Insist on the rule: a gap counts only if it is larger than both ranges.
   - The bridge: a controller that only reacts to the error at the car cannot see the corner coming, and it has no idea how late its commands arrive. Unit 5 looks ahead and meets delay.

## Common mistakes

- **Sign of the steering terms.** The law is written as a wheel angle δ (left positive) and converted with steer = −δ/δ_max. Students who mix the two get positive feedback, and the car leaves the track in the first corner. Plot the first 10 s.
- **Integrating while saturated.** The integral keeps growing while the throttle is pinned at 1. The anti-windup band is the throttle's (0, 1): integrate only when the command is inside it, or when the error would drive it back out of saturation.
- **Differentiating the error for D.** A finite difference of a jittered signal is noisy, and a set-point change produces a "derivative kick". The heading error is a cleaner measured rate (the stretch exercise shows the kick).
- **Calling the 30 s value "steady state".** The I term is slow; the error at 30 s is still settling (−0.0003). Define settling with a band and a time, not "it looks flat".
- **Claiming a win from one race.** Five seeds, median and range, and a gap larger than both ranges. This is Unit 1's rule; it is easy to forget once a plot looks convincing.

## Discussion prompts

- Why can't any finite P gain remove the steady-state error here, while a car with no drag would have none?
- The I term fixes the speed error, but the plan's steering law has no I term. What would an I term do in a long corner, and why is the feedforward a better tool for that job?
- The heading term's effective damping falls as 1/v. What would you change to keep the damping constant across speeds, and what might go wrong?
- The Unit 4 agent's run-to-run time spread is about 0.05 s against the starter's 0.35–0.65 s. Where did the noise go?

## Differentiation

- **Support:**
  - give the `PID` class skeleton (constructor, `update`, `reset`) and have students fill in `update` only;
  - give the step-response measurement helper and have students compute only overshoot and settling.
- **Core:** all non-stretch exercises unaided, plus the scorecard comparison.
- **Stretch:**
  - derivative kick: a set-point step through a finite-difference D against a measured-rate D;
  - the I term on steering vs the curvature feedforward;
  - for strong students: the closed-form time constant τ = 1/(a_T·K_P + 2c·v) of the linearized speed loop, and how well it predicts the settling times of Exercise 3 (the closed-form steady-state error is core Exercise 1).
