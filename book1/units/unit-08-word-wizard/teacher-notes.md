# Teacher Notes — Unit 08: Word Wizard

## Goals

Students leave able to use a DICTIONARY as a lookup table that pairs each key with a value — build
one with `{...}`, read it with `[]` and the safe `.get()`, add/update with `d[key] = value`, test
membership with `in`, and walk it with `.items()` — and to assemble these into a translation
wizard and a word-frequency counter. This is the first unit where data is paired (a key remembers
its value), not just listed. Success looks like: every student builds a phrasebook that translates
a word and a counter that reports how many times each word appears.

## Pacing

Budget: three lessons of 60–90 minutes. Each concept is a short **worked-example ladder** (minimal → one step up → real use, with a *Notice* per rung); the lesson-count is advisory. This unit teaches exactly two dict methods — `.get(key, default)` and `.items()` — and no others.

- **Lesson 1 — a dictionary pairs keys with values (dict-literal, dict-access) (60–90 min).**
  Open on the hook: a bilingual phrasebook — how would a program look a word up instantly?
  20 min: the dict-literal ladder (one pair → a few → the phrasebook) and the access ladder (`d["hello"]` read → `d["bird"] = "pajaro"` add → `.get("fish", "???")` safe miss).
  15 min: the KeyError bug (`translations["fish"]`) — read the traceback and name why `.get` exists. Mention cleaning a messy search with `raw.strip().lower()`.
  60-MINUTE CUT: teach ladder rungs 1–2; leave the last rung as a "try it".
- **Lesson 2 — walk the phrasebook (dict-loop; translate) (60–90 min).**
  Open on the thread: today we walk the whole phrasebook.
  20 min: the dict-loop ladder (`for word in d` keys → `for k, v in d.items()` pairs → a `translate` helper looping a whole list through `.get`).
  Rest: translate-a-list exercises.
- **Lesson 3 — count the word log (60–90 min).**
  20 min: count repeats with one loop (`if word in counts` → grow or start at 1); print each pair with `.items()` and `word + " => " + str(count)`; find the most common with a best-so-far loop.
  Rest: trade word logs and count each other's; discuss why `counts` must reset to `{}` before a re-count.

## Common mistakes

- Reaching for `translations["fish"]` when a key might be missing — that raises a KeyError. Use
  `translations.get("fish", "???")` for a safe default. This is the unit's key habit.
- Counting by looping over the DICTIONARY instead of the word LIST — the counter must iterate
  `words` (the raw log), building `counts` as it goes.
- Forgetting the `else: counts[word] = 1` first-sighting case — a brand-new word has no count to
  add 1 to yet.
- Overwriting a value by assigning to a key that already exists (`d["cat"] = "kitten"` replaces
  `"gato"`) — sometimes intended, sometimes a surprise; name it.
- After appending a new word and re-counting, forgetting to RESET `counts = {}` first — the old
  counts still sit in the dict and everything doubles.
- Case/space mismatch on lookups — `"Cat "` will not match the key `"cat"` unless you
  `.strip().lower()` first.

## Discussion prompts

- A list remembers an ORDER of values; a dictionary remembers a PAIRING. When does each fit better
  (a leaderboard vs a phrasebook)?
- Why is `.get()` with a default safer than `[]`? When would you still want `[]` to crash?
- The counter uses the word as the key. What other things could we count this way (letters, votes,
  emoji reactions)?

## Differentiation

- Strugglers: give the phrasebook dict pre-built and have them only look words up with `.get()` and
  test membership with `in`; a working translator is a satisfying win on its own.
- Fast finishers: the Challenge exercises — reverse-lookup (find the English word for a given
  translation) and merge-two-phrasebooks. Counting the letters in a single word (each letter a key)
  is a good no-new-concepts stretch.
- Middle tier: the grow-the-log exercise (append a word, reset, re-count) before the Challenges.
