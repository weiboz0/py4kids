"""Plan 096 A1: pre-written tests for unit 15's assembly evaluator (``assets/verify/asm_eval.py``).

The evaluator's author implements this interface and does NOT edit this file.

``asm_eval.run(program: str, inputs=()) -> dict``
    Runs an ACSL assembly program and returns
    ``{"memory": {label: int}, "printed": [int, ...], "acc": [int, ...]}``:

    * ``memory``: the final value of every data location -- every ``DC`` label, plus every label
      a ``STORE`` or ``READ`` wrote to. A location nothing defined or wrote is absent. Branch
      targets (labels on other instructions) are not memory.
    * ``printed``: the values ``PRINT`` printed, in order.
    * ``acc``: the ACC after each EXECUTED ``LOAD``, ``ADD``, ``SUB``, ``MULT`` and ``DIV`` (the
      instructions that write the ACC), one entry per execution, even when the value is unchanged.

    ``inputs`` is a sequence of integers that ``READ`` consumes in order.

**Line parsing.** ``program`` is text with one instruction per line (statements show programs as
fixed-width code blocks, pasted byte-identical). Blank lines are ignored. Each line is split on
whitespace into tokens. The first token is a LABEL exactly when it is not an opcode (the wiki
forbids opcodes as labels), so ``DONE END`` is a labelled ``END`` and ``LOAD B`` is an
unlabelled ``LOAD`` with ``LOC`` ``B``. The next token is the opcode (uppercase), and the next,
if any, is ``LOC``. Labels are case-sensitive.

**Opcodes** (the wiki's reference manual). ``LOC`` is a label or, for the starred opcodes only,
immediate data ``=value`` (a signed integer, ``=1``, ``=-5``):

* ``*LOAD``: ACC = contents of LOC. ``STORE``: LOC = ACC (ACC unchanged).
* ``*ADD``, ``*SUB``, ``*MULT``: ACC = ACC + LOC, ACC - LOC, ACC * LOC, then reduced by the
  modulo rule below.
* ``*DIV``: "The contents of LOC are divided INTO the contents of the ACC": ACC = ACC ÷ LOC,
  keeping the signed integer part, i.e. rounding TOWARD ZERO (``-7 DIV 2`` is ``-3``, not
  Python's ``-7 // 2 == -4``). Division by zero raises ``ZeroDivisionError``.
* ``BE``, ``BG``, ``BL``: jump to the instruction labelled LOC when ACC = 0, > 0, < 0; ``BU``
  jumps always. Otherwise execution continues with the next line.
* ``READ``: LOC = the next value of ``inputs``, reduced by the modulo rule.
  ``PRINT``: append the contents of LOC to ``printed``.
* ``DC``: ``LABEL DC value`` defines the location LABEL holding ``value`` before execution
  starts; reaching a ``DC`` line during execution does nothing.
* ``END``: stop.

A ``STORE`` or ``READ`` to a label with no ``DC`` creates that location (the wiki's ``N!``
sample does both). Execution starts at the first line; ACC starts at 0.

**The modulo rule** (a book convention for negative values). The wiki says ``ADD``, ``SUB``,
``MULT`` and ``READ`` work "modulo 1,000,000". The book keeps the sign and the last six digits:
a true result ``v`` becomes ``sign(v) * (abs(v) % 1_000_000)``. So ``999999 + 1`` is ``0``,
``-999999 - 2`` is ``-1``, and ``-1234 * 1000`` is ``-234000``. No item assesses it; every value
an item's program produces stays within ±999,999.

**Step limit.** A run that would execute more than 100,000 instructions raises
``RuntimeError`` instead of looping forever.

Sources: the ACSL wiki "Assembly Language Programming" page (categories.acsl.org, retrieved
2026-09-29) for the two samples and the semantics; hand-computed traces otherwise (working in
comments). Every expected value was re-checked against an independent throwaway interpreter.
Skips until the module exists.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

VERIFY_DIR = (
    Path(__file__).resolve().parents[1] / "acsl/units/unit-15-assembly-language/assets/verify"
)
sys.path.insert(0, str(VERIFY_DIR))
asm_eval = pytest.importorskip("asm_eval")


# ---------------------------------------------------------------- the wiki's samples

WIKI_1 = """\
TEMP  DC    0
A     DC    8
B     DC    -2
C     DC    3
      LOAD  B
      MULT  C
      ADD   A
      DIV   B
      SUB   A
      STORE TEMP
      END
