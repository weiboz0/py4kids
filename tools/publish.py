"""Turn a `publication: true` book's notebook sources into a Quarto book project."""
from __future__ import annotations

import ast
import builtins
import io
import json
import keyword
import re
import shutil
import tokenize
from contextlib import redirect_stdout
from pathlib import Path

import nbformat
import yaml

from tools.books import (
    PublicationConfig,
    book_entry,
    book_flag,
    book_path,
    book_subtitle,
    book_title,
    output_pdf_name,
    publication_config,
)
from tools.fake_turtle import imports_turtle
from tools.turtle_figure import figure_tikz
from tools.turtle_real import real_programs

THEME = Path(__file__).with_name('publish_theme')
NOTICE = re.compile(r'^(?:\*\*Notice:\*\*|Notice:|#{3,6} .*\bNotice\b)', re.IGNORECASE)
ASSET = re.compile(r'assets/([\w-]+\.py)')
DATA = re.compile(r'\b(p\d+[a-z]?_[\w-]+\.txt)\b')
ITEM = {'unit': 'Exercise', 'checkpoint': 'Question', 'project': 'Problem'}
# Solution programs under assets/ (design 010 D3): unit exN.py, checkpoint qN.py, project pN.py.
# `exN_name.py` starters are not solution sources. assets/verify/** is solution material too.
SOLUTION_SOURCE = re.compile(r'^(ex|q|p)\d+\.py$')
SOLUTION_PREFIX = {'unit': 'ex', 'checkpoint': 'q', 'project': 'p'}
# Structural subsections of an item statement (matched by prefix: "Sample Input 1" is structural).
STRUCTURAL = re.compile(r'^(?:Input|Output|Constraints|Sample Input|Sample Output|Example)(?:\s+\d+)?\s*$')
DIVISION = re.compile(r'^_Division:\s*(.+?)\.?_[ \t]*$', re.MULTILINE)
PLACEHOLDER = re.compile(r'^\*\*Your answer:\*\*')
VERIFY_TAG = 'verify'
STDIN_NOTE = ('This program reads its input from a file. To try it, save it as a `.py` file and run it '
              'with a sample input file: `python program.py < input.txt`.')

# One profile per edition drives the builder, the theme, scripts/build-book.sh and the audit.
# Every edition's PDF is named `<book id>-<edition>.pdf` (tools.books.output_pdf_name).
#   student_family    no teacher material; independence rules apply
#   starters          'all' prints every non-empty Starter; 'required' omits redundant ones (D1 rule)
#   answers_appendix  "Answers to Selected Exercises" after the units
#   answer_refs       "Answer on page N" lines and page cross-references between exercise and answer
#   body              'book' (front matter, units, back matter) or 'answers' (the Answer Key)
#   front             front-matter Markdown files; the first becomes index.qmd
#   back_matter       Glossary and Quick Reference
#   index             an index (makeindex step and the Index chapter)
EDITIONS = {
    'student-print': {
        'student_family': True, 'starters': 'required', 'answers_appendix': False,
        'answer_refs': False, 'classoption': 'open=any',
        'edition_label': 'Student Book — Print Edition', 'index': True, 'body': 'book',
        'front': ('preface.md', 'how-to-use.md'), 'back_matter': True},
    'student': {
        'student_family': True, 'starters': 'all', 'answers_appendix': True,
        'answer_refs': True, 'classoption': 'open=right',
        'edition_label': 'Student Book — Full Edition', 'index': True, 'body': 'book',
        'front': ('preface.md', 'how-to-use.md'), 'back_matter': True},
    'answer-key': {
        'student_family': True, 'starters': 'none', 'answers_appendix': False,
        'answer_refs': False, 'classoption': 'open=any',
        'edition_label': 'Answer Key', 'index': False, 'body': 'answers',
        'front': ('answer-key-intro.md',), 'back_matter': False},
    'teacher': {
        'student_family': False, 'starters': 'all', 'answers_appendix': False,
        'answer_refs': False, 'classoption': 'open=right',
        'edition_label': "Teacher's Edition", 'index': True, 'body': 'book',
        'front': ('preface.md', 'how-to-use.md', 'for-teachers.md'), 'back_matter': True},
}
# The setup chapter's source is allowed too; its name comes from the book's publication.yaml.
STUDENT_SOURCES = {'lesson.ipynb', 'exercises.ipynb', 'checkpoint.ipynb', 'brief.ipynb', 'syllabus.md',
                   'how-to-use.md', 'preface.md', 'glossary.md', 'quick-reference.md'}
# The Answer Key reads its front matter, the unit and exercise titles, and (only through
# student_answer_sources) the odd-numbered unit solutions.
ANSWER_KEY_SOURCES = {'syllabus.md', 'answer-key-intro.md', 'lesson.ipynb', 'exercises.ipynb'}
EDITION_MARK = re.compile(r'<!--\s*/?\s*edition\b')


def output_stem(book_id: str, edition: str) -> str:
    """The Quarto output-file stem of an edition: `<book id>-<edition>` (one naming helper)."""
    return output_pdf_name(book_id, edition).removesuffix('.pdf')


def profile(edition: str) -> dict:
    if edition not in EDITIONS:
        raise ValueError(f"edition must be one of {', '.join(EDITIONS)}")
    return EDITIONS[edition]


def filter_edition_blocks(text: str, edition: str, source: str = 'front matter') -> str:
    """Keep shared text and the blocks marked for this edition; drop the marker lines.

    `<!-- edition: NAME -->` (or `NAME|NAME`) opens a block and `<!-- /edition -->` closes it. A marker
    and every excluded line vanish entirely, so a block inside a list leaves no blank line behind; a
    dropped paragraph-level block leaves one blank line, not two.
    An unknown edition name, a malformed, nested, stray or unclosed marker fails the build.
    """
    out: list[str] = []
    active: list[str] | None = None
    opened = 0
    dropped = False  # a line was dropped since the last kept non-blank line
    for number, line in enumerate(text.splitlines(keepends=True), 1):
        if EDITION_MARK.search(line):
            dropped = True
            stripped = line.strip()
            if stripped == '<!-- /edition -->':
                if active is None:
                    raise ValueError(f'FAIL: {source}:{number}: edition block closed but never opened')
                active = None
                continue
            match = re.fullmatch(r'<!-- edition: ([a-z-]+(?: *\| *[a-z-]+)*) -->', stripped)
            if not match:
                raise ValueError(f'FAIL: {source}:{number}: malformed edition marker: {stripped}')
            if active is not None:
                raise ValueError(f'FAIL: {source}:{number}: edition block opened inside line {opened}')
            names = [name.strip() for name in match[1].split('|')]
            unknown = [name for name in names if name not in EDITIONS]
            if unknown:
                raise ValueError(f"FAIL: {source}:{number}: unknown edition {', '.join(unknown)}")
            active, opened = names, number
            continue
        if active is None or edition in active:
            if not line.strip():
                if dropped and out and not out[-1].strip():
                    continue
            else:
                dropped = False
            out.append(line)
        else:
            dropped = True
    if active is not None:
        raise ValueError(f'FAIL: {source}:{opened}: edition block never closed')
    return ''.join(out)


