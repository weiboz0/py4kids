"""Turn Book 1b notebook sources into a Quarto book project."""
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

from tools.fake_turtle import imports_turtle
from tools.turtle_figure import figure_tikz
from tools.turtle_real import real_programs

THEME = Path(__file__).with_name('publish_theme')
NOTICE = re.compile(r'^(?:\*\*Notice:\*\*|Notice:|#{3,6} .*\bNotice\b)', re.IGNORECASE)
ASSET = re.compile(r'assets/([\w-]+\.py)')
DATA = re.compile(r'\b(p\d+[a-z]?_[\w-]+\.txt)\b')
ITEM = {'unit': 'Exercise', 'checkpoint': 'Question', 'project': 'Problem'}
SETUP_ID = 'unit-00-getting-set-up'


def allowed_source(path: Path, edition: str) -> bool:
    """Single gate for every source read by the student builder."""
    if edition == 'teacher':
        return True
    if 'teacher-notes' in path.name or path.name == 'solutions.ipynb':
        return False
    if path.parts and path.parts[-1].startswith('solutions_'):
        return False
    if path.name in {'lesson.ipynb', 'exercises.ipynb', 'checkpoint.ipynb',
                     'brief.ipynb', 'syllabus.md', 'how-to-use.md',
                     'unit-00-getting-set-up.md', 'preface.md', 'glossary.md',
                     'quick-reference.md'}:
        return True
    return (path.suffix == '.py' and 'units' in path.parts and 'assets' in path.parts) or (
        path.suffix == '.txt' and 'projects' in path.parts)


def read_source(path: Path, edition: str) -> str:
    if not allowed_source(path, edition):
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


def markdown_blocks(source: str, first: bool = False, demote: bool = True) -> str:
    """Split a markdown cell into paragraphs while preserving Notice continuations."""
    source = strip_turtle_directives(source)
    for title, kind in (('### You will learn', 'goals'), ('### Recap', 'recap')):
        if source.startswith(title + '\n') or source.strip() == title:
            return panel(kind, source[len(title):])
    if demote:
        source = re.sub(r'(?m)^## (?!Lesson\b|Exercises\b|Answer key\b)', '### ', source)
    paragraphs = re.split(r'\n\s*\n', source.strip())
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


def route_code(cell) -> tuple[str, str]:
    tags = cell.metadata.get('tags', [])
    source = cell.source
    if 'no-exec' in tags:
        if 'error-demo' in tags:
            return 'errordemo', panel('errordemo', code_block(source))
        if 'hang-demo' in tags:
            return 'hangdemo', panel('hangdemo', code_block(source))
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
    syllabus = read_source(book / 'syllabus.md', edition)
    ids = re.findall(r'^\| `((?:unit|checkpoint|project)-[^`]+)` \|', syllabus, flags=re.MULTILINE)
    if not ids:
        raise ValueError('syllabus has no shipped entries')
    return [(id_, book / ('units' if id_.startswith('unit-') else 'checkpoints' if id_.startswith('checkpoint-') else 'projects') / id_) for id_ in ids]


def asset_blocks(text: str, entry: Path, edition: str, seen: set[str], unit: str,
                 rendered_turtles: set[tuple[tuple[int, str], ...]] | None = None) -> tuple[str, list[dict]]:
    rendered = []
    records = []
    for name in ASSET.findall(text):
        if name.startswith('solutions_') or name in seen:
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


def group_title(group, label: str) -> str:
    for c in group['cells'][1:]:
        if c.cell_type == 'markdown' and c.source.startswith('### '):
            title = c.source.splitlines()[0][4:].replace(' — Challenge', '')
            return re.sub(r'^Challenge(?: \d+)?:\s*', '', title)
    return ''


def strip_solution_pointer(paragraph: str) -> str:
    """Drop a Student Book "— see the solution" tail and keep the sentence's full stop."""
    paragraph, stripped = re.subn(r'\s*—\s*see (?:the )?solution[^.]*\.?', '', paragraph, flags=re.IGNORECASE)
    if stripped and paragraph and not re.search(r'[.!?:][*_"\'”’]*$', paragraph):
        paragraph += '.'
    return paragraph


