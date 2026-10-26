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

- **No change to checking, gating or data:** what is checked, how, what is revealed, the projections, events and attempts are untouched.
  The only changes to `practice.ts` are the `check-start` and terminal `check` notifications, `withStore` returning whether its write succeeded (a boolean), and, in **both** the code-check and typed-answer paths, the not-saved note in the result area when it did not (see Events); the only changes to `progress-page.ts` are recording the position on `py4kids:step` and the `checklist` notification after a checklist is saved.
  An item that is not shown is only hidden (`hidden`), never removed, so its editor state, checklists and results survive switching away and back.
- **Progressive enhancement:** the server-rendered page shows all items; the pager enhances it after load. A page with one item shows no pager chrome (no instance exists today; kept as a rule).
- **Strict CSP unchanged:** no inline script or style; styles go in `site/src/styles/checks.css` (or a new stylesheet imported by the page).
- **Groups.** Most `before` blocks are headings that open a *run* of items ("Milestone 2", "Challenge — Exercises 25–28 combine file skills", "Algorithm Extension — optional enrichment"); some are marker comments or short paragraphs.
  A `before` block **that contains a heading** starts a group that lasts until the next one; its label is the heading text (`lastHeading` in `entry.ts`). A `before` block without a heading (a marker comment, or a "Try these…" paragraph) starts no group and travels with its item:
  - the jump list is grouped under those headings (a sub-list per group);
  - every item in a group shows the group heading as a small kicker above its own heading (a `<p class="step-kicker">`, not a heading element, so the outline stays h1 → h2 and Pagefind makes no sub-result of it), so Exercise 26 still says it is optional stretch work and Problem 5 still says "Milestone 2". A Challenge tag is not repeated on an item whose kicker already says "Challenge";
  - the full `before` content (heading plus any paragraph) is shown with the group's first item, as today.
- **Accessibility (WCAG 2.1 AA, axe clean in both colour schemes):**
  - The list is a `<nav aria-label="Exercises on this page">` of links; the current one carries `aria-current="step"`.
  - Previous / Next are `<button>`s with text labels using the item labels ("Previous: Exercise 3", "Next: Challenge 1"), **disabled** (not removed) at the ends, so focus never drops to `body`.
  - Changing item by a pager control moves focus to the shown item's heading (`tabindex="-1"`). The heading carries a visually hidden position ("4 of 12"), so no separate live region announces navigation (no double announcement).
  - Keyboard only: every control is reachable; no keyboard trap. Arrow-key shortcuts are not added (they would fight the code editor).
- **Layout:** the practice page gets a wider layout (a `wide` option on `Base.astro`, or a `.practice-layout` grid that escapes the 72ch measure) so that on wide screens the list is a sticky side column with its own `max-height: 100dvh; overflow: auto` (pages have up to 37 items); the item itself keeps the reading measure.
  At phone width the list collapses into a `<details>` "All exercises (12)" above the item, with no horizontal scroll at 320 px.
- **Status in the list,** derived by pure functions in `site/src/lib/pager.ts` from the progress store's events (IndexedDB, read-only here):
  - ✓ passed: for an automatic-check item, **any** check event with result `pass` (a later failed experiment does not take the ✓ away); for a `self-check` item, its latest self-check event is `done`.
  - • tried: any other event for the item, including an `also_check` checklist (which never counts as passed: it is not the automatic check).
  - nothing otherwise. Each symbol has a visually hidden text equivalent ("passed", "tried").
  - A Challenge (stretch) item is tagged in the list.
  - While a check runs on an item, its list entry says "checking…" (glyph plus hidden text).
