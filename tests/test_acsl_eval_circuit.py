"""Plan 096 A1: pre-written tests for unit 13's circuit evaluator (``assets/verify/circuit_eval.py``).

The evaluator's author implements this interface and does NOT edit this file.

**Netlist.** A circuit is given as text, one statement per line:

* The first line is ``INPUTS`` followed by the circuit's input variables, single capital letters
  in alphabetical order (``INPUTS A B C``). Each declared input is a column of every tuple, even
  when no gate uses it.
* Then one gate per line: ``name = GATE(x, y)``, or ``name = GATE(x)`` for ``BUFFER`` and
  ``NOT``. ``GATE`` is one of ``BUFFER NOT AND NAND OR NOR XOR XNOR`` (two inputs for the last
  six). Each of ``x``, ``y`` is a declared input or the name of an EARLIER gate; a gate's output
  may feed several gates.
* Gate names are lowercase words (``p``, ``q``, ``na``, ``out``), so they never collide with
  the capital inputs.
* The LAST line's gate is the circuit's output.
* Layout: blank lines and leading/trailing whitespace on a line are ignored (so an indented
  triple-quoted string works), and the spaces around ``=``, ``(``, ``,`` and ``)`` are optional.

Gate truth (the wiki's table; ``x``, ``y`` in 0/1): BUFFER ``x``; NOT ``1 - x``; AND, OR, XOR as
usual; NAND = NOT AND; NOR = NOT OR; XNOR = NOT XOR (1 when the inputs are equal).

``circuit_eval.evaluate(netlist: str, values: dict[str, int]) -> int``
    The output (0 or 1) when each declared input ``v`` is ``values[v]`` (0 or 1).

``circuit_eval.solutions(netlist: str, value: int = 1) -> str``
    The input rows where the output equals ``value``, in unit 08's canonical tuple text: each
    row ``(A,B,C)`` with the values of the declared inputs in ``INPUTS`` order and no inner
    spaces, rows in ascending binary order, joined by ``", "``; ``"NONE"`` when no row
    qualifies.

``circuit_eval.count(netlist: str, value: int = 1) -> int``
    The number of rows where the output equals ``value``.

``circuit_eval.to_expression(netlist: str) -> str``
    The output as an expression in the book's Boolean notation (unit 08's ``bool_eval``
    grammar), built gate by gate from each operand's text:

    * an input is its letter; ``BUFFER(x)`` is ``x``'s text unchanged
    * an operand is an ATOM when it is a single input letter or a negation (``~`` followed by an
      atom or by one bracketed group spanning the rest: ``~A``, ``~~A``, ``~(A * B)``); any other
      operand is wrapped in brackets ``( )``
    * ``NOT(x)`` is ``~`` + atom(x); ``AND`` is ``atom(x) * atom(y)``; ``OR`` ``atom(x) + atom(y)``;
      ``XOR`` ``atom(x) ⊕ atom(y)``; ``XNOR`` ``atom(x) ⊙ atom(y)``; ``NAND`` is
      ``~(atom(x) * atom(y))``; ``NOR`` is ``~(atom(x) + atom(y))`` -- operands in the gate's own
      order, a single space around each binary operator
    * the final output is not bracketed

    So the wiki's first sample is ``~(A * B) + C`` and its third
    ``(~A * (A + B)) * ~(B + C)``, matching the wiki's own translations.

Simplifying a circuit reuses unit 08's ``bool_eval.minimal_sops`` on ``to_expression``'s text;
the tests import ``bool_eval`` from ``unit-08-boolean-algebra/assets/verify``.

Sources: the ACSL wiki "Digital Electronics" page (categories.acsl.org, retrieved 2026-09-29).
Its circuits are images; the netlists below are transcriptions of NotABorC.svg,
circuit-sample2-labels.svg and Circuit-PB.png, each checked against the wiki's own expression or
truth table. Every expected value was re-checked against an independent throwaway evaluator.
Skips until the module exists.
"""

from __future__ import annotations

