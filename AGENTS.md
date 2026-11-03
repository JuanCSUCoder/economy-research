# AGENTS.md

Economic research workspace covering general economics and Colombia. Licensed
Apache-2.0. This file defines the layout and workflow; if `pyproject.toml` is
absent, bootstrap the package with the commands below.

## Deliverable language

- Full reports: Spanish (`*.es.md`). English summary: `*.en.md`.
- Code, comments, commit messages, and technical docs: English.
- Spanish prose uses Colombian conventions: `1.234,56`, ISO dates (`2026-11-03`).

## Required workflow

Follow this order for every research request. Do not jump from a question to a
conclusion.

1. Scope the question: period, geography, indicator, unit, nominal vs real,
   seasonal adjustment, and comparison base.
2. Locate primary sources and record them before extracting numbers.
3. Create or update a fetch skill under `.opencode/skills/` (see below) before
   writing a second ad-hoc downloader for the same source.
4. Fetch raw data and keep it immutable; transform with a committed script
   stored in the skill that owns the source.
5. Write the report with figures, tables, methodology, and sources.
6. Add the economic theory (named model/mechanism), then conclusions clearly
   separated from evidence.
7. Render each report to PDF with the `markdown-to-pdf` skill
   (`.opencode/skills/markdown-to-pdf/`). Both `.es.md` and `.en.md` get a PDF
   with the same base name. Regenerate the PDF whenever the Markdown changes;
   never edit a PDF by hand.
8. Verify the PDF: `pdfinfo` (Letter, page count), `pdffonts` (embedded
   DejaVu Sans), `pdftotext -layout` (accents, figures, and tables survived).
   If a figure is missing or a table overflows, fix the Markdown or the
   stylesheet and rebuild.

Never invent a figure, source, or date. Mark unavailable series as gaps. Label
official data, estimates, and opinion separately. Note base year, revisions, and
whether a series is nominal or real.

## Authoritative sources

- Colombia, primary: DANE (statistics and microdata), Banco de la República
  (monetary, FX, rates, surveys), Ministerio de Hacienda y Crédito Público
  (fiscal), DIAN (tax and trade), Superintendencia Financiera, DNP, Datos
  Abiertos Colombia.
- Multilateral: IMF, World Bank, OECD, ECLAC. Think tanks (e.g. Fedesarrollo)
  are secondary and must be labeled as such.
- Prefer the dataset, API, or microdata over press releases and news. Record
  dataset ID, URL, retrieval timestamp, frequency, unit, and last update.

## Skills (OpenCode standard)

- One skill per source/portal: `.opencode/skills/<kebab-case-id>/SKILL.md` with
  `name` and `description` frontmatter. Documentation in `references/`. The ID
  comes from the path and is case-sensitive.
- **Every script lives in the skill that owns it**, under
  `.opencode/skills/<id>/scripts/`. Do not create a repo-root `scripts/`
  directory or a separate module just to host a fetcher. `src/econ_research/` is
  only for shared, source-agnostic analysis code.
- Each source skill documents endpoint/portal, parameters, pagination, rate
  limits, auth (env vars only), output schema, and a `Last verified` date.
- Fetch scripts must be non-interactive and idempotent, cache raw responses,
  validate schema/row counts, and fail loudly. Do not commit secrets, cookies,
  session tokens, or large downloaded PDFs.
- When a source changes, update its skill instead of creating a parallel script.

Example IDs: `dane-ipc`, `banrep-trm`, `dian-importaciones`.

### Skills in this workspace

- `colombia-fiscal`: CARF, MHCP, DANE and Banco de la República. Fetcher:
  `.opencode/skills/colombia-fiscal/scripts/fetch_fiscal.sh`.
- `congreso-proyectos-ley`: Cámara/Senado bills, status and article index.
  Fetcher: `.opencode/skills/congreso-proyectos-ley/scripts/fetch_bill.py`.
- `markdown-to-pdf`: builds the Letter/DejaVu PDF from the Markdown report.
- `install-pdf-tools`: restores Pandoc, WeasyPrint, poppler and DejaVu.

Shared, source-agnostic chart code lives in `src/econ_research/make_charts.py`
and reads `data/processed/`. Keep fetchers inside their skill.

## Layout and commands

```text
.opencode/skills/<id>/SKILL.md
.opencode/skills/<id>/scripts/      # fetchers, parsers, chart builders
.opencode/skills/<id>/references/
src/econ_research/                  # shared analysis code only, no fetchers
data/raw/<source>/<YYYY-MM-DD>/     # immutable downloads
data/processed/                     # regenerable outputs
reports/<YYYY-MM-DD>-<slug>.es.md
reports/<YYYY-MM-DD>-<slug>.es.pdf
reports/<YYYY-MM-DD>-<slug>.en.md
reports/<YYYY-MM-DD>-<slug>.en.pdf
tests/
```

- Toolchain: `uv` + `pyproject.toml`, Python 3.13. If `uv` is missing, install
  it (`curl -LsSf https://astral.sh/uv/install.sh | sh`) rather than falling
  back to system `pip`.
- Bootstrap once: `uv init --package --name econ-research`, then `uv add` only
  the libraries a source actually needs (`httpx`, `pandas`/`polars`, `openpyxl`,
  `beautifulsoup4`, `pypdf`). Dev deps: `pytest`, `ruff`, `respx`.
- `uv sync --all-groups`
- `uv run ruff format . && uv run ruff check .`
- `uv run pytest`; single test: `uv run pytest tests/test_file.py::test_name`
- `uv run python .opencode/skills/<id>/scripts/<script>.py` for skill scripts;
  shell fetchers run as `bash .opencode/skills/<id>/scripts/<script>.sh`.
- `uv run python -m econ_research.<module>` for shared analysis code.
- Create/update `.gitignore` (`.venv/`, `__pycache__/`, `.pytest_cache/`,
  `.ruff_cache/`, large `data/raw/**`) before the first code commit.
- There is no CI. Verification is local: `ruff` + `pytest`.

## Report structure

Spanish report: Resumen ejecutivo, Contexto, Datos y metodología, Resultados,
Teoría económica, Conclusiones, Limitaciones, Referencias. English summary: 5–10
bullets mirroring the conclusions. Every chart/table states source, unit,
period, and nominal/real basis. Each claim cites an APA 7 reference in
`Referencias`, with URL and access date. Every report ships as `.md` + `.pdf`
with the same base name;
the PDF is the print artifact (Letter, DejaVu Sans, no cover page, no page
numbers unless requested).

## Gotchas

- Colombian series use different base years and revision vintages; never splice
  series without an explicit note.
- DANE and Banco de la República revise data. Never overwrite `data/raw/`; a new
  download gets a new date directory.
- For FX, distinguish the official TRM from market rates; for inflation,
  distinguish IPC, deflator, and IPP, and monthly from annual.
- Schedule jobs in `America/Bogota` (UTC-5, no DST); store timestamps in UTC
  ISO 8601.
- Keep raw downloads out of Git unless small and redistributable. Otherwise
  commit the skill's fetch script plus a manifest with URLs and checksums.
