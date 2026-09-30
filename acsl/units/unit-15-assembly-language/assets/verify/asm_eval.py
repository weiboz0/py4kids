"""ACSL assembly-language evaluator used only by unit 15's ``verify`` cells (plan 096).

``run(program, inputs=())`` runs an ACSL assembly program given as text, one instruction per
line, and returns ``{"memory": {label: int}, "printed": [int, ...], "acc": [int, ...]}``:

* ``memory``: the final value of every ``DC`` label and every label a ``STORE`` or ``READ``
  wrote to (branch targets on other instructions are not memory);
* ``printed``: the values ``PRINT`` printed, in order;
* ``acc``: the ACC after each executed ``LOAD``, ``ADD``, ``SUB``, ``MULT`` and ``DIV``.

Line parsing: blank lines are skipped; tokens are split on whitespace; the first token is a
label exactly when it is not an opcode; then the opcode, then an optional ``LOC``. ``LOC`` may be
immediate data ``=value`` for ``LOAD``, ``ADD``, ``SUB``, ``MULT`` and ``DIV``.

Semantics are the ACSL wiki's: ``ADD``, ``SUB``, ``MULT`` and ``READ`` keep a value modulo
1,000,000, read by the book as keeping the sign and the last six digits
(``sign(v) * (abs(v) % 1_000_000)``, a book convention); ``DIV`` is ACC divided by LOC, rounded
toward zero, and raises ``ZeroDivisionError`` on zero; ``BE``/``BG``/``BL`` branch on ACC = 0,
> 0, < 0 and ``BU`` always; ``DC`` defines a location before execution and does nothing when
reached; ``END`` stops. A run of more than 100,000 instructions raises ``RuntimeError``.

Verification-only helper: exempt from the contest source policy.
"""

from __future__ import annotations

OPCODES = {
    "LOAD", "STORE", "ADD", "SUB", "MULT", "DIV",
    "BE", "BG", "BL", "BU", "READ", "PRINT", "DC", "END",
}
IMMEDIATE_OK = {"LOAD", "ADD", "SUB", "MULT", "DIV"}
STEP_LIMIT = 100_000


def _wrap(v: int) -> int:
    """Keep the sign and the last six digits (the book's reading of 'modulo 1,000,000')."""
    if v < 0:
        return -((-v) % 1_000_000)
    return v % 1_000_000


def _parse(program: str) -> list[tuple[str | None, str, str | None]]:
    lines = []
    for raw in program.splitlines():
        tokens = raw.split()
        if not tokens:
            continue
        label = None
        if tokens[0] not in OPCODES:
            label = tokens.pop(0)
        if not tokens:
            raise ValueError(f"no opcode on line: {raw!r}")
        op = tokens[0]
        if op not in OPCODES:
            raise ValueError(f"unknown opcode {op!r} on line: {raw!r}")
        loc = tokens[1] if len(tokens) > 1 else None
        if len(tokens) > 2:
            raise ValueError(f"too many tokens on line: {raw!r}")
        lines.append((label, op, loc))
    return lines


def run(program: str, inputs=()) -> dict:
    lines = _parse(program)
    targets: dict[str, int] = {}
    memory: dict[str, int] = {}
    for i, (label, op, loc) in enumerate(lines):
        if label is not None:
            if label in targets:
                raise ValueError(f"duplicate label {label!r}")
            targets[label] = i
        if op == "DC":
            if label is None or loc is None:
                raise ValueError("DC needs a label and a value")
            memory[label] = int(loc)

    feed = iter(inputs)
    printed: list[int] = []
    acc_trace: list[int] = []
    acc = 0
    pc = 0
    steps = 0

    def value(op: str, loc: str | None) -> int:
        if loc is None:
            raise ValueError(f"{op} needs a LOC")
        if loc.startswith("="):
            if op not in IMMEDIATE_OK:
                raise ValueError(f"{op} does not take immediate data")
            return int(loc[1:])
        if loc not in memory:
            raise KeyError(f"location {loc!r} has no value")
        return memory[loc]

    def jump(loc: str | None) -> int:
        if loc not in targets:
            raise KeyError(f"no instruction labelled {loc!r}")
        return targets[loc]

    while pc < len(lines):
        steps += 1
        if steps > STEP_LIMIT:
            raise RuntimeError(f"more than {STEP_LIMIT} instructions executed")
        _label, op, loc = lines[pc]
        nxt = pc + 1
        if op == "END":
            break
        elif op == "DC":
            pass
        elif op == "LOAD":
            acc = value(op, loc)
            acc_trace.append(acc)
        elif op == "STORE":
            if loc is None or loc.startswith("="):
                raise ValueError("STORE needs a label")
            memory[loc] = acc
        elif op == "ADD":
            acc = _wrap(acc + value(op, loc))
            acc_trace.append(acc)
        elif op == "SUB":
            acc = _wrap(acc - value(op, loc))
            acc_trace.append(acc)
        elif op == "MULT":
            acc = _wrap(acc * value(op, loc))
            acc_trace.append(acc)
        elif op == "DIV":
            d = value(op, loc)
            if d == 0:
                raise ZeroDivisionError("DIV by zero")
            q = abs(acc) // abs(d)
            acc = q if (acc < 0) == (d < 0) else -q
            acc_trace.append(acc)
        elif op == "BE":
            if acc == 0:
                nxt = jump(loc)
        elif op == "BG":
            if acc > 0:
                nxt = jump(loc)
        elif op == "BL":
            if acc < 0:
                nxt = jump(loc)
        elif op == "BU":
            nxt = jump(loc)
        elif op == "READ":
            if loc is None or loc.startswith("="):
                raise ValueError("READ needs a label")
            try:
                memory[loc] = _wrap(int(next(feed)))
            except StopIteration:
                raise ValueError("READ with no input left") from None
        elif op == "PRINT":
            printed.append(value(op, loc))
        pc = nxt

    return {"memory": memory, "printed": printed, "acc": acc_trace}