- **Events** (added to the `dom-events.ts` contract):
  - `py4kids:check-start` `{ key }`, dispatched by `practice.ts` when a check or typed answer starts (where it sets the item busy);
  - `py4kids:check` `{ key, result, saved }`, the terminal notification, dispatched by `practice.ts` from the end of **every** path: `pass`, `fail`, `partial` after the save was attempted, and `error` (runner unavailable or an unexpected failure) and `stopped` (Stop pressed). The event says what happened, not what was stored: `withStore` swallows storage failures, so the event's result is used only to clear "checking…" and for the announcement. `saved` is false when the event's write was rejected: `withStore` reports success or failure to its caller (a boolean) instead of only logging it;
  - `py4kids:checklist` `{ key, done }`, dispatched by `progress-page.ts` after a checklist is recorded;
  - `py4kids:step` `{ href }`, dispatched once per shown step from the pager's single show function (reached from the controls, the list, Back/Forward and load), which `progress-page.ts` records as the resume position, as it does for `py4kids:slide`.
  The pager sets "checking…" on `check-start` and clears it on the terminal `check`. **Statuses always come from the store:** on every `check` and `checklist` notification the pager re-reads that item's events and derives its status (`lib/pager.ts`), so ✓ appears only for a `pass` that was actually recorded, and a failed save leaves the list as it was.
  When a check ends on a **hidden** item, a page-level polite live region announces "Exercise 2: Passed" (or "Not yet", "Could not check", "Stopped"), since the item's own `aria-live` region does not speak while hidden.
  **A failed save is said, not silent:** the item's result area adds "Your result could not be saved on this device, so it will not count toward your progress." (shown on the item, so it is there when the student returns to a hidden item), and the hidden-item announcement adds "but not saved". The existing unsaved-progress notice covers only a store that was not persistent at open, so it does not cover this case. Stop stays on the item; switching away does not stop a running check.
- **Addressing and history:**
  - Hash resolution: `document.getElementById(hash)?.closest('[data-step]')`. The item anchor, the heading `#<anchor>-h` (which Pagefind sub-results link to), and any id inside a `before` block or the item all show their step. For an id other than the step or its heading, the pager scrolls that element into view after showing the step and does not move focus.
  - **At load**, an empty or unresolvable hash shows the first item and does not touch history. **On a later `hashchange`**, a hash that resolves to no step (the skip link `#main`, any in-page link outside a step) leaves the current step shown and lets the browser jump normally.
  - **Jump-list choices are real `<a href="#anchor">` links:** native fragment navigation pushes a history entry and fires `hashchange`, which drives the view. Back and Forward step through the items the student chose.
  - **Previous / Next (buttons) replace the current entry** (`history.replaceState`, then show directly, since `replaceState` fires no `hashchange`), matching the slide player, so 36 presses of Next do not leave 36 Back steps; Back still leaves the page or returns to the last list choice.
- **Intro and outro:** the entry intro is shown above the first item; on later items it is a `<details>` "About these exercises", open by default when the intro is a single short block (checkpoint rules stay visible). The outro is shown after the last item.
- **Search:** the jump list and the Previous / Next controls are outside `data-pagefind-body` (or carry `data-pagefind-ignore`), so they do not pollute excerpts. On practice pages the search results link to the matched item through Pagefind's `sub_results` heading anchors (`search.ts`), so a hit lands on that exercise rather than on item 1.
- **Print:** `@media print` shows every step and hides the pager chrome. The rule needs `display: block !important`, because `progress.css` sets `[hidden] { display: none !important; }` site-wide.
- **Checkpoints and projects** use the same page template and get the same pager.

## Phases

- **Phase A: markup and layout.** In `practice/index.astro`: wrap each item (and, for a group's first item, its `before` blocks) in a step container (`<div class="practice-step" data-step data-anchor=…>`); compute the groups (in `entry.ts`'s practice view, exposing a group label per item) and render the group kicker per item; render the grouped jump list and Previous / Next server-side, hidden until the island enables them (`[hidden]`, no inline style), outside the Pagefind body; the wide layout; the print rule.
- **Phase B: the island and events.**
  - `site/src/lib/pager.ts` (pure, unit-tested): hash → step resolution, Previous / Next targets, status derivation.
  - `site/src/scripts/practice-pager.ts`, imported by the page: shows one step, wires the list and controls with the history rules above, focus, the hidden-check live region, the "checking…" state, and the list statuses.
  - `dom-events.ts`: the four events; `practice.ts` dispatches `py4kids:check-start` and the terminal `py4kids:check` (with `saved`), makes `withStore` return a boolean, and shows the not-saved note in both the code-check and typed-answer paths; `progress-page.ts` dispatches `py4kids:checklist` and records `py4kids:step` as the resume position.
  - `search.ts`: practice-page results link to the matching sub-result anchor.
  - It must not break `practice.ts`: lazily mounted editors (IntersectionObserver) mount when their step is shown; a check running on a hidden step finishes, records and announces its result.
