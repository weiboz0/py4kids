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
2. **u08 lacks BOTH `range-function` AND `while-loop`** → NO `for i in range(n)`, NO sentinel `while`. The
   variable-count read idiom is **`.split()`** — which is **NOT taught in Book 1** (concepts.yaml `string-methods`
   = upper/lower/strip/replace; `.split` = the unregistered `str-split` → would fail `concept-scan`). **User
   ratified teaching it (option b):** register `str-split`, introduce + teach it in u08 (see "str-split teaching"
   below). Then: read-into-**list** = `words = input("...").split()`; read-into-**dict** = **pair-split**
   `for pair in input("...").split():` then `parts = pair.split(":")` / `d[parts[0]] = parts[1]` (or
   `int(parts[1])`) — **no `k, v =` unpacking** (statement-level assignment-unpacking is never taught in Book 1;
   `parts[0]` uses `list-index`, u07-introduced/prereq-valid → add to u08 practices); single-value reads are
   plain `input()`/`int(input())`. Forbidden in real-forms: `sys.stdin`, `range-function`, `while-loop`,
   assignment-unpacking, any method outside the unit's taught set. In-union & allowed: dicts, lists,
   for-over-iterable, if/elif/comparison/break, string-methods+`str-split`, in-operator, accumulator, int-type.
3. **The dict-fixture fork (user-ratified 2026-09-19 — "split: exempt some, teach some"):** 9 tasks operate on
   a PRE-GIVEN dict. Reconstructing a dict from input needs range/while (out of union) or the pair-split idiom
   (in-union but un-demonstrated in u08). Resolution: **exempt the 7 pure formatting/merge/flip tasks**
   (fixed-reference-fixture — the dict is authored lookup data, the graded skill is the transform/report), and
   **give pair-split real-forms to the 2 where reading a dict is pedagogically central** (Ex7 print-every-pair,
   Ex13 most-common-word — where "enter the phrasebook/tally as `k:v k:v`" is the natural real program).

## Design amendment (v6 — in scope, this plan)

design 003 §1/§4/§8 → **v6** (user-ratified; 4-way gate ratifies wording):
- **Fixed-reference-fixture exemption (§1 class 4):** a task whose input-shaped data is a **pre-authored
  dict/table used as reference/lookup data**, where the graded skill is a **transform or report over** the
  fixture (format, merge, flip, total, find-extreme), is EXEMPT (executable-only) when reconstructing the
  fixture from input needs out-of-union control flow. **Designated-demonstrator rule** (replaces the arbitrary
  "central act" exception — per [sol]/[glm]/[fable]): so the structure-read idiom is *shown at least once*, the
  plan **names ≥1 representative fixture task per value-type** to carry a structure-read real-form; the rest are
  class-4 exempt. u08: **Ex7** (string-valued phrasebook `.items()` walk) + **Ex13** (int-valued counts
  find-extreme) are the designated demonstrators; Ex9/10/11/17/18/Ch1/Ch2 exempt.
- **Structure-read idioms (§4, range/while-less units):** read-into-list `input().split()`, read-into-dict
  pair-split `for pair in input().split(): parts = pair.split(":"); d[parts[0]] = parts[1]` — both require
  `str-split` in the unit's union (introduced u08); no assignment-unpacking. (Reconciles the v5 "fixed-count
  reads" note: fixed-count remains the fallback for a range/while/str-split-less unit.)
- §1:25-26 "one of three settled classes" → **four**.

## Metadata / curriculum change (§5 — input add + str-split introduction)

- **`input`:** add to `practices` in `book1/units/unit-08-word-wizard/manifest.yaml` AND the u08 entry in
  `book1/curriculum/coverage-map.yaml` (in sync; io, prereq-valid via u01) — two lesson capstones gain no-exec
  input() cells.
- **`str-split` (NEW concept):** register in `book1/curriculum/concepts.yaml` (`{id: str-split, name:
  "Splitting a string into a list (.split())", category: strings}`); add to u08 **`introduces`** (manifest +
  coverage-map). Also add `list-index` to u08 `practices` (the pair-split `parts[0]`; u07-introduced, prereq-valid).
- **Downstream practice (coverage rule, curriculum.py:278 — a non-capstone entry must practice every registered
  concept):** add `str-split` to **u09 (save-point/files)** `practices` (manifest + coverage-map) AND a real
  `.split()` usage in u09 content (natural: split a file line into fields) — so `str-split` is practiced outside
  u08 and the capstone. (u08 cannot practice its own introduction.)

