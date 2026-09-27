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

### Round 4 — [sol] REJECT (folded)

- `[FIXED]` Windows fallback for an older launcher owning `py`: `pymanager install default`, and ask the
  teacher if `py --version` still picks a version below 3.12 (chapter, troubleshooting table, teacher
  notes); macOS `.pkg` steps name **Agree**; the JupyterLab browser fallback copies the full
  `http://localhost:…` URL (port may differ).

### Round 5 — [sol] APPROVE WITH NITS (folded)

- `[FIXED]` teacher notes name the official remedy (uninstall the legacy **Python launcher**); the chapter
  gives the course's GitHub address for independent learners.

### CONSENSUS

- `[glm]` APPROVE — run on `opencode-go/glm-5.3` (user decision, 2026-09-26: the `volcengine-plan`
  provider was unreachable; two earlier attempts timed out and a one-word probe hung). Verified the tooling
  and verification phases and the install steps; optional nits (Windows button label, ageing sample
  version) left as is — the text already says exact numbers do not matter.
- `[sol]` APPROVE WITH NITS (r5, nits folded) · `[fable]` APPROVE WITH NITS (r1, folded) · `[self]`
  APPROVE WITH NITS.

**Consensus reached — implementation starts.**

## Content Review

### Round 1 — verdicts (HEAD c647a38; rendered snapshots)

- `[self]` APPROVE WITH NITS — rendered-page review: the troubleshooting table wrapped badly on a 7-inch
  page and the checklist showed a bullet plus a box; both rewritten (list of symptom/fix items, plain box
  lines).
- `[fable]` APPROVE WITH NITS — accuracy re-verified against docs.python.org and thonny.org; `[OPEN]` two
  Notice panels absorbed the following paragraph; nits: a stretched troubleshooting headline, the
  Windows download wording, Thonny 4.x/5.0 Python versions, a running head, table header styling.
- `[sol]` APPROVE — no open findings; text, sections, commands, checklist, teacher-panel placement,
  main-matter start, 20-chapter outlines and the Student/Teacher boundary verified.
- `[glm]` **skipped** — user decision 2026-09-26: "skip glm reviewer for 1 day, then use
  volcengine-plan/glm-5.3" (both `volcengine-plan/glm-5.3` and `opencode-go/glm-5.3` hung on a one-word
  probe; the content review timed out after 20 minutes).

### Round 1 — fold

- `[FIXED]` every Notice now ends its section (the Windows `py` Notice follows the `pymanager` paragraph;
  the Mac `cd` shortcut precedes the JupyterLab-terminal Notice); the OneDrive troubleshooting headline is
  shortened; Windows step 1 says "choose **Python install manager**".
- `[WONTFIX]` Thonny version detail (the teacher-note wording is already hedged), the teacher-edition
  running head on page 3, and table header styling (global style, not a regression).

**Consensus reached** ([self]/[sol]/[fable]; [glm] skipped by user decision).

## Post-Execution Report

**Status: implemented; audits clean; `scripts/ci-local.sh` ALL GREEN (2026-09-26, 1777 s).**

- **Phase A (inline):** `book1b/docs/unit-00-getting-set-up.md` (student chapter) and
  `book1b/docs/unit-00-teacher-notes.md` (Teacher's Edition only). Windows follows python.org's Python
  install manager (`py install default`, `pymanager` fallback, optional PATH prompt); macOS the `.pkg`
  (Agree, Install Certificates); JupyterLab via `-m pip` / `-m jupyterlab`; Thonny per chip; one
  `Hello, Python!` program run three ways; troubleshooting list and checklist. Accuracy checked by
  `[sol]` and `[fable]` against the current Python, JupyterLab and Thonny documentation.
- **Phase B (Codex gpt-6-sol):** a separate `setup` chapter emitted before the syllabus chapters (main
  matter starts at Unit 0), `##` headings kept as level-2 sections, the teacher panel only in the
  Teacher's Edition, an explicit `teacher-notes` deny in the source allowlist, a 20-chapter audit with the
  outline check extended to Unit 0, and tests including the sentinel boundary test (33 publication tests).
- **Result:** Student Book 460 pages (Unit 0 = pages 1–6), Teacher's Edition 872 pages (Unit 0 = pages
  1–8); `publish-audit` PASS (20 chapters, 0 overfull boxes, no missing glyphs).
- **Follow-up:** Unit 6's lesson still says `python assets/l1_square.py` in JupyterLab's terminal; Unit 0
  teaches `py` / `python3` — align in an errata pass.
