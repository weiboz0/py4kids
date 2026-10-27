# Checkpoint A's reference submission (plan roar-007): agents/unit-07.py with A_LAT = 4.2, nothing
# else changed. Unit 7's 4.6 was tuned on test-circuit alone (one grid step inside that track's
# edge, 4.8), and it is not clean on the family: on test-circuit-seed1 it collides on one race seed
# in five. So the edge was found again on the training family (test-circuit and test-circuit-seed1
# ... test-circuit-seed4, five race seeds each, the carla-like car, Unit 7's reference settings
# A_DEC 5.0, PP_K 0.5, PROFILE_LEAD_S 0.3 and GRIP all 1.0): the highest A_LAT on Unit 7's grid that
# is clean on all five tracks is 4.4. Unit 7's margin rule takes one grid step back from the edge:
# A_LAT = 4.2. It was frozen before the checkpoint track (test-circuit-seed2026) was raced, and that
# track was never used for tuning.
"""Unit 7's submission: Unit 6's file, with a planned speed profile at 45 m/s.

Unit 6's speed cap is safe and slow: it never goes above 20 m/s, and it brakes only when the corner
is already close. Unit 7 plans the whole lap's speed once, in ``__init__``, and ``SPEED_MODE`` picks
the speed goal:

* ``"profile"`` (the default): the forward-backward speed profile.

  1. The cap of every waypoint: ``min(TARGET_SPEED, sqrt(A_LAT * GRIP[section] / |kappa_i|))``,
     with ``kappa_i`` Unit 2's Menger curvature at waypoint i and ``section`` the waypoint's grip
     section (the lap cut into six equal pieces of arc length from waypoint 0).
  2. The backward pass, braking: walking the lap backwards, ``v_i <= sqrt(v_{i+1}^2 + 2 * A_DEC *
     ds_i)``. A car that must be at ``v_{i+1}`` at the next waypoint, braking at ``A_DEC``, can be
     at most this fast here: the brake starts *before* the corner.
  3. The forward pass, accelerating: ``v_{i+1} <= sqrt(v_i^2 + 2 * A_ACC * ds_i)``.

  The lap is a loop, so each pass runs twice around it and the wrap-around settles. In ``step`` the
  goal is the profile **a lead ahead of the car**: the first waypoint at least
  ``max(PROFILE_LEAD_S * speed, LEAD_MIN_M)`` metres of path ahead of ``current_index``. The lead
  is measured in seconds of travel because the speed loop needs time to brake to the profile.
  ``GRIP`` holds one knob per section, multiplying ``A_LAT`` there; they are speed knobs, not grip
  estimates (they absorb everything the planner gets wrong in that section), and they are per track,
  so this file ships them all at 1.
* ``"cap"``: Unit 6's cap; with ``TARGET_SPEED = 20``, ``PP_K = 0.3`` and ``A_LAT = 6`` this file
  races exactly like ``agents/unit-06.py``.
* ``"flat"``: Unit 5's goal, ``TARGET_SPEED`` everywhere.

At 45 m/s pure pursuit needs a longer lookahead: ``PP_K = 0.5`` is the smallest clean value (0.3 and
0.4 collide on every seed). ``A_LAT = 4.6`` at ``A_DEC = 5`` is one grid step inside the clean edge
(4.8) of the (A_LAT, A_DEC) grid on the carla-like car. ``STEERING`` still picks the steering law,
so every comparison is one ``write_variant`` away:

* ``"pursuit"`` (the default): pure pursuit. The lookahead ``L_d = clip(PP_K * v, PP_MIN, PP_MAX)``
  grows with the speed. The target is the first waypoint after ``segment_index`` whose straight-line
  distance from the car is at least ``L_d``; ``alpha`` is its bearing in the car frame (Unit 2's
  ``to_car_frame``) and ``d`` its distance. The arc through the car (tangent to its heading) and the
  target has curvature ``kappa = 2 sin(alpha) / d`` (``pursuit_curvature``), and the wheel angle that
  drives it is ``delta = atan(L * kappa)``, computed as ``atan2(2 L sin(alpha), d)``
  (``pursuit_wheel_angle``).
* ``"pid"``: Unit 4's law exactly (cross-track PD with the heading error as its D term, plus the
  curvature feedforward); with it this file races exactly like ``agents/unit-04.py``.
* ``"stanley"``: the front-axle law ``delta = wrap(segment heading - yaw) + atan2(-ST_K * e_f,
  max(v, 1))``, with ``e_f`` the cross-track error of the front axle (x + L cos yaw, y + L sin yaw).

Why pure pursuit: on a car with no actuator delay Unit 4's law follows the line more closely (pure
pursuit cuts corners), but with a delay of a couple of control ticks at speed the tighter laws go
unstable and pure pursuit, whose speed-scaled lookahead detunes it for free, stays on the track.
The real car's delay is unknown until Unit 8 measures it, so the robust choice ships.

The official submission shape: one ``RoarCompetitionSolution`` class with the official constructor
and ``async def initialize`` / ``async def step``. It imports only the standard library, numpy and
``roar_py_interface``, and it runs on Python 3.8.
"""

from __future__ import annotations

import math
from typing import List, Optional, Sequence, Tuple

import numpy as np
import roar_py_interface

