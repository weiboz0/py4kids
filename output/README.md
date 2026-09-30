# Generated PDFs

This folder collects every PDF the repository builds.
The PDFs are built artifacts: git ignores them (`output/**/*.pdf` in `.gitignore`), and only this README is committed.
Rebuild them with the scripts below; `scripts/ci-local.sh` runs both.
`build-pdf.sh` runs for every book on every CI run.
A book's editions (`build-book.sh`, then `publish-audit`) render only when the change touches that book, `tools/`, `scripts/` or `books.yaml`; otherwise CI prints `SKIP` for them.
`scripts/ci-local.sh --all-books` renders every book's editions.

Each script owns its own files and replaces only those, so running one never deletes the other's PDFs.
`<id>/build/` keeps the intermediate files (Quarto projects, logs, TeX).
Folders and PDF file names use the book id from `books.yaml`; the PDFs themselves show each book's title.

## `output/python-projects/` — Python by Projects

| File | What it is | Made by |
|---|---|---|
| `python-projects-student-print.pdf` | Student Book — Print Edition: the lean book for publication, with no answers and only the Starters that print needed code | `scripts/build-book.sh --book python-projects` |
| `python-projects-student.pdf` | Student Book — Full Edition: the online book, with every Starter and Answers to Selected Exercises | `scripts/build-book.sh --book python-projects` |
| `python-projects-answer-key.pdf` | Answer Key: answers to the odd-numbered unit exercises, one chapter per unit | `scripts/build-book.sh --book python-projects` |
| `python-projects-teacher.pdf` | Teacher's Edition: the book with teacher notes and every answer key | `scripts/build-book.sh --book python-projects` |
| `syllabus.pdf` | The Python by Projects syllabus | `scripts/build-pdf.sh --book python-projects` |
| `patterns.pdf` | The Python by Projects patterns reference | `scripts/build-pdf.sh --book python-projects` |
| `handouts/<unit>.pdf` | One exercise handout per unit, printed from its `exercises.ipynb` | `scripts/build-pdf.sh --book python-projects` |

`build-book.sh` replaces `python-projects-*.pdf` (every edition is `<id>-<edition>.pdf`); `build-pdf.sh` replaces `syllabus.pdf`, `patterns.pdf` and `handouts/`.

## `output/python-concepts/` — Python, Concept by Concept

| File | What it is | Made by |
|---|---|---|
| `python-concepts-student-print.pdf` | Student Book — Print Edition: the lean book for publication, with no answers and only the Starters that print needed code | `scripts/build-book.sh --book python-concepts` |
| `python-concepts-student.pdf` | Student Book — Full Edition: the online book, with every Starter and Answers to Selected Exercises | `scripts/build-book.sh --book python-concepts` |
| `python-concepts-answer-key.pdf` | Answer Key: answers to the odd-numbered unit exercises, one chapter per unit | `scripts/build-book.sh --book python-concepts` |
| `python-concepts-teacher.pdf` | Teacher's Edition: the book with teacher notes and every answer key | `scripts/build-book.sh --book python-concepts` |
| `syllabus.pdf` | The Python, Concept by Concept syllabus | `scripts/build-pdf.sh --book python-concepts` |
| `handouts/<unit>.pdf` | One exercise handout per unit, printed from its `exercises.ipynb` | `scripts/build-pdf.sh --book python-concepts` |

`build-book.sh` replaces `python-concepts-*.pdf` (every edition is `<id>-<edition>.pdf`); `build-pdf.sh` replaces `syllabus.pdf` and `handouts/`.

## `output/usaco-bronze/` — Contest Python: USACO Bronze

| File | What it is | Made by |
|---|---|---|
| `usaco-bronze-student-print.pdf` | Student Book — Print Edition: the lean book for publication, with no answers and only the Starters that print needed code | `scripts/build-book.sh --book usaco-bronze` |
| `usaco-bronze-student.pdf` | Student Book — Full Edition: the online book, with every Starter and Answers to Selected Exercises | `scripts/build-book.sh --book usaco-bronze` |
| `usaco-bronze-answer-key.pdf` | Answer Key: answers to the odd-numbered unit exercises, one chapter per unit | `scripts/build-book.sh --book usaco-bronze` |
| `usaco-bronze-teacher.pdf` | Teacher's Edition: the book with teacher notes and every answer key | `scripts/build-book.sh --book usaco-bronze` |
| `syllabus.pdf` | The Contest Python: USACO Bronze syllabus | `scripts/build-pdf.sh --book usaco-bronze` |
| `handouts/<unit>.pdf` | One exercise handout per unit, printed from its `exercises.ipynb` | `scripts/build-pdf.sh --book usaco-bronze` |

`build-book.sh` replaces `usaco-bronze-*.pdf` (every edition is `<id>-<edition>.pdf`); `build-pdf.sh` replaces `syllabus.pdf` and `handouts/`.

## `output/acsl/` — Contest Python: ACSL

| File | What it is | Made by |
|---|---|---|
| `acsl-student-print.pdf` | Student Book — Print Edition: the lean book for publication, with no answers and only the Starters that print needed code | `scripts/build-book.sh --book acsl` |
| `acsl-student.pdf` | Student Book — Full Edition: the online book, with every Starter and Answers to Selected Exercises | `scripts/build-book.sh --book acsl` |
| `acsl-answer-key.pdf` | Answer Key: answers to the odd-numbered unit exercises, one chapter per unit | `scripts/build-book.sh --book acsl` |
| `acsl-teacher.pdf` | Teacher's Edition: the book with teacher notes and every answer key | `scripts/build-book.sh --book acsl` |
| `syllabus.pdf` | The Contest Python: ACSL syllabus | `scripts/build-pdf.sh --book acsl` |
| `handouts/<unit>.pdf` | One exercise handout per unit, printed from its `exercises.ipynb` | `scripts/build-pdf.sh --book acsl` |

`build-book.sh` replaces `acsl-*.pdf` (every edition is `<id>-<edition>.pdf`); `build-pdf.sh` replaces `syllabus.pdf` and `handouts/`.

## Publishing a release

The PDFs are published as GitHub Releases on `weiboz0/py4kids`, never committed.

1. Run `bash scripts/ci-local.sh --all-books` on the commit you release, on its own (never alongside another `ci-local.sh` run, which shares the build folders).
   It must end `ci-local: ALL GREEN`, with every book's editions rendered and audited.
2. Stage copies of every book's PDFs outside the repository, each name prefixed with its book id, because handout names repeat across books:
   `<id>-handout-<unit>.pdf`, `<id>-syllabus.pdf`, `python-projects-patterns.pdf`; the editions already start with the id (`<id>-<edition>.pdf`).
3. Tag the release `pdfs-<date>` (for example `pdfs-2026-09-30`) and create it against the **full** commit SHA (a short SHA is refused):

   ```bash
   GH_TOKEN=$(cat .gh-token) gh release create pdfs-<date> --target <full SHA> \
     --title "Book PDFs <date>" --notes "…" <staged PDFs>
   ```

The Teacher's Edition is included in the release, by the user's choice (2026-09-29), even though the release is public.
