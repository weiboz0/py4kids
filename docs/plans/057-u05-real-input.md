# Plan 057 — u05 function-factory: full real-input treatment (functions read-and-compute arm)

**Status:** DRAFT — plan-review gate pending.
**Type:** Content — apply the full real-input treatment (design 003 v4) to `unit-05-function-factory`.
**Branch:** `feature/plan-057-u05-real-input`. **Base:** main @ 0111f31.

## Motivation

Rollout slice 7 (design 003 §7 — list-less units). u05 introduces `def`/`parameters`/`return`/`scope`; its
solutions are **functions called with fixed arguments + asserts** (plus a few headless turtle-count
compute-and-print cells: Ex6/Ex9/Ex10, the u03 pattern). Treatment by **per-exercise audit** (design 003 v4):

- **Functions read-and-compute (the norm here):** keep the `def … return` **unchanged**, READ the
  argument(s) up front, then **call the function and print the result**. Type per parameter:
  **string → plain `input(...)`**; **int → `int(input(...))`**; **float (e.g. `area`'s `2.5`/`4.5`) →
  `float(input(...))`** (`float-type` is in u05's union). One read per parameter, labeled prompts (no `{i}`
  index — u05 has no lists).
- **Headless-compute read-and-compute** (Ex6/Ex9/Ex10 — no `def`, fixed shape param → counts): read the
  param(s), then the unchanged compute + print (the u03 arm).
- **Reads-nothing / generator → exempt** (design §1/§8 v4): Challenge 2 (a *written plan* + *predict* of a
  turtle **flower drawing**, kept in a markdown fence, "do not run turtle here") — no real-form.

**Key per-unit difference from u03:** u05's concept union **includes `if-statement`/`elif-else`/`comparison`/
`while-loop`/`break-statement`** (they appear inside `def` bodies — Ex16/17 `if`, Ex18 `while`). So real-forms
**may legitimately contain if/while/comparison/break** (they are in-union); the closure scan forbids only
`sys.stdin` and any **out-of-union** concept — NOT if/while (contrast u03, which banned them because u03's
union lacked them). Authorities: design 003 **v4** (§1/§8 exemption, §5 per-unit audit, §2/§3 list-less arm,
§6); merged pilots u02/u04 (list-less read-and-compute) + u03 (headless compute + drawing exemption).

## Metadata change (§5 v4 — input add IS triggered for u05)

Unlike u03 (all-drawing lesson, markdown-only), **u05's lesson gains `no-exec` `input()` CODE cells** (the
per-lesson capstone real-forms, below) → `concept-scan` sees `input()` → the **`practices:[input]` add IS
required**, in sync in BOTH:
- `book1/units/unit-05-function-factory/manifest.yaml` — append `input` to `concepts.practices`.
- `book1/curriculum/coverage-map.yaml` — append `input` to the `unit-05-function-factory` `practices` list.

`input` is category `io` (concepts.yaml) — NOT a technique → cannot trip prereq/practice/technique-spiral;
introduced/required in u01/u02/u04 (all prereq of u05) → prereq-valid. No `introduces`/`requires` change.
`int-type`/`type-conversion`/`float-type` are `never_flag`/in-union, so `int(input())`/`float(input())` are safe.

## Lesson both-forms audit (design §1/§8)

All u05 lesson capstones are **executable** (they run with fixed args) — none is input-only, so **no
executable twin needs adding**. Each **per-lesson culminating put-it-together** gains a **`no-exec` `input()`
real-form** (reads its arg(s), calls the function, prints) + a `**Notice:**` (reads live input, does not run
here), placed AFTER the executable cell:

| Lesson | Capstone cell | Real-form reads | Idiom |
|---|---|---|---|
| L1 (card factory) | cell 9 `greeting_card(name, message)` | name, message (STRINGS) | plain `input(...)` ×2 |
| L2 (return) | cell 15 `polygon_points(n)` | n (int) | `int(input(...))` |
| L3 (scope) | cell 20 `pack_card(name)` | name (STRING) | plain `input(...)` |
| Algorithm Extension | cell 28 `total_stamp_size(number_of_stamps)` | number_of_stamps (int) | `int(input(...))` |

**Build-up rungs (exempt from both-forms):** L1 cells 2/4/7 (`blank_card`, single-param `greeting_card`),
L2 cell 13 (`area` — the first `return` example, before the polygon capstone). Rungs teach one increment;
only the culminating capstone per lesson carries both forms (the plans 031–035/049 pedagogy; design §3).

## Per-exercise SHAPE table

Every solutions cell is a function call (or headless compute) on input-shaped data → **read-and-compute**,
EXCEPT Challenge 2. All exercise STATEMENTS get a `**Real version:**` cue (Ch2 gets `**No real version:**`).

