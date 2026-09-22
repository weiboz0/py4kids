"""Blocking, book-level concept-usage completeness check.

Parses every notebook (and .py asset) code cell with AST, detects which
registered concepts are USED with high confidence, and reports any that are
used but absent from that entry's introduces u requires u practices union.

Precision over recall: only report concepts we can detect confidently, so a
finding is (almost) always a real used-but-unlisted gap. Inherently-manual or
fuzzy concepts are never reported as violations (see MANUAL_ONLY). This makes
the check necessary, not sufficient: error-messages, run-program, comment,
naming, scope, loop-counter, type-conversion, int-type, boolean, and the other
MANUAL_ONLY concepts remain reviewer-enforced.

A string ``Constant`` inside a ``JoinedStr`` counts as ``string-literal``. Thus
the literal text in an f-string records both ``f-string`` and ``string-literal``.

Each scan builds a fresh per-book profile. Book 1 retains the original method,
builtin, and manual-only literals; dependent books extend that profile only for
features and techniques present in their own registry.
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from tools.books import book_path, dependency_baseline

# Concepts we do NOT flag as violations: not detectable from code, or too fuzzy
# to assert confidently. These stay reviewer-manual.
MANUAL_ONLY = {
    "run-program", "comment", "error-messages", "naming", "scope",
    "loop-counter", "type-conversion",  # accumulator now DETECTED (removed from MANUAL_ONLY)
    "boolean",  # detectable partially; too many false negatives to assert absence
    "list-index", "dict-access",  # subscript ambiguity vs string-index
    "string-index",               # subscript-index ambiguity vs list/dict
    "list-loop",                  # for-over-collection: type unknown
    "int-type",                   # bare int constants are everywhere; low signal
    "variable", "print",          # ubiquitous; still detected, low value
}

# Methods TAUGHT by book 1 (by the concept that teaches them). A method call whose
# name is not here maps to NO concept id and would slip the closure check silently
# (this is how `.index` nearly leaked into unit-06). Flag any other method call.
TAUGHT_METHODS = {
    "upper", "lower", "strip", "replace",   # string-methods (the taught subset ONLY)
    "append", "sort",                        # lists (unit-07 introduces)
    "items", "keys", "values", "get",        # dicts (unit-08 introduces)
    "read", "readlines", "readline", "write", "close",  # files (unit-09)
    "seed", "randint", "choice",             # random-module
    # turtle methods live in .py assets; add the ones the course uses:
    "forward", "backward", "left", "right", "penup", "pendown", "color",
    "pencolor", "fillcolor", "begin_fill", "end_fill", "goto", "setheading",
    "circle", "dot", "stamp", "speed", "done", "hideturtle", "shape", "bgcolor",
    "width", "pensize", "setup", "title", "exitonclick", "up", "down",
}
STRING_METHODS = {"upper", "lower", "strip", "replace"}  # the TAUGHT subset only
BUILTINS = {"len", "min", "max", "sorted", "sum", "abs", "round"}
DICT_METHODS = {"items", "keys", "values", "get"}
AUXILIARY_ROLES = {"demo", "given", "real-form", "composed"}
QUALIFIED_ID = re.compile(r"^(book1|book2):[a-z][a-z0-9-]*$")
FENCE_START = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
GIVEN_START = "# GIVEN TOOL — do not edit"
GIVEN_END = "# your work begins below"


@dataclass(frozen=True)
class ScanProfile:
    taught_methods: frozenset[str]
    builtins: frozenset[str]
    never_flag: frozenset[str]


def scanner_profile(concepts: list[dict]) -> ScanProfile:
    """Build a new immutable profile from one book's own concept registry."""
    registered = {
        concept.get("id")
        for concept in concepts
        if isinstance(concept, dict) and isinstance(concept.get("id"), str)
    }
    techniques = {
        concept["id"]
        for concept in concepts
        if isinstance(concept, dict)
        and concept.get("kind") == "technique"
        and isinstance(concept.get("id"), str)
    }
    taught_methods = set(TAUGHT_METHODS)
    if "str-split" in registered:
        taught_methods.add("split")
    if "set-ops" in registered:
        taught_methods.update({"add", "discard", "remove"})
    if "deque" in registered:
        taught_methods.update({"appendleft", "popleft"})
    return ScanProfile(
        taught_methods=frozenset(taught_methods),
        builtins=frozenset(BUILTINS),
        never_flag=frozenset(set(MANUAL_ONLY) | techniques),
    )


