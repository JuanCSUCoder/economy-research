---
name: colombia-fiscal
description: Fetch and validate Colombian fiscal and macroeconomic data from CARF, Ministerio de Hacienda, DANE and Banco de la República, keeping raw downloads immutable and documented. Use for GNC deficit, debt, primary balance, fiscal rule, CPI, GDP and monetary policy series.
---

# Colombia fiscal data

Primary-source workflow for Colombian fiscal and macro data. The aim is to avoid
ad-hoc downloads and to keep a reproducible trail from the official PDF/API to the
report.

## Sources and endpoints

| Source | What it provides | Entry point | Format |
|---|---|---|---|
| CARF | Fiscal rule monitoring, GNC balance, debt, medium-term projections | https://www.carf.gov.co | PDF |
| Ministerio de Hacienda (MHCP) | Plan Financiero, MFMP, Cierre Fiscal GNC, PGN | https://www.minhacienda.gov.co/politica-fiscal | PDF / XLSX |
| DANE | GDP, CPI, GEIH, poverty | https://www.dane.gov.co | PDF / XLSX |
| Banco de la República | Board report to Congress, policy rate, expectations | https://www.banrep.gov.co | PDF |
| Congreso | PGN, bills, committee status | https://www.camara.gov.co / https://www.senado.gov.co | PDF / HTML |

### Known direct URLs (verified 2026-11-03)

- CARF, *Seguimiento Fiscal*, September 2026:
  `https://www.valoraanalitik.com/wp-content/uploads/2026/09/Seguimiento-fiscal-Septiembre-2026.pdf`
  (mirror; the CARF site is the authoritative source but links rotate).
- CARF, technical note on the 2026 MFMP:
  `https://www.camara.gov.co/wp-content/uploads/2026/07/informes_comision/4/Documento-tecnico-CARF-MFMP-2026_5097.pdf`
- MHCP, Cierre Fiscal GNC 2024:
  `https://www.minhacienda.gov.co/documents/d/portal/cierre-fiscal-gnc-2024`
- DANE, GDP Q4 2025:
  `https://www.dane.gov.co/files/operaciones/PIB/cp-PIB-IVtrim2025.pdf`
- DANE, CPI December 2025:
  `https://www.dane.gov.co/files/operaciones/IPC/dic2025/cp-IPC-dic2025.pdf`
- DANE, poverty 2025:
  `https://www.dane.gov.co/files/operaciones/PM/cp-PM-2025.pdf`
- Banco de la República, Board report October 2026:
  `https://www.banrep.gov.co/sites/default/files/publicaciones/archivos/resumen-infografico-congreso-octubre-2026.pdf`

## Parameters and conventions

- **Coverage:** always state whether the figure is GNC, Gobierno General or SPNF.
  The fiscal rule uses GNC net debt. Mixing coverages is the most common error.
- **Definitions:** total balance includes interest; primary balance excludes it;
  net debt = gross debt − financial assets. `BPNE` is the structural primary balance.
- **Nominal vs real:** fiscal ratios use nominal GDP. GDP growth is real, base 2015.
- **Vintages:** DANE and MHCP revise. Never overwrite `data/raw/`; a new download
  gets a new `YYYY-MM-DD` directory. Note the vintage in the report.
- **OMD:** debt management operations can reduce recorded interest in a given year.
  Check the footnote before comparing interest/GDP across years.
- **Billions:** Colombian `billón` = 10^12. Keep the convention in Spanish reports.
- **Dates:** ISO 8601 (`2026-11-03`); timestamps in UTC; schedules in
  `America/Bogota`.

## Pagination, rate limits, auth

- No API keys. Public PDFs and HTML pages.
- Be polite: one request per second, `User-Agent` identifying the research project.
- No pagination for PDFs; for DANE XLSX use the direct file URL.
- If a page is JS-rendered (e.g. Minhacienda document library), use the direct
  `documents/d/portal/...` URL or the Camara mirror instead of scraping the HTML.

## Output schema

Store each download under `data/raw/<source>/<YYYY-MM-DD>/` with:

```text
<source>/<YYYY-MM-DD>/
  <slug>.pdf
  <slug>.txt          # pdftotext -layout, for grepping
  manifest.csv        # url, sha256, bytes, content_type, retrieved_at
```

Processed series go to `data/processed/<name>.csv` with a `fuente` and `estado`
column (`observado`, `proyeccion oficial`, `estimacion CARF`).

## Scripts

All scripts for this source live in this skill, never in a repo-root `scripts/`
directory.

### Fetch

`scripts/fetch_fiscal.sh` downloads the core set, verifies the PDF magic bytes,
extracts text, writes a manifest and refuses to overwrite an existing file unless
`--force` is passed. Run it from the repository root:

```bash
bash .opencode/skills/colombia-fiscal/scripts/fetch_fiscal.sh            # idempotent
bash .opencode/skills/colombia-fiscal/scripts/fetch_fiscal.sh --force    # re-download today's set
```

The script is intentionally verbose and fails with a non-zero exit code if any
download is not a PDF or is smaller than 10 KB. It resolves the repo root from
its own location; override with `REPO_ROOT=/path/to/repo` when needed.

### Charts

`scripts/make_charts.py` turns `data/processed/gnc_balance_2021_2027.csv` into
the report SVGs under `reports/figures/`. It uses only the standard library:

```bash
python3 .opencode/skills/colombia-fiscal/scripts/make_charts.py
```

Regenerate the charts after changing the processed CSV, then rebuild the report
PDFs with the `markdown-to-pdf` skill.

## Validation checklist

1. `head -c 4 file.pdf` returns `%PDF`.
2. `pdftotext -layout` produces more than 50 lines.
3. The first page text contains the expected title and date.
4. The figure appears in the document with the same coverage (GNC vs GG).
5. Record the retrieval timestamp and the document's own date.

## Gotchas

- The Minhacienda document library is a JS app; direct links end in
  `documents/d/portal/<slug>` and often require `?download=true`.
- CARF PDFs are sometimes hosted on third-party mirrors; cite the CARF site and
  keep the mirror URL in the manifest.
- The 2026-2027 figures are projections; do not present them as observed.
- The 2025 interest ratio is distorted by OMD; use 2024 or 2027 for comparisons.
- DANE revised 2023 growth to 0.8% and 2024 to 1.5% in 2026; old reports may say
  0.6% and 1.7%. Check the vintage.

**Last verified:** 2026-11-03
