import ast
from pathlib import Path

import nbformat
import pytest
import yaml

from tools import cli
from tools.concept_scan import concept_scan_findings, detect
from tools.curriculum import (
    checkpoint_findings,
    concepts_schema_findings,
    coverage_findings,
    dependency_baseline,
    global_concept_uniqueness_findings,
    lesson_budget_findings,
    practice_findings,
    prereq_findings,
)

REPO = Path(__file__).resolve().parents[1]


def _write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _entry(entry_id, *, kind="unit", introduces=None, requires=None, practices=None):
    return {
        "id": entry_id,
        "kind": kind,
        "title": "Synthetic fixture",
        "lessons": 1,
        "introduces": introduces or [],
        "requires": requires or [],
        "practices": practices or [],
    }


def _concept(concept_id, *, kind=None, category="techniques"):
    value = {"id": concept_id, "name": concept_id, "category": category}
    if kind is not None:
        value["kind"] = kind
    return value


def _write_book(root, book, concepts, entries, *, syllabus=True):
    _write_yaml(
        root / book / "curriculum/concepts.yaml",
        {"concepts_version": 1, "concepts": concepts},
    )
    _write_yaml(
        root / book / "curriculum/coverage-map.yaml",
        {"map_version": 1, "entries": entries},
    )
    if syllabus:
        rows = "\n".join(
            f"| `{entry['id']}` | {entry['kind']} | {entry['lessons']:g} |"
            for entry in entries
        )
        (root / book / "syllabus.md").write_text(rows + "\n", encoding="utf-8")


@pytest.fixture
def cross_book_root(tmp_path):
    _write_yaml(
        tmp_path / "books.yaml",
        {
            "books_version": 1,
            "books": [
                {"id": "base", "number": 1, "root": "base", "depends_on": []},
                {
                    "id": "dependent",
                    "number": 2,
                    "root": "dependent",
                    "depends_on": ["base"],
                    "concept_minimum": 1,
                    "lesson_budget": [1, 10],
                },
            ],
        },
    )
    _write_book(
        tmp_path,
        "base",
        [_concept("base-feature", category="data")],
        [_entry("unit-01-base", introduces=["base-feature"])],
    )
    _write_book(
        tmp_path,
        "dependent",
        [_concept("new-technique", kind="technique")],
        [
            _entry(
                "unit-01-dependent",
                introduces=["new-technique"],
                requires=["base-feature"],
            ),
            _entry(
                "project-03-fixture",
                kind="project",
                requires=["base-feature", "new-technique"],
            ),
        ],
    )
    return tmp_path


def test_dependency_baseline_is_directional_and_transitive(cross_book_root):
    assert dependency_baseline(cross_book_root, "base") == set()
    assert dependency_baseline(cross_book_root, "dependent") == {"base-feature"}
    assert prereq_findings(cross_book_root, "dependent") == []
    assert coverage_findings(cross_book_root, "dependent") == []

    books_path = cross_book_root / "books.yaml"
    books = yaml.safe_load(books_path.read_text(encoding="utf-8"))
    books["books"].append(
        {"id": "leaf", "number": 3, "root": "leaf", "depends_on": ["dependent"]}
    )
    _write_yaml(books_path, books)
    assert dependency_baseline(cross_book_root, "leaf") == {
        "base-feature",
        "new-technique",
    }


def test_dependency_does_not_allow_a_nowhere_taught_concept(cross_book_root):
    path = cross_book_root / "dependent/curriculum/coverage-map.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["entries"][0]["requires"].append("nowhere-taught")
    _write_yaml(path, data)

    assert prereq_findings(cross_book_root, "dependent") == [
        (
            "FAIL: dependent: unit-01-dependent uses concepts not yet introduced: "
            "['nowhere-taught']"
        )
    ]
    assert any("requires references unknown concepts" in finding for finding in coverage_findings(
        cross_book_root, "dependent"
    ))


def test_dependency_concept_may_not_be_reintroduced(cross_book_root):
    path = cross_book_root / "dependent/curriculum/coverage-map.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["entries"][0]["introduces"].append("base-feature")
    _write_yaml(path, data)

    assert any("introduces references unknown concepts" in finding for finding in coverage_findings(
        cross_book_root, "dependent"
    ))


