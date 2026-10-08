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
- **Message boundary (D7).** Only `postMessage` with a schema-validated envelope crosses (JSON Schema files in `runner/schema/`), and it is validated on both sides; anything else is dropped.
  - **Requests (site → runner):**
    - `{type: "run", id, session, code, stdin, files, check, budget_ms}`
    - `{type: "reset", id, session}`
    - `{type: "ping", id}`
    - `{type: "interrupt", id}` (the Stop button)
  - **Replies (runner → site):**
    - `{type: "result", id, session, stdout, stderr, results, timing, status}`
    - `{type: "ready" | "restarted", id}`
  - `session` is the lesson's entry id for lesson runs and a fresh unique id for each exercise check.
  - **Process-state isolation.** One Pyodide process shares `sys.modules`, standard-library module globals and `builtins` across namespaces, so a fresh namespace is not enough:
    - **Each exercise check runs in a fresh worker.** The runner keeps one prewarmed spare worker booted, so a check starts without waiting, then retires that worker after the check.
      - **Memory bound:** at most three Pyodide workers ever exist: the lesson worker, the one spare and the worker running a check. A retired worker is terminated before the next spare boots. A Playwright assertion checks the worker count.
    - **Each fixture case also runs in a fresh worker.** A reset inside one Python process cannot give fresh-process parity with `tools/judge.py`: in-place mutations survive, for example `sys.path.append` or the state of objects held by preloaded modules.
      - So a `fixtures` check runs case 1 in the spare worker and retires it, while the next spare boots in parallel, and so on.
      - The UI shows per-case progress.
      - Boot time is excluded from each case's budget.
      - Expected cost: about 1–1.5 s of boot per case on a desktop, so a 10-case item takes about 10–15 s.
      - The memory bound below still holds, because only one spare boots at a time.
    - **Lesson sessions** deliberately share one worker and its state, like the notebook kernel. "Reset" restarts that worker.
  - **Exact destinations:** every `postMessage` names its exact `targetOrigin`: the site posts to the runner origin, and the runner posts to the site origin. Never `*`. If the iframe has been navigated elsewhere, the browser drops the message, so student code cannot reach another page.
  - **Binding** (all required, each tested):
    - The site accepts a message only if `event.origin` equals the runner origin, `event.source === iframe.contentWindow`, and `id` matches a pending request (a reply for an unknown or completed id is dropped).
    - The runner accepts a message only if `event.origin` equals the site origin and `event.source === window.parent`.