def starter_code_lines(source: str) -> list[str]:
    """A Starter's non-comment, non-`pass` lines, stripped of indentation."""
    return [line.strip() for line in source.splitlines()
            if line.strip() and not line.strip().startswith('#') and line.strip() != 'pass']


def redundant_starter(source: str, statement: str) -> bool:
    """Print-edition rule: a Starter is redundant when it has no code lines, or when every code line
    appears verbatim in the item's statement (its markdown cells only)."""
    return all(line in statement for line in starter_code_lines(source))


def allowed_source(path: Path, edition: str, setup_source: str | None = None) -> bool:
    """Single gate for every source read by the student-family builders.

    `setup_source` is the book's setup chapter (publication.yaml `setup.source`), allowed by name.
    """
    if edition == 'teacher':
        return True
    if edition not in EDITIONS:
        return False
    if 'teacher-notes' in path.name or path.name == 'solutions.ipynb':
        return False
    if path.parts and path.parts[-1].startswith('solutions_'):
        return False
    if is_solution_source(path):
        return False
    if edition == 'answer-key':
        return path.name in ANSWER_KEY_SOURCES
    if path.name in STUDENT_SOURCES or (setup_source and path.name == Path(setup_source).name):
        return True
    return (path.suffix == '.py' and 'units' in path.parts and 'assets' in path.parts) or (
        path.suffix == '.txt' and 'projects' in path.parts)


def is_solution_source(path: Path) -> bool:
    """`assets/exN.py`, `assets/qN.py`, `assets/pN.py` and anything under `assets/verify/` (design 010 D3).

    They reach a student edition only as odd unit answers, through `student_answer_sources`
    (as the solution notebook's mirror cell); they are never printed as files.
    """
    parts = Path(path).parts
    if 'assets' not in parts:
        return False
    below = parts[len(parts) - 1 - parts[::-1].index('assets') + 1:]
    return bool(SOLUTION_SOURCE.match(Path(path).name)) or (len(below) > 1 and below[0] == 'verify')


def read_source(path: Path, edition: str, setup_source: str | None = None) -> str:
    if not allowed_source(path, edition, setup_source):
        raise ValueError(f'{edition} source boundary: {path}')
    return path.read_text(encoding='utf-8')


def notebook(path: Path, edition: str):
    if not allowed_source(path, edition):
        raise ValueError(f'{edition} source boundary: {path}')
    return nbformat.read(path, as_version=4)


def turtle_picture(source: str, stdin: str | None = None,
                   caption: str = 'Drawing made by the program above') -> str:
    with redirect_stdout(io.StringIO()):
        return figure_tikz(source, stdin=stdin, caption=caption)


def panel(kind: str, body: str) -> str:
    return f'::: {{.{kind}}}\n{body.strip()}\n:::\n'


def strip_turtle_directives(source: str) -> str:
    return ''.join(line for line in source.splitlines(keepends=True)
                   if not re.match(r'^\s*# turtle-check:', line))


def demote_sections(source: str, lesson_heading: str | None) -> str:
    """Demote every `## ` line to `### ` except lesson headings (the book's `lesson_heading` regex),
    `## Exercises` and `## Answer key`."""
    lesson = re.compile(lesson_heading) if lesson_heading else None
    lines = source.split('\n')
    for index, line in enumerate(lines):
        if (line.startswith('## ') and not re.match(r'## (?:Exercises|Answer key)\b', line)
                and not (lesson and lesson.match(line))):
            lines[index] = '### ' + line[3:]
    return '\n'.join(lines)


def fenced_paragraphs(source: str) -> list[str]:
    """Split Markdown on blank lines outside code fences; a fenced block keeps its blank lines."""
    paragraphs: list[str] = []
    current: list[str] = []
    fenced = False
    for line in source.split('\n'):
        if line.lstrip().startswith('```'):
            fenced = not fenced
        if not fenced and not line.strip() and not line.lstrip().startswith('```'):
            if current:
                paragraphs.append('\n'.join(current))
                current = []
            continue
        current.append(line)
    if current:
        paragraphs.append('\n'.join(current))
    return paragraphs or ['']


def markdown_blocks(source: str, first: bool = False, demote: bool = True,
                    lesson_heading: str | None = None, keep_fences: bool = False) -> str:
    """Split a markdown cell into paragraphs while preserving Notice continuations.

    With `demote`, `## ` sections become `### ` except the book's lesson headings (`lesson_heading`,
    from publication.yaml), `## Exercises` and `## Answer key`. With `keep_fences` (answers), a code
    fence is never split, so its blank lines print as written.
    """
    source = strip_turtle_directives(source)
    for title, kind in (('### You will learn', 'goals'), ('### Recap', 'recap')):
        if source.startswith(title + '\n') or source.strip() == title:
            return panel(kind, source[len(title):])
    if demote:
        source = demote_sections(source, lesson_heading)
    paragraphs = fenced_paragraphs(source.strip()) if keep_fences else re.split(r'\n\s*\n', source.strip())
    out = []
    if first and paragraphs and paragraphs[0].startswith('# '):
        out.append(paragraphs.pop(0))
        hook = []
        while paragraphs and not paragraphs[0].startswith('#'):
            hook.append(paragraphs.pop(0))
        if hook:
            out.append(panel('opener', '\n\n'.join(hook)))
    i = 0
    while i < len(paragraphs):
        p = paragraphs[i]
        if NOTICE.match(p):
            notice = re.sub(r'^(?:\*\*Notice:\*\*|Notice:)\s*', '', p, count=1, flags=re.IGNORECASE)
            if notice and notice[0].islower():
                notice = notice[0].upper() + notice[1:]
            contents = [notice]
            i += 1
            while i < len(paragraphs) and not paragraphs[i].startswith('#'):
                contents.append(paragraphs[i]); i += 1
            out.append(panel('notice', '\n\n'.join(contents)))
        else:
            out.append(p)
            i += 1
    return '\n\n'.join(out) + '\n'


def code_block(source: str) -> str:
    source = strip_turtle_directives(source)
    return '```python\n' + source + ('' if source.endswith('\n') else '\n') + '```\n'


def code_tokens(source: str) -> tuple[tuple[int, str], ...]:
    """Compare Python code while ignoring comments, blank lines, and spacing."""
    ignored = {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
               tokenize.ENCODING, tokenize.ENDMARKER}
    return tuple((token.type, token.string) for token in tokenize.generate_tokens(
        io.StringIO(source).readline) if token.type not in ignored)


def reads_stdin(source: str) -> bool:
    """A stdin program reads `sys.stdin` or `open(0)` (design 010 F1; shared with the audit)."""
    return re.search(r'\bsys\.stdin\b|(?<![\w.])open\(\s*0\s*[,)]', source) is not None


