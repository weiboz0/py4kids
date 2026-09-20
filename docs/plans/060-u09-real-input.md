# Plan 060 — u09 save-point: full real-input treatment (files: file-is-real reads + value real-forms)

**Status:** PLAN-REVIEW GATE CLOSED (4-way consensus) — implementation pending.
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
| L1 (write) | the `scores = [1200, 850, 990]` **loop-write** cell (L1 is a 3-rung ladder: single write → loop-write → settings-write; there is NO literal "Put it together" cell) | **gains a `no-exec input()` real-form** — read the scores (`for i in range(n)` read-into-list) then the unchanged write; + `**Notice:**`. **PLACEMENT: insert AFTER the last L1 cell (its final Notice, before the `## Lesson 2` heading)** so the one-increment ladder is not split |
| L2 (read ladder) | read demos (`f.read`→`for line in f`→`.strip()`→`.append()`→`int()`) | rungs → no form (build-up) |
| L3 (put it together) | `load_scores(filename)` + settings-search (both FILE-READ) | **file-is-real → NO input form** (a short note: the load already reads real input); FileNotFoundError demo = "study, do not run" + printed traceback → **predict/trace exempt (§1 class 3)** |

Only the L1 loop-write capstone gains a lesson `input()` cell (values, not filename). Identify cells by CONTENT.

## Per-exercise SHAPE table (25 exercises; ids from survey)

Real-form rule as prior units (per-task shell; one read per distinct fixed value; computed-output-lines parity;
value-coupled labels kept computed). Read-into-list uses `for i in range(n)` (u09 has range). NO `.split()`.

| Shape | Exercises | Treatment |
|---|---|---|
| **file-read → norm-satisfied (NO input form)** | Ex2 load-the-file, Ex3 report-high-score (labels e.g. "Ada" fixed), Ex5 search-settings (keep `names_to_test` fixed — statement needs both branches to run), Ex11 labeled-scoreboard (label "Space Race" fixed), Ex12 load-into-list, Ex13 sum-saved, Ex15 highest-by-scanning, Ex16 load-high-scores (keep `threshold=700` fixed — scenario rule), Ex24 highest (stretch) | `**Real version:**` note: "already reads real input — it loads a save file (no separate `input()` version)". NO solutions real-form. Secondary non-file literals stay fixed (the file read is the real input) |
| **hybrid (file-satisfied + query read)** — NOT a §1 exempt-half hybrid; the file read is norm-satisfied (no `**No real version:**` cue), the query gets one `input()` | Ex14 find-setting-stop-early — file supplies the records (satisfied), but `target_name` is the QUERY (≈ Ex23's target) → read it: `target_name = input("Which setting? ")` + the unchanged file scan | `**The real program**` block (file read + `input()` target) + `**Real version:**` cue |
| **value/save → read-into-list or single read** (`input()` real-form) | Ex1 save-scores (read-into-list via range → write), Ex4 save-settings (read player/volume/difficulty → write), Ex6 save-then-load (read values → round-trip), Ex7 save-my-score (single `int(input())` new_score, then load/append/save), **Ex9 prove-"w"-replaces (read the scores via read-into-list, then the unchanged write-twice demo — pipe the fixed values → same output)**, Ex10 save-profile (read values), Ex25 add-a-new-high (stretch; single `int(input())` new value) | `**The real program**` block + `**Real version:**` cue |
| **in-memory literal → read-into-list** (no file; `input()` real-form) | Ex17 count-boss-level, Ex18 average, Ex19 lowest, Ex20 which-save-holds (+ `int(input())` my_score), Ex21 fit-budget (+ `int(input("Budget? "))`), Ex22 until-tips (+ `int(input("Budget? "))` — same budget as Ex21), Ex23 first-at-target (+ `int(input())` target) | `**The real program**` block (read scores via `for i in range(n)`, then the scalar) + `**Real version:**` cue |
| **exempt — debug/fix-the-error** (§1 class 2) | Ex8 diagnose-missing-save (diagnose FileNotFoundError + author the ordering fix — the repair is the graded act) | `**No real version:**` (debug/fix-the-error) |

**Counts:** 9 file-read-satisfied (note, no form) · 1 hybrid (Ex14) · 7 value/save real-forms (incl. Ex9) · 7
in-memory read-into-list · 1 exempt (Ex8 debug/fix-the-error) = 25. Solutions real-forms = **15** (Ex14 + 7
value/save + 7 in-memory).

## Data growth (§3 — required for <4-element core SOURCE lists)

Per design §3 (binding: not-toy; grow <4-element core SOURCE lists to ≥4; the u07 precedent), audit the CORE
(non-enrichment) score lists and grow each <4-element one to **≥4 (target 5–6)**, updating IN LOCKSTEP: the
executable twins' asserts, any printed outputs, the paired real-forms, AND the **statement-side carriers** (the
exercise-statement expected-value lines + any solution asserts of downstream readers — these are NOT CI-caught,
so enumerate them):
- **lesson L1 loop-write** capstone list (`[1200, 850, 990]`, 3) → grow to ≥4.
- **Ex1** save-scores list (3) → ≥4. **Ex6** save-then-load list (3) → ≥4. **Ex9** prove-"w" list (`[42, 77]`,
  2 — the prohibited 2-element shape) → ≥4.
