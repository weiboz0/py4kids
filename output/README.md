# Generated PDFs

This folder collects every PDF the repository builds.
The PDFs are built artifacts: git ignores them (`output/**/*.pdf` in `.gitignore`), and only this README is committed.
Rebuild them with the scripts below; `scripts/ci-local.sh` runs both.

Each script owns its own files and replaces only those, so running one never deletes the other's PDFs.
`bookN/build/` keeps the intermediate files (Quarto projects, logs, TeX).

## `output/book1b/`

| File | What it is | Made by |
|---|---|---|
| `Book1b-Student-Print.pdf` | Student Book — Print Edition: the lean book for publication, with no answers and only the Starters that print needed code | `scripts/build-book.sh --book book1b` |
| `Book1b-Student.pdf` | Student Book — Full Edition: the online book, with every Starter and Answers to Selected Exercises | `scripts/build-book.sh --book book1b` |
| `Book1b-Answer-Key.pdf` | Answer Key: answers to the odd-numbered unit exercises, one chapter per unit | `scripts/build-book.sh --book book1b` |
| `Book1b-Teacher.pdf` | Teacher's Edition: the book with teacher notes and every answer key | `scripts/build-book.sh --book book1b` |
| `syllabus.pdf` | The Book 1b syllabus | `scripts/build-pdf.sh --book book1b` |
| `handouts/<unit>.pdf` | One exercise handout per unit, printed from its `exercises.ipynb` | `scripts/build-pdf.sh --book book1b` |

`build-book.sh` replaces `Book*-*.pdf`; `build-pdf.sh` replaces `syllabus.pdf` and `handouts/`.

## `output/book1/`

| File | What it is | Made by |
|---|---|---|
| `syllabus.pdf` | The Book 1 syllabus | `scripts/build-pdf.sh --book book1` |
| `patterns.pdf` | The Book 1 patterns reference | `scripts/build-pdf.sh --book book1` |
| `handouts/<unit>.pdf` | One exercise handout per unit, printed from its `exercises.ipynb` | `scripts/build-pdf.sh --book book1` |

`build-pdf.sh` replaces `syllabus.pdf`, `patterns.pdf` and `handouts/`.
