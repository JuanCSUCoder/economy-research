---
name: congreso-proyectos-ley
description: Locate, download and index Colombian bills from the Cámara de Representantes and Senado portals, including the Ley de Rescate Económico (PL 477 de 2026). Use to get the authoritative PDF, the legislative status, the article headings and the metadata needed to cite a bill before it becomes law.
---

# Colombian bills (Cámara / Senado)

Workflow for pulling a bill's authoritative text and status from the Congress
portals. The key rule: a bill is **not law** until the four debates, conciliation
and presidential sanction are complete. Cite the project number and the date of
radication, not a invented law number.

## Portals and URL patterns

| What | Where | Notes |
|---|---|---|
| Bill file (ficha) | `https://www.camara.gov.co/ley-<slug>/` | Status, authors, date, type, object |
| PDF (Cámara) | `https://www.camara.gov.co/wp-content/uploads/<YYYY>/<MM>/proyectos-ley/documentos/proyecto-<id>/<FILE>.pdf` | The `<id>` is internal, not the bill number |
| Project search | `https://www.camara.gov.co/proyectos-ley` | JS-driven; use the ficha URL if known |
| Senate | `https://www.senado.gov.co` | Search by project number; the same bill changes chamber |
| Status | Ficha “Estado” field | Updates slowly; check the committee acta |

### Known example (verified 2026-11-03)

- Ficha: `https://www.camara.gov.co/ley-rescate-economico/`
- PDF: `https://www.camara.gov.co/wp-content/uploads/2026/10/proyectos-ley/documentos/proyecto-36548/PROYECTO-DE-LEY-Rescate-Economico-2026-VSD-RADICADA-1.pdf`
- Metadata: Cámara 477/2026C, origin Cámara, legislature 2026-2027, filed
  2026-10-29, ordinary law, author Minister of Finance Miguel Gómez Martínez.

## Parameters

- **Chamber:** `camara` or `senado`.
- **Number and year:** e.g. `477/2026`.
- **Legislature:** e.g. `2026-2027`.
- **Project id:** internal numeric id in the PDF path (`36548` in the example).
- **Document type:** `radicada`, `ponencia`, `conciliacion`, `gaceta`.

No auth, no API key, no pagination for a known PDF. The project list is paginated
and JS-rendered; do not scrape it blindly. Use the search engine or the known
ficha, then the direct PDF.

## Rate limits and etiquette

- One request per second; identify the client with a `User-Agent`.
- Do not hammer the site during business hours; cache the PDF locally.
- Respect `robots.txt`; the ficha and PDF are public documents.

## Output schema

```text
data/raw/congreso/<YYYY-MM-DD>/
  pl-<number>-<slug>.pdf
  pl-<number>-<slug>.txt
  pl-<number>-<slug>.json   # metadata + article index
  manifest.csv
```

The JSON should contain:

```json
{
  "numero": "477/2026C",
  "camara": "Cámara",
  "legislatura": "2026-2027",
  "fecha_radicacion": "2026-10-29",
  "tipo": "Ley Ordinaria",
  "titulo": "...",
  "autores": ["..."],
  "url_ficha": "...",
  "url_pdf": "...",
  "sha256": "...",
  "articulos": [{"numero": 1, "epigrafe": "Objeto"}]
}
```

## Script

`.opencode/skills/congreso-proyectos-ley/scripts/fetch_bill.py` downloads a PDF,
validates the magic bytes, extracts text with `pdftotext -layout`, and writes an
article index. It is idempotent and fails loudly.

```bash
python3 .opencode/skills/congreso-proyectos-ley/scripts/fetch_bill.py \
  --url "https://www.camara.gov.co/.../PROYECTO-DE-LEY-...pdf" \
  --out data/raw/congreso/2026-11-03 \
  --number "477/2026C" \
  --title "Ley de Rescate Económico"
```

## Extraction rules

- The PDF has two parts: **exposición de motivos** (diagnosis, tables, fiscal
  impact) and **articulado** (the normative text). Do not confuse the two when
  citing an article.
- Article headings appear as `Artículo 1.` or `ARTÍCULO 51.`; normalize with a
  case-insensitive regex.
- Some headings are inside the exposition (e.g. “Artículo 513-1” as a proposed
  new article). Keep them, but mark the section.
- Tables in the exposition are laid out with spaces; use `pdftotext -layout` and
  read them cautiously. Do not parse numbers with a simple regex without checking
  the column alignment.
- The bill may have 105 or 106 articles depending on the version; use the PDF's
  own count, not the press.

## Gotchas

- A “Proyecto de Ley” is not a law. The file name may say “LEY” but the status is
  “Trámite en Comisión”.
- The same number can exist in both chambers (`477/2026C` vs `477/2026S`).
- The PDF URL includes an internal project id that is not the bill number.
- The Cámara page may be JS-rendered; the direct `documentos/proyecto-<id>/...`
  path is stable even when the search page is not.
- The “Estado” field can lag the committee vote; cite the date you consulted.
- Do not commit the PDF if it is large; commit the manifest and the script.

**Last verified:** 2026-11-03
