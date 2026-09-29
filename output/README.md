# Generated PDFs

This folder collects every PDF the repository builds.
The PDFs are built artifacts: git ignores them (`output/**/*.pdf` in `.gitignore`), and only this README is committed.
Rebuild them with the scripts below; `scripts/ci-local.sh` runs both.

Each script owns its own files and replaces only those, so running one never deletes the other's PDFs.
`<id>/build/` keeps the intermediate files (Quarto projects, logs, TeX).
Folders and PDF file names use the book id from `books.yaml`; the PDFs themselves show each book's title.

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

## `output/python-projects/` — Python by Projects

| File | What it is | Made by |
|---|---|---|
| `syllabus.pdf` | The Python by Projects syllabus | `scripts/build-pdf.sh --book python-projects` |
| `patterns.pdf` | The Python by Projects patterns reference | `scripts/build-pdf.sh --book python-projects` |
| `handouts/<unit>.pdf` | One exercise handout per unit, printed from its `exercises.ipynb` | `scripts/build-pdf.sh --book python-projects` |

`build-pdf.sh` replaces `syllabus.pdf`, `patterns.pdf` and `handouts/`.
