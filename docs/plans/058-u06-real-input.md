# Plan 058 — u06 secret-codes: full real-input treatment (strings/cipher read-and-compute arm)

**Status:** COMPLETE — both gates CLOSED (4-way); ci-local ALL GREEN; ready to merge.
**Type:** Content — apply the full real-input treatment (design 003 v5) to `unit-06-secret-codes`.
**Branch:** `feature/plan-058-u06-real-input`. **Base:** main @ 4111526.

## Motivation

Rollout slice 8 (design 003 §7 — list-less units). u06 teaches string surgery + ciphers (index/slice/methods,
`in`, transform-each/map, linear-search). Solutions mix **cipher FUNCTIONS** (`encode`/`decode`/`decode_atbash`/
`has_digit`/`star_vowels`/`count_letter`/`letter_value_sum`/`two_step`) called with fixed args (the u05
functions arm) and **inline string compute** on a fixed word/message (reverse/slice/count/scan — the u02/u04
list-less arm). Treatment by **per-exercise audit** (design 003 v5). Authorities: design 003 v5 (§1/§8
exemption taxonomy, §2 form-by-kind, §3 list-less arm, §4 idiom, §6); merged pilots u05 (functions arm,
per-task call shell) + u02/u04 (list-less inline).

**Two u06-specific facts (differ from u05):**
1. **NO metadata change.** `input` AND `int-type` are ALREADY in u06's `practices` (manifest + coverage-map) —
   the L3 lesson capstone already ships a `no-exec input()` real-form (cell 47). §5's `input` add applies only
   to a unit whose union LACKS input; u06 has it. No manifest/coverage-map edit.
2. **Closure: `while-loop` is NOT in u06's union** (u07 first has it) → any lesson/real-form loop uses the `for`
   idiom, never a sentinel `while` (design §4). Not a constraint in practice: the one lesson gap is a single
   read (no loop), and every exercise real-form mirrors existing `for`-scan / single-read code. In-union and
   permitted in real-forms: `for`/`range`/`if`/`elif`/`comparison`/`break`/string-index/slice/methods/
   `in`-operator/`int-type`/f-string/accumulator. Forbidden: `sys.stdin`, `while`, `list`/list-append.

## Lesson both-forms audit (design §1/§8)

The unit's culminating cipher capstone is L3's `encode` (cell 43), whose `no-exec input()` real-form **already
exists** (cell 47 `message = input("Type a secret message: ")`) — BUT that form ships with **no `**Notice:**`
cell** (cell 48 is a partner-activity prompt, not a Notice). Design §2 requires the lesson real-form to pair
its no-exec cell with a Notice. The audit finds **two lesson touches** (both additive — no merged code cell is edited):

| Lesson section | Complete-task compute capstone | Status |
|---|---|---|
| L1 (take the note apart) | none — all cells are **one-new-idea graduated rungs** on fixed words (index/slice/methods; e.g. cell 28 chains `.strip().lower().replace()`) | rungs → exempt (§3) |
| **L2 (decode the folded note)** | **cell 31** `coded_note = "nvvg nv zg gsv oryizib"` → atbash scan → prints "meet me at the library" — a complete-task compute capstone processing input-shaped data | **GAP → add a `no-exec input()` real-form + Notice** |
| **L3 (write a code)** | `encode` (cell 43) → input real-form exists (cell 47) | **add the missing `**Notice:**`** cell after 47 (no code-cell edit) |
| Algorithm Extension | two Pattern-Spotlight ladders (linear-search / map) on tiny fixed words | graduated rungs → exempt (§3) |

**Lesson changes (both additive):**
1. **L2:** after **cell 32** (the trace prompt that discusses cell 31's output — layout: fixed form 31 →
   trace prompt 32 → real-form → Notice), add a `no-exec` `input()` CODE cell that reads
   `coded_note = input("Type the coded note: ")` then runs the UNCHANGED decode scan + print. The cell must be
   **standalone for the piped-run**: include `letters = "abcdefghijklmnopqrstuvwxyz"` (cell 31 defines it).
   Follow it with a `**Notice:** (It reads live input, so it does not run here.)` markdown cell. Single read,
   NO loop over the input → `for`/`while` closure not implicated.
