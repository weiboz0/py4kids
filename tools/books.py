"""Helpers for resolving books and their dependency-provided concepts."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


def book_entries(root: Path) -> dict[str, dict]:
    """Return registered books keyed by id; tolerate legacy fixture roots."""
    path = Path(root).resolve() / "books.yaml"
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("books"), list):
        return {}
    return {
        entry["id"]: entry
        for entry in data["books"]
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }


def book_entry(root: Path, book: str) -> dict:
    return book_entries(root).get(book, {"id": book, "root": book, "depends_on": []})


def book_path(root: Path, book: str) -> Path:
    entry = book_entry(root, book)
    relative = entry.get("root", book)
    return Path(root).resolve() / relative


def variant_of(root: Path, book: str) -> str | None:
    configured = book_entry(root, book).get("variant_of")
    return configured if isinstance(configured, str) else None


def peers(root: Path, book: str) -> list[str]:
    """Return the book's declared ``peers`` (design 008 D3); malformed values read as empty.

    Validation (symmetry, known ids) lives in
    :func:`tools.curriculum.global_concept_uniqueness_findings`.
    """
    configured = book_entry(root, book).get("peers", [])
    if not isinstance(configured, list):
        return []
    return [value for value in configured if isinstance(value, str)]


def prereq_policy(root: Path, book: str) -> str | None:
    configured = book_entry(root, book).get("prereq_policy")
    return configured if isinstance(configured, str) else None


def is_buildout(root: Path, book: str) -> bool:
    configured = book_entry(root, book).get("buildout", False)
    return configured if isinstance(configured, bool) else False


def introduced_concepts(root: Path, book: str) -> set[str]:
    path = book_path(root, book) / "curriculum" / "coverage-map.yaml"
    if not path.is_file():
        return set()
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        return set()
    return {
        concept
        for entry in data["entries"]
        if isinstance(entry, dict)
        for concept in entry.get("introduces", [])
        if isinstance(concept, str)
    }


def dependency_baseline(root: Path, book: str) -> set[str]:
    """Return concepts introduced by all direct and transitive dependencies."""
    registry = book_entries(root)

    def resolve(current: str, trail: frozenset[str]) -> set[str]:
        if current in trail:
            raise ValueError(f"cyclic book dependency involving {current}")
        entry = registry.get(current, {"depends_on": []})
        result: set[str] = set()
        for dependency in entry.get("depends_on", []) or []:
            if not isinstance(dependency, str):
                continue
            result |= introduced_concepts(root, dependency)
            result |= resolve(dependency, trail | {current})
        return result

    return resolve(book, frozenset())


class BaselineConfigError(ValueError):
    """A book's optional ``curriculum/baseline.yaml`` is invalid."""


def assumed_baseline(root: Path, book: str) -> set[str]:
    """Return the book-local assumed concepts, failing closed on invalid config."""
    path = book_path(root, book) / "curriculum" / "baseline.yaml"
    if not path.is_file():
        return set()

    def invalid(detail: str) -> BaselineConfigError:
        return BaselineConfigError(f"FAIL: {book}: {detail}")

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        raise invalid("baseline.yaml is not valid YAML") from error
    if not isinstance(data, dict):
        raise invalid("baseline.yaml must be a mapping")
    if set(data) != {"baseline_version", "entries"}:
        raise invalid("baseline.yaml keys must be exactly ['baseline_version', 'entries']")
    version = data["baseline_version"]
    if not isinstance(version, int) or isinstance(version, bool) or version != 1:
        raise invalid("baseline_version must be 1")
    entries = data["entries"]
    if not isinstance(entries, list):
        raise invalid("baseline entries must be a list")

    ids: list[str] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise invalid(f"baseline entry {index} must be a mapping")
        if set(entry) != {"id", "name"}:
            raise invalid(f"bad baseline keys in entry {index}")
        if not isinstance(entry["id"], str) or not isinstance(entry["name"], str):
            raise invalid(f"baseline entry {index} id and name must be strings")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", entry["id"]):
            raise invalid(f"non-kebab baseline id: {entry['id']!r}")
        ids.append(entry["id"])

    duplicates = sorted({concept_id for concept_id in ids if ids.count(concept_id) > 1})
    if duplicates:
        raise invalid(f"duplicate baseline ids: {duplicates}")

    concepts_path = book_path(root, book) / "curriculum" / "concepts.yaml"
    own_ids: set[str] = set()
    if concepts_path.is_file():
        try:
            concepts_data = yaml.safe_load(concepts_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError):
            concepts_data = None
        if isinstance(concepts_data, dict) and isinstance(concepts_data.get("concepts"), list):
            own_ids = {
                concept["id"]
                for concept in concepts_data["concepts"]
                if isinstance(concept, dict) and isinstance(concept.get("id"), str)
            }
    overlap = sorted(set(ids) & own_ids)
    if overlap:
        raise invalid(f"assumed baseline ids also appear in concepts.yaml: {overlap}")
    return set(ids)


