/**
 * The build audit (plan 103 Phase F, no network proof 2): a scan of every file in dist/ for an
 * absolute URL in a LOAD context —
 *   - HTML: src, srcset, poster, data, action/formaction, background, ping, <link href>, <base>,
 *     <use>/<image> href, <meta http-equiv=refresh>, CSS url()/@import in any <style>;
 *   - CSS: url(), @import;
 *   - JS: fetch(), import()/import … from, new Worker/SharedWorker, importScripts(), WebSocket,
 *     EventSource, sendBeacon (beacons and sockets are refused outright, any URL);
 *   - SVG: href / xlink:href;
 *   - JSON: any HTML string inside it (the card deck's definitions are inserted as HTML).
 * A string that is not a load (`new URL("https://example.com…")` in Pagefind, an `xmlns`
 * namespace, prose) is not one. The only absolute URLs allowed anywhere are plain <a href>
 * hyperlinks on the allowlist: the CC BY-NC-SA 4.0 deed, the GitHub issues page, the prefilled
 * new-issue link and the release PDF links (only those book.json `pdfs` names; only with
 * --release). No element carries a style attribute.
 */
import { readdirSync, readFileSync } from 'node:fs';
import { join, relative } from 'node:path';
import { gunzipSync } from 'node:zlib';
import { expect, test } from '@playwright/test';
import { DIST, SITE } from './helpers/env';

