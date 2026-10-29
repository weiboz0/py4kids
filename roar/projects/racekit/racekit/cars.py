"""Car models (design 013 §4.4). roar-001 ships the kinematic bicycle; roar-004 adds the dynamic
and carla-like cars behind the same ``Car`` protocol.

Every number a racekit car produces is a *model* number: re-measure on the official simulator.
"""

# The dynamic car's inner loop clips with conditional expressions instead of min()/max(): the same
# values (the operands are never NaN), about 20% faster per tick.
# ruff: noqa: FURB136

from __future__ import annotations

import math
import random
from collections import deque
from types import MappingProxyType
from typing import (  # Protocol: 3.8+
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    Union,
)

G = 9.81  # m/s^2
SPIN_MIN_SPEED = 5.0  # m/s: the spin-out rule applies above this speed (separate from the blend band)


class Car(Protocol):
    """What the runner needs from a car. State is in the ROAR frame (x forward/east, y left)."""

    x: float
    y: float
    yaw: float
    v: float

    def reset(self, x: float, y: float, yaw: float, v: float = 0.0) -> None: ...

    def advance(
        self, throttle: float, steer: float, brake: float, hand_brake: float, reverse: float,
        dt: float, substeps: int,
    ) -> None: ...

    def velocity(self) -> Tuple[float, float]: ...


