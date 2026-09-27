"""Plan 088 turtle input, parity, and publication contracts."""
from pathlib import Path

import nbformat
import pytest

from tools import publish
from tools.publish_audit import _turtle_drawing_findings
from tools.turtle_figure import figure_tikz
from tools.turtle_real import turtle_real_findings


def fixture_unit(tmp_path, real=None, asset=None, sample='10', statement=True, asset_name='solutions_ex1_square.py'):
    unit = tmp_path / 'fixture' / 'units' / 'unit-06-turtle'
    (unit / 'assets').mkdir(parents=True, exist_ok=True)
    asset = asset or 'import turtle\nturtle.pencolor("red")\nturtle.forward(10)\nturtle.penup()\nturtle.backward(10)\nturtle.done()\n'
    (unit / 'assets' / asset_name).write_text(asset)
    if real is None:
        real = 'import turtle\nside = int(input())\nturtle.pencolor("red")\nturtle.forward(side)\nturtle.penup()\nturtle.backward(side)\nturtle.done()'
    phrase = '\n\n**Real version:** see the solution.' if statement else ''
    nbformat.write(nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell('## Exercise 1\n\n### Square' + phrase)]), unit / 'exercises.ipynb')
    cells = [nbformat.v4.new_markdown_cell('## Exercise 1\n\n**Solution asset:** `assets/' + asset_name + '`')]
    if real is not False:
        cells.append(nbformat.v4.new_markdown_cell('**The real program**\n\n```python\n' + real + '\n```' + ('' if sample is None else '\n\nSample input:\n\n```text\n' + sample + '\n```')))
    nbformat.write(nbformat.v4.new_notebook(cells=cells), unit / 'solutions.ipynb')
    return unit


def findings(tmp_path, **kwargs):
    fixture_unit(tmp_path, **kwargs)
    return turtle_real_findings(tmp_path, 'fixture')


def test_parity_and_suffixed_asset(tmp_path):
    assert findings(tmp_path) == []


@pytest.mark.parametrize(('real', 'expected'), [
    ('import turtle\nside=int(input())\nturtle.pencolor("blue")\nturtle.forward(side)\nturtle.penup()\nturtle.backward(side)', 'segment'),
    ('import turtle\nside=int(input())\nturtle.pencolor("red")\nturtle.forward(side + 1)\nturtle.penup()\nturtle.backward(side + 1)', 'segment'),
    ('import turtle\nside=int(input())\nturtle.pencolor("red")\nturtle.forward(side)', 'final state'),
])
def test_parity_failures(tmp_path, real, expected):
    assert any(expected in item for item in findings(tmp_path, real=real))


def test_missing_fence_and_sample(tmp_path):
    assert any('missing real-program fence' in item for item in findings(tmp_path, real=False))
    assert any('missing Sample input' in item for item in findings(tmp_path, sample=None))


def test_unconsumed_input(tmp_path):
    assert any('unconsumed input' in item for item in findings(tmp_path, sample='10\n20'))


def test_figure_stdin_and_header():
    source = 'import turtle\nturtle.forward(int(input()))'
    assert '(10,0)' in figure_tikz(source, stdin='10')
    assert '(10,0)' in figure_tikz('# sample-input: 10\n' + source)
    with pytest.raises(RuntimeError, match='sample input'):
        figure_tikz(source)


def test_turtle_check_header(tmp_path):
    from tools.fake_turtle import turtle_findings
    unit = tmp_path / 'fixture' / 'units' / 'unit-06-turtle'
    (unit / 'assets').mkdir(parents=True)
    asset = unit / 'assets' / 'input.py'
    asset.write_text('# sample-input: 4 | 10\nimport turtle\nn=int(input("Sides: "))\nside=int(input("Length: "))\nfor i in range(n):\n turtle.forward(side)\n turtle.left(360/n)\n')
    assert turtle_findings(tmp_path, 'fixture') == []
    asset.write_text(asset.read_text().replace('# sample-input: 4 | 10\n', ''))
    assert any('sample-input' in item for item in turtle_findings(tmp_path, 'fixture'))


def test_tryit_route_and_figure():
    cell = nbformat.v4.new_code_cell('import turtle\nturtle.forward(int(input()))', metadata={'tags': ['no-exec'], 'sample_input': '10'})
    kind, body = publish.route_code(cell)
    assert kind == 'tryit+figure'
    assert 'tryit' in body
    assert 'Drawing for the sample input: 10}\n\\end{pubfigure}' in body  # one caption, inside the frame
    assert 'Drawing made by the program above' not in body
    assert '(10,0)' in body


def test_referenced_input_asset_figure(tmp_path):
    entry = tmp_path / 'book1b' / 'units' / 'unit-06-fixture'
    (entry / 'assets').mkdir(parents=True)
    (entry / 'assets' / 'l1_square_input.py').write_text(
        '# sample-input: 10\nimport turtle\nturtle.forward(int(input("Length: ")))' + '\n')
    rendered, records = publish.asset_blocks('Run assets/l1_square_input.py', entry,
                                             'student', set(), entry.name)
    assert records == [{'id': 'asset:l1_square_input.py', 'kind': 'asset listing'}]
    assert '(10,0)' in rendered


def test_answer_key_real_figure(tmp_path):
    unit = fixture_unit(tmp_path)
    key = publish.answer_key(unit, 'unit', [{'number': 1, 'title': 'Square'}])
    assert '**The real program**' in key
    assert 'Sample input:' in key
    assert key.count('\\begin{pubfigure}') >= 2


def test_publication_audit_requires_real_drawing(tmp_path):
    unit = fixture_unit(tmp_path)
    renamed = unit.with_name('unit-16-turtle')
    unit.rename(renamed)
    unit = renamed
    nbformat.write(nbformat.v4.new_notebook(cells=[]), unit / 'lesson.ipynb')
    key = publish.answer_key(unit, 'unit', [{'number': 1, 'title': 'Square'}])
    assert _turtle_drawing_findings(unit, key, 'teacher') == []
    assert any('Exercise 1 real-program drawing' in finding for finding in
               _turtle_drawing_findings(unit, key.replace('Drawing for the sample input: 10', ''), 'teacher'))


def test_book1b_21_rows():
    root = Path(__file__).resolve().parents[1]
    assert turtle_real_findings(root, 'book1b') == []