def detect(
    tree: ast.AST,
    *,
    registered_concepts: set[str] | None = None,
    profile: ScanProfile | None = None,
    occurrence_sink: list[tuple[str, ast.AST]] | None = None,
) -> tuple[set[str], set[str]]:
    """Return (concept ids used, unknown method names) — high-confidence only."""
    registered = set() if registered_concepts is None else set(registered_concepts)
    active_profile = profile or scanner_profile([])
    current_node: ast.AST | None = None

    class _DetectedConcepts(set):
        def add(self, concept: str) -> None:
            super().add(concept)
            if occurrence_sink is not None and current_node is not None and hasattr(
                current_node, "lineno"
            ):
                occurrence_sink.append((concept, current_node))

    used: set[str] = _DetectedConcepts()
    unknown_methods: set[str] = set()
    parents = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }
    set_names = {
        target.id
        for node in ast.walk(tree)
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        for target in (
            node.targets if isinstance(node, ast.Assign) else [node.target]
        )
        if isinstance(target, ast.Name)
        and (
            isinstance(node.value, ast.Set)
            or (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "set"
            )
        )
    }

    def add_feature(concept: str) -> None:
        if concept in registered:
            used.add(concept)

    def is_set_expression(node: ast.AST) -> bool:
        return isinstance(node, ast.Set) or (
            isinstance(node, ast.Name) and node.id in set_names
        )

    class V(ast.NodeVisitor):
        def __init__(self):
            self.loop_depth = 0

        def visit(self, node):
            nonlocal current_node
            previous = current_node
            current_node = node
            try:
                return super().visit(node)
            finally:
                current_node = previous

        def _enter_loop(self, node):
            if self.loop_depth >= 1:
                used.add("nested-loops")
            self.loop_depth += 1
            self.generic_visit(node)
            self.loop_depth -= 1

        def visit_Assert(self, node):
            pass  # asserts are exempt CI scaffolding, not taught concepts

        def visit_For(self, node):
            used.add("for-loop")
            self._enter_loop(node)

        def visit_While(self, node):
            used.add("while-loop")
            self._enter_loop(node)

        def visit_If(self, node):
            used.add("if-statement")
            if node.orelse:
                used.add("elif-else")
            self.generic_visit(node)

        def visit_Break(self, node):
            used.add("break-statement")

        def visit_Compare(self, node):
            for op in node.ops:
                if isinstance(op, (ast.In, ast.NotIn)):
                    used.add("in-operator")
                elif isinstance(op, (ast.Lt, ast.Gt, ast.LtE, ast.GtE, ast.Eq, ast.NotEq)):
                    used.add("comparison")
            self.generic_visit(node)

        def visit_BoolOp(self, node):
            used.add("logical-ops")
            self.generic_visit(node)

        def visit_UnaryOp(self, node):
            if isinstance(node.op, ast.Not):
                used.add("logical-ops")
            if isinstance(node.op, ast.Invert):
                add_feature("bitwise-ops")
            self.generic_visit(node)

        def visit_BinOp(self, node):
            def has_str(n):
                # true if a chain of +/* BinOps bottoms out in any str/JoinedStr leaf
                if (isinstance(n, ast.Constant) and isinstance(n.value, str)) \
                        or isinstance(n, ast.JoinedStr):
                    return True
                if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Add, ast.Mult)):
                    return has_str(n.left) or has_str(n.right)
                return False
            if isinstance(node.op, ast.Sub) and (
                is_set_expression(node.left) or is_set_expression(node.right)
            ):
                add_feature("set-ops")
            if isinstance(node.op, (ast.BitAnd, ast.BitOr, ast.BitXor, ast.LShift, ast.RShift)):
                add_feature("bitwise-ops")
                if isinstance(node.op, (ast.BitAnd, ast.BitOr, ast.BitXor)) and (
                    is_set_expression(node.left) or is_set_expression(node.right)
                ):
                    add_feature("set-ops")
            elif isinstance(node.op, (ast.Add, ast.Mult)) and (
                has_str(node.left) or has_str(node.right)
            ):
                used.add("string-concat")  # str +/* is concat/repeat, not arithmetic
            elif isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div,
                                      ast.FloorDiv, ast.Mod, ast.Pow)):
                used.add("arithmetic")
            self.generic_visit(node)

        def visit_Assign(self, node):
            # accumulator = read-modify-write: the target also appears in the value
            def base_name(t):
                if isinstance(t, ast.Name):
                    return t.id
                if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name):
                    return t.value.id
                if isinstance(t, ast.Attribute):
                    return ast.unparse(t)  # e.g. "self.health" — attribute accumulators
                return None
            targets = {base_name(t) for t in node.targets}
            targets.discard(None)
            if targets:
                # collect both Name ids and full attribute dotted-paths appearing in the value
                names_in_value = {n.id for n in ast.walk(node.value) if isinstance(n, ast.Name)}
                names_in_value |= {ast.unparse(n) for n in ast.walk(node.value)
                                   if isinstance(n, ast.Attribute)}
                if targets & names_in_value:
                    used.add("accumulator")
            self.generic_visit(node)

        def visit_AugAssign(self, node):
            used.add("accumulator")  # x += ... is the accumulator pattern
            if isinstance(node.op, (ast.Add, ast.Mult)) and (
                    (isinstance(node.value, ast.Constant) and isinstance(node.value.value, str))
                    or isinstance(node.value, ast.JoinedStr)):
                used.add("string-concat")
            else:
                used.add("arithmetic")
            self.generic_visit(node)

        def visit_JoinedStr(self, node):
            used.add("f-string")
            self.generic_visit(node)

        def visit_Constant(self, node):
            if isinstance(node.value, str):
                used.add("string-literal")
            elif isinstance(node.value, bool):
                used.add("boolean")
            elif isinstance(node.value, float):
                used.add("float-type")
            self.generic_visit(node)

        def visit_List(self, node):
            used.add("list-literal")
            self.generic_visit(node)

        def visit_Dict(self, node):
            used.add("dict-literal")
            self.generic_visit(node)

        def visit_Set(self, node):
            add_feature("set-literal")
            self.generic_visit(node)

        def visit_Tuple(self, node):
            add_feature("tuple")
            self.generic_visit(node)

        def visit_ListComp(self, node):
            add_feature("comprehension")
            self.generic_visit(node)

        def visit_SetComp(self, node):
            add_feature("comprehension")
            self.generic_visit(node)

        def visit_DictComp(self, node):
            add_feature("comprehension")
            self.generic_visit(node)

        def visit_GeneratorExp(self, node):
            add_feature("comprehension")
            self.generic_visit(node)

        def visit_Subscript(self, node):
            if isinstance(node.slice, ast.Slice):
                used.add("string-slice")  # also covers list slice; rare either way
            self.generic_visit(node)

        def visit_Import(self, node):
            used.add("import-statement")
            for n in node.names:
                if n.name == "random":
                    used.add("random-module")
                if n.name.startswith("turtle"):
                    used.add("turtle-basics")
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            used.add("import-statement")
            if node.module == "random":
                used.add("random-module")
            self.generic_visit(node)

        def visit_With(self, node):
            used.add("with-statement")
            self.generic_visit(node)

        def visit_ClassDef(self, node):
            used.add("class-def")
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    used.add("methods")
                    if item.name == "__init__":
                        used.add("init-method")
            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            is_method = isinstance(parents.get(node), ast.ClassDef)
            if not is_method:
                used.add("def-function")
            has_parameters = node.args.args or node.args.kwonlyargs or node.args.vararg
            is_self_only_method = (
                is_method
                and node.args.args
                and node.args.args[0].arg == "self"
                and len(node.args.args) == 1
            )
            if has_parameters and not is_self_only_method:
                used.add("parameters")
            if any(
                isinstance(descendant, ast.Call)
                and isinstance(descendant.func, ast.Name)
                and descendant.func.id == node.name
                for descendant in ast.walk(node)
            ):
                add_feature("recursion")
            self.generic_visit(node)

        def visit_Return(self, node):
            if node.value is not None:
                used.add("return-value")
            self.generic_visit(node)

        def visit_Attribute(self, node):
            if node.attr in STRING_METHODS:
                used.add("string-methods")
            if node.attr == "append":
                used.add("list-append")
            if node.attr == "sort":
                used.add("list-sort")
            if node.attr in DICT_METHODS:
                used.add("dict-loop") if node.attr in {"items", "keys", "values"} else None
            if isinstance(node.value, ast.Name) and node.value.id == "self":
                used.add("attributes")
            if node.attr in ("read", "readlines", "readline"):
                used.add("file-read")
            if node.attr == "write":
                used.add("file-write")
            if node.attr == "split":
                add_feature("str-split")
            if (
                node.attr in {"add", "discard", "remove"}
                and isinstance(node.value, ast.Name)
                and node.value.id in set_names
            ):
                add_feature("set-ops")
            if node.attr in {"appendleft", "popleft"}:
                add_feature("deque")
            self.generic_visit(node)

        def visit_Name(self, node):
            if node.id == "deque":
                add_feature("deque")

        def visit_Call(self, node):
            f = node.func
            if isinstance(f, ast.Attribute):
                # a method call x.name(...) — flag names that map to no taught concept
                recv = f.value
                recv_is_self = isinstance(recv, ast.Name) and recv.id == "self"
                if (f.attr not in active_profile.taught_methods
                        and not f.attr.startswith("__")
                        and not recv_is_self):  # own object methods are fine
                    unknown_methods.add(f.attr)
            if isinstance(f, ast.Name):
                if f.id == "print":
                    used.add("print")
                elif f.id == "input":
                    used.add("input")
                elif f.id == "range":
                    used.add("range-function")
                elif f.id in ("int", "str", "float"):
                    used.add("type-conversion")
                elif f.id == "sorted":
                    used.add("builtin-functions"); used.add("list-sort")
                    if any(keyword.arg == "key" for keyword in node.keywords):
                        add_feature("sorted-key")
                elif f.id in active_profile.builtins:
                    used.add("builtin-functions")
                elif f.id == "open":
                    used.add("with-statement")
                    for kw in node.args[1:2]:
                        if isinstance(kw, ast.Constant) and isinstance(kw.value, str):
                            if "w" in kw.value or "a" in kw.value:
                                used.add("file-write")
                            if "r" in kw.value:
                                used.add("file-read")
            self.generic_visit(node)

    V().visit(tree)
    return set(used), unknown_methods


