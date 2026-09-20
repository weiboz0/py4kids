# Plan 063 — Checkpoint 03 (Data Wrangler) real-input treatment

**Design:** `docs/designs/003-book1-real-input.md` (v6). Checkpoint (non-unit) markdown path per plans 053/062 (cp01/cp02).

## Motivation

Checkpoint 03 (data-wrangler: strings, lists, dicts) is the third checkpoint to receive the design-003
real-input norm.
Same path as cp01/cp02: real-forms live in **`solutions.ipynb` markdown ONLY** (fenced ```python``` blocks
under the mirrored `## Question N` heading); the student **`checkpoint.ipynb` stays byte-unchanged**;
**no metadata change** (markdown is invisible to concept-scan / solution-policy).
The executable asserted reference solution (code cell) stays as the VALIDATED logic; each real-form swaps the
fixed values for `input()` reads.

All 10 Book-1 units (u01–u10) + cp01 + cp02 already carry the norm.

## Metadata change — NONE

cp03 real-forms use only concepts already in the union (`string-index`, `string-slice`, `string-methods`,
`in-operator`, `list-literal`, `list-index`, `list-append`, `list-loop`, `list-sort`, `builtin-functions`,
`dict-literal`, `dict-access`, `dict-loop`, `for-loop`, `if-statement`, `boolean`, `accumulator`, `arithmetic`,
`int-type`, `elif-else`, `f-string`, `string-literal`, `print`, `variable`, `error-messages`).
`input` is authored only in `solutions.ipynb` **markdown** → no `practices:[input]` add (design §5; cp01/cp02
precedent). No `.split()` (Book-2). `int()` = type-conversion is in-union (`int-type`).

## Read idiom — FIXED-COUNT reads

cp03's union has **no `range-function` and no `while-loop`**, so read-into-list uses the **fixed-count read
idiom** (u08 precedent): a list literal of N `input()` reads matching the frozen twin's length
(`scores = [int(input(...)), int(input(...)), ...]`); no loop drives the read. Single scalars read once.

## Per-question SHAPE table (8 questions)

| Q | Prompt kind | Class (v6) | Treatment |
|---|-------------|-----------|-----------|
| Q1 | `word="wizardry"` → f-string of index/slice/reverse | **read-and-compute** (string) | REAL-FORM — read one word (`input()`), unchanged f-string |
| Q2 | `phrase=…` → `strip().lower().replace(",", "")` + `in` | **read-and-compute** (string) | REAL-FORM — read one phrase, unchanged clean + membership |
| Q3 | `scores=[88,92,75]` → append 100, print first/last | **read-and-compute** (list) | REAL-FORM — fixed-count read of 3 scores, unchanged append + index |
| Q4 | `scores=[88,92,75,100]` → loop/len/max/min/sum | **read-and-compute** (list) | REAL-FORM — fixed-count read of 4 scores, unchanged loops/builtins |
| Q5 | `scores=[88,92,75,100]` → `sort(reverse=True)`, top 3 | **read-and-compute** (list) | REAL-FORM — fixed-count read of 4 scores, unchanged sort + top-3 |
| Q6 | `prices={…}` → lookups + membership branch | **fixed-reference-fixture** (class 4) | EXEMPT — `**No real version:**` note. The dict's specific keys (`pear`/`apple`/`plum`) drive the lookups and the `in` branch; reading arbitrary prices would break `prices["pear"]` and the tests |
| Q7 | `words=[…]`, `counts={}` → count into dict, report | **read-and-compute** (list→dict) | REAL-FORM — fixed-count read of 5 words, unchanged counting + `.items()` report |
| Q8 | KeyError traceback → name + fix with `.get` | **debug/fix-the-error** (class 2) | EXEMPT — `**No real version:**` note; the fix `.get("fig",0)` reads no input |

**6 real-forms (Q1, Q2, Q3, Q4, Q5, Q7); 2 exempt (Q6 fixed-reference-fixture, Q8 debug).**

