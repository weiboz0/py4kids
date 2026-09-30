"""Plan 097 Phase C/D: the missing-glyph check (tools/pdf_glyphs.py) on crafted LaTeX logs, and
the handout/syllabus/patterns build contract that runs it (design 010 D4)."""

from pathlib import Path

from tools import pdf_glyphs

REPO = Path(__file__).resolve().parents[1]

LUATEX_LOG = """This is LuaHBTeX, Version 1.15.0 (TeX Live 2022/Debian)  (format=lualatex 2023.1.1)
(./unit-05.tex
Missing character: There is no ⊕ (U+2295) in font FiraMono:mode=node;script=la
tn;language=dflt;+tlig;!
Missing character: There is no ⊕ (U+2295) in font AtkinsonHyperlegible:mode=no
de;script=latn;language=dflt;+tlig;!
Missing character: There is no ₀ (U+2080) in font AtkinsonHyperlegible/B:mode=
node;script=latn;language=dflt;+tlig;!
Output written on unit-05.pdf (2 pages, 12345 bytes).
"""

XETEX_LOG = """This is XeTeX, Version 3.141592653-2.6-0.999994
Missing character: There is no ✓ in font lmroman10-regular!
Output written on syllabus.pdf (3 pages).
"""

CLEAN_LOG = """This is LuaHBTeX, Version 1.15.0
LaTeX Font Info:    Font shape `TU/AtkinsonHyperlegible(0)/m/n' will be
(Font)              scaled to size 10.0pt on input line 12.
Output written on unit-01.pdf (1 page, 999 bytes).
"""


def test_luatex_missing_characters_are_listed_with_code_points_and_fonts():
    found = pdf_glyphs.missing_characters(LUATEX_LOG)
    assert found == [('⊕', 'U+2295', 'FiraMono'),
                     ('⊕', 'U+2295', 'AtkinsonHyperlegible'),
                     ('₀', 'U+2080', 'AtkinsonHyperlegible/B')]
    summary = pdf_glyphs.summarize(found)
    assert '⊕ U+2295 x2 (AtkinsonHyperlegible, FiraMono)' in summary
    assert '₀ U+2080 x1 (AtkinsonHyperlegible/B)' in summary


def test_xetex_missing_character_without_code_point():
    assert pdf_glyphs.missing_characters(XETEX_LOG) == [('✓', 'U+2713', 'lmroman10-regular')]


def test_clean_log_has_no_missing_characters():
    assert pdf_glyphs.missing_characters(CLEAN_LOG) == []
    assert pdf_glyphs.missing_characters('') == []


def test_cli_fails_with_the_list_and_passes_clean_logs(tmp_path, capsys):
    bad = tmp_path / 'unit-05.log'
    bad.write_text(LUATEX_LOG, encoding='utf-8')
    good = tmp_path / 'unit-01.log'
    good.write_text(CLEAN_LOG, encoding='utf-8')
    assert pdf_glyphs.main([str(good)]) == 0
    assert 'PASS' in capsys.readouterr().out
    assert pdf_glyphs.main([str(good), str(bad)]) == 1
    err = capsys.readouterr().err
    assert f'FAIL: {bad}: 3 missing character(s):' in err
    assert 'U+2295 x2' in err and 'U+2080 x1' in err
    assert str(good) not in err


def test_cli_fails_on_a_missing_log(tmp_path, capsys):
    assert pdf_glyphs.main([str(tmp_path / 'absent.log')]) == 1
    assert 'LaTeX log not found' in capsys.readouterr().err


def test_undecodable_bytes_do_not_hide_a_report(tmp_path):
    log = tmp_path / 'broken.log'
    log.write_bytes(b'\xff\xfe junk\n' + 'Missing character: There is no ⌊ (U+230A) in font '
                    'FiraMono:mode=node\n'.encode())
    assert pdf_glyphs.check_logs([log]) and 'U+230A' in pdf_glyphs.check_logs([log])[0]


def test_build_pdf_is_two_step_lualatex_with_a_checked_log():
    text = (REPO / 'scripts' / 'build-pdf.sh').read_text(encoding='utf-8')
    assert 'xelatex' not in text and '--pdf-engine' not in text and '--to pdf' not in text
    assert 'PDFExporter' not in text
    assert 'jupyter nbconvert --to latex --template-file "$templates/handout.tex.j2"' in text
    assert 'pandoc "$source" -s --template "$templates/pandoc.latex" -o "$tex_dir/$stem.tex"' in text
    assert 'lualatex -interaction=nonstopmode -halt-on-error' in text
    assert 'uv run python -m tools.pdf_glyphs "$dir/$stem.log"' in text
    # Every handout, the syllabus and patterns.pdf go through the one compile + check.
    assert text.count('compile "$tex_dir"') == 2
    assert 'pandoc_pdf "$book_root/syllabus.md" syllabus' in text
    assert 'pandoc_pdf "$book_root/reference/patterns.md" patterns' in text
    assert 'latex_root="$book_root/build/latex"' in text


def test_templates_use_the_book_fonts_and_fallback():
    templates = REPO / 'tools' / 'pdf_templates'
    handout = (templates / 'handout.tex.j2').read_text(encoding='utf-8')
    assert "extends 'index.tex.j2'" in handout and '((( super() )))' in handout
    assert r'\usepackage{py4kidsfonts}' in handout
    assert r'\usepackage{py4kidsfonts}' in (templates / 'pandoc.latex').read_text(encoding='utf-8')
    sty = (templates / 'py4kidsfonts.sty').read_text(encoding='utf-8')
    theme = (REPO / 'tools' / 'publish_theme' / 'theme.tex').read_text(encoding='utf-8')
    # The same fallback chains and font settings as the book theme.
    for text in (sty, theme):
        assert 'luaotfload.add_fallback("pubfallback", {"DejaVu Sans:mode=node;", "DejaVu Sans Mono:mode=node;"})' in text
        assert r'\setmonofont{Fira Mono}[RawFeature={fallback=pubfallbackmono},' in text
    for line in theme.splitlines():
        if 'add_fallback' in line or line.startswith((r'\setmainfont', r'\setsansfont', r'\setmonofont',
                                                     '  BoldFeatures')):
            assert line in sty.splitlines(), line
