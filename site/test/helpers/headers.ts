/**
 * The strict CSP (plan 103 Global constraints; plan 104 adds the runner's frame-src) and a
 * Cloudflare Pages `_headers` parser.
 */
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

/** The runner origin the build fills in (runner/origins.json, or PY4KIDS_RUNNER_ORIGIN). */
export const RUNNER_ORIGIN: string =
  process.env.PY4KIDS_RUNNER_ORIGIN ??
  (JSON.parse(readFileSync(join(import.meta.dirname, '..', '..', '..', 'runner', 'origins.json'), 'utf-8')) as { runner: string }).runner;

/** The CSP as written in public/_headers (the runner origin is a placeholder there). */
export const CSP_TEMPLATE =
  "default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; style-src 'self'; img-src 'self'; " +
  "frame-src {{RUNNER_ORIGIN}}; object-src 'none'; base-uri 'none'; frame-ancestors 'none'";

/** The CSP the built site sends. */
export const CSP = CSP_TEMPLATE.replace('{{RUNNER_ORIGIN}}', RUNNER_ORIGIN);

/**
 * Parse a Cloudflare Pages `_headers` file: a URL pattern on an unindented line, then its
 * headers on indented `Name: value` lines; `#` lines are comments.
 */
export function parseHeaders(text: string): Map<string, Map<string, string>> {
  const rules = new Map<string, Map<string, string>>();
  let current: Map<string, string> | undefined;
  for (const line of text.split('\n')) {
    if (line.trim() === '' || line.trimStart().startsWith('#')) continue;
    if (!/^\s/.test(line)) {
      current = new Map();
      rules.set(line.trim(), current);
      continue;
    }
    if (!current) throw new Error(`header before any URL pattern: ${line}`);
    const colon = line.indexOf(':');
    if (colon < 0) throw new Error(`not a header line: ${line}`);
    current.set(line.slice(0, colon).trim().toLowerCase(), line.slice(colon + 1).trim());
  }
  return rules;
}