- **Headers (D7).**
  - Both origins send `Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Embedder-Policy: require-corp`, so `crossOriginIsolated` is true and `SharedArrayBuffer` interrupts work.
  - Under the site's COEP, a cross-origin iframe must opt in, so **every runner response (the document, the worker script and the Pyodide files) also sends `Cross-Origin-Resource-Policy: cross-origin`**. Tests confirm that the iframe loads under the site's COEP, and that `self.crossOriginIsolated` is true inside the runner page and its worker.
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
- **Pyodide version: 0.27.8** (CPython 3.12), matching the CI interpreter (Python 3.12.12, the repo's `requires-python` floor), so the CPython parity tests compare like with like. The runner's About line shows the Python version.
  - The CI interpreter is pinned (`.python-version` set to `3.12`). The parity test asserts that the CPython minor and Pyodide's agree, so the pin cannot drift silently.
- **The Python side of the worker** (`runner/py/harness.py`, loaded into Pyodide). Per request it:
  - sets up stdin (an `io.StringIO`; `input()` reads from it, and EOF raises `EOFError` as in CPython; the contest code uses `sys.stdin.read*` (407 uses) and `input()` (229); `open(0)` and `stdin.buffer` do not occur)
  - **working directory:** one per `session`, so a lesson keeps the files its cells write (python-projects unit 09 writes a save file and reads it later); "Reset" recreates it. Each check gets a fresh directory. The mounted `files` are written there.
  - **turtle:** installs the `fake_turtle` port as `turtle` for **every** run whose source imports turtle (`imports_turtle`), because Pyodide ships no tkinter; the turtle rule applies only to items with `turtle: true`
  - **per fixture case:** a fresh worker (see Process-state isolation); empty stdout is reported as "no output", as `tools/judge.py` does
  - captures stdout and stderr
  - for `fixtures`, runs the program once per case in a fresh namespace and compares with `outputs_match` (line-exact for `acsl` books, token-based otherwise), ported verbatim from `tools/judge.py`
  - for `asserts`, runs the student's code, then each shipped assert in that namespace separately, catching `AssertionError` and other errors per assert, and reports pass/fail per assert (never the source)
  - for turtle items, installs `fake_turtle` (the browser port of `tools/fake_turtle.py`) as `turtle` and applies the three-part rule: at least one pen-down move; fewer than 10,000 moves; a closed path unless `# turtle-check: open-path`. It returns the segments, so the site can draw them.
- **Hashing checks** (`answer`, `predict`, `expected-output`) run in the **site**, with no student code needed: the site normalises the typed answer, or for `expected-output` the runner's stdout of the student's program, with part B's `normalise.ts` (now covering `aliases` and `whitespace`), then compares `answerHash` with `check.hash`. For `expected-output`, the runner runs the student's code; the site compares the stdout hash.
- **Interrupts are owned by the runner origin.** A `SharedArrayBuffer` cannot be posted across origins (agent clusters are keyed by origin under cross-origin isolation), so the **runner page** allocates it, hands it to its same-origin worker (`pyodide.setInterruptBuffer`), and owns the budget timer from `budget_ms`.
  - On expiry, the runner page sets the buffer: Pyodide raises `KeyboardInterrupt`, reported as "time limit".
  - **Hard limit:** the interrupt is catchable (a student's `try/except KeyboardInterrupt` or signal handler can swallow it), so if the worker has not returned within a 1 s grace period after the interrupt, the runner page **terminates and restarts the worker**. The result reports `interrupts: "restart"`, and a lesson session is lost (the UI says so).
  - If the runner page's `crossOriginIsolated` is false, it terminates and restarts the worker instead.
  - Every result carries `interrupts: "sab" | "restart"`, so the UI can honestly show "restarting Python (≈N s)".
  - The site may also send `{type: "interrupt", id}` (a Stop button).
- **Budgets:** the per-test-case budget is max(1 s, 10× the reference solver's CPython time), capped at 10 s; other runs get 5 s.
  - The **site** computes the budget from `check.cpu_ms`, a schema addition holding the CPython time rounded to 100 ms and clamped.
  - The measurements are cached in a committed `tools/export/timings/<book>.json`, so export stays deterministic and fast and the `content_hash` never depends on machine jitter. The cache is refreshed only by an explicit `--measure` export flag.
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
  - **The code editor under the CSP:** CodeMirror 6, self-hosted, prefilled with the Starter.
    - CodeMirror injects its theme through `style-mod`, which creates a `<style>` element for a `Document` root (blocked by `style-src 'self'`) and uses constructable stylesheets (`adoptedStyleSheets`, CSSOM, which CSP does not govern) only for a `ShadowRoot`.
    - So **each editor mounts in a shadow root** (`new EditorView({root: shadowRoot, parent: …})`). Its runtime `element.style` assignments are also CSSOM.
    - Phase B must prove this with a **zero-violation editor test** (open, type, scroll, highlight, under the served CSP).
    - If any violation remains, the editor falls back to an accessible plain `<textarea>` with Tab inserting four spaces (Escape then Tab leaves the field). The test decides which one ships.
  - The practice page gains Check controls per kind: answer and predict boxes, with the hint from `answer_format`; per-case and per-assert results; the sample-only reveal; `also_check` checklists; the turtle drawing; and odd-answer gating.
  - The reading view gains Run, Reset and stdin boxes. A block whose probe status is `mismatch` (unseeded randomness) labels its stored output "may differ when you run it".
  - Fixture files are fetched lazily, per item, when Check is pressed, never all of `files/` on page load (the Lighthouse budget).
  - Results write D11 events, and attempts go to the attempt store.
- **Phase C: export additions.** `check.cpu_ms` per fixtures item, read from the committed timing cache (`export --measure` refreshes it with `tools/judge.py`'s runner), and `answer_figures` for odd answers whose program draws with turtle. Schema and answer-model updates (`answer_figures` is tied: regenerated and compared, like lesson figures).
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
    - a valid-looking message from **another window on the allowed origin** (a second iframe or a popup) is ignored
    - a reply with an unknown id is dropped
    - an invalid envelope is dropped
    - the iframe loads under the site's COEP, and `crossOriginIsolated` is true in the site, the runner page and the worker
  - **Sessions:**
    - reset clears a lesson session
    - after a forced worker restart, the next run replays the prelude and gives the stored output
    - two exercise checks never share variables
    - **contamination through modules:** check 1 sets `math.pi = 3`, `builtins.print = None` and `sys.path.append("x")`, and seeds `random`; check 2 sees the original values. The same test runs between two fixture cases of one item (fixture case 1 mutates; case 2 checks `math.pi`, `print` and `sys.path`).
  - **Grading UI, one test per behaviour:**
    - `fixtures` in both matching modes: an acsl item line-exact (a required `15 10 4` on one line rejects `15\n10\n4`), a usaco item token-based, with CPython parity for both cases taken from `tools/judge.py`'s `outputs_match`
    - a skipped over-budget case is listed (a fixture with a forced tiny budget)
    - the sample-only reveal: the sample's input and expected output are shown, and no other case's `.out` is in the DOM
    - `expected-output`: the student's program runs, and a correct one passes by hash while a wrong one fails
    - `predict`: a typed correct answer passes, and a wrong one fails
    - `answer` with `aliases` (`^`) and with `whitespace: exact`
    - `self-check`: a checklist with no automatic verdict, and the "cannot check this" notice
    - `also_check` shown beside an automatic check
    - the turtle rule
  - **Gating:** an odd exercise's `answer_md` is absent from the DOM before an attempt, still absent after merely opening the editor, and present after **a failed Check**. An even exercise never shows it.
    - **For an odd `self-check` item** (63 in python-projects), an attempt is a Run of the student's code plus marking the checklist done; the test covers one.
  - **Interrupt path proven:** the hang test asserts `interrupts: "sab"` under the served headers, and `"restart"` with isolation disabled.
    - Code that catches the interrupt (`while True:` around `try: … except KeyboardInterrupt: pass`) is stopped by the grace-period restart within budget + 1 s + restart time.
  - **Navigation:** the test navigates the runner iframe to another local origin, then presses Run. No code is delivered (the target page records nothing), and the site shows the runner as unavailable and offers a reload.
  - **CSP on both origins:** zero `securitypolicyviolation` events on the practice page with the editor open, typed in and scrolled, and on the runner page while Pyodide loads and runs.
  - **No network:** part B's request-recording test is extended to the runner origin. Only the two local origins appear, and no request carries code or answers.
  - The part B end-to-end, axe and Lighthouse suites still pass.
  - `scripts/ci-local.sh` runs solo on the final commit.

## Out of scope

- The PWA, offline caching of both origins and the public deploy (part D).
- Accounts (E); the LLM (F).
- Running recsys.

## Plan Review

### Round 1 (c05bab9)

- `[sol]` **REJECT** (gpt-6-sol):
  - `[FIXED]` COEP would block the runner iframe: every runner response now sends `Cross-Origin-Resource-Policy: cross-origin`, tested.
  - `[FIXED]` The envelope had no session: typed `run`/`reset`/`ping`/`result`/`ready`/`restarted` messages, with session tests including a restart.
  - `[FIXED]` CodeMirror vs the CSP: style-mod's constructable stylesheets, a zero-violation editor test, and an accessible textarea fallback.
  - `[FIXED]` Replies are bound by `event.source` and pending ids on both sides; a same-origin foreign window is tested.
  - `[FIXED]` Grading UI tests for every kind and both matching modes, the skipped case, sample-only reveal and gating after a failed Check.

- `[fable]` **REJECT** (round 1, c05bab9):
  - `[FIXED]` A `SharedArrayBuffer` cannot cross origins: the runner page owns the buffer and the budget timer, and results report `interrupts: sab|restart`, which is tested.
  - `[FIXED]` CodeMirror's `style-mod` uses a `<style>` element on a Document: each editor now mounts in a shadow root (constructable stylesheets), and zero-violation tests run on the editor page and the runner page. This corrects my round-2 fold for [sol] 3, which wrongly said Document roots use `adoptedStyleSheets`.
  - `[FIXED]` (nits)
    - one working directory per session
    - the turtle stub installed for every turtle import
    - an "attempt" defined for odd self-check items, with a test
    - `cpu_ms` from a committed timing cache, so bundles stay deterministic
    - Pyodide pinned to the CI CPython minor
    - `mismatch` outputs labelled "may differ"
    - harness parity details: drain per case, clear `sys.modules`, "no output"
    - lazy fixture fetching

- `[fable]` **APPROVE WITH NITS** (round 2, 27989c5): both blockers and all nits are folded faithfully, and the [sol] folds are consistent.
  - `[FIXED]` `interrupt` added to the typed requests.
  - `[FIXED]` Pyodide pinned at 0.27.8 (CPython 3.12).
  - `[FIXED]` The timing cache moved to `tools/export/timings/`.

- `[sol]` **REJECT** (round 2, 27989c5):
  - `[FIXED]` Outbound messages lacked an exact `targetOrigin`: it is now exact in both directions, with a navigation test.
  - `[FIXED]` A SharedArrayBuffer interrupt is catchable: a 1 s grace period, then terminate and restart, tested with code that catches the interrupt.
  - `[FIXED]` Fresh sessions shared process state: a fresh prewarmed worker per check, a boot-state reset between fixture cases, and module and builtins contamination tests.
  - `[FIXED]` (nit) `interrupt` is in the request schema (0e56d8e).

- `[fable]` **APPROVE WITH NITS** (round 3, e1064cf): the [sol] folds are sound.
  - `[FIXED]` Boot-imported modules: their `__dict__` is now restored, so the `math.pi` test proves it.
  - `[FIXED]` At most three workers, asserted.
  - `[FIXED]` The CI interpreter is pinned, and the parity test checks that the minors agree.

- `[sol]` **REJECT** (round 3, e1064cf): `[FIXED]` A reset inside one process cannot reach fresh-process parity (`sys.path` and preloaded-module mutations survive). Every fixture case now runs in a fresh worker (spare booted in parallel, boot time outside the budget), with a contamination test between cases covering `math.pi`, `print`, `sys.path` and `random`.

## Content Review

## Post-Execution Report