2. **L3:** add ONE `**Notice:** (It reads live input, so it does not run here.)` markdown cell after the L3
   `input()` real-form. **Content-gate correction (round 1):** the pre-existing L3 real-form printed
   `f"Send this code: {coded_message}"` — a §6 parity mismatch with the twin's bare `print(coded_message)`;
   its final line was changed to `print(coded_message)` (the ONLY L3 code-cell edit; cells 41/43/45 untouched).

Identify all cells by CONTENT (the L2 insert shifts later indices by +2). Do NOT edit L1, the L3 code cells
(41/43/45/47), the `in`-operator demo cells, or the Algorithm-Extension ladders.

## Per-exercise SHAPE table (22 exercises + 2 challenges)

**Universal real-form rule (as u05):** the markdown `**The real program**` fenced ```python block keeps the
`def`/inline compute UNCHANGED, reads **one `input()` per distinct fixed VALUE** (string → plain `input(...)`;
int → `int(input(...))`), then reproduces the twin's EXACT call+print (BARE call for functions that PRINT
their own output; `print(func(...))` only for return-only). §6b parity compares the **computed-output lines
only** (excl. twin pedagogy/assert prints). **Multi-value twins reproduce EVERY value** (a twin that prints
two demonstrations reads two values — the u05 multi-call rule). **Value-coupled labels:** where a twin's
printed line embeds a value tied to the fixed input (Ex2 "iph", Ex3 "flow", Ex13, Ex18 `abc3d`/`abcd`, Ex21
"sec", Ex22 "r"), the real-form keeps the **computed expression** (`word[1:4]`, `f"{code} has a digit:
{has_digit(code)}"`, the scan result), NEVER a hardcoded result literal — so piping the twin's fixed value
reproduces the line (the u05-Ex3 rule).

| Shape | Exercises | Real-form / treatment |
|---|---|---|
| **read-and-compute — inline** (read the word/message, unchanged compute+print) | Ex1 reverse [str], Ex2 first/last [str; keep positional `[1:4]`], Ex3 middle [str; positional], Ex4 shout [str], Ex12 count-vowels [str], Ex13 map-each [str], Ex14 find-letter-stop-early [read `target` [str]; `letters` alphabet stays a fixed constant], Ex16 letters/spaces/marks [str], Ex17 first-vowel-pos [str], Ex21 fit-the-budget [read `word` [str] + `budget` **`int(input())`**], Ex22 until-budget-tips [`word` [str] + `budget` **`int(input())`**], Challenge 1 keyword-check [`message` + `keyword`, 2 str] | `**The real program**` markdown block + `**Real version:**` statement cue |
| **read-and-compute — function** | Ex10 compare-two-shifts [**read `message` [str] + `shift_one` + `shift_two` (2× `int(input())`)**; encode return-only. The twin (sol cell 21) prints **FIVE** computed lines — `Shift {s}:`×2, `Same output: {…}`, and two `Shift {s} first: {out[0]}, slice: {out[:3]}` lines — the real-form reproduces ALL FIVE with **computed labels** (piping "Secret zoo!",3,5 → exact); any "moves farther" note is a code COMMENT in the twin, not a printed line], Ex11 atbash-decode [`message` str; return-only], Ex15 count_letter [`message`+`letter`, 2 str; return-only], Ex18 has_digit [**2 codes** — twin prints two lines; read 2 codes, print `f"{code} has a digit: {has_digit(code)}"` for each], Ex19 star_vowels [**2 messages** — twin prints both on one line; read 2 messages, `print(star_vowels(m1), star_vowels(m2))`], Ex20 letter_value_sum [`word` str; return-only], Challenge 2 two_step [`message` str + `shift` **`int(input())`**; **block must DEFINE `encode` itself** (two_step calls it) so it runs standalone] | `**The real program**` block (def unchanged) + `**Real version:**` cue |
| **interactive / single-read — statement ALREADY reads `input()`** (design §2: the statement IS the real-program form) | Ex5 is-it-a-vowel, Ex6 encode-typed-message [reads `message`; `shift = 3` stays a fixed literal, NOT read], Ex8 secret-word-report, Ex9 classify-code-character [function PRINTS → BARE call] | solutions gain a `**The real program**` model-answer block (reads `input()`); **NO `**Real version:**` cue** on the statement (it is already a real program) |
| **exempt — debug/fix-the-error** (design §1 v5 class 2) | Ex7 fix-the-Caesar-wrap (two `no-exec` buggy cells → IndexError → repair to `% 26` / `last_position = 25`; the repair is the graded task) | NO real-form; `**No real version:**` note (debug/fix-the-error) |

