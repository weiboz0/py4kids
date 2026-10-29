# Checkpoint B's reference submission (plan roar-011): agents/unit-11.py with three module constants
# changed, nothing else. The race-day track, test-circuit-seed2027, was measured and solved, but
# never raced before the file was frozen:
# - MU_G: its grip, measured with Unit 8's six probes (agents/unit-07.py, A_LAT 3.5, one section's
#   knob at 3.5, one lap, the nominal carla-like car). Section 0's probe never slid (it finished
#   the lap clean), so 9.10 is a lower bound, used as measured (as Unit 8 did on monza-like).
# - LINE_CONTROL: its smoothest line (Unit 9's method, 131 control values).
# - MU_FRACTION = 0.48: tuned on the track x car family only (the five training tracks test-circuit,
#   test-circuit-seed1 ... test-circuit-seed4, each with its own line and measured grip, x the
#   training cars carla_like(perturb=k), k = 0-23), never on the race-day track or sealed cars.
#   Unit 11's expected-race-time rule picks 0.54 on that family (crashes there are rare and the
#   fallback finishes them), but 0.52 is not clean on test-circuit-seed2 and 0.50 is clean on every
#   family race: the edge is 0.50, and Unit 7's and Unit 11's margin rule ships one step below it.
#   The margin is insurance against what the family did not show: a new track is not in the family.
"""Unit 11's submission: Unit 10's file, made robust to a car that is not the one it was tuned on.

Unit 10's MPC was tuned on one car, the carla-like car as Unit 8 measured it. The real car differs
from any model of it. Unit 11 races a **family** of perturbed cars (``carla_like(perturb=k)``: grip,
steering gain, throttle, brake, mass and drag each a few per cent off, the ranges in
``PERTURBATION_FAMILY``), and adds three things:

**The fraction, re-tuned on the family.** A crash restarts the race from rest at the start (the
clock keeps running), so a crash at time ``t`` costs ``t + 1 s`` (the 1 s hold), to within a second:
on the 24 training perturbations (race seed ``k mod 5``) Unit 10's 0.58 crashes on 3 cars, 2 of them
in a crash loop (a respawn, the same corner, again, until the time cap). The expected race time over
the family (a race not finished counted at the 700 s cap) is lowest at 0.54, the highest fraction
one step inside the family's edge (0.56 is not clean on every training car). ``MU_FRACTION = 0.54``
is clean on all 24 **held-out** perturbations.

**The fallback.** A respawn is detected the way CARLA reports it: the collision sensor's impulse
norm over ``RESPAWN_IMPULSE`` (100 N s), edge-triggered (the reading differs from the previous
step's, and no respawn was handled in the last ``REFRACTORY_TICKS`` steps: CARLA's sensor may repeat
its last reading). ``fall_back()`` then clears the MPC's lag queue and plan, re-anchors the waypoint
index on the **next** step (CARLA's first step after a respawn still carries the stale crash pose),
switches the steering to ``FALLBACK_STEERING`` (pure pursuit, which needs no lag model) and
multiplies the lateral limit by ``FALLBACK_SCALE`` (again at every further respawn), re-planning
the speed profile. At 0.58 every perturbed race then finishes with at most one collision, where
Unit 10 crash-loops; on a car with one more tick of lag than Unit 8 measured, which no fraction
fixes, Unit 10 at 0.54 never finishes and this file finishes with one collision.

**The warnings (an instrument).** The sideslip ``beta`` (the velocity's direction against the
heading) over ``WARN_BETA_DEG`` and the line error over ``WARN_ERROR_M``, above ``WARN_MIN_SPEED``,
are counted in ``warnings`` in every mode, and never acted on: falling back on a sideslip warning
did not save the cars that crashed (each still crashed once, and finished later), so the mean race
time was worse than falling back on the respawn alone. ``WARN_FALLBACK = True`` (for testing) makes a
warning call ``fall_back()`` too.

With no respawn (``limit_scale`` stays 1.0) this file races exactly like ``agents/unit-10.py`` at
the same ``MU_FRACTION``.

Unit 10's MPC, unchanged:

**The model** (linearised about the line, discrete time). The state is the path-frame error on
the agent's own line points: the cross-track error ``e`` (left positive) and the heading error
``psi = yaw - segment heading``; the input is the path curvature ``u`` the car drives
(``delta = atan(L u)``). With ``sin(psi) ~ psi``, one tick of ``dt`` at speed ``v_t`` is

    ``e_{t+1} = e_t + a_t psi_t``,  ``psi_{t+1} = psi_t + a_t (u_t - kappa_t)``,  ``a_t = dt * v_t``,

with ``v_t`` the profile speed at the distance the car will have travelled and ``kappa_t`` the
line's curvature there. The model is **linear time-varying**: ``a_t`` and ``kappa_t`` change along
the horizon.

**The solve.** Stacked over the horizon the errors are ``x = G u + h`` with ``G`` and ``h`` in closed
form (``G_psi[t, j] = a_j`` for ``j <= t``; ``G_e[t, j] = a_j (S_t - S_j)``, ``S`` the running sum of
``a``). The cost ``sum q_e e^2 + q_psi psi^2 + r sum (u_t - u_{t-1})^2`` is one stacked linear
least-squares problem (Unit 8's tool), solved with ``np.linalg.lstsq`` every tick; the first ``u`` is
clipped to ``tan(MAX_STEER) / L``. The weights (``MPC_Q_E``, ``MPC_Q_PSI``, ``MPC_R_DU``) were tuned on
the **dynamic** car, on the training track only: weights that are fine on the kinematic car weave
on the straights and spin on the carla-like one.

**The lag.** The car applies each command one tick late (measured lag 1 tick, Unit 8). The model
first rolls the error through the ``MPC_LAG`` commands already queued, then plans from there;
without it (``MPC_LAG = 0``) the MPC is not clean in any of 15 family races at 0.60.

**The tick budget.** ``step()`` must stay well inside the 50 ms tick (``check_submission``: p99
<= 5 ms). The ``mpc()`` call (the model, the stack and the solve) is timed; a call over
``MPC_BUDGET_MS`` cannot be undone (its time is spent), so its command is applied anyway, it is
counted in ``over_budget``, and the horizon is **halved** for the rest of the race (40, 20, then
10, never below ``MPC_MIN_HORIZON``), printing one line each time. ``MPC_BUDGET_MS = None``
switches the timing off, so a race never depends on the machine's load. A plan that is not finite
(possible only from a non-finite input, such as a bad sensor reading) is never applied: the next
command of the last finite plan is, counted in ``fallbacks``. Pure pursuit is never used in MPC mode.

**Unit 10's fraction.** At Unit 9's 0.54 MPC is no faster than pursuit (the speed profile sets the lap
time); its gain is the tracking margin. Re-tuned on the training family by the margin rule:
MPC is clean on all 25 family races at 0.60, but not on every race at 0.62 (``test-circuit-seed1``),
so Unit 10 froze ``MU_FRACTION`` one step below that edge, at 0.58 (Unit 11 re-tunes it, above), where Unit 9's pure pursuit is not
clean on a training track (``test-circuit-seed4``). On ``test-circuit-seed2026``, never tuned on, it
is clean in 276.85 s (median of five), against Unit 9's 282.05 s.
With ``STEERING = "pursuit"`` and no respawn, this file races exactly like ``agents/unit-09.py`` at
the same ``MU_FRACTION``.

The official submission shape: one ``RoarCompetitionSolution`` class with the official constructor
and ``async def initialize`` / ``async def step``. It imports only the standard library, numpy and
``roar_py_interface``, and it runs on Python 3.8.
"""

