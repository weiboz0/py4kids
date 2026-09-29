"""Plan 094 A1: pre-written tests for unit 04's prefix/infix/postfix helper (``assets/verify/pip_eval.py``).

The helper's author implements this interface and does NOT edit this file:

``pip_eval.evaluate_prefix(expr: str) -> str`` and ``pip_eval.evaluate_postfix(expr: str) -> str``
    ``expr`` is single-space-separated tokens: non-negative integer operands and the binary
    operators ``+ - * /`` and ``↑`` (``^`` accepted as ``↑``; the en dash ``–`` accepted as ``-``).
    ``/`` is true division. Returns an integer when whole (``256``), otherwise Python's decimal
    (``4.5``).

``pip_eval.to_prefix(infix: str) -> str`` and ``pip_eval.to_postfix(infix: str) -> str``
    ``infix`` uses integer or letter-name operands (``12``, ``A``), the operators above, ``( )``
    and optionally ``=`` (lowest precedence); spaces optional. PEMDAS precedence (``↑`` highest),
    equal precedence left to right, operands never reordered. Returns single-space-separated
    tokens with ``↑`` for powers.

``pip_eval.prefix_to_postfix(expr) -> str`` and ``pip_eval.postfix_to_prefix(expr) -> str``
    Direct conversions; same token format in and out.

``pip_eval.prefix_to_infix(expr) -> str`` and ``pip_eval.postfix_to_infix(expr) -> str``
    Fully parenthesised infix, no spaces, as on the wiki: ``(((3*4)+(8/2))↑(7-5))``.

Expected values are the ACSL wiki's ("Prefix/Infix/Postfix Notation"), or hand-computed where the
wiki gives none (working in comments). Skips until the module exists.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

VERIFY_DIR = (
    Path(__file__).resolve().parents[1]
    / "acsl/units/unit-04-prefix-infix-postfix/assets/verify"
)
sys.path.insert(0, str(VERIFY_DIR))
pip_eval = pytest.importorskip("pip_eval")

WIKI_PREFIX = "↑ + * 3 4 / 8 2 - 7 5"
WIKI_POSTFIX = "3 4 * 8 2 / + 7 5 - ↑"


# ---------------------------------------------------------------- the wiki's examples


def test_wiki_opening_example():
    # 5 + 8/(3-1) = 9
    assert pip_eval.to_prefix("5+8/(3-1)") == "+ 5 / 8 - 3 1"
    assert pip_eval.to_postfix("5+8/(3-1)") == "5 8 3 1 - / +"
    assert pip_eval.evaluate_prefix("+ 5 / 8 - 3 1") == "9"
    assert pip_eval.evaluate_postfix("5 8 3 1 - / +") == "9"


def test_wiki_infix_to_prefix_and_postfix_with_assignment():
    infix = "X=(A*B-C/D)↑E"
    assert pip_eval.to_prefix(infix) == "= X ↑ - * A B / C D E"
    assert pip_eval.to_postfix(infix) == "X A B * C D / - E ↑ ="
    # the fully parenthesised form the wiki converts gives the same answers
    full = "(X = (((A * B) - (C / D)) ↑ E))"
    assert pip_eval.to_prefix(full) == "= X ↑ - * A B / C D E"
    assert pip_eval.to_postfix(full) == "X A B * C D / - E ↑ ="


def test_wiki_prefix_and_postfix_to_infix():
    assert pip_eval.prefix_to_infix(WIKI_PREFIX) == "(((3*4)+(8/2))↑(7-5))"
    assert pip_eval.postfix_to_infix(WIKI_POSTFIX) == "(((3*4)+(8/2))↑(7-5))"
    # the wiki's own glyphs: en dash for minus
    assert pip_eval.prefix_to_infix("↑ + * 3 4 / 8 2 – 7 5") == "(((3*4)+(8/2))↑(7-5))"


def test_wiki_expression_values():
    # (3*4 + 8/2) ↑ (7-5) = 16 ↑ 2 = 256
    assert pip_eval.evaluate_prefix(WIKI_PREFIX) == "256"
    assert pip_eval.evaluate_postfix(WIKI_POSTFIX) == "256"
    assert pip_eval.evaluate_postfix("3 4 * 8 2 / + 7 5 - ^") == "256"


def test_wiki_prefix_postfix_direct_conversions():
    assert pip_eval.prefix_to_postfix(WIKI_PREFIX) == WIKI_POSTFIX
    assert pip_eval.postfix_to_prefix(WIKI_POSTFIX) == WIKI_PREFIX
    assert pip_eval.prefix_to_postfix("+ 5 / 8 - 3 1") == "5 8 3 1 - / +"
    assert pip_eval.postfix_to_prefix("X A B * C D / - E ↑ =") == "= X ↑ - * A B / C D E"


# ---------------------------------------------------------------- precedence and order


@pytest.mark.parametrize(
    "infix, prefix, postfix",
    [
        ("8-3-2", "- - 8 3 2", "8 3 - 2 -"),  # equal precedence left to right
        ("8/4*2", "* / 8 4 2", "8 4 / 2 *"),
        ("2*3↑2", "* 2 ↑ 3 2", "2 3 2 ↑ *"),  # ↑ above *
        ("2*3^2", "* 2 ↑ 3 2", "2 3 2 ↑ *"),  # ^ accepted, answered as ↑
        ("( A + B ) * C", "* + A B C", "A B + C *"),  # spaced infix
        ("((A+B)*(C-D))/E", "/ * + A B - C D E", "A B + C D - * E /"),
        ("A+B*C-D", "- + A * B C D", "A B C * + D -"),
        ("12+30*2", "+ 12 * 30 2", "12 30 2 * +"),  # multi-digit operands
    ],
)
def test_infix_conversions(infix, prefix, postfix):
    assert pip_eval.to_prefix(infix) == prefix
    assert pip_eval.to_postfix(infix) == postfix
    assert pip_eval.prefix_to_postfix(prefix) == postfix
    assert pip_eval.postfix_to_prefix(postfix) == prefix


@pytest.mark.parametrize(
    "prefix, postfix, value",
    [
        ("- - 8 3 2", "8 3 - 2 -", "3"),  # (8-3)-2
        ("* / 8 4 2", "8 4 / 2 *", "4"),  # (8/4)*2
        ("* 2 ↑ 3 2", "2 3 2 ↑ *", "18"),  # 2*9
        ("* + 2 3 4", "2 3 + 4 *", "20"),
        ("+ 12 * 30 2", "12 30 2 * +", "72"),
        ("/ 9 2", "9 2 /", "4.5"),
        ("/ 3 4", "3 4 /", "0.75"),
        ("* / 5 2 2", "5 2 / 2 *", "5"),  # 2.5*2 is whole -> integer
        ("+ / 1 4 / 1 4", "1 4 / 1 4 / +", "0.5"),
        ("- 3 10", "3 10 -", "-7"),
    ],
)
def test_evaluations(prefix, postfix, value):
    assert pip_eval.evaluate_prefix(prefix) == value
    assert pip_eval.evaluate_postfix(postfix) == value
