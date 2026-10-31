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

## D-003 (2026-09-05) — Fixed gate roster
Originally 4-way: `[self]` / `[sol]` / `[glm]` / `[fable]` for both gates.
usaaio's dated rotation language is not carried over; this repo starts post-cutoff.
**Superseded 2026-10-05 (user directive):** the GLM reviewer is removed from the review rolls after a
persistent opencode-companion invocation-layer failure. Both gates are now **3-way**: `[self]` / `[sol]` /
`[fable]`, full-blocking consensus. Re-add GLM only on a further user directive once the companion is reliable.

## D-004 (2026-09-05) — Fresh minimal tooling, usaaio shape
Gate scripts and tools are written fresh for py4kids rather than ported verbatim;
usaaio-specific machinery (scope inventories, mutation checks, legacy-layout handling)
is deliberately absent.

## D-005 (2026-09-06) — Turtle lessons run as .py scripts, not in notebook cells
Built-in `turtle` opens a Tk window and does not render inside Jupyter cells.
Turtle-based lessons (Book 1 units 03/05, optional in projects) therefore run as `.py`
scripts launched from the JupyterLab/VS Code terminal; notebooks remain the medium for
all other work and for turtle exercise write-ups.
Rationale: keeps the zero-new-dependencies graphics choice (user-settled 2026-09-06)
compatible with notebooks-as-source-of-truth (design 000). User-approved 2026-09-06.

## D-006 (2026-10-31) — Content models
D-001 (project-first), D-002 (checkpoints replace mock tests) and D-004 (fresh minimal tooling;
usaaio scope inventories, mutation checks and legacy handling deliberately absent) govern
`py4kids`-model books.
A book registered `content_model: aio` (design 014: the AI Olympiad books migrated from usaaio)
follows the aio model instead, and for those books this decision **supersedes D-001, D-002 and D-004**:
they keep mock tests and the usaaio checks, including the mutation verifiers, isolated in `tools/aio/`.
Rationale: their audience (Calculus AB + Python), contest-shaped A/B/C practice and blueprinted mock
tests fit poorly into the beginner unit laws (design 014 §1). User-approved 2026-10-31.
