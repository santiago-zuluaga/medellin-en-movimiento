"""Pruebas de invariantes sobre fixtures manuales, no datos del proyecto."""
import unittest

from data_model import aggregate, filter_rows


class DataModelTests(unittest.TestCase):
    def setUp(self):
        self.incidents = [
            {"fecha_siniestro": "2020-02-03", "hora_siniestro": "08:15:00", "nom_comuna": "A", "clase_siniestro": "Choque", "gravedad_siniestro": "HERIDOS", "_geometry": {"type": "Point", "coordinates": [-75.6, 6.2]}},
            {"fecha_siniestro": "2020-02-03", "hora_siniestro": "08:40:00", "nom_comuna": "A", "clase_siniestro": "Atropello", "gravedad_siniestro": "DAÑOS", "_geometry": {"type": "Point", "coordinates": [-75.6, 6.2]}},
            {"fecha_siniestro": "2020-02-03", "hora_siniestro": "08:15:00", "nom_comuna": "A", "clase_siniestro": "Choque", "gravedad_siniestro": "HERIDOS", "_geometry": {"type": "Point", "coordinates": [-75.6, 6.2]}},
            {"fecha_siniestro": "2020-02-03", "hora_siniestro": "08:15:00", "nom_comuna": "A", "clase_siniestro": "Choque", "gravedad_siniestro": "HERIDOS", "_geometry": {"type": "Point", "coordinates": [-75.6, 6.2]}},
            {"fecha_siniestro": "2020-02-03", "hora_siniestro": "08:15:00", "nom_comuna": "A", "clase_siniestro": "Choque", "gravedad_siniestro": "HERIDOS", "_geometry": {"type": "Point", "coordinates": [-75.6, 6.2]}},
            {"fecha_siniestro": "2021-03-04", "hora_siniestro": "17:05:00", "nom_comuna": "B", "clase_siniestro": "Choque", "gravedad_siniestro": "HERIDOS", "_geometry": {"type": "Point", "coordinates": [-75.5, 6.3]}},
        ]

    def test_filters_produce_same_record_totals_across_aggregations(self):
        selected = filter_rows(self.incidents, "incidents", {"year": "2020", "community": "A", "category": "", "severity": ""})
        summary = aggregate(selected, "incidents")
        self.assertEqual(summary["records"], 5)
        self.assertEqual(sum(summary["years"].values()), summary["records"])
        self.assertEqual(sum(summary["communities"].values()), summary["records"])
        self.assertEqual(sum(summary["categories"].values()), summary["records"])
        self.assertEqual(sum(summary["severities"].values()), summary["records"])
        self.assertEqual(sum(cell["count"] for cell in summary["cells"]), 5)

    def test_severity_and_category_filters_are_coherent(self):
        selected = filter_rows(self.incidents, "incidents", {"year": "", "community": "", "category": "Choque", "severity": "HERIDOS"})
        self.assertEqual(len(selected), 5)

    def test_weekday_and_hour_are_applied_together(self):
        selected = filter_rows(self.incidents, "incidents", {"weekday": "0", "hour": "8"})
        self.assertEqual(len(selected), 5)
        selected = filter_rows(self.incidents, "incidents", {"weekday": "3", "hour": "8"})
        self.assertEqual(selected, [])

    def test_mortality_has_no_incident_severity_filter(self):
        rows = [{"fecha_ocurrencia": "3/02/2020", "hora_ocurrencia": "13:00:00", "nom_comuna": "A", "clase": "Choque", "_geometry": None}]
        self.assertEqual(len(filter_rows(rows, "mortality", {"severity": "HERIDOS"})), 1)
        self.assertEqual(aggregate(rows, "mortality")["records"], 1)

    def test_records_are_not_combined_across_units(self):
        incidents = aggregate(self.incidents, "incidents")
        mortality = aggregate([{"fecha_ocurrencia": "03/02/2020", "hora_ocurrencia": "13:00:00", "nom_comuna": "A", "clase": "Choque", "_geometry": None}], "mortality")
        self.assertEqual(incidents["records"], 6)
        self.assertEqual(mortality["records"], 1)
        self.assertNotEqual(incidents["unit"], mortality["unit"])


if __name__ == "__main__":
    unittest.main()
