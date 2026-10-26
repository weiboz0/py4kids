"""``write_variant``: copy a submission with some module-level constants changed (plan roar-002).

The "try a variant" idiom: a variant is a real one-file submission, so it can be raced with
``run_race`` and checked with ``check_submission`` exactly like the original::

    write_variant("agents/unit-01.py", "variant.py", {"TARGET_SPEED": "25.0"})

Standard library only.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, List, Union


def _assignments(tree: ast.Module, name: str) -> List[ast.stmt]:
    """Module-level ``name = ...`` / ``name: T = ...`` statements."""
    found = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                found.append(node)
        elif (isinstance(node, ast.AnnAssign) and node.value is not None
              and isinstance(node.target, ast.Name) and node.target.id == name):
            found.append(node)
    return found


def write_variant(
    src_path: Union[str, Path], dst_path: Union[str, Path], replacements: Dict[str, str],
) -> Path:
    """Copy ``src_path`` to ``dst_path``, replacing the value of each module-level constant.

    ``replacements`` maps a constant's name to its new value as Python source (``"25.0"``; an int
    or float is also accepted). Each name must be assigned exactly once at module level, as a
    single plain name (``TARGET_SPEED = 20.0``); a missing or duplicate constant, a new value that
    is not an expression, or a result that does not parse raises ``ValueError`` and writes nothing.
    Comments and everything else in the file are kept.
    """
    source = Path(src_path).read_text(encoding="utf-8")
    lines = source.splitlines(keepends=True)
    tree = ast.parse(source)
    edits = []
    for name, value in replacements.items():
        text = value if isinstance(value, str) else repr(value)
        try:
            ast.parse(text, mode="eval")
        except SyntaxError as error:
            raise ValueError(f"{name}: the new value {text!r} is not a Python expression") from error
        found = _assignments(tree, name)
        if len(found) != 1:
            where = "is not assigned" if not found else f"is assigned {len(found)} times"
            raise ValueError(f"{name} {where} at module level in {src_path}; it must be assigned exactly once")
        node = found[0]
        if isinstance(node, ast.Assign) and (len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name)):
            raise ValueError(f"{name}: only a single-name assignment (NAME = value) can be replaced")
        expression = node.value
        edits.append((expression.lineno, expression.col_offset, expression.end_lineno,
                      expression.end_col_offset, text))
    # apply from the end of the file backwards, so earlier offsets stay valid
    for start_line, start_col, end_line, end_col, text in sorted(edits, reverse=True):
        # ast offsets are UTF-8 byte columns
        head = lines[start_line - 1].encode("utf-8")[:start_col].decode("utf-8")
        tail = lines[end_line - 1].encode("utf-8")[end_col:].decode("utf-8")
        lines[start_line - 1:end_line] = [head + text + tail]
    result = "".join(lines)
    try:
        ast.parse(result)
    except SyntaxError as error:
        raise ValueError(f"the variant does not parse: {error.msg} (line {error.lineno})") from error
    dst = Path(dst_path)
    dst.write_text(result, encoding="utf-8")
    return dst