def route_code(cell) -> tuple[str, str]:
    """One deterministic route per lesson code cell: the error-demo and hang-demo tags first, then a
    stdin program, then turtle programs and `input(` Try-its."""
    tags = cell.metadata.get('tags', [])
    source = cell.source
    if 'no-exec' in tags:
        if 'error-demo' in tags:
            return 'errordemo', panel('errordemo', code_block(source))
        if 'hang-demo' in tags:
            return 'hangdemo', panel('hangdemo', code_block(source))
        if reads_stdin(source):
            return 'tryit-stdin', panel('tryit', code_block(source) + '\n' + STDIN_NOTE)
        if re.search(r'(^|\n)\s*(?:import turtle|from turtle import)', source) and 'input(' in source:
            body = panel('tryit', code_block(source))
            if 'sample_input' in cell.metadata:
                sample = cell.metadata['sample_input']
                stdin = '\n'.join(sample.split(' | ')) + '\n'
                body += ('\n```{=latex}\n'
                         + turtle_picture(source, stdin=stdin, caption=f'Drawing for the sample input: {sample}')
                         + '\n```\n')
            return 'tryit+figure', body
        if re.search(r'(^|\n)\s*(?:import turtle|from turtle import)', source):
            return 'figure', panel('program', code_block(source))
        if 'input(' in source:
            return 'tryit', panel('tryit', code_block(source))
        return 'program', panel('program', code_block(source))
    output = ''.join(o.get('text', '') for o in cell.outputs if o.get('output_type') == 'stream')
    body = code_block(source)
    if output:
        body += '\n' + panel('output', '```text\n' + output.rstrip() + '\n```')
        return 'code+output', panel('codeoutput', body)
    return 'code', body


def teacher_notes(source: str) -> str:
    lines = strip_turtle_directives(source).splitlines()
    if lines and lines[0].startswith('# '):
        lines.pop(0)
    body = '\n'.join(lines)
    body = re.sub(r'^(#{1,4}) ', lambda m: '#' * (len(m[1]) + 2) + ' ', body, flags=re.MULTILINE)
    body = re.sub(r'\bfor CI\b', '', body)
    body = body.replace('60-MINUTE CUT', '60-minute cut')
    body = body.replace('`/`', '` / `')
    body = re.sub(r'(?m)([^\n])\n(?=\s*(?:[-*+]\s|\d+[.)]\s))', r'\1\n\n', body)
    escaped_lines = []
    fenced = False
    for line in body.splitlines():
        if line.lstrip().startswith('```'):
            fenced = not fenced
        if not fenced:
            spans = re.split(r'(`[^`]*`)', line)
            line = ''.join(span if index % 2 else re.sub(
                r'(?<!\\)\\([nrt])', lambda match: '\\\\' + match[1], span)
                for index, span in enumerate(spans))
        escaped_lines.append(line)
    return panel('teacher', '\n'.join(escaped_lines))


def strip_asserts(source: str) -> tuple[str, bool]:
    lines = source.splitlines()
    kept = [line for line in lines if not re.match(r'^\s*assert\s+', line)]
    return '\n'.join(kept).strip(), len(kept) != len(lines)


def check_text(source: str, expression: ast.expr) -> tuple[str, str]:
    """Split an assert test into what is evaluated and the value it must give.

    `A == B` and `A is B` check that A gives B; `not X` checks that X gives False; anything else
    (a call, a name, `a < b`, `x in y`, `A != B`) checks that the whole expression gives True.
    """
    def one_line(node: ast.expr) -> str:
        return re.sub(r'\s+', ' ', ast.get_source_segment(source, node)).strip()

    if (isinstance(expression, ast.Compare) and len(expression.ops) == 1
            and isinstance(expression.ops[0], (ast.Eq, ast.Is))):
        return one_line(expression.left), one_line(expression.comparators[0])
    if isinstance(expression, ast.UnaryOp) and isinstance(expression.op, ast.Not):
        return one_line(expression.operand), 'False'
    return one_line(expression), 'True'


def render_solution_code(source: str) -> str:
    """Replace only top-level asserts with in-order checks."""
    lines = source.splitlines(keepends=True)
    checks = [node for node in ast.parse(source).body if isinstance(node, ast.Assert)]
    rendered = []
    start = 0
    for node in checks:
        fragment = ''.join(lines[start:node.lineno - 1])
        if fragment.strip():
            rendered.append(code_block(fragment).replace('```python', '```{.python .answer-code}', 1))
        evaluated, value = check_text(source, node.test)
        rendered.append(f'Check: `{evaluated}` → `{value}`\n')
        start = node.end_lineno
    fragment = ''.join(lines[start:])
    if fragment.strip():
        rendered.append(code_block(fragment).replace('```python', '```{.python .answer-code}', 1))
    return '\n'.join(rendered)


def entries(book: Path, edition: str) -> list[tuple[str, Path]]:
    """Shipped entries in syllabus order: rows `| `id` |`, optionally after a leading `| # |` column."""
    syllabus = read_source(book / 'syllabus.md', edition)
    ids = re.findall(r'^\| (?:\d+ +\| )?`((?:unit|checkpoint|project)-[^`]+)` \|', syllabus, flags=re.MULTILINE)
    if not ids:
        raise ValueError('syllabus has no shipped entries')
    return [(id_, book / ('units' if id_.startswith('unit-') else 'checkpoints' if id_.startswith('checkpoint-') else 'projects') / id_) for id_ in ids]


def asset_blocks(text: str, entry: Path, edition: str, seen: set[str], unit: str,
                 rendered_turtles: set[tuple[tuple[int, str], ...]] | None = None) -> tuple[str, list[dict]]:
    rendered = []
    records = []
    for name in ASSET.findall(text):
        if name.startswith('solutions_') or SOLUTION_SOURCE.match(name) or name in seen:
            continue
        path = entry / 'assets' / name
        if path.exists():
            seen.add(name)
            source = read_source(path, edition)
            if rendered_turtles is not None and code_tokens(source) in rendered_turtles:
                rendered.append(f'This program is saved as assets/{name}.')
                records.append({'id': f'asset:{name}', 'kind': 'asset reference'})
                continue
            rendered.append(panel('program', f'**assets/{name}**\n\n{code_block(source)}'))
            records.append({'id': f'asset:{name}', 'kind': 'asset listing'})
            if re.search(r'(^|\n)\s*(?:import turtle|from turtle import)', source):
                try:
                    rendered.append('```{=latex}\n' + turtle_picture(source) + '\n```')
                except Exception as error:
                    raise ValueError(f'FAIL: {unit}: turtle figure for asset {name}: {error}') from error
    return '\n\n'.join(block.rstrip() for block in rendered) + ('\n' if rendered else ''), records


def item_groups(cells, label: str):
    pattern = re.compile(r'^## ' + label + r' (\d+)\b') if label != 'Problem' else re.compile(r'^#{2,3} Problem (\d+)\b')
    groups = []
    current = None
    preface = []
    interlude = []
    for cell in cells:
        match = pattern.match(cell.source) if cell.cell_type == 'markdown' else None
        if match:
            current = {'number': int(match[1]), 'cells': [cell], 'interlude': interlude}
            interlude = []
            groups.append(current)
        elif current is None:
            preface.append(cell)
        elif (label != 'Problem' and cell.cell_type == 'markdown'
              and re.match(r'^## (?!#)', cell.source)):
            # A section note between items (e.g. "## Challenge") introduces the NEXT item.
            interlude.append(cell)
        elif interlude:
            interlude.append(cell)
        else:
            current['cells'].append(cell)
    if interlude and groups:
        groups[-1]['cells'].extend(interlude)
    return preface, groups