**Counts:** read-and-compute 19 (12 inline + 7 function), interactive/single-read 4 (Ex5/6/8/9), exempt 1 (Ex7). = 24.
Enrichment Ex12–Ex22 still get real-forms (§3 exempts enrichment from *data-growth* only, not the both-forms
rule — the u05 precedent added real-forms to every input-shaped Algorithm-Extension drill); their small fixed
data is untouched.

## Phases

### Phase A — apply to u06 (lesson + exercises + solutions; NO metadata)
- **lesson.ipynb (two additive touches, identify cells by content):** (1) after the L2 **trace prompt** (the
  cell after `coded_note = "nvvg …"`), add a `no-exec` `input()` real-form CODE cell (reads `coded_note`,
  includes `letters = "…"` to run standalone) + a `**Notice:**` markdown cell; (2) add ONE `**Notice:**`
  markdown cell after the L3 `no-exec input()` cell (`message = input("Type a secret message: ")`). Do NOT edit
  any merged code cell (L3 41/43/45/47), L1, the `in`-operator demos, or the Algorithm-Extension ladders.
- **exercises.ipynb:** `**Real version:**` cue on the 19 read-and-compute exercises (Ex13 cue: word the
  expected output as "for the fixed message only"); `**No real version:**` note (debug/fix-the-error) on Ex7;
  NO cue on Ex5/6/8/9 (statements already read input).
- **solutions.ipynb:** a `**The real program**` markdown fenced ```python block after each of the 23
  non-exempt exercises' asserted twins (19 read-and-compute + 4 interactive model-answers). Each keeps the
  def/compute unchanged, reads one input per distinct fixed value with the typed idiom, mirrors the twin's
  exact call+print, and keeps value-coupled labels as computed expressions. NO block under Ex7. Fenced
  real-forms must not contain a line starting `## Exercise <digit>`.
- **NO manifest.yaml / coverage-map.yaml / teacher-notes.md change** (input + int-type already in union).

