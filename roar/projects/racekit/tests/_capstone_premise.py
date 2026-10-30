"""The capstone premise races (plan roar-014 C14.0-C14.1), raced once per test session in parallel
with ``_premise.race_all``.

The capstone's bar is **the starter made clean by its own knob**: ``agents/starter.py`` with
``TARGET_SPEED = 14.0`` (the fastest clean point of its grid 8-16 on this car), on ``monza-like``,
the nominal ``carla_like(noise=True)``, race seeds 0-4, 3 laps, capped at 1300 s. Each is an
``_agent_premise.AgentJob`` raced by ``_line_premise.race_line_job`` (no line in the file: its error
is from the centreline).

The capstone's reference, ``agents/unit-13.py``, is not raced here: its five nominal races are Unit
13's U13.1 races, read from the ``race_day_premise`` session fixture (``_race_day_premise.race_key``
of ``SHIPPED_13`` at seeds 0-4).

C14.0, the shipped starter at seed 0 capped at 120 s (under 1 CPU-s), is raced in its test, outside
the pool (``STARTER_CAPPED``).

This module races no perturbed car (the capstone's test cars k = 96-119 are spent, probe p10; a
student's own test cars are k = 120-143, and Unit 13's are k = 72-95), never builds a sealed car
(k >= 1000) and never races ``test-circuit-seed2027`` or ``test-circuit-seed2028``.
"""

from __future__ import annotations

from typing import Dict, List

from _agent_premise import AgentJob
from _line_premise import MONZA, race_line_job
from _premise import race_all

STARTER = "starter.py"
SEEDS5 = (0, 1, 2, 3, 4)
BAR_SPEED = 14.0  # m/s: the starter's own knob, the fastest clean point of its grid on this car (probe p3)
BAR_CAP = 1300.0  # s: a bar race takes about 1204 s
STARTER_CAP = 120.0  # s: C14.0, long enough to show the crash loop
FORBIDDEN = ("test-circuit-seed2027", "test-circuit-seed2028")
NEVER_RACED_CARS = range(72, 144)  # Unit 13's test cars, the capstone's (spent) and a student's own

BAR_CONSTANTS = (("TARGET_SPEED", BAR_SPEED),)
STARTER_CAPPED = AgentJob(STARTER, (), MONZA, seeds=(0,), max_seconds=STARTER_CAP, car="carla")


def bar_key(seed: int) -> str:
    return f"bar|{MONZA}|s{seed}"


def bar_job(seed: int) -> AgentJob:
    return AgentJob(STARTER, BAR_CONSTANTS, MONZA, seeds=(seed,), max_seconds=BAR_CAP, car="carla")


def capstone_jobs() -> Dict[str, AgentJob]:
    """Every pooled capstone race, keyed by ``bar_key``: the bar's five."""
    jobs = {bar_key(seed): bar_job(seed) for seed in SEEDS5}
    for key, job in jobs.items():
        assert job.track not in FORBIDDEN, key
        assert getattr(job, "perturb", None) is None, key  # the nominal car only
    return jobs


def race_capstone_premise() -> Dict[str, List[object]]:
    return race_all(capstone_jobs(), worker=race_line_job)
