# Generated PDFs

This folder collects every PDF the repository builds.
The PDFs are built artifacts: git ignores them (`output/**/*.pdf` in `.gitignore`), and only this README is committed.
Rebuild them with the scripts below; `scripts/ci-local.sh` runs both.
`build-pdf.sh` runs for every book on every CI run.
A book's editions (`build-book.sh`, then `publish-audit`) render only when the change touches that book, `tools/`, `scripts/`, `books.yaml`, `pyproject.toml` or `uv.lock`; otherwise CI prints `SKIP` for them.
An `aio` book's editions (`scripts/aio/build-book.sh`, then `python -m tools.aio.publish_audit`, both under `uv run --group aio`; design 014 D6) are routed by `tools/aio/ci_scope.py` instead.
They render in full when the change touches `tools/aio/` (not `tools/aio/tests/`), `scripts/aio/`, `books.yaml`, `pyproject.toml`, `uv.lock`, `scripts/ci-local.sh` or `.python-version`, or the book's `publication.yaml`, `front-matter/` or `back-matter/`.
A change to one unit or mock test renders a scoped check of just that unit or test into `<id>/build/publish-check/` and leaves these PDFs alone; an unchanged book prints `INFO build-book: <id> unchanged (change-routed)`.
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
| `usaco-bronze-student-print.pdf` | Student Book — Print Edition: the lean book for publication, with no answers | `scripts/build-book.sh --book usaco-bronze` |
| `usaco-bronze-student.pdf` | Student Book — Full Edition: the online book, with Answers to Selected Exercises | `scripts/build-book.sh --book usaco-bronze` |
| `usaco-bronze-answer-key.pdf` | Answer Key: answers to the odd-numbered unit exercises, one chapter per unit | `scripts/build-book.sh --book usaco-bronze` |
| `usaco-bronze-teacher.pdf` | Teacher's Edition: the book with teacher notes and every answer key | `scripts/build-book.sh --book usaco-bronze` |
| `syllabus.pdf` | The Contest Python: USACO Bronze syllabus | `scripts/build-pdf.sh --book usaco-bronze` |
| `handouts/<unit>.pdf` | One exercise handout per unit, printed from its `exercises.ipynb` | `scripts/build-pdf.sh --book usaco-bronze` |

`build-book.sh` replaces `usaco-bronze-*.pdf` (every edition is `<id>-<edition>.pdf`); `build-pdf.sh` replaces `syllabus.pdf` and `handouts/`.

## `output/acsl/` — Contest Python: ACSL

| File | What it is | Made by |
|---|---|---|
| `acsl-student-print.pdf` | Student Book — Print Edition: the lean book for publication, with no answers | `scripts/build-book.sh --book acsl` |
| `acsl-student.pdf` | Student Book — Full Edition: the online book, with Answers to Selected Exercises | `scripts/build-book.sh --book acsl` |
| `acsl-answer-key.pdf` | Answer Key: answers to the odd-numbered unit exercises, one chapter per unit | `scripts/build-book.sh --book acsl` |
| `acsl-teacher.pdf` | Teacher's Edition: the book with teacher notes and every answer key | `scripts/build-book.sh --book acsl` |
| `syllabus.pdf` | The Contest Python: ACSL syllabus | `scripts/build-pdf.sh --book acsl` |
| `handouts/<unit>.pdf` | One exercise handout per unit, printed from its `exercises.ipynb` | `scripts/build-pdf.sh --book acsl` |

`build-book.sh` replaces `acsl-*.pdf` (every edition is `<id>-<edition>.pdf`); `build-pdf.sh` replaces `syllabus.pdf` and `handouts/`.

## `output/recsys/` — Applied Python: Recommendation Systems

| File | What it is | Made by |
|---|---|---|
| `syllabus.pdf` | The Applied Python: Recommendation Systems syllabus | `scripts/build-pdf.sh --book recsys` |
| `handouts/<unit>.pdf` | One exercise handout per unit, printed from its `exercises.ipynb` | `scripts/build-pdf.sh --book recsys` |

`recsys` ships in **buildout** state (design 011): units, projects, and checkpoints — and therefore the handouts — land in `recsys-002+`.
It is not a `publication` book, so it renders no student/teacher editions; `build-pdf.sh` replaces `syllabus.pdf` and `handouts/`.

