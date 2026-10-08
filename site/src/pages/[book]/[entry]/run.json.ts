/**
 * `/<book>/<entry>/run.json`: a lesson's runnable blocks (plan 104 Phase B, D6;
 * `lessonRunProjection` in src/lib/checks.ts), fetched by the run island on the first Run.
 */
import type { APIRoute, GetStaticPaths } from 'astro';
import { getBooks, type LoadedBook, type LoadedEntry } from '../../../lib/bundle';
import { isRunnable, lessonRunProjection } from '../../../lib/checks';

export const getStaticPaths = (() =>
  getBooks().flatMap((book) =>
    book.entries
      .filter((entry) => entry.data.lesson?.blocks.some(isRunnable))
      .map((entry) => ({ params: { book: book.id, entry: entry.record.id }, props: { book, entry } })),
  )) satisfies GetStaticPaths;

export const GET: APIRoute = ({ props }) => {
  const { book, entry } = props as { book: LoadedBook; entry: LoadedEntry };
  return new Response(JSON.stringify(lessonRunProjection(book, entry)), {
    headers: { 'Content-Type': 'application/json' },
  });
};
