// Types for deploy/release.mjs.
export interface Digest {
  path: string;
  sha256: string;
}
export interface Dist {
  name: string;
  dir: string;
}
export interface UrlSet {
  files: { url: string; bytes: number }[];
  bytes: number;
}
export interface BookSummary {
  content_hash: string;
  bytes: number;
  count: number;
  manifest: string;
}
export interface SiteRelease {
  release_id: string;
  app: 'site';
  shell: UrlSet;
  books: Record<string, BookSummary>;
  /** The runner's shell and Pyodide size (the download UI shows it up front). */
  runner: { bytes: number };
}
export interface RunnerRelease {
  release_id: string;
  app: 'runner';
  shell: UrlSet;
  pyodide: UrlSet & { dir: string; cache: string };
}
export const RELEASE_FILE: string;
export const MAX_FILE_BYTES: number;
export function listFiles(dir: string): string[];
export function fileDigests(dists: Dist[]): Digest[];
export function releaseIdOf(digests: Digest[]): string;
export function computeReleaseId(dirs: { site: string; runner: string }): string;
export function oversized(dists: Dist[], limit?: number): { path: string; bytes: number }[];
export function urlOf(path: string): string;
export function describeSite(dir: string): Omit<SiteRelease, 'release_id' | 'runner'>;
export function describeRunner(dir: string): Omit<RunnerRelease, 'release_id'>;
export function writeRelease(dirs: { site: string; runner: string }): string;
export function largest(dists: Dist[]): { path: string; bytes: number };
