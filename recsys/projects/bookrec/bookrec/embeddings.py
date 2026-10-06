"""Unit 7: dense semantic content embeddings over the committed GloVe subset (design 011 §6/§8).

Where Unit 3's :class:`~bookrec.lexical.LexicalRetrievalPath` represents a book as a **sparse**
bag-of-words and matches on shared surface tokens, this module represents a book as a **dense**
vector in a pretrained semantic space:

- :func:`load_glove_subset` reads the committed, checksum-pinned GloVe subset
  (``recsys/data/glove/glove_subset.{npy,json}``) with **numpy only** (no gensim) into a
  :class:`GloveSubset` — a ``(n_vocab, dim)`` matrix plus a ``token -> row`` index.
- :func:`book_embedding` composes a bag of keyword tokens into one book/reader vector: the
  **mean** of its tokens' GloVe vectors, **L2-normalized**, with out-of-vocabulary tokens skipped
  and the all-OOV case returning a safe zero vector (mean pooling is the shipped default — IDF
  weighting was measured not to help on this synthetic vocabulary).
- :class:`SemanticEmbeddingRetrievalPath` retrieves by **brute-force cosine** between a reader's
  embedding (the aggregate of the books in ``context["seen"]``) and every catalog book's embedding
  — the same dot-product-over-embeddings retriever that scores Unit 5's *learned* MF factors and
  Unit 8's *learned neural* two-tower (here the embeddings are *pretrained*).

Honest framing (recsys-009 measurement): semantic mean-pooling clears the random floor by ~8.5x but
sits **below** lexical BM25 (~0.102 vs ~0.158 hit@10) and far below the collaborative CF/MF paths.
Its value is **complementarity** — the lexical-vs-semantic top-10 overlap is only ~0.22, so GloVe
surfaces meaning-related books that share no surface tokens. The package stays numpy-only.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from bookrec.lexical import tokenize
from bookrec.protocol import BaseRetrievalPath, Candidate


def _default_glove_dir() -> Path:
    """Locate the committed ``recsys/data/glove`` directory relative to this package."""
    return Path(__file__).resolve().parents[3] / "data" / "glove"


@dataclass(frozen=True)
class GloveSubset:
    """The committed GloVe subset: a dense matrix plus the ``token -> row`` index.

    ``matrix`` is ``(n_vocab, dim)`` ``float32`` (the committed ``.npy`` is ``float16``; it is
    widened for stable arithmetic). ``token_index`` maps a vocabulary token to its matrix row;
    ``missing`` lists the out-of-vocabulary tokens (zero rows, skipped at pooling).
    """

    matrix: np.ndarray
    token_index: dict[str, int]
    tokens: list[str]
    dim: int
    missing: list[str]

    def vector(self, token: str) -> np.ndarray | None:
        """Return the GloVe vector for ``token``, or ``None`` if it is out of vocabulary."""
        row = self.token_index.get(token)
        if row is None:
            return None
        return self.matrix[row]


def load_glove_subset(path: str | Path | None = None) -> GloveSubset:
    """Load the committed GloVe subset (``.npy`` matrix + ``.json`` sidecar) with numpy only.

    ``path`` may be the ``glove`` directory, the ``.npy`` file, or ``None`` (the committed default
    under ``recsys/data/glove``). No gensim: the matrix is a plain numpy array and the sidecar is
    plain JSON.
    """
    if path is None:
        glove_dir = _default_glove_dir()
    else:
        p = Path(path)
        glove_dir = p.parent if p.suffix == ".npy" else p
    npy_path = glove_dir / "glove_subset.npy"
    json_path = glove_dir / "glove_subset.json"
    if not npy_path.is_file():
        raise FileNotFoundError(f"committed GloVe subset missing at {npy_path}")

    matrix = np.load(npy_path, allow_pickle=False).astype(np.float32)
    sidecar = json.loads(json_path.read_text(encoding="utf-8"))
    tokens = [str(token) for token in sidecar["tokens"]]
    token_index = {str(token): int(row) for token, row in sidecar["token_index"].items()}
    if matrix.shape != (len(tokens), int(sidecar["dim"])):
        raise ValueError(
            f"GloVe subset shape {matrix.shape} disagrees with sidecar "
            f"({len(tokens)}, {sidecar['dim']})"
        )
    return GloveSubset(
        matrix=matrix,
        token_index=token_index,
        tokens=tokens,
        dim=int(sidecar["dim"]),
        missing=[str(token) for token in sidecar.get("missing", [])],
    )


def book_embedding(tokens: Iterable[str], glove: GloveSubset) -> np.ndarray:
    """Compose keyword ``tokens`` into one L2-normalized embedding (mean pooling, OOV skipped).

    The embedding is the mean of the in-vocabulary tokens' GloVe vectors, then L2-normalized.
    Out-of-vocabulary tokens are skipped; if no token is in vocabulary the result is a safe zero
    vector (``dim``-length), so cosine against it is 0 rather than NaN.
    """
    rows = [glove.token_index[token] for token in tokens if token in glove.token_index]
    if not rows:
        return np.zeros(glove.dim, dtype=np.float32)
    mean = glove.matrix[rows].mean(axis=0)
    norm = float(np.linalg.norm(mean))
    if norm == 0.0:
        return np.zeros(glove.dim, dtype=np.float32)
    return (mean / norm).astype(np.float32)


class SemanticEmbeddingRetrievalPath(BaseRetrievalPath):
    """Retrieval by brute-force cosine in the pretrained GloVe embedding space.

    Like :class:`~bookrec.lexical.LexicalRetrievalPath`, the keyword corpus **and** the GloVe subset
    are provided at construction, so ``fit(interactions, catalog=None)`` keeps the exact
    ``RetrievalPath`` signature (fully substitutable) and merely precomputes each catalog book's
    L2-normalized embedding (leakage-safe: content only, no interaction log). A reader's query is the
    mean of the embeddings of the books in ``context["seen"]``, normalized; retrieval scores every
    catalog book by cosine and drops the reader's seen items.
    """

    def __init__(
        self,
        keywords: Mapping[int, str],
        glove: GloveSubset,
        *,
        name: str = "semantic",
        version: str = "1",
    ) -> None:
        super().__init__(name=name, version=version)
        if not keywords:
            raise ValueError("SemanticEmbeddingRetrievalPath needs a non-empty keyword corpus")
        self._keywords: dict[int, str] = {int(i): str(text) for i, text in keywords.items()}
        self._glove = glove
        self._item_ids: list[int] = []
        self._embeddings: np.ndarray | None = None  # (n_books, dim), each row L2-normalized or zero

    def _book_vector(self, item_id: int) -> np.ndarray:
        return book_embedding(tokenize(self._keywords.get(item_id, "")), self._glove)

    def fit(self, interactions: Any, catalog: Any | None = None) -> SemanticEmbeddingRetrievalPath:
        """Precompute each catalog book's embedding from the constructor keyword corpus + GloVe.

        Exactly the ``RetrievalPath`` protocol signature. ``interactions`` is ignored (content
        path); ``catalog`` (optional iterable of item ids) restricts the index to known items.
        """
        del interactions
        if catalog is not None:
            known = {int(item_id) for item_id in catalog}
            item_ids = sorted(i for i in self._keywords if i in known)
            if not item_ids:
                raise ValueError("SemanticEmbeddingRetrievalPath.fit: no books in the catalog")
        else:
            item_ids = sorted(self._keywords)
        self._item_ids = item_ids
        self._embeddings = np.vstack([self._book_vector(i) for i in item_ids]).astype(np.float32)
        self._fitted = True
        return self

    def load(self, artifact: Mapping[str, Any]) -> SemanticEmbeddingRetrievalPath:
        """Restore the precomputed book embeddings + ids from an :meth:`artifact` state."""
        state = dict(artifact)
        self._item_ids = [int(i) for i in state["item_ids"]]
        self._embeddings = np.array(state["embeddings"], dtype=np.float32)
        if self._embeddings.shape[0] != len(self._item_ids):
            raise ValueError("semantic artifact: embeddings/item_ids length mismatch")
        if self._embeddings.ndim != 2 or self._embeddings.shape[1] != self._glove.dim:
            raise ValueError(
                f"semantic artifact: embedding dim {self._embeddings.shape[1:]} "
                f"disagrees with the GloVe subset dim {self._glove.dim}"
            )
        self._fitted = True
        return self

    def artifact(self) -> dict[str, Any]:
        """The precomputed book-embedding matrix + ids this path owns and versions."""
        if self._embeddings is None:
            raise RuntimeError("SemanticEmbeddingRetrievalPath.artifact before fit/load")
        return {
            "item_ids": list(self._item_ids),
            "embeddings": self._embeddings.copy(),
            "dim": self._glove.dim,
        }

    def retrieve(self, query: Any, context: Any, k: int) -> list[Candidate]:
        """Top ``k`` books by cosine against the reader's embedding, minus ``seen``.

        The reader embedding is the L2-normalized mean of the embeddings of the books in
        ``context["seen"]``. An empty ``seen`` (no profile) returns ``[]``. Because each book row is
        already unit-norm (or a safe zero), the cosine score is the dot product with the normalized
        reader vector.
        """
        del query  # the reader is identified through context["seen"]
        if self._embeddings is None:
            raise RuntimeError("SemanticEmbeddingRetrievalPath.retrieve before fit/load")
        if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
            raise ValueError(f"k must be a positive int, got {k!r}")
        seen = set(context.get("seen", ())) if isinstance(context, Mapping) else set()
        rows = [row for row, item_id in enumerate(self._item_ids) if item_id in seen]
        if not rows:
            return []
        reader = self._embeddings[rows].mean(axis=0)
        norm = float(np.linalg.norm(reader))
        if norm == 0.0:
            return []
        reader = reader / norm
        scores = self._embeddings @ reader
        candidates = [
            Candidate(int(item_id), float(scores[row]), self.name)
            for row, item_id in enumerate(self._item_ids)
            if int(item_id) not in seen
        ]
        return self._finish(candidates, k)
