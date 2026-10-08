# Plan 105 — Learning website, part D: installable offline app and deploy

**Goal:** The site becomes an installable PWA.
"Download this book" makes a whole book, including running and checking code, work with the network off.
Progress can be exported and imported as a file.
Everything is ready to deploy both origins (site and runner) to Cloudflare Pages from a release tag.
**The first public deploy runs only after the user confirms and provides the hosting account** (outward-facing; AGENTS.md hard safeguard).

**Spec:** design 012 D1 (Cloudflare Pages, release tags), D9, D10, D11 ("export my progress"), §3 "an offline test that runs code and checks an exercise".
It builds on parts A–C (plans 101, 103, 104; 104 must merge first).
User goal, 2026-10-06: "non stop until full working learning website".

## Global constraints

- **Same site.** The runner origin must be a **subdomain of the site's registrable domain** (`run.<domain>`, as D7 says), so the two are same-site. Otherwise:
  - WebKit refuses service-worker registration in a cross-site iframe
  - Chrome and Firefox partition a cross-site iframe's Cache Storage and IndexedDB by top-level site
  - `persist()` from an iframe resolves `false`

  Consequences:
  - `*.pages.dev` is on the Public Suffix List, so the default Pages preview URLs (`py4kids.pages.dev`, `py4kids-run.pages.dev`) are cross-site and **cannot verify the offline runner**. Production needs a custom domain; the README says so.
  - `deploy/origins.json` validation rejects a runner origin that is not a subdomain of the site's registrable domain.
  - **Persistence:** `navigator.storage.persist()` is called from the top-level site inside the "download this book" click (Firefox prompts; calling it on load is noise). The runner's own result is informational. Both are shown.

- **One service worker per origin (D10):**
  - The site's worker caches the site's pages and assets.
  - The runner's worker caches the runner page, its worker script, the pinned Pyodide runtime and the book's fixture and asset files.
  - The site asks the runner to precache through the existing message channel, with a new typed request `{type: "precache", id, book, files}` and reply `{type: "precached", id, ok, bytes}`, validated as in part C.
- **Offline status:**
  - The site shows "available offline" for a book only after both caches confirm.
  - Both origins' persistence results are shown, following the Same site rule: `persist()` is called from the top-level site inside the download gesture, and the runner's result is informational.
  - The site explains that some browsers (Safari) can clear storage after long disuse, and offers "export my progress".
