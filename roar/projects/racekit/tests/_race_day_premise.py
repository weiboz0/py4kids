"""The Unit 13 premise races (plan roar-013 U13.1-U13.5), raced once per test session in parallel
with ``_premise.race_all``.

Every race is on ``monza-like`` (the real race's track is known: CARLA's Monza), 3 laps, capped at
900 s (``_line_premise.MONZA_CAP``), and **every race runs ``MPC_BUDGET_MS = None``** (no wall clock
in a pinned race). ``agents/unit-13.py`` sets ``MPC_MIN_HORIZON = MPC_HORIZON``, so its budget policy
only counts slow calls (U13.0b, race-free): a timing-off race is the race that ships.

The jobs:

* ``agents/unit-13.py`` (its own shipped line and grip, raced as shipped) and settings of it, each a
  ``_robust_premise.RobustJob`` raced by ``race_robust_job`` (the clean rule's numbers from the job's
  own line, a telemetry digest), on the nominal ``carla_like(noise=True)`` or a perturbed car
  ``carla_like(noise=True, perturb=k)`` at race seed ``k mod 5``;
* ``agents/unit-07.py`` as shipped (it plans on the centreline with ``A_LAT``: no line, no grip), an
  ``_agent_premise.AgentJob`` raced by ``_line_premise.race_line_job`` (its line error is from the
  centreline), on the nominal car.

``race_race_day_job`` sends each job to its worker. The settings (plan roar-013's probes):

* ``M``: the margin on ``MU_FRACTION`` only, (0.64, 5.0, 5.0): ``unit-13.py`` with ``A_DEC = 5.0``
  (U13.3, car 41; probe p3);
* ``PURSUIT``: ``unit-13.py`` with ``STEERING = "pursuit"`` (U13.4, car 34; probe p4);
* ``HIGH_MU_0``: ``unit-13.py`` with ``MU_G[0] = 12.0`` (U13.5, race seed 0; probe p5).

**Each distinct race is raced once** (37 races): U13.1's ten, U13.2's 24 test cars, and one each for
U13.3-U13.5. The validation cars (k = 24-71) are the plan's pinned record, never re-raced here; the
test cars k = 72-95 are raced only by U13.2. Unit 13 never races ``test-circuit-seed2027`` or
``test-circuit-seed2028`` and never builds a sealed car (k >= 1000).
"""

from __future__ import annotations

from typing import Dict, List, NamedTuple, Optional, Tuple

from _agent_premise import AgentJob
from _line_premise import MEASURED_MU_G, MONZA, MONZA_CAP, race_line_job
from _premise import race_all
from _robust_premise import NO_TIMING, RobustJob, race_robust_job

U07 = "unit-07.py"
U13 = "unit-13.py"
SEEDS5 = (0, 1, 2, 3, 4)
TEST_CARS = tuple(range(72, 96))  # U13.2: pre-registered (probe p11), raced only by the gate
MARGIN_CAR = 41  # U13.3: the one-knob margin M is not clean here (p3)
PURSUIT_CAR = 34  # U13.4: pursuit is not clean here (p4)
HIGH_MU_0 = 12.0  # U13.5: section 0's grip, far above its lower bound
FORBIDDEN = ("test-circuit-seed2027", "test-circuit-seed2028")


class Setting(NamedTuple):
    label: str  # the race key's prefix
    agent: str  # a file in agents/
    constants: Tuple[Tuple[str, object], ...]  # module constants changed (before NO_TIMING)


SHIPPED_13 = Setting("u13", U13, ())
SHIPPED_07 = Setting("u07", U07, ())
M = Setting("margin-mu-only", U13, (("A_DEC", 5.0),))  # (0.64, 5.0, 5.0)
PURSUIT = Setting("pursuit", U13, (("STEERING", "pursuit"),))
HIGH_MU = Setting("mu0-12", U13, (("MU_G", (HIGH_MU_0,) + tuple(MEASURED_MU_G[MONZA][1:])),))


def race_seed(k: int) -> int:
    return k % 5


def race_key(setting: Setting, seed: int, perturb: Optional[int] = None) -> str:
    key = f"{setting.label}|{MONZA}|s{seed}"
    return key + (f"|p{perturb}" if perturb is not None else "")


def _job(setting: Setting, seed: int, perturb: Optional[int] = None):
    assert perturb is None or perturb < 1000  # never a sealed car
    if setting.agent == U07:
        assert perturb is None and not setting.constants
        return AgentJob(U07, (), MONZA, seeds=(seed,), max_seconds=MONZA_CAP, car="carla")
    return RobustJob(setting.agent, setting.constants + NO_TIMING, MONZA, (seed,), perturb=perturb,
                     max_seconds=MONZA_CAP)


def race_day_jobs() -> Dict[str, object]:
    """Every pooled Unit 13 gate race, keyed by ``race_key``, each distinct race once. The likely
    crashes come first, so the pool starts them first."""
    jobs: Dict[str, object] = {}

    def add(setting: Setting, seed: int, perturb: Optional[int] = None) -> None:
        key = race_key(setting, seed, perturb)
        job = _job(setting, seed, perturb)
        assert job.track not in FORBIDDEN
        assert jobs.setdefault(key, job) == job, key

    # U13.3 and U13.4: the races that crash (p3, p4)
    add(M, race_seed(MARGIN_CAR), MARGIN_CAR)
    add(PURSUIT, race_seed(PURSUIT_CAR), PURSUIT_CAR)
    # U13.2: the test cars
    for k in TEST_CARS:
        add(SHIPPED_13, race_seed(k), k)
    # U13.1: the gate against Unit 7, nominal car
    for seed in SEEDS5:
        add(SHIPPED_13, seed)
        add(SHIPPED_07, seed)
    # U13.5: section 0's grip far above its lower bound
    add(HIGH_MU, 0)
    return jobs


def race_race_day_job(job) -> List[object]:
    """Race one job: ``agents/unit-07.py`` (no line) by ``race_line_job``, the rest by ``race_robust_job``."""
    if isinstance(job, AgentJob):
        return race_line_job(job)
    return race_robust_job(job)


def race_race_day_premise() -> Dict[str, List[object]]:
    return race_all(race_day_jobs(), worker=race_race_day_job)
