import unittest
from datetime import UTC, datetime
from unittest.mock import patch

from app.modules.enterprise_extension.engine import THRESHOLDS, evaluate, features


class FeatureEngineTests(unittest.TestCase):
    def test_invalid_timestamps_and_non_finite_amounts_are_ignored(self):
        now = datetime(2026, 10, 22, tzinfo=UTC)
        rows = [
            {
                "transaction_type": " DEPOSIT ",
                "amount": 125,
                "timestamp": "2026-10-21T10:00:00Z",
            },
            {
                "transaction_type": "DEPOSIT",
                "amount": float("nan"),
                "timestamp": "2026-10-21T10:00:00Z",
            },
            {"transaction_type": "DEPOSIT", "amount": 300, "timestamp": "not-a-date"},
        ]
        result = features(rows, now)
        self.assertEqual(result["transaction_rows"], 1)
        self.assertEqual(result["deposit_7d"], 125.0)

    def test_threshold_values_are_used_by_evaluator(self):
        now = datetime(2026, 10, 22, tzinfo=UTC)
        rows = [
            {
                "transaction_type": "DEPOSIT",
                "amount": 100,
                "timestamp": "2026-10-21T10:00:00Z",
            }
            for _ in range(3)
        ]
        result = features(rows, now)
        thresholds = dict(THRESHOLDS["AML-TXN-003"], min_count=4)
        with patch.dict(THRESHOLDS, {"AML-TXN-003": thresholds}):
            assessment = evaluate(
                result, {"country": "ZA", "customer_fica_compliant": True}, [], 0
            )
        self.assertEqual(assessment["rules"]["AML-TXN-003"]["status"], "CLEAR")

    def test_missing_transaction_and_network_data_are_not_reported_as_clear(self):
        assessment = evaluate(features([]), {"country": "ZA"}, [], None)
        self.assertEqual(assessment["assessment_status"], "INCOMPLETE")
        self.assertIn("AML-TXN-001", assessment["unavailable_rules"])
        self.assertIn("AML-NET-001", assessment["unavailable_rules"])


if __name__ == "__main__":
    unittest.main()
