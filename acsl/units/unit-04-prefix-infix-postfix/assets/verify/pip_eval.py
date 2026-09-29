"""Prefix/infix/postfix verification helper for unit 04 (plan 094).

Imported only by `verify` cells in solutions.ipynb; exempt from source-policy.
Interface documented in tests/test_acsl_eval_pip.py.
"""

from __future__ import annotations

from fractions import Fraction

OPS = {"+", "-", "*", "/", "↑", "="}
PREC = {"=": 0, "+": 1, "-": 1, "*": 2, "/": 2, "↑": 3}


def _norm(tok: str) -> str:
    if tok == "^":
        return "↑"
    if tok in ("–", "−"):
        return "-"
    return tok


def _split(expr: str) -> list[str]:
    return [_norm(t) for t in expr.split()]


def _fmt(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return str(value.numerator / value.denominator)


def _apply(op: str, a: Fraction, b: Fraction) -> Fraction:
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        return a / b
    if op == "↑":
        if b.denominator != 1:
            raise ValueError("non-integer exponent")
        return a ** b.numerator
    raise ValueError(f"cannot evaluate operator {op!r}")


def evaluate_postfix(expr: str) -> str:
    stack: list[Fraction] = []
    for tok in _split(expr):
        if tok in OPS:
            b = stack.pop()
            a = stack.pop()
            stack.append(_apply(tok, a, b))
        else:
            stack.append(Fraction(int(tok)))
    if len(stack) != 1:
        raise ValueError("malformed postfix expression")
    return _fmt(stack[0])


def evaluate_prefix(expr: str) -> str:
    stack: list[Fraction] = []
    for tok in reversed(_split(expr)):
        if tok in OPS:
            a = stack.pop()
            b = stack.pop()
            stack.append(_apply(tok, a, b))
        else:
            stack.append(Fraction(int(tok)))
    if len(stack) != 1:
        raise ValueError("malformed prefix expression")
    return _fmt(stack[0])


def _tokenize_infix(infix: str) -> list[str]:
    tokens: list[str] = []
    i = 0
    while i < len(infix):
        ch = infix[i]
        if ch.isspace():
            i += 1
        elif ch.isdigit():
            j = i
            while j < len(infix) and infix[j].isdigit():
                j += 1
            tokens.append(infix[i:j])
            i = j
        elif ch.isalpha():
            j = i
            while j < len(infix) and infix[j].isalnum():
                j += 1
            tokens.append(infix[i:j])
            i = j
        else:
            tok = _norm(ch)
            if tok not in OPS and tok not in "()":
                raise ValueError(f"unexpected character {ch!r}")
            tokens.append(tok)
            i += 1
    return tokens


def _infix_tree(infix: str):
    """Shunting-yard to a tree: leaves are str, nodes are (op, left, right)."""
    out: list = []
    ops: list[str] = []

    def reduce() -> None:
        op = ops.pop()
        right = out.pop()
        left = out.pop()
        out.append((op, left, right))

    for tok in _tokenize_infix(infix):
        if tok == "(":
            ops.append(tok)
        elif tok == ")":
            while ops[-1] != "(":
                reduce()
            ops.pop()
        elif tok in OPS:
            # all operators left-associative (equal precedence left to right)
            while ops and ops[-1] != "(" and PREC[ops[-1]] >= PREC[tok]:
                reduce()
            ops.append(tok)
        else:
            out.append(tok)
    while ops:
        reduce()
    if len(out) != 1:
        raise ValueError("malformed infix expression")
    return out[0]


def _pre(tree) -> list[str]:
    if isinstance(tree, str):
        return [tree]
    op, left, right = tree
    return [op] + _pre(left) + _pre(right)


def _post(tree) -> list[str]:
    if isinstance(tree, str):
        return [tree]
    op, left, right = tree
    return _post(left) + _post(right) + [op]


def _full(tree) -> str:
    if isinstance(tree, str):
        return tree
    op, left, right = tree
    return "(" + _full(left) + op + _full(right) + ")"


def _tree_from_prefix(expr: str):
    stack: list = []
    for tok in reversed(_split(expr)):
        if tok in OPS:
            left = stack.pop()
            right = stack.pop()
            stack.append((tok, left, right))
        else:
            stack.append(tok)
    if len(stack) != 1:
        raise ValueError("malformed prefix expression")
    return stack[0]


def _tree_from_postfix(expr: str):
    stack: list = []
    for tok in _split(expr):
        if tok in OPS:
            right = stack.pop()
            left = stack.pop()
            stack.append((tok, left, right))
        else:
            stack.append(tok)
    if len(stack) != 1:
        raise ValueError("malformed postfix expression")
    return stack[0]


def to_prefix(infix: str) -> str:
    return " ".join(_pre(_infix_tree(infix)))


def to_postfix(infix: str) -> str:
    return " ".join(_post(_infix_tree(infix)))


def prefix_to_postfix(expr: str) -> str:
    return " ".join(_post(_tree_from_prefix(expr)))


def postfix_to_prefix(expr: str) -> str:
    return " ".join(_pre(_tree_from_postfix(expr)))


def prefix_to_infix(expr: str) -> str:
    return _full(_tree_from_prefix(expr))


def postfix_to_infix(expr: str) -> str:
    return _full(_tree_from_postfix(expr))
