"""Shared test fixtures."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def real_site_bundle(tmp_path_factory):
    """`real_site_bundle(book)`: the real book exported once per session to a temporary bundle
    directory (plan 101 F: the answer-model and consumer tests share it)."""
    from tools.export.bundle import export_book

    made: dict[str, Path] = {}

    def get(book: str) -> Path:
        if book not in made:
            out = tmp_path_factory.mktemp(f"site-{book}") / "bundle"
            export_book(ROOT, book, out)
            made[book] = out
        return made[book]

    return get
