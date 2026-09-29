from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tools.curriculum import (
    coverage_findings,
    global_concept_uniqueness_findings,
    practice_findings,
    prereq_findings,
)


def _write_yaml(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _entry(
    entry_id: str,
    *,
    kind: str = "unit",
    introduces: list[str] | None = None,
    requires: list[str] | None = None,
    practices: list[str] | None = None,
    auxiliary: list[str] | None = None,
) -> dict[str, object]:
    return {
        "id": entry_id,
        "kind": kind,
        "title": "Synthetic borrowed-tools fixture",
        "lessons": 1,
        "introduces": introduces or [],
        "requires": requires or [],
        "practices": practices or [],
        "auxiliary": auxiliary or [],
    }


def _concept(concept_id: str) -> dict[str, str]:
    return {"id": concept_id, "name": concept_id, "category": "data"}


def _write_book(
    root: Path,
    book: str,
    concepts: list[str],
    entries: list[dict[str, object]],
    *,
    map_version: int,
) -> None:
    _write_yaml(
        root / book / "curriculum/concepts.yaml",
        {"concepts_version": 1, "concepts": [_concept(value) for value in concepts]},
    )
    _write_yaml(
        root / book / "curriculum/coverage-map.yaml",
        {"map_version": map_version, "entries": entries},
    )
    rows = "\n".join(
        f"| `{entry['id']}` | {entry['kind']} | {entry['lessons']} |" for entry in entries
    )
    (root / book / "syllabus.md").write_text(rows + "\n", encoding="utf-8")


@pytest.fixture
def auxiliary_root(tmp_path: Path) -> Path:
    _write_yaml(
        tmp_path / "books.yaml",
        {
            "books_version": 2,
            "books": [
                {
                    "id": "python-projects",
                    "number": 1,
                    "root": "python-projects",
                    "patterns": True,
                    "depends_on": [],
                    "concept_minimum": 2,
                    "lesson_budget": [1, 10],
                },
                {
                    "id": "bridge",
                    "number": 2,
                    "root": "bridge",
                    "depends_on": ["python-projects"],
                },
                {
                    "id": "usaco-bronze",
                    "number": 3,
                    "root": "usaco-bronze",
                    "judge": True,
                    "depends_on": ["bridge"],
                },
            ],
        },
    )
    _write_book(
        tmp_path,
        "python-projects",
        ["foundation", "future-tool"],
        [
            _entry(
                "unit-01-fixture",
                introduces=["foundation"],
                auxiliary=["python-projects:future-tool"],
            ),
            _entry(
                "unit-02-fixture",
                introduces=["future-tool"],
                practices=["foundation"],
            ),
        ],
        map_version=2,
    )
    _write_book(
        tmp_path,
        "usaco-bronze",
        ["year-two-tool"],
        [
            {
                key: value
                for key, value in _entry("unit-01-year-two", introduces=["year-two-tool"]).items()
                if key != "auxiliary"
            }
        ],
        map_version=1,
    )
    return tmp_path


def _map(root: Path) -> tuple[Path, dict]:
    path = root / "python-projects/curriculum/coverage-map.yaml"
    return path, yaml.safe_load(path.read_text(encoding="utf-8"))


def _books(root: Path) -> tuple[Path, dict]:
    path = root / "books.yaml"
    return path, yaml.safe_load(path.read_text(encoding="utf-8"))


def _write_synthetic_k2_row(root: Path) -> None:
    _write_yaml(
        root / "python-projects/curriculum/k2-exceptions.yaml",
        {
            "k2_exceptions_version": 1,
            "exceptions": [
                {
                    "cell-id": "counter",
                    "concept-ids": [
                        "python-projects:loop-counter",
                        "python-projects:accumulator",
                    ],
                    "exact-ast-form": "name = name + 1",
                    "role": "composed",
                }
            ],
        },
    )


def _install_actual_k2_curriculum(root: Path, entries: list[dict[str, object]]) -> None:
    """Install the two concepts named by the closed K2 row, not stand-ins."""
    _write_book(
        root,
        "python-projects",
        ["foundation", "loop-counter", "accumulator"],
        entries,
        map_version=2,
    )
    _write_synthetic_k2_row(root)


def test_python_projects_auxiliary_home_must_be_strictly_later(auxiliary_root: Path) -> None:
    assert prereq_findings(auxiliary_root, "python-projects") == []

    path, data = _map(auxiliary_root)
    data["entries"][0]["auxiliary"] = []
    data["entries"][1]["auxiliary"] = ["python-projects:foundation"]
    data["entries"][1]["practices"] = []
    _write_yaml(path, data)

    findings = prereq_findings(auxiliary_root, "python-projects")
    assert len(findings) == 1
    assert "python-projects:foundation" in findings[0]
    assert "later home introduction" in findings[0]


def test_python_projects_auxiliary_home_uses_map_order_not_registry_order(
    auxiliary_root: Path,
) -> None:
    concepts_path = auxiliary_root / "python-projects/curriculum/concepts.yaml"
    concepts = yaml.safe_load(concepts_path.read_text(encoding="utf-8"))
    concepts["concepts"].reverse()
    _write_yaml(concepts_path, concepts)

    registry_order = [concept["id"] for concept in concepts["concepts"]]
    _path, coverage = _map(auxiliary_root)
    map_order = [concept_id for entry in coverage["entries"] for concept_id in entry["introduces"]]
    assert registry_order == ["future-tool", "foundation"]
    assert map_order == ["foundation", "future-tool"]
    assert prereq_findings(auxiliary_root, "python-projects") == []


def test_python_projects_auxiliary_without_home_fails_closed(auxiliary_root: Path) -> None:
    path, data = _map(auxiliary_root)
    data["entries"][1]["introduces"] = []
    _write_yaml(path, data)

    findings = prereq_findings(auxiliary_root, "python-projects")
    assert len(findings) == 1
    assert "python-projects:future-tool" in findings[0]
    assert "no home introduction" in findings[0]


def test_python_projects_auxiliary_in_its_home_entry_is_rejected(auxiliary_root: Path) -> None:
    path, data = _map(auxiliary_root)
    data["entries"][0]["introduces"].append("future-tool")
    data["entries"][1]["introduces"] = []
    _write_yaml(path, data)

    findings = prereq_findings(auxiliary_root, "python-projects")
    assert len(findings) == 1
    assert "auxiliary overlaps introduces/requires/practices" in findings[0]


def test_k2_auxiliary_never_advances_seen(auxiliary_root: Path) -> None:
    _install_actual_k2_curriculum(
        auxiliary_root,
        [
            _entry(
                "unit-01-fixture",
                introduces=["foundation"],
                auxiliary=["python-projects:loop-counter", "python-projects:accumulator"],
            ),
            _entry(
                "unit-02-requires-fixture",
                requires=["loop-counter", "accumulator"],
            ),
            _entry(
                "unit-03-k2-home",
                introduces=["loop-counter", "accumulator"],
            ),
        ],
    )

    assert prereq_findings(auxiliary_root, "python-projects") == [
        (
            "FAIL: python-projects: unit-02-requires-fixture uses concepts not yet introduced: "
            "['accumulator', 'loop-counter']"
        )
    ]


def test_transitive_usaco_bronze_dependent_auxiliary_is_allowed(auxiliary_root: Path) -> None:
    path, data = _map(auxiliary_root)
    data["entries"][0]["auxiliary"] = ["usaco-bronze:year-two-tool"]
    _write_yaml(path, data)

    assert prereq_findings(auxiliary_root, "python-projects") == []


@pytest.mark.parametrize("missing", ["registration", "concept"])
def test_usaco_bronze_auxiliary_requires_registered_owner(auxiliary_root: Path, missing: str) -> None:
    path, data = _map(auxiliary_root)
    data["entries"][0]["auxiliary"] = ["usaco-bronze:year-two-tool"]
    _write_yaml(path, data)

    if missing == "registration":
        books_path, books = _books(auxiliary_root)
        books["books"] = [entry for entry in books["books"] if entry["id"] != "usaco-bronze"]
        _write_yaml(books_path, books)
    else:
        concepts_path = auxiliary_root / "usaco-bronze/curriculum/concepts.yaml"
        concepts = yaml.safe_load(concepts_path.read_text(encoding="utf-8"))
        concepts["concepts"] = []
        _write_yaml(concepts_path, concepts)

    findings = prereq_findings(auxiliary_root, "python-projects")
    assert len(findings) == 1
    if missing == "registration":
        # The owner alternation is built from books.yaml (design 008), so an unregistered
        # owner is not even a qualified id.
        assert findings == [
            "FAIL: python-projects: unit-01-fixture.auxiliary must contain qualified ids"
        ]
        return
    assert "usaco-bronze:year-two-tool" in findings[0]
    assert "registered owner" in findings[0]


@pytest.mark.parametrize(
    "malformed_entry",
    [
        {"id": "year-two-tool"},
        {"id": "year-two-tool", "name": "Year two tool"},
        {
            "id": "year-two-tool",
            "name": "Year two tool",
            "category": "not-a-category",
        },
        "year-two-tool",
    ],
)
def test_usaco_bronze_auxiliary_rejects_malformed_owner_entry(
    auxiliary_root: Path, malformed_entry: object
) -> None:
    path, data = _map(auxiliary_root)
    data["entries"][0]["auxiliary"] = ["usaco-bronze:year-two-tool"]
    _write_yaml(path, data)
    concepts_path = auxiliary_root / "usaco-bronze/curriculum/concepts.yaml"
    concepts = yaml.safe_load(concepts_path.read_text(encoding="utf-8"))
    concepts["concepts"] = [malformed_entry]
    _write_yaml(concepts_path, concepts)

    findings = prereq_findings(auxiliary_root, "python-projects")
    assert len(findings) == 1
    assert "usaco-bronze:year-two-tool" in findings[0]
    assert "registered owner" in findings[0]


def test_usaco_bronze_auxiliary_rejects_wrong_shape_concepts_registry(
    auxiliary_root: Path,
) -> None:
    path, data = _map(auxiliary_root)
    data["entries"][0]["auxiliary"] = ["usaco-bronze:year-two-tool"]
    _write_yaml(path, data)
    concepts_path = auxiliary_root / "usaco-bronze/curriculum/concepts.yaml"
    concepts = yaml.safe_load(concepts_path.read_text(encoding="utf-8"))
    concepts["concepts"] = {"id": "year-two-tool"}
    _write_yaml(concepts_path, concepts)

    findings = prereq_findings(auxiliary_root, "python-projects")
    assert len(findings) == 1
    assert "usaco-bronze:year-two-tool" in findings[0]
    assert "registered owner" in findings[0]


def test_usaco_bronze_auxiliary_owner_must_depend_on_python_projects(auxiliary_root: Path) -> None:
    path, data = _map(auxiliary_root)
    data["entries"][0]["auxiliary"] = ["usaco-bronze:year-two-tool"]
    _write_yaml(path, data)
    books_path, books = _books(auxiliary_root)
    bridge = next(entry for entry in books["books"] if entry["id"] == "bridge")
    bridge["depends_on"] = []
    _write_yaml(books_path, books)

    findings = prereq_findings(auxiliary_root, "python-projects")
    assert len(findings) == 1
    assert "usaco-bronze:year-two-tool" in findings[0]
    assert "transitive dependent" in findings[0]


@pytest.mark.parametrize("kind", ["checkpoint", "project"])
def test_prereq_rejects_auxiliary_in_strict_entries(auxiliary_root: Path, kind: str) -> None:
    path, data = _map(auxiliary_root)
    data["entries"].insert(
        1,
        _entry(
            f"{kind}-01-fixture",
            kind=kind,
            auxiliary=["python-projects:future-tool"],
        ),
    )
    _write_yaml(path, data)

    findings = prereq_findings(auxiliary_root, "python-projects")
    assert len(findings) == 1
    assert f"{kind}-01-fixture.auxiliary must be empty" in findings[0]


def test_k2_auxiliary_earns_no_practice_or_coverage_credit(
    auxiliary_root: Path,
) -> None:
    _install_actual_k2_curriculum(
        auxiliary_root,
        [
            _entry(
                "unit-01-fixture",
                introduces=["foundation"],
                auxiliary=["python-projects:loop-counter", "python-projects:accumulator"],
            ),
            _entry(
                "unit-02-k2-home",
                introduces=["loop-counter", "accumulator"],
                practices=["foundation"],
            ),
            _entry(
                "project-02-fixture",
                kind="project",
                practices=["foundation", "loop-counter", "accumulator"],
            ),
        ],
    )
    (auxiliary_root / "python-projects/projects/project-02-fixture").mkdir(parents=True)

    expected = "FAIL: python-projects: only the capstone practices: ['accumulator', 'loop-counter']"
    assert practice_findings(auxiliary_root, "python-projects") == [expected]
    assert coverage_findings(auxiliary_root, "python-projects") == [expected]


def test_auxiliary_does_not_create_a_global_concept_owner(auxiliary_root: Path) -> None:
    baseline = global_concept_uniqueness_findings(auxiliary_root)
    path, data = _map(auxiliary_root)
    data["entries"][0]["auxiliary"] = ["usaco-bronze:year-two-tool"]
    _write_yaml(path, data)

    assert data["entries"][0]["auxiliary"] == ["usaco-bronze:year-two-tool"]
    assert baseline == []
    assert global_concept_uniqueness_findings(auxiliary_root) == baseline
