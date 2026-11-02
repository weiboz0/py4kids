"""py4kids aio-001 Phase D: the mutation verifiers' `--repo-root` selects the book by aio_round.

usaaio passed each book's root by its id; py4kids picks the registered `content_model: aio`
book whose `aio_round` the verifier serves (training and classical: 1, attention: 2), so no
book id or root is hard-coded.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from types import SimpleNamespace

import pytest

VERIFIERS = [
    pytest.param("tools.aio.verify_training_mutations", "aio-ml", id="training-round-1"),
    pytest.param("tools.aio.verify_classical_mutations", "aio-ml", id="classical-round-1"),
    pytest.param("tools.aio.verify_attention_mutations", "aio-dl", id="attention-round-2"),
]


def _registry(repo: Path, *, rounds: dict[str, int]) -> None:
    lines = ["books_version: 2", "books:"]
    lines.append("  - {id: python-projects, number: 1, root: python-projects, depends_on: []}")
    previous: list[str] = []
    for book_id, aio_round in rounds.items():
        (repo / book_id).mkdir(parents=True, exist_ok=True)
        lines.append(
            f"  - {{id: {book_id}, number: 4, root: {book_id}, "
            f"depends_on: [{', '.join(previous)}], content_model: aio, aio_round: {aio_round}}}"
        )
        previous.append(book_id)
    (repo / "python-projects").mkdir(parents=True, exist_ok=True)
    (repo / "books.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _record_roots(module, monkeypatch: pytest.MonkeyPatch) -> list[Path]:
    seen: list[Path] = []
    spec = SimpleNamespace(id="fixture-mutation", notebook="fixture/solution.ipynb")

    def run_mutation(root: Path, _spec) -> object:
        seen.append(root)
        return module.MutationResult(mutation_id=spec.id, failure_cell=1)

    monkeypatch.setattr(module, "MUTATIONS", (spec,))
    monkeypatch.setattr(module, "run_mutation", run_mutation)
    if hasattr(module, "run_untouched"):
        monkeypatch.setattr(module, "run_untouched", lambda root, _spec: seen.append(root))
    return seen


@pytest.mark.parametrize(("module_name", "expected_book"), VERIFIERS)
def test_repo_root_selects_the_book_registered_for_the_verifier_round(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, module_name: str, expected_book: str
) -> None:
    module = importlib.import_module(module_name)
    _registry(tmp_path, rounds={"aio-ml": 1, "aio-dl": 2})
    seen = _record_roots(module, monkeypatch)

    assert module.main(["--repo-root", str(tmp_path)]) == 0
    assert seen
    assert set(seen) == {(tmp_path / expected_book).resolve()}


@pytest.mark.parametrize(("module_name", "_expected_book"), VERIFIERS)
def test_repo_root_without_a_book_for_the_round_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    module_name: str,
    _expected_book: str,
) -> None:
    module = importlib.import_module(module_name)
    # Register only the other round's book: the verifier's round has no book.
    other_round = 2 if module.AIO_ROUND == 1 else 1
    _registry(tmp_path, rounds={"aio-other": other_round})
    seen = _record_roots(module, monkeypatch)

    assert module.main(["--repo-root", str(tmp_path)]) == 1
    assert seen == []
    error = capsys.readouterr().err
    assert f"no single registered aio book has aio_round {module.AIO_ROUND}" in error


@pytest.mark.parametrize(("module_name", "expected_book"), VERIFIERS)
def test_root_and_repo_root_are_mutually_exclusive(
    tmp_path: Path, module_name: str, expected_book: str
) -> None:
    module = importlib.import_module(module_name)

    with pytest.raises(SystemExit) as exc_info:
        module.main(["--root", str(tmp_path / expected_book), "--repo-root", str(tmp_path)])
    assert exc_info.value.code == 2