from __future__ import annotations

import math
import time
from typing import List, Optional, Sequence, Tuple

import numpy as np
import roar_py_interface

REACHED_RADIUS = 3.0  # metres: a waypoint this close counts as reached
TARGET_SPEED = 45.0  # m/s: the top speed (the profile is at most this)
CROSS_TRACK_REACH = 8  # the projection searches segments current_index - 8 .. current_index + 8
CURVATURE_HORIZON = 25  # waypoints (about 50 m) of track to look ahead for the sharpest curvature

# Unit 3: the kinematic car's parameters (a model, not the truth; Unit 8 re-identifies them).
WHEELBASE = 2.875  # m, L
MAX_STEER = math.radians(66.0)  # rad: the full-lock wheel angle (Unit 8 measured 65.7 deg; 70 was assumed)
A_THROTTLE = 6.0  # m/s^2 at full throttle
A_BRAKE = 8.0  # m/s^2 at full brake, against the motion
C_DRAG = 4.0e-4  # 1/m: drag deceleration C_DRAG * v * |v|
CONTROL_DT = 0.05  # s: one control tick
PREDICT_TICKS = 20  # predict 1 s ahead

# Unit 4: the controllers' gains.
SPEED_KP = 0.5  # throttle per m/s of speed error
SPEED_KI = 0.1  # throttle per (m/s * s) of integrated speed error
K_E = 0.2  # rad of wheel angle per m of cross-track error (the P term)
K_HEAD = 1.0  # rad of wheel angle per rad of heading error (the D term; K_HEAD = K_D * v)
FEEDFORWARD = True  # add the curvature feedforward atan(L * kappa)

# Unit 5: the steering law, and its settings.
STEERING = "mpc"  # "mpc" (Unit 10), "pursuit", "pid" (Unit 4's law) or "stanley"
PP_K = 0.5  # s: the pure-pursuit lookahead is PP_K * speed metres ... (Unit 7: 0.5 at 45 m/s)
PP_MIN = 3.0  # m: ... but at least PP_MIN ...
PP_MAX = 40.0  # m: ... and at most PP_MAX
ST_K = 3.0  # Stanley's cross-track gain (1/s)

# Unit 6: the speed goal, and the grip it respects.
SPEED_MODE = "profile"  # "profile" (Unit 7), "cap" (Unit 6) or "flat" (Unit 5: TARGET_SPEED everywhere)
A_LAT = 4.6  # m/s^2: the lateral acceleration the cap (and the profile) allows (mu * g is about 9.81 m/s^2)

# Unit 7: the speed profile's knobs.
A_DEC = 5.0  # m/s^2: the braking the profile plans with (the backward pass)
A_ACC = 4.0  # m/s^2: the acceleration the profile allows (the forward pass)
PROFILE_LEAD_S = 0.3  # s: the goal is the profile this many seconds of travel ahead of the car ...
LEAD_MIN_M = 2.0  # m: ... but at least this far ahead
GRIP = (1.0,) * 6  # one knob per grip section, multiplying the section's lateral limit (per track)

# Unit 8: the measured grip, and the fraction of it the planner uses.
MU_G = (9.10, 9.55, 7.79, 9.35, 9.00, 7.76)  # m/s^2: measured mu * g per section (race day), or None
MU_FRACTION = 0.48  # the planner's share of the measured grip (Checkpoint B: the margin rule)