"""


def test_wiki_sample_1_temp_is_minus_9():
    # "The ACC takes on values -2, -6, 2, -1, and -9 in that order. The last value, -9, is
    # stored in location TEMP." (DIV: 2 divided by -2 is -1.)
    result = asm_eval.run(WIKI_1)
    assert result["acc"] == [-2, -6, 2, -1, -9]
    assert result["memory"] == {"TEMP": -9, "A": 8, "B": -2, "C": 3}
    assert result["printed"] == []


# Problem 2: "If the following program has an input value of N, what is the final value of X
# ... X = N!". X and A have no DC: READ creates X and STORE creates A.
WIKI_2 = """\
      READ  X
      LOAD  X
TOP   SUB   =1
      BE    DONE
      STORE A
      MULT  X
      STORE X
      LOAD  A
      BU    TOP
DONE  END
"""


@pytest.mark.parametrize("n, fact", [(2, 2), (3, 6), (4, 24), (5, 120), (6, 720), (9, 362880)])
def test_wiki_sample_2_factorial(n, fact):
    # "For example, 5! = 5 * 4 * 3 * 2 * 1 = 120."
    result = asm_eval.run(WIKI_2, [n])
    assert result["memory"]["X"] == fact
    assert result["memory"]["A"] == 1  # the last A stored before ACC reaches 0
    assert result["printed"] == []


def test_wiki_sample_2_trace_for_3():
    # Hand, N = 3: LOAD X -> 3; SUB -> 2; (STORE A=2) MULT X -> 6; (STORE X=6) LOAD A -> 2;
    # SUB -> 1; (A=1) MULT X -> 6; (X=6) LOAD A -> 1; SUB -> 0; BE DONE.
    assert asm_eval.run(WIKI_2, [3])["acc"] == [3, 2, 6, 2, 1, 6, 1, 0]


def test_wiki_sample_2_labels_created_only_when_written():
    # N = 1: READ creates X = 1; LOAD 1; SUB -> 0; BE DONE at once, so STORE A never runs and A
    # never exists.
    result = asm_eval.run(WIKI_2, [1])
    assert result["memory"] == {"X": 1}


def test_wiki_sample_2_ten_factorial_wraps():
    # 10! = 3,628,800. Hand, X after each MULT: 90, 720, 5040, 30240, 151200, 604800,
    # 1814400 -> 814400, 814400 * 2 = 1628800 -> 628800, * 1 = 628800.
    assert asm_eval.run(WIKI_2, [10])["memory"]["X"] == 628800


# ---------------------------------------------------------------- each opcode


def test_load_and_store():
    prog = """\
X     DC    41
      LOAD  X
      STORE Y
      LOAD  =7
      STORE X
      END
"""
    result = asm_eval.run(prog)
    assert result["memory"] == {"X": 7, "Y": 41}
    assert result["acc"] == [41, 7]


def test_add_sub_mult_with_labels_and_immediate():
    prog = """\
X     DC    5
      LOAD  =10
      ADD   X
      ADD   =-3
      SUB   X
      SUB   =4
      MULT  X
      MULT  =-2
      STORE R
      END
