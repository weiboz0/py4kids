"""The synchronous race runner (design 013 §4.2): the real race rules on a racekit car.

``run_race(submission, track)`` loads a competition submission (a ``.py`` file, or an agent class
defined in a notebook), drives it for ``laps`` laps and returns a ``RaceResult``.

The rules mirror the pinned official runner (``ROAR_Competition`` @ ``ab19e1b``,
``competition_runner.py``; design 013 §1.2, v4.1), re-implemented here from its described behaviour:

* a 0.05 s control tick with 10 physics substeps; each tick runs ``await agent.step()`` and then
  advances the car (the official order);
* the agent is constructed with the official arguments, then ``await agent.initialize()`` runs
  exactly once, before the first tick;
* the waypoint list is repeated once per lap (three laps by default); progress is the furthest
  waypoint reached, found by projecting the waypoints of a **forward window of 15** onto the car's
  latest motion segment;
* the race is finished when ``progress + 5 >= len(repeated waypoint list)`` (the 5-waypoint margin);
  a major collision is checked **first**, so a tick that both crosses the finish margin and
  collides is a collision (as upstream orders it);
* a **major collision** puts the car back at the race **start pose** with zero velocity, then the
  world advances **20 control ticks (1.0 s) without calling the agent** (the car stays put), and
  then the **progress index resets to 0** with the last position set to the start pose: the race
  effectively restarts while the clock keeps running;
* the result is the elapsed simulated time.

Known differences from the official runner (each an approximation, labelled wherever it is taught):

* **what counts as a major collision**: the official runner uses CARLA's collision sensor (impulse
  norm > 100 N·s, e.g. hitting a wall); racekit uses leaving the drivable width (``|offset| >
  half-width``) as the wall approximation (roar-004's dynamic car adds a spin-out rule);
* **the collision-sensor reading**: after a major collision racekit reports a lateral impulse of
  ``CRASH_IMPULSE`` N·s on the first agent step after the hold, and zeros otherwise; CARLA reports
  the real contact impulse;
* **during the 1 s hold** CARLA keeps applying the last control to a car placed at rest; racekit
  holds the car exactly still;
* **physics**: racekit's car models are simple models of CARLA's vehicle (design 013 §4.4).

The simulation is deterministic and never reads the wall clock; ``step()``'s compute time is
measured (``RaceResult.step_ms``) but never fed back. Every number is a *model* number.
"""

from __future__ import annotations

import asyncio
import contextlib
import importlib.util
import itertools
import math
import re
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple, Union

import numpy as np

from . import roar_py_interface as shim
from .cars import Car, KinematicCar
from .tracks import Track, load_track

CONTROL_DT = 0.05
SUBSTEPS = 10
PROGRESS_WINDOW = 15
SECTORS_PER_LAP = 3
DEFAULT_LAPS = 3
DEFAULT_MAX_SECONDS = 1800.0
FINISH_MARGIN = 5  # the race is finished at progress + 5 >= len(waypoints) (check_step=5)
RESPAWN_HOLD_TICKS = 20  # control ticks the world advances after a respawn, agent not called
CRASH_IMPULSE = 1000.0  # N·s reported on the collision sensor after a major collision (an approximation)

TELEMETRY_DTYPE = np.dtype(
    [
        ("t", "f8"), ("x", "f8"), ("y", "f8"), ("yaw", "f8"), ("v", "f8"),
        ("throttle", "f8"), ("steer", "f8"), ("brake", "f8"), ("progress", "i8"), ("offset", "f8"),
        ("held", "i8"),  # 1 on the respawn-hold ticks (the agent is not called), else 0
    ]
)
SOLUTION_CLASS = "RoarCompetitionSolution"
CONSTRUCTOR_PARAMS = (
    "maneuverable_waypoints", "vehicle", "camera_sensor", "location_sensor", "velocity_sensor",
    "rpy_sensor", "occupancy_map_sensor", "collision_sensor",
)
SHIM_NAME = "roar_py_interface"

