#!/usr/bin/env python3
"""Download a Colombian bill PDF and build a small article index.

Usage:
    python3 fetch_bill.py --url URL --out DIR --number 477/2026C --title "..."

No third-party dependencies. Requires `pdftotext` (poppler-utils).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ARTICLE_RE = re.compile(
    r"^(?:Art[íi]culo|ART[ÍI]CULO)\s+(\d+[\w\-]*)\s*[\.\-–—:]\s*(.+)$",
    re.IGNORECASE,
)


def slug(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[áàäâ]", "a", text)
    text = re.sub(r"[éèëê]", "e", text)
    text = re.sub(r"[íìïî]", "i", text)
    text = re.sub(r"[óòöô]", "o", text)
    text = re.sub(r"[úùüû]", "u", text)
    text = re.sub(r"[ñ]", "n", text)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "documento"


def download(url: str, dest: Path) -> str:
    if dest.exists():
        print(f"skip {dest}")
    else:
        req = urllib.request.Request(url, headers={"User-Agent": "econ-research/1.0"})
        with urllib.request.urlopen(req, timeout=60) as response:
            data = response.read()
        if not data.startswith(b"%PDF"):
            raise SystemExit(f"ERROR: {url} is not a PDF")
        if len(data) < 10_000:
            raise SystemExit(f"ERROR: {url} is too small ({len(data)} bytes)")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        print(f"ok   {dest} ({len(data)} bytes)")
    return hashlib.sha256(dest.read_bytes()).hexdigest()


def extract_text(pdf: Path, txt: Path) -> None:
    if txt.exists():
        return
    if shutil.which("pdftotext") is None:
        raise SystemExit("ERROR: pdftotext is missing (poppler-utils)")
    subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], check=True)
    lines = txt.read_text(encoding="utf-8", errors="replace").splitlines()
    if len(lines) < 50:
        raise SystemExit(f"ERROR: {txt} has only {len(lines)} lines")


def index_articles(txt: Path) -> list[dict[str, object]]:
    lines = txt.read_text(encoding="utf-8", errors="replace").splitlines()
    # Skip the exposición de motivos: the normative text starts after DECRETA.
    start = 0
    for i, line in enumerate(lines):
        if "DECRETA" in line.upper():
            start = i + 1
            break
    articles: list[dict[str, object]] = []
    seen: set[str] = set()
    for line in lines[start:]:
        match = ARTICLE_RE.match(line)
        if not match:
            continue
        number, heading = match.group(1), match.group(2).strip()
        if number in seen:
            continue
        seen.add(number)
        articles.append({"numero": number, "epigrafe": heading[:180]})
    return articles


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--number", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--chamber", default="Cámara")
    parser.add_argument("--legislature", default="2026-2027")
    parser.add_argument("--filed", default="")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    stem = f"pl-{slug(args.number)}-{slug(args.title)}"
    pdf = args.out / f"{stem}.pdf"
    txt = args.out / f"{stem}.txt"

    sha = download(args.url, pdf)
    extract_text(pdf, txt)
    articles = index_articles(txt)

    meta = {
        "numero": args.number,
        "camara": args.chamber,
        "legislatura": args.legislature,
        "fecha_radicacion": args.filed,
        "titulo": args.title,
        "url_pdf": args.url,
        "sha256": sha,
        "articulos": articles,
    }
    meta_path = args.out / f"{stem}.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest = args.out / "manifest.csv"
    with manifest.open("a", encoding="utf-8") as fh:
        fh.write(f"{args.url},{sha},{pdf.stat().st_size},application/pdf,{args.number}\n")

    print(f"articles: {len(articles)}")
    print(f"meta:     {meta_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