import sys
from itertools import product
from pathlib import Path

import pytest

ACSL_UNITS = Path(__file__).resolve().parents[1] / "acsl/units"
sys.path.insert(0, str(ACSL_UNITS / "unit-08-boolean-algebra/assets/verify"))
sys.path.insert(0, str(ACSL_UNITS / "unit-13-digital-electronics/assets/verify"))
circuit_eval = pytest.importorskip("circuit_eval")
bool_eval = pytest.importorskip("bool_eval")


def _inputs(netlist: str) -> list[str]:
    first = next(ln for ln in netlist.splitlines() if ln.strip())
    return first.split()[1:]


def _rows(netlist: str):
    names = _inputs(netlist)
    for bits in product((0, 1), repeat=len(names)):
        yield bits, dict(zip(names, bits))


def _column(netlist: str) -> str:
    return "".join(str(circuit_eval.evaluate(netlist, row)) for _, row in _rows(netlist))


# ---------------------------------------------------------------- the wiki's samples

# Sample Problem 1 ("Find all ordered triplets (A, B, C) which make the following circuit
# FALSE"). NotABorC.svg: A and B enter a NAND gate; its output and C enter an OR gate, the
# output. The wiki's own translation: ~(A * B) + C.
WIKI_1 = """
    INPUTS A B C
    p = NAND(A, B)
    out = OR(p, C)
"""


def test_wiki_sample_1_only_false_triple():
    # "The final answer is (TRUE, TRUE, FALSE), or (1, 1, 0)."
    assert circuit_eval.solutions(WIKI_1, 0) == "(1,1,0)"
    assert circuit_eval.count(WIKI_1, 0) == 1
    assert circuit_eval.count(WIKI_1) == 7
    assert circuit_eval.evaluate(WIKI_1, {"A": 1, "B": 1, "C": 0}) == 0


def test_wiki_sample_1_expression():
    # "This circuit translates to the Boolean expression" NOT(AB) + C.
    assert circuit_eval.to_expression(WIKI_1) == "~(A * B) + C"


# Sample Problem 2 ("How many ordered 4-tuples (A, B, C, D) make the following circuit TRUE?").
# circuit-sample2-labels.svg and the wiki's truth-table headings:
#   p = NOR(C, D)            "~(C+D)"
#   q = OR(p, NOT B)         "p + ~B"   (the q gate is an OR; s and t are XOR)
#   r = AND(NOT A, B)        "~A B"
#   s = r XOR q, t = s XOR p (the output)
WIKI_2_GATES = [
    "na = NOT(A)",
    "nb = NOT(B)",
    "p = NOR(C, D)",
    "q = OR(p, nb)",
    "r = AND(na, B)",
    "s = XOR(r, q)",
    "t = XOR(s, p)",
]
WIKI_2 = "INPUTS A B C D\n" + "\n".join(WIKI_2_GATES)

# The wiki's truth table, rows ABCD = 0000 .. 1111, one column per labelled gate.
# Source slip: the wiki's q column shows 1 in row 0110, where q = p + ~B = 0 + 0 = 0
# (p = ~(1 + 0) = 0, B = 1). Its s and t columns in that row (s = r ⊕ q = 1 ⊕ 0 = 1, t = 1)
# already use q = 0, so the slip is in the q cell only; the corrected column is pinned below.
WIKI_2_TABLE = {
    "p": "1000100010001000",
    "q": "1111100011111000",  # wiki prints 1111101011111000 (row 0110 slip)
    "r": "0000111100000000",
    "s": "1111011111111000",
    "t": "0111111101110000",
}


def test_wiki_sample_2_ten_true_rows():
    # "From the truth table, there are 10 rows where the final output is TRUE."
    assert circuit_eval.count(WIKI_2) == 10
    assert circuit_eval.count(WIKI_2, 0) == 6


