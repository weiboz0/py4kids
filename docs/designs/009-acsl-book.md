# Design 009 — The ACSL book: organized by the contest season

**Status:** accepted (user decisions, 2026-09-28/29).
**Refines:** design 008 D3–D4 (the contest split). Design 008's naming, the `peers` sharing rule and the independent-completeness rule stand; its "move four units" roadmap is replaced by §3 here.

## 1. Purpose

*Contest Python: ACSL* (`acsl/`) prepares students for the American Computer Science League, across every division.
Students should be able to follow the book **in step with a competition season**, studying each contest's categories in the weeks before that contest.

## 2. Decisions

- **D1 — One book, organized by contest** (user: "cover all levels in one book, but mark concepts by level"; "organize them by acsl units, so that students can follow the contest schedule in a competition season").
  - The book opens with an **ACSL Foundations** unit. It covers what every later unit and every programming problem needs: how the contest works; reading contest input (`input()`, lines, `split`, conversions); tuples; and simple complete search.
  - Then come **four contest parts**, in season order. Each part has one unit per ACSL category of that contest, and ends with a **Contest N practice** checkpoint (short-answer plus programming, per the ACSL format).
  - Category order within a part follows the official list.
- **D2 — The season map is data.** `acsl/curriculum/season.yaml` records, per contest (1–4) and per division (elementary, classroom, junior, intermediate, senior), the official category names. The source is the acsl.org Study Materials page, and the file records its retrieval date. As of 2026-09-29:

  | Contest | Junior | Intermediate & Senior | Elementary | Classroom |
  |---|---|---|---|---|
  | 1 | Computer Number Systems; Recursive Functions; What Does This Program Do? – Branching | Computer Number Systems; Recursive Functions; What Does This Program Do? | Elementary Computer Number Systems | Number Systems; Recursive Functions; WDTPD |
  | 2 | Prefix/Infix/Postfix Notation; Bit-String Flicking; WDTPD – Looping | Prefix/Infix/Postfix Notation; Bit-String Flicking; LISP | Elementary Prefix/Infix/Postfix | Prefix/Infix/Postfix; Bit-String Flicking; LISP |
  | 3 | Boolean Algebra; Data Structures; WDTPD – Arrays | Boolean Algebra; Data Structures; FSAs and Regular Expressions | Elementary Boolean Algebra | Boolean Algebra; FSAs and Regular Expressions; Data Structures |
  | 4 | Graph Theory; Digital Electronics; WDTPD – Strings | Graph Theory; Digital Electronics; Assembly Language | Elementary Graph Theory | Graph Theory; Digital Electronics; Assembly Language |

  - Junior, Intermediate and Senior contests each include a programming problem; Elementary and Classroom do not.
  - `season.yaml` also holds one merged **`unit_order`** per contest: the Junior categories in the official order, then the Intermediate/Senior-only categories (LISP, FSAs, Assembly). The book's unit order follows it; `acsl-check` needs it to be deterministic.
  - When ACSL changes the list, only `season.yaml` and the affected units change.
- **D3 — Every item is marked by division** ("mark concepts by level").
  - **Levels form a ladder:** elementary < junior < intermediate < senior.
    - Each ACSL **unit** manifest carries `acsl: {contest: 0–4, category: <season.yaml unit_order name>, divisions: [...]}`, where contest 0 is Foundations and `divisions` lists ladder levels only.
    - Each **practice checkpoint** manifest carries `acsl: {contest: 1–4, category: Practice, divisions: [...]}`. `Practice` is reserved, is not a `unit_order` entry, and is valid only on checkpoints: exactly one per shipped contest, placed after that contest's last unit. Its questions may span any of that contest's categories.
    - Each exercise carries its **lowest** ladder level as a tag on its heading cell, `acsl-elementary|acsl-junior|acsl-intermediate|acsl-senior`, which later prints as a level badge. A student following one ladder level does the items at or below it.
  - **Classroom** is a season-map column only: never a tag and never in `divisions`. The Classroom path for a contest is every **short-answer** item tagged junior or intermediate in that contest's categories, matching ACSL's Classroom test, which draws on those divisions' non-programming problems.
  - **Elementary** is a one-category, non-programming test per contest. Each Elementary category (Computer Number Systems, Prefix/Infix/Postfix, Boolean Algebra, Graph Theory) is taught as the **opening Elementary section** of the matching Junior category unit, with items tagged `acsl-elementary`.
  - **Division paths:** the Elementary path skips Foundations (no programming) and starts at Contest 1's Number Systems unit. The syllabus "Division paths" section spells out every path.
  - **WDTPD across divisions:** Intermediate and Senior Contest 1 test *all* constructs, while Junior's WDTPD moves Branching → Looping → Arrays → Strings over Contests 1–4. So the Contest 1 WDTPD unit covers Branching for Junior, plus an Intermediate-tagged section tracing loops, arrays and strings. Contests 2–4 add the Junior-flavoured drills.
  - An `acsl-check` enforces all of this:
    - contest and category exist in `season.yaml`
    - unit order follows the season
    - every exercise has exactly one division tag, and it is not below its unit's lowest division
    - every contest part has its practice checkpoint (once that contest ships)
