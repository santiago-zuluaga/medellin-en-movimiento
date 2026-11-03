#!/usr/bin/env python3
"""Auditoría empírica estructural, temporal y espacial de GeoJSON/CSV/JSON."""
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT_JSON = ROOT / "reports" / "audit_report.json"
OUT_MD = ROOT / "reports" / "audit_report.md"


def load(path: Path) -> tuple[list[dict], list[str], dict]:
    if path.suffix.lower() in {".geojson", ".json"}:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("type") == "FeatureCollection":
            rows = []
            for f in data.get("features", []):
                row = dict(f.get("properties") or {})
                if row.get("shape") is None:
                    row.pop("shape", None)  # ArcGIS geometry field echo; actual geometry is stored separately.
                geometry = f.get("geometry") or {}
                row["_geometry_type"] = geometry.get("type")
                row["_coordinates"] = geometry.get("coordinates")
                rows.append(row)
            return rows, sorted({k for row in rows for k in row}), {"format": "GeoJSON", "crs": data.get("crs")}
        if "fields" in data:
            return [], [f.get("name", "") for f in data["fields"]], {"format": "dictionary", "field_definitions": data["fields"]}
        return [], list(data), {"format": "JSON"}
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        return rows, list(reader.fieldnames or []), {"format": "CSV"}
    raise ValueError("formato no soportado")


def parse_date(value: object) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text[:19], fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def coordinate_pairs(value: object):
    if isinstance(value, (list, tuple)):
        if len(value) >= 2 and isinstance(value[0], (int, float)) and isinstance(value[1], (int, float)):
            yield float(value[0]), float(value[1])
        else:
            for item in value:
                yield from coordinate_pairs(item)


def simplify_ring(points: list[tuple[float, float]], tolerance: float = 0.00005) -> list[tuple[float, float]]:
    """Douglas-Peucker simplification for a fast, documented outlier screen."""
    if len(points) < 4:
        return points
    keep = {0, len(points) - 1}
    stack = [(0, len(points) - 1)]
    tolerance_sq = tolerance * tolerance
    while stack:
        start, end = stack.pop()
        ax, ay = points[start]
        bx, by = points[end]
        dx, dy = bx - ax, by - ay
        length_sq = dx * dx + dy * dy
        max_distance, farthest = 0.0, None
        for index in range(start + 1, end):
            px, py = points[index]
            if length_sq == 0:
                distance = (px - ax) ** 2 + (py - ay) ** 2
            else:
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_sq))
                distance = (px - (ax + t * dx)) ** 2 + (py - (ay + t * dy)) ** 2
            if distance > max_distance:
                max_distance, farthest = distance, index
        if farthest is not None and max_distance > tolerance_sq:
            keep.add(farthest)
            stack.append((start, farthest))
            stack.append((farthest, end))
    return [points[index] for index in sorted(keep)]


def point_in_ring(point: tuple[float, float], ring: list[tuple[float, float]]) -> bool:
    x, y = point
    inside = False
    for index in range(len(ring)):
        x1, y1 = ring[index]
        x2, y2 = ring[(index + 1) % len(ring)]
        if (y1 > y) != (y2 > y):
            intersection_x = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < intersection_x:
                inside = not inside
    return inside


