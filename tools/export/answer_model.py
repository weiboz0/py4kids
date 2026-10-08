"""The answer-model checks over a written bundle (design 012 D5; plan 101 Phase F).

`answer_model_findings(root, book, bundle_dir)` reads a bundle exactly as the site would (its
`book.json`, `entries/*.json` and copied `files/**`) and checks it against the hidden material that
`tools/export/answers.py` hands out as data (it never reads a solution itself):

1. **Leak, code.** The hidden code corpus is every code cell of every `solutions.ipynb` plus every
   hidden solution file (`solution_asset_files`: even and challenge solution assets, `exN/qN/pN.py`,
   `assets/verify/**`), minus what the Student Book releases as odd answers. Only the exact assert
   statements some item ships as `asserts.source` (compared by `ast.unparse`) are cut from it first.
   Each remaining stream is **counted**, never dropped: its occurrences (non-overlapping, as
   `solution_leak` matches it: the whole block, or a run inside it for a stream of 30+ tokens)
   across the JSON strings (with every code fence inside one) and copied files may not exceed its
   occurrences across the baseline sources (a trace exercise's solution is often its statement's
   own program, so a visible stream is allowed exactly as many copies as the exported sources
   hold). Every `asserts.source` must parse to top-level `assert` statements only.
2. **Leak, text.** Every hidden canonical text (`canonical_texts`), of any length, is counted as a
   whole token sequence in every counted string (`counted`: every field no tie check holds) and in
   the copied files; the count may not exceed its count in the baseline: the source text of exactly
   the material the bundle maps (`AnswerModel.baseline`; of the concept registry, only the exported
   projection's `name` fields).
3. **Odd answers.** Every `after-attempt` item's `answer_md` equals `student_answer_text`, and the
   `after-attempt` keys are exactly the odd unit exercises of the statement notebooks.
4. **Hashes.** Every `answer`, `predict` and `expected-output` item's `check.hash` equals
   `answer_hash(key, canonical, case=..., whitespace=..., aliases=...)` under its shipped
   `answer_format` (`answers.format_hash`; plan 102 Phase 0 adds `whitespace` and `aliases`).
5. **Visibility.** No `none` item carries `answer_md`.
6. **Leak, prose.** Every hidden solution Markdown paragraph (`fenced_paragraphs`) of at least 40
   characters (whitespace-normalised), or holding its item's canonical text, is counted like check 2
   over every bundle string and copied file against the same baseline.

Every string field check 2 does not count is held by a named tie check (`TIES`, `tie_of`): keys
name cells of mapped notebooks, ids are the syllabus's, paths name copied files, enums and hashes
validate against the schema, titles and labels are the sources' headings, tags are their cell's,
turtle figure segments equal the replay of the block's own code (an odd answer's `answer_figures`, captions
included, equal the replay of its released answer programs), `concepts` is the registry's
exported projection, divisions and `settings` are the book's config, and `pdfs` are the release's
links. A `fixtures` item's `check.cpu_ms` (a number, so never counted) is tied to the committed
timing cache (`tools/export/timings/<book>.json`): it equals the item's entry, whose fingerprint is
the current solver's and fixtures'. Fields that repeat another field by design are also skipped by check 1: a concept card's
`definition_md` and `term` must equal its glossary record's and its `distractors` must be glossary
terms, a predict item's `check.program` must be the item's own starter or statement code, and an
asserts item's `check.functions` must be names its asserts call.
"""

from __future__ import annotations

import ast
import json
import re
import tokenize
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

import nbformat

from tools.books import book_flag, book_path, book_subtitle, book_title, publication_config
from tools.publish import (
    code_tokens,
    entries,
    item_groups,
    read_source,
    student_answer_sources,
    student_answer_text,
)
from tools.publish_audit import solution_leak
from tools.turtle_figure import turtle_segments

from . import answers
from .bundle import UNRELEASED, _settings, dumps, pdf_links, schema_findings
from .concepts import Registry, book_registry
from .lesson import ROUTE_TYPES
from .timing import CACHE_DIR, TimingCache

