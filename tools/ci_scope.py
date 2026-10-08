"""Change-scoped book-edition renders for `scripts/ci-local.sh` (design 010 D7, plan 097 Phase C).

A publication book's four editions take minutes each to render, so ci-local renders a book only
when the change touches it:
- the book renders when `git diff origin/main...HEAD` plus the uncommitted changes (staged,
  unstaged and untracked) touch its root, which includes its `publication.yaml`;
- any change under `tools/` or `scripts/`, or to `books.yaml`, `pyproject.toml` or `uv.lock` (the
  toolchain's dependencies), renders every publication book
  (the publisher imports `tools/books.py`, the turtle modules and other tools);
- `--all-books` renders every publication book (required before a release);
- when the change set cannot be computed (no `origin/main`, not a git checkout), every book renders.

`--site` (plan 103 Phase A) scopes the learning-website build the same way: it renders when the
change touches `site/`, `runner/`, `tools/`, `scripts/`, `books.yaml`, `.nvmrc`, `pyproject.toml`, `uv.lock`,
or the root of any book whose `books.yaml` entry has `site: true` (the site keys on that flag, never
on a book id).

Usage: python -m tools.ci_scope (--book <id> | --site) [--all-books]
Prints one line, `render: <reason>` or `skip: <reason>`, and exits 0 either way.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import yaml

BASE = 'origin/main'
SHARED_DIRS = ('tools/', 'scripts/')
SHARED_FILES = ('books.yaml', 'pyproject.toml', 'uv.lock')
SITE_DIRS = ('site/', 'runner/', *SHARED_DIRS)
SITE_FILES = ('books.yaml', '.nvmrc', 'pyproject.toml', 'uv.lock')


class ScopeError(RuntimeError):
    """The change set could not be computed."""


def _git(repo: Path, *args: str) -> list[str]:
    try:
        result = subprocess.run(['git', *args], cwd=repo, capture_output=True, text=True, check=False)
    except OSError as error:
        raise ScopeError(f'git unavailable: {error}') from error
    if result.returncode != 0:
        raise ScopeError(f'git {" ".join(args)} failed: {result.stderr.strip()}')
    return [line for line in result.stdout.splitlines() if line.strip()]


def changed_files(repo: Path, base: str = BASE) -> list[str]:
    """Repo-relative paths changed on this branch since `base`, plus uncommitted changes."""
    paths = set(_git(repo, 'diff', '--no-renames', '--name-only', f'{base}...HEAD'))
    paths.update(_git(repo, 'diff', '--no-renames', '--name-only', 'HEAD'))
    paths.update(_git(repo, 'ls-files', '--others', '--exclude-standard'))
    return sorted(paths)


def _examples(paths: list[str], limit: int = 3) -> str:
    shown = ', '.join(paths[:limit])
    return shown + (f' (+{len(paths) - limit} more)' if len(paths) > limit else '')


def decide(book_root: str, changed: list[str], all_books: bool = False) -> tuple[bool, str]:
    """(render?, reason) for one publication book, given its root and the changed paths."""
    if all_books:
        return True, '--all-books'
    shared = [path for path in changed
              if path.startswith(SHARED_DIRS) or path in SHARED_FILES]
    if shared:
        return True, f'shared input changed: {_examples(shared)}'
    prefix = book_root.rstrip('/') + '/'
    own = [path for path in changed if path.startswith(prefix)]
    if own:
        return True, f'book changed: {_examples(own)}'
    return False, (f'no change under {prefix}, tools/, scripts/, books.yaml, '
                   f'pyproject.toml or uv.lock '
                   f'since {BASE} (run ci-local.sh --all-books to render it)')


def decide_site(roots: list[str], changed: list[str], all_books: bool = False) -> tuple[bool, str]:
    """(render?, reason) for the learning-website build, given the site books' roots."""
    if all_books:
        return True, '--all-books'
    shared = [path for path in changed if path.startswith(SITE_DIRS) or path in SITE_FILES]
    if shared:
        return True, f'site input changed: {_examples(shared)}'
    prefixes = tuple(root.rstrip('/') + '/' for root in roots)
    own = [path for path in changed if prefixes and path.startswith(prefixes)]
    if own:
        return True, f'site book changed: {_examples(own)}'
    books = ', '.join(prefixes) or 'none'
    return False, ('no change under site/, runner/, tools/, scripts/, books.yaml, .nvmrc, pyproject.toml, '
                   f'uv.lock or a site book ({books}) since {BASE}')


def _catalog(repo: Path) -> list[dict]:
    return yaml.safe_load((repo / 'books.yaml').read_text(encoding='utf-8'))['books']


def site_roots(repo: Path) -> list[str]:
    """The roots of the books flagged `site: true`, in registry order."""
    return [entry.get('root', entry['id']) for entry in _catalog(repo) if entry.get('site') is True]


def site_scope(repo: Path, all_books: bool = False) -> tuple[bool, str]:
    roots = site_roots(repo)
    if all_books:
        return decide_site(roots, [], all_books=True)
    try:
        changed = changed_files(repo)
    except ScopeError as error:
        return True, f'cannot compute the change set ({error}); rendering to be safe'
    return decide_site(roots, changed)


def book_root(repo: Path, book: str) -> str:
    for entry in _catalog(repo):
        if entry['id'] == book:
            return entry.get('root', book)
    raise ValueError(f'unknown book: {book}')


def scope(repo: Path, book: str, all_books: bool = False) -> tuple[bool, str]:
    root = book_root(repo, book)
    if all_books:
        return decide(root, [], all_books=True)
    try:
        changed = changed_files(repo)
    except ScopeError as error:
        return True, f'cannot compute the change set ({error}); rendering to be safe'
    return decide(root, changed)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog='python -m tools.ci_scope',
                                     description='Decide whether ci-local renders a book or the site.')
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument('--book', help="a publication book's editions")
    target.add_argument('--site', action='store_true', help='the learning-website build')
    parser.add_argument('--all-books', action='store_true')
    parser.add_argument('--repo', type=Path, default=Path('.'))
    args = parser.parse_args(argv)
    if args.site:
        render, reason = site_scope(args.repo, args.all_books)
    else:
        render, reason = scope(args.repo, args.book, args.all_books)
    print(f'{"render" if render else "skip"}: {reason}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
