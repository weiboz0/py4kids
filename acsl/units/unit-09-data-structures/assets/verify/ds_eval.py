"""Verification helper for unit 09: ACSL stacks, queues, binary search trees and heaps.

Used only by ``verify`` cells in ``solutions.ipynb`` (and ``tests/test_acsl_eval_ds.py``).

- ``run(script, kind)`` runs ``PUSH(e)`` / ``POP()`` / ``V = POP()`` statements on a stack or
  queue and returns ``{"popped": [...], "vars": {...}}`` (``"NIL"`` for an empty ``POP``).
- ``bst(keys)`` builds a BST (duplicates LEFT, root depth 0) and reports depths, path lengths,
  external nodes, leaves, height, leaf keys and the three traversals.
- ``bst_delete(keys, key)`` deletes the shallowest node holding ``key`` by ACSL's rule and
  reports the new tree (no ``depths``).
- ``heap(keys, kind)`` / ``heap_pop(keys, kind)`` give heap rows built by insertion, before and
  after ACSL root removal (ties between equal children go LEFT).

Canonical row text: letters run together, numbers separated by single spaces.
"""

from __future__ import annotations

import re

_PUSH = re.compile(r"^\s*PUSH\s*\((.*)\)\s*$")
_POP = re.compile(r"^\s*(?:([A-Z])\s*=\s*)?POP\s*\(\s*\)\s*$")
_BINOP = re.compile(r"^\s*(\S+?)\s*([+\-*])\s*(\S+)\s*$")
_INT = re.compile(r"^-?\d+$")


def _atom(text: str, variables: dict):
    text = text.strip()
    if _INT.match(text):
        return int(text)
    if text in variables:
        return variables[text]
    return text


def _value(expr: str, variables: dict):
    expr = expr.strip()
    if _INT.match(expr):
        return int(expr)
    match = _BINOP.match(expr)
    if match:
        a = _atom(match.group(1), variables)
        b = _atom(match.group(3), variables)
        op = match.group(2)
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        return a * b
    return _atom(expr, variables)


def run(script: list[str], kind: str) -> dict:
    if kind not in ("stack", "queue"):
        raise ValueError(f"unknown kind {kind!r}")
    items: list = []
    popped: list = []
    variables: dict = {}
    for statement in script:
        push = _PUSH.match(statement)
        if push:
            items.append(_value(push.group(1), variables))
            continue
        pop = _POP.match(statement)
        if not pop:
            raise ValueError(f"bad statement {statement!r}")
        if not items:
            value = "NIL"
        elif kind == "stack":
            value = items.pop()
        else:
            value = items.pop(0)
        popped.append(value)
        if pop.group(1):
            variables[pop.group(1)] = value
    return {"popped": popped, "vars": variables}


def _row(values) -> str:
    values = list(values)
    if all(isinstance(v, str) and len(v) == 1 for v in values):
        return "".join(values)
    return " ".join(str(v) for v in values)


class _Node:
    __slots__ = ("key", "left", "right")

    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


def _insert(root, key):
    """Insert ``key``; return (root, depth of the new node)."""
    node = _Node(key)
    if root is None:
        return node, 0
    current = root
    depth = 1
    while True:
        if key <= current.key:
            if current.left is None:
                current.left = node
                return root, depth
            current = current.left
        else:
            if current.right is None:
                current.right = node
                return root, depth
            current = current.right
        depth += 1


def _build(keys):
    root = None
    depths = []
    for key in keys:
        root, depth = _insert(root, key)
        depths.append(depth)
    return root, depths


def _report(root) -> dict:
    node_depths: list[int] = []
    external_depths: list[int] = []
    leaf_keys: list = []
    inorder: list = []
    preorder: list = []
    postorder: list = []

    def walk(node, depth):
        if node is None:
            external_depths.append(depth)
            return
        node_depths.append(depth)
        preorder.append(node.key)
        walk(node.left, depth + 1)
        inorder.append(node.key)
        walk(node.right, depth + 1)
        postorder.append(node.key)
        if node.left is None and node.right is None:
            leaf_keys.append(node.key)

    walk(root, 0)
    return {
        "ipl": sum(node_depths),
        "external": len(external_depths),
        "epl": sum(external_depths),
        "leaves": len(leaf_keys),
        "height": max(node_depths) if node_depths else -1,
        "leaf_keys": _row(leaf_keys),
        "inorder": _row(inorder),
        "preorder": _row(preorder),
        "postorder": _row(postorder),
    }


def bst(keys: list) -> dict:
    root, depths = _build(keys)
    report = {"depths": depths}
    report.update(_report(root))
    return report


def bst_delete(keys: list, key) -> dict:
    root, _ = _build(keys)
    # Shallowest node holding key: breadth-first, left to right, tracking parents.
    level = [(root, None)] if root is not None else []
    found = None
    while level and found is None:
        for node, parent in level:
            if node.key == key:
                found = (node, parent)
                break
        else:
            nxt = []
            for node, _parent in level:
                if node.left is not None:
                    nxt.append((node.left, node))
                if node.right is not None:
                    nxt.append((node.right, node))
            level = nxt
    if found is None:
        raise ValueError(f"{key!r} is not in the tree")
    p, f = found
    if p.left is None and p.right is None:
        replacement = None
    elif p.left is None:
        replacement = p.right
    elif p.right is None:
        replacement = p.left
    else:
        replacement = p.left
        last = replacement
        while last.right is not None:
            last = last.right
        last.right = p.right
    if f is None:
        root = replacement
    elif f.left is p:
        f.left = replacement
    else:
        f.right = replacement
    return _report(root)


def _out_of_order(parent, child, kind: str) -> bool:
    if kind == "min":
        return parent > child
    if kind == "max":
        return parent < child
    raise ValueError(f"unknown kind {kind!r}")


def _heap_list(keys, kind):
    heap = [None]
    for key in keys:
        heap.append(key)
        i = len(heap) - 1
        while i > 1 and _out_of_order(heap[i // 2], heap[i], kind):
            heap[i // 2], heap[i] = heap[i], heap[i // 2]
            i //= 2
    return heap


def _rows(heap) -> list[str]:
    rows = []
    start = 1
    while start < len(heap):
        rows.append(_row(heap[start:min(2 * start, len(heap))]))
        start *= 2
    return rows


def heap(keys: list, kind: str = "min") -> list[str]:
    return _rows(_heap_list(keys, kind))


def heap_pop(keys: list, kind: str = "min") -> list[str]:
    h = _heap_list(keys, kind)
    if len(h) <= 1:
        return []
    last = h.pop()
    if len(h) > 1:
        h[1] = last
        i = 1
        n = len(h) - 1
        while 2 * i <= n:
            child = 2 * i
            if child + 1 <= n and _out_of_order(h[child], h[child + 1], kind):
                child += 1  # right strictly better; equal children go left
            if not _out_of_order(h[i], h[child], kind):
                break
            h[i], h[child] = h[child], h[i]
            i = child
    return _rows(h)
