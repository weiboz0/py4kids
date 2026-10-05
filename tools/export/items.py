"""Items of a statement notebook for the site export (design 012 D3; plan 101 Phase D).

`entry_content` splits a unit's `exercises.ipynb`, a checkpoint's `checkpoint.ipynb` or a project's
`brief.ipynb` into `intro` blocks, items (each with its `before` interlude blocks) and `outro`
blocks, so every cell lands in exactly one place. It reads the statements through the publisher's
helpers (`item_groups`, `unit_challenges`, `statement_text`, `markdown_blocks`, …), so web and print
agree. Solution material is read only by `tools.export.answers` (each item's `solution_group`).

- Unit: `## Exercise N` groups, then unnumbered challenges (kind `challenge`, label `Challenge N`);
  a challenge section's lead-in cells go in the first challenge's `before`.
- Checkpoint: `## Question N` groups.
- Project: `Problem N` groups when the brief has them, partitioned by the export (a `## ` heading cell
  ends the current problem and goes to the next problem's `before`, or to `outro`); otherwise the
  `## Milestone N` sections. A milestone without a numbered solution section is a self-check item.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path

import nbformat
import yaml

from tools.books import book_flag, book_path, publication_config
from tools.concept_scan import detect, scanner_profile
from tools.publish import (
    ASSET,
    DATA,
    MILESTONE,
    NOTICE,
    OWN_TITLE,
    PLACEHOLDER,
    SOLUTION_SOURCE,
    VERIFY_TAG,
    _clean_title,
    allowed_source,
    group_title,
    item_divisions,
    item_groups,
    markdown_blocks,
    panel,
    statement_text,
    strip_challenge_lead,
    strip_solution_pointer,
    title_heading,
    unit_challenges,
)

from . import answers
from .ids import item_key, missing_id_findings

STEM = {"unit": "exercises", "checkpoint": "checkpoint", "project": "brief"}
PROBLEM = re.compile(r"^#{2,3} Problem (\d+)\b")
SECTION = re.compile(r"^## (?!#)")
GOALS_RECAP = (("### You will learn", "goals"), ("### Recap", "recap"))


@dataclass(eq=False)
class Item:
    """One exercise, challenge, checkpoint question, project problem or milestone.

    The first fields are the plan's interface; the rest is context the classifier and the answer
    model need (`cells` are the item's statement cells; `statement_source` their raw Markdown).
    `solution_group` is read only inside `tools.export.answers`.
    """

    key: str
    kind: str  # unit | challenge | checkpoint | project
    number: int | None
    label: str
    title: str
    division: list[str]
    stretch: bool
    concepts: list[str]
    statement_md: str
    starter: str
    files: list[str]
    heading_cell: nbformat.NotebookNode
    before: list[dict]
    solution_group: dict | None = field(default=None, repr=False)
    book: str = ""
    entry_dir: Path = field(default_factory=Path)
    entry_kind: str = ""  # unit | checkpoint | project
    mode: str = ""  # exercise | challenge | question | problem | milestone
    notebook: str = ""
    cells: list = field(default_factory=list, repr=False)
    statement_source: str = field(default="", repr=False)
    notes: list[str] = field(default_factory=list)


@dataclass
class EntryContent:
    """A statement notebook as `intro` blocks, items and `outro` blocks.

    `placement` lists `(key, place)` for every cell (place: `intro`, `outro`, `item:<key>` or
    `before:<key>`), so a test can prove every cell lands in exactly one place.
    """

    intro: list[dict]
    items: list[Item]
    outro: list[dict]
    placement: list[tuple[str, str]] = field(default_factory=list)


# --- concepts --------------------------------------------------------------------------------


def _cell_concepts_stub(profile, registered: set[str], source: str) -> list[str]:
    """Phase D's stand-in for Phase C's `tools.export.concepts.cell_concepts` (same signature)."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    used, _unknown = detect(tree, registered_concepts=set(registered), profile=profile)
    return sorted(set(used) & set(registered))


def _cell_concepts(profile, registered: set[str], source: str) -> list[str]:
    """`cell_concepts(profile, registered, source) -> list[str]`, sorted (Phase C).

    Uses Phase C's implementation when it is present, else the stub above, so the merge swaps it.
    """
    try:
        from tools.export.concepts import cell_concepts
    except ModuleNotFoundError as error:
        if error.name != "tools.export.concepts":
            raise
        return _cell_concepts_stub(profile, registered, source)
    return list(cell_concepts(profile, registered, source))


def _registry(root: Path, book: str) -> list[dict]:
    path = book_path(root, book) / "curriculum" / "concepts.yaml"
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return [c for c in data.get("concepts", []) if isinstance(c, dict) and isinstance(c.get("id"), str)]


def _manifest_concepts(entry_dir: Path) -> set[str]:
    path = entry_dir / "manifest.yaml"
    if not path.is_file():
        return set()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    concepts = data.get("concepts") or {}
    return {concept for key in ("introduces", "requires", "practices")
            for concept in concepts.get(key) or [] if isinstance(concept, str)}


def item_concept_findings(root: Path, book: str, items: list[Item]) -> list[str]:
    """`FAIL:` per heading-cell `metadata.concepts` id that is not in the book's registry (D11)."""
    registered = {c["id"] for c in _registry(root, book)}
    findings = []
    for item in items:
        authored = item.heading_cell.metadata.get("concepts")
        if authored is None:
            continue
        if not isinstance(authored, list) or not all(isinstance(c, str) for c in authored):
            findings.append(f"FAIL: {item.key}: metadata.concepts must be a list of concept ids")
            continue
        findings.extend(f"FAIL: {item.key}: unregistered concept {concept}"
                        for concept in authored if concept not in registered)
    return findings


# --- building blocks ---------------------------------------------------------------------------


@dataclass
class _Context:
    root: Path
    book: str
    entry_dir: Path
    kind: str
    stem: str
    lesson_heading: str | None
    placement: list[tuple[str, str]]

    def key(self, cell, part: int | None = None) -> str:
        return item_key(self.book, self.entry_dir.name, self.stem, cell.get("id"), part)


def _tags(cell) -> list[str]:
    return list(dict.fromkeys(cell.metadata.get("tags", [])))


def _block(key: str, type_: str, cell, **fields) -> dict:
    return {"key": key, "type": type_, **fields, "needs_prelude": False, "prelude": [], "files": [],
            "concepts": [], "probe": None, "tags": _tags(cell)}


def _side_block(ctx: _Context, cell, key: str) -> dict | None:
    """One intro, `before` or outro block, rendered as `render_items` renders such a cell."""
    if cell.cell_type == "code":
        if VERIFY_TAG in cell.metadata.get("tags", []) or not cell.source.strip():
            return None
        return _block(key, "starter", cell, code=cell.source)
    if cell.cell_type != "markdown":
        return None
    text = re.sub(r"^# [^\n]*", "", cell.source).strip()  # a notebook H1 is the chapter title
    if ctx.kind == "project":
        text = re.sub(r"(?m)^## Milestone ", "### Milestone ", text)
    if not text:
        return None
    for title, type_ in GOALS_RECAP:
        if text.startswith(title + "\n") or text == title:
            return _block(key, type_, cell, md=text[len(title):].strip())
    md = markdown_blocks(SECTION.sub("### ", text), lesson_heading=ctx.lesson_heading).rstrip()
    return _block(key, "notice" if NOTICE.match(text) else "prose", cell, md=md)


def _side_blocks(ctx: _Context, cells, place: str) -> list[dict]:
    out = []
    for cell in cells:
        key = ctx.key(cell)
        ctx.placement.append((key, place))
        block = _side_block(ctx, cell, key)
        if block is not None:
            out.append(block)
    return out


def _statement_md(ctx: _Context, cells, title_line: str | None, challenge_lead: bool) -> str:
    """`statement_text` + `markdown_blocks` per markdown cell, as `_item_body` renders the student
    edition, without Starter panels, asset listings or `**Your answer:**` placeholders."""
    parts = []
    lead_pending = challenge_lead
    for position, cell in enumerate(cells):
        if cell.cell_type != "markdown":
            continue
        text = statement_text(cell.source, position == 0, title_line)
        if lead_pending and text.strip():
            text, lead_pending = strip_challenge_lead(text.lstrip()), False
        if not text.strip():
            continue
        if ctx.kind == "project":
            text = re.sub(r"(?m)^## Milestone ", "### Milestone ", text)
        for paragraph in re.split(r"\n\s*\n", text.strip()):
            if not paragraph.strip() or PLACEHOLDER.match(paragraph):
                continue
            if re.match(r"^\*\*(?:Real version|No real version):\*\*", paragraph):
                if paragraph.startswith("**No real version:**"):
                    continue
                paragraph = re.sub(r"^\*\*(?:Real version|No real version):\*\*\s*", "", paragraph)
                paragraph = re.sub(r"(?i)^real program:\s*", "", paragraph)
                paragraph = strip_solution_pointer(paragraph)
                if paragraph[:1].islower():
                    paragraph = paragraph[0].upper() + paragraph[1:]
                parts.append(panel("realprog", paragraph))
            else:
                parts.append(markdown_blocks(paragraph, lesson_heading=ctx.lesson_heading))
    return "\n\n".join(part.rstrip() for part in parts) + ("\n" if parts else "")


def _item_files(ctx: _Context, text: str) -> list[str]:
    """Bundle paths of the tracked student files an item names (lesson assets, project data files)."""
    tracked = set(answers.tracked_paths(ctx.entry_dir))
    out = []
    for name in ASSET.findall(text):
        if name.startswith("solutions_") or SOLUTION_SOURCE.match(name):
            continue
        rel = f"assets/{name}"
        if rel in tracked and allowed_source(ctx.entry_dir / rel, "student"):
            out.append(f"files/{ctx.entry_dir.name}/{rel}")
    for name in DATA.findall(text):
        if name in tracked and allowed_source(ctx.entry_dir / name, "student"):
            out.append(f"files/{ctx.entry_dir.name}/{name}")
    return list(dict.fromkeys(out))


def _division_id(text: str) -> str:
    """`Junior and above` -> `junior` (the division the `_Division:` line starts at)."""
    match = re.match(r"[A-Za-z]+", text.strip())
    return match[0].lower() if match else text.strip().lower()


def _make_item(ctx: _Context, group: dict, *, kind: str, mode: str, label: str, title: str,
               title_line: str | None, challenge_lead: bool, before: list[dict], part: int | None,
               stretch: bool) -> Item:
    cells = group["cells"]
    heading = cells[0]
    key = ctx.key(heading, part)
    ctx.placement.append((key, f"item:{key}"))
    for cell in cells[1:]:
        ctx.placement.append((ctx.key(cell), f"item:{key}"))
    code = [cell for cell in cells if cell.cell_type == "code"
            and VERIFY_TAG not in cell.metadata.get("tags", []) and cell.source.strip()]
    starter = "\n\n".join(cell.source.rstrip() for cell in code)
    statement_source = "\n\n".join(cell.source for cell in cells if cell.cell_type == "markdown")
    return Item(
        key=key, kind=kind, number=group.get("number"), label=label, title=title,
        division=list(dict.fromkeys(_division_id(d) for d in item_divisions(group))),
        stretch=stretch, concepts=[],
        statement_md=_statement_md(ctx, cells, title_line, challenge_lead), starter=starter,
        files=_item_files(ctx, statement_source + "\n" + starter), heading_cell=heading,
        before=before, book=ctx.book, entry_dir=ctx.entry_dir, entry_kind=ctx.kind, mode=mode,
        notebook=ctx.stem, cells=cells, statement_source=statement_source)


def _numbered_item(ctx: _Context, group: dict, label: str, mode: str, before: list[dict]) -> Item:
    kind = {"exercise": "unit", "question": "checkpoint"}.get(mode, "project")
    stretch = any("stretch" in cell.metadata.get("tags", []) for cell in group["cells"])
    found = title_heading(group)
    title_line = found[1] if found else None
    lead = (mode == "exercise" and stretch and found is not None and found[0] == 0
            and OWN_TITLE.match(title_line.replace(" — Challenge", "")) is not None)
    return _make_item(ctx, group, kind=kind, mode=mode, label=f"{label} {group['number']}",
                      title=group_title(group, label), title_line=title_line, challenge_lead=lead,
                      before=before, part=None, stretch=stretch)


def _split_trailing(groups: list[dict]) -> tuple[list[dict], list]:
    """`item_groups` folds a trailing `## ` section after the last item into that item; the export
    keeps it out of the item, as `outro`."""
    if not groups:
        return groups, []
    last = groups[-1]
    for index, cell in enumerate(last["cells"][1:], 1):
        if cell.cell_type == "markdown" and SECTION.match(cell.source):
            trimmed = {**last, "cells": last["cells"][:index]}
            return [*groups[:-1], trimmed], last["cells"][index:]
    return groups, []


def _partition(cells, pattern: re.Pattern) -> tuple[list, list[dict], list]:
    """The export's project partition: (intro cells, item groups with `interlude`, outro cells).

    A markdown cell whose first line matches `pattern` starts an item. A markdown cell whose first
    line is a `## ` heading ends the current item; it and the cells after it wait for the next item
    (its `before`), or end in `outro`. Cells before the first item or `## ` heading are the intro.
    """
    intro, groups, pending = [], [], []
    current = None
    for cell in cells:
        first = cell.source.split("\n", 1)[0] if cell.cell_type == "markdown" else ""
        match = pattern.match(first) if first else None
        if match:
            current = {"number": int(match[1]), "cells": [cell], "interlude": pending}
            pending = []
            groups.append(current)
        elif first.startswith("## "):
            current = None
            pending.append(cell)
        elif current is not None:
            current["cells"].append(cell)
        elif not groups and not pending:
            intro.append(cell)
        else:
            pending.append(cell)
    return intro, groups, pending


def _lesson_heading(root: Path, book: str) -> str | None:
    return publication_config(root, book).lesson_heading if book_flag(root, book, "publication") else None


def entry_content(root: Path, book: str, entry_dir: Path, kind: str) -> EntryContent:
    """The entry's statement notebook as `EntryContent(intro, items, outro)`."""
    entry_dir = Path(entry_dir)
    stem = STEM[kind]
    path = entry_dir / f"{stem}.ipynb"
    missing = missing_id_findings(path)
    if missing:
        raise ValueError("\n".join(missing))
    notebook = nbformat.read(path, as_version=4)
    ctx = _Context(Path(root), book, entry_dir, kind, stem, _lesson_heading(root, book), [])
    items: list[Item] = []
    if kind in ("unit", "checkpoint"):
        label = "Exercise" if kind == "unit" else "Question"
        mode = "exercise" if kind == "unit" else "question"
        preface, groups = item_groups(notebook.cells, label)
        groups, trailing = _split_trailing(groups)
        intro = _side_blocks(ctx, preface, "intro")
        for group in groups:
            key = ctx.key(group["cells"][0])
            before = _side_blocks(ctx, group.get("interlude", []), f"before:{key}")
            items.append(_numbered_item(ctx, group, label, mode, before))
        if kind == "unit":
            lead_in, challenges = unit_challenges(notebook.cells)
            originals = {id(cell) for cell in notebook.cells}
            for position, challenge in enumerate(challenges):
                heading = challenge["cells"][0]
                part = None if id(heading) in originals else 2  # split out of a `## Challenge` note
                key = ctx.key(heading, part)
                before = _side_blocks(ctx, lead_in, f"before:{key}") if position == 0 else []
                title = _clean_title(challenge["title"]) if challenge["title"] else ""
                items.append(_make_item(ctx, challenge, kind="challenge", mode="challenge",
                                        label=f"Challenge {challenge['number']}", title=title,
                                        title_line=None, challenge_lead=True, before=before,
                                        part=part, stretch=True))
            if lead_in and not challenges:
                trailing = [*lead_in, *trailing]
        outro = _side_blocks(ctx, trailing, "outro")
    else:
        problems = any(cell.cell_type == "markdown" and PROBLEM.match(cell.source.split("\n", 1)[0])
                       for cell in notebook.cells)
        pattern, label, mode = (PROBLEM, "Problem", "problem") if problems else (
            MILESTONE, "Milestone", "milestone")
        preface, groups, trailing = _partition(notebook.cells, pattern)
        intro = _side_blocks(ctx, preface, "intro")
        for group in groups:
            key = ctx.key(group["cells"][0])
            before = _side_blocks(ctx, group["interlude"], f"before:{key}")
            items.append(_numbered_item(ctx, group, label, mode, before))
        outro = _side_blocks(ctx, trailing, "outro")
    answers.attach_solutions(items, entry_dir, kind)
    _attribute_concepts(ctx, items)
    for item in items:
        if item.solution_group is None:
            item.notes.append(f"{item.label}: no matching solution section (self-check)")
    return EntryContent(intro, items, outro, ctx.placement)


def _attribute_concepts(ctx: _Context, items: list[Item]) -> None:
    registry = _registry(ctx.root, ctx.book)
    registered = {c["id"] for c in registry}
    profile = scanner_profile(registry)
    allowed = _manifest_concepts(ctx.entry_dir) & registered

    def concepts_of(source: str) -> list[str]:
        return _cell_concepts(profile, registered, source)

    for item in items:
        authored = item.heading_cell.metadata.get("concepts")
        if isinstance(authored, list):
            item.concepts = list(dict.fromkeys(c for c in authored if isinstance(c, str)))
            continue
        found = set(concepts_of(item.starter)) if item.starter.strip() else set()
        found.update(answers.solution_concepts(item, concepts_of))
        item.concepts = sorted(found & allowed)
        if not item.concepts:
            item.notes.append("concepts: unattributed")


def entry_items(root: Path, book: str, entry_dir: Path, kind: str) -> list[Item]:
    return entry_content(root, book, entry_dir, kind).items


# --- the exported item -------------------------------------------------------------------------


@dataclass
class ItemExport:
    """An item as the bundle ships it (`data`, a schema `item`), with its classification and the
    report lines (`notes`)."""

    data: dict
    kind: str
    reason: str
    confirmed: bool
    notes: list[str]


def export_item(root: Path, book: str, item: Item) -> ItemExport:
    from .classify import item_kind

    kind, reason = item_kind(root, book, item)
    check, notes = answers._check(root, book, item, kind)
    data = {
        "key": item.key, "kind": item.kind, "number": item.number, "label": item.label,
        "title": item.title, "division": item.division, "stretch": item.stretch,
        "concepts": item.concepts, "statement_md": item.statement_md, "starter": item.starter,
        "files": item.files, "check": check, **answers.answer_fields(root, book, item),
        "before": item.before,
    }
    if kind == "self-check":
        notes = [f"self-check: {reason}", *notes]
    return ItemExport(data, kind, reason, check["confirmed"], [*item.notes, *notes])
