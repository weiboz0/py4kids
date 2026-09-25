"""Phase A output and turtle trace contracts."""

import ast
import contextlib
import copy
import io
import json

import nbformat
import pytest

from tools import cli, fake_turtle, notebooks
from tools.turtle_figure import figure_tikz


@pytest.fixture(autouse=True)
def kernel_without_sockets(monkeypatch):
    """Exercise output handling while the sandbox denies Jupyter kernel sockets."""
    def execute(notebook, _unit_dir):
        running = copy.deepcopy(notebook)
        namespace = {}

        def display(value):
            outputs.append(nbformat.v4.new_output("display_data", data={"text/plain": repr(value)}))

        namespace["display"] = display
        for cell in running.cells:
            if cell.cell_type != "code" or "no-exec" in cell.metadata.get("tags", []):
                continue
            outputs = []
            stdout, stderr = io.StringIO(), io.StringIO()
            try:
                tree = ast.parse(cell.source)
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    if tree.body and isinstance(tree.body[-1], ast.Expr):
                        body = ast.Module(body=tree.body[:-1], type_ignores=[])
                        exec(compile(body, "<fixture>", "exec"), namespace)  # noqa: S102 - fixture execution
                        value = eval(compile(ast.Expression(tree.body[-1].value), "<fixture>", "eval"), namespace)
                        if value is not None:
                            outputs.append(nbformat.v4.new_output(
                                "execute_result", data={"text/plain": repr(value)}, execution_count=1
                            ))
                    else:
                        exec(compile(tree, "<fixture>", "exec"), namespace)  # noqa: S102 - fixture execution
            except Exception as error:  # noqa: BLE001 - fixture records code-cell errors
                outputs.append(nbformat.v4.new_output("error", ename=type(error).__name__,
                                                      evalue=str(error), traceback=[]))
            for name, stream in (("stdout", stdout), ("stderr", stderr)):
                if stream.getvalue():
                    outputs.insert(0, nbformat.v4.new_output("stream", name=name, text=stream.getvalue()))
            cell.outputs = outputs
        return running

    monkeypatch.setattr(notebooks, "_executed_lesson", execute)


def _lesson(tmp_path, *cells, book="book1b"):
    unit = tmp_path / book / "units" / "unit-01-fixture"
    unit.mkdir(parents=True)
    path = unit / "lesson.ipynb"
    nbformat.write(nbformat.v4.new_notebook(cells=list(cells)), path)
    return path


def _code(source, *, tags=()):
    return nbformat.v4.new_code_cell(source, metadata={"tags": list(tags)})


def test_fill_check_round_trip_and_idempotence(tmp_path, capsys):
    path = _lesson(tmp_path, _code("print('hello')"), _code("print('world')"))
    before = nbformat.read(path, as_version=4)
    assert cli.main(["--root", str(tmp_path), "--book", "book1b", "fill-outputs"]) == 0
    filled = nbformat.read(path, as_version=4)
    assert [cell.outputs[0].text for cell in filled.cells] == ["hello\n", "world\n"]
    assert all(cell.execution_count is None for cell in filled.cells)
    assert filled.metadata == before.metadata
    assert [cell.metadata for cell in filled.cells] == [cell.metadata for cell in before.cells]
    once = path.read_bytes()
    assert cli.main(["--root", str(tmp_path), "--book", "book1b", "fill-outputs"]) == 0
    assert path.read_bytes() == once
    assert cli.main(["--root", str(tmp_path), "--book", "book1b", "lesson-outputs-check"]) == 0
    assert capsys.readouterr().out.endswith("lesson-outputs-check: PASS\n")


def test_fill_preserves_untouched_serialization(tmp_path):
    path = _lesson(tmp_path, _code("print('ok')"))
    notebook = json.loads(path.read_text())
    notebook["cells"][0]["outputs"] = [{"name": "stdout", "output_type": "stream", "text": ["ok\n"]}]
    path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n")
    before = path.read_bytes()
    assert notebooks.fill_outputs_findings(tmp_path, "book1b") == []
    assert path.read_bytes() == before


def test_stale_and_silent_outputs(tmp_path):
    path = _lesson(tmp_path, _code("print('fresh')"), _code("value = 3"))
    assert notebooks.fill_outputs_findings(tmp_path, "book1b") == []
    nb = nbformat.read(path, as_version=4)
    assert nb.cells[1].outputs == []
    nb.cells[0].outputs[0].text = "stale\n"
    nbformat.write(nb, path)
    assert notebooks.lesson_outputs_findings(tmp_path, "book1b") == [
        f"FAIL: unit-01-fixture: lesson code cell {nb.cells[0].id} output is stale"
    ]


