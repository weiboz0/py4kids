# Plan 008 — Unit 06 Secret Codes Implementation Plan

**Goal:** Ship `unit-06-secret-codes` — string surgery and ciphers — the first Term 3 unit, where students slice, index, and transform text to encode and crack secret messages.

**Architecture:** Standard unit pipeline (plan 004), no new tooling. ONE map amendment lands UP FRONT (the standing plan-002 substrate audit, applied proactively per the plan-007 follow-up rather than discovered at the gate): unit-06's `requires ∪ practices` omits the foundational substrate its cipher content uses — `print`, `variable`, `comparison`, `arithmetic` (Caesar shift), `range-function` (position indexing), `int-type` (shift amounts), `input` (the secret message) — all taught by units 01–03, verified green. No `ord`/`chr` concept exists, so ciphers are ALPHABET-STRING based (a `letters = "abc...z"` string; shift by `index + n`, wrap with `%` via arithmetic/comparison), never character codes (plan 002 follow-up).

**Spec:** `book1/curriculum/coverage-map.yaml` (binding, amended); plan 004 unit conventions; D-001.

## Global Constraints

- All plan-004 unit Global Constraints apply (map-equal manifest, hook-first, exercise/
  solution floors + per-line bans, seed ordering, non-vacuous asserts incl. no tautologies,
  five teacher-notes headings, per-lesson allocation, commit trailers).
- Coverage-map amendment (EXACTLY this, pre-audited): append to
  `unit-06-secret-codes.practices` — `print, variable, comparison, arithmetic,
  range-function, int-type, input` — all introduced by units 01–03; verified green.
  Apply surgically (no YAML round-trip — it reflows the file). The manifest carries the
  amended list. Every one of these must be HOMED in ≥1 exercise (not padding, gate
  round-1): print (emit the code), variable (`letters`/`result`/`shift`), comparison (the
  position scan), arithmetic (`+ shift`, `% 26`), range-function (the position scan),
  int-type (the shift is an integer LITERAL/parameter), input (an exercise reads a message
  to encode). Teacher notes name each one's reappearance.
- **Position-lookup mechanism (binding, gate round-1 blocker — sol/glm/fable):** to find a
  letter's alphabet position, content uses a `for position in range(26)` scan with
  `if letters[position] == letter` — the ONLY in-budget idiom. `len()` (that is
  `builtin-functions`, introduced unit 07) and `.index()`/`.find()` (outside the taught
  `string-methods` subset "upper/lower/strip/replace", and they would slip past a
  concept-ID closure check) are FORBIDDEN in unit-06 content; reviewers check for them
  explicitly. `range-function` is LOAD-BEARING here (not incidental) — it is the only way
  to scan the alphabet without `len`.
