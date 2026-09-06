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