- **Privacy is unchanged:**
  - The service workers make no requests beyond the files the user asked to cache.
  - There are no push notifications, background sync or analytics.
  - **Service-worker requests are recorded too.** Requests made by a service worker do not reach `page.on('request')`, so the tests record at context level (`browserContext.on('request')`, with Playwright's service-worker network events enabled) on both origins. Every request during browsing, precache and update must be on the allowlist: the files the user asked to cache, or the release's own files. Each one is a body-less GET.
- **Release identity and updates.**
  - **`release_id`** (no circularity): the build computes it as a sha256 over the sorted `(path, sha256(bytes))` list of every file in `site/dist/` and `runner/dist/`, the Pyodide runtime included, **except the one generated file that carries the id**: `release.json`, in each dist.
    - No other file embeds the id. The service-worker scripts are byte-identical across releases unless their code changed; each page registers its worker as `/sw.js?r=<release_id>`, read from `/release.json` fetched with `cache: "no-store"`, so a new id is a new script URL and the browser installs the new worker. If that fetch fails (offline, servers down), the page keeps the current registration: no error and no banner.
      - It is the **one network request the offline contract allows**: at most one `GET /release.json` per document load **on each origin** (the site page and its runner iframe each make their own update check), each failing without a console error. Phase E's offline steps assert this exactly.
    - A test rebuilds unchanged inputs and gets the same id, recomputes the id from the emitted files to match `release.json`, and changes one runner file to get a different id.
  - **Cache names**, three kinds per origin:
    - app shell: `shell-<release_id>`
    - the Pyodide runtime: `pyodide-0.27.8`, keyed by version and shared by all books
    - book content: `book-<book>-<content_hash>`
  - An update replaces the shell cache. It keeps the Pyodide cache unless the version changed. A downloaded book is marked "needs update", and its old cache is deleted **only after the new precache completes**, so a downloaded book never disappears offline.
  - Version skew between site B and runner A is caught by part C's envelope schema version: the site asks for a reload.
  - **Precache requests** carry `release_id`, and the runner refuses a mismatched one.
  - **Confirmation is a record, not cache existence.**
    - Each origin stores `{book, content_hash, release_id}` confirmed records (site: IndexedDB; runner: its own store).
    - Book files are fetched **in chunks** into the final `book-<book>-<content_hash>` cache, which feeds the progress bar, and the record is written **only at the end**. On worker start, any `book-*` cache without a confirmed record is deleted. That keeps all-or-nothing atomicity without one huge `addAll`.
    - "Available offline" means both origins hold confirmed records for the book with the same `release_id`.
  - **`activate` deletes no cache.** The B-page cleanup (below) is the only deletion path for `shell-*` and `pyodide-*`; `book-*` follows the confirmed-record rule. On an update where a book's `content_hash` is unchanged, "re-download" is a manifest verification (every listed URL is present in the cache) that re-stamps the record with the new `release_id`, not a refetch. A changed `content_hash` downloads into a new cache and deletes the old one after confirmation.
  - **Activation is user-controlled, page-mediated and safe for every open page.**
    - A new worker on each origin stays *waiting* (no `skipWaiting` on install). Each open A page keeps running on A's shell and Pyodide caches, including booting **fresh exercise workers** from them.
    - **Handshake**, when the user accepts "a new version is available — reload" (offered only when this page is the site's only client; otherwise "close your other py4kids tabs to update"):
      1. The site page messages its runner iframe `{type: "prepare-activate", release_id}`.
      2. The runner page tells its waiting worker to `skipWaiting`, waits for its own `controllerchange`, and replies `{type: "runner-activated", release_id}`.
      3. The site page then tells the site's waiting worker to `skipWaiting`.
      4. On the site's `controllerchange`, the page reloads.

      Each step has a **10 s timeout**.
    - **Forward-only recovery.** A service worker cannot be rolled back once it activates, so recovery completes the update instead of undoing it.
      - **Before step 2 succeeds:** a failure leaves both origins on A, and the page says "update failed — try again".
      - **After the runner activated, before the site did** (runner B, site A): the page says "finishing the update…" and retries step 3, which is idempotent. Meanwhile the page keeps working, because the runner's B worker still accepts the previous envelope schema version. Each runner release is required to support version N−1, which a test enforces.
      - **After the site activated, before the reload:** the page is already controlled by B and is served A's files (see below), so it keeps working until the reload, which is retried.
      - A's caches are kept through every recovery path.
    - **No cache is deleted in `activate`.** Between activation and the reload, the old A page (and its iframe) is controlled by the B workers, which serve it **A's** files. Two rules make this unambiguous:
      - **Every asset URL is release-specific:** content-hashed filenames for all site and runner assets, the runner page's `worker.js` included, and Pyodide under a versioned path (`/pyodide/0.27.8/…`). Only the HTML entry pages and `release.json` keep stable names.
      - **Immutable URLs are served from any retained cache.** Because every asset URL is content-hashed or versioned, an exact URL identifies exactly one file, so the worker serves it by exact match from any retained `shell-*` or `pyodide-*` cache. That holds whoever requests it, including dedicated workers, which are separate service-worker clients without the page's client id. No client-to-release mapping is needed.
      - The only stable-named URLs are HTML entry pages (a navigation gets the current release) and `release.json` (network only, see below).
    - **Cleanup** runs later: a page loaded under B asks its worker to clean up, and the worker deletes non-current `shell-*` and `pyodide-*` caches only when `clients.matchAll()` shows no client still running an A page (each page reports its `release_id`). `book-*` caches follow the confirmed-record rule.
  - Downloaded books are re-downloaded for the new release in the background, and their status reads "updating" until confirmed.
- **Size and count.**
  - Per-book downloads, measured on real bundles:
    - usaco-bronze: about 8.6 MB of book files, 1,358 files
    - acsl: 5.3 MB, 927 files
    - python-concepts: 1.6 MB
    - python-projects: 1 MB
    - plus Pyodide 0.27.8 (about 14–17 MB, once), the runner shell and the rendered pages
  - **The build-time manifest:** each book's carries its `bytes` and `count`, and includes the hashed `_astro/*` assets its pages import and the Pagefind index chunks for the book (search works offline).
  - **The UI:** "download this book" shows the size first, then a progress bar.
  - **The site worker:** it normalises navigations (`/x/` → `/x/index.html`).
- **Hidden answers stay hidden:** caching copies only files already in `dist/`. The part B and C leak tests are rerun on the cached file list.

## Phases

- **Phase A: site PWA.**
  - Contents:
    - `manifest.webmanifest` (name, icons generated locally from an SVG, theme colours, `display: standalone`)
    - the site service worker (`site/src/sw.ts`, hand-written: no Workbox or CDN): an app shell plus pages cached on demand, and "download this book", which precaches every page and data file of that book from a build-time manifest
    - the install prompt
    - the offline banner
- **Phase B: runner PWA.**
  - Contents:
    - the runner service worker (`runner/src/sw.ts`), which precaches the runner shell and Pyodide on first use and the book's fixtures and assets on `precache`
    - COOP/COEP/CORP headers preserved on cached responses, so `crossOriginIsolated` holds offline:
      - Responses are **cloned, not rebuilt**: `new Response(cached.body, cached)` keeps `Content-Type: application/wasm`, which `instantiateStreaming` needs; the worker then sets the three isolation headers on the clone.
      - The `_headers` `/*` rule also covers `/sw.js`, because Chrome checks a service-worker script's COEP against a COEP document.
  - Test: offline, `crossOriginIsolated` is still true in the runner and its worker.
- **Phase C: export and import progress.**
  - "Export my progress" writes a JSON file of D11 events plus Leitner state and resume positions. It contains no attempt store (code stays on the device unless the user exports attempts separately, with a clear label).
  - **Deterministic import merge**, after validating the file against the schemas:
    - **events:** union by `event_id`
    - **cards:** per card key, keep the record with the later `updated_at` (every card record now stores `updated_at`); a tie keeps the local record
    - **resume:** per book, the later `updated_at`
    - an unknown `schema` is rejected, and the file size is bounded (≤ 20 MB)
  - **Export on iOS installed PWAs:** use `showSaveFilePicker` where present, and the Web Share API as the fallback.
  - Importing the same file twice changes nothing after the first import. Importing an older file never regresses newer local state.
  - Tests:
    - export → clear storage → import restores the mastery map and resume
    - importing the same file twice into an **existing, newer** store leaves it byte-for-byte unchanged (event count, card boxes, resume)
    - importing an older export keeps the newer card boxes
    - a malformed file is rejected with a message
- **Phase D: deploy configuration (no deploy).**
  - Contents:
    - **Pages projects:** `deploy/README.md`, `deploy/site/wrangler.toml` and `deploy/runner/wrangler.toml`. Wrangler's Pages config is one project per file: `py4kids` for the site, `py4kids-run` for the runner, with custom domains `<domain>` and `run.<domain>`.
      - Cloudflare serves `.wasm` as `application/wasm` and supports COOP/COEP/CORP in `_headers`.
      - The build fails if any file exceeds Pages' 25 MiB limit (`pyodide.asm.wasm` is checked).
      - Preview origins are listed in `origins.json` too, or `frame-src` / `frame-ancestors` would block previews; previews are for reading only (see Same site).
    - **Build:** `scripts/build-release.sh <tag>` builds both apps with `--release <tag>`, so the PDF links point at that GitHub Release, and runs the full site test suite
    - **Domains:** the production origins are configured in one place (`deploy/origins.json`) and read by the site (runner origin, CSP `frame-src`) and the runner (`frame-ancestors`, `targetOrigin`)
  - Test: a preview build with two local origins standing in for production passes the whole suite.
  - **No `wrangler deploy` runs in this plan.**
- **Phase E: verification (named verification phase).**
  - **Offline end-to-end, per book:**
    1. online, open the book and press "download this book"; wait for "available offline"
    2. **stop both local servers** (`serve.mjs` for the site and for the runner); `setOffline` alone is not trusted, because service-worker fetches escape page-level emulation. Then reload, recording requests at context level. After the servers are down, the only requests allowed are **at most one failed `GET /release.json` per document load on each origin** (the update checks). Zero others, and no console error
    3. read a lesson, run a lesson cell, check one exercise of each kind the book has (a `fixtures` item included: every case boots a fresh worker from the cached Pyodide), and answer a card
    4. **rerun the hang test offline** and assert `interrupts: "sab"`, the end-to-end proof that the isolation headers survived the cache
    5. reload again offline: progress persists

    This is the D10 test design 012 §3 requires: it runs code and checks an exercise, not only reads.
  - **Update path:**
    1. build release A, download a book and open a lesson
    2. deploy release B (changing only runner code, so the bundle hash is unchanged but `release_id` differs)
    3. the open lesson keeps running and checking code on A's caches (a **fresh exercise worker boots** during the pending update), and the prompt appears; with a second A tab open, accepting asks to close it, and B stays waiting
    4. **the activation interval:** release B changes the runner's `worker.js` and moves Pyodide to a new versioned path, so serving the wrong release's file would be observed as a failure, not hidden by identical bytes. The test pauses the handshake after the runner and site workers have activated but before the reload. The A page must still run a lesson cell and check a fixtures item (fresh workers loading A's runner and Pyodide files from the retained caches), on both origins, with zero network requests and no 404. A's caches still exist then
    5. after the reload under B, cleanup deletes A's shell and Pyodide caches
    6. **failure at each step:**
       - the runner step forced to time out leaves both origins on A
       - the site step forced to fail after the runner activated leaves runner B and site A: the page keeps running and checking code (the N−1 envelope), and the retry completes the update
       - a failure after the site activated, before the reload, leaves a working page and the reload completes it
       - A's caches exist throughout
    7. B is active, and A's shell cache is gone; the book (unchanged `content_hash`) is verified and re-confirmed under B without refetching; a second scenario with changed content downloads the book into a new cache and removes the old one only after confirmation; a download **interrupted** or **failed** midway (the server stopped during the chunks) leaves A's book cache and confirmed record intact, and the partial new cache is swept on the next worker start
  - **Requests:** the no-network and request-recording suites with the service workers active.
  - **Accessibility and performance:** Lighthouse PWA installability checks, and axe on the new UI.
  - The parts B and C suites still pass.
  - `scripts/ci-local.sh` runs solo on the final commit.
- **Phase F: first public deploy (gated on the user).**
  - After the merge, the session asks the user to confirm the deploy and to provide the Cloudflare account and API token (kept in `.env`, never committed) and the two domains. Only then does it run `scripts/build-release.sh`, `wrangler pages deploy` for both projects, and a post-deploy smoke test against the real origins: headers, `crossOriginIsolated`, a lesson run, an exercise check, offline download.
  - It records the result in `output/README.md`.

## Out of scope

- Native app-store wrappers (deferred, D10).
- Accounts and sync (part E); the LLM (part F).
- Any deploy without explicit user confirmation.

## Plan Review

### Round 1 (8a4d3e6)

- `[sol]` **REJECT** (gpt-6-sol):
  - `[FIXED]` Release identity: a `release_id` over both origins' complete assets, versioned cache names, the id bound to precache, confirmation only when fully populated, user-controlled activation, and an update test with an open lesson.
  - `[FIXED]` Service-worker requests recorded at context level against an allowlist, during browsing, precache and update.
  - `[FIXED]` Deterministic import merge for cards (`updated_at`) and resume, with re-import and older-file tests.

- `[fable]` **REJECT** (round 1, 8a4d3e6):
  - `[FIXED]` The runner must be same-site (`run.<domain>`), or Safari refuses its service worker and other browsers partition its storage; `*.pages.dev` previews cannot verify offline; `persist()` is called from the top-level site inside the gesture.
  - `[FIXED]` Offline proven by stopping both servers, recording at context level (zero requests), and running the hang test offline (`interrupts: "sab"`).
  - `[FIXED]` (nits)
    - responses cloned, not rebuilt, and `/sw.js` covered by `_headers`
    - separate shell, Pyodide and book caches, with books never deleted before their re-download completes, and skew caught by the envelope version
    - size and count shown up front, with Pagefind and `_astro` in the manifest
    - one `wrangler.toml` per project, and the 25 MiB check
    - import merge bounds, and iOS export

- `[fable]` **APPROVE WITH NITS** (round 2, e8821d0):
  - `[FIXED]` Confirmation is a `{book, content_hash, release_id}` record; `activate` never deletes `book-*` caches; an unchanged content hash means verify and re-stamp.
  - `[FIXED]` Chunked fetches with the record written at the end, and unconfirmed caches swept on worker start.
  - `[FIXED]` Formatting.

- `[sol]` **REJECT** (round 2, e8821d0):
  - `[FIXED]` A circular `release_id`: it now covers every dist file except `release.json` (which carries it); workers are registered by `?r=<release_id>`; a reproducibility test.
  - `[FIXED]` `skipWaiting` with clients open: B activates only when the reloading page is the sole client, coordinated across both origins via an `activate` message; a fresh exercise worker boots in an open A lesson during a pending update; the second-tab case is tested.
  - `[FIXED]` Book replacement: already folded in cd8540a (an unchanged content hash is verified and re-stamped, never refetched in place; a changed hash downloads into a new cache), plus interrupted and failed download tests.

- `[fable]` **APPROVE WITH NITS** (round 3, 452f9e4): no new blocker.
  - `[FIXED]` The offline `release.json` failure keeps the current registration silently.
  - `[FIXED]` The site page (not the worker) sends `activate`.
  - `[WONTFIX]` The `resume` bullet was already beside `cards` in Phase C; the reviewer read an intermediate diff.

- `[sol]` **REJECT** (round 3, 452f9e4): `[FIXED]` "Sole client" is not "no client". Activation is now a page-mediated handshake across both origins; `activate` deletes nothing; B workers serve any retained cache by exact URL, so the open A page keeps working through the activation interval; cleanup runs from a B page only once no A clients remain. The interval and a failed handshake are tested on both origins.

- `[sol]` **REJECT** (round 4, 5073ff8):
  - `[FIXED]` Rollback is impossible after an activation: forward-only recovery per step (retry; N−1 envelope compatibility keeps the mixed runner-B / site-A state working; A's caches kept), with each post-activation failure interval tested.
  - `[FIXED]` A stale "activate deletes old caches" line conflicted: `activate` deletes nothing, and the B-page cleanup is the sole path.
- `[fable]` **APPROVE WITH NITS** (round 4):
  - `[FIXED]` Exact-URL serving was unsafe for unhashed URLs: all runner assets now have content-hashed names, Pyodide sits under a versioned path, exact-URL serving over release-specific paths (the `clientId` mapping was dropped in round 5), and the interval test bumps those paths.
  - `[FIXED]` A 10 s step timeout.

- `[sol]` **REJECT** (round 5, 32fd61d):
  - `[FIXED]` The offline contract now allows exactly the one update-check request per page load (`/release.json`, failing silently) and zero others.
  - `[FIXED]` Lookups by `clientId` miss dedicated workers: since every asset URL is content-hashed or versioned, any retained cache serves by exact URL, and the client mapping is dropped.

- `[fable]` **APPROVE WITH NITS** (round 5, 023113d): `[FIXED]` The stale `clientId` record line; the update-check allowance is now counted per document per origin.

### Round 6 (023113d / 590616f) — CONSENSUS

- `[self]` APPROVE.
- `[sol]` **APPROVE** (gpt-6-sol): no blocking findings.
- `[fable]` **APPROVE WITH NITS**: its nits were folded in 590616f.
- `[glm]` removed from the roster (user directive 2026-10-05).

## Content Review

### Review 1 (38a3c32)

- `[self]` APPROVE after the Phase E run.
- `[sol]` **REQUEST CHANGES** (gpt-6-sol):
  1. `[FIXED]` MAJOR: "Available offline" trusted the site's stored `runner_release_id`, so a runner origin whose storage was cleared still showed "available". → New envelope-v2 `get-state` / `state` pair: the runner answers from its *own* record. The book page shows "Checking…" until both records agree, and "Download again" when the runner's is missing. Fixing this exposed a real bug: a `py4kids-offline` database recreated without its store could never be written again; it is now repaired by a version upgrade. Tests: pwa.spec "a runner whose storage was cleared is not 'available offline'" (online and with both servers stopped), offline-records.test, runner-client.test.
  2. `[FIXED]` MAJOR (also `[fable]` 5 and 12): import validation looked up file keys on plain objects (`constructor`/`toString` passed; `__proto__` threw). → Null-prototype rule maps and `Object.hasOwn` everywhere, with the same pattern fixed in `sw.ts` and `pwa-client.ts`. progress-io.test refuses 8 prototype names × 7 record levels with the schema message.
  3. `[FIXED]` MINOR: the offline per-book test never ticked a self-check checklist. → It ticks every box, waits for the event, and asserts both after the offline reload.
- `[fable]` **APPROVE WITH NITS**:
  1. `[FIXED]` The worker's record index went stale after `activate`. → Both workers re-read records on `activate` (deleting nothing) and on an offline miss; update.spec covers B installed before a download under A.
  2. `[FIXED]` `shell-<old>` caches accumulated for visitors with no downloads. → The completeness gate applies only when the origin has a confirmed book (`cleanupAllowed`); update.spec covers the no-download visitor on both origins.
  3. `[FIXED]` A site download had no stall detection. → 60 s with no progress gives "The download stopped. Try again."; pwa.spec covers it.
  4. `[FIXED]` Step 3 retried forever against the click-time release. → Each attempt re-reads the waiting worker and accepts a newer release, and after 5 attempts falls back to a plain reload.
  5. See [sol] 2.
  6. `[FIXED]` The stand-in build was not evidenced. → `scripts/build-release.sh pdfs-2026-09-30 --target stand-in` was run: unit tests, 497 pytest and the e2e passed, apart from one journey self-check flake on the first run. Its cause was the test leaving the page milliseconds after the tick, which can abort the IndexedDB write. The test now waits for the saved event; 24/24 repeats pass. A rerun of the stand-in e2e passed in full.
  7. `[FIXED]` A slow runner install failed the 10 s step. → "Preparing the update…" waits, capped at 5 min, while the runner's next worker is installing.
  8. `[FIXED]` NITs: raw error text in a tooltip (now `console.warn`), stale deviation references, the release key no longer servable, and the runner-timeout hook now drives the real `RunnerClient` timeout.

Results after the fixes: runner 26, site 409 unit tests; `pnpm -C site e2e` with 133 main, 22 PWA and 10 hooks tests passing.

### Review 2 (fbf6291) — CONSENSUS

- `[self]` APPROVE.
- `[sol]` **APPROVE WITH NITS** (gpt-6-sol). All three round-1 findings are fixed, and `get-state`/`state` is validated with exact fields, origin and source.
  `[WONTFIX]` NIT: the new self-check assertions in the offline test would also pass on the old code. That is correct: the finding was a coverage gap, not a product bug.
- `[fable]` **APPROVE WITH NITS**. All round-1 items were verified as fixed and tested.
  - A. `[FIXED]` A page no worker controls had `from = null`, so step 3 could count the old active release as new. → `from` now falls back to the registration's active release.
    An e2e test then showed the case cannot occur. After a hard reload, no window is left on A, so the browser activates B itself and no prompt appears. With another window on A, the page answers "close your other tabs".
    The guard stays as defence, and the test pins the browser behaviour.
    That test also exposed a gap: a release still installing when a page loaded never raised the update prompt. → Fixed: `pwa.ts` now also follows `reg.installing`.
  - B. `[FIXED]` `runner/origins.json`, brought back by the merge from main, is deleted again (`deploy/origins.json` is the single source).
  - C. `[WONTFIX]` NIT: the first second of step 0 says "Updating…" before "Preparing the update…". This is cosmetic.
  - D. `[FIXED]` The runner-missing message is now shorter: "Python is no longer saved on this device, so code will not run offline. Download the book again."

## Post-Execution Report

**Shipped: design 012 part D. The site is an installable, offline-capable PWA, and both origins are ready to deploy. Nothing has been deployed (Phase F waits for the user).**

**Phase D, deploy configuration:**
- `deploy/origins.json` (+ `origins.mjs`) is the single source of the origins. `PY4KIDS_TARGET=local|production` chooses the pair.
- The same-site check uses a built-in subset of the Public Suffix List; the loopback pair is the only exception.
- The production domain is the placeholder `py4kids.example`, and `scripts/build-release.sh` refuses to build production with it.
- `deploy/site/wrangler.toml`, `deploy/runner/wrangler.toml` and `deploy/README.md` (custom domain required; `*.pages.dev` previews are read-only).
- A 25 MiB per-file check.
- `release_id` is the sha256 of the sorted `site/…`/`runner/…` `path\0sha256` lines, excluding `release.json`. Tests show it is reproducible, recomputable from the emitted files, and changed by a runner rebuild.
- Every asset URL is release-specific: content-hashed names, Pagefind under `/pagefind/<hash>/`, Pyodide under `/pyodide/0.27.8/`. A build check rejects any other stable name.

**Phase A, the site PWA:**
- The web manifest, with icons generated from an SVG.
- A hand-written `sw.js?r=<release_id>`.
- "Download this book" shows the size, then a progress bar. Downloads are chunked into `book-<book>-<content_hash>` and confirmed by a record in IndexedDB `py4kids-offline`. `persist()` is called inside the click.
- Install and offline notices.
- The forward-only page-mediated activation handshake: 10 s step timeouts, the "close your other tabs" rule, and cleanup only when every client reports the current release.

**Phase B, the runner PWA:**
- The runner's service worker caches its shell and Pyodide.
- COOP/COEP/CORP survive on cloned cached responses, so `crossOriginIsolated` and SharedArrayBuffer interrupts still work with both servers stopped.
- Envelope v2 (`v`, `precache`/`precache-progress`/`precached`, `prepare-activate`/`runner-activated`, `version-mismatch`), with N−1 support tested.

**Phase C, export and import:**
- The JSON schema `py4kids/progress-export/1.0.0`.
- Saving uses `showSaveFilePicker`, then Web Share, then a download.
- A deterministic merge:
  - events and attempts are combined by id;
  - cards and resume positions keep the later `updated_at`, and a tie keeps the local record.
- Size, schema and validation checks run before any write.
- Book pages link to the controls.

**Phase E, verification:**
- **Offline end to end, per book (all four):** download, then stop both servers. After that, at most one failed `GET /release.json` per document per origin and nothing else. Then a lesson run, a check of every kind the book has, a card, the hang test with `interrupts: "sab"`, and a persistence reload.
- **The update path:** steps 1–7, including the paused activation interval with A's files served from the retained caches, failure at every step, re-confirmation without a refetch, changed content into a new cache, and an interrupted download swept on the next worker start.
- **Request recording with service workers active** on both origins.
- **Installability** through Chromium's DevTools protocol, since Lighthouse 13 removed its PWA category.
- **axe** on all the new UI.
- **Lighthouse:** 0.99 / 1 / 1 on a book page.
- **Results:**
  - unit tests: 406 site, 25 runner;
  - `pnpm -C site e2e`: 133 main tests (site, site-sw, lighthouse), 17 PWA tests (plus 7 hook tests that are skipped there), and 8 hook tests in a separate hooks build. Hook tests exist only with `PY4KIDS_TEST_HOOKS=1`, and `build-release.sh` refuses such a build.
- **A product race fixed:** a self-check box ticked while the page was loading was not recorded.

**Deviations, accepted:**
1. Navigations normalise to `/x/` (Cloudflare redirects `/x/index.html`).
2. Envelope messages gained fields: `content_hash`, `persisted`, `precache-progress`, `version-mismatch`, and `v: 2` on every message. Plan 104 had no envelope version, so a visitor still on the plan-104 runner sees "runner unavailable — reload" once.
3. The runner caches no book files: fixtures and assets live on the site origin and travel inside `run` messages, so the site's book cache holds them, and the runner confirms the book.
4. `content_hash` covers the book's whole download set (pages, assets, Pagefind). Pagefind's index is shared, so a content change in one book re-downloads every downloaded book. That is correct but costly.
5. The main Playwright config blocks service workers; the service-worker suites live in `e2e-pwa/` and run afterwards.
6. Chromium logs one unavoidable "Failed to load resource" line per failed `release.json` update check. The offline contract accepts exactly that line, and any other console error fails.

**Follow-ups:**
- A real v1-page-against-v2-runner test.
- Per-book Pagefind indexes, to avoid re-downloading every book.
- Pyodide memory snapshots.
- **Phase F (the first public deploy) needs the user's go-ahead, the Cloudflare account and API token, and the domain.**
- `scripts/ci-local.sh` solo on the final commit: see the PR.
