# Plan 062 — Checkpoint 02 (Loops and Functions) real-input treatment

**Design:** `docs/designs/003-book1-real-input.md` (v6). Checkpoint (non-unit) markdown path per plan 053 (cp01).

## Motivation

Checkpoint 02 (loops-and-functions) is the second checkpoint to receive the design-003 real-input norm.
Following the cp01 precedent (plan 053, design v3 §2):
real-forms live in **`solutions.ipynb` markdown ONLY** (fenced ```python``` blocks under the mirrored
`## Question N` heading);
the student **`checkpoint.ipynb` stays byte-unchanged** (solution-free);
**no metadata change** (markdown real-forms are invisible to concept-scan / solution-policy, which scan code
cells only).
The executable asserted reference solution (code cell) stays as the VALIDATED logic;
each real-form is a thin adapter that swaps the fixed values for `input()` reads and (for §6d fragments)
proves termination + the result line.

All 10 Book-1 units (u01–u10) plus cp01 already carry the norm; this continues the rollout to cp02–cp04,
then projects.

## Metadata change — NONE

cp02 real-forms use only concepts already in the checkpoint's `requires`/`practices` union
(`int-type`, `while-loop`, `accumulator`, `def-function`, `parameters`, `return-value`, `comparison`,
`boolean`, `string-literal`, `f-string`, `for-loop`, `range-function`).
`input` is authored only in `solutions.ipynb` **markdown** — concept-scan cannot see it — so no
`practices:[input]` add (design §5; cp01 precedent). No `.split()` (Book-2), no list/dict.

## Per-question SHAPE table (8 questions)

| Q | Prompt kind | Class (v6) | Treatment |
|---|-------------|-----------|-----------|
| Q1 | Trace a `for range(4)` loop, predict output | **predict/trace** (class 3) | EXEMPT — `**No real version:**` note (class 3) |
| Q2 | Complete two `while`-accumulator blanks (sum 1→4) | fragment-completion → **read-and-compute** | REAL-FORM — read the upper bound `n`, sum `1..n` with the completed `while` (§6d oracle) |
| Q3 | Write `greeting(name)`, call + store + print | **read-and-compute** (functions arm) | REAL-FORM — read one name (string `input()`), `greeting(name)` unchanged |
| Q4 | Read two fns, explain `return` vs `print` | **predict/trace (class 3)** — on-paper reasoning about fixed code (which fn returns vs prints), no input to read | EXEMPT — `**No real version:**` note naming class 3 (content-gate round-2 resolution of [sol] §8 `[OPEN]`) |
| Q5 | Trace scopes, predict two output lines | **predict/trace** (class 3) | EXEMPT — `**No real version:**` note (class 3) |
| Q6 | Trace `if/elif/else` ladder, predict message | **predict/trace** (class 3) | EXEMPT — `**No real version:**` note (class 3) |
| Q7 | Turtle trace/predict ("do not run this code") | **predict/trace + reads-nothing** (class 3 + class 1) | EXEMPT — `**No real version:**` note (trace/predict of a turtle drawing) |
| Q8 | Build `score_round(3 bools)`, call + print | **read-and-compute** (functions arm) | REAL-FORM — read three yes/no answers via `== "yes"`, `score_round(...)` unchanged |

**3 real-forms (Q2, Q3, Q8); 5 exempt (Q1, Q4, Q5, Q6, Q7).**

### Real-form specifications (solutions markdown, mirrored heading)

- **Q2** — keep `count`/`total` accumulator structure; read the bound:
  ```python
  n = int(input("Add 1 up to which number? "))
  count = 1
  total = 0
  while count <= n:
      total = total + count
      count = count + 1
  print(total)
  ```
  §6d: the asserted twin (`total == 10`, `count == 5`) proves the completed blanks; the piped real-form proves
  termination + result line for a chosen `n` (e.g. `n=4` → `10`).
- **Q3** — `def greeting(name)` UNCHANGED; real-form reads the one distinct value:
  ```python
  def greeting(name):
      return f"Hello, {name}!"

  name = input("Your name? ")
  message = greeting(name)
  print(message)
  ```
  One string read (no `int()`). Bare `print(message)` (return-value function, not print-fn).
