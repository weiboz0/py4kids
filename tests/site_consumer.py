"""A minimal bundle consumer: plain Python standing in for the site (design 012 part B; plan 101 F).

`render_bundle(bundle_dir, out_dir)` writes one HTML page per entry plus `index.html` and
`glossary.html`, reading the bundle only through fields the schema declares. `load` is the JSON
reader; the consumer test swaps in a recording reader to prove that.
"""

from __future__ import annotations

import ast
import html
import json
import re
from pathlib import Path

LATEX = re.compile(r"^```\{=latex\}\n.*?^```[ \t]*\n?", re.MULTILINE | re.DOTALL)
FENCE = re.compile(r"^```([^\n]*)\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
DIV = re.compile(r"^::: *\{\.([\w-]+)\} *$|^::: *$", re.MULTILINE)
CODE_TYPES = ("code", "tryit", "error-demo", "hang-demo", "turtle-figure", "program", "starter")
CONTROL = {  # the check control each kind shows
    "fixtures": "fixture-list", "answer": "answer-box", "asserts": "assert-summary",
    "expected-output": "expected-output-box", "predict": "predict-box", "self-check": "checklist",
}


def load_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def markdown(text: str) -> str:
    """Publisher Markdown to HTML: `{=latex}` blocks are dropped, `::: {.x}` panels become divs,
    fences become `<pre>` (a `{.python .answer-code}` fence keeps its classes), the rest is prose."""
    text = LATEX.sub("", text)
    out, last = [], 0
    for match in FENCE.finditer(text):
        out.append(_prose(text[last:match.start()]))
        info = match[1].strip()
        classes = " ".join(c.lstrip(".") for c in info.strip("{}").split()) if info else ""
        out.append(f'<pre class="{html.escape(classes)}">{html.escape(match[2])}</pre>')
        last = match.end()
    out.append(_prose(text[last:]))
    return "\n".join(part for part in out if part)


def _prose(text: str) -> str:
    def div(match):
        return f'<div class="{match[1]}">' if match[1] else "</div>"
    parts = []
    for paragraph in re.split(r"\n\s*\n", text.strip()):
        if not paragraph.strip():
            continue
        if DIV.fullmatch(paragraph.strip()):
            parts.append(DIV.sub(div, paragraph.strip()))
            continue
        lines = [DIV.sub(div, line) if DIV.fullmatch(line) else html.escape(line)
                 for line in paragraph.splitlines()]
        heading = re.match(r"(#{1,6}) (.*)", lines[0])
        if heading and len(lines) == 1:
            level = len(heading[1])
            parts.append(f"<h{level}>{heading[2]}</h{level}>")
        else:
            parts.append("<p>" + "<br>".join(lines) + "</p>")
    return "\n".join(parts)


def figure(segments) -> str:
    lines = "".join(f'<line x1="{s["x1"]}" y1="{-s["y1"]}" x2="{s["x2"]}" y2="{-s["y2"]}" '
                    f'stroke="{html.escape(s["color"])}" stroke-width="{s["width"]}"/>'
                    for s in segments)
    return f'<svg class="figure">{lines}</svg>'


def block(data) -> str:
    kind = data["type"]
    if kind not in CODE_TYPES:
        return f'<div class="{kind}" id="{html.escape(data["key"])}">{markdown(data["md"])}</div>'
    parts = [f'<pre class="{kind}">{html.escape(data["code"])}</pre>']
    if "output" in data:
        parts.append(f'<pre class="output">{html.escape(data["output"])}</pre>')
    if "figure" in data:
        parts.append(figure(data["figure"]))
    if data["needs_prelude"]:
        parts.append(f'<p class="prelude">runs after {len(data["prelude"])} earlier block(s)</p>')
    return f'<div class="block" id="{html.escape(data["key"])}">' + "".join(parts) + "</div>"


def check_control(check, bundle_dir: Path) -> str:
    kind = check["kind"]
    css = CONTROL[kind]
    if kind == "fixtures":
        rows = []
        for case in check["cases"]:
            sample = ""
            if case["sample"]:
                given = (bundle_dir / case["in_file"]).read_text(encoding="utf-8")
                sample = f"<pre>{html.escape(given)}</pre>"
            rows.append(f'<li>case {case["n"]} ({check["match"]} match){sample}</li>')
        return f'<ul class="{css}">{"".join(rows)}</ul>'
    if kind == "asserts":
        # D5: the assert source runs in the runner but is never printed; the page shows only the
        # functions checked and one pass/fail line per assert.
        names = ", ".join(check["functions"])
        total = len(ast.parse(check["source"]).body)
        results = "".join(f'<li class="assert-result" data-n="{n}">check {n} of {total}: '
                          f"not run yet</li>" for n in range(1, total + 1))
        return (f'<div class="{css}"><p>Checks: {html.escape(names)}</p>'
                f"<ol>{results}</ol></div>")
    if kind == "self-check":
        ticks = "".join(f'<li><input type="checkbox"> {html.escape(r)}</li>'
                        for r in check["requirements"])
        return f'<ul class="{css}">{ticks}</ul>'
    program = f'<pre>{html.escape(check["program"])}</pre>' if kind == "predict" else ""
    hint = html.escape(check["answer_format"]["hint"])
    return f'{program}<textarea class="{css}" placeholder="{hint}" data-hash="{check["hash"]}">' \
           f'</textarea>'


def item(data, bundle_dir: Path) -> str:
    parts = [block(b) for b in data["before"]]
    parts.append(f'<section class="item {data["kind"]}" id="{html.escape(data["key"])}">'
                 f'<h2>{html.escape(data["label"])}: {html.escape(data["title"])}</h2>')
    parts.append(markdown(data["statement_md"]))
    if data["starter"]:
        parts.append(f'<pre class="starter">{html.escape(data["starter"])}</pre>')
    parts.append(check_control(data["check"], bundle_dir))
    if data.get("also_check"):  # plan 102 Phase 0: a self-check list beside the automatic check
        ticks = "".join(f'<li><input type="checkbox"> {html.escape(r)}</li>'
                        for r in data["also_check"])
        parts.append(f'<ul class="also-check">{ticks}</ul>')
    if data["answer_visibility"] == "after-attempt":
        parts.append(f'<details class="answer"><summary>Answer</summary>'
                     f'{markdown(data["answer_md"])}</details>')
    return "\n".join(parts) + "</section>"


def card(data, blocks: dict) -> str:
    if data["kind"] == "predict":
        source = blocks[data["block"]]["code"]
        return f'<div class="card predict {data["mode"]}"><pre>{html.escape(source)}</pre></div>'
    options = "".join(f"<li>{html.escape(term)}</li>" for term in [data["term"], *data["distractors"]])
    return (f'<div class="card concept {data["mode"]}">{markdown(data["definition_md"])}'
            f"<ol>{options}</ol></div>")


def entry_page(entry, bundle_dir: Path) -> str:
    blocks = (entry["lesson"] or {"blocks": []})["blocks"]
    parts = [f'<h1>{html.escape(entry["entry"]["title"])}</h1>']
    parts += [block(b) for b in blocks]
    parts += [block(b) for b in entry["intro"]]
    parts += [item(i, bundle_dir) for i in entry["items"]]
    parts += [block(b) for b in entry["outro"]]
    by_key = {b["key"]: b for b in blocks}
    if entry["cards"]:
        parts.append('<div class="deck">' + "".join(card(c, by_key) for c in entry["cards"])
                     + "</div>")
    return "\n".join(parts)


def render_bundle(bundle_dir: Path, out_dir: Path, load=load_json) -> list[Path]:
    """Render every page of the bundle under `out_dir`; returns the written paths."""
    bundle_dir, out_dir = Path(bundle_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    book = load(bundle_dir / "book.json")
    written = []

    def write(name: str, title: str, body: str) -> None:
        path = out_dir / name
        path.write_text(f"<!doctype html><title>{html.escape(title)}</title>\n{body}\n",
                        encoding="utf-8")
        written.append(path)

    links = "".join(f'<li><a href="{e["id"]}.html">{html.escape(e["title"])}</a></li>'
                    for e in book["entries"])
    pdfs = "".join(f'<a href="{url}">{edition}</a>' for edition, url in (book["pdfs"] or {}).items())
    write("index.html", book["book"]["title"], f"<ul>{links}</ul>{pdfs}"
          f'<div class="reference">{markdown(book["reference_md"])}</div>')
    terms = "".join(f'<dt id="{g["concept"]}">{html.escape(g["term"])}</dt>'
                    f'<dd>{markdown(g["definition_md"])}</dd>' for g in book["glossary"])
    write("glossary.html", "Glossary", f'<dl class="glossary">{terms}</dl>')
    for record in book["entries"]:
        write(f'{record["id"]}.html', record["title"],
              entry_page(load(bundle_dir / record["file"]), bundle_dir))
    return written
