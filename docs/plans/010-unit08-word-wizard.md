# Plan 010 — Unit 08 Word Wizard Implementation Plan

**Goal:** Ship `unit-08-word-wizard` — the dictionaries unit — where students build a translation
wizard and a word-frequency counter: a DICT maps each word (key) to its translation or its count
(value), looked up with `[]`/`.get`, guarded with `in`, and walked with `.items()`.

**Architecture:** Standard unit pipeline (plan 004), no new tooling. ONE map amendment lands UP
FRONT (the standing substrate audit, validated with the AST concept-scanner): unit-08's
`requires ∪ practices` omits the substrate its content uses. Helper functions take arguments and
return values (`for-loop`, `parameters`, `return-value` → requires); the count/translate/display
beats use `print`, `variable`, `comparison` (the CORE most-common-word `count > best_count`, plus
reverse-lookup), `string-concat` (a `word => value` label), `elif-else`, `arithmetic` (`count +
1`), `int-type` (counts), `accumulator` (the counter `counts[word] = counts[word] + 1`),
`error-messages` (the KeyError beat), `input` (an exercise prompt), `string-literal` (every
key/value/message), `type-conversion` (`str(count)`), and `boolean` (a `print("cat" in
translations)` membership-truth beat) → practices. All taught by units 01–07; verified green in
scratch. NOTE (glm plan-review): the pre-gate concept-scanner's method allowlist already maps
`.get`/`.keys`/`.values` and `.items` to taught dict concepts, so `.get()`/`.items()` do NOT
false-positive as untaught methods.

**Spec:** `book1/curriculum/coverage-map.yaml` (binding, amended); plan 004 unit conventions; D-001.

## Global Constraints

- All plan-004 unit Global Constraints apply (map-equal manifest, hook-first, exercise ≥6 core
  + ≥2 stretch, solution floors + per-line bans, seed ordering, non-vacuous asserts incl. no
  tautologies, five teacher-notes headings, per-lesson allocation, commit trailers).
- Coverage-map amendment (EXACTLY this, pre-audited + scanner-validated green):
  - append to `unit-08-word-wizard.requires` — `for-loop, parameters, return-value`.
  - append to `unit-08-word-wizard.practices` — `print, variable, comparison, string-concat,
    elif-else, arithmetic, int-type, error-messages, input, string-literal, boolean,
    type-conversion, accumulator` (`type-conversion` homes `str(count)` in the
    `word + " => " + str(count)` label; `accumulator` homes the counter `counts[word] =
    counts[word] + 1` — the read-modify-write running-total pattern, same classification unit-07
    gave `total = total + score`; fable plan-review, introduced unit 04).
  - All introduced by units 01–07; `practices ∩ introduces` stays empty (introduces =
    dict-literal/dict-access/dict-loop). Apply surgically (no YAML round-trip). Manifest carries
    the amended lists. Each amended concept HOMED in ≥1 beat/exercise (teacher notes name each).
- **Pre-gate closure self-check (standing from plan 008/009):** before dispatching the `[sol]`
  content review, run the AST concept-scanner scoped to unit-08 and confirm ZERO used-but-unlisted
  concepts AND zero untaught method calls.
- **Dict mechanics (binding):** dicts are built with `{key: value, ...}` literals; read with
  `translations[key]` and the safe `translations.get(key, default)`; updated/added with
  `translations[key] = value`; membership-tested with `key in translations`; walked with
  `for key in translations` and `for key, value in translations.items()`. `.get`, `.items`,
  `.keys`, `.values` are the ONLY dict methods used. FORBIDDEN: any other dict method
  (`.pop`/`.update`/`.setdefault`/`.pop`/comprehensions), sets, tuples-as-keys beyond trivial,
  and anything from later units (files/classes).
- **`.split()` is NOT taught (binding, closure trap):** the taught `string-methods` subset is
  ONLY `upper/lower/strip/replace`. Word-frequency counting therefore iterates a GIVEN list of
  words (`words = ["cat", "dog", "cat", ...]`), NEVER a `sentence.split()`. Reviewers reject any
  `.split()`.
- **No lists-beyond-taught / no nested loops past the counter:** list ops stay within unit-07's
  taught set (`.append`, `.sort`, index, iterate, len/max/min); `.pop`/`.insert`/`.remove`/
  `.index`/`sorted()` remain forbidden. The word-count loop is a SINGLE loop over the word list;
  reverse-lookup is a SINGLE loop over `.items()`. No nested loops.
- **Input discipline (binding):** executed cells (lessons + solutions) are input-free; `input()`
  appears only in an exercise PROMPT (markdown) with a parameterized reference solution.