def _clean_title(title: str) -> str:
    title = title.replace(' — Challenge', '')
    title = re.sub(r'\s*\*\([^()\n]*\)\*\s*$', '', title)  # a `*(topic)*` tag stays out of headings
    return re.sub(r'^Challenge(?: \d+)?:\s*', '', title).strip()


def structural(heading: str) -> bool:
    """`Input`, `Output`, `Constraints`, `Sample Input`, `Sample Output`, `Example`, optionally numbered."""
    return STRUCTURAL.match(heading.strip()) is not None


def title_heading(group) -> tuple[int, str] | None:
    """The (cell index, `### ` line) that supplies an item's title, or None.

    A `### Problem N — Title` item heading supplies its own title. Otherwise the title is the first
    `###` heading after the item heading line that is not a structural subsection.
    """
    for index, c in enumerate(group['cells']):
        if c.cell_type != 'markdown':
            continue
        source = c.source
        if index == 0:
            first, _, source = source.partition('\n')
            own = re.match(r'^#{2,3} Problem \d+ — (.+)$', first.replace(' — Challenge', ''))
            if own:
                return 0, first
        for line in source.split('\n'):
            if line.startswith('### ') and not structural(line[4:]):
                return index, line
    return None


def group_title(group, label: str) -> str:
    found = title_heading(group)
    if found is None:
        return ''
    line = found[1]
    own = re.match(r'^#{2,3} Problem \d+ — (.+)$', line.replace(' — Challenge', ''))
    return _clean_title(own[1] if own else line[4:])


def item_divisions(group) -> list[str]:
    """`_Division: X and above._` lines of an item (judge books) — printed as a division tag."""
    return [match for c in group['cells'] if c.cell_type == 'markdown'
            for match in DIVISION.findall(c.source)]


def _prose(paragraph: str) -> bool:
    return not (paragraph.startswith(('```', '- ', '* ', '+ ', '|', ':::', '#', '>', '$$'))
                or re.match(r'\d+[.)] ', paragraph))


def structural_subheads(text: str) -> str:
    """Structural `### Input` / `### Sample Input 1` sections become unnumbered run-in subheads: a bold
    label run into a following prose paragraph, or a bold label line before a list or code block."""
    if not re.search(r'(?m)^### ', text):
        return text
    paragraphs = re.split(r'\n\s*\n', text.strip())
    out = []
    index = 0
    while index < len(paragraphs):
        paragraph = paragraphs[index]
        match = re.match(r'^### ([^\n]+)(?:\n|$)', paragraph)
        if not match or not structural(match[1]):
            out.append(paragraph)
            index += 1
            continue
        name = match[1].strip()
        rest = paragraph[match.end():]
        if rest.strip():
            follow, index = rest, index + 1
        elif index + 1 < len(paragraphs):
            follow, index = paragraphs[index + 1], index + 2
        else:
            follow, index = None, index + 1
        if follow is not None and _prose(follow):
            out.append(f'**{name}.** {follow}')
        else:
            out.append(f'**{name}**')
            if follow is not None:
                out.append(follow)
    return '\n\n'.join(out)


def statement_text(source: str, heading_cell: bool, title_line: str | None) -> str:
    """An item cell's statement text: the item heading line, division lines and the title heading go
    (a leading non-structural `###` line is the old per-cell title rule); structural sections become
    run-in subheads."""
    text = source
    if heading_cell:
        text = text.partition('\n')[2].lstrip()
    if DIVISION.search(text):
        text = DIVISION.sub('', text).lstrip()
    leading = re.match(r'^### ([^\n]+)\n*', text)
    if leading and not structural(leading[1]):
        text = text[leading.end():]
    elif title_line and title_line.startswith('### '):
        lines = text.split('\n')
        if title_line in lines:
            lines.remove(title_line)
            text = '\n'.join(lines)
    return structural_subheads(text)


def strip_solution_pointer(paragraph: str) -> str:
    """Drop a Student Book "— see the solution" tail and keep the sentence's full stop."""
    paragraph, stripped = re.subn(r'\s*—\s*see (?:the )?solution[^.]*\.?', '', paragraph, flags=re.IGNORECASE)
    if stripped and paragraph and not re.search(r'[.!?:][*_"\'”’]*$', paragraph):
        paragraph += '.'
    return paragraph


def render_items(path: Path, kind: str, edition: str, entry: Path, unit: str,
                 config: PublicationConfig | None = None):
    edition_profile = profile(edition)
    lesson_heading = config.lesson_heading if config else None
    n = notebook(path, edition)
    label = ITEM[kind]
    preface, groups = item_groups(n.cells, label)
    out = []
    inventory = []
    seen_assets: set[str] = set()
    for c in preface:
        if kind != 'unit' and c is n.cells[0]:
            continue
        if c.cell_type == 'markdown':
            # The notebook H1 is replaced by the chapter H1.
            text = re.sub(r'^# [^\n]*', '', c.source).strip()
            if text:
                if kind == 'project':
                    text = re.sub(r'(?m)^## Milestone ', '### Milestone ', text)
                out.append(markdown_blocks(text, lesson_heading=lesson_heading))
    for group in groups:
        for c in group.get('interlude', []):
            text = c.source.strip()
            if text:
                out.append(markdown_blocks(re.sub(r'^## ', '### ', text), lesson_heading=lesson_heading))
        number = group['number']
        stretch = any('stretch' in c.metadata.get('tags', []) for c in group['cells'])
        title = group_title(group, label)
        display = (f'Challenge — {title}' if stretch and kind == 'unit' else
                   f'{label} {number}' + (f' — {title}' if title else ''))
        out.append(('#### ' if kind == 'project' else '### ') + display + '\n')
        if kind == 'unit':
            out.append(f'```{{=latex}}\n\\label{{ex:{entry.name}:{number}}}\n```')
        for division in item_divisions(group):
            out.append(f'[Division: {division}]{{.division}}')
        if stretch:
            out.append(panel('challenge', f'**{label} {number}**'))
        statement = '\n'.join(c.source for c in group['cells'] if c.cell_type == 'markdown')
        found = title_heading(group)
        title_line = found[1] if found else None
        for position, c in enumerate(group['cells']):
            if c.cell_type == 'code':
                if VERIFY_TAG in c.metadata.get('tags', []):
                    inventory.append({'id': c.id, 'kind': 'verify-omitted'})
                    continue
                if edition_profile['starters'] == 'required' and redundant_starter(c.source, statement):
                    inventory.append({'id': c.id, 'kind': 'starter-omitted'})
                    continue
                if c.source.strip():
                    out.append(panel('starter', code_block(c.source)))
                inventory.append({'id': c.id, 'kind': 'starter'})
                continue
            text = statement_text(c.source, position == 0, title_line)
            if position == 0 and not text.strip():
                continue
            if kind == 'project':
                text = re.sub(r'(?m)^## Milestone ', '### Milestone ', text)
            # Real-version lines become a distinct note; keep the rest of the cell.
            parts = []
            for paragraph in re.split(r'\n\s*\n', text.strip()):
                if PLACEHOLDER.match(paragraph):
                    continue  # judge books: no answer lines (design 007); students work elsewhere
                if re.match(r'^\*\*(?:Real version|No real version):\*\*', paragraph):
                    no_real = paragraph.startswith('**No real version:**')
                    paragraph = re.sub(r'^\*\*(?:Real version|No real version):\*\*\s*', '', paragraph)
                    paragraph = re.sub(r'(?i)^real program:\s*', '', paragraph)
                    if no_real:
                        continue
                    if edition_profile['student_family']:
                        paragraph = strip_solution_pointer(paragraph)
                    if paragraph[:1].islower():
                        paragraph = paragraph[0].upper() + paragraph[1:]
                    parts.append(panel('realprog', paragraph))
                else:
                    parts.append(markdown_blocks(paragraph, lesson_heading=lesson_heading))
            out.extend(parts)
            assets, records = asset_blocks(text, entry, edition, seen_assets, unit)
            if assets:
                out.append(assets); inventory.extend(records)
            if kind == 'project':
                for name in dict.fromkeys(DATA.findall(text)):
                    file = entry / name
                    if file.exists():
                        out.append(panel('datafile', f'**{name}**\n\n```text\n{read_source(file, edition).rstrip()}\n```'))
                        inventory.append({'id': f'data:{name}', 'kind': 'asset listing'})
        if kind == 'unit' and edition_profile['answer_refs'] and number % 2:
            out.append(f'Answer on page \\pageref{{ans:{entry.name}:{number}}}.')
    return '\n\n'.join(block.rstrip() for block in out) + '\n', inventory, [{'number': g['number'], 'title': group_title(g, label)} for g in groups]


