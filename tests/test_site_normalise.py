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
U01E14A = "python-concepts/unit-01-output-and-variables/exercises/u01e14a"
TAB_ALIAS = {"\\t": "\t"}

# (input, case, expected normalised text, item key[, whitespace, aliases]) — plan 102 Phase 0
# adds `whitespace` (default "collapse") and `aliases` (default none) to `answer_format`.
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
    # plan 102 Phase 0: aliases map a typed form to the canonical one, after whitespace and case.
    ("^ A B", "sensitive", "↑ A B", "acsl/unit-04-x/exercises/alias", "collapse", {"^": "↑"}),
    ("↑ A B", "sensitive", "↑ A B", "acsl/unit-04-x/exercises/alias", "collapse", {"^": "↑"}),
    ("^ A B", "sensitive", "^ A B", "acsl/unit-04-x/exercises/alias"),
    ("^  a\tb ", "insensitive", "↑ a b", "acsl/unit-04-x/exercises/alias-i", "collapse",
     {"^": "↑", "B": "b"}),
    ("<=>", "sensitive", "≤>", "acsl/unit-04-x/exercises/alias-longest", "collapse",
     {"<": "‹", "<=": "≤"}),
    # plan 102 Phase 0: `exact` keeps tabs, indentation and inner runs.
    ("a\tb", "sensitive", "a\tb", "book/unit-01-x/exercises/exact-tab", "exact"),
    ("a b", "sensitive", "a b", "book/unit-01-x/exercises/exact-tab", "exact"),
    ("a\tb", "sensitive", "a b", "book/unit-01-x/exercises/exact-tab"),
    ("a b", "sensitive", "a b", "book/unit-01-x/exercises/exact-tab"),
    ("  x\r\n\ty  \r\nz\t\r\n", "sensitive", "  x\n\ty\nz", "book/unit-01-x/exercises/exact-crlf",
     "exact"),
    ("\n \t\n  a  b\n\n\t\n", "sensitive", "  a  b", "book/unit-01-x/exercises/exact-blank-edges",
     "exact"),
    ("a\n\n  b", "sensitive", "a\n\n  b", "book/unit-01-x/exercises/exact-internal-blank", "exact"),
    ("A\tB", "insensitive", "a\tb", "book/unit-01-x/exercises/exact-i", "exact"),
    # plan 102 content review 1 ([fable] 2): a `whitespace: exact` hint says "type a tab as `\t`",
    # so `aliases: {"\\t": "\t"}` maps a typed backslash-t to a real tab after whitespace handling.
    # python-concepts u01e14a: the typed form and the real-tab canonical hash equal under the alias.
    ("Sun comes up\nBirds sing\n\\tThe end\n", "sensitive", "Sun comes up\nBirds sing\n\tThe end",
     U01E14A, "exact", TAB_ALIAS),
    ("Sun comes up\nBirds sing\n\tThe end\n", "sensitive", "Sun comes up\nBirds sing\n\tThe end",
     U01E14A, "exact", TAB_ALIAS),
    ("Sun comes up\nBirds sing\n\\tThe end\n", "sensitive", "Sun comes up\nBirds sing\n\\tThe end",
     U01E14A, "exact"),
]


def _options(row: tuple) -> tuple[str, dict]:
    """(whitespace, aliases) of a vector row, with the defaults."""
    whitespace = row[4] if len(row) > 4 else "collapse"
    aliases = row[5] if len(row) > 5 else {}
    return whitespace, aliases


def build_vectors() -> list[dict]:
    """The committed file's content: one object per vector, computed by the code under test."""
    out = []
    for row in VECTORS:
        text, case, _expected, key = row[:4]
        whitespace, aliases = _options(row)
        out.append({
            "input": text,
            "case": case,
            "whitespace": whitespace,
            "aliases": aliases,
            "normalised": normalise(text, case=case, whitespace=whitespace, aliases=aliases),
            "item_key": key,
            "hash": answer_hash(key, text, case=case, whitespace=whitespace, aliases=aliases),
        })
    return out


