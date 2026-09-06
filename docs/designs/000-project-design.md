# Design 000 — py4kids: Python Course for Middle School Students

Status: approved (brainstormed 2026-09-05).
Governs repo structure, curriculum architecture, content conventions, verification, and dev process.

## Purpose

A multi-year Python course for middle school students, taught by the author to a small class.
The end goal is a rigorous CS foundation — a complete, ordered concept progression from zero
through data structures and OOP — delivered **project-first**: every unit opens with a project
or problem the students want to solve, and concepts are introduced only when the project
demands them. Rigor is enforced by tooling (prereq closure, practice coverage);
engagement is enforced by design (no unit may open with concept drill).

## Requirements (settled during brainstorming)

- **Orientation:** rigorous CS foundation, project/problem-first delivery — especially at the
  beginning, to avoid boring content that pushes students away.
- **Audience:** a small class taught by the author; materials include teacher notes and pacing.
- **Scope:** multi-year sequence. Book 1 = Year 1 (fundamentals), Book 2 = Year 2
  (OOP, algorithms, data, larger builds). Later books possible; each book is independently
  complete like usaaio's.
- **Baseline:** design for zero programming experience and typical middle-school math.
  Ability is mixed, so every unit carries `stretch`-tagged challenge exercises.
- **Format:** Jupyter notebooks as source of truth; PDFs are built artifacts.
  Students use JupyterLab or VS Code.
- **Repo:** public `weiboz0/py4kids`. Adopts the usaaio/PowerMarket dev process
  (plan-driven lifecycle, 4-way review gates, autopilot through merge).

## 1. Repo structure

```
py4kids/
├── AGENTS.md                  # canonical agent instructions (CLAUDE.md is a pointer)
├── CLAUDE.md
├── books.yaml                 # registry of book roots
├── book1/                     # Year 1 — fundamentals, project-first
│   ├── syllabus.md
│   ├── curriculum/            # concept registry: every concept has an id
│   ├── units/
│   │   └── unit-NN-slug/
│   │       ├── manifest.yaml  # introduces/requires/practices, prereqs, provenance, blueprint version
│   │       ├── lesson.ipynb   # teacher-led session; opens with the project hook
│   │       ├── exercises.ipynb  # student-facing: NO solutions, no executed outputs; has stretch exercises
│   │       ├── solutions.ipynb  # runs top-to-bottom clean, fixed seeds
│   │       ├── teacher-notes.md
│   │       └── assets/        # seeded generation scripts only, never opaque blobs
│   ├── projects/              # multi-week milestone builds + year capstone
│   ├── checkpoints/           # lightweight assessment notebooks (replaces usaaio mocktests)
│   ├── reference/
│   ├── docs/                  # learner-facing
│   └── build/                 # PDF artifacts (gitignored)
├── book2/                     # Year 2 — OOP, algorithms, data, larger builds (same shape)
├── docs/
│   ├── designs/  plans/  proposals/  reviews/  architecture/
│   ├── development-workflow.md
│   └── content-review-gate.md
├── tools/                     # Python verification package (checks, CLI)
├── scripts/                   # ci-local.sh, pre-merge-guard.sh, build-pdf.sh
└── pyproject.toml             # uv-managed environment
```

Book 2 imports Book 1 prerequisites only through qualified registry contracts
(concept ids namespaced by book), exactly as usaaio's book2 does.
Content commands require `--book <id>` or an explicitly supported `--all` route.

## 2. Curriculum architecture

### Project-spine principle

Each unit is anchored by a project (e.g., mad-libs → guessing game → turtle art →
quiz app → text adventure → capstone). The sequence of projects is engineered so the
underlying concept progression is complete and ordered
(output/strings → variables → conditionals → loops → functions → lists/dicts → files → OOP …).
The exact Book 1 unit list is authored in the first curriculum plan, not fixed here.

### Self-containedness (law, as in usaaio)

The student baseline is zero programming + middle-school math.
- **Prereq closure:** nothing may be used before the unit that `introduces:` it.
- **Practice coverage:** every introduced concept has exercises.
- **Assessment alignment:** checkpoints test only what has been taught.
These are CI checks once the verification tooling lands; until then reviewers enforce
them manually.

### Mixed-ability rule

Every unit's `exercises.ipynb` contains at least one stretch exercise, marked with the
notebook cell tag `stretch` (the tag is machine-checkable; the rendered heading says "Challenge").
Stretch content may preview upcoming concepts but core content never depends on it.

### Teacher materials

`teacher-notes.md` per unit: learning goals, a 60–90 min pacing plan, how to run the
project hook, common student mistakes, discussion prompts, and differentiation guidance.
Checkpoints carry grading notes.

## 3. Content conventions

- Student-facing notebooks (exercises, checkpoints) contain NO solutions and no executed
  outputs; solutions live in separate notebooks that run top-to-bottom clean with fixed seeds.
- Every unit, project, and checkpoint carries a `manifest.yaml`
  (concept tags, prerequisites, provenance, blueprint version).