def solution_assets(entry: Path, number: int) -> list[Path]:
    """The printed solution assets of one exercise (`solutions_exN*.py`, including named variants,
    without matching 10 for 1). A solution source (`exN.py`, `qN.py`, `pN.py`) is never one: its
    solution notebook's mirror cell is printed instead, once."""
    return [path for path in sorted((entry / 'assets').glob('solutions_ex*.py'))
            if re.match(rf'solutions_ex{number}(?!\d)', path.stem) and not is_solution_source(path)
            ] if (entry / 'assets').exists() else []


def solution_source_files(entry: Path, kind: str, number: int) -> list[Path]:
    """An item's judge solution file (`assets/exN.py`, `qN.py` or `pN.py`) — a boundary object only:
    the leak guard treats its body as hidden solution material."""
    path = entry / 'assets' / f'{SOLUTION_PREFIX[kind]}{number}.py'
    return [path] if path.is_file() else []


def student_answer_sources(entry: Path):
    """The only solution-material read allowed for the Student Book."""
    if 'units' not in entry.parts or not entry.name.startswith('unit-'):
        return [], {}
    solution = entry / 'solutions.ipynb'
    if not solution.exists():
        raise ValueError(f'missing solutions: {solution}')
    _, groups = item_groups(nbformat.read(solution, as_version=4).cells, 'Exercise')
    odd = [group for group in groups if group['number'] % 2]
    return odd, {group['number']: solution_assets(entry, group['number']) for group in odd}


def answer_key(entry: Path, kind: str, items: list[dict], edition: str = 'teacher') -> str:
    """Teacher: every item's solution. Student family: odd unit exercises via student_answer_sources."""
    label = ITEM[kind]
    edition_profile = profile(edition)
    student = edition_profile['student_family']
    if student and not any(item['number'] % 2 for item in items):
        return ''
    if student:
        if kind != 'unit':
            raise ValueError('student answers are unit exercises only')
        groups, assets = student_answer_sources(entry)
        items = [item for item in items if item['number'] % 2]
    else:
        n = notebook(entry / 'solutions.ipynb', 'teacher')
        _, groups = item_groups(n.cells, label)
        assets = {item['number']: solution_assets(entry, item['number']) for item in items}
    by_number = {g['number']: g for g in groups}
    out = [] if student else ['## Answer key\n']
    for item in items:
        number = item['number']
        if number not in by_number:
            raise ValueError(f'{entry}: missing solution {label} {number}')
        heading = f'{label} {number}' + (f" — {item['title']}" if item['title'] and kind != 'project' else '')
        if student:
            unit_number = int(re.search(r'unit-(\d+)', entry.name)[1])
            heading = f'Unit {unit_number}, {label} {number}'
            if not edition_profile['answer_refs'] and item['title']:
                heading += f" — {item['title']}"
        refs = kind == 'unit' and (edition_profile['answer_refs'] or not student)
        page = f' (page \\pageref{{ex:{entry.name}:{number}}})' if refs else ''
        out.append('### ' + heading + page + '\n')
        if refs:
            out.append(f'```{{=latex}}\n\\label{{ans:{entry.name}:{number}}}\n```')
        real_figures = []
        if kind == 'unit':
            for program, sample in real_programs(by_number[number]):
                if imports_turtle(program) and sample is not None:
                    real_figures.append((program, sample))
        for c in by_number[number]['cells'][1:]:
            if c.cell_type == 'code':
                if VERIFY_TAG in c.metadata.get('tags', []):
                    continue  # verify cells are checks, never printed (design 010 D3)
                if (re.search(r'\brun_path\s*\(\s*["\']assets/solutions_ex', c.source)
                        and 'fake_turtle' in c.source):
                    continue
                # A judge item's mirror cell (identical to assets/exN.py, qN.py or pN.py) prints here, once.
                out.append(render_solution_code(c.source))
            elif c.cell_type == 'markdown':
                text = re.sub(r'^### [^\n]+\n*', '', c.source).strip()
                if text:
                    # Worked answers and their `**Answer:**` line, through the same Markdown rules.
                    text = markdown_blocks(text, keep_fences=True).rstrip()
                    text = text.replace('```python', '```{.python .answer-code}')
                    out.append(text + '\n')
        for program, sample in real_figures:
            try:
                caption = 'Drawing for the sample input: ' + ', '.join(sample.splitlines())
                out.append('```{=latex}\n' + turtle_picture(program, stdin=sample + '\n', caption=caption)
                           + '\n```\n')
            except Exception as error:
                raise ValueError(f'FAIL: {entry.name}: real-program figure for {label} {number}: {error}') from error
        for file in assets[number]:
            source = (file.read_text(encoding='utf-8') if student
                      else read_source(file, 'teacher'))
            out.append(panel('program', f'**{file.name}**\n\n{code_block(source).replace("```python", "```{.python .answer-code}", 1)}'))
            if 'import turtle' in source or 'from turtle import' in source:
                try:
                    out.append('```{=latex}\n' + turtle_picture(source) + '\n```')
                except Exception as error:
                    raise ValueError(f'FAIL: {entry.name}: turtle figure for asset {file.name}: {error}') from error
    return '\n\n'.join(block.rstrip() for block in out) + '\n'