- **Q8** — `def score_round(...)` UNCHANGED; read all three distinct Boolean values via `== "yes"` (in-union
  comparison + string-literal + boolean):
  ```python
  def score_round(first_correct, second_correct, third_correct):
      score = 0
      if first_correct:
          score = score + 1
      if second_correct:
          score = score + 1
      if third_correct:
          score = score + 1
      return score

  first_correct = input("First correct? (yes/no) ") == "yes"
  second_correct = input("Second correct? (yes/no) ") == "yes"
  third_correct = input("Third correct? (yes/no) ") == "yes"
  round_score = score_round(first_correct, second_correct, third_correct)
  print(round_score)
  ```
  Three distinct reads (multi-value reads-every-value rule). Piped `yes/no/yes` → `2` (matches the twin).

## Data growth (§3) — N/A

cp02 is a loops-and-functions checkpoint with NO core data lists. Q1 `range(4)` and Q2 "1 through 4" are
structural constants of trace/completion questions, not toy SOURCE lists, and Q1 is an exempt trace. No list
to grow; §3 does not apply.

## Phases

### Phase A — apply to cp02 solutions.ipynb (markdown only; NO checkpoint.ipynb / metadata change)

For each of Q2/Q3/Q8: add a markdown cell immediately AFTER the executable solution cell, containing
`**The real program**` + a fenced ```python``` block per the spec above.
For each of Q2/Q3/Q8 real-forms: give the block a §6d/§6c-clean form — a `**The real program**` label; for Q2
a one-line §6d caption naming it as the completed program ([glm] g4, cp01 Q5 pattern); PRESERVE the executable
twin's blank lines verbatim inside the fenced block, incl. the two blank lines between `def…` and the driver
in Q3/Q8 ([glm] g5, §6c line-for-line).
For each of Q1/Q4/Q5/Q6/Q7: add the exemption note as the design-prescribed **`**No real version:**` prefix +
an italic cp01-style clause that NAMES the v6 class** ([sol] s4 + [glm] g3 + [fable] n1,n2 reconciled) —
e.g. `**No real version:** _A trace/predict question (class 3) — there is no `input()` version._` Q1/Q5/Q6
class 3 (predict/trace); Q4 static code interpretation (outside the both-forms rule — the graded act is a
concept explanation, no student-authored input program); Q7 trace/predict of a turtle drawing (class 3 +
class 1 reads-nothing).
`checkpoint.ipynb` and `manifest.yaml` are NOT touched (byte-unchanged).
**teacher-notes.md audit ([fable] n3 / [sol] s3): grep confirms ZERO `input` mentions → the audit is a
foreseeable no-op; teacher-notes.md is expected to stay byte-unchanged** (edit only if an actual stale
statement is found, which none is).

### Phase B — verification

- ci-local ALL GREEN (`TMPDIR=/dev/shm bash scripts/ci-local.sh`): registry+lint, notebook execution+hygiene
  (checkpoint_solutions heading mirror intact — new markdown headings must be FENCED, never a bare
  `## Question <digit>`), manifest/prereq/coverage, PDF build, pre-merge guard.
- Real-form validation: `ast.parse` each fenced block + piped-run, compare the **computed result line ONLY**
  to its executable twin MODULO prompt text ([glm] g2 — Q2's twin also prints an explanation line; compare the
  `10`, not full stdout). Pin every parity input incl. Q3's name ([glm] g1): Q2 `n=4`→`10`; Q3 `Maya`→
  `Hello, Maya!`; Q8 `yes/no/yes`→`2`.
- Confirm 0 `input()` in any `solutions.ipynb` **code** cell (real-forms are markdown).
- **Scope invariant ([sol] s2, plan 053 precedent):** assert an EMPTY diff for the student file and metadata —
  `git diff --quiet -- book1/checkpoints/checkpoint-02-loops-and-functions/checkpoint.ipynb` and the same for
  `manifest.yaml` (and `teacher-notes.md`) — CI alone does not prove byte-identity.

## Out of scope

- No new questions, no difficulty change, no checkpoint.ipynb edit, no metadata change. teacher-notes.md is
  audit-only ([sol] s3): grep shows zero `input` mentions, so no edit is expected; it stays byte-unchanged
  unless an actual stale statement is identified (none is). Only `solutions.ipynb` is modified.
- **Verification exemption:** this is a checkpoint-content plan; Phase B is the named verification phase
  (ci-local + real-form parity), no separate test suite.
