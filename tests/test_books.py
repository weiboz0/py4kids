from pathlib import Path

import pytest
import yaml

from tools.books import SiteConfigError, books_with_flag, site_config, site_config_errors

REPO = Path(__file__).resolve().parents[1]
FLAGS = ("publication", "judge", "patterns", "acsl", "site")


def load_catalog():
    return yaml.safe_load((REPO / "books.yaml").read_text(encoding="utf-8"))


def test_registry_ids_order_and_dependencies():
    catalog = load_catalog()
    assert catalog["books_version"] == 2
    books = catalog["books"]
    assert [b["id"] for b in books] == [
        "python-projects", "python-concepts", "usaco-bronze", "acsl", "recsys",
    ]
    assert [b["number"] for b in books] == [1, 1, 2, 2, 3]  # a series ordinal only; drives no tooling
    assert books[0]["depends_on"] == []  # python-projects
    assert books[1]["depends_on"] == []  # python-concepts: self-contained variant of python-projects
    assert books[2]["depends_on"] == ["python-projects"]  # usaco-bronze
    assert books[3]["depends_on"] == ["python-projects"]  # acsl: the Python books only
    assert books[4]["depends_on"] == ["python-projects"]  # recsys: the Python concept baseline
    # the two contest books are symmetric peers (design 008 D3 / 009 D5)
    assert books[2]["peers"] == ["acsl"]
    assert books[3]["peers"] == ["usaco-bronze"]
    # python-concepts is a finished fastforward variant (the buildout flag was removed, plan 078)
    assert books[1]["variant_of"] == "python-projects"
    assert books[1]["prereq_policy"] == "fastforward"
    assert books[1].get("buildout", False) is False
    # recsys left buildout at recsys-012 (Unit 10): whole-book lessons reached the 30-lesson minimum
    # (30.5 = Units 1-10 at 3 each + Checkpoint A 0.5), so the flag was removed (design 011).
    assert books[4].get("buildout", False) is False
    assert books[4]["lesson_budget"] == [30, 60]


def test_recsys_declares_its_dependency_group_as_a_string_not_a_flag():
    # `dependency_group` is a routing VALUE, not a boolean feature flag (design 011 §7): it names
    # the pyproject [dependency-groups] entry ci-local runs the book's heavy commands under. It must
    # be a string, and must NOT be one of FLAGS (else test_registry_feature_flags_are_booleans and
    # the step-1 flag tuple would break). Only recsys declares one today.
    books = {b["id"]: b for b in load_catalog()["books"]}
    assert "dependency_group" not in FLAGS
    assert books["recsys"]["dependency_group"] == "recsys"
    for book_id, book in books.items():
        value = book.get("dependency_group")
        assert value is None or isinstance(value, str), book_id
    declared = {i for i, b in books.items() if b.get("dependency_group")}
    assert declared == {"recsys"}
    text = (REPO / "books.yaml").read_text(encoding="utf-8")
    assert "`dependency_group`" in text  # documented in the registry comment block


def test_ci_local_reads_dependency_group_separately_from_the_flags():
    text = (REPO / "scripts/ci-local.sh").read_text(encoding="utf-8")
    # Read as a SEPARATE value line, leaving the boolean-flag tuple intact.
    assert 'book.get("dependency_group")' in text
    assert "uv run --group" in text


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
    assert books["recsys"]["title"] == "Applied Python: Recommendation Systems"
    assert books["recsys"]["subtitle"] == "Build a book recommender — from counting to neural retrieval"


def test_registry_feature_flags_are_booleans():
    books = {b["id"]: b for b in load_catalog()["books"]}
    for book in books.values():
        for flag in FLAGS:
            assert isinstance(book.get(flag, False), bool), f"{book['id']} {flag}"
    enabled = {flag: [i for i, b in books.items() if b.get(flag)] for flag in FLAGS}
    assert enabled == {
        "publication": ["python-projects", "python-concepts", "usaco-bronze", "acsl"],
        "judge": ["usaco-bronze", "acsl"],
        "patterns": ["python-projects"],
        "acsl": ["acsl"],
        "site": ["python-projects", "python-concepts", "usaco-bronze", "acsl"],
    }


def test_registry_documents_every_flag():
    text = (REPO / "books.yaml").read_text(encoding="utf-8")
    for flag in FLAGS:
        assert f"#   {flag}:" in text
    assert "coverage-map v2" in text  # `patterns` covers the markdown concept scan too
    assert "`peers`" in text


def test_ci_local_reads_every_flag():
    text = (REPO / "scripts/ci-local.sh").read_text(encoding="utf-8")
    assert 'for flag in ("publication", "judge", "patterns", "acsl", "site")' in text
    assert 'has_flag acsl "$flags"' in text and "acsl-check" in text


def test_acsl_is_covered_by_the_id_guards():
    # The importable pre-merge guard and the plan-091 id guard read roots from books.yaml.
    from test_book_ids import _book_roots, live_files

    assert "acsl/" in _book_roots()
    assert any(path.startswith("acsl/") for path in live_files())
    guard = (REPO / "tools/guard.py").read_text(encoding="utf-8")
    assert 'registry["books"]' in guard and "book_roots" in guard