def render_chapter(entry: Path, kind: str, edition: str, config: PublicationConfig | None = None):
    lesson_heading = config.lesson_heading if config else None
    source = entry / ('lesson.ipynb' if kind == 'unit' else 'checkpoint.ipynb' if kind == 'checkpoint' else 'brief.ipynb')
    n = notebook(source, edition)
    title = n.cells[0].source.splitlines()[0].removeprefix('# ')
    display_title = re.sub(r'^Unit \d+ — ', '', title)
    display_title = re.sub(r'^Checkpoint \d+(?::\s*|\s+—\s+)', '', display_title)
    short_title = display_title
    if len(short_title) > 32:
        short_title = short_title[:33].rsplit(' ', 1)[0]
    if kind == 'unit':
        chapter_label = 'Unit ' + str(int(re.search(r'\d+', entry.name)[0]))
    elif kind == 'checkpoint':
        chapter_label = 'Checkpoint ' + str(int(re.search(r'\d+', entry.name)[0]))
    else:
        chapter_label = ''
        if config is None or entry.name not in config.project_headers:
            raise ValueError(f'FAIL: {entry.name}: no running header in publication.yaml project_headers')
        short_title = config.project_headers[entry.name]
    short_tex = short_title.replace('\\', r'\textbackslash{}').replace('&', r'\&').replace('%', r'\%').replace('_', r'\_')
    full_title = (chapter_label + ' — ' if chapter_label else '') + display_title
    chapter = ['# ' + full_title + ' {pub-label="' + chapter_label + '"' +
               '}\n',
               '```{=latex}\n\\chaptermark{' + (chapter_label + ' — ' if chapter_label else '') + short_tex + '}\n```']
    inventory = []
    first = n.cells[0].source
    hook = re.sub(r'^# [^\n]*\n*', '', first).strip()
    if hook:
        chapter.append(panel('opener', hook))
    if edition == 'teacher':
        chapter.append(teacher_notes(read_source(entry / 'teacher-notes.md', edition)))
    if kind == 'unit':
        seen: set[str] = set()
        rendered_turtles: set[tuple[tuple[int, str], ...]] = set()
        for c in n.cells[1:]:
            if c.cell_type == 'markdown':
                chapter.append(markdown_blocks(c.source, lesson_heading=lesson_heading))
                assets, records = asset_blocks(c.source, entry, edition, seen, entry.name,
                                               rendered_turtles)
                if assets:
                    chapter.append(assets); inventory.extend(records)
            else:
                route, body = route_code(c)
                chapter.append(body)
                inventory.append({'id': c.id, 'kind': route})
                if route == 'tryit+figure':
                    rendered_turtles.add(code_tokens(c.source))
                if route == 'figure':
                    rendered_turtles.add(code_tokens(c.source))
                    try:
                        chapter.append('```{=latex}\n' + turtle_picture(c.source) + '\n```')
                    except Exception as error:
                        raise ValueError(f'FAIL: {entry.name}: turtle figure for cell {c.id}: {error}') from error
        chapter.append('## Exercises\n')
        body, records, items = render_items(entry / 'exercises.ipynb', kind, edition, entry, entry.name,
                                            config)
        chapter.append(body); inventory.extend(records)
    else:
        body, records, items = render_items(source, kind, edition, entry, entry.name, config)
        chapter.append(body); inventory.extend(records)
    if edition == 'teacher':
        chapter.append(answer_key(entry, kind, items))
    return '\n\n'.join(block.rstrip() for block in chapter) + '\n', inventory, items, title


def render_setup_chapter(book: Path, edition: str, config: PublicationConfig):
    """Render the Markdown setup guide (publication.yaml `setup`) as the first main-matter chapter.

    Numbered, it is "Unit 0 — Getting Set Up"; unnumbered, "Getting Set Up". The source's H1 must match.
    """
    source = book / config.setup_source
    text = read_source(source, edition, config.setup_source)
    title, _, remainder = text.partition('\n')
    if title != '# ' + config.setup_title:
        raise ValueError(f'unexpected setup title: {title} (publication.yaml setup.numbered expects '
                         f'"# {config.setup_title}")')
    heading = re.search(r'(?m)^## ', remainder)
    hook = remainder[:heading.start()] if heading else remainder
    sections = remainder[heading.start():] if heading else ''
    chapter = [title + f' {{pub-label="{config.setup_label}" pub-mainmatter="true"}}',
               '```{=latex}\n\\chaptermark{' + tex_escape(config.setup_title) + '}\n```']
    if hook.strip():
        chapter.append(panel('opener', hook))
    if edition == 'teacher':
        chapter.append(teacher_notes(read_source(book / config.setup_teacher_notes, edition)))
    if sections:
        chapter.append(markdown_blocks(sections, demote=False))
    return '\n\n'.join(part.rstrip() for part in chapter) + '\n', [], [], title.removeprefix('# ')


def glossary_entries(source: str) -> list[tuple[str, str, list[str]]]:
    """Read the author-selected terms and their concept ids from glossary comments."""
    pattern = re.compile(r'^\*\*(.+?)\*\* — .+?\n<!-- concept: ([\w-]+)(?:; index: ([^>]+?))? -->', re.MULTILINE)
    return [(term, concept, [key.strip() for key in (keys or '').split(';') if key.strip()])
            for term, concept, keys in pattern.findall(source)]


def glossary_units(source: str) -> dict[str, int]:
    """Map each glossary term to the first unit that teaches it: "(Unit 4)" or "(Units 4–5)" gives 4."""
    return {term: int(unit) for term, unit in
            re.findall(r'(?m)^\*\*(.+?)\*\* — .*\*\(Units? (\d+)(?:[–-]\d+)?\)\*', source)}


CODE_SPELLING = {name.casefold(): name for name in [*dir(builtins), *keyword.kwlist]}
CODE_ONLY_NAMES = set(CODE_SPELLING)


def code_names_used(source: str) -> set[str]:
    """Names a code cell really uses: loaded names and attribute names (`.append`), not assignment targets."""
    lines = [line for line in source.splitlines() if not line.lstrip().startswith(('%', '!'))]
    try:
        tree = ast.parse('\n'.join(lines))
    except (SyntaxError, ValueError):
        try:
            return {token.string for token in tokenize.generate_tokens(io.StringIO(source).readline)
                    if token.type == tokenize.NAME}
        except (tokenize.TokenError, SyntaxError):
            return set()
    return ({node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
             and isinstance(node.ctx, ast.Load)}
            | {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)})


def lesson_code(book: Path) -> dict[int, list[str]]:
    """The code cells of each unit's lesson notebook (never exercises), keyed by unit number."""
    lessons = {}
    for path in sorted(book.glob('units/unit-*/lesson.ipynb')):
        unit = int(re.match(r'unit-(\d+)', path.parent.name)[1])
        lessons[unit] = [c.source for c in notebook(path, 'student').cells if c.cell_type == 'code']
    return lessons