- Process (standing): no commits while a `[sol]` review is in flight; codex content-gate prompts
  name the in-process execution fallback and avoid bare CLI-flag-like tokens.

## Out of scope

Content plan → Phase C is the mandatory named verification phase. Out of scope: checkpoint 03
and units 09+ (later plans); the latent practice-completeness hygiene PR for shipped units
03/04/05/cp02/proj01 + scanner promotion to `tools/` (tracked separately); PDF handouts; any map
edit beyond the Phase-A substrate amendment; files/classes; `.split()`.

## Phases

Dispatch per AGENTS.md: lesson/exercise statements via codex; solutions via a SEPARATE blind
codex session; teacher notes inline; map amendment + manifest inline.

### Phase A — map amendment + manifest (inline)

1. Amend `coverage-map.yaml` per Global Constraints (surgical, both requires + practices); full
   suite green with the amendment alone before content.
2. `book1/units/unit-08-word-wizard/manifest.yaml`, map-equal to the amended entry; lands with
   the complete directory in Phase B.
- **Acceptance (Phase A):** the map amendment ALONE is green (`uv run pytest -q` + `ci-local`)
  before any unit directory exists.

### Phase B — unit-08-word-wizard content (2 lessons)

Blueprint (introduces dict-literal, dict-access, dict-loop; requires list-loop, string-methods,
in-operator, def-function, + amended for-loop/parameters/return-value; practices list-literal,
list-append, if-statement, f-string, + amended print/variable/comparison/string-concat/elif-else/
arithmetic/int-type/error-messages/input/string-literal/boolean/type-conversion/accumulator):
- Hook: WORD WIZARD — a program that translates words and, like a spell-checker, counts how often
  each word appears. The teacher shows a tiny bilingual phrasebook and asks how a program could
  look a word up instantly.
- Lesson 1 (dict-literal, dict-access) — open on the hook: a DICT pairs each word (key) with its
  translation (value) — `translations = {"hello": "hola", "cat": "gato", "dog": "perro"}`. Look up
  `translations["hello"]`; add/update `translations["bird"] = "pajaro"`. Words arrive messy, so
  CLEAN the search word first — `clean = raw_word.strip().lower()` — so `"  Hello "` still matches
  the key `"hello"` (homes `string-methods`, which unit-08 `requires` — sol plan-review; the
  taught subset strip/lower). Test membership `print("cat" in translations)` (a True/False value —
  boolean); the SAFE lookup `translations.get("fish", "???")` that returns a default instead of
  crashing; the deliberate bug `translations["fish"]` → KeyError, read the traceback together
  (error-messages) — which is exactly why `.get` exists.