def code_sources(nb_path: Path):
    """Yield code cells with stable notebook identity and auxiliary metadata."""
    nb = json.loads(nb_path.read_text())
    for index, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") == "code":
            metadata = cell.get("metadata", {})
            if not isinstance(metadata, dict):
                metadata = {}
            tags = metadata.get("tags", [])
            role_tags = (
                [tag for tag in tags if tag in AUXILIARY_ROLES]
                if isinstance(tags, list)
                and all(isinstance(tag, str) for tag in tags)
                else []
            )
            role = role_tags[0] if len(role_tags) == 1 else None
            source = cell.get("source", [])
            if isinstance(source, list) and all(
                isinstance(part, str) for part in source
            ):
                source = "".join(source)
            elif not isinstance(source, str):
                source = ""
            yield (
                nb_path,
                cell.get("id"),
                index,
                source,
                tags,
                metadata.get("py4kids_auxiliary", []),
                role,
            )


def entry_notebooks(entry_dir: Path, kind: str):
    if kind == "unit":
        names = ["lesson.ipynb", "exercises.ipynb", "solutions.ipynb"]
    elif kind == "checkpoint":
        names = ["checkpoint.ipynb", "solutions.ipynb"]
    else:
        names = ["brief.ipynb", "solutions.ipynb"]
    for n in names:
        p = entry_dir / n
        if p.exists():
            yield p
    assets = entry_dir / "assets"
    if assets.exists():
        yield from sorted(assets.glob("*.py"))


