"""Unit 11: the neural reranker — a learned second stage over the merged candidate pool (design 011 §8).

The fifth Part-2 unit, and the second stage of **retrieve-then-rank**, finally *learned*. Units 2–10
each ship a retrieval *path* — a cheap candidate generator that sees one slice of the signal
(popularity, lexical text, item-item behaviour, MF / two-tower taste, semantic content). Unit 6
blended their calibrated scores with **fixed** weights; Unit 10 fused a sparse + dense pair. This
unit keeps that two-stage shape — cheap retrieval proposes a pool, an expensive model re-scores only
that pool — but replaces the fixed ordering key with a **learned** one.

:class:`NeuralRerankerPath` assembles, for each pooled candidate, a small **feature vector** (the
per-path calibrated scores + content/behaviour signals), and trains a tiny **PyTorch** MLP on
implicit feedback (pointwise logistic over pool positives vs sampled pool negatives) to score it.
``rank.py`` already anticipated this: *"a learned reranker replaces the ordering key in a later unit
without changing this signature."* The learned per-candidate score **is** that ordering key
(:func:`rerank`); :class:`NeuralRerankerPath` is the thin :class:`~bookrec.protocol.BaseRetrievalPath`
wrapper that lets the scoreboard and registry treat the reranker like any other path.

**The leakage trap (the headline lesson, MEASURED).** The naive recipe — label the reranker with the
reader's train positives while the feature-paths are fit on that *same* train — **leaks by
memorization**: a path that trained on an item scores it inflatedly, so "high score ⇒ positive" is
learned from in-train scores that *validation* candidates never exhibit (distribution shift). It
**tanks** to ~0.28 hit@10, below plain score-order. The fix is a **time-ordered holdout inside
train**: per reader the latest ~25% of train positives (>=1) become the reranker's *labels*; the
earlier 75% is the retrieval **profile**. **Every training-time feature and statistic** — the
feature-paths, the genre/author history, the popularity counts — is built from the **profile rows
that exclude every held-out-label-item occurrence**, so no held-out event enters the paths OR the
popularity count. (A repeat-read item can sit in both the profile set and the label set; excluding
the label item's rows wholesale — not just the held-out event — keeps the paths and ``log_pop``
consistent and conservatively leakage-safe.) The held-out 25% supplies *only* positive labels. At
serving the full-fit paths and the full-train statistics are used. Same feature code, phase-dependent
input.

**Where the lift comes from (the counterintuitive payoff, MEASURED).** On this data the lift is from
the **content** features (genre/author affinity, log-popularity), *not* clever score combination:
content-only reranking is the strongest variant and ``linear ~= MLP`` throughout — the non-linear
combiner adds nothing here. The reranker edges the two-tower / ties the hybrid on hit@10 but **loses
catalog coverage** (a precise ranker concentrates its picks). The unit reports that honestly.

**Determinism (design 011 §7, same contract as Unit 8).** Training seeds :func:`torch.manual_seed`
(MLP init) and a numpy RNG (negative sampling / shuffling), enables
:func:`torch.use_deterministic_algorithms` and pins :func:`torch.set_num_threads` to 1 — and
**saves/restores** those two process-global knobs in a ``finally`` block so a later notebook cell is
not left single-threaded / in deterministic mode. The determinism gate is identical top-k ranking +
``allclose`` on every weight (never exact-float).

**torch is imported LAZILY, inside** :meth:`RerankerModel.fit` **only** — no top-level ``import
torch`` anywhere in this module. :meth:`~NeuralRerankerPath.retrieve`, :meth:`~NeuralRerankerPath.load`
and :meth:`~NeuralRerankerPath.artifact` operate on the **numpy** MLP weights stored at fit, so
importing ``bookrec`` and serving the reranker never imports torch (proven by the import-blocked
subprocess test in ``tests/test_unit07.py``).

**Feature count.** 17 features = 6 calibrated per-path scores + 6 presence flags + ``n_paths`` + 4
content (``genre_frac``, ``genre_cos``, ``author_frac``, ``log_pop``). (The plan's "18-dim" prose
miscounts by one; the probe reference and this implementation are the authoritative 17.)
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any

import numpy as np

from bookrec.protocol import BaseRetrievalPath, Candidate
from bookrec.rank import rank

#: The six retrieval paths whose calibrated scores form the per-path feature block, in a fixed order
#: (so a persisted feature vector is reproducible). Absent paths contribute 0.0 + a 0 presence flag.
DEFAULT_PATH_NAMES: tuple[str, ...] = (
    "popularity",
    "lexical",
    "item-item",
    "mf",
    "semantic",
    "two-tower",
)

#: The feature families, each a contiguous block, so an ablation can drop a whole family by name.
FEATURE_FAMILIES: tuple[str, ...] = ("scores", "presence", "meta", "content")

_CONTENT_NAMES: tuple[str, ...] = ("genre_frac", "genre_cos", "author_frac", "log_pop")


def feature_names(path_names: Sequence[str] = DEFAULT_PATH_NAMES) -> list[str]:
    """The ordered feature names: per-path scores, per-path presence flags, ``n_paths``, content."""
    return (
        [f"score:{p}" for p in path_names]
        + [f"in:{p}" for p in path_names]
        + ["n_paths", *(_CONTENT_NAMES)]
    )


def _family_of(index: int, n_paths: int) -> str:
    """Which :data:`FEATURE_FAMILIES` block a feature column belongs to."""
    if index < n_paths:
        return "scores"
    if index < 2 * n_paths:
        return "presence"
    if index == 2 * n_paths:
        return "meta"
    return "content"


def family_mask(families: Sequence[str], path_names: Sequence[str] = DEFAULT_PATH_NAMES) -> np.ndarray:
    """A boolean column mask keeping only the named feature families (for ablations)."""
    keep = set(families)
    unknown = keep - set(FEATURE_FAMILIES)
    if unknown:
        raise ValueError(f"unknown feature families {sorted(unknown)}; choose from {FEATURE_FAMILIES}")
    if not keep:
        raise ValueError("feature_families must name at least one family")
    n = len(path_names)
    total = len(feature_names(path_names))
    return np.array([_family_of(i, n) in keep for i in range(total)], dtype=bool)


def _positive_int(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} must be a positive int, got {value!r}")
    return value


def _unit_float(value: object, name: str) -> float:
    number = float(value)  # type: ignore[arg-type]
    if not 0.0 < number < 1.0:
        raise ValueError(f"{name} must be in (0, 1), got {value!r}")
    return number


# --------------------------------------------------------------------------- the learned model
class RerankerModel:
    """A tiny pointwise-logistic ranker: a torch MLP at fit, a **numpy** forward pass at serve.

    The learned ordering key of :func:`rerank`. ``fit`` standardises the (masked) feature columns,
    trains ``17->hidden->1`` (ReLU) — or a single ``Linear`` when ``linear=True`` — under
    :class:`torch.nn.BCEWithLogitsLoss` with Adam, then stores the weights as numpy so ``score``
    needs no torch. Deterministic under ``seed`` (the Unit-8 save/restore determinism trio).
    """

    def __init__(
        self,
        *,
        hidden: int = 32,
        epochs: int = 30,
        learning_rate: float = 1e-2,
        batch_size: int = 512,
        weight_decay: float = 1e-5,
        seed: int = 0,
        linear: bool = False,
    ) -> None:
        self.hidden = _positive_int(hidden, "hidden")
        self.epochs = _positive_int(epochs, "epochs")
        self.learning_rate = float(learning_rate)
        self.batch_size = _positive_int(batch_size, "batch_size")
        self.weight_decay = float(weight_decay)
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise TypeError(f"seed must be an int, got {seed!r}")
        self.seed = seed
        self.linear = bool(linear)
        self.mask: np.ndarray | None = None
        self.mu: np.ndarray | None = None
        self.sd: np.ndarray | None = None
        self.weights: list[np.ndarray] = []

    def fit(self, X: np.ndarray, y: np.ndarray, *, feature_mask: np.ndarray | None = None) -> RerankerModel:
        """Train on standardised features ``X`` with binary labels ``y`` (torch, imported here)."""
        import torch  # LAZY: torch is needed only to train; score/state stay torch-free numpy.

        X = np.asarray(X, dtype=np.float32)
        y = np.asarray(y, dtype=np.float32)
        self.mask = (
            np.ones(X.shape[1], dtype=bool) if feature_mask is None else np.asarray(feature_mask, dtype=bool)
        )
        Xm = X[:, self.mask]
        self.mu = Xm.mean(axis=0)
        self.sd = Xm.std(axis=0) + 1e-6
        Xn = (Xm - self.mu) / self.sd

        # Save the PROCESS-GLOBAL determinism knobs and restore them when fit returns (Unit 8).
        prev_deterministic = torch.are_deterministic_algorithms_enabled()
        prev_threads = torch.get_num_threads()
        try:
            torch.use_deterministic_algorithms(True)
            torch.set_num_threads(1)
            torch.manual_seed(self.seed)
            if self.linear:
                net = torch.nn.Linear(Xn.shape[1], 1)
            else:
                net = torch.nn.Sequential(
                    torch.nn.Linear(Xn.shape[1], self.hidden),
                    torch.nn.ReLU(),
                    torch.nn.Linear(self.hidden, 1),
                )
            optimizer = torch.optim.Adam(
                net.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay
            )
            loss_fn = torch.nn.BCEWithLogitsLoss()
            Xt = torch.tensor(Xn, dtype=torch.float32)
            yt = torch.tensor(y, dtype=torch.float32).unsqueeze(1)
            generator = torch.Generator().manual_seed(self.seed)
            n = Xt.shape[0]
            for _ in range(self.epochs):
                perm = torch.randperm(n, generator=generator)
                for start in range(0, n, self.batch_size):
                    idx = perm[start : start + self.batch_size]
                    optimizer.zero_grad()
                    loss = loss_fn(net(Xt[idx]), yt[idx])
                    loss.backward()
                    optimizer.step()
            self.weights = [p.detach().numpy().astype(np.float32).copy() for p in net.parameters()]
        finally:
            torch.use_deterministic_algorithms(prev_deterministic)
            torch.set_num_threads(prev_threads)
        return self

    def score(self, X: np.ndarray) -> np.ndarray:
        """The learned ordering key for each row of ``X`` — a numpy forward pass (no torch)."""
        if self.mu is None or self.sd is None or self.mask is None or not self.weights:
            raise RuntimeError("RerankerModel.score before fit/load")
        Xn = (np.asarray(X, dtype=np.float32)[:, self.mask] - self.mu) / self.sd
        if self.linear:
            weight, bias = self.weights
            return (Xn @ weight.T + bias).ravel()
        weight1, bias1, weight2, bias2 = self.weights
        hidden = np.maximum(Xn @ weight1.T + bias1, 0.0)
        return (hidden @ weight2.T + bias2).ravel()

    def state(self) -> dict[str, Any]:
        """A torch-free numpy snapshot of the trained model (for the path's artifact)."""
        if self.mu is None or self.sd is None or self.mask is None or not self.weights:
            raise RuntimeError("RerankerModel.state before fit/load")
        return {
            "linear": self.linear,
            "mask": self.mask.copy(),
            "mu": self.mu.copy(),
            "sd": self.sd.copy(),
            "weights": [w.copy() for w in self.weights],
            "params": {
                "hidden": self.hidden,
                "epochs": self.epochs,
                "learning_rate": self.learning_rate,
                "batch_size": self.batch_size,
                "weight_decay": self.weight_decay,
                "seed": self.seed,
            },
        }

    @classmethod
    def from_state(cls, state: Mapping[str, Any]) -> RerankerModel:
        """Rebuild a model from :meth:`state` (numpy only — never imports torch)."""
        params = dict(state.get("params", {}))
        model = cls(linear=bool(state["linear"]), **{k: params[k] for k in ("seed",) if k in params})
        for key in ("hidden", "epochs", "batch_size"):
            if key in params:
                setattr(model, key, int(params[key]))
        for key in ("learning_rate", "weight_decay"):
            if key in params:
                setattr(model, key, float(params[key]))
        # Copy (never alias) so a later mutation of the artifact dict cannot reach into the model.
        model.mask = np.array(state["mask"], dtype=bool)
        model.mu = np.array(state["mu"], dtype=np.float32)
        model.sd = np.array(state["sd"], dtype=np.float32)
        model.weights = [np.array(w, dtype=np.float32) for w in state["weights"]]
        return model


def rerank(
    items: Sequence[int],
    features: np.ndarray,
    model: RerankerModel,
    *,
    k: int,
    seen: Iterable[int] = (),
    provenance: str = "reranker",
) -> list[Candidate]:
    """The authoritative learned ordering key: score ``items`` by ``model`` and take the top ``k``.

    ``features`` is the per-candidate feature matrix aligned with ``items``. Returns the top ``k``
    :class:`~bookrec.protocol.Candidate` after dropping ``seen`` — the drop-in replacement for the
    score-order key of :func:`~bookrec.rank.rank`, now *learned*. Deterministic (score desc, id asc).
    """
    scores = model.score(features)
    candidates = [Candidate(int(i), float(s), provenance) for i, s in zip(items, scores)]
    return rank(candidates, n=k, exclude=seen)


# --------------------------------------------------------------- feature assembly (phase-aware)
def split_profile_labels(
    interactions: Iterable[Mapping[str, Any]], holdout_frac: float = 0.25
) -> tuple[dict[int, set[int]], dict[int, set[int]]]:
    """Per reader, split train positives **time-ordered** into a 75% profile + 25% reranker labels.

    The latest ``holdout_frac`` (at least 1) of a reader's train positives — ordered by
    ``(timestamp, item_id)`` for determinism — become the reranker's positive **labels**; the earlier
    rest is the retrieval **profile** (the ``seen`` set the feature-paths are fit on and the content
    statistics are computed from). A reader with fewer than 2 train positives cannot be split, so it
    keeps all of them as profile and supplies **no** label (it never trains the reranker). Only
    ``split == "train"`` and ``label == 1`` rows count; every row needs a ``timestamp``.
    """
    positives: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for row in interactions:
        if row["split"] != "train" or int(row["label"]) != 1:
            continue
        positives[int(row["reader_id"])].append((int(row["timestamp"]), int(row["item_id"])))
    profile: dict[int, set[int]] = {}
    labels: dict[int, set[int]] = {}
    for reader, stamped in positives.items():
        stamped.sort()
        ordered = [item for _, item in stamped]
        if len(ordered) < 2:
            profile[reader] = set(ordered)
            labels[reader] = set()
            continue
        n_hold = max(1, round(len(ordered) * holdout_frac))
        profile[reader] = set(ordered[:-n_hold])
        labels[reader] = set(ordered[-n_hold:])
    return profile, labels


def _train_positive_counts(
    interactions: Iterable[Mapping[str, Any]], keep: Mapping[int, set[int]] | None = None
) -> dict[int, int]:
    """``{item_id: train-positive count}``; when ``keep`` is given, only that reader's kept items count.

    ``keep=None`` counts every train positive in the given rows — the serving-time statistic over the
    full train, and (when the rows are the label-item-excluded *profile* rows) the leakage-safe
    training count. ``keep`` restricts counting to each reader's kept (profile) items by
    item-membership; note this canNOT exclude the held-out *event* of a repeat-read item that sits in
    both the profile and the label set, so the training count is taken over label-item-excluded rows
    (``keep=None``) rather than by profile membership. ``keep`` is retained for illustrating that
    contrast.
    """
    counts: dict[int, int] = defaultdict(int)
    for row in interactions:
        if row["split"] != "train" or int(row["label"]) != 1:
            continue
        reader = int(row["reader_id"])
        item = int(row["item_id"])
        if keep is not None and item not in keep.get(reader, ()):  # held-out label item -> excluded
            continue
        counts[item] += 1
    return dict(counts)


class NeuralRerankerPath(BaseRetrievalPath):
    """A learned second-stage reranker over the merged retrieval pool (registers as ``reranker-v1``).

    Construction supplies the already-fit **serving** paths (``paths``), a ``path_factory`` that
    refits those paths on a given row subset (used **once**, on the 75% profile, to build leakage-safe
    *training* features), and the ``catalog_books`` for content lookups. :meth:`fit` builds the
    time-ordered holdout, assembles the training feature matrix from the profile-fit paths + profile
    statistics, trains a :class:`RerankerModel`, and stores the full-train serving statistics.
    :meth:`retrieve` builds each reader's pool from the **serving** paths, scores it with the learned
    numpy model, and returns the top ``k`` unseen books. ``load`` / ``artifact`` persist the numpy
    model + feature spec + serving statistics (torch-free); the paths and catalog are the
    construction-provided components (as a hybrid owns only its fusion state).

    The ``path_factory`` IS a real one-time refit on the profile split — not a reuse of the serving
    paths. Set ``leaky=True`` to reproduce the **teaching anti-pattern**: train on the serving
    (full-fit) paths + full-train counts, so the paths have memorized the label items and the ranker
    learns inflated in-train scores that validation never shows — it tanks (the measured leak).
    """

    def __init__(
        self,
        paths: Mapping[str, Any],
        path_factory: Callable[[list[dict[str, Any]]], Mapping[str, Any]],
        catalog_books: Mapping[int, Any],
        *,
        pool: int = 50,
        holdout_frac: float = 0.25,
        hidden: int = 32,
        epochs: int = 30,
        learning_rate: float = 1e-2,
        batch_size: int = 512,
        n_negatives: int = 10,
        weight_decay: float = 1e-5,
        seed: int = 0,
        linear: bool = False,
        feature_families: Sequence[str] = FEATURE_FAMILIES,
        leaky: bool = False,
        path_names: Sequence[str] = DEFAULT_PATH_NAMES,
        name: str = "reranker",
        version: str = "1",
    ) -> None:
        super().__init__(name=name, version=version)
        self._path_names = tuple(path_names)
        missing = [p for p in self._path_names if p not in paths]
        if missing:
            raise ValueError(f"paths is missing the serving path(s) {missing}; needs {self._path_names}")
        self._paths = dict(paths)
        if not callable(path_factory):
            raise TypeError("path_factory must be callable: rows -> {name: fitted RetrievalPath}")
        self._path_factory = path_factory
        self.pool = _positive_int(pool, "pool")
        self.holdout_frac = _unit_float(holdout_frac, "holdout_frac")
        self.hidden = _positive_int(hidden, "hidden")
        self.epochs = _positive_int(epochs, "epochs")
        self.learning_rate = float(learning_rate)
        self.batch_size = _positive_int(batch_size, "batch_size")
        self.n_negatives = _positive_int(n_negatives, "n_negatives")
        self.weight_decay = float(weight_decay)
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise TypeError(f"seed must be an int, got {seed!r}")
        self.seed = seed
        self.linear = bool(linear)
        self._feature_mask = family_mask(feature_families, self._path_names)
        self._feature_families = tuple(feature_families)
        self.leaky = bool(leaky)
        self._feature_names = feature_names(self._path_names)
        self._build_content_lookups(catalog_books)
        # Fitted state (set by fit/load):
        self._model: RerankerModel | None = None
        self._counts: dict[int, int] = {}
        self._max_log_pop: float = 1.0
        self._known_readers: set[int] = set()

    # ----------------------------------------------------------------- content lookups (catalog)
    def _build_content_lookups(self, catalog_books: Mapping[int, Any]) -> None:
        genres_of: dict[int, set[str]] = {}
        author_of: dict[int, str] = {}
        for item_id, book in catalog_books.items():
            fields = getattr(book, "fields", {})
            raw = fields.get("genres", "")
            genres_of[int(item_id)] = {g for g in raw.split(";") if g}
            author_of[int(item_id)] = fields.get("author_id", "")
        all_genres = sorted({g for gs in genres_of.values() for g in gs})
        gidx = {g: j for j, g in enumerate(all_genres)}
        genre_vec = {
            item: np.array([1.0 if g in gs else 0.0 for g in all_genres], dtype=np.float32)
            for item, gs in genres_of.items()
        }
        self._genres_of = genres_of
        self._author_of = author_of
        self._all_genres = all_genres
        self._gidx = gidx
        self._genre_vec = genre_vec

    # ------------------------------------------------------------------------- feature assembly
    def _build_pool(self, paths: Mapping[str, Any], reader: int, seen: set[int]) -> dict[int, dict[str, float]]:
        """Merge the per-path top-``pool`` calibrated scores, kept APART per path (not summed)."""
        per_item: dict[int, dict[str, float]] = defaultdict(dict)
        context = {"seen": seen}
        for name in self._path_names:
            path = paths[name]
            for cand in path.calibrate(path.retrieve(reader, context, self.pool)):
                per_item[cand.item_id][name] = cand.score
        return per_item

    def _features(
        self, per_item: Mapping[int, Mapping[str, float]], history: set[int], counts: Mapping[int, int], max_log_pop: float
    ) -> tuple[list[int], np.ndarray]:
        """Build the 17-dim feature matrix for a reader's pool, using ``history``/``counts`` as the profile."""
        hist = [i for i in history if i in self._genre_vec]
        if hist:
            hist_genre = np.sum([self._genre_vec[i] for i in hist], axis=0)
            hist_genre_set: set[str] = set().union(*(self._genres_of[i] for i in hist))
        else:
            hist_genre = np.zeros(len(self._all_genres), dtype=np.float32)
            hist_genre_set = set()
        hist_authors: dict[str, int] = defaultdict(int)
        for i in hist:
            hist_authors[self._author_of[i]] += 1
        n_hist = max(len(hist), 1)
        hg_norm = float(np.linalg.norm(hist_genre)) or 1.0
        n_paths = len(self._path_names)

        items = sorted(per_item)
        matrix = np.zeros((len(items), len(self._feature_names)), dtype=np.float32)
        for row, item in enumerate(items):
            scored = per_item[item]
            for col, name in enumerate(self._path_names):
                if name in scored:
                    matrix[row, col] = scored[name]
                    matrix[row, n_paths + col] = 1.0
            matrix[row, 2 * n_paths] = len(scored) / n_paths
            genres = self._genres_of.get(item, set())
            matrix[row, 2 * n_paths + 1] = len(genres & hist_genre_set) / max(len(genres), 1)
            gvec = self._genre_vec.get(item)
            if gvec is None:
                gvec = np.zeros(len(self._all_genres), dtype=np.float32)
            matrix[row, 2 * n_paths + 2] = float(gvec @ hist_genre) / (hg_norm * (float(np.linalg.norm(gvec)) or 1.0))
            matrix[row, 2 * n_paths + 3] = hist_authors.get(self._author_of.get(item, ""), 0) / n_hist
            matrix[row, 2 * n_paths + 4] = np.log1p(counts.get(item, 0)) / max_log_pop
        return items, matrix

    # -------------------------------------------------------------------------------- training
    def assemble_training_matrix(
        self,
        interactions: Iterable[Mapping[str, Any]],
        *,
        train_paths: Mapping[str, Any] | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Build the leakage-safe ``(X, y)`` training matrix AND fix the serving statistics.

        Builds the per-reader time-ordered holdout; the feature-paths AND the popularity count come
        from the **profile rows that exclude every held-out-label-item occurrence** (via
        ``path_factory`` — or the serving paths + full counts when ``leaky``), so no held-out event
        enters any training input. The held-out 25% supplies only the positive labels. ``train_paths``
        may be passed to reuse an already-refit profile-path set (so a test / notebook refits the
        paths once); the ``log_pop`` count is recomputed from the label-item-excluded rows regardless.
        Side effect: records the FULL-train serving ``counts`` / ``max_log_pop`` / ``known_readers``
        used at :meth:`retrieve` time. Rows need a ``timestamp``. Pure given the fitted paths.
        """
        rows = list(interactions)
        profile, labels = split_profile_labels(rows, self.holdout_frac)
        self._known_readers = {reader for reader in profile}
        label_readers = sorted(r for r in labels if labels[r] and profile.get(r))
        if not label_readers:
            raise ValueError("NeuralRerankerPath.fit found no reader with a time-ordered train holdout")

        # Serving statistics: the FULL train history (counts) — used at retrieve time.
        self._counts = _train_positive_counts(rows)
        self._max_log_pop = float(np.log1p(max(self._counts.values()))) if self._counts else 1.0

        # TRAINING-time inputs: the 75% profile ONLY (leakage-safe), unless the leaky anti-pattern.
        if self.leaky:
            train_paths = self._paths  # memorized the label items (the leak)
            train_counts = self._counts
        else:
            # The label-item-excluded profile rows: EVERY occurrence of a held-out-label item is
            # dropped (not just the held-out event). A repeat-read item that lands in BOTH the
            # profile and label sets would keep its held-out event under a profile-membership count
            # (`keep=profile`), leaking it into log_pop; counting the already-event-filtered rows
            # (keep=None) drops it — and the feature-paths refit on the SAME rows, so the paths and
            # the popularity count share one leakage-safe training input. Built UNCONDITIONALLY so
            # log_pop is label-item-excluded even when a caller passes a pre-refit ``train_paths``.
            profile_rows = [
                row
                for row in rows
                if not (
                    row["split"] == "train"
                    and int(row["label"]) == 1
                    and int(row["item_id"]) in labels.get(int(row["reader_id"]), set())
                )
            ]
            if train_paths is None:
                train_paths = self._path_factory(profile_rows)
            missing = [p for p in self._path_names if p not in train_paths]
            if missing:
                raise ValueError(f"path_factory did not return the path(s) {missing}")
            train_counts = _train_positive_counts(profile_rows)
        train_max_log_pop = float(np.log1p(max(train_counts.values()))) if train_counts else 1.0

        rng = np.random.default_rng(self.seed)
        feature_blocks: list[np.ndarray] = []
        label_blocks: list[np.ndarray] = []
        for reader in label_readers:
            per_item = self._build_pool(train_paths, reader, profile[reader])
            if not per_item:
                continue
            items, matrix = self._features(per_item, profile[reader], train_counts, train_max_log_pop)
            y = np.array([1.0 if item in labels[reader] else 0.0 for item in items], dtype=np.float32)
            positive_idx = np.flatnonzero(y == 1.0)
            if positive_idx.size == 0:  # no held-out label landed in the pool
                continue
            negative_idx = np.flatnonzero(y == 0.0)
            take = min(negative_idx.size, self.n_negatives * positive_idx.size)
            if take:
                negative_idx = rng.choice(negative_idx, size=take, replace=False)
            else:
                negative_idx = negative_idx[:0]
            keep = np.concatenate([positive_idx, negative_idx])
            feature_blocks.append(matrix[keep])
            label_blocks.append(y[keep])
        if not feature_blocks:
            raise ValueError("NeuralRerankerPath.fit: no held-out label landed in any reader's pool")
        return np.concatenate(feature_blocks), np.concatenate(label_blocks)

    def fit(
        self,
        interactions: Iterable[Mapping[str, Any]],
        catalog: Any | None = None,
        *,
        train_paths: Mapping[str, Any] | None = None,
    ) -> NeuralRerankerPath:
        """Train the reranker leakage-safely from the interaction log (torch, lazy inside the model).

        Assembles the leakage-safe training matrix (:meth:`assemble_training_matrix`) and trains a
        :class:`RerankerModel` on it. ``catalog`` is accepted for protocol substitutability (the
        content lookups come from the construction ``catalog_books``); ``train_paths`` optionally
        reuses an already-refit profile-path set. Raises on an empty fit.
        """
        X, y = self.assemble_training_matrix(interactions, train_paths=train_paths)
        model = RerankerModel(
            hidden=self.hidden,
            epochs=self.epochs,
            learning_rate=self.learning_rate,
            batch_size=self.batch_size,
            weight_decay=self.weight_decay,
            seed=self.seed,
            linear=self.linear,
        ).fit(X, y, feature_mask=self._feature_mask)
        return self.set_model(model)

    def set_model(self, model: RerankerModel) -> NeuralRerankerPath:
        """Install a trained :class:`RerankerModel` as the ordering key (keeping the serving stats).

        Lets a test or notebook assemble the training matrix **once** and swap in model variants
        (linear, a feature ablation, a different seed) without re-assembling features or re-fitting
        the paths. The serving statistics must already be fixed (via
        :meth:`assemble_training_matrix`). Returns ``self``.
        """
        if not self._known_readers:
            raise RuntimeError("set_model before assemble_training_matrix fixed the serving statistics")
        self._model = model
        self.linear = model.linear
        self._fitted = True
        return self

    # --------------------------------------------------------------------------------- serving
    def retrieve(self, query: Any, context: Any, k: int) -> list[Candidate]:
        """Top ``k`` unseen books: build the reader's pool from the serving paths, learned-score it.

        The pool is the union of the serving paths' top-``pool`` calibrated candidates; the content /
        popularity features use the reader's **full-train** ``seen`` history + the stored serving
        counts; the learned numpy model scores each candidate and :func:`rerank` drops ``seen`` and
        keeps the top ``k``. An unknown reader (no train positive at fit) returns ``[]``.
        """
        if self._model is None:
            raise RuntimeError("NeuralRerankerPath.retrieve before fit/load")
        if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
            raise ValueError(f"k must be a positive int, got {k!r}")
        try:
            reader_id = int(query)
        except (TypeError, ValueError):
            return []
        if reader_id not in self._known_readers:  # unknown / cold reader -> no recommendation
            return []
        seen = set(context.get("seen", ())) if isinstance(context, Mapping) else set()
        per_item = self._build_pool(self._paths, reader_id, seen)
        if not per_item:
            return []
        items, matrix = self._features(per_item, seen, self._counts, self._max_log_pop)
        return rerank(items, matrix, self._model, k=k, seen=seen, provenance=self.name)

    # ----------------------------------------------------------------------------- persistence
    def load(self, artifact: Mapping[str, Any]) -> NeuralRerankerPath:
        """Restore the numpy model + feature spec + serving statistics from :meth:`artifact`.

        The serving paths and catalog lookups are the construction-provided components (as a hybrid
        owns only its fusion state), so a loaded reranker over the same paths retrieves identically.
        Numpy only — never imports torch.
        """
        state = dict(artifact)
        self._model = RerankerModel.from_state(state["model"])
        self._feature_names = list(state.get("feature_names", self._feature_names))
        self._path_names = tuple(state.get("path_names", self._path_names))
        self._counts = {int(i): int(c) for i, c in dict(state.get("counts", {})).items()}
        self._max_log_pop = float(state.get("max_log_pop", 1.0)) or 1.0
        self._known_readers = {int(r) for r in state.get("known_readers", ())}
        params = dict(state.get("params", {}))
        for key in ("pool", "n_negatives"):
            if key in params:
                setattr(self, key, int(params[key]))
        if "holdout_frac" in params:
            self.holdout_frac = float(params["holdout_frac"])
        if "leaky" in params:
            self.leaky = bool(params["leaky"])
        self.linear = self._model.linear
        self._feature_mask = (
            np.asarray(self._model.mask, dtype=bool) if self._model.mask is not None else self._feature_mask
        )
        self._fitted = True
        return self

    def artifact(self) -> dict[str, Any]:
        """The fitted state this path owns and versions: the numpy model + feature spec + statistics."""
        if self._model is None:
            raise RuntimeError("NeuralRerankerPath.artifact before fit/load")
        return {
            "model": self._model.state(),
            "feature_names": list(self._feature_names),
            "path_names": list(self._path_names),
            "counts": {int(i): int(c) for i, c in self._counts.items()},
            "max_log_pop": self._max_log_pop,
            "known_readers": sorted(self._known_readers),
            "params": {
                "pool": self.pool,
                "holdout_frac": self.holdout_frac,
                "n_negatives": self.n_negatives,
                "leaky": self.leaky,
            },
        }

    @property
    def model(self) -> RerankerModel:
        """The learned ranking model (the authoritative ordering key)."""
        if self._model is None:
            raise RuntimeError("NeuralRerankerPath.model before fit/load")
        return self._model

    @property
    def feature_spec(self) -> list[str]:
        """The persisted feature ordering (names), so a stored vector is interpretable."""
        return list(self._feature_names)
