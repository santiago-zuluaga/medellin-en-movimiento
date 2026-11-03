"""Lectura y agregación segura para el servicio web local."""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "incidents": {"file": "siniestralidad_2019_2025.geojson", "date": "fecha_siniestro", "time": "hora_siniestro", "community": "nom_comuna", "class": "clase_siniestro", "severity": "gravedad_siniestro", "label": "Siniestros registrados"},
    "mortality": {"file": "mortalidad_2019_2024.geojson", "date": "fecha_ocurrencia", "time": "hora_ocurrencia", "community": "nom_comuna", "class": "clase", "severity": None, "label": "Registros de la capa de mortalidad"},
}


def parse_date(value: object) -> datetime | None:
    text = str(value or "").strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text[:10], fmt)
        except ValueError:
            continue
    return None


def parse_hour(value: object) -> int | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        hour = int(text[:2])
        return hour if 0 <= hour <= 23 else None
    except ValueError:
        return None


def read_source(dataset: str, root: Path = ROOT) -> list[dict]:
    if dataset not in SOURCES:
        raise ValueError(f"Fuente desconocida: {dataset}")
    path = root / "data" / "raw" / SOURCES[dataset]["file"]
    data = json.loads(path.read_text(encoding="utf-8"))
    return [dict(feature.get("properties") or {}) | {"_geometry": feature.get("geometry")} for feature in data.get("features", [])]


def filter_rows(rows: list[dict], dataset: str, filters: dict) -> list[dict]:
    spec = SOURCES[dataset]
    result = []
    for row in rows:
        date = parse_date(row.get(spec["date"]))
        if not date:
            continue
        if filters.get("year") and str(date.year) != str(filters["year"]):
            continue
        if filters.get("community") and row.get(spec["community"]) != filters["community"]:
            continue
        if filters.get("category") and row.get(spec["class"]) != filters["category"]:
            continue
        if filters.get("severity") and spec["severity"] and row.get(spec["severity"]) != filters["severity"]:
            continue
        if filters.get("hour", "") != "":
            hour = parse_hour(row.get(spec["time"]))
            if hour is None or hour != int(filters["hour"]):
                continue
        if filters.get("weekday", "") != "" and date.weekday() != int(filters["weekday"]):
            continue
        if filters.get("cell"):
            geometry = row.get("_geometry") or {}
            coords = geometry.get("coordinates") or []
            try:
                wanted_lon, wanted_lat = (float(part) for part in filters["cell"].split(",", 1))
                if geometry.get("type") != "Point" or len(coords) < 2 or round(float(coords[0]), 2) != wanted_lon or round(float(coords[1]), 2) != wanted_lat:
                    continue
            except (ValueError, TypeError):
                continue
        result.append(row)
    return result


def aggregate(rows: list[dict], dataset: str, coverage_rows: list[dict] | None = None) -> dict:
    spec = SOURCES[dataset]
    years, months, communities, categories, severities, weekday_hours, cells = Counter(), Counter(), Counter(), Counter(), Counter(), Counter(), Counter()
    coverage_months = set()
    for row in coverage_rows if coverage_rows is not None else rows:
        date = parse_date(row.get(spec["date"]))
        if date:
            coverage_months.add(date.strftime("%Y-%m"))
    for row in rows:
        date = parse_date(row.get(spec["date"]))
        if not date:
            continue
        years[str(date.year)] += 1
        months[date.strftime("%Y-%m")] += 1
        communities[str(row.get(spec["community"]) or "Sin dato")] += 1
        categories[str(row.get(spec["class"]) or "Sin dato")] += 1
        if spec["severity"]:
            severities[str(row.get(spec["severity"]) or "Sin dato")] += 1
        hour = parse_hour(row.get(spec["time"]))
        if hour is not None:
            weekday_hours[(date.weekday(), hour)] += 1
        geometry = row.get("_geometry") or {}
        coords = geometry.get("coordinates") or []
        if geometry.get("type") == "Point" and len(coords) >= 2:
            cells[(round(float(coords[0]), 2), round(float(coords[1]), 2))] += 1
    return {
        "dataset": dataset, "unit": spec["label"], "records": len(rows),
        "years": dict(sorted(years.items())), "months": dict(sorted(months.items())), "coverage_months": sorted(coverage_months),
        "communities": dict(sorted(communities.items())), "categories": dict(sorted(categories.items())), "severities": dict(sorted(severities.items())),
        "weekday_hours": [{"weekday": day, "hour": hour, "count": count} for (day, hour), count in sorted(weekday_hours.items())],
        "cells": [{"longitude": lon, "latitude": lat, "count": count} for (lon, lat), count in sorted(cells.items()) if count >= 5],
        "cell_note": "Coordenadas agrupadas por redondeo de 0.01°; no es una malla de área igual. Se omiten grupos menores de 5 en el mapa.",
    }
