from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
FLAGS = ("publication", "judge", "patterns", "acsl")


def load_catalog():
    return yaml.safe_load((REPO / "books.yaml").read_text(encoding="utf-8"))


def test_registry_ids_order_and_dependencies():
    catalog = load_catalog()
    assert catalog["books_version"] == 2
    books = catalog["books"]
    assert [b["id"] for b in books] == ["python-projects", "python-concepts", "usaco-bronze", "acsl"]
    assert [b["number"] for b in books] == [1, 1, 2, 2]  # a series ordinal only; drives no tooling
    assert books[0]["depends_on"] == []  # python-projects
    assert books[1]["depends_on"] == []  # python-concepts: self-contained variant of python-projects
    assert books[2]["depends_on"] == ["python-projects"]  # usaco-bronze
    assert books[3]["depends_on"] == ["python-projects"]  # acsl: the Python books only
    # the two contest books are symmetric peers (design 008 D3 / 009 D5)
    assert books[2]["peers"] == ["acsl"]
    assert books[3]["peers"] == ["usaco-bronze"]
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
    assert books["acsl"]["title"] == "Contest Python: ACSL"
    assert books["acsl"]["subtitle"] == "From Elementary to Senior, one contest at a time"


def test_registry_feature_flags_are_booleans():
    books = {b["id"]: b for b in load_catalog()["books"]}
    for book in books.values():
        for flag in FLAGS:
            assert isinstance(book.get(flag, False), bool), f"{book['id']} {flag}"
    enabled = {flag: [i for i, b in books.items() if b.get(flag)] for flag in FLAGS}
    assert enabled == {
        "publication": ["python-concepts"],
        "judge": ["usaco-bronze", "acsl"],
        "patterns": ["python-projects"],
        "acsl": ["acsl"],
    }


def test_registry_documents_every_flag():
    text = (REPO / "books.yaml").read_text(encoding="utf-8")
    for flag in FLAGS:
        assert f"#   {flag}:" in text
    assert "coverage-map v2" in text  # `patterns` covers the markdown concept scan too
    assert "`peers`" in text


def test_ci_local_reads_every_flag():
    text = (REPO / "scripts/ci-local.sh").read_text(encoding="utf-8")
    assert 'for flag in ("publication", "judge", "patterns", "acsl")' in text
    assert 'has_flag acsl "$flags"' in text and "acsl-check" in text


def test_acsl_is_covered_by_the_id_guards():
    # pre-merge-guard and the plan-091 id guard read book roots from books.yaml, not a pinned list.
    from test_book_ids import _book_roots, live_files

    assert "acsl/" in _book_roots()
    assert any(path.startswith("acsl/") for path in live_files())
    guard = (REPO / "scripts/pre-merge-guard.sh").read_text(encoding="utf-8")
    assert 'registry["books"]' in guard and "book_roots" in guard


def test_acsl_season_map_records_source_and_contests():
    season = yaml.safe_load((REPO / "acsl/curriculum/season.yaml").read_text(encoding="utf-8"))
    assert season["source"].startswith("https://www.acsl.org/")
    assert season["retrieved"] == "2026-09-29"
    contests = {c["contest"]: c for c in season["contests"]}
    assert sorted(contests) == [0, 1, 2, 3, 4]
    assert contests[0]["unit_order"] == ["Foundations"] and "categories" not in contests[0]
    for number in (1, 2, 3, 4):
        assert set(contests[number]["categories"]) == set(season["divisions"])
        assert "Practice" not in contests[number]["unit_order"]
    assert contests[2]["unit_order"][-1] == "LISP"
    assert contests[3]["unit_order"][-1] == "FSAs and Regular Expressions"
    assert contests[4]["unit_order"][-1] == "Assembly Language"


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
    assert pattern.fullmatch("acsl:bit-string")  # registered by plan 092
    assert not pattern.fullmatch("usaco-silver:bfs")  # not registered here
    assert not pattern.fullmatch(":str-split")
    (tmp_path / "books.yaml").write_text(
        "books_version: 2\nbooks:\n- {id: usaco-silver, root: usaco-silver, depends_on: []}\n",
        encoding="utf-8",
    )
    assert qualified_concept_id_pattern(tmp_path).fullmatch("usaco-silver:bfs")
    assert not qualified_concept_id_pattern(tmp_path / "empty").fullmatch(":x")