_load_counter = itertools.count()
_MISSING = object()


class RaceResult:
    """The outcome of one race. Times are simulated seconds."""

    def __init__(
        self,
        track: str,
        laps: int,
        finished: bool,
        total_time: float,
        collisions: int,
        respawn_times: List[float],
        sector_splits: np.ndarray,
        telemetry: np.ndarray,
        step_ms: np.ndarray,
        progress: int,
        progress_total: int,
        progress_required: int,
        seed: int,
    ) -> None:
        self.track = track
        self.laps = laps
        self.finished = finished
        self.total_time = total_time
        self.collisions = collisions
        self.respawn_times = respawn_times  # sim time of each major collision (start of its hold)
        self.sector_splits = sector_splits
        self.telemetry = telemetry
        self.step_ms = step_ms
        self.progress = progress
        self.progress_total = progress_total  # the length of the repeated waypoint list
        self.progress_required = progress_required  # finished at progress >= this (5-waypoint margin)
        self.seed = seed

    @property
    def ticks(self) -> int:
        return int(self.telemetry.shape[0])

    def step_ms_p99(self, warmup: int = 50) -> float:
        """The 99th percentile of ``step()`` compute time, excluding the first ``warmup`` steps.

        ``step_ms`` has one entry per agent step (respawn-hold ticks call no step)."""
        tail = self.step_ms[warmup:] if self.step_ms.size > warmup else self.step_ms
        return float(np.percentile(tail, 99)) if tail.size else 0.0

    def __repr__(self) -> str:
        state = "finished" if self.finished else f"did not finish ({self.progress}/{self.progress_required})"
        return (
            f"RaceResult({self.track}, {self.laps} laps, {state}, {self.total_time:.2f} s, "
            f"{self.collisions} collisions)"
        )


# --- the progress rule ---------------------------------------------------------------------------


def advance_progress(
    wx: Sequence[float], wy: Sequence[float], furthest: int,
    last_x: float, last_y: float, x: float, y: float, window: int = PROGRESS_WINDOW,
) -> int:
    """The furthest-waypoint rule: return the new furthest index.

    Each waypoint in ``[furthest, furthest + window)`` is projected onto the car's latest motion
    segment (last position -> current position); the waypoint closest to that segment becomes the
    new furthest index. Waypoints beyond the window are never considered.
    """
    dx, dy = x - last_x, y - last_y
    norm = math.hypot(dx, dy)
    ux, uy = (dx / norm, dy / norm) if norm >= 1e-5 else (0.0, 0.0)
    end = min(furthest + window, len(wx))
    best_d2 = math.inf
    best = furthest
    for i in range(furthest, end):
        px, py = wx[i] - last_x, wy[i] - last_y
        along = px * ux + py * uy
        along = max(0.0, min(along, norm))
        ex, ey = px - along * ux, py - along * uy
        d2 = ex * ex + ey * ey
        if d2 < best_d2:
            best_d2 = d2
            best = i
    return best


# --- loading a submission under the shim ---------------------------------------------------------


@contextlib.contextmanager
def shim_installed() -> Iterator[Any]:
    """Install the shim as ``roar_py_interface`` for the duration, then restore the previous state.

    Refuses to shadow a different ``roar_py_interface`` that is already imported or installed.
    """
    previous = sys.modules.get(SHIM_NAME, _MISSING)
    if previous is not _MISSING and previous is not shim:
        raise RuntimeError(
            "a different roar_py_interface module is already imported; racekit refuses to shadow it"
        )
    if previous is _MISSING:
        try:
            real = importlib.util.find_spec(SHIM_NAME)
        except (ImportError, ValueError):
            real = None
        if real is not None:
            raise RuntimeError(
                f"a real roar_py_interface is installed ({real.origin}); racekit refuses to shadow it"
            )
    sys.modules[SHIM_NAME] = shim
    try:
        yield shim
    finally:
        if previous is _MISSING:
            sys.modules.pop(SHIM_NAME, None)
        else:
            sys.modules[SHIM_NAME] = previous