## `output/roar/` — Applied Python: Autonomous Racing

| File | What it is | Made by |
|---|---|---|
| `syllabus.pdf` | The Applied Python: Autonomous Racing syllabus | `scripts/build-pdf.sh --book roar` |
| `handouts/<unit>.pdf` | One exercise handout per unit, printed from its `exercises.ipynb` | `scripts/build-pdf.sh --book roar` |

`roar` ships in **buildout** state (design 013): units, checkpoints and the capstone, and therefore the handouts, land in `roar-002` and later.
It is not a `publication` book yet, so it renders no student/teacher editions; `build-pdf.sh` replaces `syllabus.pdf` and `handouts/`.

## `output/aio-ml/` — Machine Learning for the AI Olympiad

"Selected answers" in the two `aio` books are the Set A (fundamentals) practices, set by `student_answers:` in each book's `publication.yaml`.

| File | What it is | Made by |
|---|---|---|
| `aio-ml-student-print.pdf` | Student Book — Print Edition: lessons, reviews and practice statements (markdown only, with a pointer to each practice file); no answers of any kind | `scripts/aio/build-book.sh --book aio-ml` |
| `aio-ml-student-vol1.pdf` | Student Book — Full Edition, Volume 1: Foundations and First Models (units 01–08: F1–F5, C1–C3), with starter code and an appendix of checkpoint answers and selected-practice solutions | `scripts/aio/build-book.sh --book aio-ml` |
| `aio-ml-student-vol2.pdf` | Student Book — Full Edition, Volume 2: Practice, Embeddings, and Neural Networks (units 09–14: C4, C5, C6, F6, C7, F7) | `scripts/aio/build-book.sh --book aio-ml` |
| `aio-ml-student-vol3.pdf` | Student Book — Full Edition, Volume 3: Training, Deep Models, and Competition Practice (units 15–19: C8–C12) | `scripts/aio/build-book.sh --book aio-ml` |
| `aio-ml-answer-key.pdf` | Answer Key: the selected-practice solutions, one chapter per unit | `scripts/aio/build-book.sh --book aio-ml` |
| `aio-ml-teacher-vol1.pdf` | Teacher's Edition, Volume 1: Foundations and First Models, with every answer inline and every practice solution | `scripts/aio/build-book.sh --book aio-ml` |
| `aio-ml-teacher-vol2.pdf` | Teacher's Edition, Volume 2: Practice, Embeddings, and Neural Networks | `scripts/aio/build-book.sh --book aio-ml` |
| `aio-ml-teacher-vol3.pdf` | Teacher's Edition, Volume 3: Training, Deep Models, and Competition Practice, ending with the `r1-001` mock test, its answers, rubric and solutions | `scripts/aio/build-book.sh --book aio-ml` |
| `syllabus.pdf` | The Round 1 course structure (`aio-ml/docs/course-structure.md`) | `scripts/aio/build-pdf.sh --book aio-ml` |
| `handouts/<unit>.pdf` | One practice handout per unit: its practice statement notebooks, without answers | `scripts/aio/build-pdf.sh --book aio-ml` |
| `mocktests/r1-001-paper.pdf` | Mock test `r1-001`: `test.md`, then each problem file in manifest order | `scripts/aio/build-pdf.sh --book aio-ml` |
| `mocktests/r1-001-solutions.pdf` | Mock test `r1-001`: the answer key, rubric and solution notebooks | `scripts/aio/build-pdf.sh --book aio-ml` |

Both scripts run under `uv run --group aio`.
`build-book.sh` replaces `aio-ml-*.pdf` (every edition is `<id>-<edition>[-vol<N>].pdf`); `build-pdf.sh` replaces `syllabus.pdf`, `handouts/` and `mocktests/`.

## `output/aio-dl/` — Deep Learning for the AI Olympiad

