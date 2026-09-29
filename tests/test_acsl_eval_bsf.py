"""Plan 094 A1: pre-written tests for unit 05's bit-string evaluator (``assets/verify/bsf_eval.py``).

The evaluator's author implements this interface and does NOT edit this file:

``bsf_eval.evaluate(expr: str) -> str``
    Evaluate an ACSL bit-string expression and return the result bit string. Operators, word forms
    case-insensitive: ``NOT``/``~``/``¬``, ``AND``/``&``, ``OR``/``|``, ``XOR``/``⊕``, and
    ``LSHIFT-n``, ``RSHIFT-n``, ``LCIRC-n``, ``RCIRC-n`` (n may exceed the length: circulates take
    it mod the length, shifts clear the string). Parentheses group; a shift/circulate may be
    written with or without parentheses around it and its operand (``(LSHIFT-2 x)``). ``~`` may
    touch its operand (``~101110``). Precedence, highest first: NOT; shift/circulate; AND; XOR;
    OR. Equal precedence evaluates left to right; unary operators bind right to left
    (``NOT RSHIFT-1 x`` = ``NOT (RSHIFT-1 x)``). A binary operator pads the shorter operand with 0s
    on the left, so the result has the longer operand's width; shifts and circulates keep width.

``bsf_eval.solve(expr_with_x: str, result: str, width: int) -> list[str]``
    Every ``width``-bit value of the variable ``x`` for which ``evaluate`` of the expression
    (with ``x`` replaced by that value) equals ``result``, in ascending binary order (brute force).

Expected values are the ACSL wiki's ("Bit-String Flicking"), or hand-computed where the wiki gives
none (working in comments). Wiki erratum: its XOR example prints ``1011011 xor 011001 = 110010``;
the true value (7 bits, 0-padded) is ``1000010``, tested below. Skips until the module exists.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

VERIFY_DIR = (
    Path(__file__).resolve().parents[1] / "acsl/units/unit-05-bit-string-flicking/assets/verify"
)
sys.path.insert(0, str(VERIFY_DIR))
bsf_eval = pytest.importorskip("bsf_eval")


# ---------------------------------------------------------------- the wiki's operator examples


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("~101110", "010001"),
        ("NOT 101110", "010001"),
        ("1011011 and 0011001", "0011001"),
        ("1011011 or 0011001", "1011011"),
        ("1011011 xor 011001", "1000010"),  # wiki prints 110010 (erratum, see docstring)
        ("11010 and 1110", "01010"),  # 1110 padded to 01110
    ],
)
def test_wiki_bitwise_examples(expr, expected):
    assert bsf_eval.evaluate(expr) == expected


SHIFT_TABLE = [
    # x, LSHIFT-2, RSHIFT-3, LCIRC-3, RCIRC-1
    ("01101", "10100", "00001", "01011", "10110"),
    ("10", "00", "00", "01", "01"),
    ("1110", "1000", "0001", "0111", "0111"),
    ("1011011", "1101100", "0001011", "1011101", "1101101"),
]


@pytest.mark.parametrize("row", SHIFT_TABLE, ids=[row[0] for row in SHIFT_TABLE])
def test_wiki_shift_table(row):
    x, lshift2, rshift3, lcirc3, rcirc1 = row
    assert bsf_eval.evaluate(f"(LSHIFT-2 {x})") == lshift2
    assert bsf_eval.evaluate(f"(RSHIFT-3 {x})") == rshift3
    assert bsf_eval.evaluate(f"(LCIRC-3 {x})") == lcirc3
    assert bsf_eval.evaluate(f"(RCIRC-1 {x})") == rcirc1


@pytest.mark.parametrize(
    "expr, expected",
    [
        # Sample Problem 1
        ("(101110 AND NOT 110110 OR (LSHIFT-3 101010))", "011000"),
        # Sample Problem 2
        ("(RCIRC-2 01101)", "01011"),
        ("(LCIRC-4 01011)", "10101"),
        ("(RSHIFT-1 (LCIRC-4 (RCIRC-2 01101)))", "01010"),
        # Sample Problem 4 (circulate counts beyond the length)
        ("(LCIRC-23 01101)", "01011"),
        ("(RCIRC-14 (LCIRC-23 01101))", "10110"),
        ("(LSHIFT-1 10011)", "00110"),
        ("(RSHIFT-2 10111)", "00101"),
        ("((RCIRC-14 (LCIRC-23 01101)) | (LSHIFT-1 10011) & (RSHIFT-2 10111))", "10110"),
    ],
)
def test_wiki_sample_problems(expr, expected):
    assert bsf_eval.evaluate(expr) == expected


# ---------------------------------------------------------------- precedence and forms


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("1 | 1 ⊕ 1", "1"),  # XOR before OR: 1 | (1 ⊕ 1) = 1 | 0; left-to-right would give 0
        ("1 XOR 1 AND 0", "1"),  # AND before XOR: 1 ⊕ (1 & 0); left-to-right would give 0
        ("NOT 01 AND 01", "00"),  # NOT binds its operand only: 10 & 01
        ("LSHIFT-1 011 AND 001", "000"),  # shift before AND: 110 & 001
        ("NOT RSHIFT-1 01101", "11001"),  # right to left: NOT 00110
        ("RSHIFT-1 NOT 01101", "01001"),  # RSHIFT-1 10010
        ("1011 ⊕ 0110", "1101"),
        ("1100 & 1010", "1000"),
        ("10 | 01", "11"),
        ("¬0011", "1100"),
        ("(RSHIFT-3 (LCIRC-2 (NOT 10110)))", "00000"),  # NOT 01001, LCIRC-2 00101, RSHIFT-3
        ("LSHIFT-7 10110", "00000"),  # a shift past the length clears the string
    ],
)
def test_precedence_and_operator_forms(expr, expected):
    assert bsf_eval.evaluate(expr) == expected


# ---------------------------------------------------------------- solve for x


def test_wiki_solve_for_x():
    # Sample Problem 3: x = 00*0* -> four values
    assert bsf_eval.solve("(LSHIFT-1 (10110 XOR (RCIRC-3 x) AND 11011))", "01100", 5) == [
        "00000", "00001", "00100", "00101",
    ]


@pytest.mark.parametrize(
    "expr, result, width, expected",
    [
        ("NOT x", "0101", 4, ["1010"]),
        ("x AND 1100", "0100", 4, ["0100", "0101", "0110", "0111"]),  # x = 01**
        ("x AND 0000", "0001", 4, []),  # no solution
        ("(LCIRC-1 x)", "0011", 4, ["1001"]),
    ],
)
def test_solve_single_operation(expr, result, width, expected):
    assert bsf_eval.solve(expr, result, width) == expected
