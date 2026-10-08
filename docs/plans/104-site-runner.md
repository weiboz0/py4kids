# Plan 104 — Learning website, part C: the isolated runner and checks

**Goal:** Students run Python in the browser, inside an isolated runner, and get honest feedback on every checkable item. The site gains:
- **"Run"** on lesson code, with cumulative lesson state, prelude replay, mounted asset files and input boxes for `input()`
- **"Check"** for every check kind: `fixtures`, `answer`, `asserts`, `expected-output`, `predict`, `self-check`, plus the turtle rule
- **answer gating:** odd unit exercises reveal their Student Book answer after a genuine attempt

No code, answer or result leaves the device.

**Spec:** design 012 D4, D5, D6 (runnable reading view), D7, D9, D11, §3 "Runner acceptance" and "Reference solvers".
It builds on part A (plan 101, merged) and part B (plan 103, which must merge first), and uses plan 102's metadata (`also_check`, `answer_format.aliases` and `whitespace`).
User goal, 2026-10-06: "non stop until full working learning website".

## Global constraints

- **Isolation (D7).**
  - Student code runs only in a **separate runner origin**: in development, `http://localhost:<runner port>`, a different port and so a different origin; in production, `run.<site>`.
  - It runs inside a sandboxed `<iframe sandbox="allow-scripts allow-same-origin" allow="cross-origin-isolated">` that holds a Web Worker running Pyodide.
  - The runner origin has no access to the site's storage. The site never runs student code itself.
- **Message boundary (D7).** Only `postMessage` with a schema-validated envelope crosses, and it is validated on both sides; anything else is dropped.
  - The site sends `{id, code, stdin, files, check, budget_ms}`.
  - The runner returns `{id, stdout, stderr, results, timing, status}`.
  - Both sides check `event.origin` against the configured counterpart origin.
- **Headers (D7).**
  - Both origins send `Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Embedder-Policy: require-corp`, so `crossOriginIsolated` is true and `SharedArrayBuffer` interrupts work.
  - The site CSP adds `frame-src <runner origin>`.
  - The runner origin has its own strict CSP: `script-src 'self' 'wasm-unsafe-eval'`, `connect-src 'self'` for Pyodide's own files, and `frame-ancestors <site origin>`.
- **Self-hosted Pyodide (D9).** The Pyodide runtime (pinned version, from the `pyodide` npm package) is copied into the runner build. Nothing loads from a CDN, and no extra packages are installed at runtime: the books use only the standard library, plus turtle, which the browser port of `fake_turtle` provides.
- **Hidden answers stay hidden (D5).**
  - Checks compare by hash (`answer`, `predict`, `expected-output`), run the shipped asserts or fixtures, and report pass/fail.
  - Assert source is never displayed.
  - Only the sample fixture's input and expected output are shown.
  - `answer_md` is rendered only for `answer_visibility: after-attempt` items, and only after an attempt (one Check run, or one submitted answer).
- **Honesty.**
  - A `self-check` item says plainly that the site cannot check it.
  - `also_check` requirements always show as a self-check list beside an automatic check.
  - A skipped fixture (over budget) is listed, never silent.
  - A worker restart shows its cost.
- **Progress (D11).**
  - Part C writes `lesson-run`, `exercise`, `checkpoint`, `project` and `self-check` events with `detail.cases` (pass/fail per test case) or `detail.checklist`.
  - Code and answers go to the on-device attempt store only, never into an event.

## Architecture

- **`runner/`** (new, a sibling of `site/`): a tiny static app with the same toolchain (Node 24, pnpm lockfile).
  - `runner/index.html` is the iframe page.
  - `runner/src/worker.ts` loads Pyodide, keeps one namespace per `session` (a lesson), and executes requests.
  - It builds to `runner/dist/` with its own `_headers`.
- **The Python side of the worker** (`runner/py/harness.py`, loaded into Pyodide). Per request it:
  - sets up stdin (an `io.StringIO`; `input()` reads from it, and EOF raises `EOFError` as in CPython)
  - writes the mounted `files` into a per-request directory and `chdir`s there
  - captures stdout and stderr
  - for `fixtures`, runs the program once per case in a fresh namespace and compares with `outputs_match` (line-exact for `acsl` books, token-based otherwise), ported verbatim from `tools/judge.py`
  - for `asserts`, runs the student's code, then each shipped assert in that namespace separately, catching `AssertionError` and other errors per assert, and reports pass/fail per assert (never the source)
  - for turtle items, installs `fake_turtle` (the browser port of `tools/fake_turtle.py`) as `turtle` and applies the three-part rule: at least one pen-down move; fewer than 10,000 moves; a closed path unless `# turtle-check: open-path`. It returns the segments, so the site can draw them.
