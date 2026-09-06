# Plan 001 — Scaffolding & Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the py4kids repo skeleton, governance docs, uv environment, and the two gate scripts (`ci-local.sh`, `pre-merge-guard.sh`) so every later plan runs the full usaaio-style lifecycle.

**Architecture:** Mirror usaaio's shape — `books.yaml` registry, two book roots, `docs/` lifecycle tree, `tools/` Python package, `scripts/` bash gates — but written fresh and minimal for py4kids (no usaaio-specific machinery). Content checks that plan 003 will build print `SKIP (plan 003)`.

**Tech Stack:** Python ≥3.12, uv, hatchling, pytest, ruff, PyYAML, bash.

**Spec:** `docs/designs/000-project-design.md`

## Global Constraints

- The repo is PUBLIC: never commit `.gh-token`, secrets, or student data (design §3).
- Docs use semantic line breaks — one sentence per line (design §3).
- Every `gh` command uses `GH_TOKEN=$(cat .gh-token)`; remote is `git@github-weiboz0:weiboz0/py4kids.git` (design §7).
- Unit/project/checkpoint directory names: `unit-NN-slug`, `project-NN-slug`, `checkpoint-NN-slug` (two-digit NN).
- Commit messages end with the Co-Authored-By / Claude-Session trailer used by this session.

## Out of scope

This is a tooling/docs-only plan: it ships no units, projects, or checkpoints, so the design's "named verification phase" rule for content plans does not apply (exemption per design §5). Verification here is: pytest green, both gate scripts run green, `uv run python -c "import tools"` works. Also out of scope: any curriculum content (plan 002), real content checks (plan 003), PDF build tooling (plan 003).

---

### Task 1: uv environment + tools package stub

**Files:**
- Create: `pyproject.toml`
- Create: `tools/__init__.py` (empty)

**Interfaces:**
- Produces: importable `tools` package; `uv run` works project-wide; ruff/pytest configured (line-length 100, testpaths `tests`).

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[project]
name = "py4kids-tools"
version = "0.1.0"
description = "Verification and build tooling for the py4kids course"
requires-python = ">=3.12"
dependencies = [
    "ipykernel>=7.3.0",
    "jupyter>=1.1.1",
    "nbclient>=0.11.0",
    "nbformat",
    "pyyaml",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.6",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["tools"]

[tool.ruff]
target-version = "py312"
line-length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create empty `tools/__init__.py`**

- [ ] **Step 3: Sync and verify**

Run: `uv sync && uv run python -c "import tools; print('ok')"`
Expected: prints `ok`.

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml uv.lock tools/__init__.py
git commit -m "chore: uv environment and tools package stub (plan 001)"
```

### Task 2: book registry + directory skeleton (TDD)

**Files:**
- Create: `books.yaml`
- Create: `book1/syllabus.md`, `book2/syllabus.md`
- Create: `.gitkeep` in `book1/{curriculum,units,projects,checkpoints,reference,docs}` and the same six under `book2/`
- Test: `tests/test_books.py`

**Interfaces:**
- Produces: `books.yaml` with `books: [{id, number, root, depends_on}]`, ids exactly `["book1", "book2"]` — ci-local.sh (Task 5) and pre-merge-guard.sh (Task 6) rely on these ids and the six-subdir layout.

- [ ] **Step 1: Write the failing test**

`tests/test_books.py`:

```python
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]


def load_catalog():
    return yaml.safe_load((REPO / "books.yaml").read_text(encoding="utf-8"))


def test_registry_ids_order_and_dependencies():
    books = load_catalog()["books"]
    assert [b["id"] for b in books] == ["book1", "book2"]
    assert [b["number"] for b in books] == [1, 2]
    assert books[0]["depends_on"] == []
    assert books[1]["depends_on"] == ["book1"]


def test_book_roots_have_required_layout():
    for book in load_catalog()["books"]:
        root = REPO / book["root"]
        for sub in ("curriculum", "units", "projects", "checkpoints", "reference", "docs"):
            assert (root / sub).is_dir(), f"{book['id']} missing {sub}/"
        assert (root / "syllabus.md").is_file(), f"{book['id']} missing syllabus.md"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_books.py -v`
Expected: FAIL (`books.yaml` not found).

- [ ] **Step 3: Create `books.yaml`**

```yaml
books_version: 1
books:
- id: book1
  number: 1
  root: book1
  depends_on: []
