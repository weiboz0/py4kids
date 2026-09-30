"""Plan 097/099/100 regression contract: python-concepts', python-projects' and usaco-bronze's
generated Quarto projects equal their immutable pre-change baselines, except for files listed (with a
D2/D3 reason) in each
book's allowed-diffs list."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

import pytest
import yaml

from tools.publish import EDITIONS, build

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / 'tests' / 'data'
# Each regression-guarded book: python-concepts (plan 097), python-projects (plan 099, captured
# before plan 099's first tooling change) and usaco-bronze (plan 100, captured before plan 100's first
# tooling change).
BOOKS = ('python-concepts', 'python-projects', 'usaco-bronze')


def baseline_path(book: str) -> Path:
    return DATA / f'{book}-publish-baseline.json'


def allowed_path(book: str) -> Path:
    return DATA / f'{book}-publish-allowed-diffs.yaml'

# Environment-independent digests. A project's data files (`p7_words.txt`, `p11_in.txt`, ...) are not
# in the repository: its solutions write them when they execute, so a fresh clone or an exported tree
# has none. The publisher prints a `::: {.datafile}` panel (and records a `data:<name>` inventory
# entry) only for a data file that exists, so both are normalised away, in the baseline and in the
# current output alike, before hashing. Everything else is hashed byte for byte.
DATAFILE_PANEL = re.compile(r'\n\n::: \{\.datafile\}\n\*\*[\w.-]+\*\*\n\n```text\n.*?\n```\n:::(?=\n|$)',
                            re.DOTALL)


def normalised(path: Path) -> bytes:
    """A generated file's bytes without anything that depends on the project's data files."""
    text = path.read_text(encoding='utf-8')
    if path.suffix == '.qmd':
        return DATAFILE_PANEL.sub('', text).encode('utf-8')
    manifest = json.loads(text)
    for chapter in manifest['chapters']:
        chapter['inventory'] = [record for record in chapter['inventory']
                                if not record['id'].startswith('data:')]
    return (json.dumps(manifest, indent=2) + '\n').encode('utf-8')


def digest(project: Path) -> dict[str, str]:
    """SHA-256 of every generated .qmd and inventory.json of one edition's Quarto project, after
    `normalised` (the baseline records these normalised digests)."""
    return {path.name: hashlib.sha256(normalised(path)).hexdigest() for path in sorted(project.iterdir())
            if path.suffix == '.qmd' or path.name == 'inventory.json'}


def allowed_diffs(book: str) -> dict[tuple[str, str], str]:
    entries = yaml.safe_load(allowed_path(book).read_text(encoding='utf-8'))['allowed_diffs'] or []
    allowed = {}
    for entry in entries:
        assert set(entry) == {'edition', 'file', 'reason'}, entry
        assert entry['edition'] in EDITIONS, entry
        assert re.search(r'\bD[23]\b', entry['reason']), f'reason must name a design 010 D2/D3 rule: {entry}'
        allowed[(entry['edition'], entry['file'])] = entry['reason']
    return allowed


@pytest.mark.parametrize('book', BOOKS)
def test_baseline_covers_every_edition(book):
    baseline = json.loads(baseline_path(book).read_text(encoding='utf-8'))
    assert set(baseline['editions']) == set(EDITIONS)
    for edition, files in baseline['editions'].items():
        assert 'inventory.json' in files and any(name.endswith('.qmd') for name in files), edition


def test_normalisation_removes_only_data_file_panels_and_records(tmp_path):
    qmd = tmp_path / 'p.qmd'
    qmd.write_text('Use it.\n\n::: {.datafile}\n**p7_words.txt**\n\n```text\nfern\n\nmoss\n```\n:::\n\n'
                   '::: {.program}\nx\n:::\n', encoding='utf-8')
    assert normalised(qmd) == b'Use it.\n\n::: {.program}\nx\n:::\n'
    inventory = tmp_path / 'inventory.json'
    records = [{'id': 'c1', 'kind': 'starter'}, {'id': 'data:p7_words.txt', 'kind': 'asset listing'}]
    inventory.write_text(json.dumps({'chapters': [{'id': 'p', 'inventory': records}]}), encoding='utf-8')
    assert json.loads(normalised(inventory)) == {'chapters': [{'id': 'p', 'inventory': records[:1]}]}


@pytest.mark.parametrize(('book', 'data_files'), [(book, data_files) for book in BOOKS
                                                  for data_files in ('absent', 'present')])
def test_output_matches_the_baseline(tmp_path, book, data_files):
    # Build from a copy so the test never touches <book>/build (the rendered editions).
    shutil.copy(REPO / 'books.yaml', tmp_path / 'books.yaml')
    shutil.copytree(REPO / book, tmp_path / book, ignore=shutil.ignore_patterns('build'))
    # The result must not depend on whether the project's generated data files exist here.
    for project in (tmp_path / book / 'projects').glob('project-*'):
        for data in project.glob('p*_*.txt'):
            data.unlink()
        if data_files == 'present':
            (project / 'p7_words.txt').write_text('fern\nmoss\n', encoding='utf-8')
            (project / 'p11_in.txt').write_text('3\n1 2 3\n', encoding='utf-8')
    baseline = json.loads(baseline_path(book).read_text(encoding='utf-8'))['editions']
    differing = set()
    for edition in EDITIONS:
        current = digest(build(tmp_path, book, edition))
        expected = baseline[edition]
        differing |= {(edition, name) for name in set(current) | set(expected)
                      if current.get(name) != expected.get(name)}
    allowed = allowed_diffs(book)
    assert differing <= set(allowed), f'unlisted differences from the baseline: {sorted(differing - set(allowed))}'
    assert set(allowed) <= differing, f'stale allowed-diffs entries: {sorted(set(allowed) - differing)}'
