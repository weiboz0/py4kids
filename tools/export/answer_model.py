"""The answer-model checks over a written bundle (design 012 D5; plan 101 Phase F).

`answer_model_findings(root, book, bundle_dir)` reads a bundle exactly as the site would (its
`book.json`, `entries/*.json` and copied `files/**`) and checks it against the hidden material that
`tools/export/answers.py` hands out as data (it never reads a solution itself):

1. **Leak, code.** The hidden code corpus is every code cell of every `solutions.ipynb` plus every
   hidden solution file (`solution_asset_files`: even and challenge solution assets, `exN/qN/pN.py`,
   `assets/verify/**`), minus what the Student Book releases as odd answers. Only the exact assert
   statements some item ships as `asserts.source` (compared by `ast.unparse`) are cut from it first.
   A hidden stream that a student-visible source already contains (`solution_leak` over the
   baseline's code) is not hidden: a trace exercise's solution is often its statement's own program.
   `solution_leak` then runs against every JSON string (and every code fence inside one) and every
   copied file. Every `asserts.source` must parse to top-level `assert` statements only.
2. **Leak, text.** Every hidden canonical text (`canonical_texts`), of any length, is counted as a
   whole token sequence in the content fields (`CONTENT_FIELDS`) and copied files; the count may not
   exceed its count in the baseline: the source text of exactly the material the bundle maps
   (`AnswerModel.baseline`).
3. **Odd answers.** Every `after-attempt` item's `answer_md` equals `student_answer_text`, and the
   `after-attempt` keys are exactly the odd unit exercises of the statement notebooks.
4. **Hashes.** Every `answer`, `predict` and `expected-output` item's `check.hash` equals
   `answer_hash(key, canonical, case=answer_format.case)`.
5. **Visibility.** No `none` item carries `answer_md`.
6. **Leak, prose.** Every hidden solution Markdown paragraph (`fenced_paragraphs`) of at least 40
   characters (whitespace-normalised), or holding its item's canonical text, is counted like check 2
   over every bundle string and copied file against the same baseline.

Fields that repeat another field by design are not counted in check 2 but are tied to it instead:
a concept card's `definition_md` must equal its glossary record's, and a predict item's
`check.program` must be the item's own starter or statement code.
"""

from __future__ import annotations

import ast
import json
import re
import tokenize
from collections import defaultdict
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

import nbformat

from tools.books import book_flag, book_path, publication_config
from tools.publish import (
    code_tokens,
    entries,
    item_groups,
    read_source,
    student_answer_sources,
    student_answer_text,
)
from tools.publish_audit import solution_leak

from . import answers
from .normalise import answer_hash

CONTENT_FIELDS = frozenset({"md", "code", "output", "statement_md", "starter", "answer_md",
                            "definition_md", "reference_md"})
HASHED_KINDS = ("answer", "predict", "expected-output")
STEM = {"unit": "exercises", "checkpoint": "checkpoint", "project": "brief"}
ENTRY_DIR = {"unit": "units", "checkpoint": "checkpoints", "project": "projects"}
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


def _walk(value, where: str, pointer: list[str], owner: str, out: list[BundleString]) -> None:
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