class KinematicCar:
    """A kinematic bicycle about the rear axle, with a simple longitudinal map.

    * steering: ``steer`` in [-1, 1] maps to the wheel angle ``δ = -steer · δ_max`` (a positive
      steer turns right, as in the official interface); yaw rate ``v · tan δ / L``;
    * longitudinal: ``a = a_throttle · throttle`` (backwards when ``reverse``), minus
      ``a_brake · brake`` against the motion, minus quadratic drag ``c_drag · v · |v|``;
      braking stops the car, it never reverses it;
    * integration: RK4 (or explicit Euler, for teaching) over ``substeps`` equal substeps per tick,
      in plain ``math`` scalars;
    * **actuator jitter** (plan roar-002; design 013 §4.4 puts noise on roar-004's carla-like car,
      which reuses this protocol): with ``jitter = σ > 0`` each tick adds ``gauss(0, σ)`` to the
      throttle (clipped to [0, 1]) and then ``gauss(0, σ)`` to the steer (clipped to [-1, 1]), drawn
      from ``random.Random(seed)``; the brake is never jittered. ``run_race(seed=...)`` calls
      ``seed()`` before each race. With ``jitter = 0`` (the default) no random number is drawn and
      the car is exactly deterministic.
    * **actuator lag** (plan roar-005, taught in Unit 5): with ``lag_ticks = N > 0`` the action takes
      effect ``N`` control ticks after it is commanded, through the same FIFO as ``DynamicCar``'s.
      The FIFO holds (throttle, steer, brake) only; ``hand_brake`` and ``reverse`` act immediately
      (as in ``DynamicCar``). The jitter is drawn at command time (first) and the jittered action is
      queued (then); ``reset()`` refills the queue with ``N`` zero actions, so a respawn discards the
      queued commands. With ``lag_ticks = 0`` (the default) the queue is never used and the car is exactly
      the lag-free car.

    The steady-state circle radius is ``L / tan δ``.

    **Brake creep** (a documented model property, kept so Unit 3's taught parity holds): under
    full brake near rest the car can creep at a few cm/s instead of stopping (from ``v = 0.01``,
    1 s of full brake still leaves ``v ≈ 0.01``), because a substep that starts just above 0 straddles
    the jump in ``v'`` at 0 and the RK4 stages cancel; the creep is bounded by ``a_brake · h``.
    ``agents/unit-03.py``'s ``stopping_tick`` reproduces it. ``DynamicCar`` stops exactly instead.
    No race brakes to rest, so no race time is affected.
    """

    def __init__(
        self,
        wheelbase: float = 2.875,
        max_steer: float = math.radians(70.0),
        a_throttle: float = 6.0,
        a_brake: float = 8.0,
        c_drag: float = 4.0e-4,
        integrator: str = "rk4",
        jitter: float = 0.0,
        lag_ticks: int = 0,
    ) -> None:
        if integrator not in ("rk4", "euler"):
            raise ValueError("integrator must be 'rk4' or 'euler'")
        if not jitter >= 0.0:
            raise ValueError("jitter must be a standard deviation >= 0")
        if isinstance(lag_ticks, bool) or lag_ticks < 0 or int(lag_ticks) != lag_ticks:
            raise ValueError("lag_ticks must be an int >= 0")
        self.wheelbase = wheelbase
        self.max_steer = max_steer
        self.a_throttle = a_throttle
        self.a_brake = a_brake
        self.c_drag = c_drag
        self.integrator = integrator
        self.jitter = float(jitter)
        self.lag_ticks = int(lag_ticks)
        self.queue: deque = deque([(0.0, 0.0, 0.0)] * self.lag_ticks)
        self._rng = random.Random(0)
        self.x = self.y = self.yaw = self.v = 0.0

    def seed(self, seed: int) -> None:
        """Restart the jitter's random stream (``run_race`` calls it with the race seed)."""
        self._rng = random.Random(seed)

    def reset(self, x: float, y: float, yaw: float, v: float = 0.0) -> None:
        self.x, self.y, self.yaw, self.v = float(x), float(y), float(yaw), float(v)
        self.queue = deque([(0.0, 0.0, 0.0)] * self.lag_ticks)

    def velocity(self) -> Tuple[float, float]:
        return self.v * math.cos(self.yaw), self.v * math.sin(self.yaw)

    def advance(
        self, throttle: float, steer: float, brake: float, hand_brake: float, reverse: float,
        dt: float, substeps: int,
    ) -> None:
        """Advance one control tick of ``dt`` seconds with the action held constant."""
        if self.jitter != 0.0:
            gauss = self._rng.gauss
            throttle = min(1.0, max(0.0, throttle + gauss(0.0, self.jitter)))
            steer = min(1.0, max(-1.0, steer + gauss(0.0, self.jitter)))
        if self.lag_ticks:
            self.queue.append((throttle, steer, brake))
            throttle, steer, brake = self.queue.popleft()
        tan_delta = math.tan(-steer * self.max_steer)
        k_yaw = tan_delta / self.wheelbase
        drive = self.a_throttle * throttle * (-1.0 if reverse >= 0.5 else 1.0)
        braking = self.a_brake * max(brake, 1.0 if hand_brake >= 0.5 else 0.0)
        c = self.c_drag
        h = dt / substeps
        x, y, yaw, v = self.x, self.y, self.yaw, self.v
        cos, sin = math.cos, math.sin

        def accel(speed: float) -> float:
            a = drive - c * speed * abs(speed)
            if speed > 0.0:
                a -= braking
            elif speed < 0.0:
                a += braking
            return a

        for _ in range(substeps):
            v_old = v
            if self.integrator == "euler":
                x += h * v * cos(yaw)
                y += h * v * sin(yaw)
                yaw += h * v * k_yaw
                v += h * accel(v)
            else:
                # RK4 on (x, y, yaw, v) with x' = v cos(yaw), y' = v sin(yaw), yaw' = v k, v' = a(v)
                k1x, k1y, k1w, k1v = v * cos(yaw), v * sin(yaw), v * k_yaw, accel(v)
                v2, w2 = v + 0.5 * h * k1v, yaw + 0.5 * h * k1w
                k2x, k2y, k2w, k2v = v2 * cos(w2), v2 * sin(w2), v2 * k_yaw, accel(v2)
                v3, w3 = v + 0.5 * h * k2v, yaw + 0.5 * h * k2w
                k3x, k3y, k3w, k3v = v3 * cos(w3), v3 * sin(w3), v3 * k_yaw, accel(v3)
                v4, w4 = v + h * k3v, yaw + h * k3w
                k4x, k4y, k4w, k4v = v4 * cos(w4), v4 * sin(w4), v4 * k_yaw, accel(v4)
                s = h / 6.0
                x += s * (k1x + 2.0 * k2x + 2.0 * k3x + k4x)
                y += s * (k1y + 2.0 * k2y + 2.0 * k3y + k4y)
                yaw += s * (k1w + 2.0 * k2w + 2.0 * k3w + k4w)
                v += s * (k1v + 2.0 * k2v + 2.0 * k3v + k4v)
            # braking (or drag) brings the car to rest; it never pushes it backwards
            if braking > 0.0:
                crossed_zero = (v_old > 0.0 > v) or (v_old < 0.0 < v)
                held_at_rest = v_old == 0.0 and abs(drive) <= braking
                if crossed_zero or held_at_rest:
                    v = 0.0
        self.x, self.y, self.v = x, y, v
        self.yaw = (yaw + math.pi) % (2.0 * math.pi) - math.pi