- **Case contract (binding, sol #3):** ciphers operate on LOWERCASE a–z. Encode/decode
  normalize the message with `.lower()` first; letters not in `letters` (spaces,
  punctuation) pass through unchanged; the round-trip is `decode(encode(msg, n), n)`
  equals `msg.lower()` — mixed-case exact round-trip is NOT claimed, and all sample
  messages in exercises/solutions are lowercase. The shift is a fixed integer literal or
  parameter, NEVER `int(input(...))` (which would drag in un-amended `type-conversion`).
- NO `ord`/`chr`: ciphers work on an alphabet STRING via `string-index` + `in-operator` +
  arithmetic (shift `%`), never character codes (the registry has no ord/chr concept).
- No lists/dicts/classes (units 07/08/10). No turtle (no assets).
- Process (standing): no commits while a `[sol]` review is in flight; codex content-gate
  prompts name the in-process fallback and avoid bare CLI-flag-like tokens.

## Out of scope

Content plan → Phase C is the mandatory named verification phase. Out of scope: units 07+,
checkpoint 03 (later plans); PDF handouts; any map edit beyond the Phase-A substrate
amendment; ord/chr; lists/dicts.

## Phases

Dispatch per AGENTS.md: lesson/exercise statements via codex; solutions via a SEPARATE
blind codex session; teacher notes inline; map amendment + manifest inline.

### Phase A — map amendment + manifest (inline)

1. Amend `coverage-map.yaml` per Global Constraints (surgical); full suite green with the
   amendment alone before content.
2. `book1/units/unit-06-secret-codes/manifest.yaml`, map-equal to the amended entry; lands
   with the complete directory.
- **Acceptance (Phase A):** the map amendment ALONE is green (`uv run pytest -q` +
  `ci-local`) before any unit directory exists (glm #3 — manifest-check lands with the
  content in Phase B, not here).

### Phase B — unit-06-secret-codes content (2 lessons)

Blueprint (introduces string-index, string-slice, string-methods, in-operator; requires
for-loop, string-concat, def-function, parameters, return-value; practices f-string,
accumulator, if-statement, loop-counter, + amended print/variable/comparison/arithmetic/
range-function/int-type/input):
- Hook: SECRET CODES — pass messages only your friends can crack; the teacher shows an
  encoded note and the class tries to break it.
- Lesson 1 (string-index, string-slice, string-methods) — opens on the hook (decode a
  note): text as a sequence — grab a character by position (`word[0]`), a slice
  (`word[1:4]`), and clean it up (`.upper()`/`.lower()`/`.strip()`/`.replace()`), PRINTing
  each result. A REVERSE cipher (`word[::-1]` via slicing) and an ATBASH-style flip built by
  scanning `letters = "abcdefghijklmnopqrstuvwxyz"` with `for position in range(26)` +
  `if letters[position] == letter` and taking `letters[25 - position]`.
- Lesson 2 (in-operator; practices the Caesar build) — opens on the thread ("yesterday we
  read codes; today we write one only your friend can crack"): membership
  (`if letter in letters`) to pass spaces/punctuation through unchanged; the CAESAR cipher
  as a function `encode(message, shift)` — `.lower()` the message first (case contract),
  for each letter scan `range(26)` for its position, `new = (position + shift) % 26`
  (arithmetic + comparison), rebuild with string-concat in a `result` accumulator; `decode`
  = `encode(message, 26 - shift)`. The shift is an integer parameter (never `int(input())`).
  A deliberate wrap/off-by-one bug + traceback moment. An exercise reads a message via
  `input()` to encode (homes `input`).
- Exercises ≥6 core + ≥2 stretch, each HOMING an amended practice: reverse-a-word (slice),
  first-and-last-letter (index), grab-the-middle (slice), shout-it-and-print (string-methods
  + print), is-it-a-vowel (in-operator + comparison), encode-my-typed-message
  (input + the Caesar function), fix-the-caesar (debug the `% 26` wrap); stretch: a
  case-insensitive keyword check, a two-step cipher (reverse then shift).
- Solutions: execute headless, input-free (assigned LOWERCASE sample messages), non-vacuous
  asserts on round-trips honoring the case contract
  (`decode(encode(msg, 3), 3) == msg` where `msg` is lowercase), plus a boundary assert
  (`z` with shift 3 → `c`).
- Teacher notes: five headings, per-lesson allocation (L1 index/slice/methods, L2
  in-operator + Caesar), 60-min cut points, differentiation; common mistakes (off-by-one
  slice bounds, forgetting the `%` wrap, mutating vs rebuilding a string, case mismatch in
  membership).

### Phase C — Verification (NAMED, mandatory)

Mechanical: full pytest green; `ci-local.sh` ALL GREEN; solutions execute with non-vacuous
asserts (round-trip encode/decode); manifest map-equal.
Reviewer duties: blind-solve exercises; cumulative closure (only ≤unit-06 concepts — NO
ord/chr, NO lists/dicts, NO `len()`, NO `.index()`/`.find()` — check for these explicitly
since `.index()` maps to an allowed concept id and would slip a mechanical closure check);
the alphabet-string cipher is buildable and correct (encode/decode round-trip on lowercase,
boundary wrap); solutions non-vacuous/complete; grading usable; timing; each lesson opens on
the project thread (hook-first, per D-001); age-appropriate; EACH of the 7 amended practices
is exercised by ≥1 named exercise (print/input especially — they were the round-1 padding
risk).

**Acceptance criteria:** the unit directory complete; `uv run pytest -q` green; ci-local ALL
GREEN; content gate 4-way consensus.

---

## Plan Review

### Review 1 — [self] (2026-09-06)
- **Verdict**: APPROVE — substrate pre-audited and verified green; unit pipeline reused; no-ord/chr constraint stated.

### Review 2 — [glm] (2026-09-06)
- **Verdict**: APPROVE WITH NITS (amendment verified green live; no-ord/chr Caesar confirmed buildable)
1. `[FIXED]` Position-lookup unspecified — pin `range(26)` scan, forbid `.index()`/`.find()`/`len()`.
2. `[FIXED]` Home each amended practice (esp. input/int-type); avoid `int(input())` → type-conversion; name reappearances.
3. `[FIXED]` Phase A acceptance contradicted Phase B (manifest-check) — reworded to amendment-only-green.

### Review 3 — [fable] (2026-09-06)
- **Verdict**: APPROVE WITH NITS (PROTOTYPED the cipher in /tmp — round-trips across 5 msgs × 7 shifts, no list/ord/chr/len)
1. `[FIXED]` Position-lookup latent closure trap (= glm #1; `.index()` slips a concept-id check) — pinned + forbidden.
2. `[FIXED]` Out-of-scope said "Phase D" — corrected to Phase C.
3. `[FIXED]` range-function role understated — now stated as load-bearing.

### Review 4 — [sol] (2026-09-06)
- **Verdict**: REJECT
1. `[FIXED]` (Major) print/input unhomed (padding risk); `int()` is type-conversion not int-type. → both homed in exercises; shift kept a fixed integer.
2. `[FIXED]` (Blocker) Position-lookup unspecified/unenforceable (= glm/fable). → pinned `for position in range(26)` + `letters[position] == letter`; len/.index/.find forbidden.
3. `[FIXED]` (Major) Round-trip needs a CASE CONTRACT (lowercasing loses case; not lowercasing breaks on uppercase). → cipher operates on lowercase (`.lower()` first); round-trip asserted on lowercase; mixed-case not claimed.
4. `[FIXED]` (Major) print/input not bound to any exercise (= #1).
5. `[FIXED]` (Nit) Lesson 2 continuing hook not explicit. → both lessons now open on the thread.
6. `[FIXED]` (Minor) Phase D→C (= fable #2).

### Round 2 (2026-09-06)
- **[fable]**: APPROVE — re-prototyped the case contract in /tmp (round-trip 4 msgs × 25 shifts, boundary, passthrough, mixed-case→lower all pass); all 7 practices homed; no new defect.
- **[glm]**: APPROVE — all 3 nits fixed, case contract coherent, re-prototyped green.
- **[sol]**: APPROVE — all 6 findings resolved; no new issues.

### Gate result (2026-09-06)
- `[self]` APPROVE · `[sol]` APPROVE (round 2) · `[glm]` APPROVE (round 2) · `[fable]` APPROVE (round 2).
- Full consensus, no `[OPEN]` items — **gate PASSED; approval to implement.**

## Content Review

### Review 1 — [self] (2026-09-06)
- **Verdict**: APPROVE — boundary sweep clean (range(26) scan, no .index/len/lists), round-trip + boundary asserts, hook-first; 336 tests, ci-local ALL GREEN.

### Review 2 — [fable] (2026-09-06)
- **Verdict**: APPROVE (no findings)
- Blind-solved all 9 exercises — zero discrepancies; independently verified round-trip, boundary (z+3→c), atbash (decoded the hook to "meet me at the library"); closure clean (no len/.index/.find/ord/chr/lists/dicts; range(26) scan ×5); case contract honored; all 7 amended practices homed; 11 non-vacuous asserts; 336 tests, ci-local ALL GREEN.
- Optional observation (no change): input() practice lives in the exercise prompt + the lesson's no-exec cell, not an executable solution cell — by design (headless).

### Review 3 — [glm] (2026-09-06)
- **Verdict**: APPROVE WITH NITS (no blockers)
- Blind-solved all 9 (zero substantive discrepancies), executed solutions in /tmp (round-trip + boundary green); closure clean; `%` confirmed taught unit 02; all 7 practices homed.
1. `[FIXED]` (NTH) E4 solution had a stray space `" " )`. → tidied.
2. `[WONTFIX]` (NTH) E2 "print both characters" is open-ended (`"c r"` vs `"cr"`) — the c/r asserts are the real check; format left student-open by design.
3. `[FIXED]` (NTH) Teacher-notes L2 pacing had no explicit 60-min cut like L1. → cut added.
4. `[WONTFIX]` (NTH) E5 solution cell is print-only (no assert) — a branch demo; the notebook meets the ≥3 non-vacuous assert floor overall.

### Review 4 — [sol] (2026-09-06)
- **Verdict**: REJECT — two closure violations fable/glm missed (both real)
1. `[FIXED]` (Blocker) `elif-else` used throughout (the cipher's `else` passthrough branch, the vowel classifier) but absent from the union. → map+manifest amended: unit-06 practices += `elif-else` (introduced unit 02; genuinely homed).
2. `[FIXED]` (Blocker) Lesson 2 teaches traceback reading / IndexError — the `error-messages` concept, absent from the union. → amended: practices += `error-messages` (introduced unit 01; homed by the deliberate-bug moment).
- Otherwise clean: zero blind-solve discrepancies, no forbidden constructs, range(26) scan, 11 asserts, round-trip + boundary verified.
- Note: my Phase-A pre-audit missed `elif-else`/`error-messages` — the `else` passthrough and the traceback beat weren't in the "plausibly needed" set. Future pre-audits must include else-branches and deliberate-bug moments.

### Review 5 — [sol] round 2 (2026-09-06)
- **Verdict**: REJECT — elif-else/error-messages confirmed fixed, but a re-scan found TWO MORE used-but-unlisted concepts:
1. `[FIXED]` (Blocker) `nested-loops` — the `for position in range(26)` alphabet scan nests inside `for letter in message`. → amended (introduced unit 03).
2. `[FIXED]` (Blocker) `boolean` — Lesson 2's `print("m" in letters)` truth-value predictions. → amended (introduced unit 02).
- I then ran my OWN thorough code-only concept scan to catch anything else before re-review: confirmed NO other used-but-unlisted concept (the "logical-ops" apparent hits were all English "not" inside strings; no while/break/type-conversion in code; negative index → string-index, `[::-1]` → string-slice). unit-06 practices is now 15 concepts.

### Review 6 — [sol] round 3 (2026-09-06)
- **Verdict**: REJECT — declarations match and both round-2 additions valid, but sol's definitive 25-concept code-cell inventory found ONE more registered-but-unlisted: `string-literal` (`"nvvg"`, `"stressed"` etc.), introduced unit 01, used throughout.
- **Resolution**: `[FIXED]` — added `string-literal`. Considered pushing back (units 04/05, both sol-approved, use string literals without listing string-literal — an ambient-concept inconsistency), but checkpoint-01 DOES list it, and adding it makes sol's own enumerated inventory provably complete, so this is the convergent close rather than a round-4 over concept philosophy. unit-06 practices is now 16 concepts.
- **Latent map issue (follow-up, not blocking unit-06):** units 04 and 05 use string literals without listing `string-literal`; the map treats ambient foundational concepts (string-literal/comment/naming) inconsistently across units vs checkpoints. Worth a systemic pass, but out of unit-06 scope.
- **Tooling follow-up:** content-level closure (every concept USED in code is in the entry's union) is entirely reviewer-manual — it took 3 sol rounds to enumerate elif-else/error-messages/nested-loops/boolean/string-literal. A concept-usage scanner would mechanize it (concept-from-code detection is fuzzy but a keyword+AST heuristic would catch the obvious ones).

## Post-Execution Report

(written before shipping.)