def load_submission(path: Union[str, Path]) -> Tuple[type, str]:
    """Load ``path`` under a unique module name; return ``(RoarCompetitionSolution, module name)``.

    Call it inside ``shim_installed()``.
    """
    path = Path(path)
    stem = re.sub(r"\W", "_", path.stem)
    name = f"racekit_submission_{next(_load_counter)}_{stem}"
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    agent_class = getattr(module, SOLUTION_CLASS, None)
    if not isinstance(agent_class, type):
        sys.modules.pop(name, None)
        raise ImportError(f"{path} does not define a class {SOLUTION_CLASS}")  # noqa: TRY004
    return agent_class, name


# --- the race ------------------------------------------------------------------------------------


class _Sensors:
    def __init__(self) -> None:
        self.location = shim.RoarPyLocationInWorldSensor()
        self.rpy = shim.RoarPyRollPitchYawSensor()
        self.velocity = shim.RoarPyVelocimeterSensor()
        self.collision = shim.RoarPyCollisionSensor()
        self.camera = shim.RoarPyCameraSensor()
        self.occupancy = shim.RoarPyOccupancyMapSensor()

    def update(self, car: Car, vehicle: shim.RacekitVehicle, impulse: Tuple[float, float, float]) -> None:
        self.location._set_observation(shim.RoarPyLocationInWorldSensorData(car.x, car.y, 0.0))
        self.rpy._set_observation(shim.RoarPyRollPitchYawSensorData((0.0, 0.0, car.yaw)))
        vx, vy = car.velocity()
        self.velocity._set_observation(shim.RoarPyVelocimeterSensorData((vx, vy, 0.0)))
        self.collision._set_observation(shim.RoarPyCollisionSensorData(vehicle, None, impulse))


async def _race(
    agent_class: type, track: Track, car: Car, laps: int, max_seconds: float, seed: int
) -> RaceResult:
    vehicle = shim.RacekitVehicle()
    sensors = _Sensors()
    vehicle._sensors = [sensors.location, sensors.rpy, sensors.velocity, sensors.collision]
    start_x, start_y, start_yaw = track.start_pose()
    car.reset(start_x, start_y, start_yaw, 0.0)
    no_impulse = (0.0, 0.0, 0.0)
    sensors.update(car, vehicle, no_impulse)

    agent = agent_class(
        track.waypoints, vehicle, sensors.camera, sensors.location, sensors.velocity, sensors.rpy,
        sensors.occupancy, sensors.collision,
    )
    await agent.initialize()

    # The progress list: one lap starting just after the start waypoint, repeated once per lap.
    n = len(track)
    order = list(range(1, n)) + [0]
    wx = [float(track.x[i]) for i in order] * laps
    wy = [float(track.y[i]) for i in order] * laps
    total = len(wx)
    max_ticks = math.floor(max_seconds / CONTROL_DT + 1e-9)
    required = total - FINISH_MARGIN
    rows: List[Tuple[float, ...]] = []
    step_ms: List[float] = []
    furthest = 0
    last_x, last_y = start_x, start_y
    hint = 0
    respawn_times: List[float] = []
    finished = False
    tick = 0
    t = 0.0
    perf = time.perf_counter
    advance = car.advance
    impulse = no_impulse

    while tick < max_ticks:
        started = perf()
        await agent.step()
        step_ms.append((perf() - started) * 1000.0)
        action = vehicle.last_action
        advance(action["throttle"], action["steer"], action["brake"], action["hand_brake"],
                action["reverse"], CONTROL_DT, SUBSTEPS)
        tick += 1
        t = tick * CONTROL_DT
        x, y = car.x, car.y
        furthest = advance_progress(wx, wy, furthest, last_x, last_y, x, y)
        last_x, last_y = x, y
        hint, offset, _, half_width = track.nearest(x, y, hint)
        rows.append((t, x, y, car.yaw, car.v, action["throttle"], action["steer"], action["brake"],
                     furthest, offset, 0))
        impulse = no_impulse
        if abs(offset) > half_width:
            # A major collision: back to the start pose at rest, a 1.0 s hold without calling the
            # agent, then progress resets to 0 (the race restarts; the clock keeps running).
            respawn_times.append(t)
            side = 1.0 if offset > 0 else -1.0
            impulse = (0.0, -side * CRASH_IMPULSE, 0.0)
            car.reset(start_x, start_y, start_yaw, 0.0)
            hint, offset, _, _ = track.nearest(start_x, start_y, 0)
            for _ in range(RESPAWN_HOLD_TICKS):
                if tick >= max_ticks:
                    break
                tick += 1
                t = tick * CONTROL_DT
                rows.append((t, car.x, car.y, car.yaw, 0.0, 0.0, 0.0, 0.0, furthest, offset, 1))
            furthest = 0
            last_x, last_y = car.x, car.y
        elif furthest + FINISH_MARGIN >= total:
            finished = True
            break
        sensors.update(car, vehicle, impulse)

    from .telemetry import sector_splits  # telemetry imports this module, so import it here

    telemetry = np.array(rows, dtype=TELEMETRY_DTYPE) if rows else np.zeros(0, TELEMETRY_DTYPE)
    return RaceResult(
        track=track.name, laps=laps, finished=finished, total_time=t, collisions=len(respawn_times),
        respawn_times=respawn_times, sector_splits=sector_splits(telemetry, total, laps, SECTORS_PER_LAP),
        telemetry=telemetry, step_ms=np.asarray(step_ms, dtype=np.float64), progress=furthest,
        progress_total=total, progress_required=required, seed=seed,
    )


