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
   `sentinel-loop`, `while-loop`, `break-statement`, `int-type` all already in union. **`int()` in the numeric
   real-forms is `type-conversion`** — a TAUGHT Book-1 concept (introduced u02), prereq-valid for u10, and it is
   `MANUAL_ONLY` in concept-scan. It is NOT in u10's own `practices` list, but that triggers **no add**: it
   appears ONLY in solutions MARKDOWN real-forms (invisible to concept-scan) and in NO lesson no-exec cell (the 3
   lesson capstones read only STRINGS — names/food-keys). So: no metadata change; `int()` is prereq-valid, not a
   closure violation (contrast the untaught `.split()`).
2. **u10 HAS `while-loop` + `sentinel-loop`, LACKS `range-function`** → the read-into-list idiom is the **TAUGHT
   sentinel shape** (u02 lesson precedent — `while guess != secret:`), i.e. **prime-read + `while … != "":`**:
   `name = input("Pet name (blank to stop)? ")` / `while name != "": pets.append(Pet(name)); name = input(...)`
   — NOT `while True: … break` (never taught in a Book-1 lesson) and NOT `for i in range(n)` (u10 lacks range).
   Where a task's graded point IS a `break` boundary (Ex22/Ex23), use a **fixed-count read** for the values so
   the ONLY `break` is the graded one. **Apply ONE sentinel shape across all read-into-list real-forms.** Single
   scalars: `int(input())`.
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
| foods-dict feed capstone (`foods = {...}` → `buddy.feed(foods["steak"])` → status) | read `name` + `food = input("Which food? ")`; the `foods` dict stays a fixed fixture; `buddy = Pet(name)`; `buddy.feed(foods[food])`; status. Notice adds "(type a food that is in the table)" — `foods[food]` KeyErrors on a mistyped key; do NOT switch to `.get` (that would change the twin) |
| build-a-pet-list capstone (`pets=[]` + append Rex/Mochi/Ziggy → pass_time+status loop) | read names via the **taught sentinel** (`name = input(...)` / `while name != "": pets.append(Pet(name)); name = input(...)`) into `pets`, then the unchanged loop — **§3: grow to ≥4 names** |
| play-until-happy capstone (`while buddy.happiness < 10: buddy.play()`) | read `name` → `Pet(name)` → the unchanged play loop |

The AttributeError "study, do not run" demo (cell 29/30) → **predict/trace exempt (§1 class 3)**, no form.
**Metadata impact: NONE** (input already in union). Identify cells by CONTENT.

## Per-exercise SHAPE table (26 exercises; ids from survey)

Real-form rule as prior units (per-task shell; one read per distinct fixed value; mirror the twin's exact
construct+drive+print; multi-value twins read every value; value-coupled outputs kept computed). Read-into-list
via sentinel `while`/fixed-count `.append` — NO range. NO `.split()`.

