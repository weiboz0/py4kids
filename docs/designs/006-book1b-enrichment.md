# Design 006 — Book 1b enrichment: gentler ladders, ASCII art, CP-ready input, filled facets

Status: proposed (2026-09-24).
Extends design 005 (Book 1b).
Governs a content-enrichment pass over all 13 Book 1b units plus one shared tooling change.

## 1. Purpose

Book 1b shipped complete (plans 070–078), but a whole-book audit (four parallel read-only
auditors, 2026-09-24) found four systematic weaknesses the user asked to fix:

1. **Steep ladders.** Lessons sometimes introduce two or more new ideas in one code cell
   (U02 precedence inside a "realistic" cell; U03 leap year in one rung; U05 first nested loop that
   is also the first string-building loop; U07 first `def` with parameter + return + float at once;
   U09 palindrome before any index loop; U10/U12 dense first cells).
2. **Low variety.** Exercise sets are thin (7 core + 2 stretch from U04 on) and most exercises
   re-skin a lesson cell with new numbers.
   ASCII art is nearly absent (one triangle in U05; `"*" * n` is catalogued under `string-concat`
   but never actually taught).
3. **No CP-ready input.** No Book 1b unit uses Book 1's real-input pattern, so students never
   write a program that reads stdin and prints an answer.
4. **Missing facets.** Several everyday facets of already-catalogued concepts are never taught
   (`print(a, b)`, `sep`/`end`, escapes, string repetition, `**`, precedence, `+=`, `round`,
   chained comparison, `range` step, `continue`, default parameters, composition, negative index,
   open slices and `[::-1]`, nested-list grids, file append mode, lists/dicts as attributes), and the
   most common CP input idiom — `input().split()` — is outside the scanner's allowed toolkit.

## 2. Decisions

- **D1 — Catalog unchanged.** The 62-concept catalog stays content-identical to Book 1
  (the `variant_of` invariant).
  "Missing concepts" are filled as **facets** of existing concepts, never as new catalog ids.
  Catalog *names* may be broadened (identically in both books) to describe the widened facets.
- **D2 — Widen the shared toolkit (user decision, 2026-09-24: "widen for both books").**
  The shared scanner pins in `tools/concept_scan.py` grow so both Book 1 and Book 1b may use:
  string methods `split`, `join`, `isdigit`, `isalpha`, `count`, `find`, `startswith`, `endswith`;
  list methods `pop`, `insert`, `remove`, `index`; and the `continue` statement.
  Each maps to an **existing** concept so prereq closure keeps catching premature use:
  string methods → `string-methods`; `pop`/`insert`/`remove` → `list-append`;
  `index` → `list-index`; `continue` → `break-statement`.
  Book 2 behavior is preserved: where `str-split` is registered, `split` still maps to `str-split`.
  Delivered first, as its own tooling plan (079).
- **D3 — Book 1's real-input pattern, everywhere it fits.**
  - Lessons: at least one `no-exec` code cell per lesson that runs the lesson's idea on real
    `input()` (CI forces interactive cells to `no-exec`, `notebooks.py:855-878`).
  - Exercises: every non-turtle exercise ends with a `**Real version:**` line naming what the real
    program reads.
  - Solutions: every non-turtle exercise gets a markdown `**The real program**` fenced block in
    **competitive-programming shape** — read input, compute (call the function from U07 on), print —
    beside the existing executable fixed-value stand-in with asserts (solution code cells may never
    call `input()`, `notebooks.py:283-287`).
  - Input idioms ramp with the toolkit: one value per line (U01–U03), read `n` then `n` lines
    (U04–U05), `input().split()` with `int()` conversion from the unit that teaches `split`
    (U09) onward, reading a grid of rows (U10), words/records (U11–U12), object construction from
    input (U13).
  - Turtle work (U06) is exempt (no stdin in turtle scripts).