# Every string field of the bundle is either counted by check 2 or held by a named tie check (plan 101
# content review 2, [sol] 3): no string field is silently left out. The counted fields are the
# content a student reads; an unknown field is counted too (`counted` is `tie_of(...) is None`).
COUNTED_FIELDS = frozenset({
    "md", "code", "output", "sample_input", "statement_md", "starter", "answer_md", "requirements",
    "hint", "source", "name", "definition_md", "term", "reference_md", "also_check", "aliases",
})
# The named tie checks (`AnswerModel._tie_findings`): each holds its fields to the repo sources or to
# a counted field, so a value cannot carry text the sources do not. Keys, ids, paths, enums, titles
# and labels are never matched by check 2 (plan 101 Phase F: "never in keys, labels or titles").
TIES = {
    "schema": "the bundle validates against the schema (enums, consts and sha256 patterns)",
    "keys": "a key is a cell id of a statement or lesson notebook the entry maps (plus its part, "
            "`asset:` or `predict` suffix), or a glossary card key of a registered concept",
    "ids": "book, entry and entry-file ids are the book's and its syllabus entries'",
    "paths": "a bundle path names a copied file whose repo source exists",
    "release": "the release tag is `unreleased` or `pdfs-<date>` and `pdfs` are its links",
    "settings": "`settings` is the book's publication and ACSL season config",
    "routes": "a lesson block's route is a `route_code` route of the block's type",
    "figures": "a turtle figure equals the replay of the block's own (counted) code; an odd "
               "answer's figures (segments and captions) equal the replay of its released answer "
               "programs",
    "tags": "a block's tags are tags of its source cell",
    "registry": "`concepts` is the registry's exported projection; concept references are its ids",
    "divisions": "an item's divisions are the season ladder's",
    "titles": "titles are the book's, the entry notebook's H1 and the item's own heading text; "
              "labels are `<Exercise|Question|...> <number>`",
    "predict program": "a predict item's program is its own starter or statement code",
    "assert functions": "assert function names are called by the item's counted asserts",
    "glossary cards": "a concept card's term and definition are its glossary record's and its "
                      "distractors are glossary terms",
    "timings": "a fixtures item's cpu_ms is its current entry in the committed timing cache",
}
FIELD_TIES = {
    "key": "keys", "block": "keys", "prelude": "keys",
    "id": "ids", "file": "ids",
    "files": "paths", "in_file": "paths", "out_file": "paths",
    "hash": "schema", "schema_version": "schema", "kind": "schema", "type": "schema",
    "probe": "schema", "match": "schema", "case": "schema", "whitespace": "schema",
    "answer_visibility": "schema",
    "mode": "schema",
    "tag": "release", "content_hash": "schema",
    "lesson_heading": "settings", "acsl_divisions": "settings",
    "route": "routes", "color": "figures", "caption": "figures", "tags": "tags",
    "concept": "registry", "concepts": "registry", "category": "registry",
    "division": "divisions",
    "title": "titles", "subtitle": "titles", "label": "titles",
    "program": "predict program", "functions": "assert functions", "distractors": "glossary cards",
}
TREE_TIES = {"release": "release", "pdfs": "release", "settings": "settings"}  # book.json config
CARD_TIED = frozenset({"definition_md", "term"})  # a concept card repeats its glossary record
# Fields that repeat another bundle field by design: check 1 skips them, the tie holds them.
REPEATS = frozenset({"predict program", "assert functions", "glossary cards"})
HASHED_KINDS = ("answer", "predict", "expected-output")
STEM = {"unit": "exercises", "checkpoint": "checkpoint", "project": "brief"}
STEMS = frozenset({"lesson", *STEM.values()})
ENTRY_DIR = {"unit": "units", "checkpoint": "checkpoints", "project": "projects"}
LABEL = re.compile(r"^(Exercise|Question|Challenge|Problem|Milestone) (\d+)$")
RELEASE_TAG = re.compile(r"^pdfs-\d{4}-\d{2}-\d{2}$")
PROSE_MIN = 40
LONG_STREAM = 30  # `solution_leak` embeds only streams this long
NGRAM = 8
FENCE = re.compile(r"^[ \t]*(```|~~~)[^\n]*\n(.*?)^[ \t]*\1[ \t]*$", re.MULTILINE | re.DOTALL)
WORD = re.compile(r"\w+|[^\w\s]")
FIXTURE = re.compile(r"^fixtures/([^/]+)/(\d+\.(?:in|out))$")
SEPARATOR = "\0"


# --- reading a bundle ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BundleString:
    where: str  # `<bundle file>:<json pointer>`
    owner: str  # the nearest enclosing `key`, else the bundle file
    field: str
    value: str


@dataclass
class Bundle:
    path: Path
    documents: dict[str, object]  # `book.json`, `entries/<id>.json`
    files: dict[str, str | None]  # `files/...` -> text (None when not UTF-8)
    strings: list[BundleString] = field(default_factory=list)


def _pointer(string: BundleString) -> list[str]:
    return string.where.split(":", 1)[1].split("/")


def tie_of(string: BundleString) -> str | None:
    """The named tie check (`TIES`) that holds this string, or None when check 2 counts it."""
    pointer = _pointer(string)
    if string.field in ("hash", "content_hash"):
        return "schema"  # a sha256 pattern holds no text
    if pointer[0] in TREE_TIES:
        return TREE_TIES[pointer[0]]
    if pointer[0] == "cards" and string.field in CARD_TIED:
        return "glossary cards"
    if string.where.startswith("book.json:concepts/") and string.field in ("id", "category"):
        return "registry"
    return FIELD_TIES.get(string.field)


def tied(string: BundleString) -> bool:
    """A field that repeats another bundle field by design (check 1 skips it; a tie holds it)."""
    return tie_of(string) in REPEATS


def counted(string: BundleString) -> bool:
    """Whether check 2 counts this string: every field no tie check holds."""
    return tie_of(string) is None


def _walk(value, where: str, pointer: list[str], owner: str, out: list[BundleString]) -> None:
    if isinstance(value, dict) and pointer and pointer[-1] == "aliases":
        # An `answer_format.aliases` map: both its typed keys and its canonical values are text a
        # student sees, so each is a counted string named `aliases` (plan 102 Phase 0).
        for name in sorted(value):
            for part, text in (("key", name), ("value", value[name])):
                if isinstance(text, str):
                    out.append(BundleString(f"{where}:{'/'.join([*pointer, name, part])}", owner,
                                            "aliases", text))
        return
    if isinstance(value, dict):
        if isinstance(value.get("key"), str):
            owner = value["key"]
        for name in sorted(value):
            _walk(value[name], where, [*pointer, name], owner, out)
    elif isinstance(value, list):
        for index, element in enumerate(value):
            _walk(element, where, [*pointer, str(index)], owner, out)
    elif isinstance(value, str):
        name = next((part for part in reversed(pointer) if not part.isdigit()), "")
        out.append(BundleString(f"{where}:{'/'.join(pointer)}", owner, name, value))


def load_bundle(bundle_dir: Path) -> Bundle:
    """The bundle's JSON documents, copied files and every string value with its location."""
    bundle_dir = Path(bundle_dir)
    documents: dict[str, object] = {"book.json": json.loads(
        (bundle_dir / "book.json").read_text(encoding="utf-8"))}
    for path in sorted((bundle_dir / "entries").glob("*.json")):
        documents[f"entries/{path.name}"] = json.loads(path.read_text(encoding="utf-8"))
    files: dict[str, str | None] = {}
    for path in sorted((bundle_dir / "files").rglob("*")):
        if path.is_file():
            try:
                files[path.relative_to(bundle_dir).as_posix()] = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                files[path.relative_to(bundle_dir).as_posix()] = None
    bundle = Bundle(bundle_dir, documents, files)
    for name, document in documents.items():
        _walk(document, name, [], name, bundle.strings)
    return bundle