## str-split teaching (option b — new EXECUTABLE lesson content)

Because `str-split` is newly introduced in u08, it must be **taught and used in an executable (CI-run) cell**
so the introduction is real (concept-scan detects `str-split` used in u08 = where it is introduced):
- **`.split()` intro rung (L2, executable):** a small graduated rung BEFORE the translate capstone —
  `sentence = "cat dog owl"` / `words = sentence.split()` / `print(words)` (+ a one-line markdown explainer:
  ".split() turns a sentence into a list of words"). Runs in `exec-lessons`; introduces `str-split`.
- **pair-split demo rung (L2/L3, executable):** since Ex7/Ex13 real-forms use pair-split, demonstrate it once on
  a FIXED string so the idiom is grounded (not first-seen in a solution): `pairs = "cat:gato dog:perro".split()`
  / `phrasebook = {}` / `for pair in pairs: parts = pair.split(":"); phrasebook[parts[0]] = parts[1]` /
  `print(phrasebook)` (+ explainer). Runs; uses `str-split` + `list-index` + dict-access (all in/added-to union).
- **Coverage:** `str-split` introduced in u08 (used in these rungs + real-forms) and **practiced in u09**
  (downstream, per the metadata section) → coverage-check + prereq-check GREEN. teacher-notes (u08) gains a line
  on `.split()`; **cp04 + project-02 teacher-notes revised** (they currently assert `.split()` is untaught —
  now false: cp04 Q4's model still uses `for line in f`+`.strip()`+`int()` but a `.split()` solution is now
  legitimate; project-02 removes `.split()` from its "untaught tools" list).

## Lesson both-forms audit (design §1/§8)

Two L-capstones process input-shaped word LISTS and gain a `no-exec input()` real-form (via `.split()`) + a
`**Notice:** (It reads live input, so it does not run here.)`; the dict-operating lesson cells are rungs (exempt).
The `.split()` + pair-split intro rungs (above) are NEW executable teaching cells placed before the capstones.

| Lesson cell (by content) | Capstone | Real-form |
|---|---|---|
| L2 capstone — `def translate` + loop over `words_to_translate` list (after the "**Put it together:**" cell) | word-list translate | `words_to_translate = input("Words to translate? ").split()`, phrasebook fixed literal, unchanged loop `print(f"{word} means {translate(word, translations)}")` — include a miss ("fish") to show "???" |
| L3 capstone — count-the-log (`words = [...]` count-by-condition) | word-list count | `words = input("Word log? ").split()`, unchanged count loop, `print(counts)` |
| L3 cells operating on GIVEN counts dicts (labels-from-counts, most-common-from-counts) | dict-fixture | rungs → no real-form (fixed-reference-fixture) |
| L1 rungs + the `no-exec` KeyError debug cell | — | rungs / debug → exempt |

Both new no-exec input() cells read word lists via `.split()` — no dict trap. Identify cells by CONTENT.

## Per-exercise SHAPE table (21 exercises + 2 challenges)

Real-form rule as u05/u06 (per-task call shell; one input per distinct fixed value; BARE call for print-fns;
computed-output-lines parity; multi-value twins read every value; value-coupled labels kept as computed
expressions). Solution cell indices from the survey.