Already-≥4 core lists need not grow. **Only the in-memory Ex17–Ex23 lists stay small** (Algorithm-Extension
"small fixed data" enrichment; their real-forms carry realism via the arbitrary-`n` read). Growth governs
SOURCE lists, not computed-result literals.

**Growth RIPPLE (enumerate + update in lockstep — the growth cascades through the `savegame.txt` chain):**
- **Ex1 grows** → update Ex1's own asserts/output; ripples to **Ex2** (raw-text expected lines/assert) and
  **Ex3** (`max` high-score message + assert).
- **Ex6 grows** → ripples to every later file-reader that shares the save chain: **Ex7** ("Saved …; N scores
  total." + the appended list), **Ex11** ("… loaded N scores."), **Ex12–Ex16** (their STATEMENT expected values
  AND their self-contained-setup lists in solutions — the student exercises have NO setup cell, so Ex12–16 must
  track the grown Ex6/Ex7 chain), **Ex24/Ex25** (asserts). ("Enrichment stays small" applies ONLY to the
  file-less Ex17–23 in-memory lists, NOT the Ex12–16 file-readers.)
- **Lesson L1 loop-write grows** → update the L1 print (e.g. "Saved N scores.") + any L2/L3 rung outputs that
  read that file. **Ex9 grows** → pick ≥4 values with an unambiguous two-save length; update solutions cell 20's assert.

## Phases

### Phase A — apply to u09 (lesson + exercises + solutions + metadata + coverage-map)
- **§3 data growth (do FIRST):** grow the 4 <4-element core SOURCE score lists (lesson L1 loop-write, Ex1, Ex6,
  Ex9) to ≥4, updating the executable twins' asserts + printed outputs before adding real-forms.
- **lesson.ipynb:** add ONE `no-exec input()` real-form (read-into-list via range → unchanged write of the
  grown list) + Notice, inserted AFTER the last L1 cell (not splitting the ladder); pair with the loop-write
  capstone by content. Add a `**Real version:**` file-is-real markdown note after each of the two L3 file-read
  capstones (`load_scores` + settings-search) — "already reads real input (a save file); no separate input()
  version." L2 rungs + the FileNotFoundError predict/trace demo stay form-less. The L1 settings-write cell is a
  rung (its value-read coverage lives in Ex4/Ex10).
- **exercises.ipynb:** `**Real version:**` note on the 9 file-read tasks; `**Real version:**` cue on the 15
  real-form tasks (Ex14 hybrid + 7 value/save + 7 in-memory); `**No real version:**` note on Ex8 (debug/fix-the-
  error). NOTE: 24 `**Real version:**` cues (9 file-read notes + 15 paired with a block) vs 15 `**The real
  program**` blocks — expected, not cue-vs-block drift.
