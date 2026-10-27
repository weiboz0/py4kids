"""Checkpoint A's races (plan roar-007 CP.2-CP.4), raced once per test session in parallel with
``_premise.race_all``.

Each job races ``agents/unit-07.py`` with ``A_LAT`` changed through ``write_variant`` (or the shipped
``agents/checkpoint-a.py`` / ``agents/unit-06.py`` unchanged) on ``carla_like(noise=True)``, race
seeds 0-4, capped at 450 s, through ``_agent_premise``'s ``AgentJob`` / ``race_agent_job``. The
results are ``{job key: [AgentOutcome per seed]}``, read through the session fixture
``checkpoint_a`` (``conftest.py``).

The tracks are loaded by their LITERAL generated names. The carla-like car draws its hidden grip
from the track name, so renaming a track changes the car raced on it and invalidates every pin.
"""

from __future__ import annotations

from typing import Dict, List

from _agent_premise import AgentJob, AgentOutcome, race_agent_job
from _premise import SEEDS, race_all

CAP = 450.0  # s: the gates' cap (a clean lap takes about 320 s; the probes used 1500 s)
BASE = "test-circuit"
TRAINING = ("test-circuit", "test-circuit-seed1", "test-circuit-seed2", "test-circuit-seed3",
            "test-circuit-seed4")
CHECKPOINT = "test-circuit-seed2026"

# the gate-bearing cells only (plan roar-007 "Where each gate is asserted"): 18 cells, 90 races
A_LAT_CELLS = {
    "test-circuit": (4.2, 4.4, 4.6, 4.8, 5.0),
    "test-circuit-seed1": (4.2, 4.4, 4.6),
    "test-circuit-seed2": (4.2, 4.4),
    "test-circuit-seed3": (4.2, 4.4),
    "test-circuit-seed4": (4.2, 4.4),
    "test-circuit-seed2026": (4.4, 4.6),  # its 4.2 cell is agents/checkpoint-a.py itself
}


def cell_key(track: str, a_lat: float) -> str:
    return f"cp-a-{track}-{a_lat}"


CHECKPOINT_RACE = "cp-a-race-day"  # agents/checkpoint-a.py on the checkpoint track
UNIT_06_RACE = "cp-a-unit-06"  # agents/unit-06.py on the checkpoint track


def checkpoint_a_jobs() -> Dict[str, AgentJob]:
    """Every Checkpoint A gate race, keyed by name."""
    jobs: Dict[str, AgentJob] = {}
    for track, values in A_LAT_CELLS.items():
        for a_lat in values:
            jobs[cell_key(track, a_lat)] = AgentJob("unit-07.py", (("A_LAT", a_lat),), track, seeds=SEEDS,
                                                    max_seconds=CAP, car="carla")
    jobs[CHECKPOINT_RACE] = AgentJob("checkpoint-a.py", (), CHECKPOINT, seeds=SEEDS, max_seconds=CAP, car="carla")
    jobs[UNIT_06_RACE] = AgentJob("unit-06.py", (), CHECKPOINT, seeds=SEEDS, max_seconds=CAP, car="carla")
    return jobs


def race_checkpoint_a() -> Dict[str, List[AgentOutcome]]:
    return race_all(checkpoint_a_jobs(), worker=race_agent_job)