Designated-demonstrator (§1) — honest accounting ([fable] plan-review nit a): cp03's ONLY dict fixture task is
Q6, and it CANNOT be a structure-read demonstrator without breaking its hardcoded-key logic (`prices["pear"]`,
the `in` branch), so **cp03 carries no dict structure-read real-form**. Dict *construction from input* is still
shown by Q7 (reads a word list → builds `counts`), but Q7 is a list-read, not a §4 dict structure-read
(`d[input()] = input()`). The §1 designated-demonstrator rule is **per-unit**, and Book-1's dict structure-read
demonstrators already live in u08 (Ex7/Ex13, plan 059) — cp03 need not add one. Q6 is therefore exempt as a
fixed-reference-fixture, which is the correct and non-awkward outcome.

### Real-form specifications (solutions markdown, mirrored heading; §6c preserve twin structure + blank lines)

- **Q1**: `word = input("Type a word: ")` then the unchanged `print(f"{word[0]} {word[-1]} {word[2:5]} {word[::-1]}")`.
- **Q2**: `phrase = input("Type a phrase: ")` then unchanged `cleaned = phrase.strip().lower().replace(",", "")` / `print("data" in cleaned)`.
- **Q3**: `scores = [int(input("Score 1? ")), int(input("Score 2? ")), int(input("Score 3? "))]` then unchanged `scores.append(100)` / `print(scores[0])` / `print(scores[-1])`.
- **Q4**: fixed-count read of 4 scores, then unchanged print-loop / `len`/`max`/`min` / accumulator-sum loop.
- **Q5**: fixed-count read of 4 scores, then unchanged `scores.sort(reverse=True)` / print `[0]`,`[1]`,`[2]`.
- **Q7**: `words = [input("Word 1? "), input("Word 2? "), input("Word 3? "), input("Word 4? "), input("Word 5? ")]` then the unchanged counting loop + `.items()` report.

Each real-form reads every distinct SOURCE value (Q3 three scores, Q4/Q5 four, Q7 five words; Q1/Q2 one string);
task CONSTANTS stay fixed (Q3's `append(100)` operand — the appended value is part of the task structure, not
source data, cp01-Q7 `secret=8` precedent). Q1's caption asks for a word ≥5 letters (so `[2:5]` is meaningful
and `[0]`/`[-1]` never hit empty input — [fable] fb / [sol] N2). Captions: cp01-style parenthetical after
`**The real program**`.

## Data growth (§3) — constrained by the byte-frozen checkpoint

cp03 has score/word lists (Q3 has a 3-element source, Q4/Q5 four, Q7 five). §3 realism growth is NOT applied:
the **checkpoint.ipynb is byte-unchanged** (the checkpoint-path invariant), so the frozen twins' source counts
cannot be grown without editing the assessment. Each real-form mirrors its frozen twin's count (Q3 reads 3,
Q4/Q5 read 4, Q7 reads 5). This is consistent with cp01/cp02: the norm ADDS real-forms without altering the
frozen assessment; §3 realism governs unit TEACHING data, not frozen checkpoint questions.

## Phases

### Phase A — apply to cp03 solutions.ipynb (markdown only; NO checkpoint.ipynb / manifest / metadata change)

For each of Q1/Q2/Q3/Q4/Q5/Q7: add a markdown cell immediately AFTER the executable solution cell —
`**The real program**` + cp01-style caption + a fenced ```python``` block per the spec, preserving the twin's
structure and blank lines (§6c).
For Q6/Q8: add a `**No real version:**` note naming the v6 class (Q6 fixed-reference-fixture / class 4; Q8
debug/fix-the-error / class 2).
`checkpoint.ipynb`, `manifest.yaml`, `teacher-notes.md` are NOT touched (byte-unchanged; teacher-notes audit is
expected to be a no-op — verify grep shows no stale `input` claim).

### Phase B — verification

- ci-local ALL GREEN (`TMPDIR=/dev/shm bash scripts/ci-local.sh`): registry+lint, notebook execution+hygiene
  (checkpoint_solutions heading mirror intact — no unfenced bare `## Question <digit>` added), manifest/prereq/
  coverage, PDF build, pre-merge guard.
- Real-form validation: `ast.parse` each fenced block + piped-run, compare the COMPUTED result line(s) to the
  executable twin MODULO prompt text — Q1 `wizardry`→`w y zar yrdraziw`; Q2 the frozen phrase→`True`;
  Q3 `88/92/75`→`88`,`100`; Q4 `88/92/75/100`→`88`,`92`,`75`,`100`,`4`,`100`,`75`,`355` (8 lines); Q5
  `88/92/75/100`→`100`,`92`,`88`; Q7 `cat/dog/cat/bird/cat`→`cat 3`,`dog 1`,`bird 1`.
