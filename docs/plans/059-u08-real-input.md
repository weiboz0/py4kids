# Plan 059 — u08 word-wizard: full real-input treatment (dicts + lists + strings)

**Status:** COMPLETE — both gates CLOSED (4-way); ci-local ALL GREEN (both books); ready to merge.
**Type:** Content — apply the full real-input treatment (design 003 v6) to `unit-08-word-wizard`.
**Branch:** `feature/plan-059-u08-real-input`. **Base:** main @ aaf21f2.

## Motivation

Rollout slice 9 (design 003 §7 — list units). u08 introduces **dicts** (dict-literal/access/loop) over a base
of **lists** (list-loop/literal/append/filter) + **strings** (string-methods/`in`). Translation-game
solutions: 1 function (Ex14 `translate`, return-only), the rest inline dict/list/string compute. Treatment by
**per-exercise audit** (design 003 v6). Authorities: design 003 v6; merged pilots u07 (list arm), u05
(functions arm — per-task call shell), u06 (mixed inline+function, statement-is-the-form, multi-value reads).

**Three u08-specific facts:**
1. **`input` is NOT in u08's union** → because two LESSON capstones gain `no-exec input()` cells (below),
   **ADD `practices:[input]`** to `manifest.yaml` AND `coverage-map.yaml` (in sync; `io` category → cannot trip
   prereq/practice/technique-spiral; introduced u01, prereq-valid). §5 per-unit-audit = YES (contrast u06 which
   already had it, u03 which got none).
2. **u08 lacks BOTH `range-function` AND `while-loop`** — AND `.split()`/`str-split` is a **Book-2** concept
   (Book-1 `string-methods` = upper/lower/strip/replace only; teaching it in Book 1 collides with Book 2's
   ownership + needs a shared-tool change). **User ratified fixed-count reads (option a).** So the variable-count
   read idiom is **fixed-count explicit reads**, matching the paired twin's fixed length:
   - read-into-**list**: `words = [input("Word 1? "), input("Word 2? "), input("Word 3? ")]` (list-literal of
     reads; or a fixed sequence of `words.append(input(...))`).
   - read-into-**dict** (Ex7/Ex13 demonstrators): `phrasebook = {}` then `k1 = input("English 1? ")` /
     `v1 = input("Spanish 1? ")` / `phrasebook[k1] = v1` ×N (dict-access; `int(input())` for int values).
   - single-value reads: plain `input()`/`int(input())`.
   Forbidden in real-forms: `sys.stdin`, `range-function`, `while-loop`, `.split()`/any method outside u08's
   taught set, assignment-unpacking. In-union & allowed: dicts, lists (literal/append), for-over-iterable,
   if/elif/comparison/break, string-methods (upper/lower/strip/replace), in-operator, accumulator, int-type.
   Cost accepted: real-forms read a FIXED count (no arbitrary length) — design §3 accepts this (the u01 precedent).
3. **The dict-fixture fork (user-ratified — "split: exempt some, teach some"):** 9 tasks operate on a PRE-GIVEN
   dict (authored reference/lookup data the exercise transforms/reports over — not data the student collects).
   Resolution (design §1 class 4 v6 + designated-demonstrator): **Ex7** (string-valued phrasebook `.items()`
   walk) + **Ex13** (int-valued tally find-extreme) carry **fixed-count dict-read** real-forms (demonstrate
   reading a dict once per value-type); the other 7 (Ex9/10/11/17/18/Ch1/Ch2) are fixed-reference-fixture exempt.

## Design amendment (v6 — in scope, this plan)

design 003 §1/§4/§8 → **v6** (user-ratified; 4-way gate ratifies wording):
- **Fixed-reference-fixture exemption (§1 class 4):** a task that transforms/reports **over** a pre-authored
  dict/table the student is *given* (rather than obtains) is EXEMPT (executable-only) **unless it is a
  designated demonstrator** — re-reading authored reference data is not the graded act, and repeating a
  structure-read across every fixture task is mechanical noise. **Designated-demonstrator rule:** the plan
  names **≥1 representative fixture task per value-type** to carry a structure-read real-form (u08: Ex7
  string-valued + Ex13 int-valued, via fixed-count dict-read); the rest are class-4 exempt.
- **§4 range/while-less read idiom = FIXED-COUNT reads** (list literal of reads; dict `d[input()]=input()` ×N).
  (`.split()`/`str-split` is a Book-2 concept — kept out of Book 1; design stays Book-1-only.)
