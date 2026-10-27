"""The Unit 4 and Unit 5 premise races (plan roar-005 U4.3, U4.4, U5.3, U5.4, U5.5), raced once per
test session in parallel with ``_premise.race_all``.

Each job races a reference submission (``agents/*.py``), with some module constants changed through
``write_variant``, on ``KinematicCar(jitter=..., lag_ticks=...)`` (the default ``car="kinematic"``) or,
for Units 6-7 (plan roar-006, ``_speed_premise.py``), on ``DynamicCar()`` (``"dynamic"``),
``carla_like(noise=False)`` (``"carla0"``) or ``carla_like(noise=True)`` (``"carla"``). The results are
``{job key: [AgentOutcome per seed]}``, read through the session fixture ``agent_premise``
(``conftest.py``).
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Dict, List, NamedTuple, Tuple

from _premise import SEEDS, race_all

AGENTS = Path(__file__).resolve().parents[1] / "agents"
TRACKS = ("oval", "test-circuit", "monza-like")
JITTER = 0.05
DELAY_CAP = 400.0  # s: U5.4/U5.5 and the K_HEAD = 0 ablation race with max_seconds=400
SCORECARD_CAP = 1500.0

# The settings (plan roar-005 "The reference submissions"); the starter keeps its P speed loop.
UNIT_04: Tuple[Tuple[str, object], ...] = ()
NO_FEEDFORWARD = (("FEEDFORWARD", False),)
NO_D_TERM = (("K_HEAD", 0.0),)
PURSUIT: Tuple[Tuple[str, object], ...] = ()
STANLEY = (("STEERING", "stanley"),)
PD_ON_UNIT_05 = (("STEERING", "pid"),)  # U5.2: races exactly like agents/unit-04.py
DETUNED_PD = (("K_E", 0.05), ("K_HEAD", 0.5))
FAST = (("TARGET_SPEED", 30.0),)
LOOKAHEADS = (0.2, 0.3, 0.4, 0.5)  # PP_K, U5.5
DELAY_CONTROLLERS = {  # U5.4: name -> (agent file, constants)
    "pd": ("unit-04.py", UNIT_04),
    "stanley": ("unit-05.py", STANLEY),
    "pursuit": ("unit-05.py", PURSUIT),
    "starter": ("unit-01.py", ()),
    "detuned": ("unit-04.py", DETUNED_PD),
}


class AgentOutcome(NamedTuple):
    total_time: float
    collisions: int
    finished: bool
    rms: float  # RMS |offset| over the driving rows (held == 0)
    max_offset: float  # max |offset| over the driving rows
    spins: int = 0  # respawns caused by a spin-out (plan roar-006)


class AgentJob(NamedTuple):
    agent: str  # a file in agents/
    constants: Tuple[Tuple[str, object], ...]
    track: str
    jitter: float = JITTER
    lag_ticks: int = 0
    seeds: Tuple[int, ...] = SEEDS
    max_seconds: float = SCORECARD_CAP
    car: str = "kinematic"  # "kinematic" (jitter, lag_ticks), "dynamic", "carla0" or "carla"


def make_car(job: AgentJob):
    """A fresh car for one race of ``job``."""
    from racekit.cars import DynamicCar, KinematicCar, carla_like

    if job.car == "kinematic":
        return KinematicCar(jitter=job.jitter, lag_ticks=job.lag_ticks)
    if job.car == "dynamic":
        return DynamicCar()
    if job.car == "carla0":
        return carla_like(noise=False)
    if job.car == "carla":
        return carla_like(noise=True)
    raise ValueError(f"unknown car {job.car!r}")


def race_agent_job(job: AgentJob) -> List[AgentOutcome]:
    """Race one job (every seed in ``job.seeds``) in this process."""
    import numpy as np
    from racekit.runner import run_race
    from racekit.variants import write_variant

    constants = job.constants
    with tempfile.TemporaryDirectory() as folder:
        submission = AGENTS / job.agent
        if constants:
            key = hashlib.sha256(json.dumps([job.agent, constants]).encode()).hexdigest()[:12]
            submission = write_variant(submission, Path(folder) / f"variant_{key}.py",
                                       {name: repr(value) for name, value in constants})
        outcomes = []
        for seed in job.seeds:
            result = run_race(submission, job.track, car=make_car(job), seed=seed, max_seconds=job.max_seconds)
            telemetry = result.telemetry
            offset = np.abs(telemetry["offset"][telemetry["held"] == 0])
            outcomes.append(AgentOutcome(result.total_time, result.collisions, result.finished,
                                         float(np.sqrt(np.mean(offset ** 2))), float(np.max(offset)),
                                         result.respawn_causes.count("spin")))
    return outcomes


def agent_premise_jobs() -> Dict[str, AgentJob]:
    """Every Unit 4 / Unit 5 premise race, keyed by name."""
    jobs: Dict[str, AgentJob] = {}
    for track in TRACKS:
        # U4.2 / U5.2: the reference submissions, deterministic (jitter 0, one race each)
        for name, agent, constants in (("u4", "unit-04.py", UNIT_04), ("u5", "unit-05.py", PURSUIT),
                                       ("u5-pid", "unit-05.py", PD_ON_UNIT_05)):
            jobs[f"{name}-exact-{track}"] = AgentJob(agent, constants, track, jitter=0.0, seeds=(0,))
        # U4.3: the scorecard at 20 m/s (Unit 4 vs the starter)
        jobs[f"u4-{track}"] = AgentJob("unit-04.py", UNIT_04, track)
        jobs[f"starter-{track}"] = AgentJob("unit-01.py", (), track)
        # U4.4: no feedforward
        jobs[f"u4-noff-{track}"] = AgentJob("unit-04.py", NO_FEEDFORWARD, track)
        # U5.3: pure pursuit and Stanley at 20 m/s
        jobs[f"pursuit-{track}"] = AgentJob("unit-05.py", PURSUIT, track)
        jobs[f"stanley-{track}"] = AgentJob("unit-05.py", STANLEY, track)
    # U4.4: no D term
    jobs["u4-nod-test-circuit"] = AgentJob("unit-04.py", NO_D_TERM, "test-circuit", max_seconds=DELAY_CAP)
    # U5.4: the delay study, test-circuit at 30 m/s, lags 0 and 2
    for lag in (0, 2):
        for name, (agent, constants) in DELAY_CONTROLLERS.items():
            jobs[f"delay-{name}-lag{lag}"] = AgentJob(agent, constants + FAST, "test-circuit", lag_ticks=lag,
                                                      max_seconds=DELAY_CAP)
        # U5.5: the lookahead sweep (PP_K = 0.3 is the pursuit row above)
        for k in LOOKAHEADS:
            if k != 0.3:
                jobs[f"sweep-{k}-lag{lag}"] = AgentJob("unit-05.py", (("PP_K", k),) + FAST, "test-circuit",
                                                       lag_ticks=lag, max_seconds=DELAY_CAP)
    return jobs


def race_agent_premise() -> Dict[str, List[AgentOutcome]]:
    return race_all(agent_premise_jobs(), worker=race_agent_job)
