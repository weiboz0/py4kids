"""Plan 092 Phase D: the `peers` exemption, the `acsl` book's season structure (`acsl-check`),
the `acsl` manifest key, and short-answer items (design 009 D4)."""

from __future__ import annotations

import shutil
from pathlib import Path

import nbformat
import pytest
import yaml
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

from tools.acsl import acsl_findings
from tools.concept_scan import concept_scan_findings
from tools.curriculum import (
    coverage_findings,
    global_concept_uniqueness_findings,
    prereq_findings,
    referenced_concepts_findings,
)
from tools.judge import judge_findings, outputs_match, verify_literals
from tools.notebooks import exec_solutions_findings, manifest_findings, structure_findings
from tools.source_policy import source_policy_findings

REPO = Path(__file__).resolve().parents[1]
SEASON = REPO / "acsl/curriculum/season.yaml"


def _write_yaml(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _nb(path: Path, *cells) -> None:
    notebook = new_notebook()
    notebook.cells = list(cells)
    nbformat.write(notebook, path)


def _heading(text: str, *cell_tags: str):
    cell = new_markdown_cell(text)
    cell.metadata["tags"] = list(cell_tags)
    return cell


def _code(source: str, *cell_tags: str):
    cell = new_code_cell(source)
    cell.metadata["tags"] = list(cell_tags)
    return cell


# ---------------------------------------------------------------- D1 peers


def _concept(concept_id, name=None, category="io", kind=None):
    value = {"id": concept_id, "name": name or concept_id, "category": category}
    if kind is not None:
        value["kind"] = kind
    return value


def _entry(entry_id, introduces=(), requires=(), practices=()):
    return {
        "id": entry_id,
        "kind": "unit",
        "title": "Fixture",
        "lessons": 1,
        "introduces": list(introduces),
        "requires": list(requires),
        "practices": list(practices),
    }


def _peer_root(tmp_path, *, left_peers=("right",), right_peers=("left",), left=None, right=None):
    books = [
        {"id": "base", "number": 1, "root": "base", "depends_on": []},
        {"id": "left", "number": 2, "root": "left", "depends_on": ["base"], "peers": list(left_peers)},
        {"id": "right", "number": 2, "root": "right", "depends_on": ["base"],
         "peers": list(right_peers)},
    ]
    _write_yaml(tmp_path / "books.yaml", {"books_version": 2, "books": books})
    catalogs = {
        "base": [_concept("print")],
        "left": left or [_concept("shared", "Shared", kind="technique"), _concept("left-only")],
        "right": right or [_concept("shared", "Shared", kind="technique"), _concept("right-only")],
    }
    for book, concepts in catalogs.items():
        _write_yaml(tmp_path / book / "curriculum/concepts.yaml",
                    {"concepts_version": 1, "concepts": concepts})
        entries = [_entry("unit-01-x", introduces=[c["id"] for c in concepts])]
        if book != "base":
            entries[0]["requires"] = ["print"]
        _write_yaml(tmp_path / book / "curriculum/coverage-map.yaml",
                    {"map_version": 1, "entries": entries})
        (tmp_path / book / "syllabus.md").write_text("| `unit-01-x` | unit | 1 |\n", encoding="utf-8")
    return tmp_path


def test_peers_may_share_identical_concept_entries(tmp_path):
    root = _peer_root(tmp_path)
    assert global_concept_uniqueness_findings(root) == []
    assert coverage_findings(root, "left") == []
    assert coverage_findings(root, "right") == []
    assert prereq_findings(root, "left") == []


def test_peer_entries_compare_as_dicts_not_text(tmp_path):
    root = _peer_root(tmp_path)
    path = root / "right/curriculum/concepts.yaml"
    path.write_text(
        "concepts_version: 1\nconcepts:\n"
        "- {kind: technique, category: io, name: 'Shared', id: \"shared\"}\n"
        "- {id: right-only, name: right-only, category: io}\n",
        encoding="utf-8",
    )
    assert global_concept_uniqueness_findings(root) == []


@pytest.mark.parametrize(
    "drifted",
    [
        _concept("shared", "Shared ids", kind="technique"),  # name
        _concept("shared", "Shared", category="search", kind="technique"),  # category
        _concept("shared", "Shared", kind="feature"),  # kind
        _concept("shared", "Shared"),  # kind absent on one side
    ],
)
def test_peer_registry_drift_fails(tmp_path, drifted):
    root = _peer_root(tmp_path, right=[drifted, _concept("right-only")])
    findings = global_concept_uniqueness_findings(root)
    assert any("'shared' drifts between peers ['left', 'right']" in f for f in findings), findings
    assert findings[0] in coverage_findings(root, "left")


def test_asymmetric_peer_is_reported_and_grants_nothing(tmp_path):
    root = _peer_root(tmp_path, right_peers=())
    findings = global_concept_uniqueness_findings(root)
    assert any("'left' peer 'right' is asymmetric" in f for f in findings), findings
    assert any("'shared' is defined in multiple books" in f for f in findings), findings


def test_unknown_or_self_peer_is_reported(tmp_path):
    root = _peer_root(tmp_path, left_peers=("right", "ghost", "left"))
    findings = global_concept_uniqueness_findings(root)
    assert any("'left' peer 'ghost' is unknown" in f for f in findings), findings
    assert any("'left' lists itself as a peer" in f for f in findings), findings


def test_non_peers_still_may_not_share_ids(tmp_path):
    root = _peer_root(tmp_path, left_peers=(), right_peers=())
    findings = global_concept_uniqueness_findings(root)
    assert findings == [
        "FAIL: books: concept id 'shared' is defined in multiple books: ['left', 'right']"
    ]


def test_requiring_a_peer_only_id_fails(tmp_path):
    root = _peer_root(tmp_path)
    data = yaml.safe_load((root / "left/curriculum/coverage-map.yaml").read_text(encoding="utf-8"))
    data["entries"][0]["requires"].append("right-only")
    _write_yaml(root / "left/curriculum/coverage-map.yaml", data)
    findings = referenced_concepts_findings(root, "left")
    assert findings == [
        "FAIL: left: unit-01-x.requires references unknown concepts: ['right-only']"
    ]
    assert findings[0] in coverage_findings(root, "left")


def test_real_registry_peers_and_contest_books_close_separately():
    assert global_concept_uniqueness_findings(REPO) == []
    for book in ("acsl", "usaco-bronze"):
        assert prereq_findings(REPO, book) == [], book
        assert coverage_findings(REPO, book) == [], book
    acsl = yaml.safe_load((REPO / "acsl/curriculum/concepts.yaml").read_text(encoding="utf-8"))
    usaco = yaml.safe_load(
        (REPO / "usaco-bronze/curriculum/concepts.yaml").read_text(encoding="utf-8")
    )
    usaco_by_id = {c["id"]: c for c in usaco["concepts"]}
    shared = {c["id"] for c in acsl["concepts"]}
    assert {"input-parse", "str-split", "tuple", "complete-search"} <= shared  # grows as contests ship
    for concept in acsl["concepts"]:
        assert concept == usaco_by_id[concept["id"]]


# ---------------------------------------------------------------- acsl book fixture


def _acsl_root(tmp_path, *, flag=True):
    books = [
        {"id": "python-projects", "number": 1, "root": "python-projects", "depends_on": []},
        {"id": "usaco-bronze", "number": 2, "root": "usaco-bronze",
         "depends_on": ["python-projects"], "judge": True},
        {"id": "acsl", "number": 2, "root": "acsl", "depends_on": ["python-projects"],
         "judge": True, "acsl": flag},
    ]
    _write_yaml(tmp_path / "books.yaml", {"books_version": 2, "books": books})
    for book in ("usaco-bronze", "acsl"):
        for sub in ("units", "checkpoints", "projects"):
            (tmp_path / book / sub).mkdir(parents=True, exist_ok=True)
    (tmp_path / "acsl/curriculum").mkdir(parents=True, exist_ok=True)
    shutil.copy(SEASON, tmp_path / "acsl/curriculum/season.yaml")
    _write_yaml(tmp_path / "acsl/curriculum/concepts.yaml",
                {"concepts_version": 1, "concepts": [_concept("tuple", "Tuples",
                                                              "data-structures", "feature")]})
    _set_map(tmp_path, [])
    return tmp_path


def _set_map(root, ids, book="acsl"):
    entries = []
    for entry_id in ids:
        kind = "checkpoint" if entry_id.startswith("checkpoint-") else "unit"
        entry = _entry(entry_id)
        entry["kind"] = kind
        entries.append(entry)
    _write_yaml(root / book / "curriculum/coverage-map.yaml", {"map_version": 1, "entries": entries})


def _manifest(entry_dir, kind, acsl_block, lessons=1):
    manifest = {
        "id": entry_dir.name,
        "kind": kind,
        "blueprint_version": 1,
        "lessons": lessons,
        "concepts": {"introduces": [], "requires": [], "practices": []},
        "provenance": "original",
    }
    if acsl_block is not None:
        manifest["acsl"] = acsl_block
    _write_yaml(entry_dir / "manifest.yaml", manifest)


def _acsl_unit(root, name, contest, category, divisions=("junior",), item_tags=(("acsl-junior",),),
               book="acsl"):
    entry_dir = root / book / "units" / name
    entry_dir.mkdir(parents=True)
    _manifest(entry_dir, "unit",
              {"contest": contest, "category": category, "divisions": list(divisions)})
    cells = [_heading(f"## Exercise {n}\n\nDo it.", *t) for n, t in enumerate(item_tags, 1)]
    _nb(entry_dir / "exercises.ipynb", *cells)
    return entry_dir


def _acsl_checkpoint(root, name, contest, category="Practice", divisions=("junior",),
                     item_tags=(("acsl-junior",),)):
    entry_dir = root / "acsl" / "checkpoints" / name
    entry_dir.mkdir(parents=True)
    _manifest(entry_dir, "checkpoint",
              {"contest": contest, "category": category, "divisions": list(divisions)})
    cells = [_heading(f"## Question {n}\n\nAnswer it.", *t) for n, t in enumerate(item_tags, 1)]
    _nb(entry_dir / "checkpoint.ipynb", *cells)
    return entry_dir


def _shipped_contest_one(root):
    _acsl_unit(root, "unit-00-foundations", 0, "Foundations")
    _acsl_unit(root, "unit-01-number-systems", 1, "Computer Number Systems",
               divisions=("elementary", "junior"),
               item_tags=(("acsl-elementary",), ("acsl-junior", "stretch")))
    _acsl_checkpoint(root, "checkpoint-01-contest-1-practice", 1)
    _set_map(root, ["unit-00-foundations", "unit-01-number-systems",
                    "checkpoint-01-contest-1-practice"])


# ---------------------------------------------------------------- D3 manifest-check + acsl-check


def test_acsl_check_is_a_noop_for_other_books():
    for book in ("python-projects", "python-concepts", "usaco-bronze"):
        assert acsl_findings(REPO, book) == [], book


def test_acsl_check_passes_a_valid_season(tmp_path):
    root = _acsl_root(tmp_path)
    _shipped_contest_one(root)
    assert acsl_findings(root, "acsl") == []


def test_foundations_alone_needs_no_practice(tmp_path):
    root = _acsl_root(tmp_path)
    _acsl_unit(root, "unit-00-foundations", 0, "Foundations")
    _set_map(root, ["unit-00-foundations"])
    assert acsl_findings(root, "acsl") == []


def test_manifest_accepts_acsl_block_only_on_acsl_books(tmp_path):
    root = _acsl_root(tmp_path)
    _acsl_unit(root, "unit-00-foundations", 0, "Foundations")
    _set_map(root, ["unit-00-foundations"])
    assert manifest_findings(root, "acsl") == []
    # the same block on a non-acsl book is rejected
    _acsl_unit(root, "unit-01-reading", 0, "Foundations", book="usaco-bronze")
    _set_map(root, ["unit-01-reading"], book="usaco-bronze")
    assert manifest_findings(root, "usaco-bronze") == [
        "FAIL: unit-01-reading: manifest key 'acsl' is only allowed in books with the 'acsl' flag"
    ]


def test_manifest_still_rejects_other_unknown_keys_on_acsl_books(tmp_path):
    root = _acsl_root(tmp_path)
    unit = _acsl_unit(root, "unit-00-foundations", 0, "Foundations")
    _set_map(root, ["unit-00-foundations"])
    data = yaml.safe_load((unit / "manifest.yaml").read_text(encoding="utf-8"))
    data["level"] = "junior"
    _write_yaml(unit / "manifest.yaml", data)
    assert any("manifest keys" in f for f in manifest_findings(root, "acsl"))


def _mutate(root, entry, **changes):
    path = root / "acsl" / entry / "manifest.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["acsl"].update(changes)
    _write_yaml(path, data)


@pytest.mark.parametrize(
    "entry, changes, expected",
    [
        ("units/unit-01-number-systems", {"category": "Graph Theory"},
         "acsl category 'Graph Theory' is not a unit of contest 1"),
        ("units/unit-01-number-systems", {"category": "Number Theory"},
         "acsl category 'Number Theory' is not a unit of contest 1"),
        ("units/unit-01-number-systems", {"contest": 7}, "acsl contest 7 is not in season.yaml"),
        ("units/unit-01-number-systems", {"category": "Practice"},
         "'Practice' is reserved for practice checkpoints"),
        ("checkpoints/checkpoint-01-contest-1-practice", {"category": "Recursive Functions"},
         "a checkpoint's acsl category must be 'Practice'"),
        ("checkpoints/checkpoint-01-contest-1-practice", {"contest": 0},
         "Practice checkpoints belong to contests 1-4"),
        ("units/unit-01-number-systems", {"divisions": ["junior", "classroom"]},
         "classroom is never a division"),
        ("units/unit-01-number-systems", {"divisions": ["expert"]},
         "acsl division 'expert' is not a ladder level"),
        ("units/unit-01-number-systems", {"divisions": []},
         "acsl divisions must be a non-empty list"),
    ],
)
def test_acsl_block_mutations_fail(tmp_path, entry, changes, expected):
    root = _acsl_root(tmp_path)
    _shipped_contest_one(root)
    _mutate(root, entry, **changes)
    findings = acsl_findings(root, "acsl")
    assert any(expected in f for f in findings), findings


def test_missing_acsl_block_fails(tmp_path):
    root = _acsl_root(tmp_path)
    _shipped_contest_one(root)
    path = root / "acsl/units/unit-01-number-systems/manifest.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    del data["acsl"]
    _write_yaml(path, data)
    assert any("unit manifest needs an acsl: block" in f for f in acsl_findings(root, "acsl"))


@pytest.mark.parametrize(
    "item_tags, expected",
    [
        ((("acsl-elementary",),), "Exercise 1: acsl-elementary is below the unit's lowest division"),
        (((),), "Exercise 1: needs exactly one division tag (found [])"),
        ((("stretch",),), "Exercise 1: needs exactly one division tag (found [])"),
        ((("acsl-junior", "acsl-senior"),), "needs exactly one division tag"),
        ((("acsl-classroom",),), "Exercise 1: acsl-classroom is not a division tag"),
        ((("acsl-expert",),), "unknown division tag(s) ['acsl-expert']"),
    ],
)
def test_division_tag_mutations_fail(tmp_path, item_tags, expected):
    root = _acsl_root(tmp_path)
    _acsl_unit(root, "unit-00-foundations", 0, "Foundations", item_tags=item_tags)
    _set_map(root, ["unit-00-foundations"])
    findings = acsl_findings(root, "acsl")
    assert any(expected in f for f in findings), findings


def test_question_tag_bounded_by_the_checkpoint_divisions(tmp_path):
    root = _acsl_root(tmp_path)
    _shipped_contest_one(root)
    shutil.rmtree(root / "acsl/checkpoints/checkpoint-01-contest-1-practice")
    _acsl_checkpoint(root, "checkpoint-01-contest-1-practice", 1,
                     divisions=("intermediate", "senior"), item_tags=(("acsl-junior",),))
    findings = acsl_findings(root, "acsl")
    assert any("Question 1: acsl-junior is below the checkpoint's lowest division" in f
               for f in findings), findings


def _practice_with(root, item_tags):
    shutil.rmtree(root / "acsl/checkpoints/checkpoint-01-contest-1-practice")
    _acsl_checkpoint(root, "checkpoint-01-contest-1-practice", 1, item_tags=item_tags)
    return [f for f in acsl_findings(root, "acsl") if "programming question" in f]


SA = ("acsl-junior", "short-answer")
PROG = ("acsl-junior",)


def test_practice_checkpoint_closing_with_one_programming_question_passes(tmp_path):
    root = _acsl_root(tmp_path)
    _shipped_contest_one(root)
    _practice_with(root, (SA, SA, SA, PROG))
    assert acsl_findings(root, "acsl") == []


@pytest.mark.parametrize(
    "item_tags, expected",
    [
        ((SA, SA), ("a practice checkpoint needs exactly one programming question "
                    "(a Question heading not tagged short-answer); found none")),
        ((SA, PROG, PROG), ("a practice checkpoint needs exactly one programming question; "
                            "found 2: ['Question 2', 'Question 3']")),
        ((SA, PROG, SA), ("the programming question (Question 2) must be the last question "
                          "(last is Question 3)")),
    ],
    ids=["zero-programming", "two-programming", "programming-not-last"],
)
def test_practice_checkpoint_programming_question_mutations_fail(tmp_path, item_tags, expected):
    root = _acsl_root(tmp_path)
    _shipped_contest_one(root)
    findings = _practice_with(root, item_tags)
    assert findings == [f"FAIL: checkpoint-01-contest-1-practice: {expected}"], findings


def test_out_of_season_order_fails(tmp_path):
    root = _acsl_root(tmp_path)
    _acsl_unit(root, "unit-00-foundations", 0, "Foundations")
    _acsl_unit(root, "unit-01-recursive-functions", 1, "Recursive Functions")
    _acsl_unit(root, "unit-02-number-systems", 1, "Computer Number Systems")
    _acsl_checkpoint(root, "checkpoint-01-contest-1-practice", 1)
    _set_map(root, ["unit-00-foundations", "unit-01-recursive-functions",
                    "unit-02-number-systems", "checkpoint-01-contest-1-practice"])
    findings = acsl_findings(root, "acsl")
    assert any(f.startswith("FAIL: unit-02-number-systems: out of season order") for f in findings)


def test_contest_before_foundations_fails(tmp_path):
    root = _acsl_root(tmp_path)
    _shipped_contest_one(root)
    _set_map(root, ["unit-01-number-systems", "unit-00-foundations",
                    "checkpoint-01-contest-1-practice"])
    assert any("unit-00-foundations: out of season order" in f for f in acsl_findings(root, "acsl"))


def test_shipped_contest_unit_without_practice_fails(tmp_path):
    root = _acsl_root(tmp_path)
    _shipped_contest_one(root)
    shutil.rmtree(root / "acsl/checkpoints/checkpoint-01-contest-1-practice")
    assert "FAIL: acsl: contest 1 has shipped units but no practice checkpoint" in acsl_findings(
        root, "acsl"
    )


def test_practice_before_its_last_unit_fails(tmp_path):
    root = _acsl_root(tmp_path)
    _shipped_contest_one(root)
    _set_map(root, ["unit-00-foundations", "checkpoint-01-contest-1-practice",
                    "unit-01-number-systems"])
    assert any("unit-01-number-systems: out of season order" in f
               for f in acsl_findings(root, "acsl"))


def test_practice_without_units_and_duplicate_practice_fail(tmp_path):
    root = _acsl_root(tmp_path)
    _shipped_contest_one(root)
    _acsl_checkpoint(root, "checkpoint-02-contest-2-practice", 2)
    _acsl_checkpoint(root, "checkpoint-03-contest-1-again", 1)
    _set_map(root, ["unit-00-foundations", "unit-01-number-systems",
                    "checkpoint-01-contest-1-practice", "checkpoint-02-contest-2-practice",
                    "checkpoint-03-contest-1-again"])
    findings = acsl_findings(root, "acsl")
    assert any("contest 2 practice checkpoint has no shipped unit" in f for f in findings)
    assert any("contest 1 has more than one practice checkpoint" in f for f in findings)


def test_season_file_is_required_and_practice_reserved(tmp_path):
    root = _acsl_root(tmp_path)
    season = yaml.safe_load(SEASON.read_text(encoding="utf-8"))
    season["contests"][1]["units"].append({"name": "Practice", "divisions": ["junior"]})
    _write_yaml(root / "acsl/curriculum/season.yaml", season)
    assert any("units use the reserved 'Practice'" in f for f in acsl_findings(root, "acsl"))
    (root / "acsl/curriculum/season.yaml").unlink()
    assert acsl_findings(root, "acsl") == ["FAIL: acsl: curriculum/season.yaml does not exist"]


@pytest.mark.parametrize(
    "contest, category, divisions, bad",
    [
        (2, "LISP", ("junior",), ["junior"]),
        (4, "Assembly Language", ("junior", "intermediate"), ["junior"]),
        (1, "Recursive Functions", ("elementary", "junior"), ["elementary"]),
        (3, "WDTPD – Arrays", ("junior", "senior"), ["senior"]),
    ],
)
def test_unit_divisions_must_take_the_category(tmp_path, contest, category, divisions, bad):
    root = _acsl_root(tmp_path)
    _acsl_unit(root, "unit-00-foundations", 0, "Foundations")
    _acsl_unit(root, "unit-01-x", contest, category, divisions=divisions)
    _set_map(root, ["unit-00-foundations", "unit-01-x"])
    findings = acsl_findings(root, "acsl")
    assert any(f"unit-01-x: acsl divisions {bad} do not take contest {contest} {category!r}" in f
               for f in findings), findings


def test_unit_divisions_within_the_category_pass(tmp_path):
    root = _acsl_root(tmp_path)
    _acsl_unit(root, "unit-00-foundations", 0, "Foundations")
    _acsl_unit(root, "unit-01-lisp", 2, "LISP", divisions=("intermediate", "senior"),
               item_tags=(("acsl-intermediate",),))
    _set_map(root, ["unit-00-foundations", "unit-01-lisp"])
    findings = acsl_findings(root, "acsl")
    assert not any("do not take" in f for f in findings), findings


@pytest.mark.parametrize(
    "mutate, expected",
    [
        (lambda c: c.__setitem__("units", []), "contest 1 units must be a non-empty list"),
        (lambda c: c.__setitem__("units", ["Recursive Functions"]),
         "contest 1 units must be a non-empty list"),
        (lambda c: c["units"][0].__setitem__("divisions", ["classroom"]),
         "contest 1 unit 'Computer Number Systems' divisions must be ladder levels"),
        (lambda c: c["units"].append(dict(c["units"][0])), "contest 1 units repeat a name"),
    ],
)
def test_season_units_schema_mutations_fail(tmp_path, mutate, expected):
    root = _acsl_root(tmp_path)
    season = yaml.safe_load(SEASON.read_text(encoding="utf-8"))
    mutate(season["contests"][1])
    _write_yaml(root / "acsl/curriculum/season.yaml", season)
    findings = acsl_findings(root, "acsl")
    assert any(expected in f for f in findings), findings


# ---------------------------------------------------------------- D4 short-answer items

SOLVER = "a, b = input().split()\nprint(int(a) + int(b))\n"
VERIFY = 'value = int("3F", 16)\nassert str(value) == "63"\n'


def _sa_unit(root, *, answer_md="**Answer:** `63`", verify=VERIFY, verify_tags=("verify",),
             solver=True, short_tag_on_ex2=True, lessons=0):
    """Exercise 1 is programming (ex1.py), Exercise 2 is short-answer."""
    entry_dir = root / "acsl" / "units" / "unit-00-foundations"
    entry_dir.mkdir(parents=True)
    _manifest(entry_dir, "unit", {"contest": 0, "category": "Foundations", "divisions": ["junior"]},
              lessons=lessons)
    ex2_tags = ["acsl-junior"] + (["short-answer"] if short_tag_on_ex2 else [])
    _nb(entry_dir / "exercises.ipynb",
        _heading("## Exercise 1 — add\n\nRead two numbers.", "acsl-junior"),
        _heading("## Exercise 2 — convert\n\nWhat is 3F in base 10?", *ex2_tags))
    solution_cells = [
        _heading("## Exercise 1 — add"),
        _code(SOLVER, "no-exec"),
        _heading(f"## Exercise 2 — convert\n\n3 x 16 + 15 = 63.\n\n{answer_md}"),
    ]
    if verify is not None:
        solution_cells.append(_code(verify, *verify_tags))
    _nb(entry_dir / "solutions.ipynb", *solution_cells)
    if solver:
        assets = entry_dir / "assets"
        (assets / "ex1").mkdir(parents=True)
        (assets / "ex1.py").write_text(SOLVER, encoding="utf-8")
        for k, (inp, out) in enumerate((("1 2\n", "3\n"), ("10 20\n", "30\n")), 1):
            (assets / "ex1" / f"{k}.in").write_text(inp, encoding="utf-8")
            (assets / "ex1" / f"{k}.out").write_text(out, encoding="utf-8")
    _set_map(root, ["unit-00-foundations"])
    return entry_dir


def test_short_answer_item_needs_no_solver(tmp_path):
    root = _acsl_root(tmp_path)
    _sa_unit(root)
    assert judge_findings(root, "acsl") == []


def test_omitted_programming_solver_fails(tmp_path):
    root = _acsl_root(tmp_path)
    _sa_unit(root, solver=False)
    # an acsl entry is stdin-model even without assets/
    assert judge_findings(root, "acsl") == ["FAIL: unit-00-foundations: missing solver ex1.py"]


def test_acsl_short_answer_only_checkpoint_cannot_escape_solver_rule(tmp_path):
    root = _acsl_root(tmp_path)
    _acsl_checkpoint(root, "checkpoint-01-contest-1-practice", 1)  # no assets/, untagged Q1
    assert judge_findings(root, "acsl") == [
        "FAIL: checkpoint-01-contest-1-practice: missing solver q1.py"
    ]


def test_short_answer_tag_on_a_solver_item_is_reported(tmp_path):
    root = _acsl_root(tmp_path)
    entry = _sa_unit(root)
    notebook = nbformat.read(entry / "exercises.ipynb", as_version=4)
    notebook.cells[0].metadata["tags"].append("short-answer")
    nbformat.write(notebook, entry / "exercises.ipynb")
    findings = judge_findings(root, "acsl")
    assert any("ex1 is tagged short-answer but has solver ex1.py" in f for f in findings), findings


def test_untagged_short_answer_item_needs_a_solver(tmp_path):
    root = _acsl_root(tmp_path)
    _sa_unit(root, short_tag_on_ex2=False)
    assert "FAIL: unit-00-foundations: missing solver ex2.py" in judge_findings(root, "acsl")


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({"verify": None}, "Exercise 2: short-answer solution has no executed 'verify' cell"),
        ({"verify_tags": ("verify", "no-exec")}, "has no executed 'verify' cell"),
        ({"verify_tags": ()}, "has no executed 'verify' cell"),
        ({"verify": 'assert str("63") == "63"\n'}, "no non-vacuous verify assert"),
        ({"verify": 'assert "63" == "63"\n'}, "no non-vacuous verify assert"),
        ({"verify": "value = 63\nassert value == 63\n"}, "no non-vacuous verify assert"),
        ({"answer_md": "**Answer:** `64`"}, "no non-vacuous verify assert str(...) == '64'"),
        ({"answer_md": "The answer is 63."}, "needs exactly one '**Answer:** `<text>`' line"),
        ({"answer_md": "**Answer:** 63"}, "found 0 well-formed of 1"),
        ({"answer_md": "**Answer:** `63`\n\n**Answer:** `63`"}, "found 2 well-formed of 2"),
    ],
)
def test_short_answer_static_mutations_fail(tmp_path, kwargs, expected):
    root = _acsl_root(tmp_path)
    _sa_unit(root, **kwargs)
    findings = judge_findings(root, "acsl")
    assert any(expected in f for f in findings), findings