- Confirm 0 `input()` in any `solutions.ipynb` **code** cell (real-forms are markdown).
- Scope invariant: `git diff --quiet` for checkpoint.ipynb, manifest.yaml, teacher-notes.md (plan 062 precedent).

## Out of scope

- No new questions, no difficulty change, no checkpoint.ipynb edit, no metadata change. teacher-notes.md is
  audit-only (expected no-op). Only `solutions.ipynb` is modified.
- **Verification exemption:** checkpoint-content plan; Phase B is the named verification phase.
- cp04 and projects are separate plans.

## Plan Review

### Round 1 (2026-09-20) — [self] inline; [sol] gpt-5.6-sol; [glm] volcengine-plan/glm-5.3; [fable] Fable 5.

#### [self] (2026-09-20)
**APPROVE.** Q1/Q2 string read-and-compute; Q3/Q4/Q5 list read-and-compute (fixed-count 3/4/4); Q7 list→dict
read-and-compute (fixed-count 5). Q6 EXEMPT as fixed-reference-fixture (class 4) — the key judgment call, sound:
`prices["pear"]` and the `"apple"/"plum" in prices` branch hardcode fixture keys, so reading arbitrary prices
would break the assessed lookups; the designated-demonstrator rule is met by Q7 (dict construction-from-input).
Q8 EXEMPT class 2 (fix reads no input). Fixed-count read idiom correct (no range/while in union; u08 precedent).
Metadata NONE (markdown path). §3 N/A — the checkpoint is byte-frozen, so source counts can't grow without
editing the assessment; real-forms mirror frozen counts. No `.split()`; `int(input())` in-union (`int-type`).
Phase B is the named verification phase incl. the heading-mirror guard + scope `git diff --quiet`.

