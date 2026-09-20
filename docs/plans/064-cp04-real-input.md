# Plan 064 — Checkpoint 04 (Year One Finale) real-input treatment

**Design:** `docs/designs/003-book1-real-input.md` (v6) + the u09 (plan 060) **files-are-real** precedent.
Checkpoint (non-unit) markdown path per plans 053/062/063 (cp01/cp02/cp03).

## Motivation

Checkpoint 04 (year-one-finale: classes, files, dicts) is the LAST checkpoint to receive the design-003
real-input norm. Same path as cp01/cp02/cp03: real-forms live in **`solutions.ipynb` markdown ONLY** (fenced
```python``` blocks under the mirrored `## Question N` heading); the student **`checkpoint.ipynb` stays
byte-unchanged**; **no metadata change**.
cp04 is the first CHECKPOINT that reads files, so it also applies the **u09 files-are-real** precedent: a pure
file-READ task is norm-satisfied by a `**Real version:**` note stating the file already IS real input — no
`input()` form, no new design class.

All 10 Book-1 units (u01–u10) + cp01 + cp02 + cp03 already carry the norm.

## Metadata change — NONE

cp04 real-forms use only concepts already in the union (`class-def`, `init-method`, `attributes`, `methods`,
`file-read`, `file-write`, `with-statement`, `dict-literal`, `dict-access`, `dict-loop`, `list-literal`,
`list-append`, `list-index`, `list-sort`, `for-loop`, `list-loop`, `if-statement`, `in-operator`, `int-type`,
`type-conversion`, `string-concat`, `string-methods`, `f-string`, `print`, `variable`, `boolean`,
`error-messages`, `return-value`, `parameters`, `arithmetic`, `string-literal`).
`input` is authored only in `solutions.ipynb` **markdown** → no `practices:[input]` add (design §5; cp01–cp03
precedent). No `.split()` (Book-2).

## Read idiom — FIXED-COUNT reads

cp04's union has **no `range-function` and no `while-loop`**, so read-into-list / read-into-dict uses the
**fixed-count read idiom** (u08 precedent) matching the frozen twin's length. Scalars read once.

## Per-question SHAPE table (8 questions)

