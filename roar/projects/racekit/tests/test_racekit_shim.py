"""The ``roar_py_interface`` shim against the MIT ``ROAR_PY`` contract fixture (plan roar-001 Phase D)."""

from __future__ import annotations

import hashlib
import inspect
import json
import math
import subprocess
import sys

import numpy as np
import pytest
import racekit.roar_py_interface as shim
from conftest import RACEKIT
from racekit.runner import run_race

CONTRACT = RACEKIT / "racekit" / "contract"
FIXTURE = CONTRACT / "roar_py_contract.json"
PINNED = "3cbb087ccc5198248815b57742a945e81ef55b64"

# Fixture classes the shim provides under the same name. The two vehicle classes are represented by
# racekit's own RacekitVehicle (a RoarPyActor), checked through the action contract instead.
PROVIDED_CLASSES = (
    "RoarPyWaypoint", "RoarPySensor", "RoarPyActor",
    "RoarPyLocationInWorldSensor", "RoarPyLocationInWorldSensorData",
    "RoarPyRollPitchYawSensor", "RoarPyRollPitchYawSensorData",
    "RoarPyVelocimeterSensor", "RoarPyVelocimeterSensorData",
    "RoarPyCollisionSensor", "RoarPyCollisionSensorData",
    "RoarPyCameraSensor", "RoarPyOccupancyMapSensor",
)
VEHICLE_CLASSES = ("RoarPyVehicleAutoGearActor", "RoarPyVehicleManualGearActor")
# Fixture methods the shim deliberately does not provide, with the reason.
NOT_PROVIDED = {
    ("RoarPyWaypoint", "line_representation"): "geometry helper; submissions compute their own geometry",
    ("RoarPyWaypoint", "load_waypoint_list"): "file helper for map waypoints, which racekit never uses",
    ("RoarPyWaypoint", "save_waypoint_list"): "file helper for map waypoints, which racekit never uses",
    ("RoarPyWaypoint", "from_line_representation"): "geometry helper",
    ("RoarPyWaypoint", "interpolate"): "geometry helper",
    ("RoarPyWaypoint", "distance_to_waypoint_polygon"): "geometry helper (needs shapely)",
    ("RoarPySensor", "__del__"): "finalizer",
    ("RoarPyActor", "__del__"): "finalizer",
}


@pytest.fixture(scope="module")
def contract():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _params(function, owner: str):
    names = []
    for parameter in inspect.signature(function).parameters.values():
        name = parameter.name
        mangled = f"_{owner}__"
        if name.startswith(mangled):
            name = "__" + name[len(mangled):]
        if parameter.kind is parameter.VAR_POSITIONAL:
            name = "*" + name
        elif parameter.kind is parameter.VAR_KEYWORD:
            name = "**" + name
        names.append(name)
    return names


