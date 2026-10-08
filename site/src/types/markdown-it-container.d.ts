// markdown-it-container ships no types, and @types/markdown-it-container pins the obsolete
// @types/markdown-it (markdown-it 15 ships its own). The one call the site makes:
declare module 'markdown-it-container' {
  import type { MarkdownIt, RendererRule } from 'markdown-it';

  interface ContainerOptions {
    marker?: string;
    validate?: (params: string) => boolean;
    render?: RendererRule;
  }

  export default function container(md: MarkdownIt, name: string, options?: ContainerOptions): void;
}