- cp03/cp04 and projects are separate plans.

## Plan Review

### Round 1 (2026-09-20) — [self] inline; [sol] gpt-5.6-sol; [glm] volcengine-plan/glm-5.3; [fable] Fable 5.

#### [self] (2026-09-20)
**APPROVE.** Classifications hold: Q1/Q5/Q6/Q7 predict-trace, Q4 read-and-explain → exempt (class 3);
Q2/Q3/Q8 real-forms. Q2 is a valid §6d fragment (the real-form keeps the exact assessed blanks
`total = total + count` / `count = count + 1`, generalizing only the fixed bound `4`→`n`). Q3/Q8 follow the
functions arm (def unchanged; distinct reads — Q8 reads all three; bare `print` for return-value fns).
Metadata NONE correct (markdown-only real-forms invisible to concept-scan; cp01 precedent). §3 N/A (list-less
checkpoint). One self-watch folded into Phase A: exemption notes must append to the EXISTING solution area,
never introduce a bare `## Question <digit>` markdown heading (checkpoint_solutions mirror hazard). No
`.split()`; `input() == "yes"` is in-union (comparison + string-literal + boolean).

#### [fable] (2026-09-20)
**APPROVE WITH NITS.** All 8 classifications correct/none unclassified; Q4 is a genuine class-3 exemption
(graded act is reasoning about fixed code, nothing input-shaped — same as cp01 Q6). Pedagogy OK: cp02 sits
after u01–u05; `input(...) == "yes"` → Boolean is the core u04 quiz-show idiom (23 `== "yes"` in u04 exercises;
u04 solutions real-forms already bind it), so Q8 is taught/practised/precedented. All 3 real-forms use only
manifest-union ids; no `.split()`, no lists; metadata-NONE consistent with §5. Q2 preserves the assessed
blanks (twin `total==10`/`count==5`; real-form changes only `4`→`n`); §6d oracle applied correctly. Phase B is
a named verification phase; `## Out of scope` states the checkpoint exemption. No blockers.
Nits (wording/consistency, to fold in Phase A):
- (n1) name the **v6 class** in each exemption note (Q4 = predict/trace class 3, not "read-and-explain";
  Q7 = trace/predict of a turtle drawing, class 3 + class 1) — design §8 wants the note to name the class.
- (n2) pick the exemption-note STYLE: cp01's actual notes are italic sentences (accepted precedent), not the
  design's literal `**No real version:**` label — state which Phase A uses so the content gate can't split.
- (n3) teacher-notes.md has ZERO `input` mentions (grep) → the Phase-A audit is a foreseeable no-op; say so.

#### [sol] (2026-09-20)
**APPROVE WITH NITS.** No substantive curriculum/parity/metadata/CI blocker. SHAPE correct (Q1/Q5/Q6/Q7
predict-trace exempt; Q2 valid §6d fragment generalizing only `4`→`n`; Q3/Q8 real-forms; Q4 rightly no
real-form — graded work is static code interpretation, adding an input adapter would change the assessed task).
Prereq closure sound (all in-union; `input(...) == "yes"` appropriate + already used in u04; no `.split()`/list/
dict/method). Metadata correct (no input add — real-forms are fenced markdown). Multi-value satisfied (Q8 three
independent reads; Q2 reads only the input-shaped bound; `0`/`1` are structural initializers). Parity oracles
sufficient (Q2 `4`→`10`, twin asserts total==10/count==5; Q3 `Maya`→`Hello, Maya!`; Q8 `yes/no/yes`→`2`).
Heading-mirror hazard correctly guarded. Phase B adequate. Nits (folded below):
- (s1) Q4 taxonomy label imprecise — class 3 §1 literally describes predict/trace of fixed OUTPUT; name Q4
  "read-and-explain / static code interpretation" and clarify it falls outside the both-forms applicability rule
  (same substance as [fable] n1).
- (s2) Phase B should require an explicit EMPTY DIFF for `checkpoint.ipynb` AND `manifest.yaml` (plan 053
  precedent) — CI alone does not prove the byte-identical scope invariant.
- (s3) Out-of-scope teacher-notes allowance slightly conflicts with the solutions-only contract → make it
  audit-only unless a real stale statement is found ([fable] n3: grep shows none).
