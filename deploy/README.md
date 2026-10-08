# Deploying the learning website

Design 012 D1 and plan 105 Phase D: the site and the Python runner deploy as two Cloudflare Pages projects from a release tag.
**Nothing in this repository deploys.**
The first public deploy (plan 105 Phase F) runs only after the user confirms it and provides the Cloudflare account, its API token (kept in `.env`, never committed) and the domain.

## Files

- `origins.json`: the only place the origins are configured.
  `local` is development and the tests, `production` the custom domain, `preview` the Pages default hosts.
  `origins.mjs` reads and validates it for the runner build, the site build, the test servers and the tests.
- `release.mjs`: the release identity, the release description in each dist's `release.json`, and the 25 MiB check.
- `site/wrangler.toml`: Pages project `py4kids` (`site/dist/`).
- `runner/wrangler.toml`: Pages project `py4kids-run` (`runner/dist/`).
  Wrangler's Pages config is one project per file.

## Same site: a custom domain is required

The runner must be on a subdomain of the site's registrable domain: the site on `<domain>`, the runner on `run.<domain>`.
Two origins on one registrable domain are same-site, and only then does the offline runner work:

- WebKit (Safari) refuses to register a service worker in a cross-site iframe.
- Chrome and Firefox partition a cross-site iframe's Cache Storage and IndexedDB by the top-level site.
- `navigator.storage.persist()` called from a cross-site iframe resolves `false`.

`*.pages.dev` is on the Public Suffix List, so the default Pages hosts (`py4kids.pages.dev` and `py4kids-run.pages.dev`) are two different sites.
**A preview on the Pages hosts is for reading only**: it cannot verify the offline runner.
The preview pair is still listed in `origins.json`, because a production build lists it in the site's CSP `frame-src` and the runner's `frame-ancestors`, which would otherwise block the preview's iframe; each app picks its partner at run time from its own `location.origin`.

`origins.mjs` rejects a production runner origin that is not a subdomain of the site's registrable domain (computed with a small embedded subset of the Public Suffix List; extend `PUBLIC_SUFFIXES` if the site moves to another multi-label suffix).
The local pair (`127.0.0.1` and `localhost`, two loopback hosts) is the one allowed exception: Chromium, the test browser, still runs the runner's service worker in a cross-site iframe, inside a storage partition that is stable across loads, so the offline tests exercise the real caching code.
That says nothing about Safari, which is why production needs the custom domain.

## Building a release

```
scripts/build-release.sh <tag>                      # the deployable production build
scripts/build-release.sh <tag> --target stand-in    # only the local stand-in build and its tests
```

1. A stand-in build for two local origins (the `PY4KIDS_SITE_ORIGIN` / `PY4KIDS_RUNNER_ORIGIN` overrides, else `local`) with `--release <tag>`, so each unit page links to that GitHub Release's PDFs, then the full site test suite against it: unit tests, the Python site checks and the browser suites.
2. With `--target production`, a rebuild for the production origins (and the preview pair), and the unit tests again.
   A placeholder `.example` production domain is refused.

Every build (`scripts/build-site.sh`):

- fails if any file exceeds Cloudflare Pages' 25 MiB per-file limit (`pyodide.asm.wasm` is the largest);
- gives every asset a release-specific URL: Astro's content-hashed `_astro/*`, the content-hashed root assets, icons, web manifest and Pagefind folder (`site/scripts/fingerprint.ts`), the runner's content-hashed `assets/main-*.js` and `assets/worker-*.js`, and Pyodide under `/pyodide/0.27.8/`.
  Only the HTML pages, `release.json` and `sw.js` keep stable names (and the books' data files, which are cached and served as one unit per book content hash);
- computes the `release_id` (a sha256 over the sorted `(path, sha256)` list of every file of both dists, except each dist's `release.json`) and writes it to both `release.json` files.

A release built with `PY4KIDS_TEST_HOOKS=1` (the test-only service-worker hooks) is refused.

## Headers

Cloudflare Pages applies each dist's `_headers` file:

- **site:** the strict CSP (`frame-src` names the runner origins), COOP `same-origin`, COEP `require-corp`;
- **runner:** its own CSP (`frame-ancestors` names the site origins), COOP, COEP and `Cross-Origin-Resource-Policy: cross-origin` on every response under `/*`, which includes `/sw.js` (Chrome checks a service worker script's COEP against a COEP document).

Pages serves `.wasm` as `application/wasm`, which `WebAssembly.instantiateStreaming` needs.

## Deploying (Phase F only, after the user confirms)

1. Set `production` in `origins.json` to the real `https://<domain>` and `https://run.<domain>`.
2. `scripts/build-release.sh <tag>`.
3. `wrangler pages deploy` for each project (`deploy/site/wrangler.toml`, `deploy/runner/wrangler.toml`), with the token from `.env`.
4. Attach the custom domains to the two Pages projects.
5. Smoke-test the real origins (headers, `crossOriginIsolated`, a lesson run, an exercise check, an offline download) and record the result in `output/README.md`.
