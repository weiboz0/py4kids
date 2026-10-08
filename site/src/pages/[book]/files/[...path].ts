/**
 * `/<book>/files/<entry>/<path>`: the bundle's files (lesson assets, item files, fixture pairs),
 * byte for byte (plan 104 Phase B). A run or check fetches only the files it mounts or compares
 * with, one at a time, when it is pressed; no page loads them. A hidden fixture's `.out` is fetched
 * into memory to compare with and never shown.
 */
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { APIRoute, GetStaticPaths } from 'astro';
import { getBooks } from '../../../lib/bundle';
import { bundleFiles } from '../../../lib/checks';

export const getStaticPaths = (() =>
  getBooks().flatMap((book) =>
    bundleFiles(book).map((path) => ({
      // `files/<entry>/<path>` is served at `/<book>/files/<entry>/<path>`.
      params: { book: book.id, path: path.replace(/^files\//, '') },
      props: { file: join(book.dir, path) },
    })),
  )) satisfies GetStaticPaths;

export const GET: APIRoute = ({ props }) =>
  new Response(readFileSync((props as { file: string }).file), {
    headers: { 'Content-Type': 'application/octet-stream' },
  });