def python_name_units(glossary: list[tuple[str, str, list[str]]], first_units: dict[str, int],
                      lessons: dict[int, list[str]], index_names: frozenset[str]) -> dict[str, int]:
    """Map each indexed Python name to the first unit that teaches it.

    Rule: a name that is a glossary term's headword or one of its `index:` keys (ignoring backticks
    and a leading `.`, case-insensitively) is taught in that term's unit (`glossary_units`); any other name is taught
    in the first unit whose LESSON code cells use it (exercises never count).
    A name that no lesson uses maps to nothing and is never indexed.
    """
    units = {}
    for name in sorted(index_names):
        owners = [first_units[term] for term, _, aliases in glossary if term in first_units
                  and any(key.strip('`').lstrip('.').casefold() == name for key in [term, *aliases])]
        if owners:
            units[name] = min(owners)
            continue
        for unit in sorted(lessons):
            if any(name in code_names_used(cell) for cell in lessons[unit]):
                units[name] = unit
                break
    return units


def index_key(raw: str) -> tuple[str, bool]:
    """A key is (text, code_only): backticked keys and Python names match only in code, as Python spells them."""
    plain = raw.strip('`')
    if raw.startswith('`'):
        return plain, True
    if plain.casefold() in CODE_ONLY_NAMES:
        return CODE_SPELLING[plain.casefold()], True
    return plain, False


def code_span_names(span: str) -> set[str]:
    """The Python names a code span really uses: none for output text, strings, or comments.

    A span counts as code when it is a lone name (`elif`, `.append`, `input()`) or parses as Python,
    possibly as a block header (`for key in d`); only NAME tokens count, so `'int'` and `# open-path` do not.
    """
    text = span.strip()
    if not re.fullmatch(r'\.?[A-Za-z_]\w*(?:\(\))?', text):
        for attempt in (text, text.rstrip(':') + ': pass'):
            try:
                ast.parse(attempt)
                break
            except (SyntaxError, ValueError):
                continue
        else:
            return set()
    try:
        return {token.string for token in tokenize.generate_tokens(io.StringIO(text).readline)
                if token.type == tokenize.NAME}
    except (tokenize.TokenError, SyntaxError):
        return set()


def code_key_used(key: str, span: str, used: set[str]) -> bool:
    """A code key matches a real code span: a name as a NAME token, `.append` or `random.choice` as text."""
    if not used:
        return False
    if key.isidentifier():
        return key in used
    before = '' if key.startswith('.') else r'(?<![\w.])'
    return re.search(before + re.escape(key) + r'(?!\w)', span) is not None


def index_entry(term: str) -> str:
    """Use one case-insensitive makeindex identity with the author's display text."""
    plain = term.strip('`')
    escaped = lambda value: value.replace('!', r'\!').replace('@', r'\@')
    return escaped(plain.casefold()) + '@' + escaped(plain)


def index_first_prose(qmd: str, glossary: list[tuple[str, str, list[str]]],
                      unit: int | None = None, first_units: dict[str, int] | None = None,
                      name_units: dict[str, int] | None = None,
                      index_names: frozenset[str] = frozenset()) -> str:
    """Index each glossary concept once per unit, using aliases only as match triggers.

    With `unit` and `first_units`, a term is indexed only in units at or after the one that teaches it.
    With `unit` and `name_units` (from `python_name_units`), a "Python names" subentry is gated the
    same way: a name is indexed only in units at or after its teaching unit, never if it has none.
    Code-only keys and Python names match inside inline code spans only, case-sensitively.
    `index_names` is the book's set of indexed Python names (publication.yaml `index_names`).
    """
    remaining = {term: [index_key(raw) for raw in dict.fromkeys([term, *aliases])
                        if not raw.startswith('-') and '-' + raw not in aliases]
                 for term, _, aliases in glossary
                 if unit is None or first_units is None or first_units.get(term, 0) <= unit}
    names = set(index_names) - {term.casefold() for term, _, _ in glossary}
    if unit is not None and name_units is not None:
        names = {name for name in names if name_units.get(name, unit + 1) <= unit}
    rendered = []
    fence = False
    for line in qmd.splitlines(keepends=True):
        if line.lstrip().startswith('```'):
            fence = not fence
            rendered.append(line)
            continue
        if fence or line.startswith(('#', ':::')) or line.lstrip().startswith('\\'):
            rendered.append(line)
            continue
        spans = re.split(r'(`[^`]*`)', line)
        for position, span in enumerate(spans):
            in_code = position % 2 == 1
            prose = span[1:-1] if in_code else span
            used = code_span_names(prose) if in_code else set()
            insertions = []
            for term, aliases in list(remaining.items()):
                matches = [(0, 0) for alias, code_only in aliases
                           if in_code and code_only and code_key_used(alias, prose, used)]
                matches += [(match.start(), match.end())
                            for alias, code_only in aliases if not in_code and not code_only
                            for match in [re.search(r'(?<![\w-])' + re.escape(alias) + r'(?![\w-])',
                                                    prose, re.IGNORECASE)] if match]
                if matches:
                    start, end = min(matches)
                    offset = end
                    if not in_code and prose[:end].count('**') % 2:
                        offset = prose.rfind('**', 0, start)
                    insertions.append((offset, index_entry(term)))
                    del remaining[term]
            if in_code:
                for name in sorted(names):
                    if name in used:
                        insertions.append((len(prose), 'Python names!' + name +
                                           r'@\texttt{' + name + '}'))
                        names.remove(name)
            for offset, entry in sorted(insertions, reverse=True):
                if in_code:
                    offset = len(span)
                span = span[:offset] + r'\index{' + entry + '}' + span[offset:]
            spans[position] = span
        line = ''.join(spans)
        rendered.append(line)
    return ''.join(rendered)


def yaml_string(text: str) -> str:
    """A double-quoted YAML scalar (JSON strings are valid YAML) for `_quarto.yml` placeholders."""
    return json.dumps(text, ensure_ascii=False)


def tex_escape(text: str) -> str:
    return text.replace('\\', r'\textbackslash{}').replace('&', r'\&').replace('%', r'\%').replace('_', r'\_')


def answer_chapter_heading(unit: int, lesson_title: str, mainmatter: bool) -> str:
    """The heading block of one Answer Key chapter, from the unit's lesson title (its H1)."""
    display_title = re.sub(r'^Unit \d+ — ', '', lesson_title)
    label = f'Unit {unit}'
    short_title = display_title if len(display_title) <= 32 else display_title[:33].rsplit(' ', 1)[0]
    attributes = f'pub-label="{label}"' + (' pub-mainmatter="true"' if mainmatter else '')
    return (f'# {label} — {display_title} {{{attributes}}}\n\n'
            '```{=latex}\n\\chaptermark{' + label + ' — ' + tex_escape(short_title) + '}\n```\n')


def render_answer_chapter(entry: Path, edition: str, mainmatter: bool):
    """One Answer Key chapter: the odd-numbered answers of one unit, with titled flat headings."""
    lesson = notebook(entry / 'lesson.ipynb', edition)
    title = lesson.cells[0].source.splitlines()[0].removeprefix('# ')
    display_title = re.sub(r'^Unit \d+ — ', '', title)
    unit = int(re.search(r'\d+', entry.name)[0])
    label = f'Unit {unit}'
    _, groups = item_groups(notebook(entry / 'exercises.ipynb', edition).cells, 'Exercise')
    items = [{'number': group['number'], 'title': group_title(group, 'Exercise')} for group in groups]
    chapter = [answer_chapter_heading(unit, title, mainmatter), answer_key(entry, 'unit', items, edition)]
    answered = [item for item in items if item['number'] % 2]
    return '\n\n'.join(block.rstrip() for block in chapter) + '\n', answered, f'{label} — {display_title}'