def _run_coroutine(factory: Any) -> Any:
    """Run ``factory()`` on a private event loop: a fresh one when no loop is running in this
    thread, otherwise a worker thread with its own loop (e.g. inside a Jupyter kernel)."""
    try:
        asyncio.get_running_loop()
        running = True
    except RuntimeError:
        running = False
    if not running:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(factory())
        finally:
            loop.close()
    outcome: Dict[str, Any] = {}

    def worker() -> None:
        loop = asyncio.new_event_loop()
        try:
            outcome["value"] = loop.run_until_complete(factory())
        except BaseException as error:  # noqa: BLE001 - re-raised in the calling thread
            outcome["error"] = error
        finally:
            loop.close()

    thread = threading.Thread(target=worker, name="racekit-race")
    thread.start()
    thread.join()
    if "error" in outcome:
        raise outcome["error"]
    return outcome["value"]


def run_race(
    submission: Union[str, Path, type],
    track: Union[str, Path, Track] = "oval",
    car: Optional[Car] = None,
    laps: int = DEFAULT_LAPS,
    max_seconds: float = DEFAULT_MAX_SECONDS,
    seed: int = 0,
) -> RaceResult:
    """Race ``submission`` (a submission ``.py`` path or an agent class) on ``track``.

    A plain synchronous function: no ``await`` needed, in a script or in a notebook.
    ``seed`` is recorded on the result and passed to the car's ``seed()`` when it has one (the
    kinematic car's actuator jitter draws from it; with ``jitter=0`` the race is deterministic and
    the seed changes nothing).
    """
    track_obj = load_track(track)
    if car is None:
        car = KinematicCar()
    if hasattr(car, "seed"):
        car.seed(seed)
    if laps < 1:
        raise ValueError("laps must be at least 1")
    with shim_installed():
        module_name = None
        if isinstance(submission, type):
            agent_class = submission
        else:
            agent_class, module_name = load_submission(submission)
        try:
            return _run_coroutine(lambda: _race(agent_class, track_obj, car, laps, max_seconds, seed))
        finally:
            if module_name is not None:
                sys.modules.pop(module_name, None)
