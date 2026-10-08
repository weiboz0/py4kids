// The harness sources are bundled into the worker as text (esbuild's `text` loader).
declare module '*.py' {
  const source: string;
  export default source;
}