def write_vectors() -> None:
    VECTORS_PATH.write_text(
        json.dumps(build_vectors(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )


@pytest.mark.parametrize("row", VECTORS)
def test_vector_normalises(row):
    text, case, expected, _key = row[:4]
    whitespace, aliases = _options(row)
    assert normalise(text, case=case, whitespace=whitespace, aliases=aliases) == expected


def test_vector_file_matches_code():
    assert json.loads(VECTORS_PATH.read_text(encoding="utf-8")) == build_vectors()


def test_vector_file_pins_every_case():
    vectors = json.loads(VECTORS_PATH.read_text(encoding="utf-8"))
    assert [vector["normalised"] for vector in vectors] == [row[2] for row in VECTORS]
    assert {vector["case"] for vector in vectors} == {"sensitive", "insensitive"}
    assert {vector["whitespace"] for vector in vectors} == {"collapse", "exact"}
    assert any(vector["aliases"] for vector in vectors)
    for vector in vectors:
        assert set(vector) == {"input", "case", "whitespace", "aliases", "normalised", "item_key",
                               "hash"}
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


def _hash(key: str, text: str, **options) -> str:
    return answer_hash(key, text, case=options.pop("case", "sensitive"), **options)


def test_alias_makes_typed_and_canonical_forms_equal():
    key = "acsl/unit-04-x/exercises/alias"
    assert _hash(key, "^ A B", aliases={"^": "↑"}) == _hash(key, "↑ A B", aliases={"^": "↑"})
    assert _hash(key, "^ A B") != _hash(key, "↑ A B")
    assert _hash(key, "^ A B", aliases={}) == _hash(key, "^ A B")


def test_exact_whitespace_keeps_tabs_and_collapse_does_not():
    key = "book/unit-01-x/exercises/exact-tab"
    assert _hash(key, "a\tb", whitespace="exact") != _hash(key, "a b", whitespace="exact")
    assert _hash(key, "a\tb", whitespace="collapse") == _hash(key, "a b", whitespace="collapse")
    assert _hash(key, "a\tb") == _hash(key, "a b")  # collapse is the default
    # exact still folds CRLF, trailing spaces and blank edge lines
    assert _hash(key, "\r\n  x \r\n\ty\r\n\r\n", whitespace="exact") == _hash(
        key, "  x\n\ty", whitespace="exact")


def test_defaults_leave_existing_hashes_unchanged():
    """An item without `whitespace` or `aliases` hashes exactly as before plan 102."""
    for row in VECTORS:
        text, case, _expected, key = row[:4]
        if len(row) == 4:
            payload = f"py4kids-answer-v1\n{key}\n{normalise(text, case=case)}"
            assert answer_hash(key, text, case=case) == (
                "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest())
            assert answer_hash(key, text, case=case) == answer_hash(
                key, text, case=case, whitespace="collapse", aliases=None)


def test_typed_backslash_t_is_a_tab_under_the_tab_alias():
    """[fable] 2: a literal `\\t` typed for u01e14a's tab hashes as the tab only under the alias;
    the alias runs after `exact` whitespace handling, so a real tab and leading indentation stay."""
    canonical = "Sun comes up\nBirds sing\n\tThe end\n"
    typed = "Sun comes up\nBirds sing\n\\tThe end\n"
    exact = {"whitespace": "exact"}
    assert _hash(U01E14A, typed, aliases=TAB_ALIAS, **exact) == _hash(
        U01E14A, canonical, aliases=TAB_ALIAS, **exact)
    assert _hash(U01E14A, typed, **exact) != _hash(U01E14A, canonical, **exact)
    # exact still distinguishes a tab from a space with the alias present
    assert _hash(U01E14A, canonical.replace("\t", " "), aliases=TAB_ALIAS, **exact) != _hash(
        U01E14A, canonical, aliases=TAB_ALIAS, **exact)
    assert _hash(U01E14A, canonical, aliases=TAB_ALIAS, **exact) == _hash(
        U01E14A, canonical, **exact)


def test_unknown_whitespace_mode_is_rejected():
    with pytest.raises(ValueError):
        normalise("a", case="sensitive", whitespace="loose")


def test_hash_payload_is_pinned():
    payload = "py4kids-answer-v1\na/b/c/d\n5"
    expected = "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()
    assert answer_hash("a/b/c/d", "  5 ", case="sensitive") == expected


if __name__ == "__main__":
    write_vectors()
    print(f"wrote {VECTORS_PATH.relative_to(REPO)} ({len(VECTORS)} vectors)")
