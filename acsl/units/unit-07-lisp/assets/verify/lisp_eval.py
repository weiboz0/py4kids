"""ACSL LISP evaluator used only by unit 07's ``verify`` cells (plan 094).

``run(program)`` evaluates one or more ACSL LISP expressions in order, in one fresh environment,
and returns the canonical text of the last value. It implements ACSL's wiki set only
(categories.acsl.org, "LISP"): quote, SET, SETQ, EVAL, ATOM, CAR, CDR, the compositions
CAAR CADR CDAR CDDR CADDR CDDAR, CONS, REVERSE, ADD/+, MULT/*, SUB/-, DIV//, SQUARE, EXP,
EQ, POS, NEG, DEF and DEFUN. Built-in names are case-insensitive (CLISP).

Values: numbers are Python int/float, atoms are str (case kept), lists are Python lists,
NIL / () is the empty list, and true is the ``TRUE`` sentinel.
Verification-only helper: exempt from the contest source policy.
"""

from __future__ import annotations


class _True:
    def __repr__(self) -> str:
        return "true"


TRUE = _True()


class _Quote:
    """A quoted datum as read from the program text: ``'x``."""

    def __init__(self, datum):
        self.datum = datum


class LispError(Exception):
    pass


# ---------------------------------------------------------------- reading


def _tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    current = ""
    for ch in text:
        if ch in "()'":
            if current:
                tokens.append(current)
                current = ""
            tokens.append(ch)
        elif ch.isspace():
            if current:
                tokens.append(current)
                current = ""
        else:
            current += ch
    if current:
        tokens.append(current)
    return tokens


def _atom(token: str):
    try:
        return int(token)
    except ValueError:
        pass
    try:
        value = float(token)
    except ValueError:
        value = None
    if value is not None and token not in ("+", "-"):
        return _norm(value)
    if token.upper() == "NIL":
        return []
    return token


def _read(tokens: list[str], pos: int):
    if pos >= len(tokens):
        raise LispError("unexpected end of program")
    token = tokens[pos]
    if token == "'":
        datum, pos = _read(tokens, pos + 1)
        return _Quote(datum), pos
    if token == "(":
        items = []
        pos += 1
        while True:
            if pos >= len(tokens):
                raise LispError("missing )")
            if tokens[pos] == ")":
                return items, pos + 1
            item, pos = _read(tokens, pos)
            items.append(item)
    if token == ")":
        raise LispError("unexpected )")
    return _atom(token), pos + 1


def parse(program: str) -> list:
    tokens = _tokenize(program)
    exprs = []
    pos = 0
    while pos < len(tokens):
        expr, pos = _read(tokens, pos)
        exprs.append(expr)
    return exprs


# ---------------------------------------------------------------- evaluating


def _norm(x):
    if isinstance(x, float) and x.is_integer():
        return int(x)
    return x