- **solutions.ipynb:** `**The real program**` block after each of the 15 real-form twins (Ex14 file-read +
  read-target; value/save read-into-list-via-range / single reads; in-memory read-into-list). Keep def/compute
  unchanged; value-coupled labels computed. NO block under the 9 file-read tasks or Ex8. No fenced
  `## Exercise <digit>` line.
- **metadata:** `input` added to manifest + coverage-map (in sync).
- **teacher-notes.md:** no change (pacing unaffected; the grown lists are a data tweak).

### Phase B — verification
- The grown core twins (§3) re-run clean under `exec-solutions`/`exec-lessons` with updated asserts/outputs.
- `ast.parse` + piped-run every real-form (1 lesson no-exec + 15 solutions markdown); computed-output lines ==
  the twin's modulo prompt text (§6a–c). Read-into-list forms: pipe `n` then the values. **Cross-exercise state:**
  Ex7/Ex24/Ex25 call `load_scores`/`save_scores` (defined in Ex6) and depend on `savegame.txt` contents at run
  time — their piped-run harness prepends Ex6's helper defs and pre-writes the file with **the grown Ex6 list**
  (Ex7) / **grown list + the appended 1350** (Ex25) so parity is checked honestly against the post-growth chain.
  **Ex14's harness pre-writes `settings.txt`** (e.g. `["Ada","Mina","Leo"]`) so the piped `target_name` scan runs.
- CLOSURE AST scan: real-forms use only in-union concepts (file/for/range/list/dict/if/elif/comparison/break/
  string-methods/int/accumulator); **NO `.split()`, NO `while`, NO `sys.stdin`, NO method outside u09's taught set.**
- Hygiene: 0 `input()` in solutions CODE cells; ≥3 non-vacuous assert cells; no fenced `## Exercise <digit>`;
  lesson read capstones/rungs/FileNotFound demo unchanged; executable twins unchanged EXCEPT the four §3-grown
  twins + their chain dependents (Ex1→Ex2/Ex3; Ex6→Ex7/Ex11/Ex12–16/Ex24/Ex25; lesson L1); teacher-notes untouched.
- Metadata: `input` add in sync; concept-scan/prereq/coverage/technique-spiral GREEN (both books; no `.split()`).
- `scripts/ci-local.sh` ALL GREEN.

## Out of scope
- Any Book-1 entry other than u09. No new design class (user chose "lighter"); the file-is-real-for-reads
  treatment is plan-local + a **citable precedent** (cp03/cp04/project rollout plans should cite
  `docs/plans/060-u09-real-input.md` by path). No `.split()`/str-split/Book-2 change. **§3 growth of the 4
  <4-element core score lists IS in scope** (see "Data growth"); only the file-less Ex17–23 in-memory drills stay
  untouched (Ex12–16 file-readers grow with the shared save chain); no rename. Phase B present. Rollout continues: u10, cp02–04, projects.