- (s4) Phase A should explicitly require the design-prescribed `**No real version:**` prefix on exemption
  notes (resolves [fable] n2's style question — adopt the design label + name the class).

#### [glm] (2026-09-20)
**APPROVE WITH NITS.** Verified against notebooks/manifest/design-v6/tools-source/cp01, and EMPIRICALLY ran
all 3 real-forms with piped input (Q2 `4`→`10`, n=10→55; Q3 `Maya`→`Hello, Maya!`; Q8 `yes/no/yes`→`2`,
no/no/no→0; all `ast.parse` clean). Classifications correct (Q4 exempt = concept explanation, cp01-Q6
precedent; Q2 valid §6d fragment even though it grades two lines — design "e.g." is illustrative; terminates
for all int n incl. n≤0). Prereq closure clean (verified concept-scan reads code cells only,
concept_scan.py:500; `input()=="yes"` in-union no methods). Metadata NONE correct (design §5; add is contingent
on a lesson input() code cell checkpoints can't have). CI hazard correctly guarded (verified
`_markdown_heading_occurrences` strips fences, notebooks.py:196; hazard is an UNFENCED bare `## Question
<digit>`, :670; ≥3-assert floor holds at 8). §3 N/A right; teacher-notes a verified no-op; §8 coverage complete
(Q2/Q3/Q8 the only non-exempt tasks). Non-blocking nits (folded into Phase A/B):
- (g1) pin Q3's parity name (`Maya`) in Phase B, like Q2/Q8.
- (g2) state Q2 parity targets the COMPUTED RESULT LINE only (twin stdout has 10 + an explanation print) so a
  naive full-stdout compare doesn't false-fail.
- (g3) exempt-note wording — cp01's ratified house style is an italic sentence ("… there is no `input()`
  version."). RESOLUTION (reconciles [sol] s4): use the design-prescribed **`**No real version:**` prefix +
  an italic cp01-style clause naming the class** — satisfies the design's literal label AND cp01 precedent.
- (g4) give Q2's real-form a §6d caption naming it as the completed program (cp01 Q5 pattern).
- (g5) §6c line-for-line: PRESERVE the twins' blank lines inside the fenced blocks (cp01's content gate fixed
  exactly this) — keep the two blank lines between `def` and the driver in Q3/Q8.

### Round 1 — outcome: **FULL 4-way plan-review consensus.** [self] APPROVE · [fable] APPROVE-WITH-NITS ·
[sol] APPROVE-WITH-NITS · [glm] APPROVE-WITH-NITS. No open blockers; all nits are plan-wording /
implementation-quality and folded into Phase A/B below. Gate CLOSED → proceed to implementation.

## Content Review

### Round 1 (2026-09-20) — on implementation commit 5591763. [self] inline; [sol]/[glm]/[fable] dispatched.

#### [self] (2026-09-20)
**APPROVE.** Verified on 5591763: 3 real-forms (cp2-q2/q3/q8-real) + 5 exemption notes (cp2-q1/q4/q5/q6/q7-
no-real) added to solutions.ipynb only. Parity modulo prompt PASS 3/3 (Q2 n=4→10; Q3 Maya→Hello, Maya!;
Q8 yes/no/yes→2; endswith-verified). Hygiene: 0 `input()` in any code cell; exactly 8 top-level `## Question N`
headings (mirror intact); 8 assert cells preserved (≥3 floor). Scope invariant: `git diff --quiet` clean for
checkpoint.ipynb, manifest.yaml, teacher-notes.md. Folded nits present: exemption notes use `**No real
version:**` + italic class-naming clause; Q2 has a §6d caption; §6c blank lines preserved (two blanks between
`def` and driver in Q3/Q8). No `.split()`; `input()=="yes"` in-union. ci-local ALL GREEN.

#### [fable] (2026-09-20)
**APPROVE WITH NITS — no `[OPEN]` blockers.** All 3 real-forms parse/run under piped input, line-for-line the
asserted twins with only fixed values→reads (§6c); all 5 exemptions correctly classified; student
checkpoint.ipynb/manifest.yaml/teacher-notes.md unchanged (§2/§5). Q8's `input(...) == "yes"`→Boolean is the
u04 quiz idiom (`correct = answer == 3` in u04 lesson), age-appropriate. Q2 keeps both blanks verbatim
(4→n); explanation print rightly dropped. Nits (none blocking):
- N1 `[WONTFIX-acceptable]` Q3 `name = input(...)` shadows the param `name`; on a checkpoint whose Q5 assesses
  global-vs-local scope, a distinct name (e.g. `player_name`) avoids a "which name?" question. → FOLD (cheap,
  pedagogically apt here).