#### [fable] (2026-09-20)
**APPROVE WITH NITS.** Validated all 8 classifications (Q6 fixture-exempt confirmed via the `branch_taken=="pear"`
assert + hardcoded keys; Q8 class-2 fix reads nothing); pipe-ran Q1/Q2/Q7 → `w y zar yrdraziw`/`True`/`cat 3,
dog 1, bird 1` match twins; closure clean (int-type never_flag, no `.split()`/range/while); §3-N/A sound; Phase B
adequate. Nits (non-blocking):
- (fa) designated-demonstrator wording overstated — Q7 is a list-read that builds a dict, not a §4 dict
  structure-read; cp03 carries no dict structure-read (Q6 can't be one), and Book-1's dict demonstrators are
  u08 Ex7/Ex13. → FOLDED into the SHAPE section (reworded).
- (fb) Q1 real-form: empty input → `word[0]` IndexError; caption should ask for a word ≥5 letters (matches
  cp02's usage-hint captions). → FOLD in implementation (Phase A).

#### [glm] (2026-09-20)
**APPROVE WITH NITS — no open blockers.** All 6 oracles verified by ACTUAL piped execution (Q1→`w y zar
yrdraziw`, Q2→`True`, Q3→88/100, Q4→…355, Q5→100/92/88, Q7→cat 3/dog 1/bird 1). Q6 fixture-exempt confirmed
(twin asserts `branch_taken=="pear"`; arbitrary reads break the lookup + branch; v6 §1 "per-plan coverage
choice"). Q8 valid class-2. Fixed-count idiom = only in-union option (no range/while), matches u08 line 206.
Metadata NONE correct (scan code cells only). §3-N/A right (frozen checkpoint; count forced by §6b/c). Heading-
mirror robust (notebooks.py:191 strips fences). Nits (cosmetic, no revision round required):
- (g1) demonstrator framing — same as [fable] fa (FOLDED); [glm]'s tighter grounds: the §1 rule is per-unit,
  u08 owns Book-1's dict demonstrators (solutions 296–300), checkpoints aren't bound.
- (g2) Metadata union enumeration omits `print`/`variable`/`error-messages` — add for completeness. → FOLD.
- (g3) Q4 Phase-B oracle abbreviated (`…355`) — spell out all 8 lines for a self-contained check. → FOLD.
- (g4) "reads every distinct fixed value" — distinguish SOURCE data (read) from task CONSTANTS kept fixed
  (Q3's append operand `100`, cp01-Q7 precedent). → FOLD (wording).

#### [sol] (2026-09-20)
**APPROVE WITH NITS.** Verified parity by fresh execution (Q1 `w y zar yrdraziw`, Q2 `True`, Q3 88/100, Q4
88/92/75/100/4/100/75/355, Q5 100/92/88, Q7 cat 3/dog 1/bird 1). Q6 properly class-4 (question fixes keys
pear/apple/plum; solution asserts the `pear` branch — arbitrary keys break it). Q8 valid class-2 (fix reads no
input). Fixed-count idiom correct (no range/while); counts confirmed against frozen cells (3/4/4/5). Closure
pass; metadata correct; §3-N/A correct; CI heading-mirror guarded; Phase B adequate.
- N1 (demonstrator framing) — same as [fable] fa / [glm] g1: state the rule is INAPPLICABLE here (per-unit;
  u08 owns Book-1's dict demonstrators), not "satisfied by Q7". → FOLDED.
- N2 (Q1 caption) — same as [fable] fb: ask for a non-empty word, ≥5 letters, so `[2:5]` stays meaningful. →
  FOLD in implementation.

### Round 1 — outcome: **FULL 4-way plan-review consensus.** [self] APPROVE · [fable]/[glm]/[sol]
APPROVE-WITH-NITS · no open blockers. All nits folded (demonstrator wording reworded; g2/g3/g4 cosmetic below;
Q1 caption ≥5 letters applied in Phase A). Gate CLOSED → implementation.

## Content Review

### Round 1 (2026-09-20) — on implementation commit 2c5e98e. [self] inline; [sol]/[glm]/[fable] dispatched.

#### [self] (2026-09-20)
**APPROVE.** Verified on 2c5e98e: 6 real-forms (cp3-q1/q2/q3/q4/q5/q7-real) + 2 exemption notes
(cp3-q6/q8-no-real) added to solutions.ipynb only. Parity 6/6 modulo prompt (Q1 `w y zar yrdraziw`, Q2 `True`,
Q3 88/100, Q4 88/92/75/100/4/100/75/355, Q5 100/92/88, Q7 cat 3/dog 1/bird 1). Fixed-count reads match frozen
counts (3/4/4/5); Q3 append(100) constant kept. Q1 caption asks for a word ≥5 letters. Hygiene: 0 `input()` in
code cells; exactly 8 `## Question N` headings (mirror intact); 8 assert cells. Scope invariant clean
(checkpoint/manifest/teacher-notes byte-unchanged). Exemption notes name the class (Q6 class 4, Q8 class 2). No
`.split()`; `int(input())` in-union. ci-local ALL GREEN.

#### [fable] (2026-09-20)
**APPROVE WITH NITS — 0 `[OPEN]`.** Independently `ast.parse`d + pipe-ran all 6 real-forms; result lines match
the asserted twins modulo prompt (Q1 `w y zar yrdraziw`, Q2 `True`, Q3 88/100, Q4 …355, Q5 100/92/88, Q7 cat 3/
dog 1/bird 1); each is line-for-line its twin with only the literal→reads and asserts dropped (§6c). Closure
clean (all union concepts; `int-type` never_flag; no `.split()`); fixed-count counts match (3/4/4/5); Q7
`counts={}` correctly stays a literal (built, not read). Q6/Q8 exemption notes correct + name the class. Scope
diff shows solutions.ipynb only (+115). Nits (all `[WONTFIX]`-grade cosmetic):
- Q2 caption could add "(try typing spaces around it)" to make the `.strip()` step visible. → FOLD (cheap
  clarity gain).
- Q1 empty-entry IndexError already handled by the ≥5-letters caption — no change.
- Q6 note is one long sentence — could split. → optional.

#### [glm] (2026-09-20)
**APPROVE WITH NITS — 0 `[OPEN]`.** Piped-run 6/6 PASS (Q1 `w y zar yrdraziw`, Q2 `True`, Q3 88/100, Q4 8-line
…355, Q5 100/92/88, Q7 cat 3/dog 1/bird 1); all `ast.parse` clean. §6c diffs: each real-form = twin with exactly
two deltas (source-literal→fixed-count reads, asserts dropped); Q3 append(100)/Q4 total=0/Q7 counts={} stay
fixed; counts 3/4/4/5. Closure PASS (no `.split()`/range/while/sys.stdin; `int(input())` in-union; input
markdown-only → no metadata add; concept/prereq/coverage/manifest re-run PASS). Multi-value PASS. Q6/Q8
exemption notes name the class + genuinely exempt. Hygiene: 0 input() in code cells, 8 `## Question N` headings,
8 assert cells byte-preserved (+115/−0 pure insertions). Scope `git diff --quiet` clean. Nits:
- `[WONTFIX]` n1: Q2 caption thinner than cp02's usage-hint style — suggest typing spaces/comma to make
  `.strip()`/`.replace()` visible ([fable] flagged same). → FOLD (cheap).
- `[WONTFIX]` n2: Q4/Q5 read line ~110 chars, but §6c line-for-line forces it. Not a defect.

#### [sol] (2026-09-20)
**APPROVE — 0 `[OPEN]`, 0 `[WONTFIX]`.** Blind-solved all 6 real-forms (match); piped parity exact (Q1
`w y zar yrdraziw`, Q2 `True`, Q3 88/100, Q4 8 lines→355, Q5 100/92/88, Q7 cat 3/dog 1/bird 1). §6c AST-confirmed
(read counts 1/1/3/4/4/5; Q3 append(100) fixed). Closure clean (no `.split()`/range/while; `int(input())`
authorized). Q6 class-4 + Q8 class-2 exemptions correct. Hygiene: 0 input() in code cells, 8 headings, 8 asserts
preserved. Scope `git diff --quiet` clean.

### Content-review outcome: **FULL 4-way consensus.** [self] APPROVE · [sol] APPROVE · [fable]/[glm]
APPROVE-WITH-NITS (0 `[OPEN]`). No open blockers. Shared cosmetic nit folded post-consensus: Q2 caption now
suggests typing spaces/comma so `.strip()`/`.replace()` do visible work (ci-local re-verified GREEN). Gate CLOSED → PR.

## Post-Execution Report

**Status: COMPLETE.** Checkpoint 03 (data-wrangler: strings/lists/dicts) received the design-003 real-input
treatment via the checkpoint markdown path. Third checkpoint done (after cp01/cp02).

**What shipped** (branch `feature/plan-063-cp03-real-input`, `solutions.ipynb` only, +8 markdown cells):
- 6 real-forms — Q1/Q2 (read one string), Q3 (fixed-count read 3 scores + append 100), Q4/Q5 (read 4 scores),
  Q7 (read 5 words → counts dict). Fixed-count read idiom (cp03 union has no range/while; u08 precedent). Q1
  caption asks for a word ≥5 letters; Q2 caption prompts spaces/comma to exercise `.strip()`/`.replace()`.
- 2 exemption notes — Q6 fixed-reference-fixture (class 4; the price table's specific keys drive the lookups +
  membership branch, arbitrary reads would break `prices["pear"]`), Q8 debug/fix-the-error (class 2).
- **No metadata change** (markdown real-forms invisible to concept-scan; design §5). §3 growth N/A — the
  checkpoint is byte-frozen (real-forms mirror frozen counts). `checkpoint.ipynb`/`manifest.yaml`/
  `teacher-notes.md` byte-unchanged.

**Gate history**: plan-review FULL 4-way consensus (all APPROVE / APPROVE-WITH-NITS; [sol]/[glm] verified parity
by execution; folded demonstrator-framing wording + cosmetic nits) → implementation (2c5e98e) → content-review
FULL 4-way consensus (0 `[OPEN]`; [self]/[sol] APPROVE, [fable]/[glm] APPROVE-WITH-NITS) → Q2 caption nit folded.

**Verification**: `scripts/ci-local.sh` ALL GREEN; parity 6/6 modulo prompt; 0 `input()` in code cells;
heading-mirror intact (8 `## Question N`); scope invariant clean; `pre-merge-guard --pr`.

**Follow-ups**: none for cp03. cp04 (year-one-finale) is next — it has a `finale.txt`, so the u09
**files-are-real** precedent (file-read tasks norm-satisfied by a `**Real version:**` note, no input form) may
apply to any file-reading question there.
