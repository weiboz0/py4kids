/// <reference types="astro/client" />

// Astro's client types, declared here so a fresh checkout type-checks before `astro sync`
// writes .astro/types.d.ts (gitignored).

interface ImportMetaEnv {
  /** The primary runner origin, defined at build time by astro.config.mjs (deploy/origins.json). */
  readonly PY4KIDS_RUNNER_ORIGIN?: string;
  /** Every site/runner origin pair the build accepts (a production build adds the preview pair). */
  readonly PY4KIDS_ORIGIN_PAIRS?: { site: string; runner: string }[];
  /** True only in a test build (PY4KIDS_TEST_HOOKS=1): the update handshake's test hooks. */
  readonly PY4KIDS_TEST_HOOKS?: boolean;
}