def test_noexec_skipped_and_stored_output_rejected(tmp_path):
    path = _lesson(tmp_path, _code("raise RuntimeError('skip')", tags=["no-exec"]), _code("print('ok')"))
    assert notebooks.fill_outputs_findings(tmp_path, "book1b") == []
    nb = nbformat.read(path, as_version=4)
    assert nb.cells[0].outputs == []
    nb.cells[0].outputs = [nbformat.v4.new_output("stream", name="stdout", text="bad\n")]
    nbformat.write(nb, path)
    assert notebooks.lesson_outputs_findings(tmp_path, "book1b") == [
        f"FAIL: unit-01-fixture: lesson code cell {nb.cells[0].id} no-exec cell has stored output"
    ]
    assert notebooks.fill_outputs_findings(tmp_path, "book1b") == []
    assert nbformat.read(path, as_version=4).cells[0].outputs == []


def test_fill_unit_selector_only_changes_selected_unit(tmp_path):
    selected = _lesson(tmp_path, _code("print('one')"))
    other = selected.parent.parent / "unit-02-fixture"
    other.mkdir()
    second = other / "lesson.ipynb"
    nbformat.write(nbformat.v4.new_notebook(cells=[_code("print('two')")]), second)
    before = second.read_bytes()
    assert cli.main(["--root", str(tmp_path), "--book", "book1b", "--unit",
                     selected.parent.name, "fill-outputs"]) == 0
    assert second.read_bytes() == before
    assert nbformat.read(selected, as_version=4).cells[0].outputs


@pytest.mark.parametrize("source,kind", [
    ("import sys; print('oops', file=sys.stderr)", "stderr"),
    ("2 + 2", "execute_result"),
    ("display('x')", "display_data"),
    ("raise ValueError('broken')", "error"),
])
def test_non_stdout_rejected(tmp_path, source, kind):
    path = _lesson(tmp_path, _code(source))
    cell_id = nbformat.read(path, as_version=4).cells[0].id
    expected = f"FAIL: unit-01-fixture: lesson code cell {cell_id} produced non-stdout output ({kind})"
    assert notebooks.fill_outputs_findings(tmp_path, "book1b") == [expected]
    assert notebooks.lesson_outputs_findings(tmp_path, "book1b") == [expected]


@pytest.mark.parametrize("book", ["book1", "book2"])
def test_unpopulated_other_book_skips(tmp_path, capsys, book):
    _lesson(tmp_path, _code("print('ok')"), book=book)
    assert cli.main(["--root", str(tmp_path), "--book", book, "lesson-outputs-check"]) == 0
    assert capsys.readouterr().out == "lesson-outputs-check: SKIP (plan 086)\n"


def test_segments_square_and_penup_and_reset():
    fake_turtle.reset()
    fake_turtle.pencolor("royalblue")
    fake_turtle.pensize(3)
    for _ in range(4):
        fake_turtle.forward(10)
        fake_turtle.left(90)
    segments = fake_turtle.segments()
    assert len(segments) == 4
    assert segments[0] == (0.0, 0.0, 10.0, 0.0, "royalblue", 3)
    assert segments[-1][2:4] == pytest.approx((0, 0))
    fake_turtle.penup()
    fake_turtle.forward(5)
    assert fake_turtle.segments() == segments
    segments.clear()
    assert len(fake_turtle.segments()) == 4
    fake_turtle.reset()
    assert fake_turtle.segments() == []


def test_figure_square_and_unsupported_call():
    source = "import turtle\nturtle.color('royalblue')\nturtle.pensize(2)\nfor _ in range(4):\n turtle.forward(10)\n turtle.left(90)\n"
    figure = figure_tikz(source)
    assert figure.count(" -- ") == 4
    assert figure.count("\\draw[") == 4
    assert "color=RoyalBlue" in figure
    assert "circle" in figure
    assert "0.8\\textwidth" in figure
    assert "7cm" in figure
    assert figure_tikz("import turtle\nturtle.forward(1)").count(" -- ") == 1
    assert "color=Crimson" in figure_tikz("import turtle\nturtle.pencolor('crimson')\nturtle.forward(1)")
    assert "color=black" in figure_tikz("import turtle\nturtle.pencolor('not-a-color')\nturtle.forward(1)")
    with pytest.raises(RuntimeError, match="turtle figure replay failed: .*unsupported_method"):
        figure_tikz("import turtle\nturtle.unsupported_method()")