def build(root: Path, book_id: str, edition: str) -> Path:
    edition_profile = profile(edition)
    registry = yaml.safe_load((root / 'books.yaml').read_text(encoding='utf-8'))
    if book_id not in [b['id'] for b in registry['books']]:
        raise ValueError(f'unknown book: {book_id}')
    if not book_flag(root, book_id, 'publication'):
        raise ValueError(f'{book_id} is not a publication book (books.yaml publication: true)')
    config = publication_config(root, book_id)
    book = book_path(root, book_id)
    output_name = output_stem(book_id, edition)
    project = book / 'build' / 'publish' / edition
    if project.exists():
        shutil.rmtree(project)
    project.mkdir(parents=True)
    shutil.copytree(THEME, project / 'theme')
    theme_tex = project / 'theme' / 'theme.tex'
    theme_text = theme_tex.read_text(encoding='utf-8')
    for placeholder, value in (('@EDITION@', edition_profile['edition_label']),
                               ('@TITLE@', tex_escape(book_title(root, book_id))),
                               ('@SUBTITLE@', tex_escape(book_subtitle(root, book_id))),
                               ('@FOLDER@', tex_escape(book_entry(root, book_id).get('root', book_id)))):
        theme_text = theme_text.replace(placeholder, value)
    theme_tex.write_text(theme_text, encoding='utf-8')
    chapters = []
    manifest = {'edition': edition, 'output_name': output_name, 'chapters': []}
    front = []
    for position, source_name in enumerate(edition_profile['front']):
        source = book / 'front-matter' / source_name
        body = filter_edition_blocks(read_source(source, edition), edition, str(source.relative_to(root)))
        body = re.sub(r'(?m)^## ', '### ', body)
        name = 'index.qmd' if position == 0 else source_name.replace('.md', '.qmd')
        (project / name).write_text(body, encoding='utf-8')
        front.append(name)
        manifest['chapters'].append({'id': source_name.removesuffix('.md'), 'file': name,
                                     'source': str(source.relative_to(root)),
                                     'kind': 'front', 'title': body.splitlines()[0].removeprefix('# '),
                                     'items': [], 'inventory': []})
    if edition_profile['body'] == 'answers':
        units = [(id_, entry) for id_, entry in entries(book, edition) if id_.startswith('unit-')]
        for position, (id_, entry) in enumerate(units):
            body, items, title = render_answer_chapter(entry, edition, mainmatter=position == 0)
            filename = f'answers-{id_}.qmd'
            (project / filename).write_text(body, encoding='utf-8')
            chapters.append(filename)
            manifest['chapters'].append({'id': f'answers-{id_}', 'file': filename,
                                         'source': str(entry.relative_to(root)), 'kind': 'answers',
                                         'title': title, 'items': items, 'inventory': []})
    else:
        setup_source = book / config.setup_source
        body, inventory, items, title = render_setup_chapter(book, edition, config)
        setup_file = f'{config.setup_id}.qmd'
        (project / setup_file).write_text(body, encoding='utf-8')
        chapters.append(setup_file)
        manifest['chapters'].append({'id': config.setup_id, 'file': setup_file,
                                     'source': str(setup_source.relative_to(root)),
                                     'kind': 'setup', 'title': title, 'items': items,
                                     'inventory': inventory})
        for id_, entry in entries(book, edition):
            kind = id_.split('-', 1)[0]
            body, inventory, items, title = render_chapter(entry, kind, edition, config)
            filename = id_ + '.qmd'
            (project / filename).write_text(body, encoding='utf-8')
            chapters.append(filename)
            manifest['chapters'].append({'id': id_, 'file': filename, 'source': str(entry.relative_to(root)),
                                         'kind': kind, 'title': title, 'items': items, 'inventory': inventory})
    if edition_profile['answers_appendix']:
        answer_sections = []
        for chapter in manifest['chapters']:
            if chapter['kind'] != 'unit':
                continue
            entry = root / chapter['source']
            answer_sections.append(answer_key(entry, 'unit', chapter['items'], edition=edition))
        filename = 'answers.qmd'
        (project / filename).write_text('# Answers to Selected Exercises\n\n'
                                        + '\n\n'.join(answer_sections), encoding='utf-8')
        chapters.append(filename)
        manifest['chapters'].append({'id': 'answers', 'file': filename, 'source': '',
                                     'kind': 'answers', 'title': 'Answers to Selected Exercises',
                                     'items': [], 'inventory': []})
    if edition_profile['back_matter']:
        for name, kind, title in (('glossary', 'glossary', 'Glossary'),
                                  ('quick-reference', 'quickref', 'Quick Reference')):
            filename = name + '.qmd'
            source = book / 'back-matter' / (name + '.md')
            body = read_source(source, edition)
            (project / filename).write_text(body, encoding='utf-8')
            chapters.append(filename)
            manifest['chapters'].append({'id': name, 'file': filename,
                                         'source': str(source.relative_to(root)), 'kind': kind,
                                         'title': title, 'items': [], 'inventory': []})
    if edition_profile['index']:
        index_file = 'the-index.qmd'
        (project / index_file).write_text('\\printindex\n', encoding='utf-8')
        chapters.append(index_file)
        manifest['chapters'].append({'id': 'index', 'file': index_file, 'source': '',
                                     'kind': 'index', 'title': 'Index', 'items': [], 'inventory': []})
        glossary = (project / 'glossary.qmd').read_text(encoding='utf-8')
        terms = glossary_entries(glossary)
        first_units = glossary_units(glossary)
        name_units = python_name_units(terms, first_units, lesson_code(book), config.index_names)
        glossary = re.sub(r'(?m)^(\*\*(.+?)\*\* — .+)$',
                          lambda match: match[1] + r'\index{' + index_entry(match[2]) + '}', glossary)
        (project / 'glossary.qmd').write_text(glossary, encoding='utf-8')
        for chapter in manifest['chapters']:
            if chapter['kind'] != 'unit':
                continue
            path = project / chapter['file']
            unit = int(re.match(r'unit-(\d+)', chapter['id'])[1])
            path.write_text(index_first_prose(path.read_text(encoding='utf-8'), terms, unit, first_units,
                                             name_units, config.index_names),
                            encoding='utf-8')
    config = (project / 'theme' / '_quarto.yml').read_text(encoding='utf-8')
    config = config.replace('@CHAPTERS@', '\n'.join('    - ' + x for x in chapters))
    config = config.replace('@FRONT@', '\n'.join('    - ' + name for name in front))
    config = config.replace('@TITLE@', yaml_string(book_title(root, book_id)))
    config = config.replace('@SUBTITLE@', yaml_string(book_subtitle(root, book_id)))
    config = config.replace('@OUTPUT@', output_name)
    config = config.replace('@CLASSOPTION@', edition_profile['classoption'])
    (project / '_quarto.yml').write_text(config, encoding='utf-8')
    (project / 'inventory.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return project
