"""Unit 2's submission: the starter's driving, plus the instruments of track geometry.

The control law is the starter's, unchanged (``agents/unit-01.py``): steer toward the waypoint three
ahead of the current one with a gain proportional to 1/sqrt(speed), and hold 20 m/s with a
proportional speed controller. This file races exactly like the starter.

What Unit 2 adds is measurement. Every tick ``step()`` computes, and stores on ``self``:

* ``cross_track_error``: the signed distance from the centreline (m, left positive), from a windowed
  projection onto the waypoint polyline. The window is anchored at ``self.current_index`` (the
  starter's reached-radius index), so it can never drift away from the driving index, and a respawn
  is handled for free;
* ``segment_index``: the polyline segment that error was measured against;
* ``curvature_ahead``: the signed Menger curvature (1/m, left turns positive) of largest magnitude
  among the next ``CURVATURE_HORIZON`` waypoints: what is coming.

None of them feeds the controls yet. Units 4 and 5 build controllers that use them.

The official submission shape: one ``RoarCompetitionSolution`` class with the official constructor
and ``async def initialize`` / ``async def step``. It imports only the standard library, numpy and
``roar_py_interface``, and it runs on Python 3.8.
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

import numpy as np
import roar_py_interface

LOOKAHEAD_WAYPOINTS = 3  # steer toward the waypoint this many past the current one
REACHED_RADIUS = 3.0  # metres: a waypoint this close counts as reached
STEER_GAIN = 8.0  # steering gain, divided by sqrt(speed)
TARGET_SPEED = 20.0  # m/s
SPEED_GAIN = 0.05  # throttle per m/s of speed error
CROSS_TRACK_REACH = 8  # the projection searches segments current_index - 8 .. current_index + 8
CURVATURE_HORIZON = 25  # waypoints (about 50 m) of track to look ahead for the sharpest curvature


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


class RoarCompetitionSolution:
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

        await self.vehicle.apply_action({
            "throttle": throttle,
            "steer": steer,
            "brake": brake,
            "hand_brake": 0.0,
            "reverse": 0,
            "target_gear": 0,
        })
