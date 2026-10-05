"""Unit 3: lexical / content retrieval over each book's keyword text (design 011 §6/§8).

recsys-004 gave every catalog book a keyword document (``keywords.csv.gz`` — a bag of real-word
tokens with genuine repetition and length variation). This module turns those documents into a
content retrieval path:

- :class:`BM25Index` — a bag-of-words index with document frequency ``df``, inverse-document
  frequency ``idf``, per-document term frequencies, document lengths and ``avgdl``; it scores a
  query token multiset against every document with Okapi **BM25** (parameters ``k1`` term
  saturation and ``b`` length normalization). :func:`tfidf_matrix` / :func:`cosine_similarity`
  expose the lighter TF-IDF-cosine scorer the lesson derives from scratch first.
- :class:`LexicalRetrievalPath` — a :class:`~bookrec.protocol.BaseRetrievalPath` whose **keyword
  corpus is provided at construction** (mirroring ``RandomRetrievalPath(item_ids=...)``), so
  ``fit(interactions, catalog=None)`` keeps the exact ``RetrievalPath`` protocol signature and is
  fully substitutable. It is **reader-dependent**: a reader's query is the keyword tokens of the
  books they have read (``context["seen"]``), and it retrieves other books whose words match.

Honest framing (recsys-004 measurement): keyword BM25 beats the random floor by ~13x and is a
strong *content candidate source*; it is comparable to simple genre matching and sits below the
collaborative/latent paths to come — it is **not** claimed to beat TF-IDF cosine on the scoreboard
(empirically TF-IDF cosine is ~on par here). ``k1`` saturation is a small effect on these short,
lightly-repeating keyword bags; the ``b`` length-normalization effect is clearly visible.

The package stays numpy-only (no pandas import).
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from typing import Any

import numpy as np

from bookrec.protocol import BaseRetrievalPath, Candidate


def tokenize(text: str) -> list[str]:
    """Split a keyword bag into tokens on whitespace (tokens may repeat → term frequency)."""
    return text.split()


class BM25Index:
    """A bag-of-words BM25 index over ``{item_id: "space joined token bag"}`` documents."""

    def __init__(
        self, documents: Mapping[int, str], *, k1: float = 1.2, b: float = 0.75
    ) -> None:
        k1 = float(k1)
        b = float(b)
        if not math.isfinite(k1) or k1 < 0:
            raise ValueError(f"k1 must be finite and >= 0, got {k1!r}")
        if not math.isfinite(b) or not 0.0 <= b <= 1.0:
            raise ValueError(f"b must be in [0, 1], got {b!r}")
        if not documents:
            raise ValueError("BM25Index needs at least one document")
        self.k1 = k1
        self.b = b
        self.item_ids: list[int] = [int(i) for i in sorted(documents)]
        self._row_of: dict[int, int] = {item: row for row, item in enumerate(self.item_ids)}
        tokenized = [tokenize(documents[item]) for item in self.item_ids]

        vocab: dict[str, int] = {}
        for tokens in tokenized:
            for token in tokens:
                if token not in vocab:
                    vocab[token] = len(vocab)
        self.vocab = vocab
        n_docs = len(self.item_ids)
        n_terms = len(vocab)

        tf = np.zeros((n_docs, n_terms), dtype=float)
        for row, tokens in enumerate(tokenized):
            for token in tokens:
                tf[row, vocab[token]] += 1.0
        self.tf = tf
        self.doc_len = tf.sum(axis=1)
        self.avgdl = float(self.doc_len.mean()) if n_docs else 0.0
        df = (tf > 0).sum(axis=0)
        self.df = df
        # BM25 "plus-one" IDF: always positive and monotonically decreasing in df.
        self.idf = np.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))

    def score(self, query_tokens: Iterable[str]) -> np.ndarray:
        """BM25 score of every document against a query token multiset (shape ``(n_docs,)``)."""
        qtf: dict[str, int] = {}
        for token in query_tokens:
            if token in self.vocab:
                qtf[token] = qtf.get(token, 0) + 1
        scores = np.zeros(len(self.item_ids), dtype=float)
        if not qtf:
            return scores
        # Length-normalization denominator shared across query terms.
        norm = self.k1 * (1.0 - self.b + self.b * self.doc_len / (self.avgdl or 1.0))
        for token, q_count in qtf.items():
            col = self.tf[:, self.vocab[token]]
            saturated = (col * (self.k1 + 1.0)) / (col + norm)
            scores += q_count * self.idf[self.vocab[token]] * saturated
        return scores


def tfidf_matrix(index: BM25Index) -> np.ndarray:
    """L2-normalized TF-IDF document vectors (shape ``(n_docs, n_terms)``) from a :class:`BM25Index`."""
    weighted = index.tf * index.idf[np.newaxis, :]
    norms = np.linalg.norm(weighted, axis=1, keepdims=True)
    return np.divide(weighted, norms, out=np.zeros_like(weighted), where=norms > 0)


def cosine_similarity(query_vector: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Cosine similarity of one (already TF-IDF-weighted) query vector against each matrix row."""
    query = np.asarray(query_vector, dtype=float)
    q_norm = float(np.linalg.norm(query))
    if q_norm == 0:
        return np.zeros(matrix.shape[0], dtype=float)
    row_norms = np.linalg.norm(matrix, axis=1)
    denom = row_norms * q_norm
    dots = matrix @ query
    return np.divide(dots, denom, out=np.zeros_like(dots), where=denom > 0)


