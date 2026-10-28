"""``racekit.sysid_data``: the committed sensor logs' names and loader (plan roar-008 Phase A)."""

from __future__ import annotations

import shutil

import numpy as np
import pytest
from conftest import DATA
from racekit.sysid_data import LOGS, load_log, log_path, sysid_dir
from racekit.telemetry import read_log_csv

SYSID = DATA / "generated" / "sysid"


def test_the_logs_are_the_two_generated_ones():
    assert LOGS == ("monza-like-seed0.csv", "oval-steady-seed0.csv")
    assert sysid_dir() == SYSID
    for name in LOGS:
        assert log_path(name) == SYSID / name


@pytest.mark.parametrize("name", LOGS)
def test_load_log_returns_what_read_log_csv_returns(name):
    if not (SYSID / name).is_file():
        pytest.fail(f"{SYSID / name} is missing; run "
                    "`PYTHONHASHSEED=0 uv run --group roar python roar/data/generate.py`")
    log, meta = load_log(name)
    expected_log, expected_meta = read_log_csv(SYSID / name)
    assert meta == expected_meta
    assert log.dtype == expected_log.dtype and np.array_equal(log, expected_log)


def test_an_unknown_name_raises():
    with pytest.raises(ValueError, match="unknown sensor log"):
        log_path("monza-like-seed1.csv")
    with pytest.raises(ValueError, match="unknown sensor log"):
        load_log("../tracks/oval.npz")


def test_the_directory_can_be_overridden(tmp_path, monkeypatch):
    name = LOGS[1]
    shutil.copy(SYSID / name, tmp_path / name)
    monkeypatch.setenv("RACEKIT_SYSID_DIR", str(tmp_path))
    assert log_path(name) == tmp_path / name
    assert load_log(name)[1] == read_log_csv(SYSID / name)[1]
    with pytest.raises(FileNotFoundError, match="generate.py"):
        load_log(LOGS[0])