class DynamicCar:
    """A dynamic bicycle with saturating tyres (plan roar-004; design 013 §4.4, taught in Unit 6).

    State, in the ROAR frame: the centre of gravity ``x``, ``y``; the heading ``yaw``; the body-frame
    velocity ``vx`` (forward) and ``vy`` (left); the yaw rate ``r``; the actual wheel angle
    ``delta``; and the actuator-lag queue. ``v`` is the signed speed ``±‖(vx, vy)‖`` with the sign of
    ``vx``; ``velocity()`` is world-frame.

    * **Steering**: ``steer`` in [-1, 1] sets the target wheel angle ``-steer · max_steer`` (a
      positive steer turns right, as in ``KinematicCar``); the wheel moves towards it at
      ``steer_rate`` once per substep.
    * **Actuator lag**: the action takes effect ``lag_ticks`` control ticks after it is commanded.
    * **Longitudinal**: ``m · (a_throttle · throttle (backwards when reverse) − a_brake · brake
      against the motion − c_drag · vx · |vx|)``, split between the axles in proportion to their
      static load (an all-wheel-drive model choice), each axle's force clipped to ``±μ F_z``.
    * **Tyres**: ``F_y = −√((μ F_z)² − F_x²) · sin(C · atan(B · α))`` per axle (a per-axle friction
      circle), with slip angles ``α_f = atan2(vy + l_f r, u) − δ``, ``α_r = atan2(vy − l_r r, u)``
      and ``u = max(|vx|, v_kin_lo)``. Static loads: there is no load transfer.
    * **Low speed**: below ``v_kin_hi`` the derivatives blend (weight
      ``clip((|vx| − v_kin_lo) / (v_kin_hi − v_kin_lo), 0, 1)``) towards a kinematic bicycle whose
      acceleration vector is capped at ``μ g``; no state is projected after a step.
    * **Brake stop**: a substep that starts with the brake on, braking ≥ |drive|, and
      ``‖v‖ ≤ min(net deceleration, μ g) · h`` ends at rest (``vx = vy = r = 0``; zeroing ``r`` is a
      labelled simplification, an angular jump at rest). Under braking, a sign change of ``vx`` below
      0.5 m/s clamps ``vx`` (only) to 0. Unlike ``KinematicCar`` the car stops exactly.
    * **Integration**: RK4 over ``substeps`` substeps per tick, in plain ``math`` scalars.
    * **Spin-out**: ``spun_out()`` is ``|β| > spin_beta`` (25°) at a speed above ``SPIN_MIN_SPEED``
      (5 m/s), with sideslip ``β = atan2(vy, |vx|)``. The runner treats a spin-out as a major
      collision.
    * **Grip**: ``mu`` is a scalar, or a sequence of ``GRIP_SECTIONS`` (6) values, one per grip
      section (``racekit.tracks.grip_sections``). A per-section car needs ``attach_track(track)``
      (the runner calls it once per race); it finds its section with ``track.nearest`` from a carried
      hint (reset by ``reset()``) and reads μ once per tick. Advancing a per-section car without a
      track raises.
    * **Noise**: ``jitter`` (throttle) and ``steer_jitter`` are standard deviations. Whenever either
      is non-zero, each tick draws one ``gauss`` for the throttle and then one for the steer from
      ``random.Random(seed)`` (clipped to [0, 1] and [-1, 1]); the brake is never jittered.
      ``run_race(seed=...)`` calls ``seed()``. With both 0 no random number is drawn.

    Model limits (labelled): no load transfer, gears, power limit or tyre temperature; reversing at
    speed is not modelled (the slip-angle signs assume forward motion). Every number is a *model*
    number.
    """

    def __init__(
        self,
        mass: float = 1845.0,
        yaw_inertia: float = 2900.0,
        lf: float = 1.40,
        wheelbase: float = 2.875,
        max_steer: float = math.radians(70.0),
        steer_rate: float = math.radians(360.0),
        a_throttle: float = 6.0,
        a_brake: float = 8.0,
        c_drag: float = 4.0e-4,
        mu: Union[float, Sequence[float]] = 1.0,
        tyre_b: float = 10.0,
        tyre_c: float = 1.6,
        lag_ticks: int = 1,
        jitter: float = 0.0,
        steer_jitter: float = 0.0,
        v_kin_lo: float = 1.0,
        v_kin_hi: float = 2.0,
        spin_beta: float = math.radians(25.0),
    ) -> None:
        if not (jitter >= 0.0 and steer_jitter >= 0.0):
            raise ValueError("jitter and steer_jitter must be standard deviations >= 0")
        if lag_ticks < 0 or int(lag_ticks) != lag_ticks:
            raise ValueError("lag_ticks must be an int >= 0")
        if not 0.0 < v_kin_lo < v_kin_hi:
            raise ValueError("need 0 < v_kin_lo < v_kin_hi")
        self.mass = float(mass)
        self.yaw_inertia = float(yaw_inertia)
        self.lf = float(lf)
        self.wheelbase = float(wheelbase)
        self.lr = self.wheelbase - self.lf
        self.max_steer = max_steer
        self.steer_rate = steer_rate
        self.a_throttle = a_throttle
        self.a_brake = a_brake
        self.c_drag = c_drag
        self.tyre_b = tyre_b
        self.tyre_c = tyre_c
        self.lag_ticks = int(lag_ticks)
        self.jitter = float(jitter)
        self.steer_jitter = float(steer_jitter)
        self.v_kin_lo = v_kin_lo
        self.v_kin_hi = v_kin_hi
        self.spin_beta = spin_beta
        self.fz_f = self.mass * G * self.lr / self.wheelbase  # static axle loads
        self.fz_r = self.mass * G * self.lf / self.wheelbase
        self._grip_table: Optional[Callable[[str], Sequence[float]]] = None  # set by carla_like
        self.mu = mu
        self.track: Any = None
        self._sections: Optional[List[int]] = None
        self._hint = 0
        self.mu_now = 1.0
        self._rng = random.Random(0)
        self.reset(0.0, 0.0, 0.0, 0.0)

    # --- grip ---------------------------------------------------------------------------------

    @property
    def mu(self) -> Union[float, Tuple[float, ...]]:
        return self._mu

    @mu.setter
    def mu(self, value: Union[float, Sequence[float]]) -> None:
        if isinstance(value, (int, float)):
            self._mu: Union[float, Tuple[float, ...]] = float(value)
            self._mu_table: Optional[Tuple[float, ...]] = None
            return
        from .tracks import GRIP_SECTIONS

        table = tuple(float(m) for m in value)
        if len(table) != GRIP_SECTIONS:
            raise ValueError(f"a per-section mu needs {GRIP_SECTIONS} values, got {len(table)}")
        self._mu = table
        self._mu_table = table

    @property
    def per_section(self) -> bool:
        """True when μ varies by grip section (the car then needs ``attach_track``)."""
        return self._mu_table is not None or self._grip_table is not None

    def attach_track(self, track: Any) -> None:
        """Tell the car which track it races on (the runner calls this once per race)."""
        from .tracks import grip_sections

        self.track = track
        if self._grip_table is not None:
            self.mu = self._grip_table(track.name)
        self._sections = [int(i) for i in grip_sections(track)] if self.per_section else None
        self._hint = 0

    # --- the car protocol ---------------------------------------------------------------------

    def seed(self, seed: int) -> None:
        """Restart the jitter's random stream (``run_race`` calls it with the race seed)."""
        self._rng = random.Random(seed)

    def reset(self, x: float, y: float, yaw: float, v: float = 0.0) -> None:
        self.x, self.y, self.yaw = float(x), float(y), float(yaw)
        self.vx, self.vy, self.r, self.delta = float(v), 0.0, 0.0, 0.0
        self.queue: deque = deque([(0.0, 0.0, 0.0)] * self.lag_ticks)
        self.v = self.vx
        self._hint = 0

    def velocity(self) -> Tuple[float, float]:
        c, s = math.cos(self.yaw), math.sin(self.yaw)
        return self.vx * c - self.vy * s, self.vx * s + self.vy * c

    def sideslip(self) -> float:
        """The body sideslip angle ``β = atan2(vy, |vx|)`` in radians (0 at rest)."""
        return math.atan2(self.vy, abs(self.vx)) if abs(self.vx) > 1e-9 or self.vy else 0.0

    def spun_out(self) -> bool:
        """The spin-out predicate: ``|β| > spin_beta`` at a speed above ``SPIN_MIN_SPEED``."""
        return math.hypot(self.vx, self.vy) > SPIN_MIN_SPEED and abs(self.sideslip()) > self.spin_beta

    def _grip_now(self) -> float:
        if self._mu_table is None and self._grip_table is None:
            return self._mu  # type: ignore[return-value]
        if self._sections is None or self.track is None or self._mu_table is None:
            raise RuntimeError(
                "this DynamicCar has a per-section mu and no track: call attach_track(track) first "
                "(run_race does this once per race)"
            )
        self._hint, _, _, _ = self.track.nearest(self.x, self.y, self._hint)
        return self._mu_table[self._sections[self._hint]]

    def advance(
        self, throttle: float, steer: float, brake: float, hand_brake: float, reverse: float,
        dt: float, substeps: int,
    ) -> None:
        """Advance one control tick of ``dt`` seconds with the action held constant."""
        if self.jitter or self.steer_jitter:
            gauss = self._rng.gauss
            throttle = min(1.0, max(0.0, throttle + gauss(0, self.jitter)))
            steer = min(1.0, max(-1.0, steer + gauss(0, self.steer_jitter)))
        if self.lag_ticks:
            self.queue.append((throttle, steer, brake))
            throttle, steer, brake = self.queue.popleft()
        mu = self.mu_now = self._grip_now()
        target = -steer * self.max_steer
        drive = self.a_throttle * throttle * (-1.0 if reverse >= 0.5 else 1.0)
        braking = self.a_brake * max(brake, 1.0 if hand_brake >= 0.5 else 0.0)
        h = dt / substeps
        half_h = 0.5 * h
        sixth_h = h / 6
        m, iz, lf, lr, wheelbase = self.mass, self.yaw_inertia, self.lf, self.lr, self.wheelbase
        fz_f, fz_r = self.fz_f, self.fz_r
        c_drag, tyre_b, tyre_c = self.c_drag, self.tyre_b, self.tyre_c
        v_lo, v_hi = self.v_kin_lo, self.v_kin_hi
        v_band = v_hi - v_lo
        m_g = m * G
        fmax_f, fmax_r = mu * fz_f, mu * fz_r
        cap = mu * G
        step = self.steer_rate * h
        sin, cos, tan, hypot = math.sin, math.cos, math.tan, math.hypot
        x, y, psi, vx, vy, r, delta = self.x, self.y, self.yaw, self.vx, self.vy, self.r, self.delta

        for _ in range(substeps):
            # the steering actuator: rate-limited towards its target, once per substep
            change = target - delta
            change = change if change < step else step
            delta += change if change > -step else -step
            d = delta
            cos_d, sin_d, tan_d = cos(d), sin(d), tan(d)
            # the stop event: a brake that can stop the car within this substep does
            toward = braking - (drive if vx > 0 else -drive if vx < 0 else 0.0) + c_drag * vx * vx
            toward = cap if cap < toward else toward  # a deceleration, bounded by the grip
            if braking > 0.0 and abs(drive) <= braking and hypot(vx, vy) <= toward * h:
                vx = 0.0
                vy = 0.0
                r = 0.0
                continue
            vx0 = vx
            # RK4, unrolled; each stage evaluates the same derivative (_rhs below, inlined)
            k1 = _rhs(psi, vx, vy, r, drive, braking, c_drag, m, m_g, fz_f, fmax_f, fmax_r, v_lo,
                      v_band, lf, lr, iz, wheelbase, d, cos_d, sin_d, tan_d, tyre_b, tyre_c, cap)
            k2 = _rhs(psi + half_h * k1[2], vx + half_h * k1[3], vy + half_h * k1[4],
                      r + half_h * k1[5], drive, braking, c_drag, m, m_g, fz_f, fmax_f, fmax_r,
                      v_lo, v_band, lf, lr, iz, wheelbase, d, cos_d, sin_d, tan_d, tyre_b, tyre_c, cap)
            k3 = _rhs(psi + half_h * k2[2], vx + half_h * k2[3], vy + half_h * k2[4],
                      r + half_h * k2[5], drive, braking, c_drag, m, m_g, fz_f, fmax_f, fmax_r,
                      v_lo, v_band, lf, lr, iz, wheelbase, d, cos_d, sin_d, tan_d, tyre_b, tyre_c, cap)
            k4 = _rhs(psi + h * k3[2], vx + h * k3[3], vy + h * k3[4], r + h * k3[5], drive,
                      braking, c_drag, m, m_g, fz_f, fmax_f, fmax_r, v_lo, v_band, lf, lr, iz,
                      wheelbase, d, cos_d, sin_d, tan_d, tyre_b, tyre_c, cap)
            x = x + sixth_h * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
            y = y + sixth_h * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
            psi = psi + sixth_h * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
            vx = vx + sixth_h * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3])
            vy = vy + sixth_h * (k1[4] + 2 * k2[4] + 2 * k3[4] + k4[4])
            r = r + sixth_h * (k1[5] + 2 * k2[5] + 2 * k3[5] + k4[5])
            if braking > 0.0 and ((vx0 > 0 > vx) or (vx0 < 0 < vx)) and hypot(vx, vy) < 0.5:
                vx = 0.0  # longitudinal only: vy and r stay with the (μg-bounded) forces
        self.x, self.y, self.vx, self.vy, self.r, self.delta = x, y, vx, vy, r, delta
        self.yaw = (psi + math.pi) % (2 * math.pi) - math.pi
        self.v = math.copysign(math.hypot(vx, vy), vx) if vx else math.hypot(vx, vy)


