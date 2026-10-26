"""Unit 3's submission: Unit 2's file, plus a model of the car that can predict.

The control law is the starter's, unchanged (``agents/unit-01.py``), and so are Unit 2's
instruments (the cross-track error, its segment and the curvature ahead, measured every tick).
On racekit's kinematic car the starter neither wobbles nor cuts corners, so Units 2-3 add
instruments, not a new controller. This file races exactly like the starter.

What Unit 3 adds is the kinematic bicycle with its longitudinal map, and a rollout:

* ``predict(state, actions, dt=0.05)`` takes the state (x, y, psi, v) and a sequence of
  (throttle, steer, brake) actions, applies one RK4 step of ``dt`` per action with the action held,
  and returns the final (x, y, psi, v) (psi is not wrapped). A tick in which the car can reach rest
  under the brake is the exception: there v' jumps at v = 0, RK4's smoothness assumption fails, and
  the tick is integrated exactly the way racekit's car integrates it (10 RK4 substeps, v set to 0 on
  a sign change or when the brake holds the car at rest), so the two agree;
* every tick ``step()`` stores ``predicted_state``: where the car will be in 1 s if it holds the
  action it is about to apply. Nothing uses it for control yet.

The model's parameters are the *kinematic car's* (racekit's ``KinematicCar`` defaults). They are a
model, not the truth: Unit 8 re-identifies them from logged data.

The official submission shape: one ``RoarCompetitionSolution`` class with the official constructor
and ``async def initialize`` / ``async def step``. It imports only the standard library, numpy and
``roar_py_interface``, and it runs on Python 3.8.
"""

from __future__ import annotations

import math
from typing import List, Optional, Sequence, Tuple

import numpy as np
import roar_py_interface

LOOKAHEAD_WAYPOINTS = 3  # steer toward the waypoint this many past the current one
REACHED_RADIUS = 3.0  # metres: a waypoint this close counts as reached
STEER_GAIN = 8.0  # steering gain, divided by sqrt(speed)
TARGET_SPEED = 20.0  # m/s
SPEED_GAIN = 0.05  # throttle per m/s of speed error
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
        # The instruments: measured every tick, not yet used for control.
        self.cross_track_error = 0.0
        self.segment_index = 0
        self.curvature_ahead = 0.0
        self.predicted_state = (0.0, 0.0, 0.0, 0.0)  # Unit 3: (x, y, psi, v) 1 s ahead, action held

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

    async def step(self) -> None:
        location = self.location_sensor.get_last_gym_observation()
        yaw = float(self.rpy_sensor.get_last_gym_observation()[2])
        speed = float(np.linalg.norm(self.velocity_sensor.get_last_gym_observation()))

        self.current_index = self.advance_index(location)
        self.measure(float(location[0]), float(location[1]))
        count = len(self.maneuverable_waypoints)
        target = self.maneuverable_waypoints[(self.current_index + LOOKAHEAD_WAYPOINTS) % count]

        # Heading error toward the target, wrapped to [-pi, pi).
        to_target = target.location[:2] - location[:2]
        heading_error = wrap_angle(math.atan2(float(to_target[1]), float(to_target[0])) - yaw)

        # Steering: a positive steer turns right, so a target to the left (positive error) needs a
        # negative steer. The gain falls as 1/sqrt(speed); at a standstill, steer fully toward it.
        if speed > 1e-2:
            steer = -STEER_GAIN / math.sqrt(speed) * heading_error / math.pi
        else:
            steer = -float(np.sign(heading_error))
        steer = float(np.clip(steer, -1.0, 1.0))

        # Speed: a proportional controller toward TARGET_SPEED.
        speed_command = SPEED_GAIN * (TARGET_SPEED - speed)
        throttle = float(np.clip(speed_command, 0.0, 1.0))
        brake = float(np.clip(-speed_command, 0.0, 1.0))

        # Unit 3: where the car will be in 1 s if it holds this action (measured, not yet used).
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
