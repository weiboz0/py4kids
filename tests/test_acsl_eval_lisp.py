"""Plan 094 A1: pre-written tests for unit 07's LISP evaluator (``assets/verify/lisp_eval.py``).

The evaluator's author implements this interface and does NOT edit this file:

``lisp_eval.run(program: str) -> str``
    ``program`` is one or more ACSL LISP expressions (whitespace/newlines between them; a
    ``(`` or ``)`` needs no surrounding space). They are evaluated in order in ONE fresh environment,
    so ``SET`` / ``SETQ`` bindings and ``DEF`` / ``DEFUN`` definitions persist to later
    expressions of the same call (never across calls). It returns the canonical text of the
    LAST expression's value:

    * a number: an integer when whole (``-2``, ``1024``), otherwise Python's decimal (``13.5``);
      ``DIV`` is true division
    * an atom: exactly as written in the program (case kept: ``CA``, ``This``, ``b``)
    * a list: ``(A B C)``, single spaces, nested lists the same way
    * the empty list and false: ``NIL`` (``()`` and ``NIL`` are the same value); true: ``true``

    Supported (ACSL's wiki set): quote ``'``; ``SET`` (first argument evaluated, normally quoted),
    ``SETQ`` (first argument taken as quoted), ``EVAL``, ``ATOM`` (true for atoms and NIL);
    ``CAR``, ``CDR`` (``CDR`` of a one-element list is ``NIL``), ``CONS`` (second argument a list),
    ``REVERSE`` (top level only); the compositions ``CAAR CADR CDAR CDDR CADDR CDDAR``; variadic
    ``ADD``/``+`` and ``MULT``/``*``; ``SUB``/``-``, ``DIV``/``/``, ``SQUARE``, ``EXP``;
    ``EQ`` (numbers or atoms), ``POS``, ``NEG``; ``DEF`` and ``DEFUN``
    (``(DEF NAME (p1 p2 ...) body)``, a space before the parameter list optional). Built-in
    function names are case-insensitive (CLISP, which ACSL uses: ``(car x)`` is legal).

Expected values are the ACSL wiki's (categories.acsl.org, "LISP"), or hand-computed where the
wiki gives none (each such case shows its working in a comment). Skips until the module exists.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

VERIFY_DIR = Path(__file__).resolve().parents[1] / "acsl/units/unit-07-lisp/assets/verify"
sys.path.insert(0, str(VERIFY_DIR))
lisp_eval = pytest.importorskip("lisp_eval")


def run(program: str) -> str:
    return lisp_eval.run(program)


# ---------------------------------------------------------------- the wiki's samples and tables


@pytest.mark.parametrize(
    "program, expected",
    [
        # Sample Problem 1
        ("(MULT (ADD 6 5 0) (MULT 5 1 2 2) (DIV 6 (SUB 2 5)))", "-440"),
        # Sample Problem 2 (note the ")(" with no space)
        ("(CDR '((2 (3))(4 (5 6) 7)))", "((4 (5 6) 7))"),
        # Sample Problem 3
        ("(SETQ X '(RI VA FL CA TX))\n(CAR (CDR (REVERSE X)))", "CA"),
        # Syntax section
        ("(MULT (ADD 2 3) (ADD 1 4 2))", "35"),
        # Arithmetic table
        ("(ADD (EXP 2 3) (SUB 4 1) (DIV 54 4))", "24.5"),
        ("(- (* 3 2) (- 12 (+ 1 2 1)))", "-2"),
        ("(ADD (SQUARE 3) (SQUARE 4))", "25"),
        # List table
        ("(CAR '(This is a list))", "This"),
        ("(CDR '(This is a list))", "(is a list)"),
        ("(CONS 'red '(white blue))", "(red white blue)"),
    ],
)
def test_wiki_single_expressions(program, expected):
    assert run(program) == expected


SET_TABLE = [
    ("(SET 'a (MULT 2 3))", "6"),
    ("(SET 'a '(MULT 2 3))", "(MULT 2 3)"),
    ("(SET 'b 'a)", "a"),
    ("(SET 'c a)", "(MULT 2 3)"),
    ("(SETQ EX (ADD 3 (MULT 2 5)))", "13"),
    ("(SETQ VOWELS '(A E I O U))", "(A E I O U)"),
]


@pytest.mark.parametrize("row", range(len(SET_TABLE)))
def test_wiki_set_setq_table(row):
    # each row is the value of its statement after the rows above it have run
    program = "\n".join(statement for statement, _ in SET_TABLE[: row + 1])
    assert run(program) == SET_TABLE[row][1]


EVAL_Z = [
    ("(SETQ z '(ADD 2 3))", "(ADD 2 3)"),
    ("(EVAL 'z)", "(ADD 2 3)"),
    ("(EVAL z)", "5"),
    ("(CAR z)", "ADD"),  # "the binding of the atom z has not changed"
]


@pytest.mark.parametrize("row", range(len(EVAL_Z)))
def test_wiki_eval_example(row):
    program = "\n".join(statement for statement, _ in EVAL_Z[: row + 1])
    assert run(program) == EVAL_Z[row][1]


ATOM_TABLE = [
    ("(SETQ p '(ADD 1 2 3 4))", "(ADD 1 2 3 4)"),
    ("(ATOM 'p)", "true"),
    ("(ATOM p)", "NIL"),
    ("(EVAL p)", "10"),
]


@pytest.mark.parametrize("row", range(len(ATOM_TABLE)))
def test_wiki_atom_table(row):
    program = "\n".join(statement for statement, _ in ATOM_TABLE[: row + 1])
    assert run(program) == ATOM_TABLE[row][1]


LIST_Z = "(SETQ z (CONS '(red white blue) (CDR '(This is a list))))"


@pytest.mark.parametrize(
    "tail, expected",
    [
        ("", "((red white blue) is a list)"),
        ("(REVERSE z)", "(list a is (red white blue))"),
        ("(CDDAR z)", "(blue)"),  # the wiki's composition example
    ],
)
def test_wiki_list_table(tail, expected):
    assert run(f"{LIST_Z}\n{tail}") == expected


WHAT_SECOND = (
    "(SETQ X '(a c s l))\n"
    "(DEF WHAT(args) (CONS args (REVERSE (CDR args))))\n"
    "(DEF SECOND(args) (CONS (CAR (CDR args)) NIL))\n"
)


@pytest.mark.parametrize(
    "call, expected",
    [
        ("(WHAT X)", "((a c s l) l s c)"),
        ("(SECOND X)", "(c)"),
        ("(SECOND (WHAT X))", "(l)"),
        ("(WHAT (SECOND X))", "((c))"),
    ],
)
def test_wiki_def_what_second(call, expected):
    assert run(WHAT_SECOND + call) == expected


def test_wiki_def_second_single_parameter():
    assert run("(DEF SECOND (args) (CAR (CDR args)))\n(SECOND '(a b c d e))") == "b"


def test_wiki_defun_hy_fy():
    # the wiki's (commented-out) Problem 4
    program = (
        "(DEFUN HY(PARM) (REVERSE (CDR PARM)))\n"
        "(DEFUN FY(PARM) (CAR (HY (CDR PARM))))\n"
        "(FY '(DO RE (MI FA) SO))"
    )
    assert run(program) == "SO"


# ---------------------------------------------------------------- one case per operation


@pytest.mark.parametrize(
    "program, expected",
    [
        # SET: first argument evaluated -> 'a; the binding is then used
        ("(SET 'a 6)\n(ADD a 1)", "7"),
        # SET with a non-quoted first argument whose value is an atom (b -> n): binds n
        ("(SET 'b 'n)\n(SET b 4)\n(MULT n 2)", "8"),
        # SETQ: first argument taken as quoted; rebinding replaces the old value
        ("(SETQ k 2)\n(SETQ k (ADD k 3))\n(SQUARE k)", "25"),  # k = 5, 5*5
        # EVAL of a quoted expression
        ("(EVAL '(SUB 10 4))", "6"),
        # CAR / CDR
        ("(CAR '((a b) c))", "(a b)"),
        ("(CDR '(a))", "NIL"),  # CDR of a one-element list
        ("(CDR '(23 (this is easy) hello 821))", "((this is easy) hello 821)"),
        # CONS: a list as first argument nests; onto NIL / () makes a one-element list
        ("(CONS '(a) '(b))", "((a) b)"),
        ("(CONS 'a NIL)", "(a)"),
        ("(CONS 'a ())", "(a)"),
        ("(CONS 5 '(6 7))", "(5 6 7)"),
        # REVERSE: top level only
        ("(REVERSE '(1 (2 3) 4))", "(4 (2 3) 1)"),
        # ADD / MULT are variadic
        ("(ADD 1 2 3 4 5)", "15"),
        ("(MULT 2 3 4)", "24"),
        # SUB / DIV
        ("(SUB 2 5)", "-3"),
        ("(DIV 54 4)", "13.5"),
        ("(DIV 6 (SUB 2 5))", "-2"),
        ("(DIV 1 4)", "0.25"),
        ("(MULT (DIV 5 2) 2)", "5"),  # 2.5 * 2 = 5.0 -> whole -> 5
        # SQUARE / EXP
        ("(SQUARE -4)", "16"),
        ("(EXP 2 10)", "1024"),
        ("(EXP 5 0)", "1"),
        # symbol forms + - * /
        ("(+ 1 2 3)", "6"),
        ("(- 10 4)", "6"),
        ("(* 2 3 4)", "24"),
        ("(/ 10 4)", "2.5"),
        # EQ
        ("(EQ (ADD 1 2) 3)", "true"),
        ("(EQ 2 3)", "NIL"),
        ("(EQ 'a 'a)", "true"),
        # POS / NEG (zero is neither)
        ("(POS 5)", "true"),
        ("(POS 0)", "NIL"),
        ("(NEG -3)", "true"),
        ("(NEG 0)", "NIL"),
        # ATOM: numbers, quoted atoms and NIL are atoms; a quoted list is not
        ("(ATOM 5)", "true"),
        ("(ATOM '(1 2))", "NIL"),
        ("(ATOM NIL)", "true"),
        # quote: a quoted list is returned unevaluated
        ("'(ADD 1 2)", "(ADD 1 2)"),
        ("(CAR '(ADD 1 2))", "ADD"),
        # NIL and () are the same value
        ("NIL", "NIL"),
        ("()", "NIL"),
        ("(REVERSE NIL)", "NIL"),
        ("(CONS NIL '(a))", "(NIL a)"),
        # built-in names are case-insensitive (CLISP)
        ("(car (cdr '(x y z)))", "y"),
    ],
)
def test_each_operation(program, expected):
    assert run(program) == expected


def test_def_separately():
    assert run("(DEF TWICE (n) (MULT n 2))\n(TWICE 21)") == "42"


def test_defun_separately_with_two_parameters():
    # (3 + 4) / 2 = 3.5
    assert run("(DEFUN AVG (A B) (DIV (ADD A B) 2))\n(AVG 3 4)") == "3.5"


def test_defun_parameters_do_not_clobber_globals():
    # A is 100 globally; AVG's parameter A is 3 only during the call
    program = "(SETQ A 100)\n(DEFUN AVG (A B) (DIV (ADD A B) 2))\n(AVG 3 4)\n(ADD A 0)"
    assert run(program) == "100"


def test_defun_calls_another_user_function():
    # SQ 3 = 9; SUMSQ 3 4 = 9 + 16 = 25
    program = (
        "(DEFUN SQ (N) (MULT N N))\n"
        "(DEFUN SUMSQ (X Y) (ADD (SQ X) (SQ Y)))\n"
        "(SUMSQ 3 4)"
    )
    assert run(program) == "25"


# ---------------------------------------------------------------- CxR compositions

Z = "(SETQ z '((red white blue) is a list))\n"  # the wiki's z, bound directly


@pytest.mark.parametrize(
    "composition, expected",
    [
        ("CAAR", "red"),  # CAR (CAR z) = CAR (red white blue)
        ("CADR", "is"),  # CAR (CDR z) = CAR (is a list)
        ("CDAR", "(white blue)"),  # CDR (CAR z) = CDR (red white blue)
        ("CDDR", "(a list)"),  # CDR (CDR z) = CDR (is a list)
        ("CADDR", "a"),  # CAR (CDR (CDR z)) = CAR (a list)
        ("CDDAR", "(blue)"),  # CDR (CDR (CAR z)) = CDR (white blue)
    ],
)
def test_each_composition(composition, expected):
    assert run(f"{Z}({composition} z)") == expected


def test_composition_equals_its_expansion():
    assert run(f"{Z}(CADDR z)") == run(f"{Z}(CAR (CDR (CDR z)))")


def test_cddr_of_a_two_element_list_is_nil():
    assert run("(CDDR '(a b))") == "NIL"
