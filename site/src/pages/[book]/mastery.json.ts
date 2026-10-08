/**
 * The mastery map's build-time projection, `/<book>/mastery.json` (plan 103 "Mastery map and
 * cards"): each card's concepts, for the concepts the map shows with a percentage.
 */
import type { APIRoute, GetStaticPaths } from 'astro';
import { getBooks, type LoadedBook } from '../../lib/bundle';
import { masteryProjection } from '../../lib/mastery';

export const getStaticPaths = (() =>
  getBooks().map((book) => ({ params: { book: book.id }, props: { book } }))) satisfies GetStaticPaths;

export const GET: APIRoute = ({ props }) =>
  new Response(JSON.stringify(masteryProjection((props as { book: LoadedBook }).book)), {
    headers: { 'Content-Type': 'application/json' },
  });