- **Phase C: tests (the named verification phase).**
  - Unit (vitest, `site/test/pager.test.ts`): hash resolution (item anchor, heading id, an id inside a `before` block, unknown or empty at load → first item, unresolvable later → unchanged); Previous / Next at both ends; the status rule (any pass → ✓ after a later fail; a self-check `done` → ✓; an automatic item whose `also_check` list is done but whose check failed → •; no events → nothing); grouping from `before` blocks.
  - Playwright (`site/e2e/pager.spec.ts`):
    - one item visible on load (the first); `#<anchor>` and `#<anchor>-h` deep links show that item;
    - a jump-list choice pushes history (Back returns to the previous item, Forward again); Previous / Next replace it (after Next×3, one Back leaves the page or returns to the last list choice);
    - focus moves to the item heading on a control or list choice; the heading's position text reads "4 of 12";
    - a Check passed on item 2, a jump to item 5 and back: the code and the result are still there, and the list shows ✓ for item 2; a failed re-check keeps the ✓;
    - a check started on item 2, then a jump to item 5 before it ends: item 2's list entry says "checking…", then the page live region announces its result;
    - a check that ends without a result (Stop pressed on item 2 after a jump away and back, and a runner failure forced by blocking the runner origin): "checking…" clears and the outcome is announced;
    - the skip link on item 5 (`#main`) keeps item 5 shown;
    - a group whose first item has two `before` blocks (a heading and a marker comment, unit-04-quiz-show Exercise 11; a heading and a paragraph, unit-05-function-factory Challenge 1): one group, both blocks with the first item, the kicker from the heading only;
    - a passing check whose save fails (and, separately, a correct typed answer whose save fails) clears "checking…", shows no ✓, and shows the not-saved note on the item; done on a hidden item, the announcement says "Passed, but not saved". The harness makes an **open** IndexedDB store's write reject (an init script stubs `IDBObjectStore.prototype.put` / `add` to throw for the `events` store before Check is pressed). Making IndexedDB unavailable would not do: the store would fall back to memory, where the write succeeds;
    - a self-check ticked to done shows ✓; an `also_check` list ticked on a failed automatic item shows •;
    - group kickers: an item in the middle of a group (Exercise 26 of unit 12, Problem 5 of project 1) shows its group heading; the list shows the groups;
    - resume: navigate to item 3 by Next, assert the saved resume href ends with item 3's anchor, leave, follow "Continue", land on item 3;
    - a search for words unique to a later exercise links to that exercise's anchor and lands on it;
    - print (`page.emulateMedia({ media: 'print' })`): every item visible and the pager chrome hidden;
    - phone width (360 px): the list is a collapsed `<details>`, no horizontal scroll; wide width: the side list scrolls on its own;
    - with JavaScript disabled, every item is visible;
    - axe on the pager in light and dark (list open and closed); zero CSP violations.
  - **Existing tests that address items directly are updated:**
    - `e2e/helpers/content.ts`: `Found` gains `anchor` (from `itemAnchors`);
    - `e2e/helpers/practice.ts` `open()` navigates to `page + '#' + anchor`;
    - `acceptance.spec.ts` (≈55–58: its own goto and fill) and `journey.spec.ts` (≈63–70: the first self-check box on the page) go to the item's anchor first;
    - `review-fixes.spec.ts` (≈115: the resume href has no hash on first load) stays as is: an empty hash touches nothing.
  - The existing site, site-sw, PWA and lighthouse suites still pass.
  - `scripts/ci-local.sh` solo on the final commit.

## Out of scope

- One HTML page per item (rejected above).
- Changing what is checked, how, or what is revealed.
- Redeploying the live site: after merge, `scripts/build-release.sh` + `scripts/deploy-pages.sh` + `pnpm -C site e2e:live`, run only with the user's go-ahead.
- No unit, project or checkpoint content changes, so the curriculum checks are unaffected (a site-only plan; the verification phase is Phase C).

## Plan Review

### Round 1 (d9b756e)

- `[self]` APPROVE after one fix: search results (Pagefind sub-results) and other links target ids *inside* a step, such as the heading `#<anchor>-h`, not only the step anchor. Hash resolution now maps any contained id to its step (Addressing), and Phase C's deep-link test covers a heading hash.