@dataclass(frozen=True)
class _Block:
    path: Path
    cell_id: str | None
    cell_index: int
    source: str
    tags: object
    declared: object
    has_declaration: bool
    role: str | None
    task_id: object
    block_kind: str


def _source(value: object) -> tuple[str, bool]:
    if isinstance(value, list) and all(isinstance(part, str) for part in value):
        return "".join(value), True
    if isinstance(value, str):
        return value, True
    return "", False


def _python_fences(source: str) -> tuple[list[str], bool]:
    fences: list[str] = []
    active: tuple[str, int, bool, list[str]] | None = None
    for line in source.splitlines(keepends=True):
        marker = line.rstrip("\r\n")
        if active is None:
            match = FENCE_START.fullmatch(marker)
            if match is None:
                continue
            delimiter = match.group(1)
            info = match.group(2).strip()
            first_token = info.split(maxsplit=1)[0].lower() if info else ""
            active = (
                delimiter[0],
                len(delimiter),
                first_token in {"python", "py"},
                [],
            )
            continue

        delimiter, minimum, is_python, body = active
        candidate = marker.lstrip(" ")
        indentation = len(marker) - len(candidate)
        run = len(candidate) - len(candidate.lstrip(delimiter))
        closes = (
            indentation <= 3
            and run >= minimum
            and candidate[:run] == delimiter * run
            and not candidate[run:].strip()
        )
        if closes:
            if is_python:
                fences.append("".join(body))
            active = None
        elif is_python:
            body.append(line)
    return fences, active is not None and active[2]


def _notebook_blocks(
    path: Path, *, include_markdown: bool
) -> tuple[list[_Block], list[str]]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    blocks: list[_Block] = []
    issues: list[str] = []
    for index, cell in enumerate(notebook.get("cells", [])):
        if not isinstance(cell, dict):
            continue
        cell_type = cell.get("cell_type")
        if cell_type != "code" and not (include_markdown and cell_type == "markdown"):
            continue
        metadata = cell.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        tags = metadata.get("tags", [])
        role_tags = (
            [tag for tag in tags if tag in AUXILIARY_ROLES]
            if isinstance(tags, list)
            and all(isinstance(tag, str) for tag in tags)
            else []
        )
        role = role_tags[0] if len(role_tags) == 1 else None
        common = {
            "path": path,
            "cell_id": cell.get("id"),
            "cell_index": index,
            "tags": tags,
            "declared": metadata.get("py4kids_auxiliary", []),
            "has_declaration": "py4kids_auxiliary" in metadata,
            "role": role,
            "task_id": metadata.get("py4kids_task_id"),
        }
        source, source_valid = _source(cell.get("source", ""))
        identity = cell.get("id") if isinstance(cell.get("id"), str) else index
        if not source_valid:
            issues.append(
                f"{path.name} cell {identity}: {cell_type} source must be a "
                "string or list of strings"
            )
        if cell_type == "code":
            blocks.append(_Block(source=source, block_kind="code", **common))
        else:
            fences, unclosed = _python_fences(source)
            if unclosed:
                issues.append(f"{path.name} cell {identity}: unclosed python fence")
            for fence in fences:
                blocks.append(
                    _Block(source=fence, block_kind="markdown", **common)
                )
    return blocks, issues


def _where(block: _Block) -> str:
    identity = block.cell_id if isinstance(block.cell_id, str) else block.cell_index
    return f"{block.path.name} cell {identity}"


def _qualified(raw: str, entry_auxiliary: set[str]) -> str | None:
    if raw == "str-split":
        return "book2:str-split"
    matches = sorted(qid for qid in entry_auxiliary if qid.endswith(f":{raw}"))
    return matches[0] if len(matches) == 1 else None


def _borrowed_occurrences(
    tree: ast.AST,
    *,
    registered: set[str],
    profile: ScanProfile,
) -> list[tuple[str, ast.AST]]:
    """Map detector emissions to AST nodes without discarding block context."""
    occurrences: list[tuple[str, ast.AST]] = []
    detect(
        tree,
        registered_concepts=registered,
        profile=profile,
        occurrence_sink=occurrences,
    )
    deduplicated: list[tuple[str, ast.AST]] = []
    seen: set[tuple[str, int]] = set()
    for concept, node in occurrences:
        key = (concept, id(node))
        if key not in seen:
            seen.add(key)
            deduplicated.append((concept, node))
    return deduplicated


def _given_region(source: str) -> tuple[str, int, int] | None:
    lines = source.splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == GIVEN_START]
    ends = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == GIVEN_END]
    if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
        return None
    start, end = starts[0], ends[0]
    return "".join(lines[start : end + 1]), start + 1, end + 1


