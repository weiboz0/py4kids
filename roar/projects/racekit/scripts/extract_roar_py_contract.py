"""Extract the ``roar_py_interface`` contract fixture from a local ``ROAR_PY`` checkout.

Clean-room tooling (design 013 §4.1, §7.4; plan roar-001 Phase D). It **reads** the MIT-licensed
``ROAR_PY`` source with ``ast`` and records facts as data: class, method, attribute and parameter
names, async flags, observation-space shapes and dtypes, and the action keys and ranges. It copies
no code. Units and frames, which the source does not state reliably, come from the competition
documentation and are marked ``"source": "docs"``.

Usage (a manual step, not CI: it needs a network clone)::

    git clone https://github.com/augcog/ROAR_PY /path/to/roar_py
    git -C /path/to/roar_py checkout 3cbb087ccc5198248815b57742a945e81ef55b64
    uv run --group roar python roar/projects/racekit/scripts/extract_roar_py_contract.py /path/to/roar_py

It refuses any commit other than the pinned one, and writes, deterministically (sorted keys, fixed
float format, canonical JSON):

* ``racekit/contract/roar_py_contract.json``;
* ``racekit/contract/roar_py_contract.json.sha256`` (the sidecar: sha256 of the fixture's bytes);
* ``racekit/contract/LICENSE-ROAR_PY`` (the checkout's MIT licence text, unchanged).
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

EXTRACTOR_VERSION = 1
PINNED_COMMIT = "3cbb087ccc5198248815b57742a945e81ef55b64"
REPOSITORY = "https://github.com/augcog/ROAR_PY"
DOCS_URL = "https://roar.gitbook.io/roar-competition-documentation"
INTERFACE = "roar_py_core/roar_py_interface"
CONTRACT_DIR = Path(__file__).resolve().parents[1] / "racekit" / "contract"
FIXTURE_NAME = "roar_py_contract.json"

# The surface a competition submission touches: source file -> classes recorded.
SURFACE = {
    "worlds/waypoint.py": ["RoarPyWaypoint"],
    "base/sensor.py": ["RoarPySensor"],
    "actors/actor.py": ["RoarPyActor"],
    "actors/vehicle.py": ["RoarPyVehicleAutoGearActor", "RoarPyVehicleManualGearActor"],
    "sensors/location_in_world_sensor.py": ["RoarPyLocationInWorldSensor", "RoarPyLocationInWorldSensorData"],
    "sensors/rotation_sensor.py": ["RoarPyRollPitchYawSensor", "RoarPyRollPitchYawSensorData"],
    "sensors/velocimeter_sensor.py": ["RoarPyVelocimeterSensor", "RoarPyVelocimeterSensorData"],
    "sensors/collision_sensor.py": ["RoarPyCollisionSensor", "RoarPyCollisionSensorData"],
    "sensors/camera_sensor.py": ["RoarPyCameraSensor"],
    "sensors/occupancy_map_sensor.py": ["RoarPyOccupancyMapSensor"],
}
# Observation name -> (sensor class, data class). Shapes and dtypes are read from the data class's
# observation space; units and frames come from the documentation (DOCS below).
OBSERVATIONS = {
    "location": ("RoarPyLocationInWorldSensor", "RoarPyLocationInWorldSensorData"),
    "roll_pitch_yaw": ("RoarPyRollPitchYawSensor", "RoarPyRollPitchYawSensorData"),
    "velocity": ("RoarPyVelocimeterSensor", "RoarPyVelocimeterSensorData"),
    "collision": ("RoarPyCollisionSensor", "RoarPyCollisionSensorData"),
}
ROAR_FRAME = "world, right-handed: x forward, y left, z up"
DOCS = {
    "location": {"units": "m", "frame": ROAR_FRAME},
    "roll_pitch_yaw": {"units": "rad", "frame": "roll, pitch, yaw, each normalized to [-pi, pi)"},
    "velocity": {"units": "m/s", "frame": ROAR_FRAME},
    "collision": {"units": "N*s", "frame": "vehicle-local x, y, z"},
}
WAYPOINT_DOCS = {
    "location": {"shape": [3], "dtype": "float64", "units": "m", "frame": ROAR_FRAME},
    "roll_pitch_yaw": {"shape": [3], "dtype": "float64", "units": "rad", "frame": "road roll, pitch, yaw"},
    "lane_width": {"shape": [], "dtype": "float64", "units": "m", "frame": "scalar"},
}
ACTION_CLASS = "RoarPyVehicleManualGearActor"


def _num(value: float) -> Any:
    if math.isinf(value):
        return "inf" if value > 0 else "-inf"
    return round(float(value), 6)


def _value(node: ast.AST) -> Any:
    """A small, explicit evaluator for the literal forms the observation/action specs use."""
    if isinstance(node, ast.Constant):
        return _num(node.value) if isinstance(node.value, float) else node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        inner = _value(node.operand)
        if inner == "inf":
            return "-inf"
        if isinstance(inner, (int, float)):
            return _num(-inner)
    if isinstance(node, ast.Tuple):
        return [_value(element) for element in node.elts]
    if isinstance(node, ast.Attribute):
        if node.attr == "inf":
            return "inf"
        if node.attr == "pi":
            return _num(math.pi)
        if isinstance(node.value, ast.Name) and node.value.id == "self":
            return node.attr  # a parameter, e.g. num_gears
        return node.attr  # a dtype such as np.float32
    if isinstance(node, ast.Name):
        return node.id
    raise ValueError(f"unsupported spec expression: {ast.dump(node)}")


def _dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_dotted(node.value)}.{node.attr}"
    if isinstance(node, ast.Subscript):
        return _dotted(node.value)
    if isinstance(node, ast.Call):
        return _dotted(node.func)
    return type(node).__name__


def _params(function: ast.AST) -> List[str]:
    arguments = function.args
    names = [arg.arg for arg in arguments.posonlyargs + arguments.args]
    if arguments.vararg:
        names.append("*" + arguments.vararg.arg)
    names += [arg.arg for arg in arguments.kwonlyargs]
    if arguments.kwarg:
        names.append("**" + arguments.kwarg.arg)
    return names


def _space(call: ast.Call) -> Dict[str, Any]:
    space: Dict[str, Any] = {"space": _dotted(call.func).split(".")[-1]}
    if space["space"] == "Discrete" and call.args:
        space["n"] = _value(call.args[0])
    if space["space"] == "MultiBinary" and call.args:
        space["n"] = _value(call.args[0])
    for keyword in call.keywords:
        space[keyword.arg] = _value(keyword.value)
    return space


def _returned_call(function: ast.AST) -> ast.Call:
    for node in ast.walk(function):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Call):
            return node.value
    raise ValueError(f"no returned call in {function.name}")


def extract_class(node: ast.ClassDef, source: str) -> Dict[str, Any]:
    methods = {}
    fields = []
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decorators = sorted(_dotted(decorator) for decorator in item.decorator_list)
            key = item.name if item.name not in methods else f"{item.name}#setter"
            methods[key] = {
                "async": isinstance(item, ast.AsyncFunctionDef),
                "params": _params(item),
                "decorators": decorators,
            }
        elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            fields.append(item.target.id)
    return {
        "source": source,
        "bases": [_dotted(base) for base in node.bases],
        "fields": fields,
        "methods": methods,
    }


def extract(checkout: Path) -> Dict[str, Any]:
    classes: Dict[str, Any] = {}
    nodes: Dict[str, ast.ClassDef] = {}
    paths = []
    for relative, names in SURFACE.items():
        path = checkout / INTERFACE / relative
        paths.append(f"{INTERFACE}/{relative}")
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        found = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}
        for name in names:
            if name not in found:
                raise SystemExit(f"FAIL: {relative}: class {name} not found")
            nodes[name] = found[name]
            classes[name] = extract_class(found[name], f"{INTERFACE}/{relative}")

    observations = {}
    for name, (sensor, data_class) in OBSERVATIONS.items():
        spec_method = next(
            item for item in nodes[data_class].body
            if isinstance(item, ast.FunctionDef) and item.name == "get_gym_observation_spec"
        )
        space = _space(_returned_call(spec_method))
        observations[name] = {
            "sensor": sensor,
            "data_class": data_class,
            "data_fields": classes[data_class]["fields"],
            "space": space["space"],
            "shape": space["shape"],
            "dtype": space["dtype"],
            "low": space["low"],
            "high": space["high"],
            "units": DOCS[name]["units"],
            "frame": DOCS[name]["frame"],
            "units_source": {"source": "docs", "url": DOCS_URL},
        }

    action_method = next(
        item for item in nodes[ACTION_CLASS].body
        if isinstance(item, ast.FunctionDef) and item.name == "get_action_spec"
    )
    action_dict = _returned_call(action_method).args[0]
    if not isinstance(action_dict, ast.Dict):
        raise SystemExit("FAIL: the action spec is not a dict literal")
    action = {
        key.value: _space(value)
        for key, value in zip(action_dict.keys, action_dict.values)
        if isinstance(key, ast.Constant) and isinstance(value, ast.Call)
    }
    return {
        "fixture_version": 1,
        "source": {
            "repository": REPOSITORY,
            "commit": PINNED_COMMIT,
            "license": "MIT",
            "license_file": "LICENSE-ROAR_PY",
            "paths": sorted(paths),
        },
        "extractor": {
            "path": "roar/projects/racekit/scripts/extract_roar_py_contract.py",
            "version": EXTRACTOR_VERSION,
        },
        "classes": classes,
        "observations": observations,
        "waypoint": {
            "class": "RoarPyWaypoint",
            "fields": {
                name: dict(spec, source="docs", url=DOCS_URL) for name, spec in WAYPOINT_DOCS.items()
            },
        },
        "action": {"class": ACTION_CLASS, "keys": action},
    }


def canonical_json(data: Dict[str, Any]) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")


def write_fixture(data: Dict[str, Any], out_dir: Path, license_text: str) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = canonical_json(data)
    (out_dir / FIXTURE_NAME).write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    (out_dir / f"{FIXTURE_NAME}.sha256").write_text(f"{digest}  {FIXTURE_NAME}\n", encoding="ascii")
    (out_dir / "LICENSE-ROAR_PY").write_text(license_text, encoding="utf-8")
    return digest


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Extract the ROAR_PY contract fixture (clean room).")
    parser.add_argument("checkout", type=Path, help="a local ROAR_PY checkout at the pinned commit")
    parser.add_argument("--out", type=Path, default=CONTRACT_DIR)
    args = parser.parse_args(argv)
    head = subprocess.run(
        ["git", "-C", str(args.checkout), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    if head != PINNED_COMMIT:
        print(f"FAIL: {args.checkout} is at {head}, not the pinned {PINNED_COMMIT}", file=sys.stderr)
        return 1
    data = extract(args.checkout)
    license_text = (args.checkout / "LICENSE").read_text(encoding="utf-8")
    digest = write_fixture(data, args.out, license_text)
    print(f"wrote {args.out / FIXTURE_NAME} (sha256 {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