def render_items(path: Path, kind: str, edition: str, entry: Path, unit: str):
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
                out.append(markdown_blocks(text))
    for group in groups:
        for c in group.get('interlude', []):
            text = c.source.strip()
            if text:
                out.append(markdown_blocks(re.sub(r'^## ', '### ', text)))
        number = group['number']
        stretch = any('stretch' in c.metadata.get('tags', []) for c in group['cells'])
        title = group_title(group, label)
        display = (f'Challenge — {title}' if stretch and kind == 'unit' else
                   f'{label} {number}' + (f' — {title}' if title else ''))
        out.append(('#### ' if kind == 'project' else '### ') + display + '\n')
        if kind == 'unit':
            out.append(f'```{{=latex}}\n\\label{{ex:{entry.name}:{number}}}\n```')
        if stretch:
            out.append(panel('challenge', f'**{label} {number}**'))
        for c in (group['cells'] if kind == 'project' else group['cells'][1:]):
            if c.cell_type == 'code':
                if c.source.strip():
                    out.append(panel('starter', code_block(c.source)))
                inventory.append({'id': c.id, 'kind': 'starter'})
                continue
            text = c.source
            text = re.sub(r'^### [^\n]+\n*', '', text)
            if kind == 'project':
                text = re.sub(r'(?m)^## Milestone ', '### Milestone ', text)
            # Real-version lines become a distinct note; keep the rest of the cell.
            parts = []
            for paragraph in re.split(r'\n\s*\n', text.strip()):
                if re.match(r'^\*\*(?:Real version|No real version):\*\*', paragraph):
                    no_real = paragraph.startswith('**No real version:**')
                    paragraph = re.sub(r'^\*\*(?:Real version|No real version):\*\*\s*', '', paragraph)
                    paragraph = re.sub(r'(?i)^real program:\s*', '', paragraph)
                    if no_real:
                        continue
                    if edition == 'student':
                        paragraph = strip_solution_pointer(paragraph)
                    if paragraph[:1].islower():
                        paragraph = paragraph[0].upper() + paragraph[1:]
                    parts.append(panel('realprog', paragraph))
                else:
                    parts.append(markdown_blocks(paragraph))
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
        if kind == 'unit' and edition == 'student' and number % 2:
            out.append(f'Answer on page \\pageref{{ans:{entry.name}:{number}}}.')
    return '\n\n'.join(block.rstrip() for block in out) + '\n', inventory, [{'number': g['number'], 'title': group_title(g, label)} for g in groups]


def solution_assets(entry: Path, number: int) -> list[Path]:
    """Match one exercise number, including named variants, without matching 10 for 1."""
    return [path for path in sorted((entry / 'assets').glob('solutions_ex*.py'))
            if re.match(rf'solutions_ex{number}(?!\d)', path.stem)] if (entry / 'assets').exists() else []


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
    label = ITEM[kind]
    if edition == 'student' and not any(item['number'] % 2 for item in items):
        return ''
    if edition == 'student':
        if kind != 'unit':
            raise ValueError('student answers are unit exercises only')
        groups, assets = student_answer_sources(entry)
        items = [item for item in items if item['number'] % 2]
    else:
        n = notebook(entry / 'solutions.ipynb', 'teacher')
        _, groups = item_groups(n.cells, label)
        assets = {item['number']: solution_assets(entry, item['number']) for item in items}
    by_number = {g['number']: g for g in groups}
    out = ['## Answer key\n'] if edition == 'teacher' else []
    for item in items:
        number = item['number']
        if number not in by_number:
            raise ValueError(f'{entry}: missing solution {label} {number}')
        heading = f'{label} {number}' + (f" — {item['title']}" if item['title'] and kind != 'project' else '')
        if edition == 'student':
            unit_number = int(re.search(r'unit-(\d+)', entry.name)[1])
            heading = f'Unit {unit_number}, {label} {number}'
        page = f' (page \\pageref{{ex:{entry.name}:{number}}})' if kind == 'unit' else ''
        out.append('### ' + heading + page + '\n')
        if kind == 'unit':
            out.append(f'```{{=latex}}\n\\label{{ans:{entry.name}:{number}}}\n```')
        real_figures = []
        if kind == 'unit':
            for program, sample in real_programs(by_number[number]):
                if imports_turtle(program) and sample is not None:
                    real_figures.append((program, sample))
        for c in by_number[number]['cells'][1:]:
            if c.cell_type == 'code':
                if (re.search(r'\brun_path\s*\(\s*["\']assets/solutions_ex', c.source)
                        and 'fake_turtle' in c.source):
                    continue
                out.append(render_solution_code(c.source))
            elif c.cell_type == 'markdown':
                text = re.sub(r'^### [^\n]+\n*', '', c.source).strip()
                if text:
                    text = strip_turtle_directives(text)
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
            source = (file.read_text(encoding='utf-8') if edition == 'student'
                      else read_source(file, 'teacher'))
            out.append(panel('program', f'**{file.name}**\n\n{code_block(source).replace("```python", "```{.python .answer-code}", 1)}'))
            if 'import turtle' in source or 'from turtle import' in source:
                try:
                    out.append('```{=latex}\n' + turtle_picture(source) + '\n```')
                except Exception as error:
                    raise ValueError(f'FAIL: {entry.name}: turtle figure for asset {file.name}: {error}') from error
    return '\n\n'.join(block.rstrip() for block in out) + '\n'


