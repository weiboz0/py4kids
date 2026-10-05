"""Integrity check for the committed GloVe subset artifact (plan recsys-009, design 011 §6).

``recsys/data/glove/glove_subset.npy`` is a **committed, tracked** artifact (it is NOT under the
gitignored ``recsys/data/generated/``). This check — run in ``scripts/ci-local.sh`` step 1, REAL
and executed (never skipped) — mirrors the catalog checksum discipline: it fails unless the
committed ``.npy``

1. matches the ``sha256`` recorded in its ``glove_subset.json`` sidecar, and
2. is under a hard ``1 MB`` size cap (the publish-safe vocabulary-restricted subset is ~0.12 MB).

numpy-free / dependency-light (stdlib only) so it adds no cost to the registry+lint step.

Run::

    uv run python -m tools.glove_integrity
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

SIZE_CAP_BYTES = 1_000_000  # hard cap: the subset is ~0.12 MB; > 1 MB means it is not the subset
GLOVE_DIR = Path(__file__).resolve().parents[1] / "recsys" / "data" / "glove"
NPY_PATH = GLOVE_DIR / "glove_subset.npy"
JSON_PATH = GLOVE_DIR / "glove_subset.json"


def check() -> None:
    if not NPY_PATH.is_file():
        sys.exit(f"FAIL: committed GloVe subset missing: {NPY_PATH}")
    if not JSON_PATH.is_file():
        sys.exit(f"FAIL: GloVe sidecar missing: {JSON_PATH}")

    sidecar = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    expected = sidecar.get("sha256")
    if not expected:
        sys.exit(f"FAIL: GloVe sidecar {JSON_PATH.name} has no sha256")

    data = NPY_PATH.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        sys.exit(
            f"FAIL: GloVe subset sha256 mismatch: {NPY_PATH.name} is {actual}, "
            f"sidecar records {expected}"
        )

    size = len(data)
    if size >= SIZE_CAP_BYTES:
        sys.exit(
            f"FAIL: GloVe subset {NPY_PATH.name} is {size / 1_000_000:.3f} MB, "
            f">= {SIZE_CAP_BYTES / 1_000_000:.1f} MB cap"
        )

    print(f"glove integrity: {NPY_PATH.name} OK (sha256 {actual[:16]}…, {size / 1_000_000:.3f} MB)")


if __name__ == "__main__":
    check()
