"""The data-side pure-pursuit driver (plan roar-004): one module, used by the telemetry generator
(``gen_sysid.py``) and imported by racekit's premise tests. Never student-facing.

``pure_pursuit(...)`` returns an agent class with the official submission constructor and
``async def initialize`` / ``async def step``, ready for ``racekit.runner.run_race``:

* **steering**: pure pursuit towards the waypoint about ``max(6, 0.5·v)`` m ahead, with the wheel
  angle ``atan2(2 L sin α, l_d)`` mapped to ``steer = −δ / 70°`` (clipped);
* **speed**, ``mode="limited"``: a curvature-limited speed. Each waypoint's cap is
  ``min(target_speed, √(a_lat · grip[section] / κ))``, with κ from the circle through it and its
  two neighbours and ``section`` the driver's own equal arc-length sixth of the lap; the goal is the
  lowest ``√(cap² + 2 a_dec d)`` over the next ``ahead`` waypoints (``d`` = 2 m per waypoint), and
  ``0.3 · (goal − v)`` is split into throttle and brake;
* **speed**, ``mode="flat"``: ``0.05 · (target_speed − v)``, no look-ahead (the Unit 6 failure);
* **recording** (``record=True``): every step the driver keeps one row of what it observed and what
  it commanded, as a CARLA recorder would, ``(t, x, y, yaw, vx, vy, throttle, steer, brake)``:
  the sensor readings before the action (world-frame velocity) and the commanded action (before
  any actuator jitter). ``t`` counts control ticks from the driver's own steps, adding the runner's
  1.0 s respawn hold when the collision sensor reports a major-collision impulse.

The arithmetic is the roar-004 probe drivers' (``pp.py``, ``pp_sec.py``, ``pp_flat.py``),
including the float32 sensor values, so the plan's pinned race times reproduce; only the
look-ahead minimum is vectorised (exactly: ``√`` is monotone and correctly rounded).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import numpy as np

A_LAT_DEFAULT = 0.7 * 9.81
LD_MIN = 6.0  # m: the minimum look-ahead distance
LD_GAIN = 0.5  # s: look-ahead distance per m/s of speed
WHEELBASE = 2.875  # m, the driver's model of the car
MAX_STEER = math.radians(70.0)  # the driver's model of the full-lock wheel angle
REACHED_RADIUS = 3.0  # m: a waypoint this close counts as reached
WAYPOINT_SPACING = 2.0  # m per waypoint, as the look-ahead braking assumes
LIMITED_GAIN = 0.3  # throttle per m/s of speed error (limited mode)
FLAT_GAIN = 0.05  # throttle per m/s of speed error (flat mode)
SECTIONS = 6
CONTROL_DT = 0.05
RESPAWN_HOLD_TICKS = 20
RESPAWN_IMPULSE = 100.0  # N·s, the official major-collision threshold
LOG_COLUMNS = ("t", "x", "y", "yaw", "vx", "vy", "throttle", "steer", "brake")
DECIDE_MARGIN = 1e-3  # m: a float64 distance this far from a threshold decides the float32 test


def _closer_than(point: np.ndarray, pxy: tuple[float, float], location: np.ndarray,
                 lxy: tuple[float, float], threshold: float) -> bool:
    """``np.linalg.norm(point - location[:2]) < threshold`` on the float32 sensor values, decided
    in float64 when the distance is clearly away from the threshold (the float32 norm differs from
    it by far less than ``DECIDE_MARGIN``) and by that exact numpy expression otherwise."""
    distance = math.hypot(pxy[0] - lxy[0], pxy[1] - lxy[1])
    if distance < threshold - DECIDE_MARGIN:
        return True
    if distance > threshold + DECIDE_MARGIN:
        return False
    return bool(np.linalg.norm(point - location[:2]) < threshold)


def wrap_angle(angle: float) -> float:
    """Wrap an angle in radians to [-pi, pi)."""
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def pure_pursuit(
    target_speed: float = 20.0,
    a_lat: float = A_LAT_DEFAULT,
    grip: Sequence[float] | None = None,
    a_dec: float = 5.0,
    ahead: int = 60,
    mode: str = "limited",
    record: bool = False,
) -> type:
    """A pure-pursuit agent class with these settings (see the module docstring).

    ``grip`` is the per-section multiplier of ``a_lat`` (six values, default all 1). The class's
    ``last`` attribute is the most recently constructed instance; with ``record=True`` its ``rows``
    hold the log.
    """
    if mode not in ("limited", "flat"):
        raise ValueError("mode must be 'limited' or 'flat'")
    section_grip = [1.0] * SECTIONS if grip is None else list(grip)
    if len(section_grip) != SECTIONS:
        raise ValueError(f"grip needs {SECTIONS} values")
    settings = {
        "target_speed": target_speed, "a_lat": a_lat, "grip": tuple(section_grip), "a_dec": a_dec,
        "ahead": ahead, "mode": mode, "record": record,
    }

    class PurePursuit:
        last: Any | None = None
        config = settings

        def __init__(
            self, maneuverable_waypoints: list[Any], vehicle: Any, camera_sensor: Any = None,
            location_sensor: Any = None, velocity_sensor: Any = None, rpy_sensor: Any = None,
            occupancy_map_sensor: Any = None, collision_sensor: Any = None,
        ) -> None:
            type(self).last = self
            self.maneuverable_waypoints = maneuverable_waypoints
            self.vehicle = vehicle
            self.location_sensor = location_sensor
            self.velocity_sensor = velocity_sensor
            self.rpy_sensor = rpy_sensor
            self.collision_sensor = collision_sensor
            self.current_index = 0
            self.rows: list[tuple[float, ...]] = []
            self._tick = 0
            n = len(maneuverable_waypoints)
            pts = [w.location[:2] for w in maneuverable_waypoints]
            self._points = pts
            self._xy = [(float(p[0]), float(p[1])) for p in pts]
            vcap = []
            cum = [0.0]
            for i in range(1, n):
                cum.append(cum[-1] + float(np.linalg.norm(pts[i] - pts[i - 1])))
            total = cum[-1] + float(np.linalg.norm(pts[0] - pts[-1]))
            for i in range(n):
                a_lat_i = a_lat * section_grip[min(int(cum[i] / total * SECTIONS), SECTIONS - 1)]
                a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
                ab, bc, ca = np.linalg.norm(b - a), np.linalg.norm(c - b), np.linalg.norm(a - c)
                cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
                k = abs(2 * cross / (ab * bc * ca))
                vcap.append(min(target_speed, math.sqrt(a_lat_i / k) if k > 1e-6 else target_speed))
            # the braking look-ahead, exactly as min over j of sqrt(cap[i + j]**2 + 2 a_dec (2 j)):
            # sqrt is monotone and correctly rounded, so the min commutes with it
            squares = [cap ** 2 for cap in vcap]
            self._cap_squared = np.array(squares + squares[:ahead], dtype=np.float64)
            self._braking = np.array([2 * a_dec * (WAYPOINT_SPACING * j) for j in range(ahead)])

        async def initialize(self) -> None:
            location = self.location_sensor.get_last_gym_observation()
            distances = [float(np.linalg.norm(location[:2] - point)) for point in self._points]
            self.current_index = int(np.argmin(distances))

        def advance_index(self, location: np.ndarray) -> int:
            """Search forward from the current index for the first waypoint within REACHED_RADIUS."""
            count = len(self._points)
            lxy = (float(location[0]), float(location[1]))
            for step in range(count):
                index = (self.current_index + step) % count
                if _closer_than(self._points[index], self._xy[index], location, lxy, REACHED_RADIUS):
                    return index
            return self.current_index

        async def step(self) -> None:
            location = self.location_sensor.get_last_gym_observation()
            yaw = float(self.rpy_sensor.get_last_gym_observation()[2])
            velocity = self.velocity_sensor.get_last_gym_observation()
            speed = float(np.linalg.norm(velocity))
            if record and self.collision_sensor is not None:
                impulse = self.collision_sensor.get_last_gym_observation()
                if impulse is not None and float(np.linalg.norm(impulse)) > RESPAWN_IMPULSE:
                    self._tick += RESPAWN_HOLD_TICKS

            self.current_index = self.advance_index(location)
            count = len(self._points)
            points = self._points

            # pure pursuit: the look-ahead point at distance l_d along the waypoints
            ld = max(LD_MIN, LD_GAIN * speed)
            j = self.current_index
            lxy = (float(location[0]), float(location[1]))
            xy = self._xy
            while _closer_than(points[j % count], xy[j % count], location, lxy, ld) and j < self.current_index + 200:
                j += 1
            tgt = points[j % count] - location[:2]
            alpha = wrap_angle(math.atan2(float(tgt[1]), float(tgt[0])) - yaw)
            delta = math.atan2(2.0 * WHEELBASE * math.sin(alpha), ld)
            steer = float(np.clip(-delta / MAX_STEER, -1.0, 1.0))

            if mode == "limited":
                i = self.current_index
                window = self._cap_squared[i:i + ahead] + self._braking
                goal = min(target_speed, math.sqrt(float(window.min())))
                speed_command = LIMITED_GAIN * (goal - speed)
            else:
                speed_command = FLAT_GAIN * (target_speed - speed)
            throttle = float(np.clip(speed_command, 0.0, 1.0))
            brake = float(np.clip(-speed_command, 0.0, 1.0))

            if record:
                self.rows.append((
                    self._tick * CONTROL_DT, float(location[0]), float(location[1]), yaw,
                    float(velocity[0]), float(velocity[1]), throttle, steer, brake,
                ))
                self._tick += 1
            await self.vehicle.apply_action({
                "throttle": throttle, "steer": steer, "brake": brake, "hand_brake": 0.0,
                "reverse": 0, "target_gear": 0,
            })

    PurePursuit.__name__ = "RoarCompetitionSolution"
    PurePursuit.__qualname__ = "RoarCompetitionSolution"
    return PurePursuit
