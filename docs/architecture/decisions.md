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
