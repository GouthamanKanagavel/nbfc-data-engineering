
#!/usr/bin/env python3
"""Read-only data-quality report for the corrected NBFC QA source tables."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

import snowflake.connector

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports"
MD_PATH = REPORT_DIR / "data_quality_report.md"
JSON_PATH = REPORT_DIR / "data_quality_report.json"

SOURCES = {
    "loans": "NBFC_DW.QA.RAW_LOANS_V2",
    "emi_schedule": "NBFC_DW.QA.RAW_EMI_SCHEDULE_V2",
    "payments": "NBFC_DW.QA.RAW_PAYMENTS_V2",
    "collections": "NBFC_DW.QA.RAW_COLLECTIONS_V2",
}


def git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime,)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    return value


def one(cursor: Any, sql: str) -> dict[str, Any]:
    cursor.execute(sql)
    row = cursor.fetchone()
    if row is None:
        raise RuntimeError("A metric query returned no rows.")
    columns = [item[0].lower() for item in cursor.description]
    return dict(zip(columns, row))


def run() -> dict[str, Any]:
    required = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PRIVATE_KEY_PATH",
    ]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError("Missing environment variables: " + ", ".join(missing))

    key_path = Path(os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"]).expanduser()
    if not key_path.is_file():
        raise RuntimeError("Configured Snowflake private key file was not found.")

    report: dict[str, Any] = {
        "report_name": "NBFC Corrected QA Source Data Quality Report",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "scope": {"source_tables": SOURCES},
        "status": "ERROR",
        "source_row_counts": {},
        "metrics": {},
        "checks": [],
        "fact_table_metrics": {
            "status": "UNAVAILABLE",
            "reason": (
                "FACT_LOAN_QA was not visible in NBFC_DW table metadata "
                "to the current CI role during this run."
            ),
        },
        "limitations": [
            "This report covers corrected QA source tables only.",
            "No fact-table, DPD, or PAR metrics are reported in this version.",
            "Passing source checks does not certify a reconciled financial ledger.",
            "Financial summaries are descriptive and not audited balances.",
        ],
    }

    conn = None
    try:
        conn = snowflake.connector.connect(
            account=os.environ["SNOWFLAKE_ACCOUNT"],
            user=os.environ["SNOWFLAKE_USER"],
            private_key_file=str(key_path),
            database="NBFC_DW",
            schema="QA",
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
            role=os.getenv("SNOWFLAKE_ROLE", "NBFC_CI_ROLE"),
            login_timeout=20,
            network_timeout=30,
        )

        with conn.cursor() as cur:
            report["snowflake_session"] = one(
                cur,
                """
                SELECT CURRENT_ACCOUNT() AS account_name,
                       CURRENT_ROLE() AS active_role,
                       CURRENT_DATABASE() AS active_database,
                       CURRENT_WAREHOUSE() AS active_warehouse
                """,
            )

            counts = {}
            for name, table in SOURCES.items():
                counts[name] = int(
                    one(cur, f"SELECT COUNT(*) AS n FROM {table}")["n"]
                )
            report["source_row_counts"] = counts

            loans = SOURCES["loans"]
            applications = "NBFC_DW.RAW.RAW_LOAN_APPLICATIONS"

            missing_apps = int(one(
                cur,
                f"""
                SELECT COUNT(*) AS n
                FROM {loans} l
                LEFT JOIN {applications} a
                  ON l.application_id = a.application_id
                WHERE a.application_id IS NULL
                """,
            )["n"])

            app_mismatches = int(one(
                cur,
                f"""
                SELECT COUNT(*) AS n
                FROM {loans} l
                INNER JOIN {applications} a
                  ON l.application_id = a.application_id
                WHERE l.customer_id IS DISTINCT FROM a.customer_id
                   OR l.branch_id IS DISTINCT FROM a.branch_id
                   OR l.application_date IS DISTINCT FROM a.application_date
                   OR l.loan_type IS DISTINCT FROM a.loan_type
                   OR l.requested_amount IS DISTINCT FROM a.requested_amount
                   OR l.tenure_months IS DISTINCT FROM a.tenure_months
                   OR l.risk_grade IS DISTINCT FROM a.risk_grade
                   OR a.application_status IS DISTINCT FROM 'APPROVED'
                """,
            )["n"])

            loan_keys = one(
                cur,
                f"""
                SELECT COUNT_IF(loan_id IS NULL) AS null_ids,
                       COUNT(*) - COUNT(DISTINCT loan_id) AS duplicate_rows
                FROM {loans}
                """,
            )

            orphans = {}
            for label in ("emi_schedule", "payments", "collections"):
                child = SOURCES[label]
                orphans[label] = int(one(
                    cur,
                    f"""
                    SELECT COUNT(*) AS n
                    FROM {child} c
                    LEFT JOIN {loans} l ON c.loan_id = l.loan_id
                    WHERE l.loan_id IS NULL
                    """,
                )["n"])

            financial = one(
                cur,
                f"""
                SELECT
                    COUNT_IF(requested_amount IS NULL) AS null_requested,
                    COUNT_IF(requested_amount < 0) AS negative_requested,
                    SUM(requested_amount) AS total_requested,
                    MIN(requested_amount) AS min_requested,
                    MAX(requested_amount) AS max_requested
                FROM {loans}
                """,
            )

            checks = [
                {
                    "name": "No missing loan application links",
                    "status": "PASS" if missing_apps == 0 else "FAIL",
                    "observed": missing_apps,
                    "expected": 0,
                },
                {
                    "name": "Loan/application fields consistent and application approved",
                    "status": "PASS" if app_mismatches == 0 else "FAIL",
                    "observed": app_mismatches,
                    "expected": 0,
                },
                {
                    "name": "No null loan IDs",
                    "status": "PASS" if int(loan_keys["null_ids"]) == 0 else "FAIL",
                    "observed": int(loan_keys["null_ids"]),
                    "expected": 0,
                },
                {
                    "name": "No duplicate loan IDs",
                    "status": (
                        "PASS" if int(loan_keys["duplicate_rows"]) == 0 else "FAIL"
                    ),
                    "observed": int(loan_keys["duplicate_rows"]),
                    "expected": 0,
                },
            ]

            for label, value in orphans.items():
                checks.append({
                    "name": f"No orphan {label} loan references",
                    "status": "PASS" if value == 0 else "FAIL",
                    "observed": value,
                    "expected": 0,
                })

            invalid_money = (
                int(financial["null_requested"]) > 0
                or int(financial["negative_requested"]) > 0
            )
            checks.append({
                "name": "Requested amounts are present and non-negative",
                "status": "FAIL" if invalid_money else "PASS",
                "observed": {
                    "null": int(financial["null_requested"]),
                    "negative": int(financial["negative_requested"]),
                },
                "expected": {"null": 0, "negative": 0},
            })

            report["metrics"] = {
                "loan_application_missing_links": missing_apps,
                "loan_application_consistency_violations": app_mismatches,
                "loan_key_quality": safe(loan_keys),
                "orphan_child_records": orphans,
                "loan_requested_amount_summary": safe(financial),
                "total_source_rows_across_four_tables": sum(counts.values()),
            }
            report["checks"] = checks
            report["status"] = (
                "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
            )

    finally:
        if conn is not None:
            conn.close()

    return report


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NBFC Corrected QA Source Data Quality Report",
        "",
        f"- **Status:** {report['status']}",
        f"- **Generated UTC:** {report['generated_at_utc']}",
        f"- **Git commit:** {report.get('git_commit') or 'unavailable'}",
        f"- **Snowflake role:** {report.get('snowflake_session', {}).get('active_role', 'unavailable')}",
        "",
        "## Source row counts",
        "",
        "| Source table | Rows |",
        "|---|---:|",
    ]
    for name, count in report["source_row_counts"].items():
        lines.append(f"| `{name}` | {count:,} |")

    lines.extend([
        "",
        f"**Total rows across source tables:** "
        f"{report['metrics']['total_source_rows_across_four_tables']:,}",
        "",
        "## Data quality checks",
        "",
        "| Check | Status | Observed |",
        "|---|---|---:|",
    ])
    for check in report["checks"]:
        lines.append(
            f"| {check['name']} | **{check['status']}** | "
            f"`{json.dumps(safe(check['observed']))}` |"
        )

    lines.extend([
        "",
        "## Requested amount summary",
        "",
        "```json",
        json.dumps(
            safe(report["metrics"]["loan_requested_amount_summary"]),
            indent=2,
        ),
        "```",
        "",
        "## Fact table metrics",
        "",
        f"**{report['fact_table_metrics']['status']}** — "
        f"{report['fact_table_metrics']['reason']}",
        "",
        "## Limitations",
        "",
    ])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        report = run()
    except Exception as exc:
        print(
            f"Report generation failed ({type(exc).__name__}): {exc}",
            file=sys.stderr,
        )
        print("No successful report was written.", file=sys.stderr)
        return 1

    JSON_PATH.write_text(
        json.dumps(safe(report), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    MD_PATH.write_text(markdown(report), encoding="utf-8")

    failures = sum(c["status"] == "FAIL" for c in report["checks"])
    print(f"Report status: {report['status']}")
    print(f"Markdown: {MD_PATH}")
    print(f"JSON: {JSON_PATH}")
    print(f"Checks: {len(report['checks'])}")
    print(f"Failed checks: {failures}")
    print(f"Fact table metrics: {report['fact_table_metrics']['status']}")
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