- id: book2
  number: 2
  root: book2
  depends_on:
  - book1
```

- [ ] **Step 4: Create the skeleton**

```bash
for b in book1 book2; do
  mkdir -p $b/curriculum $b/units $b/projects $b/checkpoints $b/reference $b/docs
  touch $b/curriculum/.gitkeep $b/units/.gitkeep $b/projects/.gitkeep \
        $b/checkpoints/.gitkeep $b/reference/.gitkeep $b/docs/.gitkeep
done
```

`book1/syllabus.md`:

```markdown
# Book 1 — Year 1 Syllabus

Authored in plan 002 (Book 1 curriculum architecture).
Until then this file records only the book's identity: Year 1, project-first Python fundamentals, zero-experience baseline.
```

`book2/syllabus.md`:

```markdown
# Book 2 — Year 2 Syllabus

Registered but intentionally unauthored (design §"Out of scope").
Year 2: OOP, algorithms, data, larger builds; prerequisites import from Book 1 via qualified registry contracts.
```

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_books.py -v`
Expected: PASS (2 tests).

- [ ] **Step 6: Commit**

```bash
git add books.yaml book1 book2 tests/test_books.py
git commit -m "feat: book registry and two-book skeleton (plan 001)"
```

### Task 3: AGENTS.md + CLAUDE.md

**Files:**
- Create: `AGENTS.md`
- Create: `CLAUDE.md`

**Interfaces:**
- Produces: the canonical agent instructions every future session loads; references docs created in Task 4 and scripts created in Tasks 5–6 (they land later in this same plan — acceptable within one plan).

- [ ] **Step 1: Write `AGENTS.md`**

```markdown
# Project Instructions

py4kids. A multi-year, project-first Python course for middle school students,
taught by the author to a small class.
Content-as-code: notebooks are the source of truth, PDFs are built artifacts,
and correctness is enforced by executable verification.
Full design: `docs/designs/000-project-design.md`.

It adopts the usaaio development workflow (plan-driven lifecycle, multi-model review
gates, autopilot through merge) tailored for course-content development.

## CRITICAL RULES (never skip)

- **Autopilot is the DEFAULT operating mode.** For design, plans, and fixes, run the full
  lifecycle autonomously through merge — design → 4-way plan-review gate → phase-by-phase
  implementation → verification (`scripts/ci-local.sh`) → 4-way content-review gate →
  post-execution report → PR → `scripts/pre-merge-guard.sh --pr` → squash-merge — without
  per-step approval. **Pause only for:**
  - **Genuine judgment forks** (scope / curriculum-direction / trust decisions) via `AskUserQuestion`.
  - **Hard safeguards** (always stop): committing secrets (`.gh-token`, `.env*`, `*token*`,
    `*secret*`, `*credential*`); committing student data — names, rosters, grades, work
    (**the repo is PUBLIC**); `git push --force`/`reset --hard` on shared history;
    a direct commit to `main`; edits to this file / `docs/development-workflow.md` /
    `docs/content-review-gate.md` / `docs/architecture/decisions.md` (governance —
    human-reviewed, except when the user explicitly asks); plan-scope expansion beyond the
    plan file's phases; unresolved `[OPEN]` blockers at the gate round-cap; a failing
    `pre-merge-guard --pr` / `ci-local.sh`.
  - The user can redirect at any time. Gates are conducted by autopilot, never skipped by it.
- **Branch BEFORE drafting a plan.** `git checkout -b feature/plan-NNN-description` first;
  the plan file and all review verdicts live on that branch. Never commit directly to `main`.
- **Run the 4-way plan-review gate before any implementation** (see `## Plan-review gate`).
- **Run the 4-way content-review gate before opening a PR** (see `docs/content-review-gate.md`).
- **Self-containedness is law.** The student baseline is ZERO programming experience plus
  typical middle-school math.
  Nothing may be used before it is taught (prereq closure), nothing taught without practice
  (coverage), nothing assessed that was not taught. These are CI checks once plan 003 lands;
  until then reviewers enforce them manually.