def test_short_answer_rule_applies_to_checkpoint_questions(tmp_path):
    root = _acsl_root(tmp_path)
    entry = _acsl_checkpoint(root, "checkpoint-01-contest-1-practice", 1,
                             item_tags=(("acsl-junior", "short-answer"),))
    _nb(entry / "solutions.ipynb", _heading("## Question 1\n\n**Answer:** `7`"),
        _code("total = 3 + 4\nassert str(total) == \"8\"\n", "verify"))
    findings = judge_findings(root, "acsl")
    assert findings == [(
        "FAIL: checkpoint-01-contest-1-practice: Question 1: no non-vacuous verify assert "
        "str(...) == '7' matching the **Answer:** line (verify literals: ['8'])"
    )]


def test_verify_literals_parses_only_the_contract_form():
    assert verify_literals('x = 1\nassert str(x + 62) == "63"\n') == ["63"]
    assert verify_literals('assert "63" == str(x)\n') == []
    assert verify_literals('assert str(x) != "63"\n') == []
    assert verify_literals('assert str(x, "utf-8") == "63"\n') == []
    assert verify_literals("assert str(x) == 63\n") == []
    assert verify_literals("not python (") == []


@pytest.mark.parametrize(
    "verify",
    [
        'if False:\n    assert str(int("3F", 16)) == "63"\n',
        'try:\n    assert str(int("3E", 16)) == "63"\nexcept AssertionError:\n    pass\n',
        'def check():\n    assert str(int("3F", 16)) == "63"\n',
        'for _ in range(0):\n    assert str(int("3F", 16)) == "63"\n',
        'with open(__file__) as f:\n    assert str(int("3F", 16)) == "63"\n',
        'check = lambda: str(int("3F", 16)) == "63"\n',
    ],
)
def test_nested_verify_assert_does_not_count(tmp_path, verify):
    assert verify_literals(verify) == []
    root = _acsl_root(tmp_path)
    _sa_unit(root, verify=verify)
    findings = judge_findings(root, "acsl")
    assert any("no non-vacuous verify assert str(...) == '63'" in f for f in findings), findings