def known_baseline(root: Path, book: str) -> set[str]:
    """Return concepts supplied by dependencies or explicitly assumed by this book."""
    return dependency_baseline(root, book) | assumed_baseline(root, book)


def concept_minimum(root: Path, book: str) -> int:
    entry = book_entry(root, book)
    configured = entry.get("concept_minimum")
    if isinstance(configured, int) and not isinstance(configured, bool) and configured >= 0:
        return configured
    return 1 if entry.get("depends_on") else 40


def lesson_budget(root: Path, book: str) -> tuple[float, float | None]:
    entry = book_entry(root, book)
    configured = entry.get("lesson_budget")
    if (
        isinstance(configured, list)
        and len(configured) == 2
        and all(isinstance(value, (int, float)) for value in configured)
    ):
        return configured[0], configured[1]
    return (1, None) if entry.get("depends_on") else (28, 32)


def book_flag(root: Path, book: str, flag: str) -> bool:
    """Return a boolean feature flag from books.yaml (absent or non-boolean means False).

    Tools key features on these flags, never on book ids (design 008):
    ``publication`` (book-publication pipeline), ``judge`` (stdin solvers + subprocess judge),
    ``patterns`` (pattern checks and the coverage-map v2 / markdown concept scan),
    ``acsl`` (the ACSL season structure: manifest ``acsl:`` block, season.yaml, acsl-check).
    """
    configured = book_entry(root, book).get(flag, False)
    return configured if isinstance(configured, bool) else False


def books_with_flag(root: Path, flag: str) -> list[str]:
    """Return registered book ids (registry order) whose ``flag`` is true."""
    return [book for book in book_entries(root) if book_flag(root, book, flag)]


def book_title(root: Path, book: str) -> str:
    configured = book_entry(root, book).get("title")
    return configured if isinstance(configured, str) and configured.strip() else book


def book_subtitle(root: Path, book: str) -> str:
    configured = book_entry(root, book).get("subtitle")
    return configured if isinstance(configured, str) else ""


def output_pdf_name(book: str, edition: str) -> str:
    """The one PDF file name for a book edition: ``<id>-<edition>.pdf`` (design 008 D1)."""
    return f"{book}-{edition}.pdf"


def qualified_owner_alternation(root: Path, book: str | None = None) -> str:
    """Regex alternation of every registered book id (plus ``book``), longest first.

    Qualified concept ids are ``<owner>:<concept-id>``; building the owner part from the
    registry lets hyphenated ids (``usaco-bronze:str-split``) and future books work unedited.
    """
    owners = set(book_entries(root))
    if book:
        owners.add(book)
    ordered = sorted(owners, key=lambda owner: (-len(owner), owner))
    return "|".join(re.escape(owner) for owner in ordered) or "(?!)"


def qualified_concept_id_pattern(
    root: Path, book: str | None = None, concept: str = r"[a-z][a-z0-9-]*"
) -> re.Pattern[str]:
    """Compiled ``^(owner|...):<concept>$`` for the registered owners."""
    return re.compile(rf"^(?:{qualified_owner_alternation(root, book)}):{concept}$")


# --- per-book publication config (design 010 D1, plan 097) ---------------------------------

PUBLICATION_CONFIG = "publication.yaml"
# Chapter kinds recorded in a generated project's inventory.json.
CHAPTER_KINDS = frozenset({"front", "setup", "unit", "checkpoint", "project", "answers",
                           "glossary", "quickref", "index"})


