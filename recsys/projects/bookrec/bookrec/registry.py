"""A small registry mapping stable path names to retrieval paths.

Duplicate names are rejected (two paths blending under one provenance label would be ambiguous),
and duplicate artifact ownership is rejected (a path owns exactly one artifact; §5).
"""

from __future__ import annotations

from collections.abc import Iterator

from bookrec.protocol import RetrievalPath


class DuplicatePathError(ValueError):
    """Raised when a name — or an artifact — is already claimed in the registry."""


class PathRegistry:
    """An insertion-ordered name→:class:`RetrievalPath` registry."""

    def __init__(self) -> None:
        self._paths: dict[str, RetrievalPath] = {}
        self._artifacts: dict[str, str] = {}

    def register(self, path: RetrievalPath) -> RetrievalPath:
        name = getattr(path, "name", None)
        if not isinstance(name, str) or not name:
            raise ValueError("a retrieval path must expose a non-empty string name")
        if name in self._paths:
            raise DuplicatePathError(f"path name already registered: {name!r}")
        artifact = getattr(path, "artifact_name", lambda: name)()
        if artifact in self._artifacts:
            raise DuplicatePathError(
                f"artifact {artifact!r} already owned by path {self._artifacts[artifact]!r}"
            )
        self._paths[name] = path
        self._artifacts[artifact] = name
        return path

    def get(self, name: str) -> RetrievalPath:
        return self._paths[name]

    def names(self) -> list[str]:
        return list(self._paths)

    def __contains__(self, name: object) -> bool:
        return name in self._paths

    def __len__(self) -> int:
        return len(self._paths)

    def __iter__(self) -> Iterator[RetrievalPath]:
        return iter(self._paths.values())
