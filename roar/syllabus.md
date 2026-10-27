# Applied Python: Autonomous Racing

*Build a competitive ROAR agent, from waypoints to optimal control.*

This is an advanced, applied book.
Its goal is practical: a strong student finishes it able to enter the Berkeley ROAR Simulation Racing Series
with an agent that reaches a reasonable ranking.
It assumes Python fluency well beyond *Python by Projects*
(classes, modules, comprehensions, exceptions, type hints, and using `async def` and `await`),
comfort with NumPy,
and the mathematics of a student who has studied calculus:
derivatives and integrals, trigonometry, and vectors with the dot product.
Those assumptions are declared in `curriculum/baseline.yaml`.
Everything the book itself teaches, including matrices as linear maps, least squares, linearization,
and the statistics of repeated measurements, is introduced before it is used and practised before it is assessed.

## The through-line

One project runs the length of the book: **a single competition submission file, upgraded unit by unit.**
The file has exactly the shape the real race expects:
one class with the official constructor, an asynchronous `initialize` and `step`, and a control dictionary for the car.
It may import only the standard library, NumPy and the race's own interface, and it must run on Python 3.8.
Every unit adds or replaces a technique inside that file,
and every unit measures the result against the race clock.

## How the book is organised

**Part 1: A car that finishes clean laps.**
The race rules and the starter agent, measured with repeated runs, a median and a spread;
the geometry of a track (frames, heading, angle wrapping, cross-track error, curvature);
a model of the car and how to integrate it;
PID control and geometric steering with pure pursuit;
grip, the friction circle and the speed limit a corner imposes;
and speed planning that brakes before the corner.
The part closes with Checkpoint A, a complete clean agent on a track it was not tuned for.

**Part 2: Measuring the real car.**
System identification from logged telemetry with least squares;
the racing line and the honest question of whether it helps;
model predictive control within a fixed compute budget per tick;
and robustness, because a single crash sends the car back to the start with its progress reset, so the race begins again while the clock keeps running.
The part closes with Checkpoint B, a full agent under parameter uncertainty.

**Part 3: Going fast.**
Tuning against race time when run-to-run noise is larger than the gains you are chasing,
with noise-aware acceptance and held-out tracks;
then race day, which assembles, qualifies and packages the submission without introducing anything new.
The book ends with a capstone: the agent you submit, with an engineering report that shows what each stage bought.

## Working method

The book's simulator, `racekit`, is a harness and never part of a submission.
It runs a submission file under the real race rules:
a fixed control tick, three laps, progress measured over a short forward window of waypoints,
and a crash that sends the car back to the start line, holds it there for a second
and resets its progress to zero, so the race starts again while the clock keeps running.
Tracks are produced by seeded generation scripts, never copied from the official map.
Every number `racekit` produces is a *model* number:
units with a real-simulator lab show how to re-measure gains, grip and lap times on the official simulator.
Comparisons are noise-aware: one agent beats another only by more than the spread of repeated runs.

## Units

| # | Id | Kind | Lessons | The question it answers |
|---|----|------|---------|-------------------------|
| 1 | `unit-01-the-race-and-baseline` | unit | 3 | How fast is the official starter agent, and where does it lose time? Race rules, telemetry, sector splits and honest repeated-run measurement. |
| 2 | `unit-02-track-geometry` | unit | 3 | The starter steers at a point three waypoints ahead and never looks further: where exactly is the car relative to the track, and what is coming? Frames, heading, angle wrapping, projection, cross-track error and curvature, used to measure the starter. |
| 3 | `unit-03-modelling-the-car` | unit | 3 | Where will the car be in one second? The kinematic bicycle, the longitudinal map, and Euler vs RK4 integration with their error orders. |
| 4 | `unit-04-pid-control` | unit | 3 | Hold 20 m/s, then follow the line. P, I and D; windup and anti-windup; step-response tuning; steering from the cross-track error with heading damping and a curvature feedforward. |
| 5 | `unit-05-geometric-steering` | unit | 3 | Steer like a driver looks ahead. Pure pursuit, a speed-scaled lookahead, actuator delay and Stanley: stability vs corner-cutting, decided on CARLA in the lab. |
| 6 | `unit-06-grip-and-speed-limit` | unit | 3 | Why does the car spin at Parabolica? The dynamic bicycle, tyre saturation and the friction circle, and a curvature-limited speed that removes the spin-outs. |
| 7 | `unit-07-speed-planning` | unit | 3 | Brake before the corner, and find the grip that is really there. A forward-backward speed profile, the braking and cornering trade, and per-section speed knobs tuned one at a time, then on CARLA in the lab. |
| — | `checkpoint-01-part-1` | checkpoint | 0.5 | Checkpoint A: tune one setting on a family of training tracks, then race a track it was never tuned on, once, clean and within 330 s. |

*Later units, the checkpoints and the capstone are added by the plans that follow.*