def test_top_level_verify_assert_after_setup_counts():
    source = 'def f(x):\n    return int(x, 16)\n\nassert str(f("3F")) == "63"\n'
    assert verify_literals(source) == ["63"]


def test_exec_solutions_runs_verify_cells_and_skips_display_cells(tmp_path):
    root = _acsl_root(tmp_path)
    _sa_unit(root)
    assert exec_solutions_findings(root, "acsl") == []


def test_changing_only_the_computation_fails_at_execution(tmp_path):
    root = _acsl_root(tmp_path)
    _sa_unit(root, verify='value = int("3E", 16)\nassert str(value) == "63"\n')
    assert judge_findings(root, "acsl") == []  # the literal still matches the markdown answer
    findings = exec_solutions_findings(root, "acsl")
    assert findings and "solutions.ipynb execution failed" in findings[0], findings


def test_a_wrong_answer_fails(tmp_path):
    # answer and literal agree with each other, but the computation disagrees
    root = _acsl_root(tmp_path)
    _sa_unit(root, answer_md="**Answer:** `64`", verify='assert str(int("3F", 16)) == "64"\n')
    assert judge_findings(root, "acsl") == []
    assert any("execution failed" in f for f in exec_solutions_findings(root, "acsl"))


def test_exec_solutions_skips_display_only_notebooks(tmp_path):
    # usaco-bronze's solutions are all no-exec display cells: nothing is left to run.
    root = _acsl_root(tmp_path)
    unit = root / "usaco-bronze/units/unit-01-x"
    unit.mkdir(parents=True)
    _nb(unit / "solutions.ipynb", _heading("## Exercise 1"),
        _code("while True:\n    data = input()\n", "no-exec"))
    assert exec_solutions_findings(root, "usaco-bronze") == []


