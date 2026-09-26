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
install Python on Windows (python.org, "Add python.exe to PATH", `py --version`) and on macOS (python.org
`.pkg`, "Install Certificates.command", `python3 --version`); install and start JupyterLab, open the course
folder, run a cell with Shift+Enter, restart the kernel, stop the server with Ctrl+C; install Thonny, save
and run `hello.py`; run a `.py` file from the terminal (the Unit 6 turtle workflow); troubleshooting
table; a final checklist. `unit-00-teacher-notes.md`: goals, a 60–90 minute setup-day plan, preparation
(admin rights, offline installers, lab pre-installs), common problems, devices that cannot install Python,
and a per-student sign-off checklist.

## Phase B — Tooling (Codex gpt-6-sol)

- `tools/publish.py`: after the front matter, emit the Unit 0 chapter from the docs file with the kind
  label "Unit 0" and title "Getting Set Up" (TOC, running heads and the PDF outline read "Unit 0 — Getting
  Set Up"); main matter (arabic page 1) starts at Unit 0 instead of Unit 1; in the Teacher's Edition the
  teacher notes follow the chapter opener in the usual Teacher panel. Markdown `text` blocks keep their
  styling as code panels; the `Notice:` rule applies.
- `allowed_source`: admit `unit-00-getting-set-up.md`; teacher notes stay teacher-only.
- `tools/publish_audit.py`: expect 20 chapters (Unit 0 + 13 units + 5 checkpoints + the Algorithm
  Challenge) in order, with Unit 0 first after the front matter; Unit 0 has no exercise/answer-key
  expectations.
- `book1b/front-matter/how-to-use.md` gains one sentence pointing to Unit 0 (inline edit).
- Tests: Unit 0 placement and label in both editions; teacher panel only in the teacher edition; the
  student allowlist refuses `unit-00-teacher-notes.md` (sentinel); main matter starts at Unit 0.

## Phase C — VERIFICATION

1. Publication tests pass; `publish-audit` PASS for both editions (20 chapters).
2. Rendered-page review of the Unit 0 pages in both editions (opener, install steps, text blocks,
   troubleshooting table, checklist, the teacher panel) recorded here.
3. A sentinel check: a string unique to `unit-00-teacher-notes.md` is absent from the Student PDF text
   and present in the Teacher PDF.
4. `scripts/ci-local.sh` ALL GREEN; post-execution report.

## Out of scope

A Unit 0 notebook or manifest (user decision); Chromebook/iPad set-up beyond a teacher note; Book 1 and
Book 2; screenshots.

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- Scope reduced per the user ("only make unit 0 a pdf chapter, no lesson notebook"): no curriculum
  artefacts change, so registry/prereq/coverage checks are untouched; the risk is concentrated in the
  accuracy of the install instructions and in the builder's chapter handling.
- Watch items: glyphs Atkinson Hyperlegible may lack (`▸`, task-list boxes) must hit the fallback font
  (the render-log audit catches misses); the Windows "Modify ▸ Add Python to environment variables"
  wording; macOS Gatekeeper wording for Thonny.

## Content Review
_(4-way content-review gate — including rendered pages.)_

## Post-Execution Report
_(filled before merge.)_
