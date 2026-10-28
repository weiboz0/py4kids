"""The Unit 8 and Unit 9 premise races (plan roar-008 U8.2-U8.5, U9.2-U9.6), raced once per test
session in parallel with ``_premise.race_all``.

Each job is an ``_agent_premise.AgentJob`` on ``carla_like(noise=True)``: a reference submission
(``agents/unit-07.py``, ``unit-08.py`` or ``unit-09.py``) with some module constants changed through
``write_variant``. The per-track constants are written in exactly as Checkpoint A's settings were:
``MU_G`` from the grip probes (``MEASURED_MU_G``, the probe ``p6`` estimates rounded to 0.01) and
``LINE_CONTROL`` from the test-side solver (``_line_solver.py``, QR + ``bvls``), solved once per
session. On ``test-circuit`` the shipped values are raced as shipped (no override).

``race_line_job`` races one job and keeps what the gates need: the clean rule's numbers, the max
cross-track error **from the job's own line** (the centreline offset minus ``n`` at the car's
waypoint ``(progress + 1) mod n``, over driving rows; for a centreline race it is the max |offset|),
a digest of the telemetry (the equivalences are asserted to the tick), and, for the one-lap grip
probes, each section's |a| estimate.

The tracks are loaded by their LITERAL generated names: the carla-like car's hidden grip is keyed to
the track name, so a rename changes the car and invalidates every pin.
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
import multiprocessing
import os
import tempfile
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List, NamedTuple, Optional, Tuple

from _agent_premise import AGENTS, AgentJob, make_car
from _premise import SEEDS, race_all

CAP = 450.0  # s: a test-circuit race (a clean lap takes about 300 s)
MONZA_CAP = 900.0  # s: a monza-like race (a clean one takes about 500 s)
TRAINING = ("test-circuit", "test-circuit-seed1", "test-circuit-seed2", "test-circuit-seed3",
            "test-circuit-seed4")
CHECKPOINT = "test-circuit-seed2026"
MONZA = "monza-like"
BASE = "test-circuit"  # the track whose MU_G and LINE_CONTROL the agents ship

# U8.2: the grip probe (the student's Unit 7 agent, A_LAT 3.5, one section's knob at 3.5, one lap)
PROBE_A_LAT = 3.5
PROBE_KNOB = 3.5
PROBE_CAP = 300.0
PROBE_TRACKS = (BASE, MONZA)
PROBE_MIN_ROWS = 20  # a section with this many qualifying rows or fewer gives no estimate
PROBE_PERCENTILE = 99.0
G_DT = 0.05  # s: the telemetry's row spacing

# the measured mu * g per grip section (m/s^2), from the probe p6, rounded to 0.01; monza-like's
# section 0 never slid (a lower bound), and the planner uses it as measured
MEASURED_MU_G = {
    "test-circuit": (7.89, 9.72, 8.65, 7.87, 8.30, 8.14),
    "test-circuit-seed1": (7.72, 9.80, 9.36, 8.38, 9.53, 7.56),
    "test-circuit-seed2": (9.06, 8.37, 8.49, 8.86, 9.78, 9.92),
    "test-circuit-seed3": (9.55, 8.89, 8.15, 9.94, 8.50, 9.09),
    "test-circuit-seed4": (8.79, 8.53, 9.10, 8.54, 8.41, 9.97),
    "test-circuit-seed2026": (7.70, 7.69, 7.70, 9.81, 8.16, 8.04),
    "monza-like": (5.38, 8.96, 9.12, 9.14, 9.70, 7.97),
}
LINE_TRACKS = TRAINING + (CHECKPOINT, MONZA)  # U9.1: every track with a solved line
LOCAL_TRACKS = (BASE, MONZA)
STEER_70 = math.radians(70.0)  # Unit 7's assumed steering gain
STEER_66 = math.radians(66.0)  # Unit 8's measured one


class LineOutcome(NamedTuple):
    total_time: float
    collisions: int
    finished: bool
    max_offset: float  # max |offset from the centreline| over the driving rows
    line_error: float  # max |offset - n[(progress + 1) mod n]| over the driving rows (n = 0: centreline)
    digest: str  # sha256 of the telemetry and the respawn causes (the equivalences)
    sections: Tuple[Tuple[int, Optional[float]], ...]  # per section: (qualifying rows, p99 |a| or None)


def cap_for(track: str) -> float:
    return MONZA_CAP if track == MONZA else CAP


def solve_lines() -> Dict[Tuple[str, str], Tuple[float, ...]]:
    """Every line the gates race or check, ``{(track, "global" or "local"): control values}``,
    solved in parallel (about 16 s on monza-like, 3-4 s on a test-circuit track)."""
    from _line_solver import solve_track

    specs = [(track, "global") for track in LINE_TRACKS] + [(track, "local") for track in LOCAL_TRACKS]
    specs.sort(key=lambda spec: spec[0] != MONZA)  # the slow ones first
    context = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=max(1, min(8, os.cpu_count() or 1)), mp_context=context) as pool:
        return dict(zip(specs, pool.map(solve_track, specs)))


def probe_grip(section: int) -> Tuple[float, ...]:
    grip = [1.0] * 6
    grip[section] = PROBE_KNOB
    return tuple(grip)


def probe_key(track: str, section: int) -> str:
    return f"probe-{track}-{section}"


def centre_key(track: str, fraction: float) -> str:
    return f"centre-{track}-{fraction}"


def line_key(track: str, fraction: float) -> str:
    return f"line-{track}-{fraction}"


def local_key(track: str, fraction: float) -> str:
    return f"local-{track}-{fraction}"


U8_70_MONZA = "u8-70deg-monza-like-0.54"  # U8.3: the measured-mu planner at the assumed 70 degrees
U8_MONZA_EDGE = "u8-monza-like-0.62"  # U8.3: at 66 degrees
U7_66_CHECKPOINT = "u7-66deg-test-circuit-seed2026"  # U8.3: the Unit 7 reference at 66 degrees
U8_REFERENCE = "u8-reference"  # U8.5: agents/unit-08.py as shipped, on test-circuit
U8_NO_MU = "u8-mu-g-none"  # U8.5: unit-08 with MU_G = None, race seed 0 ...
U7_66 = "u7-66deg"  # ... and unit-07 at 66 degrees, race seed 0
U9_REFERENCE = line_key(BASE, 0.54)  # U9.2 / U9.6: agents/unit-09.py as shipped, on test-circuit
U9_NO_LINE = "u9-line-none"  # U9.6: unit-09 with LINE_CONTROL = None, race seed 0 ...
U8_054 = "u8-0.54"  # ... and unit-08 at MU_FRACTION 0.54, race seed 0


def _mu(track: str) -> Tuple[Tuple[str, object], ...]:
    return () if track == BASE else (("MU_G", MEASURED_MU_G[track]),)


def _fraction(agent: str, fraction: float) -> Tuple[Tuple[str, object], ...]:
    shipped = {"unit-08.py": 0.56, "unit-09.py": 0.54}[agent]
    return () if fraction == shipped else (("MU_FRACTION", fraction),)


def _job(agent, constants, track, seeds=SEEDS, **extra) -> AgentJob:
    return AgentJob(agent, tuple(constants), track, seeds=seeds, max_seconds=cap_for(track), car="carla", **extra)


def centre_job(track: str, fraction: float, *extra) -> AgentJob:
    """``agents/unit-08.py`` on the centreline with the track's measured grip."""
    return _job("unit-08.py", _mu(track) + _fraction("unit-08.py", fraction) + tuple(extra), track)


