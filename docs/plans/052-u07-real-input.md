# Plan 052 — u07 high-score-hall: full real-input treatment (rollout slice 1, list arm)

**Status:** DRAFT — plan-review gate pending.
**Type:** Content — apply the full u04 end-state treatment to `unit-07-high-score-hall`.
**Branch:** `feature/plan-052-u07-real-input`. **Base:** main @ 741bde7.

## Motivation

Roll out the treatment u04 now carries (plans 050 + 051) to the rest of Book 1, author-directed, in the
design-003 §7 order. **u07 is slice 1** — the first LIST unit — chosen to exercise the untested list arm
(realistic fixed lists + the "read into a list" real-form idiom + list-vs-count naming). Authorities:
`docs/designs/003-book1-real-input.md` (real-input norm) and plan 051 (CP-light naming + numbered prompts).

## The treatment (the full u04 package, per unit)

1. **Real-input hybrid forms** (design 003): every complete lesson task (put-it-together / Algorithm-Extension
   home) and every exercise keeps its EXECUTABLE fixed-data form AND gains one `input()`-reading "real program"
   form — a `no-exec` `input()` CODE cell (+ `**Notice:**`) in `lesson.ipynb`; a MARKDOWN fenced ```python
   block``` in `solutions.ipynb` (input() banned in solutions code cells). u07 already has `input` in its
   concept union → **no metadata change**.
2. **Realistic data** (design 003 §3, list arm): culminating put-it-together + exercise fixed lists use
   realistic 6–8-element lists (real score/name variety, ties where apt). Build-up rungs stay minimal
   (protects the graduated-ladder pedagogy). Toy lists to grow: `names = ["Ada","Bo","Cy"]`,
   `scores = [3,9,5,7]`, and the 2–4-element demo lists in culminating cells.
3. **CP-light names** (plan 051 "Light trim"): drop verbose suffixes, single-letter loop counters. **List-unit
   naming rule:** the plural noun names the LIST (`scores`, `names`, `board`, `kept`), the item count is `n`,
   the loop index is `i` — this is the natural, non-confusing mapping (a plural bound to a scalar is what we
   avoid). Concretely for u07: `best_so_far`→`best`; explicit list-index loop counters → `i`; keep already-short
   domain names (`scores`, `names`, `board`, `kept`, `place`, `score`, function/param names). Default: any name
   not obviously verbose is kept verbatim.
4. **Numbered per-iteration prompts** (plan 051): `f"Score {i + 1}: "` / `f"Name {i + 1}: "` etc., 1-based,
   never index 0. Arithmetic-in-f-string is in-union (u07 requires/practices f-string + arithmetic).

## u07 real-form idiom (read into a list)

u07's union includes `for`, `range`, `input`, `int`, `list-append`, `sentinel-loop`. The real program reads the
values the fixed list stands in for, into a list, then runs the SAME (unchanged) list-processing body:

```python
n = int(input("How many scores? "))
scores = []
for i in range(n):
    scores.append(int(input(f"Score {i + 1}: ")))
# ...unchanged list logic below...
```

(String lists read with `names.append(input(f"Name {i + 1}: "))`.) The `for i in range(n)` + `.append` prologue
is entirely in u07's union. The executable twin keeps the realistic FIXED list; the real-form replaces the
literal list with the read-into-list prologue and is otherwise line-for-line identical (design 003 §6).

## Per-notebook-kind forms (CI-forced, unchanged from design 003 §2)

- **lesson.ipynb:** real-form = `no-exec` `input()` CODE cell + `**Notice:**` (concept-scan sees input() — u07
  already has it, no add). Executable fixed-data ladder unchanged.
- **solutions.ipynb:** real-form = markdown fenced ```python``` block after the executable asserted cell; the
  asserted fixed-data reference solution (≥3 non-vacuous assert cells/nb) stays the validated logic. A fenced
  block must not contain a line starting `## Exercise <digit>`.

## Closure (self-containedness — unchanged)

Names + prompts + realistic-data + read-into-list prologue ONLY. No concept outside u07's union
(introduces list-literal/index/append/loop/sort, builtin-functions, find-extreme, filter-into-list; requires
for-loop, def, comparison, parameters, return; practices input, range, while, sentinel-loop, f-string,
arithmetic, int, in-operator, string-methods, accumulator, running-total, count-by-condition, transform-each,
break, linear-search, …). No `sys.stdin`. Build-up rungs untouched.

## Phases

### Phase A — apply to u07 (lesson + exercises + solutions + teacher-notes)
Real-input forms on every put-it-together + Algorithm-Extension home (lesson) and every exercise (solutions
markdown); realistic 6–8-element lists on culminating cells; light-trim names + numbered prompts; teacher-notes
swept for any renamed variable. Markers/§3 marker adjacency untouched; build-up rungs untouched.

### Phase B — verification
- `ast.parse` + piped-run every real-form + executable twin; each real-form's RESULT line equals its
  fixed-data twin's output **modulo `input()` prompt text**; numbered prompts display 1..n never 0.
- AST-level closure scan: no concept outside u07's union introduced (no `sys.stdin`; no new builtin/idiom).
- Assert NO old name (from the light-trim map) survives anywhere under the unit dir (AST for bare names).
- `scripts/ci-local.sh` ALL GREEN (exec-lessons runs ladders/twins; exec-solutions runs asserted cells;
  concept-scan/prereq/coverage/pattern-marker/technique-spiral stay clean).

## Out of scope
- Any Book-1 entry other than u07 (rollout continues: checkpoint mini-pilot next, then remaining units +
  projects — design 003 §7 order). Design 003 (no amendment). Verification phase present (Phase B).

## Plan Review
_(pending — 4-way.)_

## Content Review
_(pending — 4-way.)_

## Post-Execution Report
_(pending.)_
