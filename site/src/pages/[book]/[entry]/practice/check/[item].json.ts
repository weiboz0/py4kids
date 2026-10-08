/**
 * `/<book>/<entry>/practice/check/<anchor>.json`: what one item's check needs (plan 104 Phase B;
 * `checkProjection` in src/lib/checks.ts). The check island fetches it only when Check (or Run)
 * is pressed, and never renders its hash or asserts.
 */
import type { APIRoute, GetStaticPaths } from 'astro';
import { getBooks } from '../../../../../lib/bundle';
import { checkProjection, itemRoutes, type ItemRoute } from '../../../../../lib/checks';

export const getStaticPaths = (() =>
  itemRoutes(getBooks()).map((route) => ({
    params: { book: route.book, entry: route.entry, item: route.anchor },
    props: { route },
  }))) satisfies GetStaticPaths;

export const GET: APIRoute = ({ props }) => {
  const { route } = props as { route: ItemRoute };
  return new Response(JSON.stringify(checkProjection(route.book, route.item)), {
    headers: { 'Content-Type': 'application/json' },
  });
};
