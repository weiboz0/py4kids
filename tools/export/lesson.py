"""Lesson notebooks → bundle blocks (design 012 D3, D6; plan 101 C).

The blocks follow the publisher (`tools/publish.py`), so web and print agree:

- The first cell's `# ` H1 line is the entry title (not a block); the rest of cell 0 is one
  `opener` block, exactly `render_chapter`'s hook (`re.sub(r'^# [^\\n]*\\n*', '', cell0).strip()`).
- A markdown cell starting `### You will learn` is `goals`, `### Recap` is `recap`; a Notice
  paragraph and its continuations (grouped as `markdown_blocks` groups them) is `notice`; other
  prose splits at every `## ` / `### ` heading into `prose` blocks. Block n ≥ 2 of a cell is keyed
  `…/<cell_id>#n`.
- Lesson asset listings (`asset_blocks`' `asset listing` records) are `program` blocks keyed
  `…/<cell_id>#asset:<name>`.
- Code cells take their type from `route_code` (`ROUTE_TYPES`); an unknown route fails.

Every executed code cell is probed (`tools/export/probe.py`). A probe `error` or `timeout` is
reported in `Lesson.probes` (a site-check FAIL) and the block carries `probe: null`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import nbformat

from tools.books import book_path
from tools.export.concepts import Registry, book_registry, cell_concepts, concept_override
from tools.export.ids import item_key
from tools.export.probe import (
    ProbeResult,
    analyse,
    named_files,
    probe_cells,
    tracked_files,
)
from tools.publish import (
    NOTICE,
    asset_blocks,
    code_tokens,
    fenced_paragraphs,
    read_source,
    route_code,
    strip_turtle_directives,
    tryit_ahead_assets,
    tryit_run_asset,
)
from tools.turtle_figure import turtle_segments

ROUTE_TYPES = {
    "code+output": "code",
    "code": "code",
    "tryit": "tryit",
    "tryit-stdin": "tryit",
    "tryit+figure": "tryit",
    "errordemo": "error-demo",
    "hangdemo": "hang-demo",
    "figure": "turtle-figure",
    "program": "program",
}
CODE_TYPES = {"code", "tryit", "error-demo", "hang-demo", "turtle-figure", "program"}
PANELS = (("### You will learn", "goals"), ("### Recap", "recap"))
SECTION = re.compile(r"^#{2,3} ")
H1 = re.compile(r"^# [^\n]*\n*")
TURTLE = re.compile(r"(^|\n)\s*(?:import turtle|from turtle import)")


@dataclass
class Lesson:
    """One lesson's export: the entry title, its blocks, and what the report and site-check need."""

    title: str
    blocks: list[dict]
    probes: dict[str, ProbeResult] = field(default_factory=dict)  # block key → probe result
    findings: list[str] = field(default_factory=list)  # FAIL: lines (unregistered concepts)
    unattributed: list[str] = field(default_factory=list)  # code-like block keys with no concept


def _block(key: str, kind: str, tags: list[str]) -> dict:
    return {"key": key, "type": kind, "needs_prelude": False, "prelude": [], "files": [],
            "concepts": [], "probe": None, "tags": tags}


def markdown_parts(source: str) -> list[tuple[str, str]]:
    """A markdown cell (not cell 0) as `(type, md)` parts, in order."""
    source = strip_turtle_directives(source)
    for title, kind in PANELS:
        if source.startswith(title + "\n") or source.strip() == title:
            return [(kind, source[len(title):].strip())]
    paragraphs = [p for p in fenced_paragraphs(source.strip()) if p.strip()]
    parts: list[tuple[str, list[str]]] = []
    i = 0
    while i < len(paragraphs):
        paragraph = paragraphs[i]
        if NOTICE.match(paragraph):
            notice = re.sub(r"^(?:\*\*Notice:\*\*|Notice:)\s*", "", paragraph, count=1,
                            flags=re.IGNORECASE)
            if notice and notice[0].islower():
                notice = notice[0].upper() + notice[1:]
            contents = [notice]
            i += 1
            while i < len(paragraphs) and not paragraphs[i].startswith("#"):
                contents.append(paragraphs[i])
                i += 1
            parts.append(("notice", contents))
            continue
        if SECTION.match(paragraph) or not parts or parts[-1][0] != "prose":
            parts.append(("prose", [paragraph]))
        else:
            parts[-1][1].append(paragraph)
        i += 1
    return [(kind, "\n\n".join(chunk)) for kind, chunk in parts]


def opener_hook(cell0_source: str) -> str:
    """`render_chapter`'s opener panel body: cell 0 minus its `# ` H1 line, stripped."""
    return H1.sub("", cell0_source, count=1).strip()


def _bundle_paths(entry: str, relatives: list[str]) -> list[str]:
    return [f"files/{entry}/{relative}" for relative in relatives]


def _code_block(cell, key: str, route: str) -> dict:
    if route not in ROUTE_TYPES:
        raise ValueError(f"FAIL: {key}: unknown route_code route {route!r}")
    block = _block(key, ROUTE_TYPES[route], list(cell.metadata.get("tags", [])))
    block["code"] = strip_turtle_directives(cell.source)
    block["route"] = route
    if route == "code+output":
        block["output"] = "".join(o.get("text", "") for o in cell.outputs
                                  if o.get("output_type") == "stream")
    if block["type"] == "tryit":
        block["stdin"] = route == "tryit-stdin"
        if isinstance(cell.metadata.get("sample_input"), str):
            block["sample_input"] = cell.metadata["sample_input"]
    try:
        if route == "figure":
            block["figure"] = turtle_segments(cell.source)
        elif route == "tryit+figure" and "sample_input" in block:
            stdin = "\n".join(block["sample_input"].split(" | ")) + "\n"
            block["figure"] = turtle_segments(cell.source, stdin=stdin)
    except Exception as error:
        raise ValueError(f"FAIL: {key}: turtle figure: {error}") from error
    return block