def _entry_docs(bundle: Bundle) -> list[tuple[dict, dict]]:
    """(book.json entry record, entry document) in syllabus order."""
    book = bundle.documents["book.json"]
    return [(record, bundle.documents[record["file"]]) for record in book["entries"]
            if record["file"] in bundle.documents]


def _items(bundle: Bundle):
    for record, document in _entry_docs(bundle):
        for index, item in enumerate(document["items"]):
            yield record, index, item


# --- token helpers ------------------------------------------------------------------------------


def _tokens(source: str) -> tuple:
    try:
        return code_tokens(source)
    except (tokenize.TokenError, SyntaxError, ValueError):
        return ()


class _StreamIndex:
    """`solution_leak(block, [stream])` for many hidden streams at once (exact, or embedded when long)."""

    def __init__(self, streams: list[tuple]):
        self.streams = streams
        self.exact: dict[tuple, list[int]] = defaultdict(list)
        self.prefix: dict[tuple, list[int]] = defaultdict(list)
        for index, stream in enumerate(streams):
            if not stream:
                continue
            self.exact[stream].append(index)
            if len(stream) >= LONG_STREAM:
                self.prefix[stream[:NGRAM]].append(index)

    def hits(self, block: tuple) -> list[int]:
        found = set(self.exact.get(block, ()))
        if len(block) >= LONG_STREAM and self.prefix:
            for start in range(len(block) - NGRAM + 1):
                found.update(self.prefix.get(block[start:start + NGRAM], ()))
        return sorted(i for i in found if solution_leak(block, [self.streams[i]]))

    def occurrences(self, block: tuple) -> dict[int, int]:
        """Hidden stream -> its non-overlapping occurrences in `block` (1 for an exact match)."""
        return {i: _occurrences(block, self.streams[i]) for i in self.hits(block)}

    def text_occurrences(self, text: str) -> Counter:
        """Occurrences in a text: the larger of its whole-text stream's count and its code fences'
        summed counts, so a fence inside a tokenisable text is not counted twice."""
        whole, fences = _tokens(text), []
        if "```" in text or "~~~" in text:
            fences = [_tokens(match[2]) for match in FENCE.finditer(text)]
        out: Counter = Counter(self.occurrences(whole) if whole else {})
        fenced: Counter = Counter()
        for block in fences:
            if block:
                fenced.update(self.occurrences(block))
        for i, n in fenced.items():
            out[i] = max(out[i], n)
        return out


def _occurrences(block: tuple, stream: tuple) -> int:
    """Non-overlapping occurrences of `stream` in `block`, as `solution_leak` matches it: the whole
    block, or (for a stream of at least `LONG_STREAM` tokens) a contiguous run inside it."""
    if block == stream:
        return 1
    if len(stream) < LONG_STREAM:
        return 0
    count, start, size = 0, 0, len(stream)
    while start <= len(block) - size:
        if block[start:start + size] == stream:
            count += 1
            start += size
        else:
            start += 1
    return count


class _TokenCounter:
    """Whole-token-sequence counts over a list of texts (texts never join into one match)."""

    def __init__(self, texts: list[str]):
        self.words: list[str] = []
        for text in texts:
            self.words += WORD.findall(text)
            self.words.append(SEPARATOR)
        self._index: dict[bool, dict[str, list[int]]] = {}

    def _positions(self, folded: bool) -> dict[str, list[int]]:
        if folded not in self._index:
            index: dict[str, list[int]] = defaultdict(list)
            for position, word in enumerate(self.words):
                index[word.casefold() if folded else word].append(position)
            self._index[folded] = index
        return self._index[folded]

    def count(self, needle: list[str], folded: bool) -> int:
        if not needle:
            return 0
        index = self._positions(folded)
        if folded:
            needle = [word.casefold() for word in needle]
        words = self.words
        total = 0
        for start in index.get(needle[0], ()):
            end = start + len(needle)
            if end <= len(words) and all(
                    (words[start + i].casefold() if folded else words[start + i]) == needle[i]
                    for i in range(1, len(needle))):
                total += 1
        return total


def _canonical_words(canonical: str) -> list[str]:
    return WORD.findall(canonical)


def _contains_canonical(text: str, canonical: str, case: str) -> bool:
    words = _canonical_words(canonical)
    return bool(words) and _TokenCounter([text]).count(words, case == "insensitive") > 0


def _squash(text: str) -> str:
    return " ".join(text.split())


# --- the model ----------------------------------------------------------------------------------


def _file_source(entry_dir: Path, bundle_path: str) -> Path | None:
    """The repo source of a copied file `files/<entry>/<relative>` (fixtures from their asset pair)."""
    parts = bundle_path.split("/", 2)
    if len(parts) != 3 or parts[0] != "files" or parts[1] != entry_dir.name:
        return None
    fixture = FIXTURE.match(parts[2])
    return entry_dir / "assets" / fixture[1] / fixture[2] if fixture else entry_dir / parts[2]


@dataclass(frozen=True)
class Source:
    """One piece of student-visible source text the bundle maps (`origin`: repo path[#part])."""

    origin: str
    text: str