REACHED_RADIUS = 3.0  # metres: a waypoint this close counts as reached
TARGET_SPEED = 45.0  # m/s: the top speed (the profile is at most this)
CROSS_TRACK_REACH = 8  # the projection searches segments current_index - 8 .. current_index + 8
CURVATURE_HORIZON = 25  # waypoints (about 50 m) of track to look ahead for the sharpest curvature

# Unit 3: the kinematic car's parameters (a model, not the truth; Unit 8 re-identifies them).
WHEELBASE = 2.875  # m, L
MAX_STEER = math.radians(70.0)  # rad: the wheel angle at |steer| = 1 (delta = -steer * MAX_STEER)
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
STEERING = "pursuit"  # "pursuit", "pid" (Unit 4's law) or "stanley"
PP_K = 0.5  # s: the pure-pursuit lookahead is PP_K * speed metres ... (Unit 7: 0.5 at 45 m/s)
PP_MIN = 3.0  # m: ... but at least PP_MIN ...
PP_MAX = 40.0  # m: ... and at most PP_MAX
ST_K = 3.0  # Stanley's cross-track gain (1/s)

# Unit 6: the speed goal, and the grip it respects.
SPEED_MODE = "profile"  # "profile" (Unit 7), "cap" (Unit 6) or "flat" (Unit 5: TARGET_SPEED everywhere)
A_LAT = 4.2  # m/s^2: the lateral acceleration the cap (and the profile) allows (mu * g is about 9.81 m/s^2)

# Unit 7: the speed profile's knobs.
A_DEC = 5.0  # m/s^2: the braking the profile plans with (the backward pass)
A_ACC = 4.0  # m/s^2: the acceleration the profile allows (the forward pass)
PROFILE_LEAD_S = 0.3  # s: the goal is the profile this many seconds of travel ahead of the car ...
LEAD_MIN_M = 2.0  # m: ... but at least this far ahead
GRIP = (1.0,) * 6  # one knob per grip section, multiplying A_LAT there (per track: tuned in the lesson)

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
        self.curvature = [
            menger_curvature(self.xs[i - 1], self.ys[i - 1], self.xs[i], self.ys[i],
                             self.xs[(i + 1) % count], self.ys[(i + 1) % count])
            for i in range(count)
        ]
        # Unit 7: the speed profile, planned once for the whole lap.
        self.segment_length, self.section = segments_and_sections(self.xs, self.ys)
        self.cap = [
            corner_cap(self.curvature[i], A_LAT * GRIP[self.section[i]]) for i in range(count)
        ]
        self.profile = speed_profile(self.cap, self.segment_length, A_DEC, A_ACC)
        # The instruments: measured every tick, not yet used for control.
        self.cross_track_error = 0.0
        self.segment_index = 0
        self.curvature_ahead = 0.0
        self.predicted_state = (0.0, 0.0, 0.0, 0.0)  # Unit 3: (x, y, psi, v) 1 s ahead, action held
        # Unit 4: the controllers (the speed's limits are the throttle's).
        self.speed_pid = PID(kp=SPEED_KP, ki=SPEED_KI, limits=(0.0, 1.0))
        self.steer_pid = PID(kp=K_E, kd=K_HEAD)

    async def initialize(self) -> None:
        # Start from the waypoint nearest the car.
        location = self.location_sensor.get_last_gym_observation()
        self.current_index = self.nearest_index(location)

    def nearest_index(self, location: np.ndarray) -> int:
        distances = [
            float(np.linalg.norm(location[:2] - waypoint.location[:2]))
            for waypoint in self.maneuverable_waypoints
        ]
        return int(np.argmin(distances))

    def advance_index(self, location: np.ndarray) -> int:
        """Search forward from the current index for the first waypoint within REACHED_RADIUS."""
        count = len(self.maneuverable_waypoints)
        for step in range(count):
            index = (self.current_index + step) % count
            waypoint = self.maneuverable_waypoints[index]
            if np.linalg.norm(location[:2] - waypoint.location[:2]) < REACHED_RADIUS:
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

    async def step(self) -> None:
        location = self.location_sensor.get_last_gym_observation()
        yaw = float(self.rpy_sensor.get_last_gym_observation()[2])
        speed = float(np.linalg.norm(self.velocity_sensor.get_last_gym_observation()))

        self.current_index = self.advance_index(location)
        self.measure(float(location[0]), float(location[1]))
        count = len(self.maneuverable_waypoints)

        i = self.segment_index
        if STEERING == "pursuit":
            delta = self.pursuit(float(location[0]), float(location[1]), yaw, speed)
        elif STEERING == "stanley":
            delta = self.stanley(float(location[0]), float(location[1]), yaw, speed)
        elif STEERING == "pid":
            # Unit 4: the error is -e (the line is at e = 0); its rate is v * sin(psi_e), so the
            # measured heading error psi_e is the D term's rate (K_HEAD = K_D * v).
            j = (i + 1) % count
            segment_heading = math.atan2(self.ys[j] - self.ys[i], self.xs[j] - self.xs[i])
            psi_e = wrap_angle(segment_heading - yaw)
            delta = self.steer_pid.update(-self.cross_track_error, CONTROL_DT, rate=psi_e)
            if FEEDFORWARD:
                delta += math.atan(WHEELBASE * self.curvature[i])  # hold the corner without an error
        else:
            raise ValueError(f"unknown STEERING {STEERING!r}")
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
