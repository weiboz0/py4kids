"""The starter agent: a re-implementation of the competition skeleton's *described* behaviour.

Clean room (design 013 §1.2, §7.4): written from the documented behaviour, not from the skeleton's
code. It steers with a proportional controller toward the waypoint three ahead of the current one,
with a gain proportional to 1/sqrt(speed), and holds 20 m/s with a proportional speed controller.

This file has the official submission shape: one ``RoarCompetitionSolution`` class with the official
constructor and ``async def initialize`` / ``async def step``. It imports only the standard library,
numpy and ``roar_py_interface``, and it runs on Python 3.8. It is the baseline the book's first
unit measures (roar-002 copies it to ``agents/unit-01.py``).
"""

from __future__ import annotations

import math
from typing import List, Optional

import numpy as np
import roar_py_interface

LOOKAHEAD_WAYPOINTS = 3  # steer toward the waypoint this many past the current one
REACHED_RADIUS = 3.0  # metres: a waypoint this close counts as reached
STEER_GAIN = 8.0  # steering gain, divided by sqrt(speed)
TARGET_SPEED = 20.0  # m/s
SPEED_GAIN = 0.05  # throttle per m/s of speed error


def wrap_angle(angle: float) -> float:
    """Wrap an angle in radians to [-pi, pi)."""
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


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

    async def step(self) -> None:
        location = self.location_sensor.get_last_gym_observation()
        yaw = float(self.rpy_sensor.get_last_gym_observation()[2])
        speed = float(np.linalg.norm(self.velocity_sensor.get_last_gym_observation()))

        self.current_index = self.advance_index(location)
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
