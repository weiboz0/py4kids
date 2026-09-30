"""Verification helper for unit 13: logic-gate circuits given as netlists.

Used only by ``verify`` cells in ``solutions.ipynb`` (and ``tests/test_acsl_eval_circuit.py``).

Netlist: the first line is ``INPUTS A B C`` (the input letters, in alphabetical order; each is a
column of every tuple, used or not). Then one gate per line, ``name = GATE(x, y)`` (one operand
for ``BUFFER`` and ``NOT``), where ``GATE`` is one of ``BUFFER NOT AND NAND OR NOR XOR XNOR`` and
each operand is a declared input or an earlier gate's name. The last line's gate is the output.
Blank lines and spaces around ``=``, ``(``, ``,`` and ``)`` are layout.

- ``evaluate(netlist, values)`` gives the output (0 or 1) for one row.
- ``solutions(netlist, value=1)`` gives the rows where the output equals ``value``, as unit 08's
  canonical tuple text (``(1,1,0), (1,1,1)``), or ``NONE``.
- ``count(netlist, value=1)`` counts those rows.
- ``to_expression(netlist)`` writes the output in the book's Boolean notation, gate by gate.
"""

from __future__ import annotations

import re
from itertools import product

_GATE = re.compile(r"^([a-z][a-z0-9_]*)\s*=\s*([A-Z]+)\s*\((.*)\)$")
_ARITY = {
    "BUFFER": 1,
    "NOT": 1,
    "AND": 2,
    "NAND": 2,
    "OR": 2,
    "NOR": 2,
    "XOR": 2,
    "XNOR": 2,
}


def _parse(netlist: str) -> tuple[list[str], list[tuple[str, str, list[str]]]]:
    lines = [ln.strip() for ln in netlist.splitlines() if ln.strip()]
    if not lines or lines[0].split()[0] != "INPUTS":
        raise ValueError("a netlist starts with an INPUTS line")
    inputs = lines[0].split()[1:]
    for name in inputs:
        if len(name) != 1 or not name.isupper():
            raise ValueError(f"input {name!r} is not a single capital letter")
    if inputs != sorted(inputs) or len(set(inputs)) != len(inputs):
        raise ValueError("inputs must be distinct and in alphabetical order")
    known = set(inputs)
    gates: list[tuple[str, str, list[str]]] = []
    for line in lines[1:]:
        match = _GATE.match(line)
        if not match:
            raise ValueError(f"cannot read gate line {line!r}")
        name, gate, args = match.group(1), match.group(2), match.group(3)
        if gate not in _ARITY:
            raise ValueError(f"unknown gate {gate!r}")
        operands = [a.strip() for a in args.split(",")]
        if len(operands) != _ARITY[gate]:
            raise ValueError(f"{gate} takes {_ARITY[gate]} input(s): {line!r}")
        for op in operands:
            if op not in known:
                raise ValueError(f"{op!r} is not an input or an earlier gate: {line!r}")
        if name in known:
            raise ValueError(f"gate name {name!r} used twice")
        known.add(name)
        gates.append((name, gate, operands))
    if not gates:
        raise ValueError("a netlist needs at least one gate")
    return inputs, gates


def _apply(gate: str, x: int, y: int = 0) -> int:
    if gate == "BUFFER":
        return x
    if gate == "NOT":
        return 1 - x
    if gate == "AND":
        return x & y
    if gate == "NAND":
        return 1 - (x & y)
    if gate == "OR":
        return x | y
    if gate == "NOR":
        return 1 - (x | y)
    if gate == "XOR":
        return x ^ y
    return 1 - (x ^ y)  # XNOR


def _run(inputs, gates, values: dict[str, int]) -> int:
    wire = {}
    for name in inputs:
        v = values[name]
        if v not in (0, 1):
            raise ValueError(f"{name} must be 0 or 1")
        wire[name] = v
    for name, gate, operands in gates:
        wire[name] = _apply(gate, *(wire[op] for op in operands))
    return wire[gates[-1][0]]


def evaluate(netlist: str, values: dict[str, int]) -> int:
    inputs, gates = _parse(netlist)
    return _run(inputs, gates, values)


def _table(netlist: str) -> list[tuple[tuple[int, ...], int]]:
    inputs, gates = _parse(netlist)
    rows = []
    for bits in product((0, 1), repeat=len(inputs)):
        rows.append((bits, _run(inputs, gates, dict(zip(inputs, bits)))))
    return rows


def solutions(netlist: str, value: int = 1) -> str:
    rows = [bits for bits, out in _table(netlist) if out == value]
    if not rows:
        return "NONE"
    return ", ".join("(" + ",".join(str(b) for b in bits) + ")" for bits in rows)


def count(netlist: str, value: int = 1) -> int:
    return sum(1 for _, out in _table(netlist) if out == value)


def _is_atom(text: str) -> bool:
    if len(text) == 1 and text.isupper():
        return True
    if text.startswith("~"):
        rest = text[1:]
        if _is_atom(rest):
            return True
        if rest.startswith("("):
            depth = 0
            for i, ch in enumerate(rest):
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        return i == len(rest) - 1
    return False


def _atom(text: str) -> str:
    return text if _is_atom(text) else f"({text})"


_SYMBOL = {"AND": "*", "OR": "+", "XOR": "⊕", "XNOR": "⊙", "NAND": "*", "NOR": "+"}


def to_expression(netlist: str) -> str:
    inputs, gates = _parse(netlist)
    text = {name: name for name in inputs}
    for name, gate, operands in gates:
        if gate == "BUFFER":
            text[name] = text[operands[0]]
        elif gate == "NOT":
            text[name] = "~" + _atom(text[operands[0]])
        else:
            x, y = (_atom(text[op]) for op in operands)
            body = f"{x} {_SYMBOL[gate]} {y}"
            text[name] = f"~({body})" if gate in ("NAND", "NOR") else body
    return text[gates[-1][0]]
