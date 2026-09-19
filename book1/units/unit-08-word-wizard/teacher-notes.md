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
  In class, complete Exercises 1–4, 6, and 8 only after their matching ladder or review beat.
  60-MINUTE CUT: teach ladder rungs 1–2; leave the last rung as a "try it".
- **Lesson 2 — walk the phrasebook (dict-loop; translate) (60–90 min).**
  Open on the thread: today we walk the whole phrasebook.
  20 min: the dict-loop ladder (`for word in d` keys → `for k, v in d.items()` pairs → a `translate` helper looping a whole list through `.get`). Review building a result list with `.append()` before asking students to collect translations.
  In class, complete Exercise 7 after this ladder. The **transform-each**, **linear-search**, and
  **filter** patterns are named in class here, but their exercises now live in the closing Algorithm
  Extension and run as time permits: Exercise 14 (Translate a List, transform-each); Exercise 15
  (Reverse Lookup — **linear-search**: finding an English key from a Spanish value checks values one by
  one and stops at the match); and Exercise 16 (Keep only the long words — **filter**: check each word's
  `len(...)` against a threshold and append only the passing words to a new list; words and lengths
  instead of scores and a score bar).
- **Lesson 3 — count the word log (60–90 min).**
  20 min: count repeats with one loop (`if word in counts` → grow or start at 1); review integer arithmetic, comparisons, stored booleans, and the accumulator pattern; print each pair with `.items()`; find the most common with a best-so-far loop.
  The **count-by-condition** (tally-by-key) and **find-extreme** patterns are named in class here; their
  exercises now live in the Algorithm Extension and run as time permits: Exercise 12 (Count the Words) and
  Exercise 13 (Most Common Word — the scan keeps both `best_word` and `best_count`, dictionary word/count
  pairs replacing Unit 07's parallel lists). Complete Exercise 5 (Grow the Log) in class after the
  counting beat.
  Rest: trade word logs and count each other's; discuss why `counts` must reset to `{}` before a re-count.

**In-class versus homework split:** Exercises 1–8 are the in-class path across the three lessons as
allocated above; the labelled **More Practice** Exercises 9–11 (two `+`/`str()` reporting reps and a
direct key-only dictionary loop) are homework after Lesson 3.
The **Algorithm Extension** (Exercises 12–21) is optional enrichment: the five relocated pattern
exercises (count-by-condition Ex12, find-extreme Ex13, transform-each Ex14, linear-search Ex15, filter
Ex16) plus five new unmarked drills (Ex17–21). Only the naming beats ride the lessons; the exercises run
as time permits (see the Algorithm Extension section below).
Every concept has at least one authored rep across the unit; the extension adds fluency rather than
introducing a concept.

## Algorithm Extension (enrichment)

The unit's algorithm track sits in a labelled **`## Algorithm Extension`** section at the end of the
notebook (design 002 v8). It gathers the five pattern reps — count-by-condition/tally-by-key (Ex 12),
find-extreme (Ex 13), transform-each (Ex 14), linear-search (Ex 15, reverse lookup), filter-into-list
(Ex 16, keep the long words) — then five new **unmarked** drills (Ex 17–21). The pattern-naming beats are
read in class; every exercise here (Ex 12–21) is routed as time-permitting / homework / differentiation.

- **Ex 17** total-of-tally (an accumulator over dict values → 6) — an **unmarked** sum rep; u08 stays
  running-total-free per design §7, so this is a plain accumulator, not a tagged locus.
- **Ex 18** rarest word (argmin over pairs, seed from the first → "fox"/1), **Ex 19** known vs unknown
  (two counters over a word list against the dictionary → 2 / 1).
- **Ex 20 & Ex 21** are the **same words (owl, dragon, cat, wizard, sun; lengths 3,6,3,6,3),
  opposite-boundary** pair ÷ 12: Ex 20 *checks before adding* (an **exact hit** — 3 words fit for total
  12, which is why the rule is `<=` not `<`); Ex 21 *adds then checks* (4 words, total 18, tipping word
  "wizard"). Run them back-to-back.

These are extra reps of patterns students have met; being a broad-core unit, they are routed to
More-Practice/homework so the in-class core stays the phrasebook + counter build.

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
