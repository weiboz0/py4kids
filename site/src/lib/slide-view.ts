/**
 * The slide player's view model (plan 103 Phase C): one lesson's slides, built by
 * `buildSlides` (the audit's own rules) and turned into render-ready parts. Pages read bundle
 * data only through `slideDecks`, which `test/schema-keys.test.ts` runs over a recording proxy.
 *
 * `renderSlideMarkdown` is a deliberately small, escape-only adapter (paragraphs, headings,
 * lists, fenced code, pipe tables, inline code, bold and italics). Phase B's Markdown pipeline
 * (`markdown.ts`: containers, Shiki, KaTeX) replaces it at merge: swap the body of
 * `renderSlideMarkdown`, keep its signature.
 */

import type { LoadedBook } from './bundle';
import { buildSlides, slideKey, type MdUnit, type SlideKind } from './slides';
import type { BlockType, Segment } from './types';

export interface DeckMdPart {
  kind: 'md';
  /** The source block's type (prose, opener, goals, recap, notice). */
  type: BlockType;
  html: string;
}

export interface DeckCodePart {
  kind: 'code';
  type: BlockType;
  /** A heading for blocks the PDFs label (try-it, demos, drawings, program listings). */
  label: string | null;
  code: string;
  output: string | null;
  /** An inline SVG drawing for a turtle figure, else null. */
  svg: string | null;
}

export type DeckPart = DeckMdPart | DeckCodePart;

export interface DeckSlide {
  kind: SlideKind;
  /** The first block key on the slide: the `item_key` of its progress event. */
  key: string;
  parts: DeckPart[];
}

export interface Deck {
  book: string;
  entry: string;
  title: string;
  /** The reading view this deck returns to. */
  readingHref: string;
  slidesHref: string;
  slides: DeckSlide[];
}