- **Project-first is law.** Every unit opens with its project/problem hook;
  a unit that opens with concept drill is a gate-blocking finding.
- **Always run `scripts/ci-local.sh` before merge — local is the gate.**
- **Always write a post-execution report** in the plan file before shipping.

## Project Structure

See `docs/designs/000-project-design.md §1` for the full tree. Top level:
`books.yaml` registers two independently complete roots: `book1/` (Year 1 fundamentals)
and `book2/` (Year 2: OOP, algorithms, data, larger builds).
Each book owns its `syllabus.md`, `curriculum/`, `units/`, `projects/`, `checkpoints/`,
`reference/`, and learner-facing `docs/`;
Book 2 imports Book 1 prerequisites only through qualified registry contracts.
`tools/` (Python verification package), `scripts/` (ci-local, pre-merge-guard),
and top-level `docs/` (shared lifecycle, design, plan, and review records).

## Content Conventions

- Student-facing notebooks (exercises, checkpoints) contain NO solutions and no executed
  outputs; solutions live in separate notebooks that run top-to-bottom clean with fixed seeds.
- Every unit, project, and checkpoint carries a `manifest.yaml`
  (concept tags `introduces:`/`requires:`/`practices:`, prerequisites, provenance,
  blueprint version).
- Every unit's `exercises.ipynb` has at least one exercise cell-tagged `stretch`
  (rendered heading "Challenge"); core content never depends on stretch content.
- Every unit ships `teacher-notes.md`: learning goals, 60–90 min pacing plan, project hook,
  common mistakes, discussion prompts, differentiation guidance.
- Datasets come from seeded generation scripts, never opaque blobs.
- Provenance: original content by default; adaptations carry `adapted-from: <reference id>`.
- Docs use semantic line breaks (one sentence per line).

## Verification (the "test suite")

`scripts/ci-local.sh` is authoritative (design §4): registry + lint, unit tests,
notebook execution + hygiene, manifest/prereq/coverage/stretch checks, PDF build,
pre-merge guard.
Checks whose tools don't exist yet print `SKIP (plan NNN)` — a skip is only acceptable
while the named plan is unshipped.

## Git

- Origin is `git@github-weiboz0:weiboz0/py4kids.git` (SSH alias `github-weiboz0` →
  `~/.ssh/id_ed25519_weiboz0`). Do NOT switch to HTTPS or plain `github.com` SSH —
  this machine's default credentials map to a different account.
- Every `gh` command needs `GH_TOKEN=$(cat .gh-token)` (file is gitignored).
- Git identity: Weibo Zhou <weibo.zhou6fe@gmail.com>.
- Never commit directly to `main`; feature branch + PR via `gh pr create`.
- Before any merge: `bash scripts/pre-merge-guard.sh --pr` — catches plan-number and
  unit/project/checkpoint-ID collisions from parallel sessions.
- Commit messages: what changed and why. Batch related small fixes into one logical commit.

## Plan-review gate (mandatory — 4-way)

| # | Reviewer | Dispatch | Model |
|---|----------|----------|-------|
| 1 | Self-review | active session inline; record in `## Plan Review` | active session model |
| 2 | Sol reviewer | `codex:codex-rescue` subagent, fresh and read-only (request `--model gpt-5.6-sol`) | GPT-5.6-sol |
| 3 | GLM reviewer | `opencode:opencode-review` subagent, fresh and read-only | opencode-go/glm-5.2 |
| 4 | Fable reviewer | fresh, read-only Fable 5 subagent (`Agent`, general-purpose) | Fable 5 |

Dispatch 2–4 in parallel with the inline self-review (one message).
Consensus is full blocking: all four APPROVE / APPROVE WITH NITS, no open blockers.
Verdicts use tags `[self]` / `[sol]` / `[glm]` / `[fable]`.
Reviewers MUST REJECT a plan shipping units/projects/checkpoints without a named
verification phase (docs-only and tooling-only plans state the exemption in `## Out of scope`).

## Content-review gate (mandatory — 4-way, pre-PR)

