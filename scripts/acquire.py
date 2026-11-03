#!/usr/bin/env python3
"""Adquiere extractos mínimos de capas ArcGIS oficiales y diccionarios MEData."""
from __future__ import annotations

import hashlib
import json
import argparse
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
META = ROOT / "data" / "metadata"
MANIFEST = ROOT / "reports" / "acquisition_manifest.json"
SOURCES = {
    "incidents": {
        "url": "https://www.medellin.gov.co/servidormapas/rest/services/transporte/VM_Accidentes/MapServer/0",
        "fields": ["fecha_siniestro", "hora_siniestro", "dia", "mes", "anio", "clase_siniestro", "gravedad_siniestro", "barrio", "num_comuna", "nom_comuna", "latitud", "longitud"],
        "filename": "siniestralidad_2019_2025.geojson",
    },
    "fatalities": {
        "url": "https://www.medellin.gov.co/servidormapas/rest/services/transporte/VM_Mortalidad/MapServer/0",
        "fields": ["fecha_ocurrencia", "hora_ocurrencia", "clase", "nom_comuna", "latitud", "longitud"],
        "filename": "mortalidad_2019_2024.geojson",
    },
    "municipality_boundary": {
        "url": "https://www.medellin.gov.co/servidormapas/rest/services/mapas_nacionales/VC_Limite_Politico_Admtivo/MapServer/2",
        "fields": [],
        "filename": "limite_municipal.geojson",
    },
}
DICTIONARIES = {
    "victims": "https://medata.app.medellin.gov.co/sites/default/files/distribution/1-023-25-000360/diccionario_mede_victimas_inci.json",
    "bicycles": "https://medata.app.medellin.gov.co/sites/default/files/distribution/1-023-25-000269/caracterizacion_uso_bicicleta.json",
}


def request_bytes(url: str, attempts: int = 4) -> tuple[bytes, str, str, int]:
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            req = Request(url, headers={"User-Agent": "MedellinEnMovimiento/1.0 (academic data audit)"})
            with urlopen(req, timeout=45) as response:
                payload = response.read()
                content_type = response.headers.get("Content-Type", "")
                final_url = response.geturl()
                if response.status >= 400:
                    raise RuntimeError(f"HTTP {response.status}")
                return payload, content_type, final_url, response.status
        except (HTTPError, URLError, TimeoutError, RuntimeError) as exc:
            last = exc
            if attempt + 1 < attempts:
                time.sleep(min(2 ** attempt, 8))
    # Avoid dumping long query strings (object IDs) into the manifest/log.
    from urllib.parse import urlsplit
    short_url = urlsplit(url)
    raise RuntimeError(f"Falló GET {short_url.netloc}{short_url.path}: {last}")


