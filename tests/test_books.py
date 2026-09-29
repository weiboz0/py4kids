from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
FLAGS = ("publication", "judge", "patterns")


def load_catalog():
    return yaml.safe_load((REPO / "books.yaml").read_text(encoding="utf-8"))


def test_registry_ids_order_and_dependencies():
    catalog = load_catalog()
    assert catalog["books_version"] == 2
    books = catalog["books"]
    assert [b["id"] for b in books] == ["python-projects", "python-concepts", "usaco-bronze"]
    assert [b["number"] for b in books] == [1, 1, 2]  # a series ordinal only; drives no tooling
    assert books[0]["depends_on"] == []  # python-projects
    assert books[1]["depends_on"] == []  # python-concepts: self-contained variant of python-projects
    assert books[2]["depends_on"] == ["python-projects"]  # usaco-bronze
    # python-concepts is a finished fastforward variant (the buildout flag was removed, plan 078)
    assert books[1]["variant_of"] == "python-projects"
    assert books[1]["prereq_policy"] == "fastforward"
    assert books[1].get("buildout", False) is False


def test_registry_ids_are_roots_and_unique():
    books = load_catalog()["books"]
    ids = [b["id"] for b in books]
    assert len(ids) == len(set(ids))
    for book in books:
        assert book["root"] == book["id"]


def test_registry_titles_and_subtitles():
    books = {b["id"]: b for b in load_catalog()["books"]}
    for book in books.values():
        for key in ("title", "subtitle"):
            assert isinstance(book.get(key), str) and book[key].strip(), f"{book['id']} {key}"
    assert books["python-projects"]["title"] == "Python by Projects"
    assert books["python-projects"]["subtitle"] == "Learn Python by building things"
    assert books["python-concepts"]["title"] == "Python, Concept by Concept"
    assert books["python-concepts"]["subtitle"] == "Learn Python one idea at a time"
    assert books["usaco-bronze"]["title"] == "Contest Python: USACO Bronze"
    assert books["usaco-bronze"]["subtitle"] == "Algorithms for your first programming contests"


def test_registry_feature_flags_are_booleans():
    books = {b["id"]: b for b in load_catalog()["books"]}
    for book in books.values():
        for flag in FLAGS:
            assert isinstance(book.get(flag, False), bool), f"{book['id']} {flag}"
    enabled = {flag: [i for i, b in books.items() if b.get(flag)] for flag in FLAGS}
    assert enabled == {
        "publication": ["python-concepts"],
        "judge": ["usaco-bronze"],
        "patterns": ["python-projects"],
    }


def test_registry_documents_every_flag():
    text = (REPO / "books.yaml").read_text(encoding="utf-8")
    for flag in FLAGS:
        assert f"#   {flag}:" in text
    assert "coverage-map v2" in text  # `patterns` covers the markdown concept scan too


def test_book_roots_have_required_layout():
    for book in load_catalog()["books"]:
        root = REPO / book["root"]
        for sub in ("curriculum", "units", "projects", "checkpoints", "reference", "docs"):
            assert (root / sub).is_dir(), f"{book['id']} missing {sub}/"
        assert (root / "syllabus.md").is_file(), f"{book['id']} missing syllabus.md"


def test_qualified_concept_ids_use_registry_owners(tmp_path):
    from tools.books import qualified_concept_id_pattern

    pattern = qualified_concept_id_pattern(REPO)
    assert pattern.fullmatch("usaco-bronze:str-split")
    assert pattern.fullmatch("python-projects:list-literal")
    assert not pattern.fullmatch("acsl:bit-string")  # not registered here
    assert not pattern.fullmatch(":str-split")
    (tmp_path / "books.yaml").write_text(
        "books_version: 2\nbooks:\n- {id: acsl, root: acsl, depends_on: []}\n", encoding="utf-8"
    )
    assert qualified_concept_id_pattern(tmp_path).fullmatch("acsl:bit-string")
    assert not qualified_concept_id_pattern(tmp_path / "empty").fullmatch(":x")