const LICENSE = 'https://creativecommons.org/licenses/by-nc-sa/4.0/';
const ISSUES = 'https://github.com/weiboz0/py4kids/issues';
const NEW_ISSUE = /^https:\/\/github\.com\/weiboz0\/py4kids\/issues\/new\?title=[^&#]*&body=[^&#]*$/;
const PDF = /^https:\/\/github\.com\/weiboz0\/py4kids\/releases\/download\/pdfs-\d{4}-\d{2}-\d{2}\/[\w.-]+\.pdf$/;

/** The release PDF links the bundles name (empty unless built with --release). */
function releasePdfs(): Set<string> {
  const out = new Set<string>();
  const content = join(SITE, 'content');
  for (const book of readdirSync(content)) {
    const pdfs = (JSON.parse(readFileSync(join(content, book, 'book.json'), 'utf-8')) as { pdfs: Record<string, string> | null }).pdfs;
    for (const href of Object.values(pdfs ?? {})) out.add(href);
  }
  return out;
}

const ABSOLUTE = /^\s*(?:[a-z][a-z0-9+.-]*:)?\/\//i;
const decode = (s: string) =>
  s.replace(/&(amp|quot|#39|lt|gt);/g, (_, e: string) => ({ amp: '&', quot: '"', '#39': "'", lt: '<', gt: '>' })[e] ?? _);

interface Tag {
  name: string;
  attrs: Map<string, string>;
}

/** Every start tag of an HTML (or SVG) text, with its attributes. */
function tags(html: string): Tag[] {
  const out: Tag[] = [];
  const text = html.replace(/<!--[\s\S]*?-->/g, '');
  for (const m of text.matchAll(/<([a-zA-Z][\w:-]*)((?:\s+[^\s"'>/=]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s"'=<>`]+))?)*)\s*\/?>/g)) {
    const attrs = new Map<string, string>();
    for (const a of m[2]!.matchAll(/([^\s"'>/=]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+)))?/g)) {
      attrs.set(a[1]!.toLowerCase(), decode(a[2] ?? a[3] ?? a[4] ?? ''));
    }
    out.push({ name: m[1]!.toLowerCase(), attrs });
  }
  return out;
}

const LOAD_ATTRS = ['src', 'poster', 'data', 'action', 'formaction', 'background', 'ping', 'manifest', 'codebase', 'cite', 'longdesc', 'lowsrc', 'dynsrc'];

/** Absolute URLs in CSS load contexts. */
function cssLoads(css: string): string[] {
  const out: string[] = [];
  const IMPORT = /@import\s+(?:url\(\s*)?(['"]?)([^'")\s;]+)[^;]*;?/gi;
  for (const m of css.matchAll(IMPORT)) if (ABSOLUTE.test(m[2]!)) out.push(`@import ${m[2]}`);
  for (const m of css.replace(IMPORT, '').matchAll(/url\(\s*(['"]?)([^'")]*)\1\s*\)/gi)) if (ABSOLUTE.test(m[2]!)) out.push(`url(${m[2]})`);
  return out;
}

/** Absolute URLs loaded from HTML/SVG, the absolute hyperlinks, and the elements with style. */
function htmlAudit(html: string): { loads: string[]; links: string[]; styled: string[] } {
  const loads: string[] = [];
  const links: string[] = [];
  const styled: string[] = [];
  for (const tag of tags(html)) {
    const { name, attrs } = tag;
    if (attrs.has('style')) styled.push(`<${name} style="${attrs.get('style')}">`);
    for (const attr of LOAD_ATTRS) {
      const v = attrs.get(attr);
      if (v !== undefined && ABSOLUTE.test(v)) loads.push(`<${name} ${attr}="${v}">`);
    }
    for (const attr of ['srcset', 'imagesrcset']) {
      for (const part of (attrs.get(attr) ?? '').split(',')) if (ABSOLUTE.test(part.trim())) loads.push(`<${name} ${attr}="${part.trim()}">`);
    }
    const href = attrs.get('href') ?? attrs.get('xlink:href');
    if (href !== undefined && ABSOLUTE.test(href)) {
      // Only a plain <a href> is a hyperlink (a user-initiated navigation); any other element's
      // href (link, base, use, image, area with ping …) is a load or changes where loads go.
      if (name === 'a' && !attrs.has('ping') && !attrs.has('download')) links.push(href);
      else loads.push(`<${name} href="${href}">`);
    }
    if (name === 'meta' && /refresh/i.test(attrs.get('http-equiv') ?? '') && /url\s*=/i.test(attrs.get('content') ?? '')) {
      loads.push(`<meta http-equiv=refresh content="${attrs.get('content')}">`);
    }
  }
  for (const m of html.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/gi)) loads.push(...cssLoads(m[1]!));
  return { loads, links, styled };
}

/** Absolute URLs (or any beacon/socket) in JS load calls. String literals only: a load built
 * at run time from a variable would still be caught by the request recording. */
function jsLoads(js: string): string[] {
  const out: string[] = [];
  const lit = String.raw`\s*(?:"((?:[a-z][a-z0-9+.-]*:)?\/\/[^"]*)"|'((?:[a-z][a-z0-9+.-]*:)?\/\/[^']*)'|\x60((?:[a-z][a-z0-9+.-]*:)?\/\/[^\x60]*)\x60)`;
  const calls = [
    String.raw`\bfetch\(`,
    String.raw`\bimport\(`,
    String.raw`\bimport\b[^;"'\x60()]*?\bfrom`,
    String.raw`^\s*import`,
    String.raw`\bnew\s+(?:Shared)?Worker\(`,
    String.raw`\bimportScripts\(`,
    String.raw`\bnew\s+EventSource\(`,
    String.raw`\.open\(\s*["'][A-Z]+["']\s*,`, // XMLHttpRequest.open(method, url)
  ];
  for (const call of calls) {
    for (const m of js.matchAll(new RegExp(call + lit, 'gim'))) out.push(`${call}: ${m[1] ?? m[2] ?? m[3]}`);
  }
  if (/\bnew\s+WebSocket\s*\(/.test(js)) out.push('new WebSocket(');
  if (/\bsendBeacon\s*\(/.test(js)) out.push('navigator.sendBeacon(');
  return out;
}

/** HTML strings anywhere inside a JSON value. */
function htmlStrings(value: unknown, out: string[] = []): string[] {
  if (typeof value === 'string') {
    if (/<[a-z]/i.test(value)) out.push(value);
  } else if (Array.isArray(value)) value.forEach((v) => htmlStrings(v, out));
  else if (value && typeof value === 'object') Object.values(value).forEach((v) => htmlStrings(v, out));
  return out;
}

function files(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((d) => (d.isDirectory() ? files(join(dir, d.name)) : [join(dir, d.name)]));
}

test.describe('build audit of dist/', () => {
  const all = files(DIST);
  const rel = (f: string) => relative(DIST, f);

  test('no absolute URL in any load context; only allowlisted hyperlinks; no style attribute', () => {
    const pdfs = releasePdfs();
    for (const href of pdfs) expect(href, 'a release PDF link').toMatch(PDF);
    const loads: string[] = [];
    const badLinks: string[] = [];
    const styled: string[] = [];
    const seen = { license: 0, issues: 0, newIssue: 0, pdf: 0 };
    let scanned = 0;
    for (const file of all) {
      const name = rel(file);
      let found: { loads: string[]; links: string[]; styled: string[] } | null = null;
      if (/\.(html|svg)$/.test(file)) found = htmlAudit(readFileSync(file, 'utf-8'));
      else if (file.endsWith('.css')) found = { loads: cssLoads(readFileSync(file, 'utf-8')), links: [], styled: [] };
      else if (/\.m?js$/.test(file)) found = { loads: jsLoads(readFileSync(file, 'utf-8')), links: [], styled: [] };
      else if (file.endsWith('.json')) {
        const parts = htmlStrings(JSON.parse(readFileSync(file, 'utf-8'))).map(htmlAudit);
        found = { loads: parts.flatMap((p) => p.loads), links: parts.flatMap((p) => p.links), styled: parts.flatMap((p) => p.styled) };
      } else if (file.endsWith('.pf_fragment')) {
        // Pagefind's fragments carry page text, rendered by the search page as text only.
        const text = gunzipSync(readFileSync(file)).toString('utf-8').replace(/^pagefind_dcd/, '');
        found = { loads: htmlStrings(JSON.parse(text)).flatMap((h) => htmlAudit(h).loads), links: [], styled: [] };
      }
      if (!found) continue;
      scanned += 1;
      loads.push(...found.loads.map((l) => `${name}: ${l}`));
      styled.push(...found.styled.map((s) => `${name}: ${s}`));
      for (const href of found.links) {
        if (href === LICENSE) seen.license += 1;
        else if (href === ISSUES) seen.issues += 1;
        else if (NEW_ISSUE.test(href)) seen.newIssue += 1;
        else if (pdfs.has(href)) seen.pdf += 1;
        else badLinks.push(`${name}: <a href="${href}">`);
      }
    }
    expect(scanned).toBeGreaterThan(350);
    expect(loads, 'absolute URLs in load contexts').toEqual([]);
    expect(badLinks, 'absolute hyperlinks not on the allowlist').toEqual([]);
    expect(styled, 'style attributes').toEqual([]);
    // The allowlisted links are really there (the scan sees them), and PDF links only with --release.
    expect(seen.license).toBeGreaterThan(0);
    expect(seen.issues).toBeGreaterThan(0);
    expect(seen.newIssue).toBeGreaterThan(0);
    expect(seen.pdf > 0).toBe(pdfs.size > 0);
  });

  test('the scanner catches each kind of load it looks for', () => {
    const html = [
      '<img src="https://x.test/a.png">',
      '<img srcset="/a.png 1x, //x.test/b.png 2x">',
      '<link rel="stylesheet" href="https://x.test/s.css">',
      '<link rel="preconnect" href="https://x.test">',
      '<script src="//x.test/s.js"></script>',
      '<form action="https://x.test/post"></form>',
      '<a href="https://x.test/" ping="https://x.test/ping">x</a>',
      '<svg><use href="https://x.test/i.svg#a"/></svg>',
      '<meta http-equiv="refresh" content="0; url=https://x.test/">',
      '<style>@import "https://x.test/i.css"; p { background: url(https://x.test/bg.png) }</style>',
      '<p style="color: red">x</p>',
      '<svg xmlns="http://www.w3.org/2000/svg"></svg>',
    ].join('\n');
    const result = htmlAudit(html);
    expect(result.loads).toHaveLength(12);
    expect(result.styled).toHaveLength(1);
    expect(htmlAudit('<a href="https://x.test/">a link</a>').links).toEqual(['https://x.test/']);
    const js = [
      'fetch("https://x.test/a")',
      "import('https://x.test/m.js')",
      'import { a } from "https://x.test/m.js";',
      'new Worker(`https://x.test/w.js`)',
      'importScripts("//x.test/w.js")',
      'navigator.sendBeacon("/b", d)',
      'new WebSocket(u)',
      'xhr.open("GET", "https://x.test/")',
      'const u = new URL("https://example.com/" + p);', // a parsing trick, not a load
    ].join('\n');
    expect(jsLoads(js)).toHaveLength(8);
    expect(cssLoads('a{background:url("https://x.test/a.png")} @import url(//x.test/b.css);')).toHaveLength(2);
  });
});
