#!/usr/bin/env python3
"""EDA reproducible: resumen temporal/categórico y gráficos SVG sin dependencias."""
from __future__ import annotations

import csv
import json
import html
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
MONTHS = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")
WEEKDAYS = ("lun", "mar", "mié", "jue", "vie", "sáb", "dom")
SPECS = [
    ("siniestralidad", "siniestralidad_2019_2025.geojson", "fecha_siniestro", "hora_siniestro", "dia", "nom_comuna", "gravedad_siniestro"),
    ("mortalidad", "mortalidad_2019_2024.geojson", "fecha_ocurrencia", "hora_ocurrencia", None, "nom_comuna", "clase"),
]


def parse_date(value: object) -> datetime | None:
    text = str(value or "").strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text[:10], fmt)
        except ValueError:
            continue
    return None


def read_features(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [dict(feature.get("properties") or {}) for feature in data.get("features", [])]


def svg_bars(values: dict[str, int], title: str, filename: Path, color: str) -> None:
    width, height = 900, 390
    left, right, top, bottom = 70, 30, 50, 70
    chart_w, chart_h = width - left - right, height - top - bottom
    max_value = max(values.values(), default=1)
    max_value = max(max_value, 1)
    slot = chart_w / max(len(values), 1)
    bar_w = min(54, slot * 0.65)
    elements = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc"><title id="title">{html.escape(title)}</title><desc id="desc">Barras de registros por año.</desc><rect width="100%" height="100%" fill="#fbf8f1"/>']
    elements.append(f'<text x="{left}" y="30" font-family="Arial" font-size="18" font-weight="700" fill="#1b332e">{html.escape(title)}</text>')
    for tick in range(5):
        value = max_value * tick / 4
        y = top + chart_h * (1 - tick / 4)
        elements.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" stroke="#d6ddd5"/>')
        elements.append(f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" font-family="Arial" font-size="11" fill="#52615c">{value:,.0f}</text>')
    for index, (label, value) in enumerate(sorted(values.items())):
        x = left + slot * index + (slot - bar_w) / 2
        h = chart_h * value / max_value
        y = top + chart_h - h
        elements.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" rx="3" fill="{color}"/>')
        elements.append(f'<text x="{x+bar_w/2:.1f}" y="{y-7:.1f}" text-anchor="middle" font-family="Arial" font-size="11" fill="#1b332e">{value:,}</text>')
        elements.append(f'<text x="{x+bar_w/2:.1f}" y="{height-40}" text-anchor="middle" font-family="Arial" font-size="13" fill="#1b332e">{html.escape(label)}</text>')
    elements.append(f'<text x="{left}" y="{height-12}" font-family="Arial" font-size="11" fill="#52615c">Filas registradas por año; el gráfico no mide riesgo ni exposición.</text></svg>')
    filename.write_text("\n".join(elements), encoding="utf-8")


def run_one(spec: tuple) -> dict | None:
    name, filename, date_field, time_field, weekday_field, community_field, category_field = spec
    path = RAW / filename
    if not path.exists():
        return None
    rows = read_features(path)
    yearly, monthly, weekday_hour = Counter(), Counter(), Counter()
    communities, categories = Counter(), Counter()
    invalid_dates = 0
    for row in rows:
        date = parse_date(row.get(date_field))
        if date is None:
            invalid_dates += 1
            continue
        year = str(date.year)
        yearly[year] += 1
        monthly[date.strftime("%Y-%m")] += 1
        try:
            hour = int(str(row.get(time_field, ""))[:2])
        except ValueError:
            hour = -1
        if 0 <= hour <= 23:
            weekday_hour[(date.weekday(), hour)] += 1
        if weekday_field and row.get(weekday_field):
            pass  # Preserve source weekday; derived weekday is used for consistent ordering.
        communities[str(row.get(community_field) or "Sin dato")] += 1
        categories[str(row.get(category_field) or "Sin dato")] += 1
    summary = {
        "dataset": name, "unit": "registro de evento según fila fuente" if name == "siniestralidad" else "registro de la capa de mortalidad; equivalencia a persona fallecida/evento pendiente",
        "records": len(rows), "invalid_dates": invalid_dates,
        "period_start": min(monthly) if monthly else None, "period_end": max(monthly) if monthly else None,
        "records_by_year": dict(sorted(yearly.items())), "records_by_month": dict(sorted(monthly.items())),
        "records_by_weekday_hour": [{"dia": WEEKDAYS[day], "dia_num": day, "hora": hour, "registros": count} for (day, hour), count in sorted(weekday_hour.items())],
        "records_by_community": dict(sorted(communities.items())), "records_by_category": dict(sorted(categories.items())),
        "method": "Counts source records; no denominator, join, interpolation or imputation. Year counts are descriptive; coverage/capture changes require caution.",
    }
    PROCESSED.mkdir(parents=True, exist_ok=True)
    (PROCESSED / f"eda_{name}.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    svg_bars(dict(sorted(yearly.items())), f"Registros de {name} por año", REPORTS / f"eda_{name}_por_anio.svg", "#bd4b2d" if name == "siniestralidad" else "#315a52")
    return summary


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    summaries = [value for spec in SPECS if (value := run_one(spec)) is not None]
    report = {"created_utc": datetime.now(timezone.utc).isoformat(), "datasets": summaries}
    (PROCESSED / "eda_summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# EDA reproducible", "", "Las tablas y gráficos se regeneran con `python scripts/eda.py`. Son conteos de registros, no estimaciones de riesgo.", ""]
    for data in summaries:
        lines += [f"## {data['dataset']}", "", f"- Unidad: {data['unit']}.", f"- Filas: {data['records']:,}; fechas no parseables: {data['invalid_dates']:,}.", f"- Periodo observado: {data['period_start']} a {data['period_end']}.", f"- Registros por año: `{json.dumps(data['records_by_year'], ensure_ascii=False)}`.", f"- Categorías: `{json.dumps(data['records_by_category'], ensure_ascii=False)}`.", "- Cobertura y clasificación pueden cambiar con revisiones de la fuente; los conteos no son tasas.", ""]
    (REPORTS / "eda_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"EDA ejecutado para {len(summaries)} fuentes; informe reports/eda_summary.md")
    return 0 if summaries else 1


if __name__ == "__main__":
    raise SystemExit(main())
