"""Publication transform and source-boundary checks."""
from pathlib import Path
from types import SimpleNamespace

from tools.publish import allowed_source, markdown_blocks, route_code, strip_asserts, teacher_notes


def test_student_boundary():
    for name in ('teacher-notes.md', 'solutions.ipynb', 'assets/solutions_ex1.py'):
        assert not allowed_source(Path(name), 'student')
    assert allowed_source(Path('lesson.ipynb'), 'student')


def test_notice_forms_and_opener():
    blocks = markdown_blocks('# Unit\n\nThe hook.\n\nNext hook.', first=True)
    assert '::: {.opener}' in blocks and 'The hook.' in blocks
    for source in ('**Notice:** bold', 'Notice: plain', '### Contrast Notice\n\nMore'):
        assert '::: {.notice}' in markdown_blocks(source)


def test_lesson_routing():
    def cell(source, tags=(), outputs=()):
        return SimpleNamespace(source=source, metadata={'tags': list(tags)}, outputs=list(outputs))
    assert route_code(cell('oops', ['no-exec', 'error-demo']))[0] == 'errordemo'
    assert route_code(cell('while True: pass', ['no-exec', 'hang-demo']))[0] == 'hangdemo'
    assert route_code(cell('name = input()', ['no-exec']))[0] == 'tryit'
    assert route_code(cell('print(1)', outputs=[{'output_type': 'stream', 'name': 'stdout', 'text': '1\n'}]))[0] == 'code+output'
    assert route_code(cell('print(1)'))[0] == 'code'


def test_teacher_cleanup():
    assert '### Goal' in teacher_notes('# Title\n\n# Goal\n\n60-MINUTE CUT (design 006 D9 genres) for CI')
    assert '60-minute cut' in teacher_notes('# Title\n\n60-MINUTE CUT')
    assert 'design 006' not in teacher_notes('# Title\n\n(design 006 D9 genres)')
    escaped = teacher_notes(r'# Title' + '\n\n' + r'File is "5\n8\n"; code is `"5\n"`.')
    assert r'"5\\n8\\n"' in escaped and r'`"5\n"`' in escaped
    assert '`a` / `b`' in teacher_notes('# Title\n\n`a`/`b`')
    code, removed = strip_asserts('x=1\nassert x == 1\nprint(x)')
    assert removed and code == 'x=1\nprint(x)'


def test_student_sentinel_stays_out_of_project_and_pdf(tmp_path):
    import os
    import shutil
    import subprocess

    import nbformat
    import pytest

    from tools.publish import build

    quarto = shutil.which('quarto') or str(Path.home() / '.local/bin/quarto')
    if not Path(quarto).exists():
        pytest.skip('Quarto is not installed')
    root = tmp_path
    (root / 'books.yaml').write_text('books:\n- id: book1b\n  number: 1\n  root: book1b\n')
    book = root / 'book1b'
    book.mkdir()
    (book / 'syllabus.md').write_text('# Book 1b — Year 1 Syllabus\n\n| entry | kind | lessons | the hook |\n|---|---|---|---|\n| `unit-01-fixture` | unit | 1 | Hook. |\n')
    front = book / 'front-matter'
    front.mkdir()
    (front / 'how-to-use.md').write_text('# How to use\n')
    (front / 'for-teachers.md').write_text('# For teachers\n')
    entry = book / 'units' / 'unit-01-fixture'
    (entry / 'assets').mkdir(parents=True)
    (entry / 'teacher-notes.md').write_text('# Notes\n\nTEACHER_SENTINEL_7429 [1]→{\"x\":[2]}\n')
    (entry / 'assets' / 'solutions_ex1.py').write_text('# ASSET_SENTINEL_7429\n')
    def save(name, cells):
        n = nbformat.v4.new_notebook(cells=cells)
        nbformat.write(n, entry / name)
    save('lesson.ipynb', [nbformat.v4.new_markdown_cell('# Fixture\n\nA hook.'),
                          nbformat.v4.new_code_cell('print("hello")')])
    save('exercises.ipynb', [nbformat.v4.new_markdown_cell('# Practice'),
                             nbformat.v4.new_markdown_cell('## Exercise 1'),
                             nbformat.v4.new_markdown_cell('### Test\n\nDo a thing for $5 and $6.'),
                             nbformat.v4.new_code_cell('# starter')])
    save('solutions.ipynb', [nbformat.v4.new_markdown_cell('# Solutions'),
                             nbformat.v4.new_markdown_cell('## Exercise 1\n\n### Test'),
                             nbformat.v4.new_code_cell('print("SOLUTION_SENTINEL_7429")')])
    student = build(root, 'book1b', 'student')
    teacher = build(root, 'book1b', 'teacher')
    student_text = '\n'.join(p.read_text() for p in student.glob('*.qmd'))
    teacher_text = '\n'.join(p.read_text() for p in teacher.glob('*.qmd'))
    for marker in ('TEACHER_SENTINEL_7429', 'ASSET_SENTINEL_7429', 'SOLUTION_SENTINEL_7429'):
        assert marker not in student_text
        assert marker in teacher_text
    env = os.environ.copy()
    env['TEXMFCACHE'] = str(tmp_path / 'tex-cache')
    env['XDG_CACHE_HOME'] = str(tmp_path / 'xdg-cache')
    subprocess.run([quarto, 'render', str(student), '--to', 'pdf'], check=True,
                   capture_output=True, text=True, env=env)
    pdf_text = subprocess.run(['pdftotext', str(student / '_book' / 'Book1b-Student.pdf'), '-'],
                              check=True, capture_output=True, text=True).stdout
    assert '$5 and $6' in pdf_text
    assert 'Student Book' in pdf_text and 'Invalid Date' not in pdf_text
    assert all(marker not in pdf_text for marker in ('TEACHER_SENTINEL_7429',
               'ASSET_SENTINEL_7429', 'SOLUTION_SENTINEL_7429'))
    subprocess.run([quarto, 'render', str(teacher), '--to', 'pdf'], check=True,
                   capture_output=True, text=True, env=env)
    teacher_pdf_text = subprocess.run(['pdftotext', str(teacher / '_book' / 'Book1b-Teacher.pdf'), '-'],
                                      check=True, capture_output=True, text=True).stdout
    assert 'TEACHER_SENTINEL_7429' in teacher_pdf_text


