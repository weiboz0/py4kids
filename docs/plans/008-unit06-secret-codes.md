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
  amended list.
- NO `ord`/`chr`: ciphers work on an alphabet STRING via `string-index` + `in-operator` +
  arithmetic (shift `%`), never character codes (the registry has no ord/chr concept).
- No lists/dicts/classes (units 07/08/10). No turtle (no assets).
- Process (standing): no commits while a `[sol]` review is in flight; codex content-gate
  prompts name the in-process fallback and avoid bare CLI-flag-like tokens.

## Out of scope

Content plan → Phase D is the mandatory named verification phase. Out of scope: units 07+,
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
- **Acceptance:** amendment green (`ci-local`); manifest passes `manifest-check`.

### Phase B — unit-06-secret-codes content (2 lessons)

Blueprint (introduces string-index, string-slice, string-methods, in-operator; requires
for-loop, string-concat, def-function, parameters, return-value; practices f-string,
accumulator, if-statement, loop-counter, + amended print/variable/comparison/arithmetic/
range-function/int-type/input):
- Hook: SECRET CODES — pass messages only your friends can crack; the teacher shows an
  encoded note and the class tries to break it.
- Lesson 1 (string-index, string-slice, string-methods): text as a sequence — grab a
  character by position (`word[0]`), a slice (`word[1:4]`), and clean it up
  (`.upper()`/`.lower()`/`.strip()`/`.replace()`). A REVERSE cipher (`word[::-1]` via
  slicing) and an ATBASH-style flip built by looking up each letter's index in a
  `letters = "abcdefghijklmnopqrstuvwxyz"` string.
- Lesson 2 (in-operator; practices the Caesar build): membership (`if letter in letters`)
  to skip spaces/punctuation; the CAESAR cipher as a function — for each letter find its
  index, add the shift, wrap with `%` (arithmetic + comparison), rebuild with string-concat
  in an accumulator; decode = shift back. A deliberate off-by-one/wrap bug + traceback moment.
- Exercises ≥6 core + ≥2 stretch: reverse-a-word, first-and-last-letter (index),
  grab-the-middle (slice), shout-it (string-methods), is-it-a-vowel (in-operator),
  fix-the-caesar (debug); stretch: a keyword check that ignores case, a two-step cipher
  (reverse then shift).
- Solutions: execute headless, input-free (assigned sample messages), non-vacuous asserts
  on encoded/decoded round-trips (`decode(encode(msg, 3), 3) == msg`).
- Teacher notes: five headings, per-lesson allocation (L1 index/slice/methods, L2
  in-operator + Caesar), 60-min cut points, differentiation; common mistakes (off-by-one
  slice bounds, forgetting the `%` wrap, mutating vs rebuilding a string, case mismatch in
  membership).

### Phase C — Verification (NAMED, mandatory)

Mechanical: full pytest green; `ci-local.sh` ALL GREEN; solutions execute with non-vacuous
asserts (round-trip encode/decode); manifest map-equal.
Reviewer duties: blind-solve exercises; cumulative closure (only ≤unit-06 concepts — NO
ord/chr, NO lists/dicts); the alphabet-string cipher approach is genuinely buildable and
correct (encode/decode round-trip); solutions non-vacuous/complete; grading usable; timing;
hook-first; age-appropriate; the amended practices are each exercised by ≥1 exercise.

**Acceptance criteria:** the unit directory complete; `uv run pytest -q` green; ci-local ALL
GREEN; content gate 4-way consensus.

---

## Plan Review

(4-way gate verdicts land here.)

## Content Review

(pre-PR gate findings land here.)

## Post-Execution Report

(written before shipping.)
