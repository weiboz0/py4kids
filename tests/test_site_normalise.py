"""Answer normalisation and hashing (design 012 D5; plan 101 B, Review Focus 3).

`tools/export/hash_vectors.json` pins every case below for part C's JavaScript port. Each
vector's expected normalised text is written out here by hand, so the code and the committed
file are both checked against an independent statement of the rule.
Regenerate the file (only when VECTORS change) with `uv run python tests/test_site_normalise.py`.
"""

import hashlib
import json
import re
from pathlib import Path

import pytest

from tools.export.normalise import answer_hash, normalise

REPO = Path(__file__).resolve().parents[1]

VECTORS_PATH = REPO / "tools" / "export" / "hash_vectors.json"
NBSP = " "

# (input, case, expected normalised text, item key)
VECTORS = [
    ("5", "sensitive", "5", "acsl/unit-01-computer-number-systems/exercises/ex1#1"),
    ("  5  ", "sensitive", "5", "acsl/unit-01-computer-number-systems/exercises/ex2"),
    ("a\r\nb\r\n", "sensitive", "a\nb", "book/unit-01-x/exercises/crlf"),
    ("a\rb", "sensitive", "a\nb", "book/unit-01-x/exercises/cr"),
    ("x  \r\ny\t\r\n", "sensitive", "x\ny", "book/unit-01-x/exercises/crlf-trailing"),
    ("a\t\tb", "sensitive", "a b", "book/unit-01-x/exercises/tabs"),
    ("1 \t 0  1", "sensitive", "1 0 1", "book/unit-01-x/exercises/mixed-ws"),
    (f"a{NBSP}b", "sensitive", "a b", "book/unit-01-x/exercises/nbsp"),
    (f"{NBSP}x{NBSP}", "sensitive", "x", "book/unit-01-x/exercises/nbsp-edges"),
    ("a b　c", "sensitive", "a b c", "book/unit-01-x/exercises/em-ideographic"),
    ("a\x1fb", "sensitive", "a b", "book/unit-01-x/exercises/unit-separator"),
    ("a\x85b", "sensitive", "a b", "book/unit-01-x/exercises/nel"),
    ("a b", "sensitive", "a b", "book/unit-01-x/exercises/line-separator"),
    ("a﻿b", "sensitive", "a﻿b", "book/unit-01-x/exercises/bom-kept"),
    ("\n\n  \nhello\n\n", "sensitive", "hello", "book/unit-01-x/exercises/blank-edges"),
    ("\r\n \t\r\nhello\r\n\r\n", "sensitive", "hello", "book/unit-01-x/exercises/blank-crlf"),
    ("a\n\nb", "sensitive", "a\n\nb", "book/unit-01-x/exercises/internal-blank"),
    ("a  \n   \nb", "sensitive", "a\n\nb", "book/unit-01-x/exercises/ws-only-line"),
    ("", "sensitive", "", "book/unit-01-x/exercises/empty"),
    (" \n\t\n", "sensitive", "", "book/unit-01-x/exercises/blank-only"),
    ("Straße", "sensitive", "Straße", "book/unit-01-x/exercises/strasse-s"),
    ("Straße", "insensitive", "strasse", "book/unit-01-x/exercises/strasse-i"),
    ("Hello  World", "sensitive", "Hello World", "book/unit-01-x/exercises/hello-s"),
    ("Hello  World", "insensitive", "hello world", "book/unit-01-x/exercises/hello-i"),
    ("ﬁve", "insensitive", "five", "book/unit-01-x/exercises/ligature"),
    ("A + ~B", "sensitive", "A + ~B", "acsl/unit-08-boolean-algebra/exercises/ex6"),
    ("5E", "insensitive", "5e", "acsl/unit-01-computer-number-systems/exercises/ex4"),
    ("True\nFalse\n", "sensitive", "True\nFalse", "book/unit-01-x/exercises/multi"),
]


def build_vectors() -> list[dict]:
    """The committed file's content: one object per vector, computed by the code under test."""
    return [
        {
            "input": text,
            "case": case,
            "normalised": normalise(text, case=case),
            "item_key": key,
            "hash": answer_hash(key, text, case=case),
        }
        for text, case, _expected, key in VECTORS
    ]


def write_vectors() -> None:
    VECTORS_PATH.write_text(
        json.dumps(build_vectors(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )


@pytest.mark.parametrize(("text", "case", "expected", "key"), VECTORS)
def test_vector_normalises(text, case, expected, key):
    assert normalise(text, case=case) == expected


def test_vector_file_matches_code():
    assert json.loads(VECTORS_PATH.read_text(encoding="utf-8")) == build_vectors()


def test_vector_file_pins_every_case():
    vectors = json.loads(VECTORS_PATH.read_text(encoding="utf-8"))
    assert [vector["normalised"] for vector in vectors] == [row[2] for row in VECTORS]
    assert {vector["case"] for vector in vectors} == {"sensitive", "insensitive"}
    for vector in vectors:
        assert set(vector) == {"input", "case", "normalised", "item_key", "hash"}
        assert re.fullmatch(r"sha256:[0-9a-f]{64}", vector["hash"])


def test_hash_is_salted_by_item_key():
    assert answer_hash("a/b/c/d", "5", case="sensitive") != answer_hash(
        "a/b/c/e", "5", case="sensitive"
    )


def test_hash_compares_normalised_text():
    assert answer_hash("a/b/c/d", " 5\r\n\n", case="sensitive") == answer_hash(
        "a/b/c/d", "5", case="sensitive"
    )
    assert answer_hash("a/b/c/d", "Yes", case="insensitive") == answer_hash(
        "a/b/c/d", "yes", case="insensitive"
    )
    assert answer_hash("a/b/c/d", "Yes", case="sensitive") != answer_hash(
        "a/b/c/d", "yes", case="sensitive"
    )


def test_hash_payload_is_pinned():
    payload = "py4kids-answer-v1\na/b/c/d\n5"
    expected = "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()
    assert answer_hash("a/b/c/d", "  5 ", case="sensitive") == expected


if __name__ == "__main__":
    write_vectors()
    print(f"wrote {VECTORS_PATH.relative_to(REPO)} ({len(VECTORS)} vectors)")
