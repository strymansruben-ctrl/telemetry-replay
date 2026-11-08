import unittest
from io import StringIO

from replay import analyze


class ReplayTests(unittest.TestCase):
    def scan(self, rows):
        return analyze(StringIO("time_ms,value\n" + rows), limit=70, max_gap_ms=150)

    def test_threshold_is_inclusive_and_exact_gap_limit_stays_contiguous(self):
        report = self.scan("0,70\n150,75\n250,69\n")
        self.assertEqual(report["alerts"], [
            {"first_ms": 0, "last_ms": 150, "samples": 2, "peak": 75.0}
        ])
        self.assertEqual(report["gaps"], [])

    def test_gap_splits_alerts_even_if_both_readings_are_high(self):
        report = self.scan("0,75\n200,76\n")
        self.assertEqual(report["gaps"], [{"after_ms": 0, "before_ms": 200, "gap_ms": 200}])
        self.assertEqual([alert["samples"] for alert in report["alerts"]], [1, 1])

    def test_below_limit_ends_alert(self):
        report = self.scan("0,75\n50,69\n100,71\n")
        self.assertEqual([alert["first_ms"] for alert in report["alerts"]], [0, 100])

    def test_valid_quiet_run(self):
        report = self.scan("0,20\n100,30\n")
        self.assertEqual(report["samples"], 2)
        self.assertEqual(report["alerts"], [])
        self.assertEqual(report["gaps"], [])

    def test_rejects_missing_invalid_or_unordered_samples(self):
        for rows in ("", "0,nan\n", "0,1,2\n", "-1,71\n", "0,70\n0,73\n", "1,70\n0,73\n"):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                self.scan(rows)
