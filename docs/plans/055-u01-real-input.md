# Plan 055 — u01 story-machine: full real-input treatment (text-only arm)

**Status:** DRAFT — plan-review gate pending.
**Type:** Content — apply the full treatment to `unit-01-story-machine`.
**Branch:** `feature/plan-055-u01-real-input`. **Base:** main @ 5bdfc80.

## Motivation

Rollout slice 4 (design 003 §7 — list-less units). u01 is the **text-only** unit (Mad-Libs story machine):
concepts = run-program, print, comment, string-literal, variable, naming, **input**, string-concat, f-string,
error-messages — **NO `int`, no `if`, no loop, no comparison**. Per design 003 §4, u01 real-forms are
**TEXT-ONLY: read/print strings, fixed-count named prompts, NO `int()`, no loop, no sentinel**. `input` is in
`introduces` → **no metadata change**. Authorities: design 003 v3 (§2/§3 u01–u06 arm/§4/§6); merged pilots
u02/u04 (list-less) + cp01. This plan bakes in the recurring gate audits (lesson both-forms twins, statement
cues, per-exercise SHAPE) up front.

## The treatment (text-only)

1. **Real-input forms — all three notebooks (unit convention):**
   - **solutions.ipynb:** markdown fenced real-forms beside fixed-data asserted twins.
   - **lesson.ipynb:** every complete task keeps an executable fixed-data twin AND a `no-exec` input() real-form
     (Lesson both-forms audit below).
   - **exercises.ipynb statements:** `**Real version:**` cue on non-exempt fixed-data exercises; one-line note
     on exempt ones.
2. **No data growth.** Text-only, no numbers/lists — nothing toy to fix; the input() real-form carries realism
   (design 003 §3, u01–u06 arm).
3. **CP-light naming — near-zero.** u01 names (`hero`, `name`, `color`, `word`, `story`, `hero_name`,
   `silly_object`, `favorite_snack`) are clean domain nouns. Keep verbatim.
4. **No numbered prompts.** Fixed-count NAMED text prompts ("Your name? ", "A noun: ", "An action: ") — not a
   sequence, so no `{i + 1}` indices.
5. **Text-only closure.** Real-forms read strings with `input(...)` and combine via `+`/f-string — **NO
   `int(input())`** (int/str are u02), no loop, no comparison, no `if`. Nothing outside u01's union.

## Lesson both-forms audit (design §1/§8)

The both-forms/parity rule applies to **complete-task capstones**, not build-up rungs (§3/§6 — rungs stay minimal).

| Lesson cell | Status | Action |
|---|---|---|
| cell 60 (full Mad-Libs Story Machine **capstone**) | `no-exec` input only | **ADD executable twin** before it (fixed stand-in words → the same printed story) + a Notice — the ONLY input-only capstone |
| L2 cells 39/41/43 ("save a typed word/color/hero" demos) | `no-exec` input | **input-teaching BUILD-UP RUNGS** (introduce `input()` one step at a time), NOT capstones → exempt from the both-forms parity (their fixed-value counterparts 25–36 show the non-input form of the same idea); no twin |
| L1 (print basics 2–23), L3 combine demos (46–57, fixed values) | executable, no interactive capstone | no unpaired task — unchanged |

## Per-exercise SHAPE table