class LexicalRetrievalPath(BaseRetrievalPath):
    """Content retrieval by BM25 over book keyword text; a reader's query is what they have read."""

    def __init__(
        self,
        keywords: Mapping[int, str],
        *,
        k1: float = 1.2,
        b: float = 0.75,
        name: str = "lexical",
        version: str = "1",
    ) -> None:
        super().__init__(name=name, version=version)
        if not keywords:
            raise ValueError("LexicalRetrievalPath needs a non-empty keyword corpus")
        self._keywords: dict[int, str] = {int(i): str(text) for i, text in keywords.items()}
        self.k1 = float(k1)
        self.b = float(b)
        self._index: BM25Index | None = None

    def fit(self, interactions: Any, catalog: Any | None = None) -> LexicalRetrievalPath:
        """Build the BM25 index from the constructor-provided keyword corpus.

        Exactly the ``RetrievalPath`` protocol signature (fully substitutable). ``interactions`` is
        ignored — a content path indexes the catalog text, not the interaction log. ``catalog``
        (optional iterable of item ids) restricts the index to known catalog items.
        """
        del interactions
        documents = self._keywords
        if catalog is not None:
            known = {int(item_id) for item_id in catalog}
            documents = {i: text for i, text in self._keywords.items() if i in known}
            if not documents:
                raise ValueError("LexicalRetrievalPath.fit: no keyword documents in the catalog")
        self._index = BM25Index(documents, k1=self.k1, b=self.b)
        self._fitted = True
        return self

    def load(self, artifact: Mapping[str, Any]) -> LexicalRetrievalPath:
        """Restore the fitted index from its concrete ``artifact()`` state (no re-tokenization)."""
        state = dict(artifact)
        index = BM25Index.__new__(BM25Index)
        index.k1 = float(state["k1"])
        index.b = float(state["b"])
        index.item_ids = [int(i) for i in state["item_ids"]]
        index._row_of = {item: row for row, item in enumerate(index.item_ids)}
        index.vocab = {str(token): int(col) for token, col in dict(state["vocab"]).items()}
        index.tf = np.asarray(state["tf"], dtype=float)
        index.doc_len = np.asarray(state["doc_len"], dtype=float)
        index.avgdl = float(state["avgdl"])
        index.df = np.asarray(state["df"], dtype=float)
        index.idf = np.asarray(state["idf"], dtype=float)
        self._index = index
        self.k1 = index.k1
        self.b = index.b
        self._fitted = True
        return self

    def artifact(self) -> dict[str, Any]:
        """The concrete fitted index state this path owns and versions."""
        if self._index is None:
            raise RuntimeError("LexicalRetrievalPath.artifact before fit/load")
        index = self._index
        return {
            "k1": index.k1,
            "b": index.b,
            "item_ids": list(index.item_ids),
            "vocab": dict(index.vocab),
            "tf": index.tf.copy(),
            "doc_len": index.doc_len.copy(),
            "avgdl": index.avgdl,
            "df": index.df.copy(),
            "idf": index.idf.copy(),
        }

    def retrieve(self, query: Any, context: Any, k: int) -> list[Candidate]:
        """Top ``k`` books by BM25 against the reader's keyword profile, minus ``seen``.

        The query is the keyword tokens of the books in ``context["seen"]`` (what the reader has
        read). An empty ``seen`` (no profile) returns ``[]``.
        """
        del query  # the reader is identified through context["seen"], not the query id
        if self._index is None:
            raise RuntimeError("LexicalRetrievalPath.retrieve before fit/load")
        if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
            raise ValueError(f"k must be a positive int, got {k!r}")
        seen = set(context.get("seen", ())) if isinstance(context, Mapping) else set()
        query_tokens: list[str] = []
        for item_id in seen:
            text = self._keywords.get(int(item_id))
            if text:
                query_tokens.extend(tokenize(text))
        if not query_tokens:
            return []
        scores = self._index.score(query_tokens)
        candidates = [
            Candidate(int(item_id), float(scores[row]), self.name)
            for row, item_id in enumerate(self._index.item_ids)
            if int(item_id) not in seen
        ]
        return self._finish(candidates, k)