def test_checkpoint_seen_set_starts_with_dependency_baseline(cross_book_root):
    path = cross_book_root / "dependent/curriculum/coverage-map.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["entries"].insert(
        0,
        _entry(
            "checkpoint-01-fixture",
            kind="checkpoint",
            requires=["base-feature"],
            practices=["base-feature"],
        ),
    )
    _write_yaml(path, data)

    assert checkpoint_findings(cross_book_root, "dependent") == []


def test_lesson_budget_is_per_book(cross_book_root):
    assert lesson_budget_findings(cross_book_root, "dependent") == []
    books_path = cross_book_root / "books.yaml"
    books = yaml.safe_load(books_path.read_text(encoding="utf-8"))
    books["books"][1]["lesson_budget"] = [5, 10]
    _write_yaml(books_path, books)
    assert lesson_budget_findings(cross_book_root, "dependent") == [
        "FAIL: dependent: lesson budget 2 outside 5-10"
    ]


def test_kind_is_optional_and_accepts_feature_or_technique(cross_book_root):
    assert concepts_schema_findings(cross_book_root, "dependent") == []
    path = cross_book_root / "dependent/curriculum/concepts.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["concepts"][0]["kind"] = "pattern"
    _write_yaml(path, data)
    assert concepts_schema_findings(cross_book_root, "dependent") == [
        "FAIL: dependent: bad concept kind in new-technique: pattern"
    ]


def test_concept_count_floor_is_per_book(cross_book_root):
    books_path = cross_book_root / "books.yaml"
    books = yaml.safe_load(books_path.read_text(encoding="utf-8"))
    books["books"][1]["concept_minimum"] = 2
    _write_yaml(books_path, books)
    assert concepts_schema_findings(cross_book_root, "dependent") == [
        "FAIL: dependent: concept registry has fewer than 2 concepts"
    ]


def test_global_concept_id_collision_is_caught(cross_book_root):
    path = cross_book_root / "dependent/curriculum/concepts.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["concepts"].append(_concept("base-feature", kind="feature", category="data"))
    _write_yaml(path, data)

    assert global_concept_uniqueness_findings(cross_book_root) == [
        (
            "FAIL: books: concept id 'base-feature' is defined in multiple books: "
            "['base', 'dependent']"
        )
    ]
    assert global_concept_uniqueness_findings(cross_book_root)[0] in coverage_findings(
        cross_book_root, "dependent"
    )


def test_practice_completeness_is_deferred_for_contentless_skeleton(cross_book_root):
    assert practice_findings(cross_book_root, "dependent") == []


def test_practice_completeness_reactivates_when_content_exists(cross_book_root):
    (cross_book_root / "dependent/units/unit-01-dependent").mkdir(parents=True)
    assert practice_findings(cross_book_root, "dependent") == [
        "FAIL: dependent: only the capstone practices: ['new-technique']"
    ]


def test_dependency_practices_do_not_expand_own_completeness_set(cross_book_root):
    path = cross_book_root / "dependent/curriculum/coverage-map.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["entries"][0]["practices"] = ["base-feature"]
    data["entries"][1]["practices"] = ["new-technique"]
    _write_yaml(path, data)
    (cross_book_root / "dependent/units/unit-01-dependent").mkdir(parents=True)

    assert practice_findings(cross_book_root, "dependent") == [
        "FAIL: dependent: only the capstone practices: ['new-technique']"
    ]


FEATURE_CASES = [
    ("set-literal", "values = {1, 2}"),
    ("set-ops", "left = {1}\nright = {2}\nboth = left | right\nleft.add(3)"),
    ("tuple", "point = (1, 2)"),
    ("comprehension", "values = [n for n in range(3)]"),
    ("str-split", "parts = text.split()"),
    ("sorted-key", "ordered = sorted(values, key=len)"),
    ("deque", "from collections import deque\nqueue = deque()\nqueue.popleft()"),
    ("recursion", "def visit(n):\n    if n:\n        return visit(n - 1)"),
    ("bitwise-ops", "mask = (value << 1) | ~value"),
]

SET_OP_CASES = [
    "left & right",
    "left | right",
    "left - right",
    "left ^ right",
    "left.add(3)",
    "left.discard(3)",
    "left.remove(3)",
]