def test_real_usaco_bronze_solutions_have_no_live_cells():
    # Pins why exec-solutions may stop skipping stdin-model entries: nothing in usaco-bronze runs.
    for path in sorted((REPO / "usaco-bronze").glob("*/*/solutions.ipynb")):
        notebook = nbformat.read(path, as_version=4)
        live = [c for c in notebook.cells
                if c.cell_type == "code" and "no-exec" not in c.metadata.get("tags", [])]
        assert live == [], path


def test_structure_check_skips_solve_asserts_for_acsl_entries(tmp_path):
    root = _acsl_root(tmp_path)
    _sa_unit(root)
    findings = structure_findings(root, "acsl", "unit-00-foundations")
    assert not any("non-vacuous assert" in f or "input()" in f for f in findings), findings


def test_source_policy_skips_verify_cells(tmp_path):
    root = _acsl_root(tmp_path)
    banned = 'import subprocess, sys\nparts = [c for c in "3F"]\nassert str(len(parts)) == "2"\n'
    entry = _sa_unit(root, verify=banned, answer_md="**Answer:** `2`")
    assert source_policy_findings(root, "acsl") == []
    notebook = nbformat.read(entry / "solutions.ipynb", as_version=4)
    notebook.cells[-1].metadata["tags"] = []
    nbformat.write(notebook, entry / "solutions.ipynb")
    assert any("comprehension" in f for f in source_policy_findings(root, "acsl"))