@pytest.mark.parametrize("gate", ["p", "q", "r", "s", "t"])
def test_wiki_sample_2_every_gate_column(gate):
    # Cut the netlist after the gate, so it becomes the output, and compare with the wiki.
    upto = next(i for i, g in enumerate(WIKI_2_GATES) if g.startswith(gate + " "))
    netlist = "INPUTS A B C D\n" + "\n".join(WIKI_2_GATES[: upto + 1])
    assert _column(netlist) == WIKI_2_TABLE[gate]


def test_wiki_sample_2_false_rows():
    # The six FALSE rows of the wiki's t column: 0000, 1000, 1100, 1101, 1110, 1111.
    expected = "(0,0,0,0), (1,0,0,0), (1,1,0,0), (1,1,0,1), (1,1,1,0), (1,1,1,1)"
    assert circuit_eval.solutions(WIKI_2, 0) == expected


# Sample Problem 3 ("Simplify the Boolean expression that this circuit represents").
# Circuit-PB.png: A -> NOT; A and B -> OR; NOT(A) and the OR -> AND; B and C -> NOR; the AND
# and the NOR -> AND, the output. The wiki's translation: (~A(A+B)) * ~(B+C), which is 0.
WIKI_3 = """
    INPUTS A B C
    na = NOT(A)
    o = OR(A, B)
    x = AND(na, o)
    y = NOR(B, C)
    out = AND(x, y)
"""


def test_wiki_sample_3_simplifies_to_zero():
    assert circuit_eval.count(WIKI_3) == 0
    assert circuit_eval.solutions(WIKI_3) == "NONE"
    expr = circuit_eval.to_expression(WIKI_3)
    assert expr == "(~A * (A + B)) * ~(B + C)"
    assert bool_eval.minimal_sops(expr) == ["0"]


# ---------------------------------------------------------------- every gate's truth table

# Rows in ascending binary order: A = 0, 1 for one input; AB = 00, 01, 10, 11 for two.
GATE_COLUMNS = {
    "BUFFER": "01",
    "NOT": "10",
    "AND": "0001",
    "NAND": "1110",
    "OR": "0111",
    "NOR": "1000",
    "XOR": "0110",
    "XNOR": "1001",
}


@pytest.mark.parametrize("gate", list(GATE_COLUMNS))
def test_every_gate_truth_table(gate):
    if gate in ("BUFFER", "NOT"):
        netlist = f"INPUTS A\nout = {gate}(A)"
    else:
        netlist = f"INPUTS A B\nout = {gate}(A, B)"
    assert _column(netlist) == GATE_COLUMNS[gate]
    assert circuit_eval.count(netlist) == GATE_COLUMNS[gate].count("1")


@pytest.mark.parametrize(
    "gate, expr",
    [
        ("BUFFER", "A"),
        ("NOT", "~A"),
        ("AND", "A * B"),
        ("NAND", "~(A * B)"),
        ("OR", "A + B"),
        ("NOR", "~(A + B)"),
        ("XOR", "A ⊕ B"),
        ("XNOR", "A ⊙ B"),
    ],
)
def test_every_gate_expression(gate, expr):
    if gate in ("BUFFER", "NOT"):
        netlist = f"INPUTS A\nout = {gate}(A)"
    else:
        netlist = f"INPUTS A B\nout = {gate}(A, B)"
    assert circuit_eval.to_expression(netlist) == expr


# ---------------------------------------------------------------- the INPUTS line


def test_inputs_line_sets_columns_including_an_unused_input():
    # C is declared but feeds no gate: it is still the third column of every tuple.
    netlist = "INPUTS A B C\nout = AND(A, B)"
    assert circuit_eval.solutions(netlist) == "(1,1,0), (1,1,1)"
    assert circuit_eval.count(netlist) == 2
    assert circuit_eval.count(netlist, 0) == 6