def line_job(track: str, fraction: float, controls, kind: str = "global") -> AgentJob:
    """``agents/unit-09.py`` on the track's own line (global or local) with its measured grip."""
    line = () if (track == BASE and kind == "global") else (("LINE_CONTROL", controls[(track, kind)]),)
    return _job("unit-09.py", _mu(track) + _fraction("unit-09.py", fraction) + line, track)


def line_premise_jobs(controls) -> Dict[str, AgentJob]:
    """Every Unit 8-9 gate race, keyed by name: 141 races (the plan's job table, shared jobs once)."""
    jobs: Dict[str, AgentJob] = {}
    # U8.2: six probes per track, one race each
    for track in PROBE_TRACKS:
        for section in range(6):
            jobs[probe_key(track, section)] = AgentJob(
                "unit-07.py", (("A_LAT", PROBE_A_LAT), ("GRIP", probe_grip(section))), track, seeds=(0,),
                max_seconds=PROBE_CAP, car="carla", laps=1)
    # U8.3: the steering gain
    jobs[U8_70_MONZA] = centre_job(MONZA, 0.54, ("MAX_STEER", STEER_70))
    jobs[U8_MONZA_EDGE] = centre_job(MONZA, 0.62)
    jobs[U7_66_CHECKPOINT] = _job("unit-07.py", (("MAX_STEER", STEER_66),), CHECKPOINT)
    # U8.4: the family edge and the transfer
    for track in TRAINING:
        jobs[centre_key(track, 0.58)] = centre_job(track, 0.58)
    jobs[centre_key("test-circuit-seed4", 0.6)] = centre_job("test-circuit-seed4", 0.60)
    jobs[centre_key(CHECKPOINT, 0.56)] = centre_job(CHECKPOINT, 0.56)
    # U8.5: the reference, and its equivalence with Unit 7 at 66 degrees
    jobs[U8_REFERENCE] = centre_job(BASE, 0.56)
    jobs[U8_NO_MU] = _job("unit-08.py", (("MU_G", None),), BASE, seeds=(0,))
    jobs[U7_66] = _job("unit-07.py", (("MAX_STEER", STEER_66),), BASE, seeds=(0,))
    # U9.2: the same f
    jobs[U9_REFERENCE] = line_job(BASE, 0.54, controls)
    jobs[centre_key(BASE, 0.54)] = centre_job(BASE, 0.54)
    jobs[line_key(MONZA, 0.6)] = line_job(MONZA, 0.60, controls)
    jobs[local_key(MONZA, 0.6)] = line_job(MONZA, 0.60, controls, "local")
    jobs[centre_key(MONZA, 0.6)] = centre_job(MONZA, 0.60)
    # U9.3: Unit 8's edge with the line
    jobs[line_key("test-circuit-seed4", 0.58)] = line_job("test-circuit-seed4", 0.58, controls)
    # U9.4: the family and the transfer
    for track in TRAINING:
        jobs[line_key(track, 0.56)] = line_job(track, 0.56, controls)
    jobs[line_key(CHECKPOINT, 0.54)] = line_job(CHECKPOINT, 0.54, controls)
    jobs[line_key(CHECKPOINT, 0.58)] = line_job(CHECKPOINT, 0.58, controls)
    # U9.5: local widening on test-circuit
    jobs[local_key(BASE, 0.5)] = line_job(BASE, 0.50, controls, "local")
    # U9.6: the equivalence with Unit 8 at 0.54
    jobs[U9_NO_LINE] = _job("unit-09.py", (("LINE_CONTROL", None),), BASE, seeds=(0,))
    jobs[U8_054] = _job("unit-08.py", (("MU_FRACTION", 0.54),), BASE, seeds=(0,))
    return jobs


