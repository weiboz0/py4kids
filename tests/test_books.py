from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]


def load_catalog():
    return yaml.safe_load((REPO / "books.yaml").read_text(encoding="utf-8"))


def test_registry_ids_order_and_dependencies():
    books = load_catalog()["books"]
    assert [b["id"] for b in books] == ["book1", "book2"]
    assert [b["number"] for b in books] == [1, 2]
    assert [b["root"] for b in books] == ["book1", "book2"]
    assert books[0]["depends_on"] == []
    assert books[1]["depends_on"] == ["book1"]


def test_book_roots_have_required_layout():
    for book in load_catalog()["books"]:
        root = REPO / book["root"]
        for sub in ("curriculum", "units", "projects", "checkpoints", "reference", "docs"):
            assert (root / sub).is_dir(), f"{book['id']} missing {sub}/"
        assert (root / "syllabus.md").is_file(), f"{book['id']} missing syllabus.md"
