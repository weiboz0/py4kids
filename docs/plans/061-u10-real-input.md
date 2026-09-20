# Plan 061 — u10 pet-simulator: full real-input treatment (classes: construct-and-drive)

**Status:** DRAFT — plan-review gate pending.
**Type:** Content — apply the full real-input treatment (design 003 v6) to `unit-10-pet-simulator`.
**Branch:** `feature/plan-061-u10-real-input`. **Base:** main @ 1bbd017.

## Motivation

Rollout slice 11 (design 003 §7) — **the LAST Book-1 unit.** u10 introduces classes (class-def/init-method/
attributes/methods). Solutions **construct and drive** objects (a `Pet` with `__init__` + `feed`/`play`/
`pass_time`/`status`/`show_trick`). Treatment by **per-exercise audit** (design 003 v6). The norm fits classes
directly: the "real program" reads the **constructor arg (pet name)** and/or **method inputs** (feed amount,
food-key, hunger, happiness) then constructs/drives the object — line-for-line the fixed twin with fixed values
→ `input()` reads (§6c). **No design fork / no new exemption class.** Authorities: design 003 v6; merged pilots
u05 (per-task call shell), u07 (list arm), u09 (read-into-list, §3 growth, decorative-input upgrade).

**Three u10-specific facts:**
1. **NO metadata change** — **`input` is ALREADY in u10's union** (manifest + coverage-map `practices`), so the
   §5 add is NOT triggered even though the lesson gains no-exec `input()` cells. Verified: `input`,
   `sentinel-loop`, `while-loop`, `break-statement` all already in union. No other new concept appears in any
   real-form → **no manifest/coverage-map change at all.**
2. **u10 HAS `while-loop` + `sentinel-loop`, LACKS `range-function`** → the read-into-list idiom is a **sentinel
   `while` loop** (`while True: entry = input(...); if entry == "": break; pets.append(Pet(entry))`) or a
   **fixed-count `.append(input())` ×N**, NEVER `for i in range(n)` (opposite of u09). Interactive play/command
   loops are in-union and natural. Single scalars: `int(input())`.
3. **NO `.split()`** (Book-2 concept — verified absent). Methods used: `.append`/`.get` (taught) + student-
   defined class methods. Forbidden in real-forms: `.split()`, `range-function`, `sys.stdin`, any method outside
   u10's taught set. In-union: classes/methods, `while`/sentinel/`break`, `for`/list-loop, list-append/index/
   literal, dict-access/literal, if/elif/comparison, accumulator, find-extreme, filter-into-list, int-type, input.

## Metadata change — NONE

`input` (+ sentinel-loop, while-loop) already in u10's `practices`. The 3 new lesson `no-exec input()` cells use
only in-union concepts → NO add to manifest.yaml / coverage-map.yaml. (Contrast u05/u08/u09 which added `input`.)

## Lesson both-forms audit (design §1/§8)

L1 (meet-your-pet) + L2 (methods) are one-increment build-up rungs → no form. The **3 L3 put-it-together
capstones each process input-shaped data → each gains a `no-exec input()` real-form + `**Notice:** (It reads
live input, so it does not run here.)`** (placed after the capstone, not splitting a ladder):

| L3 capstone (by content) | Real-form |
|---|---|
| foods-dict feed capstone (`foods = {...}` → `buddy.feed(foods["steak"])` → status) | read `name` + `food = input("Which food? ")`; the `foods` dict stays a fixed fixture; `buddy = Pet(name)`; `buddy.feed(foods[food])`; status |
| build-a-pet-list capstone (`pets=[]` + append Rex/Mochi/Ziggy → pass_time+status loop) | read names via **sentinel `while`** (or fixed-count `.append(Pet(input()))`, NO range) into `pets`, then the unchanged loop — **§3: grow to ≥4 names** |
| play-until-happy capstone (`while buddy.happiness < 10: buddy.play()`) | read `name` → `Pet(name)` → the unchanged play loop |

The AttributeError "study, do not run" demo (cell 29/30) → **predict/trace exempt (§1 class 3)**, no form.
**Metadata impact: NONE** (input already in union). Identify cells by CONTENT.

## Per-exercise SHAPE table (26 exercises; ids from survey)

Real-form rule as prior units (per-task shell; one read per distinct fixed value; mirror the twin's exact
construct+drive+print; multi-value twins read every value; value-coupled outputs kept computed). Read-into-list
via sentinel `while`/fixed-count `.append` — NO range. NO `.split()`.

