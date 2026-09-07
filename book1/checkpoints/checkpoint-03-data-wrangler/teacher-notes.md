# Teacher Notes — Checkpoint 03: Data Wrangler

## Goals

This checkpoint confirms that students can WRANGLE the term's three data tools on their own:
string surgery (index, slice, clean with methods, test membership — Unit 06), lists (build, index,
append, loop, measure with `len`/`max`/`min`, rank with `.sort()` — Unit 07), and dictionaries
(build, look up with `[]`/`.get`, walk with `.items()`, count with the word-frequency pattern —
Unit 08). It also checks the habit of reaching for `.get()` instead of a crashing `[]` lookup.
Nothing new is introduced; every question uses only skills taught in Units 06–08.

## Pacing

Budget: 35–40 minutes (half a lesson). The checkpoint has 8 self-contained questions — each
restates its own data, so students may attempt them in any order and cells run correctly
top-to-bottom. Q4 (loop + `len`/`max`/`min` + accumulated total) and Q7 (build a counter
dictionary from scratch, then walk it with `.items()`) are the two multi-step write-from-scratch
tasks; budget the most time there. Remind students to run cells top-to-bottom and that each
question stands alone.

## Common mistakes

- Off-by-one on slice bounds: `word[2:5]` is characters 2, 3, 4 (not 5).
- Expecting `.sort()` to hand back a sorted list — it returns `None` and rearranges in place; use
  the list variable afterward.
- Forgetting `reverse=True`, so "top three" comes out lowest-first.
- Reaching for `prices["fig"]` on a missing key (a KeyError) instead of `prices.get("fig", 0)` —
  this is exactly what Q8 checks.
- In the Q7 counter, forgetting the `else: counts[word] = 1` first-sighting branch, or counting by
  looping over a dictionary instead of the given word list.
- Off-by-one on the numbered/indexed output (index 0 is the first item).

## Discussion prompts

- When is a list the right tool and when is a dictionary? (Order-of-values vs paired lookups.)
- Why is `.get(key, default)` safer than `[key]`? When might you still want `[key]` to crash?
- The word counter uses each word as a key. What else could you count this way?

## Differentiation

- A struggling student can earn solid credit on Q1–Q4 and Q6 alone; Q5 (sort + top three) and Q8
  (fix the KeyError) are the natural skip-if-stuck questions.
- A fast finisher can be asked to extend Q7 to also print the most common word (a running-best
  loop over `counts.items()`) — no new concepts.

## Grading

40 points total, 5 points per question. Full credit = correct, runnable code using only the
taught tools; partial credit as noted.

- **Q1 — string surgery (5):** first `word[0]`, last `word[-1]`, slice `word[2:5]`, reverse
  `word[::-1]`, each printed. 1 pt per correct piece + 1 for an f-string that shows them.
  Partial: `[::-1]` reverse or the slice bounds are the usual slips.
- **Q2 — clean & search (5):** `.strip().lower()` chain (2), `.replace(",", "")` (1), membership
  test printing True/False (2). Partial: cleaning without `.replace`, or printing the phrase
  instead of the True/False result.
- **Q3 — build a list (5):** literal (1), `.append(100)` (2), first + last via `[0]`/`[-1]` (2).
- **Q4 — measure a list (5):** loop printing each (1), `len`/`max`/`min` (1 each), accumulated
  `total == 355` via a LOOP (1). The total point requires the accumulator loop — `sum()` is NOT
  taught and does not earn it (it does not demonstrate the accumulator skill Q4 assesses).
- **Q5 — rank a list (5):** `.sort(reverse=True)` in place (2), top three by index 0/1/2 (3).
  Partial: sorting ascending and reading from the end, or expecting `.sort()` to return a list.
- **Q6 — price book (5):** `["pear"]` (1), `.get("fig", 0)` default (2), `in` membership print (1),
  3-way MEMBERSHIP branch (1). The branch must use `in` (the taught idiom — a `==` comparison is
  out of scope) and the `elif`/`else` must be VISIBLE in the code: with `plum` and `pear` both
  present the branches never run at runtime, so credit rests on the written structure, not output.
- **Q7 — count words (5):** `counts = {}` start (1), single loop with the `if`/`else`
  first-sighting counter (3), `.items()` walk printing each pair (1). `counts["cat"] == 3` is the
  key check. Partial: missing the `else` branch, or looping the dict instead of the word list.
- **Q8 — fix the bug (5):** replaces the crashing `prices["fig"]` with `prices.get("fig", 0)` so it
  prints safely (5). The statement already names the error (`KeyError: 'fig'`), so there is no
  separate point for restating it — the credit is the working `.get` fix.

A student scoring ≥ 28/40 (70%) is solid on the term's data tools; below that, revisit `.get()` vs
`[]` (Q6/Q8) and the word-counter pattern (Q7) first.
