/**
 * deploy/origins.mjs (plan 105 Phase D "Domains", Global constraints "Same site"): one config,
 * validated so a production runner is a subdomain of the site's registrable domain.
 */
import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { checkPair, isPlaceholder, ORIGINS_FILE, readOrigins, registrableDomain, resolveOrigins } from '../../deploy/origins.mjs';

const TEXT = readFileSync(ORIGINS_FILE, 'utf-8');

describe('registrableDomain', () => {
  it('takes one label past the public suffix', () => {
    expect(registrableDomain('py4kids.org')).toBe('py4kids.org');
    expect(registrableDomain('run.py4kids.org')).toBe('py4kids.org');
    expect(registrableDomain('a.b.py4kids.co.uk')).toBe('py4kids.co.uk');
    expect(registrableDomain('py4kids.pages.dev')).toBe('py4kids.pages.dev');
    expect(registrableDomain('py4kids-run.pages.dev')).toBe('py4kids-run.pages.dev');
  });
  it('knows a public suffix is not registrable', () => {
    expect(registrableDomain('pages.dev')).toBeNull();
    expect(registrableDomain('co.uk')).toBeNull();
  });
});

describe('checkPair', () => {
  it('accepts run.<domain> for <domain> (same site)', () => {
    expect(() => checkPair({ site: 'https://py4kids.org', runner: 'https://run.py4kids.org' })).not.toThrow();
    expect(() => checkPair({ site: 'https://www.py4kids.org', runner: 'https://run.py4kids.org' })).not.toThrow();
  });
  it('rejects a runner on another registrable domain (cross-site)', () => {
    expect(() => checkPair({ site: 'https://py4kids.org', runner: 'https://run.other.org' })).toThrow(/not a subdomain/);
    expect(() => checkPair({ site: 'https://py4kids.pages.dev', runner: 'https://py4kids-run.pages.dev' })).toThrow(/not a subdomain/);
    expect(() => checkPair({ site: 'https://pages.dev', runner: 'https://run.pages.dev' })).toThrow(/public suffix/);
  });
  it('rejects one origin for both, a non-origin, and plain http off loopback', () => {
    expect(() => checkPair({ site: 'https://py4kids.org', runner: 'https://py4kids.org' })).toThrow(/different origin/);
    expect(() => checkPair({ site: 'https://py4kids.org/', runner: 'https://run.py4kids.org' })).toThrow(/not an origin/);
    expect(() => checkPair({ site: 'http://py4kids.org', runner: 'http://run.py4kids.org' })).toThrow(/https/);
  });
  it('allows the loopback pair (the local tests), and only over http', () => {
    expect(() => checkPair({ site: 'http://127.0.0.1:4391', runner: 'http://localhost:4392' })).not.toThrow();
    expect(() => checkPair({ site: 'https://127.0.0.1:4391', runner: 'https://localhost:4392' })).toThrow(/http/);
    expect(() => checkPair({ site: 'http://127.0.0.1:4391', runner: 'https://run.py4kids.org' })).toThrow();
  });
  it('checks a preview pair only for two valid, different origins', () => {
    expect(() => checkPair({ site: 'https://py4kids.pages.dev', runner: 'https://py4kids-run.pages.dev' }, { preview: true })).not.toThrow();
  });
});

describe('deploy/origins.json', () => {
  it('validates, with production same-site and the preview pair listed', () => {
    const config = readOrigins(TEXT);
    expect(config.production.runner.startsWith('https://run.')).toBe(true);
    expect(isPlaceholder(config.production)).toBe(true); // until plan 105 Phase F sets the domain
  });

  it('refuses a cross-site production runner', () => {
    const bad = JSON.parse(TEXT) as Record<string, { site: string; runner: string }>;
    bad.production = { site: 'https://py4kids.org', runner: 'https://py4kids-run.org' };
    expect(() => readOrigins(JSON.stringify(bad))).toThrow(/production: the runner .* is not a subdomain/);
  });

  it('resolves local, production (with the preview pair) and the env overrides', () => {
    const local = resolveOrigins({ env: {}, text: TEXT });
    expect(local.pairs).toHaveLength(1);
    expect(local.primary).toEqual(readOrigins(TEXT).local);
    const prod = resolveOrigins({ env: { PY4KIDS_TARGET: 'production' }, text: TEXT });
    expect(prod.pairs.map((p) => p.preview)).toEqual([false, true]);
    expect(prod.primary.site).toBe(readOrigins(TEXT).production.site);
    const stand = resolveOrigins({
      env: { PY4KIDS_TARGET: 'production', PY4KIDS_SITE_ORIGIN: 'http://127.0.0.1:4691', PY4KIDS_RUNNER_ORIGIN: 'http://localhost:4692' },
      text: TEXT,
    });
    expect(stand.pairs).toEqual([{ site: 'http://127.0.0.1:4691', runner: 'http://localhost:4692', preview: false }]);
    expect(() => resolveOrigins({ env: { PY4KIDS_TARGET: 'staging' }, text: TEXT })).toThrow(/PY4KIDS_TARGET/);
    expect(() => resolveOrigins({ env: { PY4KIDS_RUNNER_ORIGIN: 'http://127.0.0.1:4391' }, text: TEXT })).toThrow(/different origin/);
  });
});
