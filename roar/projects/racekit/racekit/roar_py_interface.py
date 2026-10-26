"""A clean-room shim of the ``roar_py_interface`` surface a competition submission uses.

Design 013 §4.1. ``racekit.run_race`` and ``racekit.check_submission`` install this module in
``sys.modules["roar_py_interface"]`` for the whole call, so a submission's unchanged
``import roar_py_interface`` line (top level or function-local) resolves here.

It is written from the competition documentation (<https://roar.gitbook.io/roar-competition-documentation>)
and observed behaviour; no ``ROAR_PY`` code is copied. Its names, async flags, parameters, observation
shapes and dtypes, and the action keys and ranges are tested against the MIT-licensed contract
fixture ``racekit/contract/roar_py_contract.json`` (see ``LICENSE-ROAR_PY``).

Conventions (the ROAR frame): right-handed, x forward, y left, z up; angles in radians; a positive
``steer`` turns the car to the right (clockwise, yaw decreasing).
Observations are ``float32`` arrays, as the interface's observation spaces declare.
"""

from __future__ import annotations

import math
import numbers
from typing import Any, Dict, Iterable, List, Optional

import numpy as np

OBS_DTYPE = np.float32
_PI32 = np.nextafter(np.float32(math.pi), np.float32(0.0))  # the largest float32 below pi

# The action dictionary (design 013 §1.2, §4.1): name -> (kind, low, high). `target_gear` is
# optional: the race vehicle is auto-gear and ignores it (the competition skeleton sends 0), so it
# is only type-checked as an int. Every other key is required.
ACTION_SPEC = {
    "throttle": ("real", 0.0, 1.0),
    "steer": ("real", -1.0, 1.0),
    "brake": ("real", 0.0, 1.0),
    "hand_brake": ("real", 0.0, 1.0),
    "reverse": ("binary", 0, 1),
    "target_gear": ("int", None, None),
}
REQUIRED_ACTION_KEYS = ("throttle", "steer", "brake", "hand_brake", "reverse")


def _vector(values: Any) -> np.ndarray:
    return np.asarray(values, dtype=np.float64).reshape(3).copy()


class RoarPyWaypoint:
    """A waypoint: ``location`` (3,) metres, ``roll_pitch_yaw`` (3,) radians, ``lane_width`` metres."""

    def __init__(self, location: Any, roll_pitch_yaw: Any, lane_width: float) -> None:
        self.location = _vector(location)
        self.roll_pitch_yaw = _vector(roll_pitch_yaw)
        self.lane_width = float(lane_width)

    def __eq__(self, __value: object) -> bool:  # noqa: PYI063 - the interface's parameter name
        if not isinstance(__value, RoarPyWaypoint):
            return False
        return bool(
            np.allclose(self.location, __value.location)
            and np.allclose(self.roll_pitch_yaw, __value.roll_pitch_yaw)
            and np.isclose(self.lane_width, __value.lane_width)
        )

    __hash__ = None  # type: ignore[assignment]  # mutable value object, like the original

    def __repr__(self) -> str:
        x, y, z = self.location
        return f"RoarPyWaypoint(location=({x:.2f}, {y:.2f}, {z:.2f}), lane_width={self.lane_width:.2f})"


# --- sensor data ---------------------------------------------------------------------------------


class RoarPyLocationInWorldSensorData:
    """Location in the world frame, metres."""

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def get_gym_observation_spec(self) -> Dict[str, Any]:
        return {"shape": (3,), "dtype": "float32"}

    def convert_obs_to_gym_obs(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z], dtype=OBS_DTYPE)


class RoarPyRollPitchYawSensorData:
    """Roll, pitch and yaw in radians; the constructor wraps each angle to [-pi, pi)."""

    def __init__(self, roll_pitch_yaw: Any) -> None:
        angles = np.asarray(roll_pitch_yaw, dtype=np.float64).reshape(3)
        wrapped = (angles + math.pi) % (2.0 * math.pi) - math.pi
        # float32 rounding must not push an angle onto or past ±pi
        self.roll_pitch_yaw = np.clip(wrapped.astype(OBS_DTYPE), -_PI32, _PI32)

    def get_gym_observation_spec(self) -> Dict[str, Any]:
        return {"shape": (3,), "dtype": "float32"}

    def convert_obs_to_gym_obs(self) -> np.ndarray:
        return self.roll_pitch_yaw


