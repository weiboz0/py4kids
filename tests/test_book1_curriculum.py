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