- `[sol]` **REQUEST CHANGES** (gpt-6-sol). All five findings are folded into round 2:
  - resume is not recorded on navigation (now `py4kids:step`);
  - the status list has no event source (now `py4kids:check` and `py4kids:checklist`);
  - an `also_check` list must not count as passed;
  - print contradicts hiding (now a print rule, with a test);
  - the history mechanism must be explicit (links push; Previous / Next replace).
  It also named `acceptance.spec.ts` and `journey.spec.ts`.
- `[fable]` **REQUEST CHANGES**. All folded into round 2:
  - MAJOR: `before` blocks are group headers. They now form groups, with a kicker on every item and a grouped list.
  - MAJOR: the resume mechanism and the missing check event, as [sol] found.
  - MINOR:
    - closest-step hash resolution;
    - search hits on hidden items (sub-result anchors; the chrome is outside the Pagefind body);
    - push vs replace;
    - hidden-check silence ("checking…" plus a page live region);
    - the wide layout;
    - the named e2e files;
    - status as "any pass";
    - the logic in `src/lib/pager.ts`.
  - NIT, all taken:
    - item labels in the position text;
    - no double announcement (position text in the heading);
    - print;
    - the intro `<details>` open when short.

### Round 2 (8611624)

- `[fable]` **APPROVE WITH NITS**. Folded:
  - MINOR: the skip link and other unresolvable hashes no longer reset to item 1 after load.
  - MINOR: "checking…" needs start and terminal signals on every path (`check-start`, plus `check` with `error` and `stopped`).
  - MINOR: Previous / Next are buttons, disabled at the ends.
  - NITs, all taken: print `!important`; a group is a `before` block with a heading, and the kicker is a `<p>` taken from the heading text; no repeated Challenge tag; `py4kids:step` comes from the single show function.
- `[sol]` **REQUEST CHANGES** (gpt-6-sol). Both folded; each is the same as one of [fable]'s:
  - MAJOR: start and terminal check notifications, including unsaved failures, with a test.
  - MINOR: group only on an actual heading, keep other blocks with their item, and test a multi-block case.

### Round 3 (9a3a903)

- `[fable]` **APPROVE WITH NITS**. Both nits fixed: the Content Review section heading, deleted by the round-2 edit, is restored, and the fixture is named "Exercise 11".
- `[sol]` **REQUEST CHANGES** (gpt-6-sol). Folded:
  - MAJOR: `withStore` swallows save failures, so a terminal `pass` could show ✓ for an unrecorded pass. → Statuses are always re-derived from the store on each notification, and the event result only clears "checking…" and drives the announcement. A save-failure test is added. The stale "one notification" constraint and the Phase B summary are corrected.
  - MINOR: the Exercise 11 fixture is fixed, and the claim that every `before` block is a heading is removed.

### Round 4 (1013d94)

- `[fable]` **APPROVE WITH NITS**. Its nit is fixed: the save-failure test makes an *open* IndexedDB store's write reject, since making IndexedDB unavailable would fall back to memory, where the write succeeds.
- `[sol]` **REQUEST CHANGES** (gpt-6-sol). Folded:
  - MAJOR: a write rejected after the store opened was silent, because the unsaved-progress notice covers only a store that was not persistent at open. → `withStore` returns whether the write succeeded, and the terminal event carries `saved`. The item shows "Your result could not be saved on this device…", and the hidden announcement says "Passed, but not saved". The test is the write rejection on an open store.

### Round 5 (6dee031)

- `[fable]` **APPROVE WITH NITS**. Both nits fixed:
  - the round-record edit had split a Round 3 line and created a stray second Content Review heading; the records are rebuilt in order;
  - the duplicated hidden-item announcement sentence is merged.

- `[sol]` **REQUEST CHANGES** (gpt-6-sol). Folded:
  - MAJOR: the global constraint still limited `practice.ts` to notifications, contradicting the round-4 fix. → The constraint and Phase B now require the boolean `withStore` and the not-saved note in both the code-check and typed-answer paths, and the test covers both paths.
  - MINOR: the malformed record, already rebuilt in 0c29b02.


### Round 6 (808f4a4) — CONSENSUS

- `[self]` APPROVE.
- `[sol]` **APPROVE** (gpt-6-sol): no remaining findings.
- `[fable]` **APPROVE**: the plan is internally consistent, with no new problem.

## Content Review

### Review 1 (d1a2d5a) — CONSENSUS

