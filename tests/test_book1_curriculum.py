from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
CURRICULUM = REPO / "book1" / "curriculum"

CATEGORIES = {
    "io", "data", "strings", "control", "loops", "functions",
    "collections", "files", "oop", "graphics", "modules",
}


def load_concepts():
    data = yaml.safe_load((CURRICULUM / "concepts.yaml").read_text(encoding="utf-8"))
    assert data["concepts_version"] == 1
    return data["concepts"]


def test_concepts_schema_and_unique_ids():
    concepts = load_concepts()
    assert len(concepts) >= 40
    ids = [c["id"] for c in concepts]
    assert len(ids) == len(set(ids)), "duplicate concept ids"
    import re

    for c in concepts:
        assert set(c) == {"id", "name", "category"}, f"bad keys in {c}"
        assert c["category"] in CATEGORIES, f"unknown category: {c}"
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", c["id"]), f"non-kebab id: {c['id']!r}"


def load_map():
    data = yaml.safe_load((CURRICULUM / "coverage-map.yaml").read_text(encoding="utf-8"))
    assert data["map_version"] == 1
    return data["entries"]


def test_map_schema_and_id_contract():
    import re

    entries = load_map()
    kinds = {"unit": r"^unit-[0-9]{2}-[a-z0-9-]+$",
             "project": r"^project-[0-9]{2}-[a-z0-9-]+$",
             "checkpoint": r"^checkpoint-[0-9]{2}-[a-z0-9-]+$"}
    ids = [e["id"] for e in entries]
    assert len(ids) == len(set(ids)), "duplicate entry ids"
    for e in entries:
        assert set(e) == {"id", "kind", "title", "lessons", "introduces", "requires", "practices"}
        assert e["kind"] in kinds and re.match(kinds[e["kind"]], e["id"]), f"bad id: {e['id']}"
        assert isinstance(e["lessons"], (int, float)) and e["lessons"] > 0


def test_lesson_budget_close_to_thirty():
    total = sum(e["lessons"] for e in load_map())
    assert 28 <= total <= 32, f"lesson budget {total} outside 28-32"


def test_all_referenced_concepts_exist():
    known = {c["id"] for c in load_concepts()}
    for e in load_map():
        for field in ("introduces", "requires", "practices"):
            unknown = set(e[field]) - known
            assert not unknown, f"{e['id']}.{field} references unknown concepts: {unknown}"


def test_every_concept_introduced_exactly_once():
    known = {c["id"] for c in load_concepts()}
    introduced = [c for e in load_map() for c in e["introduces"]]
    assert len(introduced) == len(set(introduced)), "concept introduced twice"
    assert set(introduced) == known, f"never introduced: {known - set(introduced)}"


def test_prereq_closure_planning_level():
    # Both requires AND practices may only use concepts introduced by EARLIER entries —
    # design §2's "nothing may be used before it is taught", enforced for every entry kind.
    seen: set[str] = set()
    for e in load_map():
        missing = (set(e["requires"]) | set(e["practices"])) - seen
        assert not missing, f"{e['id']} uses concepts not yet introduced: {missing}"
        seen |= set(e["introduces"])


def test_practice_coverage_planning_level():
    # Practicing means an entry OTHER than the introduction: practices-only union must
    # cover the whole registry, and no entry may "practice" what it itself introduces.
    for e in load_map():
        overlap = set(e["practices"]) & set(e["introduces"])
        assert not overlap, f"{e['id']} practices its own introductions: {overlap}"
        for field in ("introduces", "requires", "practices"):
            assert len(e[field]) == len(set(e[field])), f"{e['id']}.{field} has duplicates"
    # Coverage must hold WITHOUT the capstone: an omnibus final project must not be the
    # only place a concept is ever practiced (anti-tautology rule, gate finding sol #2).
    known = {c["id"] for c in load_concepts()}
    pre_capstone = {
        c for e in load_map() if e["id"] != "project-02-grand-adventure" for c in e["practices"]
    }
    assert pre_capstone == known, f"only the capstone practices: {known - pre_capstone}"


def test_checkpoints_only_assess_taught_concepts():
    seen: set[str] = set()
    for e in load_map():
        if e["kind"] == "checkpoint":
            assert not e["introduces"], f"{e['id']} introduces concepts"
            untaught = set(e["practices"]) - seen
            assert not untaught, f"{e['id']} assesses untaught concepts: {untaught}"
        seen |= set(e["introduces"])