const ESCAPES: Record<string, string> = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
export const escapeHtml = (text: string): string => text.replace(/[&<>"']/g, (c) => ESCAPES[c]!);

/** Inline Markdown on escaped text: `code`, **bold**, *italic* / _italic_. */
function inline(text: string): string {
  const parts = text.split(/(`+)([\s\S]*?)\1/);
  let out = '';
  for (let i = 0; i < parts.length; i += 3) {
    out += escapeHtml(parts[i]!)
      .replace(/\*\*(?=\S)([\s\S]*?\S)\*\*/g, '<strong>$1</strong>')
      .replace(/(^|[^\w*])\*(?=\S)([^*]*?\S)\*(?!\w)/g, '$1<em>$2</em>')
      .replace(/(^|[^\w])_(?=\S)([^_]*?\S)_(?!\w)/g, '$1<em>$2</em>');
    if (i + 2 < parts.length) out += `<code>${escapeHtml(parts[i + 2]!.trim())}</code>`;
  }
  return out;
}

const FENCE_LINE = /^\s*(`{3,}|~{3,})/;

/** Render a run of lines that may hold fenced code: prose lines become paragraphs. */
function flow(lines: string[]): string {
  let html = '';
  let text: string[] = [];
  let code: string[] | null = null;
  const flushText = () => {
    if (text.length > 0) html += `<p>${text.map((l) => inline(l.trim())).join('<br>')}</p>`;
    text = [];
  };
  for (const line of lines) {
    if (code !== null) {
      if (FENCE_LINE.test(line)) {
        html += `<pre class="slide-code"><code>${escapeHtml(code.join('\n'))}</code></pre>`;
        code = null;
      } else {
        code.push(line);
      }
    } else if (FENCE_LINE.test(line)) {
      flushText();
      code = [];
    } else if (line.trim() === '') {
      flushText();
    } else {
      text.push(line);
    }
  }
  if (code !== null) html += `<pre class="slide-code"><code>${escapeHtml(code.join('\n'))}</code></pre>`;
  flushText();
  return html;
}

const cells = (row: string): string[] =>
  row.trim().replace(/^\|/, '').replace(/\|$/, '').split(/(?<!\\)\|/).map((c) => c.trim());

function table(md: string): string {
  const rows = md.split('\n').filter((l) => l.trim() !== '');
  const [head, , ...body] = rows;
  const th = cells(head ?? '').map((c) => `<th scope="col">${inline(c)}</th>`).join('');
  const tr = body.map((r) => `<tr>${cells(r).map((c) => `<td>${inline(c)}</td>`).join('')}</tr>`).join('');
  return `<div class="slide-table"><table><thead><tr>${th}</tr></thead><tbody>${tr}</tbody></table></div>`;
}

const ITEM = /^([-*+]|\d{1,9}[.)])\s+/;

/** One unit's HTML (list items without their `<ul>`/`<ol>`). */
function unitHtml(unit: MdUnit): string {
  switch (unit.kind) {
    case 'heading': {
      const m = /^(#{1,6})\s*(.*?)\s*#*\s*$/.exec(unit.md.split('\n')[0]!)!;
      const level = Math.min(Math.max(m[1]!.length, 2), 4);
      const rest = unit.md.split('\n').slice(1);
      return `<h${level}>${inline(m[2]!)}</h${level}>${flow(rest)}`;
    }
    case 'table':
      return table(unit.md);
    case 'item': {
      const lines = unit.md.split('\n');
      lines[0] = lines[0]!.replace(ITEM, '');
      return `<li>${flow(lines.map((l, i) => (i === 0 ? l : l.replace(/^ {1,4}/, ''))))}</li>`;
    }
    default:
      return flow(unit.md.split('\n'));
  }
}

/**
 * Render slide Markdown (the units of one block on one slide) as HTML. An escape-only adapter:
 * raw HTML is shown as text, never interpreted. Phase B's pipeline replaces the body.
 */
export function renderSlideMarkdown(units: readonly MdUnit[]): string {
  let html = '';
  let list: 'ul' | 'ol' | null = null;
  for (const unit of units) {
    const kind = unit.kind === 'item' ? (/^\d/.test(unit.md) ? 'ol' : 'ul') : null;
    if (list !== kind) {
      if (list) html += `</${list}>`;
      if (kind) html += `<${kind}>`;
      list = kind;
    }
    html += unitHtml(unit);
  }
  if (list) html += `</${list}>`;
  return html;
}

const LABELS: Partial<Record<BlockType, string>> = {
  tryit: 'Try it',
  'error-demo': 'Error demo: this code stops with an error',
  'hang-demo': 'Hang demo: this code never finishes',
  'turtle-figure': 'Drawing',
  program: 'Program',
};

const num = (n: number) => String(Math.round(n * 100) / 100);

/**
 * A turtle drawing as inline SVG (plan 103 "Turtle SVG"): y flipped, a padded bounding-box
 * viewBox, a white background. Phase B's reading-view renderer may replace this at merge.
 */
export function turtleSvg(segments: readonly Segment[], label: string): string {
  if (segments.length === 0) return '';
  const xs = segments.flatMap((s) => [s.x1, s.x2]);
  const ys = segments.flatMap((s) => [-s.y1, -s.y2]);
  const pad = 10 + Math.max(...segments.map((s) => s.width));
  const x0 = Math.min(...xs) - pad;
  const y0 = Math.min(...ys) - pad;
  const w = Math.max(...xs) + pad - x0;
  const h = Math.max(...ys) + pad - y0;
  const lines = segments
    .map((s) => `<line x1="${num(s.x1)}" y1="${num(s.y1)}" x2="${num(s.x2)}" y2="${num(s.y2)}" stroke="${escapeHtml(s.color)}" stroke-width="${num(s.width)}" stroke-linecap="round"/>`)
    .join('');
  return `<svg class="slide-drawing" role="img" aria-label="${escapeHtml(label)}" viewBox="${num(x0)} ${num(y0)} ${num(w)} ${num(h)}" xmlns="http://www.w3.org/2000/svg">` +
    `<rect x="${num(x0)}" y="${num(y0)}" width="${num(w)}" height="${num(h)}" fill="white"/>` +
    `<g transform="scale(1,-1)">${lines}</g></svg>`;
}

/** The entries of a book that have lesson slides, in syllabus order. */
export function slideDecks(book: LoadedBook): Deck[] {
  const decks: Deck[] = [];
  for (const { record, data } of book.entries) {
    const blocks = data.lesson?.blocks ?? [];
    const slides = buildSlides(blocks);
    if (slides.length === 0) continue;
    const readingHref = `/${book.id}/${record.id}/`;
    decks.push({
      book: book.id,
      entry: record.id,
      title: record.title,
      readingHref,
      slidesHref: `${readingHref}slides/`,
      slides: slides.map((slide, i) => ({
        kind: slide.kind,
        key: slideKey(slide),
        parts: slide.parts.map((part): DeckPart => {
          if (part.kind === 'md') return { kind: 'md', type: part.type, html: renderSlideMarkdown(part.units) };
          const b = part.block;
          return {
            kind: 'code',
            type: b.type,
            label: LABELS[b.type] ?? null,
            code: b.code ?? '',
            output: b.output ?? null,
            svg: b.figure ? turtleSvg(b.figure, `Drawing for ${record.title}, slide ${i + 1}`) : null,
          };
        }),
      })),
    });
  }
  return decks;
}