- Datasets come from seeded generation scripts, never opaque blobs.
- Provenance: original content by default; adaptations carry `adapted-from: <reference id>`.
- Docs use semantic line breaks (one sentence per line).
- **The repo is PUBLIC:** never commit student data, rosters, grades, or secrets.

## 4. Verification (CI)

`scripts/ci-local.sh` is authoritative — local is the gate. Checks:

1. Solution-notebook execution (top-to-bottom, fixed seeds, reproduces stated answers).
2. Student-notebook hygiene (no solutions, no executed outputs).
3. Manifest validation (schema + referenced concepts exist in the registry).
4. Prereq closure.
5. Practice coverage.
6. Stretch-exercise presence per unit.
7. PDF build.
8. Lint (ruff) for `tools/`, `scripts/`, and notebook code cells.

Checks whose tools don't exist yet print `SKIP (plan NNN)`;
a skip is only acceptable while the named plan is unshipped.

## 5. Lifecycle and gates

Adopts the usaaio workflow unchanged in shape; `docs/development-workflow.md` and
`docs/content-review-gate.md` are ported and adapted.

- Autopilot is the default operating mode: design → 4-way plan-review gate →
  phase-by-phase implementation → `ci-local.sh` → 4-way content-review gate →
  post-execution report → PR → `pre-merge-guard.sh --pr` → squash-merge.
  Pause only for genuine judgment forks and hard safeguards.
- Branch before drafting a plan (`feature/plan-NNN-description`); never commit to `main`.
- **Plan-review gate (4-way):** `[self]` (active session, inline),
  `[sol]` (codex:codex-rescue, GPT-5.6-sol, fresh read-only),
  `[glm]` (opencode:opencode-review, fresh read-only),
  `[fable]` (fresh read-only Fable 5 reviewer — post-2026-08-09 rotation).
  Full blocking consensus: all four APPROVE / APPROVE WITH NITS, no open blockers.
  Reviewers MUST REJECT a plan shipping units/projects/checkpoints without a named
  verification phase (docs-only and tooling-only plans state the exemption in `## Out of scope`).
- **Content-review gate (4-way, pre-PR):** same roster; findings tracked
  `[OPEN]` / `[FIXED]` / `[WONTFIX]` in the plan file's `## Content Review`;
  all `[OPEN]` resolve before merge. Reviewers blind-solve exercises and checkpoints,
  and additionally review for age-appropriateness and engagement
  (does the unit open with the hook, or with drill?).
- **Errata:** post-merge content bugs get 2-way diagnosis (Claude inline + Codex GPT-5.6-sol,
  read-only) → fix plan → gates → merge, plus an `ERRATA.md` entry in the affected directory.
  Typos skip diagnosis.

## 6. Agent dispatch

| Work | Dispatch |
|------|----------|
| Planning, review orchestration, curriculum architecture | Active session inline |
| Lesson content + exercise/checkpoint STATEMENTS | `codex:codex-rescue` (GPT-5.6-sol) |
| SOLUTIONS to exercises + checkpoints | `codex:codex-rescue` (GPT-5.6-sol) — separate fresh session, never reads statement outlines; cross-model verification lives in the gates |
| Blind independent solving (content gate) | Gate roster (all four reviewers solve blind) |
| Tooling code (`tools/`, `scripts/`) | `codex:codex-rescue` (GPT-5.6-sol) |
| Teacher notes | Active session inline (pedagogy judgment) |
| Trivially-scoped edits | Inline |

## 7. Git and GitHub

- Origin: `git@github-weiboz0:weiboz0/py4kids.git` (SSH alias `github-weiboz0`).
  Do NOT switch to HTTPS or plain `github.com` SSH.
- Every `gh` command: `GH_TOKEN=$(cat .gh-token)` (file gitignored, copied from usaaio).
- Git identity: Weibo Zhou <weibo.zhou6fe@gmail.com>.
- Feature branch + PR; `pre-merge-guard.sh --pr` before every merge; squash-merge.

## First milestones (each its own plan)

1. **Plan 001 — Scaffolding & governance:** AGENTS.md/CLAUDE.md, books.yaml, directory
   skeleton, ported workflow docs, pyproject/uv, ci-local.sh with all checks SKIPping,
   pre-merge-guard.sh.
2. **Plan 002 — Book 1 curriculum architecture:** concept registry, syllabus, full Year 1
   unit/project arc with manifests' concept mapping.
3. **Plan 003 — Verification tooling:** manifest validation, notebook hygiene, prereq
   closure, practice coverage, stretch presence, solution execution, PDF build.
4. **Plan 004 — First units:** units 01–03 end-to-end through the content gate,
   proving the pipeline.

## Out of scope (for now)

- Book 2 syllabus detail (Year 2 is registered but authored later).
- Auto-grading of student submissions; grading stays manual with grading notes.
- Hosting/LMS integration; distribution is PDFs + notebooks.
- Videos or slides; the lesson notebook is the classroom medium.
