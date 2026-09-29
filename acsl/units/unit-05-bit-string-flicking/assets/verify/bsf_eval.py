"""Verification helper for unit 05: an ACSL bit-string expression evaluator.

Used only by ``verify`` cells in ``solutions.ipynb`` (and ``tests/test_acsl_eval_bsf.py``).

- ``evaluate(expr)`` returns the result bit string of an ACSL bit-string expression.
- ``solve(expr_with_x, result, width)`` brute-forces every ``width``-bit x giving ``result``.

Rules (ACSL "Bit-String Flicking"): precedence NOT > shift/circulate > AND > XOR > OR;
equal-precedence binary operators go left to right; unary operators bind right to left;
a binary operator pads the shorter operand with 0s on the left; circulate counts are taken
mod the length; a shift by the length or more clears the string.
"""

from __future__ import annotations

import re

_TOKEN = re.compile(
    r"\s*(?:(?P<shift>(?:LSHIFT|RSHIFT|LCIRC|RCIRC)-\d+)"
    r"|(?P<word>NOT|AND|OR|XOR)(?![A-Za-z0-9])"
    r"|(?P<sym>[()~¬&|⊕])"
    r"|(?P<bits>[01]+)"
    r"|(?P<var>x)(?![A-Za-z0-9]))",
    re.IGNORECASE,
)

_BINARY = {"AND": "AND", "&": "AND", "OR": "OR", "|": "OR", "XOR": "XOR", "⊕": "XOR"}
_LEVELS = ("OR", "XOR", "AND")  # lowest to highest binary precedence


def _tokenize(expr: str) -> list[str]:
    tokens: list[str] = []
    pos = 0
    text = expr.rstrip()
    while pos < len(text):
        m = _TOKEN.match(text, pos)
        if not m or m.end() == pos:
            raise ValueError(f"cannot read {text[pos:]!r}")
        pos = m.end()
        if m.group("shift"):
            tokens.append(m.group("shift").upper())
        elif m.group("word"):
            tokens.append(m.group("word").upper())
        elif m.group("var"):
            tokens.append("x")
        else:
            tokens.append(m.group(m.lastgroup))
    return tokens


def _pad(a: str, b: str) -> tuple[str, str]:
    width = max(len(a), len(b))
    return a.rjust(width, "0"), b.rjust(width, "0")


def _binary(op: str, a: str, b: str) -> str:
    a, b = _pad(a, b)
    out = []
    for p, q in zip(a, b):
        if op == "AND":
            out.append("1" if p == q == "1" else "0")
        elif op == "OR":
            out.append("1" if "1" in (p, q) else "0")
        else:
            out.append("1" if p != q else "0")
    return "".join(out)


def _unary(op: str, bits: str) -> str:
    n = len(bits)
    if op == "NOT":
        return "".join("1" if c == "0" else "0" for c in bits)
    name, count = op.split("-")
    k = int(count)
    if name == "LSHIFT":
        k = min(k, n)
        return bits[k:] + "0" * k
    if name == "RSHIFT":
        k = min(k, n)
        return "0" * k + bits[: n - k]
    k %= n
    if name == "LCIRC":
        return bits[k:] + bits[:k]
    return bits[n - k:] + bits[: n - k]  # RCIRC


class _Parser:
    def __init__(self, tokens: list[str], x: str | None):
        self.tokens = tokens
        self.pos = 0
        self.x = x

    def peek(self) -> str | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def take(self) -> str:
        tok = self.peek()
        if tok is None:
            raise ValueError("unexpected end of expression")
        self.pos += 1
        return tok

    def binary(self, level: int) -> str:
        if level == len(_LEVELS):
            return self.unary()
        left = self.binary(level + 1)
        while _BINARY.get(self.peek() or "") == _LEVELS[level]:
            self.take()
            right = self.binary(level + 1)
            left = _binary(_LEVELS[level], left, right)
        return left

    def unary(self) -> str:
        tok = self.peek()
        if tok in ("NOT", "~", "¬"):
            self.take()
            return _unary("NOT", self.unary())
        if tok is not None and "-" in tok:
            self.take()
            return _unary(tok, self.unary())
        return self.primary()

    def primary(self) -> str:
        tok = self.take()
        if tok == "(":
            value = self.binary(0)
            if self.take() != ")":
                raise ValueError("missing )")
            return value
        if tok == "x":
            if self.x is None:
                raise ValueError("x has no value")
            return self.x
        if set(tok) <= {"0", "1"}:
            return tok
        raise ValueError(f"unexpected token {tok!r}")


def evaluate(expr: str, x: str | None = None) -> str:
    """Evaluate an ACSL bit-string expression (optionally with a value for ``x``)."""
    parser = _Parser(_tokenize(expr), x)
    value = parser.binary(0)
    if parser.peek() is not None:
        raise ValueError(f"unexpected token {parser.peek()!r}")
    return value


def solve(expr_with_x: str, result: str, width: int) -> list[str]:
    """Every ``width``-bit x (ascending) for which the expression evaluates to ``result``."""
    answers = []
    for value in range(2**width):
        x = format(value, f"0{width}b")
        if evaluate(expr_with_x, x) == result:
            answers.append(x)
    return answers
