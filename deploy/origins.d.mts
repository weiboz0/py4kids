// Types for deploy/origins.mjs (plain ESM, so astro.config.mjs and the Node scripts can import it).
export interface OriginPair {
  site: string;
  runner: string;
}
export interface ListedPair extends OriginPair {
  preview: boolean;
}
export interface OriginsConfig {
  local: OriginPair;
  production: OriginPair;
  preview: OriginPair;
}
export interface ResolvedOrigins {
  target: 'local' | 'production';
  primary: OriginPair;
  pairs: ListedPair[];
}
export const ORIGINS_FILE: URL;
export const PUBLIC_SUFFIXES: string[];
export function isLoopback(host: string): boolean;
export function checkOrigin(value: string, what?: string): string;
export function registrableDomain(host: string): string | null;
export function checkPair(pair: OriginPair, options?: { preview?: boolean; name?: string }): OriginPair;
export function isPlaceholder(pair: OriginPair): boolean;
export function readOrigins(text?: string): OriginsConfig;
export function resolveOrigins(options?: { env?: Record<string, string | undefined>; text?: string }): ResolvedOrigins;
