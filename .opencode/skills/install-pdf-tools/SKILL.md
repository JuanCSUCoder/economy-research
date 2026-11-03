---
name: Install PDF tools
description: Reinstall the Pandoc + WeasyPrint + poppler + DejaVu toolchain when the sandbox loses it, so Markdown-to-PDF builds work again. Use when build-pdf.sh reports "pandoc is missing" or "weasyprint is missing".
---

# Install PDF tools

Use this skill when the Markdown → PDF toolchain disappears. This sandbox is rebuilt from a base image from time to time, and `pandoc`, `weasyprint`, `poppler-utils` and the DejaVu fonts go missing with it. That is expected, not a repo problem.

## Symptom

Running `.opencode/skills/markdown-to-pdf/scripts/build-pdf.sh` fails with:

```
pandoc is missing. Install it with: sudo apt-get install -y pandoc weasyprint poppler-utils
```

or `weasyprint is missing`, or the PDF builds but the font falls back to a serif face because `fonts-dejavu-core` is absent (`/usr/share/fonts` empty, `fc-list` unavailable).

## Fix

```sh
.opencode/skills/install-pdf-tools/scripts/install-pdf-tools.sh
```

The script:

- checks for `pandoc`, `weasyprint`, `pdfinfo`, `pdftotext`, `pdffonts` and a registered **DejaVu Sans** face;
- exits immediately when everything is present (safe to run any time);
- asserts Debian/Ubuntu, then uses `sudo -n` (or runs directly as root) with `DEBIAN_FRONTEND=noninteractive`, which is what avoids the `debconf: unable to initialize frontend` noise;
- installs `pandoc weasyprint poppler-utils fonts-dejavu-core` with `--no-install-recommends`;
- re-verifies every binary and the font, and fails loudly if something is still missing.

## Notes

- Do **not** try to work around a missing toolchain with Node, headless browsers or hand-rolled PDF code. The repo's PDFs follow one standard: Letter, DejaVu Sans, built by `.opencode/skills/markdown-to-pdf`. Keep them consistent.
- The install needs network access; `apt-get update` runs first because the image may ship with empty package lists.
- After installing, rebuild the affected PDFs and verify with `pdfinfo` (612 x 792 pts), `pdffonts` (DejaVu-Sans) and `pdftotext -layout`.
- Then update `markdown-to-pdf`'s prerequisite note if the package list ever changes.