- **D4 — ACSL items.** Each exercise and checkpoint question is exactly one of two kinds, classified per item:
  - **Short-answer**, the ACSL non-programming questions (e.g. "convert 3F₁₆ to base 8"). The heading cell carries a `short-answer` tag.
    - The statement asks for one exact answer.
    - The solution has a **worked answer** in markdown (student-readable) that ends with exactly one machine-readable line, `**Answer:** `<answer text>``.
    - A code cell tagged **`verify`** computes the answer and asserts it, as `assert str(<computed>) == "<answer text>"`, where the literal equals the markdown answer text exactly.
    - The check compares the two statically and then executes the cell, so neither the printed answer nor the computation can drift alone.
    - `verify` cells are verification-only: executed by `exec-solutions`, exempt from `source-policy` and `concept-scan` (so simulators for LISP, assembly or FSAs may use any Python), never printed to students.
    - A `verify` cell that needs a program's output runs it with `subprocess.run([sys.executable, "assets/<file>.py"], input=..., capture_output=True, text=True)` from the entry folder, so all short-answer solutions look alike.
  - **Programming**, the ACSL programming problem: a stdin `.py` solver under the `judge` contract, as in USACO Bronze.
- **D5 — Independence and sharing** (design 008): `acsl` depends on the Python books only, and is a `peers` of `usaco-bronze`.
  - It may introduce the same concept ids (e.g. `input-parse`, `str-split`, `tuple`, `complete-search`, `code-tracing`, `base-conversion`, `bitwise-ops`, `boolean-algebra`, `tree-traversal`), with identical registry entries.
  - It teaches each in its own words and problems. Content is written for ACSL; USACO notebooks are not copied.

## 3. Roadmap (replaces design 008 D4 steps 2–3)

| Plan | Scope |
|---|---|
| 092 | This design. Tooling: the `peers` exemption; `acsl` manifest fields and `acsl-check`; short-answer item support in the checks; register `acsl` with `season.yaml`, a syllabus showing the whole season map (future units marked *planned*), and the curriculum registry. The **ACSL Foundations** unit. |
| 093 | Contest 1: Computer Number Systems; Recursive Functions; What Does This Program Do? (Branching); Contest 1 practice. |
| 094 | Contest 2: Prefix/Infix/Postfix; Bit-String Flicking; WDTPD (Looping); LISP (Intermediate+); practice. |
| 095 | Contest 3: Boolean Algebra; Data Structures; WDTPD (Arrays); FSAs & Regular Expressions (Intermediate+); practice. |
| 096 | Contest 4: Graph Theory; Digital Electronics; WDTPD (Strings); Assembly Language (Intermediate+); practice. |
| 097 | **USACO trim.** Remove the ACSL-only topics from `usaco-bronze`: Unit 02 (Boolean logic and code tracing); the base-conversion/bitwise parts of Unit 11 (gcd, sieve and modular arithmetic stay, as a Number Theory unit); and the postfix half of Unit 10 (stacks, queues and `deque` stay). Unit 12 (binary trees) is removed or kept as Bronze-relevant after review. Units are renumbered. Mock-contest questions on moved topics are **replaced** with USACO-topic questions (user: "Replace and move"). The originals **move** into ACSL as practice: an ACSL practice checkpoint already holds 6–8 questions with exactly one programming problem (the ACSL format), so a moved programming question either replaces that checkpoint's programming problem or becomes an extra exercise in the matching category unit. |

- Unit 10 (stacks, queues, deques) stays in USACO: BFS in the graphs unit needs `deque`. ACSL teaches its own Data Structures in Contest 3.
- Until plan 097, the shared topics exist in both books, as the `peers` rule allows.

## 4. Non-goals

- ACSL finals and all-star content.
- A publication pipeline for `acsl` (it can gain `publication: true` later).
- Separate books per division.