def _is_accumulator_statement(node: ast.AST) -> bool:
    if isinstance(node, ast.AugAssign):
        return True
    if not isinstance(node, ast.Assign):
        return False

    def base_name(target: ast.AST) -> str | None:
        if isinstance(target, ast.Name):
            return target.id
        if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
            return target.value.id
        if isinstance(target, ast.Attribute):
            return ast.unparse(target)
        return None

    targets = {base_name(target) for target in node.targets}
    targets.discard(None)
    names = {child.id for child in ast.walk(node.value) if isinstance(child, ast.Name)}
    names |= {
        ast.unparse(child)
        for child in ast.walk(node.value)
        if isinstance(child, ast.Attribute)
    }
    return bool(targets & names)


def _exact_counter_statement(node: ast.AST) -> bool:
    if not isinstance(node, ast.Assign) or len(node.targets) != 1:
        return False
    target = node.targets[0]
    value = node.value
    return (
        isinstance(target, ast.Name)
        and isinstance(value, ast.BinOp)
        and isinstance(value.op, ast.Add)
        and isinstance(value.left, ast.Name)
        and value.left.id == target.id
        and isinstance(value.right, ast.Constant)
        and type(value.right.value) is int
        and value.right.value == 1
    )


def _load_k2(root: Path, book: str) -> tuple[list[dict], list[str]]:
    if book != "book1":
        return [], []
    path = book_path(root, book) / "curriculum" / "k2-exceptions.yaml"
    if not path.is_file():
        return [], []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [], [f"FAIL: book1: k2-exceptions.yaml invalid YAML: {exc}"]
    if not isinstance(data, dict):
        return [], ["FAIL: book1: k2-exceptions.yaml must be a mapping"]
    if set(data) != {"k2_exceptions_version", "exceptions"}:
        return [], ["FAIL: book1: k2-exceptions.yaml keys are invalid"]
    if data.get("k2_exceptions_version") != 1:
        return [], ["FAIL: book1: k2_exceptions_version must be 1"]
    rows = data.get("exceptions")
    if not isinstance(rows, list):
        return [], ["FAIL: book1: k2 exceptions must be a list"]
    findings: list[str] = []
    valid: list[dict] = []
    expected_keys = {"cell-id", "concept-ids", "exact-ast-form", "role"}
    expected_concepts = {"book1:loop-counter", "book1:accumulator"}
    for index, row in enumerate(rows):
        prefix = f"FAIL: book1: k2 exception {index}"
        if not isinstance(row, dict) or set(row) != expected_keys:
            findings.append(f"{prefix} must have exactly {sorted(expected_keys)}")
            continue
        concepts = row.get("concept-ids")
        if (
            not isinstance(row.get("cell-id"), str)
            or not row["cell-id"]
            or not isinstance(concepts, list)
            or any(not isinstance(value, str) for value in concepts)
            or len(concepts) != len(set(concepts))
            or set(concepts) != expected_concepts
            or row.get("exact-ast-form") != "name = name + 1"
            or row.get("role") != "composed"
        ):
            findings.append(f"{prefix} is not an allowed closed-table row")
            continue
        valid.append(row)
    return valid, findings


def _declared_owner_concepts(root: Path, auxiliary: set[str]) -> list[dict]:
    """Load registry metadata for exactly-qualified auxiliary concept owners."""
    selected: list[dict] = []
    by_owner: dict[str, set[str]] = {}
    for qid in auxiliary:
        if ":" not in qid:
            continue
        owner, concept_id = qid.split(":", 1)
        by_owner.setdefault(owner, set()).add(concept_id)
    for owner in sorted(by_owner):
        path = book_path(root, owner) / "curriculum" / "concepts.yaml"
        if not path.is_file():
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        rows = data.get("concepts", []) if isinstance(data, dict) else []
        selected.extend(
            concept
            for concept in rows
            if isinstance(concept, dict)
            and isinstance(concept.get("id"), str)
            and concept["id"] in by_owner[owner]
        )
    return selected


def _metadata_findings(
    eid: str, block: _Block, entry_auxiliary: set[str]
) -> tuple[list[str], set[str]]:
    """Validate one governed cell and return its usable declarations."""
    prefix = f"FAIL: {eid}: {_where(block)}"
    findings: list[str] = []
    tags = block.tags
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        return [f"{prefix}: metadata tags must be a list of strings"], set()
    has_aux_tag = "auxiliary" in tags
    role_tags = [tag for tag in tags if tag in AUXILIARY_ROLES]
    marked = has_aux_tag or block.has_declaration or bool(role_tags)
    if not marked:
        return [], set()
    declared = block.declared
    if not isinstance(declared, list) or any(not isinstance(qid, str) for qid in declared):
        return [f"{prefix}: py4kids_auxiliary must be a list of qualified ids"], set()
    if any(not QUALIFIED_ID.fullmatch(qid) for qid in declared):
        findings.append(f"{prefix}: py4kids_auxiliary contains an unqualified id")
    if len(declared) != len(set(declared)):
        findings.append(f"{prefix}: py4kids_auxiliary contains duplicate ids")
    if "book1:str-split" in declared:
        findings.append(f"{prefix}: str-split must be declared as book2:str-split")
    if has_aux_tag and not declared:
        findings.append(f"{prefix}: auxiliary tag requires at least one id")
    if declared and not has_aux_tag:
        findings.append(f"{prefix}: py4kids_auxiliary requires the auxiliary tag")
    if role_tags and not has_aux_tag:
        findings.append(f"{prefix}: auxiliary role requires the auxiliary tag")
    if role_tags and not declared:
        findings.append(f"{prefix}: auxiliary role requires at least one id")
    if len(role_tags) != 1:
        findings.append(f"{prefix}: borrowed cell must have exactly one auxiliary role")
    undeclared = sorted(set(declared) - entry_auxiliary)
    if undeclared:
        findings.append(f"{prefix}: cell auxiliary ids not declared by entry: {undeclared}")
    detectable = [qid for qid in set(declared) if qid.split(":", 1)[-1] not in MANUAL_ONLY]
    if len(detectable) > 1:
        findings.append(f"{prefix}: more than one detectable auxiliary id")
    if findings:
        return findings, set()
    return [], set(declared)


