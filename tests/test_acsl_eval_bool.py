"""Plan 095 A1: pre-written tests for unit 08's Boolean evaluator (``assets/verify/bool_eval.py``).

The evaluator's author implements this interface and does NOT edit this file.

**Notation** (the book's, used by every item and answer):

* variables are single capital letters; ``1`` and ``0`` are TRUE and FALSE
* ``~`` NOT applies to the variable, constant or bracket right after it (``~A``, ``~(A + B)``);
  it may repeat (``~~A`` is double negation)
* binary operators, with a single space around each: ``*`` AND, ``⊕`` XOR, ``⊙`` XNOR, ``+`` OR
* precedence, highest first (ACSL's): ``~``; ``*``; ``⊕`` and ``⊙`` (one level); ``+``.
  Operators of equal precedence group left to right.
* brackets ``( )`` group

**Variables of an expression** are the distinct capital letters that appear in it, in
alphabetical order. ``solutions``, ``count``, ``column`` and ``minimal_sops`` run over those;
``equivalent`` runs over the union of both expressions' variables.

``bool_eval.evaluate(expr: str, values: dict[str, int]) -> int``
    The value (``0`` or ``1``) of ``expr`` when each variable ``v`` is ``values[v]`` (0 or 1).
    An expression with no variables takes ``{}``.

``bool_eval.solutions(expr: str, value: int = 1) -> str``
    The rows where ``expr`` equals ``value``, in canonical tuple text: each row is
    ``(A,B)`` / ``(A,B,C)`` / ... (values in alphabetical order of the variables, no inner spaces),
    rows in ascending binary order, joined by ``", "``: ``"(1,0), (1,1)"``. ``"NONE"`` when no
    row qualifies.

``bool_eval.count(expr: str, value: int = 1) -> int``
    The number of rows where ``expr`` equals ``value``.

``bool_eval.equivalent(a: str, b: str) -> bool``
    True when ``a`` and ``b`` agree on every row of the full truth table.

``bool_eval.minimal_sops(expr: str) -> list[str]``
    EVERY minimal sum of products of ``expr`` (fewest terms, then fewest literals in total),
    found by brute force over prime-implicant covers (2 to 4 variables), each in canonical text:

    * a term is its literals joined by ``" * "``, in alphabetical order of their variable
      (``~A * B``, not ``B * ~A``); terms are joined by ``" + "``
    * terms are ordered by comparing their literal lists position by position: the earlier
      variable first, then ``X`` before ``~X`` for the same variable, and a term that runs out
      first goes first (``A * B + ~A * C``; ``A * C + B``)
    * no ``⊕`` or ``⊙`` appears; a tautology gives ``["1"]`` and a contradiction ``["0"]``

    The list's own order is not pinned (tests compare it sorted).

``bool_eval.column(expr: str) -> str``
    The truth-table result column: one ``0``/``1`` per row, rows in ascending binary order of the
    variables (``00, 01, 10, 11`` for ``A, B``): ``column("~A + B") == "1101"``.

Expected values are the ACSL wiki's ("Boolean Algebra", categories.acsl.org) and the ACSL
Elementary Division's Boolean Algebra doc, translated into the book's notation, or hand-computed
where neither gives one (working in comments). All were re-checked by an independent throwaway
evaluator. Two sources' quirks: the Elementary doc lists truth-table rows and tuples in
DESCENDING order (the book uses ascending), and the wiki's Problem 2 table labels its column 6
"ADD of Col#1, Col#2" where it means the AND of columns 5 and 2 (its values are right).
Skips until the module exists.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

VERIFY_DIR = (
    Path(__file__).resolve().parents[1] / "acsl/units/unit-08-boolean-algebra/assets/verify"
)
sys.path.insert(0, str(VERIFY_DIR))
bool_eval = pytest.importorskip("bool_eval")

# Wiki Problem 1: NOT( NOT(A(A+B)) + B NOT A ), overbars translated to brackets.
WIKI_1 = "~(~(A * (A + B)) + B * ~A)"
# Wiki Problem 2: NOT( NOT(A+B) + NOT A B ).
WIKI_2 = "~(~(A + B) + ~A * B)"

ALL_PAIRS = "(0,0), (0,1), (1,0), (1,1)"


# ---------------------------------------------------------------- the wiki's two samples


def test_wiki_sample_1_simplifies_to_a():
    assert bool_eval.equivalent(WIKI_1, "A")
    assert bool_eval.minimal_sops(WIKI_1) == ["A"]


def test_wiki_sample_2_solutions():
    assert bool_eval.solutions(WIKI_2) == "(1,0), (1,1)"
    assert bool_eval.solutions(WIKI_2, 1) == "(1,0), (1,1)"
    assert bool_eval.count(WIKI_2) == 2
    # The wiki's truth table: rightmost column 0, 0, 1, 1 for rows 00, 01, 10, 11.
    assert bool_eval.column(WIKI_2) == "0011"
    assert bool_eval.equivalent(WIKI_2, "A")


def test_wiki_sample_2_false_rows():
    assert bool_eval.solutions(WIKI_2, 0) == "(0,0), (0,1)"
    assert bool_eval.count(WIKI_2, 0) == 2


def test_wiki_video_triples():
    # Wiki video (2013-14 Senior, Contest 3): (AB + ~C)(~A + BC)(A + ~B + C).
    # Rows: 000 -> 1*1*1 = 1; 001 -> AB + ~C = 0; 010 -> A + ~B + C = 0; 011 -> AB + ~C = 0;
    # 100 -> ~A + BC = 0; 101 -> AB + ~C = 0; 110 -> ~A + BC = 0; 111 -> 1*1*1 = 1.
    expr = "(A * B + ~C) * (~A + B * C) * (A + ~B + C)"
    assert bool_eval.solutions(expr) == "(0,0,0), (1,1,1)"
    assert bool_eval.count(expr) == 2


# ---------------------------------------------------------------- the Elementary doc


def test_elementary_simplify_sample():
    # Doc: ~(A + ~B) + ~A * B = ~A * ~(~B) + ~A * B = ~A * B; the only pair is (0, 1).
    expr = "~(A + ~B) + ~A * B"
    assert bool_eval.equivalent(expr, "~A * B")
    assert bool_eval.minimal_sops(expr) == ["~A * B"]
    assert bool_eval.solutions(expr) == "(0,1)"


def test_elementary_truth_table_examples():
    # Doc: ~(A * B) is FALSE only at (1, 1); A + ~B is TRUE for 3 pairs.
    assert bool_eval.solutions("~(A * B)", 0) == "(1,1)"
    assert bool_eval.count("A + ~B") == 3
    assert bool_eval.column("~(A * B)") == "1110"
    assert bool_eval.column("A + ~B") == "1011"


def test_elementary_de_morgan_table():
    # Doc: columns 4 and 7, and columns 9 and 10, are the same.
    assert bool_eval.column("~(A * B)") == bool_eval.column("~A + ~B")
    assert bool_eval.column("~(A + B)") == bool_eval.column("~A * ~B") == "1000"


def test_elementary_no_true_pairs():
    # Doc: (NOT (NOT A OR B)) AND (NOT (A OR NOT B)) = (A * ~B) * (~A * B) = 0.
    expr = "~(~A + B) * ~(A + ~B)"
    assert bool_eval.solutions(expr) == "NONE"
    assert bool_eval.count(expr) == 0
    assert bool_eval.solutions(expr, 0) == ALL_PAIRS
    assert bool_eval.count(expr, 0) == 4
    assert bool_eval.minimal_sops(expr) == ["0"]


def test_elementary_tautology_options():
    # Doc: a) A * ~A + B = B; b) A + ~A * B does not simplify to 1; c) (A + ~A) + B = 1.
    assert bool_eval.equivalent("A * ~A + B", "B")
    assert bool_eval.count("A * ~A + B") == 2
    assert bool_eval.count("A + ~A * B") == 3
    assert bool_eval.count("(A + ~A) + B") == 4
    assert bool_eval.minimal_sops("(A + ~A) + B") == ["1"]
    # Doc: ~(A * B) + B, A + 1 and A + ~A are tautologies.
    assert bool_eval.count("~(A * B) + B") == 4
    assert bool_eval.count("A + 1") == 2
    assert bool_eval.count("A + ~A") == 2
    assert bool_eval.minimal_sops("A + ~A + B") == ["1"]


def test_elementary_count_pairs():
    # Doc: ~(~(A * (A + B)) + (B * ~A)) is TRUE for (1,1) and (1,0): 2 pairs.
    expr = "~(~(A * (A + B)) + (B * ~A))"
    assert bool_eval.count(expr) == 2
    assert bool_eval.solutions(expr) == "(1,0), (1,1)"


def test_elementary_equivalence_options():
    # Doc: a) A * ~(B + ~A) and b) A * ~B are equivalent; c) A * ~(~B + A) is not (always 0).
    assert bool_eval.equivalent("A * ~(B + ~A)", "A * ~B")
    assert not bool_eval.equivalent("A * ~(~B + A)", "A * ~B")
    assert bool_eval.column("A * ~(~B + A)") == "0000"


def test_elementary_simplify_then_count_false():
    # Doc: NOT (((A OR NOT A) AND NOT B) AND (NOT A AND B)) = 1; 0 pairs make it FALSE.
    expr = "~(((A + ~A) * ~B) * (~A * B))"
    assert bool_eval.count(expr, 0) == 0
    assert bool_eval.solutions(expr, 0) == "NONE"
    assert bool_eval.minimal_sops(expr) == ["1"]
    # Doc: NOT (A AND NOT B) OR NOT (NOT A AND B) = 1; all 4 pairs make it TRUE.
    assert bool_eval.solutions("~(A * ~B) + ~(~A * B)") == ALL_PAIRS


def test_elementary_statements_as_constants():
    # Doc: "3+4>6 AND 7-2>6" is TRUE AND FALSE = FALSE.
    assert bool_eval.evaluate("1 * 0", {}) == 0
    # Doc: (NOT (3+4<6) AND (7-2>6)) OR NOT (5+1=6) = (~0 * 0) + ~1 = 0 + 0 = FALSE.
    assert bool_eval.evaluate("(~0 * 0) + ~1", {}) == 0
    assert bool_eval.evaluate("~0 * 0 + ~1", {}) == 0


# ---------------------------------------------------------------- precedence


@pytest.mark.parametrize(
    "expr, same_as, not_same_as",
    [
        ("~A * B", "(~A) * B", "~(A * B)"),  # ~ binds only the next variable
        ("A ⊕ B * C", "A ⊕ (B * C)", "(A ⊕ B) * C"),  # * before ⊕
        ("A ⊙ B * C", "A ⊙ (B * C)", "(A ⊙ B) * C"),  # * before ⊙
        ("A + B ⊕ C", "A + (B ⊕ C)", "(A + B) ⊕ C"),  # ⊕ before +
        ("A ⊕ B + C", "(A ⊕ B) + C", "A ⊕ (B + C)"),
        ("A + B ⊙ C", "A + (B ⊙ C)", "(A + B) ⊙ C"),  # ⊙ before +
        ("A ⊙ B + C", "(A ⊙ B) + C", "A ⊙ (B + C)"),
        ("~A * B + C", "((~A) * B) + C", "~(A * B + C)"),
        ("A * ~B ⊕ C + D", "((A * (~B)) ⊕ C) + D", "A * ~(B ⊕ C + D)"),  # all four levels
    ],
)
def test_precedence_by_bracketing(expr, same_as, not_same_as):
    assert bool_eval.equivalent(expr, same_as)
    assert not bool_eval.equivalent(expr, not_same_as)


@pytest.mark.parametrize(
    "expr, values, expected",
    [
        ("~A * B", {"A": 0, "B": 0}, 0),  # (~0) * 0 = 0; ~(0 * 0) would be 1
        ("A ⊕ B * C", {"A": 1, "B": 1, "C": 0}, 1),  # 1 ⊕ (1 * 0) = 1; (1 ⊕ 1) * 0 = 0
        ("A ⊙ B * C", {"A": 0, "B": 1, "C": 0}, 1),  # 0 ⊙ (1 * 0) = 0 ⊙ 0 = 1; (0 ⊙ 1) * 0 = 0
        ("A + B ⊕ C", {"A": 1, "B": 1, "C": 1}, 1),  # 1 + (1 ⊕ 1) = 1; (1 + 1) ⊕ 1 = 0
        ("A ⊙ B + C", {"A": 0, "B": 1, "C": 1}, 1),  # (0 ⊙ 1) + 1 = 1; 0 ⊙ (1 + 1) = 0
        ("A + B ⊙ C", {"A": 1, "B": 0, "C": 0}, 1),  # 1 + (0 ⊙ 0) = 1; (1 + 0) ⊙ 0 = 0
        ("A * B + C", {"A": 0, "B": 1, "C": 1}, 1),
        ("A + B * C", {"A": 0, "B": 1, "C": 0}, 0),  # 0 + (1 * 0) = 0; (0 + 1) * 0 = 0
        ("A + B * C", {"A": 1, "B": 0, "C": 0}, 1),  # 1 + (0 * 0) = 1; (1 + 0) * 0 = 0
    ],
)
def test_precedence_spot_values(expr, values, expected):
    assert bool_eval.evaluate(expr, values) == expected


@pytest.mark.parametrize(
    "expr, left_grouped",
    [
        ("A ⊕ B ⊙ C", "(A ⊕ B) ⊙ C"),
        ("A ⊙ B ⊕ C", "(A ⊙ B) ⊕ C"),
        ("A ⊕ B ⊕ C ⊙ D", "((A ⊕ B) ⊕ C) ⊙ D"),
        ("A * B * C", "(A * B) * C"),
        ("A + B + C", "(A + B) + C"),
    ],
)
def test_equal_precedence_left_to_right(expr, left_grouped):
    # ⊕/⊙ chains are associative in value (x ⊙ y = x ⊕ y ⊕ 1), so left-to-right grouping is
    # not observable in values; these check that mixed same-level chains parse at all.
    assert bool_eval.equivalent(expr, left_grouped)


# ---------------------------------------------------------------- laws


def test_de_morgan():
    assert bool_eval.equivalent("~(A + B)", "~A * ~B")
    assert bool_eval.equivalent("~(A * B)", "~A + ~B")
    assert not bool_eval.equivalent("~(A + B)", "~A + ~B")
    assert not bool_eval.equivalent("~(A * B)", "~A * ~B")
    assert bool_eval.equivalent("~(A + B + C)", "~A * ~B * ~C")


@pytest.mark.parametrize(
    "left, right",
    [
        ("A ⊕ B", "A * ~B + ~A * B"),  # XOR from the basic operators
        ("A ⊙ B", "A * B + ~A * ~B"),  # XNOR from the basic operators
        ("A ⊙ B", "~(A ⊕ B)"),  # XNOR is NOT XOR
        ("A ⊙ B", "A ⊕ ~B"),
        ("A ⊙ B", "~A ⊕ B"),
        ("A ⊕ B", "B ⊕ A"),
        ("A ⊙ B", "B ⊙ A"),
    ],
)
def test_xor_xnor_identities(left, right):
    assert bool_eval.equivalent(left, right)


def test_xor_and_xnor_columns():
    assert bool_eval.column("A ⊕ B") == "0110"
    assert bool_eval.column("A ⊙ B") == "1001"
    assert not bool_eval.equivalent("A ⊕ B", "A ⊙ B")


@pytest.mark.parametrize(
    "left, right",
    [
        ("A + A * B", "A"),  # absorptive
        ("A + ~A * B", "A + B"),  # absorptive
        ("A * (A + B)", "A"),  # absorptive
        ("(A + B) * (A + C)", "A + B * C"),  # distributive
        ("A * (B + C)", "A * B + A * C"),  # distributive
        ("A + 0", "A"),
        ("A * 1", "A"),
        ("A * 0", "0"),
        ("A + 1", "1"),
    ],
)
def test_other_laws(left, right):
    assert bool_eval.equivalent(left, right)


# ---------------------------------------------------------------- double negation


def test_double_negation():
    assert bool_eval.evaluate("~~A", {"A": 1}) == 1
    assert bool_eval.evaluate("~~A", {"A": 0}) == 0
    assert bool_eval.equivalent("~~A", "A")
    assert bool_eval.equivalent("~(~A)", "A")
    assert bool_eval.equivalent("~~~A", "~A")
    assert bool_eval.equivalent("~~(A + B)", "A + B")
    assert bool_eval.column("~~A * B") == "0001"


# ---------------------------------------------------------------- truth-table columns


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("~A + B", "1101"),  # the plan's example
        ("A * B", "0001"),
        ("A + B", "0111"),
        # rows 000..111: C or (A and B) -> 0 1 0 1 0 1 1 1
        ("A * B + C", "01010111"),
        # odd parity -> 0 1 1 0 1 0 0 1
        ("A ⊕ B ⊕ C", "01101001"),
    ],
)
def test_column(expr, expected):
    assert bool_eval.column(expr) == expected


# ---------------------------------------------------------------- tuple order and counts


def test_tuple_order_two_variables():
    assert bool_eval.solutions("A + B") == "(0,1), (1,0), (1,1)"
    assert bool_eval.solutions("A + B", 0) == "(0,0)"
    # variables sorted alphabetically, whatever order they appear in
    assert bool_eval.solutions("B * ~A") == "(0,1)"


def test_tuple_order_three_variables():
    # C + A*B true at 001, 011, 101, 110, 111 (see the column test)
    assert bool_eval.solutions("A * B + C") == "(0,0,1), (0,1,1), (1,0,1), (1,1,0), (1,1,1)"
    assert bool_eval.solutions("A * B + C", 0) == "(0,0,0), (0,1,0), (1,0,0)"
    assert bool_eval.count("A * B + C") == 5
    assert bool_eval.count("A * B + C", 0) == 3


def test_four_variable_counts():
    # A*B true on 4 rows, C*D on 4, both on 1: 4 + 4 - 1 = 7
    assert bool_eval.count("A * B + C * D") == 7
    assert bool_eval.count("A * B + C * D", 0) == 9
    assert bool_eval.solutions("A * B * C * D") == "(1,1,1,1)"
    assert bool_eval.count("A ⊕ B ⊕ C ⊕ D") == 8


def test_equivalent_over_union_of_variables():
    assert bool_eval.equivalent("A + A * B", "A")
    assert bool_eval.equivalent("A", "A + A * B")
    assert not bool_eval.equivalent("A", "A * B")


# ---------------------------------------------------------------- minimal sums of products


def test_minimal_sop_drops_consensus_term():
    # Primes: A*B, ~A*C, B*C. Only {A*B, ~A*C} covers with 2 terms; B*C is the consensus term.
    assert bool_eval.minimal_sops("A * B + ~A * C + B * C") == ["A * B + ~A * C"]
    assert bool_eval.minimal_sops("A * B + ~A * C") == ["A * B + ~A * C"]


def test_minimal_sop_ties_return_all():
    # True unless A = B = C. Six primes (A~B, ~AB, B~C, ~BC, A~C, ~AC); two cyclic 3-term covers.
    result = bool_eval.minimal_sops("A * ~B + ~A * B + B * ~C + ~B * C")
    assert len(result) > 1
    assert sorted(result) == sorted(["A * ~B + ~A * C + B * ~C", "A * ~C + ~A * B + ~B * C"])


def test_minimal_sop_two_variable_input():
    assert bool_eval.minimal_sops("A + ~A * B") == ["A + B"]
    assert bool_eval.minimal_sops("A * B + A * ~B") == ["A"]


def test_minimal_sop_tautology_and_contradiction():
    # minimal_sops is pinned for 2 to 4 variables, so these carry a second variable
    assert bool_eval.minimal_sops("A + ~A + B") == ["1"]
    assert bool_eval.minimal_sops("A * ~A * B") == ["0"]
    assert bool_eval.minimal_sops("~(A * B) + B") == ["1"]


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("~A * C + A * B", "A * B + ~A * C"),  # A before ~A
        ("B * ~A", "~A * B"),  # literals in variable order within a term
        ("B + A * C", "A * C + B"),  # first variable decides, not term length
        ("~A * B + A * ~B", "A * ~B + ~A * B"),
        ("A ⊕ B", "A * ~B + ~A * B"),  # no XOR in a simplified answer
        ("A ⊙ B", "A * B + ~A * ~B"),  # no XNOR in a simplified answer
        ("A * B * C * D + A * B * C * ~D", "A * B * C"),  # 4 variables
    ],
)
def test_minimal_sop_canonical_order(expr, expected):
    assert bool_eval.minimal_sops(expr) == [expected]