def build_ring_index(ring: list[tuple[float, float]], bin_size: float = 0.0001) -> dict:
    bins: dict[int, list[tuple[float, float, float, float]]] = {}
    for index, (x1, y1) in enumerate(ring):
        x2, y2 = ring[(index + 1) % len(ring)]
        first = int(min(y1, y2) // bin_size)
        last = int(max(y1, y2) // bin_size)
        edge = (x1, y1, x2, y2)
        for bucket in range(first, last + 1):
            bins.setdefault(bucket, []).append(edge)
    return {"bins": bins, "bin_size": bin_size}


def point_in_ring_index(point: tuple[float, float], index: dict) -> bool:
    x, y = point
    bucket = int(y // index["bin_size"])
    inside = False
    for x1, y1, x2, y2 in index["bins"].get(bucket, []):
        if (y1 > y) != (y2 > y):
            intersection_x = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < intersection_x:
                inside = not inside
    return inside


def point_in_municipality(point: tuple[float, float], polygons: list[list[dict]]) -> bool:
    for rings in polygons:
        if rings and point_in_ring_index(point, rings[0]) and not any(point_in_ring_index(point, hole) for hole in rings[1:]):
            return True
    return False


def audit(path: Path) -> dict:
    rows, columns, details = load(path)
    if not rows:
        return {"name": path.name, "status": "WARN", "rows": 0, "columns": len(columns), "column_names": columns, "metadata": details, "warnings": ["No data rows; dictionary or empty dataset only"]}
    nulls = {column: sum(row.get(column) in (None, "") for row in rows) for column in columns}
    id_fields = {name for name in columns if name.lower() in {"objectid", "fid", "oid"}}
    signatures = [json.dumps({k: v for k, v in row.items() if k not in id_fields and k not in {"_geometry_type", "_coordinates"}}, sort_keys=True, ensure_ascii=False, default=str) for row in rows]
    exact_duplicates = len(signatures) - len(set(signatures))
    cardinality = {column: len({str(row.get(column)) for row in rows if row.get(column) not in (None, "")}) for column in columns}
    candidate_keys = []
    for column in columns:
        values = [str(row[column]) for row in rows if row.get(column) not in (None, "")]
        if not column.startswith("_") and len(values) == len(rows) and len(set(values)) == len(rows):
            candidate_keys.append({"field": column, "unique_non_null": True})
    date_fields = [c for c in columns if any(key in c.lower() for key in ("fecha", "date"))]
    temporal = {}
    for field in date_fields:
        parsed = [parse_date(row.get(field)) for row in rows]
        valid = [value for value in parsed if value]
        temporal[field] = {"parseable": len(valid), "unparseable_nonempty": sum(bool(row.get(field)) for row in rows) - len(valid), "minimum": min(valid).isoformat() if valid else None, "maximum": max(valid).isoformat() if valid else None}
    coordinate_rows = [row for row in rows if row.get("_geometry_type") == "Point" and row.get("_coordinates") is not None]
    coordinate_errors = 0
    coordinate_extent = None
    attribute_geometry_mismatches = 0
    if coordinate_rows:
        points = []
        for row in coordinate_rows:
            coords = row["_coordinates"]
            if not isinstance(coords, list) or len(coords) < 2:
                coordinate_errors += 1
                continue
            lon, lat = coords[:2]
            if not isinstance(lon, (int, float)) or not isinstance(lat, (int, float)) or not (-180 <= lon <= 180 and -90 <= lat <= 90):
                coordinate_errors += 1
            else:
                points.append((lon, lat))
                try:
                    attr_lon, attr_lat = float(row.get("longitud")), float(row.get("latitud"))
                    if abs(attr_lon - lon) > 1e-5 or abs(attr_lat - lat) > 1e-5:
                        attribute_geometry_mismatches += 1
                except (ValueError, TypeError):
                    pass
        if points:
            coordinate_extent = {"longitude_min": min(p[0] for p in points), "longitude_max": max(p[0] for p in points), "latitude_min": min(p[1] for p in points), "latitude_max": max(p[1] for p in points)}
    categories = {}
    for column in columns:
        if cardinality[column] <= 50:
            categories[column] = dict(Counter(str(row[column]) for row in rows if row.get(column) not in (None, "")))
    warnings = []
    if exact_duplicates:
        warnings.append(f"{exact_duplicates} duplicados exactos")
    if coordinate_errors:
        warnings.append(f"{coordinate_errors} geometrías/puntos inválidos en validación WGS84")
    for field, info in temporal.items():
        if info["unparseable_nonempty"]:
            warnings.append(f"{field}: {info['unparseable_nonempty']} valores no parseables")
    if path.name.startswith("siniestralidad"):
        warnings.append("Conteos son eventos registrados; no expresan riesgo ni exposición")
    if path.name.startswith("mortalidad"):
        warnings.append("La unidad exacta (persona fallecida/evento/registro) requiere definición oficial y validación")
    municipal_bbox = None
    bbox_outside = None
    polygon_outside = None
    boundary_method = None
    boundary_path = RAW / "limite_municipal.geojson"
    if coordinate_rows and boundary_path.exists():
        boundary = json.loads(boundary_path.read_text(encoding="utf-8"))
        boundary_points = [point for feature in boundary.get("features", []) for point in coordinate_pairs((feature.get("geometry") or {}).get("coordinates"))]
        if boundary_points:
            municipal_bbox = {"longitude_min": min(x for x, _ in boundary_points), "longitude_max": max(x for x, _ in boundary_points), "latitude_min": min(y for _, y in boundary_points), "latitude_max": max(y for _, y in boundary_points)}
            bbox_outside = sum(not (municipal_bbox["longitude_min"] <= x <= municipal_bbox["longitude_max"] and municipal_bbox["latitude_min"] <= y <= municipal_bbox["latitude_max"]) for x, y in points)
            if bbox_outside:
                warnings.append(f"{bbox_outside} puntos fuera de la envolvente rectangular del límite municipal (no equivale a prueba punto-en-polígono)")
            geometry = boundary.get("features", [{}])[0].get("geometry") or {}
            source_polygons = [geometry.get("coordinates", [])] if geometry.get("type") == "Polygon" else geometry.get("coordinates", []) if geometry.get("type") == "MultiPolygon" else []
            polygons = []
            for rings in source_polygons:
                indexed_rings = []
                for ring in rings:
                    points_in_ring = list(coordinate_pairs(ring))
                    if len(points_in_ring) > 1 and points_in_ring[0] == points_in_ring[-1]:
                        points_in_ring.pop()
                    indexed_rings.append(build_ring_index(points_in_ring))
                if indexed_rings:
                    polygons.append(indexed_rings)
            if polygons:
                polygon_outside = sum(not point_in_municipality(point, polygons) for point in points)
                boundary_method = {"type": "point-in-polygon over official WGS84 polygon with latitude-bin edge index", "latitude_bin_degrees": 0.0001, "use": "outlier QA only; coordinates are not transformed or removed"}
                if polygon_outside:
                    warnings.append(f"{polygon_outside} puntos fuera del límite municipal en prueba punto-en-polígono simplificada")
    if attribute_geometry_mismatches:
        warnings.append(f"{attribute_geometry_mismatches} coordenadas de atributos difieren de la geometría GeoJSON > 1e-5 grados")
    return {"name": path.name, "status": "WARN" if warnings else "PASS", "rows": len(rows), "columns": len(columns), "column_names": columns, "nulls": nulls, "null_percent": {k: round(v * 100 / len(rows), 4) for k, v in nulls.items()}, "exact_duplicates_excluding_source_ids": exact_duplicates, "candidate_keys": candidate_keys, "cardinality": cardinality, "temporal": temporal, "coordinate_rows": len(coordinate_rows), "coordinate_errors": coordinate_errors, "coordinate_extent_wgs84": coordinate_extent, "attribute_geometry_mismatches": attribute_geometry_mismatches, "municipal_bbox_wgs84": municipal_bbox, "points_outside_municipal_bbox": bbox_outside, "points_outside_municipal_polygon": polygon_outside, "municipal_boundary_method": boundary_method, "categories": categories, "metadata": details, "warnings": warnings}


def main() -> int:
    files = sorted(p for p in RAW.rglob("*") if p.suffix.lower() in {".geojson", ".json", ".csv"} and p.is_file()) if RAW.exists() else []
    reports = []
    for path in files:
        try:
            reports.append(audit(path))
        except Exception as exc:
            reports.append({"name": path.name, "status": "FAIL", "error": str(exc)})
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"created_utc": datetime.now(timezone.utc).isoformat(), "datasets": reports}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Informe de auditoría de datos", "", "El estado WARN señala aspectos que requieren lectura metodológica; no equivale automáticamente a datos inválidos.", ""]
    for report in reports:
        lines += [f"## {report['name']} — {report['status']}", "", f"- Filas: {report.get('rows', '—')} | columnas: {report.get('columns', '—')}"]
        if "null_percent" in report:
            lines.append(f"- Duplicados exactos excluyendo IDs técnicos: {report['exact_duplicates_excluding_source_ids']}")
            lines.append(f"- Claves candidatas completas y únicas: {', '.join(x['field'] for x in report['candidate_keys']) or 'ninguna'}")
            lines.append(f"- Coberturas temporales parseables: {json.dumps(report['temporal'], ensure_ascii=False)}")
            lines.append(f"- Extensión de coordenadas WGS84: {json.dumps(report['coordinate_extent_wgs84'], ensure_ascii=False)}")
            if report.get("points_outside_municipal_bbox") is not None:
                lines.append(f"- Puntos fuera de envolvente municipal: {report['points_outside_municipal_bbox']}")
            if report.get("points_outside_municipal_polygon") is not None:
                lines.append(f"- Puntos fuera del polígono municipal (pantalla simplificada): {report['points_outside_municipal_polygon']}")
            lines.append(f"- Diferencias entre atributos y geometría > 1e-5°: {report.get('attribute_geometry_mismatches', 0)}")
            lines.append(f"- Nulos por campo (%): `{json.dumps(report['null_percent'], ensure_ascii=False)}`")
        for warning in report.get("warnings", []):
            lines.append(f"- Advertencia: {warning}")
        if report.get("error"):
            lines.append(f"- Error: {report['error']}")
        lines.append("")
    if not reports:
        lines.append("Sin archivos locales en `data/raw/`; todavía no hay auditoría empírica.")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Auditoría de {len(reports)} archivos: {OUT_MD.relative_to(ROOT)}")
    return 1 if any(r.get("status") == "FAIL" for r in reports) else 0


if __name__ == "__main__":
    raise SystemExit(main())