def _line_of(submission) -> Optional[Tuple[Tuple[float, ...], int]]:
    """The submission's ``(LINE_CONTROL, LINE_STEP)``, or None when it has no line."""
    tree = ast.parse(submission.read_text(encoding="utf-8"))
    values = {}
    for node in tree.body:
        target = node.targets[0] if isinstance(node, ast.Assign) and len(node.targets) == 1 else None
        if isinstance(target, ast.Name) and target.id in ("LINE_CONTROL", "LINE_STEP"):
            values[target.id] = ast.literal_eval(node.value)
    if values.get("LINE_CONTROL") is None:
        return None
    return values["LINE_CONTROL"], values["LINE_STEP"]


def _section_estimates(telemetry, section_of) -> Tuple[Tuple[int, Optional[float]], ...]:
    """The probe's rule: |a| from the second difference of (x, y) at 0.05 s, on rows whose three
    consecutive rows are driving (``held == 0``) with no jump over 5 m and v > 5 m/s, assigned to the
    section of waypoint ``(progress + 1) mod n``; the estimate is the 99th percentile, or None with
    ``PROBE_MIN_ROWS`` qualifying rows or fewer."""
    import numpy as np

    x, y, held = telemetry["x"], telemetry["y"], telemetry["held"]
    accel = np.full(x.size, np.nan)
    ok = (held[:-2] == 0) & (held[1:-1] == 0) & (held[2:] == 0)
    jump = np.hypot(np.diff(x), np.diff(y))
    ok &= (jump[:-1] < 5) & (jump[1:] < 5)
    ax = (x[2:] - 2 * x[1:-1] + x[:-2]) / G_DT ** 2
    ay = (y[2:] - 2 * y[1:-1] + y[:-2]) / G_DT ** 2
    accel[1:-1] = np.where(ok, np.hypot(ax, ay), np.nan)
    section = section_of[(telemetry["progress"] + 1) % section_of.size]
    estimates = []
    for s in range(6):
        rows = (section == s) & ~np.isnan(accel) & (telemetry["v"] > 5)
        count = int(rows.sum())
        estimates.append((count, float(np.percentile(accel[rows], PROBE_PERCENTILE)) if count > PROBE_MIN_ROWS
                          else None))
    return tuple(estimates)


