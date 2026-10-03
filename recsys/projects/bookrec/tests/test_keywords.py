"""Tests for ``bookrec.load_keywords`` ([fable]#5): the committed keyword slice round-trips, and
``load_keywords`` enforces its error contract (missing column, duplicate item id).

The round-trip loads the committed ``keywords.csv.gz`` from the generated data dir and asserts every
token is drawn from the committed vocabulary (``recsys/data/vocabulary.py``) — the slice is never an
opaque blob. The vocabulary module lives under ``recsys/data``; add that directory to ``sys.path``
(as the data suite's own conftest does) so it imports as a plain module here too.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from bookrec import generated_dir, load_keywords

_DATA_DIR = str(Path(__file__).resolve().parents[3] / "data")
if _DATA_DIR not in sys.path:
    sys.path.insert(0, _DATA_DIR)

from _common import DatasetConfig
from vocabulary import vocabulary


def test_committed_keywords_round_trip_within_vocabulary() -> None:
    config = DatasetConfig()
    keywords = load_keywords(generated_dir() / "keywords.csv.gz")

    # One bag per catalog book, keyed by stable item id 0 .. n_books-1.
    assert len(keywords) == config.n_books
    assert set(keywords) == set(range(config.n_books))

    vocab = set(vocabulary(config.n_genres, config.latent_dim))
    tokens = {token for bag in keywords.values() for token in bag.split()}
    assert tokens, "expected non-empty keyword tokens"
    unknown = tokens - vocab
    assert not unknown, f"keyword tokens outside the committed vocabulary: {sorted(unknown)[:10]}"


def test_missing_column_raises(tmp_path: Path) -> None:
    path = tmp_path / "missing.csv"
    path.write_text("item_id,other\n0,alpha\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required column"):
        load_keywords(path)


def test_duplicate_item_id_raises(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.csv"
    path.write_text("item_id,keywords\n0,alpha beta\n0,gamma delta\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate item_id"):
        load_keywords(path)
