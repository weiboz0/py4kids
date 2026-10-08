"""Plan 097 Phase C/D: change-scoped book-edition renders in ci-local.sh (design 010 D7,
tools/ci_scope.py), and ci-local's step 5 building handouts and syllabi for every book (D5)."""

import subprocess
from pathlib import Path

import pytest

from tools import ci_scope

REPO = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('changed, render, reason', [
    (['python-concepts/units/unit-01-x/lesson.ipynb'], True, 'book changed'),
    (['python-concepts/publication.yaml'], True, 'book changed'),
    (['tools/publish.py'], True, 'shared input changed'),
    (['tools/pdf_templates/pandoc.latex'], True, 'shared input changed'),
    (['scripts/build-book.sh'], True, 'shared input changed'),
    (['books.yaml'], True, 'shared input changed'),
    (['pyproject.toml'], True, 'shared input changed'),
    (['uv.lock'], True, 'shared input changed'),
    (['acsl/pyproject.toml', 'docs/uv.lock'], False, 'no change'),  # only the repo-root files
    (['acsl/units/unit-05-x/lesson.ipynb', 'docs/plans/097.md', 'tests/test_x.py'], False, 'no change'),
    (['python-concepts-notes.md', 'python-conceptsx/a.md'], False, 'no change'),
    ([], False, 'no change'),
])
def test_decide(changed, render, reason):
    decision = ci_scope.decide('python-concepts', changed)
    assert decision[0] is render
    assert decision[1].startswith(reason)


def test_decide_all_books_and_reasons_name_the_paths():
    assert ci_scope.decide('python-concepts', [], all_books=True) == (True, '--all-books')
    render, reason = ci_scope.decide('acsl', [f'acsl/u{i}.md' for i in range(5)])
    assert render and reason == 'book changed: acsl/u0.md, acsl/u1.md, acsl/u2.md (+2 more)'
    render, reason = ci_scope.decide('acsl', ['python-concepts/a.md'])
    assert not render and 'acsl/' in reason and '--all-books' in reason


def _git(repo, *args):
    subprocess.run(['git', *args], cwd=repo, check=True, capture_output=True,
                   env={'GIT_AUTHOR_NAME': 't', 'GIT_AUTHOR_EMAIL': 't@t', 'GIT_COMMITTER_NAME': 't',
                        'GIT_COMMITTER_EMAIL': 't@t', 'HOME': str(repo), 'PATH': '/usr/bin:/bin'})


@pytest.fixture
def repo(tmp_path):
    (tmp_path / 'books.yaml').write_text(
        'books:\n- id: alpha\n  root: alpha\n- id: beta\n  root: beta\n', encoding='utf-8')
    for name in ('alpha/a.md', 'beta/b.md', 'tools/t.py', 'docs/d.md'):
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text('x\n', encoding='utf-8')
    _git(tmp_path, 'init', '-q', '-b', 'main')
    _git(tmp_path, 'add', '.')
    _git(tmp_path, 'commit', '-q', '-m', 'base')
    _git(tmp_path, 'update-ref', 'refs/remotes/origin/main', 'HEAD')
    _git(tmp_path, 'checkout', '-q', '-b', 'feature')
    return tmp_path


def test_changed_files_cover_commits_staged_unstaged_and_untracked(repo):
    assert ci_scope.changed_files(repo) == []
    (repo / 'alpha' / 'a.md').write_text('y\n', encoding='utf-8')
    _git(repo, 'commit', '-q', '-am', 'branch change')
    (repo / 'docs' / 'd.md').write_text('y\n', encoding='utf-8')      # unstaged
    (repo / 'docs' / 'new.md').write_text('y\n', encoding='utf-8')    # untracked
    assert ci_scope.changed_files(repo) == ['alpha/a.md', 'docs/d.md', 'docs/new.md']
    assert ci_scope.scope(repo, 'alpha')[0] is True
    render, reason = ci_scope.scope(repo, 'beta')
    assert render is False and reason.startswith('no change under beta/')


