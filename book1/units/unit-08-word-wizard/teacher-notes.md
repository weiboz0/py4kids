# Teacher Notes — Unit 08: Word Wizard

## Goals

Students leave able to use a DICTIONARY as a lookup table that pairs each key with a value — build
one with `{...}`, read it with `[]` and the safe `.get()`, add/update with `d[key] = value`, test
membership with `in`, store that check as a boolean, and walk keys directly or pairs with `.items()` — and to assemble these into a translation
wizard and a word-frequency counter. This is the first unit where data is paired (a key remembers
its value), not just listed. Success looks like: every student builds a phrasebook that translates
a word and a counter that reports how many times each word appears, including text lines built with
`+` and `str()`.

## Pacing

Budget: three lessons of 60–90 minutes. Each concept is a short **worked-example ladder** (minimal → one step up → real use, with a *Notice* per rung); the lesson-count is advisory. This unit teaches exactly two dict methods — `.get(key, default)` and `.items()` — and no others.

- **Lesson 1 — a dictionary pairs keys with values (dict-literal, dict-access) (60–90 min).**
  Open on the hook: a bilingual phrasebook — how would a program look a word up instantly?
  20 min: the dict-literal ladder (one pair → a few → the phrasebook) and the access ladder (`d["hello"]` read → `d["bird"] = "pajaro"` add → `.get("fish", "???")` safe miss).
  10 min: review `in`, storing its result in a boolean variable, `if`/`else`, f-strings, `+`, and `str()` before students use them with dictionaries.
  15 min: show the actual KeyError traceback for `translations["fish"]`; students name the missing key before discussing why `.get` exists. Review cleaning a messy search with `raw.strip().lower()`.
  In class, complete Exercises 1–4, 8, and 11 only after their matching ladder or review beat.
  60-MINUTE CUT: teach ladder rungs 1–2; leave the last rung as a "try it".
- **Lesson 2 — walk the phrasebook (dict-loop; translate) (60–90 min).**
  Open on the thread: today we walk the whole phrasebook.
  20 min: the dict-loop ladder (`for word in d` keys → `for k, v in d.items()` pairs → a `translate` helper looping a whole list through `.get`). Review building a result list with `.append()` before asking students to collect translations.
  In class, complete Exercises 9–10 after this ladder.
  Assign Exercise 15 as a **linear-search** retrieval after the ladder: dictionary lookup by English key is instant, but finding an English key from a Spanish value requires checking values one by one and stopping when the match is found.
  Assign Exercise 16, **Keep only the long words**, after the result-list review: students retrieve
  the filter pattern by checking each word's `len(...)` against a threshold and appending only the
  passing words to a new list. The variation is words and lengths instead of scores and a score bar.
- **Lesson 3 — count the word log (60–90 min).**
  20 min: count repeats with one loop (`if word in counts` → grow or start at 1); review integer arithmetic, comparisons, stored booleans, and the accumulator pattern; print each pair with `.items()`; find the most common with a best-so-far loop.
  In class, complete Exercise 5 after the counting beat, then use Exercise 6 as a
  **find-extreme** retrieval: the scan must keep both `best_word` and `best_count`, with
  dictionary word/count pairs replacing Unit 07's parallel lists. Complete Exercise 7 after it.
  Rest: trade word logs and count each other's; discuss why `counts` must reset to `{}` before a re-count.

**In-class versus homework split:** Exercises 1–11 are the in-class path across the three lessons as allocated above.
The notebook's **More Practice** section, Exercises 12–16, is homework: Exercises 12–14 follow Lesson 3, and Exercises 15–16 follow Lesson 2's dictionary-loop and result-list work.
The set provides two varied `+`/`str()` reporting reps, a direct key-only dictionary loop, a reverse-lookup search that stops early, and a filter that keeps only the passing words in a new list.
Every concept has at least one in-class rep; homework adds fluency rather than introducing a concept.

**Why one traceback rep is enough here:** `error-messages` is peripheral in this unit; dictionaries drive Word Wizard, while traceback reading is practiced again in other units.

## Common mistakes

- Reaching for `translations["fish"]` when a key might be missing — that raises a KeyError. Use
  `translations.get("fish", "???")` for a safe default. This is the unit's key habit.
- Printing `word in translations` inline when the task asks for a stored boolean — assign the check
  to `known` first, then print and reuse `known`.
- Using an f-string in a `+`/`str()` practice task — build the requested pieces in order so students
  practice converting an integer before concatenation.
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
- Fast finishers: the Challenge exercises — merge-two-phrasebooks and flip-the-phrasebook.
  Counting the letters in a single word (each letter a key) is a good no-new-concepts stretch.
- Middle tier: the grow-the-log exercise (append a word, reset, re-count) before **More Practice** and
  the Challenges.
