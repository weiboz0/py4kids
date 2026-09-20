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
| Q1 | Trace a `for range(4)` loop, predict output | **predict/trace** (class 3) | EXEMPT — solutions note |
| Q2 | Complete two `while`-accumulator blanks (sum 1→4) | fragment-completion → **read-and-compute** | REAL-FORM — read the upper bound `n`, sum `1..n` with the completed `while` (§6d oracle) |
| Q3 | Write `greeting(name)`, call + store + print | **read-and-compute** (functions arm) | REAL-FORM — read one name (string `input()`), `greeting(name)` unchanged |
| Q4 | Read two fns, explain `return` vs `print` | **read-and-explain** (class 3 predict/trace) | EXEMPT — solutions note |
| Q5 | Trace scopes, predict two output lines | **predict/trace** (class 3) | EXEMPT — solutions note |
| Q6 | Trace `if/elif/else` ladder, predict message | **predict/trace** (class 3) | EXEMPT — solutions note |
| Q7 | Turtle trace/predict ("do not run this code") | **predict/trace + reads-nothing** (class 3/1) | EXEMPT — solutions note |
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
For each of Q1/Q4/Q5/Q6/Q7: add a one-line exemption note in the solutions markdown (why no real-form:
predict/trace / read-and-explain / reads-nothing).
`checkpoint.ipynb` and `manifest.yaml` are NOT touched (byte-unchanged).

### Phase B — verification

- ci-local ALL GREEN (`TMPDIR=/dev/shm bash scripts/ci-local.sh`): registry+lint, notebook execution+hygiene
  (checkpoint_solutions heading mirror intact — new markdown headings must be FENCED, never a bare
  `## Question <digit>`), manifest/prereq/coverage, PDF build, pre-merge guard.
- Real-form validation: `ast.parse` each fenced block + piped-run, compare the result line to its executable
  twin MODULO prompt text (Q2 `n=4`→`10`; Q3 name→`Hello, <name>!`; Q8 `yes/no/yes`→`2`).
- Confirm 0 `input()` in any `solutions.ipynb` **code** cell (real-forms are markdown).

## Out of scope

- No new questions, no difficulty change, no checkpoint.ipynb edit, no metadata/teacher-notes change beyond
  what the norm requires (teacher-notes only if it makes a now-stale claim about input — audit in Phase A).
- **Verification exemption:** this is a checkpoint-content plan; Phase B is the named verification phase
  (ci-local + real-form parity), no separate test suite.
- cp03/cp04 and projects are separate plans.

## Plan Review
_(pending)_

## Content Review
_(pending)_

## Post-Execution Report
_(pending)_
