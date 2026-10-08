/**
 * The export/import island (design 012 D11; plan 105 Phase C; markup in
 * src/components/ProgressTransfer.astro). Everything happens on the device.
 *
 * Saving the export, in order of preference:
 * 1. `showSaveFilePicker` (the File System Access API), where present. It is opened first, inside
 *    the click, because it needs the click's user activation.
 * 2. The Web Share API with a file (iOS and Android, including installed PWAs), when
 *    `navigator.canShare({files})` says yes.
 * 3. A download link: `<a download>` on a `blob:` URL. A download is a navigation, which the CSP's
 *    fetch directives do not govern, so the CSP needs no change.
 *
 * After an import the page's "Continue" links are refreshed (`PROGRESS_IMPORTED_EVENT`).
 */

import { PROGRESS_IMPORTED_EVENT } from '../lib/dom-events';
import { exportFileName, exportProgress, ImportError, importProgress, readImportFile, type MergeSummary } from '../lib/progress-io';
import { sharedProgress } from '../lib/progress';

interface WritableFile {
  write(data: Blob): Promise<void>;
  close(): Promise<void>;
}
interface SaveFileHandle {
  createWritable(): Promise<WritableFile>;
}
type SaveFilePicker = (options: {
  suggestedName: string;
  types: { description: string; accept: Record<string, string[]> }[];
}) => Promise<SaveFileHandle>;

type Saved = 'saved' | 'shared' | 'downloaded' | 'cancelled';

const isAbort = (error: unknown) => error instanceof DOMException && error.name === 'AbortError';

function download(blob: Blob, name: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = name;
  link.hidden = true;
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 60_000);
}

async function save(build: () => Promise<string>, name: string): Promise<Saved> {
  const picker = (window as unknown as { showSaveFilePicker?: SaveFilePicker }).showSaveFilePicker;
  if (typeof picker === 'function') {
    let handle: SaveFileHandle | undefined;
    try {
      handle = await picker.call(window, {
        suggestedName: name,
        types: [{ description: 'py4kids progress', accept: { 'application/json': ['.json'] } }],
      });
    } catch (error) {
      if (isAbort(error)) return 'cancelled';
      // Refused (no user activation, a sandbox): fall through to sharing or a download.
    }
    if (handle) {
      const writable = await handle.createWritable();
      await writable.write(new Blob([await build()], { type: 'application/json' }));
      await writable.close();
      return 'saved';
    }
  }
  const blob = new Blob([await build()], { type: 'application/json' });
  const file = new File([blob], name, { type: 'application/json' });
  if (typeof navigator.share === 'function' && typeof navigator.canShare === 'function' && navigator.canShare({ files: [file] })) {
    try {
      await navigator.share({ files: [file], title: 'py4kids progress' });
      return 'shared';
    } catch (error) {
      if (isAbort(error)) return 'cancelled';
      // Not allowed (the click's activation expired): fall back to a download.
    }
  }
  download(blob, name);
  return 'downloaded';
}

const plural = (n: number, one: string, many: string) => `${n} ${n === 1 ? one : many}`;

function importMessage(summary: MergeSummary): string {
  const parts: string[] = [];
  if (summary.events) parts.push(plural(summary.events, 'result', 'results'));
  if (summary.cards) parts.push(plural(summary.cards, 'quiz card', 'quiz cards'));
  if (summary.resume) parts.push(plural(summary.resume, 'reading place', 'reading places'));
  if (summary.attempts) parts.push(plural(summary.attempts, 'code attempt', 'code attempts'));
  if (parts.length === 0) return 'Import finished: this device already had everything in that file, so nothing changed.';
  const list = parts.length === 1 ? parts[0] : `${parts.slice(0, -1).join(', ')} and ${parts.at(-1)}`;
  return `Import finished: brought back ${list}.`;
}

function main(): void {
  const section = document.querySelector<HTMLElement>('[data-transfer]');
  if (!section) return;
  const status = section.querySelector<HTMLElement>('[data-transfer-status]')!;
  const exportButton = section.querySelector<HTMLButtonElement>('[data-transfer-export]')!;
  const attempts = section.querySelector<HTMLInputElement>('[data-transfer-attempts]')!;
  const input = section.querySelector<HTMLInputElement>('[data-transfer-import]')!;

  const say = (text: string, kind: 'ok' | 'error' | 'busy') => {
    status.textContent = text;
    status.dataset.state = kind;
  };

  exportButton.addEventListener('click', () => {
    const options = { attempts: attempts.checked };
    const now = new Date();
    exportButton.disabled = true;
    say('Preparing your progress file…', 'busy');
    save(async () => exportProgress(await sharedProgress(), options, now), exportFileName(options, now))
      .then((saved) => {
        const what = options.attempts ? 'your progress and code attempts were' : 'your progress was';
        const name = exportFileName(options, now);
        if (saved === 'cancelled') say('Export cancelled: no file was saved.', 'ok');
        else if (saved === 'shared') say(`Export finished: ${what} shared as ${name}.`, 'ok');
        else if (saved === 'saved') say(`Export finished: ${what} saved.`, 'ok');
        else say(`Export finished: ${what} downloaded as ${name}.`, 'ok');
      })
      .catch((error: unknown) => {
        console.warn('py4kids export:', error);
        say('Sorry, the export did not work. Nothing was changed; please try again.', 'error');
      })
      .finally(() => {
        exportButton.disabled = false;
      });
  });

  input.addEventListener('change', () => {
    const file = input.files?.[0];
    if (!file) return;
    say(`Reading ${file.name}…`, 'busy');
    (async () => {
      const data = await readImportFile(file);
      return importProgress(await sharedProgress(), data);
    })()
      .then((summary) => {
        say(importMessage(summary), 'ok');
        document.dispatchEvent(new CustomEvent(PROGRESS_IMPORTED_EVENT, { detail: summary }));
      })
      .catch((error: unknown) => {
        if (error instanceof ImportError) {
          if (error.details.length) console.warn('py4kids import:', error.details.slice(0, 20));
          say(error.message, 'error');
        } else {
          console.warn('py4kids import:', error);
          say('Sorry, the import did not work. Nothing was changed; please try again.', 'error');
        }
      })
      .finally(() => {
        // Clear the choice, so choosing the same file again imports it again.
        input.value = '';
      });
  });
}

main();
