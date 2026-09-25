"""Turn Book 1b notebook sources into a Quarto book project."""
from __future__ import annotations

import io
import json
import re
import shutil
import tokenize
from contextlib import redirect_stdout
from pathlib import Path

import nbformat
import yaml

from tools.turtle_figure import figure_tikz

THEME = Path(__file__).with_name('publish_theme')
NOTICE = re.compile(r'^(?:\*\*Notice:\*\*|Notice:|#{3,6} .*\bNotice\b)', re.IGNORECASE)
ASSET = re.compile(r'assets/([\w-]+\.py)')
DATA = re.compile(r'\b(p\d+[a-z]?_[\w-]+\.txt)\b')
ITEM = {'unit': 'Exercise', 'checkpoint': 'Question', 'project': 'Problem'}


def allowed_source(path: Path, edition: str) -> bool:
    """Single gate for every source read by the student builder."""
    if edition == 'teacher':
        return True
    if path.name in {'teacher-notes.md', 'solutions.ipynb'}:
        return False
    if path.parts and path.parts[-1].startswith('solutions_'):
        return False
    if path.name in {'lesson.ipynb', 'exercises.ipynb', 'checkpoint.ipynb',
                     'brief.ipynb', 'syllabus.md', 'how-to-use.md'}:
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


def turtle_picture(source: str) -> str:
    with redirect_stdout(io.StringIO()):
        return figure_tikz(source)


def panel(kind: str, body: str) -> str:
    return f'::: {{.{kind}}}\n{body.strip()}\n:::\n'


def markdown_blocks(source: str, first: bool = False) -> str:
    """Split a markdown cell into paragraphs while preserving Notice continuations."""
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
    return '```python\n' + source.rstrip() + '\n```\n'


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
    lines = source.splitlines()
    if lines and lines[0].startswith('# '):
        lines.pop(0)
    body = '\n'.join(lines)
    body = re.sub(r'^(#{1,4}) ', lambda m: '#' * (len(m[1]) + 2) + ' ', body, flags=re.MULTILINE)
    body = re.sub(r'\(design 006 D9 genres\)|design 006 D3|\(plan 0\d\d\)', '', body)
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
                        # No stdin program exists, so there is nothing to point to in the Teacher's Edition.
                        reason = paragraph.rstrip(' .')
                        reason = reason[0].lower() + reason[1:] if reason[:1].isupper() and not reason[:2].isupper() else reason
                        item = {'checkpoint': 'question', 'project': 'problem'}.get(kind, 'exercise')
                        stripped = re.sub(r'^this (?:exercise|question|problem)\s+', '', reason)
                        reason = f'it {stripped}' if stripped != reason else reason
                        paragraph = f'There is no real program for this {item}: {reason}.'
                    elif edition == 'student':
                        not_graded = bool(re.search(r'\(Not graded\.\)', paragraph, re.IGNORECASE))
                        paragraph = re.sub(r'\s*\(Not graded\.\)', '', paragraph, flags=re.IGNORECASE)
                        paragraph = re.sub(r'\s*—\s*see (?:the )?solution[^.]*\.?', '', paragraph, flags=re.IGNORECASE)
                        paragraph = paragraph.rstrip(' .—')
                        if not re.match(r'(?i)^the real program\b|^no real program\b', paragraph):
                            paragraph = 'The real program ' + paragraph
                        paragraph = paragraph[0].upper() + paragraph[1:]
                        if not_graded:
                            paragraph += ' (not graded)'
                        paragraph += ". The full program is in the Teacher's Edition."
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
        if edition == 'student' and kind == 'unit':
            out.append('\\answerlines{' + ('8' if stretch else '4') + '}\n')
    return '\n\n'.join(block.rstrip() for block in out) + '\n', inventory, [{'number': g['number'], 'title': group_title(g, label)} for g in groups]


def answer_key(entry: Path, kind: str, items: list[dict]) -> str:
    n = notebook(entry / 'solutions.ipynb', 'teacher')
    label = ITEM[kind]
    _, groups = item_groups(n.cells, label)
    by_number = {g['number']: g for g in groups}
    out = ['## Answer key\n']
    for item in items:
        number = item['number']
        if number not in by_number:
            raise ValueError(f'{entry}: missing solution {label} {number}')
        heading = f'{label} {number}' + (f" — {item['title']}" if item['title'] and kind != 'project' else '')
        out.append('### ' + heading + '\n')
        for c in by_number[number]['cells'][1:]:
            if c.cell_type == 'code':
                if (re.search(r'\brun_path\s*\(\s*["\']assets/solutions_ex', c.source)
                        and 'fake_turtle' in c.source):
                    continue
                code, removed = strip_asserts(c.source)
                if code:
                    out.append(code_block(code))
                if removed:
                    out.append("(checked by the course's test suite)\n")
            elif c.cell_type == 'markdown':
                text = re.sub(r'^### [^\n]+\n*', '', c.source).strip()
                if text:
                    out.append(text + '\n')
        for file in sorted((entry / 'assets').glob(f'solutions_ex{number}*.py')) if (entry / 'assets').exists() else []:
            source = read_source(file, 'teacher')
            out.append(panel('program', f'**{file.name}**\n\n{code_block(source)}'))
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
               (' pub-mainmatter="true"' if kind == 'unit' and entry.name.startswith('unit-01-') else '') + '}\n',
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
    front = [(read_source(book / 'front-matter' / 'how-to-use.md', edition), 'index.qmd')]
    if edition == 'teacher':
        front.append((read_source(book / 'front-matter' / 'for-teachers.md', edition), 'for-teachers.qmd'))
    for body, name in front:
        body = re.sub(r'(?m)^## ', '### ', body)
        (project / name).write_text(body, encoding='utf-8')
    for id_, entry in entries(book, edition):
        kind = id_.split('-', 1)[0]
        body, inventory, items, title = render_chapter(entry, kind, edition)
        filename = id_ + '.qmd'
        (project / filename).write_text(body, encoding='utf-8')
        chapters.append(filename)
        manifest['chapters'].append({'id': id_, 'file': filename, 'source': str(entry.relative_to(root)),
                                     'kind': kind, 'title': title, 'items': items, 'inventory': inventory})
    config = (project / 'theme' / '_quarto.yml').read_text(encoding='utf-8')
    config = config.replace('@CHAPTERS@', '\n'.join('    - ' + x for x in chapters))
    config = config.replace('@FRONT@', '\n'.join('    - ' + name for _, name in front))
    config = config.replace('@SUBTITLE@', syllabus_title)
    config = config.replace('@OUTPUT@', 'Book1b-' + ('Teacher' if edition == 'teacher' else 'Student'))
    (project / '_quarto.yml').write_text(config, encoding='utf-8')
    (project / 'inventory.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return project
