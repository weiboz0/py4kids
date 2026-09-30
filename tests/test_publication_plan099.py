"""Plan 099 Phase A: publisher and audit gaps exposed by *Contest Python: USACO Bronze* (one fixture per fix)."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import nbformat
import pytest
from publication_helpers import (
    REPO,
    fixture_config,
    python_concepts_config,
    write_publication_config,
)

from tools.books import PublicationConfigError, publication_config, publication_config_errors
from tools.publish import (
    STDIN_NOTE,
    THEME,
    answer_chapter_heading,
    answer_key,
    render_answer_chapter,
    render_chapter,
    render_items,
)
from tools.publish_audit import (
    _turtle_drawing_findings,
    answer_key_equivalence_findings,
    index_findings,
)

md = nbformat.v4.new_markdown_cell
code = nbformat.v4.new_code_cell


def _write(path: Path, cells) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nbformat.v4.new_notebook(cells=cells), path)


# --- A1: a stdin solver prints once -----------------------------------------------------------------

SOLVER = 'import sys\n\ndata = sys.stdin.read().split()\nprint(sum(int(x) for x in data[1:]))\n'
RUN_LINE = 'Run the full solver from this unit folder:\n\n```text\npython assets/l1.py < assets/l1/1.in\n```'


def _stdin_unit(entry: Path, *, asset_source: str = SOLVER, run_cell: str = RUN_LINE) -> None:
    (entry / 'assets').mkdir(parents=True, exist_ok=True)
    (entry / 'assets' / 'l1.py').write_text(asset_source, encoding='utf-8')
    (entry / 'assets' / 'l2.py').write_text('import sys\nprint(len(sys.stdin.read()))\n', encoding='utf-8')
    _write(entry / 'lesson.ipynb', [
        md('# Unit 1 — Reading Input\n\nA hook.', id='title'),
        md('## Lesson 1 — Sum the values\n\nPut it together.', id='l1'),
        # Same code tokens as assets/l1.py (comments and spacing differ).
        code('import sys\n# read everything\ndata = sys.stdin.read().split()\nprint(sum(int(x) for x in data[1:]))',
             id='solver1', metadata={'tags': ['no-exec']}),
        md(run_cell, id='run1'),
        md('## Lesson 2 — Count characters', id='l2'),
        # A stdin program with no run line after it keeps the generic note.
        code('import sys\nprint(sys.stdin.read().upper())', id='solver2', metadata={'tags': ['no-exec']}),
        md('The helper is saved as assets/l2.py.', id='l2-asset'),
    ])
    _write(entry / 'exercises.ipynb', [md('# Practice', id='x0'), md('## Exercise 1\n\n### Go\n\nDo it.', id='x1')])


@pytest.mark.parametrize('edition', ['student-print', 'student', 'teacher'])
def test_stdin_solver_prints_once_without_the_generic_note(tmp_path, edition):
    entry = tmp_path / 'units' / 'unit-01-fixture'
    _stdin_unit(entry)
    (entry / 'teacher-notes.md').write_text('# Notes\n\nNotes.\n', encoding='utf-8')
    _write(entry / 'solutions.ipynb', [md('# Solutions', id='s0'), md('## Exercise 1', id='s1'),
                                       code('print(1)', id='s1c')])
    body, inventory, _, _ = render_chapter(entry, 'unit', edition, fixture_config())
    lesson = body.split('## Exercises', 1)[0]
    # The solver prints once, as the Try-it, then the run line; no listing and no generic note.
    assert lesson.count('data = sys.stdin.read().split()') == 1
    assert '::: {.tryit}\n```python\nimport sys\n# read everything' in lesson
    assert '**assets/l1.py**' not in lesson and 'This program is saved as assets/l1.py' not in lesson
    assert 'python assets/l1.py < assets/l1/1.in' in lesson
    solver_panel = lesson.split('::: {.tryit}', 2)[1]
    assert STDIN_NOTE not in solver_panel.split(':::', 1)[0]
    # The second stdin program has no run line: its note stays, and l2.py (different code) is listed.
    assert lesson.count(STDIN_NOTE) == 1
    assert '**assets/l2.py**' in lesson
    kinds = [(record['id'], record['kind']) for record in inventory]
    assert kinds[:4] == [('solver1', 'tryit-stdin'), ('asset:l1.py', 'asset reference'),
                         ('solver2', 'tryit-stdin'), ('asset:l2.py', 'asset listing')]
    # The audit agrees with the new output, and catches a repeated listing or a stray note.
    assert _turtle_drawing_findings(entry, body, edition) == []
    listed = lesson + '\n::: {.program}\n**assets/l1.py**\n\n```python\n' + SOLVER + '```\n:::\n'
    assert any('try-it asset l1.py listed again in full' in finding
               for finding in _turtle_drawing_findings(entry, listed + '## Exercises', edition))
    noted = lesson + '\n' + STDIN_NOTE + '\n'
    assert any('stdin try-it notes' in finding
               for finding in _turtle_drawing_findings(entry, noted + '## Exercises', edition))


def test_stdin_solver_differing_from_its_asset_keeps_both(tmp_path):
    entry = tmp_path / 'units' / 'unit-01-fixture'
    _stdin_unit(entry, asset_source='import sys\nprint(sys.stdin.read())\n')
    body, inventory, _, _ = render_chapter(entry, 'unit', 'student', fixture_config())
    lesson = body.split('## Exercises', 1)[0]
    assert lesson.count(STDIN_NOTE) == 2 and '**assets/l1.py**' in lesson
    assert ('asset:l1.py', 'asset listing') in [(record['id'], record['kind']) for record in inventory]
    assert _turtle_drawing_findings(entry, body, 'student') == []


# --- A2: project answer titles ----------------------------------------------------------------------

def test_project_problem_answers_take_the_brief_titles(tmp_path):
    entry = tmp_path / 'projects' / 'project-03-fixture'
    _write(entry / 'brief.ipynb', [
        md('# Grand Mock Contest\n\nEight problems.', id='b0'),
        md('## Milestone 1 — Warmups', id='m1'),
        md('### Problem 1 — Checkpoint Ledger  *(prefix sums)*\n\nSum the ledger.', id='p1'), code('', id='p1s'),
        md('### Problem 2 — Warehouse Robot  *(simulation on a grid)*\n\nMove the robot.', id='p2'),
        code('', id='p2s'),
    ])
    _write(entry / 'solutions.ipynb', [
        md('# Solutions', id='s0'),
        md('## Problem 1', id='s1'), code('print(1)', id='s1c'),
        md('## Problem 2', id='s2'), code('print(2)', id='s2c'),
    ])
    _, _, items = render_items(entry / 'brief.ipynb', 'project', 'teacher', entry, entry.name)
    assert items == [{'number': 1, 'title': 'Checkpoint Ledger'}, {'number': 2, 'title': 'Warehouse Robot'}]
    key = answer_key(entry, 'project', items, 'teacher')
    assert re.findall(r'(?m)^### .*$', key) == ['### Problem 1 — Checkpoint Ledger',
                                                '### Problem 2 — Warehouse Robot']


# --- A3: inline-code break points (panels.lua) ------------------------------------------------------

@pytest.mark.skipif(shutil.which('pandoc') is None, reason='pandoc is not installed')
def test_inline_code_never_breaks_between_or_before_punctuation():
    source = ('`assets/l1.py` `assets/ex1/1.out` `1.in` `1..n` `a[l..r]` `N - 1` `foo.bar_baz(x, y)` '
              '`__init__` `abcdefghijklmnopq`\n')
    latex = _pandoc_latex(source)
    spans = re.findall(r'\\texttt\{((?:[^{}]|\{\})*)\}', latex)
    assert spans == [
        'assets/\\allowbreak{}l1.py',       # never "assets/l1. / py"
        'assets/\\allowbreak{}ex1/\\allowbreak{}1.out',
        '1.in',
        '1..n',                             # never after a dot
        'a[l..r]',
        'N - 1',                            # never "N - / 1" (the spaces break anyway)
        'foo.bar\\_\\allowbreak{}baz(\\allowbreak{}x, y)',
        '\\_\\_\\allowbreak{}init\\_\\_',   # after `_` only before an identifier character
        'abcdefghijkl\\allowbreak{}mnopq',  # a long run of letters still breaks
    ]


def _pandoc_latex(source: str) -> str:
    return subprocess.run(['pandoc', '-f', 'markdown', '-t', 'latex', '--wrap=none', '--lua-filter',
                           str(THEME / 'panels.lua')], input=source, capture_output=True, text=True, check=True).stdout


@pytest.mark.skipif(shutil.which('pandoc') is None, reason='pandoc is not installed')
def test_answer_key_headings_keep_with_what_follows():
    """`## Answer key` and every answer heading under it get \\Needspace, so none sits alone at a page
    foot; headings outside an answer key are untouched, and the mark never reaches the output."""
    source = ('# Project 1\n\n### Lucky Guess\n\nBrief.\n\n## Answer key\n\n### Exercise 1 — A\n\nx\n\n'
              '### Milestone 1 — Open the arcade\n\ny\n\n# Answers\n\n### Unit 3, Exercise 1\n\nz\n')
    latex = _pandoc_latex(source)
    needs = re.findall(r'\\Needspace\{(\d+)\\baselineskip\}\s*\\hypertarget\{[^}]*\}\{%\s*\\\w+\{([^}]*)\}', latex)
    assert needs == [('20', 'Answer key'), ('16', 'Exercise 1 --- A'),
                     ('16', 'Milestone 1 --- Open the arcade'), ('16', 'Unit 3, Exercise 1')]
    assert 'pub-keep' not in latex


# --- A4: running headers ----------------------------------------------------------------------------

def _unit_with_title(root: Path, unit_id: str, title: str) -> Path:
    entry = root / 'units' / unit_id
    _write(entry / 'lesson.ipynb', [md(f'# {title}\n\nA hook.', id='t')])
    _write(entry / 'exercises.ipynb', [md('# Practice', id='x0'), md('## Exercise 1\n\n### Go\n\nDo it.', id='x1')])
    _write(entry / 'solutions.ipynb', [md('# Solutions', id='s0'), md('## Exercise 1', id='s1'),
                                       code('print(1)', id='s1c')])
    return entry


def test_unit_headers_apply_to_the_unit_and_answer_key_chapters(tmp_path):
    entry = _unit_with_title(tmp_path, 'unit-11-number-systems-bitwise',
                             'Unit 11 — Number Systems, Bitwise & Number Theory')
    config = fixture_config(unit_headers={'unit-11-number-systems-bitwise': 'Number Systems & Bitwise'})
    body, _, _, _ = render_chapter(entry, 'unit', 'student', config)
    assert body.startswith('# Unit 11 — Number Systems, Bitwise & Number Theory {pub-label="Unit 11"}')
    assert '\\chaptermark{Unit 11 — Number Systems \\& Bitwise}' in body
    answers, _, _ = render_answer_chapter(entry, 'answer-key', True, config=config)
    assert '\\chaptermark{Unit 11 — Number Systems \\& Bitwise}' in answers
    heading = answer_chapter_heading(11, 'Unit 11 — Number Systems, Bitwise & Number Theory', True,
                                     entry.name, config)
    assert answers.startswith(heading)
    # The audit's heading-block check builds the same heading from the same config.
    assert not any('heading block' in finding for finding in answer_key_equivalence_findings(
        'answers-' + entry.name, 11, answers, '', 'Unit 11 — Number Systems, Bitwise & Number Theory', {},
        True, entry.name, config))


def test_an_over_long_title_without_a_unit_header_is_a_publisher_error(tmp_path):
    entry = _unit_with_title(tmp_path, 'unit-11-number-systems-bitwise',
                             'Unit 11 — Number Systems, Bitwise & Number Theory')
    with pytest.raises(ValueError, match='39 characters.*unit_headers'):
        render_chapter(entry, 'unit', 'student', fixture_config())
    with pytest.raises(ValueError, match='unit_headers'):
        render_answer_chapter(entry, 'answer-key', True, config=fixture_config())
    # A title of exactly 32 characters needs no entry.
    short = _unit_with_title(tmp_path, 'unit-02-fixture', 'Unit 2 — ' + 'x' * 32)
    body, _, _, _ = render_chapter(short, 'unit', 'student', fixture_config())
    assert '\\chaptermark{Unit 2 — ' + 'x' * 32 + '}' in body


def test_python_concepts_unit_08_pins_its_current_head():
    config = python_concepts_config()
    title = 'Randomness: Dice, Simulations, and a Wandering Turtle'
    old_truncation = title[:33].rsplit(' ', 1)[0]  # the silent rule this plan removes
    assert config.unit_headers == {'unit-08-randomness': old_truncation}
    assert old_truncation == 'Randomness: Dice, Simulations,'
    projects = publication_config(REPO, 'python-projects')
    assert projects.unit_headers == {}


def _book(tmp_path: Path) -> Path:
    root = tmp_path / 'book'
    (root / 'docs').mkdir(parents=True)
    (root / 'docs' / 'unit-00-getting-set-up.md').write_text('# Unit 0 — Getting Set Up\n')
    (root / 'docs' / 'unit-00-teacher-notes.md').write_text('# Notes\n')
    (root / 'units' / 'unit-11-bits').mkdir(parents=True)
    (root / 'checkpoints' / 'checkpoint-01-mock').mkdir(parents=True)
    return root


@pytest.mark.parametrize('headers,message', [
    ({'project-01-x': 'Mock'}, 'key project-01-x must be a unit or checkpoint id'),
    ({'unit-12-missing': 'Missing'}, 'unit unit-12-missing does not exist'),
    ({'checkpoint-02-missing': 'Missing'}, 'checkpoint checkpoint-02-missing does not exist'),
    ({'unit-11-bits': ''}, 'needs a header text'),
    ({'unit-11-bits': 'x' * 33}, 'header is 33 characters (at most 32)'),
    (['unit-11-bits'], 'unit_headers: must be a mapping'),
])
def test_unit_headers_validation(tmp_path, headers, message):
    write_publication_config(_book(tmp_path), unit_headers=headers)
    errors = publication_config_errors(tmp_path, 'book')
    assert any(message in error for error in errors), errors
    with pytest.raises(PublicationConfigError, match='FAIL'):
        publication_config(tmp_path, 'book')


def test_unit_headers_valid_config(tmp_path):
    write_publication_config(_book(tmp_path), unit_headers={'unit-11-bits': 'x' * 32})
    assert publication_config(tmp_path, 'book').unit_headers == {'unit-11-bits': 'x' * 32}


# --- A5: index entries wrapped across .ind lines ----------------------------------------------------

def test_index_audit_matches_entries_wrapped_across_ind_lines():
    ind = ('\\begin{theindex}\n\n'
           '  \\item Complete search over every candidate answer in a bounded range, \n'
           '\t\t\\hyperpage{12}, \\hyperpage{14}\n\n  \\indexspace\n\n'
           '  \\item Python names\n    \\subitem \\texttt{sorted}, \\hyperpage{5}\n\n'
           '  \\item Set operations, \\hyperpage{3}\n\n\\end{theindex}\n')
    glossary = [('Complete search over every candidate answer in a bounded range', 'complete-search', []),
                ('Set operations', 'set-ops', [])]
    assert index_findings(ind, glossary) == []
    # The pages on the continuation line belong to the wrapped entry.
    assert index_findings(ind, glossary, glossary_pages={12}) == []
    assert index_findings(ind, glossary, glossary_pages={12, 14}) == [
        'FAIL: index glossary-only Complete search over every candidate answer in a bounded range']


def test_unit_headers_valid_checkpoint_key(tmp_path):
    headers = {'unit-11-bits': 'Bits', 'checkpoint-01-mock': 'Mock Contest'}
    write_publication_config(_book(tmp_path), unit_headers=headers)
    assert publication_config(tmp_path, 'book').unit_headers == headers


def test_unit_headers_give_a_checkpoint_chapter_its_short_head(tmp_path):
    entry = tmp_path / 'checkpoints' / 'checkpoint-02-mock-contest'
    _write(entry / 'checkpoint.ipynb', [
        md('# Checkpoint 2: A Full Mock Contest of Four Bronze Problems\n\nOpening task.', id='c0'),
        md('## Question 1', id='c1'), md('### First\n\nDo it.', id='c2')])
    with pytest.raises(ValueError, match='unit_headers'):
        render_chapter(entry, 'checkpoint', 'student', fixture_config())
    config = fixture_config(unit_headers={entry.name: 'Full Mock Contest'})
    body, _, _, _ = render_chapter(entry, 'checkpoint', 'student', config)
    assert '\\chaptermark{Checkpoint 2 — Full Mock Contest}' in body
