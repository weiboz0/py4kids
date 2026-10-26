"""The telemetry CSV schema (plan roar-001 Phase D)."""

from __future__ import annotations

import numpy as np
import pytest
from conftest import STARTER
from racekit.runner import run_race
from racekit.telemetry import COLUMNS, read_csv, write_csv


def test_csv_round_trip_with_the_fixed_schema(tmp_path):
    result = run_race(STARTER, "oval", max_seconds=5.0)
    path = write_csv(result.telemetry, tmp_path / "telemetry.csv")
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "t,x,y,yaw,v,throttle,steer,brake,progress,offset"
    assert COLUMNS == result.telemetry.dtype.names
    assert len(lines) == 1 + result.ticks
    back = read_csv(path)
    assert back.dtype == result.telemetry.dtype
    for name in COLUMNS:
        assert np.allclose(back[name], result.telemetry[name], atol=1e-6)
    assert write_csv(back, tmp_path / "again.csv").read_bytes() == path.read_bytes()


def test_bad_csvs_are_rejected(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("t,x,y\n0,1,2\n")
    with pytest.raises(ValueError, match="header"):
        read_csv(bad)
    short = tmp_path / "short.csv"
    short.write_text(",".join(COLUMNS) + "\n0.05,1,2\n")
    with pytest.raises(ValueError, match="line 2"):
        read_csv(short)
    with pytest.raises(ValueError, match="columns"):
        write_csv(np.zeros(3, dtype=[("t", "f8")]), tmp_path / "x.csv")
