---
name: Markdown to PDF
description: Generate print-ready Letter PDFs from Markdown with Pandoc and WeasyPrint, using DejaVu Sans, then verify fonts, page size, page count, and extracted text.
---

# Markdown to PDF

Use this skill when a Markdown document must become a clean PDF for printing or sending, especially the research reports in `reports/`.

## What this produces

- Letter-size PDF (`612 x 792 pts`).
- DejaVu Sans, sans-serif, embedded in the PDF.
- No cover page, footer, page numbers, watermarks, or assistant notes.
- Text selectable and accents preserved.
- Markdown and PDF kept side by side with the same base name.

## Prerequisites

The sandbox sometimes loses the toolchain. Restore it with:

```sh
.opencode/skills/install-pdf-tools/scripts/install-pdf-tools.sh
```

It installs `pandoc weasyprint poppler-utils fonts-dejavu-core`, is idempotent and verifies the binaries and the DejaVu font. Manual equivalent: `sudo apt-get install -y pandoc weasyprint poppler-utils fonts-dejavu-core`.

Check:

```sh
pandoc --version | head -1
weasyprint --version
pdffonts -v 2>&1 | head -2
```

## Workflow

1. Read the Markdown file and remove any placeholders, notes, instructions, or non-document text.
2. Run the helper script:

```sh
.opencode/skills/markdown-to-pdf/scripts/build-pdf.sh input.md output.pdf
```

3. Verify the result:

```sh
pdfinfo output.pdf
pdffonts output.pdf
pdftotext -layout output.pdf - | sed -n '1,220p'
```

4. If the text or page breaks are wrong, adjust the Markdown and rebuild.
5. Keep the `.md` and `.pdf` versions in sync.

For a batch:

```sh
for f in reports/*.md; do
  .opencode/skills/markdown-to-pdf/scripts/build-pdf.sh "$f" "${f%.md}.pdf"
done
```

## Layout rules

- Use `references/pdf-style.css`.
- `@page`: Letter, margins `1.8cm 1.9cm`.
- Body: `10.5pt`, line-height `1.35`.
- H1: `15pt`; H2: `11.5pt`.
- Use `break-after: avoid` on headings and `break-inside: avoid` on list items.
- If a signature or short final block lands alone on a page, reduce body size slightly or tighten margins before changing content.
- Do not add page numbers unless requested.

## Pitfalls

- **Do not use Pandoc's standalone HTML template.** It can add a duplicate title block. Build a small HTML wrapper around the body output instead.
- **Use `<br>` for forced line breaks.** Two trailing spaces work in some renderers, but they fail whitespace checks and are fragile.
- **Do not wrap email addresses in `<...>` if the PDF needs explicit separators.** Pandoc turns them into links and may collapse the surrounding text.
- **Verify the actual font.** `pdffonts` must show `DejaVu-Sans` (or another embedded sans-serif), not a serif fallback.
- **Check page size.** `pdfinfo` must show `612 x 792 pts (letter)`.
- **Check page count.** A signature alone on the last page usually means the body is too airy; tune CSS before cutting content.
- **Match the existing filename casing.** If the tracked PDF is `PQR-Aliensalud.pdf`-style with capitals, pass that exact path as the second argument; otherwise the script creates a lowercase duplicate.
- **No notes in final documents.** Files in `required_info/` are print-and-send documents: no “Documento listo”, checklists, placeholders, or meta-commentary.
- **No automatic PDF for internal data sheets.** Only convert final documents.

## Repo-specific rule

In this repository:

- `reports/<YYYY-MM-DD>-<slug>.es.md` and `.en.md` are final documents.
- Their PDFs use the same base name in the same directory.
- After editing a Markdown report, regenerate its PDF.
- Relative figure paths (`figures/fig1.svg`) resolve because the build script
  passes the input directory as WeasyPrint's base URL. Keep figures beside the
  report and reference them relatively.
- Data sheets under `data/` are not final documents and get no PDF.