def test_acsl_season_map_records_source_and_contests():
    season = yaml.safe_load((REPO / "acsl/curriculum/season.yaml").read_text(encoding="utf-8"))
    assert season["source"].startswith("https://www.acsl.org/")
    assert season["retrieved"] == "2026-09-29"
    contests = {c["contest"]: c for c in season["contests"]}
    assert sorted(contests) == [0, 1, 2, 3, 4]
    names = {n: [u["name"] for u in c["units"]] for n, c in contests.items()}
    assert names[0] == ["Foundations"] and "categories" not in contests[0]
    for number in (1, 2, 3, 4):
        assert set(contests[number]["categories"]) == set(season["divisions"])
        assert "Practice" not in names[number]
    assert names[2][-1] == "LISP"
    assert names[3][-1] == "FSAs and Regular Expressions"
    assert names[4][-1] == "Assembly Language"
    # the official acsl.org strings (design 009 D2)
    assert [contests[n]["categories"]["elementary"] for n in (1, 2, 3, 4)] == [
        ["Elementary Computer Number Systems"], ["Elementary Prefix/Infix/Postfix Notation"],
        ["Elementary Boolean Algebra"], ["Elementary Graph Theory"],
    ]
    assert contests[1]["categories"]["classroom"] == [
        "Computer Number Systems", "Recursive Functions", "What Does This Program Do?"
    ]
    assert contests[2]["categories"]["classroom"] == [
        "Prefix/Infix/Postfix Notation", "Bit-String Flicking", "LISP"
    ]
    for number, topic in ((2, "Looping"), (3, "Arrays"), (4, "Strings")):
        assert contests[number]["categories"]["junior"][-1] == (
            f"What Does This Program Do? - {topic}"
        )


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


# --- the `site` flag and per-book site.yaml (design 012 D1, plan 101 A) ----------------------


def make_registry(tmp_path: Path, books: list[dict]) -> Path:
    """Write a minimal `books.yaml` (books_version 2) and one folder per book under tmp_path."""
    entries = [{"root": book["id"], "depends_on": [], **book} for book in books]
    (tmp_path / "books.yaml").write_text(
        yaml.safe_dump({"books_version": 2, "books": entries}, sort_keys=False), encoding="utf-8"
    )
    for book in books:
        (tmp_path / book["id"]).mkdir(exist_ok=True)
    return tmp_path


def test_site_flag_books():
    assert books_with_flag(REPO, "site") == [
        "python-projects", "python-concepts", "usaco-bronze", "acsl",
    ]


def test_site_config_real_books():
    for book in books_with_flag(REPO, "site"):
        assert site_config_errors(REPO, book) == []
        config = site_config(REPO, book)
        assert config.classification == "proposed"
        assert config.fixture_budget_kb == 130


def test_site_config_validation(tmp_path):
    root = make_registry(tmp_path, books=[{"id": "b", "site": True}])
    path = tmp_path / "b" / "site.yaml"
    path.write_text("classification: maybe\nfixture_budget_kb: 130\n")
    assert site_config_errors(root, "b") == [
        "FAIL: b/site.yaml: classification must be one of: proposed, confirmed"
    ]
    path.write_text("classification: proposed\nfixture_budget_kb: 130\nextra: 1\n")
    assert site_config_errors(root, "b") == ["FAIL: b/site.yaml: unknown key: extra"]
    path.write_text("classification: confirmed\nfixture_budget_kb: 0\n")
    assert site_config_errors(root, "b") == [
        "FAIL: b/site.yaml: fixture_budget_kb must be a positive integer"
    ]
    path.write_text("classification: proposed\n")
    assert site_config_errors(root, "b") == ["FAIL: b/site.yaml: missing key: fixture_budget_kb"]
    path.write_text("[1, 2]\n")
    assert site_config_errors(root, "b") == ["FAIL: b/site.yaml: must be a mapping"]
    path.write_text("classification: confirmed\nfixture_budget_kb: 64\n")
    assert site_config_errors(root, "b") == []
    config = site_config(root, "b")
    assert (config.classification, config.fixture_budget_kb) == ("confirmed", 64)
    with pytest.raises(AttributeError):
        config.classification = "proposed"  # frozen


def test_site_config_invalid_raises(tmp_path):
    root = make_registry(tmp_path, books=[{"id": "b", "site": True}])
    (tmp_path / "b" / "site.yaml").write_text("classification: maybe\nfixture_budget_kb: 130\n")
    with pytest.raises(SiteConfigError, match="classification must be one of"):
        site_config(root, "b")


def test_site_book_needs_site_yaml(tmp_path):
    root = make_registry(tmp_path, books=[{"id": "b", "site": True}])
    with pytest.raises(SiteConfigError, match="site: true but b/site.yaml is missing"):
        site_config(root, "b")
    assert site_config_errors(root, "b") == [
        "FAIL: b: site: true but b/site.yaml is missing (design 012 D1)"
    ]
