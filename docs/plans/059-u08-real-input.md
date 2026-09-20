# Plan 059 — u08 word-wizard: full real-input treatment (dicts + lists + strings)

**Status:** DRAFT — plan-review gate pending.
**Type:** Content — apply the full real-input treatment (design 003 v6) to `unit-08-word-wizard`.
**Branch:** `feature/plan-059-u08-real-input`. **Base:** main @ aaf21f2.

## Motivation

Rollout slice 9 (design 003 §7 — list units). u08 introduces **dicts** (dict-literal/access/loop) over a base
of **lists** (list-loop/literal/append/filter) + **strings** (string-methods/`.split`/`in`). Translation-game
solutions: 1 function (Ex14 `translate`, return-only), the rest inline dict/list/string compute. Treatment by
**per-exercise audit** (design 003 v6). Authorities: design 003 v6; merged pilots u07 (list arm), u05
(functions arm — per-task call shell), u06 (mixed inline+function, statement-is-the-form, multi-value reads).

**Three u08-specific facts:**
1. **`input` is NOT in u08's union** → because two LESSON capstones gain `no-exec input()` cells (below),
   **ADD `practices:[input]`** to `manifest.yaml` AND `coverage-map.yaml` (in sync; `io` category → cannot trip
   prereq/practice/technique-spiral; introduced u01, prereq-valid). §5 per-unit-audit = YES (contrast u06 which
   already had it, u03 which got none).
