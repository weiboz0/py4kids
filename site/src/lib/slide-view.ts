/**
 * The slide player's view model (plan 103 Phase C): one lesson's slides, built by
 * `buildSlides` (the audit's own rules) and turned into render-ready parts. Pages read bundle
 * data only through `slideDecks`, which `test/schema-keys.test.ts` runs over a recording proxy.
 *
 * Markdown renders through Phase B's pipeline (`markdown.ts`: containers, Shiki, KaTeX), code
 * through its highlighter and turtle figures through `turtle.ts`: one implementation each, shared
 * with the reading view.
 */

import type { LoadedBook } from './bundle';
import { buildSlides, slideKeys, type MdUnit, type SlideKind } from './slides';
import { highlightCode, renderMarkdown } from './markdown';
import { turtleSvg } from './turtle';
import type { BlockType } from './types';

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
  /** The code highlighted at build time (classes only; `/code.css` styles them). */
  codeHtml: string;
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

/**
 * Render slide Markdown (the units of one block on one slide) as HTML with the site's one
 * Markdown pipeline (`markdown.ts`): units rejoin as paragraphs, so a run of list items forms one
 * list, and raw HTML is escaped, never interpreted.
 */
export function renderSlideMarkdown(units: readonly MdUnit[]): string {
  return renderMarkdown(units.map((u) => u.md).join('\n\n'));
}

const LABELS: Partial<Record<BlockType, string>> = {
  tryit: 'Try it',
  'error-demo': 'Error demo: this code stops with an error',
  'hang-demo': 'Hang demo: this code never finishes',
  'turtle-figure': 'Drawing',
  program: 'Program',
};

/** The entries of a book that have lesson slides, in syllabus order. */
export function slideDecks(book: LoadedBook): Deck[] {
  const decks: Deck[] = [];
  for (const { record, data } of book.entries) {
    const blocks = data.lesson?.blocks ?? [];
    const slides = buildSlides(blocks);
    if (slides.length === 0) continue;
    const keys = slideKeys(slides);
    const readingHref = `/${book.id}/${record.id}/`;
    decks.push({
      book: book.id,
      entry: record.id,
      title: record.title,
      readingHref,
      slidesHref: `${readingHref}slides/`,
      slides: slides.map((slide, i) => ({
        kind: slide.kind,
        key: keys[i]!,
        parts: slide.parts.map((part): DeckPart => {
          if (part.kind === 'md') return { kind: 'md', type: part.type, html: renderSlideMarkdown(part.units) };
          const b = part.block;
          return {
            kind: 'code',
            type: b.type,
            label: LABELS[b.type] ?? null,
            code: b.code ?? '',
            codeHtml: highlightCode(b.code ?? '', 'python'),
            output: b.output ?? null,
            svg: b.figure ? turtleSvg(b.figure, `Drawing for ${record.title}, slide ${i + 1}`) : null,
          };
        }),
      })),
    });
  }
  return decks;
}
