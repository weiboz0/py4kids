# Errata — Unit 1: The recommendation problem and the scoreboard

## 2026-10-03 — recsys-004 generator regeneration

Plan recsys-004 redesigned the synthetic interaction generator (taste-aware exposure:
exposure proportional to `popularity^alpha * exp(beta * z-scored affinity)`), so the
regenerated `interactions.csv.gz` carries different values.
The `catalog.csv.gz` and `cold_partitions.json` are byte-identical to before, so every
catalog-derived pin is unchanged.

Updated figures (verified on the committed seed, k=10, cold readers excluded):

- `solutions.ipynb` Exercise 5 now uses reader 1 (the first ascending
  non-cold reader whose `val_positives - seen` is non-empty). Reader 0 is
  ineligible: its three val positives `{205, 518, 1249}` are all in its `seen`
  set, so its relevant set is empty and it is never scored. Reader 1 has
  `seen == {122, 304, 389, 403, 484, 529, 606, 607, 683, 823, 883, 989, 1296,
  1341, 1660, 1680, 1764, 1803}` and `val_positives == {195, 460, 823, 830}`;
  subtracting seen (823 is a re-read) gives `relevant == {195, 460, 830}`,
  consistent with the scoreboard contract (`relevant = val_positives - seen`).
- `lesson.ipynb` section 5 aggregate-floor note: "~368 readers" -> "~500 readers"
  (the positive rate rose ~0.23 -> ~0.33, so more readers have a scorable `val` positive).

Unchanged and re-verified (catalog byte-identical):

- The catalog-search id pins in `solutions.ipynb` Exercise 3
  (`[377, 489, 903, 1052, 1542]` and `[2, 7, 21, 40, 45]`).
- The `(5, 5)` first-five catalog-shape and book-0 schema assertions.
- The random-floor narrative: the floor is non-zero and every later retrieval path must beat it.
