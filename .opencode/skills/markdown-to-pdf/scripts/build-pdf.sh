#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 input.md [output.pdf]" >&2
  exit 2
}

[[ $# -ge 1 && $# -le 2 ]] || usage

input=$1
[[ -f "$input" ]] || { echo "Input not found: $input" >&2; exit 1; }

output=${2:-"${input%.md}.pdf"}
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
css="$script_dir/../references/pdf-style.css"

command -v pandoc >/dev/null || {
  echo "pandoc is missing. Install it with: sudo apt-get install -y pandoc weasyprint poppler-utils" >&2
  exit 1
}
command -v weasyprint >/dev/null || {
  echo "weasyprint is missing. Install it with: sudo apt-get install -y pandoc weasyprint poppler-utils" >&2
  exit 1
}
[[ -f "$css" ]] || { echo "Stylesheet not found: $css" >&2; exit 1; }

tmpdir=$(mktemp -d "${TMPDIR:-/tmp}/opencode-pdf.XXXXXX")
trap 'rm -rf "$tmpdir"' EXIT

pandoc "$input" \
  --from markdown \
  --to html5 \
  --wrap=none \
  --output "$tmpdir/body.html"

{
  printf '%s\n' '<!doctype html><html lang="es"><head><meta charset="utf-8"><style>'
  cat "$css"
  printf '%s\n' '</style></head><body>'
  cat "$tmpdir/body.html"
  printf '%s\n' '</body></html>'
} > "$tmpdir/document.html"

mkdir -p "$(dirname "$output")"
weasyprint "$tmpdir/document.html" "$output"

echo "PDF: $output"

if command -v pdfinfo >/dev/null; then
  pdfinfo "$output" | awk '/Pages|Page size|File size/'
fi

if command -v pdffonts >/dev/null; then
  if pdffonts "$output" | grep -qi 'DejaVu-Sans'; then
    echo "Font: DejaVu Sans"
  else
    echo "Warning: DejaVu Sans not found in the PDF. Check the CSS and installed fonts." >&2
  fi
fi
