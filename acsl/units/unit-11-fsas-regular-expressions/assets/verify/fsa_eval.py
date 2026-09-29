"""ACSL FSA / regular-expression evaluator used only by unit 11's ``verify`` cells (plan 095).

``accepts(pattern, s)`` translates an ACSL regular expression to Python's ``re`` syntax, token by
token, and uses ``re.fullmatch``. Outside a ``[...]`` class, ``U`` (union) becomes ``|`` and
``λ`` (the empty string) becomes an empty group ``()``; inside a class both are literal
characters and the class operators (ranges, ``^``) keep their meaning. Everything else passes
through: concatenation, ``|``, ``*``, ``?``, ``+``, ``.``, ``( )``, with ``re``'s precedence
(quantifiers, then concatenation, then union), which is ACSL's.

``run_dfa(table, start, finals, s)`` runs a DFA given as a dict from ``(state, symbol)`` to the
next state; a missing entry rejects at once.

``same_language(p, q, alphabet, max_len)`` compares ``accepts`` on every string over
``alphabet`` of length 0 to ``max_len``.

Verification-only helper: exempt from the contest source policy.
"""

from __future__ import annotations

import itertools
import re


def _translate(pattern: str) -> str:
    out: list[str] = []
    in_class = False
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if in_class:
            if ch == "\\" and i + 1 < len(pattern):
                out.append(pattern[i : i + 2])
                i += 2
                continue
            if ch == "]":
                in_class = False
            out.append(ch)
        elif ch == "[":
            in_class = True
            out.append(ch)
            # A leading ^ and a leading ] belong to the class, as in re.
            if i + 1 < len(pattern) and pattern[i + 1] == "^":
                out.append("^")
                i += 1
            if i + 1 < len(pattern) and pattern[i + 1] == "]":
                out.append("\\]")
                i += 1
        elif ch == "U":
            out.append("|")
        elif ch == "λ":
            out.append("()")
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def accepts(pattern: str, s: str) -> bool:
    """True when the ACSL regular expression ``pattern`` matches the whole of ``s``."""
    return re.fullmatch(_translate(pattern), s) is not None


def run_dfa(table: dict, start, finals, s: str) -> bool:
    """Run the DFA ``table`` from ``start`` on ``s``; accept when it ends in ``finals``."""
    state = start
    for symbol in s:
        key = (state, symbol)
        if key not in table:
            return False
        state = table[key]
    return state in set(finals)


def same_language(p: str, q: str, alphabet, max_len: int) -> bool:
    """True when ``p`` and ``q`` agree on every string over ``alphabet`` up to ``max_len``."""
    symbols = list(alphabet)
    for length in range(max_len + 1):
        for letters in itertools.product(symbols, repeat=length):
            w = "".join(letters)
            if accepts(p, w) != accepts(q, w):
                return False
    return True