def test_sidecar_matches_the_fixture_bytes_and_the_json_is_canonical(contract):
    payload = FIXTURE.read_bytes()
    sidecar = (CONTRACT / "roar_py_contract.json.sha256").read_text(encoding="ascii")
    assert sidecar == f"{hashlib.sha256(payload).hexdigest()}  roar_py_contract.json\n"
    assert payload == (json.dumps(contract, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode()


def test_fixture_schema_and_provenance(contract):
    assert set(contract) == {
        "fixture_version", "source", "extractor", "classes", "observations", "waypoint", "action",
    }
    assert contract["source"]["commit"] == PINNED
    assert contract["source"]["license"] == "MIT"
    assert contract["source"]["repository"] == "https://github.com/augcog/ROAR_PY"
    assert all(path.startswith("roar_py_core/roar_py_interface/") for path in contract["source"]["paths"])
    assert contract["extractor"]["path"] == "roar/projects/racekit/scripts/extract_roar_py_contract.py"
    licence = (CONTRACT / contract["source"]["license_file"]).read_text(encoding="utf-8")
    assert licence.startswith("MIT License") and "Permission is hereby granted" in licence
    assert set(contract["classes"]) == set(PROVIDED_CLASSES) | set(VEHICLE_CLASSES)
    for name in ("location", "roll_pitch_yaw", "velocity", "collision"):
        observation = contract["observations"][name]
        assert {"shape", "dtype", "units", "frame", "units_source"} <= set(observation)
        assert observation["units_source"]["source"] == "docs"
        assert observation["units_source"]["url"].startswith("https://")
    for field in contract["waypoint"]["fields"].values():
        assert field["source"] == "docs" and "units" in field


@pytest.mark.parametrize("name", PROVIDED_CLASSES)
def test_shim_class_matches_the_contract(contract, name):
    cls = getattr(shim, name)
    spec = contract["classes"][name]
    for method, facts in spec["methods"].items():
        method = method.split("#")[0]
        if (name, method) in NOT_PROVIDED:
            assert not callable(getattr(cls, method, None)) or method == "__del__"
            continue
        attribute = inspect.getattr_static(cls, method, None)
        assert attribute is not None, f"{name}.{method} is missing"
        if "property" in facts["decorators"]:
            assert isinstance(attribute, property), f"{name}.{method} must be a property"
            continue
        function = getattr(cls, method)
        assert inspect.iscoroutinefunction(function) == facts["async"], f"{name}.{method} async-ness"
        assert _params(function, name) == facts["params"], f"{name}.{method} parameters"
    for field in spec["fields"]:
        if field.startswith("_") or field == "sensordata_type":
            continue
        assert field in _params(cls.__init__, name), f"{name} field {field}"


def test_every_unprovided_method_is_in_the_contract(contract):
    for owner, method in NOT_PROVIDED:
        assert method in contract["classes"][owner]["methods"]


def test_action_contract_matches_the_shim(contract):
    keys = contract["action"]["keys"]
    assert set(keys) == set(shim.ACTION_SPEC)
    for key, space in keys.items():
        kind, low, high = shim.ACTION_SPEC[key]
        if space["space"] == "Box":
            assert (kind, low, high) == ("real", space["low"], space["high"])
        elif space["space"] == "MultiBinary":
            assert kind == "binary" and (low, high) == (0, 1)
        else:
            assert space["space"] == "Discrete" and kind == "int"
    assert set(shim.REQUIRED_ACTION_KEYS) == set(keys) - {"target_gear"}


GOOD = {"throttle": 0.5, "steer": -0.25, "brake": 0.0, "hand_brake": 0.0, "reverse": 0}


@pytest.mark.parametrize("action", [
    GOOD,
    dict(GOOD, target_gear=0),
    dict(GOOD, throttle=np.float32(1.0), steer=np.float64(-1.0), reverse=False),
    dict(GOOD, throttle=1, brake=np.array([0.5])),
])
def test_valid_actions_are_accepted(action):
    clean = shim.validate_action(action)
    assert set(clean) <= set(shim.ACTION_SPEC)
    assert all(isinstance(value, float) for value in clean.values())


@pytest.mark.parametrize(("action", "message"), [
    ([0.5, 0.0], "must be a dict"),
    (dict(GOOD, nitro=1.0), "unknown action keys"),
    ({key: value for key, value in GOOD.items() if key != "brake"}, "missing action keys"),
    (dict(GOOD, throttle=1.5), "outside"),
    (dict(GOOD, steer=-1.01), "outside"),
    (dict(GOOD, brake=float("nan")), "outside"),
    (dict(GOOD, throttle="0.5"), "real number"),
    (dict(GOOD, throttle=True), "real number"),
    (dict(GOOD, reverse=2), "0 or 1"),
    (dict(GOOD, target_gear=1.0), "must be an int"),
])
def test_invalid_actions_raise_value_error(action, message):
    with pytest.raises(ValueError, match=message):
        shim.validate_action(action)


def test_apply_action_is_async_and_validates():
    vehicle = shim.RacekitVehicle()
    assert inspect.iscoroutinefunction(vehicle.apply_action)
    loop = __import__("asyncio").new_event_loop()
    try:
        assert loop.run_until_complete(vehicle.apply_action(dict(GOOD))) is True
        with pytest.raises(shim.ActionValidationError):
            loop.run_until_complete(vehicle.apply_action(dict(GOOD, steer=3.0)))
    finally:
        loop.close()
    assert vehicle.actions_applied == 1


class ObservationRecorder:
    seen = []  # noqa: RUF012 - a per-test observation log

    def __init__(self, maneuverable_waypoints, vehicle, camera_sensor, location_sensor,
                 velocity_sensor, rpy_sensor, occupancy_map_sensor, collision_sensor):
        self.waypoints = maneuverable_waypoints
        self.vehicle = vehicle
        self.sensors = {
            "location": location_sensor, "velocity": velocity_sensor, "roll_pitch_yaw": rpy_sensor,
            "collision": collision_sensor, "camera": camera_sensor, "occupancy": occupancy_map_sensor,
        }

    async def initialize(self):
        ObservationRecorder.seen.clear()

    async def step(self):
        ObservationRecorder.seen.append({
            name: sensor.get_last_gym_observation() for name, sensor in self.sensors.items()
        })
        await self.vehicle.apply_action({"throttle": 0.6, "steer": 0.0, "brake": 0.0,
                                         "hand_brake": 0.0, "reverse": 0})


def test_observations_during_a_race_match_the_contract(contract):
    result = run_race(ObservationRecorder, "oval", laps=1, max_seconds=4.0)
    seen = ObservationRecorder.seen
    assert len(seen) == result.ticks
    for name in ("location", "velocity", "roll_pitch_yaw", "collision"):
        expected = contract["observations"][name]
        for observation in seen:
            assert observation[name].shape == tuple(expected["shape"])
            assert observation[name].dtype == np.dtype(expected["dtype"])
    assert all(observation["camera"] is None and observation["occupancy"] is None for observation in seen)
    # units: the observation before tick k reflects the state after tick k-1 (metres, m/s, radians)
    telemetry = result.telemetry
    for k in range(1, result.ticks):
        location, velocity, rpy = (seen[k][name] for name in ("location", "velocity", "roll_pitch_yaw"))
        assert math.hypot(location[0] - telemetry["x"][k - 1], location[1] - telemetry["y"][k - 1]) < 1e-3
        assert abs(float(np.linalg.norm(velocity)) - telemetry["v"][k - 1]) < 1e-3
        assert abs(float(rpy[2]) - telemetry["yaw"][k - 1]) < 1e-5 and -math.pi <= rpy[2] < math.pi
    assert telemetry["v"][-1] > 5.0  # it really moved, in m/s


def test_waypoints_match_the_contract(contract):
    from racekit.tracks import load_track

    waypoints = load_track("oval").waypoints
    fields = contract["waypoint"]["fields"]
    for waypoint in waypoints[:5]:
        assert waypoint.location.shape == tuple(fields["location"]["shape"])
        assert waypoint.location.dtype == np.dtype(fields["location"]["dtype"])
        assert waypoint.roll_pitch_yaw.shape == tuple(fields["roll_pitch_yaw"]["shape"])
        assert isinstance(waypoint.lane_width, float)
    assert waypoints[0] == shim.RoarPyWaypoint(waypoints[0].location, waypoints[0].roll_pitch_yaw,
                                               waypoints[0].lane_width)
    assert waypoints[0] != waypoints[1]


def test_extractor_refuses_an_unpinned_checkout(tmp_path):
    repo = tmp_path / "roar_py"
    repo.mkdir()
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com", "PATH": __import__("os").environ["PATH"]}
    subprocess.run(["git", "init", "-q", str(repo)], check=True, env=env)
    (repo / "LICENSE").write_text("x\n")
    subprocess.run(["git", "-C", str(repo), "add", "LICENSE"], check=True, env=env)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "x"], check=True, env=env)
    run = subprocess.run(
        [sys.executable, str(RACEKIT / "scripts" / "extract_roar_py_contract.py"), str(repo),
         "--out", str(tmp_path / "out")],
        capture_output=True, text=True, check=False,
    )
    assert run.returncode == 1
    assert "not the pinned" in run.stderr
    assert not (tmp_path / "out").exists()
