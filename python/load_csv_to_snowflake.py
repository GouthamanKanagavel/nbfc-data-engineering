import csv
import os
from pathlib import Path
from decimal import Decimal

import snowflake.connector

ROOT = Path(__file__).resolve().parents[1]

TABLES = {
    "RAW.BRANCHES": ("data/generated/branches.csv", {
        "branch_id": "VARCHAR", "branch_name": "VARCHAR", "city": "VARCHAR",
        "state": "VARCHAR", "region": "VARCHAR", "branch_manager": "VARCHAR",
        "opening_date": "DATE",
    }),
    "RAW.CUSTOMERS": ("data/generated/customers.csv", {
        "customer_id": "VARCHAR", "customer_name": "VARCHAR",
        "date_of_birth": "DATE", "gender": "VARCHAR", "city": "VARCHAR",
        "state": "VARCHAR", "employment_type": "VARCHAR",
        "monthly_income": "NUMBER(14,2)", "credit_score": "NUMBER(5,0)",
        "customer_segment": "VARCHAR", "kyc_status": "VARCHAR",
        "created_at": "TIMESTAMP_NTZ",
    }),
    "RAW.LOAN_APPLICATIONS": ("data/generated/loan_applications.csv", {
        "application_id": "VARCHAR", "customer_id": "VARCHAR",
        "branch_id": "VARCHAR", "application_date": "DATE",
        "loan_type": "VARCHAR", "requested_amount": "NUMBER(14,2)",
        "tenure_months": "NUMBER(5,0)", "application_status": "VARCHAR",
        "risk_grade": "VARCHAR",
    }),
    "RAW.LOANS": ("data/generated/loans.csv", {
        "loan_id": "VARCHAR", "application_id": "VARCHAR",
        "customer_id": "VARCHAR", "branch_id": "VARCHAR",
        "application_date": "DATE", "loan_type": "VARCHAR",
        "requested_amount": "NUMBER(14,2)", "sanctioned_amount": "NUMBER(14,2)",
        "disbursed_amount": "NUMBER(14,2)", "disbursement_date": "DATE",
        "interest_rate": "NUMBER(8,4)", "tenure_months": "NUMBER(5,0)",
        "loan_status": "VARCHAR", "risk_grade": "VARCHAR",
    }),
    "RAW.EMI_SCHEDULE": ("data/generated/emi_schedule.csv", {
        "loan_id": "VARCHAR", "installment_number": "NUMBER(5,0)",
        "due_date": "DATE", "principal_due": "NUMBER(14,2)",
        "interest_due": "NUMBER(14,2)", "emi_amount": "NUMBER(14,2)",
    }),
    "RAW.PAYMENTS": ("data/generated/payments.csv", {
        "payment_id": "VARCHAR", "loan_id": "VARCHAR",
        "payment_date": "DATE", "payment_amount": "NUMBER(14,2)",
        "payment_mode": "VARCHAR", "payment_status": "VARCHAR",
    }),
    "RAW.COLLECTIONS": ("data/generated/collections.csv", {
        "collection_id": "VARCHAR", "loan_id": "VARCHAR",
        "collection_date": "DATE", "amount_collected": "NUMBER(14,2)",
        "collection_method": "VARCHAR", "collection_status": "VARCHAR",
    }),
    "QA.RAW_LOANS_V2": ("data/qa_corrected/loans.csv", {
        "loan_id": "VARCHAR", "application_id": "VARCHAR",
        "customer_id": "VARCHAR", "branch_id": "VARCHAR",
        "application_date": "DATE", "loan_type": "VARCHAR",
        "requested_amount": "NUMBER(14,2)", "sanctioned_amount": "NUMBER(14,2)",
        "disbursed_amount": "NUMBER(14,2)", "disbursement_date": "DATE",
        "interest_rate": "NUMBER(8,4)", "tenure_months": "NUMBER(5,0)",
        "loan_status": "VARCHAR", "risk_grade": "VARCHAR",
    }),
    "QA.RAW_EMI_SCHEDULE_V2": ("data/qa_corrected/emi_schedule.csv", {
        "loan_id": "VARCHAR", "installment_number": "NUMBER(5,0)",
        "due_date": "DATE", "principal_due": "NUMBER(14,2)",
        "interest_due": "NUMBER(14,2)", "emi_amount": "NUMBER(14,2)",
    }),
    "QA.RAW_PAYMENTS_V2": ("data/qa_corrected/payments.csv", {
        "payment_id": "VARCHAR", "loan_id": "VARCHAR",
        "payment_date": "DATE", "payment_amount": "NUMBER(14,2)",
        "payment_mode": "VARCHAR", "payment_status": "VARCHAR",
    }),
    "QA.RAW_COLLECTIONS_V2": ("data/qa_corrected/collections.csv", {
        "collection_id": "VARCHAR", "loan_id": "VARCHAR",
        "collection_date": "DATE", "amount_collected": "NUMBER(14,2)",
        "collection_method": "VARCHAR", "collection_status": "VARCHAR",
    }),
}
def convert(value, sql_type):
    value = value.strip()
    if not value:
        return None
    if sql_type.startswith("NUMBER"):
        return Decimal(value)
    return value


