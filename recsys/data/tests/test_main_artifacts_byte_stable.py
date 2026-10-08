"""Byte-stability of the four main artifacts (plan recsys-014 Goal 1 — the hard gate).

Adding the U12 series + session log (``gen_sessions.py``) must not move a single byte of the data
every Unit 1–11 / Checkpoint A number is computed on. The sha256 pins below were captured from
``main`` 9d3cecf BEFORE any recsys-014 change. This test hashes the files CI just regenerated in
``recsys/data/generated/`` (zero regeneration cost here); it skips when that directory is absent.

NEP-19: the pins hold under ``uv.lock``. A numpy bump that changes the bit stream legitimately
re-pins these values, exactly as it re-pins every notebook number (design 011 §7).
"""

from __future__ import annotations

import hashlib

import pytest
from _common import GENERATED_DIR

GOAL1_PINS = {
    "catalog.csv.gz": "e4112a485b03c2922ea9cbb7b72b54392bb8add03e55e48c4e821d52460fbfea",
    "interactions.csv.gz": "151e6443fed4890f02f8fe5e89889b3ea9a9a86a5e11c58a14d18d48dd4bbbee",
    "keywords.csv.gz": "e3cc89b8c80f9e1539d25f693007d708a2c1b4eb29d6d5449253338a6d1e9981",
    "cold_partitions.json": "ba710208dcfce3f8d8ea8d56ace7a539cb2c79ed228254d6d5b4690377f38565",
}


@pytest.mark.parametrize("name", sorted(GOAL1_PINS))
def test_main_artifact_is_byte_identical_to_goal1_pin(name: str) -> None:
    if not GENERATED_DIR.is_dir():
        pytest.skip("CI-generated artifacts are absent; run gen_catalog.py and gen_interactions.py")
    path = GENERATED_DIR / name
    assert path.is_file(), f"generated directory is incomplete (missing {name})"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == GOAL1_PINS[name]