- `[self]` APPROVE.
- `[sol]` **APPROVE WITH NITS** (gpt-6-sol). No blocking findings, and the three deviations are sound.
  Its caveat is recorded below: the phone-width axe check excludes the code editor, so it does not prove the whole page clean at phone width.
- `[fable]` **APPROVE WITH NITS**. Every plan rule holds in the code, every Phase C bullet has a test, and there are no regressions. Responses, all in `6ecf4ee`:
  1. `[FIXED]` (Should Fix) On wide screens, keyboard and screen-reader users tabbed through the whole list (up to 37 links) before reaching the exercise. → A "Skip to the exercise" link, visually hidden until focused, is now the nav's first child and moves focus to the current heading; an e2e test covers it.
  2. `[FIXED]` (Should Fix) The kicker repeated the heading directly above it on a group's first item. → The kicker is not rendered on a group's first item; the tests assert it on later items only.
  3. `[FIXED]` NIT: the position text ran into the heading. → It now reads ", 4 of 12".
  4. `[FIXED]` NIT: a control pressed before checks were ready leaked the position into the editor label. → Positions are added only once checks are ready.
  5. `[FIXED]` NIT: the intro threshold closed usaco-bronze checkpoint-04's rules. → `SHORT_INTRO` is 600; an e2e test covers it.
  6. `[FIXED]` NIT: wide print left an empty grid column. → The layout is `display: block` in print; the test asserts it at 1280 px.
  7. `[FIXED]` NIT: two announcements within 50 ms lost the first. → They are joined; an e2e test covers it.
  8. `[WONTFIX]` (follow-ups): kind-aware nouns ("All questions" on checkpoints, "problems" on projects); `before`-block headings have no ids, so a search hit there lands one item early; a junk hash at load is saved as the resume href, which is harmless because it resolves to item 1.
- The deviations were accepted by both reviewers:
  - test-file edits beyond the named list (`e2e-pwa/update.spec.ts`, `helpers/site.ts` `settle()`, `helpers/practice.ts` `check()`, which now waits on `py4kids:check` and fixes a pre-existing race);
  - "4 of 12" inserted by the island once checks are ready (`practice.ts` names editors from the heading text);
  - axe skips `.code-editor` at phone width.

## Post-Execution Report

**Shipped: practice pages show one exercise at a time, with Previous / Next and a grouped jump list.**

- **The pager:** a client-side pager (`site/src/scripts/practice-pager.ts`) over the unchanged static page. Every item stays in the DOM, and without JavaScript every item shows.
  - Each item is addressed by its anchor. Jump-list links push history; Previous / Next (buttons, disabled at the ends) replace it.
  - Inner ids (Pagefind heading sub-results) resolve to their step, and the skip link keeps the current step.
- **Groups and the list:**
  - Groups start at `before` headings ("Milestone 2", "Challenge — …").
  - Each later item in a group carries a kicker, and the list is grouped.
  - List statuses (✓ passed, • tried, "checking…") are always derived from the store (`site/src/lib/pager.ts`).
- **Events:** `py4kids:check-start`, a terminal `py4kids:check {key, result, saved}` from every exit path, `py4kids:checklist` and `py4kids:step`. The step event drives resume.
- **Saving:** `withStore` reports whether the write succeeded, and a failed save is shown on the item.
- **Presentation:**
  - A wide layout with a sticky side list; a `<details>` list at phone width.
  - A "Skip to the exercise" link.
  - Print shows every item.
  - Search hits on practice pages land on the matched exercise.
- **No change** to what is checked, how, or what is revealed; the CSP is unchanged.

**Verification:**

- Vitest: 426 tests.
- `e2e/pager.spec.ts`: 26 tests.
- Full `pnpm -C site e2e`: 159 site, site-sw and lighthouse tests, 23 PWA and 10 hooks, 0 failed.
- `astro check` and `tsc` clean.
- `scripts/ci-local.sh` solo on the final commit: see the PR.

**Follow-ups:**

- The code editor fails axe `scrollable-region-focusable` at phone width on every practice page (pre-existing; the CodeMirror scroller is not keyboard-focusable). A fix in `editor.ts` (e.g. `contentAttributes: { tabindex: '0' }`) needs its own plan.
- Kind-aware nouns in the pager chrome.
- Ids on `before`-block headings, for search.
- `e2e:live` uses the updated `check()` helper, so it passes only once this release is deployed.
- Redeploying learn.futurespark.cc needs the user's go-ahead.