def test_inputs_line_sets_column_order():
    # out = A AND NOT C over (A, B, C): rows 100 and 110.
    netlist = "INPUTS A B C\nnc = NOT(C)\nout = AND(nc, A)"
    assert circuit_eval.solutions(netlist) == "(1,0,0), (1,1,0)"
    # Over (A, B, C, D) the same function doubles its rows, D free.
    netlist4 = "INPUTS A B C D\nnc = NOT(C)\nout = AND(nc, A)"
    assert circuit_eval.solutions(netlist4) == "(1,0,0,0), (1,0,0,1), (1,1,0,0), (1,1,0,1)"


def test_solutions_none_and_all():
    always = "INPUTS A\nna = NOT(A)\nout = OR(A, na)"
    assert circuit_eval.solutions(always, 0) == "NONE"
    assert circuit_eval.solutions(always) == "(0), (1)"


def test_layout_is_free():
    tight = "INPUTS A B C\np=NAND(A,B)\nout=OR(p,C)"
    loose = "\n\n   INPUTS A B C  \n\n  p  =  NAND( A , B )\n  out = OR(p, C)   \n\n"
    for text in (tight, loose, WIKI_1):
        assert circuit_eval.solutions(text, 0) == "(1,1,0)"


def test_last_line_is_the_output():
    # The last gate is the output even when an earlier gate is not used by it.
    netlist = "INPUTS A B\nunused = XOR(A, B)\nout = AND(A, B)"
    assert _column(netlist) == "0001"


def test_nested_nots_and_buffer():
    # ~~A = A. The expression keeps both tildes (a negation is an atom).
    netlist = "INPUTS A B\nn1 = NOT(A)\nn2 = NOT(n1)\nb = BUFFER(n2)\nout = AND(b, B)"
    assert _column(netlist) == "0001"
    assert circuit_eval.to_expression(netlist) == "~~A * B"


def test_xnor_chain():
    # Hand: x = A ⊙ B is 1 when A = B; out = x ⊙ C is 1 when x = C.
    #   000: x=1, C=0 -> 0    001: x=1, C=1 -> 1    010: x=0, C=0 -> 1    011: x=0, C=1 -> 0
    #   100: x=0, C=0 -> 1    101: x=0, C=1 -> 0    110: x=1, C=0 -> 0    111: x=1, C=1 -> 1
    # Column 01101001 (1 when an odd number of inputs are 1), 4 TRUE rows.
    netlist = "INPUTS A B C\nx = XNOR(A, B)\nout = XNOR(x, C)"
    assert _column(netlist) == "01101001"
    assert circuit_eval.to_expression(netlist) == "(A ⊙ B) ⊙ C"


# ---------------------------------------------------------------- to_expression == evaluate

NAND_ONLY_OR = """
    INPUTS A B
    na = NAND(A, A)
    nb = NAND(B, B)
    out = NAND(na, nb)
"""

MIXED = """
    INPUTS A B C D
    p = NOR(A, B)
    q = NAND(C, p)
    r = XNOR(q, D)
    s = BUFFER(r)
    t = NOT(s)
    u = XOR(t, p)
    out = OR(u, A)
"""


def test_nand_only_or():
    # NAND(NAND(A,A), NAND(B,B)) = A + B.
    assert _column(NAND_ONLY_OR) == "0111"
    assert circuit_eval.to_expression(NAND_ONLY_OR) == "~(~(A * A) * ~(B * B))"


@pytest.mark.parametrize(
    "netlist",
    [WIKI_1, WIKI_2, WIKI_3, NAND_ONLY_OR, MIXED, "INPUTS A B C\nx = XNOR(A, B)\nout = XOR(x, C)"],
    ids=["wiki1", "wiki2", "wiki3", "nand_or", "mixed", "xnor_xor"],
)
def test_to_expression_agrees_with_evaluate(netlist):
    expr = circuit_eval.to_expression(netlist)
    for _, row in _rows(netlist):
        used = {v: row[v] for v in row if v in expr}
        assert bool_eval.evaluate(expr, used) == circuit_eval.evaluate(netlist, row)


def test_wiki_sample_2_expression_text():
    assert circuit_eval.to_expression(WIKI_2) == ("((~A * B) ⊕ (~(C + D) + ~B)) ⊕ ~(C + D)")