# Unit 9: the racing line, as the control values of a cubic B-spline of offsets (per track).
LINE_STEP = 10  # waypoints per control value
LINE_CONTROL = (  # m: test-circuit-seed2027's line (131 values), or None for the centreline
    -1e-12, -1e-12, -1e-12, -1e-12,
    -1e-12, -0.22602433759095442, -0.562895366926512, -0.9883055392831122,
    -1.4547991025494047, -1.9212928354254482, -2.346704667191331, -2.6835759593358564,
    -2.9096065524879204, -2.9096065524879204, -2.9096065524879204, -2.9096065524879204,
    -2.9096065524879204, -2.9096065524879204, -2.9096065524879204, -1.8130872636689046,
    1.4607520189483678, 2.9990247387313644, 2.9990247387313644, 2.9990247387313644,
    1.2740057007765435, -1.9240452723513375, -2.5499192931343533, -1.5649308982238281,
    0.1781111991293549, 1.8165051715181195, 2.418124204071616, 1.3346762489600972,
    -3.1333911596194195, -3.1333911596194195, 2.6023190033274215, 3.1333911596194195,
    -1.5332713211523847, -3.1333911596194195, -3.573082811620738, -3.573082811620738,
    -3.573082811620738, -3.573082811620738, -3.4116699132421435, -2.9107288208988376,
    -2.179513406892876, -0.2101091692940301, 2.0130905051586936, 2.9107288208988376,
    2.9107288208988376, 2.9107288208988376, 2.9107288208988376, 2.9107288208988376,
    2.1156142603136394, -0.062086425498140224, -2.1355425886566306, -2.9107288208988376,
    -3.358736568190423, -3.3216348457366602, -2.943414357849958, -2.2858766538291206,
    -1.433195865889478, -0.4634586328470278, 0.5436005664600196, 1.50866214541231,
    2.3524171356872805, 2.995099725343928, 3.358736568190423, 3.358736568190423,
    2.934713924315643, 2.6925017064490047, 0.5729913468550866, -2.6708613882603442,
    -2.934713924315643, -2.934713924315643, -2.934713924315643, -0.6084731533236695,
    0.13168731896137872, -1.1594750329080092, -2.6395387007976927, -3.2459090927872616,
    -0.9399780288019033, 3.2459090927872616, 3.1204509689117836, 3.1204509689117836,
    -2.2326909513196673, -3.1204509689117836, -3.1204509689117836, -3.1204509689117836,
    -2.7664327502946127, -2.2249966556896434, -1.521035998393298, -0.7180144857265257,
    0.13112890216444972, 0.9704866566163246, 1.745342339560437, 2.3992476016664894,
    2.8813971954437303, 3.1204509689117836, 3.120450968911783, 2.608651053527015,
    1.4656412048297887, -0.6060163941562628, -2.7710379431666214, -3.759629196726765,
    -3.759629196726765, -2.424561502186931, -0.48255074956764243, 0.7559462872984359,
    1.1924345156789988, 1.0542462944186712, 0.48570079857021153, -0.3456263624457381,
    -1.2809385483304434, -2.1500464883597648, -2.818944676490822, -3.0222223686615717,
    -2.9768477494293935, -1.1282977470008548, 2.1384229343102286, 3.0222223686615717,
    3.0222223686615717, 3.0222223686615717, 3.0222223686615717, 2.8253865837764387,
    0.2922366250001866, -1.299983590064683, -0.9390800220916528, -1e-12,
    1e-12, -1e-12, -1e-12,
)

# Unit 10: model predictive control (STEERING = "mpc"), its weights, and the tick budget.
MPC_HORIZON = 40  # ticks (2 s) planned every tick
MPC_Q_E = 0.3  # cost per m^2 of cross-track error
MPC_Q_PSI = 20.0  # cost per rad^2 of heading error
MPC_R_DU = 1000.0  # cost per (1/m)^2 of change in the curvature command from one tick to the next
MPC_LAG = 1  # ticks of actuator lag the model knows (measured lag 1 tick, Unit 8)
MPC_BUDGET_MS = 5.0  # ms: an mpc() call slower than this halves the horizon; None switches timing off
MPC_MIN_HORIZON = 10  # ticks: the horizon is never halved below this

# Unit 11: the respawn handler, the fallback, and the warnings.
RESPAWN_IMPULSE = 100.0  # N s: a collision-sensor impulse norm over this is a respawn (CARLA's signal)
REFRACTORY_TICKS = 40  # steps (2 s): a respawn handled this recently is not handled again
FALLBACK_STEERING = "pursuit"  # the steering after a respawn
FALLBACK_SCALE = 0.86  # the lateral limit is multiplied by this at every respawn
WARN_BETA_DEG = 8.0  # deg: a sideslip over this is a warning ...
WARN_ERROR_M = 1.6  # m: ... and so is a line error over this (None switches a warning off) ...
WARN_MIN_SPEED = 5.0  # m/s: ... above this speed; warnings are counted, never acted on ...
WARN_FALLBACK = False  # ... unless this is True (for testing only: a warning then calls fall_back())

State = Tuple[float, float, float, float]  # (x, y, psi, v)
Action = Tuple[float, float, float]  # (throttle, steer, brake)


def wrap_angle(angle: float) -> float:
    """Wrap an angle in radians to [-pi, pi)."""
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def to_car_frame(px: float, py: float, cx: float, cy: float, yaw: float) -> Tuple[float, float]:
    """The point (px, py) in the frame of a car at (cx, cy) with heading yaw: (forward, left)."""
    dx, dy = px - cx, py - cy
    c, s = math.cos(yaw), math.sin(yaw)
    return c * dx + s * dy, -s * dx + c * dy


def project_onto_segment(
    px: float, py: float, ax: float, ay: float, bx: float, by: float,
) -> Tuple[float, float, float]:
    """Project p onto the segment a -> b: (clamped foot parameter t, squared distance to the
    clamped foot, signed distance to the segment's line, left of a -> b positive)."""
    dx, dy = bx - ax, by - ay
    ex, ey = px - ax, py - ay
    seg2 = dx * dx + dy * dy
    t = (ex * dx + ey * dy) / seg2
    t = max(0.0, min(t, 1.0))
    fx, fy = px - (ax + t * dx), py - (ay + t * dy)
    return t, fx * fx + fy * fy, (dx * ey - dy * ex) / math.sqrt(seg2)


def menger_curvature(ax: float, ay: float, bx: float, by: float, cx: float, cy: float) -> float:
    """The signed curvature of the circle through a, b, c: 4 * area / (product of the sides),
    positive when a -> b -> c turns left."""
    cross = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)  # twice the signed area
    product = math.hypot(bx - ax, by - ay) * math.hypot(cx - bx, cy - by) * math.hypot(ax - cx, ay - cy)
    return 2.0 * cross / product


def derivatives(state: State, action: Action) -> State:
    """The kinematic bicycle with the longitudinal map: (x', y', psi', v')."""
    _, _, psi, v = state
    throttle, steer, brake = action
    kappa = math.tan(-steer * MAX_STEER) / WHEELBASE  # signed path curvature, left positive
    accel = A_THROTTLE * throttle - C_DRAG * v * abs(v)
    if v > 0.0:
        accel -= A_BRAKE * brake
    elif v < 0.0:
        accel += A_BRAKE * brake
    return v * math.cos(psi), v * math.sin(psi), v * kappa, accel


