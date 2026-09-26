# Plan 087 — Book 1b Unit 0: Getting Set Up (a book chapter)

**Goal:** Add "Unit 0 — Getting Set Up" to both Book 1b editions: how to install Python and the two
course editors (JupyterLab and Thonny) on macOS and Windows, run a first program three ways, and fix the
common setup problems.

**Spec:** user requests (2026-09-26): "add unit 0 to introduce installation of python and python editors
in mac and windows"; decisions — editors **JupyterLab + Thonny**; install Python from the **python.org
installer** on both systems; **Unit 0 is a PDF chapter only — no lesson notebook**. Design 007 (book
publication) governs how chapters are built.

## Global constraints

- Unit 0 is **not** a curriculum unit: no `units/unit-00-*` folder, no notebook, no `manifest.yaml`, no
  concept-catalog, coverage-map or syllabus-table change (the registry, prereq and coverage checks are
  untouched). It is a Markdown learner doc that the book builder places as the first main-matter chapter.
- Sources: `book1b/docs/unit-00-getting-set-up.md` (student-facing; also usable on its own as the setup
  guide promised by `book1b/docs/README.md`) and `book1b/docs/unit-00-teacher-notes.md` (Teacher's
  Edition only).
- The Student Book's source allowlist admits the student file and still refuses every teacher-notes file.
- Instructions name no exact Python patch version: "Python 3.12 or newer" (the course's floor,
  `pyproject.toml`), current installer wording as of 2026, no screenshots (text steps with the exact
  button/checkbox names).
- Commands are shown per system in text blocks: Windows uses the `py` launcher, macOS uses `python3`;
  JupyterLab is installed and started with `-m` (`py -m pip install jupyterlab`, `py -m jupyterlab`) so the
  same Python is always used.

## Phase A — Content (inline; learner/teacher prose)

`unit-00-getting-set-up.md`: hook (run your first program three ways); what you will install and why;
install Python on Windows (python.org's **Python install manager** → **Install**, then
`py install default` (the optional PATH prompt only adds versioned aliases), then `py --version` — the classic
installer is deprecated from 3.14) and on macOS (python.org `.pkg`, "Install Certificates.command" in
`/Applications/Python 3.x/`, `python3 --version`); install and start JupyterLab, open the course
folder, run a cell with Shift+Enter, restart the kernel, stop the server with Ctrl+C; install Thonny, save
and run `hello.py`; run a `.py` file from the terminal (the Unit 6 turtle workflow); troubleshooting
table; a final checklist. `unit-00-teacher-notes.md`: goals, a 60–90 minute setup-day plan, preparation
(admin rights, offline installers, lab pre-installs), common problems, devices that cannot install Python,
and a per-student sign-off checklist.

## Phase B — Tooling (Codex gpt-6-sol)

