# Teacher Notes — Unit 09: Strings

## Goals

Students leave able to treat a string as a sequence of characters: reach in with an index (`s[0]`, `s[-1]`),
take a slice (`s[a:b]`, stop excluded, open ends `s[:3]`/`s[3:]`, and the reversing slice `s[::-1]`),
measure it with `len(s)`, clean and test it with string methods (`upper`, `lower`, `strip`, `replace`, then
`find`, `startswith`/`endswith`, `isdigit`/`isalpha`, `join`, and `split` for walking the words of a line)
and membership (`ch in word`), build a NEW string one
character at a time (`transform-each`), and scan for something with a `linear-search`.
Success looks like: every student writes a function that inspects or rebuilds a string character by
character, and one that searches a string and returns a position (or -1).
Everything is in the function form from Unit 07 — define a function to a spec, checked on several inputs.

## Pacing

Budget: three lessons of 60–90 minutes.

- **Lesson 1 — Reach into a String (`string-index`, `string-slice`).** Positive indexing, then negative
  indexing (one rung each); `s[a:b]` with the stop excluded (the same rule as `range`); open-ended slices
  `word[:3]`/`word[3:]`; the reversing slice `word[::-1]` (the only step slice we use); `len(s)` — a recall
  from Unit 07. Hooks: badge initials, a substring.
- **Lesson 2 — Clean and Test (`string-methods`, `in-operator`).** One method per rung — `upper`, `lower`,
  `strip`, `replace` — then the chain; then `find`, `startswith`/`endswith`, `isdigit`/`isalpha` (note:
  `"-3".isdigit()` is False, so `isdigit` validation cannot accept negatives), `"-".join("abc")`, and
  `for word in line.split():` (split is only used to walk words — never subscript the list it returns);
  `ch in word` membership. Before the palindrome: an index loop `for i in range(len(w))` and ONE mirror
  pair. **Palindrome by index-walk** (`for i in range(len(s)//2): if s[i] != s[len(s)-1-i]: return False`);
  `s[::-1]` gives a one-line alternative students may use in the exercises. Vowel count by condition. A
  classify-the-character function (`elif` ladder). `no-exec` cells read a PIN and a word.
- **Lesson 3 — Transform and Search (`transform-each`, `linear-search`).** Build a new string with `+` in a
  loop (the lesson's `double_letters`; masking and alternating case are the exercises); a `linear-search`
  `position(text, ch)` returning the first index or -1; a char-frequency report as `count_char(text, ch)`
  plus a printed alphabet scan (a letter→count MAP needs a dictionary — Unit 11 — so we print each count
  instead of storing them). A `no-exec` cell reads a line and counts its words.

**60-minute cut:** Lesson 3's Caesar shift is the cut casualty (already a Challenge); keep the core
`transform-each` and `linear-search`.

## Exercises — core vs. More Practice vs. challenge

29 exercises, all in the function form.

- **Core (1–10):** Badge Line, Clean a Route Label, Palindrome Gate, Classify a Character, Mask the Vowels,
  First Matching Position (-1 when absent), Alphabet Scan Report, plus **Word Count** (8: `Words: 5`),
  **Initials** (9: `"grace brewster hopper"` → `GBH`) and **Valid PIN** (10: `4071` True, `40a1` and `407`
  False). Exercises 8–10 require a purpose comment.
- **More Practice (11–25)**, grouped by genre:
  - *Text:* Longest Word (`Longest: launch`), Sentence Palindrome ("Was it a car or a cat I saw" → True),
    File Type (`endswith`), Rotate Left (`nova` → `ovan`), Ends of a Word (`tel...ope`), Common Letters
    (`under`).
  - *Encoding & ciphers:* Run-Length Encoding (`aaabcc` → `a3b1c2`), Atbash Cipher (`abc xyz!` →
    `zyx cba!`; capitals pass through).
  - *Text layout & ASCII art:* Word Triangle (`C` / `CO` / `COD` / `CODE`), Center Text (`gnat` in 10 →
    three spaces each side), Letter Spacer (`R-O-B-O-T`), Word Box (the `CODE` frame).
  - *Validation & search:* Spam Check, First Vowel (7 / -1), Has a Digit.
- **Challenges (26–29, `stretch`):** Alternating Case, Caesar Shift, **Word Wrap** (width 10 →
  `the quick` / `brown fox` / `jumps`), **Safe Number** (`"42"` → 42, `"4x"` → -1).
The Caesar and Atbash ciphers use an **alphabet string** with `find` or a linear search — never `ord`/`chr`.

**Real versions.** Every exercise has a real program: it defines the function, reads the text (and any
number) with bare `input()`, and prints the same line.

## Common mistakes

- Off-by-one at the ends: `s[len(s)]` is out of range; the last character is `s[len(s)-1]` (or `s[-1]`).
- Comparing without case-folding (`"Anna"` fails a naive palindrome) — `lower()` first.
- Expecting a slice to include the stop index (`s[0:3]` is three characters, indices 0,1,2).
- Reaching for an untaught method (`index`, `count`) — use `find` or walk the string yourself.
- Subscripting the list from `split()` (`line.split()[0]`) — lists come in Unit 10; walk the words with
  `for word in line.split():`.
- `find` returns -1 when the text is absent — check before using the position.
- Center Text: the extra space goes on the right when the padding is odd.
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
- Fast finishers: the ciphers and layout exercises, then the Challenges (Word Wrap is the capstone); then
  extend `count_char` to be
  case-insensitive (`text.lower()` first) or to ignore a chosen punctuation mark via `replace`.
- Middle tier: extend the palindrome to also ignore punctuation (`replace("!", "")`/`replace(",", "")`
  before the walk), or count vowels per word rather than per string.

## Value plan (sample inputs)

Each exercise uses inputs distinct from the lesson examples and each other; the solution notebook asserts
several distinct cases per function.
- Ex1 `badge_line`: `("Mira","Stone","AX742Q")`, `("Leo","Park","ZZcat9")`, `("Nia","Young","12SUN")`.
- Ex2 `clean_route`: `"  north_gate "`, `"moon_base"`, `"  red_fox_2  "`.
- Ex3 `is_palindrome`: `"Taco cat"`, `"python"`, `"Level"`.
- Ex4 `classify_char`: `"U"`, `"m"`, `"7"`.
- Ex5 `mask_vowels`: `"Rocket"`, `"SKY"`, `"A-OK!"`.
- Ex6 `position`: `("banana","n")`, `("cocoa","o")`, `("planet","x")` (absent → -1).
- Ex7 `count_char`: `("pepper","p")`→3, `("pepper","z")`→0; `print_alphabet_scan("Bee")` prints the scan.
- Ex26 (stretch) `alternating_case`: `"python"`, `"moon base"`, `"A1b2!"`.
- Ex27 (stretch) `position("abcdefghijklmnopqrstuvwxyz","q")`→16; Caesar `shift`: `("Code 9!",2)`→`"eqfg 9!"`,
  `("XYZ",3)`→`"abc"` (wraparound), `("stay",0)`→`"stay"`.
- New exercises 8–29: fixtures as in the exercise statements (plan 082's tables), grep-distinct from shipped
  Book 1b content.

## More Practice ideas (design 006 D9 genres)

- **Encoding:** a "pig latin" function for one lowercase word.
- **Validation:** `is_valid_username(text)` — 3–10 characters, letters and digits only.
- **Text layout:** right-align a word in a width (the Center Text idea with all padding on the left).
