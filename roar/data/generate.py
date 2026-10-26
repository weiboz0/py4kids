"""The single seeded-data driver for *Applied Python: Autonomous Racing* (design 013 §4.3).

``PYTHONHASHSEED=0 uv run --group roar python roar/data/generate.py``

It runs its steps in a declared order and writes everything into ``roar/data/generated/``
(gitignored, regenerated on every CI run, never committed):

1. tracks (``gen_tracks.py``): ``generated/tracks/<name>.npz``;
2. the carla-like telemetry logs (added by roar-004);
3. the ``lab-check`` sample CSV (added by roar-002).

The checksum contract (plan roar-001 Phase C):

* every output is generated **twice in-process** and the two content hashes must agree;
* hashes are taken over ``np.round(values, 6)`` in a fixed field order, never raw bytes, so a 1-ulp
  libm difference cannot fail CI;
* the regenerated ``generated/checksums.json`` is written each run (gitignored, as recsys does);
  there is no tracked golden file, so a numpy bump under ``uv.lock`` legitimately re-pins;
* after writing, each file is re-read and re-hashed.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).resolve().parent
if str(DATA_DIR) not in sys.path:
    sys.path.insert(0, str(DATA_DIR))

import gen_tracks

GENERATED = DATA_DIR / "generated"


def track_outputs() -> dict[str, tuple[bytes, str]]:
    """Step 1: every named track, as ``relative path -> (npz bytes, content hash)``."""
    outputs = {}
    for name in gen_tracks.TRACK_NAMES:
        track = gen_tracks.build(name)
        arrays = track.arrays()
        outputs[f"tracks/{name}.npz"] = (gen_tracks.npz_bytes(arrays), gen_tracks.content_hash(arrays))
    return outputs


STEPS = (("tracks", track_outputs),)


def generate(out_dir: Path = GENERATED) -> dict[str, str]:
    checksums: dict[str, str] = {}
    for step, produce in STEPS:
        first = produce()
        second = produce()
        hashes_first = {path: digest for path, (_, digest) in first.items()}
        hashes_second = {path: digest for path, (_, digest) in second.items()}
        if hashes_first != hashes_second:
            raise SystemExit(f"FAIL: {step}: two in-process runs disagree (non-deterministic output)")
        for path, (payload, digest) in first.items():
            target = out_dir / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            with np.load(target) as loaded:
                reread = gen_tracks.content_hash({field: loaded[field] for field in gen_tracks.FIELDS})
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