def _legacy_scan_findings(
    root: Path,
    book: str,
    entries: list,
    registered: set[str],
    profile: ScanProfile,
    baseline: set[str],
) -> list[str]:
    """Preserve schema-v1 concept-scan behavior and finding text byte-for-byte."""
    book_dir = book_path(root, book)
    dirs = {
        "unit": book_dir / "units",
        "checkpoint": book_dir / "checkpoints",
        "project": book_dir / "projects",
    }
    findings: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        kind = entry.get("kind")
        eid = entry.get("id")
        if kind not in dirs or not isinstance(eid, str):
            continue
        edir = dirs[kind] / eid
        if not edir.exists():
            continue
        allowed = (
            set(entry.get("introduces", []) or [])
            | set(entry.get("requires", []) or [])
            | set(entry.get("practices", []) or [])
            | baseline
        )
        used: set[str] = set()
        methods: set[str] = set()
        defined_names: set[str] = set()
        for path in entry_notebooks(edir, kind):
            if path.suffix == ".ipynb":
                sources = [block[3] for block in code_sources(path)]
            else:
                sources = [path.read_text(encoding="utf-8")]
            for source in sources:
                try:
                    tree = ast.parse(source)
                except SyntaxError:
                    continue
                block_used, block_methods = detect(
                    tree, registered_concepts=registered, profile=profile
                )
                used |= block_used
                methods |= block_methods
                defined_names |= {
                    node.name
                    for node in ast.walk(tree)
                    if isinstance(node, ast.FunctionDef)
                }
        methods -= defined_names
        findings.extend(
            f"FAIL: {eid}: used-but-unlisted concept {concept}"
            for concept in sorted((used - allowed) - profile.never_flag)
        )
        findings.extend(
            f"FAIL: {eid}: untaught method {method}"
            for method in sorted(methods)
        )
    return findings