| Q | Prompt kind | Class (v6) | Treatment |
|---|-------------|-----------|-----------|
| Q1 | `class Hero`, construct `Hero("Ada")`, print attrs | **read-and-compute** (class construct-and-drive) | REAL-FORM — read the name, `Hero(name)`, class unchanged |
| Q2 | `Hero`+`heal`, `hero.heal(3)`, print | **read-and-compute** (class, multi-value) | REAL-FORM — read name + heal amount (2 distinct reads) |
| Q3 | `scores=[40,90,20]` → write finale.txt | **read-and-compute** (save) | REAL-FORM — fixed-count read of 3 scores, then unchanged file-write |
| Q4 | read finale.txt line-by-line → `loaded`, print | **files-are-real** (u09) | `**Real version:**` note — the file IS real input; NO `input()` form |
| Q5 | sort `loaded` desc, print top (no `max`) | **files-are-real** (u09, continuation) | `**Real version:**` note — sorts data loaded from the real file in Q4; NO `input()` form |
| Q6 | `inventory={…}` → `for item,count in .items()` print | **read-and-compute** (dict, generic iterate) | REAL-FORM — fixed-count dict read (2 entries), then unchanged `.items()` loop |
| Q7 | `"sword" in inventory`, `if "shield"` branch | **fixed-reference-fixture** (class 4) | EXEMPT — `**No real version:**` note; a pre-authored lookup table — the graded skill is guarded membership/lookup over a GIVEN dict, and its asserted output (`True`, `no shield`) depends on that specific fixture. (Q7 GUARDS `inventory["shield"]` with `if "shield" in inventory`, so it wouldn't crash on other data; it's exempt because it's a fixture and Q6 is the chosen dict demonstrator, NOT because arbitrary reads break it — [sol] NIT-1.) |
| Q8 | KeyError traceback → name + guard with `if in` | **debug/fix-the-error** (class 2) | EXEMPT — `**No real version:**` note; the fix reads no input |

**4 real-forms (Q1, Q2, Q3, Q6); 2 files-are-real notes (Q4, Q5); 2 exempt notes (Q7 class 4, Q8 class 2).**

Dict value-type: Q6 (generic `.items()` iteration — naturally reads any dict and reports it) is the chosen
**read-and-compute demonstrator** for cp04; Q7 is a **fixed-reference-fixture** — the graded skill is guarded
membership/lookup over a GIVEN table, and its asserted output (`True`, `no shield`) is a property of that
specific fixture. Q7 is exempt as a per-plan coverage choice (§1 designated-demonstrator: Q6 already carries the
dict demonstrator), NOT because it would crash on other data — its `inventory["shield"]` is guarded by
`if "shield" in inventory` ([sol] NIT-1 correction). (Contrast cp03-Q6, whose UNGUARDED `prices["pear"]` genuinely
would crash on arbitrary reads — a different, also-valid reason for that fixture's exemption.)

### Real-form specifications (solutions markdown; §6c preserve twin structure + blank lines; asserts/scaffolding dropped)

- **Q1**: class `Hero` unchanged; `name = input("Hero name? ")`; `hero = Hero(name)`; print `hero.name`/`hero.health`.
- **Q2**: class `Hero`+`heal` unchanged; read `name` (string) AND `amount = int(input("Heal by how much? "))`;
  `hero.heal(amount)`; print returned value. Two distinct reads (multi-value reads-every-value).
- **Q3**: `scores = [int(input("Score 1? ")), int(input("Score 2? ")), int(input("Score 3? "))]`; then the
  unchanged `with open("finale.txt", "w") as f: for score in scores: f.write(str(score) + "\n")`.
- **Q6** (§4 canonical dict sequence idiom, [fable] NIT-3): `inventory = {}` then
  `inventory[input("Item 1? ")] = int(input("Count 1? "))` and
  `inventory[input("Item 2? ")] = int(input("Count 2? "))`; then the unchanged
  `for item, count in inventory.items(): print(f"{item}: {count}")` (the twin's `lines` accumulator is assert
  scaffolding → dropped, like dropped asserts).

Each real-form reads every distinct SOURCE value (Q1 one name; Q2 name+amount; Q3 three scores; Q6 two item/count
pairs). Captions: cp01-style parenthetical after `**The real program**`, with usage hints ([glm] g3): Q2 "a
whole number" for the heal amount; Q6 "two different items" (a duplicate key would collapse).

### files-are-real notes (Q4, Q5 — u09 precedent, NOT a v6 exempt class)

- **Q4**: `**Real version:**` — `finale.txt` is a real file on disk (written by Q3); `for line in f` already
  reads whatever scores it actually contains, so the file read IS the real program — no separate `input()` form.
- **Q5**: `**Real version:**` — `loaded` already holds real data read from `finale.txt` in Q4; sorting it and
  printing the top score is the real program — no separate `input()` form.

## Data growth (§3) — N/A (byte-frozen checkpoint)

Q3's `scores=[40,90,20]` (3) and `finale.txt` (3 lines) are frozen; the real-form mirrors the count (reads 3).
As with cp02/cp03, the checkpoint-path invariant keeps the assessment byte-frozen, so §3 growth does not apply.

## Phases

### Phase A — apply to cp04 solutions.ipynb (markdown only; NO checkpoint.ipynb / manifest / finale.txt / metadata change)

For Q1/Q2/Q3/Q6: add a `**The real program**` markdown cell (cp01-style caption + fenced ```python``` block per
spec, §6c blank lines preserved) immediately AFTER the executable solution cell.
For Q4/Q5: add a `**Real version:**` files-are-real note (no code block).
For Q7/Q8: add a `**No real version:**` note naming the v6 class (Q7 fixed-reference-fixture / class 4; Q8
debug/fix-the-error / class 2).
`checkpoint.ipynb`, `manifest.yaml`, `teacher-notes.md` are NOT touched (byte-unchanged; teacher-notes audit
expected no-op). `finale.txt` is a **gitignored build artifact** (.gitignore:31), regenerated by the Q3 twin
during `exec-solutions`; the plan adds no code that writes it, and its post-CI bytes must remain `40\n90\n20\n`
([fable] NIT-1 — this is a byte invariant, not a git-diff one).

### Phase B — verification

- ci-local ALL GREEN (`TMPDIR=/dev/shm bash scripts/ci-local.sh`): registry+lint, notebook execution+hygiene
  (checkpoint_solutions heading mirror intact — no unfenced bare `## Question <digit>`), manifest/prereq/
  coverage, PDF build, pre-merge guard. (Q3 twin writes finale.txt with the same 40/90/20, so no diff.)
- Real-form validation: `ast.parse` each fenced block + piped-run **in a SCRATCH cwd** ($TMPDIR — [fable] NIT-2,
  so the Q3 write never clobbers the checkpoint-dir `finale.txt`), compare COMPUTED result line(s) to the twin
  MODULO prompt text — Q1 `Ada`→`Ada`,`10`; Q2 `Ada`/`3`→`13`; Q6 `sword`/`1`/`potion`/`3`→`sword: 1`,`potion: 3`.
  Q3's oracle is a DIRECT BYTE COMPARE ([sol] NIT-6): run it on `40/90/20` in a scratch cwd, then assert the
  written `finale.txt` bytes equal exactly `40\n90\n20\n` (not merely a reread into `[40,90,20]`, which would
  miss stray whitespace / leading zeros / blank lines).
- Confirm 0 `input()` in any `solutions.ipynb` **code** cell (real-forms are markdown).
- Scope invariant: `git diff --quiet` for checkpoint.ipynb, manifest.yaml, teacher-notes.md (tracked files);
  and `finale.txt` (gitignored) bytes remain `40\n90\n20\n` after CI ([fable] NIT-1 — a `cmp`/byte check, since
  git cannot diff an ignored file).

## Out of scope

- No new questions, no difficulty change, no checkpoint.ipynb edit, no metadata change. `finale.txt` is a
  gitignored artifact the plan never writes (its bytes stay `40\n90\n20\n`, regenerated by the Q3 twin).
  teacher-notes.md audit-only (expected no-op). Only `solutions.ipynb` is modified.
- **Verification exemption:** checkpoint-content plan; Phase B is the named verification phase.
- Projects (project-01, project-02) are separate plans — the last rollout slice after cp04.

## Plan Review

### Round 1 (2026-09-20) — [self] inline; [sol] gpt-5.6-sol; [glm] volcengine-plan/glm-5.3; [fable] Fable 5.

#### [self] (2026-09-20)
**APPROVE.** Q1/Q2 class construct-and-drive read-and-compute (Q2 multi-value: name + heal amount); Q3 save
read-and-compute (fixed-count 3 scores → write); Q6 dict read-and-compute (generic `.items()` iterate — safe to
read arbitrary dict). Q4/Q5 files-are-real (u09) — the correct call for a checkpoint's file-read pipeline
(Q4 reads finale.txt; Q5 sorts the loaded data), no awkward input() form. Q7 EXEMPT fixed-reference-fixture
(class 4 — hardcoded `sword`/`shield` lookups + branch break on arbitrary reads, like cp03 Q6); Q8 EXEMPT class 2
(fix reads no input). The Q6-real-form vs Q7-exempt split is principled (generic-iterate vs hardcoded-key).
Fixed-count idiom correct (no range/while). Metadata NONE. finale.txt stays byte-unchanged (Q3 twin writes the
same 40/90/20); added to the Phase-B scope check. §3 N/A (frozen). No `.split()`. Phase B is the named
verification phase.

#### [fable] (2026-09-20)
**APPROVE WITH NITS** (no blockers). All 8 classifications correct (Q1/Q2 read-and-compute; Q3 save mirrors
u09's value/save row; Q4/Q5 files-are-real verbatim per u09 — forcing input() would replace the assessed skill;
Q6 vs Q7 split principled + Q6 satisfies class-4 designated-demonstrator for cp04's dict value-type; Q8 class 2).
Pedagogy OK (union-only, `int()` never_flag, no `.split()`). Real-forms realize the task (Q3 keeps the write
loop; Q6 keeps `.items()`; note dict-literal evaluates key-before-value so prompt order is fine). Nits:
- **NIT-1 (factual — FOLD):** `finale.txt` is GITIGNORED (.gitignore:31, verified `git check-ignore`), so a
  `git diff --quiet` on it is vacuous. The invariant is a BYTE-COMPARE against `40\n90\n20\n` after CI (the Q3
  twin regenerates it via `exec-solutions`), not git diff. → Phase A/B reworded.
- **NIT-2 (FOLD):** the Q3 real-form writes `finale.txt` relative to cwd; its piped validation must run in a
  SCRATCH cwd ($TMPDIR) so it never clobbers the checkpoint-dir artifact the Q4/Q5 twins depend on. → Phase B pinned.
- **NIT-3 (FOLD):** Q6 — switch the dict read to the §4 canonical sequence idiom (`inventory = {}` then
  `inventory[input("Item 1? ")] = int(input("Count 1? "))` ×2) rather than a dict-literal-of-reads; reuses the
  design/u08 idiom and reads more clearly for a middle-schooler. → spec updated.

#### [glm] (2026-09-20)
**APPROVE WITH NITS — no open blockers.** Classifications 8/8 correct (verified parity by own piped execution:
Q1 Ada→Ada,10; Q2→13; Q3 writes [40,90,20]; Q6 sword/1/potion/3→"sword: 1","potion: 3"). Q3 matches u09
value/save row; Q4/Q5 files-are-real (Q5 pure continuation, no query unlike u09 Ex14 hybrid); Q6-real vs
Q7-exempt principled (Q6 = u08-Ex7 demonstrator shape). Fixed-count correct; closure pass; metadata NONE;
heading-mirror safe (notebooks.py:164-196 strips fences); §3-N/A right. Nits (reviewed pre-fold draft):
- g1 (Q6 dict literal-of-reads vs §4 sequence) — SUPERSEDED: already switched Q6 to the §4 sequence idiom per
  [fable] NIT-3.
- g4 (Q3 piped-run in temp dir) — SUPERSEDED: already pinned scratch-cwd per [fable] NIT-2. (Also: [fable] NIT-1
  corrected the finale.txt invariant to a byte-compare since it's gitignored — supersedes [glm]'s git-diff note.)
- g2: union enumeration omits `arithmetic`/`string-literal` (both in the manifest union, used by real-forms) →
  FOLD (completeness).
- g3 (optional): caption hints — Q2 "a whole number" for the amount; Q6 "two different items" (duplicate key
  collapses) → FOLD in implementation.

#### [sol] (2026-09-20) — reviewed stale draft 5d7222c (pre-fold)
**REJECT** on the draft. Assessed against current HEAD:
- BLOCKER 5 + 7 (finale.txt gitignored → git-diff vacuous; needs scratch-cwd probe + byte-compare to
  `40\n90\n20\n`): **already resolved** by the [fable] NIT-1/NIT-2 folds (66a21ca) — the current plan states
  exactly this.
- NIT 2 (Q6 → §4 sequence idiom): already folded.
- NIT 6 (Q3 oracle should be a direct byte-compare, not reread-into-ints): FOLDED — Phase B now asserts the
  written bytes equal `40\n90\n20\n`.
- **NIT 1 (valid new catch): the Q7 "hardcoded keys break arbitrary reads" rationale is FALSE** — Q7 guards
  `inventory["shield"]` with `if "shield" in inventory`, so it wouldn't crash. Correct rationale: Q7 is a
  pre-authored lookup fixture (guarded membership/lookup over a GIVEN table), exempt as the per-plan
  coverage choice (Q6 is the dict demonstrator). FOLDED into the SHAPE row + dict paragraph.

### Round 1 — outcome: [self]/[fable]/[glm] APPROVE (with nits, all folded); [sol] REJECT on the STALE draft
whose BLOCKERs (finale.txt) were ALREADY fixed in HEAD before [sol] ran, plus a valid Q7-rationale NIT-1 and the
Q3 byte-compare NIT-6 (both now folded). Re-dispatching [sol] on the corrected plan to convert REJECT→APPROVE
before implementing (no 3-of-4 shortcut on a REJECT).

#### [sol] round 2 (2026-09-20) — re-verify on 381b41d
**APPROVE.** All four findings RESOLVED: (5+7) finale.txt identified as gitignored artifact, scratch-cwd probe +
exact byte-compare (not git diff); (6) Phase B asserts bytes `40\n90\n20\n`; (1) Q7 rationale corrected (guarded
lookup, exempt as fixture/coverage-choice with Q6 the demonstrator); (2) Q6 uses the §4 sequence idiom.
Reconfirmed unchanged: 8 classifications, closure, metadata NONE, counts (Q3=3/Q6=2), heading-mirror, §3-N/A,
Phase B named.

### Round 1 — FINAL outcome: **FULL 4-way plan-review consensus.** [self]/[fable]/[glm]/[sol] APPROVE (all nits
folded; [sol] REJECT→APPROVE after Q7-rationale + Q3-byte-compare folds). Gate CLOSED → implementation.

## Content Review
_(pending)_

## Post-Execution Report
_(pending)_
