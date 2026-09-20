# Plan 058 — u06 secret-codes: full real-input treatment (strings/cipher read-and-compute arm)

**Status:** DRAFT — plan-review gate pending.
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
exists** (cell 47 `message = input("Type a secret message: ")` + Notice cell 48) — L3 is already compliant.
The audit finds **exactly ONE gap:**

| Lesson section | Complete-task compute capstone | Status |
|---|---|---|
| L1 (take the note apart) | none — all cells are single-operation build-up rungs on fixed words (index/slice/methods) | rungs → exempt (§3) |
| **L2 (decode the folded note)** | **cell 31** `coded_note = "nvvg nv zg gsv oryizib"` → atbash scan → prints "meet me at the library" — a complete-task compute capstone processing input-shaped data | **GAP → add a `no-exec input()` real-form** |
| L3 (write a code) | `encode` (cell 43) | **already has** the input real-form (cell 47) — no change |
| Algorithm Extension | two Pattern-Spotlight ladders (linear-search / map) on tiny fixed words | graduated rungs → exempt (§3) |

**The one lesson change:** after cell 31, add a `no-exec` `input()` CODE cell that reads
`coded_note = input("Type the coded note: ")` then runs the UNCHANGED decode scan + print, plus a
`**Notice:** (It reads live input, so it does not run here.)`. Single read, NO loop over the input → `for`/
`while` closure not implicated. The `in`-operator demo cells after 31 are rungs (unchanged). Do NOT touch the
L3 cells (41/43/45/47), L1, or the Algorithm-Extension ladders.

## Per-exercise SHAPE table (22 exercises + 2 challenges)

**Universal real-form rule (as u05):** the markdown `**The real program**` fenced ```python block keeps the
`def`/inline compute UNCHANGED, reads **one `input()` per distinct fixed VALUE** (string → plain `input(...)`;
int → `int(input(...))`), then reproduces the twin's EXACT call+print (BARE call for functions that PRINT
their own output; `print(func(...))` only for return-only). §6b parity compares the **computed-output lines
only** (excl. twin pedagogy/assert prints). **Value-coupled labels:** where a twin's printed line embeds a
value tied to the fixed input (Ex2 "iph", Ex3 "flow", Ex13, Ex21 "sec", Ex22 "r"), the real-form keeps the
**computed expression** (`word[1:4]`, the scan result), NEVER a hardcoded result literal — so piping the
twin's fixed value reproduces the line (the u05-Ex3 rule).

| Shape | Exercises | Real-form / treatment |
|---|---|---|
| **read-and-compute — inline** (read the word/message, unchanged compute+print) | Ex1 reverse [str], Ex2 first/last [str; keep positional `[1:4]`], Ex3 middle [str; positional], Ex4 shout [str], Ex12 count-vowels [str], Ex13 map-each [str], Ex14 find-letter-stop-early [read `target` [str]; `letters` alphabet stays a fixed constant], Ex16 letters/spaces/marks [str], Ex17 first-vowel-pos [str], Ex21 fit-the-budget [read `word` [str] + `budget` **`int(input())`**], Ex22 until-budget-tips [`word` [str] + `budget` **`int(input())`**], Challenge 1 keyword-check [`message` + `keyword`, 2 str] | `**The real program**` markdown block + `**Real version:**` statement cue |
| **read-and-compute — function** | Ex10 compare-two-shifts [**read `message` [str] ONLY; keep shifts fixed at 3 and 5** — reading the shifts would break the twin's "shift 5 moves farther than shift 3" comparison narrative; encode is return-only → `print(encode(message, 3))` / `print(encode(message, 5))`], Ex11 atbash-decode [`message` str; return-only], Ex15 count_letter [`message`+`letter`, 2 str; return-only], Ex18 has_digit [`code` str; return-only; read ONE representative], Ex19 star_vowels [`message` str; return-only], Ex20 letter_value_sum [`word` str; return-only], Challenge 2 two_step [`message` str + `shift` **`int(input())`**; **block must DEFINE `encode` itself** (two_step calls it) so it runs standalone] | `**The real program**` block (def unchanged) + `**Real version:**` cue |
| **interactive / single-read — statement ALREADY reads `input()`** (design §2: the statement IS the real-program form) | Ex5 is-it-a-vowel, Ex6 encode-typed-message [reads `message`; `shift = 3` stays a fixed literal, NOT read], Ex8 secret-word-report, Ex9 classify-code-character [function PRINTS → BARE call] | solutions gain a `**The real program**` model-answer block (reads `input()`); **NO `**Real version:**` cue** on the statement (it is already a real program) |
| **exempt — debug/fix-the-error** (design §1 v5 class 2) | Ex7 fix-the-Caesar-wrap (two `no-exec` buggy cells → IndexError → repair to `% 26` / `last_position = 25`; the repair is the graded task) | NO real-form; `**No real version:**` note (debug/fix-the-error) |

**Counts:** read-and-compute 19 (12 inline + 7 function), interactive/single-read 4 (Ex5/6/8/9), exempt 1 (Ex7). = 24.
Enrichment Ex12–Ex22 still get real-forms (§3 exempts enrichment from *data-growth* only, not the both-forms
rule — the u05 precedent added real-forms to every input-shaped Algorithm-Extension drill); their small fixed
data is untouched.

## Phases

### Phase A — apply to u06 (lesson + exercises + solutions; NO metadata)
- **lesson.ipynb:** add ONE `no-exec` `input()` real-form CODE cell + `**Notice:**` after the L2 decode
  capstone (cell 31, identify by content — the `coded_note = "nvvg …"` cell). Do NOT touch L3 (41/43/45/47),
  L1, or the Algorithm-Extension ladders, or any executable capstone/rung.
- **exercises.ipynb:** `**Real version:**` cue on the 19 read-and-compute exercises; `**No real version:**`
  note (debug/fix-the-error) on Ex7; NO cue on Ex5/6/8/9 (statements already read input).
- **solutions.ipynb:** a `**The real program**` markdown fenced ```python block after each of the 23
  non-exempt exercises' asserted twins (19 read-and-compute + 4 interactive model-answers). Each keeps the
  def/compute unchanged, reads one input per distinct fixed value with the typed idiom, mirrors the twin's
  exact call+print, and keeps value-coupled labels as computed expressions. NO block under Ex7. Fenced
  real-forms must not contain a line starting `## Exercise <digit>`.
- **NO manifest.yaml / coverage-map.yaml / teacher-notes.md change** (input + int-type already in union).

### Phase B — verification
- `ast.parse` + piped-run every real-form (1 lesson no-exec + 23 solutions markdown); the **computed-output
  lines** == the paired twin's computed-output lines modulo `input()` prompt text (design §6a–c). Ex10: piping
  the message reproduces both fixed-shift lines + the comparison text. Challenge 2: the block defines `encode`
  and runs standalone.
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
  (exec-only). Ex10's keep-shifts-fixed decision (read message only) is the value-coupled-narrative fix.

## Plan Review
_(pending — 4-way.)_

## Content Review
_(pending — 4-way, post-implementation.)_

## Post-Execution Report
_(pending.)_
