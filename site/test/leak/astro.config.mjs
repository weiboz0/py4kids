// The poisoned-bundle leak build (plan 103 Phase B; site/test/leak.test.ts). The site's own
// config, plus one injected page that deliberately renders a forbidden field (`answer_md`): the
// regression that proves the leak scan catches a leak. Production builds never load this file.
import { fileURLToPath } from 'node:url';
import base from '../../astro.config.mjs';

const cacheDir = process.env.PY4KIDS_LEAK_CACHE;

export default {
  ...base,
  ...(cacheDir ? { cacheDir } : {}),
  integrations: [
    ...(base.integrations ?? []),
    {
      name: 'py4kids-leak-regression',
      hooks: {
        'astro:config:setup': ({ injectRoute }) => {
          injectRoute({
            pattern: '/leak-regression/',
            entrypoint: fileURLToPath(new URL('./regression.astro', import.meta.url)),
          });
        },
      },
    },
  ],
};
