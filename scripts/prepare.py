#!/usr/bin/env python3
"""Crea tablas agregadas reproducibles sin mutar adquisiciones raw."""
from __future__ import annotations

import csv
import json
import hashlib
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"


def read_geojson(path: Path) -> list[dict]:
    source = json.loads(path.read_text(encoding="utf-8"))
    return [dict(feature.get("properties") or {}) | {"_geometry": feature.get("geometry")} for feature in source.get("features", [])]


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_date(value: object) -> datetime | None:
    value = str(value or "").strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value[:10], fmt)
        except ValueError:
            pass
    return None


def group_counts(rows: list[dict], fields: list[str]) -> list[dict]:
    counts = Counter(tuple(str(row.get(field) or "Sin dato") for field in fields) for row in rows)
    return [dict(zip(fields, key)) | {"registros": value} for key, value in sorted(counts.items())]


def process(source_name: str, path: Path, date_field: str, geo_field: str, category_field: str) -> int:
    rows = read_geojson(path)
    monthly = Counter()
    by_community = Counter()
    by_category = Counter()
    for row in rows:
        date_value = parse_date(row.get(date_field))
        if date_value:
            monthly[date_value.strftime("%Y-%m")] += 1
        by_community[str(row.get(geo_field) or "Sin dato")] += 1
        by_category[str(row.get(category_field) or "Sin dato")] += 1
    PROCESSED.mkdir(parents=True, exist_ok=True)
    write_csv(PROCESSED / f"{source_name}_por_mes.csv", [{"mes": k, "registros": v} for k, v in sorted(monthly.items())], ["mes", "registros"])
    write_csv(PROCESSED / f"{source_name}_por_comuna.csv", [{"comuna": k, "registros": v} for k, v in sorted(by_community.items())], ["comuna", "registros"])
    write_csv(PROCESSED / f"{source_name}_por_categoria.csv", [{"categoria": k, "registros": v} for k, v in sorted(by_category.items())], ["categoria", "registros"])
    coordinate_counts = Counter()
    for row in rows:
        geometry = row.get("_geometry") or {}
        coords = geometry.get("coordinates") or []
        if len(coords) >= 2:
            # Two decimal places are used only for a city-scale overview, not distance calculations.
            coordinate_counts[(round(coords[0], 2), round(coords[1], 2))] += 1
    # Keep this coarse overview non-identifying; this is not a true hexbin grid.
    write_csv(PROCESSED / f"{source_name}_hex_overview.csv", [{"longitud_aprox": x, "latitud_aprox": y, "registros": n} for (x, y), n in sorted(coordinate_counts.items()) if n >= 5], ["longitud_aprox", "latitud_aprox", "registros"])
    return len(rows)


def main() -> int:
    summary = {"created_utc": datetime.now(timezone.utc).isoformat(), "method": "Counts by source rows; no cross-dataset joins or denominators. City overview groups coordinates rounded to 0.01 degree and is not a metric hexbin.", "datasets": []}
    specs = [("siniestralidad", "siniestralidad_2019_2025.geojson", "fecha_siniestro", "nom_comuna", "gravedad_siniestro"), ("mortalidad", "mortalidad_2019_2024.geojson", "fecha_ocurrencia", "nom_comuna", "clase")]
    for name, filename, date, community, category in specs:
        path = RAW / filename
        if not path.exists():
            summary["datasets"].append({"name": name, "status": "PENDING", "reason": f"No existe {filename}"})
            continue
        n = process(name, path, date, community, category)
        summary["datasets"].append({"name": name, "status": "PASS", "input_rows": n, "files": [f"{name}_por_mes.csv", f"{name}_por_comuna.csv", f"{name}_por_categoria.csv", f"{name}_hex_overview.csv"]})
    dictionary = {"created_utc": datetime.now(timezone.utc).isoformat(), "datasets": []}
    for name, filename, *_ in specs:
        path = RAW / filename
        if not path.exists():
            continue
        features = json.loads(path.read_text(encoding="utf-8")).get("features", [])
        fields = {}
        for feature in features:
            for key, value in (feature.get("properties") or {}).items():
                entry = fields.setdefault(key, {"observed_types": set(), "nulls": 0, "non_null": 0})
                if value is None:
                    entry["nulls"] += 1
                else:
                    entry["non_null"] += 1
                    entry["observed_types"].add(type(value).__name__)
        for field in fields.values():
            field["observed_types"] = sorted(field["observed_types"])
            field["null_percent"] = round(field["nulls"] * 100 / max(len(features), 1), 4)
        dictionary["datasets"].append({"name": name, "unit": "evento registrado" if name == "siniestralidad" else "registro de capa; equivalencia de unidad pendiente", "row_count": len(features), "sha256_raw": hashlib.sha256(path.read_bytes()).hexdigest(), "fields": fields})
    PROCESSED.mkdir(parents=True, exist_ok=True)
    (PROCESSED / "prepare_manifest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    metadata_dir = ROOT / "data" / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    (metadata_dir / "data_dictionary.json").write_text(json.dumps(dictionary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