| Shape | Exercises | Real-form (solutions markdown) + statement treatment |
|---|---|---|
| **read-and-compute — function** | Ex1 `cheer(name)` [str], Ex2 `greeting_card(name)` [str], Ex3 `show_double`/`get_double(number)` [int], Ex4 `area(w,h)` [w,h **float**], Ex5 `player_label(name)` [str; scope demo keeps `team`], Ex7 `make_label(name)` [str], Ex8 `turn_angle(n)`/`angle_message` [int], Ex11 `total_card_borders` [int], Ex12–Ex15 `count_bonus_stamps`/`total_even_stamps`/`stamps_in_triangle`/`average_side` [int; Ex15 returns float], Ex16 `stamps_that_fit`/`width_used(limit)` [int, `if` in body], Ex17 `stamps_to_pass`/`width_when_passed(limit)` [int, `if`], Ex18 `stamps_to_reach(target)` [int, `while`], Ex19 `count_jumbo_stamps(n, threshold)` [2×int], Ex20 `total_ribbon(n, start, growth)` [3×int], Challenge 1 `name_badge(name, club)` [2×str] | markdown real-form = the unchanged `def … return`, then read the arg(s) with the typed idiom (labeled prompts, no index), then `print(func(args))`; statement `**Real version:**` cue |
| **read-and-compute — headless compute** (no `def`) | Ex6 (`stamp_count` → last_pen_size, side_moves), Ex9 (`rows`,`columns` → stamps_drawn), Ex10 (`bands`,`stamps_per_band` → last_size, stamps_drawn) | read the shape param(s) via `int(input(...))`, then the unchanged compute + `print` (u03 arm); statement `**Real version:**` cue |
| **exempt — reads-nothing/generator + predict** | Challenge 2 (`flower`/`petal` — written PLAN + predict of a turtle flower **drawing**, "do not run turtle here"; the notebook headless-computes petal COUNT only) | NO real-form; statement `**No real version:**` note (turtle drawing + predict; reads nothing) |

Notes: Ex3/Ex8/Ex16/Ex17 define TWO functions — the real-form reads the shared input once and calls/prints
both (or the primary, mirroring whatever the twin prints). Ex5 keeps the module-level `team = "Comets"` scope
line (it is the scope point) and reads only `name`. Homework Ex19/Ex20 are still read-and-compute (multi-arg
labeled prompts). Enrichment Ex11–Ex20 use small fixed data by design (§3 "small fixed data" drills) — the
real-form carries arbitrary-count realism via the read; the exec twin's small data is untouched.

## The treatment (functions read-and-compute, hybrid forms)

1. **Real-input forms:** lesson `no-exec` `input()` CODE cells (the 4 capstones) + solutions.ipynb markdown
   fenced real-forms (every read-and-compute exercise). Exercise STATEMENTS get `**Real version:**` cues
   (Ch2 `**No real version:**`).
2. **No data growth / no rename.** Function + parameter names (`cheer`, `area`, `w`, `h`, `n`, `target`,
   `threshold`) are already clean and meaningful — keep verbatim. Fixed args are modest/realistic (§3
   list-less arm). Enrichment drills keep small fixed data.
3. **Typed reads, labeled prompts:** string → `input(...)`; int → `int(input(...))`; float → `float(input(...))`.
   Multi-arg functions read each parameter with its own labeled prompt (e.g. `"Name? "`, `"Message? "`,
   `"Width? "`, `"Height? "`) — one read per parameter, **no `{i}` index** (u05 has no lists).
4. **Closure (u05-specific):** real-forms add `input`/`int`/`float` reads to the unchanged def/compute.
   **`if`/`elif`/`comparison`/`while`/`break` ARE permitted** (in-union — they live inside the def bodies).
   Forbidden: `sys.stdin`, `list`/list-append (not in u05 union), any other out-of-union concept. `input()`
   lives ONLY in lesson `no-exec` cells + solutions markdown (never a solutions CODE cell — solution-policy ban).

## Phases

### Phase A — apply to u05 (lesson + exercises + solutions + metadata + coverage-map)
- **lesson.ipynb:** add a `no-exec` `input()` real-form + `**Notice:**` after each of cells 9, 15, 20, 28
  (per the both-forms table). Do NOT alter the executable capstones or the build-up rungs.
- **exercises.ipynb:** `**Real version:**` cue on Ex1–Ex20 + Challenge 1; `**No real version:**` note on
  Challenge 2 (turtle-drawing + predict, reads nothing).
- **solutions.ipynb:** markdown read-and-compute real-forms per the SHAPE table (each = the unchanged
  `def`/compute + typed reads + `print(func(args))`), placed after each exercise's asserted twin. Fenced
  real-forms must not contain a line starting `## Exercise <digit>`.
- **metadata:** append `input` to `practices` in `manifest.yaml` AND `coverage-map.yaml` (in sync).
- **teacher-notes.md:** no change (pedagogy unchanged; real-forms are the established norm).

### Phase B — verification
- `ast.parse` + piped-run every real-form (lesson no-exec + solutions markdown); result line(s) == the paired
  executable twin's output modulo `input()` prompt text (design §6a–c). Multi-arg forms: one read per param.
- CLOSURE AST scan: real-forms use only in-union concepts (input/int/float/def/return/for/while/if/elif/
  comparison/break/range/arithmetic/print/f-string); **NO `sys.stdin`, NO list/list-append**, no other
  out-of-union id.
- Hygiene: 0 `input()` in any solutions CODE cell; ≥3 non-vacuous assert cells; no fenced `## Exercise <digit>`
  line; lesson executable capstones + rungs unchanged.
- Metadata: `manifest.yaml` + `coverage-map.yaml` `input` add is in sync; prereq/coverage/concept-scan/
  technique-spiral GREEN (input is `io`, prereq-valid).
- `scripts/ci-local.sh` ALL GREEN.

## Out of scope
- Any Book-1 entry other than u05 (rollout continues per design 003 §7: u06, u08, u09, u10, cp02–04,
  projects). Turtle `assets/*.py` drawing files (separate artifact). No design-003 amendment (v4 already
  covers the functions arm via the list-less + exemption clauses). No data growth, no rename. Phase B present.

## Plan Review
_(pending — 4-way.)_

## Content Review
_(pending — 4-way, post-implementation.)_

## Post-Execution Report
_(pending.)_