- N2 `[WONTFIX-acceptable]` Q8 case-sensitivity (`"Yes"`→False); `.lower()` is u06 (out of union) so `== "yes"`
  is the correct in-union choice — add a one-clause "type exactly `yes`" caption. → FOLD (caption only).
- N3 `[WONTFIX]` Q4 note has no numbered class — deliberately settled as "read-and-explain / static code
  interpretation"; clear as written. → keep.
- N4 `[nit]` Q2 prompt `"Add 1 up to which number?"` slightly ambiguous → clearer wording. → FOLD.
- N5 `[nit]` Q3/Q8 bare `**The real program**` vs cp01's parenthetical caption → add short captions. → FOLD.
- N6 `[out of scope, pre-existing]` `ci-note` mentions `random.seed(4)` though cp02 uses no random. → keep
  (not this plan).

#### [glm] (2026-09-20)
**APPROVE — no `[OPEN]` findings.** Empirical: parity 3/3 (Q2 `4`→10, Q3 Maya→Hello, Maya!, Q8 yes/no/yes→2;
edges n=10→55/n≤0 terminates, no/no/no→0, yes/yes/yes→3; all `ast.parse` clean). §6c unified diffs show ONLY
fixed-value→read swaps, assessed blanks untouched, blank lines intact, Q2 §6d caption present. Prereq closure
clean (no `.split()`/list/dict; `input()=="yes"` verified as the u04 quiz idiom, 6+ occurrences). Multi-value
PASS (Q8 three distinct reads). All 5 exemption notes correct + class-naming. Hygiene: 0 input() in code cells,
exactly 8 `## Question N` headings (mirror intact), 8 assert cells (≥3). Scope: `git diff --quiet` clean for
checkpoint.ipynb/manifest.yaml/teacher-notes.md; commit is +107/−0 on solutions.ipynb only. Two `[WONTFIX]`
nice-to-haves (Q3/Q8 caption, Q4 class label) — both plan-conformant, no action. Consensus-ready.

#### [sol] (2026-09-20)
**REJECT — 1 `[OPEN]`.** All checks passed (blind-solves 3/3 match; parity; §6c line-for-line incl. blank
lines; closure; hygiene 0-input/8-headings/11-asserts; scope `git diff` clean) EXCEPT:
- `[OPEN]` Must: Q4's exemption note (`cp2-q4-no-real`) says "read-and-explain / static code interpretation" —
  neither a design-003 v6 class name nor number, but §8 requires the note to name a ratified §1 class. Resolve
  by mapping Q4 to a ratified class (class 3, predict/trace) OR amend the design to authorize the category.

### Content-review round 2 — fixes (fold [sol] `[OPEN]` + [fable] cheap nits) → re-verify.
- `[FIXED]` [sol] `[OPEN]`: reworded Q4's note to name **class 3 (predict/trace)** — Q4 is on-paper reasoning
  about fixed code without running it (which fn returns vs prints), the essence of class 3; satisfies §8, no
  design edit. (Supersedes [sol]'s plan-review s1 "static code interpretation" label, which §8 disallows as a
  note class; the description is kept, only the class is now named.) SHAPE table Q4 reconciled to class 3.
- `[FIXED]` [fable] N1: Q3 real-form global `name`→`player_name` (avoids shadowing the `name` param on a
  scope-assessing checkpoint).
- `[FIXED]` [fable] N2: Q8 caption adds "type exactly `yes`" (case-sensitivity, `.lower()` is u06/out-of-union).
- `[FIXED]` [fable] N4: Q2 prompt `"Add 1 up to which number?"`→`"Add up to which number?"` (clearer).
- `[FIXED]` [fable] N5: Q3/Q8 gain cp01-style parenthetical captions after `**The real program**`.
- `[WONTFIX]` [fable] N3 (Q4 numbered class) — resolved by the class-3 reword above.
- `[WONTFIX]` [fable] N6 / [glm] notes — pre-existing/plan-conformant, no action.

## Post-Execution Report
_(pending)_