| Shape | Exercises | Treatment |
|---|---|---|
| **class-construct / method (read the args)** | Ex1 make-a-pet (read name), Ex2 two-pets (read 2 names; multi-value), Ex3 feed-method (name + `int(input())` amount), Ex4 mood-ladder (name + `int(input())` hunger; "hungry" stays computed), Ex6 feed-from-foods (read name **+ the food-key** — `buddy.feed(meals[input("Meal? ")])` / `treats[input("Treat? ")]` so the read affects output; `meals`/`treats` dicts + the `treats["fish"]=3` mutation stay the graded fixture), Ex10 three-snack-stops (read name **+ the snack-key each stop** — `snacks[input("Snack? ")]`; `snacks` dict fixed) | `**The real program**` block + `**Real version:**` cue |
| **class + read-into-list of Pets** (sentinel/`.append`, NO range) | Ex5 make-a-pet-list (**§3 grow 2→≥4**), Ex11 pet-roll-call (**§3 grow 3→≥4**; per-pet index hunger-settings stay), + Alg-Ext Ex13–Ex26 (enrichment "small fixed data" — STAY small, real-forms carry realism via the read): Ex13 happiest (read (name,happiness) pairs → find-extreme), Ex14 play-until-happy (name → play loop), Ex15 list-happy (pairs; `threshold=7` → `int(input())`), Ex16 count-hungry (N hungers), Ex17 hunger-total (N hungers), Ex18 find-by-name (N names + **target** — multi-value; the real-form prints the READ target, not the twin's hardcoded "Mia" — parity modulo prompt), Ex19 roll-call (N names), Ex20 hungriest+least (N (name,hunger) pairs; seed-from-pets[0] stays), Ex21 mood-tally (N moods → `.get` tally — moods ARE data, read them), Ex22 feed-until-overfeed (hunger + snacks via **FIXED-COUNT reads**, NOT a sentinel — the graded `break` boundary must be the ONLY break), Ex23 feed-until-negative (**PAIRED with Ex22 — identical FIXED-COUNT read shape**), Ex24 feed-every-hungry (N hungers → transform), Ex25 talent-show (stretch; (name,trick) pairs), Ex26 pet-care-list (stretch; **read (name, food-key) pairs** — the twin feeds each pet a DIFFERENT food by index, so read pairs and feed inside the loop, NOT names-only) | `**The real program**` block + `**Real version:**` cue |
| **upgrade decorative-input → genuine real-form** | Ex7 type-a-name (existing no-exec cell reads a name then IGNORES it → make it USE the name), Ex9 feed-a-team (**§3 grow 2→≥4**; read names into list, feed from `foods` fixture), Ex12 run-a-pet-day (In-Class Finale; read name → construct → drive all 4 methods) | replace the decorative read with a genuine `**The real program**` block that USES the value; `**Real version:**` cue |
| **exempt — debug/fix-the-error** (§1 class 2) | Ex8 run/read/fix AttributeError (`hapiness`→`happiness`; the repair is the graded act) | `**No real version:**` (debug/fix-the-error) |

**Counts:** 25 real-forms (Ex1–7, Ex9–26 minus Ex8) + 3 lesson no-exec = 28 real-forms; 1 exempt (Ex8). No
fixed-reference-fixture exemptions (every fixture-bearing task also constructs a pet → input-shaped). Solutions
real-forms = 25.

## Data growth (§3 — <4-element core SOURCE pet-lists)

Grow the core (non-enrichment) pet-lists whose NAME source-count is <4 to **≥4 (target 5)**, updating asserts/
printed outputs/paired real-forms/statement expected-value lines in lockstep:
- **Ex5** (2 pets Ivy/Rocket — prohibited 2-element) → ≥4. **Ex9** (2 pets Mochi/Pip — prohibited) → ≥4.
- **Ex11** (3 pets → 5; leave the two NEW pets at default hunger 5 = "content" — the statement only mandates
  indexes 0/1's settings; update the "append N pets" statement + `pets[2].name`/`assert` + `moods` length).
- **Lesson build-a-pet-list capstone** (3 pets Rex/Mochi/Ziggy) → ≥4.
Enrichment Alg-Ext Ex13–Ex26 stay small (incl. the Ex25/Ex26 stretch drills) (their real-forms carry arbitrary-count realism via the read). Ex6's
2-entry food dicts are the graded dict fixture — leave. Growth governs SOURCE (name) lists, not computed results.

## Phases

### Phase A — apply to u10 (lesson + exercises + solutions; NO metadata)
- **§3 growth FIRST:** grow the 4 core <4-element pet-lists (Ex5, Ex9, Ex11, lesson capstone) to ≥4, updating
  asserts/outputs/statements in lockstep.
- **lesson.ipynb:** add a `no-exec input()` real-form + `**Notice:**` after each of the 3 L3 capstones (foods-
  feed reads name+food; build-a-pet-list reads names via sentinel/`.append` into the grown list; play-until-happy
  reads name). L1/L2 rungs + the AttributeError demo unchanged. NO metadata change.
- **exercises.ipynb:** `**Real version:**` cue on the 25 real-form exercises; `**No real version:**` note on Ex8
  (debug/fix-the-error). **Ex7/Ex9/Ex12 upgrade (definitive):** their `no-exec` cells are EMPTY student cells
  whose STATEMENTS direct a decorative name-read. Rewrite the STATEMENT/cue so it asks for a genuine real program
  that USES the read value (construct `Pet(input(...))`, drive, print); the student `no-exec` code cell stays
  **solution-free**; the COMPLETE program goes in `solutions.ipynb` as the `**The real program**` model block.
  (NOT statement-is-the-form — a read the program discards is the "programs look fake" problem the norm fixes.)
- **solutions.ipynb:** `**The real program**` block after each of the 25 real-form twins (construct-and-drive
  reads; read-into-list via sentinel/`.append`, NO range; multi-value twins read every value; Ex22↔Ex23 identical
  read shape; value-coupled outputs computed). NO block under Ex8. No fenced `## Exercise <digit>` line.
- **teacher-notes.md:** no change.

### Phase B — verification
- The 4 §3-grown twins re-run clean under `exec-solutions`/`exec-lessons` with updated asserts/outputs.
- `ast.parse` + piped-run every real-form (3 lesson no-exec + 25 solutions markdown); computed-output lines ==
  the (grown) twin's modulo prompt text (§6a–c). Read-into-list: pipe the names/values (sentinel: values then a
  blank line to break; or the fixed count). Multi-value twins reproduce every value; Ex22/Ex23 same shape.
- CLOSURE AST scan: real-forms use only **prereq-valid** concepts (u10 union + earlier-taught, incl. `int()`=
  type-conversion from u02); **NO `range`, NO `.split()`, NO `sys.stdin`, NO method outside the taught set.**
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

### Round 1 (2026-09-20) — [self] inline; [sol] gpt-5.6-sol; [glm] volcengine-plan/glm-5.3; [fable] Fable 5.
#### [self] (2026-09-20)
- **Verdict**: APPROVE — grounded in the read-only u10 survey. NO metadata change (input+sentinel+while already
  in union — verified); closure = sentinel/`.append` read-into-list (u10 lacks range), no `.split()`; classes
  fit v6 (construct-and-drive) with NO design fork; 3 L3 capstones gain no-exec input() forms; SHAPE 25
  real-forms + Ex8 debug-exempt; §3 grows the 4 core <4-element pet-lists. Self-flagged judgment forks:
  - **Ex7/Ex9/Ex12 decorative-input UPGRADE** (genuine real-form that USES the read value) vs statement-is-the-
    form (§2). Recommend upgrade (norm intent); gate ratifies.
  - **3-element Ex11/lesson lists grow?** Proposal yes (§3 calls n=3 toy); the 2-element Ex5/Ex9 must grow.
  - **sentinel `while` vs fixed-count `.append`** per exercise — gate ratifies.

#### [fable] (2026-09-20)
- **Verdict**: APPROVE WITH NITS — no Must-Fix; verified all 6 asks (no-metadata, closure enforceable [range in
  a no-exec cell WOULD fail concept-scan], lesson audit, §3 set = exactly the 4 <4-elt lists, Phase B). 5 Should
  + 4 Nice, all FOLDED: (1) sentinel shape pinned to the TAUGHT `while name != "":` prime-read (not un-taught
  `while True:/break`); (2) Ex22↔Ex23 use FIXED-COUNT reads so the only break is the graded boundary; (3)
  Ex6/Ex10 read the food/snack KEY too (a name-only read leaves output unaffected = fake); (4) Ex26 reads
  (name,food) pairs (twin feeds each pet a different food by index); (5) Ex7/9/12 upgrade un-hedged (rewrite the
  no-exec cell into the complete real program); Ex11 grows leaving new pets at default hunger 5; Ex18 prints the
  read target; lesson foods Notice adds "type a food in the table" (KeyError).

#### [sol] (2026-09-20)
- **Verdict**: REJECT (verified green: input/sentinel/while/break in union, no range/.split in solutions, 3 L3
  capstones, Ex8 exempt, §3 set correct, Phase B). 1 Must + 1 Should + 1 Nice, all FOLDED:
1. `[FIXED]` Must: `int()` = `type-conversion` isn't in u10's practices → corrected the "only in-union" wording:
   int() is a TAUGHT concept (u02), prereq-valid, MANUAL_ONLY, appears ONLY in solutions markdown + no lesson
   no-exec cell (those read strings) → no add, no closure violation (unlike untaught .split()). Phase B closure
   scan reworded to "prereq-valid concepts (incl. int()/type-conversion from u02)".
2. `[FIXED]` Should: Ex7/9/12 no-exec cells are EMPTY student cells → upgrade = rewrite the STATEMENT/cue + put
   the complete program in solutions markdown; student cell stays solution-free (was wrongly "rewrite the cell").
3. `[FIXED]` Nice: enrichment span Ex13–24 → Ex13–26 (Ex25/26 stretch drills also stay small).

#### [glm] (pending)

## Content Review
_(pending — 4-way, post-implementation.)_

## Post-Execution Report
_(pending.)_