def concept_scan_findings(
    root: Path, book: str, unit: str | None = None
) -> list[str]:
    """Return high-confidence used-but-unlisted findings for every book entry."""
    del unit
    book_dir = book_path(root, book)
    map_path = book_dir / "curriculum" / "coverage-map.yaml"
    if not map_path.is_file():
        return [f"FAIL: {book}: coverage-map.yaml does not exist"]
    cmap = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    if not isinstance(cmap, dict) or not isinstance(cmap.get("entries"), list):
        return [f"FAIL: {book}: coverage-map entries must be a list"]
    concepts_path = book_dir / "curriculum" / "concepts.yaml"
    concepts_data = (
        yaml.safe_load(concepts_path.read_text(encoding="utf-8"))
        if concepts_path.is_file()
        else {}
    )
    concepts = concepts_data.get("concepts", []) if isinstance(concepts_data, dict) else []
    registered = {
        concept["id"]
        for concept in concepts
        if isinstance(concept, dict) and isinstance(concept.get("id"), str)
    }
    profile = scanner_profile(concepts)
    baseline = dependency_baseline(root, book)
    if cmap.get("map_version") == 1:
        return _legacy_scan_findings(
            root, book, cmap["entries"], registered, profile, baseline
        )
    dirs = {
        "unit": book_dir / "units",
        "checkpoint": book_dir / "checkpoints",
        "project": book_dir / "projects",
    }
    k2_rows, findings = _load_k2(root, book)
    all_cell_ids: list[str] = []
    k2_cells: dict[
        str, list[tuple[str, str, set[str], _Block, ast.AST]]
    ] = {}
    parsed_by_entry: dict[str, list[tuple[_Block, ast.AST]]] = {}
    home_indexes: dict[str, int] = {}
    for entry_index, entry in enumerate(cmap["entries"]):
        if not isinstance(entry, dict):
            continue
        for concept_id in entry.get("introduces", []) or []:
            if isinstance(concept_id, str):
                home_indexes.setdefault(concept_id, entry_index)

    # Parse all governed notebook blocks once. This also supplies the real cell-id
    # set used to fail closed when a K2 row becomes stale.
    for entry in cmap["entries"]:
        if not isinstance(entry, dict):
            continue
        kind = entry.get("kind")
        eid = entry.get("id")
        if kind not in dirs or not isinstance(eid, str):
            continue
        edir = dirs[kind] / eid
        if not edir.exists():
            continue
        entry_auxiliary = {
            qid for qid in (entry.get("auxiliary", []) or []) if isinstance(qid, str)
        }
        parsed: list[tuple[_Block, ast.AST]] = []
        for path in entry_notebooks(edir, kind):
            if path.suffix != ".ipynb":
                try:
                    parsed.append(
                        (
                            _Block(path, None, 0, path.read_text(), [], [], False,
                                   None, None, "asset"),
                            ast.parse(path.read_text()),
                        )
                    )
                except SyntaxError:
                    findings.append(
                        f"FAIL: {eid}: assets/{path.name} has SyntaxError"
                    )
                continue
            blocks, notebook_issues = _notebook_blocks(
                path, include_markdown=book == "book1"
            )
            findings.extend(f"FAIL: {eid}: {issue}" for issue in notebook_issues)
            for block in blocks:
                if isinstance(block.cell_id, str):
                    all_cell_ids.append(block.cell_id)
                try:
                    tree = ast.parse(block.source)
                    parsed.append((block, tree))
                    if block.block_kind == "code" and isinstance(block.cell_id, str):
                        k2_cells.setdefault(block.cell_id, []).append(
                            (kind, eid, entry_auxiliary, block, tree)
                        )
                except SyntaxError:
                    if block.block_kind == "markdown":
                        findings.append(
                            f"FAIL: {eid}: {_where(block)}: python fence has SyntaxError"
                        )
                    elif not (
                        kind == "unit"
                        and isinstance(block.tags, list)
                        and all(isinstance(tag, str) for tag in block.tags)
                        and "no-exec" in block.tags
                    ):
                        findings.append(
                            f"FAIL: {eid}: {_where(block)}: code cell has SyntaxError"
                        )
        parsed_by_entry[eid] = parsed

    active_k2_rows: list[dict] = []
    for row in k2_rows:
        if all_cell_ids.count(row["cell-id"]) != 1:
            findings.append(
                f"FAIL: book1: k2 exception cell-id {row['cell-id']} "
                "must name exactly one existing cell"
            )
            continue
        candidates = k2_cells.get(row["cell-id"], [])
        matches = False
        if len(candidates) == 1:
            row_kind, row_eid, row_auxiliary, block, tree = candidates[0]
            _metadata_errors, validated_declared = _metadata_findings(
                row_eid, block, row_auxiliary
            )
            accumulator_nodes = [
                node
                for node in ast.walk(tree)
                if isinstance(node, (ast.Assign, ast.AugAssign))
                and _is_accumulator_statement(node)
            ]
            matches = (
                row_kind == "unit"
                and block.role == "composed"
                and isinstance(block.tags, list)
                and "auxiliary" in block.tags
                and validated_declared == set(row["concept-ids"])
                and any(_exact_counter_statement(node) for node in accumulator_nodes)
            )
        if matches:
            active_k2_rows.append(row)
        else:
            findings.append(
                f"FAIL: book1: k2 exception cell-id {row['cell-id']} does not "
                "match its concepts, role, location, and exact AST form"
            )

    for entry_index, entry in enumerate(cmap["entries"]):
        if not isinstance(entry, dict):
            continue
        kind = entry.get("kind")
        eid = entry.get("id")
        if kind not in dirs or not isinstance(eid, str):
            continue
        edir = dirs[kind] / eid
        if not edir.exists():
            continue
        base_allowed = (
            set(entry.get("introduces", []) or [])
            | set(entry.get("requires", []) or [])
            | set(entry.get("practices", []) or [])
            | baseline
        )
        entry_auxiliary = {
            qid for qid in (entry.get("auxiliary", []) or []) if isinstance(qid, str)
        }
        entry_profile = scanner_profile(
            concepts + _declared_owner_concepts(root, entry_auxiliary)
        )
        future_concepts = {
            concept_id
            for concept_id, home_index in home_indexes.items()
            if home_index > entry_index
        }
        entry_registered = (
            registered
            | {"str-split"}
            | {qid.split(":", 1)[-1] for qid in entry_auxiliary if ":" in qid}
        )
        parsed = parsed_by_entry.get(eid, [])
        defined_names = set()  # functions + class methods defined in this entry's notebooks
        for _block, tree in parsed:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    defined_names.add(node.name)  # incl. class methods

        exercise_cells: dict[str, list[tuple[_Block, str | None]]] = {}
        solution_cells: dict[str, list[tuple[_Block, str | None]]] = {}
        for block, tree in parsed:
            metadata_errors: list[str] = []
            declared: set[str] = set()
            if book == "book1" and block.block_kind != "asset":
                metadata_errors, declared = _metadata_findings(
                    eid, block, entry_auxiliary
                )
                findings.extend(metadata_errors)
            used, methods = detect(
                tree, registered_concepts=entry_registered, profile=entry_profile
            )
            methods -= defined_names
            raw_declared = {qid.split(":", 1)[-1] for qid in declared}
            used_borrowed = {
                raw
                for raw in used
                if raw in raw_declared and raw not in entry_profile.never_flag
            }
            for raw in sorted(raw_declared - used_borrowed - entry_profile.never_flag):
                findings.append(
                    f"FAIL: {eid}: {_where(block)}: declared auxiliary "
                    f"{_qualified(raw, declared) or raw} is unused"
                )

            is_k1 = bool(raw_declared) and block.role != "composed"
            if kind == "unit" and is_k1:
                if block.path.name == "exercises.ipynb" and block.role != "given":
                    findings.append(
                        f"FAIL: {eid}: {_where(block)}: exercise auxiliary "
                        "cell must use role given"
                    )
                elif (
                    block.path.name == "solutions.ipynb"
                    and block.role != "real-form"
                ):
                    findings.append(
                        f"FAIL: {eid}: {_where(block)}: solution auxiliary "
                        "cell must use role real-form"
                    )
                elif (
                    block.path.name == "lesson.ipynb"
                    and block.role not in {"demo", "real-form"}
                ):
                    findings.append(
                        f"FAIL: {eid}: {_where(block)}: lesson auxiliary cell must "
                        "use role demo or real-form"
                    )

            if block.block_kind == "markdown":
                borrowed_raw = {
                    raw
                    for raw in used
                    if raw == "str-split"
                    or raw in future_concepts
                    or any(qid.endswith(f":{raw}") for qid in entry_auxiliary)
                }
                for raw in sorted(borrowed_raw - raw_declared):
                    qid = _qualified(raw, entry_auxiliary)
                    if qid is None and raw in future_concepts:
                        qid = f"{book}:{raw}"
                    if qid:
                        findings.append(
                            f"FAIL: {eid}: {_where(block)}: undeclared borrowed tool {qid}"
                        )
                continue

            block_allowed = set(base_allowed)
            if block.role != "composed":
                block_allowed |= raw_declared

            # Composed K2 authorization is per statement, never per cell.
            accumulator_nodes = [
                node
                for node in ast.walk(tree)
                if isinstance(node, (ast.Assign, ast.AugAssign))
                and _is_accumulator_statement(node)
            ]
            matching_rows = [
                row
                for row in active_k2_rows
                if row["cell-id"] == block.cell_id
                and set(row["concept-ids"]) == declared
                and block.role == "composed"
                and kind == "unit"
                and all_cell_ids.count(row["cell-id"]) == 1
            ]
            if (
                accumulator_nodes
                and len(matching_rows) == 1
                and all(_exact_counter_statement(node) for node in accumulator_nodes)
            ):
                block_allowed.add("accumulator")

            if kind == "unit" and block.path.name == "exercises.ipynb":
                region = _given_region(block.source)
                if block.role != "composed":
                    for raw, node in _borrowed_occurrences(
                        tree, registered=entry_registered, profile=entry_profile
                    ):
                        if raw not in raw_declared:
                            continue
                        inside = (
                            region is not None
                            and region[1] < getattr(node, "lineno", 0) < region[2]
                            and getattr(node, "end_lineno", 0) < region[2]
                        )
                        if not inside:
                            findings.append(
                                f"FAIL: {eid}: {_where(block)}: auxiliary {raw} "
                                "is outside the GIVEN region"
                            )
                if raw_declared and block.role != "composed":
                    task_id = block.task_id
                    if not isinstance(task_id, str) or not task_id:
                        findings.append(
                            f"FAIL: {eid}: {_where(block)}: auxiliary exercise cell "
                            "requires py4kids_task_id"
                        )
                    else:
                        exercise_cells.setdefault(task_id, []).append(
                            (block, region[0] if region else None)
                        )
            elif kind == "unit" and block.path.name == "solutions.ipynb":
                if raw_declared and block.role != "composed":
                    task_id = block.task_id
                    if isinstance(task_id, str) and task_id:
                        region = _given_region(block.source)
                        solution_cells.setdefault(task_id, []).append(
                            (block, region[0] if region else None)
                        )
                    else:
                        findings.append(
                            f"FAIL: {eid}: {_where(block)}: auxiliary solution cell "
                            "requires py4kids_task_id"
                        )
            # `.split()` is reported as one borrowed-tool failure in Book 1,
            # and its generic unknown-method duplicate is suppressed only when
            # the declaration fully authorizes this block.
            if book == "book1" and "str-split" in used:
                if "str-split" not in raw_declared:
                    findings.append(
                        f"FAIL: {eid}: {_where(block)}: undeclared borrowed tool "
                        "book2:str-split"
                    )
                    used.discard("str-split")
                elif "str-split" in block_allowed:
                    methods.discard("split")

            gaps = sorted((used - block_allowed) - entry_profile.never_flag)
            findings.extend(
                f"FAIL: {eid}: {_where(block)}: used-but-unlisted concept {concept}"
                for concept in gaps
            )
            findings.extend(
                f"FAIL: {eid}: {_where(block)}: untaught method {method}"
                for method in sorted(methods)
            )

        task_ids = set(exercise_cells) | set(solution_cells)
        for task_id in sorted(task_ids):
            exercises = exercise_cells.get(task_id, [])
            solutions = solution_cells.get(task_id, [])
            if len(exercises) != 1 or len(solutions) != 1:
                findings.append(
                    f"FAIL: {eid}: auxiliary task id {task_id} must pair exactly one "
                    "exercise cell with one solution cell"
                )
            elif exercises[0][1] is None or solutions[0][1] is None:
                findings.append(
                    f"FAIL: {eid}: auxiliary task id {task_id} must contain GIVEN "
                    "regions on both sides"
                )
            elif exercises[0][1] != solutions[0][1]:
                findings.append(
                    f"FAIL: {eid}: auxiliary task id {task_id} GIVEN regions differ"
                )
    return findings