def race_line_job(job: AgentJob) -> List[LineOutcome]:
    """Race one job (every seed in ``job.seeds``) in this process."""
    import numpy as np
    from _line_solver import line_offsets
    from racekit.runner import run_race
    from racekit.tracks import grip_sections, load_track
    from racekit.variants import write_variant

    track = load_track(job.track)
    section_of = np.asarray(grip_sections(track))
    with tempfile.TemporaryDirectory() as folder:
        submission = AGENTS / job.agent
        if job.constants:
            key = hashlib.sha256(json.dumps([job.agent, job.constants]).encode()).hexdigest()[:12]
            submission = write_variant(submission, os.path.join(folder, f"variant_{key}.py"),
                                       {name: repr(value) for name, value in job.constants})
        line = _line_of(submission)
        n = len(track)
        if line is None:
            target = np.zeros(n)
        else:
            control, step = line
            assert step == 10 and len(control) == n // step, (job.agent, len(control), n)
            target = line_offsets(control, n)
        outcomes = []
        for seed in job.seeds:
            laps = {} if job.laps is None else {"laps": job.laps}
            result = run_race(submission, job.track, car=make_car(job), seed=seed, max_seconds=job.max_seconds,
                              **laps)
            telemetry = result.telemetry
            driving = telemetry["held"] == 0
            offset = telemetry["offset"][driving]
            error = np.abs(offset - target[(telemetry["progress"][driving] + 1) % n])
            digest = hashlib.sha256(telemetry.tobytes() + repr(result.respawn_causes).encode()).hexdigest()
            outcomes.append(LineOutcome(result.total_time, result.collisions, result.finished,
                                        float(np.max(np.abs(offset))), float(np.max(error)), digest,
                                        _section_estimates(telemetry, section_of)))
    return outcomes


def race_line_premise(controls) -> Dict[str, List[LineOutcome]]:
    return race_all(line_premise_jobs(controls), worker=race_line_job)