def json_get(url: str, capture: list | None = None) -> dict:
    payload, content_type, final_url, status = request_bytes(url)
    if capture is not None:
        capture.append({"url": final_url, "content_type": content_type, "http_status": status, "bytes": len(payload)})
    if "json" not in content_type.lower() and not payload.lstrip().startswith((b"{", b"[")):
        raise RuntimeError(f"Se esperaba JSON en {final_url}; Content-Type={content_type}")
    value = json.loads(payload)
    if isinstance(value, dict) and value.get("error"):
        raise RuntimeError(f"Error API: {value['error']}")
    return value


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def acquire_layer(name: str, spec: dict) -> dict:
    base = spec["url"]
    started = datetime.now(timezone.utc).isoformat()
    record = {"name": name, "source_url": base, "started_utc": started, "status": "FAIL", "errors": []}
    metadata_response = []
    metadata = json_get(base + "?" + urlencode({"f": "json"}), metadata_response)
    if metadata.get("error"):
        raise RuntimeError(str(metadata["error"]))
    available = {field["name"].lower() for field in metadata.get("fields", [])}
    invalid = [field for field in spec["fields"] if field.lower() not in available]
    if invalid:
        raise RuntimeError(f"Campos solicitados ausentes del esquema vigente: {invalid}")
    oid_field = metadata.get("objectIdField") or next((f["name"] for f in metadata["fields"] if f["type"] == "esriFieldTypeOID"), None)
    if not oid_field:
        raise RuntimeError("La capa no declara un campo ObjectID")
    destination = RAW / spec["filename"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        existing = destination.read_bytes()
        stored = json.loads(existing)
        return {"name": name, "source_url": base, "final_url": base, "status": "PASS", "reused_existing_raw": True, "http_status": 200, "metadata_response": metadata_response[0] if metadata_response else None,
                "metadata": {"name": metadata.get("name"), "description": metadata.get("description"), "fields": spec["fields"], "object_id_field": oid_field, "max_record_count": metadata.get("maxRecordCount"), "source_crs": metadata.get("sourceSpatialReference"), "requested_output_crs": "EPSG:4326"},
                "object_ids_requested": len(stored.get("features", [])), "features_downloaded": len(stored.get("features", [])), "batches": 0,
                "path": str(destination.relative_to(ROOT)), "content_type": "application/geo+json (previous immutable extract)", "bytes": len(existing), "sha256": digest(existing),
                "completed_utc": datetime.fromtimestamp(destination.stat().st_mtime, timezone.utc).isoformat(), "privacy_note": "Extracto de campos minimizado; se reutilizó raw local inmutable."}
    id_url = base + "/query?" + urlencode({"f": "json", "where": "1=1", "returnIdsOnly": "true"})
    ids_response = []
    ids_obj = json_get(id_url, ids_response)
    object_ids = ids_obj.get("objectIds")
    if not isinstance(object_ids, list):
        raise RuntimeError("La API no devolvió objectIds")
    maximum = max(1, int(metadata.get("maxRecordCount", 1000)))
    features: list[dict] = []
    requested: set[int] = set()
    batch_content_types = set()
    batch_statuses = set()
    # Pagination avoids a huge URL containing thousands of objectIds. We compare
    # all returned object IDs against the complete ID inventory after retrieval.
    batches = list(range(0, len(object_ids), maximum))
    for batch_index, offset in enumerate(batches, start=1):
        params = {
            "f": "geojson", "where": "1=1", "orderByFields": oid_field,
            "resultOffset": offset, "resultRecordCount": maximum,
            "outFields": ",".join([oid_field, *spec["fields"]]), "returnGeometry": "true", "outSR": "4326",
        }
        payload, content_type, final_url, status = request_bytes(base + "/query?" + urlencode(params))
        batch_content_types.add(content_type)
        batch_statuses.add(status)
        if "html" in content_type.lower() or payload.lstrip().lower().startswith((b"<!doctype html", b"<html")):
            raise RuntimeError(f"La consulta devolvió HTML, no GeoJSON (lote {batch_index})")
        result = json.loads(payload)
        if result.get("error"):
            raise RuntimeError(f"Error ArcGIS lote {batch_index}: {result['error']}")
        got = result.get("features", [])
        if not isinstance(got, list):
            raise RuntimeError(f"Respuesta inválida en lote {batch_index}")
        features.extend(got)
        requested.update(object_ids[offset:offset + maximum])
    received = {feature.get("properties", {}).get(oid_field) for feature in features}
    missing = requested - received
    unexpected = received - requested
    if missing or unexpected or len(features) != len(requested):
        raise RuntimeError(f"Verificación ObjectID falló: solicitados={len(requested)}, recibidos={len(features)}, faltantes={len(missing)}, inesperados={len(unexpected)}")
    output = {"type": "FeatureCollection", "name": name, "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}, "features": features}
    raw = (json.dumps(output, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    destination.write_bytes(raw)
    record.update({
        "status": "PASS", "final_url": base + "/query (paginated)", "http_status": sorted(batch_statuses), "metadata_response": metadata_response[0] if metadata_response else None, "object_ids_response": ids_response[0] if ids_response else None, "feature_response_content_types": sorted(batch_content_types),
        "metadata": {"name": metadata.get("name"), "description": metadata.get("description"), "fields": spec["fields"], "object_id_field": oid_field, "max_record_count": maximum, "source_crs": metadata.get("sourceSpatialReference"), "requested_output_crs": "EPSG:4326", "last_edit_date": metadata.get("editingInfo", {}).get("lastEditDate")},
        "object_ids_requested": len(requested), "features_downloaded": len(features), "batches": len(batches),
        "path": str(destination.relative_to(ROOT)), "content_type": "application/geo+json (serialized from ArcGIS GeoJSON responses)", "bytes": len(raw), "sha256": digest(raw), "completed_utc": datetime.now(timezone.utc).isoformat(),
        "privacy_note": "Extracto de campos minimizado; excluye dirección y radicado/id. Coordenadas exactas solo se conservan en raw local no versionado.",
    })
    return record


def acquire_dictionary(name: str, url: str) -> dict:
    payload, content_type, final_url, status = request_bytes(url)
    parsed = json.loads(payload)
    destination = META / "dictionaries" / f"{name}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    reused = False
    if destination.exists():
        old_content = destination.read_bytes()
        if digest(old_content) == digest(payload):
            reused = True
        else:
            suffix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            destination = destination.with_name(f"{name}_{suffix}.json")
    if not reused:
        destination.write_bytes(payload)
    return {"name": f"{name}_dictionary", "source_url": url, "final_url": final_url, "content_type": content_type, "http_status": status, "bytes": len(payload), "sha256": digest(payload), "path": str(destination.relative_to(ROOT)), "status": "PASS", "field_count": len(parsed.get("fields", [])), "reused_existing_raw": reused, "completed_utc": datetime.now(timezone.utc).isoformat()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=[*SOURCES, "victims_dictionary", "bicycles_dictionary"], help="Ejecuta solo una fuente (útil para adquirir una versión faltante sin repetir raw).")
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)
    previous = {}
    previous_runs = []
    if MANIFEST.exists():
        try:
            old_manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
            previous = {item["name"]: item for item in old_manifest.get("sources", []) if item.get("name")}
            previous_runs = old_manifest.get("runs", [])
        except (json.JSONDecodeError, OSError):
            pass
    # Recover immutable files omitted by an earlier single-source execution.
    for name, spec in SOURCES.items():
        path = RAW / spec["filename"]
        if name not in previous and path.exists():
            content = path.read_bytes()
            previous[name] = {"name": name, "source_url": spec["url"], "status": "PASS", "path": str(path.relative_to(ROOT)), "bytes": len(content), "sha256": digest(content), "features_downloaded": len(json.loads(content).get("features", [])), "completed_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(), "reconstructed_entry": True, "note": "Metadatos del primer intento se perdieron por reemplazo accidental del manifiesto; entrada reconstruida desde el raw inmutable."}
    for name, url in DICTIONARIES.items():
        path = META / "dictionaries" / f"{name}.json"
        key = f"{name}_dictionary"
        if key not in previous and path.exists():
            content = path.read_bytes()
            previous[key] = {"name": key, "source_url": url, "status": "PASS", "path": str(path.relative_to(ROOT)), "bytes": len(content), "sha256": digest(content), "completed_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(), "reconstructed_entry": True, "note": "Entrada reconstruida desde el diccionario preservado."}
    attempted = []
    chosen_sources = {name: spec for name, spec in SOURCES.items() if not args.only or args.only == name}
    for name, spec in chosen_sources.items():
        try:
            attempted.append(acquire_layer(name, spec))
        except Exception as exc:
            attempted.append({"name": name, "source_url": spec["url"], "status": "FAIL", "errors": [str(exc)], "completed_utc": datetime.now(timezone.utc).isoformat()})
    chosen_dictionaries = {name: url for name, url in DICTIONARIES.items() if not args.only or args.only == f"{name}_dictionary"}
    for name, url in chosen_dictionaries.items():
        try:
            attempted.append(acquire_dictionary(name, url))
        except Exception as exc:
            attempted.append({"name": f"{name}_dictionary", "source_url": url, "status": "FAIL", "errors": [str(exc)], "completed_utc": datetime.now(timezone.utc).isoformat()})
    previous.update({item["name"]: item for item in attempted})
    run = {"started_utc": datetime.now(timezone.utc).isoformat(), "requested_only": args.only or "all", "attempted_sources": [item["name"] for item in attempted]}
    manifest = {"started_utc": datetime.now(timezone.utc).isoformat(), "tool": "scripts/acquire.py", "sources": list(previous.values()), "runs": previous_runs + [run], "safety": "MEData victim/bicycle person-level CSV files deliberately excluded; dictionaries only. ArcGIS extracts omit direct identifiers and addresses."}
    manifest["completed_utc"] = datetime.now(timezone.utc).isoformat()
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    passed = sum(item.get("status") == "PASS" for item in attempted)
    print(f"Fuentes con PASS en esta ejecución: {passed}/{len(attempted)}. Fuentes registradas: {len(manifest['sources'])}. Manifiesto: {MANIFEST.relative_to(ROOT)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
