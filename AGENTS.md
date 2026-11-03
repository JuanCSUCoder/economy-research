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
4. Fetch raw data and keep it immutable; transform with a committed script.
5. Write the report with figures, tables, methodology, and sources.
6. Add the economic theory (named model/mechanism), then conclusions clearly
   separated from evidence.

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
  `name` and `description` frontmatter. Supporting code in `scripts/`,
  documentation in `references/`. The ID comes from the path and is
  case-sensitive.
- Each source skill documents endpoint/portal, parameters, pagination, rate
  limits, auth (env vars only), output schema, and a `Last verified` date.
- Fetch scripts must be non-interactive and idempotent, cache raw responses,
  validate schema/row counts, and fail loudly. Do not commit secrets, cookies,
  session tokens, or large downloaded PDFs.
- When a source changes, update its skill instead of creating a parallel script.

Example IDs: `dane-ipc`, `banrep-trm`, `dian-importaciones`.

## Layout and commands

```text
src/econ_research/                  # package (bootstrap on first code task)
.opencode/skills/<id>/SKILL.md
data/raw/<source>/<YYYY-MM-DD>/     # immutable downloads
data/processed/                     # regenerable outputs
reports/<YYYY-MM-DD>-<slug>.es.md
reports/<YYYY-MM-DD>-<slug>.en.md
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
- `uv run python -m econ_research.<module>` for fetches and scheduled jobs.
- Create/update `.gitignore` (`.venv/`, `__pycache__/`, `.pytest_cache/`,
  `.ruff_cache/`, large `data/raw/**`) before the first code commit.
- There is no CI. Verification is local: `ruff` + `pytest`.

## Report structure

Spanish report: Resumen ejecutivo, Contexto, Datos y metodología, Resultados,
Teoría económica, Conclusiones, Limitaciones, Fuentes. English summary: 5–10
bullets mirroring the conclusions. Every chart/table states source, unit,
period, and nominal/real basis. Each claim links to a `Fuentes` entry with URL
and access date.

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
  commit the fetch script plus a manifest with URLs and checksums.
