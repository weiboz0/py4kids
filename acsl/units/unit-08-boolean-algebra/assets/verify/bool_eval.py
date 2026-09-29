"""Verification helper for unit 08: a Boolean-expression evaluator in the book's notation.

Used only by ``verify`` cells in ``solutions.ipynb`` (and ``tests/test_acsl_eval_bool.py``).

Notation: single capital letters are variables, ``1`` and ``0`` are TRUE and FALSE,
``~`` NOT (applies to the variable, constant or bracket right after it, and may repeat),
``*`` AND, ``⊕`` XOR, ``⊙`` XNOR, ``+`` OR, and ``( )`` group.
Precedence, highest first: ``~``; ``*``; ``⊕`` and ``⊙`` (one level); ``+``.
Equal-precedence operators group left to right.

- ``evaluate(expr, values)`` gives the value (0 or 1) for one row.
- ``solutions(expr, value=1)`` gives the rows where ``expr`` equals ``value`` as tuple text.
- ``count(expr, value=1)`` counts those rows.
- ``equivalent(a, b)`` compares full truth tables over both expressions' variables.
- ``column(expr)`` gives the result column, rows in ascending binary order.
- ``minimal_sops(expr)`` gives every minimal sum of products, in canonical text.
"""

from __future__ import annotations

from itertools import combinations, product

_BINARY = {"*": 3, "⊕": 2, "⊙": 2, "+": 1}  # binding power of each binary operator


def _tokenize(expr: str) -> list[str]:
    tokens: list[str] = []
    for ch in expr:
        if ch.isspace():
            continue
        if ch.isupper() or ch in "01~()" or ch in _BINARY:
            tokens.append(ch)
        else:
            raise ValueError(f"unexpected character {ch!r} in {expr!r}")
    return tokens


class _Parser:
    def __init__(self, expr: str) -> None:
        self.tokens = _tokenize(expr)
        self.pos = 0

    def peek(self) -> str | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def take(self) -> str:
        tok = self.peek()
        if tok is None:
            raise ValueError("unexpected end of expression")
        self.pos += 1
        return tok

    def parse(self):
        tree = self.binary(1)
        if self.peek() is not None:
            raise ValueError(f"unexpected {self.peek()!r}")
        return tree

    def binary(self, level: int):
        if level > 3:
            return self.unary()
        left = self.binary(level + 1)
        while self.peek() in _BINARY and _BINARY[self.peek()] == level:
            op = self.take()
            right = self.binary(level + 1)
            left = (op, left, right)
        return left

    def unary(self):
        tok = self.take()
        if tok == "~":
            return ("~", self.unary())
        if tok == "(":
            inner = self.binary(1)
            if self.take() != ")":
                raise ValueError("missing )")
            return inner
        if tok in "01":
            return ("const", int(tok))
        if tok.isupper():
            return ("var", tok)
        raise ValueError(f"unexpected {tok!r}")


def _eval(tree, values: dict[str, int]) -> int:
    kind = tree[0]
    if kind == "const":
        return tree[1]
    if kind == "var":
        return 1 if values[tree[1]] else 0
    if kind == "~":
        return 1 - _eval(tree[1], values)
    a = _eval(tree[1], values)
    b = _eval(tree[2], values)
    if kind == "*":
        return a & b
    if kind == "+":
        return a | b
    if kind == "⊕":
        return a ^ b
    return 1 - (a ^ b)  # ⊙


def _variables(*exprs: str) -> list[str]:
    return sorted({ch for e in exprs for ch in e if ch.isupper()})


def _rows(names: list[str]):
    for bits in product((0, 1), repeat=len(names)):
        yield bits, dict(zip(names, bits))


def evaluate(expr: str, values: dict[str, int]) -> int:
    return _eval(_Parser(expr).parse(), values)


def _table(expr: str) -> list[tuple[tuple[int, ...], int]]:
    tree = _Parser(expr).parse()
    names = _variables(expr)
    return [(bits, _eval(tree, row)) for bits, row in _rows(names)]


def solutions(expr: str, value: int = 1) -> str:
    rows = ["(" + ",".join(str(b) for b in bits) + ")" for bits, v in _table(expr) if v == value]
    return ", ".join(rows) if rows else "NONE"


def count(expr: str, value: int = 1) -> int:
    return sum(1 for _, v in _table(expr) if v == value)


def column(expr: str) -> str:
    return "".join(str(v) for _, v in _table(expr))


def equivalent(a: str, b: str) -> bool:
    ta, tb = _Parser(a).parse(), _Parser(b).parse()
    names = _variables(a, b)
    return all(_eval(ta, row) == _eval(tb, row) for _, row in _rows(names))


# ---------------------------------------------------------------- minimal sums of products
# A cube is a tuple with one entry per variable: 1 (the variable), 0 (its NOT) or None (absent).


def _cube_rows(cube: tuple) -> set[tuple[int, ...]]:
    choices = [(0, 1) if c is None else (c,) for c in cube]
    return set(product(*choices))


def _cube_text(cube: tuple, names: list[str]) -> str:
    return " * ".join(n if c == 1 else "~" + n for n, c in zip(names, cube) if c is not None)


def _cube_key(cube: tuple) -> list[tuple[int, int]]:
    # position by position: earlier variable first, then X before ~X; shorter prefix first
    return [(i, 0 if c == 1 else 1) for i, c in enumerate(cube) if c is not None]


def minimal_sops(expr: str) -> list[str]:
    names = _variables(expr)
    on = {bits for bits, v in _table(expr) if v == 1}
    if not on:
        return ["0"]
    if len(on) == 2 ** len(names):
        return ["1"]
    implicants = [
        cube
        for cube in product((None, 0, 1), repeat=len(names))
        if _cube_rows(cube) <= on
    ]
    implicant_set = set(implicants)
    primes = []
    for cube in implicants:
        widened = (cube[:i] + (None,) + cube[i + 1 :] for i, c in enumerate(cube) if c is not None)
        if not any(w in implicant_set for w in widened):
            primes.append(cube)
    covers = {p: _cube_rows(p) for p in primes}
    for size in range(1, len(primes) + 1):
        found = []
        for combo in combinations(primes, size):
            if set().union(*(covers[p] for p in combo)) == on:
                literals = sum(1 for p in combo for c in p if c is not None)
                found.append((literals, combo))
        if found:
            best = min(lit for lit, _ in found)
            texts = []
            for lit, combo in found:
                if lit == best:
                    ordered = sorted(combo, key=_cube_key)
                    texts.append(" + ".join(_cube_text(p, names) for p in ordered))
            return sorted(set(texts))
    raise AssertionError("unreachable: the primes always cover the on-set")