- **Reviewer-judgment flagged:** the file-read-satisfied "note, no form" treatment for the **9** pure file-read
  tasks (+ hybrid Ex14 which reads its query) (user-ratified "lighter" — gate ratifies
  the exact wording of the note); whether a one-line design §-note should record the file-is-real precedent
  (proposal: keep plan-local per the user's "no new class" choice).

## Plan Review

### Round 1 (2026-09-19) — [self] inline; [sol] gpt-5.6-sol; [glm] volcengine-plan/glm-5.3; [fable] Fable 5.
#### [self] (2026-09-19)
- **Verdict**: APPROVE — grounded in the read-only u09 survey + the user-ratified "files-are-real for reads
  (lighter)" direction. Metadata add (input not in union; L1 write capstone gains no-exec input()); closure =
  read-into-list via range (u09 has range, no while), no .split() (Book-2), file methods taught; SHAPE 10
  file-read-satisfied / 6 value-save / 7 in-memory read-into-list / 2 exempt; no new design class (per user).
  Self-flagged judgment forks for the gate:
  - **Ex9 (prove-"w"-replaces):** exempt-as-file-mechanic-demonstrator vs read-into-list — flagged.
  - **File-read-satisfied note wording:** the 10 read tasks get a `**Real version:**` note (no form); the gate
    ratifies the exact note wording.
  - **Ex16 threshold / Ex14 search-target:** file-read tasks with a secondary fixed literal — kept fixed (file
    read satisfies the norm); a reviewer may argue the literal deserves a single read. Flagged.

#### [fable] (2026-09-19)
- **Verdict**: APPROVE WITH NITS — no Must-Fix; the "files-are-real (lighter)" direction applied coherently
  per exercise; metadata/closure correct; no misclassification; Ex17-23 verified file-less; Phase B present.
  5 Should + Nice, all FOLDED: (1) Ex9 relabeled predict/trace (§1 class 3; "demonstrator" collided with the
  designated-demonstrator term); (2) L1 has no put-it-together — pair the form with the `scores=[1200,850,990]`
  loop-write cell, insert AFTER the last L1 cell so the ladder isn't split; (3) Ex21/Ex22 now READ `budget`
  (consistent with Ex20/Ex23 reading their scalar; budget isn't in output so not value-coupled); (4) Phase B
  names the Ex7/Ex24/Ex25 cross-exercise harness (prepend Ex6 helpers + pre-write savegame.txt); (5) Ex14
  `target_name` + Ex5 `names_to_test` + Ex3/Ex11 labels get "keep fixed" parentheticals; FileNotFound demo →
  class 3; the 23-cues-vs-13-blocks count is expected (not drift).

#### [sol] (2026-09-19)
- **Verdict**: REJECT. 3 Must + 1 Should (metadata/closure/Ex17-23-file-less/Phase-B otherwise verified):
1. `[OPEN]` Must: **Ex9 not exempt** — it RUNS a save over `[42,77]` (not predict/trace, which is on-paper-
   without-running; [fable]'s class-3 label was wrong). Reclassify → value/save **read-into-list** (pipe [42,77]
   preserves the "w"-replacement demo + parity). Update counts + Phase B totals.
2. `[OPEN]` Must: **Ex14 hybrid** — `target_name="Mina"` is the QUERY (same role as Ex23's target, which is
   read) → give Ex14 a single-read target + the file read. (Ex16 threshold stays fixed = scenario rule, OK.)
3. `[OPEN]` Must: **§3 data growth missing** — the blanket "no data growth" conflicts with §3: core score lists
   are <4-element (lesson loop-write=3, Ex1=3, Ex6=3, Ex9=2) → §3 requires growing <4-element core SOURCE lists
   to ≥4 (u07 precedent); Ex9's 2-element shape is directly prohibited. Grow the core twins + update asserts/
   outputs; enrichment "small fixed data" drills (Ex12-23) stay small.
4. `[OPEN]` Should: **L3-note contradiction** — audit promises a file-is-real note but Phase A says L3
   unchanged; specify the `**Real version:**` note wording + placement for the 2 L3 file-read capstones.

#### [glm] (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: APPROVE WITH NITS — all 6 checkpoints confirmed (metadata add necessary; closure; 10 file-reads
  genuine; lesson audit matches; 10+6+7+2=25 no misclass; Phase B present). (Did NOT audit §3 list sizes — the
  [sol]#3 growth gap stands.) Should: (1) budget asymmetry Ex21/22 vs Ex20/23 — read budget too [already folded];
  (2) ratify Ex14/Ex16 secondary literals in ## Plan Review so the content gate doesn't re-litigate. Nice: Ex9
  label loose (superseded by [sol]#1 → read-into-list); note the L1 settings-write is a rung (coverage in
  Ex4/Ex10); cp03/cp04/project plans should cite plan 060 by path for the file-is-real precedent.

### Round 1 — outcome: REJECT (1 of 4 [sol]; [glm]/[fable] APPROVE-WITH-NITS). Fixed → round 2.
**Round 1 responses (plan revised):**
- → [FIXED] [sol]#1 Ex9 → value/save **read-into-list** (not exempt; it runs a save, not predict/trace).
- → [FIXED] [sol]#2 Ex14 → **hybrid**: file-read (satisfied) + single-read `target` (the query; ≈ Ex23). Ex16
  threshold stays fixed (scenario rule — ratified per [glm]#S2).
- → [FIXED] [sol]#3 **§3 data growth** — new "## Data growth (§3)" section: grow the <4-element core SOURCE
  score lists (lesson loop-write, Ex1, Ex6, Ex9) to ≥4; update asserts/outputs/real-forms + the ripple chain
  (Ex1→Ex2/Ex3; Ex6→Ex7/Ex11/Ex12–16/Ex24/Ex25; lesson L1); only the file-less Ex17–23 in-memory drills stay small.
- → [FIXED] [sol]#4 L3 note — specified the `**Real version:**` file-is-real note after the 2 L3 file-read
  capstones (audit/Phase A reconciled).
- → [FIXED] [glm] budget read (Ex21/22) [folded]; L1 settings-write rung clause; precedent-citation note.
- → [FIXED] [fable] round-1 Should/Nice (all folded above/earlier).
Re-dispatching round 2.

### Round 2 (2026-09-20) — re-review of the round-1 fixes (7e71ba4)
#### [fable] round 2
- **Verdict**: APPROVE WITH NITS — all 3 [sol] Must-Fixes verified landed (Ex9→read-into-list; Ex14 hybrid;
  §3 growth names the right 4 core <4-element lists); folded items intact; nothing regressed. 1 Should + 3 Nice,
  all FOLDED: (1) **§3 growth RIPPLE** enumerated (Ex1→Ex2/Ex3; Ex6→Ex7/Ex11/Ex12–16/Ex24/Ex25; lesson L1) +
  Phase B harness literals replaced with the GROWN values (were stale pre-growth [300,450,725]) + "enrichment
  stays small" scoped to the file-less Ex17–23 only; (2) Phase B "twins unchanged" reworded to except the grown
  twins + dependents; (3) Ex14 "hybrid" relabeled "file-satisfied + query read" (no missing §1 No-real cue);
  (4) Ex9 growth values note.

#### [sol] round 2 (2026-09-20)
- **Verdict**: APPROVE WITH NITS — all 4 round-1 findings RESOLVED (Ex9 read-into-list; Ex14 hybrid; §3 growth
  names the exact 4 <4-element core lists + enumerates the ripple; L3 notes placed); metadata/closure/Ex17-23-
  file-less/Phase-B all OK. 2 stale-wording nits FOLDED: out-of-scope "enrichment untouched" → scoped to the
  file-less Ex17-23 (Ex12-16 grow with the chain); "10 read tasks" → 9 file-read + hybrid Ex14. (Historical
  round-1 verdict quotes retain their original wording.)

#### [glm] round 2 (2026-09-20, volcengine-plan/glm-5.3)
- **Verdict**: APPROVE WITH NITS — all 4 [sol] Musts + folded Shoulds genuinely fixed (audited every list: the
  §3 section names EXACTLY the 4 core <4-element score lists, none missed; Ex17=5/Ex18-23=4 already ok; Ex9 runs
  a save [not predict/trace]; Ex14 query read; metadata/closure/Phase-B all verified). 2 Should + 3 Nice FOLDED:
  §3 lockstep now names statement-side carriers + downstream asserts; Phase B harness uses grown values (already);
  Ex14 harness pre-writes settings.txt; "twins unchanged" reworded; Ex5 §3 parenthetical present.

### PLAN-REVIEW GATE CLOSED (2026-09-20) — 4-way consensus:
[self] APPROVE · [sol] APPROVE WITH NITS · [glm] APPROVE WITH NITS · [fable] APPROVE WITH NITS (all nits folded).
No open blockers. (Novel file-unit fork user-ratified: "files-are-real for reads (lighter)"; §3 data-growth of
the 4 core <4-element score lists + its ripple chain is in scope.)

## Content Review
_(pending — 4-way, post-implementation.)_

## Post-Execution Report
_(pending.)_