| File | What it is | Made by |
|---|---|---|
| `aio-dl-student-print.pdf` | Student Book — Print Edition: lessons, reviews and practice statements (markdown only, with a pointer to each practice file); no answers of any kind | `scripts/aio/build-book.sh --book aio-dl` |
| `aio-dl-student.pdf` | Student Book — Full Edition: with starter code and an appendix of checkpoint answers and selected-practice solutions | `scripts/aio/build-book.sh --book aio-dl` |
| `aio-dl-answer-key.pdf` | Answer Key: the selected-practice solutions, one chapter per unit | `scripts/aio/build-book.sh --book aio-dl` |
| `aio-dl-teacher.pdf` | Teacher's Edition: every answer inline, every practice solution, and the `r2-001` mock test with its answers, rubric and solutions | `scripts/aio/build-book.sh --book aio-dl` |
| `syllabus.pdf` | The Round 2 course structure (`aio-dl/docs/course-structure.md`) | `scripts/aio/build-pdf.sh --book aio-dl` |
| `handouts/<unit>.pdf` | One practice handout per unit: its practice statement notebooks, without answers | `scripts/aio/build-pdf.sh --book aio-dl` |
| `mocktests/r2-001-paper.pdf` | Mock test `r2-001`: `test.md`, then each problem file in manifest order (theory and programming parts interleaved) | `scripts/aio/build-pdf.sh --book aio-dl` |
| `mocktests/r2-001-solutions.pdf` | Mock test `r2-001`: the answer key, rubric and solution notebooks | `scripts/aio/build-pdf.sh --book aio-dl` |

Both scripts run under `uv run --group aio`.
`build-book.sh` replaces `aio-dl-*.pdf`; `build-pdf.sh` replaces `syllabus.pdf`, `handouts/` and `mocktests/`.

## Publishing a release

The PDFs are published as GitHub Releases on `weiboz0/py4kids`, never committed.

1. Run `bash scripts/ci-local.sh --all-books` on the commit you release, on its own (never alongside another `ci-local.sh` run, which shares the build folders).
   It must end `ci-local: ALL GREEN`, with every book's editions rendered and audited.
2. Stage copies of the release PDFs outside the repository, each name prefixed with its book id, because handout names repeat across books.
   Stage only this allowlist:
   - every py4kids-model book's PDFs: `<id>-handout-<unit>.pdf`, `<id>-syllabus.pdf`, `python-projects-patterns.pdf`; the editions already start with the id (`<id>-<edition>.pdf`);
   - for an `aio` book (`aio-ml`, `aio-dl`), **only** its student editions (`<id>-student*.pdf`), its syllabus (`<id>-syllabus.pdf`), its handouts (`<id>-handout-<unit>.pdf`) and its mock-test papers (`output/<id>/mocktests/<test>-paper.pdf`, staged as `<id>-<test>-paper.pdf`).

   Never stage, for an `aio` book, `<id>-teacher*.pdf`, `<id>-answer-key.pdf` or any `mocktests/<test>-solutions.pdf`: they print the Set B/C answers and the mock-test solutions, and design 014 D7 releases only Set A answers and no mock-test solution.
3. Tag the release `pdfs-<date>` (for example `pdfs-2026-09-30`) and create it against the **full** commit SHA (a short SHA is refused):

   ```bash
   GH_TOKEN=$(cat .gh-token) gh release create pdfs-<date> --target <full SHA> \
     --title "Book PDFs <date>" --notes "…" <staged PDFs>
   ```

For the py4kids-model books, the Teacher's Edition is included in the release, by the user's choice (2026-09-29), even though the release is public.
That choice does not cover the `aio` books (step 2).

## The learning website (design 012; plan 105 Phase F)

Deployed to Cloudflare Pages from release `pdfs-2026-09-30` (`release_id` `9a1e6ecd…`) on 2026-10-22:

| Pages project | Serves | Address |
|---|---|---|
| `py4kids` | `site/dist/` | https://learn.futurespark.cc |
| `py4kids-run` | `runner/dist/` | https://run-learn.futurespark.cc |
| `py4kids-alias` | `deploy/alias/public/` | https://py4kids.futurespark.cc (301 to the site) |

Procedure: `scripts/build-release.sh <tag>`, then `scripts/deploy-pages.sh all` (token and account id from `.env`), then the live smoke test `pnpm -C site e2e:live`.
The smoke test checks the headers and `crossOriginIsolated`, runs a lesson cell, passes an expected-output check and a fixtures check, downloads a book to "Available offline", and follows the alias redirect.
On 2026-10-22 every step passed. The one failure was Cloudflare Web Analytics, automatically injected into the `futurespark.cc` zone's pages (blocked by the CSP, so nothing was collected); it must be disabled for the zone (the privacy page promises no analytics).