def test_a_change_on_main_after_the_branch_point_does_not_count(repo):
    _git(repo, 'checkout', '-q', 'main')
    (repo / 'beta' / 'b.md').write_text('main moved\n', encoding='utf-8')
    _git(repo, 'commit', '-q', '-am', 'main change')
    _git(repo, 'update-ref', 'refs/remotes/origin/main', 'HEAD')
    _git(repo, 'checkout', '-q', 'feature')
    assert ci_scope.scope(repo, 'beta')[0] is False   # origin/main...HEAD is the branch's own diff


def test_shared_tool_change_renders_every_book(repo):
    (repo / 'tools' / 't.py').write_text('changed\n', encoding='utf-8')
    for book in ('alpha', 'beta'):
        render, reason = ci_scope.scope(repo, book)
        assert render and reason == 'shared input changed: tools/t.py'


def test_no_base_renders_to_be_safe(repo, capsys):
    _git(repo, 'update-ref', '-d', 'refs/remotes/origin/main')
    render, reason = ci_scope.scope(repo, 'beta')
    assert render and 'cannot compute the change set' in reason
    assert ci_scope.main(['--book', 'beta', '--repo', str(repo)]) == 0
    assert capsys.readouterr().out.startswith('render: cannot compute the change set')
    assert ci_scope.main(['--book', 'beta', '--repo', str(repo), '--all-books']) == 0
    assert capsys.readouterr().out == 'render: --all-books\n'


def test_unknown_book_fails(repo):
    with pytest.raises(ValueError, match='unknown book'):
        ci_scope.scope(repo, 'gamma')


def test_ci_local_step_5_builds_pdfs_for_every_book_and_scopes_renders():
    text = (REPO / 'scripts' / 'ci-local.sh').read_text(encoding='utf-8')
    step5 = text[text.index('step "5/7 PDF build"'):text.index('step "6/7 site"')]
    # D5: no judge gate around the handout/syllabus build.
    assert 'has_flag judge' not in step5
    loop = step5.index('while read -r book flags')
    assert step5.index('bash scripts/build-pdf.sh --book "$book"') > loop
    assert step5.index('bash scripts/build-pdf.sh --book "$book"') < step5.index('has_flag publication')
    # D7: the render and the audit follow the scope decision, and both are reported.
    decision = step5.index('uv run python -m tools.ci_scope --book "$book" "${scope_args[@]}"')
    assert decision < step5.index('bash scripts/build-book.sh') < step5.index('py4kids-tools --book "$book" publish-audit')
    assert 'if [[ "$decision" == render:* ]]; then' in step5
    assert 'echo "book editions: $book: $decision"' in step5
    assert 'SKIP: $book: book editions and publish-audit' in step5
    assert 'book editions rendered:' in step5
    assert '--all-books) scope_args=(--all-books) ;;' in text


# --- plan 103 Phase A: `--site` scopes the learning-website build ------------------------------

SITE_ROOTS = ['python-projects', 'acsl']


@pytest.mark.parametrize('changed, render, reason', [
    (['site/src/pages/index.astro'], True, 'site input changed'),
    (['site/pnpm-lock.yaml'], True, 'site input changed'),
    (['runner/src/worker.ts'], True, 'site input changed'),
    (['site/ids/acsl.json'], True, 'site input changed'),
    (['tools/export/bundle.py'], True, 'site input changed'),
    (['scripts/build-site.sh'], True, 'site input changed'),
    (['books.yaml'], True, 'site input changed'),
    (['.nvmrc'], True, 'site input changed'),
    (['uv.lock'], True, 'site input changed'),                     # the exporter's dependencies
    (['acsl/units/unit-05-x/lesson.ipynb'], True, 'site book changed'),
    (['python-projects/site.yaml'], True, 'site book changed'),
    (['recsys/units/unit-01-x/lesson.ipynb'], False, 'no change'),   # not a site book
    (['docs/plans/103.md', 'tests/test_x.py', 'sitex/a.md', 'acslx/a.md'], False, 'no change'),
    (['site.md', 'x/.nvmrc'], False, 'no change'),
    ([], False, 'no change'),
])
def test_decide_site(changed, render, reason):
    decision = ci_scope.decide_site(SITE_ROOTS, changed)
    assert decision[0] is render
    assert decision[1].startswith(reason)