def render_chapter(entry: Path, kind: str, edition: str):
    source = entry / ('lesson.ipynb' if kind == 'unit' else 'checkpoint.ipynb' if kind == 'checkpoint' else 'brief.ipynb')
    n = notebook(source, edition)
    title = n.cells[0].source.splitlines()[0].removeprefix('# ')
    display_title = re.sub(r'^Unit \d+ — ', '', title)
    display_title = re.sub(r'^Checkpoint \d+:\s*', '', display_title)
    short_title = display_title
    if len(short_title) > 32:
        short_title = short_title[:33].rsplit(' ', 1)[0]
    if kind == 'unit':
        chapter_label = 'Unit ' + str(int(re.search(r'\d+', entry.name)[0]))
    elif kind == 'checkpoint':
        chapter_label = 'Checkpoint ' + str(int(re.search(r'\d+', entry.name)[0]))
    else:
        chapter_label = ''
        short_title = 'Algorithm Challenge'
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
                chapter.append(markdown_blocks(c.source))
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
        body, records, items = render_items(entry / 'exercises.ipynb', kind, edition, entry, entry.name)
        chapter.append(body); inventory.extend(records)
    else:
        body, records, items = render_items(source, kind, edition, entry, entry.name)
        chapter.append(body); inventory.extend(records)
    if edition == 'teacher':
        chapter.append(answer_key(entry, kind, items))
    return '\n\n'.join(block.rstrip() for block in chapter) + '\n', inventory, items, title


def render_setup_chapter(source: Path, edition: str):
    """Render the Markdown setup guide as the first main-matter chapter."""
    text = read_source(source, edition)
    title, _, remainder = text.partition('\n')
    if title != '# Unit 0 — Getting Set Up':
        raise ValueError(f'unexpected setup title: {title}')
    heading = re.search(r'(?m)^## ', remainder)
    hook = remainder[:heading.start()] if heading else remainder
    sections = remainder[heading.start():] if heading else ''
    chapter = [title + ' {pub-label="Unit 0" pub-mainmatter="true"}',
               '```{=latex}\n\\chaptermark{Unit 0 — Getting Set Up}\n```']
    if hook.strip():
        chapter.append(panel('opener', hook))
    if edition == 'teacher':
        chapter.append(teacher_notes(read_source(source.with_name('unit-00-teacher-notes.md'), edition)))
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


PYTHON_INDEX_NAMES = {'print', 'input', 'range', 'len', 'str', 'int', 'float',
                      'append', 'split', 'open', 'sorted', 'sum'}
CODE_SPELLING = {name.casefold(): name for name in [*dir(builtins), *keyword.kwlist]}
CODE_ONLY_NAMES = set(CODE_SPELLING)


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
                      unit: int | None = None, first_units: dict[str, int] | None = None) -> str:
    """Index each glossary concept once per unit, using aliases only as match triggers.

    With `unit` and `first_units`, a term is indexed only in units at or after the one that teaches it.
    Code-only keys and Python names match inside inline code spans only, case-sensitively.
    """
    remaining = {term: [index_key(raw) for raw in dict.fromkeys([term, *aliases])
                        if not raw.startswith('-') and '-' + raw not in aliases]
                 for term, _, aliases in glossary
                 if unit is None or first_units is None or first_units.get(term, 0) <= unit}
    names = PYTHON_INDEX_NAMES - {term.casefold() for term, _, _ in glossary}
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