def _code_blocks(text: str) -> list[tuple]:
    """The text as one token stream, plus each code fence inside it (Markdown)."""
    blocks = [_tokens(text)]
    if "```" in text or "~~~" in text:
        blocks += [_tokens(match[2]) for match in FENCE.finditer(text)]
    return [block for block in blocks if block]


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
            if output_keys is None or f"{key_prefix}{cell.get('id')}" not in output_keys:
                continue
            for output in cell.get("outputs", []):
                text = output.get("text") or output.get("data", {}).get("text/plain", "")
                if text:
                    out.append(Source(f"{rel}#{cell.get('id')}:output", "".join(text)))
        return out

    def baseline(self, bundle: Bundle) -> list[Source]:
        """The student-visible source text of exactly the material `bundle` maps: its entries'
        lesson and statement notebooks (lesson outputs where a block ships one), each lesson asset
        listing, the source of every copied file (fixtures included), the glossary and the quick
        reference when exported, and `student_answer_text` of every `after-attempt` item."""
        book = bundle.documents["book.json"]
        out: list[Source] = []
        back = self.base / "back-matter"
        if book.get("glossary") and (back / "glossary.md").is_file():
            out.append(Source(self._rel(back / "glossary.md"), self._read(back / "glossary.md")))
        if book.get("reference_md") and (back / "quick-reference.md").is_file():
            out.append(Source(self._rel(back / "quick-reference.md"),
                              self._read(back / "quick-reference.md")))
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
            statement = entry_dir / f"{STEM[record['kind']]}.ipynb"
            if (document["items"] or document["intro"] or document["outro"]) and statement.is_file():
                out += self._notebook_sources(statement, None, "")
            for path in document["files"]:
                relative = path.split("/", 2)[2]
                fixture = FIXTURE.match(relative)
                source = (entry_dir / "assets" / fixture[1] / fixture[2] if fixture
                          else entry_dir / relative)
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
        texts = [(s.where, s.value) for s in bundle.strings
                 if s.field in CONTENT_FIELDS and not _is_card_definition(s.where)]
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
        bundle = load_bundle(bundle_dir)
        baseline = self.baseline(bundle)
        findings: list[str] = []
        findings += self._asserts_findings(bundle)
        findings += self._code_findings(bundle, baseline)
        findings += self._text_findings(bundle, baseline)
        findings += self._odd_findings(bundle)
        findings += self._hash_findings(bundle)
        findings += self._visibility_findings(bundle)
        findings += self._prose_findings(bundle, baseline)
        findings += self._tie_findings(bundle)
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
        streams = self._hidden_streams
        index = _StreamIndex([stream for _, stream in streams])
        visible: set[int] = set()
        for source in baseline:
            for block in _code_blocks(source.text):
                visible.update(index.hits(block))
        hidden = [i for i in range(len(streams)) if i not in visible]
        index = _StreamIndex([() if i in visible else stream
                              for i, (_source, stream) in enumerate(streams)])
        self.stats.update(hidden_code=len(hidden), hidden_code_visible=len(visible))
        out: list[str] = []
        by_value: dict[str, list[BundleString]] = defaultdict(list)
        for string in bundle.strings:
            by_value[string.value].append(string)
        located = [(value, [(s.owner, s.where) for s in strings])
                   for value, strings in by_value.items()]
        located += [(text, [(path, path)]) for path, text in bundle.files.items() if text is not None]
        for value, places in located:
            leaked = sorted({i for block in _code_blocks(value) for i in index.hits(block)})
            for i in leaked:
                origin = streams[i][0].origin
                for owner, where in places:
                    out.append(f"FAIL: {self.book}: {owner}: solution code leaked into {where} "
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
        for record, _index, item in _items(bundle):
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
            case = check.get("answer_format", {}).get("case", "")
            if check.get("hash") != answer_hash(key, known[1], case=case):
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

    def _tie_findings(self, bundle: Bundle) -> list[str]:
        """The fields check 2 does not count must repeat a counted one exactly."""
        out = []
        book = bundle.documents["book.json"]
        glossary = {record["concept"]: record["definition_md"] for record in book.get("glossary", [])}
        for _record, document in _entry_docs(bundle):
            for card in document["cards"]:
                if card.get("kind") == "concept" and card.get("definition_md") != glossary.get(
                        card.get("concept")):
                    out.append(f"FAIL: {card['key']}: concept card definition_md differs from "
                               f"the glossary")
        for _record, _index, item in _items(bundle):
            check = item["check"]
            if check.get("kind") == "predict":
                program = _squash(check.get("program", ""))
                if program and program not in _squash(item["starter"]) and program not in _squash(
                        item["statement_md"]):
                    out.append(f"FAIL: {item['key']}: check.program is not the item's own code")
        return out


def _is_card_definition(where: str) -> bool:
    return where.split(":", 1)[1].startswith("cards/")


def answer_model_findings(root: Path, book: str, bundle_dir: Path) -> list[str]:
    """Checks 1-6 of plan 101 Phase F over the bundle written in `bundle_dir`."""
    return AnswerModel(root, book).findings(bundle_dir)