def lesson_export(root: Path, book: str, entry_dir: Path, *, probe: bool = True,
                  timeout_s: float = 20, registry: Registry | None = None) -> Lesson:
    """Export `entry_dir/lesson.ipynb` as blocks. `probe=False` skips the probe (`probe: null`)."""
    entry_dir = Path(entry_dir)
    entry = entry_dir.name
    registry = registry or book_registry(root, book)
    nb = nbformat.read(entry_dir / "lesson.ipynb", as_version=4)
    cells = nb.cells
    if not cells or cells[0].cell_type != "markdown" or not cells[0].source.startswith("# "):
        raise ValueError(f"FAIL: {book}/{entry}: lesson cell 0 must open with a `# ` title")
    title = cells[0].source.splitlines()[0].removeprefix("# ")
    blocks: list[dict] = []
    findings: list[str] = []
    probes = probe_cells(entry_dir, cells, timeout_s=timeout_s) if probe else {}
    tracked = set(tracked_files(entry_dir))
    keys = {cell.id: item_key(book, entry, "lesson", cell.id) for cell in cells}

    hook = opener_hook(cells[0].source)
    if hook:
        block = _block(keys[cells[0].id], "opener", list(cells[0].metadata.get("tags", [])))
        block["md"] = hook
        override, problems = concept_override(block["key"], cells[0].metadata, registry.ids)
        findings += problems
        block["concepts"] = override or []
        blocks.append(block)

    seen: set[str] = set()
    rendered_turtles: set[tuple[tuple[int, str], ...]] = set()
    rendered_tryits: set[str] = set()
    rest = cells[1:]
    for position, cell in enumerate(rest):
        key = keys[cell.id]
        tags = list(cell.metadata.get("tags", []))
        override, problems = concept_override(key, cell.metadata, registry.ids)
        findings += problems
        if cell.cell_type == "markdown":
            for n, (kind, md) in enumerate(markdown_parts(cell.source), start=1):
                block = _block(key if n == 1 else f"{key}#{n}", kind, tags)
                block["md"] = md
                block["concepts"] = override or []
                blocks.append(block)
            rendered_tryits |= tryit_ahead_assets(cell, rest[position + 1:], entry_dir)
            _text, records = asset_blocks(cell.source, entry_dir, "student", seen, entry,
                                          rendered_turtles, rendered_tryits)
            for record in records:
                if record["kind"] != "asset listing":
                    continue
                name = record["id"].removeprefix("asset:")
                source = read_source(entry_dir / "assets" / name, "student")
                block = _block(f"{key}#asset:{name}", "program", tags)
                block["code"] = strip_turtle_directives(source)
                block["files"] = _bundle_paths(entry, [f"assets/{name}"])
                block["concepts"] = (override if override is not None
                                     else cell_concepts(registry.profile, registry.ids, source))
                if TURTLE.search(source):
                    block["figure"] = turtle_segments(source)
                blocks.append(block)
        elif cell.cell_type == "code":
            run_asset = tryit_run_asset(cell, rest[position + 1] if position + 1 < len(rest)
                                        else None, entry_dir)
            if run_asset:
                rendered_tryits.add(run_asset)
            route, _body = route_code(cell, stdin_note=run_asset is None)
            if route in ("tryit+figure", "figure"):
                rendered_turtles.add(code_tokens(cell.source))
            block = _code_block(cell, key, route)
            block["concepts"] = (override if override is not None
                                 else cell_concepts(registry.profile, registry.ids, cell.source))
            result = probes.get(cell.id)
            if result is not None:
                block["probe"] = result.status if result.status in (
                    "standalone", "prelude", "mismatch") else None
                if block["probe"] is not None:
                    block["prelude"] = [keys[cell_id] for cell_id in result.prelude]
                    block["needs_prelude"] = bool(block["prelude"])
                block["files"] = _bundle_paths(entry, result.files)
            else:
                block["files"] = _bundle_paths(entry, named_files(analyse(cell.source).files,
                                                                  tracked))
            blocks.append(block)
    unattributed = [b["key"] for b in blocks if b["type"] in CODE_TYPES and not b["concepts"]]
    return Lesson(
        title=title,
        blocks=blocks,
        probes={keys[cell_id]: result for cell_id, result in probes.items()},
        findings=findings,
        unattributed=unattributed,
    )


def lesson_blocks(root: Path, book: str, entry_dir: Path, **options) -> list[dict]:
    """The block dicts of `entry_dir`'s lesson, per the bundle schema, in cell order."""
    return lesson_export(root, book, entry_dir, **options).blocks


def lesson_dirs(root: Path, book: str) -> list[Path]:
    """The book's unit directories that hold a lesson, in syllabus order."""
    from tools.publish import entries

    return [path for entry_id, path in entries(book_path(root, book), "student")
            if entry_id.startswith("unit-") and (path / "lesson.ipynb").is_file()]