class RoarPyVelocimeterSensorData:
    """Linear velocity (x, y, z) in the world frame, m/s."""

    def __init__(self, velocity: Any) -> None:
        self.velocity = np.asarray(velocity, dtype=OBS_DTYPE).reshape(3).copy()

    def get_gym_observation_spec(self) -> Dict[str, Any]:
        return {"shape": (3,), "dtype": "float32"}

    def convert_obs_to_gym_obs(self) -> np.ndarray:
        return self.velocity


class RoarPyCollisionSensorData:
    """The most recent collision: the two actors and the impulse (x, y, z, vehicle frame), N·s."""

    def __init__(self, actor: Any, other_actor: Any, impulse_normal: Any) -> None:
        self.actor = actor
        self.other_actor = other_actor
        self.impulse_normal = np.asarray(impulse_normal, dtype=OBS_DTYPE).reshape(3).copy()

    def get_gym_observation_spec(self) -> Dict[str, Any]:
        return {"shape": (3,), "dtype": "float32"}

    def convert_obs_to_gym_obs(self) -> np.ndarray:
        return self.impulse_normal


# --- sensors -------------------------------------------------------------------------------------


class RoarPySensor:
    """A sensor. ``get_last_gym_observation()`` returns its latest observation as an array."""

    sensordata_type: Any = None
    _obs_shape: Any = (3,)

    def __init__(self, name: str, control_timestep: float) -> None:
        self.name = name
        self._control_timestep = control_timestep
        self._last_obs: Any = None
        self._closed = False

    @property
    def control_timestep(self) -> float:
        return self._control_timestep

    def get_gym_observation_spec(self) -> Dict[str, Any]:
        return {"shape": self._obs_shape, "dtype": "float32"}

    async def receive_observation(self) -> Any:
        return self._last_obs

    def get_last_observation(self) -> Any:
        return self._last_obs

    def convert_obs_to_gym_obs(self, obs: Any) -> Any:
        return None if obs is None else obs.convert_obs_to_gym_obs()

    def close(self) -> None:
        self._closed = True

    def is_closed(self) -> bool:
        return self._closed

    def get_last_gym_observation(self) -> Optional[Any]:
        return self.convert_obs_to_gym_obs(self.get_last_observation())

    def _set_observation(self, obs: Any) -> None:  # racekit-internal: the runner's update
        self._last_obs = obs


class RoarPyLocationInWorldSensor(RoarPySensor):
    sensordata_type = RoarPyLocationInWorldSensorData

    def __init__(self, name: str = "location_sensor", control_timestep: float = 0.05) -> None:
        super().__init__(name, control_timestep)


class RoarPyRollPitchYawSensor(RoarPySensor):
    sensordata_type = RoarPyRollPitchYawSensorData

    def __init__(self, name: str = "rpy_sensor", control_timestep: float = 0.05) -> None:
        super().__init__(name, control_timestep)


class RoarPyVelocimeterSensor(RoarPySensor):
    sensordata_type = RoarPyVelocimeterSensorData

    def __init__(self, name: str = "velocity_sensor", control_timestep: float = 0.05) -> None:
        super().__init__(name, control_timestep)


class RoarPyCollisionSensor(RoarPySensor):
    sensordata_type = RoarPyCollisionSensorData

    def __init__(self, name: str = "collision_sensor", control_timestep: float = 0.05) -> None:
        super().__init__(name, control_timestep)


class RoarPyCameraSensor(RoarPySensor):
    """A stub: racekit renders no images, so every observation is ``None`` (not taught)."""

    def __init__(
        self, name: str = "camera_sensor", control_timestep: float = 0.05, target_data_type: Any = None
    ) -> None:
        super().__init__(name, control_timestep)
        self.target_data_type = target_data_type

    @property
    def image_size_width(self) -> int:
        return 0

    @property
    def image_size_height(self) -> int:
        return 0

    @property
    def fov(self) -> float:
        return 0.0

    def get_gym_observation_spec(self) -> Dict[str, Any]:
        return {"shape": None, "dtype": "uint8"}

    def convert_obs_to_gym_obs(self, obs: Any) -> Any:
        return None


class RoarPyOccupancyMapSensor(RoarPySensor):
    """A stub: racekit builds no occupancy map, so every observation is ``None`` (not taught)."""

    def __init__(self, name: str = "occupancy_map_sensor") -> None:
        super().__init__(name, 0.05)

    def get_gym_observation_spec(self) -> Dict[str, Any]:
        return {"shape": None, "dtype": "uint8"}

    def convert_obs_to_gym_obs(self, obs: Any) -> Any:
        return None


# --- actors --------------------------------------------------------------------------------------


class ActionValidationError(ValueError):
    """An action dictionary broke the interface's keys, types or ranges (a ``ValueError``)."""


