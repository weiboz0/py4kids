"""Unit 12: sequence-aware retrieval — what a reader read *last* matters (design 011 §6/§8).

Every earlier path treats a reader's history as a **bag** (the scoreboard's ``context["seen"]`` is a
set). Unit 12 scores on the separate **session log** (``sessions.csv.gz``), where the order of reads
carries signal (series next-volumes, author streaks, genre moods), and ships three order-aware paths:

- :class:`LastKItemItemPath` — Unit 4's item-item cosine, queried with only the reader's **last
  ``k_last`` distinct** train positives (recency) instead of all of them. ``k_last=None`` queries
  with every distinct item and reproduces :class:`~bookrec.neighborhood.ItemItemRetrievalPath`.
- :class:`TransitionRetrievalPath` — a first-order **item transition** (Markov) model: ``T[a, b]``
  counts how often ``b`` was read *right after* ``a`` in the train sequences; a reader is scored by
  the summed ``T`` rows of their last ``k_last`` reads.
- :class:`SasrecRetrievalPath` — a tiny SASRec-style **causal self-attention** model (1 block,
  1 head, dim 32, max_len 50, learned positions, tied output embedding, per-position next-item
  full-softmax cross-entropy) trained in PyTorch at the frozen recsys-015 recipe D.

**The ordered-history contract.** Every path's ``fit(rows, catalog=None)`` builds each reader's
ordered history through :func:`~bookrec.sessions.ordered_train_histories` — the ONE ordering
implementation (train positives only, ordered by ``(timestamp, row order)``), shared with
:func:`~bookrec.sessions.load_train_sequences`. Rows must carry ``timestamp`` besides the U4 keys
``reader_id, item_id, split, label``. The fitted path **stores** those histories (persisted by
``artifact()`` / restored by ``load()``), and ``retrieve(query=reader_id, context, k)`` queries with
the stored history — ``context["seen"]`` (an unordered set) is only the exclusion set. An unknown
reader retrieves ``[]``, and only strictly positive-score items are returned (the U4
coverage-ceiling convention).

**The order-shuffled control.** ``shuffle_seed`` permutes each reader's history (seeded, readers in
ascending id order) **before learning AND for querying** — the same path with order destroyed but
the item set kept, so a drop proves that *order* carries the lift.

**Leakage safety.** Only train positives enter any learned statistic or stored history; val/test
rows and sampled negatives never do (the fitted artifact is identical with or without them).

**torch only in** :meth:`SasrecRetrievalPath.fit` (lazy import). ``retrieve`` runs a numpy forward
pass over the stored weights, and ``artifact``/``load`` are numpy-only, so importing ``bookrec`` and
serving a loaded SASRec never imports torch. Training seeds ``torch.manual_seed`` and a numpy RNG,
and enables deterministic algorithms on one thread — saved and restored around ``fit`` (as in
:mod:`bookrec.two_tower`).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import numpy as np

from bookrec.neighborhood import item_item_cosine
from bookrec.protocol import BaseRetrievalPath, Candidate
from bookrec.sessions import ordered_train_histories


def shuffle_histories(histories: Mapping[int, list[int]], seed: int) -> dict[int, list[int]]:
    """The order-shuffled control: permute each reader's history with one seeded RNG.

    Readers are visited in ascending id order and each history is replaced by
    ``rng.permutation(history)`` — the item multiset is kept, only the order is destroyed.
    """
    rng = np.random.default_rng(seed)
    return {
        reader_id: [int(item) for item in rng.permutation(np.array(histories[reader_id]))]
        for reader_id in sorted(histories)
    }


def distinct_recent(history: list[int], k_last: int | None) -> list[int]:
    """The last ``k_last`` **distinct** items of a history, most recent first.

    A re-read counts once, at its most recent occurrence. ``k_last=None`` returns every distinct
    item (still most-recent first).
    """
    picked: list[int] = []
    taken: set[int] = set()
    for item in reversed(history):
        if item in taken:
            continue
        picked.append(item)
        taken.add(item)
        if k_last is not None and len(picked) == k_last:
            break
    return picked


def _check_k_last(k_last: object, *, allow_none: bool) -> int | None:
    if k_last is None and allow_none:
        return None
    if not isinstance(k_last, int) or isinstance(k_last, bool) or k_last <= 0:
        allowed = "a positive int or None" if allow_none else "a positive int"
        raise ValueError(f"k_last must be {allowed}, got {k_last!r}")
    return k_last


def _check_seed(seed: object, name: str) -> int | None:
    if seed is None:
        return None
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise TypeError(f"{name} must be an int or None, got {seed!r}")
    return seed


class _SequencePath(BaseRetrievalPath):
    """Shared fit/retrieve plumbing for the Unit-12 paths (stored ordered histories).

    Subclasses implement :meth:`_learn` (fit statistics from the learning histories) and
    :meth:`_scores` (a score per item in ``self._item_ids`` from a query history). The three hooks
    :meth:`_ordered_histories`, :meth:`_prepare_histories` and :meth:`_query_history` are the
    single places the ordered-history contract is implemented.
    """

    _positive_only = True

    def __init__(self, *, shuffle_seed: int | None, name: str, version: str) -> None:
        super().__init__(name=name, version=version)
        self.shuffle_seed = _check_seed(shuffle_seed, "shuffle_seed")
        self._histories: dict[int, list[int]] = {}
        self._item_ids: list[int] = []
        self._row_of: dict[int, int] = {}

    # ------------------------------------------------------------------ the history contract
    def _ordered_histories(self, rows: Iterable[Mapping[str, Any]]) -> dict[int, list[int]]:
        """Train-positive histories in ``(timestamp, row order)`` — the shared helper."""
        return ordered_train_histories(rows)

    def _prepare_histories(
        self, ordered: dict[int, list[int]]
    ) -> tuple[dict[int, list[int]], dict[int, list[int]]]:
        """``(learning histories, query histories)``: the shuffle control permutes BOTH."""
        if self.shuffle_seed is None:
            return ordered, ordered
        shuffled = shuffle_histories(ordered, self.shuffle_seed)
        return shuffled, shuffled

    def _query_history(self, reader_id: int, context: Any) -> list[int]:
        """The stored (ordered, or shuffled-control) history — never ``context["seen"]``."""
        del context
        return self._histories.get(reader_id, [])

    # ------------------------------------------------------------------------------- fitting
    def _histories_from_rows(
        self, interactions: Iterable[Mapping[str, Any]], catalog: Any | None
    ) -> dict[int, list[int]]:
        ordered = self._ordered_histories(interactions)
        if catalog is not None:
            known = {int(item_id) for item_id in catalog}
            ordered = {
                reader: [item for item in items if item in known]
                for reader, items in ordered.items()
            }
            ordered = {reader: items for reader, items in ordered.items() if items}
        if not ordered:
            raise ValueError(
                f"{type(self).__name__}.fit found no positive train interactions to learn from"
            )
        return ordered

    def _set_items(self, item_ids: list[int]) -> None:
        self._item_ids = item_ids
        self._row_of = {item: idx for idx, item in enumerate(item_ids)}

    @property
    def histories(self) -> dict[int, list[int]]:
        """A copy of the stored query histories (after any ``shuffle_seed`` permutation)."""
        return {reader: list(items) for reader, items in self._histories.items()}

    def _base_state(self) -> dict[str, Any]:
        return {
            "item_ids": list(self._item_ids),
            "histories": self.histories,
        }

    def _restore_base(self, state: Mapping[str, Any]) -> None:
        self._set_items([int(i) for i in state["item_ids"]])
        self._histories = {
            int(reader): [int(item) for item in items]
            for reader, items in dict(state["histories"]).items()
        }

    # ----------------------------------------------------------------------------- retrieval
    def _scores(self, history: list[int]) -> np.ndarray | None:
        raise NotImplementedError

    def retrieve(self, query: Any, context: Any, k: int) -> list[Candidate]:
        """Top ``k`` unseen, positive-score items for a reader, scored from the STORED history.

        ``query`` is the reader id; ``context["seen"]`` only excludes already-read books. An
        unknown reader (no stored history) returns ``[]``; only strictly positive scores are
        surfaced, so the result may hold fewer than ``k`` items.
        """
        if not self._fitted:
            raise RuntimeError(f"{type(self).__name__}.retrieve before fit/load")
        if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
            raise ValueError(f"k must be a positive int, got {k!r}")
        try:
            reader_id = int(query)
        except (TypeError, ValueError):
            return []
        history = self._query_history(reader_id, context)
        if not history:
            return []
        scores = self._scores(history)
        if scores is None:
            return []
        seen = set(context.get("seen", ())) if isinstance(context, Mapping) else set()
        candidates = [
            Candidate(self._item_ids[row], float(scores[row]), self.name)
            for row in (
                np.flatnonzero(scores > 0.0) if self._positive_only else np.arange(len(scores))
            ).tolist()
            if self._item_ids[row] not in seen
        ]
        return self._finish(candidates, k)


class LastKItemItemPath(_SequencePath):
    """Recency item-item CF: Unit 4's cosine, queried with the reader's last ``k_last`` distinct reads.

    :meth:`fit` builds the same item x item cosine as
    :class:`~bookrec.neighborhood.ItemItemRetrievalPath` (binary incidence of train positives,
    readers in sorted order) and stores each reader's ordered history; :meth:`retrieve` sums the
    similarity columns of the reader's ``k_last`` most recent **distinct** items
    (:func:`distinct_recent`). ``k_last=None`` uses every distinct item, i.e. the bag query, and
    returns exactly :class:`~bookrec.neighborhood.ItemItemRetrievalPath`'s top-k.
    """

    def __init__(
        self,
        k_last: int | None = 3,
        *,
        shuffle_seed: int | None = None,
        name: str = "last-k-item-item",
        version: str = "1",
    ) -> None:
        super().__init__(shuffle_seed=shuffle_seed, name=name, version=version)
        self.k_last = _check_k_last(k_last, allow_none=True)
        self._similarity: np.ndarray | None = None

    def fit(
        self, interactions: Iterable[Mapping[str, Any]], catalog: Any | None = None
    ) -> LastKItemItemPath:
        """Build the item-item cosine from the train positives and store the ordered histories.

        Rows are mappings with ``reader_id, item_id, timestamp, split, label``. The item universe
        is ``catalog`` when given, else the train-positive items. Raises :class:`ValueError` on an
        empty fit or a train-positive row without ``timestamp``.
        """
        ordered = self._histories_from_rows(interactions, catalog)
        learn, query = self._prepare_histories(ordered)
        items = (
            sorted({int(i) for i in catalog})
            if catalog is not None
            else sorted({item for seq in learn.values() for item in seq})
        )
        self._set_items(items)
        readers = sorted(learn)
        incidence = np.zeros((len(readers), len(items)), dtype=float)
        for idx, reader in enumerate(readers):
            for item in learn[reader]:
                incidence[idx, self._row_of[item]] = 1.0
        self._similarity = item_item_cosine(incidence)
        self._histories = {reader: list(items_) for reader, items_ in query.items()}
        self._fitted = True
        return self

    def _scores(self, history: list[int]) -> np.ndarray | None:
        assert self._similarity is not None
        cols = sorted(
            self._row_of[item]
            for item in distinct_recent(history, self.k_last)
            if item in self._row_of
        )
        if not cols:
            return None
        return self._similarity[:, cols].sum(axis=1)

    @property
    def similarity(self) -> np.ndarray:
        """A copy of the fitted item x item cosine similarity."""
        if self._similarity is None:
            raise RuntimeError("LastKItemItemPath.similarity before fit/load")
        return self._similarity.copy()

    def artifact(self) -> dict[str, Any]:
        """Fitted state: item ids, similarity, stored histories, and the ``k_last``/shuffle knobs."""
        if self._similarity is None:
            raise RuntimeError("LastKItemItemPath.artifact before fit/load")
        return {
            **self._base_state(),
            "similarity": self._similarity.copy(),
            "params": {"k_last": self.k_last, "shuffle_seed": self.shuffle_seed},
        }

    def load(self, artifact: Mapping[str, Any]) -> LastKItemItemPath:
        """Restore from :meth:`artifact` (arrays and histories copied, never aliased)."""
        state = dict(artifact)
        self._restore_base(state)
        similarity = np.array(state["similarity"], dtype=float)
        n_items = len(self._item_ids)
        if similarity.shape != (n_items, n_items):
            raise ValueError(
                f"LastKItemItemPath.load: similarity shape {similarity.shape} does not match "
                f"({n_items}, {n_items})"
            )
        self._similarity = similarity
        params = dict(state.get("params", {}))
        if "k_last" in params:
            self.k_last = _check_k_last(params["k_last"], allow_none=True)
        if "shuffle_seed" in params:
            self.shuffle_seed = _check_seed(params["shuffle_seed"], "shuffle_seed")
        self._fitted = True
        return self


class TransitionRetrievalPath(_SequencePath):
    """First-order item transitions: "what do readers read right after X?" (a Markov-chain view).

    :meth:`fit` counts ``T[a, b]`` = the number of times ``b`` directly follows ``a`` in a reader's
    train sequence (consecutive train positives); :meth:`retrieve` scores items by the summed ``T``
    rows of the reader's last ``k_last`` reads. ``shuffle_seed`` is the order-shuffled control: it
    permutes each history before counting AND before querying.
    """

    def __init__(
        self,
        k_last: int = 5,
        *,
        shuffle_seed: int | None = None,
        name: str = "transition",
        version: str = "1",
    ) -> None:
        super().__init__(shuffle_seed=shuffle_seed, name=name, version=version)
        self.k_last = _check_k_last(k_last, allow_none=False)
        self._transitions: np.ndarray | None = None

    def fit(
        self, interactions: Iterable[Mapping[str, Any]], catalog: Any | None = None
    ) -> TransitionRetrievalPath:
        """Count consecutive train-positive transitions and store the (possibly shuffled) histories."""
        ordered = self._histories_from_rows(interactions, catalog)
        learn, query = self._prepare_histories(ordered)
        items = (
            sorted({int(i) for i in catalog})
            if catalog is not None
            else sorted({item for seq in learn.values() for item in seq})
        )
        self._set_items(items)
        counts = np.zeros((len(items), len(items)), dtype=float)
        for reader in sorted(learn):
            seq = [self._row_of[item] for item in learn[reader]]
            if len(seq) >= 2:
                np.add.at(counts, (seq[:-1], seq[1:]), 1.0)
        self._transitions = counts
        self._histories = {reader: list(items_) for reader, items_ in query.items()}
        self._fitted = True
        return self

    def _scores(self, history: list[int]) -> np.ndarray | None:
        assert self._transitions is not None
        rows = [self._row_of[item] for item in history[-self.k_last :] if item in self._row_of]
        if not rows:
            return None
        return self._transitions[rows].sum(axis=0)

    @property
    def transitions(self) -> np.ndarray:
        """A copy of the fitted transition-count matrix ``T`` (rows: from, columns: to)."""
        if self._transitions is None:
            raise RuntimeError("TransitionRetrievalPath.transitions before fit/load")
        return self._transitions.copy()

    def artifact(self) -> dict[str, Any]:
        """Fitted state: item ids, transition counts, stored histories, ``k_last``/shuffle knobs."""
        if self._transitions is None:
            raise RuntimeError("TransitionRetrievalPath.artifact before fit/load")
        return {
            **self._base_state(),
            "transitions": self._transitions.copy(),
            "params": {"k_last": self.k_last, "shuffle_seed": self.shuffle_seed},
        }

    def load(self, artifact: Mapping[str, Any]) -> TransitionRetrievalPath:
        """Restore from :meth:`artifact` (arrays and histories copied, never aliased)."""
        state = dict(artifact)
        self._restore_base(state)
        transitions = np.array(state["transitions"], dtype=float)
        n_items = len(self._item_ids)
        if transitions.shape != (n_items, n_items):
            raise ValueError(
                f"TransitionRetrievalPath.load: transitions shape {transitions.shape} does not "
                f"match ({n_items}, {n_items})"
            )
        self._transitions = transitions
        params = dict(state.get("params", {}))
        if "k_last" in params:
            self.k_last = _check_k_last(params["k_last"], allow_none=False)
        if "shuffle_seed" in params:
            self.shuffle_seed = _check_seed(params["shuffle_seed"], "shuffle_seed")
        self._fitted = True
        return self


# ------------------------------------------------------------------------------------ SASRec
def build_sasrec_module(
    torch: Any, *, n_vocab: int, dim: int, max_len: int, dropout: float, init_std: float
) -> Any:
    """Build the (torch) SASRec module — one causal self-attention block over a padded history.

    ``torch`` is passed in so this module never imports it at top level. Index ``0`` is the padding
    item; histories are LEFT-padded to ``max_len``. The forward pass: item + learned position
    embeddings (dropout, padding zeroed) -> pre-LayerNorm single-head causal self-attention with a
    residual -> pre-LayerNorm ReLU feed-forward with a residual -> a final LayerNorm. Scores are the
    dot product of a position's hidden state with the (tied) item embeddings.
    """
    nn = torch.nn

    class SASRec(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.item = nn.Embedding(n_vocab, dim, padding_idx=0)
            self.pos = nn.Embedding(max_len, dim)
            self.attn = nn.MultiheadAttention(dim, 1, dropout=dropout, batch_first=True)
            self.ln1, self.ln2, self.lnf = nn.LayerNorm(dim), nn.LayerNorm(dim), nn.LayerNorm(dim)
            self.ff = nn.Sequential(
                nn.Linear(dim, dim), nn.ReLU(), nn.Dropout(dropout), nn.Linear(dim, dim)
            )
            self.drop = nn.Dropout(dropout)
            nn.init.normal_(self.item.weight, std=init_std)
            nn.init.normal_(self.pos.weight, std=init_std)
            with torch.no_grad():
                self.item.weight[0].zero_()

        def forward(self, x: Any) -> Any:
            length = x.shape[1]
            keep = (x != 0).float()[..., None]
            h = self.drop(self.item(x) + self.pos(torch.arange(length))[None]) * keep
            # Causal mask: True above the diagonal = position i may not attend to a later j.
            # No key_padding_mask: real positions may attend to the left-pad positions (a constant
            # LayerNorm-bias key/value). Standard SASRec masks pads; recipe D is frozen as measured
            # (recsys-014/015 gates), and the numpy forward reproduces this exact behaviour.
            mask = torch.triu(torch.ones(length, length, dtype=torch.bool), 1)
            # q, k and v are three separate (equal) LayerNorm outputs, exactly as in the recipe-D
            # probe: passing ONE shared tensor routes MultiheadAttention through a packed in-proj
            # matmul whose float rounding differs, so the seeded fit would not reproduce bit-exactly.
            attended, _ = self.attn(self.ln1(h), self.ln1(h), self.ln1(h), attn_mask=mask)
            h = (h + attended) * keep
            h = (h + self.ff(self.ln2(h))) * keep
            return self.lnf(h)

    return SASRec()


def _layer_norm(
    x: np.ndarray, weight: np.ndarray, bias: np.ndarray, eps: float = 1e-5
) -> np.ndarray:
    mean = x.mean(axis=-1, keepdims=True)
    var = ((x - mean) ** 2).mean(axis=-1, keepdims=True)
    return (x - mean) / np.sqrt(var + eps) * weight + bias


class SasrecRetrievalPath(_SequencePath):
    """Tiny SASRec: causal self-attention over a reader's last <= 50 reads (torch to train only).

    The constructor defaults are the **frozen recsys-015 recipe D** (dim 32, max_len 50, 30 epochs,
    batch 128, Adam lr 2e-3, dropout 0.2, weight decay 0, init std 0.02, seed 0). :meth:`fit`
    trains on every reader with >= 2 train positives (per-position next-item full-softmax
    cross-entropy against the tied item embeddings); the vocabulary is the train-positive items.
    :meth:`retrieve` runs a **numpy** forward pass of the reader's stored history (torch-free) and
    scores every vocabulary item by its dot product with the final hidden state.
    """

    def __init__(
        self,
        *,
        dim: int = 32,
        max_len: int = 50,
        n_epochs: int = 30,
        batch_size: int = 128,
        learning_rate: float = 2e-3,
        dropout: float = 0.2,
        weight_decay: float = 0.0,
        init_std: float = 0.02,
        seed: int = 0,
        shuffle_seed: int | None = None,
        name: str = "sasrec",
        version: str = "1",
    ) -> None:
        super().__init__(shuffle_seed=shuffle_seed, name=name, version=version)
        for value, label in (
            (dim, "dim"),
            (max_len, "max_len"),
            (n_epochs, "n_epochs"),
            (batch_size, "batch_size"),
        ):
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{label} must be a positive int, got {value!r}")
        if dim > 32 or max_len > 50:
            raise ValueError("design 011 §7 caps SASRec at dim <= 32 and max_len <= 50")
        self.dim, self.max_len, self.n_epochs, self.batch_size = dim, max_len, n_epochs, batch_size
        self.learning_rate = float(learning_rate)
        self.dropout = float(dropout)
        self.weight_decay = float(weight_decay)
        self.init_std = float(init_std)
        if not (self.learning_rate > 0 and self.init_std > 0):
            raise ValueError("learning_rate and init_std must be positive")
        if not (0.0 <= self.dropout < 1.0) or self.weight_decay < 0.0:
            raise ValueError("dropout must be in [0, 1) and weight_decay non-negative")
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise TypeError(f"seed must be an int, got {seed!r}")
        self.seed = seed
        self._weights: dict[str, np.ndarray] | None = None
        self._w64: dict[str, np.ndarray] | None = None  # float64 cache for the numpy forward
        self._loss_history: list[float] = []

    def _params(self) -> dict[str, Any]:
        return {
            "dim": self.dim,
            "max_len": self.max_len,
            "n_epochs": self.n_epochs,
            "batch_size": self.batch_size,
            "learning_rate": self.learning_rate,
            "dropout": self.dropout,
            "weight_decay": self.weight_decay,
            "init_std": self.init_std,
            "seed": self.seed,
            "shuffle_seed": self.shuffle_seed,
        }

    def fit(
        self, interactions: Iterable[Mapping[str, Any]], catalog: Any | None = None
    ) -> SasrecRetrievalPath:
        """Train the SASRec block on the (possibly shuffled) train-positive sequences.

        torch is imported **here only**. Deterministic under ``seed``: ``torch.manual_seed`` (init +
        dropout), a numpy RNG (epoch reader order), deterministic algorithms and one thread — the
        last two are process-global, so they are saved and restored in a ``finally`` block.
        """
        import torch  # LAZY: torch trains; retrieve/load/artifact stay numpy-only.

        ordered = self._histories_from_rows(interactions, catalog)
        learn, query = self._prepare_histories(ordered)
        vocab = sorted({item for seq in learn.values() for item in seq})
        self._set_items(vocab)
        index = {item: row + 1 for row, item in enumerate(vocab)}  # 0 = padding
        n_vocab = len(vocab) + 1
        data = {
            reader: [index[item] for item in seq] for reader, seq in learn.items() if len(seq) >= 2
        }
        readers = sorted(data)
        length = self.max_len

        def make_batch(batch_readers: list[int]) -> tuple[Any, Any]:
            inputs = np.zeros((len(batch_readers), length), dtype=np.int64)
            targets = np.zeros_like(inputs)
            for r, reader in enumerate(batch_readers):
                seq = data[reader][-(length + 1) :]
                inputs[r, length - len(seq) + 1 :] = seq[:-1]
                targets[r, length - len(seq) + 1 :] = seq[1:]
            return torch.tensor(inputs), torch.tensor(targets)

        rng = np.random.default_rng(self.seed)
        prev_deterministic = torch.are_deterministic_algorithms_enabled()
        prev_threads = torch.get_num_threads()
        try:
            torch.use_deterministic_algorithms(True)
            torch.set_num_threads(1)
            torch.manual_seed(self.seed)
            model = build_sasrec_module(
                torch,
                n_vocab=n_vocab,
                dim=self.dim,
                max_len=length,
                dropout=self.dropout,
                init_std=self.init_std,
            )
            optimizer = torch.optim.Adam(
                model.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay
            )
            self._loss_history = []
            for _ in range(self.n_epochs):
                model.train()
                order = rng.permutation(len(readers))
                epoch_loss, n_batches = 0.0, 0
                for start in range(0, len(order), self.batch_size):
                    inputs, targets = make_batch(
                        [readers[j] for j in order[start : start + self.batch_size]]
                    )
                    logits = model(inputs) @ model.item.weight.T  # tied output embedding
                    logits[..., 0] = -1e9  # never predict the padding item
                    loss = torch.nn.functional.cross_entropy(
                        logits.reshape(-1, n_vocab), targets.reshape(-1), ignore_index=0
                    )
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                    epoch_loss += loss.item()
                    n_batches += 1
                self._loss_history.append(epoch_loss / max(n_batches, 1))
            model.eval()
            weights = {
                key: value.detach().numpy().astype(np.float32).copy()
                for key, value in model.state_dict().items()
            }
        finally:
            torch.use_deterministic_algorithms(prev_deterministic)
            torch.set_num_threads(prev_threads)

        self._weights = weights
        self._w64 = None
        self._histories = {reader: list(items_) for reader, items_ in query.items()}
        self._fitted = True
        return self

    # ------------------------------------------------------------------ numpy forward / score
    def encode(self, history: list[int]) -> np.ndarray:
        """Left-padded vocabulary indices (0 = padding) of the last ``max_len`` known items."""
        indices = [self._row_of[item] + 1 for item in history if item in self._row_of]
        indices = indices[-self.max_len :]
        padded = np.zeros(self.max_len, dtype=np.int64)
        if indices:
            padded[self.max_len - len(indices) :] = indices
        return padded

    def final_state(self, history: list[int]) -> np.ndarray | None:
        """The numpy forward pass: the final position's hidden state (``None`` for no known item)."""
        if self._weights is None:
            raise RuntimeError("SasrecRetrievalPath.final_state before fit/load")
        x = self.encode(history)
        if x[-1] == 0:
            return None
        if self._w64 is None:
            self._w64 = {key: value.astype(np.float64) for key, value in self._weights.items()}
        w = self._w64
        dim = w["item.weight"].shape[1]
        keep = (x != 0).astype(np.float64)[:, None]
        h = (w["item.weight"][x] + w["pos.weight"][: len(x)]) * keep
        normed = _layer_norm(h, w["ln1.weight"], w["ln1.bias"])
        w_q, w_k, w_v = np.split(w["attn.in_proj_weight"], 3, axis=0)
        b_q, b_k, b_v = np.split(w["attn.in_proj_bias"], 3)
        # Causal attention for the LAST position: it may attend to every position (all are <= it).
        q = normed[-1] @ w_q.T + b_q
        keys = normed @ w_k.T + b_k
        values = normed @ w_v.T + b_v
        logits = keys @ q / np.sqrt(dim)
        attn = np.exp(logits - logits.max())
        attn /= attn.sum()
        attended = (attn @ values) @ w["attn.out_proj.weight"].T + w["attn.out_proj.bias"]
        last = h[-1] + attended
        ff_in = _layer_norm(last, w["ln2.weight"], w["ln2.bias"])
        hidden = np.maximum(ff_in @ w["ff.0.weight"].T + w["ff.0.bias"], 0.0)
        last = last + hidden @ w["ff.3.weight"].T + w["ff.3.bias"]
        return _layer_norm(last, w["lnf.weight"], w["lnf.bias"])

    def _scores(self, history: list[int]) -> np.ndarray | None:
        state = self.final_state(history)
        if state is None:
            return None
        assert self._w64 is not None
        return self._w64["item.weight"][1:] @ state

    # --------------------------------------------------------------------------- persistence
    @property
    def loss_history(self) -> list[float]:
        """Mean training loss per epoch from the last :meth:`fit` (restored by :meth:`load` when the
        artifact carries one; empty for an artifact saved without it)."""
        return list(self._loss_history)

    def artifact(self) -> dict[str, Any]:
        """Fitted state (numpy only): weights, vocabulary item ids, stored histories, recipe."""
        if self._weights is None:
            raise RuntimeError("SasrecRetrievalPath.artifact before fit/load")
        return {
            **self._base_state(),
            "weights": {key: value.copy() for key, value in self._weights.items()},
            # Additive (recsys-017): the per-epoch training curve travels with a cached artifact.
            "loss_history": [float(x) for x in self._loss_history],
            "params": self._params(),
        }

    def load(self, artifact: Mapping[str, Any]) -> SasrecRetrievalPath:
        """Restore from :meth:`artifact` — numpy only, never imports torch."""
        state = dict(artifact)
        self._restore_base(state)
        weights = {
            str(key): np.array(value, dtype=np.float32)
            for key, value in dict(state["weights"]).items()
        }
        item_weight = weights.get("item.weight")
        if item_weight is None or item_weight.shape[0] != len(self._item_ids) + 1:
            raise ValueError(
                "SasrecRetrievalPath.load: item.weight must have one row per vocabulary item "
                "plus the padding row"
            )
        params = dict(state.get("params", {}))
        for key in ("dim", "max_len", "n_epochs", "batch_size", "seed"):
            if key in params:
                setattr(self, key, int(params[key]))
        for key in ("learning_rate", "dropout", "weight_decay", "init_std"):
            if key in params:
                setattr(self, key, float(params[key]))
        if "shuffle_seed" in params:
            self.shuffle_seed = _check_seed(params["shuffle_seed"], "shuffle_seed")
        self._weights = weights
        self._w64 = None
        # Version-compatible: an artifact saved before recsys-017 has no curve -> empty list.
        self._loss_history = [float(x) for x in state.get("loss_history", [])]
        self._fitted = True
        return self