| Shape | Exercises | Real-form + statement treatment |
|---|---|---|
| **exempt** | Ex1 (greeting-card printer — a fixed printed card that **reads no external input**, the established generator/no-input class like the u02 dice roller / u04 countdown; also placed before variables/concat are practiced), Ex2 (fix the missing quote — SyntaxError debug), Ex3 (fix the mixed-up name — NameError debug) | NO real-form; a one-line **`**No real version:**`** note in the STATEMENT (Ex1: "a fixed printed card — it reads nothing, so there's no `input()` version"; Ex2/Ex3: "a fix-the-error exercise — the fix is the answer, so there's no `input()` version") |
| **interactive** (statement already reads `input()`) | Ex5 (interview bot — asks name/snack/dream job), Ex6 (Story Machine remix — collects character/place/object/action with `input(...)`), **Challenge 2** (emoji-art title — "Ask for an emoji and title words with `input()`") | markdown real-form = the input()-reading program (fixed stand-in words in the runnable twin; **real-form mirrors the solutions twin's variable names**, e.g. Ex5 `player_name`); no cue (already interactive). Ch2 real-form: `emoji = input("An emoji: ")` / `title_words = input("Title words: ")` then the unchanged concat → parity `🚀 Moon Mission 🚀`. |
| **read-and-compute** (fixed values → real version reads them) | Ex4 (story remix — read hero/place/object), Ex7 (build a greeting with `+` — read `name`), **Challenge 1** (multi-paragraph story — read `hero`/`place`) | markdown real-form reads the word(s) with `input(...)` (text, NO `int()`) then the unchanged concat/print/f-string; statements get a `**Real version:**` cue. **Ex7 keeps its constraint** (exactly three `+` pieces, NO f-string): `name = input("Your name: ")` / `greeting = "Hello, " + name + "!"` / `print(greeting)`. |

## Phases
### Phase A — apply to u01 (lesson + exercises + solutions)
- **lesson.ipynb:** reword cell 59 ("…run it first with fixed words, then the asking version") → add an
  executable fixed-data twin (stand-in words e.g. `hero="Captain Pickle"`, `place="the moon library"`,
  `object_name="a squeaky crown"`, `action="yodel"`; the SAME five print lines incl. the `+` title) → a
  `**Notice:**` → the existing `no-exec` cell 60. L2 39/41/43 are build-up rungs (untouched); L3 unchanged.
- **exercises.ipynb:** `**Real version:**` cues on Ex4/Ex7 + Challenge 1; `**No real version:**` notes on
  Ex1/Ex2/Ex3. No cue on the already-interactive Ex5/Ex6/Challenge 2.
- **solutions.ipynb:** markdown real-forms per the SHAPE table — interactive Ex5/Ex6/Ch2; read-and-compute
  Ex4/Ex7/Ch1. Ex1/Ex2/Ex3 exempt (no real-form). Fix Ex1's twin comment/assert only if the exempt note needs
  it (else leave the pure-print twin as-is).
- No growth, no rename, no numbered prompts. **No teacher-notes change** (no variable renamed; the twin's
  explanation lives in its Notice). Fenced real-forms must not contain a `## Exercise <digit>` line.

### Phase B — verification
- `ast.parse` + piped-run every real-form + the new lesson twin; result line == fixed-data twin modulo
  `input()` prompt text (all standard §6(a–c) — no random, no fragment).
- CLOSURE AST scan: **NO `int(`**, no `for`/`while`/`if`/comparison/list/`sys.stdin` in any real-form (text-only).
- 0 `input()` in solutions CODE cells; ≥3 non-vacuous assert cells; no fenced `## Exercise <digit>` line.
- `scripts/ci-local.sh` ALL GREEN.

## Out of scope
- Any Book-1 entry other than u01 (rollout continues per design 003 §7). No design amendment. No data growth
  (text-only). Phase B present.
- **Pre-existing errata (NOT this plan):** u01 solutions' teacher-note cites `random.seed(4)` though u01 uses no
  `random` — an errata candidate for a later fix, out of this plan's scope.

## Plan Review

### Round 1 (2026-09-19) — [self] inline; [sol] gpt-5.6-sol; [glm] volcengine-plan/glm-5.3; [fable] Fable 5.
#### [self] (2026-09-19)
- **Verdict**: APPROVE
- Text-only closure (§4: no int(input)/loop/if); lesson both-forms audit (executable twin for the full
  Mad-Libs capstone cell 60; L2 39/41/43 paired with fixed-value analogs 25–36) baked in up front; SHAPE table
  (exempt Ex2/Ex3 debug; interactive Ex5/Ex6; read-and-compute Ex1/Ex4/Ex7) + unit statement cues; no
  growth/rename/numbered-prompts; `input` in introduces → no metadata. Phase B present incl. the "no int(" scan.
#### [sol] (2026-09-19)
- **Verdict**: REJECT
1. `[OPEN]` Must Fix: SHAPE table + Phase A omit both Challenges (== fable#1/glm#1).
2. `[OPEN]` Must Fix: Ex1 is a pure-print/comment task, not read-and-compute — its fixed twin has no
   variable/concat, so a recipient read can't be §6(c) line-for-line. Reclassify exempt or scope a rewrite.
3. `[OPEN]` Should Fix: L2 cell 41 isn't a genuine parity analog (prints a fixed label then the color); it's a
   build-up rung — exempt from the parity claim; also "reads one word" is wrong (cell 43 reads two).

#### [glm] (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: REJECT
1. `[OPEN]` Must Fix: SHAPE table + Phase A omit Challenge 1 (read-and-compute) + Challenge 2 (interactive).
2. `[OPEN]` Nice: Ex1 twin has no variable → real-form parity is §6(b) result-lines, not §6(c) line-for-line.
3. `[OPEN]` Nice: L2 cell 43 reads two words (hero+sidekick); cell-41 label wording.
4. `[OPEN]` Nice: Phase A omitted teacher-notes — include or scope out.
5. `[OPEN]` Nice (FYI, pre-existing): u01 teacher-note cites `random.seed(4)` but u01 has no random — errata.
- (glm classified Ex1 read-and-compute; resolved as exempt below — the reads-nothing/generator class, which
  answers "no pure-print class": it's the same class as the dice roller / countdown.)

### Round 1 — outcome: REJECT (2 of 4: [sol]+[glm]). Fixed → round 2.
**Round 1 responses:**
- → [FIXED] Challenges omitted ([sol]#1/[glm]#1/[fable]#1 — Must): added a **stretch** row — Ch1
  read-and-compute (read hero/place + cue + real-form), Ch2 interactive (real-form reads emoji+title_words).
- → [FIXED] Ex1 → **EXEMPT** ([sol]#2 Must / [fable]#2): reclassified as the established **reads-no-external-input
  / generator** exemption (a fixed printed card, like the u02 dice roller / u04 countdown) — this answers
  [glm]'s "no pure-print class" (it IS the reads-nothing class); `**No real version:**` statement note; no §6c
  transform of the pure-print twin.
- → [FIXED] L2 audit ([sol]#3/[glm]#3): 39/41/43 reframed as input-teaching **build-up rungs** (exempt from the
  both-forms parity per §3/§6); only cell 60 (capstone) gets a twin; removed the "one word"/label wording.
- → [FIXED] exempt-note label → `**No real version:**` ([fable]#3); cell-60 twin placement/wording spelled out
  ([fable]#4); Ex5 real-form mirrors solutions `player_name` ([fable]#5); Ex7 keeps the 3-`+`-pieces/no-f-string
  constraint ([fable]#6); Ex1 parity moot now (exempt) ([glm]#2).
- → [FIXED] Phase A: **no teacher-notes change** stated ([glm]#4); pre-existing `random.seed(4)` teacher-note
  recorded as out-of-scope errata ([glm]#5).
Re-dispatching round 2 (Challenges + Ex1-exempt changed materially).

#### [fable] (2026-09-19)
- **Verdict**: APPROVE WITH NITS — verified: text-only closure holds; cell 60 is the only input-only capstone
  without a twin (L2 39/41/43 covered by fixed analogs 25/27/29; cell 21 pairs with 23; L1/L3 no capstone);
  Ex2/Ex3 exempt, Ex5/Ex6 interactive, Ex4 read-and-compute all correct; Phase B present.
1. `[OPEN]` Must Fix: SHAPE table OMITS the 2 Challenges — add a **stretch** row (Ch2 interactive: reads emoji +
   title words → markdown real-form; Ch1 classify — read-and-compute or exempt). Name them now (scope safeguard).
2. `[OPEN]` Should Fix: Ex1 (greeting-card printer) is a PURE-PRINT drill placed BEFORE variables (Ex4 is the
   first variable exercise) — read-and-compute forces a premature variable+concat → make Ex1 **exempt** ("a
   plain-print card — no input() version").
3. `[OPEN]` Should Fix: exempt-note label → the pilot's `**No real version:**` cue (u02 style).
4. `[OPEN]` Should Fix: spell out cell-60 twin placement — reword cell 59 ("first with fixed words, then the
   asking version") → executable twin (fixed stand-in words, identical 5 print lines incl. the `+` title) →
   Notice → existing no-exec cell 60.
5. `[OPEN]` Nice: Ex5 real-form mirrors the solutions twin's `player_name` (starter uses `name`) — note that
   real-forms mirror the twin, or allow the single rename.
6. `[OPEN]` Nice: Ex7 real-form keeps the constraint (exactly three `+` pieces, NO f-string):
   `name = input("Your name: ")` / `greeting = "Hello, " + name + "!"` / `print(greeting)`.

## Content Review
_(pending — 4-way.)_

## Post-Execution Report
_(pending.)_
