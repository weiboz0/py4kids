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

- **One service worker per origin (D10):**
  - The site's worker caches the site's pages and assets.
  - The runner's worker caches the runner page, its worker script, the pinned Pyodide runtime and the book's fixture and asset files.
  - The site asks the runner to precache through the existing message channel, with a new typed request `{type: "precache", id, book, files}` and reply `{type: "precached", id, ok, bytes}`, validated as in part C.
- **Offline status:**
  - The site shows "available offline" for a book only after both caches confirm.
  - Both origins call `navigator.storage.persist()`, and the result is shown.
  - The site explains that some browsers (Safari) can clear storage after long disuse, and offers "export my progress".
- **Privacy is unchanged:**
  - The service workers make no requests beyond the files the user asked to cache.
  - There are no push notifications, background sync or analytics.
  - **Service-worker requests are recorded too.** Requests made by a service worker do not reach `page.on('request')`, so the tests record at context level (`browserContext.on('request')`, with Playwright's service-worker network events enabled) on both origins. Every request during browsing, precache and update must be on the allowlist: the files the user asked to cache, or the release's own files. Each one is a body-less GET.
- **Release identity and updates.**
  - **`release_id`:** the build computes it as a sha256 over the **complete** asset manifests of both origins: every file in `site/dist/` and `runner/dist/`, the Pyodide runtime included. It covers site code, runner code, Pyodide and content. A change to any of them is a new release.
  - **Cache names:** `site-<release_id>`, `runner-<release_id>` and `book-<book>-<release_id>`.
  - **Precache requests** carry `release_id`, and the runner refuses a mismatched one.
  - **A cache is confirmed only after it is fully populated** (`cache.addAll`, which is all-or-nothing). "Available offline" means both origins confirmed the same `release_id`.
  - **Activation is user-controlled:** a new worker stays *waiting* (no `skipWaiting` on install). An open lesson keeps running on the old release's caches until the user accepts "a new version is available — reload". Only then does the new worker activate (`skipWaiting` on that message). Old caches are deleted in `activate`, after the old clients are gone.
  - Downloaded books are re-downloaded for the new release in the background, and their status reads "updating" until confirmed.
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
    - COOP/COEP/CORP headers preserved on cached responses (the worker re-attaches them when serving from cache), so `crossOriginIsolated` holds offline
  - Test: offline, `crossOriginIsolated` is still true in the runner and its worker.
- **Phase C: export and import progress.**
  - "Export my progress" writes a JSON file of D11 events plus Leitner state and resume positions. It contains no attempt store (code stays on the device unless the user exports attempts separately, with a clear label).
  - **Deterministic import merge**, after validating the file against the schemas:
    - **events:** union by `event_id`
    - **cards:** per card key, keep the record with the later `updated_at` (every card record now stores `updated_at`); a tie keeps the local record
    - **resume:** per book, the later `updated_at`
  - Importing the same file twice changes nothing after the first import. Importing an older file never regresses newer local state.
  - Tests:
    - export → clear storage → import restores the mastery map and resume
    - importing the same file twice into an **existing, newer** store leaves it byte-for-byte unchanged (event count, card boxes, resume)
    - importing an older export keeps the newer card boxes
    - a malformed file is rejected with a message
- **Phase D: deploy configuration (no deploy).**
  - Contents:
    - **Pages projects:** `deploy/README.md` and `deploy/wrangler.toml` (two Pages projects: `py4kids` for the site, `py4kids-run` for the runner, custom domains as placeholders)
    - **Build:** `scripts/build-release.sh <tag>` builds both apps with `--release <tag>`, so the PDF links point at that GitHub Release, and runs the full site test suite
    - **Domains:** the production origins are configured in one place (`deploy/origins.json`) and read by the site (runner origin, CSP `frame-src`) and the runner (`frame-ancestors`, `targetOrigin`)
  - Test: a preview build with two local origins standing in for production passes the whole suite.
  - **No `wrangler deploy` runs in this plan.**
- **Phase E: verification (named verification phase).**
  - **Offline end-to-end, per book:**
    1. online, open the book and press "download this book"; wait for "available offline"
    2. go offline (Playwright `context.setOffline(true)`) and reload
    3. read a lesson, run a lesson cell, check one exercise of each kind the book has, and answer a card
    4. reload again offline: progress persists

    This is the D10 test design 012 §3 requires: it runs code and checks an exercise, not only reads.
  - **Update path:**
    1. build release A, download a book and open a lesson
    2. deploy release B (changing only runner code, so the bundle hash is unchanged but `release_id` differs)
    3. the open lesson keeps running and checking code on A's caches, and the prompt appears
    4. accept: B activates, A's caches are gone, and the book re-downloads and confirms under B
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

## Content Review

## Post-Execution Report
