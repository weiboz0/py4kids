# Teacher Notes — Unit 08: Word Wizard

## Goals

Students leave able to use a DICTIONARY as a lookup table that pairs each key with a value — build
one with `{...}`, read it with `[]` and the safe `.get()`, add/update with `d[key] = value`, test
membership with `in`, and walk it with `.items()` — and to assemble these into a translation
wizard and a word-frequency counter. This is the first unit where data is paired (a key remembers
its value), not just listed. Success looks like: every student builds a phrasebook that translates
a word and a counter that reports how many times each word appears.

## Pacing

Budget: two lessons of 60–90 minutes.

- **Lesson 1 — a dictionary pairs keys with values (dict-literal, dict-access) (60–90 min).**
  Open on the hook: a tiny bilingual phrasebook — how would a program look a word up instantly?
  15 min: a dict pairs each word (key) with its translation (value) —
  `translations = {"hello": "hola", "cat": "gato", "dog": "perro"}`; look up `translations["hello"]`.
  10 min: add or change a pair with `translations["bird"] = "pajaro"`.
  15 min: words arrive messy, so CLEAN the search word first — `clean = raw_word.strip().lower()` —
  so `"  Hello "` still matches the key `"hello"`. This is case-insensitive matching; it reuses the
  string methods from Unit 06.
  10 min: membership — `print("cat" in translations)` shows a True/False value (a boolean).
  20 min: the SAFE lookup — `translations.get("fish", "???")` returns a default instead of crashing.
  Then the deliberate bug: `translations["fish"]` raises a KeyError — show it, read the traceback
  together, and name why `.get` exists.
  60-MINUTE CUT: trim the normalization beat (it returns whenever input is messy); build/lookup/
  `.get`/KeyError are the core.
- **Lesson 2 — count and translate with a loop (dict-loop) (60–90 min).**
  Open on the thread: yesterday we looked words up; today we count them and translate a whole list.
  The counter can OPEN this lesson if L1 ran long.
  10 min: walk a dict — `for word in translations:` (keys) and
  `for word, translation in translations.items():` (pairs).
  15 min: the word-FREQUENCY counter over a GIVEN list — `words = ["cat","dog","cat","bird","cat"]`,
  `counts = {}`, then one loop: `if word in counts: counts[word] = counts[word] + 1` else
  `counts[word] = 1`. The `else` handles a word's FIRST sighting (start it at 1); the `if` branch
  adds to a word already seen (the accumulator/running-total idea, now per key).
  15 min: print each `word => count` with `.items()`, and find the "most common word" by tracking
  a running best (`best_count = 0`, `if count > best_count: ...`).
  10 min: a `translate(word, dictionary)` helper returning `dictionary.get(word, "???")`.
  10 min: a "new word arrives" beat — `words.append("bird")` — then RESET `counts = {}` and
  re-count. Emphasize the reset: without it, the counts double.
  60-MINUTE CUT: skip the translate helper + most-common beat; the counter is the non-negotiable
  core.

Practices reappearance: `print`/`f-string` show every result; `string-methods` (`.strip().lower()`)
cleans the search word; `in-operator` tests membership and guards the counter; `arithmetic`/
`int-type`/`accumulator` are the count increment; `comparison` finds the most-common word;
`string-concat`/`type-conversion` build the `word => count` label; `elif-else` handles a word's
first sighting; `error-messages` is the KeyError beat; `list-literal`/`list-append`/`list-loop`
carry the word list; `def-function`/`parameters`/`return-value` build `translate`; `boolean` is the
membership print. `input` is practiced only in the `safe-lookup` exercise PROMPT — the executable
cells stay input-free so the notebooks run in class without waiting on typed input, and the
reference solution uses a fixed sample word. All of these return in units 09–10 and the capstone.

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