- §1:25-26 "one of three settled classes" → **four**.

## Metadata change (§5 — input add only)

Add `input` to `practices` in BOTH `book1/units/unit-08-word-wizard/manifest.yaml` AND the `unit-08-word-wizard`
entry in `book1/curriculum/coverage-map.yaml` (in sync; `io` category → cannot trip prereq/practice/technique-
spiral; introduced u01, prereq-valid) — two lesson capstones gain `no-exec input()` cells. **Nothing else** — no
`str-split`, no `concepts.yaml`/Book-2/u09/`concept_scan.py`/teacher-notes(cp04/project-02) change (fixed-count
reads use only in-union concepts; `.split()` stays untaught in Book 1, so the cp04/project-02 "untaught" notes
remain CORRECT and are untouched).

## Lesson both-forms audit (design §1/§8)

Two L-capstones process input-shaped word LISTS and gain a `no-exec input()` real-form (via a **fixed-count
list literal of reads**) + a `**Notice:** (It reads live input, so it does not run here.)`; the dict-operating
lesson cells are rungs (exempt). NO new teaching rungs (fixed-count reads use only in-union concepts).

| Lesson cell (by content) | Capstone | Real-form |
|---|---|---|
| L2 capstone — `def translate` + loop over `words_to_translate` list (after the "**Put it together:**" cell) | word-list translate | `words_to_translate = [input("Word 1? "), input("Word 2? "), input("Word 3? ")]` (match the twin's fixed list length), phrasebook fixed literal, unchanged loop `print(f"{word} means {translate(word, translations)}")` — include the twin's miss ("fish") so "???" still shows |
| L3 capstone — count-the-log (`words = [...]` count-by-condition) | word-list count | `words = [input("Word 1? "), …]` (match the twin's list length), unchanged count loop, `print(counts)` |
| L3 cells operating on GIVEN counts dicts (labels-from-counts, most-common-from-counts) | dict-fixture | rungs → no real-form (fixed-reference-fixture) |
| L1 rungs + the `no-exec` KeyError debug cell | — | rungs / debug → exempt |

Both new no-exec input() cells build a fixed-count word list — the reads match the twin's list, so §6b parity
holds (pipe the twin's words). Identify cells by CONTENT. **Placement note:** the L3 count-the-log capstone is
the FIRST rung of the L3 ladder (its Notice cell precedes the label/most-common rungs) — place the new no-exec
cell + Notice at the END of L3 (after the last given-counts rung) so the ladder stays one-increment; implementer's call.

## Per-exercise SHAPE table (21 exercises + 2 challenges)

Real-form rule as u05/u06 (per-task call shell; one input per distinct fixed value; BARE call for print-fns;
computed-output-lines parity; multi-value twins read every value; value-coupled labels kept as computed
expressions). Solution cell indices from the survey.

| Shape | Tasks | Real-form / treatment |
|---|---|---|
| **read-and-compute — word list** (**fixed-count** `[input(...), input(...), …]` matching the twin's list length) | Ex5 grow-the-log, Ex12 count-the-words, Ex14 translate-a-list (fn return-only → `translated.append(translate(word, translations))`), Ex16 keep-long-words (**keep `minimum_length=5` FIXED**), Ex19 known/unknown, Ex20 lengths-that-fit (**keep `budget=12` FIXED**), Ex21 lengths-until-tips (**keep `budget=12` FIXED**) | `**The real program**` block + `**Real version:**` cue. GOTCHA(c): Ex5/Ex12 hard-code dict keys in comparisons (`counts["cat"]>counts["dog"]`, `counts["owl"]>counts["fox"]`) → use `.get(k,0)` so a read log can't KeyError. Ex5 twin also has `new_word = "cat"` in addition to its
`words` list → the real-form **reads `new_word` too** (one input per distinct fixed value; a separate `input("New word? ")`) |
| **read-and-compute — single / few explicit reads** (twin is NOT a loop → plain `input()`, one per distinct value) | Ex2 safe-lookup (`word=input`; `.get(word,"???")`), Ex6 tidy-then-translate (`raw_word=input`; `.strip().lower()`), Ex15 reverse-lookup (read the `target`; fixed phrasebook loop+break), **Ex3 in-the-book** (twin is TWO sequential single-word checks, NOT a loop → **two plain `input()` reads**, one a hit + one a miss — do NOT `.split()`-loop it, §6c), Ex4 add-a-word (`word`+`meaning`→`translations[word]=meaning`; keep `new_words=1` fixed) | block + cue |
| **fixed-count dict-read** (designated demonstrators, §1 class 4) | Ex7 print-every-pair (build the phrasebook via `d={}` + N `k=input(); v=input(); d[k]=v` matching the twin's dict, then `.items()` walk), Ex13 most-common-word (build counts via N `word=input(); n=int(input()); counts[word]=n`, then find-extreme) | `**The real program**` block (fixed-count dict-read, dict-access; NO `.split()`, NO `k,v=`) + `**Real version:**` cue |
| **exempt — reads-nothing/generator** (§1 class 1) | Ex1 build-a-phrasebook (dict-literal IS the graded artifact) | `**No real version:**` (reads-nothing) |
| **exempt — debug/fix-the-error + predict/trace** (§1 class 2+3 hybrid) | Ex8 fix-the-KeyError (part 1 explain traceback = predict/trace; part 2 repair bracket→`.get` = debug/fix, fix is not reading input) | `**No real version:**` naming both |
| **exempt — fixed-reference-fixture** (§1 class 4 v6; pure transform/report of a given dict) | Ex9 scoreboard-lines, Ex10 visit-labels, Ex11 walk-the-keys, Ex17 total-of-tally, Ex18 rarest-word, Challenge 1 merge-two-phrasebooks, Challenge 2 flip-the-phrasebook | `**No real version:**` (fixed-reference-fixture — authored lookup data; the transform is the graded skill) |

**Counts:** 14 read-and-compute (7 word-list fixed-count + 5 single/few [incl Ex4] + 2 fixed-count dict-read) · 9 exempt (Ex1
reads-nothing, Ex8 debug/predict, 7 fixed-reference-fixture). = 23. (Ex3/Ex4 grouped into the single/few row.)

## Phases

### Phase A — apply to u08 (lesson + exercises + solutions + metadata + coverage-map + design v6)
- **design 003 → v6** (§1 class-4 fixed-reference-fixture + designated-demonstrator; §4 FIXED-COUNT read idiom;
  §1:25-26 four classes) — done in this plan. **No str-split, no Book-2, no concept_scan, no cross-unit edits.**
- **u08 manifest + coverage-map:** add `input` to `practices` (in sync). Nothing else.
- **u08 lesson.ipynb:** add a `no-exec input()` real-form (fixed-count list literal of reads) + `**Notice:**`
  after each of the two word-list capstones (L2 translate, L3 count). Do NOT touch existing rungs, dict-operating
  cells, or the KeyError debug cell. (No new teaching rungs — fixed-count reads are all in-union.)
- **u08 exercises.ipynb:** `**Real version:**` cue on the 14 read-and-compute tasks (incl. Ex7/Ex13 fixed-count
  dict-read); `**No real version:**` notes on Ex1 (reads-nothing), Ex8 (debug/predict), Ex9/10/11/17/18/Ch1/Ch2
  (fixed-reference-fixture, each naming the class).
- **u08 solutions.ipynb:** `**The real program**` block after each of the 14 read-and-compute twins. Word-list
  tasks use fixed-count `[input(...), …]` matching the twin's length; Ex3 = two plain reads (twin is 2 blocks,
  not a loop); Ex7/Ex13 = fixed-count dict-read (`d[k]=v` ×N; NO `.split()`); value-coupled numerics fixed;
  `.get(k,0)` for Ex5/Ex12. NO block under the 9 exempt. No fenced `## Exercise <digit>` line.
- **NO change** to `concepts.yaml`, u09, cp04/project-02, `concept_scan.py`, or u08 `teacher-notes.md`.

### Phase B — verification
- `ast.parse` + piped-run every real-form (2 lesson no-exec + 14 solutions markdown); computed-output lines ==
  the twin's modulo prompt text (§6a–c). Multi-value twins (Ex3 hit+miss; Ex14/L2 include a miss) reproduce every
  line. Fixed-count list/dict reads: pipe the twin's items in order reproducing the twin's output.
- CLOSURE AST scan: real-forms use only in-union concepts; **NO `range`, NO `while`, NO `.split()`/any method
  outside u08's taught set, NO assignment-unpacking, NO `sys.stdin`**.
- Hygiene: 0 `input()` in solutions CODE cells; ≥3 non-vacuous assert cells; no fenced `## Exercise <digit>`;
  existing lesson rungs/dict cells/executable twins unchanged; teacher-notes/other units untouched.
- Curriculum: `input` add in sync → concept-scan / prereq-check / **coverage-check (runs `practice_findings`)** /
  technique-spiral ALL GREEN (book1 + book2 — no Book-2 impact).
- `scripts/ci-local.sh` ALL GREEN.

## Out of scope
- Any Book-1 entry other than u08. **No `str-split` / Book-2 / `concept_scan.py` / u09 / cp04 / project-02
  change** (fixed-count reads keep `.split()` untaught in Book 1 → those units' "untaught" notes stay correct).
  Rollout continues: u09, u10, cp02–04, projects. design 003 → v6 (fixed-reference-fixture exemption +
  designated-demonstrator + fixed-count idiom) IS in scope. No data growth, no rename. Phase B present.
- **Reviewer-judgment flagged:** the Ex7/Ex13 designated-demonstrator choice (string- + int-valued fixed-count
  dict-reads) vs the 7 exempt is the user-ratified split; the gate ratifies. Fixed-count dict-reads are verbose —
  reviewers may prefer exempting Ex7/Ex13 too (all 9 exempt); flagged as a judgment call.

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

### Round 2 (2026-09-19) — re-review of the teach-`.split()` redraft (5a22213)
#### [sol] round 2
- **Verdict**: REJECT. Must: (1) class-4 "out-of-union reconstruction" precondition contradicts §4 (pair-split
  is in-union once str-split is taught) → re-base on designated-demonstrator + authored-reference-data.
  (2) cp04 revision wrong — Q4 assesses `for line in f`+`.strip()`+`int()`; `.split()` doesn't substitute → keep
  the no-credit rule, drop only the false "untaught" claim. Nit: no `practice-check` CLI (it's `coverage-check`).
#### [fable] round 2
- **Verdict**: REJECT. **BLOCKER (verified):** `str-split` is ALREADY a Book-2 concept (book2/concepts.yaml:7;
  book2 unit-01 introduces; 19 refs) → registering in Book 1 fails `global_concept_uniqueness_findings`
  (curriculum.py:52/332) → coverage-check RED for BOTH books. Teaching `.split()` in Book 1 requires:
  de-register str-split from Book 2 (concepts + unit-01 introduces, map+manifest), MOVE ownership to Book 1, +
  a `concept_scan.py` change (registered/profile from own ∪ dependency registry, else Book 2 emits 19× "untaught
  method split"), + reverse design's "Book 1 only / Book 2 unaffected". Should: cp04 wording (== [sol]#2).
  Everything else (u08 mechanics, u09 coverage ripple, criterion, Ex3, four-classes, Phase B) verified sound.

#### [glm] round 2
- **Verdict**: REJECT — both round-1 blockers resolved, but confirms the **same M1 Book-2 collision** as [fable]
  (str-split owned by book2; global uniqueness fails; migration needs a concept_scan.py profile change from own
  ∪ dependency registry — out of the plan's file scope). Verified sound: teach mechanics, u09 downstream
  practice, class-4 designated-demonstrator, Ex3 two-reads, four-classes, Phase B. Nits: cp04 wording (== sol#2);
  practice-check → coverage-check; §4 keeps a stray v4 "fixed-count" clause beside the v6 .split() para.

### Round 2 — outcome: REJECT (3 of 4; Book-2 `str-split` collision decisive). **USER RE-RATIFIED → (a)
fixed-count reads (2026-09-19)**, reversing the teach-`.split()` choice given the newly-surfaced cross-book +
tooling cost. Redrafting for option (a): NO str-split / concepts.yaml / Book-2 / u09 / concept_scan changes;
in-union **fixed-count reads** (list via `[input(...), input(...), …]`; dict via `d[input(...)] = input(...)`
×N); Ex7/Ex13 stay demonstrators via fixed-count dict-read (honoring fork-1 "teach some"); metadata = `input`
add only; design v6 shrinks to the fixed-reference-fixture exemption + designated-demonstrator + fixed-count
read idiom (str-split apparatus removed). Fold cp04 wording + practice-check→coverage-check. Then re-gate (round 3).

### Round 3 (2026-09-19) — re-review of the option-(a) fixed-count redraft (b4e0f3c)
#### [fable] round 3
- **Verdict**: APPROVE WITH NITS — round-2 Book-2 blocker fully resolved (diff touches only the two docs; no
  str-split/Book-2/tooling/cross-unit change; Book-1-only preserved; no global-uniqueness collision). Fixed-count
  idiom in-union; metadata = input add only; design v6 coherent (four classes, fixed-reference-fixture +
  designated-demonstrator, fixed-count §4, no out-of-union precondition); SHAPE 14/9 matches notebooks; Phase B
  present + correct (coverage-check runs practice_findings). 5 nits — 4 FOLDED (design Status "pair-split"→
  "fixed-count"; §3 arbitrary-count caveat for u08; plan counts "2 pair-split"→"2 fixed-count dict-read"; Ex5
  new_word clarification), 1 noted (L3 placement — put the no-exec cell at END of L3, implementer's call).

#### [sol] round 3
- **Verdict**: APPROVE WITH NITS — no blocker (option a in-union, Book-1-only, metadata adds only `input`,
  design v6 coherent, Phase B correct). 2 nits FOLDED: counts arithmetic (7 word-list + 5 single/few [incl Ex4]
  + 2 dict-read = 14, was double-counting Ex4); Ex5 `new_word` resolved to READ it (contract-consistent).

#### [glm] round 3
- **Verdict**: APPROVE WITH NITS — all 6 points confirmed (M1 resolved, no str-split anywhere; fixed-count
  in-union; input add only; design v6 coherent [no out-of-union residue]; SHAPE 14/9 vs twins; Phase B correct);
  ratified the Ex7/Ex13 per-value-type demonstrator split. Its 3 nits (counts parenthetical; Status header
  "pair-split"; §3 arbitrary-count caveat) were ALL already folded in the commits post-dating its review.

#### [self] round 3 (2026-09-19)
- **Verdict**: APPROVE — concur with the option-(a) redraft (supersedes my round-1 verdict, which was on the
  pair-split/.split() version). Fixed-count reads, input add only, Book-1-only, design v6 coherent; all
  round-3 nits folded.

### PLAN-REVIEW GATE CLOSED (2026-09-19) — 4-way consensus on the option-(a) redraft:
[self] APPROVE · [sol] APPROVE WITH NITS · [glm] APPROVE WITH NITS · [fable] APPROVE WITH NITS (all nits folded).
No open blockers. (Journey: 3 user forks [exempt/teach dict-fixtures → teach .split() → Book-2 collision] →
fixed-count reads; design 003 → v6 [fixed-reference-fixture + designated-demonstrator + fixed-count idiom].)

## Content Review

4-way, on the implementation commit ee61176. Tags [self]/[sol]/[glm]/[fable].

#### [self] (2026-09-19)
- **Verdict**: APPROVE. Verified the load-bearing constraint: **ZERO `.split(`** in any solutions/lesson cell.
  Ex7 (sol 20) + Ex13 (sol 36) are clean fixed-count dict-reads (explicit `word=input(); v=input(); d[word]=v`
  triples; Ex13 `n=int(input())`; NO `.split()`; the `for k,v in d.items()` is the taught dict-loop for-target,
  not statement-level unpacking). L2 (les 27, no-exec) + L3 fixed-count word lists. Diff = exactly the 5 scoped
  files (no str-split/concepts.yaml/Book-2/u09/concept_scan/teacher-notes). ci-local ALL GREEN — both books
  (concept-scan/coverage/prereq PASS; exec-solutions/exec-lessons PASS). 0 input() in solution CODE cells.

#### [fable] (2026-09-19)
- **Verdict**: REJECT → (after fix) APPROVE. 1 Must-Fix: Ex4 real-form (sol 11) used `word.replace('b','B',1)`
  — the **3-arg `.replace(old,new,count)` is untaught in Book 1** (only 2-arg taught, u06) AND a contrived hack
  to reproduce the twin's hardcoded prose literal "Bird". → `[FIXED]`: replaced with the plain computed
  `print(f"{word} means {translations[word]}.")` (value-coupled-label rule — the twin's capital "B" is prose,
  not data; §6b parity holds modulo that case). Everything else verified clean (all 16 real-forms parse +
  match twins; closure NO .split()/range/while/unpacking; metadata input-only, 5-file scope; 14 cues + 9 exempt
  notes; 0 input() in solution code cells; 23 asserts; both books green). WONTFIX nits: Ex7/Ex13 scratch names;
  Ex14 two-lines-collapsed (output-identical, plan-specified).

#### [sol] (2026-09-19)
- **Verdict**: APPROVE WITH NITS — all checks pass at ee61176 (16/16 AST + piped parity, closure, metadata,
  scope, exemptions, cues, hygiene). 1 Should-Fix: same Ex4 `.replace('b','B',1)` (corrupts input, e.g. rabbit
  → raBbit) → resolve by lowercasing the twin's prose "Bird"→"bird" + printing `{word}`. → `[FIXED]`: real-form
  now prints `{word}` (done for [fable]#1) AND the Ex4 twin (sol 10) prose "Bird"→"bird" for EXACT §6b parity
  (no assert on that line; exec-solutions unaffected).

#### [glm] (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: APPROVE (retry — the first invocation timed out; re-run on 763d091). No `[OPEN]`. All 16 real-forms
  parse + exact piped parity; closure clean (0 `split` repo-wide in u08; no 3-arg `.replace`; taught methods only);
  metadata input-only + 5-file scope; 14 Real + 9 No-real cues; 0 input() in solution code cells; 46 asserts;
  both books green. Verified the Ex4 fix (computed `{word}` + twin "Bird"→"bird" → exact parity). WONTFIX:
  Ex7/Ex13 scratch names, Ex14 two-line collapse (both output-identical).

### Content-review gate — outcome: **CLOSED** — 4-way consensus:
[self] APPROVE · [sol] APPROVE WITH NITS · [fable] APPROVE (Ex4 Must-Fix applied) · [glm] APPROVE. No `[OPEN]`
findings. (Pre-existing u02 `DuplicateCellId` noise noted, out of scope.)

## Post-Execution Report

**Shipped (2026-09-19).** u08 word-wizard given the full real-input treatment (design 003 **v6**), **OPTION A =
fixed-count reads** — Book-1-only, no `.split()`/str-split/Book-2/tooling change.

**What changed (5 files):**
- `lesson.ipynb` (additive): 2 `no-exec input()` fixed-count word-list capstone real-forms + Notices (L2
  translate; L3 count, placed at end of L3).
- `solutions.ipynb`: 14 `**The real program**` real-forms (7 word-list `[input(),…]`; 5 single/few incl. Ex3
  two-reads + Ex4; 2 fixed-count dict-reads Ex7/Ex13) + one Ex4 twin prose lowercase ("Bird"→"bird") for exact
  parity (content-gate fix — the initial Ex4 real-form's untaught 3-arg `.replace` hack was replaced by the
  computed `{word}`).
- `exercises.ipynb`: 14 `**Real version:**` cues + 9 `**No real version:**` notes (Ex1 reads-nothing, Ex8
  debug/predict, 7 fixed-reference-fixture).
- `manifest.yaml` + `coverage-map.yaml`: `input` added to `practices` (in sync).
- `docs/designs/003-book1-real-input.md` → **v6**: §1 fixed-reference-fixture exemption + designated-demonstrator
  rule; §4 fixed-count read idiom; four exempt classes. Book-1-only preserved.

**Verification:** `scripts/ci-local.sh` ALL GREEN — 493 passed / 2 skipped; exec-solutions + exec-lessons PASS;
**concept-scan/coverage-check/prereq-check GREEN for BOTH books** (fixed-count avoided the Book-2 `str-split`
collision entirely); PDF + guard OK. All 16 real-forms piped-run-match twins (Ex4 exact after the twin lowercase);
0 `input()` in solutions CODE cells; no fenced `## Exercise <digit>`.

**Gates:** plan-review CLOSED (4-way; 3 user forks [exempt/teach dict-fixtures → teach .split() → Book-2
collision] → fixed-count; design → v6). Content-review CLOSED (4-way; 1 Ex4 untaught-`.replace` fix).

**Rollout status (design 003 §7):** merged — u04, u07, cp01, u02, u01, u03, u05, u06, **u08 (dicts/lists/strings)**.
Remaining: u09 (files), u10 (classes); checkpoints cp02–cp04; projects. u08 established the **fixed-reference-
fixture exemption + designated-demonstrator rule** and the **fixed-count read idiom** for range/while/str-split-
less units, and confirmed `.split()` stays a Book-2-only concept.
