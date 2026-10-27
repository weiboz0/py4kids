"""The single seeded-data driver for *Applied Python: Autonomous Racing* (design 013 §4.3).

``PYTHONHASHSEED=0 uv run --group roar python roar/data/generate.py``

It runs its steps in a declared order and writes everything into ``roar/data/generated/``
(gitignored, regenerated on every CI run, never committed):

1. tracks (``gen_tracks.py``): ``generated/tracks/<name>.npz`` for the three named tracks
   (``oval``, ``test-circuit``, ``monza-like``) and the seeded checkpoint tracks (plan roar-007:
   ``test-circuit-seed1`` … ``test-circuit-seed4``, Checkpoint A's training family, and
   ``test-circuit-seed2026``, its checkpoint track), all under the same checksum contract;
2. the carla-like car's sensor logs (``gen_sysid.py``, plan roar-004): a noisy ``monza-like`` race
   at global a_lat 3.5 and a noisy steady 15 m/s ``oval`` lap, recorded by the data-side driver
   (``drivers.py``) in the racekit sensor-log format, at ``generated/sysid/monza-like-seed0.csv``
   and ``generated/sysid/oval-steady-seed0.csv`` (Unit 8's system-identification data);
3. the ``lab-check`` sample CSV (plan roar-002): the starter on ``monza-like`` with actuator
   jitter 0.05 and seed 0, in the racekit-telemetry v1 format, at ``generated/lab/sample_telemetry.csv``
   (named by ``roar/curriculum/labs.yaml``; the lab notebooks are executed against it).

The checksum contract (plan roar-001 Phase C):

* every output is generated **twice in-process** and the two content hashes must agree;
* hashes are taken over ``np.round(values, 6)`` in a fixed field order, never raw bytes, so a 1-ulp
  libm difference cannot fail CI;
* the regenerated ``generated/checksums.json`` is written each run (gitignored, as recsys does);
  there is no tracked golden file, so a numpy bump under ``uv.lock`` legitimately re-pins;
* after writing, each file is re-read and re-hashed.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).resolve().parent
if str(DATA_DIR) not in sys.path:
    sys.path.insert(0, str(DATA_DIR))

import gen_sysid
import gen_tracks

GENERATED = DATA_DIR / "generated"


LAB_SAMPLE = "lab/sample_telemetry.csv"
LAB_TRACK = "monza-like"
LAB_JITTER = 0.05
LAB_SEED = 0
STARTER = DATA_DIR.parent / "projects" / "racekit" / "agents" / "starter.py"


def track_outputs(out_dir: Path) -> dict[str, tuple[bytes, str]]:
    """Step 1: every named and seeded track, as ``relative path -> (npz bytes, content hash)``."""
    outputs = {}
    for name in gen_tracks.ALL_NAMES:
        track = gen_tracks.build(name)
        arrays = track.arrays()
        outputs[f"tracks/{name}.npz"] = (gen_tracks.npz_bytes(arrays), gen_tracks.content_hash(arrays))
    return outputs


def rehash_track(path: Path) -> str:
    with np.load(path) as loaded:
        return gen_tracks.content_hash({field: loaded[field] for field in gen_tracks.FIELDS})


def telemetry_hash(telemetry: np.ndarray, meta: dict) -> str:
    """sha256 over the meta and ``np.round(column, 6)`` in the fixed column order (never raw bytes)."""
    digest = hashlib.sha256(json.dumps(meta, sort_keys=True).encode("ascii"))
    for name in telemetry.dtype.names:
        values = np.round(np.asarray(telemetry[name], dtype=np.float64), 6) + 0.0  # -0.0 -> 0.0
        digest.update(name.encode("ascii") + b"\0")
        digest.update(np.ascontiguousarray(values, dtype="<f8").tobytes())
    return digest.hexdigest()


def sysid_outputs(out_dir: Path) -> dict[str, tuple[bytes, str]]:
    """Step 2: the sensor logs, raced on the track step's freshly written tracks."""
    from racekit.telemetry import read_log_csv, write_log_csv

    outputs = {}
    for spec in gen_sysid.LOGS:
        log, meta = gen_sysid.record(spec, out_dir / "tracks")
        with tempfile.TemporaryDirectory() as scratch:
            path = write_log_csv(log, Path(scratch) / "log.csv", meta)
            payload = path.read_bytes()
            reread, reread_meta = read_log_csv(path)  # hash what a reader sees
        outputs[spec.name] = (payload, telemetry_hash(reread, reread_meta))
    return outputs


def rehash_log(path: Path) -> str:
    from racekit.telemetry import read_log_csv

    return telemetry_hash(*read_log_csv(path))


def lab_outputs(out_dir: Path) -> dict[str, tuple[bytes, str]]:
    """Step 3: the lab sample CSV, raced on the track step's freshly written ``monza-like``."""
    from racekit.cars import KinematicCar
    from racekit.runner import run_race
    from racekit.telemetry import race_meta, read_csv, write_csv

    track = out_dir / "tracks" / f"{LAB_TRACK}.npz"
    result = run_race(STARTER, track, car=KinematicCar(jitter=LAB_JITTER), seed=LAB_SEED)
    if not (result.finished and result.collisions == 0):
        raise SystemExit(f"FAIL: lab: the starter must finish {LAB_TRACK} cleanly ({result!r})")
    with tempfile.TemporaryDirectory() as scratch:
        path = write_csv(result.telemetry, Path(scratch) / "sample.csv", race_meta(result))
        payload = path.read_bytes()
        telemetry, meta = read_csv(path)  # hash what a reader sees
    return {LAB_SAMPLE: (payload, telemetry_hash(telemetry, meta))}


def rehash_csv(path: Path) -> str:
    from racekit.telemetry import read_csv

    return telemetry_hash(*read_csv(path))


# (step, produce(out_dir) -> {relative path: (bytes, content hash)}, rehash(written path) -> hash)
STEPS = (
    ("tracks", track_outputs, rehash_track),
    ("sysid", sysid_outputs, rehash_log),
    ("lab", lab_outputs, rehash_csv),
)


def generate(out_dir: Path = GENERATED) -> dict[str, str]:
    checksums: dict[str, str] = {}
    for step, produce, rehash in STEPS:
        first = produce(out_dir)
        second = produce(out_dir)
        hashes_first = {path: digest for path, (_, digest) in first.items()}
        hashes_second = {path: digest for path, (_, digest) in second.items()}
        if hashes_first != hashes_second:
            raise SystemExit(f"FAIL: {step}: two in-process runs disagree (non-deterministic output)")
        for path, (payload, digest) in first.items():
            target = out_dir / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            reread = rehash(target)
            if reread != digest:
                raise SystemExit(f"FAIL: {path}: the written file does not re-hash to its checksum")
            checksums[path] = digest
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "checksums.json").write_text(
        json.dumps(checksums, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return checksums


def main() -> int:
    start = time.perf_counter()
    checksums = generate()
    elapsed = time.perf_counter() - start
    for path, digest in sorted(checksums.items()):
        print(f"{path}: sha256 {digest[:16]}…")
    print(f"generate: {len(checksums)} outputs, two-run checksums agree, {elapsed:.2f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