- **Hashing checks** (`answer`, `predict`, `expected-output`) run in the **site**, with no student code needed: the site normalises the typed answer, or for `expected-output` the runner's stdout of the student's program, with part B's `normalise.ts` (now covering `aliases` and `whitespace`), then compares `answerHash` with `check.hash`. For `expected-output`, the runner runs the student's code; the site compares the stdout hash.
- **Interrupts:** the site allocates a `SharedArrayBuffer` interrupt buffer and passes it to Pyodide's `setInterruptBuffer`.
  - On budget expiry, the site sets the buffer: Pyodide raises `KeyboardInterrupt`, reported as "time limit".
  - If `crossOriginIsolated` is false, the site terminates and restarts the worker instead and shows "restarting Python (≈N s)".
- **Budgets:** the per-test-case budget starts at max(1 s, 10× the CPython time measured by `tools/judge.py` for the reference solver), capped at 10 s. It is exported per fixtures item as `check.budget_ms` (a schema addition, computed at export from the reference solver's measured time). Other runs get 5 s.
- **Cumulative lesson state (D6):** "Run" on a lesson block sends the block code with `session = <entry id>`.
  - The first run of a block whose probe says `prelude` first replays its `prelude` blocks, silently, in that session.
  - "Reset" clears the session.
  - Input boxes: a `tryit` block that calls `input()` shows a stdin textarea before Run.
- **Odd answers after an attempt:** the site records the attempt in the attempt store and then renders `answer_md` with part B's Markdown pipeline. Its `{=latex}` TikZ figures are dropped, and an odd turtle answer's drawing comes instead from a new `answer_figures` field (segments from `turtle_segments`, added at export in Phase C), drawn with part B's turtle SVG.

## Phases

- **Phase A: the runner app and harness.**
  - `runner/` scaffold, Pyodide self-hosted, `worker.ts`, `harness.py`, `fake_turtle` browser port, the message envelope with validation on both sides, origin checks, interrupts and restart.
  - `scripts/build-site.sh` builds both apps.
  - `site/scripts/serve.mjs` serves both dists on two ports with their `_headers`.
- **Phase B: check UIs and gating in the site.**
  - The practice page gains Check controls per kind: a code editor (CodeMirror 6, self-hosted, no inline styles) prefilled with the Starter; answer and predict boxes, with the hint from `answer_format`; per-case and per-assert results; the sample-only reveal; `also_check` checklists; the turtle drawing; and odd-answer gating.
  - The reading view gains Run, Reset and stdin boxes.
  - Results write D11 events, and attempts go to the attempt store.
- **Phase C: export additions.** `check.budget_ms` per fixtures item, measured with `tools/judge.py`'s runner at export (deterministic: rounded to 100 ms and capped), and `answer_figures` for odd answers whose program draws with turtle. Schema and answer-model updates (`answer_figures` is tied: regenerated and compared, like lesson figures).
- **Phase D: verification (named verification phase), in a headless browser in CI.**
  - **Runner acceptance:** one Playwright test per row of design 012 §3, each named:
    - stdin programs, including `input()` at end of input (`EOFError`, as in CPython)
    - an interrupt on a hang (`while True: pass` stops within budget + 1 s), and the restart path, with isolation disabled
    - recursion depth and float formatting against CPython: 20 fixed expressions whose CPython output is recorded at test time
    - function-assert isolation: one failing assert does not stop the others, and the source never appears in the DOM
    - short-answer hashing and normalisation against every `hash_vectors.json` vector, through the UI
    - turtle directives: closed, open-path, no pen-down, too many moves
    - mounted asset files read by a lesson cell
    - cumulative lesson state, with prelude replay
  - **Reference solvers:** every reference solver (`assets/{l,ex,q,p}N.py` in usaco-bronze and acsl) runs in Pyodide against all its fixtures, and every result equals `tools/judge.py`'s. This is a slow-marked test run in `ci-local`. The solvers are read from the repo at test time and never shipped.
  - **Isolation:**
    - the runner iframe cannot read the site's IndexedDB or localStorage
    - a message from a wrong origin is ignored
    - an invalid envelope is dropped
    - `crossOriginIsolated` is true under the served headers
  - **Gating:** an odd exercise's `answer_md` is absent from the DOM before an attempt and present after one; an even exercise never shows it.
  - **No network:** part B's request-recording test is extended to the runner origin. Only the two local origins appear, and no request carries code or answers.
  - The part B end-to-end, axe and Lighthouse suites still pass.
  - `scripts/ci-local.sh` runs solo on the final commit.

## Out of scope

- The PWA, offline caching of both origins and the public deploy (part D).
- Accounts (E); the LLM (F).
- Running recsys.

## Plan Review

## Content Review

## Post-Execution Report
