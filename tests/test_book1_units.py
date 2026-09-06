import os
from pathlib import Path

import pytest

from tools.notebooks import (
    exec_solutions_findings,
    exercise_structure_findings,
    hygiene_findings,
    layout_findings,
    manifest_findings,
    noexec_findings,
    prefix_findings,
    solutions_structure_findings,
    teacher_notes_findings,
)

REPO = Path(__file__).resolve().parents[1]
UNITS_ROOT = REPO / "book1" / "units"
UNIT_DIRS = sorted(path for path in UNITS_ROOT.glob("unit-*") if path.is_dir())

if not UNIT_DIRS:
    pytest.skip("no unit directories yet (pre-content)", allow_module_level=True)


@pytest.fixture(params=UNIT_DIRS, ids=lambda path: path.name)
def unit_dir(request):
    return request.param


def test_layout(unit_dir):
    assert layout_findings(REPO, "book1", unit_dir.name) == []


def test_manifest_schema_and_map_agreement(unit_dir):
    assert manifest_findings(REPO, "book1", unit_dir.name) == []


def test_student_hygiene(unit_dir):
    assert hygiene_findings(REPO, "book1", unit_dir.name) == []


def test_exercise_structure(unit_dir):
    assert exercise_structure_findings(REPO, "book1", unit_dir.name) == []


def test_solutions_structure_and_execution(unit_dir):
    assert solutions_structure_findings(REPO, "book1", unit_dir.name) == []
    if os.environ.get("PY4KIDS_CI") != "1":
        assert exec_solutions_findings(REPO, "book1", unit_dir.name) == []


def test_lesson_conventions(unit_dir):
    assert noexec_findings(REPO, "book1", unit_dir.name) == []


def test_teacher_notes_structure(unit_dir):
    assert teacher_notes_findings(REPO, "book1", unit_dir.name) == []


def test_all_three_units_present():
    assert prefix_findings(REPO, "book1") == []