### Phase B — verification
- `ast.parse` + piped-run every real-form (1 lesson no-exec + 23 solutions markdown); the **computed-output
  lines** == the paired twin's computed-output lines modulo `input()` prompt text (design §6a–c). Oracle by shape:
  - **multi-value real-forms** (Ex10 msg+2 shifts, Ex18 2 codes, Ex19 2 messages) read every value and reproduce
    EVERY line the twin prints (Ex10: piping 3/5 → "Shift 3:"/"Shift 5:"; Ex19: one combined line).
  - **statement-is-the-form model answers** whose twin demonstrates MULTIPLE fixtures (Ex5 2 runs, Ex9 3 calls)
    are validated **per-representative**: pipe ONE representative fixture, compare that run's lines to the
    corresponding twin segment (the single-read model answer need not reproduce all of the twin's demo runs).
  - Challenge 2: the block defines `encode` and runs standalone.
- CLOSURE AST scan: real-forms use only in-union concepts (for/range/if/elif/comparison/break/string-index/
  slice/methods/in-operator/int/f-string/accumulator); **NO `sys.stdin`, NO `while`, NO list/list-append**.
- Hygiene: 0 `input()` in any solutions CODE cell; ≥3 non-vacuous assert cells; no fenced `## Exercise <digit>`
  line; lesson L1/L3/Algo-Ext + all executable twins unchanged; manifest/coverage-map/teacher-notes untouched.
- `scripts/ci-local.sh` ALL GREEN (prereq/coverage/concept-scan unaffected — no metadata change).

## Out of scope
- Any Book-1 entry other than u06 (rollout continues per design 003 §7: u08, u09, u10, cp02–04, projects).
  No design-003 amendment (v5 covers the functions + list-less arms + exemption taxonomy). No metadata add, no
  data growth, no rename. Phase B present.
- **Reviewer judgment flagged:** Ex14 (searches a fixed alphabet constant; only `target` is input-shaped) —
  classified read-and-compute (read `target`); a reviewer may argue it is a pure fixed-constant algorithm drill
  (exec-only). Ex10 reads `message` + both shifts (`shift_one`/`shift_two`) with computed labels (resolved in
  round 1 — see the SHAPE row + Phase B; supersedes the initial keep-shifts-fixed idea).

## Plan Review

### Round 1 (2026-09-19) — [self] inline; [sol] gpt-5.6-sol; [glm] volcengine-plan/glm-5.3; [fable] Fable 5.
#### [self] (2026-09-19)
- **Verdict**: APPROVE — grounded in the read-only survey (all 24 statements + solutions + lesson read).
  No metadata change (input+int-type in union, verified); closure = for/single-read (no while in union); lesson
  audit = ONE gap (L2 cell 31; L3 cell 47 already exists; L1/Algo-Ext rungs); SHAPE per taxonomy (Ex7 debug
  exempt; Ex5/6/8/9 statement-is-the-form; 19 read-and-compute; print-fns bare; value-coupled labels kept as
  computed expressions). Two self-flagged judgment forks for the gate:
  - **Ex10** (compare two shifts): I keep the shifts fixed at 3/5 and read the message only, to preserve the
    twin's "shift 5 moves farther than shift 3" comparison + exact §6b parity. A reviewer could argue for
    reading both shifts + generic rewording; flagged.
  - **Ex14** (find-letter-stop-early): reads `target`, treats `letters` alphabet as a fixed constant →
    read-and-compute. A reviewer could argue it is a pure fixed-constant algorithm drill (exec-only); flagged.

#### [fable] (2026-09-19)
- **Verdict**: APPROVE WITH NITS — all 5 claims CONFIRMED against the files (no metadata; closure; ONE lesson
  gap cell 31; SHAPE 12+7+4+1=24; Ex7 debug-exempt; Ex5/6/8/9 statement-is-the-form; Ex10 fixed-shifts agreed;
  Ex14 read target agreed; Phase B present). No Must-Fix. 3 Should + Nice:
1. `[OPEN]` Should: **Ex18/Ex19 multi-value parity** — Ex18 twin (sol 38) prints TWO lines (`abc3d…True`/
   `abcd…False`); Ex19 twin (sol 40) prints both on ONE line (`print(star_vowels("cat"), star_vowels("hello"))`
   → `c*t h*ll*`). A single-read real-form can't reproduce those → **Ex18 reads 2 codes (2 lines), Ex19 reads 2
   messages (one line, both)** — the multi-call rule. Add Ex18 to value-coupled labels (`f"{code} has a digit:
   {has_digit(code)}"`, not literal `abc3d`).
2. `[OPEN]` Should: plan line 30 wrongly calls lesson cell 48 a "Notice" — it's a partner-activity prompt; L3's
   cell 47 input form ships WITHOUT the standard `**Notice:**` parenthetical. → correct the description; accept
   L3 as-shipped (do NOT re-touch merged L3 content); the NEW L2 cell gets the standard Notice.
3. `[OPEN]` Should: insert the new L2 real-form **after cell 32** (the trace prompt for cell 31), not between
   31/32 — layout: fixed form (31) → trace prompt (32) → real-form + Notice (u04 layout).
- Nice: (4) the new L2 no-exec cell should include `letters = "abcdefghijklmnopqrstuvwxyz"` so the piped-run is
  standalone; (5) Ex13 cue: word the expected output as "for the fixed message only"; (6) Ex10 fixed-shifts
  defensible, no change; (7) Challenge 2 encode variant is documentation-only (both give `"!edc"`).

#### [sol] (2026-09-19)
- **Verdict**: REJECT (verified green: no metadata, closure, L2 cell-31 gap, Ex7 debug-exempt, Ex5/6/8/9
  statement-is-the-form, no misclassification, Phase B present). 4 Must + 1 Nice:
1. `[OPEN]` Must: **L3 Notice missing** — cell 48 is partner-prose, not a `**Notice:**`; design §2 requires the
   lesson real-form to have a Notice. Amend "do NOT touch L3" → ADD a `**Notice:**` cell after cell 47.
2. `[OPEN]` Must: **Ex10 read BOTH shifts** — shifts are input-shaped values, not structural constants;
   keeping 3/5 fixed violates the distinct-value rule + §6c. Read `message`+`shift_one`+`shift_two`, computed
   labels `f"Shift {shift_one}: …"` (preserves narrative + exact parity piping 3/5). [Supersedes my keep-fixed
   call; fable Nice #6 confirmed this variant satisfies the rule.]
3. `[OPEN]` Must: **Phase B oracle** — Ex5 twin runs 2 fixtures, Ex9 runs 3; the single-read model reads once →
   specify PER-REPRESENTATIVE validation (run the block per fixture, compare to that twin segment).
4. `[OPEN]` Must: **Ex18/Ex19** (== fable #1) — Ex18 reads 2 codes (both labels computed), Ex19 reads 2
   messages (one line both); add Ex18 to value-coupled labels.
5. `[OPEN]` Nice: L1 "single-operation" → "one-new-idea graduated rungs" (cell 28 chains methods).

#### [glm] (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: REJECT — all 5 core claims verified; 2 Must + 2 Should + 2 Nice (converges with [sol]/[fable]):
1. `[OPEN]` Must: Ex18/Ex19 multi-read (== [sol]#4/[fable]#1) — Ex18 reads 2 codes (both lines, computed
   `f"{code} has a digit: {has_digit(code)}"`), Ex19 reads 2 messages (one combined print); add Ex18 to
   value-coupled list.
2. `[OPEN]` Must: "cell 47 + Notice cell 48" is false (cell 48 = partner prompt; 0 "does not run" in lesson) —
   add one Notice cell after cell 47 (new cell, doesn't edit 41/43/45/47) or reasoned WONTFIX. (== [sol]#1/[fable]#2)
3. `[OPEN]` Should: insert the L2 real-form + Notice after cell 32 (trace prompt), not 31/32. (== [fable]#3)
4. `[OPEN]` Should: interactive model-answer per-representative parity for Ex5 (2 runs)/Ex9 (3 calls). (== [sol]#3)
5. `[OPEN]` Nice: new L2 cell must include `letters = "..."` to piped-run standalone. (== [fable]#4)
6. `[OPEN]` Nice: identify L3 cells by content (indices shift +2 after the L2 insert).
- Note: [glm] concurred with keep-shifts-fixed for Ex10 but verified read-both also satisfies the distinct-value
  rule → resolving to read-both (clears [sol]#2; [fable]/[glm] both accept).

### Round 1 — outcome: REJECT (3 of 4). Fixed → round 2.
**Round 1 responses (plan revised):**
- → [FIXED] L3 Notice ([sol]#1/[glm]#2/[fable]#2): ADD a `**Notice:**` markdown cell after cell 47 (new cell,
  does not edit L3's code cells 41/43/45/47); corrected the audit's false "Notice cell 48" claim.
- → [FIXED] Ex10 ([sol]#2): read `message`+`shift_one`+`shift_two`, computed labels `f"Shift {shift_one}: …"`
  (satisfies distinct-value rule + exact parity piping 3/5; any "which moved farther" observation is the
  exercise's written question / computed, not a hardcoded universal claim). Reclassified read-and-compute-function (3 reads).
- → [FIXED] Ex18/Ex19 ([sol]#4/[glm]#1/[fable]#1): Ex18 reads 2 codes → 2 computed-label lines (added to
  value-coupled list); Ex19 reads 2 messages → one combined print.
- → [FIXED] Phase B oracle ([sol]#3/[glm]#4): multi-call real-forms (Ex10/Ex18/Ex19) reproduce EVERY call;
  statement-is-the-form model answers (Ex5 2-run, Ex9 3-call) validated PER-REPRESENTATIVE (pipe one fixture,
  compare that run's segment).
- → [FIXED] Insertion after cell 32 ([glm]#3/[fable]#3); new L2 cell includes `letters="…"` standalone
  ([glm]#5/[fable]#4); L3 cells identified by content ([glm]#6); L1 "one-new-idea graduated rungs" ([sol]#5);
  Ex13 cue "for the fixed message only" ([fable] Nice #5).
Re-dispatching round 2.

### Round 2 (2026-09-19) — re-review after round-1 fixes (dad6ccf)
#### [fable] round 2 (2026-09-19)
- **Verdict**: APPROVE — all 5 round-1 findings verified resolved; Ex10 read-both-shifts sound (the "moves
  farther" note is a code COMMENT, not a printed line → no parity issue). 1 non-blocking nit FOLDED:
  Ex10's twin (sol cell 21) prints FIVE computed lines (Shift×2 / Same output / two first+slice) — the SHAPE
  row now enumerates all five with computed labels (the universal rule + Phase B already required reproducing
  every line). No regressions.

#### [sol] round 2 (2026-09-19)
- **Verdict**: REJECT — sole finding: the Out-of-scope reviewer-judgment note (line 118) still said "Ex10 keeps
  shifts fixed / reads message only", contradicting the revised SHAPE + Phase B. All other round-1 findings
  resolved, no other regressions. → `[FIXED]`: line 118 rewritten to "reads message + both shifts, computed
  labels (supersedes keep-shifts-fixed)". Re-confirming [sol] round 3.

#### [glm] round 2 (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: APPROVE WITH NITS — all 6 round-1 findings verified FIXED against the files; Ex10 read-both
  confirmed (twin prints 5 computed lines, reproduced exactly piping 3/5; "moves farther" is a comment/written
  question, not a printed claim). 2 non-blocking findings, **both already resolved in commit 87eeff4** (which
  post-dated [glm]'s dad6ccf review): (1) stale Ex10 line 118 → fixed to read-both; (2) Ex10 first/slice labels
  → the five-line clarification names them. No open blockers.

#### [sol] round 3 (2026-09-19)
- **Verdict**: APPROVE — the Out-of-scope note now reads "Ex10 reads message + both shifts, computed labels";
  SHAPE row + Phase B consistent. No remaining contradiction.

### PLAN-REVIEW GATE CLOSED (2026-09-19) — 4-way consensus:
[self] APPROVE · [sol] APPROVE (round 3) · [glm] APPROVE WITH NITS (nits resolved in 87eeff4) · [fable] APPROVE
(round 2). No open blockers.

## Content Review

4-way, on the implementation commit ea82640. Tags [self]/[sol]/[glm]/[fable].

#### [self] (2026-09-19)
- **Verdict**: APPROVE. Spot-checked the bug-prone real-forms + new lesson cells: Ex10 (sol 30 — reads
  message + 2 int shifts, reproduces all FIVE computed-label lines); Ex18 (sol 55 — 2 codes, computed labels);
  Ex19 (sol 58 — 2 messages, one combined `print(star_vowels(m1), star_vowels(m2))`); L2 real-form (les 33 —
  `no-exec`, standalone `letters="…"`, for-loop decode, single read); both Notices (les 34/50) exact. 0
  `input()` in any solution CODE cell. No metadata change; L2 real-form + L3 Notice are additive (pre-existing
  cells unchanged). ci-local ALL GREEN (493 passed; exec-solutions + exec-lessons PASS — kernel validated the
  new no-exec cell).

#### [fable] (2026-09-19)
- **Verdict**: APPROVE — no `[OPEN]` findings (mechanical: ast.parse + closure AST walk + piped-run parity per
  real-form). All 25 real-forms parse + match twins (Ex10 5 lines; Ex18/Ex19 multi-read; Ex5/Ex9
  per-representative first segment; Ch2 standalone encode → `!edc`; value-coupled labels all computed). Lesson
  70→73 cells, added [33,34,50] only, pre-existing cells identical; 19 Real cues + 1 Ex7 No-real; metadata zero
  diff; 0 input() in solutions code cells, 24 non-vacuous assert cells, no fenced `## Exercise <digit>`. Ready for PR.

#### [sol] (2026-09-19)
- **Verdict**: REJECT — 1 Must Fix (all other checks passed):
1. `[OPEN]` Must: the PRE-EXISTING L3 no-exec real-form (lesson cell 49) printed `f"Send this code:
   {coded_message}"` while its executable twin (cell 45) prints the bare `coded_message` → §6 parity mismatch
   (real-form output `Send this code: phhw ph dw 4!` ≠ twin `phhw ph dw 4!`).
   → `[FIXED]`: changed cell 49's final line to `print(coded_message)` (now line-for-line the twin). This is a
   gate-driven one-line correction to a pre-existing merged no-exec cell (the L3 input form predates the
   systematic norm) — amends the plan's "do NOT touch L3 code cells" note for this cell only; no other L3 edit.
   Re-confirming [sol].

#### [glm] (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: APPROVE — no defects; verified all 24 forms (ast.parse + closure + piped parity; Ex5/Ex9
  per-representative; Ch2 standalone; value-coupled labels computed), lesson additive (only [33,34,50]), 19
  Real + 1 No-real cues, metadata untouched, 0 input() in solutions code cells; re-ran book1 checks incl.
  exec-solutions/exec-lessons — ALL PASS; blind-solve cross-check matched twins. (Reviewed ea82640 — did not
  flag the L3 "Send this code:" form that [sol] Must-Fixed; the round-1 parity correction is a strict
  improvement that does not affect anything [glm] verified.) 1 `[WONTFIX]` out-of-scope: pre-existing u02
  non-unique cell ids (`u2-ex8-*`) — nbformat warning, checks still PASS, future cleanup.

#### [sol] re-confirm (2026-09-19)
- **Verdict**: APPROVE — L3 real-form final line now `print(coded_message)`; piping "Meet me at 4!" reproduces
  the twin's `phhw ph dw 4!` exactly. Nothing else regressed.

### Content-review gate — outcome: **CLOSED** — 4-way consensus:
[self] APPROVE · [sol] APPROVE (after the L3 parity one-line fix) · [glm] APPROVE · [fable] APPROVE. No `[OPEN]`
findings remain. (Pre-existing u02 `DuplicateCellId` noted for a future cleanup plan — out of scope here.)

## Post-Execution Report

**Shipped (2026-09-19).** u06 secret-codes given the full real-input treatment (design 003 v5): strings/cipher
read-and-compute arm (functions + inline), **no metadata change** (`input`/`int-type` already in the union).

**What changed (3 notebooks):**
- `lesson.ipynb` (70→73 cells, additive): new L2 decode `no-exec input()` real-form + Notice (after the trace
  prompt); L3 gains its missing Notice; **content-gate correction** — the pre-existing L3 real-form's
  `print(f"Send this code: …")` → `print(coded_message)` (§6 parity with its twin). No other merged cell edited.
- `solutions.ipynb`: 23 `**The real program**` markdown real-forms (per-task call shell; Ex10 reads msg + 2
  shifts → 5 computed-label lines; Ex18 2 codes; Ex19 2 messages one line; Ex5/6/8/9 model answers; Ch2
  self-contained `encode`; value-coupled labels kept as computed expressions).
- `exercises.ipynb`: 19 `**Real version:**` cues + 1 `**No real version:**` (Ex7 debug/fix-the-error).

**Verification:** `scripts/ci-local.sh` ALL GREEN — 493 passed / 2 skipped; exec-solutions + exec-lessons PASS
(kernel validated the new L2 no-exec cell + Notices); manifest/prereq/coverage/concept-scan/technique-spiral
PASS (no metadata change); PDF + guard OK. All 25 real-forms piped-run-match their twins (multi-value forms
reproduce every line; Ex5/Ex9 per-representative). 0 `input()` in solutions CODE cells; no fenced `## Exercise
<digit>`.

**Gates:** plan-review CLOSED (4-way, 3 rounds); content-review CLOSED (4-way; 1 L3-parity fix).

**Rollout status (design 003 §7):** merged — u04, u07 (list), cp01, u02, u01, u03 (turtle), u05 (functions),
**u06 (strings/ciphers)**. Remaining: u08 (word-wizard), u09 (files), u10 (classes); checkpoints cp02–cp04;
projects. u06 confirmed the functions + inline list-less arms compose cleanly, and that a unit already carrying
`input` in its union needs no metadata add (only the per-unit lesson-gap audit + Notices).