def build(root: Path, book_id: str, edition: str) -> Path:
    if edition not in {'student', 'teacher'}:
        raise ValueError('edition must be student or teacher')
    registry = yaml.safe_load((root / 'books.yaml').read_text(encoding='utf-8'))
    if book_id not in [b['id'] for b in registry['books']]:
        raise ValueError(f'unknown book: {book_id}')
    book = root / book_id
    project = book / 'build' / 'publish' / edition
    if project.exists():
        shutil.rmtree(project)
    project.mkdir(parents=True)
    shutil.copytree(THEME, project / 'theme')
    edition_name = "Teacher's Edition" if edition == 'teacher' else 'Student Book'
    theme_tex = project / 'theme' / 'theme.tex'
    theme_tex.write_text(theme_tex.read_text(encoding='utf-8').replace('@EDITION@', edition_name), encoding='utf-8')
    chapters = []
    manifest = {'edition': edition, 'chapters': []}
    syllabus_header = read_source(book / 'syllabus.md', edition).splitlines()[0].removeprefix('# ')
    title_match = re.match(r'(Book [^ ]+ — Year \d+)', syllabus_header)
    if not title_match:
        raise ValueError('syllabus title lacks book and year')
    syllabus_title = title_match[1]
    front = [(read_source(book / 'front-matter' / 'preface.md', edition), 'index.qmd'),
             (read_source(book / 'front-matter' / 'how-to-use.md', edition), 'how-to-use.qmd')]
    if edition == 'teacher':
        front.append((read_source(book / 'front-matter' / 'for-teachers.md', edition), 'for-teachers.qmd'))
    for body, name in front:
        body = re.sub(r'(?m)^## ', '### ', body)
        (project / name).write_text(body, encoding='utf-8')
        source_name = 'preface.md' if name == 'index.qmd' else name.replace('.qmd', '.md')
        manifest['chapters'].append({'id': 'preface' if name == 'index.qmd' else name.removesuffix('.qmd'),
                                     'file': name,
                                     'source': str((book / 'front-matter' / source_name).relative_to(root)),
                                     'kind': 'front', 'title': body.splitlines()[0].removeprefix('# '),
                                     'items': [], 'inventory': []})
    setup_source = book / 'docs' / f'{SETUP_ID}.md'
    body, inventory, items, title = render_setup_chapter(setup_source, edition)
    setup_file = f'{SETUP_ID}.qmd'
    (project / setup_file).write_text(body, encoding='utf-8')
    chapters.append(setup_file)
    manifest['chapters'].append({'id': SETUP_ID, 'file': setup_file,
                                 'source': str(setup_source.relative_to(root)),
                                 'kind': 'setup', 'title': title, 'items': items,
                                 'inventory': inventory})
    for id_, entry in entries(book, edition):
        kind = id_.split('-', 1)[0]
        body, inventory, items, title = render_chapter(entry, kind, edition)
        filename = id_ + '.qmd'
        (project / filename).write_text(body, encoding='utf-8')
        chapters.append(filename)
        manifest['chapters'].append({'id': id_, 'file': filename, 'source': str(entry.relative_to(root)),
                                     'kind': kind, 'title': title, 'items': items, 'inventory': inventory})
    if edition == 'student':
        answer_sections = []
        for chapter in manifest['chapters']:
            if chapter['kind'] != 'unit':
                continue
            entry = root / chapter['source']
            answer_sections.append(answer_key(entry, 'unit', chapter['items'], edition='student'))
        filename = 'answers.qmd'
        (project / filename).write_text('# Answers to Selected Exercises\n\n'
                                        + '\n\n'.join(answer_sections), encoding='utf-8')
        chapters.append(filename)
        manifest['chapters'].append({'id': 'answers', 'file': filename, 'source': '',
                                     'kind': 'answers', 'title': 'Answers to Selected Exercises',
                                     'items': [], 'inventory': []})
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
    index_file = 'the-index.qmd'
    (project / index_file).write_text('\\printindex\n', encoding='utf-8')
    chapters.append(index_file)
    manifest['chapters'].append({'id': 'index', 'file': index_file, 'source': '',
                                 'kind': 'index', 'title': 'Index', 'items': [], 'inventory': []})
    glossary = (project / 'glossary.qmd').read_text(encoding='utf-8')
    terms = glossary_entries(glossary)
    first_units = glossary_units(glossary)
    glossary = re.sub(r'(?m)^(\*\*(.+?)\*\* — .+)$',
                      lambda match: match[1] + r'\index{' + index_entry(match[2]) + '}', glossary)
    (project / 'glossary.qmd').write_text(glossary, encoding='utf-8')
    for chapter in manifest['chapters']:
        if chapter['kind'] != 'unit':
            continue
        path = project / chapter['file']
        unit = int(re.match(r'unit-(\d+)', chapter['id'])[1])
        path.write_text(index_first_prose(path.read_text(encoding='utf-8'), terms, unit, first_units),
                        encoding='utf-8')
    config = (project / 'theme' / '_quarto.yml').read_text(encoding='utf-8')
    config = config.replace('@CHAPTERS@', '\n'.join('    - ' + x for x in chapters))
    config = config.replace('@FRONT@', '\n'.join('    - ' + name for _, name in front))
    config = config.replace('@SUBTITLE@', syllabus_title)
    config = config.replace('@OUTPUT@', 'Book1b-' + ('Teacher' if edition == 'teacher' else 'Student'))
    (project / '_quarto.yml').write_text(config, encoding='utf-8')
    (project / 'inventory.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return project
