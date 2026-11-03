"""Pruebas de integración contra la app local usando archivos reales si están adquiridos."""
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen
from urllib.error import HTTPError

from serve import Handler

ROOT = Path(__file__).resolve().parents[1]


class LocalApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=2)
        cls.server.server_close()

    def get_json(self, path):
        with urlopen(self.base + path, timeout=30) as response:
            return json.loads(response.read())

    def require_data(self):
        path = ROOT / "data" / "raw" / "siniestralidad_2019_2025.geojson"
        if not path.exists():
            self.skipTest("Ejecuta scripts/acquire.py para probar con datos reales")

    def test_shared_filters_keep_all_view_totals_coherent(self):
        self.require_data()
        data = self.get_json("/api/data?dataset=incidents&year=2019&community=La%20Candelaria")
        self.assertGreater(data["records"], 0)
        self.assertEqual(sum(data["years"].values()), data["records"])
        self.assertEqual(sum(data["months"].values()), data["records"])
        self.assertEqual(sum(data["communities"].values()), data["records"])
        self.assertEqual(sum(data["categories"].values()), data["records"])
        self.assertEqual(sum(data["severities"].values()), data["records"])

    def test_api_never_returns_source_ids_or_unrounded_points(self):
        self.require_data()
        data = self.get_json("/api/data?dataset=incidents&year=2019")
        self.assertTrue(all(cell["count"] >= 5 for cell in data["cells"]))
        self.assertTrue(all(round(cell["longitude"], 2) == cell["longitude"] and round(cell["latitude"], 2) == cell["latitude"] for cell in data["cells"]))
        self.assertNotIn("objectid", json.dumps(data).lower())
        self.assertNotIn("radicado", json.dumps(data).lower())

    def test_separate_sources_have_distinct_units_and_severity_contract(self):
        self.require_data()
        incidents = self.get_json("/api/data?dataset=incidents")
        mortality = self.get_json("/api/data?dataset=mortality")
        self.assertNotEqual(incidents["unit"], mortality["unit"])
        self.assertTrue(incidents["severities"])
        self.assertEqual(mortality["severities"], {})

    def test_incident_payload_supplies_each_explore_visualization(self):
        self.require_data()
        data = self.get_json("/api/data?dataset=incidents")
        for key in ("records", "years", "months", "coverage_months", "communities", "categories", "severities", "weekday_hours", "cells"):
            self.assertIn(key, data)
        self.assertEqual(sum(data["months"].values()), data["records"])
        self.assertEqual(sum(data["communities"].values()), data["records"])
        self.assertEqual(sum(data["categories"].values()), data["records"])
        self.assertEqual(sum(data["severities"].values()), data["records"])
        self.assertTrue(data["weekday_hours"])
        self.assertTrue(all(cell["count"] >= 5 for cell in data["cells"]))

    def test_map_and_weekday_hour_selections_filter_api_rows(self):
        self.require_data()
        all_rows = self.get_json("/api/data?dataset=incidents")
        monday_morning = self.get_json("/api/data?dataset=incidents&weekday=0&hour=8")
        self.assertGreater(monday_morning["records"], 0)
        self.assertLess(monday_morning["records"], all_rows["records"])
        self.assertEqual(
            sum(monday_morning["weekday_hours"][i]["count"] for i in range(len(monday_morning["weekday_hours"]))),
            monday_morning["records"],
        )
        self.assertTrue(all(item["weekday"] == 0 and item["hour"] == 8 for item in monday_morning["weekday_hours"]))

        cell = all_rows["cells"][0]
        cell_value = quote(f'{cell["longitude"]:.2f},{cell["latitude"]:.2f}', safe="")
        selected_cell = self.get_json(f"/api/data?dataset=incidents&cell={cell_value}")
        self.assertEqual(selected_cell["records"], cell["count"])
        self.assertTrue(all(
            item["longitude"] == cell["longitude"] and item["latitude"] == cell["latitude"]
            for item in selected_cell["cells"]
        ))

    def test_unknown_dataset_returns_client_error(self):
        with self.assertRaises(HTTPError) as context:
            self.get_json("/api/data?dataset=victims")
        self.assertEqual(context.exception.code, 400)

    def test_static_app_and_assets_are_served(self):
        with urlopen(self.base + "/", timeout=10) as response:
            self.assertEqual(response.status, 200)
            self.assertIn("Medellín en movimiento".encode("utf-8"), response.read())
        with urlopen(self.base + "/app.js", timeout=10) as response:
            self.assertEqual(response.status, 200)
            self.assertIn("javascript", response.headers.get("Content-Type", ""))


if __name__ == "__main__":
    unittest.main()
