/**
 * `/<book>/<entry>/practice/answer/<anchor>.json`: an odd unit exercise's answer (plan 104 Phase B;
 * `answerProjection` in src/lib/checks.ts), and only theirs. The check island fetches it only
 * after a genuine attempt, so the answer is never in the page's DOM before one.
 */
import type { APIRoute, GetStaticPaths } from 'astro';
import { getBooks } from '../../../../../lib/bundle';
import { answerProjection, itemRoutes, shipsAnswer, type ItemRoute } from '../../../../../lib/checks';

export const getStaticPaths = (() =>
  itemRoutes(getBooks())
    .filter((route) => shipsAnswer(route.item))
    .map((route) => ({
      params: { book: route.book, entry: route.entry, item: route.anchor },
      props: { route },
    }))) satisfies GetStaticPaths;

export const GET: APIRoute = ({ props }) => {
  const { route } = props as { route: ItemRoute };
  return new Response(JSON.stringify(answerProjection(route.item)), {
    headers: { 'Content-Type': 'application/json' },
  });
};