# The publication audit's banned phrases (tools.publish_audit reads them from here). Every
# student-family edition bans INDEPENDENCE_BANS; the full Student Book also bans "Answer key"; answer
# chapters also ban "assert". A phrase exemption must name one of them (case-insensitively).
INDEPENDENCE_BANS = ("Teacher's Edition", 'your teacher', 'with your teacher',
                     'ask your teacher', 'not graded', 'no-exec', 'solutions.ipynb',
                     'python assets/', 'Lesson One', "checked by the course's test suite",
                     'There is no real program')
STUDENT_BANS = INDEPENDENCE_BANS + ('Answer key',)
ANSWER_BANS = ('assert',)
BANNED_PHRASES = STUDENT_BANS + ANSWER_BANS


class PublicationConfigError(ValueError):
    """A publication book's `publication.yaml` is missing or invalid."""


@dataclass(frozen=True)
class PhraseExemption:
    """A banned phrase allowed in chapters of the given kinds whose book-relative source matches a glob."""

    phrase: str
    kinds: tuple[str, ...]
    chapters: tuple[str, ...]
    reason: str

    def applies(self, kind: str | None, source: str | None, book_prefix: str) -> bool:
        """True when a chapter of `kind`, recorded with the repo-relative `source`, is exempt.

        The recorded `<book root>/` prefix is stripped before matching, so globs are book-relative.
        An empty source (the combined answers appendix, the index) never matches.
        """
        if kind not in self.kinds or not source:
            return False
        prefix = book_prefix.rstrip("/") + "/"
        relative = source.removeprefix(prefix)
        return any(fnmatch.fnmatchcase(relative, pattern) for pattern in self.chapters)


@dataclass(frozen=True)
class PublicationConfig:
    """Everything book-specific the publisher and the audit need (a `<book>/publication.yaml`)."""

    book: str
    setup_source: str
    setup_teacher_notes: str
    setup_numbered: bool
    project_headers: dict[str, str]
    lesson_heading: str
    index_names: frozenset[str]
    # A unit's or checkpoint's running header when its title is over RUNNING_HEAD_MAX characters
    # (plan 099 A4); keyed by unit or checkpoint id.
    unit_headers: dict[str, str] = field(default_factory=dict)
    error_demo_ids: frozenset[str] = frozenset()
    hang_demo_ids: frozenset[str] = frozenset()
    print_required_starters: frozenset[str] = frozenset()
    error_demo_routing_exceptions: frozenset[str] = frozenset()
    print_page_target: int | None = None
    turtle_tryits: dict[str, int] = field(default_factory=dict)
    teacher_turtle_drawings: int = 0
    phrase_exemptions: tuple[PhraseExemption, ...] = ()
    goals_recap: str = "required"

    @property
    def setup_id(self) -> str:
        """The setup chapter's id (and .qmd stem): its source file's stem."""
        return Path(self.setup_source).stem

    @property
    def setup_name(self) -> str:
        return Path(self.setup_source).name

    @property
    def setup_title(self) -> str:
        return "Unit 0 — Getting Set Up" if self.setup_numbered else "Getting Set Up"

    @property
    def setup_label(self) -> str:
        return "Unit 0" if self.setup_numbered else ""

    def exempt_phrases(self, kind: str | None, source: str | None, book_prefix: str) -> frozenset[str]:
        return frozenset(exemption.phrase for exemption in self.phrase_exemptions
                         if exemption.applies(kind, source, book_prefix))


_TOP_KEYS = {"setup", "project_headers", "unit_headers", "lesson_heading", "index_names", "audit"}
# The longest running header (chapter mark) the theme sets; a longer unit or checkpoint title needs a
# `unit_headers` entry, and the publisher never truncates silently (plan 099 A4).
RUNNING_HEAD_MAX = 32
_SETUP_KEYS = {"source", "teacher_notes", "numbered"}
_AUDIT_KEYS = {"error_demo_ids", "hang_demo_ids", "print_required_starters",
               "error_demo_routing_exceptions", "print_page_target", "turtle_tryits",
               "teacher_turtle_drawings", "phrase_exemptions", "goals_recap"}
_EXEMPTION_KEYS = {"phrase", "kinds", "chapters", "reason"}


def _string_list(value, where: str, errors: list[str]) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        errors.append(f"{where}: must be a list of non-empty strings")
        return []
    return value


def _mapping(value, where: str, errors: list[str]) -> dict:
    if not isinstance(value, dict):
        errors.append(f"{where}: must be a mapping")
        return {}
    return value


