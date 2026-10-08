/**
 * The site and runner origins (design 012 D1, D7; plan 105 Phase D "Domains"): the one reader of
 * deploy/origins.json, shared by the runner build, the site build, the test servers and the tests.
 *
 * - **Target.** `PY4KIDS_TARGET=local` (the default) builds for the `local` pair. `production`
 *   builds for the `production` pair and also lists the `preview` pair, so the same build works on
 *   the Cloudflare Pages default hosts (frame-src and frame-ancestors would block them otherwise);
 *   each app picks its partner at run time by its own `location.origin`.
 * - **Overrides.** `PY4KIDS_SITE_ORIGIN` / `PY4KIDS_RUNNER_ORIGIN` replace everything with one pair
 *   (a missing half falls back to the `local` value): a stand-in for production on two local ports.
 * - **Same site (plan 105 Global constraints).** The runner must be a subdomain of the site's
 *   registrable domain (`run.<domain>`), or WebKit refuses its service worker, Chrome and Firefox
 *   partition its storage by the top-level site, and `persist()` from the iframe resolves false.
 *   Every non-preview pair is checked. Two exceptions, both explicit:
 *     - **Loopback** (`127.0.0.1`, `localhost`, `[::1]` over http): the local pair is two loopback
 *       hosts, which no registrable domain covers. It is allowed because Chromium (the test
 *       browser) still runs a service worker in a cross-site iframe, in a storage partition keyed
 *       by the top-level site, and that partition is stable across loads, so the offline tests
 *       exercise the real caching code. It proves nothing about Safari, which is why production
 *       needs the custom domain.
 *     - **Preview** pairs are listed for reading only; they are cross-site by construction.
 *   Registrable domains use a small embedded subset of the Public Suffix List (no dependency);
 *   `PUBLIC_SUFFIXES` must grow if the site moves to another multi-label suffix.
 */
import { readFileSync } from 'node:fs';

export const ORIGINS_FILE = new URL('./origins.json', import.meta.url);

/**
 * Multi-label public suffixes the deploy may meet (a subset of the Public Suffix List). A single
 * label (`org`, `dev`, `example`) is always a public suffix.
 */
export const PUBLIC_SUFFIXES = [
  'pages.dev',
  'workers.dev',
  'github.io',
  'gitlab.io',
  'netlify.app',
  'vercel.app',
  'web.app',
  'firebaseapp.com',
  'herokuapp.com',
  'co.uk',
  'org.uk',
  'ac.uk',
  'gov.uk',
  'com.au',
  'net.au',
  'org.au',
  'edu.au',
  'co.nz',
  'co.jp',
  'com.br',
  'com.cn',
  'com.tw',
  'co.in',
];

const LOOPBACK = new Set(['127.0.0.1', 'localhost', '[::1]']);

/** True for a loopback host name. */
export function isLoopback(host) {
  return LOOPBACK.has(host.toLowerCase());
}

/** The origin `value` if it is exactly an origin (scheme, host, port; no path), else throw. */
export function checkOrigin(value, what = 'origin') {
  let url;
  try {
    url = new URL(value);
  } catch {
    throw new Error(`${what}: not a URL: ${value}`);
  }
  if (url.origin !== value) throw new Error(`${what}: not an origin (scheme://host[:port], no slash): ${value}`);
  if (url.protocol !== 'https:' && url.protocol !== 'http:') throw new Error(`${what}: not http(s): ${value}`);
  return value;
}

/**
 * The registrable domain (eTLD+1) of `host` under `PUBLIC_SUFFIXES`, or null when the host is
 * itself a public suffix. An IP literal or a single-label host is its own site.
 */
