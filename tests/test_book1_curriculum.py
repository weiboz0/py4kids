from pathlib import Path

from tools.curriculum import (
    checkpoint_findings,
    concepts_schema_findings,
    introduction_findings,
    lesson_budget_findings,
    map_schema_findings,
    practice_findings,
    prereq_findings,
    referenced_concepts_findings,
    syllabus_findings,
)

REPO = Path(__file__).resolve().parents[1]


def test_concepts_schema_and_unique_ids():
    assert concepts_schema_findings(REPO, "book1") == []


def test_map_schema_and_id_contract():
    assert map_schema_findings(REPO, "book1") == []


def test_lesson_budget_close_to_thirty():
    assert lesson_budget_findings(REPO, "book1") == []


def test_all_referenced_concepts_exist():
    assert referenced_concepts_findings(REPO, "book1") == []


def test_every_concept_introduced_exactly_once():
    assert introduction_findings(REPO, "book1") == []


def test_prereq_closure_planning_level():
    assert prereq_findings(REPO, "book1") == []


def test_practice_coverage_planning_level():
    assert practice_findings(REPO, "book1") == []


def test_checkpoints_only_assess_taught_concepts():
    assert checkpoint_findings(REPO, "book1") == []


def test_syllabus_table_matches_map():
    assert syllabus_findings(REPO, "book1") == []
