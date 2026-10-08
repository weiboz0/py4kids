# Content-Review Gate

The pre-PR quality gate for course content
(the tailored equivalent of a code-review gate). 3-way, full-blocking consensus.

## Roster

| # | Reviewer | Dispatch | Model |
|---|----------|----------|-------|
| 1 | Self-review | active session inline | active session model |
| 2 | Sol reviewer | `codex:codex-rescue` subagent, fresh and read-only (request `--model gpt-6-sol`; if it is rejected or unavailable, fall back to `--model gpt-5.6-sol`) | GPT-6-sol (fallback GPT-5.6-sol) |
| 3 | Fable reviewer | fresh, read-only Fable 5 subagent (`Agent`, general-purpose) | Fable 5 |

(The GLM reviewer was removed from the review rolls by user directive on 2026-10-05 after a persistent
opencode-companion invocation failure; the gate is 3-way.)

Dispatch 2–3 in parallel with the inline self-review.
Tooling code changes (`tools/`, `scripts/`) in the same plan get conventional code review
by the same roster in the same round.

## Reviewer duties (content)

1. **Solve blind first.** Attempt each exercise and checkpoint from the student-facing
   materials alone, BEFORE reading the solution. Report your answer, then compare.
2. **Correctness.** Verify solutions against your independent solve.
3. **Clarity.** Flag ambiguous wording, underspecified inputs, unstated assumptions.
4. **Engagement (project-first law).** The unit must open with its project/problem hook;
   opening with concept drill is a blocking finding.
   Judge whether the book's declared audience would care about the project.
5. **Audience-appropriateness.** Reading level, cultural references, and content suit
   the book's declared audience — design 000's middle-school default, or a book's own
   declared baseline per its design doc (e.g. design 011 for an advanced book).
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
    - **Verdict**: APPROVE / APPROVE WITH NITS / REJECT
    1. `[OPEN]` Finding with file/section reference. Priority: Must Fix / Should Fix / Nice to Have.

Authors respond inline with `→ Response:` and retag `[FIXED]` / `[WONTFIX]` (with reason).
Source tags: `[self]` / `[sol]` / `[fable]`.

## Acceptance

All three reviewers APPROVE or APPROVE WITH NITS and every `[OPEN]` item is resolved.
One REJECT blocks. Iterate fix → re-review to consensus.