@pytest.mark.parametrize(("concept_id", "source"), FEATURE_CASES)
def test_new_feature_detector_is_registry_gated(concept_id, source):
    gated_on, _ = detect(ast.parse(source), registered_concepts={concept_id})
    gated_off, _ = detect(ast.parse(source), registered_concepts=set())

    assert concept_id in gated_on
    assert concept_id not in gated_off


@pytest.mark.parametrize("operation", SET_OP_CASES)
def test_each_set_operation_is_detected(operation):
    source = f"left = {{1}}\nright = {{2}}\nresult = {operation}"
    used, _ = detect(ast.parse(source), registered_concepts={"set-ops"})
    assert "set-ops" in used


def test_technique_kind_is_never_scanner_flagged(cross_book_root):
    entry = cross_book_root / "dependent/units/unit-01-dependent"
    entry.mkdir(parents=True)
    nbformat.write(
        nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("value = 1 + 2")]),
        entry / "lesson.ipynb",
    )
    path = cross_book_root / "dependent/curriculum/concepts.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["concepts"][0] = _concept("arithmetic", kind="technique", category="data")
    _write_yaml(path, data)

    assert concept_scan_findings(cross_book_root, "dependent") == []


def test_base_feature_used_by_dependent_lesson_is_allowed(cross_book_root):
    entry = cross_book_root / "dependent/units/unit-01-dependent"
    entry.mkdir(parents=True)
    nbformat.write(
        nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("value = 1 + 2")]),
        entry / "lesson.ipynb",
    )
    base_concepts = cross_book_root / "base/curriculum/concepts.yaml"
    data = yaml.safe_load(base_concepts.read_text(encoding="utf-8"))
    data["concepts"][0]["id"] = "arithmetic"
    _write_yaml(base_concepts, data)
    base_map = cross_book_root / "base/curriculum/coverage-map.yaml"
    data = yaml.safe_load(base_map.read_text(encoding="utf-8"))
    data["entries"][0]["introduces"] = ["arithmetic"]
    _write_yaml(base_map, data)

    assert concept_scan_findings(cross_book_root, "dependent") == []


def test_dependent_checks_do_not_change_book1_output_in_process(cross_book_root, capsys):
    def book1_outputs():
        outputs = []
        for check in ("prereq-check", "coverage-check", "concept-scan"):
            code = cli.main(["--root", str(REPO), "--book", "book1", check])
            captured = capsys.readouterr()
            outputs.append((code, captured.out, captured.err))
        return outputs

    before = book1_outputs()

    assert prereq_findings(cross_book_root, "dependent") == []
    assert coverage_findings(cross_book_root, "dependent") == []
    assert concept_scan_findings(cross_book_root, "dependent") == []

    assert book1_outputs() == before


def test_scanner_profile_does_not_mutate_module_globals():
    """Locks per-book profile immutability: building a profile that activates every
    extension path (str-split -> split; set-ops -> add/discard/remove; deque ->
    appendleft/popleft; a technique -> never_flag) must NOT mutate the module-global
    TAUGHT_METHODS / MANUAL_ONLY sets. Reverting the `set(...)` copies to in-place
    aliases/updates makes this test fail (the vacuity gap sol flagged at the content gate)."""
    import tools.concept_scan as cs

    taught_before = set(cs.TAUGHT_METHODS)
    manual_before = set(cs.MANUAL_ONLY)

    concepts = [
        {"id": "str-split", "name": "Split", "category": "io", "kind": "feature"},
        {"id": "set-ops", "name": "Set ops", "category": "data-structures", "kind": "feature"},
        {"id": "deque", "name": "Deque", "category": "data-structures", "kind": "feature"},
        {"id": "greedy", "name": "Greedy", "category": "techniques", "kind": "technique"},
    ]
    profile = cs.scanner_profile(concepts)

    # Sensitivity: the extension paths actually ran (non-vacuous).
    assert "split" in profile.taught_methods
    assert {"add", "discard", "remove"} <= profile.taught_methods
    assert {"appendleft", "popleft"} <= profile.taught_methods
    assert "greedy" in profile.never_flag

    # Immutability lock: the module globals are unchanged by profile construction.
    assert cs.TAUGHT_METHODS == taught_before
    assert cs.MANUAL_ONLY == manual_before
