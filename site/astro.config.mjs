// The learning website (design 012 part B; plan 103). A static build with no inline scripts or
// styles (the strict CSP, D9) and no integrations that load remote assets.
import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
  trailingSlash: 'always',
  build: {
    format: 'directory',
    // Every stylesheet is an external file: the CSP's style-src is 'self' only.
    inlineStylesheets: 'never',
  },
  // No dev toolbar overlay.
  devToolbar: { enabled: false },
  vite: {
    build: {
      // Never inline a script or asset as a data: URL or inline <script>.
      assetsInlineLimit: 0,
    },
  },
});