Same roster and tags as the plan-review gate.
Duties and format: `docs/content-review-gate.md`.
Findings use `[OPEN]` / `[FIXED]` / `[WONTFIX]` in the plan file's `## Content Review`;
all `[OPEN]` resolve before merge.

## Agent dispatch

| Work | Dispatch |
|------|----------|
| Planning, review orchestration, curriculum architecture | Active session inline |
| Lesson content + exercise/checkpoint STATEMENTS | `codex:codex-rescue` (GPT-5.6-sol) |
| SOLUTIONS to exercises + checkpoints | `codex:codex-rescue` (GPT-5.6-sol) — SEPARATE fresh session, never reads statements' outlines; cross-model verification lives in the gates |
| Blind independent solving (content gate) | Gate roster (all four reviewers solve blind) |
| Tooling code (`tools/`, `scripts/`) | `codex:codex-rescue` (GPT-5.6-sol) |
| Teacher notes | Active session inline (pedagogy judgment) |
| Trivially-scoped edits | Inline |

## Errata

Post-merge content bugs (wrong answer, broken exercise): 2-way diagnosis
(Claude inline + Codex on GPT-5.6-sol, read-only) → fix plan → gates → merge, plus an
`ERRATA.md` entry in the affected unit/project/checkpoint directory. Typos skip diagnosis.

## Session Handoff

- Commit before ending a session (`WIP:` prefix fine); uncommitted work is invisible.
- Check `git status` at session start; ask before discarding leftovers.
- Verify prior work via plan files' post-execution reports + `git log`, not summaries.
```

- [ ] **Step 2: Write `CLAUDE.md`**

```markdown
# Project Instructions → AGENTS.md

Canonical, agent-agnostic instructions live in [`AGENTS.md`](AGENTS.md) — **edit that file, not
this pointer.** The import below auto-loads it for Claude Code.

@AGENTS.md
```

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md CLAUDE.md
git commit -m "docs: canonical agent instructions (plan 001)"
```

### Task 4: workflow docs, decisions log, TODO

**Files:**
- Create: `docs/development-workflow.md`
- Create: `docs/content-review-gate.md`
- Create: `docs/architecture/decisions.md`
- Create: `TODO.md`

**Interfaces:**
- Produces: the process docs `AGENTS.md` references; `decisions.md` is the append-only decision log later plans must read before designing.

- [ ] **Step 1: Write `docs/development-workflow.md`**

```markdown
# Development Workflow

Follow this process for every plan. Do NOT skip steps or batch them.
Trivial changes (typos, one-line fixes) use judgment; anything multi-file follows the workflow.

## Step 1 — Design

1. Clarify intent: what does the student gain, what does success look like?
2. Read `docs/architecture/decisions.md`, the design doc, and existing plans.
3. Brainstorm approaches, compare trade-offs, align with the user when the fork is genuine.

Output: verbal alignment, a proposal in `docs/proposals/`, or a design in `docs/designs/`.
Skip when the task is well-defined (e.g. "add unit NN per the syllabus").

## Step 2 — Plan

1. Branch: `git checkout -b feature/plan-NNN-description`.
2. Write the plan: phases, file lists, per-phase verification, acceptance criteria.
3. **Named verification phase is mandatory** for any plan shipping units, projects, or
   checkpoints (design §5): solutions execute and reproduce stated answers; manifests
   validate; prereq closure, practice coverage, and stretch presence pass; student
   notebooks are hygienic; PDF builds; the unit opens with its project hook.
   Exempt (docs-only, tooling-only, plan-design plans) must say so in `## Out of scope`.
4. Self-review, then run the 4-way plan-review gate (`AGENTS.md ## Plan-review gate`).
   A passing gate IS approval to implement.
5. Save as `docs/plans/NNN-name.md` (next free number) and commit before any implementation.

## Step 3 — Build

Per phase: implement (dispatch per `AGENTS.md ## Agent dispatch`) → verify → self-review
against the plan and `decisions.md` → update docs → commit.
Independent phases may run in parallel subagents; dependent phases run in order.

## Step 4 — Verify

1. Run `scripts/ci-local.sh` — the full suite, not just changed checks.
2. Confirm the verification phase shipped exactly what its acceptance criteria promised.
3. Check cross-phase consistency (duplicate content, inconsistent terminology, orphan concepts).

