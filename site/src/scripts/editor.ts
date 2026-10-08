/**
 * The code editor under the strict CSP (plan 104 Phase B): CodeMirror 6, bundled (self-hosted),
 * mounted in a shadow root. CodeMirror injects its theme through `style-mod`, which writes a
 * `<style>` element for a Document root (blocked by `style-src 'self'`) but uses a constructable
 * stylesheet (`adoptedStyleSheets`, CSSOM, which CSP does not govern) for a ShadowRoot; its
 * runtime `element.style` writes are CSSOM too. e2e/checks.spec.ts proves zero CSP violations
 * while the editor is opened, typed in, scrolled and highlighted.
 *
 * The page renders an ordinary `<textarea>` holding the starter, so the item works before (and
 * without) this module: it is the editor's accessible fallback, with Tab inserting four spaces
 * (Escape, then Tab, leaves the field). When CodeMirror mounts, the textarea is hidden.
 * CodeMirror is loaded with a dynamic import, so pages without an editor never fetch it.
 */

export interface CodeEditor {
  readonly kind: 'codemirror' | 'textarea';
  getValue(): string;
  setValue(text: string): void;
  focus(): void;
}

/** Tab inserts `insert` at the caret; Escape, then Tab, moves focus on as usual. */
export function tabInserts(field: HTMLTextAreaElement, insert: string): void {
  let escaped = false;
  field.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      escaped = true;
      return;
    }
    if (event.key !== 'Tab' || event.shiftKey || event.altKey || event.ctrlKey || event.metaKey) {
      if (event.key !== 'Shift') escaped = false;
      return;
    }
    if (escaped) {
      escaped = false;
      return;
    }
    event.preventDefault();
    const { selectionStart: start, selectionEnd: end, value } = field;
    field.value = value.slice(0, start) + insert + value.slice(end);
    field.selectionStart = field.selectionEnd = start + insert.length;
    field.dispatchEvent(new Event('input', { bubbles: true }));
  });
}

/** The textarea itself as the editor (the fallback). */
export function textareaEditor(field: HTMLTextAreaElement): CodeEditor {
  tabInserts(field, '    ');
  return {
    kind: 'textarea',
    getValue: () => field.value,
    setValue: (text) => {
      field.value = text;
    },
    focus: () => field.focus(),
  };
}

/**
 * Mount CodeMirror in a shadow root beside `field` and hide the field; falls back to the field
 * itself if CodeMirror cannot load. `label` names the editor for assistive technology.
 */
export async function mountEditor(field: HTMLTextAreaElement, label: string): Promise<CodeEditor> {
  try {
    const [{ EditorView, keymap, lineNumbers, highlightActiveLine, drawSelection }, { EditorState }, commands, language, { python }, { tags }] =
      await Promise.all([
        import('@codemirror/view'),
        import('@codemirror/state'),
        import('@codemirror/commands'),
        import('@codemirror/language'),
        import('@codemirror/lang-python'),
        import('@lezer/highlight'),
      ]);
    // Token colours are the site's tokens (src/styles/checks.css), which inherit into the shadow
    // root, so they follow the light and dark themes with accessible contrast.
    const highlight = language.HighlightStyle.define([
      { tag: [tags.keyword, tags.controlKeyword, tags.operatorKeyword, tags.definitionKeyword, tags.moduleKeyword], color: 'var(--code-keyword)' },
      { tag: [tags.string, tags.special(tags.string)], color: 'var(--code-string)' },
      { tag: [tags.number, tags.bool, tags.null], color: 'var(--code-number)' },
      { tag: [tags.comment, tags.lineComment], color: 'var(--code-comment)', fontStyle: 'italic' },
      { tag: [tags.function(tags.variableName), tags.function(tags.definition(tags.variableName)), tags.definition(tags.className)], color: 'var(--code-function)' },
      { tag: tags.invalid, color: 'var(--code-keyword)' },
    ]);
    const host = document.createElement('div');
    host.className = 'code-editor';
    const root = host.attachShadow({ mode: 'open' });
    field.after(host);
    const theme = EditorView.theme({
      '&': {
        color: 'var(--text)',
        backgroundColor: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: '6px',
        fontSize: '0.95rem',
      },
      '&.cm-focused': { outline: '3px solid var(--focus)', outlineOffset: '2px' },
      '.cm-scroller': { fontFamily: 'var(--font-code)', lineHeight: '1.5', maxHeight: '28rem', overflow: 'auto' },
      '.cm-content': { caretColor: 'var(--text)', minHeight: '6rem' },
      '.cm-gutters': { backgroundColor: 'var(--surface)', color: 'var(--muted)', borderRight: '1px solid var(--border)' },
      '.cm-activeLine': { backgroundColor: 'transparent' },
      '&.cm-focused .cm-activeLine': { backgroundColor: 'rgba(128, 128, 128, 0.12)' },
      '&.cm-focused .cm-selectionBackground, .cm-selectionBackground, ::selection': { backgroundColor: 'rgba(80, 140, 255, 0.35)' },
      '.cm-cursor': { borderLeftColor: 'var(--text)' },
    });
    const view = new EditorView({
      root,
      parent: root,
      state: EditorState.create({
        doc: field.value,
        extensions: [
          lineNumbers(),
          drawSelection(),
          highlightActiveLine(),
          commands.history(),
          language.indentOnInput(),
          language.bracketMatching(),
          language.syntaxHighlighting(highlight),
          python(),
          EditorState.tabSize.of(4),
          language.indentUnit.of('    '),
          // Tab indents; Escape, then Tab, leaves the editor (CodeMirror's own tab-focus rule).
          keymap.of([...commands.defaultKeymap, ...commands.historyKeymap, commands.indentWithTab]),
          EditorView.contentAttributes.of({ 'aria-label': label }),
          theme,
        ],
      }),
    });
    field.hidden = true;
    host.dataset.editor = 'codemirror';
    return {
      kind: 'codemirror',
      getValue: () => view.state.doc.toString(),
      setValue: (text) => view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: text } }),
      focus: () => view.focus(),
    };
  } catch (error) {
    console.warn('py4kids editor: CodeMirror unavailable, using the plain editor', error);
    return textareaEditor(field);
  }
}