- **D4 — ASCII art as a first-class exercise genre.**
  Taught formally at the first point the tools exist:
  U01 print-only banners/boxes/art (multi-line `print`, escapes);
  U02 `"=" * n` dividers and a `"#" * n` progress bar (string repetition taught as a U02 facet of
  `string-concat`);
  U03 decision-chosen art (traffic light, mood face, filled vs hollow line);
  U04 `while`-built bars and countdown art;
  **U05 the full pattern ladder** — rectangle → right triangle → inverted → right-aligned →
  hollow box → checkerboard → centered pyramid → diamond → tree with trunk → number/Floyd triangles —
  first with nested loops that build a row string, then with `"*" * n` and `" " * k` one-liners;
  U07 shape functions (`draw_triangle(n)` returning the art as a string, `banner(text)`);
  U08 dice faces and a two-dice histogram; U09 word frames and word triangles;
  U10 grids from nested lists and bar charts; U11 tally histograms; U12 saved text-art maps;
  U13 `Rectangle.draw()` / `Board.render()` returning multi-line strings.
  Art exercises are **assertable**: functions/cells build the picture as a string (rows joined with
  `"\n"`) and the solution asserts the exact string; printing is the last line.
- **D5 — Algorithm variants replace lesson copies.**
  Exercises that merely re-skin a lesson cell are rewritten or supplemented with a *transfer*
  variant (e.g. FizzBuzz variants, max-of-3, coin change, digit count/reverse/palindrome-number,
  sum of multiples of 3 or 5, primes up to n, perfect numbers, LCM via GCD, dice streaks,
  run-length encoding, second-largest, dedupe, rotate, two-pointer reverse, selection sort by hand,
  top-k, invert a dict, anagram by tally, BankAccount/Inventory classes).
- **D6 — Gentler ladders.**
  Every lesson jump the audit named gets the missing intermediate rung(s) inserted, so each code
  cell adds at most **one** new idea; dense multi-function cells are split.
  A rung may be a one-line demo; the ladder rule is about new ideas per cell, not cell length.
- **D7 — Volume.**
  Per the standing preference (memory: exercise-sets-favor-volume) and design 005's "no exercise
  cap", each unit gains new exercises until every concept it `introduces` appears in ≥5 exercises
  and every concept it `practices` in ≥3, with at least 3 ASCII-art/algorithm-variant exercises per
  unit (U01–U02 stay comparatively lean — the fragile-intro exception).
  Extra reps are labelled **More Practice**; at least one rep of each concept stays on the in-class
  path.
  This enrichment request is the user's explicit sign-off for growth beyond the plan-037 Phase-V
  volume thresholds; each plan still reports its cell/page deltas.
- **D8 — Same guardrails as the original build.**
  Self-containedness (taught-before-used in core; fastforward only as design-005 practices;
  checkpoints and the project stay strict), value-distinctness (every new fixture grepped against
  shipped content), function form from U07, `random.seed(4)` literal, one-concept-per-cell teaching,
  student notebooks solution-free with no outputs, statements and solutions authored in separate
  fresh sessions, 4-way plan and content gates.

## 3. Rollout

| plan | scope |
|---|---|
| 079 | Tooling: widen the shared scanner pins (D2) + tests + catalog-name broadening in both books. |
| 080 | U01–U03 enrichment. |
| 081 | U04–U06 enrichment. |
| 082 | U07–U09 enrichment (teaches the widened string methods, incl. `split`). |
| 083 | U10–U11 enrichment (teaches `pop`/`insert`/`remove`/`index`, nested-list grids). |
| 084 | U12–U13 enrichment + checkpoint "Real version" notes + syllabus/teacher-notes refresh. |

Each content plan names, per unit: the rungs to insert (by cell id, from the audit), the facets to
teach, the new exercises (with values plan), and the input-pattern additions.
Each ships with a named verification phase (`scripts/ci-local.sh` + a static AST/grep audit + the
per-concept depth count from D7).

## 4. Non-goals

- No new catalog concepts; no Book 1 *content* changes (Book 1 only receives the widened toolkit).
- No `enumerate`/`zip`/tuple unpacking (tuple unpacking is a Book 2 feature; `for k, v in d.items()`
  keeps its existing U11 carve-out).
- No `__str__`/inheritance/decorators; no `+=`-style policy change beyond teaching `+=` as a U04 facet
  of `accumulator`.