## Step 5 — Review

Run the 4-way content-review gate per `docs/content-review-gate.md`.
Findings live in the plan file's `## Content Review`; all `[OPEN]` items resolve before merge.
Evaluate findings rigorously — push back with reasoning rather than agreeing performatively.

## Step 6 — Ship

1. Post-execution report in the plan file (deviations, limitations, follow-ups).
2. Update `decisions.md` and `TODO.md`.
3. Final `scripts/ci-local.sh` run — must be green.
4. Push; `GH_TOKEN=$(cat .gh-token) gh pr create`; `bash scripts/pre-merge-guard.sh --pr`;
   squash-merge.

## Session Handoff

Commit everything before ending (`WIP:` ok); push the branch;
check `git status` on start; trust `git log` + post-execution reports, not summaries.
```

- [ ] **Step 2: Write `docs/content-review-gate.md`**

```markdown
# Content-Review Gate

The pre-PR quality gate for course content
(the tailored equivalent of a code-review gate). 4-way, full-blocking consensus.

## Roster

| # | Reviewer | Dispatch | Model |
|---|----------|----------|-------|
| 1 | Self-review | active session inline | active session model |
| 2 | Sol reviewer | `codex:codex-rescue` subagent, fresh and read-only (request `--model gpt-5.6-sol`) | GPT-5.6-sol |
| 3 | GLM reviewer | `opencode:opencode-review` subagent, fresh and read-only | opencode-go/glm-5.2 |
| 4 | Fable reviewer | fresh, read-only Fable 5 subagent (`Agent`, general-purpose) | Fable 5 |

Dispatch 2–4 in parallel with the inline self-review.
Tooling code changes (`tools/`, `scripts/`) in the same plan get conventional code review
by the same roster in the same round.

## Reviewer duties (content)

1. **Solve blind first.** Attempt each exercise and checkpoint from the student-facing
   materials alone, BEFORE reading the solution. Report your answer, then compare.
2. **Correctness.** Verify solutions against your independent solve.
3. **Clarity.** Flag ambiguous wording, underspecified inputs, unstated assumptions.
4. **Engagement (project-first law).** The unit must open with its project/problem hook;
   opening with concept drill is a blocking finding.
   Judge whether a middle schooler would care about the project.
5. **Age-appropriateness.** Reading level, cultural references, and content suit
   middle school students.
6. **Difficulty + pacing.** Judge against the 60–90 min lesson budget and the declared
   position in the concept progression; stretch exercises stretch without gatekeeping core.
7. **Accessibility.** Read as the target student
   (ZERO programming experience + middle-school math + declared prerequisites only);
   flag any silently-assumed concept.
8. **Provenance.** `adapted-from` tags present where content resembles a known source;
   note any resemblance the tags miss.

## Format

Findings append to the plan file's `## Content Review`, one review round per reviewer pass:

    ### Review N — <reviewer> (YYYY-MM-DD)
    - **Verdict**: Approved / Approved with suggestions / Changes requested
    1. `[OPEN]` Finding with file/section reference. Priority: Must Fix / Should Fix / Nice to Have.

Authors respond inline with `→ Response:` and retag `[FIXED]` / `[WONTFIX]` (with reason).
Source tags: `[self]` / `[sol]` / `[glm]` / `[fable]`.

## Acceptance

All four reviewers APPROVE (or approve-with-nits) and every `[OPEN]` item is resolved.
One REJECT blocks. Iterate fix → re-review to consensus.
```

- [ ] **Step 3: Write `docs/architecture/decisions.md`**

```markdown
# Architecture Decisions

Append-only log.
Read this before designing any plan.

## D-001 (2026-09-05) — Project-first is law
Every unit opens with its project/problem hook; concepts are introduced only when the
project demands them.
Rationale: rigorous CS foundation delivered without pushing students away
(design 000 §Purpose).

## D-002 (2026-09-05) — Checkpoints replace mock tests
Assessment is lightweight checkpoint notebooks plus milestone projects, not exam-style
mock tests; grading stays manual with grading notes.

## D-003 (2026-09-05) — Fixed 4-way gate roster
`[self]` / `[sol]` / `[glm]` / `[fable]` for both gates.
usaaio's dated rotation language is not carried over; this repo starts post-cutoff.