def test_grouped_exercise_and_brief_keep_statements(tmp_path):
    import nbformat

    from tools.publish import render_items

    entry = tmp_path / 'units' / 'entry'
    (entry / 'assets').mkdir(parents=True)
    (entry / 'assets' / 'ex1_start.py').write_text('print("starter")\n')
    brief_entry = tmp_path / 'projects' / 'project-01-fixture'
    brief_entry.mkdir(parents=True)
    (brief_entry / 'p7_words.txt').write_text('fern\nmoss\n')
    exercise = nbformat.v4.new_notebook(cells=[
        nbformat.v4.new_markdown_cell('# Practice'),
        nbformat.v4.new_markdown_cell('## Exercise 1'),
        nbformat.v4.new_markdown_cell('### A title\n\nKeep this statement. Use assets/ex1_start.py.\n\n**Real version:** reads input.'),
        nbformat.v4.new_code_cell('# fill this in', metadata={'tags': ['stretch']}),
    ])
    nbformat.write(exercise, entry / 'exercises.ipynb')
    student, inventory, items = render_items(entry / 'exercises.ipynb', 'unit', 'student', entry, 'unit-01-fixture')
    teacher, _, _ = render_items(entry / 'exercises.ipynb', 'unit', 'teacher', entry, 'unit-01-fixture')
    assert '### Exercise 1 — A title' in student
    assert 'Keep this statement.' in student
    assert '::: {.challenge}' in student and r'\answerlines{12}' in student
    assert "your teacher's edition has the full program" in student
    assert "your teacher's edition has the full program" not in teacher
    assert '# fill this in' in student
    assert ('asset:ex1_start.py', 'asset listing') in [(x['id'], x['kind']) for x in inventory]
    assert items == [{'number': 1, 'title': 'A title'}]

    brief = nbformat.v4.new_notebook(cells=[
        nbformat.v4.new_markdown_cell('# Brief\n\nHook.'),
        nbformat.v4.new_markdown_cell('## Milestone 1\n\nWords'),
        nbformat.v4.new_markdown_cell('### Problem 7\n\nKeep this problem statement. Use p7_words.txt.'),
        nbformat.v4.new_code_cell('# solve'),
    ])
    nbformat.write(brief, brief_entry / 'brief.ipynb')
    body, _, items = render_items(brief_entry / 'brief.ipynb', 'project', 'student', brief_entry, 'project-01-fixture')
    assert '## Milestone 1' in body
    assert '### Problem 7' in body and 'Keep this problem statement.' in body
    assert '::: {.datafile}' in body and 'fern' in body
    assert items == [{'number': 7, 'title': ''}]


def test_checkpoint_group_and_answer_key(tmp_path):
    import nbformat

    from tools.publish import answer_key, render_items

    entry = tmp_path / 'checkpoints' / 'checkpoint-01-fixture'
    entry.mkdir(parents=True)
    checkpoint = nbformat.v4.new_notebook(cells=[
        nbformat.v4.new_markdown_cell('# Checkpoint\n\nOpening task.'),
        nbformat.v4.new_markdown_cell('## Question 1'),
        nbformat.v4.new_markdown_cell('### First title\n\nKeep this question.'),
        nbformat.v4.new_code_cell('# complete the function'),
    ])
    nbformat.write(checkpoint, entry / 'checkpoint.ipynb')
    body, inventory, items = render_items(entry / 'checkpoint.ipynb', 'checkpoint', 'student', entry, 'checkpoint-01-fixture')
    assert '## Question 1 — First title' in body and 'Keep this question.' in body
    assert '::: {.challenge}' not in body
    assert inventory[0]['kind'] == 'starter'
    solutions = nbformat.v4.new_notebook(cells=[
        nbformat.v4.new_markdown_cell('# Solutions'),
        nbformat.v4.new_markdown_cell('## Question 1\n\n### First title'),
        nbformat.v4.new_code_cell('answer = 1\nassert answer == 1\nprint(answer)'),
        nbformat.v4.new_markdown_cell('**The real program**\n\n```python\nprint(1)\n```\n\nSample input/output.'),
    ])
    nbformat.write(solutions, entry / 'solutions.ipynb')
    key = answer_key(entry, 'checkpoint', items)
    assert '## Answer key' in key and '### Question 1 — First title' in key
    assert 'assert answer' not in key and "(checked by the course's test suite)" in key
    assert '**The real program**' in key and 'Sample input/output.' in key
