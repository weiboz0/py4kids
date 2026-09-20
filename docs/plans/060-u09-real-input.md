# Plan 060 — u09 save-point: full real-input treatment (files: file-is-real reads + value real-forms)

**Status:** DRAFT — plan-review gate pending.
**Type:** Content — apply the full real-input treatment (design 003 v6) to `unit-09-save-point`.
**Branch:** `feature/plan-060-u09-real-input`. **Base:** main @ 14a9081.

## Motivation

Rollout slice 10 (design 003 §7 — list units). u09 is **Book 1's only FILE unit** (introduces file-read/
file-write/with-statement). Solutions do live file round-trips (write a literal → read it back; exec-solutions
runs them). Treatment by **per-exercise audit** (design 003 v6). Authorities: design 003 v6; merged pilots u07
(list arm / read-into-list), u05 (functions), u08 (fixed-count, fixed-reference-fixture).

**The file-unit fork (user-ratified 2026-09-19 — "files-are-real for reads, lighter"):** files are themselves
real input, so a program that **reads a file** already satisfies the norm's "reads real data, not toy fixed
data" goal — pure file-READ tasks get **NO `input()` real-form** (a short note records why). But 7 exercises
(Ex17–23) never open a file (they compute over an in-memory literal), and the write/value tasks supply their
data from a literal — those get `input()` real-forms. **No new design class** (user chose the lighter touch over
codifying a v7 "reads-a-file" class); the precedent is established by this plan and is citable for cp03/cp04/
projects that read files.

**Two u09-specific facts:**
1. **`input` NOT in u09's union** → the L1 write capstone gains a `no-exec input()` real-form (read the values,
   then write) → **ADD `practices:[input]`** to `manifest.yaml` + `coverage-map.yaml` (in sync; io, prereq-valid).
