/** The strict CSP (plan 103 Global constraints) and a Cloudflare Pages `_headers` parser. */

export const CSP =
  "default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; style-src 'self'; img-src 'self'; " +
  "object-src 'none'; base-uri 'none'; frame-ancestors 'none'";

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
