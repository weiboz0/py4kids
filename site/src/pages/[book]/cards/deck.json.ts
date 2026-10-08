/**
 * The card deck's build-time projection, `/<book>/cards/deck.json` (plan 103 Architecture:
 * no bundle JSON reaches the client; the island gets only this projection).
 */
import type { APIRoute, GetStaticPaths } from 'astro';
import { getBooks, type LoadedBook } from '../../../lib/bundle';
import { deckProjection } from '../../../lib/cards';

export const getStaticPaths = (() =>
  getBooks()
    .filter((book) => book.entries.some((e) => e.data.cards.length > 0))
    .map((book) => ({ params: { book: book.id }, props: { book } }))) satisfies GetStaticPaths;

export const GET: APIRoute = ({ props }) =>
  new Response(JSON.stringify(deckProjection((props as { book: LoadedBook }).book)), {
    headers: { 'Content-Type': 'application/json' },
  });
