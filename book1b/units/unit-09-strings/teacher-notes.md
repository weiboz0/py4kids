# Teacher Notes — Unit 09: Strings

## Goals

Students leave able to treat a string as a sequence of characters: reach in with an index (`s[0]`, `s[-1]`),
take a slice (`s[a:b]`, stop excluded), measure it with `len(s)`, clean and test it with the four taught
methods (`upper`, `lower`, `strip`, `replace`) and membership (`ch in word`), build a NEW string one
character at a time (`transform-each`), and scan for something with a `linear-search`.
Success looks like: every student writes a function that inspects or rebuilds a string character by
character, and one that searches a string and returns a position (or -1).
Everything is in the function form from Unit 07 — define a function to a spec, checked on several inputs.

## Pacing

Budget: three lessons of 60–90 minutes.

- **Lesson 1 — Reach into a String (`string-index`, `string-slice`).** `s[0]`/`s[-1]`; `s[a:b]` with the
  stop excluded (the same rule as `range`); `len(s)`. Hooks: badge initials, a substring.
- **Lesson 2 — Clean and Test (`string-methods`, `in-operator`).** `upper`/`lower` (case-fold before
  comparing), `strip` (trim input), `replace` (swap a substring); `ch in word` membership. **Palindrome by
  index-walk** (`for i in range(len(s)//2): if s[i] != s[len(s)-1-i]: return False`) — NOT `s[::-1]` (step
  slices are never taught). Vowel count by condition. A classify-the-character function (`elif` ladder).
- **Lesson 3 — Transform and Search (`transform-each`, `linear-search`).** Build a new string with `+` in a
  loop (`mask the vowels`, `alternating case`); a `linear-search` `position(text, ch)` returning the first
  index or -1; a char-frequency report as `count_char(text, ch)` plus a printed alphabet scan (a table needs
  a dictionary — Unit 11 — so we print instead of storing).

**60-minute cut:** Lesson 3's Caesar shift is the cut casualty (already a Challenge); keep the core
`transform-each` and `linear-search`.

## Exercises — core vs. extra vs. challenge

Core (1–7): Badge Line (index/slice), Clean a Route Label (methods), Palindrome Gate (index-walk),
Classify a Character (`elif` + membership), Mask the Vowels (`transform-each`), First Matching Position
(`linear-search`, -1 when absent), Alphabet Scan Report (`count_char` + printed scan).
Challenges (8–9, `stretch`): Alternating Case (transform-each); Caesar Shift (helper-first: `position` +
`shift`, lowercase, `(pos+k)%26`, non-letters pass through).
The Caesar cipher uses an **alphabet string** + linear-search + `%` — never `ord`/`chr` (character codes are
not taught).

## Common mistakes

- Off-by-one at the ends: `s[len(s)]` is out of range; the last character is `s[len(s)-1]` (or `s[-1]`).
- Comparing without case-folding (`"Anna"` fails a naive palindrome) — `lower()` first.
- Expecting a slice to include the stop index (`s[0:3]` is three characters, indices 0,1,2).
- Reaching for an untaught method (`split`, `find`, `index`, `count`) — only `upper`/`lower`/`strip`/`replace`
  are taught; search by walking the string yourself.
- `linear-search`: forgetting the `-1`/"not found" case, or returning after the loop instead of inside it.
- Caesar: using `ord`/`chr` (not taught) instead of the alphabet + `%`; forgetting to pass non-letters through.

## Discussion prompts

- How is `s[a:b]` like `range(a, b)`? Where does the "stop is excluded" rule show up again?
- Why does the palindrome check only need to walk to `len(s)//2`?
- When you search a string by hand, why return inside the loop rather than after it?
- The Caesar cipher never uses character codes — how does the alphabet string plus `%` do the same job?

## Differentiation

- Strugglers: Core 1–4 (index/slice, methods, palindrome, classify); give the loop header and have them fill
  the body.
- Fast finishers: the two Challenges (alternating case, Caesar), then extend `count_char` into a "which
  vowel is most common" (a `find-extreme`, previews Unit 10).
- Middle tier: rewrite the palindrome to also ignore spaces (a `replace(" ", "")` before the walk).

## Value plan (sample inputs)

Each exercise uses inputs distinct from the lesson examples and each other; the solution notebook asserts
several distinct cases per function.
- Ex1 `badge_line`: `("Mira","Stone","AX742Q")`, `("Leo","Park","ZZcat9")`, `("Nia","Young","12SUN")`.
- Ex2 `clean_route`: `"  north_gate "`, `"moon_base"`, `"  red_fox_2  "`.
- Ex3 `is_palindrome`: `"Taco cat"`, `"python"`, `"Level"`.
- Ex4 `classify_char`: `"U"`, `"m"`, `"7"`.
- Ex5 `mask_vowels`: `"Rocket"`, `"SKY"`, `"A-OK!"`.
- Ex6 `position`: `("banana","n")`, `("cocoa","o")`, `("planet","x")` (absent → -1).
- Ex7 `count_char`: `("pepper","p")` and further cases in the solution.
- Ex8 (stretch) `alternating_case`: `"python"`, `"moon base"`, `"A1b2!"`.
- Ex9 (stretch) Caesar `shift`: several `(message, k)` pairs with wraparound and non-letters, seeded by spec.
