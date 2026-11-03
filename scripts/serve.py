#!/usr/bin/env python3
"""Sirve la aplicación estática y agregaciones locales sin librerías externas."""
from __future__ import annotations
import os
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from data_model import ROOT, SOURCES, aggregate, filter_rows, read_source

WEB = ROOT / "web"
INCIDENTS = None
MORTALITY = None
BOUNDARY = None


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def send_json(self, value: dict, status: int = 200):
        payload = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        global INCIDENTS, MORTALITY, BOUNDARY
        parsed = urlparse(self.path)
        if parsed.path == "/api/data":
            params = parse_qs(parsed.query)
            dataset = params.get("dataset", ["incidents"])[0]
            if dataset not in SOURCES:
                return self.send_json({"error": "dataset no reconocido"}, 400)
            try:
                if dataset == "incidents":
                    INCIDENTS = INCIDENTS if INCIDENTS is not None else read_source(dataset)
                    rows = INCIDENTS
                else:
                    MORTALITY = MORTALITY if MORTALITY is not None else read_source(dataset)
                    rows = MORTALITY
                filters = {
                    "year": params.get("year", [""])[0],
                    "community": params.get("community", [""])[0],
                    "category": params.get("category", [""])[0],
                    "severity": params.get("severity", [""])[0],
                    "hour": params.get("hour", [""])[0],
                    "weekday": params.get("weekday", [""])[0],
                    "cell": params.get("cell", [""])[0],
                }
                selected = filter_rows(rows, dataset, filters)
                return self.send_json(aggregate(selected, dataset, rows))
            except FileNotFoundError as exc:
                return self.send_json({"error": f"No hay datos locales: {exc}. Ejecuta python scripts/acquire.py primero."}, 503)
        if parsed.path == "/api/boundary":
            try:
                path = ROOT / "data" / "raw" / "limite_municipal.geojson"
                if BOUNDARY is None:
                    BOUNDARY = json.loads(path.read_text(encoding="utf-8"))
                return self.send_json(BOUNDARY)
            except FileNotFoundError:
                return self.send_json({"error": "No se adquirió la geometría municipal"}, 503)
        return super().do_GET()

    def log_message(self, format, *args):
        print("[web] " + (format % args))


def main():
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))

    print(f"Aplicación disponible en http://{host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()

if __name__ == "__main__":
    main()