def _unknown(data: dict, allowed: set[str], where: str, errors: list[str]) -> None:
    for key in sorted(set(data) - allowed, key=str):
        errors.append(f"{where}: unknown key {key}")


def _parse_publication_config(root: Path, book: str) -> tuple[PublicationConfig | None, list[str]]:
    base = book_path(root, book)
    path = base / PUBLICATION_CONFIG
    where = f"{book}/{PUBLICATION_CONFIG}"
    if not path.is_file():
        return None, [f"{where}: missing (every publication book needs one; design 010 D1)"]
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        return None, [f"{where}: invalid YAML: {error}"]
    errors: list[str] = []
    data = _mapping(data, where, errors)
    _unknown(data, _TOP_KEYS, where, errors)
    for key in ("setup", "project_headers", "lesson_heading", "audit"):
        if key not in data:
            errors.append(f"{where}: missing key {key}")

    setup = _mapping(data.get("setup", {}), f"{where}: setup", errors)
    _unknown(setup, _SETUP_KEYS, f"{where}: setup", errors)
    for key in sorted(_SETUP_KEYS - set(setup)):
        errors.append(f"{where}: setup: missing key {key}")
    source = setup.get("source")
    notes = setup.get("teacher_notes")
    numbered = setup.get("numbered")
    for key, value in (("source", source), ("teacher_notes", notes)):
        if key in setup and (not isinstance(value, str) or not value):
            errors.append(f"{where}: setup: {key} must be a book-relative path")
    if isinstance(source, str) and source:
        if not (base / source).is_file():
            errors.append(f"{where}: setup: source {source} does not exist")
        if "teacher-notes" in Path(source).name or Path(source).suffix != ".md":
            errors.append(f"{where}: setup: source {source} must be a Markdown file that is not teacher notes")
    if isinstance(notes, str) and notes:
        if "teacher-notes" not in Path(notes).name:
            errors.append(f"{where}: setup: teacher_notes {notes} must match the teacher-notes "
                          "exclusion pattern (its file name contains 'teacher-notes')")
        if not (base / notes).is_file():
            errors.append(f"{where}: setup: teacher_notes {notes} does not exist")
    if "numbered" in setup and not isinstance(numbered, bool):
        errors.append(f"{where}: setup: numbered must be true or false")

    headers = _mapping(data.get("project_headers", {}) or {}, f"{where}: project_headers", errors)
    for project, header in headers.items():
        if not isinstance(project, str) or not project.startswith("project-"):
            errors.append(f"{where}: project_headers: key {project} must be a project id")
        if not isinstance(header, str) or not header.strip():
            errors.append(f"{where}: project_headers: {project} needs a header text")

    unit_headers = _mapping(data.get("unit_headers", {}) or {}, f"{where}: unit_headers", errors)
    for unit, header in unit_headers.items():
        # Units and checkpoints share `running_head`, so a checkpoint id is a valid key too.
        kind = unit.split("-", 1)[0] if isinstance(unit, str) else None
        if kind not in ("unit", "checkpoint"):
            errors.append(f"{where}: unit_headers: key {unit} must be a unit or checkpoint id")
        elif not (base / f"{kind}s" / unit).is_dir():
            errors.append(f"{where}: unit_headers: {kind} {unit} does not exist")
        if not isinstance(header, str) or not header.strip():
            errors.append(f"{where}: unit_headers: {unit} needs a header text")
        elif len(header) > RUNNING_HEAD_MAX:
            errors.append(f"{where}: unit_headers: {unit} header is {len(header)} characters "
                          f"(at most {RUNNING_HEAD_MAX})")

    lesson_heading = data.get("lesson_heading")
    if "lesson_heading" in data:
        if not isinstance(lesson_heading, str) or not lesson_heading.startswith("^## "):
            errors.append(f"{where}: lesson_heading must be a regex starting with '^## '")
        else:
            try:
                re.compile(lesson_heading)
            except re.error as error:
                errors.append(f"{where}: lesson_heading: invalid regex: {error}")
    index_names = _string_list(data.get("index_names"), f"{where}: index_names", errors)

    audit = _mapping(data.get("audit", {}), f"{where}: audit", errors)
    _unknown(audit, _AUDIT_KEYS, f"{where}: audit", errors)
    ids = {key: _string_list(audit.get(key), f"{where}: audit: {key}", errors)
           for key in ("error_demo_ids", "hang_demo_ids", "print_required_starters",
                       "error_demo_routing_exceptions")}
    target = audit.get("print_page_target")
    if target is not None and (not isinstance(target, int) or isinstance(target, bool) or target <= 0):
        errors.append(f"{where}: audit: print_page_target must be a positive integer")
        target = None
    tryits = _mapping(audit.get("turtle_tryits", {}) or {}, f"{where}: audit: turtle_tryits", errors)
    for unit, count in tryits.items():
        if not isinstance(unit, str) or not unit.startswith("unit-"):
            errors.append(f"{where}: audit: turtle_tryits: key {unit} must be a unit id")
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            errors.append(f"{where}: audit: turtle_tryits: {unit} must be a count")
    drawings = audit.get("teacher_turtle_drawings", 0)
    if not isinstance(drawings, int) or isinstance(drawings, bool) or drawings < 0:
        errors.append(f"{where}: audit: teacher_turtle_drawings must be a count")
        drawings = 0
    goals_recap = audit.get("goals_recap")
    if goals_recap != "required":
        errors.append(f"{where}: audit: goals_recap must be 'required' (every book; design 010)")

    exemptions = []
    raw_exemptions = audit.get("phrase_exemptions", []) or []
    if not isinstance(raw_exemptions, list):
        errors.append(f"{where}: audit: phrase_exemptions must be a list")
        raw_exemptions = []
    for position, raw in enumerate(raw_exemptions, 1):
        label = f"{where}: audit: phrase_exemptions[{position}]"
        raw = _mapping(raw, label, errors)
        _unknown(raw, _EXEMPTION_KEYS, label, errors)
        missing = sorted(_EXEMPTION_KEYS - set(raw))
        if missing:
            errors.append(f"{label}: missing {', '.join(missing)}")
            continue
        phrase, reason = raw["phrase"], raw["reason"]
        if not isinstance(phrase, str) or not phrase:
            errors.append(f"{label}: phrase must be a non-empty string")
        elif phrase.casefold() not in {banned.casefold() for banned in BANNED_PHRASES}:
            errors.append(f"{label}: unknown phrase {phrase!r} (not on the audit's ban list: "
                          f"{', '.join(BANNED_PHRASES)})")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{label}: reason must say why the book teaches the phrase")
        kinds = _string_list(raw["kinds"], f"{label}: kinds", errors)
        chapters = _string_list(raw["chapters"], f"{label}: chapters", errors)
        if not kinds or not chapters:
            errors.append(f"{label}: kinds and chapters must be non-empty")
        for kind in kinds:
            if kind not in CHAPTER_KINDS:
                errors.append(f"{label}: unknown chapter kind {kind}")
        for pattern in chapters:
            if pattern.startswith(("/", f"{book}/")):
                errors.append(f"{label}: chapter glob {pattern} must be book-relative")
        exemptions.append(PhraseExemption(str(phrase), tuple(kinds), tuple(chapters), str(reason)))

    if errors:
        return None, errors
    return PublicationConfig(
        book=book,
        setup_source=source,
        setup_teacher_notes=notes,
        setup_numbered=numbered,
        project_headers=dict(headers),
        unit_headers=dict(unit_headers),
        lesson_heading=lesson_heading,
        index_names=frozenset(index_names),
        error_demo_ids=frozenset(ids["error_demo_ids"]),
        hang_demo_ids=frozenset(ids["hang_demo_ids"]),
        print_required_starters=frozenset(ids["print_required_starters"]),
        error_demo_routing_exceptions=frozenset(ids["error_demo_routing_exceptions"]),
        print_page_target=target,
        turtle_tryits=dict(tryits),
        teacher_turtle_drawings=drawings,
        phrase_exemptions=tuple(exemptions),
        goals_recap=goals_recap,
    ), []


def publication_config_errors(root: Path, book: str) -> list[str]:
    """Every problem with a book's `publication.yaml` (empty when it is valid)."""
    return _parse_publication_config(root, book)[1]


def publication_config(root: Path, book: str) -> PublicationConfig:
    """Load and validate a publication book's `publication.yaml`; fail loudly when it is missing or bad."""
    config, errors = _parse_publication_config(root, book)
    if config is None:
        raise PublicationConfigError("FAIL: " + "\n  ".join(errors))
    return config
