"""``write_variant``: the "try a variant" idiom (plan roar-002 Phase 1, [fable] S3)."""

from __future__ import annotations

import pytest
import racekit
from conftest import RACEKIT
from racekit.check_submission import check_submission
from racekit.runner import run_race

UNIT_01 = RACEKIT / "agents" / "unit-01.py"


def test_a_variant_changes_only_the_named_constants_and_races(tmp_path):
    variant = racekit.write_variant(UNIT_01, tmp_path / "variant.py", {"TARGET_SPEED": "22.0", "STEER_GAIN": 7})
    original = UNIT_01.read_text(encoding="utf-8").splitlines()
    changed = variant.read_text(encoding="utf-8").splitlines()
    assert len(original) == len(changed)
    diff = [(a, b) for a, b in zip(original, changed) if a != b]
    assert diff == [
        ("STEER_GAIN = 8.0  # steering gain, divided by sqrt(speed)", "STEER_GAIN = 7  # steering gain, divided by sqrt(speed)"),
        ("TARGET_SPEED = 20.0  # m/s", "TARGET_SPEED = 22.0  # m/s"),
    ]
    assert check_submission(variant).ok
    assert run_race(variant, "oval", max_seconds=30.0).progress > 0


@pytest.mark.parametrize(("replacements", "match"), [
    ({"TOP_SPEED": "25.0"}, "TOP_SPEED is not assigned at module level"),
    ({"TARGET_SPEED": "25.0 +"}, "not a Python expression"),
    ({"current_index": "1"}, "current_index is not assigned at module level"),  # an attribute, not a constant
])
def test_a_missing_constant_or_a_bad_value_fails(tmp_path, replacements, match):
    with pytest.raises(ValueError, match=match):
        racekit.write_variant(UNIT_01, tmp_path / "variant.py", replacements)
    assert not (tmp_path / "variant.py").exists()


def test_a_duplicate_or_multi_target_constant_fails(tmp_path):
    source = tmp_path / "agent.py"
    source.write_text("SPEED = 1.0\nGAIN = 2.0\nSPEED = 3.0\nA = B = 4\nC: float = 5.0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="SPEED is assigned 2 times"):
        racekit.write_variant(source, tmp_path / "out.py", {"SPEED": "9.0"})
    with pytest.raises(ValueError, match="single-name assignment"):
        racekit.write_variant(source, tmp_path / "out.py", {"A": "9"})
    out = racekit.write_variant(source, tmp_path / "out.py", {"C": "6.5", "GAIN": "(1.0 +\n 2.0)"})
    assert out.read_text(encoding="utf-8") == (
        "SPEED = 1.0\nGAIN = (1.0 +\n 2.0)\nSPEED = 3.0\nA = B = 4\nC: float = 6.5\n")
