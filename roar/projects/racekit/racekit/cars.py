"""Car models (design 013 §4.4). roar-001 ships the kinematic bicycle; roar-004 adds the dynamic
and carla-like cars behind the same ``Car`` protocol.

Every number a racekit car produces is a *model* number: re-measure on the official simulator.
"""

from __future__ import annotations

import math
from typing import Protocol, Tuple  # typing.Protocol exists from Python 3.8


class Car(Protocol):
    """What the runner needs from a car. State is in the ROAR frame (x forward/east, y left)."""

    x: float
    y: float
    yaw: float
    v: float

    def reset(self, x: float, y: float, yaw: float, v: float = 0.0) -> None: ...

    def advance(
        self, throttle: float, steer: float, brake: float, hand_brake: float, reverse: float,
        dt: float, substeps: int,
    ) -> None: ...

    def velocity(self) -> Tuple[float, float]: ...


class KinematicCar:
    """A kinematic bicycle about the rear axle, with a simple longitudinal map.

    * steering: ``steer`` in [-1, 1] maps to the wheel angle ``δ = -steer · δ_max`` (a positive
      steer turns right, as in the official interface); yaw rate ``v · tan δ / L``;
    * longitudinal: ``a = a_throttle · throttle`` (backwards when ``reverse``), minus
      ``a_brake · brake`` against the motion, minus quadratic drag ``c_drag · v · |v|``;
      braking stops the car, it never reverses it;
    * integration: RK4 (or explicit Euler, for teaching) over ``substeps`` equal substeps per tick,
      in plain ``math`` scalars.

    The steady-state circle radius is ``L / tan δ``.
    """

    def __init__(
        self,
        wheelbase: float = 2.875,
        max_steer: float = math.radians(70.0),
        a_throttle: float = 6.0,
        a_brake: float = 8.0,
        c_drag: float = 4.0e-4,
        integrator: str = "rk4",
    ) -> None:
        if integrator not in ("rk4", "euler"):
            raise ValueError("integrator must be 'rk4' or 'euler'")
        self.wheelbase = wheelbase
        self.max_steer = max_steer
        self.a_throttle = a_throttle
        self.a_brake = a_brake
        self.c_drag = c_drag
        self.integrator = integrator
        self.x = self.y = self.yaw = self.v = 0.0

    def reset(self, x: float, y: float, yaw: float, v: float = 0.0) -> None:
        self.x, self.y, self.yaw, self.v = float(x), float(y), float(yaw), float(v)

    def velocity(self) -> Tuple[float, float]:
        return self.v * math.cos(self.yaw), self.v * math.sin(self.yaw)

    def advance(
        self, throttle: float, steer: float, brake: float, hand_brake: float, reverse: float,
        dt: float, substeps: int,
    ) -> None:
        """Advance one control tick of ``dt`` seconds with the action held constant."""
        tan_delta = math.tan(-steer * self.max_steer)
        k_yaw = tan_delta / self.wheelbase
        drive = self.a_throttle * throttle * (-1.0 if reverse >= 0.5 else 1.0)
        braking = self.a_brake * max(brake, 1.0 if hand_brake >= 0.5 else 0.0)
        c = self.c_drag
        h = dt / substeps
        x, y, yaw, v = self.x, self.y, self.yaw, self.v
        cos, sin = math.cos, math.sin

        def accel(speed: float) -> float:
            a = drive - c * speed * abs(speed)
            if speed > 0.0:
                a -= braking
            elif speed < 0.0:
                a += braking
            return a

        for _ in range(substeps):
            v_old = v
            if self.integrator == "euler":
                x += h * v * cos(yaw)
                y += h * v * sin(yaw)
                yaw += h * v * k_yaw
                v += h * accel(v)
            else:
                # RK4 on (x, y, yaw, v) with x' = v cos(yaw), y' = v sin(yaw), yaw' = v k, v' = a(v)
                k1x, k1y, k1w, k1v = v * cos(yaw), v * sin(yaw), v * k_yaw, accel(v)
                v2, w2 = v + 0.5 * h * k1v, yaw + 0.5 * h * k1w
                k2x, k2y, k2w, k2v = v2 * cos(w2), v2 * sin(w2), v2 * k_yaw, accel(v2)
                v3, w3 = v + 0.5 * h * k2v, yaw + 0.5 * h * k2w
                k3x, k3y, k3w, k3v = v3 * cos(w3), v3 * sin(w3), v3 * k_yaw, accel(v3)
                v4, w4 = v + h * k3v, yaw + h * k3w
                k4x, k4y, k4w, k4v = v4 * cos(w4), v4 * sin(w4), v4 * k_yaw, accel(v4)
                s = h / 6.0
                x += s * (k1x + 2.0 * k2x + 2.0 * k3x + k4x)
                y += s * (k1y + 2.0 * k2y + 2.0 * k3y + k4y)
                yaw += s * (k1w + 2.0 * k2w + 2.0 * k3w + k4w)
                v += s * (k1v + 2.0 * k2v + 2.0 * k3v + k4v)
            # braking (or drag) brings the car to rest; it never pushes it backwards
            if braking > 0.0:
                crossed_zero = (v_old > 0.0 > v) or (v_old < 0.0 < v)
                held_at_rest = v_old == 0.0 and abs(drive) <= braking
                if crossed_zero or held_at_rest:
                    v = 0.0
        self.x, self.y, self.v = x, y, v
        self.yaw = (yaw + math.pi) % (2.0 * math.pi) - math.pi
