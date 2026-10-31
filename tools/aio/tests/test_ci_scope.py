"""Plan 030 Task 5: the edition-build change routing (tools/ci_scope.py, D6)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

from tools.aio.ci_scope import INFO_UNCHANGED, BookInfo, change_set, route_books

BOOKS = [
    BookInfo("aio-ml", "aio-ml", ("F1-a", "C3-b"), ("F1-a", "C3-b")),
    BookInfo("aio-dl", "aio-dl", ("B2-019-c",), ("B2-019-c",)),
]


def _route(changed, **kwargs):
    routes = route_books(BOOKS, changed, **kwargs)
    return {book: route.command(book) for book, route in routes.items()}


def test_unit_content_change_routes_to_a_scoped_check_of_exactly_that_unit() -> None:
    assert _route(["aio-ml/units/C3-b/lessons/01-x.ipynb", "aio-ml/units/C3-b/manifest.yaml"]) == {
        "aio-ml": "scoped aio-ml --units C3-b", "aio-dl": "none aio-dl"}


def test_mock_only_change_routes_to_mocktests_with_zero_units() -> None:
    assert _route(["aio-dl/mocktests/r2-001/theory/p01.md"]) == {
        "aio-ml": "none aio-ml", "aio-dl": "scoped aio-dl --mocktests r2-001"}


def test_global_publication_inputs_route_every_book_full() -> None:
    for path in ("tools/aio/publish.py", "tools/aio/publish_audit.py",
                 "tools/aio/publish_theme/theme.tex", "tools/aio/books.py",
                 "scripts/aio/build-book.sh", "books.yaml", "pyproject.toml", "uv.lock"):
        assert _route([path, "aio-ml/units/C3-b/x.ipynb"]) == {
            "aio-ml": "full aio-ml", "aio-dl": "full aio-dl"}, path


def test_front_and_back_matter_route_full() -> None:
    assert _route(["aio-dl/front-matter/preface.md"])["aio-dl"] == "full aio-dl"
    assert _route(["aio-ml/back-matter/glossary.md"])["aio-ml"] == "full aio-ml"


def test_unrelated_changes_are_unchanged_and_print_info() -> None:
    routes = _route(["docs/plans/030-book-editions.md", "tools/aio/checks/scope.py", "TODO.md",
                     "tools/publish.py", "tools/books.py", "scripts/build-book.sh"])
    assert routes == {"aio-ml": "none aio-ml", "aio-dl": "none aio-dl"}
    assert INFO_UNCHANGED.format(book="aio-dl") == "INFO build-book: aio-dl unchanged (change-routed)"


def test_all_books_and_missing_merge_base_render_everything() -> None:
    assert _route([], all_books=True) == {"aio-ml": "full aio-ml", "aio-dl": "full aio-dl"}
    assert _route(["TODO.md"], diff_available=False) == {
        "aio-ml": "full aio-ml", "aio-dl": "full aio-dl"}


def _config(chapters: list[dict[str, str]], **extra: object) -> str:
    return yaml.safe_dump({"publication_version": 1, "student_answers": {"set": "A"},
                           "chapters": chapters, "mocktests": [], "audit": {}, **extra})


def test_publication_yaml_that_only_adds_chapters_routes_to_the_added_units() -> None:
    old = _config([{"unit": "F1-a", "title": "A"}])
    new = _config([{"unit": "F1-a", "title": "A"}, {"unit": "C3-b", "title": "B"}])
    texts = {"old": old, "new": new}
    routes = _route(["aio-ml/publication.yaml"], old_text=lambda _: texts["old"],
                    new_text=lambda _: texts["new"])
    assert routes["aio-ml"] == "scoped aio-ml --units C3-b"
    retitled = _config([{"unit": "F1-a", "title": "A2"}, {"unit": "C3-b", "title": "B"}])
    routes = _route(["aio-ml/publication.yaml"], old_text=lambda _: old,
                    new_text=lambda _: retitled)
    assert routes["aio-ml"] == "full aio-ml"
    other_key = _config([{"unit": "F1-a", "title": "A"}, {"unit": "C3-b", "title": "B"}],
                        volumes={"editions": ["teacher"], "parts": []})
    assert _route(["aio-ml/publication.yaml"], old_text=lambda _: old,
                  new_text=lambda _: other_key)["aio-ml"] == "full aio-ml"


def _coverage(rows: list[dict[str, object]]) -> str:
    return yaml.safe_dump({"roadmap_version": 1, "knowledge_points": rows})


def test_coverage_map_changes_route_by_introduced_concepts() -> None:
    old = _coverage([
        {"id": "k1", "shipped_concepts": ["a"], "destination": "C3-b", "depends_on": []},
        {"id": "k2", "shipped_concepts": ["b"], "destination": "F1-a", "depends_on": []},
    ])
    changed_unit = _coverage([
        {"id": "k1", "shipped_concepts": ["a", "a2"], "destination": "C3-b", "depends_on": []},
        {"id": "k2", "shipped_concepts": ["b"], "destination": "F1-a", "depends_on": []},
    ])
    prerequisites_only = _coverage([
        {"id": "k1", "shipped_concepts": ["a"], "destination": "C3-b", "depends_on": ["k2"]},
        {"id": "k2", "shipped_concepts": ["b"], "destination": "F1-a", "depends_on": []},
    ])
    unattributed = _coverage([
        {"id": "k1", "shipped_concepts": ["a"], "destination": "C3-b", "depends_on": []},
        {"id": "k2", "shipped_concepts": ["b"], "destination": "F1-a", "depends_on": []},
        {"id": "k3", "shipped_concepts": ["c"], "depends_on": []},
    ])
    path = ["aio-ml/curriculum/coverage-map.yaml"]

    def route(new: str) -> str:
        return _route(path, old_text=lambda _: old, new_text=lambda _: new)["aio-ml"]

    assert route(changed_unit) == "scoped aio-ml --units C3-b"
    assert route(prerequisites_only) == "glossary aio-ml"
    assert route(unattributed) == "full aio-ml"


def test_teaching_order_prefixed_folder_routes_by_unit_id() -> None:
    """Plan 031: `units/03-C3-b/...` is unit C3-b, so the route stays scoped."""
    assert _route(["aio-ml/units/03-C3-b/lessons/01-x.ipynb"]) == _route(
        ["aio-ml/units/C3-b/lessons/01-x.ipynb"]
    )


def test_unconfigured_unit_change_routes_full() -> None:
    assert _route(["aio-ml/units/C9-new/lesson.ipynb"])["aio-ml"] == "full aio-ml"


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          check=True).stdout


def test_change_set_unions_committed_staged_unstaged_and_untracked(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "fixture@example.com")
    _git(repo, "config", "user.name", "Fixture")
    for name in ("committed.txt", "staged.txt", "unstaged.txt"):
        (repo / name).write_text("base\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "base")
    _git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    (repo / "committed.txt").write_text("changed\n")
    _git(repo, "commit", "-q", "-am", "change")
    (repo / "staged.txt").write_text("changed\n")
    _git(repo, "add", "staged.txt")
    (repo / "unstaged.txt").write_text("changed\n")
    (repo / "untracked.txt").write_text("new\n")
    changed, base = change_set(repo)
    assert base is not None
    assert changed == ["committed.txt", "staged.txt", "unstaged.txt", "untracked.txt"]

    _git(repo, "update-ref", "-d", "refs/remotes/origin/main")
    changed, base = change_set(repo)
    assert base is None  # fail-safe: route_books(..., diff_available=False) renders everything
    assert "untracked.txt" in changed
