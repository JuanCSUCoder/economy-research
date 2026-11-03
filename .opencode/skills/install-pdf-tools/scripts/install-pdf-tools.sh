#!/usr/bin/env bash
# Install the Markdown -> PDF toolchain used by this repository.
# Idempotent: exits fast when everything is already present.
set -uo pipefail

PACKAGES=(pandoc weasyprint poppler-utils fonts-dejavu-core)
BINARIES=(pandoc weasyprint pdfinfo pdftotext pdffonts)

missing=()
for bin in "${BINARIES[@]}"; do
  command -v "$bin" >/dev/null 2>&1 || missing+=("$bin")
done

if ! fc-list 2>/dev/null | grep -qi "dejavu sans"; then
  missing+=("dejavu-fonts")
fi

if [[ ${#missing[@]} -eq 0 ]]; then
  echo "Toolchain already installed."
  pandoc --version | head -1
  weasyprint --version
  echo "DejaVu Sans: present"
  exit 0
fi

echo "Missing: ${missing[*]}"

if [[ ! -r /etc/os-release ]] || ! grep -qiE 'debian|ubuntu' /etc/os-release; then
  echo "This installer assumes Debian/Ubuntu (apt). Install manually: ${PACKAGES[*]}" >&2
  exit 1
fi

if [[ $EUID -eq 0 ]]; then
  SUDO=()
elif sudo -n true 2>/dev/null; then
  SUDO=(sudo -n)
else
  echo "No root and no passwordless sudo. Ask the user to run:" >&2
  echo "  sudo apt-get install -y ${PACKAGES[*]}" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
"${SUDO[@]}" apt-get update -qq
"${SUDO[@]}" apt-get install -y --no-install-recommends "${PACKAGES[@]}"

for bin in "${BINARIES[@]}"; do
  command -v "$bin" >/dev/null 2>&1 || { echo "Install failed: $bin still missing" >&2; exit 1; }
done

fc-list 2>/dev/null | grep -qi "dejavu sans" || { echo "Install failed: DejaVu Sans not registered" >&2; exit 1; }

echo "OK"
pandoc --version | head -1
weasyprint --version