class AnswerModel:
    """The hidden corpora of one book (read once) and the checks over any bundle of it."""

    def __init__(self, root: Path, book: str):
        self.root, self.book = Path(root), book
        self.base = book_path(self.root, book)
        self.entry_dirs = dict(entries(self.base, "student"))
        self.lesson_heading = (publication_config(self.root, book).lesson_heading
                               if book_flag(self.root, book, "publication") else None)
        self.stats: dict[str, int] = {}
        self._read_cache: dict[Path, str] = {}
        self._cells_cache: dict[tuple[str, str], list | None] = {}

    counted = staticmethod(counted)

    @cached_property
    def registry(self) -> Registry:
        """The concept registry as the export projects it (`{id, name, category}` per concept)."""
        return book_registry(self.root, self.book)

    # -- hidden material (answers.py, as data) --

    @cached_property
    def shipped(self) -> dict[str, str]:
        return answers.shipped_asserts(self.root, self.book)

    @cached_property
    def removed_asserts(self) -> set[str]:
        """`ast.unparse` of every assert statement some item ships as `asserts.source`."""
        out: set[str] = set()
        for source in self.shipped.values():
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue
            out |= {ast.unparse(node) for node in tree.body if isinstance(node, ast.Assert)}
        return out

    def _strip_shipped(self, text: str) -> str:
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return text
        drop: set[int] = set()
        for node in tree.body:
            if isinstance(node, ast.Assert) and ast.unparse(node) in self.removed_asserts:
                drop.update(range(node.lineno - 1, node.end_lineno))
        if not drop:
            return text
        return "".join(line for number, line in enumerate(text.splitlines(keepends=True))
                       if number not in drop)

    @cached_property
    def hidden_code(self) -> list[answers.HiddenSource]:
        """Unreleased solution code cells and solution files."""
        cells = answers.solution_code_cells(self.root, self.book)
        files = answers.solution_asset_files(self.root, self.book)
        return [source for source in [*cells, *files] if not source.released]

    @cached_property
    def _hidden_streams(self) -> list[tuple[answers.HiddenSource, tuple]]:
        out = []
        for source in self.hidden_code:
            stream = _tokens(self._strip_shipped(source.text))
            if stream:
                out.append((source, stream))
        return out

    @cached_property
    def hidden_prose(self) -> list[answers.HiddenSource]:
        """Unreleased solution Markdown paragraphs."""
        return [p for p in answers.solution_markdown_paragraphs(self.root, self.book)
                if not p.released and p.text.strip()]

    @cached_property
    def canonicals(self) -> dict[str, tuple[str, str, str]]:
        return answers.canonical_texts(self.root, self.book)

    @cached_property
    def check_texts(self) -> list[tuple[str, str, str]]:
        return answers.check_texts(self.root, self.book)

    # -- the baseline: source text of exactly what the bundle maps --

    def _read(self, path: Path) -> str:
        if path not in self._read_cache:
            self._read_cache[path] = read_source(path, "student")
        return self._read_cache[path]

    def _rel(self, path: Path) -> str:
        return path.resolve().relative_to(self.root.resolve()).as_posix()

    def _notebook_sources(self, path: Path, output_keys: set[str] | None, key_prefix: str
                          ) -> list[Source]:
        notebook = nbformat.reads(self._read(path), as_version=4)
        rel = self._rel(path)
        out = []
        for cell in notebook.cells:
            out.append(Source(f"{rel}#{cell.get('id')}", cell.source))
            if isinstance(cell.metadata.get("sample_input"), str):
                out.append(Source(f"{rel}#{cell.get('id')}:sample_input",
                                  cell.metadata["sample_input"]))
            if output_keys is None or f"{key_prefix}{cell.get('id')}" not in output_keys:
                continue
            for output in cell.get("outputs", []):
                text = output.get("text") or output.get("data", {}).get("text/plain", "")
                if text:
                    out.append(Source(f"{rel}#{cell.get('id')}:output", "".join(text)))
        return out

    def baseline(self, bundle: Bundle) -> list[Source]:
        """The student-visible source text of exactly the material `bundle` maps: its entries'
        lesson and statement notebooks (lesson outputs where a block ships one, and a cell's
        `sample_input`), each lesson asset listing, the source of every copied file (fixtures
        included), the glossary, the quick reference and the concept registry when exported, the
        check text each item ships (`answers.check_texts`: requirements, answer-format hints, the
        asserts of `asserts` items) and `student_answer_text` of every `after-attempt` item."""
        book = bundle.documents["book.json"]
        out: list[Source] = []
        back = self.base / "back-matter"
        if book.get("glossary") and (back / "glossary.md").is_file():
            out.append(Source(self._rel(back / "glossary.md"), self._read(back / "glossary.md")))
        if book.get("reference_md") and (back / "quick-reference.md").is_file():
            out.append(Source(self._rel(back / "quick-reference.md"),
                              self._read(back / "quick-reference.md")))
        if book.get("concepts"):
            # Only the exported projection of the registry earns allowance, field by field: its
            # counted field `name` (ids and categories are tied to the projection, not counted).
            # A comment or an unexported field of `concepts.yaml` never ships, so it earns nothing.
            registry = self._rel(self.base / "curriculum" / "concepts.yaml")
            out += [Source(f"{registry}#concept:{concept['id']}/name", concept["name"])
                    for concept in self.registry.concepts]
        item_keys = {item["key"] for _record, _index, item in _items(bundle)}
        out += [Source(origin, text) for key, origin, text in self.check_texts if key in item_keys]
        for record, document in _entry_docs(bundle):
            entry_dir = self.entry_dirs.get(record["id"])
            if entry_dir is None:
                continue
            prefix = f"{self.book}/{record['id']}/"
            if document["lesson"]:
                blocks = document["lesson"]["blocks"]
                with_output = {block["key"] for block in blocks if "output" in block}
                out += self._notebook_sources(entry_dir / "lesson.ipynb", with_output,
                                              prefix + "lesson/")
                for block in blocks:
                    _, _, part = block["key"].partition("#")
                    if part.startswith("asset:"):
                        asset = entry_dir / "assets" / part.removeprefix("asset:")
                        out.append(Source(f"{self._rel(asset)}#listing", self._read(asset)))
            statement = entry_dir / f"{STEM.get(record['kind'], '-')}.ipynb"
            if (document["items"] or document["intro"] or document["outro"]) and statement.is_file():
                out += self._notebook_sources(statement, None, "")
            for path in document["files"]:
                source = _file_source(entry_dir, path)
                if source is None:
                    continue
                try:
                    text = source.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue
                out.append(Source(self._rel(source), text))
            released = [item for item in document["items"]
                        if item.get("answer_visibility") == "after-attempt"
                        and item["kind"] == "unit" and isinstance(item.get("number"), int)]
            if released:
                sources = student_answer_sources(entry_dir)
                solutions = self._rel(entry_dir / "solutions.ipynb")
                for item in released:
                    try:
                        text = student_answer_text(entry_dir, item["number"], self.lesson_heading,
                                                   sources=sources)
                    except ValueError:
                        continue
                    out.append(Source(f"{solutions}#answer:{item['key']}", text))
        return out

    # -- the checks --

    def _content_texts(self, bundle: Bundle) -> list[tuple[str, str]]:
        texts = [(s.where, s.value) for s in bundle.strings if counted(s)]
        texts += [(path, text) for path, text in bundle.files.items() if text is not None]
        return texts

    def canonical_counts(self, bundle: Bundle, baseline: list[Source] | None = None
                         ) -> list[tuple[str, int, int]]:
        """(item key, bundle count, baseline count) per hidden canonical text (check 2)."""
        baseline = self.baseline(bundle) if baseline is None else baseline
        shipped = _TokenCounter([text for _, text in self._content_texts(bundle)])
        allowed = _TokenCounter([source.text for source in baseline])
        out = []
        for key, (_kind, canonical, case) in sorted(self.canonicals.items()):
            words = _canonical_words(canonical)
            if not words:
                continue
            folded = case == "insensitive"
            out.append((key, shipped.count(words, folded), allowed.count(words, folded)))
        return out

    def findings(self, bundle_dir: Path) -> list[str]:
        """Checks 1-6 and the tie checks. A check that cannot read a malformed bundle (a field the
        schema requires is missing or retyped) gives a `FAIL:` instead of crashing."""
        bundle = load_bundle(bundle_dir)
        findings: list[str] = []

        def run(name: str, check, *args) -> list[str]:
            try:
                return check(*args)
            except (KeyError, IndexError, TypeError, ValueError, AttributeError) as error:
                return [(f"FAIL: {self.book}: {name} could not read the bundle "
                         f"({type(error).__name__}: {error})")]

        baseline: list[Source] = []
        problem = run("the baseline", lambda: baseline.extend(self.baseline(bundle)) or [])
        findings += problem
        findings += run("check 1", self._asserts_findings, bundle)
        if not problem:
            findings += run("check 1", self._code_findings, bundle, baseline)
            findings += run("check 2", self._text_findings, bundle, baseline)
        findings += run("check 3", self._odd_findings, bundle)
        findings += run("check 4", self._hash_findings, bundle)
        findings += run("check 5", self._visibility_findings, bundle)
        if not problem:
            findings += run("check 6", self._prose_findings, bundle, baseline)
        findings += run("the tie checks", self._tie_findings, bundle)
        return findings

    def _asserts_findings(self, bundle: Bundle) -> list[str]:
        out = []
        for _record, _index, item in _items(bundle):
            check = item["check"]
            if check.get("kind") != "asserts":
                continue
            try:
                tree = ast.parse(check.get("source", ""))
            except SyntaxError:
                tree = None
            if tree is None or not all(isinstance(node, ast.Assert) for node in tree.body):
                out.append(f"FAIL: {item['key']}: asserts.source holds non-assert code")
        return out

    def _code_findings(self, bundle: Bundle, baseline: list[Source]) -> list[str]:
        """Each hidden stream is counted, never dropped: its occurrences (`_occurrences`, as
        `solution_leak` matches it) across the bundle strings and copied files may not outnumber its
        occurrences across the exported sources."""
        streams = self._hidden_streams
        index = _StreamIndex([stream for _, stream in streams])
        allowed: Counter = Counter()
        for source in baseline:
            allowed.update(index.text_occurrences(source.text))
        by_value: dict[str, list[BundleString]] = defaultdict(list)
        for string in bundle.strings:
            if not tied(string):
                by_value[string.value].append(string)
        located = [(value, [(s.owner, s.where) for s in strings])
                   for value, strings in by_value.items()]
        located += [(text, [(path, path)]) for path, text in bundle.files.items() if text is not None]
        places: dict[int, list[tuple[str, str]]] = defaultdict(list)
        shipped: Counter = Counter()
        for value, where in located:
            for i, n in index.text_occurrences(value).items():
                places[i] += where
                shipped[i] += n * len(where)
        self.stats.update(hidden_code=len(streams), hidden_code_visible=len(allowed))
        out: list[str] = []
        for i in sorted(places):
            if shipped[i] <= allowed[i]:
                continue
            origin = streams[i][0].origin
            for owner, where in places[i]:
                out.append(f"FAIL: {self.book}: {owner}: solution code leaked into {where} "
                           f"({shipped[i]} occurrence(s), {allowed[i]} in exported sources) "
                           f"(from {origin})")
        return out

    def _text_findings(self, bundle: Bundle, baseline: list[Source]) -> list[str]:
        counts = self.canonical_counts(bundle, baseline)
        self.stats["canonicals"] = len(counts)
        out = []
        for key, shipped, allowed in counts:
            if shipped > allowed:
                _kind, canonical, case = self.canonicals[key]
                where = [place for place, text in self._content_texts(bundle)
                         if _contains_canonical(text, canonical, case)][:3]
                out.append(f"FAIL: {self.book}: {key}: hidden answer text leaked into the bundle "
                           f"({shipped} occurrence(s), {allowed} in exported sources; "
                           f"in {', '.join(where)})")
        return out

    def _odd_keys(self) -> set[str]:
        """Keys of the odd unit exercises, read from the statement notebooks."""
        keys = set()
        for entry_id, entry_dir in self.entry_dirs.items():
            path = entry_dir / "exercises.ipynb"
            if not entry_id.startswith("unit-") or not path.is_file():
                continue
            cells = nbformat.reads(self._read(path), as_version=4).cells
            for group in item_groups(cells, "Exercise")[1]:
                if group["number"] % 2:
                    keys.add(f"{self.book}/{entry_id}/exercises/{group['cells'][0].get('id')}")
        return keys

    def _odd_findings(self, bundle: Bundle) -> list[str]:
        out = []
        odd = self._odd_keys()
        seen = set()
        outside = set()
        for record, _index, item in _items(bundle):
            if record["id"] not in self.entry_dirs:
                if record["id"] not in outside:
                    outside.add(record["id"])
                    out.append(f"FAIL: {self.book}: {record['id']}: entry is not in the syllabus")
                continue
            key = item["key"]
            seen.add(key)
            if item.get("answer_visibility") != "after-attempt":
                if key in odd:
                    out.append(f"FAIL: {key}: odd unit exercise is not after-attempt")
                continue
            if key not in odd or item["kind"] != "unit":
                out.append(f"FAIL: {key}: after-attempt but not an odd unit exercise")
                continue
            entry_dir = self.entry_dirs[record["id"]]
            try:
                expected = student_answer_text(entry_dir, item["number"], self.lesson_heading)
            except ValueError:
                expected = None
            if item.get("answer_md") != expected:
                out.append(f"FAIL: {key}: answer_md differs from the Student Book appendix text "
                           f"(student_answer_text)")
        out += [f"FAIL: {key}: odd unit exercise missing from the bundle" for key in sorted(odd - seen)]
        return out

    def _hash_findings(self, bundle: Bundle) -> list[str]:
        out = []
        seen = set()
        for _record, _index, item in _items(bundle):
            check, key = item["check"], item["key"]
            if check.get("kind") not in HASHED_KINDS:
                continue
            seen.add(key)
            known = self.canonicals.get(key)
            if known is None or known[0] != check["kind"]:
                out.append(f"FAIL: {key}: {check['kind']} item without a matching canonical text")
                continue
            if check.get("hash") != answers.format_hash(key, known[1], check.get("answer_format", {})):
                out.append(f"FAIL: {key}: check.hash does not match its canonical answer")
        out += [f"FAIL: {key}: canonical text for an item the bundle does not hash"
                for key in sorted(set(self.canonicals) - seen)]
        return out

    def _visibility_findings(self, bundle: Bundle) -> list[str]:
        return [f"FAIL: {item['key']}: answer_visibility none but answer_md ships"
                for _record, _index, item in _items(bundle)
                if item.get("answer_visibility") == "none" and "answer_md" in item]

    def _prose_findings(self, bundle: Bundle, baseline: list[Source]) -> list[str]:
        labels = {(record["id"], item["label"]): item["key"] for record, _i, item in _items(bundle)}
        corpus: dict[str, answers.HiddenSource] = {}
        for paragraph in self.hidden_prose:
            text = _squash(paragraph.text)
            key = labels.get((paragraph.entry, paragraph.item or ""))
            canonical = self.canonicals.get(key) if key else None
            if len(text) >= PROSE_MIN or (canonical and _contains_canonical(
                    paragraph.text, canonical[1], canonical[2])):
                corpus.setdefault(text, paragraph)
        self.stats["hidden_prose"] = len(corpus)
        places = [(s.where, _squash(s.value)) for s in bundle.strings]
        places += [(path, _squash(text)) for path, text in bundle.files.items() if text is not None]
        shipped_text = SEPARATOR.join(text for _, text in places)
        allowed_text = SEPARATOR.join(_squash(source.text) for source in baseline)
        out = []
        for text, paragraph in corpus.items():
            shipped = shipped_text.count(text)
            if not shipped:
                continue
            allowed = allowed_text.count(text)
            if shipped > allowed:
                where = [place for place, value in places if text in value][:3]
                out.append(f"FAIL: {self.book}: {paragraph.origin}: solution prose leaked into "
                           f"{', '.join(where)} ({shipped} occurrence(s), {allowed} in exported "
                           f"sources)")
        return out

    # -- the tie checks: every string field check 2 does not count (`TIES`) --

    def _tie_findings(self, bundle: Bundle) -> list[str]:
        """Each named tie check (`TIES`) over the bundle; one that cannot read it gives a FAIL."""
        out: list[str] = []
        for name in TIES:
            try:
                out += getattr(self, "_tie_" + name.replace(" ", "_"))(bundle)
            except (KeyError, IndexError, TypeError, ValueError, AttributeError) as error:
                out.append(f"FAIL: {self.book}: tie check {name!r} could not read the bundle "
                           f"({type(error).__name__}: {error})")
        return out

    @staticmethod
    def _held(bundle: Bundle, tie: str) -> list[BundleString]:
        return [string for string in bundle.strings if tie_of(string) == tie]

    def _cells(self, entry_id: str, stem: str):
        """The cells of an entry's `stem` notebook, or None when there is no such notebook."""
        if (entry_id, stem) not in self._cells_cache:
            entry_dir = self.entry_dirs.get(entry_id)
            path = entry_dir / f"{stem}.ipynb" if entry_dir is not None else None
            self._cells_cache[entry_id, stem] = (
                nbformat.reads(self._read(path), as_version=4).cells
                if path is not None and stem in STEMS and path.is_file() else None)
        return self._cells_cache[entry_id, stem]

    def _key_cell(self, key: str):
        """(entry id, stem, cell index, cells, suffix parts) of a block or item key, or None when the
        key names no cell of a notebook the book maps."""
        parts = key.split("/") if isinstance(key, str) else []
        if len(parts) != 4 or parts[0] != self.book:
            return None
        entry_id, stem, rest = parts[1], parts[2], parts[3]
        cell_id, *suffix = rest.split("#")
        cells = self._cells(entry_id, stem)
        if cells is None:
            return None
        index = next((i for i, cell in enumerate(cells) if cell.get("id") == cell_id), None)
        return None if index is None else (entry_id, stem, index, cells, suffix)

    def _valid_key(self, key: str) -> bool:
        glossary = re.fullmatch(rf"{re.escape(self.book)}/back-matter/glossary/([^/#]+)", key or "")
        if glossary:
            return glossary[1] in self.registry.ids
        found = self._key_cell(key)
        if found is None:
            return False
        entry_id, _stem, _index, _cells, suffix = found
        for position, part in enumerate(suffix):
            if position == 0 and part.isdigit() and int(part) >= 1:
                continue
            if position == len(suffix) - 1 and part == "predict":
                continue
            name = part.removeprefix("asset:")
            if (position == 0 and part.startswith("asset:") and ".." not in name.split("/")
                    and (self.entry_dirs[entry_id] / "assets" / name).is_file()):
                continue
            return False
        return True

    def _tie_schema(self, bundle: Bundle) -> list[str]:
        out = schema_findings("book.json", bundle.documents["book.json"], "book_file")
        for name, document in bundle.documents.items():
            if name != "book.json":
                out += schema_findings(name, document, "entry_file")
        return out

    def _tie_keys(self, bundle: Bundle) -> list[str]:
        return [f"FAIL: {self.book}: {s.where}: key names no cell of a mapped notebook ({s.value})"
                for s in self._held(bundle, "keys") if not self._valid_key(s.value)]

    def _tie_ids(self, bundle: Bundle) -> list[str]:
        book = bundle.documents["book.json"]
        out = []
        for string in self._held(bundle, "ids"):
            document, _, pointer = string.where.partition(":")
            if pointer == "book/id":
                ok = string.value == self.book
            elif document == "book.json" and re.fullmatch(r"entries/\d+/file", pointer):
                record = book["entries"][int(pointer.split("/")[1])]
                ok = string.value == f"entries/{record['id']}.json"
            elif pointer == "entry/id":
                ok = document == f"entries/{string.value}.json" and string.value in self.entry_dirs
            else:
                ok = string.value in self.entry_dirs
            if not ok:
                out.append(f"FAIL: {self.book}: {string.where}: not the book's or a syllabus "
                           f"entry's id ({string.value})")
        return out

    def _tie_paths(self, bundle: Bundle) -> list[str]:
        out = []
        for string in self._held(bundle, "paths"):
            if string.value not in bundle.files:
                out.append(f"FAIL: {self.book}: {string.where}: names no copied file "
                           f"({string.value})")
        for path in bundle.files:
            entry_dir = self.entry_dirs.get(path.split("/")[1]) if path.count("/") >= 2 else None
            source = _file_source(entry_dir, path) if entry_dir is not None else None
            if source is None or not source.is_file():
                out.append(f"FAIL: {self.book}: {path}: copied file has no repo source")
        return out

    def _tie_release(self, bundle: Bundle) -> list[str]:
        book = bundle.documents["book.json"]
        release = book.get("release") or {}
        tag = release.get("tag")
        out = []
        if tag != UNRELEASED and not (isinstance(tag, str) and RELEASE_TAG.match(tag)):
            out.append(f"FAIL: {self.book}: book.json release.tag is not `{UNRELEASED}` or "
                       f"`pdfs-<date>` ({tag})")
        elif book.get("pdfs") != pdf_links(self.book, tag):
            out.append(f"FAIL: {self.book}: book.json pdfs are not the links of release {tag}")
        return out

    def _tie_settings(self, bundle: Bundle) -> list[str]:
        settings = bundle.documents["book.json"].get("settings")
        if settings != json.loads(dumps(_settings(self.root, self.book))):
            return [f"FAIL: {self.book}: book.json settings differ from the book's config"]
        return []

    def _blocks(self, bundle: Bundle):
        """Every block of the bundle (lesson, intro, `before`, outro) with its owning entry id."""
        for record, document in _entry_docs(bundle):
            for block in (document["lesson"] or {}).get("blocks", []):
                yield record["id"], block
            for block in [*document["intro"], *document["outro"]]:
                yield record["id"], block
            for item in document["items"]:
                for block in item["before"]:
                    yield record["id"], block

    def _tie_routes(self, bundle: Bundle) -> list[str]:
        return [f"FAIL: {block['key']}: route {block['route']} is not a route_code route of a "
                f"{block['type']} block"
                for _entry, block in self._blocks(bundle)
                if "route" in block and ROUTE_TYPES.get(block["route"]) != block["type"]]

    def _tie_figures(self, bundle: Bundle) -> list[str]:
        out = []
        for _entry, block in self._blocks(bundle):
            if "figure" not in block:
                continue
            stdin = None
            if block.get("route") == "tryit+figure" and isinstance(block.get("sample_input"), str):
                stdin = "\n".join(block["sample_input"].split(" | ")) + "\n"
            try:
                replay = json.loads(json.dumps(turtle_segments(block["code"], stdin=stdin)))
            except Exception as error:  # noqa: BLE001 - any replay failure is a mismatch
                replay = f"replay failed: {error}"
            if block["figure"] != replay:
                out.append(f"FAIL: {block['key']}: turtle figure differs from the replay of its "
                           f"code")
        for record, _index, item in _items(bundle):
            entry_dir = self.entry_dirs.get(record["id"])
            expected = []
            if (entry_dir is not None and item.get("answer_visibility") == "after-attempt"
                    and isinstance(item.get("number"), int)):
                try:
                    expected = json.loads(json.dumps(answers.answer_figures(entry_dir,
                                                                            item["number"])))
                except Exception as error:  # noqa: BLE001 - any replay failure is a mismatch
                    expected = f"replay failed: {error}"
            if item.get("answer_figures", []) != expected:
                out.append(f"FAIL: {item['key']}: answer_figures differ from the replay of its "
                           f"released answer programs")
        return out

    def _tie_timings(self, bundle: Bundle) -> list[str]:
        cache = TimingCache(self.root, self.book)
        out = []
        for record, _index, item in _items(bundle):
            check = item["check"]
            if check.get("kind") != "fixtures":
                continue
            entry_dir = self.entry_dirs.get(record["id"])
            stem = FIXTURE.match(check["cases"][0]["in_file"].split("/", 2)[2])[1]
            found = cache.entry(item["key"])
            fingerprint = (answers.item_fingerprint(entry_dir, stem)
                           if entry_dir is not None else None)
            if found is None or check.get("cpu_ms") != found.get("cpu_ms"):
                out.append(f"FAIL: {item['key']}: check.cpu_ms is not its entry in "
                           f"{CACHE_DIR}/{self.book}.json")
            elif fingerprint is None or found.get("fingerprint") != fingerprint:
                out.append(f"FAIL: {item['key']}: stale timing in {CACHE_DIR}/{self.book}.json")
        return out

    def _tie_tags(self, bundle: Bundle) -> list[str]:
        out = []
        for _entry, block in self._blocks(bundle):
            if not block.get("tags"):
                continue
            found = self._key_cell(block["key"])
            allowed = set(found[3][found[2]].metadata.get("tags", [])) if found else set()
            for tag in block["tags"]:
                if tag not in allowed:
                    out.append(f"FAIL: {block['key']}: tag {tag} is not a tag of its source cell")
        return out

    def _tie_registry(self, bundle: Bundle) -> list[str]:
        out = []
        projection = [dict(concept) for concept in self.registry.concepts]
        if bundle.documents["book.json"].get("concepts") != projection:
            out.append(f"FAIL: {self.book}: book.json concepts are not the registry's exported "
                       f"projection")
        out += [f"FAIL: {self.book}: {s.where}: not a registered concept id ({s.value})"
                for s in self._held(bundle, "registry")
                if not s.where.startswith("book.json:concepts/") and s.value not in self.registry.ids]
        return out

    def _tie_divisions(self, bundle: Bundle) -> list[str]:
        ladder = _settings(self.root, self.book).get("acsl_divisions", [])
        return [f"FAIL: {s.owner}: division {s.value} is not on the season ladder"
                for s in self._held(bundle, "divisions") if s.value not in ladder]

    def _entry_title(self, entry_id: str, kind: str, has_lesson: bool) -> str:
        cells = self._cells(entry_id, "lesson") if has_lesson else None
        if cells:
            return cells[0].source.splitlines()[0].removeprefix("# ")
        for cell in self._cells(entry_id, STEM.get(kind, "-")) or []:
            if cell.cell_type == "markdown" and cell.source.startswith("# "):
                return cell.source.splitlines()[0].removeprefix("# ").strip()
        return entry_id

    @cached_property
    def _exported_titles(self) -> dict[str, str]:
        """Every item's title as the exporter derives it from its heading (exact tie, content
        review 3): a title may not carry any other text, even text found in its own statement."""
        from .items import entry_content

        kinds = {"units": "unit", "checkpoints": "checkpoint", "projects": "project"}
        return {item.key: item.title for entry_dir in self.entry_dirs.values()
                for item in entry_content(self.root, self.book, entry_dir,
                                          kinds[entry_dir.parent.name]).items}

    def _tie_titles(self, bundle: Bundle) -> list[str]:
        book = bundle.documents["book.json"]
        out = []
        if book["book"]["title"] != book_title(self.root, self.book) or (
                book["book"]["subtitle"] != book_subtitle(self.root, self.book)):
            out.append(f"FAIL: {self.book}: book.json book title or subtitle is not books.yaml's")
        for record, document in _entry_docs(bundle):
            expected = self._entry_title(record["id"], record["kind"], bool(document["lesson"]))
            if record["title"] != expected or document["entry"]["title"] != expected:
                out.append(f"FAIL: {self.book}: {record['id']}: entry title is not the H1 of its "
                           f"notebook")
            for item in document["items"]:
                label = LABEL.match(item["label"])
                if not label or (isinstance(item.get("number"), int)
                                 and int(label[2]) != item["number"]):
                    out.append(f"FAIL: {item['key']}: label {item['label']} is not "
                               f"`<kind> <number>`")
                if item["title"] != self._exported_titles.get(item["key"]):
                    out.append(f"FAIL: {item['key']}: title is not the item's heading text")
        return out

    def _tie_predict_program(self, bundle: Bundle) -> list[str]:
        out = []
        for _record, _index, item in _items(bundle):
            check = item["check"]
            if check.get("kind") == "predict":
                program = _squash(check.get("program", ""))
                if program and program not in _squash(item["starter"]) and program not in _squash(
                        item["statement_md"]):
                    out.append(f"FAIL: {item['key']}: check.program is not the item's own code")
        return out

    def _tie_assert_functions(self, bundle: Bundle) -> list[str]:
        out = []
        for _record, _index, item in _items(bundle):
            check = item["check"]
            if check.get("kind") == "asserts":
                try:
                    called = {node.func.id for node in ast.walk(ast.parse(check.get("source", "")))
                              if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
                except SyntaxError:
                    called = set()
                if not set(check.get("functions", [])) <= called:
                    out.append(f"FAIL: {item['key']}: check.functions names a function the "
                               f"asserts do not call")
        return out

    def _tie_glossary_cards(self, bundle: Bundle) -> list[str]:
        out = []
        book = bundle.documents["book.json"]
        glossary = {record["concept"]: record["definition_md"] for record in book.get("glossary", [])}
        terms = {record["concept"]: record["term"] for record in book.get("glossary", [])}
        for _record, document in _entry_docs(bundle):
            for card in document["cards"]:
                if card.get("kind") != "concept":
                    continue
                if card.get("definition_md") != glossary.get(card.get("concept")):
                    out.append(f"FAIL: {card['key']}: concept card definition_md differs from "
                               f"the glossary")
                if card.get("term") != terms.get(card.get("concept")):
                    out.append(f"FAIL: {card['key']}: concept card term differs from the glossary")
                if not set(card.get("distractors", [])) <= set(terms.values()):
                    out.append(f"FAIL: {card['key']}: concept card distractor is not a glossary "
                               f"term")
        return out


def answer_model_findings(root: Path, book: str, bundle_dir: Path) -> list[str]:
    """Checks 1-6 of plan 101 Phase F over the bundle written in `bundle_dir`."""
    return AnswerModel(root, book).findings(bundle_dir)