def test_concept_scan_skips_verify_cells(tmp_path):
    root = _acsl_root(tmp_path)
    verify = 'pair = (3, 15)\nassert str(pair[0] * 16 + pair[1]) == "63"\n'
    entry = _sa_unit(root, verify=verify, solver=False)
    notebook = nbformat.read(entry / "solutions.ipynb", as_version=4)
    notebook.cells = notebook.cells[2:]  # keep only the short-answer item
    nbformat.write(notebook, entry / "solutions.ipynb")
    assert concept_scan_findings(root, "acsl") == []
    notebook = nbformat.read(entry / "solutions.ipynb", as_version=4)
    notebook.cells[-1].metadata["tags"] = []
    nbformat.write(notebook, entry / "solutions.ipynb")
    assert "FAIL: unit-00-foundations: used-but-unlisted concept tuple" in concept_scan_findings(
        root, "acsl"
    )


# ---------------------------------------------------------------- D4 output comparison


def _layout_entry(root, book):
    """A solver printing one number per line where the fixtures require one single line."""
    entry_dir = root / book / "units" / "unit-01-layout"
    (entry_dir / "assets" / "ex1").mkdir(parents=True)
    solver = "for token in input().split():\n    print(token)\n"
    (entry_dir / "assets" / "ex1.py").write_text(solver, encoding="utf-8")
    for k, line in enumerate(("15 10 4", "1 2"), 1):
        (entry_dir / "assets" / "ex1" / f"{k}.in").write_text(line + "\n", encoding="utf-8")
        (entry_dir / "assets" / "ex1" / f"{k}.out").write_text(line + "\n", encoding="utf-8")
    _nb(entry_dir / "exercises.ipynb", _heading("## Exercise 1\n\nEcho.", "acsl-junior"))
    _nb(entry_dir / "solutions.ipynb", _heading("## Exercise 1"), _code(solver, "no-exec"))
    _manifest(entry_dir, "unit", {"contest": 0, "category": "Foundations",
                                  "divisions": ["junior"]}, lessons=0)
    _set_map(root, ["unit-01-layout"], book=book)


