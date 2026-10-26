"""The premise races (plan roar-004 G4.3–G4.5), raced once per test session in parallel.

Every premise is a set of real races; ``race_all`` runs the declared jobs in a process pool (the
races are independent and deterministic) and returns ``{job key: [Outcome per seed]}``. The test
modules read the shared results through the session fixture ``premise`` (``conftest.py``).
"""

from __future__ import annotations

import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple

SEEDS = (0, 1, 2, 3, 4)
CRASH_CAP = 600.0  # s: the cap for races expected to crash (keeps the suite short)
UNIT7_CAP = 45.0  # m/s
UNIT7_A_DEC = 6.0  # m/s², look-ahead braking over 150 waypoints (300 m)
UNIT7_AHEAD = 150


class Outcome(NamedTuple):
    total_time: float
    collisions: int
    finished: bool
    spins: int


class Job(NamedTuple):
    """One premise: ``car`` is 'carla-noisy', 'dynamic' or 'kinematic'; ``driver`` holds the
    ``drivers.pure_pursuit`` settings; ``until_crash`` races the seeds in order and stops at the first
    one with a collision."""

    track: str
    car: str
    driver: Tuple[Tuple[str, object], ...]
    seeds: Tuple[int, ...] = SEEDS
    max_seconds: float = 1200.0
    until_crash: bool = False


def unit7(a_lat: float, grip: Optional[Sequence[float]] = None, **extra) -> Job:
    """The Unit 7 fixture: carla_like(noise=True) on test-circuit, a 45 m/s cap, 300 m of braking."""
    driver = (("target_speed", UNIT7_CAP), ("a_lat", a_lat), ("grip", tuple(grip) if grip else None),
              ("a_dec", UNIT7_A_DEC), ("ahead", UNIT7_AHEAD))
    return Job("test-circuit", "carla-noisy", driver, **extra)


def _race_job(job: Job) -> List[Outcome]:
    from drivers import pure_pursuit
    from racekit.cars import DynamicCar, KinematicCar, carla_like
    from racekit.runner import run_race

    make_car = {"carla-noisy": lambda: carla_like(noise=True), "dynamic": DynamicCar,
                "kinematic": KinematicCar}[job.car]
    outcomes = []
    for seed in job.seeds:
        result = run_race(pure_pursuit(**dict(job.driver)), job.track, car=make_car(),
                          max_seconds=job.max_seconds, seed=seed)
        outcomes.append(Outcome(result.total_time, result.collisions, result.finished,
                                result.respawn_causes.count("spin")))
        if job.until_crash and result.collisions:
            break
    return outcomes


def race_all(jobs: Dict[str, Job]) -> Dict[str, List[Outcome]]:
    """Race every job, in parallel (one process per CPU, at most 8)."""
    keys = list(jobs)
    # split multi-seed jobs into one task per seed, except the sequential until-crash ones
    tasks: List[Tuple[str, Job]] = []
    for key in keys:
        job = jobs[key]
        if job.until_crash:
            tasks.append((key, job))
        else:
            tasks.extend((key, job._replace(seeds=(seed,))) for seed in job.seeds)
    # longest first: until-crash and long tracks
    tasks.sort(key=lambda task: (not task[1].until_crash, task[1].track != "monza-like"))
    workers = max(1, min(8, os.cpu_count() or 1, len(tasks)))
    context = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=workers, mp_context=context) as pool:
        results = list(pool.map(_race_job, [job for _, job in tasks]))
    merged: Dict[str, List[Outcome]] = {key: [] for key in keys}
    for (key, _), outcomes in zip(tasks, results):
        merged[key].extend(outcomes)
    return merged


def premise_jobs() -> Dict[str, Job]:
    """Every premise race of the suite, keyed by name."""
    return {
        # G4.4: noise on the carla-like car (monza-like, global 3.5, seeds 0–4)
        "noise-monza-3.5": unit7(3.5)._replace(track="monza-like"),
    }