def _is_number(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _num(x):
    if not _is_number(x):
        raise LispError(f"not a number: {show(x)}")
    return x


def _list(x) -> list:
    if not isinstance(x, list):
        raise LispError(f"not a list: {show(x)}")
    return x


def _car(x):
    x = _list(x)
    return x[0] if x else []


def _cdr(x):
    x = _list(x)
    return list(x[1:])


_COMPOSITIONS = {"CAAR", "CADR", "CDAR", "CDDR", "CADDR", "CDDAR"}


def _truth(flag: bool):
    return TRUE if flag else []


class _Env:
    def __init__(self) -> None:
        self.globals: dict[str, object] = {}
        self.functions: dict[str, tuple[list[str], object]] = {}

    def lookup(self, name: str, frames: list[dict]):
        for frame in reversed(frames):
            if name in frame:
                return frame[name]
        if name in self.globals:
            return self.globals[name]
        raise LispError(f"unbound atom: {name}")

    def bind(self, name: str, value, frames: list[dict]) -> None:
        for frame in reversed(frames):
            if name in frame:
                frame[name] = value
                return
        self.globals[name] = value


def _eval(expr, env: _Env, frames: list[dict]):
    if isinstance(expr, _Quote):
        return expr.datum
    if _is_number(expr) or expr is TRUE:
        return expr
    if isinstance(expr, str):
        return env.lookup(expr, frames)
    if not isinstance(expr, list):
        raise LispError(f"cannot evaluate {expr!r}")
    if not expr:
        return []
    head = expr[0]
    if not isinstance(head, str):
        raise LispError(f"not a function: {show(head)}")
    name = head.upper()
    args = expr[1:]

    # special forms
    if name in ("DEF", "DEFUN"):
        fname, params, body = args[0], args[1], args[2]
        env.functions[fname.upper()] = (list(params), body)
        return fname
    if name == "SETQ":
        value = _eval(args[1], env, frames)
        env.bind(args[0], value, frames)
        return value
    if name == "SET":
        target = _eval(args[0], env, frames)
        if not isinstance(target, str):
            raise LispError(f"SET needs an atom, got {show(target)}")
        value = _eval(args[1], env, frames)
        env.bind(target, value, frames)
        return value

    values = [_eval(a, env, frames) for a in args]

    if name in env.functions:
        params, body = env.functions[name]
        if len(params) != len(values):
            raise LispError(f"{head} takes {len(params)} arguments")
        frame = dict(zip(params, values))
        return _eval(body, env, frames + [frame])

    if name == "EVAL":
        return _eval(values[0], env, frames)
    if name == "ATOM":
        return _truth(not (isinstance(values[0], list) and values[0]))
    if name == "CAR":
        return _car(values[0])
    if name == "CDR":
        return _cdr(values[0])
    if name in _COMPOSITIONS:
        value = values[0]
        for letter in reversed(name[1:-1]):
            value = _car(value) if letter == "A" else _cdr(value)
        return value
    if name == "CONS":
        return [values[0]] + _list(values[1])
    if name == "REVERSE":
        return list(reversed(_list(values[0])))
    if name in ("ADD", "+"):
        total = 0
        for v in values:
            total = total + _num(v)
        return _norm(total)
    if name in ("MULT", "*"):
        product = 1
        for v in values:
            product = product * _num(v)
        return _norm(product)
    if name in ("SUB", "-"):
        if len(values) == 1:
            return _norm(-_num(values[0]))
        result = _num(values[0])
        for v in values[1:]:
            result = result - _num(v)
        return _norm(result)
    if name in ("DIV", "/"):
        result = _num(values[0])
        for v in values[1:]:
            result = result / _num(v)
        return _norm(result)
    if name == "SQUARE":
        return _norm(_num(values[0]) * _num(values[0]))
    if name == "EXP":
        return _norm(_num(values[0]) ** _num(values[1]))
    if name == "EQ":
        a, b = values
        if _is_number(a) and _is_number(b):
            return _truth(a == b)
        if isinstance(a, list) and isinstance(b, list):
            return _truth(not a and not b)
        if isinstance(a, list) or isinstance(b, list):
            return []
        return _truth(a is b or (type(a) is type(b) and a == b))
    if name == "POS":
        return _truth(_num(values[0]) > 0)
    if name == "NEG":
        return _truth(_num(values[0]) < 0)
    raise LispError(f"unknown function: {head}")


# ---------------------------------------------------------------- printing


def show(value) -> str:
    if value is TRUE:
        return "true"
    if isinstance(value, _Quote):
        return "'" + show(value.datum)
    if isinstance(value, list):
        if not value:
            return "NIL"
        return "(" + " ".join(show(v) for v in value) + ")"
    if _is_number(value):
        return str(_norm(value))
    return str(value)


def run(program: str) -> str:
    env = _Env()
    result = []
    for expr in parse(program):
        result = _eval(expr, env, [])
    return show(result)