2. **u09 HAS `range-function`, lacks `while-loop`** → read-into-list idiom is **`for i in range(n)`**:
   `n = int(input("How many scores? "))` / `for i in range(n): scores.append(int(input(f"Score {i+1}? ")))`.
   Single scalars: `int(input(...))`. **NO `.split()`** (a Book-2 concept, untaught in Book 1 — verified absent
   from u09's solutions). Forbidden: `.split()`, `while`, `sys.stdin`, any method outside u09's taught set.
   In-union & allowed: file-read/write/with, `for`/`range`, list-literal/append/loop, dict-access/literal, if/
   elif/comparison/break, string-methods (strip/lower/upper/replace), int-type/type-conversion, accumulator,
   find-extreme, filter-into-list, linear-search.

## Metadata change (§5 — input add)

Add `input` to `practices` in BOTH `book1/units/unit-09-save-point/manifest.yaml` AND the `unit-09-save-point`
entry in `book1/curriculum/coverage-map.yaml` (in sync; `io` category → cannot trip prereq/practice/technique-
spiral; introduced u01, prereq-valid). Nothing else. (Triggered by the L1 write-capstone lesson `no-exec input()`
cell; the file-read capstones get no input cell.)

## Lesson both-forms audit (design §1/§8)

| Lesson section | Capstone | Treatment |
|---|---|---|
| L1 (write) | write-scores capstone (writes a fixed score list to a file) | **gains a `no-exec input()` real-form** — read the scores (`for i in range(n)` read-into-list) then the unchanged write; + `**Notice:**` |
| L2 (read ladder) | read demos (`f.read`→`for line in f`→`.strip()`→`.append()`→`int()`) | rungs → no form (build-up) |
| L3 (put it together) | `load_scores(filename)` + settings-search (both FILE-READ) | **file-is-real → NO input form** (a short note: the load already reads real input); FileNotFoundError demo = reads-nothing/error → exempt |

Only the L1 write capstone gains a lesson `input()` cell (values, not filename). Identify cells by CONTENT.

## Per-exercise SHAPE table (25 exercises; ids from survey)

Real-form rule as prior units (per-task shell; one read per distinct fixed value; computed-output-lines parity;
value-coupled labels kept computed). Read-into-list uses `for i in range(n)` (u09 has range). NO `.split()`.

| Shape | Exercises | Treatment |
|---|---|---|
| **file-read → norm-satisfied (NO input form)** | Ex2 load-the-file, Ex3 report-high-score, Ex5 search-settings, Ex11 labeled-scoreboard, Ex12 load-into-list, Ex13 sum-saved, Ex14 find-setting-stop-early, Ex15 highest-by-scanning, Ex16 load-high-scores (keep `threshold=700` fixed), Ex24 highest (stretch) | `**Real version:**` note: "already reads real input — it loads a save file (no separate `input()` version)". NO solutions real-form |
| **value/save → read-into-list or single read** (`input()` real-form) | Ex1 save-scores (read-into-list via range → write), Ex4 save-settings (read player/volume/difficulty → write), Ex6 save-then-load (read values → round-trip), Ex7 save-my-score (single `int(input())` new_score, then load/append/save), Ex10 save-profile (read values), Ex25 add-a-new-high (stretch; single `int(input())` new value) | `**The real program**` block + `**Real version:**` cue |
| **in-memory literal → read-into-list** (no file; `input()` real-form) | Ex17 count-boss-level, Ex18 average, Ex19 lowest, Ex20 which-save-holds (+ `int(input())` my_score), Ex21 fit-budget (keep `budget` fixed), Ex22 until-tips (keep `budget` fixed), Ex23 first-at-target (+ `int(input())` target) | `**The real program**` block (read scores via `for i in range(n)`) + `**Real version:**` cue |
| **exempt — debug/fix-the-error** (§1 class 2) | Ex8 diagnose-missing-save (diagnose FileNotFoundError + author the ordering fix — the repair is the graded act) | `**No real version:**` (debug/fix-the-error) |
| **exempt — file-mechanic demonstrator** (predict/demonstrate, §1 class 3-adjacent) | Ex9 prove-"w"-replaces (writes twice to demonstrate `"w"` truncates — the point is proving the mechanic, not obtaining data) | `**No real version:**` (demonstrator); **flag to gate** — reviewer may prefer read-into-list |

**Counts:** 10 file-read-satisfied (note, no form) · 6 value/save real-forms · 7 in-memory read-into-list · 2
exempt (Ex8 debug, Ex9 demonstrator) = 25. Solutions real-forms = 13 (6 value/save + 7 in-memory).

## Phases

### Phase A — apply to u09 (lesson + exercises + solutions + metadata + coverage-map)
- **lesson.ipynb:** add ONE `no-exec input()` real-form (read-into-list via range → unchanged write) + Notice
  after the L1 write capstone. L3 file-read capstones + rungs + FileNotFoundError demo unchanged.
- **exercises.ipynb:** `**Real version:**` note on the 10 file-read tasks ("already reads real input — loads a
  save file"); `**Real version:**` cue on the 13 value/in-memory tasks; `**No real version:**` note on Ex8
  (debug), Ex9 (file-mechanic demonstrator).
- **solutions.ipynb:** `**The real program**` block after each of the 13 value/in-memory twins (read-into-list
  via range / single reads; keep def/compute unchanged; value-coupled numerics [budget] fixed). NO block under
  the 10 file-read tasks or the 2 exempt. No fenced `## Exercise <digit>` line.
- **metadata:** `input` added to manifest + coverage-map (in sync).
- **teacher-notes.md:** no change.

### Phase B — verification
- `ast.parse` + piped-run every real-form (1 lesson no-exec + 13 solutions markdown); computed-output lines ==
  the twin's modulo prompt text (§6a–c). Read-into-list forms: pipe `n` then the values.
- CLOSURE AST scan: real-forms use only in-union concepts (file/for/range/list/dict/if/elif/comparison/break/
  string-methods/int/accumulator); **NO `.split()`, NO `while`, NO `sys.stdin`, NO method outside u09's taught set.**
- Hygiene: 0 `input()` in solutions CODE cells; ≥3 non-vacuous assert cells; no fenced `## Exercise <digit>`;
  lesson read capstones/rungs/FileNotFound demo + all executable twins unchanged; teacher-notes untouched.
- Metadata: `input` add in sync; concept-scan/prereq/coverage/technique-spiral GREEN (both books; no `.split()`).
- `scripts/ci-local.sh` ALL GREEN.

## Out of scope
- Any Book-1 entry other than u09. No new design class (user chose "lighter"); the file-is-real-for-reads
  treatment is plan-local + citable precedent. No `.split()`/str-split/Book-2 change. No data growth, no rename.
  Phase B present. Rollout continues: u10, cp02–04, projects.
- **Reviewer-judgment flagged:** Ex9 (prove-"w"-replaces) exempt-as-demonstrator vs read-into-list; the
  file-read-satisfied "note, no form" treatment for the 10 read tasks (user-ratified "lighter" — gate ratifies
  the exact wording of the note); whether a one-line design §-note should record the file-is-real precedent
  (proposal: keep plan-local per the user's "no new class" choice).

## Plan Review
_(pending — 4-way.)_

## Content Review
_(pending — 4-way, post-implementation.)_

## Post-Execution Report
_(pending.)_
