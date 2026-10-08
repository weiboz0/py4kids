/**
 * Answer normalisation and salted hashing: the TypeScript port of `tools/export/normalise.py`
 * (design 012 D5; plan 103 Architecture). It must agree with Python byte for byte;
 * `tools/export/hash_vectors.json` pins the cases and `site/test/normalise.test.ts` runs every one.
 *
 * Plan 102 rule 3 extends the Python side with `whitespace` and `aliases`; this port implements
 * them now so part C's checks follow the same rule:
 * - `whitespace: 'collapse'` (the default): every run of whitespace inside a line becomes one
 *   space and each line is trimmed.
 * - `whitespace: 'exact'`: line endings fold to `\n` and trailing whitespace is stripped from each
 *   line; tabs, leading indentation and inner runs are kept.
 * - Both drop leading and trailing blank lines.
 * - `case: 'insensitive'` applies Python's `str.casefold()`.
 * - `aliases` (`{typed: canonical}`) map the typed form, after whitespace and case.
 *
 * Python's `\s` (a `str` pattern) is not JavaScript's: Python includes U+001C..U+001F and U+0085
 * and excludes U+FEFF, which JavaScript's `\s` includes. The class below is Python's exactly
 * (`str.isspace()`); `str.strip()` uses the same set.
 */

const PY_WS = '\\t\\n\\v\\f\\r\\x1c-\\x1f \\x85\\xa0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000';
const WS_RUN = new RegExp(`[${PY_WS}]+`, 'g');
const LEADING = new RegExp(`^[${PY_WS}]+`);
const TRAILING = new RegExp(`[${PY_WS}]+$`);

export type Case = 'sensitive' | 'insensitive';
export type Whitespace = 'collapse' | 'exact';

export interface NormaliseOptions {
  case: Case;
  whitespace?: Whitespace;
  aliases?: Record<string, string>;
}

/**
 * One code point's full case folding, as Python's `str.casefold()` (Unicode 15) gives it.
 * Upper-then-lower casing per code point agrees with the folding table everywhere except the
 * exceptions below (found by comparing both over every assigned code point; the exhaustive test
 * repeats that comparison when a Python is available).
 */
function foldChar(ch: string): string {
  const cp = ch.codePointAt(0)!;
  if (cp === 0x131) return ch; // dotless i folds to itself
  if (cp === 0x1e9e) return 'ss'; // capital sharp s
  if (cp >= 0x13a0 && cp <= 0x13f5) return ch; // Cherokee folds to the uppercase letters
  if (cp >= 0x13f8 && cp <= 0x13fd) return String.fromCodePoint(cp - 8);
  if (cp >= 0xab70 && cp <= 0xabbf) return String.fromCodePoint(cp - 0xab70 + 0x13a0);
  return ch.toUpperCase().toLowerCase();
}

/** Python's `str.casefold()`. Per code point, so no context rule (final sigma) applies. */
export function casefold(text: string): string {
  let out = '';
  for (const ch of text) out += foldChar(ch);
  return out;
}

function applyAliases(text: string, aliases: Record<string, string>): string {
  const keys = Object.keys(aliases).filter((k) => k.length > 0);
  if (keys.length === 0) return text;
  keys.sort((a, b) => b.length - a.length);
  const pattern = new RegExp(keys.map((k) => k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|'), 'gu');
  return text.replace(pattern, (m) => aliases[m]!);
}

export function normalise(text: string, options: NormaliseOptions): string {
  const exact = options.whitespace === 'exact';
  const lines = text
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .split('\n')
    .map((line) => (exact ? line.replace(TRAILING, '') : line.replace(WS_RUN, ' ').replace(LEADING, '').replace(TRAILING, '')));
  // Both modes strip each line's trailing whitespace, so a blank line is now empty.
  while (lines.length > 0 && lines[0] === '') lines.shift();
  while (lines.length > 0 && lines[lines.length - 1] === '') lines.pop();
  let out = lines.join('\n');
  if (options.case === 'insensitive') out = casefold(out);
  if (options.aliases) out = applyAliases(out, options.aliases);
  return out;
}

const HEX = (bytes: ArrayBuffer) => [...new Uint8Array(bytes)].map((b) => b.toString(16).padStart(2, '0')).join('');

/**
 * `sha256:<hex>` of `py4kids-answer-v1\n<item_key>\n<normalised>` (UTF-8), exactly as
 * `answer_hash` in Python. The salt is the item's public global key, so equal answers to
 * different items hash differently (D5). Uses WebCrypto (browsers, and Node >= 19).
 */
export async function answerHash(itemKey: string, canonical: string, options: NormaliseOptions): Promise<string> {
  const payload = `py4kids-answer-v1\n${itemKey}\n${normalise(canonical, options)}`;
  const digest = await globalThis.crypto.subtle.digest('SHA-256', new TextEncoder().encode(payload));
  return `sha256:${HEX(digest)}`;
}