def test_wrong_line_layout_fails_in_acsl(tmp_path):
    root = _acsl_root(tmp_path)
    _layout_entry(root, "acsl")
    assert judge_findings(root, "acsl") == [
        "FAIL: unit-01-layout: ex1.py wrong output on 1.in",
        "FAIL: unit-01-layout: ex1.py wrong output on 2.in",
    ]


def test_wrong_line_layout_passes_token_judge(tmp_path):
    # usaco-bronze's documented contract compares whitespace-split tokens
    root = _acsl_root(tmp_path)
    _layout_entry(root, "usaco-bronze")
    assert judge_findings(root, "usaco-bronze") == []


@pytest.mark.parametrize(
    "actual, expected, match",
    [
        ("15 10 4\n", "15 10 4\n", True),
        ("15 10 4   \n\n\n", "15 10 4\n", True),
        ("15 10 4", "15 10 4\n", True),
        ("a\r\nb\r\n", "a\nb\n", True),
        ("15\n10\n4\n", "15 10 4\n", False),
        ("15  10 4\n", "15 10 4\n", False),
        (" 15 10 4\n", "15 10 4\n", False),
        ("\n15 10 4\n", "15 10 4\n", False),
        ("a\n\nb\n", "a\nb\n", False),
    ],
)
def test_line_exact_comparison(actual, expected, match):
    assert outputs_match(actual, expected, line_exact=True) is match
    assert outputs_match(actual, expected, line_exact=False) is (actual.split() == expected.split())


def test_code_tracing_registry_teaches_math_floor_and_sqrt():
    from tools.concept_scan import scanner_profile

    with_tracing = scanner_profile([{"id": "code-tracing", "kind": "technique"}])
    without = scanner_profile([{"id": "tuple", "kind": "feature"}])
    assert {"floor", "sqrt"} <= with_tracing.taught_methods
    assert not ({"floor", "sqrt"} & without.taught_methods)