- `tools/publish.py`: `entries()` keeps reading the syllabus table (unchanged). The builder emits the
  Unit 0 chapter **separately, before the syllabus loop**, as a chapter of its own kind `setup` (never
  `unit`, so no lesson/exercise/answer-key logic applies) with id `unit-00-getting-set-up`, kind label
  "Unit 0" and title "Getting Set Up" (TOC, running heads and the PDF outline read "Unit 0 — Getting Set
  Up"). The `pub-mainmatter` marker moves from the `unit-01-` chapter to Unit 0, so arabic page 1 is Unit 0.
  The setup chapter keeps its `##` headings as level-2 sections (the ordinary `markdown_blocks()`
  demotion of `##` to `###` does not apply), so each appears in the TOC and the PDF outline in both
  editions; its `###` headings stay level 3.
  The chapter body is the docs file through the normal Markdown handling (H1 → chapter title, the hook
  paragraphs → opener, the `Notice:` rule, `text` blocks as code panels, tables, the `- [ ]` checklist).
  In the Teacher's Edition, `unit-00-teacher-notes.md` follows the opener in the usual Teacher panel.
- `allowed_source`: explicitly admit `unit-00-getting-set-up.md` for the student edition and explicitly
  deny any file whose name contains `teacher-notes` (not only by falling through).
- `tools/publish_audit.py`: the expected chapter order is `unit-00-getting-set-up` followed by the
  syllabus entries (20 chapters); the audit skips notebook, exercise, Notice-count, inventory and
  answer-key checks for the `setup` chapter; the PDF outline check is extended to it (the outline must
contain "Unit 0 — Getting Set Up" and its `##` section headings) and the artefact check applies.
- Glyphs: `▸` and the checklist box must render through the fallback font — the render-log audit fails on
  any `Missing character`.
- `book1b/front-matter/how-to-use.md` gains one sentence pointing to Unit 0 (inline edit).
- Tests: Unit 0 placement, kind and label in both editions; the setup outline check (every `##`
  heading of the docs file is a level-2 bookmark under "Unit 0 — Getting Set Up" in both PDFs); main matter starts at Unit 0; the teacher
  panel only in the teacher edition; the student allowlist admits the chapter and refuses
  `unit-00-teacher-notes.md` (sentinel string absent from the student project and PDF text); the audit's
  20-chapter order.

## Phase C — VERIFICATION

1. Publication tests pass; `publish-audit` PASS for both editions (20 chapters).
2. Rendered-page review of the Unit 0 pages in both editions (opener, install steps, text blocks,
   troubleshooting table, checklist, the teacher panel) recorded here.
3. A sentinel check: a string unique to `unit-00-teacher-notes.md` is absent from the Student PDF text
   and present in the Teacher PDF.
4. `scripts/ci-local.sh` ALL GREEN; post-execution report.

## Out of scope

A Unit 0 notebook or manifest (user decision); Chromebook/iPad set-up beyond a teacher note; Book 1 and
Book 2; screenshots. Unit 6's lesson still tells students to run `python assets/l1_square.py` in
JupyterLab's terminal; Unit 0 now teaches `py` / `python3` and mentions the JupyterLab terminal — aligning
Unit 6's wording is a follow-up (errata), not part of this plan.

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- Scope reduced per the user ("only make unit 0 a pdf chapter, no lesson notebook"): no curriculum
  artefacts change, so registry/prereq/coverage checks are untouched; the risk is concentrated in the
  accuracy of the install instructions and in the builder's chapter handling.
- Watch items: glyphs Atkinson Hyperlegible may lack (`▸`, task-list boxes) must hit the fallback font
  (the render-log audit catches misses); the Windows "Modify ▸ Add Python to environment variables"
  wording; macOS Gatekeeper wording for Thonny.

### Round 1 — verdicts

- `[fable]` APPROVE WITH NITS — accuracy: the Modify path does not restore `py`; OneDrive-redirected
  Documents breaks `cd`; pip warnings; Disable path length limit; SmartScreen; double Ctrl+C; Thonny's
  bundled Python below 3.12; Unit 6 uses JupyterLab's terminal; pedagogy: saving, where the course folder
  comes from; teacher notes: offline wheels, proxies; tooling specifics (separate kind, audit order,
  main-matter marker, explicit teacher-notes deny).
- `[sol]` **REJECT** — the Windows flow must follow the current **Python install manager** (the classic
  "Add python.exe to PATH" installer is deprecated from 3.14); the plan must specify how a chapter
  outside the syllabus is emitted and audited; Thonny's per-architecture downloads; the Mac certificate
  script location.
- `[glm]` first attempt timed out; retried.

### Round 1 — fold

- `[FIXED]` Windows steps rewritten for the install manager (Install → `py install default` → `y` to the
  PATH prompt → `py --version`), with matching troubleshooting and teacher notes (verified against the
  current docs.python.org Windows guide).
- `[FIXED]` all of [fable]'s content points (commit 0c13721) and [sol]'s Thonny download choice and Mac
  certificate location.
- `[FIXED]` Phase B now specifies the separate `setup` chapter, main-matter move, explicit deny, audit
  order and skipped checks, glyph fallback, and tests; the Unit 6 wording mismatch is recorded as a
  follow-up.

### Round 2 — [sol] REJECT (folded)

- `[FIXED]` one program in all three runs (`print("Hello, Python!")`); the Windows PATH prompt is described
  as optional (it adds versioned aliases; `py` works either way) in the chapter, teacher notes and plan;
  "Requirement already satisfied" accepted as a successful pip result; the audit's PDF outline check is
  specified and tested for the `setup` chapter.

### Round 3 — [sol] REJECT (folded)

- `[FIXED]` the terminal run no longer repeats `cd` in the terminal that is already in the course folder
  (the `cd` step is given only for a new terminal); the plan states that the setup chapter keeps `##`
  headings as level-2 sections and the audit checks them as bookmarks in both editions.

## Content Review
_(4-way content-review gate — including rendered pages.)_

## Post-Execution Report
_(filled before merge.)_