- Lesson 2 (dict-loop; the counter + translator) — open on the thread ("yesterday we looked words
  up; today we count them and translate a whole list"): walk keys `for word in translations:` and
  pairs `for word, translation in translations.items():`; a `translate(word, dictionary)` helper
  returning `dictionary.get(word, "???")` (def-function, parameters, return-value); a
  word-FREQUENCY counter over a GIVEN list (NOT split) — `words = ["cat","dog","cat","bird","cat"]`,
  `counts = {}`, then a SINGLE loop `for word in words: if word in counts: counts[word] =
  counts[word] + 1` (arithmetic/int-type/in-operator) `else: counts[word] = 1` (elif-else path);
  print each `word => count` with `.items()` and a `word + " => " + str(count)` label
  (string-concat + type-conversion via `str` — both in the amended union). Then a "most common
  word" beat over `.items()` — `best_word = ""; best_count = 0; for word, count in counts.items():
  if count > best_count: best_count = count; best_word = word` — which homes `comparison` in CORE
  content (not only the reverse-lookup stretch), a SINGLE loop, no nesting. A "new word arrives"
  beat homes `list-append` (glm plan-review): the word log grows as more text comes in —
  `words.append("cat")` — then RESET `counts = {}` and re-run the counter over the grown list
  (single loop, no nesting; the reset avoids double-counting — fable plan-review).
- Exercises ≥6 core + ≥2 stretch: build-a-phrasebook (dict-literal), safe-lookup (a game asks for
  a word with `input("word? ")` in the PROMPT prose — do NOT call it; the reference solution uses a
  FIXED sample word — then `.get(word, "???")`; this is the named home for `input`, fable
  plan-review), is-it-in-the-book (`in` condition), add-a-word (`dict[key] = value`), count-the-words
  (single loop over a given word list), most-common-word (single loop over `.items()`, `comparison`
  — core), grow-the-log (`words.append(new_word)`, then RESET `counts = {}` and re-count over the
  grown list so counts don't double — homes `list-append` in a core exercise), tidy-then-translate
  (clean a messy word with `.strip().lower()` before looking it up,
  so `"  CAT "` finds `"cat"` — homes `string-methods` in a core exercise), print-every-pair
  (`.items()`), translate-a-list (loop a word list, print each `translate`), fix-the-KeyError
  (swap `[]` for `.get`); stretch: reverse-lookup (find
  the key whose value matches a target — SINGLE loop over `.items()`, comparison), merge-two-
  phrasebooks (copy pairs from a second dict with a single loop + `dict[key] = value`).
- Solutions: execute headless, input-free (fixed sample dicts/word-lists), non-vacuous asserts —
  a `.get` default assert (`translate("fish", d) == "???"`), a count assert (`counts["cat"] == 3`),
  a membership assert (`("cat" in d) == True` is a tautology-risk — instead assert on a computed
  lookup), a reverse-lookup assert. `random.seed(4)` only if any randomness.
- Teacher notes: five headings, per-lesson allocation (L1 build/lookup/normalize/get/KeyError, L2
  loop/count/translate) with an EXPLICIT L2-density split (L2 is dense — the counter can open L2;
  the translate helper + most-common can be a 60-min cut) and an L1 60-min cut (normalization can
  be trimmed if L1 runs long) — glm plan-review; 60-min cuts,
  differentiation; common mistakes (KeyError on a missing key →
  use `.get`; overwriting a value by re-assigning an existing key; counting by iterating the dict
  instead of the word list; forgetting the `else: = 1` first-sighting case).

**Design decision (resolved):** the `word + " => " + str(count)` label homes both `string-concat`
and `type-conversion` (`str`, introduced unit 02, closure-safe) — both are in the amended union.
All other display uses f-strings.

### Phase C — Verification (NAMED, mandatory)

Mechanical: full pytest green; `ci-local.sh` ALL GREEN; AST concept-scanner scoped to unit-08
clean (zero used-but-unlisted, zero untaught methods) BEFORE the content gate; solutions execute
with non-vacuous asserts; manifest map-equal.
Reviewer duties: blind-solve exercises; cumulative closure (only ≤unit-08 — NO `.split()`, NO
files/classes, NO dict methods beyond `.get`/`.items`/`.keys`/`.values`, NO sets, NO nested loops
— check explicitly); the phrasebook + counter are buildable and correct (`.get` default, KeyError
motivation, single-loop count, reverse-lookup); solutions non-vacuous/complete; grading usable;
timing; each lesson opens on the project thread (hook-first, D-001); age-appropriate; each amended
concept exercised by ≥1 named beat.

**Acceptance criteria:** the unit directory complete; `uv run pytest -q` green; ci-local ALL
GREEN; concept-scanner clean; content gate 4-way consensus.

---

## Plan Review

### Review 1 — [self] (2026-09-06)
APPROVE (after one self-fix pre-dispatch): caught that `comparison` would be homed only in the
reverse-lookup STRETCH exercise (core must not depend on stretch), so added a core "most common
word" beat (`if count > best_count`) + a core exercise homing `comparison`. Amendment validated
green (prereq/practice/reference/schema/checkpoint/introduction). Closure design honors: `.split()`
forbidden (word-count iterates a GIVEN list, not a split sentence); KeyError→`error-messages`;
only `.get`/`.items`/`.keys`/`.values` dict methods; single loops (no nesting); `boolean` via
`print("cat" in translations)`; `string-literal` via keys/values; `type-conversion`+`string-concat`
via the `word + " => " + str(count)` label. `practices ∩ introduces` empty.

### Review 2 — [glm] (2026-09-06)
APPROVE WITH NITS → all addressed (revised in place before commit):
1. `[FIXED]` (Minor) `list-append` listed-but-unhomed — homed via a "new word arrives"
   `words.append(...)` lesson beat + a `grow-the-log` core exercise.
2. `[FIXED]` (Nit) Architecture prose pinned `comparison` to the stretch — now names the CORE
   most-common-word homing.
3. `[FIXED]` (Nit) scanner allowlist mapping for `.get`/`.items` — noted in Architecture; the
   scanner already registers these as taught (no false positive).
4. `[FIXED]` (Nit) L2 density — explicit L2 split carried to the teacher-notes spec.
- glm affirmed: closure complete (no used-but-unlisted), amendment closure-safe, `.split()` trap
  avoided, KeyError→`.get` sound, only `.get/.items` dict methods, no nesting.

### Review 3 — [fable] (2026-09-06)
REJECT → both findings RESOLVED:
1. `[FIXED]` (Blocker) `accumulator` used-but-unlisted — the counter `counts[word] =
   counts[word] + 1` is the read-modify-write accumulator pattern (unit-07 classified the
   identical `total = total + score` as accumulator). Added to the practices amendment
   (introduced unit 04, closure-safe; `practices ∩ introduces` stays empty). Re-validated green.
2. `[FIXED]` (Major) `list-append` listed-but-unhomed — same as glm #1, homed.
- fable affirmed: prereq closure of all amended concepts; `.split()` avoided; dict-method
  discipline; no nested loops / builtin-functions / float-type; counter + most-common logic
  correct; boolean correctly homed+listed; comparison in core; hook-first pedagogy.

### Round 2 revisions (2026-09-06)
Amendment now: requires += `for-loop, parameters, return-value`; practices += `print, variable,
comparison, string-concat, elif-else, arithmetic, int-type, error-messages, input, string-literal,
boolean, type-conversion, accumulator` (13). `list-append` homed (lesson beat + core exercise).
Re-validated green.

### Review 4 — [sol] (2026-09-06)
REJECT → all findings RESOLVED:
1. `[FIXED]` (Blocker) `accumulator` used-but-unlisted — same as fable #1; added to practices.
2. `[FIXED]` (Blocker) `list-append` over-listed/unhomed — homed via the `words.append(...)`
   lesson beat + `grow-the-log` core exercise (now a genuine practice, not padding).
3. `[FIXED]` (Nit) `string-methods` in `requires` had no described use — added a word-
   normalization beat (`clean = raw_word.strip().lower()` before lookup) to L1 + a
   `tidy-then-translate` core exercise. Pedagogically strong (case-insensitive matching).
- sol affirmed: no `.split()`; only `.get`/`.items` dict methods; no sets/comprehensions/nested-
  loops/files/classes; mechanical map checks + `tests/test_book1_curriculum.py` (9 tests) pass.

### Round 2 revisions — FINAL (2026-09-06)
All three external reviewers converged on `accumulator` (used-but-unlisted) and `list-append`
(unhomed); sol added `string-methods` (unhomed requires). Amendment now: requires += `for-loop,
parameters, return-value`; practices += `print, variable, comparison, string-concat, elif-else,
arithmetic, int-type, error-messages, input, string-literal, boolean, type-conversion,
accumulator` (13). `list-append` homed (beat + exercise); `string-methods` homed (normalization
beat + exercise). Re-validated green. Re-dispatching [glm]/[fable]/[sol] round 2 to confirm.

### Round 2 re-review verdicts (2026-09-06)
**[fable] round 2: APPROVE WITH NITS.** Both round-1 blockers confirmed resolved; traced all 27
union concepts homed, zero used-but-unlisted, no untaught leaks; counter/most-common/normalization
logic correct. Non-blocking nits folded into the exercise specs: (a) `input` pinned to the named
`safe-lookup` exercise (prompt prose only, fixed-sample solution); (b) `grow-the-log` resets
`counts = {}` before re-counting so counts don't double. Awaiting [glm]/[sol] round 2.

**[glm] round 2: APPROVE WITH NITS.** Independently re-ran the amendment on a scratch map →
tests/test_book1_curriculum.py 9/9 pass. All three round-1 fixes present + coherent; full-union
audit clean (every concept homed, nothing over-listed/used-but-unlisted, `practices ∩ introduces`
empty); no untaught leak (no .split, only .get/.items, no sets/comprehensions/nested-loops/files/
classes). One doc-coherence nit FIXED: teacher-notes L1 allocation now names the normalize beat +
an L1 60-min cut. Awaiting [sol] round 2.

### Review — [sol] round 2 (2026-09-06)
REJECT (reviewed pre-fix commit 5309bf9). Confirmed all three round-1 findings RESOLVED
(accumulator/list-append/string-methods) and NO untaught leak. Sole REJECT reason: `input`
listed-but-unhomed — no named exercise identified the input prompt. This is the SAME finding as
fable round-2 nit (a), already fixed in the (then-uncommitted) revision: `input` is now pinned to
the named `safe-lookup` exercise (prompt prose only, fixed-sample solution). `[FIXED]`.
Re-dispatching a focused [sol] round 3 to confirm the input home.

**[sol] round 3: APPROVE.** `input` confirmed homed in the named `safe-lookup` exercise (prompt
prose, fixed-sample solution). All prior findings cleared.

## Plan Gate — CONSENSUS REACHED (2026-09-06)
- `[self]` APPROVE · `[glm]` APPROVE WITH NITS · `[fable]` APPROVE WITH NITS · `[sol]` APPROVE.
- Round 1 was a convergent REJECT (accumulator used-but-unlisted + list-append unhomed; sol added
  string-methods unhomed); all fixed in round 2 (+accumulator; homed list-append + string-methods +
  input). No open blockers; nits are Phase-B authoring specs, staged.
- **Gate PASSED. Proceeding to Phase A → Phase B → Phase C.**
