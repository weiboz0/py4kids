# Errata — Unit 1: The recommendation problem and the scoreboard

## 2026-10-03 — recsys-004 generator regeneration

Plan recsys-004 redesigned the synthetic interaction generator (taste-aware exposure:
exposure proportional to `popularity^alpha * exp(beta * z-scored affinity)`), so the
regenerated `interactions.csv.gz` carries different values.
The `catalog.csv.gz` and `cold_partitions.json` are byte-identical to before, so every
catalog-derived pin is unchanged.

Updated figures (verified on the committed seed, k=10, cold readers excluded):

- `solutions.ipynb` Exercise 5 (reader 0, interaction-derived):
  `seen` set updated to the new train-positive items, and
  `relevant == {205, 518, 1249}` (was `{400}`).
- `lesson.ipynb` section 5 aggregate-floor note: "~368 readers" -> "~500 readers"
  (the positive rate rose ~0.23 -> ~0.33, so more readers have a scorable `val` positive).

Unchanged and re-verified (catalog byte-identical):

- The catalog-search id pins in `solutions.ipynb` Exercise 3
  (`[377, 489, 903, 1052, 1542]` and `[2, 7, 21, 40, 45]`).
- The `(5, 5)` first-five catalog-shape and book-0 schema assertions.
- The random-floor narrative: the floor is non-zero and every later retrieval path must beat it.