| Shape | Tasks | Real-form / treatment |
|---|---|---|
| **read-and-compute — word list** (`input(...).split()` loop) | Ex5 grow-the-log, Ex12 count-the-words, Ex14 translate-a-list (fn return-only → `translated.append(translate(word, translations))`), Ex16 keep-long-words (**keep `minimum_length=5` FIXED**), Ex19 known/unknown, Ex20 lengths-that-fit (**keep `budget=12` FIXED**), Ex21 lengths-until-tips (**keep `budget=12` FIXED**) | `**The real program**` block + `**Real version:**` cue. GOTCHA(c): Ex5/Ex12 hard-code dict keys in comparisons (`counts["cat"]>counts["dog"]`, `counts["owl"]>counts["fox"]`) → use `.get(k,0)` so a read log can't KeyError |
| **read-and-compute — single / few explicit reads** (twin is NOT a loop → plain `input()`, one per distinct value) | Ex2 safe-lookup (`word=input`; `.get(word,"???")`), Ex6 tidy-then-translate (`raw_word=input`; `.strip().lower()`), Ex15 reverse-lookup (read the `target`; fixed phrasebook loop+break), **Ex3 in-the-book** (twin is TWO sequential single-word checks, NOT a loop → **two plain `input()` reads**, one a hit + one a miss — do NOT `.split()`-loop it, §6c), Ex4 add-a-word (`word`+`meaning`→`translations[word]=meaning`; keep `new_words=1` fixed) | block + cue |
| **pair-split dict-read** (v6 idiom; dict-reading central) | Ex7 print-every-pair (read a phrasebook `k:v k:v`, `.items()` walk), Ex13 most-common-word (read counts `word:n`, `int(parts[1])`, find-extreme) | `**The real program**` block (pair-split, NO tuple-unpacking) + `**Real version:**` cue |
| **exempt — reads-nothing/generator** (§1 class 1) | Ex1 build-a-phrasebook (dict-literal IS the graded artifact) | `**No real version:**` (reads-nothing) |
| **exempt — debug/fix-the-error + predict/trace** (§1 class 2+3 hybrid) | Ex8 fix-the-KeyError (part 1 explain traceback = predict/trace; part 2 repair bracket→`.get` = debug/fix, fix is not reading input) | `**No real version:**` naming both |
| **exempt — fixed-reference-fixture** (§1 class 4 v6; pure transform/report of a given dict) | Ex9 scoreboard-lines, Ex10 visit-labels, Ex11 walk-the-keys, Ex17 total-of-tally, Ex18 rarest-word, Challenge 1 merge-two-phrasebooks, Challenge 2 flip-the-phrasebook | `**No real version:**` (fixed-reference-fixture — authored lookup data; the transform is the graded skill) |

**Counts:** 14 read-and-compute (6 word-list-loop + 5 single/few + 1 [Ex4] + 2 pair-split) · 9 exempt (Ex1
reads-nothing, Ex8 debug/predict, 7 fixed-reference-fixture). = 23. (Ex3/Ex4 grouped into the single/few row.)

## Phases

### Phase A — multi-unit (u08 + curriculum + u09 + cross-unit teacher-notes + design v6)
- **design 003 → v6** (§1 class-4 fixed-reference-fixture + designated-demonstrator; §4 structure-read idioms
  requiring `str-split`; §1:25-26 four classes) — done in this plan.
- **concepts.yaml:** register `str-split` (category strings).
- **u08 manifest + coverage-map:** add `str-split` to `introduces`; add `input` + `list-index` to `practices` (in sync).
- **u08 lesson.ipynb:** add the two EXECUTABLE intro rungs (`.split()` on a fixed sentence; pair-split on a
  fixed `k:v` string) before the L2 capstone; add a `no-exec input()` real-form (via `.split()`) + `**Notice:**`
  after each of the two word-list capstones (L2 translate, L3 count). Do NOT touch existing rungs, dict-operating
  cells, or the KeyError debug cell.
- **u08 exercises.ipynb:** `**Real version:**` cue on the 14 read-and-compute tasks (incl. Ex7/Ex13 pair-split);
  `**No real version:**` notes on Ex1 (reads-nothing), Ex8 (debug/predict), Ex9/10/11/17/18/Ch1/Ch2 (fixed-ref).
- **u08 solutions.ipynb:** `**The real program**` block after each of the 14 read-and-compute twins. Ex3 = two
  plain reads (NOT a loop); pair-split (Ex7/Ex13) uses `parts[0]`/`parts[1]` (no `k,v=`); value-coupled numerics
  fixed; `.get(k,0)` for Ex5/Ex12. NO block under the 9 exempt. No fenced `## Exercise <digit>` line.
- **u08 teacher-notes.md:** add a line noting `.split()` is now taught here.
- **u09 (save-point):** add `str-split` to `practices` (manifest + coverage-map) AND a real `.split()` usage in
  u09 content (split a file line into fields) — the required downstream practicer. Minimal, executable.
- **cp04 + project-02 teacher-notes:** revise the notes that assert `.split()` is untaught (cp04 Q4: `.split()`
  is now taught → a split-based answer is legitimate, model still uses `for line in f`+`.strip()`+`int()`;
  project-02: remove `.split()` from the "untaught tools" list).

### Phase B — verification
- `ast.parse` + piped-run every real-form (2 lesson no-exec + 14 solutions markdown); computed-output lines ==
  the twin's modulo prompt text (§6a–c). Multi-value twins (Ex3 hit+miss; Ex14/L2 include a miss) reproduce every
  line. Pair-split (Ex7/Ex13): pipe a `k:v k:v` line reproducing the twin's dict output.
