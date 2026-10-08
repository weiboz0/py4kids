/**
 * `/code.css`: the one stylesheet for highlighted code (plan 103, Architecture — Shiki with
 * `transformerStyleToClass`, so no token carries an inline style under the CSP). The pipeline is
 * warmed over every book first, so the class registry is complete whatever order Astro builds in.
 */
import type { APIRoute } from 'astro';
import { getBooks } from '../lib/bundle';
import { warmPipeline } from '../lib/entry';
import { codeCss } from '../lib/markdown';

export const GET: APIRoute = () => {
  warmPipeline(getBooks());
  return new Response(codeCss(), { headers: { 'Content-Type': 'text/css; charset=utf-8' } });
};
