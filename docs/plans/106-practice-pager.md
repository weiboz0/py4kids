# Plan 106 — Practice pages: one exercise at a time, with a list to jump around

**Goal:** a practice page shows **one exercise (item) at a time**, with Previous / Next and a list of every item on the page to jump to any of them.
User request, 2026-10-22: "Let's make the exercise one per page, and provide a list to jump around."

**Spec:** design 012 part B (the practice page, plan 103 Phase B; checks, plan 104 Phase B).
The live site is https://learn.futurespark.cc (plan 105 Phase F); redeploying it after merge is a separate, user-approved step (`scripts/deploy-pages.sh`).

## Decision: a client-side pager over the existing page, not one HTML page per item

Each entry keeps its one static practice page `/<book>/<entry>/practice/`.
A small island shows one item at a time, addressed by the item's existing anchor (`#<anchor>`, already unique per page and already used by links and resume).

Why not a static page per item:

- About 2,000 more HTML pages, a larger offline download per book, and Pagefind results split per item.
- The leak tests, the offline manifests, the item-level resume and the `answer/` and `check/` projections are all built around one page per entry. Re-deriving them gains nothing a student sees.
- Hash addressing already gives each exercise its own URL, Back/Forward history and a working resume.

Without JavaScript (and for search indexing and printing), the page renders exactly as today: every item in order.

## Global constraints

- **No change to checking, gating or data:** `practice.ts` check logic, the projections, odd-answer gating, events and attempts are untouched.
  An item that is not shown is only hidden (`hidden`), never removed, so its editor state, checklists and results survive switching away and back.
- **Progressive enhancement:** the server-rendered page shows all items; the pager enhances it after load. A page with one item shows no pager chrome.
- **Strict CSP unchanged:** no inline script or style; styles go in `site/src/styles/checks.css` (or a new stylesheet imported by the page).
- **Accessibility (WCAG 2.1 AA, axe clean in both colour schemes):**
  - The list is a `<nav aria-label="Exercises on this page">` of links; the current one carries `aria-current="step"`.
  - Previous / Next are real buttons or links with text labels ("Previous: Exercise 3", "Next: Exercise 5"), disabled at the ends.
  - Changing item moves focus to the shown item's heading (`tabindex="-1"`), and a polite live region announces "Exercise 4 of 12".
  - Keyboard only: every control is reachable; no keyboard trap. Arrow-key shortcuts are not added (they would fight the code editor).
- **Layout:** on wide screens the list is a sticky side column; at phone width it collapses into a `<details>` "All exercises (12)" above the item, with no horizontal scroll at 320 px.
- **Status in the list,** from the progress store (IndexedDB, read-only here): ✓ passed (latest check event `pass`, or a self-check marked `done`), • tried (any event), nothing otherwise, each with a visually hidden text equivalent ("passed", "tried").
  A Challenge (stretch) item is tagged in the list. The list updates when a Check or a self-check completes on the page (listen for the events the page already writes, or re-read on the existing result event).
- **Addressing:**
  - `#<anchor>` of an item shows that item; an empty or unknown hash shows the first item and does not push history.
  - Choosing an item pushes a history entry (`#anchor`), so Back returns to the previous exercise; `hashchange` drives the view.
  - Resume already records `pathname + hash`; it must keep landing on the item.
- **What travels with an item:** each item's `before` blocks (context paragraphs authored before it) are shown with that item. The entry intro is shown above the first item and collapsible on later items ("About these exercises"); the outro is shown after the last item.
- **Checkpoints and projects** use the same page template and get the same pager.

## Phases

- **Phase A: markup.** In `practice/index.astro`, wrap each item's `before` blocks and its `<section class="practice-item">` in one step container (`<div class="practice-step" data-step data-anchor=…>`), and render the jump list and Previous / Next controls server-side (hidden until the island enables them; `[hidden]` attribute, no inline style). The list's labels come from the same `item.label` / `item.title` the headings use.
- **Phase B: the island.** `site/src/scripts/practice-pager.ts`, imported by the page: reads the hash, shows one step and hides the rest, wires the list and Previous / Next, manages focus, the live region and history, and fills list statuses from the progress store. It must not break `practice.ts`: lazily mounted editors (IntersectionObserver) mount when their step is shown; a Check running on a hidden step finishes and still records its result.
- **Phase C: tests (the named verification phase).**
  - Unit (vitest): hash → step resolution (known, unknown, empty), Previous / Next bounds, status derivation from events (pass, tried, self-check done, none).
  - Playwright (`site/e2e/pager.spec.ts`):
    - one item visible on load (the first), and `#<anchor>` deep links show that item;
    - list navigation and Previous / Next change the shown item, push history, and Back returns to the previous item;
    - focus moves to the item heading and the live region announces the position;
    - a Check passed on item 2, then a jump to item 5 and back to item 2: the code and the result are still there, and the list shows ✓ for item 2;
    - a self-check ticked shows • or ✓ per the rule;
    - resume: leaving from item 3 and following "Continue" lands on item 3;
    - phone width (360 px): the list is a collapsed `<details>`, no horizontal scroll;
    - with JavaScript disabled, every item is visible;
    - a one-item page shows no pager chrome;
    - axe on the pager in light and dark; zero CSP violations.
  - The existing site, site-sw, PWA and lighthouse suites still pass (some e2e tests address items on a practice page directly and may need the hash or a helper that shows the item first: update `e2e/helpers/practice.ts` `open()` to navigate to `#<anchor>`).
  - `scripts/ci-local.sh` solo on the final commit.

## Out of scope

- One HTML page per item (rejected above).
- Changing what is checked, how, or what is revealed.
- Redeploying the live site: after merge, `scripts/build-release.sh` + `scripts/deploy-pages.sh` + `pnpm -C site e2e:live`, run only with the user's go-ahead.
- No unit, project or checkpoint content changes, so the curriculum checks are unaffected (a site-only plan; the verification phase is Phase C).

## Plan Review

## Content Review

## Post-Execution Report