- CLOSURE AST scan: real-forms use only in-union concepts + `str-split`/`list-index`; **NO `range`, NO `while`,
  NO assignment-unpacking, NO `sys.stdin`, and NO method outside u08's taught set** (the split-bug class).
- The two new executable lesson rungs run clean under `exec-lessons` and introduce `str-split` (concept-scan
  sees it used in u08 where introduced).
- Hygiene: 0 `input()` in solutions CODE cells; ≥3 non-vacuous assert cells; no fenced `## Exercise <digit>`;
  existing lesson rungs/dict cells/executable twins unchanged.
- Curriculum: `str-split` introduced (u08) + practiced (u09), `input`/`list-index` added in sync →
  concept-scan / prereq-check / coverage-check / practice-check / technique-spiral ALL GREEN (book1 + book2).
- `scripts/ci-local.sh` ALL GREEN.

## Out of scope
- Book-1 entries other than u08 + the u09 `.split()`-practice touch + the cp04/project-02 teacher-notes revisions
  (all required by the user-ratified teach-`.split()` decision). Rollout continues: u09 (full real-input),
  u10, cp02–04, projects. design 003 → v6 IS in scope. No data growth, no rename. Phase B present.
- **Reviewer-judgment flagged:** the exact Ex7/Ex13 designated-demonstrator choice (string-valued + int-valued
  representatives) vs the 7 exempt is the user-ratified split; the gate ratifies. The two executable lesson
  intro rungs (`.split()` + pair-split) are NEW authored content — reviewers should sanity-check pedagogy/placement.

## Plan Review

### Round 1 (2026-09-19) — [self] inline; [sol] gpt-5.6-sol; [glm] volcengine-plan/glm-5.3; [fable] Fable 5.
#### [self] (2026-09-19)
- **Verdict**: APPROVE — grounded in the read-only u08 survey (all 23 tasks + lesson read) + the user-ratified
  dict-fork direction ("split: exempt some, teach some"). Metadata add correct (input not in union; io;
  prereq-valid; 2 lesson capstones gain no-exec input()); closure = .split()/pair-split, no range/while/unpacking
  (u08 lacks range+while); design v6 codifies the fixed-reference-fixture exemption + pair-split idiom; SHAPE 14
  read-and-compute / 9 exempt; gotchas baked (Ex5/Ex12 .get; value-coupled numerics fixed; multi-value twins).
  Self-flagged judgment forks for the gate:
  - **Ex7/Ex13 pair-split vs the other 7 exempt:** the user endorsed the split with the survey's specific
    assignment (Ex7 print-every-pair + Ex13 most-common are the "dict-reading central" cases; the rest are pure
    transforms of authored fixtures). The exact line is a judgment the gate ratifies.
  - **Lesson rung for pair-split:** proposal is NO new rung — Ex7/Ex13's solutions-markdown model answers show
    the in-union pair-split idiom fully. A reviewer may argue for a lesson demo; flagged.

#### [sol] (2026-09-19)
- **Verdict**: REJECT. Must-Fix: (1) `.split()` is NOT the in-union `string-methods` concept (Book-1
  `string-methods` = upper/lower/strip/replace; the scanner classifies `.split` as unregistered `str-split`) →
  the two lesson cells + all `.split()`/pair-split forms are out-of-union and would fail `concept-scan`;
  invalidates the closure/GREEN claims. (2) the class-4 predicate doesn't separate Ex7/Ex13 (report/find-extreme
  over given dicts — shape-identical to the 7 exempt) from the exempt set → arbitrary as written; keep the 7/2
  split but rewrite the criterion. Should: design §23-26 still says "v5 / three classes". Metadata/closure(range,
  while)/lesson-targets/23-count/gotchas/Phase B otherwise correct.