## D-004 (2026-09-05) — Fresh minimal tooling, usaaio shape
Gate scripts and tools are written fresh for py4kids rather than ported verbatim;
usaaio-specific machinery (scope inventories, mutation checks, legacy-layout handling)
is deliberately absent.
```

- [ ] **Step 4: Write `TODO.md`**

```markdown
# TODO

Milestones (design 000 §First milestones):

- [x] Plan 001 — scaffolding & governance (this plan)
- [ ] Plan 002 — Book 1 curriculum architecture: concept registry, syllabus, Year 1 unit/project arc
- [ ] Plan 003 — verification tooling: manifest validation, hygiene, prereq closure, coverage, stretch presence, solution execution, PDF build
- [ ] Plan 004 — first units (01–03) end-to-end through the content gate
```

- [ ] **Step 5: Commit**

```bash
git add docs/development-workflow.md docs/content-review-gate.md docs/architecture/decisions.md TODO.md
git commit -m "docs: workflow, content gate, decisions log, TODO (plan 001)"
```

### Task 5: ci-local.sh

**Files:**
- Create: `scripts/ci-local.sh` (mode 755)

**Interfaces:**
- Consumes: `books.yaml` ids `["book1", "book2"]` (Task 2), `tools`/`tests` (Tasks 1–2), `scripts/pre-merge-guard.sh` (Task 6 — run Task 5's verification only after Task 6 lands, or stub-check for existence as written below).
- Produces: the authoritative local gate every plan runs before merge.

- [ ] **Step 1: Write `scripts/ci-local.sh`**

```bash
#!/usr/bin/env bash
# Authoritative local gate for py4kids.
set -euo pipefail
cd "$(dirname "$0")/.."

step() { echo; echo "=== $1 ==="; }

step "1/6 registry + lint"
uv run python - <<'PY'
import yaml

catalog = yaml.safe_load(open("books.yaml", encoding="utf-8"))
ids = [book["id"] for book in catalog["books"]]
assert ids == ["book1", "book2"], f"unexpected book registry: {ids}"
print("registry: book1 -> book2")
PY
uv run ruff check tools/ tests/ scripts/

step "2/6 unit tests"
uv run pytest -q

step "3/6 notebook execution + hygiene"
echo "SKIP (plan 003): solution/lesson notebook execution, student-notebook hygiene"

step "4/6 manifest + curriculum checks"
echo "SKIP (plan 003): manifest validation, prereq closure, practice coverage, stretch presence"

step "5/6 PDF build"
echo "SKIP (plan 003): PDF build"

step "6/6 pre-merge guard"
bash scripts/pre-merge-guard.sh

echo
echo "ci-local: ALL GREEN"
```

- [ ] **Step 2: Make executable**

Run: `chmod +x scripts/ci-local.sh`

- [ ] **Step 3: Verify steps 1–5 run (guard lands in Task 6)**

Run: `bash scripts/ci-local.sh || true`
Expected: steps 1/6–5/6 green with three `SKIP (plan 003)` lines; step 6/6 fails only because `scripts/pre-merge-guard.sh` doesn't exist yet.

- [ ] **Step 4: Commit**

```bash
git add scripts/ci-local.sh
git commit -m "feat: ci-local gate with plan-003 SKIPs (plan 001)"
```

### Task 6: pre-merge-guard.sh

**Files:**
- Create: `scripts/pre-merge-guard.sh` (mode 755)

**Interfaces:**
- Consumes: repo layout from Task 2 (`bookN/{units,projects,checkpoints}/`, `docs/{proposals,designs,plans,reviews}/`).
- Produces: `bash scripts/pre-merge-guard.sh [--pr]` — exit 0 on OK; `--pr` adds the origin/main union for parallel-session collision detection.

- [ ] **Step 1: Write `scripts/pre-merge-guard.sh`**

```bash
#!/usr/bin/env bash
# Collision and public-repository safety guard.
set -euo pipefail
cd "$(dirname "$0")/.."

mode=${1:-}
if [[ -n "$mode" && "$mode" != --pr ]]; then
  echo "usage: pre-merge-guard.sh [--pr]   (unknown argument: $mode)" >&2
  exit 2
