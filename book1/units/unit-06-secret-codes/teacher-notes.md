# Teacher Notes — Unit 06: Secret Codes

## Goals

Students leave able to treat text as a sequence — index a character, slice a substring,
clean a string with methods, and test membership — and to build a working Caesar cipher
that encodes and decodes secret messages. This is the first unit where a string is
something you take apart and rebuild, not just print.
Success looks like: every student encodes a message their neighbour then decodes correctly.

## Pacing

Budget: three lessons of 60–90 minutes. Each concept is a short **worked-example ladder** (minimal → one step up → real cipher use, with a *Notice* per rung); the lesson-count is advisory. The unit teaches exactly four string methods — `.strip()`, `.lower()`, `.upper()`, `.replace()` — and reverse slicing `[::-1]` (no other method/step); the cipher loops use `for`/`range` and string `+`, all owned here.

- **Lesson 1 — string-index, string-slice, string-methods (60–90 min).**
  Open on the hook: the teacher shows an encoded note; the class tries to crack it.
  20 min: the index ladder (`word[0]` → more positions → `word[-1]` → index in a `for` loop).
  20 min: the slice ladder (`[1:4]` → `[:2]` → `[2:]` → the reverse slice `[::-1]`, a one-line reverse cipher!).
  25 min: the methods ladder (`.lower()` → `.upper()` → `.strip()` → `.replace()` → chained), PRINTing each result.
  In-class exercises: 1–3.
  60-MINUTE CUT: teach rungs 1–2 of each ladder; leave the last rung as a "try it".
- **Lesson 2 — the ATBASH decode + in-operator (60–90 min).**
  Open on the thread: crack the folded note.
  25 min: the ATBASH flip — scan the alphabet with `for position in range(26)` to find a letter's position, then take `letters[25 - position]`; this introduces the position-scan the Caesar cipher reuses.
  20 min: the `in` ladder (`"m" in letters` → a space/mark is False → inside a `for` loop to tell letters from marks).
  In-class exercises: 4, 5, 8, 9, and 11.
- **Lesson 3 — the Caesar encoder (60–90 min).**
  Open on the thread: yesterday we READ codes; today we WRITE one only a friend can crack.
  25 min: the CAESAR cipher as `encode(message, shift)` — lowercase first (the case contract), scan `range(26)`, `(position + shift) % 26`, rebuild with `result = result + new_letter`; `decode` shifts back by `26 - shift`.
  15 min: the deliberate wrap bug — forget `% 26` and watch `z` shift off the end; read the `IndexError` together.
  Rest: the trade-and-decode activity — pairs swap encoded messages and crack each other's.
  In-class exercises: 6, 7, and 10.
  60-MINUTE CUT: skip the wrap-bug demo (the fix-the-caesar exercise covers it); the encode/decode function is the non-negotiable core.

**Exercise split:** Exercises 1–11 are the in-class core, spread across the three lessons as
listed above. The notebook's **Challenge** section contains Challenges 1–2;
these stretch tasks are optional, and no core concept depends on completing them.

`error-messages` has a justified peripheral count exemption: Exercise 7 supplies one focused,
genuine authoring exercise with two run-read-fix rounds. Repeating traceback failures across three
separate core exercises would be artificial; the class instead spends its time building and testing
working ciphers.

Practices reappearance: print runs through every "show your result" step; input is used in
the typed-message and character exercises; variable/arithmetic/comparison/range-function are the
guts of the position scan and shift; two integer shift values are compared directly; f-string,
accumulator, if/elif/else, boolean values, nested loops, and loop counters all carry earlier learning
into the cipher work.

## Common mistakes

- Off-by-one on slice bounds (`word[1:4]` is characters 1,2,3 — not 4).
- Forgetting the `% 26` wrap, so shifting `z` runs past the alphabet (the planned Lesson-3
  bug — read the wrong output together).
- Trying to CHANGE a letter in place (`word[0] = "x"`) — strings can't be mutated; you
  REBUILD a new string with concatenation. Name this explicitly; it's the unit's key idea.
- Case mismatch in membership: `"A" in letters` is False because `letters` is lowercase —
  the case contract (`.lower()` first) exists precisely to avoid this.
- Skipping the alphabet scan and guessing a position; require the taught
  `for position in range(26)` pattern instead.

## Discussion prompts

- Why can't we just change a letter inside a word? What does "rebuild the string" mean?
- The reverse cipher is easy to crack; the Caesar is harder. What makes a code hard to break?
- If you didn't know the shift, how would you crack a Caesar message? (Seeds frequency ideas.)

## Differentiation

- Strugglers: give the Caesar `encode` as a fill-in-the-scan skeleton; the reverse and
  Atbash ciphers are complete, satisfying results on their own.
- Fast finishers: the Challenge exercises — a case-insensitive keyword check and a two-step
  cipher (reverse then shift). Cracking a message by trying all 25 shifts is a great extension
  (a loop over shifts — no new concepts).
- Middle tier: the fix-the-caesar debugging exercise before the Challenges.