def rk4_step(state: State, action: Action, h: float) -> State:
    """One classical Runge-Kutta step of length h with the action held."""
    x, y, psi, v = state
    k1 = derivatives(state, action)
    k2 = derivatives((x + 0.5 * h * k1[0], y + 0.5 * h * k1[1], psi + 0.5 * h * k1[2], v + 0.5 * h * k1[3]), action)
    k3 = derivatives((x + 0.5 * h * k2[0], y + 0.5 * h * k2[1], psi + 0.5 * h * k2[2], v + 0.5 * h * k2[3]), action)
    k4 = derivatives((x + h * k3[0], y + h * k3[1], psi + h * k3[2], v + h * k3[3]), action)
    w = h / 6.0
    return (
        x + w * (k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0]),
        y + w * (k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1]),
        psi + w * (k1[2] + 2.0 * k2[2] + 2.0 * k3[2] + k4[2]),
        v + w * (k1[3] + 2.0 * k2[3] + 2.0 * k3[3] + k4[3]),
    )


STOP_SUBSTEPS = 10  # substeps for a tick that may end at rest (as racekit integrates every tick)


def stopping_tick(state: State, action: Action, dt: float) -> State:
    """A tick in which the car can reach rest under the brake: v' jumps at v = 0, so one RK4 step
    across the jump is wrong (it can even predict reversing). Integrate the tick exactly as racekit's
    car does: 10 RK4 substeps, with v set to 0 on a sign change or when the brake holds the car at
    rest. (Neither removes the straddle: a substep that starts just above 0 can leave the car
    creeping at a few cm/s. The point here is to agree with the car, creep included.)"""
    throttle, _, brake = action
    h = dt / STOP_SUBSTEPS
    current = state
    for _ in range(STOP_SUBSTEPS):
        v_old = current[3]
        current = rk4_step(current, action, h)
        v = current[3]
        crossed_zero = (v_old > 0.0 > v) or (v_old < 0.0 < v)
        held_at_rest = v_old == 0.0 and A_THROTTLE * throttle <= A_BRAKE * brake
        if crossed_zero or held_at_rest:
            current = (current[0], current[1], current[2], 0.0)
    return current


def predict(state: Sequence[float], actions: Sequence[Sequence[float]], dt: float = CONTROL_DT) -> State:
    """Roll the model forward one RK4 step of ``dt`` per (throttle, steer, brake) action.

    A tick in which the car could reach rest under the brake uses ``stopping_tick``: the brake is on
    and |v| is within one tick of an upper bound on the deceleration towards zero, throttle (which
    slows a reversing car) plus brake plus drag.
    Returns the final (x, y, psi, v); psi is not wrapped.
    """
    current = (float(state[0]), float(state[1]), float(state[2]), float(state[3]))
    for action in actions:
        held = (float(action[0]), float(action[1]), float(action[2]))
        v = current[3]
        towards_zero = A_THROTTLE * held[0] + A_BRAKE * held[2] + C_DRAG * v * v
        if held[2] > 0.0 and abs(v) <= towards_zero * dt:
            current = stopping_tick(current, held, dt)
        else:
            current = rk4_step(current, held, dt)
    return current


def segments_and_sections(xs: Sequence[float], ys: Sequence[float]) -> Tuple[List[float], List[int]]:
    """The length of every segment i -> i + 1 (the last one closes the lap), and the grip section
    of every waypoint: its distance along the lap from waypoint 0 as a fraction of the lap length,
    times 6, rounded down (the lap cut into six equal pieces of arc length, as racekit cuts it)."""
    count = len(xs)
    segment_length = [
        math.hypot(xs[(i + 1) % count] - xs[i], ys[(i + 1) % count] - ys[i]) for i in range(count)
    ]
    distance = [0.0]  # the distance along the lap to each waypoint
    for length in segment_length[:-1]:
        distance.append(distance[-1] + length)
    lap_length = distance[-1] + segment_length[-1]
    section = [min(int(d / lap_length * 6), 5) for d in distance]
    return segment_length, section


def normals(xs: Sequence[float], ys: Sequence[float]) -> Tuple[List[float], List[float]]:
    """The left unit normal at every waypoint: the direction from waypoint i - 1 to i + 1, turned
    90 degrees to the left (the lap is a loop, so the ends wrap)."""
    count = len(xs)
    nx, ny = [], []
    for i in range(count):
        dx = xs[(i + 1) % count] - xs[i - 1]
        dy = ys[(i + 1) % count] - ys[i - 1]
        h = math.hypot(dx, dy)
        nx.append(-dy / h)
        ny.append(dx / h)
    return nx, ny


def spline_offsets(control: Sequence[float], count: int) -> List[float]:
    """The periodic uniform cubic B-spline of ``control`` evaluated at ``count`` waypoints: waypoint
    i sits at t = i * m / count, and its offset is a weighted average of the four control values
    j - 1 .. j + 2 (mod m), j = floor(t)."""
    c = np.asarray(control, dtype=float)
    m = len(c)
    t = np.arange(count) * m / count
    j = np.floor(t).astype(int)
    u = t - j
    w0 = (1.0 - u) ** 3 / 6.0
    w1 = (3.0 * u ** 3 - 6.0 * u ** 2 + 4.0) / 6.0
    w2 = (-3.0 * u ** 3 + 3.0 * u ** 2 + 3.0 * u + 1.0) / 6.0
    w3 = u ** 3 / 6.0
    offsets = w0 * c[(j - 1) % m] + w1 * c[j % m] + w2 * c[(j + 1) % m] + w3 * c[(j + 2) % m]
    return [float(value) for value in offsets]


def corner_cap(kappa: float, a_lat: float) -> float:
    """The fastest speed through a waypoint of curvature ``kappa`` at the lateral acceleration
    ``a_lat``: ``sqrt(a_lat / |kappa|)``, but never above TARGET_SPEED (a straight has no limit)."""
    k = abs(kappa)
    return min(TARGET_SPEED, math.sqrt(a_lat / k)) if k > 1e-9 else TARGET_SPEED


def speed_profile(
    cap: Sequence[float], segment_length: Sequence[float], a_dec: float, a_acc: float,
) -> List[float]:
    """The forward-backward speed profile: start from each waypoint's cap, then

    * the backward pass (braking): ``v_i <= sqrt(v_{i+1}^2 + 2 * a_dec * ds_i)``, walking the lap
      backwards, so the car starts braking early enough to reach the corner at its cap;
    * the forward pass (accelerating): ``v_{i+1} <= sqrt(v_i^2 + 2 * a_acc * ds_i)``.

    The lap is a loop, so each pass runs twice around it: the second time round, the speeds at
    the wrap-around (the last waypoint and waypoint 0) have settled."""
    count = len(cap)
    v = list(cap)
    for _ in range(2):
        for i in range(count - 1, -1, -1):
            j = (i + 1) % count
            v[i] = min(v[i], math.sqrt(v[j] * v[j] + 2.0 * a_dec * segment_length[i]))
    for _ in range(2):
        for i in range(count):
            j = (i + 1) % count
            v[j] = min(v[j], math.sqrt(v[i] * v[i] + 2.0 * a_acc * segment_length[i]))
    return v


