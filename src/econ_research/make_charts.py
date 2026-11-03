"""Generate the SVG figures used in the fiscal report.

No third-party dependencies: the SVGs are written directly so the figures can be
regenerated in any environment with Python 3.11+.

Run from the repository root:

    python3 src/econ_research/make_charts.py
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed" / "gnc_balance_2021_2027.csv"
OUT = ROOT / "reports" / "figures"

INK = "#1f2933"
MUTED = "#6b7280"
GRID = "#e5e7eb"
BLUE = "#1f4e79"
RED = "#b23a48"
GREEN = "#2f6f4e"
SAND = "#c9a227"
FONT = "font-family:'DejaVu Sans',Arial,sans-serif"


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg_open(width: int, height: int) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">',
        f"<style>text{{{FONT};fill:{INK}}} .muted{{fill:{MUTED}}} "
        f".grid{{stroke:{GRID};stroke-width:1}} .axis{{stroke:{MUTED};stroke-width:1}}</style>",
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
    ]


def load() -> list[dict[str, str]]:
    with DATA.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def fig_deficit_debt(rows: list[dict[str, str]]) -> str:
    width, height = 760, 330
    out = svg_open(width, height)
    years = [str(y) for y in range(2021, 2028)]
    base = [r for r in rows if r["estado"] not in {"estimacion CARF", "proyeccion oficial con ley"}]
    deficit = {r["anio"]: float(r["balance_total_pib"]) for r in base}
    debt = {r["anio"]: float(r["deuda_neta_pib"]) for r in base if r["deuda_neta_pib"]}

    panels = [
        (40, 55, 330, 210, "Balance total del GNC (% del PIB)", deficit, -10.0, 0.0, RED, "bar"),
        (420, 55, 300, 210, "Deuda neta del GNC (% del PIB)", debt, 45.0, 70.0, BLUE, "line"),
    ]
    out.append('<text x="20" y="20" font-size="15" font-weight="700">Colombia: déficit y deuda del Gobierno Nacional Central, 2021-2027</text>')
    for x0, y0, w, h, title, series, lo, hi, color, kind in panels:
        out.append(f'<text x="{x0}" y="{y0 - 4}" font-size="12" font-weight="600">{esc(title)}</text>')
        steps = 5
        for i in range(steps + 1):
            val = lo + (hi - lo) * i / steps
            y = y0 + h - (val - lo) / (hi - lo) * h
            out.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0 + w}" y2="{y:.1f}" class="grid"/>')
            out.append(f'<text x="{x0 - 6}" y="{y + 4:.1f}" font-size="10" text-anchor="end" class="muted">{val:.0f}</text>')
        if lo < 0 < hi:
            yz = y0 + h - (0 - lo) / (hi - lo) * h
            out.append(f'<line x1="{x0}" y1="{yz:.1f}" x2="{x0 + w}" y2="{yz:.1f}" class="axis"/>')
        n = len(years)
        slot = w / n
        if kind == "bar":
            for i, yr in enumerate(years):
                if yr not in series:
                    continue
                val = series[yr]
                yv = y0 + h - (val - lo) / (hi - lo) * h
                yz = y0 + h - (0 - lo) / (hi - lo) * h
                top, bottom = min(yv, yz), max(yv, yz)
                bx = x0 + i * slot + slot * 0.18
                bw = slot * 0.64
                projected = yr in {"2026", "2027"}
                fill = color if not projected else "url(#hatch)"
                out.append(f'<rect x="{bx:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{bottom - top:.1f}" fill="{fill}" opacity="0.92"/>')
                label = f"{val:.1f}".replace(".", ",")
                out.append(f'<text x="{bx + bw / 2:.1f}" y="{bottom + 13:.1f}" font-size="10" text-anchor="middle">{label}</text>')
        else:
            pts = []
            for i, yr in enumerate(years):
                if yr in series:
                    cx = x0 + i * slot + slot / 2
                    cy = y0 + h - (series[yr] - lo) / (hi - lo) * h
                    pts.append((cx, cy, yr))
            out.append('<polyline fill="none" stroke="%s" stroke-width="2.4" points="%s"/>' % (color, " ".join(f"{x:.1f},{y:.1f}" for x, y, _ in pts)))
            for cx, cy, yr in pts:
                out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.4" fill="{color}"/>')
                label = f"{series[yr]:.1f}".replace(".", ",")
                out.append(f'<text x="{cx:.1f}" y="{cy - 8:.1f}" font-size="10" text-anchor="middle">{label}</text>')
        for i, yr in enumerate(years):
            out.append(f'<text x="{x0 + i * slot + slot / 2:.1f}" y="{y0 + h + 16}" font-size="10" text-anchor="middle" class="muted">{yr}</text>')
    out.append('<defs><pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
               f'<rect width="5" height="5" fill="{RED}" opacity="0.25"/><line x1="0" y1="0" x2="0" y2="5" stroke="{RED}" stroke-width="2"/></pattern></defs>')
    out.append('<text x="40" y="305" font-size="9" class="muted">Barras rayadas: 2026-2027 son proyección oficial (Plan Financiero de agosto de 2026). 2027 sin la Ley de Rescate.</text>')
    out.append('<text x="40" y="319" font-size="9" class="muted">Fuente: MHCP, Cierre fiscal 2024; CARF, Informe al Congreso, septiembre de 2026; Plan Financiero 2026-2027.</text>')
    out.append("</svg>")
    return "\n".join(out)


def fig_adjustment() -> str:
    width, height = 760, 330
    out = svg_open(width, height)
    out.append('<text x="20" y="20" font-size="15" font-weight="700">Composición del ajuste de la Ley de Rescate (% del PIB)</text>')
    years = ["2027", "2028", "2029", "2030"]
    spending = [2.04, 2.05, 2.33, 2.39]
    revenue = [0.32, 1.75, 1.77, 1.79]
    x0, y0, w, h = 60, 45, 660, 220
    hi = 3.0
    for i in range(6):
        val = hi * i / 5
        y = y0 + h - val / hi * h
        out.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0 + w}" y2="{y:.1f}" class="grid"/>')
        lab_y = f"{val:.1f}".replace(".", ",")
        out.append(f'<text x="{x0 - 8}" y="{y + 4:.1f}" font-size="10" text-anchor="end" class="muted">{lab_y}</text>')
    slot = w / len(years)
    for i, yr in enumerate(years):
        bx = x0 + i * slot + slot * 0.22
        bw = slot * 0.26
        hs = spending[i] / hi * h
        out.append(f'<rect x="{bx:.1f}" y="{y0 + h - hs:.1f}" width="{bw:.1f}" height="{hs:.1f}" fill="{GREEN}"/>')
        lab_s = f"{spending[i]:.2f}".replace(".", ",")
        out.append(f'<text x="{bx + bw / 2:.1f}" y="{y0 + h - hs - 6:.1f}" font-size="10" text-anchor="middle">{lab_s}</text>')
        hr = revenue[i] / hi * h
        out.append(f'<rect x="{bx + bw + 4:.1f}" y="{y0 + h - hr:.1f}" width="{bw:.1f}" height="{hr:.1f}" fill="{SAND}"/>')
        lab_r = f"{revenue[i]:.2f}".replace(".", ",")
        out.append(f'<text x="{bx + bw + 4 + bw / 2:.1f}" y="{y0 + h - hr - 6:.1f}" font-size="10" text-anchor="middle">{lab_r}</text>')
        out.append(f'<text x="{bx + bw + 2:.1f}" y="{y0 + h + 16}" font-size="11" text-anchor="middle">{yr}</text>')
    out.append(f'<rect x="60" y="295" width="11" height="11" fill="{GREEN}"/><text x="76" y="304" font-size="10">Gasto (Pilar I)</text>')
    out.append(f'<rect x="180" y="295" width="11" height="11" fill="{SAND}"/><text x="196" y="304" font-size="10">Ingresos (Pilar II)</text>')
    out.append('<text x="60" y="323" font-size="9" class="muted">Fuente: PL 477 de 2026, exposición de motivos, tabla 14. El efecto total de la Ley (2,35; 3,58; 3,87; 4,09) incluye otros efectos (pilares III, IV y VI).</text>')
    out.append("</svg>")
    return "\n".join(out)


def fig_budget_2027() -> str:
    width, height = 760, 190
    out = svg_open(width, height)
    out.append('<text x="20" y="20" font-size="15" font-weight="700">Presupuesto General de la Nación 2027: $634,9 billones</text>')
    total = 634.9
    parts = [
        ("Funcionamiento", 393.25, BLUE),
        ("Servicio de la deuda", 147.07, RED),
        ("Inversión", 94.63, GREEN),
    ]
    x0, y0, w, h = 40, 50, 680, 46
    x = x0
    for label, value, color in parts:
        ww = value / total * w
        out.append(f'<rect x="{x:.1f}" y="{y0}" width="{ww:.1f}" height="{h}" fill="{color}"/>')
        pct = value / total * 100
        lab_pct = f"{pct:.1f}".replace(".", ",")
        lab_val = f"{value:.1f}".replace(".", ",")
        out.append(f'<text x="{x + ww / 2:.1f}" y="{y0 + 20}" font-size="10" text-anchor="middle" fill="white" font-weight="700">{lab_pct}%</text>')
        out.append(f'<text x="{x + ww / 2:.1f}" y="{y0 + 34}" font-size="9" text-anchor="middle" fill="white">${lab_val} bn</text>')
        x += ww
    out.append('<text x="40" y="125" font-size="11">El servicio de la deuda (23,2%) supera la inversión (14,9%). Los intereses solos absorben $94,4 billones,</text>')
    out.append('<text x="40" y="141" font-size="11">casi el mismo monto que toda la inversión pública del año.</text>')
    out.append('<text x="40" y="170" font-size="9" class="muted">Fuente: Ley de Presupuesto 2027 aprobada por el Congreso el 20 de octubre de 2026; cifras en billones de pesos corrientes.</text>')
    out.append("</svg>")
    return "\n".join(out)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = load()
    (OUT / "fig1_deficit_deuda.svg").write_text(fig_deficit_debt(rows), encoding="utf-8")
    (OUT / "fig2_ajuste.svg").write_text(fig_adjustment(), encoding="utf-8")
    (OUT / "fig3_pgn2027.svg").write_text(fig_budget_2027(), encoding="utf-8")
    print(f"Figures written to {OUT}")


if __name__ == "__main__":
    main()