#### [fable] (2026-09-19)
- **Verdict**: REJECT. Must-Fix #1 (same .split() blocker, fully evidenced: concepts.yaml line 13; TAUGHT_METHODS;
  0 `.split(` in Book-1; cp04 teacher-notes line 46 + project-02 line 98 say it's untaught → prereq-closure
  violation + contradicts shipped teacher-notes). Presents the resolution as a USER fork: (a) in-union
  fixed-count reads vs (b) teach `.split()` (register str-split + lesson rung + exercise + teacher-notes +
  revise cp04/proj-02). Must-Fix #2 = design v6 §4/§9 ".split is string-methods" is false. Should: class-4
  EXCEPTION is arbitrary → reword as a "designated-demonstrator" rule (name ≥1 representative dict task per value
  type to carry the structure-read form; rest exempt). #4 `parts[0]/[1]` uses `list-index` (u07, prereq-valid,
  MANUAL_ONLY so no CI trip) — add to practices if pair-split survives. Nice: Ex3 → two single reads (twin is
  two sequential blocks, not a loop); tuple-unpacking forbidden for pedagogy not union. Metadata/lesson/SHAPE/
  gotchas/Phase B otherwise verified correct.
#### [glm] (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: REJECT (confirms [sol]/[fable]). Must: (1) `.split()` untaught → out-of-union, fails CI,
  prereq-closure violation (fully re-evidenced); (2) class-4 criterion doesn't separate Ex7/Ex13 from the 7
  exempt (shape-identical) → reword as **designated-demonstrator** (per fixture value-type, ≥1 named
  representative carries the structure-read form; rest exempt). Should: §1:25-26 "three classes" → four; Ex3 =
  two single reads (twin is 2 blocks); pair-split `parts[0]` uses `list-index` (u07, prereq-valid, MANUAL_ONLY)
  → add to u08 practices; ban `k,v=` as pedagogical not union; under (b) pair-split needs a LESSON demo rung;
  harden Phase B closure scan to assert no method outside the unit's taught set. Nice: include the solution
  cell-index mapping; reconcile §4 v5/v6 fixed-count guidance. Suggests **u09 (files, line-parsing) as the
  natural downstream `.split()` practicer.** Metadata/closure/lesson-audit/SHAPE/gotchas/Phase B verified correct.

### Round 1 — outcome: REJECT (3 of 4). **USER-RATIFIED "Proceed — full multi-unit teach" (2026-09-19)** for the
`.split()` fork. Redrafting plan for the full teach: register `str-split`; introduce + teach in u08 (lesson
`.split()` rung + pair-split demo rung); **practice `.split()` in u09 (files/line-parsing)** + add `str-split`
to u09 practices; revise cp04 + project-02 teacher-notes; design v6 reworked (§1 designated-demonstrator, §4
`.split()`=str-split, §25-26 four classes). Then re-gate. Prior PAUSE note (fork options) retained below.

### Round 1 — outcome (superseded): REJECT (2 of 4 in; the `.split()`-untaught blocker is decisive). **PAUSED for a user
fork** (the read-idiom decision — see below). Plan + design v6 to be redrafted per the user's choice, then re-gated.

**The blocker:** u08's read-into-list/dict idiom cannot be `.split()` (untaught in Book 1 → fails concept-scan +
violates prereq-closure + contradicts cp04/project-02 teacher-notes). u08 also lacks `range`/`while`. So the
only IN-UNION way to read a variable structure is **fixed-count explicit `input()` calls**. User fork:
- (a) **Fixed-count reads** (in-union, no new tool): lists via `[input(...), input(...), input(...)]` or
  `.append(input())` ×N; dicts via `d[input(...)] = input(...)` ×N. Loses arbitrary-count realism (design §3
  already accepts this for u01). Pair-split dies → Ex7/Ex13 become fixed-count dict-reads (or exempt).
- (b) **Teach `.split()` in u08** (register `str-split`; add to introduces + a lesson rung + ≥1 executable
  exercise + teacher-notes; revise cp04 + project-02 teacher-notes that say it's untaught). Enables arbitrary
  count + pair-split, but expands scope and changes the Year-1 tool set.

**User chose (b) — teach `.split()`.** Investigating the mechanics surfaced a ripple beyond the option text:
`practice_findings` (curriculum.py:278) requires every registered concept to be **practiced by a non-capstone
entry**, and a unit **cannot practice its own `introduces`**. So registering `str-split` + introducing it in u08
FORCES `.split()` usage into a **downstream** non-capstone entry (u09/u10/cp02–04/project-01) — otherwise
coverage-check fails "only the capstone practices: [str-split]". Plus cp04 Q4's rubric currently assumes
`.split()` is untaught. → Confirming scope (proceed with the multi-unit change vs fall back to fixed-count) before redraft.

## Content Review
_(pending — 4-way, post-implementation.)_

## Post-Execution Report
_(pending.)_
