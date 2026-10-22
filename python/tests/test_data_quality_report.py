
"""Unit tests for the NBFC data quality report generator."""

import importlib.util
import json
import unittest
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "reporting"
    / "generate_data_quality_report.py"
)

spec = importlib.util.spec_from_file_location(
    "generate_data_quality_report", SCRIPT_PATH
)
report_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report_module)


class TestReportHelpers(unittest.TestCase):
    def test_safe_converts_decimal_to_string(self):
        from decimal import Decimal

        self.assertEqual(report_module.safe(Decimal("123.45")), "123.45")

    def test_safe_converts_nested_values(self):
        from decimal import Decimal

        result = report_module.safe({
            "amount": Decimal("10.25"),
            "items": [Decimal("2.00")],
        })

        self.assertEqual(result, {
            "amount": "10.25",
            "items": ["2.00"],
        })

    def test_report_serializes_to_valid_json(self):
        sample = {
            "status": "PASS",
            "source_row_counts": {"loans": 8476},
            "checks": [{"name": "No null IDs", "status": "PASS"}],
        }

        encoded = json.dumps(report_module.safe(sample))
        decoded = json.loads(encoded)

        self.assertEqual(decoded["status"], "PASS")
        self.assertEqual(decoded["source_row_counts"]["loans"], 8476)

    def test_markdown_includes_status_counts_and_limitations(self):
        sample = {
            "status": "PASS",
            "generated_at_utc": "2026-10-22T00:00:00+00:00",
            "git_commit": "test-commit",
            "snowflake_session": {"active_role": "NBFC_CI_ROLE"},
            "source_row_counts": {
                "loans": 8476,
                "emi_schedule": 279486,
                "payments": 93753,
                "collections": 9136,
            },
            "metrics": {
                "total_source_rows_across_four_tables": 390851,
                "loan_requested_amount_summary": {
                    "null_requested": 0,
                    "negative_requested": 0,
                    "total_requested": "100.00",
                    "min_requested": "10.00",
                    "max_requested": "90.00",
                },
            },
            "checks": [
                {
                    "name": "No null loan IDs",
                    "status": "PASS",
                    "observed": 0,
                    "expected": 0,
                },
            ],
            "fact_table_metrics": {
                "status": "UNAVAILABLE",
                "reason": "Fact table not visible to the CI role.",
            },
            "limitations": [
                "This report covers corrected QA source tables only.",
            ],
        }

    def test_markdown_displays_failed_check(self):
        sample = {
            "status": "FAIL",
            "generated_at_utc": "2026-10-22T00:00:00+00:00",
            "git_commit": "test-commit",
            "snowflake_session": {"active_role": "NBFC_CI_ROLE"},
            "source_row_counts": {},
            "metrics": {
                "total_source_rows_across_four_tables": 0,
                "loan_requested_amount_summary": {},
            },
            "checks": [
                {
                    "name": "No null loan IDs",
                    "status": "FAIL",
                    "observed": 3,
                    "expected": 0,
                },
            ],
            "fact_table_metrics": {
                "status": "UNAVAILABLE",
                "reason": "Not available in this test.",
            },
            "limitations": [],
        }

        rendered = report_module.markdown(sample)

        self.assertIn("**Status:** FAIL", rendered)
        self.assertIn("No null loan IDs", rendered)
        self.assertIn("**FAIL**", rendered)
        self.assertIn("3", rendered)

    def test_connection_failure_returns_error_without_writing_reports(self):
        from unittest.mock import patch
        from contextlib import redirect_stderr
        from io import StringIO
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as temp_dir:
            report_dir = Path(temp_dir)
            markdown_path = report_dir / "data_quality_report.md"
            json_path = report_dir / "data_quality_report.json"
            error_output = StringIO()

            with (
                patch.object(report_module, "REPORT_DIR", report_dir),
                patch.object(report_module, "MD_PATH", markdown_path),
                patch.object(report_module, "JSON_PATH", json_path),
                patch.object(
                    report_module,
                    "run",
                    side_effect=RuntimeError("simulated connection failure"),
                ),
                redirect_stderr(error_output),
            ):
                exit_code = report_module.main()

            self.assertEqual(exit_code, 1)
            self.assertFalse(markdown_path.exists())
            self.assertFalse(json_path.exists())
            self.assertIn(
                "No successful report was written.",
                error_output.getvalue(),
            )

    def test_failed_quality_report_returns_exit_code_two(self):
        from unittest.mock import patch
        from contextlib import redirect_stdout
        from io import StringIO
        from tempfile import TemporaryDirectory

        failed_report = {
            "status": "FAIL",
            "checks": [{"name": "No null IDs", "status": "FAIL"}],
            "fact_table_metrics": {"status": "UNAVAILABLE"},
        }

        with TemporaryDirectory() as temp_dir:
            report_dir = Path(temp_dir)
            markdown_path = report_dir / "data_quality_report.md"
            json_path = report_dir / "data_quality_report.json"

            with (
                patch.object(report_module, "REPORT_DIR", report_dir),
                patch.object(report_module, "MD_PATH", markdown_path),
                patch.object(report_module, "JSON_PATH", json_path),
                patch.object(report_module, "run", return_value=failed_report),
                patch.object(report_module, "markdown", return_value="# FAIL"),
                redirect_stdout(StringIO()),
            ):
                exit_code = report_module.main()

            self.assertEqual(exit_code, 2)
            self.assertTrue(markdown_path.exists())
            self.assertTrue(json_path.exists())
if __name__ == "__main__":
    unittest.main()