def test_decide_site_all_books_and_reason():
    assert ci_scope.decide_site(SITE_ROOTS, [], all_books=True) == (True, '--all-books')
    render, reason = ci_scope.decide_site(SITE_ROOTS, ['docs/a.md'])
    assert not render
    assert reason == ('no change under site/, runner/, tools/, scripts/, books.yaml, .nvmrc, pyproject.toml, '
                      'uv.lock or a site book (python-projects/, acsl/) since origin/main')


@pytest.fixture
def site_repo(repo):
    (repo / 'books.yaml').write_text(
        'books:\n- id: alpha\n  root: alpha\n  site: true\n- id: beta\n  root: beta\n',
        encoding='utf-8')
    _git(repo, 'commit', '-q', '-am', 'flags')
    _git(repo, 'update-ref', 'refs/remotes/origin/main', 'HEAD')
    return repo


def test_site_scope_keys_on_the_site_flag(site_repo):
    assert ci_scope.site_roots(site_repo) == ['alpha']
    assert ci_scope.site_scope(site_repo)[0] is False
    (site_repo / 'beta' / 'b.md').write_text('y\n', encoding='utf-8')
    assert ci_scope.site_scope(site_repo)[0] is False                  # beta has no site flag
    (site_repo / 'alpha' / 'a.md').write_text('y\n', encoding='utf-8')
    render, reason = ci_scope.site_scope(site_repo)
    assert render and reason == 'site book changed: alpha/a.md'


def test_site_cli(site_repo, capsys):
    assert ci_scope.main(['--site', '--repo', str(site_repo)]) == 0
    assert capsys.readouterr().out.startswith('skip: no change under site/')
    (site_repo / '.nvmrc').write_text('24\n', encoding='utf-8')         # untracked counts
    assert ci_scope.main(['--site', '--repo', str(site_repo)]) == 0
    assert capsys.readouterr().out == 'render: site input changed: .nvmrc\n'
    assert ci_scope.main(['--site', '--all-books', '--repo', str(site_repo)]) == 0
    assert capsys.readouterr().out == 'render: --all-books\n'
    _git(site_repo, 'update-ref', '-d', 'refs/remotes/origin/main')
    assert ci_scope.main(['--site', '--repo', str(site_repo)]) == 0
    assert capsys.readouterr().out.startswith('render: cannot compute the change set')


@pytest.mark.parametrize('argv', [[], ['--book', 'alpha', '--site']])
def test_cli_needs_exactly_one_of_book_or_site(site_repo, argv):
    with pytest.raises(SystemExit) as error:
        ci_scope.main([*argv, '--repo', str(site_repo)])
    assert error.value.code == 2


def test_ci_local_site_step():
    text = (REPO / 'scripts' / 'ci-local.sh').read_text(encoding='utf-8')
    pdf = text.index('step "5/7 PDF build"')
    site = text.index('step "6/7 site"')
    guard = text.index('step "7/7 pre-merge guard"')
    assert pdf < site < guard
    step6 = text[site:guard]
    decision = step6.index('uv run python -m tools.ci_scope --site "${scope_args[@]}"')
    assert decision < step6.index('bash scripts/build-site.sh') < step6.index('-C site test')
    # Scope first; an in-scope change with a missing tool FAILS (never a silent green); only an
    # out-of-scope change skips.
    assert decision < step6.index('if ! site_node_env')
    assert 'FAIL: site in scope but node >= 22.12 is missing' in step6
    assert 'FAIL: site in scope but pnpm is missing' in step6
    assert 'FAIL: site in scope but no Chromium was found' in step6
    assert 'SKIP (Node missing)' not in step6
    assert 'SKIP: site (' in step6