"""
    # 10, +5 = 15, -3 = 12, -5 = 7, -4 = 3, *5 = 15, *-2 = -30.
    result = asm_eval.run(prog)
    assert result["acc"] == [10, 15, 12, 7, 3, 15, -30]
    assert result["memory"]["R"] == -30
    assert result["memory"]["X"] == 5  # LOC is unchanged by arithmetic


@pytest.mark.parametrize(
    "acc, loc, quotient",
    [
        (20, 6, 3),  # ACC / LOC, not LOC / ACC (6 / 20 would be 0)
        (-7, 2, -3),  # toward zero; floor would give -4
        (7, -2, -3),
        (-7, -2, 3),
        (7, 2, 3),
        (6, 3, 2),
        (-6, 3, -2),
        (1, 5, 0),
        (-1, 5, 0),
    ],
)
def test_div_operand_order_and_toward_zero(acc, loc, quotient):
    immediate = f"      LOAD  ={acc}\n      DIV   ={loc}\n      END\n"
    assert asm_eval.run(immediate)["acc"] == [acc, quotient]
    labelled = f"D     DC    {loc}\n      LOAD  ={acc}\n      DIV   D\n      STORE Q\n      END\n"
    assert asm_eval.run(labelled)["memory"]["Q"] == quotient


def test_div_by_zero_raises():
    with pytest.raises(ZeroDivisionError):
        asm_eval.run("      LOAD  =5\n      DIV   =0\n      END\n")
    with pytest.raises(ZeroDivisionError):
        asm_eval.run("Z     DC    0\n      LOAD  =5\n      DIV   Z\n      END\n")


def test_read_and_print():
    prog = """\
      READ  A
      READ  B
      LOAD  A
      SUB   B
      STORE D
      PRINT D
      PRINT A
      END
"""
    result = asm_eval.run(prog, [12, 30])
    assert result["printed"] == [-18, 12]
    assert result["memory"] == {"A": 12, "B": 30, "D": -18}
    assert result["acc"] == [12, -18]  # READ, STORE and PRINT leave ACC alone


def test_read_creates_a_label_and_dc_is_a_no_op_mid_program():
    prog = """\
      READ  N
      LOAD  N
      ADD   K
K     DC    100
      STORE N
      END
"""
    # K is defined before execution (100); reaching its line does nothing.
    result = asm_eval.run(prog, [5])
    assert result["memory"] == {"N": 105, "K": 100}
    assert result["acc"] == [5, 105]


# The same classifier with its tests in two orders, so each branch is seen both taken and not
# taken: prints 1 for a positive input, 0 for zero, -1 for a negative one.
CLASSIFY_GEL = """\
ONE   DC    1
ZERO  DC    0
NEG   DC    -1
      READ  N
      LOAD  N
      BG    POS
      BE    ZER
      BL    MIN
      END
POS   PRINT ONE
      BU    DONE
ZER   PRINT ZERO
      BU    DONE
MIN   PRINT NEG
DONE  END
"""

CLASSIFY_LEG = """\
ONE   DC    1
ZERO  DC    0
NEG   DC    -1
      READ  N
      LOAD  N
      BL    MIN
      BE    ZER
      BG    POS
      PRINT N
      END
POS   PRINT ONE
      BU    DONE
ZER   PRINT ZERO
      BU    DONE
MIN   PRINT NEG
DONE  END
"""


@pytest.mark.parametrize("prog", [CLASSIFY_GEL, CLASSIFY_LEG], ids=["BG-BE-BL", "BL-BE-BG"])
@pytest.mark.parametrize("n, printed", [(5, [1]), (0, [0]), (-5, [-1]), (999999, [1])])
def test_each_branch(prog, n, printed):
    assert asm_eval.run(prog, [n])["printed"] == printed


def test_bu_skips_code_and_loops():
    # Count down from 3, printing each value: BU jumps back; BE leaves the loop.
    prog = """\
      READ  I
TOP   LOAD  I
      BE    OUT
      PRINT I
      SUB   =1
      STORE I
      BU    TOP
      PRINT I
