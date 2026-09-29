"""Plan 095 A1: pre-written tests for unit 11's FSA / regex evaluator (``assets/verify/fsa_eval.py``).

The evaluator's author implements this interface and does NOT edit this file:

``fsa_eval.accepts(pattern: str, s: str) -> bool``
    True when the ACSL regular expression ``pattern`` matches the WHOLE string ``s``. It
    translates ``pattern`` to Python's ``re`` syntax and uses ``re.fullmatch``. The translation is
    token by token:

    * OUTSIDE a ``[...]`` class, ``U`` is union and becomes ``|``, and ``λ`` (the empty string)
      becomes an empty group ``()``, so a quantifier after it stays valid (``λ*``, ``(λUa)b``)
    * INSIDE a class, ``U`` and ``λ`` are literal characters, while the class operators keep
      their meaning (``[A-D]`` a range, ``[^a-ceiou]`` a negated class)
    * everything else passes through unchanged, with ACSL's meaning = ``re``'s: concatenation,
      ``|``, ``*``, ``?``, ``+``, ``.`` (any character), ``( )``; precedence star (and the other
      quantifiers), then concatenation, then union

    * whitespace OUTSIDE a class is layout and is dropped (``ab U λ`` means ``abUλ``, as the
      wiki's identity table spaces its ``U``); INSIDE a class every character, a space
      included, stays literal (``[a ]`` matches a space)

    Items never use ``U`` or ``λ`` as a literal symbol outside a class.

``fsa_eval.run_dfa(table: dict, start, finals, s: str) -> bool``
    ``table`` maps ``(state, symbol)`` to the next state; ``finals`` is a collection of states.
    Starting at ``start``, read ``s`` one symbol at a time; a missing entry rejects at once.
    Accepts when the whole string is read and the state is in ``finals``.

``fsa_eval.same_language(p: str, q: str, alphabet, max_len: int) -> bool``
    True when ``accepts(p, w) == accepts(q, w)`` for every string ``w`` over ``alphabet`` (an
    iterable of one-character symbols) of length 0 to ``max_len``.

Expected values are the ACSL wiki's ("FSAs and Regular Expressions", categories.acsl.org), every
listed option of its "which strings are accepted" samples with the wiki's verdict, or
hand-computed (working in comments). All were re-checked with Python's ``re`` on hand
translations. Skips until the module exists.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

VERIFY_DIR = (
    Path(__file__).resolve().parents[1]
    / "acsl/units/unit-11-fsas-regular-expressions/assets/verify"
)
sys.path.insert(0, str(VERIFY_DIR))
fsa_eval = pytest.importorskip("fsa_eval")


# ---------------------------------------------------------------- the wiki's "accepted" samples

# Problem 2: "00*1*1U11*0*0"; the wiki accepts A and E.
WIKI_2 = [
    ("0000001111111", True),  # A
    ("1010101010", False),  # B
    ("1111111", False),  # C: 11*0*0 must end in 0; 00*1*1 must start with 0
    ("0110", False),  # D
    ("10", True),  # E
]

# Problem 3: "[A-D]*[a-d]*[0-9]"; the wiki accepts 1, 2, 3 and 7.
WIKI_3 = [
    ("ABCD8", True),  # 1
    ("abcd5", True),  # 2
    ("ABcd9", True),  # 3
    ("AbCd7", False),  # 4: an uppercase letter after a lowercase one
    ("X", False),  # 5
    ("abCD7", False),  # 6
    ("DCCBBBaaaa5", True),  # 7
]

# Problem 4: "Hi?g+h+[^a-ceiou]"; the wiki accepts 3, 6 and 7.
WIKI_4 = [
    ("Highb", False),  # 1: b is excluded
    ("HiiighS", False),  # 2: at most one i
    ("HigghhhC", True),  # 3
    ("Hih", False),  # 4: needs at least one g
    ("Hghe", False),  # 5: e is excluded
    ("Highd", True),  # 6: d is not excluded
    ("HgggggghX", True),  # 7
]


@pytest.mark.parametrize("s, expected", WIKI_2, ids=[s for s, _ in WIKI_2])
def test_wiki_problem_2(s, expected):
    assert fsa_eval.accepts("00*1*1U11*0*0", s) is expected


@pytest.mark.parametrize("s, expected", WIKI_3, ids=[s for s, _ in WIKI_3])
def test_wiki_problem_3(s, expected):
    assert fsa_eval.accepts("[A-D]*[a-d]*[0-9]", s) is expected


@pytest.mark.parametrize("s, expected", WIKI_4, ids=[s for s, _ in WIKI_4])
def test_wiki_problem_4(s, expected):
    assert fsa_eval.accepts("Hi?g+h+[^a-ceiou]", s) is expected


@pytest.mark.parametrize(
    "pattern, s, expected",
    [
        # The wiki's text examples.
        ("dca*b", "dcb", True),
        ("dca*b", "dcaab", True),
        ("dca*b", "db", False),
        ("d(ca)*b", "db", True),
        ("d(ca)*b", "dcacab", True),
        ("d(ca)*b", "dcb", False),
        ("colou?r", "color", True),
        ("colou?r", "colour", True),
        ("ab+c", "ac", False),
        ("ab+c", "abbc", True),
        ("a.b", "a7b", True),
        ("a.b", "abbb", False),
        ("gray|grey", "grey", True),
        ("xx*yy*", "xxxyy", True),
        ("xx*yy*", "yx", False),
        ("01*01", "011101", True),  # Problem 1's answer
        ("01*01", "0110", False),
    ],
)
def test_wiki_text_examples(pattern, s, expected):
    assert fsa_eval.accepts(pattern, s) is expected


def test_whole_string_only():
    assert not fsa_eval.accepts("ab", "abb")
    assert not fsa_eval.accepts("ab", "cab")
    assert fsa_eval.accepts("a*", "")


# ---------------------------------------------------------------- token-by-token translation


@pytest.mark.parametrize(
    "s, expected",
    [("a", True), ("b", True), ("ab", False), ("aUb", False), ("U", False), ("", False)],
)
def test_u_outside_a_class_is_union(s, expected):
    assert fsa_eval.accepts("aUb", s) is expected


@pytest.mark.parametrize(
    "s, expected",
    [("ab", True), ("c", True), ("abc", False), ("ac", False)],
)
def test_union_is_lowest_precedence(s, expected):
    # abUc = (ab) | c
    assert fsa_eval.accepts("abUc", s) is expected


@pytest.mark.parametrize(
    "s, expected",
    # If U became | inside the class, "U" would be rejected and "|" accepted.
    [("T", True), ("U", True), ("V", True), ("|", False), ("TU", False)],
)
def test_u_inside_a_class_is_literal(s, expected):
    assert fsa_eval.accepts("[TUV]", s) is expected


def test_lambda_inside_a_class_is_literal():
    assert fsa_eval.accepts("[λa]b", "λb")
    assert fsa_eval.accepts("[λa]b", "ab")
    assert not fsa_eval.accepts("[λa]b", "b")


def test_class_range_and_negation_kept():
    assert fsa_eval.accepts("[A-D]", "C")
    assert not fsa_eval.accepts("[A-D]", "E")
    assert not fsa_eval.accepts("[A-D]", "-")
    assert fsa_eval.accepts("[^a-ceiou]", "d")
    assert fsa_eval.accepts("[^a-ceiou]", "Z")
    assert not fsa_eval.accepts("[^a-ceiou]", "b")
    assert not fsa_eval.accepts("[^a-ceiou]", "o")


@pytest.mark.parametrize(
    "s, expected",
    # (λ U a)b: an optional a, then b
    [("b", True), ("ab", True), ("aab", False), ("", False)],
)
def test_lambda_union(s, expected):
    assert fsa_eval.accepts("(λUa)b", s) is expected


def test_lambda_with_a_quantifier():
    assert fsa_eval.accepts("λ*", "")
    assert not fsa_eval.accepts("λ*", "a")
    assert fsa_eval.accepts("aλ*b", "ab")
    assert fsa_eval.accepts("λ", "")
    assert not fsa_eval.accepts("λ", "λ")


# ---------------------------------------------------------------- the wiki's identities

ABC = ["a", "b", "c"]

WIKI_IDENTITIES = [
    ("(a*)*", "a*"),  # 1
    ("aa*", "a*a"),  # 2
    ("aa*Uλ", "a*"),  # 3
    ("a(bUc)", "abUac"),  # 4
    ("a(ba)*", "(ab)*a"),  # 5
    ("(aUb)*", "(a*Ub*)*"),  # 6
    ("(aUb)*", "(a*b*)*"),  # 7
    ("(aUb)*", "a*(ba*)*"),  # 8
]


@pytest.mark.parametrize("p, q", WIKI_IDENTITIES, ids=[f"{p} = {q}" for p, q in WIKI_IDENTITIES])
def test_wiki_identities(p, q):
    assert fsa_eval.same_language(p, q, ABC, 5)


@pytest.mark.parametrize(
    "p, q",
    [
        ("a*b*", "(aUb)*"),  # differ on "ba"
        ("(ab)*", "a*b*"),  # differ on "a"
        ("aa*", "a*"),  # differ on "" (identity 3 needs the U λ)
        ("a(bUc)", "abUc"),  # differ on "c"
    ],
)
def test_non_identities(p, q):
    assert not fsa_eval.same_language(p, q, ABC, 5)


def test_same_language_respects_max_len():
    # a{0,3} and a* agree on every string of length <= 3 and first differ on "aaaa".
    assert fsa_eval.same_language("(λUa)(λUa)(λUa)", "a*", ["a"], 3)
    assert not fsa_eval.same_language("(λUa)(λUa)(λUa)", "a*", ["a"], 4)


# ---------------------------------------------------------------- DFA tables

# The wiki's first FSA (states A, B, C; start A; final C): A -x-> B, B -x-> B, B -y-> C,
# C -y-> C; there are no other transitions. It accepts xx*yy*.
WIKI_FSA = {("A", "x"): "B", ("B", "x"): "B", ("B", "y"): "C", ("C", "y"): "C"}

# The wiki's Problem 1 FSA (unlabelled states, numbered here 1-4; start 1; final 4):
# 1 -0-> 2, 2 -1-> 2, 2 -0-> 3, 3 -1-> 4. Its expression is 01*01.
WIKI_FSA_1 = {(1, "0"): 2, (2, "1"): 2, (2, "0"): 3, (3, "1"): 4}


@pytest.mark.parametrize(
    "s, expected",
    [
        ("xy", True),  # the wiki's examples: xy, xxy, xxxyy, xyyy, xxyyyy
        ("xxy", True),
        ("xxxyy", True),
        ("xyyy", True),
        ("xxyyyy", True),
        ("", False),  # ends in A, not final
        ("x", False),  # ends in B, not final
        ("y", False),  # no (A, y) entry: missing transition rejects
        ("xyx", False),  # no (C, x) entry: missing transition rejects
        ("xyz", False),  # z is in no entry
    ],
)
def test_wiki_fsa_run(s, expected):
    assert fsa_eval.run_dfa(WIKI_FSA, "A", {"C"}, s) is expected
    # The table and its regular expression agree.
    assert fsa_eval.accepts("xx*yy*", s) is expected


@pytest.mark.parametrize("s", ["001", "0101", "011101", "01", "0110", "", "00", "0011"])
def test_wiki_problem_1_fsa_matches_its_expression(s):
    assert fsa_eval.run_dfa(WIKI_FSA_1, 1, {4}, s) is fsa_eval.accepts("01*01", s)


def test_dfa_finals_may_be_a_list():
    assert fsa_eval.run_dfa(WIKI_FSA, "A", ["C"], "xy")
    assert not fsa_eval.run_dfa(WIKI_FSA, "A", ["B"], "xy")
    assert fsa_eval.run_dfa(WIKI_FSA, "A", ["B"], "xx")


# ---------------------------------------------------------------- whitespace is layout outside a class


def test_spaced_union_is_layout():
    # (ab U λ)*a means (abUλ)*a, which is a(ba)* (wiki identity 5 with a λ).
    assert fsa_eval.same_language("a(ba)*", "(ab U λ)*a", "ab", 7)
    assert fsa_eval.accepts("a U b", "b")
    assert fsa_eval.accepts("a U b", "a")
    assert not fsa_eval.accepts("a U b", " ")


def test_space_inside_a_class_is_literal():
    assert fsa_eval.accepts("[a ]", " ")
    assert fsa_eval.accepts("[a ]", "a")
    assert not fsa_eval.accepts("[a ]", "")