| Shape | Exercises | Treatment |
|---|---|---|
| **class-construct / method (read the args)** | Ex1 make-a-pet (read name), Ex2 two-pets (read 2 names; multi-value), Ex3 feed-method (name + `int(input())` amount), Ex4 mood-ladder (name + `int(input())` hunger; "hungry" stays computed), Ex6 feed-from-foods (read name; `meals`/`treats` dicts + the `treats["fish"]=3` mutation stay the graded fixture), Ex10 three-snack-stops (read name; `snacks` dict fixed) | `**The real program**` block + `**Real version:**` cue |
| **class + read-into-list of Pets** (sentinel/`.append`, NO range) | Ex5 make-a-pet-list (**§3 grow 2→≥4**), Ex11 pet-roll-call (**§3 grow 3→≥4**; per-pet index hunger-settings stay), + Alg-Ext Ex13–Ex24 (enrichment "small fixed data" — STAY small, real-forms carry realism via the read): Ex13 happiest (read (name,happiness) pairs → find-extreme), Ex14 play-until-happy (name → play loop), Ex15 list-happy (pairs; `threshold=7` → `int(input())`), Ex16 count-hungry (N hungers), Ex17 hunger-total (N hungers), Ex18 find-by-name (N names + **target** — multi-value), Ex19 roll-call (N names), Ex20 hungriest+least (N (name,hunger) pairs; seed-from-pets[0] stays), Ex21 mood-tally (N moods → `.get` tally — moods ARE data, read them), Ex22 feed-until-overfeed (hunger + N snacks), Ex23 feed-until-negative (**PAIRED with Ex22 — read identical shape**), Ex24 feed-every-hungry (N hungers → transform), Ex25 talent-show (stretch; (name,trick) pairs), Ex26 pet-care-list (stretch; names; `foods` fixed) | `**The real program**` block + `**Real version:**` cue |
| **upgrade decorative-input → genuine real-form** | Ex7 type-a-name (existing no-exec cell reads a name then IGNORES it → make it USE the name), Ex9 feed-a-team (**§3 grow 2→≥4**; read names into list, feed from `foods` fixture), Ex12 run-a-pet-day (In-Class Finale; read name → construct → drive all 4 methods) | replace the decorative read with a genuine `**The real program**` block that USES the value; `**Real version:**` cue |
| **exempt — debug/fix-the-error** (§1 class 2) | Ex8 run/read/fix AttributeError (`hapiness`→`happiness`; the repair is the graded act) | `**No real version:**` (debug/fix-the-error) |

**Counts:** 25 real-forms (Ex1–7, Ex9–26 minus Ex8) + 3 lesson no-exec = 28 real-forms; 1 exempt (Ex8). No
fixed-reference-fixture exemptions (every fixture-bearing task also constructs a pet → input-shaped). Solutions
real-forms = 25.

## Data growth (§3 — <4-element core SOURCE pet-lists)

Grow the core (non-enrichment) pet-lists whose NAME source-count is <4 to **≥4 (target 5)**, updating asserts/
printed outputs/paired real-forms/statement expected-value lines in lockstep:
- **Ex5** (2 pets Ivy/Rocket — prohibited 2-element) → ≥4. **Ex9** (2 pets Mochi/Pip — prohibited) → ≥4.
- **Ex11** (3 pets — add the missing per-pet hunger-settings for the new pets + update asserts) → ≥4.
- **Lesson build-a-pet-list capstone** (3 pets Rex/Mochi/Ziggy) → ≥4.
Enrichment Alg-Ext Ex13–Ex24 stay small (their real-forms carry arbitrary-count realism via the read). Ex6's
2-entry food dicts are the graded dict fixture — leave. Growth governs SOURCE (name) lists, not computed results.

## Phases

### Phase A — apply to u10 (lesson + exercises + solutions; NO metadata)
- **§3 growth FIRST:** grow the 4 core <4-element pet-lists (Ex5, Ex9, Ex11, lesson capstone) to ≥4, updating
  asserts/outputs/statements in lockstep.
- **lesson.ipynb:** add a `no-exec input()` real-form + `**Notice:**` after each of the 3 L3 capstones (foods-
  feed reads name+food; build-a-pet-list reads names via sentinel/`.append` into the grown list; play-until-happy
  reads name). L1/L2 rungs + the AttributeError demo unchanged. NO metadata change.
- **exercises.ipynb:** `**Real version:**` cue on the 25 real-form exercises; `**No real version:**` note on Ex8
  (debug/fix-the-error). For Ex7/Ex9/Ex12, the upgrade may adjust the existing decorative no-exec cell's compute
  to USE the read value (or add the model-answer block in solutions) — keep the graded task intact.
- **solutions.ipynb:** `**The real program**` block after each of the 25 real-form twins (construct-and-drive
  reads; read-into-list via sentinel/`.append`, NO range; multi-value twins read every value; Ex22↔Ex23 identical
  read shape; value-coupled outputs computed). NO block under Ex8. No fenced `## Exercise <digit>` line.
- **teacher-notes.md:** no change.

### Phase B — verification
- The 4 §3-grown twins re-run clean under `exec-solutions`/`exec-lessons` with updated asserts/outputs.
- `ast.parse` + piped-run every real-form (3 lesson no-exec + 25 solutions markdown); computed-output lines ==
  the (grown) twin's modulo prompt text (§6a–c). Read-into-list: pipe the names/values (sentinel: values then a
  blank line to break; or the fixed count). Multi-value twins reproduce every value; Ex22/Ex23 same shape.
- CLOSURE AST scan: real-forms use only in-union concepts; **NO `range`, NO `.split()`, NO `sys.stdin`, NO method
  outside u10's taught set.**
- Hygiene: 0 `input()` in solutions CODE cells; ≥3 non-vacuous assert cells; no fenced `## Exercise <digit>`;
  lesson rungs + AttributeError demo + all executable twins (except the 4 §3-grown) unchanged; teacher-notes untouched.
- Metadata: NO change; concept-scan/prereq/coverage/technique-spiral GREEN (both books).
- `scripts/ci-local.sh` ALL GREEN.

## Out of scope
- Any Book-1 entry other than u10. NO metadata change (input already in union); NO `.split()`/Book-2/design
  change (classes fit v6). **§3 growth of the 4 core <4-element pet-lists IS in scope.** No rename. Phase B present.
  After u10, remaining rollout: checkpoints cp02–cp04, projects project-01/project-02.
- **Reviewer-judgment flagged:** the Ex7/Ex9/Ex12 decorative-input UPGRADE approach (genuine real-form vs
  statement-is-the-form §2); whether the 3-element Ex11/lesson lists must grow (proposal: yes, §3 "n=3 is toy");
  the sentinel-vs-fixed-count read-into-list choice per exercise (gate ratifies).

## Plan Review
_(pending — 4-way.)_

## Content Review
_(pending — 4-way, post-implementation.)_

## Post-Execution Report
_(pending.)_