OUT   END
"""
    result = asm_eval.run(prog, [3])
    assert result["printed"] == [3, 2, 1]
    assert result["memory"]["I"] == 0


def test_end_stops_before_later_lines():
    prog = "      LOAD  =1\n      END\n      LOAD  =2\n"
    assert asm_eval.run(prog)["acc"] == [1]


# ---------------------------------------------------------------- line parsing


def test_labelled_end_versus_unlabelled_load():
    # "DONE END": DONE is not an opcode, so it is a label on END. "LOAD B": LOAD is an opcode, so
    # the line has no label and B is its LOC. A label may even be the same letter as a LOC.
    prog = """\
B     DC    4
      LOAD  B
      BU    DONE
      LOAD  =99
DONE  END
"""
    result = asm_eval.run(prog)
    assert result["acc"] == [4]
    assert result["memory"] == {"B": 4}


def test_whitespace_layout_is_free():
    tight = "X DC 2\nLOAD X\nMULT =3\nSTORE Y\nEND"
    tabs = "X\tDC\t2\n\tLOAD\tX\n\n\tMULT\t=3\n\tSTORE\tY\n\tEND\n"
    for prog in (tight, tabs):
        assert asm_eval.run(prog)["memory"] == {"X": 2, "Y": 6}


def test_labels_are_case_sensitive():
    prog = "x     DC    1\nX     DC    2\n      LOAD  x\n      STORE y\n      END\n"
    assert asm_eval.run(prog)["memory"] == {"x": 1, "X": 2, "y": 1}


# ---------------------------------------------------------------- the book's modulo rule


@pytest.mark.parametrize(
    "prog, expected",
    [
        ("      LOAD  =999999\n      ADD   =1\n      END\n", 0),  # 1,000,000 -> 0
        ("      LOAD  =-999999\n      SUB   =2\n      END\n", -1),  # -1,000,001 -> -1
        ("      LOAD  =1000\n      MULT  =1000\n      END\n", 0),  # 1,000,000 -> 0
        ("      LOAD  =-1234\n      MULT  =1000\n      END\n", -234000),  # -1,234,000
        ("      LOAD  =999999\n      ADD   =2\n      END\n", 1),  # 1,000,001 -> 1
        ("      LOAD  =-5\n      SUB   =999999\n      END\n", -4),  # -1,000,004 -> -4
        ("      LOAD  =999\n      MULT  =-1001\n      END\n", -999999),  # -999,999 stays
        ("      LOAD  =123456\n      MULT  =10\n      END\n", 234560),  # 1,234,560
    ],
)
def test_modulo_rule_at_the_boundaries(prog, expected):
    assert asm_eval.run(prog)["acc"][-1] == expected


def test_read_is_reduced_by_the_modulo_rule():
    prog = "      READ  X\n      READ  Y\n      PRINT X\n      PRINT Y\n      END\n"
    result = asm_eval.run(prog, [1000005, -2000017])
    assert result["printed"] == [5, -17]
    assert result["memory"] == {"X": 5, "Y": -17}


# ---------------------------------------------------------------- the step limit


def test_step_limit_on_an_endless_loop():
    with pytest.raises(RuntimeError):
        asm_eval.run("TOP   BU    TOP\n      END\n")


def test_step_limit_on_the_factorial_program_with_zero():
    # N = 0: ACC goes 0, -1 (never 0 at BE), and the loop counts down about 7 instructions per
    # pass; ACC would reach 0 again only after ~1,000,000 passes, far past 100,000 steps.
    with pytest.raises(RuntimeError):
        asm_eval.run(WIKI_2, [0])


def test_long_but_finite_run_is_allowed():
    # 5,000 passes of a 5-instruction loop (about 25,000 steps) stays under the limit.
    prog = """\
      READ  I
TOP   LOAD  I
      BE    OUT
      SUB   =1
      STORE I
      BU    TOP
OUT   END
"""
    assert asm_eval.run(prog, [5000])["memory"]["I"] == 0
