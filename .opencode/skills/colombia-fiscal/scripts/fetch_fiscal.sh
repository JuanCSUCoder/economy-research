#!/usr/bin/env bash
# Fetch the core Colombian fiscal/macro documents for a given research cut-off.
# Idempotent: skips files that already exist unless --force is passed.
set -euo pipefail

FORCE=0
if [[ "${1:-}" == "--force" ]]; then FORCE=1; fi

ROOT="${REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)}"
TODAY="$(date +%F)"
OUT="$ROOT/data/raw"
UA="econ-research/1.0 (+https://github.com/)"

declare -a ITEMS=(
  "carf/$TODAY/seguimiento-fiscal-sep2026.pdf|https://www.valoraanalitik.com/wp-content/uploads/2026/09/Seguimiento-fiscal-Septiembre-2026.pdf"
  "carf/$TODAY/carf-mfmp2026.pdf|https://www.camara.gov.co/wp-content/uploads/2026/07/informes_comision/4/Documento-tecnico-CARF-MFMP-2026_5097.pdf"
  "dane/$TODAY/pib-ivtrim2025.pdf|https://www.dane.gov.co/files/operaciones/PIB/cp-PIB-IVtrim2025.pdf"
  "dane/$TODAY/ipc-dic2025.pdf|https://www.dane.gov.co/files/operaciones/IPC/dic2025/cp-IPC-dic2025.pdf"
  "dane/$TODAY/pobreza-2025.pdf|https://www.dane.gov.co/files/operaciones/PM/cp-PM-2025.pdf"
  "banrep/$TODAY/resumen-congreso-oct2026.pdf|https://www.banrep.gov.co/sites/default/files/publicaciones/archivos/resumen-infografico-congreso-octubre-2026.pdf"
)

mkdir -p "$OUT"

for item in "${ITEMS[@]}"; do
  rel="${item%%|*}"
  url="${item##*|}"
  dest="$OUT/$rel"
  dir="$(dirname "$dest")"
  mkdir -p "$dir"

  if [[ -f "$dest" && "$FORCE" -ne 1 ]]; then
    echo "skip  $rel"
  else
    echo "fetch $url"
    tmp="$(mktemp)"
    curl -fsSL --retry 3 --retry-delay 2 -A "$UA" -o "$tmp" "$url"
    magic="$(head -c 4 "$tmp")"
    bytes="$(wc -c < "$tmp")"
    if [[ "$magic" != "%PDF" ]]; then
      echo "ERROR: $url is not a PDF (magic=$magic)" >&2
      rm -f "$tmp"
      exit 1
    fi
    if [[ "$bytes" -lt 10000 ]]; then
      echo "ERROR: $url is too small ($bytes bytes)" >&2
      rm -f "$tmp"
      exit 1
    fi
    mv "$tmp" "$dest"
    pdftotext -layout "$dest" "${dest%.pdf}.txt"
    sha="$(sha256sum "$dest" | cut -d' ' -f1)"
    printf '%s,%s,%s,%s,%s\n' "$url" "$sha" "$bytes" "application/pdf" "$(date -u +%FT%TZ)" >> "$dir/manifest.csv"
    echo "ok    $rel ($bytes bytes)"
  fi

  txt="${dest%.pdf}.txt"
  if [[ -f "$txt" ]]; then
    lines="$(wc -l < "$txt")"
    if [[ "$lines" -lt 50 ]]; then
      echo "WARN: $txt has only $lines lines; check the PDF" >&2
    fi
  fi
done

echo "done: $OUT"