2. **u08 lacks BOTH `range-function` AND `while-loop`** → NO `for i in range(n)`, NO sentinel `while` in any
   real-form. The read-into-**list** idiom is **`words = input("...").split()`** (split ONE line — `.split` is
   in-union string-methods), the read-into-**dict** idiom is **pair-split** `for pair in input("...").split():`
   (then extract `key`/`value` from `pair.split(":")` **without tuple-unpacking** — use `parts = pair.split(":")`,
   `parts[0]`/`parts[1]`, since multiple-assignment is not in u08's union), single-value reads are plain
   `input()`/`int(input())`. Forbidden: `sys.stdin`, `range-function`, `while-loop`, tuple-unpacking, any
   out-of-union concept. In-union & allowed: dicts, lists, for-over-iterable, if/elif/comparison/break,
   string-methods, in-operator, accumulator, int-type/type-conversion.
3. **The dict-fixture fork (user-ratified 2026-09-19 — "split: exempt some, teach some"):** 9 tasks operate on
   a PRE-GIVEN dict. Reconstructing a dict from input needs range/while (out of union) or the pair-split idiom
   (in-union but un-demonstrated in u08). Resolution: **exempt the 7 pure formatting/merge/flip tasks**
   (fixed-reference-fixture — the dict is authored lookup data, the graded skill is the transform/report), and
   **give pair-split real-forms to the 2 where reading a dict is pedagogically central** (Ex7 print-every-pair,
   Ex13 most-common-word — where "enter the phrasebook/tally as `k:v k:v`" is the natural real program).

## Design amendment (v6 — in scope, this plan)

design 003 §1/§8 → **v6**, codifying (ratified by the user for the u08 dict fork; the 4-way gate ratifies wording):
- **Fixed-reference-fixture exemption (§1 class 4):** a task whose input-shaped data is a **pre-authored
  dict/table used as reference/lookup data**, where the graded skill is a **transform or report over** the
  fixture (format, merge, flip, total, find-extreme) rather than obtaining it, is EXEMPT (executable-only) when
  reconstructing the fixture from input would require out-of-union control flow. EXCEPTION: where **building the
  dict from user-supplied data is itself the pedagogically central act**, give a **pair-split real-form**.
- **Pair-split dict-read idiom (§4):** the sanctioned range/while-less way to read a dict from one line —
  `for pair in input(...).split():` then `parts = pair.split(":")` / `d[parts[0]] = parts[1]` (or `int(parts[1])`),
  no tuple-unpacking.

## Metadata change (§5 — input add IS triggered)

Add `input` to `practices` in BOTH `book1/units/unit-08-word-wizard/manifest.yaml` (concepts.practices) AND the
`unit-08-word-wizard` entry in `book1/curriculum/coverage-map.yaml` (in sync). Nothing else.

## Lesson both-forms audit (design §1/§8)

Two L-capstones process input-shaped word LISTS and gain a `no-exec input()` real-form (via `.split()`) + a
`**Notice:** (It reads live input, so it does not run here.)`; the dict-operating lesson cells are rungs (exempt).

| Lesson cell (by content) | Capstone | Real-form |
|---|---|---|
| L2 capstone — `def translate` + loop over `words_to_translate` list (after the "**Put it together:**" cell) | word-list translate | `words_to_translate = input("Words to translate? ").split()`, phrasebook fixed literal, unchanged loop `print(f"{word} means {translate(word, translations)}")` — include a miss ("fish") to show "???" |
| L3 capstone — count-the-log (`words = [...]` count-by-condition) | word-list count | `words = input("Word log? ").split()`, unchanged count loop, `print(counts)` |
| L3 cells operating on GIVEN counts dicts (labels-from-counts, most-common-from-counts) | dict-fixture | rungs → no real-form (fixed-reference-fixture) |
| L1 rungs + the `no-exec` KeyError debug cell | — | rungs / debug → exempt |

Both new no-exec cells read word lists via `.split()` (in-comfort) — no dict trap. Identify cells by CONTENT.

## Per-exercise SHAPE table (21 exercises + 2 challenges)

Real-form rule as u05/u06 (per-task call shell; one input per distinct fixed value; BARE call for print-fns;
computed-output-lines parity; multi-value twins read every value; value-coupled labels kept as computed
expressions). Solution cell indices from the survey.

| Shape | Tasks | Real-form / treatment |
|---|---|---|
| **read-and-compute — word list** (`input(...).split()`) | Ex3 in-the-book (input needs a hit + a miss), Ex5 grow-the-log, Ex12 count-the-words, Ex14 translate-a-list (fn return-only → `translated.append(translate(word, translations))`), Ex16 keep-long-words (**keep `minimum_length=5` FIXED**), Ex19 known/unknown, Ex20 lengths-that-fit (**keep `budget=12` FIXED**), Ex21 lengths-until-tips (**keep `budget=12` FIXED**) | `**The real program**` block + `**Real version:**` cue. GOTCHA(c): Ex5/Ex12 hard-code dict keys in comparisons (`counts["cat"]>counts["dog"]`, `counts["owl"]>counts["fox"]`) → use `.get(k,0)` so a read log can't KeyError |
| **read-and-compute — single value** (plain `input()`/target) | Ex2 safe-lookup (`word=input`; `.get(word,"???")`), Ex6 tidy-then-translate (`raw_word=input`; `.strip().lower()`), Ex15 reverse-lookup (read the `target`; fixed phrasebook loop+break) | block + cue |
| **read-and-compute — two string reads** | Ex4 add-a-word (`word`+`meaning`→`translations[word]=meaning`; keep `new_words=1` fixed) | block + cue |
| **pair-split dict-read** (v6 idiom; dict-reading central) | Ex7 print-every-pair (read a phrasebook `k:v k:v`, `.items()` walk), Ex13 most-common-word (read counts `word:n`, `int(parts[1])`, find-extreme) | `**The real program**` block (pair-split, NO tuple-unpacking) + `**Real version:**` cue |
| **exempt — reads-nothing/generator** (§1 class 1) | Ex1 build-a-phrasebook (dict-literal IS the graded artifact) | `**No real version:**` (reads-nothing) |
| **exempt — debug/fix-the-error + predict/trace** (§1 class 2+3 hybrid) | Ex8 fix-the-KeyError (part 1 explain traceback = predict/trace; part 2 repair bracket→`.get` = debug/fix, fix is not reading input) | `**No real version:**` naming both |
| **exempt — fixed-reference-fixture** (§1 class 4 v6; pure transform/report of a given dict) | Ex9 scoreboard-lines, Ex10 visit-labels, Ex11 walk-the-keys, Ex17 total-of-tally, Ex18 rarest-word, Challenge 1 merge-two-phrasebooks, Challenge 2 flip-the-phrasebook | `**No real version:**` (fixed-reference-fixture — authored lookup data; the transform is the graded skill) |

**Counts:** 14 read-and-compute (8 word-list + 3 single + 1 two-read + 2 pair-split) · 9 exempt (Ex1 reads-nothing,
Ex8 debug/predict, 7 fixed-reference-fixture). = 23.

## Phases

### Phase A — apply to u08 (lesson + exercises + solutions + metadata + coverage-map + design v6)
- **design 003 → v6** (§1 class 4 fixed-reference-fixture exemption; §4 pair-split dict-read idiom) — done in this plan.
- **lesson.ipynb:** add a `no-exec input()` real-form (via `.split()`) + `**Notice:**` after each of the two
  word-list capstones (L2 translate, L3 count). Do NOT touch rungs, dict-operating cells, or the debug cell.
- **exercises.ipynb:** `**Real version:**` cue on the 14 read-and-compute tasks (incl. Ex7/Ex13 pair-split);
  `**No real version:**` notes on Ex1 (reads-nothing), Ex8 (debug/predict), Ex9/10/11/17/18/Ch1/Ch2
  (fixed-reference-fixture, each naming the class).
- **solutions.ipynb:** `**The real program**` markdown block after each of the 14 read-and-compute twins
  (word-list `.split()`, single reads, two reads, pair-split for Ex7/Ex13). Keep def/compute unchanged; value-
  coupled numeric params fixed; `.get(k,0)` for Ex5/Ex12 hard-coded keys. NO block under the 9 exempt. Fenced
  blocks must not contain a line starting `## Exercise <digit>`.
- **metadata:** `input` added to `practices` in manifest.yaml + coverage-map.yaml (in sync).
- **teacher-notes.md:** no change.

### Phase B — verification
- `ast.parse` + piped-run every real-form (2 lesson no-exec + 14 solutions markdown); computed-output lines ==
  the twin's modulo prompt text (§6a–c). Multi-value twins (Ex3 hit+miss; Ex14/L2 include a miss) reproduce every
  line. Pair-split real-forms (Ex7/Ex13): pipe a `k:v k:v` line reproducing the twin's dict output.
- CLOSURE AST scan: real-forms use only in-union concepts (dict/list/for-over-iterable/if/elif/comparison/break/
  string-methods/in/int/accumulator); **NO `range`, NO `while`, NO tuple-unpacking, NO `sys.stdin`**.
- Hygiene: 0 `input()` in solutions CODE cells; ≥3 non-vacuous assert cells; no fenced `## Exercise <digit>`;
  lesson rungs + dict cells + all executable twins unchanged; teacher-notes untouched.
- Metadata: `input` add in sync; prereq/coverage/concept-scan/technique-spiral GREEN.
- `scripts/ci-local.sh` ALL GREEN.

## Out of scope
- Any Book-1 entry other than u08 (rollout continues: u09, u10, cp02–04, projects). design 003 → v6 IS in scope
  (the dict-fixture fork resolution). No data growth, no rename. Phase B present.
- **Reviewer-judgment flagged:** the exempt-vs-pair-split split among the 9 dict-fixture tasks (Ex7/Ex13
  pair-split; the other 7 exempt) is the user-ratified "split" direction; the gate ratifies the exact assignment
  + whether Ex7/Ex13 need a lesson rung demonstrating pair-split (proposal: NO — the solution model answer shows
  the in-union idiom; flagged).

## Plan Review
_(pending — 4-way.)_

## Content Review
_(pending — 4-way, post-implementation.)_

## Post-Execution Report
_(pending.)_