# Test hook: set to a list to record (F_x front, F_y front, μF_z front, F_x rear, F_y rear, μF_z rear)
# at every RK4 stage; None (the default) records nothing.
_force_log: Optional[List[Tuple[float, float, float, float, float, float]]] = None


def _rhs(
    psi: float, vx: float, vy: float, r: float, drive: float, braking: float, c_drag: float,
    m: float, m_g: float, fz_f: float, fmax_f: float, fmax_r: float, v_lo: float, v_band: float,
    lf: float, lr: float, iz: float, wheelbase: float, d: float, cos_d: float, sin_d: float,
    tan_d: float, tyre_b: float, tyre_c: float, cap: float,
) -> Tuple[float, float, float, float, float, float]:
    """The dynamic car's derivative ``(x', y', ψ', vx', vy', r')`` at one RK4 stage."""
    ax_long = drive - c_drag * vx * abs(vx)
    if vx > 0:
        ax_long -= braking
    elif vx < 0:
        ax_long += braking
    fx = m * ax_long
    fx_f = fx * fz_f / m_g  # the longitudinal force split by static load (all-wheel drive)
    fx_r = fx - fx_f
    lim = fx_f if fx_f < fmax_f else fmax_f
    fx_f = lim if lim > -fmax_f else -fmax_f
    lim = fx_r if fx_r < fmax_r else fmax_r
    fx_r = lim if lim > -fmax_r else -fmax_r
    avx = abs(vx)
    u = v_lo if v_lo > avx else avx
    alpha_f = math.atan2(vy + lf * r, u) - d
    alpha_r = math.atan2(vy - lr * r, u)
    # the tyres: the lateral force left inside each axle's friction circle, shaped by C·atan(B·α)
    fyf = -math.sqrt(max(0.0, fmax_f * fmax_f - fx_f * fx_f)) * math.sin(tyre_c * math.atan(tyre_b * alpha_f))
    fyr = -math.sqrt(max(0.0, fmax_r * fmax_r - fx_r * fx_r)) * math.sin(tyre_c * math.atan(tyre_b * alpha_r))
    if _force_log is not None:  # a test hook: the friction-circle regression guard
        _force_log.append((fx_f, fyf, fmax_f, fx_r, fyr, fmax_r))
    c, s = math.cos(psi), math.sin(psi)
    dvx = (fx_f * cos_d - fyf * sin_d + fx_r) / m + vy * r
    dvy = (fx_f * sin_d + fyf * cos_d + fyr) / m - vx * r
    dr = (lf * (fx_f * sin_d + fyf * cos_d) - lr * fyr) / iz
    w = (avx - v_lo) / v_band
    w = w if w > 0.0 else 0.0
    w = w if w < 1.0 else 1.0
    if w < 1.0:
        # the kinematic regime: the acceleration vector (longitudinal, lateral) stays within μg
        rk = vx * tan_d / wheelbase
        relax = (lr * rk - vy) / 0.1
        relax = relax if relax < cap else cap
        relax = relax if relax > -cap else -cap
        ay_k = vx * rk + relax  # centripetal plus the sideslip relaxation
        ay_k = ay_k if ay_k < cap else cap
        ay_k = ay_k if ay_k > -cap else -cap
        ax_cap = math.sqrt(max(0.0, cap * cap - ay_k * ay_k))
        ax_k = ax_long if ax_long < ax_cap else ax_cap
        ax_k = ax_k if ax_k > -ax_cap else -ax_cap
        dvy = w * dvy + (1 - w) * (ay_k - vx * r)
        dr = w * dr + (1 - w) * (rk - r) / 0.1
        dvx = w * dvx + (1 - w) * (ax_k + vy * r)
    return vx * c - vy * s, vx * s + vy * c, r, dvx, dvy, dr