def pursuit_curvature(alpha: float, distance: float) -> float:
    """The curvature of the arc that leaves the car along its heading and passes through a point
    at bearing ``alpha`` (radians, left positive) and straight-line distance ``distance``:
    ``2 sin(alpha) / distance`` (left positive)."""
    return 2.0 * math.sin(alpha) / distance


def pursuit_wheel_angle(alpha: float, distance: float) -> float:
    """The wheel angle that drives that arc: ``atan(L * kappa)``, written as
    ``atan2(2 L sin(alpha), distance)`` (the same angle for a positive distance)."""
    return math.atan2(2.0 * WHEELBASE * math.sin(alpha), distance)


def stack_horizon(e: float, psi: float, a: np.ndarray, kappa: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Unit 10: the error model over a horizon of ``m = len(a)`` ticks, stacked as ``x = G u + h``.

    One tick: ``e' = e + a_t psi``, ``psi' = psi + a_t (u_t - kappa_t)`` with ``a_t = dt * v_t``.
    ``x`` is ``(e_1, psi_1, e_2, psi_2, ..., e_m, psi_m)``, the errors after each tick, starting from
    ``(e, psi)``. In closed form, with ``S_t = a_0 + ... + a_t``: the psi rows of ``G`` are ``a_j``
    (``j <= t``), the e rows ``a_j (S_t - S_j)``; ``h`` is the same model with ``u = 0``."""
    m = len(a)
    S = np.cumsum(a)
    lower = np.tril(np.ones((m, m)))
    G_psi = lower * a[None, :]
    G_e = np.tril(S[:, None] - S[None, :]) * a[None, :]
    h_psi = psi - G_psi @ kappa
    h_e = e + S * psi - G_e @ kappa
    G = np.empty((2 * m, m))
    G[0::2], G[1::2] = G_e, G_psi  # rows e_1, psi_1, e_2, psi_2, ...
    h = np.empty(2 * m)
    h[0::2], h[1::2] = h_e, h_psi
    return G, h


def least_squares_plan(G: np.ndarray, h: np.ndarray, u_last: float) -> np.ndarray:
    """Unit 10: the plan ``u`` minimising ``sum MPC_Q_E e^2 + MPC_Q_PSI psi^2`` over ``x = G u + h``
    plus ``MPC_R_DU sum (u_t - u_{t-1})^2`` (the first change is from ``u_last``, the last command
    applied), written as one stacked least-squares problem and solved with ``lstsq``."""
    m = G.shape[1]
    w = np.tile([math.sqrt(MPC_Q_E), math.sqrt(MPC_Q_PSI)], m)
    D = np.eye(m) - np.eye(m, k=-1)  # (D u)_t = u_t - u_{t-1}, and (D u)_0 = u_0 ...
    d = np.zeros(m)
    d[0] = u_last  # ... so the target d makes the first row u_0 - u_last
    rows = np.vstack([w[:, None] * G, math.sqrt(MPC_R_DU) * D])
    rhs = np.concatenate([-w * h, math.sqrt(MPC_R_DU) * d])
    return np.linalg.lstsq(rows, rhs, rcond=None)[0]


class PID:
    """A PID controller: ``kp * e + ki * (integral of e) + kd * (rate of e)``.

    ``limits=(low, high)`` is the range the actuator can follow. Outside it the actuator saturates,
    and conditional integration (anti-windup) keeps the integral from winding up: a step's error is
    integrated only if the command with it would be inside the limits, or if the error drives the
    command back towards them. ``update`` returns the unclipped command; the caller clips it.
    """

    def __init__(
        self, kp: float, ki: float = 0.0, kd: float = 0.0,
        limits: Optional[Tuple[float, float]] = None,
    ) -> None:
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.limits = limits
        self.reset()

    def reset(self) -> None:
        """Forget the integral and the previous error."""
        self.integral = 0.0
        self.previous: Optional[float] = None

    def update(self, error: float, dt: float, rate: Optional[float] = None) -> float:
        """One control step: the command for this ``error``. ``rate`` is the error's measured rate
        of change; without it the D term uses the finite difference ``(error - previous) / dt``."""
        candidate = self.integral + error * dt
        command = self.kp * error + self.ki * candidate
        if self.limits is None:
            self.integral = candidate
        else:
            low, high = self.limits
            inside = low < command < high
            unwinding = (command >= high and error < 0) or (command <= low and error > 0)
            if inside or unwinding:
                self.integral = candidate
        output = self.kp * error + self.ki * self.integral
        if self.kd:
            if rate is None:
                rate = (error - self.previous) / dt if self.previous is not None else 0.0
            output += self.kd * rate
        self.previous = error
        return output


class RoarCompetitionSolution:
    predict = staticmethod(predict)  # a loaded class exposes the model: Agent.predict(state, actions)

    def __init__(
        self,
        maneuverable_waypoints: List[roar_py_interface.RoarPyWaypoint],
        vehicle: roar_py_interface.RoarPyActor,
        camera_sensor: Optional[roar_py_interface.RoarPyCameraSensor] = None,
        location_sensor: Optional[roar_py_interface.RoarPyLocationInWorldSensor] = None,
        velocity_sensor: Optional[roar_py_interface.RoarPyVelocimeterSensor] = None,
        rpy_sensor: Optional[roar_py_interface.RoarPyRollPitchYawSensor] = None,
        occupancy_map_sensor: Optional[roar_py_interface.RoarPyOccupancyMapSensor] = None,
        collision_sensor: Optional[roar_py_interface.RoarPyCollisionSensor] = None,
    ) -> None:
        self.maneuverable_waypoints = maneuverable_waypoints
        self.vehicle = vehicle
        self.camera_sensor = camera_sensor
        self.location_sensor = location_sensor
        self.velocity_sensor = velocity_sensor
        self.rpy_sensor = rpy_sensor
        self.occupancy_map_sensor = occupancy_map_sensor
        self.collision_sensor = collision_sensor
        self.current_index = 0

        # Plain-float copies of the waypoints, and the curvature at each one (cyclic triples).
        self.xs = [float(waypoint.location[0]) for waypoint in maneuverable_waypoints]
        self.ys = [float(waypoint.location[1]) for waypoint in maneuverable_waypoints]
        count = len(self.xs)
        # Unit 9: move the path onto the racing line, along each waypoint's left normal.
        self.offsets = [0.0] * count
        if LINE_CONTROL is not None:
            if len(LINE_CONTROL) != count // LINE_STEP:
                raise ValueError(f"LINE_CONTROL has {len(LINE_CONTROL)} values, this track needs "
                                 f"{count // LINE_STEP}: the line was solved for another track")
            self.offsets = spline_offsets(LINE_CONTROL, count)
            nx, ny = normals(self.xs, self.ys)
            self.xs = [self.xs[i] + self.offsets[i] * nx[i] for i in range(count)]
            self.ys = [self.ys[i] + self.offsets[i] * ny[i] for i in range(count)]
        self.curvature = [
            menger_curvature(self.xs[i - 1], self.ys[i - 1], self.xs[i], self.ys[i],
                             self.xs[(i + 1) % count], self.ys[(i + 1) % count])
            for i in range(count)
        ]
        # Unit 7: the speed profile, planned once for the whole lap (Unit 11: and again at a fall-back,
        # with the lateral limit times limit_scale, FALLBACK_SCALE per fall-back).
        self.limit_scale = 1.0
        self.segment_length, self.section = segments_and_sections(self.xs, self.ys)
        self.cap = [corner_cap(self.curvature[i], self.lateral_limit(self.section[i])) for i in range(count)]
        self.profile = speed_profile(self.cap, self.segment_length, A_DEC, A_ACC)
        # The instruments: measured every tick, not yet used for control.
        self.cross_track_error = 0.0
        self.segment_index = 0
        self.curvature_ahead = 0.0
        self.predicted_state = (0.0, 0.0, 0.0, 0.0)  # Unit 3: (x, y, psi, v) 1 s ahead, action held
        # Unit 4: the controllers (the speed's limits are the throttle's).
        self.speed_pid = PID(kp=SPEED_KP, ki=SPEED_KI, limits=(0.0, 1.0))
        self.steer_pid = PID(kp=K_E, kd=K_HEAD)
        # Unit 10: the MPC's memory. Every applied curvature command goes into the lag queue and
        # becomes mpc_last (the next tick's change-cost starts from it).
        self.mpc_last = 0.0  # 1/m: the last curvature command applied
        self.mpc_queue = [0.0] * MPC_LAG  # the commands sent but not yet acting (oldest first)
        self.horizon = MPC_HORIZON  # ticks: what mpc() plans with (the budget policy halves it)
        self.plan: Optional[np.ndarray] = None  # the last finite plan (1/m per tick) ...
        self.plan_used = 0  # ... and how many of its commands have been applied
        self.over_budget = 0  # mpc() calls slower than MPC_BUDGET_MS
        self.fallbacks = 0  # ticks whose plan was not finite
        # Unit 11: the respawn handler's memory, the fallback's state and the instruments.
        self.ticks = 0  # step() calls so far
        self.last_impulse: Optional[Tuple[float, ...]] = None  # the previous step's collision reading
        self.respawn_tick: Optional[int] = None  # the step the last respawn was handled on
        self.respawns = 0  # respawns handled
        self.reanchor = False  # True: the next step re-anchors the waypoint index
        self.mode = "primary"  # "primary" (STEERING) or "fallback" (FALLBACK_STEERING)
        self.beta = 0.0  # deg: the sideslip on the last step
        self.warnings = 0  # steps with a warning (sideslip or line error)

    def lateral_limit(self, section: int) -> float:
        """Unit 8: the lateral acceleration the cap allows in a grip section, MU_FRACTION of the
        measured mu * g there (times the section's knob); without a measurement, Unit 7's A_LAT.
        Unit 11: times ``limit_scale`` (1.0 until the first fall-back)."""
        if MU_G is None:
            return self.limit_scale * A_LAT * GRIP[section]
        return self.limit_scale * MU_FRACTION * MU_G[section] * GRIP[section]

    async def initialize(self) -> None:
        # Start from the waypoint nearest the car.
        location = self.location_sensor.get_last_gym_observation()
        self.current_index = self.nearest_index(location)

    def nearest_index(self, location: np.ndarray) -> int:
        """The index of the path point (on the line) nearest the car."""
        px, py = float(location[0]), float(location[1])
        distances = [math.hypot(px - x, py - y) for x, y in zip(self.xs, self.ys)]
        return int(np.argmin(distances))

    def advance_index(self, location: np.ndarray) -> int:
        """Search forward from the current index for the first path point (on the line) within
        REACHED_RADIUS."""
        px, py = float(location[0]), float(location[1])
        count = len(self.xs)
        for step in range(count):
            index = (self.current_index + step) % count
            if math.hypot(px - self.xs[index], py - self.ys[index]) < REACHED_RADIUS:
                return index
        return self.current_index

    def measure(self, px: float, py: float) -> None:
        """Update the cross-track error and the curvature ahead (the window is anchored at
        current_index: the smallest clamped-foot distance wins, ties to the first segment)."""
        xs, ys, count = self.xs, self.ys, len(self.xs)
        best_d2, best_segment, best_offset = math.inf, self.current_index, 0.0
        for k in range(self.current_index - CROSS_TRACK_REACH, self.current_index + CROSS_TRACK_REACH + 1):
            i = k % count
            j = (i + 1) % count
            _, d2, offset = project_onto_segment(px, py, xs[i], ys[i], xs[j], ys[j])
            if d2 < best_d2:
                best_d2, best_segment, best_offset = d2, i, offset
        self.segment_index = best_segment
        self.cross_track_error = best_offset

        sharpest = 0.0
        for k in range(self.current_index, self.current_index + CURVATURE_HORIZON):
            kappa = self.curvature[k % count]
            if abs(kappa) > abs(sharpest):
                sharpest = kappa
        self.curvature_ahead = sharpest

    def pursuit(self, px: float, py: float, yaw: float, speed: float) -> float:
        """Pure pursuit: the wheel angle toward the first waypoint after segment_index that is at
        least the lookahead distance away."""
        xs, ys, count = self.xs, self.ys, len(self.xs)
        lookahead = min(max(PP_K * speed, PP_MIN), PP_MAX)
        k = self.segment_index
        tx, ty = xs[k], ys[k]
        for _ in range(count):
            k = (k + 1) % count
            tx, ty = xs[k], ys[k]
            if math.hypot(tx - px, ty - py) >= lookahead:
                break
        forward, left = to_car_frame(tx, ty, px, py, yaw)
        alpha = math.atan2(left, forward)  # the target's bearing, left positive
        distance = math.hypot(forward, left)
        return pursuit_wheel_angle(alpha, distance)

    def stanley(self, px: float, py: float, yaw: float, speed: float) -> float:
        """Stanley: the segment heading error plus atan2(-ST_K * e_f, max(v, 1)), with e_f the
        front axle's cross-track error."""
        xs, ys, count = self.xs, self.ys, len(self.xs)
        fx = px + WHEELBASE * math.cos(yaw)
        fy = py + WHEELBASE * math.sin(yaw)
        i = self.segment_index
        # The front axle (L = 2.875 m ahead, waypoints about 2 m apart) lands on segment i + 1 or
        # i + 2; the window i - 4 .. i + 11 is wider than it needs to be.
        best_d2, best_offset, best_segment = math.inf, 0.0, i
        for k in range(i - 4, i + 12):
            a = k % count
            b = (a + 1) % count
            _, d2, offset = project_onto_segment(fx, fy, xs[a], ys[a], xs[b], ys[b])
            if d2 < best_d2:
                best_d2, best_offset, best_segment = d2, offset, a
        a = best_segment
        b = (a + 1) % count
        segment_heading = math.atan2(ys[b] - ys[a], xs[b] - xs[a])
        return wrap_angle(segment_heading - yaw) + math.atan2(-ST_K * best_offset, max(speed, 1.0))

    def mpc(self, yaw: float, speed: float) -> np.ndarray:
        """Unit 10: plan ``self.horizon`` ticks of curvature commands (1/m) by LTV least squares on
        the path-frame error model. Returns the plan for the ticks after the queued commands; its
        first value is this tick's command. Nothing is clipped or stored here (``mpc_command``
        does that)."""
        count = len(self.xs)
        i = self.segment_index
        j = (i + 1) % count
        heading = math.atan2(self.ys[j] - self.ys[i], self.xs[j] - self.xs[i])
        e0 = self.cross_track_error
        p0 = wrap_angle(yaw - heading)
        n, dt = self.horizon, CONTROL_DT
        # The reference along the line: the profile speed and the curvature at the distance the
        # car will have travelled after t + 1 ticks. v_ref[t], k_ref[t] drive the transition
        # t -> t + 1, so the reference is half a step ahead. The distance starts at the start of the
        # car's segment, ignoring where the car is inside it (under 2 m). The braking side of the
        # profile is taken as given (the model assumes the speed loop follows it); the speeding-up
        # side is capped by what full throttle can reach, A_THROTTLE.
        v_ref = np.empty(n)
        k_ref = np.empty(n)
        s_need, k, travelled = 0.0, i, 0.0
        v = max(speed, 1.0)
        for t in range(n):
            s_need += v * dt
            while travelled < s_need and k - i < count:  # (the bound: never more than a lap)
                travelled += self.segment_length[k % count]
                k += 1
            v_ref[t] = max(min(self.profile[k % count], speed + A_THROTTLE * dt * (t + 1)), 1.0)
            k_ref[t] = self.curvature[k % count]
            v = v_ref[t]
        # The lag: the commands already queued act first; roll the model through them.
        e, p = e0, p0
        t0 = 0
        for u_old in self.mpc_queue:
            a_t = dt * v_ref[t0]
            e, p = e + a_t * p, p + a_t * (u_old - k_ref[t0])
            t0 += 1
        # The rest of the horizon, stacked, and the one least-squares solve.
        G, h = stack_horizon(e, p, dt * v_ref[t0:], k_ref[t0:])
        return least_squares_plan(G, h, self.mpc_last)

    def mpc_command(self, yaw: float, speed: float) -> float:
        """Unit 10: one MPC tick, with the budget policy. Times ``mpc()``, applies its first command
        (clipped to full lock), or, when the plan is not finite (or the solve fails), the next
        command of the last finite plan; queues the command for the lag and returns the wheel angle ``atan(L u)``."""
        started = time.perf_counter()
        try:
            plan: Optional[np.ndarray] = self.mpc(yaw, speed)
        except np.linalg.LinAlgError:  # lstsq gives up on a non-finite G (a non-finite input)
            plan = None
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        if plan is not None and np.all(np.isfinite(plan)):
            self.plan, self.plan_used = plan, 1
            u = float(plan[0])
        else:
            # Never apply a non-finite command: the last finite plan, shifted by one tick per use
            # (once it is used up, the last command applied).
            self.fallbacks += 1
            if self.plan is not None and self.plan_used < len(self.plan):
                u = float(self.plan[self.plan_used])
                self.plan_used += 1
            else:
                u = self.mpc_last
        u_max = math.tan(MAX_STEER) / WHEELBASE
        u = min(max(u, -u_max), u_max)
        self.mpc_last = u
        if MPC_LAG:
            self.mpc_queue.append(u)
            self.mpc_queue = self.mpc_queue[-MPC_LAG:]
        # The budget: this tick's time is already spent, so its command stands; the next ticks
        # plan a shorter horizon (halved, never below MPC_MIN_HORIZON).
        if MPC_BUDGET_MS is not None and elapsed_ms > MPC_BUDGET_MS:
            self.over_budget += 1
            shorter = max(self.horizon // 2, MPC_MIN_HORIZON)
            if shorter != self.horizon:
                print(f"unit-11: mpc() took {elapsed_ms:.2f} ms (budget {MPC_BUDGET_MS} ms): "
                      f"horizon {self.horizon} -> {shorter} ticks")
                self.horizon = shorter
        return math.atan(WHEELBASE * u)

    def profile_goal(self, speed: float) -> float:
        """Unit 7: the profile speed a lead ahead of the car. Walk forward from current_index,
        adding up segment lengths, until the path covered reaches max(PROFILE_LEAD_S * speed,
        LEAD_MIN_M); the goal is the profile at the waypoint reached. The faster the car, the
        further ahead it reads the profile, which gives the speed loop time to brake."""
        count = len(self.profile)
        lead = max(PROFILE_LEAD_S * speed, LEAD_MIN_M)
        j, ahead = self.current_index, 0.0
        while ahead < lead:
            ahead += self.segment_length[j % count]
            j += 1
        return self.profile[j % count]

    def respawned(self) -> bool:
        """Unit 11: was the car respawned before this step? The collision sensor's impulse norm is
        over RESPAWN_IMPULSE, the reading is not the previous step's (edge-triggered: CARLA's sensor
        may repeat its last reading), and no respawn was handled in the last REFRACTORY_TICKS steps."""
        if self.collision_sensor is None:
            return False
        reading = tuple(float(value) for value in np.ravel(self.collision_sensor.get_last_gym_observation()))
        previous, self.last_impulse = self.last_impulse, reading
        if float(np.linalg.norm(reading)) <= RESPAWN_IMPULSE or reading == previous:
            return False
        return self.respawn_tick is None or self.ticks - self.respawn_tick >= REFRACTORY_TICKS

    def fall_back(self) -> None:
        """Unit 11: forget the MPC's queue and plan, re-anchor the waypoint index on the next step (this
        step's pose may be the stale crash pose), switch to FALLBACK_STEERING, and multiply the
        lateral limit by FALLBACK_SCALE, re-planning the speed profile."""
        self.mpc_queue = [0.0] * MPC_LAG
        self.mpc_last = 0.0
        self.plan, self.plan_used = None, 0
        self.reanchor = True
        self.mode = "fallback"
        self.limit_scale *= FALLBACK_SCALE
        count = len(self.xs)
        self.cap = [corner_cap(self.curvature[i], self.lateral_limit(self.section[i])) for i in range(count)]
        self.profile = speed_profile(self.cap, self.segment_length, A_DEC, A_ACC)

    def warn(self, velocity: np.ndarray, yaw: float, speed: float) -> bool:
        """Unit 11: the instruments. The sideslip ``beta`` (degrees: the velocity's direction minus
        the heading) and the line error, checked above WARN_MIN_SPEED; a step with either over its
        threshold is counted in ``warnings``. Returns True on a warning."""
        self.beta = math.degrees(wrap_angle(math.atan2(float(velocity[1]), float(velocity[0])) - yaw))
        if speed <= WARN_MIN_SPEED:
            return False
        sliding = WARN_BETA_DEG is not None and abs(self.beta) > WARN_BETA_DEG
        off_line = WARN_ERROR_M is not None and abs(self.cross_track_error) > WARN_ERROR_M
        if sliding or off_line:
            self.warnings += 1
            return True
        return False

    async def step(self) -> None:
        location = self.location_sensor.get_last_gym_observation()
        yaw = float(self.rpy_sensor.get_last_gym_observation()[2])
        velocity = self.velocity_sensor.get_last_gym_observation()
        speed = float(np.linalg.norm(velocity))
        self.ticks += 1

        # Unit 11: a respawn falls back; the step after it re-anchors (this step's pose may be stale).
        if self.respawned():
            self.respawns += 1
            self.respawn_tick = self.ticks
            self.fall_back()
        elif self.reanchor:
            self.current_index = self.nearest_index(location)
            self.reanchor = False

        self.current_index = self.advance_index(location)
        self.measure(float(location[0]), float(location[1]))
        count = len(self.maneuverable_waypoints)

        # Unit 11: the warnings, counted in every mode (acted on only with WARN_FALLBACK).
        if self.warn(velocity, yaw, speed) and WARN_FALLBACK and self.mode == "primary":
            self.fall_back()

        i = self.segment_index
        steering = STEERING if self.mode == "primary" else FALLBACK_STEERING
        if steering == "mpc":
            delta = self.mpc_command(yaw, speed)
        elif steering == "pursuit":
            delta = self.pursuit(float(location[0]), float(location[1]), yaw, speed)
        elif steering == "stanley":
            delta = self.stanley(float(location[0]), float(location[1]), yaw, speed)
        elif steering == "pid":
            # Unit 4: the error is -e (the line is at e = 0); its rate is v * sin(psi_e), so the
            # measured heading error psi_e is the D term's rate (K_HEAD = K_D * v).
            j = (i + 1) % count
            segment_heading = math.atan2(self.ys[j] - self.ys[i], self.xs[j] - self.xs[i])
            psi_e = wrap_angle(segment_heading - yaw)
            delta = self.steer_pid.update(-self.cross_track_error, CONTROL_DT, rate=psi_e)
            if FEEDFORWARD:
                delta += math.atan(WHEELBASE * self.curvature[i])  # hold the corner without an error
        else:
            raise ValueError(f"unknown steering {steering!r}")
        # A positive steer turns right: the wheel angle delta = -steer * MAX_STEER.
        steer = float(np.clip(-delta / MAX_STEER, -1.0, 1.0))

        # The speed goal: Unit 7's profile, a lead ahead; Unit 6's cap from the sharpest corner
        # ahead, v_max = sqrt(A_LAT / |kappa|); or Unit 5's flat TARGET_SPEED.
        if SPEED_MODE == "profile":
            goal = self.profile_goal(speed)
        elif SPEED_MODE == "cap":
            goal = corner_cap(self.curvature_ahead, A_LAT)
        elif SPEED_MODE == "flat":
            goal = TARGET_SPEED
        else:
            raise ValueError(f"unknown SPEED_MODE {SPEED_MODE!r}")

        # Speed: PI toward the goal, split into throttle and brake.
        speed_command = self.speed_pid.update(goal - speed, CONTROL_DT)
        throttle = float(np.clip(speed_command, 0.0, 1.0))
        brake = float(np.clip(-speed_command, 0.0, 1.0))

        # Unit 3: where the car will be in 1 s if it holds this action (measured, not used).
        now = (float(location[0]), float(location[1]), yaw, speed)
        self.predicted_state = predict(now, [(throttle, steer, brake)] * PREDICT_TICKS)

        await self.vehicle.apply_action({
            "throttle": throttle,
            "steer": steer,
            "brake": brake,
            "hand_brake": 0.0,
            "reverse": 0,
            "target_gear": 0,
        })