def _is_real(value: Any) -> bool:
    return isinstance(value, numbers.Real) and not isinstance(value, (bool, np.bool_))


def validate_action(action: Any) -> Dict[str, float]:
    """Check an action dictionary's keys, types and ranges; raise ``ActionValidationError`` (a
    ``ValueError``) on a violation."""
    if not isinstance(action, dict):
        raise ActionValidationError(f"action must be a dict, not {type(action).__name__}")
    unknown = sorted(str(key) for key in action if key not in ACTION_SPEC)
    if unknown:
        raise ActionValidationError(f"unknown action keys: {unknown}")
    missing = [key for key in REQUIRED_ACTION_KEYS if key not in action]
    if missing:
        raise ActionValidationError(f"missing action keys: {missing}")
    clean: Dict[str, float] = {}
    for key, value in action.items():
        kind, low, high = ACTION_SPEC[key]
        if isinstance(value, np.ndarray) and value.size == 1:
            value = value.reshape(()).item()
        if kind == "real":
            if not _is_real(value):
                raise ActionValidationError(f"action[{key!r}] must be a real number, not {type(value).__name__}")
            number = float(value)
            if math.isnan(number) or not low <= number <= high:
                raise ActionValidationError(f"action[{key!r}] = {number!r} is outside [{low}, {high}]")
            clean[key] = number
        elif kind == "binary":
            if not isinstance(value, (bool, np.bool_, numbers.Integral)) or int(value) not in (0, 1):
                raise ActionValidationError(f"action[{key!r}] must be 0 or 1 (or a bool), not {value!r}")
            clean[key] = float(int(value))
        else:  # target_gear
            if not isinstance(value, numbers.Integral) or isinstance(value, (bool, np.bool_)):
                raise ActionValidationError(f"action[{key!r}] must be an int, not {type(value).__name__}")
            clean[key] = float(int(value))
    return clean


class RoarPyActor:
    """An actor that accepts actions. ``apply_action`` is a coroutine: ``await`` it."""

    def __init__(
        self, name: str, control_timestep: float = 0.05, force_real_control_timestep: bool = False
    ) -> None:
        self.name = name
        self._control_timestep = control_timestep
        self._force_real_control_timestep = force_real_control_timestep
        self._sensors: List[RoarPySensor] = []
        self._last_obs: Optional[Dict[str, Any]] = None
        self._closed = False

    @property
    def control_timestep(self) -> float:
        return self._control_timestep

    @property
    def force_real_control_timestep(self) -> bool:
        return self._force_real_control_timestep

    def get_sensors(self) -> Iterable[RoarPySensor]:
        return list(self._sensors)

    def get_action_spec(self) -> Dict[str, Any]:
        return {key: {"kind": kind, "low": low, "high": high} for key, (kind, low, high) in ACTION_SPEC.items()}

    async def _apply_action(self, action: Any) -> bool:
        raise NotImplementedError

    def close(self) -> None:
        self._closed = True

    def is_closed(self) -> bool:
        return self._closed

    async def apply_action(self, action: Any) -> bool:
        return await self._apply_action(action)

    def get_gym_observation_spec(self) -> Dict[str, Any]:
        return {sensor.name: sensor.get_gym_observation_spec() for sensor in self._sensors}

    async def receive_observation(self) -> Dict[str, Any]:
        self._last_obs = {sensor.name: sensor.get_last_observation() for sensor in self._sensors}
        return self._last_obs

    def get_last_observation(self) -> Optional[Dict[str, Any]]:
        return self._last_obs

    def get_last_gym_observation(self) -> Optional[Dict[str, Any]]:
        if self._last_obs is None:
            return None
        return self.convert_obs_to_gym_obs(self._last_obs)

    def convert_obs_to_gym_obs(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        return {
            sensor.name: sensor.convert_obs_to_gym_obs(observation.get(sensor.name))
            for sensor in self._sensors
        }


class RacekitVehicle(RoarPyActor):
    """The car a submission drives in racekit. Every action is validated, then held for the tick."""

    def __init__(self, name: str = "vehicle", control_timestep: float = 0.05) -> None:
        super().__init__(name, control_timestep)
        self.last_action: Dict[str, float] = {
            "throttle": 0.0, "steer": 0.0, "brake": 0.0, "hand_brake": 0.0, "reverse": 0.0,
        }
        self.actions_applied = 0

    async def _apply_action(self, action: Any) -> bool:
        clean = validate_action(action)
        self.last_action = clean
        self.actions_applied += 1
        return True