# The perturbed carla-like family (plan roar-010; design 013 §4.4 v4.9): each factor multiplies one of
# the car's parameters, drawn uniformly from its range, in this order. The ranges are the book's
# choice (a model of model error, not a measurement of CARLA's): grip from -8 % to 0 %, the rest a few
# per cent either way. "mass" scales the mass and the yaw inertia together; "grip" scales every
# section's mu. The lag is not perturbed (``carla_like(lag_ticks=...)`` changes it on its own).
PERTURBATION_FAMILY: Mapping[str, Tuple[float, float]] = MappingProxyType({
    "grip": (0.92, 1.00),
    "steering": (0.95, 1.05),
    "throttle": (0.90, 1.10),
    "brake": (0.90, 1.05),
    "mass": (0.95, 1.10),
    "drag": (0.90, 1.10),
})


def perturbation_factors(k: int) -> Dict[str, float]:
    """The factors of the perturbed car number ``k``: one ``uniform(low, high)`` per entry of
    ``PERTURBATION_FAMILY``, in its order, from ``random.Random(f"perturb:{k}")``. Deterministic: the
    same ``k`` gives the same factors on every machine. Each factor is relative (1.0 is the car of
    ``carla_like()``)."""
    if isinstance(k, bool) or not isinstance(k, int):
        raise TypeError("k must be an int")
    rng = random.Random(f"perturb:{k}")
    return {name: rng.uniform(low, high) for name, (low, high) in PERTURBATION_FAMILY.items()}


