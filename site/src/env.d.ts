/// <reference types="astro/client" />

// Astro's client types, declared here so a fresh checkout type-checks before `astro sync`
// writes .astro/types.d.ts (gitignored).

interface ImportMetaEnv {
  /** The runner origin, defined at build time by astro.config.mjs (runner/origins.json). */
  readonly PY4KIDS_RUNNER_ORIGIN?: string;
}