fi
if [[ "$mode" == --pr ]]; then
  if ! git fetch -q origin main 2>/dev/null; then
    echo "FAIL: origin/main fetch unavailable; --pr union is unverified" >&2
    exit 1
  fi
fi

uv run python - "$mode" <<'PY'
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

mode = sys.argv[1]
refs = ["WORKTREE"] + (["origin/main"] if mode == "--pr" else [])
failures: list[str] = []


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False)


def paths(ref: str) -> set[str]:
    if ref == "WORKTREE":
        return {
            path.as_posix()
            for path in Path(".").rglob("*")
            if path.is_file() and ".git" not in path.parts and ".venv" not in path.parts
        }
    return set(git("ls-tree", "-r", "--name-only", ref).stdout.splitlines())


def duplicate_numbers(label: str, names: set[str], pattern: str) -> None:
    numbers = [match.group(0) for name in names if (match := re.match(pattern, name))]
    duplicates = sorted(value for value, count in Counter(numbers).items() if count > 1)
    if duplicates:
        failures.append(f"duplicate {label} number(s): {' '.join(duplicates)}")


all_paths = {ref: paths(ref) for ref in refs}

for directory in ("docs/proposals", "docs/designs", "docs/plans", "docs/reviews"):
    names = {
        path.split("/")[-1]
        for ref in refs
        for path in all_paths[ref]
        if path.startswith(directory + "/") and path.count("/") == directory.count("/") + 1
    }
    duplicate_numbers(directory, names, r"^[0-9]{3}")

for book_id in ("book1", "book2"):
    for kind, pattern in (
        ("units", r"^unit-[0-9]{2}"),
        ("projects", r"^project-[0-9]{2}"),
        ("checkpoints", r"^checkpoint-[0-9]{2}"),
    ):
        prefix = f"{book_id}/{kind}/"
        names = {
            path[len(prefix):].split("/", 1)[0]
            for ref in refs
            for path in all_paths[ref]
            if path.startswith(prefix) and "/" in path[len(prefix):]
        }
        duplicate_numbers(f"{book_id}/{kind}", names, pattern)

tracked = set(git("ls-files").stdout.splitlines())
for path in sorted(tracked):
    name = path.rsplit("/", 1)[-1].lower()
    if (
        name == ".gh-token"
        or name.startswith(".env")
        or any(marker in name for marker in ("token", "secret", "credential"))
    ):
        failures.append(f"tracked secret-like file: {path}")
    if any(segment in ("student-data", "rosters", "grades") for segment in path.split("/")):
        failures.append(f"tracked student-data path: {path}")

conflicts = git("grep", "-nE", r"^(<{7}|={7}|>{7})( |$)", "--", ":!scripts/pre-merge-guard.sh")
if conflicts.returncode == 0:
    failures.append("conflict markers found")

for failure in failures:
    print(f"FAIL: {failure}")
if not failures:
    print("pre-merge-guard: OK")
raise SystemExit(bool(failures))
PY
```

- [ ] **Step 2: Make executable and verify OK path**

Run: `chmod +x scripts/pre-merge-guard.sh && bash scripts/pre-merge-guard.sh`
Expected: `pre-merge-guard: OK`, exit 0.

- [ ] **Step 3: Verify the FAIL path (throwaway probe)**

```bash
touch docs/plans/001-collision-probe.md
bash scripts/pre-merge-guard.sh && echo "BUG: guard missed collision" || echo "guard caught collision"
rm docs/plans/001-collision-probe.md
```

Expected: `FAIL: duplicate docs/plans number(s): 001` then `guard caught collision`.

- [ ] **Step 4: Run the full gate green**

Run: `bash scripts/ci-local.sh`
Expected: all six steps pass, `ci-local: ALL GREEN`.

- [ ] **Step 5: Commit**

```bash
git add scripts/pre-merge-guard.sh
git commit -m "feat: pre-merge collision and safety guard (plan 001)"
```

---

## Plan Review

(4-way gate verdicts land here.)

## Content Review

(pre-PR gate findings land here.)

## Post-Execution Report

(written before shipping.)