class _ScaledGrip:
    """A track's per-section grip, every section multiplied by one factor (a perturbed car's)."""

    def __init__(self, table: Callable[[str], Sequence[float]], factor: float) -> None:
        self.table = table
        self.factor = factor

    def __call__(self, track_name: str) -> Tuple[float, ...]:
        return tuple(mu * self.factor for mu in self.table(track_name))


def carla_like(noise: bool = False, perturb: Optional[int] = None, lag_ticks: Optional[int] = None) -> DynamicCar:
    """The book's stand-in for CARLA: a ``DynamicCar`` with its own (unpublished) parameters and a
    seeded per-section grip that it takes from the track it is raced on. ``noise=True`` adds a
    seeded throttle jitter (``run_race(seed=...)`` seeds it).

    ``perturb=k`` (an int) builds car ``k`` of the perturbed family: its mass and yaw inertia, steering
    gain, throttle and brake authority, drag and grip are each multiplied by
    ``perturbation_factors(k)`` (ranges in ``PERTURBATION_FAMILY``). ``lag_ticks=N`` (an int >= 0)
    replaces the car's actuator lag. With ``perturb=None`` and ``lag_ticks=None`` (the defaults) it is
    exactly the unperturbed car."""
    from . import _truth

    if lag_ticks is not None and (isinstance(lag_ticks, bool) or not isinstance(lag_ticks, int) or lag_ticks < 0):
        raise ValueError("lag_ticks must be None or an int >= 0")
    # unperturbed, every factor is 1.0 (x * 1.0 == x exactly, so the car is today's to the bit)
    f = perturbation_factors(perturb) if perturb is not None else dict.fromkeys(PERTURBATION_FAMILY, 1.0)
    car = DynamicCar(
        mass=_truth.MASS * f["mass"], yaw_inertia=_truth.YAW_INERTIA * f["mass"], lf=_truth.LF,
        wheelbase=_truth.WHEELBASE, max_steer=_truth.MAX_STEER * f["steering"],
        a_throttle=_truth.A_THROTTLE * f["throttle"], a_brake=_truth.A_BRAKE * f["brake"],
        c_drag=_truth.C_DRAG * f["drag"], tyre_b=_truth.TYRE_B, tyre_c=_truth.TYRE_C,
        lag_ticks=_truth.LAG_TICKS if lag_ticks is None else lag_ticks,
        jitter=_truth.NOISE_SIGMA if noise else 0.0,
    )
    car._grip_table = _truth.grip_table if perturb is None else _ScaledGrip(_truth.grip_table, f["grip"])
    return car