def main():
    required = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PRIVATE_KEY_PATH",
        "SNOWFLAKE_ROLE",
        "SNOWFLAKE_WAREHOUSE",
    ]
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise SystemExit("Missing environment variables: " + ", ".join(missing))

    key_path = Path(os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"]).expanduser()
    if not key_path.is_file():
        raise SystemExit(f"Private key not found: {key_path}")

    for table, (filename, _) in TABLES.items():
        if not (ROOT / filename).is_file():
            raise SystemExit(f"CSV file missing: {ROOT / filename}")

    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        private_key_file=str(key_path),
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database="NBFC_DW",
        schema="RAW",
    )

    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT CURRENT_DATABASE(), CURRENT_ROLE()")
            print("Connected:", cur.fetchone())

            # Stop rather than overwrite any existing destination table.
            for table in TABLES:
                schema, name = table.split(".")
                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM NBFC_DW.INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                    """,
                    (schema, name),
                )
                if cur.fetchone()[0]:
                    raise SystemExit(
                        f"STOP: NBFC_DW.{table} already exists. "
                        "Inspect it before loading."
                    )

            for table, (filename, columns) in TABLES.items():
                full_table = f"NBFC_DW.{table}"
                path = ROOT / filename
                definitions = ", ".join(
                    f'"{name}" {kind}' for name, kind in columns.items()
                )
                cur.execute(f"CREATE TABLE {full_table} ({definitions})")

                names = list(columns)
                quoted_names = ", ".join(f'"{name}"' for name in names)
                placeholders = ", ".join(["%s"] * len(names))
                insert_sql = (
                    f"INSERT INTO {full_table} ({quoted_names}) "
                    f"VALUES ({placeholders})"
                )

                loaded = 0
                with path.open(newline="", encoding="utf-8-sig") as file:
                    reader = csv.DictReader(file, skipinitialspace=True)
                    headers = [h.strip() for h in (reader.fieldnames or [])]
                    if headers != names:
                        raise ValueError(
                            f"Header mismatch in {path}: {headers}"
                        )

                    batch = []
                    for row in reader:
                        batch.append(tuple(
                            convert(row[name], columns[name]) for name in names
                        ))
                        if len(batch) == 1000:
                            cur.executemany(insert_sql, batch)
                            loaded += len(batch)
                            batch.clear()

                    if batch:
                        cur.executemany(insert_sql, batch)
                        loaded += len(batch)

                cur.execute(f"SELECT COUNT(*) FROM {full_table}")
                actual = cur.fetchone()[0]
                if actual != loaded:
                    raise RuntimeError(
                        f"{full_table}: expected {loaded}, found {actual}"
                    )
                print(f"Verified {full_table}: {actual:,} rows")

            conn.commit()
            print("All 11 tables loaded and verified.")
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