export function registrableDomain(host) {
  const name = host.toLowerCase().replace(/\.$/, '');
  if (/^\d+\.\d+\.\d+\.\d+$/.test(name) || name.startsWith('[') || !name.includes('.')) return name;
  const labels = name.split('.');
  let suffixLabels = 1;
  for (const suffix of PUBLIC_SUFFIXES) {
    const n = suffix.split('.').length;
    if (n > suffixLabels && (name === suffix || name.endsWith(`.${suffix}`))) suffixLabels = n;
  }
  if (labels.length <= suffixLabels) return null;
  return labels.slice(-(suffixLabels + 1)).join('.');
}

/**
 * Throw unless the pair can host the offline runner: two different origins, and either the
 * loopback exception or https with the runner a subdomain of the site's registrable domain.
 * A `preview` pair is only checked for being two valid, different origins.
 */
export function checkPair(pair, { preview = false, name = 'pair' } = {}) {
  const site = new URL(checkOrigin(pair.site, `${name}.site`));
  const runner = new URL(checkOrigin(pair.runner, `${name}.runner`));
  if (site.origin === runner.origin) throw new Error(`${name}: the runner must be a different origin from the site`);
  if (preview) return pair;
  if (isLoopback(site.hostname) && isLoopback(runner.hostname)) {
    if (site.protocol !== 'http:' || runner.protocol !== 'http:') throw new Error(`${name}: loopback origins are http`);
    return pair;
  }
  if (site.protocol !== 'https:' || runner.protocol !== 'https:') throw new Error(`${name}: a deployed origin must be https`);
  const domain = registrableDomain(site.hostname);
  if (!domain) throw new Error(`${name}: the site host ${site.hostname} is a public suffix, not a registrable domain`);
  if (runner.hostname !== domain && !runner.hostname.endsWith(`.${domain}`)) {
    throw new Error(
      `${name}: the runner ${runner.hostname} is not a subdomain of the site's registrable domain ${domain} ` +
        '(cross-site: Safari refuses its service worker and other browsers partition its storage; use run.<domain>)',
    );
  }
  return pair;
}

/** True when a pair still holds the `.example` placeholder domain. */
export function isPlaceholder(pair) {
  return [pair.site, pair.runner].some((o) => new URL(o).hostname.endsWith('.example'));
}

/** Parse and validate deploy/origins.json (or `text`). */
export function readOrigins(text = readFileSync(ORIGINS_FILE, 'utf-8')) {
  const config = JSON.parse(text);
  for (const key of ['local', 'production', 'preview']) {
    if (!config[key] || typeof config[key].site !== 'string' || typeof config[key].runner !== 'string') {
      throw new Error(`deploy/origins.json: "${key}" needs "site" and "runner"`);
    }
  }
  checkPair(config.local, { name: 'local' });
  checkPair(config.production, { name: 'production' });
  checkPair(config.preview, { name: 'preview', preview: true });
  return config;
}

/**
 * The origins a build uses: `{ target, primary, pairs }`. `primary` is the pair the build is for
 * (the test servers listen there); `pairs` are every pair the build accepts (CSP lists, run-time
 * partner selection), primary first.
 */
export function resolveOrigins({ env = process.env, text } = {}) {
  const config = readOrigins(text);
  const target = env.PY4KIDS_TARGET ?? 'local';
  if (target !== 'local' && target !== 'production') throw new Error(`PY4KIDS_TARGET: "local" or "production", not "${target}"`);
  if (env.PY4KIDS_SITE_ORIGIN || env.PY4KIDS_RUNNER_ORIGIN) {
    const primary = checkPair(
      { site: env.PY4KIDS_SITE_ORIGIN || config.local.site, runner: env.PY4KIDS_RUNNER_ORIGIN || config.local.runner },
      { name: 'PY4KIDS_SITE_ORIGIN/PY4KIDS_RUNNER_ORIGIN' },
    );
    return { target, primary, pairs: [{ ...primary, preview: false }] };
  }
  if (target === 'local') return { target, primary: config.local, pairs: [{ ...config.local, preview: false }] };
  return {
    target,
    primary: config.production,
    pairs: [
      { ...config.production, preview: false },
      { ...config.preview, preview: true },
    ],
  };
}
