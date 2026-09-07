# Teacher Notes — Unit 06: Secret Codes

## Goals

Students leave able to treat text as a sequence — index a character, slice a substring,
clean a string with methods, and test membership — and to build a working Caesar cipher
that encodes and decodes secret messages. This is the first unit where a string is
something you take apart and rebuild, not just print.
Success looks like: every student encodes a message their neighbour then decodes correctly.

## Pacing

Budget: two lessons of 60–90 minutes.

- **Lesson 1 — string-index, string-slice, string-methods (60–90 min).**
  Open on the hook: the teacher shows an encoded note; the class tries to crack it.
  20 min: text is a sequence — `word[0]`, `word[-1]`, slices `word[1:4]`, and the reverse
  slice `word[::-1]` (a one-line reverse cipher!).
  20 min: cleaning text — `.upper()`, `.lower()`, `.strip()`, `.replace()` — and PRINTing
  each result to see it.
  25 min: the ATBASH flip — scan the alphabet with `for position in range(26)` to find a
  letter's position, then take `letters[25 - position]`. This introduces the position-scan
  the Caesar cipher will reuse.
  60-MINUTE CUT: drop Atbash (it returns in Lesson 2's scan); index + slice + methods are core.
- **Lesson 2 — in-operator + the Caesar build (60–90 min).**
  Open on the thread: yesterday we READ codes; today we WRITE one only a friend can crack.
  15 min: membership — `if letter in letters` to leave spaces and punctuation untouched.
  30 min: the CAESAR cipher as `encode(message, shift)` — lowercase the message first (the
  case contract), scan `range(26)` for each letter's position, `(position + shift) % 26`,
  rebuild with `result = result + new_letter`; `decode` shifts back by `26 - shift`.
  15 min: the deliberate wrap bug — forget the `% 26` and watch `z` shift off the end; read
  the resulting error/wrong output together.

Practices reappearance: print runs through every "show your result" step; input is used in
the encode-my-typed-message exercise; variable/arithmetic/comparison/range-function are the
guts of the position scan and shift; int-type is the shift value; f-string/accumulator/
if-statement/loop-counter carry over from earlier units in the cipher loop. All reappear in
unit 07's high-score work and the capstone.

## Common mistakes

- Off-by-one on slice bounds (`word[1:4]` is characters 1,2,3 — not 4).
- Forgetting the `% 26` wrap, so shifting `z` runs past the alphabet (the planned Lesson-2
  bug — read the wrong output together).
- Trying to CHANGE a letter in place (`word[0] = "x"`) — strings can't be mutated; you
  REBUILD a new string with concatenation. Name this explicitly; it's the unit's key idea.
- Case mismatch in membership: `"A" in letters` is False because `letters` is lowercase —
  the case contract (`.lower()` first) exists precisely to avoid this.
- Reaching for `.index()` or `len()` — neither is taught yet; the alphabet scan
  (`for position in range(26)`) is the tool we have.

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
