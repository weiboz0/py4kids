"""The carla-like car's hidden parameters (plan roar-004; design 013 §4.4). Do not read this in
teaching material.

``racekit.cars.carla_like()`` is the book's stand-in for CARLA: a ``DynamicCar`` whose parameters
differ from the public defaults, with a seeded per-section grip. Units identify these numbers from
logs (Unit 8); a lesson, exercise, milestone or lab that quotes them gives the answer away. A routed
test fails if this module's name appears in any student-facing source.
"""

from __future__ import annotations

import hashlib
import math
import random
from typing import Tuple

MASS = 1845.0  # kg (shared with the DynamicCar default)
YAW_INERTIA = 3100.0  # kg m^2
LF = 1.45  # m, centre of gravity to the front axle
WHEELBASE = 2.875  # m (shared)
MAX_STEER = math.radians(66.0)
A_THROTTLE = 5.4  # m/s^2 at full throttle
A_BRAKE = 8.6  # m/s^2 at full brake
C_DRAG = 3.4e-4  # 1/m
TYRE_B = 9.0
TYRE_C = 1.45
LAG_TICKS = 1  # shared: Unit 8 finds the lag rather than recovering a changed one

NOISE_SIGMA = 0.1  # throttle jitter of carla_like(noise=True) (plan roar-004 G4.4)

GRIP_LOW = 0.78
GRIP_HIGH = 1.05
GRIP_SALT = "racekit-grip:"


def grip_table(track_name: str, sections: int = 6) -> Tuple[float, ...]:
    """The per-section μ of a track: uniform in [0.78, 1.05], rounded to 3 decimals, drawn from
    ``random.Random`` seeded by the first 16 hex digits of sha256("racekit-grip:" + name)."""
    seed = int(hashlib.sha256((GRIP_SALT + track_name).encode("utf-8")).hexdigest()[:16], 16)
    rng = random.Random(seed)
    return tuple(round(rng.uniform(GRIP_LOW, GRIP_HIGH), 3) for _ in range(sections))
