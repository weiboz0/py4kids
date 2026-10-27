"""The premise races (plan roar-004 G4.3–G4.5), raced once per test session in parallel.

Every premise is a set of real races; ``race_all`` runs the declared jobs in a process pool (the
races are independent and deterministic) and returns ``{job key: [Outcome per seed]}``. The test
modules read the shared results through the session fixture ``premise`` (``conftest.py``).
"""

from __future__ import annotations

import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Sequence, Tuple

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


def race_all(jobs: Dict[str, Any], worker: Callable[[Any], List[Any]] = _race_job) -> Dict[str, List[Any]]:
    """Race every job, in parallel (one process per CPU, at most 8).

    ``worker`` races one job (a module-level function, so the spawned processes can import it);
    a job is any NamedTuple with ``track`` and ``seeds`` (and optionally ``until_crash``).
    """
    keys = list(jobs)
    # split multi-seed jobs into one task per seed, except the sequential until-crash ones
    tasks: List[Tuple[str, Any]] = []
    for key in keys:
        job = jobs[key]
        if getattr(job, "until_crash", False):
            tasks.append((key, job))
        else:
            tasks.extend((key, job._replace(seeds=(seed,))) for seed in job.seeds)
    # longest first: until-crash and long tracks
    tasks.sort(key=lambda task: (not getattr(task[1], "until_crash", False), task[1].track != "monza-like"))
    workers = max(1, min(8, os.cpu_count() or 1, len(tasks)))
    context = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=workers, mp_context=context) as pool:
        results = list(pool.map(worker, [job for _, job in tasks]))
    merged: Dict[str, List[Outcome]] = {key: [] for key in keys}
    for (key, _), outcomes in zip(tasks, results):
        merged[key].extend(outcomes)
    return merged


UNIT7_GRID_CLEAN = (3.5, 3.6, 3.7)  # global a_lat on the 0.1 grid: clean in 5/5 (probe)
UNIT7_GRID_UNCLEAN = (3.8, 3.9, 4.0)  # collisions on at least one seed (probe: 4/5, 5/5, 5/5)
# the seeds that collide, per unclean grid value (probe on the frozen prototype)
UNIT7_GRID_UNCLEAN_SEEDS = {3.8: (0, 1, 2, 4), 3.9: (0, 1, 2, 3, 4), 4.0: (0, 1, 2, 3, 4)}
UNIT7_STACK_SEEDS = (0, 4)  # the stack's colliding seeds (probe)
UNIT7_BEST_GLOBAL = 3.7
UNIT7_COMBINED = (1.35, 1.35, 1.2, 1.0, 1.0, 1.1)  # per-section knobs on top of 3.7
UNIT7_STACK = (1.5, 1.5, 1.3, 1.15, 1.0, 1.15)  # on base 3.5: each knob clean alone, the stack not


def unit7_singles():
    """The non-trivial single-section knobs of the stack (section 4's ×1 is the base run)."""
    for section, knob in enumerate(UNIT7_STACK):
        if knob != 1.0:
            grip = [1.0] * 6
            grip[section] = knob
            yield section, tuple(grip)


def premise_jobs() -> Dict[str, Job]:
    """Every premise race of the suite, keyed by name."""
    flat = (("target_speed", 20.0), ("mode", "flat"))
    limited = (("target_speed", 20.0), ("a_lat", 0.7 * 9.81), ("a_dec", 5.0), ("ahead", 60))
    jobs = {
        # G4.3: the Unit 6 premise on DynamicCar() defaults, test-circuit
        "u6-flat-dynamic": Job("test-circuit", "dynamic", flat, seeds=(0,), max_seconds=CRASH_CAP),
        "u6-limited-dynamic": Job("test-circuit", "dynamic", limited, seeds=(0,), max_seconds=1500.0),
        "u6-flat-kinematic": Job("test-circuit", "kinematic", flat, seeds=(0,), max_seconds=1500.0),
        # G4.4: noise on the carla-like car (monza-like, global 3.5, seeds 0–4)
        "noise-monza-3.5": unit7(3.5)._replace(track="monza-like"),
        # G4.5: the Unit 7 premise (clean races finish well inside the crash cap)
        "u7-combined": unit7(UNIT7_BEST_GLOBAL, UNIT7_COMBINED, max_seconds=CRASH_CAP),
        "u7-stack": unit7(3.5, UNIT7_STACK, max_seconds=CRASH_CAP),
    }
    for a_lat in UNIT7_GRID_CLEAN:
        jobs[f"u7-global-{a_lat}"] = unit7(a_lat, max_seconds=CRASH_CAP)
    for a_lat in UNIT7_GRID_UNCLEAN:  # all five seeds ([sol] content r1 B2)
        jobs[f"u7-global-{a_lat}"] = unit7(a_lat, max_seconds=CRASH_CAP)
    for section, grip in unit7_singles():
        jobs[f"u7-single-{section}"] = unit7(3.5, grip, max_seconds=CRASH_CAP)
    return jobs
