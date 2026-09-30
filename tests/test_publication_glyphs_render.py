"""Plan 097 Phase D: real renders through the D4 font fallback (design 010).

A minimal Quarto book through the book theme, a one-cell nbconvert handout and a pandoc syllabus
through the tools/pdf_templates templates, each with one character from every D4 range in prose,
inline code and a code block, compile with no "Missing character" in the LaTeX log.
These are slow (a Quarto render and several lualatex runs); ci-local runs them with the rest of
pytest. Outside ci-local a missing tool skips them; under ci-local (PY4KIDS_CI=1) it fails.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

import nbformat
import pytest
import yaml

from tools.pdf_glyphs import missing_characters

REPO = Path(__file__).resolve().parents[1]
THEME = REPO / 'tools' / 'publish_theme'
TEMPLATES = REPO / 'tools' / 'pdf_templates'

# One character from each D4 range, plus the ranges panels.lua already wrapped.
GLYPHS = {
    'arrows': '→ ← ↑ ⇒',
    'math operators U+2200–22FF': '⊕ ⊙ ≤ ≥ ≠ −',
    'misc technical U+2300–23FF': '⌊ ⌋',
    'sub/superscripts U+2070–209F': 'x₀ x₁ ₈ ⁿ ⁴',
    'box drawing U+2500–257F': '─ │ ┌ ┐ └ ┘',
    'dingbats U+2700–27BF': '✓ ✗',
    'greek': 'λ',
}
SAMPLE = ' '.join(GLYPHS.values())
pytestmark = pytest.mark.slow


def _need(*tools):
    missing = [tool for tool in tools if shutil.which(tool) is None]
    if missing:
        if os.environ.get('PY4KIDS_CI') == '1':
            pytest.fail(f'ci-local needs {", ".join(missing)}')
        pytest.skip(f'{", ".join(missing)} not installed')


def _lualatex(directory: Path, stem: str, extra_inputs: list[Path] = ()) -> str:
    env = dict(os.environ)
    env['TEXINPUTS'] = ':'.join(str(path) for path in [*extra_inputs]) + ':'
    subprocess.run(['lualatex', '-interaction=nonstopmode', '-halt-on-error', f'{stem}.tex'],
                   cwd=directory, env=env, capture_output=True, check=False)
    log = (directory / f'{stem}.log').read_text(encoding='utf-8', errors='replace')
    assert f'Output written on {stem}.pdf' in log, log[-2000:]
    return log


def _assert_no_missing(log: str):
    assert missing_characters(log) == [], missing_characters(log)[:10]


def _pdf_text(pdf: Path) -> str | None:
    if shutil.which('pdftotext') is None:
        return None
    return subprocess.run(['pdftotext', str(pdf), '-'], capture_output=True, text=True,
                          check=True).stdout


def test_the_theme_sets_the_quarto_fonts_with_fallback():
    text = (THEME / '_quarto.yml').read_text(encoding='utf-8')
    text = text.replace('@FRONT@', '    - index.qmd').replace('@CHAPTERS@', '    - a.qmd')
    config = yaml.safe_load(re.sub(r'@[A-Z]+@', 'x', text))
    theme = (THEME / 'theme.tex').read_text(encoding='utf-8')
    pdf = config['format']['pdf']
    assert pdf['pdf-engine'] == 'lualatex'
    assert f'\\setmainfont{{{pdf["mainfont"]}}}[RawFeature={{fallback=pubfallback}},' in theme
    assert f'\\setmonofont{{{pdf["monofont"]}}}[RawFeature={{fallback=pubfallbackmono}},' in theme
    assert r'\setsansfont{Atkinson Hyperlegible}[RawFeature={fallback=pubfallback},' in theme
    # The fallback is declared before any font uses it.
    assert theme.index('luaotfload.add_fallback') < theme.index(r'\setmainfont')
    # panels.lua keeps its x-height-matched \fallbackfont wrapping and the inline-code breaks.
    lua = (THEME / 'panels.lua').read_text(encoding='utf-8')
    assert r'\newfontfamily\fallbackfont{DejaVu Sans}' in theme
    assert "'{\\\\fallbackfont '" in lua and '\\\\allowbreak{}' in lua


def test_book_theme_render_has_no_missing_glyph(tmp_path):
    _need('quarto', 'lualatex')
    project = tmp_path / 'book'
    shutil.copytree(THEME, project / 'theme')
    theme = project / 'theme' / 'theme.tex'
    theme.write_text(re.sub(r'@[A-Z]+@', 'Glyph Test', theme.read_text(encoding='utf-8')),
                     encoding='utf-8')
    config = (THEME / '_quarto.yml').read_text(encoding='utf-8')
    for placeholder, value in (('@OUTPUT@', 'glyphs'), ('@CLASSOPTION@', 'open=any'),
                               ('@FRONT@', '    - index.qmd'), ('@CHAPTERS@', '    - glyphs.qmd')):
        config = config.replace(placeholder, value)
    (project / '_quarto.yml').write_text(re.sub(r'@[A-Z]+@', 'Glyph Test', config), encoding='utf-8')
    (project / 'index.qmd').write_text('# Preface\n\nA glyph test.\n', encoding='utf-8')
    (project / 'glyphs.qmd').write_text(
        f'# Glyphs {SAMPLE}\n\n'
        f'## Section {SAMPLE}\n\n'
        f'Prose: {SAMPLE}. **Bold: {SAMPLE}.** *Italic: {SAMPLE}.*\n\n'
        f'Inline code: `{SAMPLE}` and **`{SAMPLE}`**.\n\n'
        f'```python\nprint("{SAMPLE}")\n# {SAMPLE}\n```\n\n'
        f'::: {{.tryit}}\n```python\nprint("{SAMPLE}")\n```\n:::\n', encoding='utf-8')
    env = dict(os.environ, TEXMFCACHE=str(tmp_path / 'tex'), XDG_CACHE_HOME=str(tmp_path / 'xdg'))
    result = subprocess.run(['quarto', 'render', str(project), '--to', 'pdf'], env=env,
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0, (result.stdout + result.stderr)[-3000:]
    tex = (project / 'glyphs.tex').read_text(encoding='utf-8')
    for sample in GLYPHS.values():
        for char in sample.replace(' ', ''):
            assert char in tex, char
    # Quarto discards its LaTeX log; a draft pass gives one, as build-book.sh does for the audit.
    _assert_no_missing(_lualatex(project, 'glyphs'))
    text = _pdf_text(project / '_book' / 'glyphs.pdf')
    if text is not None:
        for char in '⊕⌊₀─✓':
            assert char in text, char


def test_handout_template_render_has_no_missing_glyph(tmp_path):
    _need('lualatex')
    notebook = nbformat.v4.new_notebook(cells=[
        nbformat.v4.new_markdown_cell(f'# Unit\n\n## Exercise 1\n\nProse {SAMPLE} and `{SAMPLE}`.'),
        nbformat.v4.new_code_cell(f'print("{SAMPLE}")  # {SAMPLE}'),
    ])
    source = tmp_path / 'exercises.ipynb'
    nbformat.write(notebook, source)
    out = tmp_path / 'handout'
    env = dict(os.environ, JUPYTER_CONFIG_DIR=str(tmp_path / 'jupyter'))
    subprocess.run(['jupyter', 'nbconvert', '--to', 'latex', '--template-file',
                    str(TEMPLATES / 'handout.tex.j2'), '--output', 'unit', '--output-dir', str(out),
                    str(source)], env=env, check=True, capture_output=True)
    tex = (out / 'unit.tex').read_text(encoding='utf-8')
    assert r'\usepackage{py4kidsfonts}' in tex and '⊕' in tex
    _assert_no_missing(_lualatex(out, 'unit', [TEMPLATES, tmp_path]))
    text = _pdf_text(out / 'unit.pdf')
    if text is not None:
        assert '⊕' in text and '✓' in text


def _pandoc(tmp_path: Path, markdown: str) -> tuple[Path, str]:
    out = tmp_path / 'syllabus'
    out.mkdir()
    (out / 'syllabus.md').write_text(markdown, encoding='utf-8')
    subprocess.run(['pandoc', 'syllabus.md', '-s', '--template', str(TEMPLATES / 'pandoc.latex'),
                    '-o', 'syllabus.tex'], cwd=out, check=True, capture_output=True)
    return out, _lualatex(out, 'syllabus', [TEMPLATES])


def test_syllabus_template_render_has_no_missing_glyph(tmp_path):
    _need('pandoc', 'lualatex')
    out, log = _pandoc(tmp_path, (
        f'# Syllabus {SAMPLE}\n\nProse {SAMPLE}, **bold {SAMPLE}**, `{SAMPLE}`.\n\n'
        '| Unit | Topic |\n|---|---|\n'
        f'| `unit-01` | {SAMPLE} |\n\n'
        f'- item {SAMPLE}\n- [link](https://example.com)\n\n```\n{SAMPLE}\n```\n'))
    _assert_no_missing(log)
    text = _pdf_text(out / 'syllabus.pdf')
    if text is not None:
        assert '⊕' in text and '≥' in text


def test_the_check_catches_a_glyph_no_font_has(tmp_path):
    """The negative control: a character outside every font (and its fallback) is reported."""
    _need('pandoc', 'lualatex')
    _, log = _pandoc(tmp_path, '# Syllabus\n\nA private-use glyph: .\n')
    assert [code for _, code, _ in missing_characters(log)][:1] == ['U+E000']
