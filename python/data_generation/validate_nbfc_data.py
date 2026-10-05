from pathlib import Path
import csv
from collections import Counter

DATA_DIR = Path("data/generated")


def read_csv(filename):
    path = DATA_DIR / filename

    with path.open("r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def check_unique(rows, column):
    values = [row[column] for row in rows]
    duplicates = [
        value
        for value, count in Counter(values).items()
        if count > 1
    ]
    return duplicates


def check_references(rows, column, valid_values):
    return [
        row[column]
        for row in rows
        if row[column] not in valid_values
    ]


def check_non_empty(rows, column):
    return [
        row
        for row in rows
        if not row[column]
    ]


def main():
    print("=" * 60)
    print("NBFC DATA QUALITY VALIDATION")
    print("=" * 60)

    branches = read_csv("branches.csv")
    customers = read_csv("customers.csv")
    applications = read_csv("loan_applications.csv")
    loans = read_csv("loans.csv")
    emi = read_csv("emi_schedule.csv")
    payments = read_csv("payments.csv")
    collections = read_csv("collections.csv")

    # Primary key sets
    branch_ids = {row["branch_id"] for row in branches}
    customer_ids = {row["customer_id"] for row in customers}
    application_ids = {row["application_id"] for row in applications}
    loan_ids = {row["loan_id"] for row in loans}

    print("\nROW COUNTS")
    print("-" * 60)

    for name, rows in [
        ("Branches", branches),
        ("Customers", customers),
        ("Loan Applications", applications),
        ("Loans", loans),
        ("EMI Schedule", emi),
        ("Payments", payments),
        ("Collections", collections),
    ]:
        print(f"{name:<25} {len(rows):>10,}")

    print("\nPRIMARY KEY CHECKS")
    print("-" * 60)

    primary_keys = [
        ("Branches", branches, "branch_id"),
        ("Customers", customers, "customer_id"),
        ("Applications", applications, "application_id"),
        ("Loans", loans, "loan_id"),
        ("Payments", payments, "payment_id"),
        ("Collections", collections, "collection_id"),
    ]

    for name, rows, column in primary_keys:
        duplicates = check_unique(rows, column)

        if duplicates:
            print(
                f"{name:<25} FAIL - "
                f"{len(duplicates):,} duplicate {column}"
            )
        else:
            print(f"{name:<25} PASS")

    print("\nREFERENTIAL INTEGRITY")
    print("-" * 60)

    checks = [
        (
            "Application -> Customer",
            check_references(
                applications,
                "customer_id",
                customer_ids,
            ),
        ),
        (
            "Application -> Branch",
            check_references(
                applications,
                "branch_id",
                branch_ids,
            ),
        ),
        (
            "Loan -> Application",
            check_references(
                loans,
                "application_id",
                application_ids,
            ),
        ),
        (
            "Loan -> Customer",
            check_references(
                loans,
                "customer_id",
                customer_ids,
            ),
        ),
        (
            "Loan -> Branch",
            check_references(
                loans,
                "branch_id",
                branch_ids,
            ),
        ),
        (
            "EMI -> Loan",
            check_references(
                emi,
                "loan_id",
                loan_ids,
            ),
        ),
        (
            "Payment -> Loan",
            check_references(
                payments,
                "loan_id",
                loan_ids,
            ),
        ),
        (
            "Collection -> Loan",
            check_references(
                collections,
                "loan_id",
                loan_ids,
            ),
        ),
    ]

    for name, invalid in checks:
        if invalid:
            print(
                f"{name:<25} FAIL - "
                f"{len(invalid):,} invalid references"
            )
        else:
            print(f"{name:<25} PASS")

    print("\nREQUIRED FIELD CHECKS")
    print("-" * 60)

    required_checks = [
        ("Customers", customers, [
            "customer_id",
            "customer_name",
            "credit_score",
        ]),
        ("Applications", applications, [
            "application_id",
            "customer_id",
            "branch_id",
        ]),
        ("Loans", loans, [
            "loan_id",
            "application_id",
            "customer_id",
            "branch_id",
        ]),
        ("EMI", emi, [
            "loan_id",
            "due_date",
            "emi_amount",
        ]),
        ("Payments", payments, [
            "payment_id",
            "loan_id",
            "payment_date",
            "payment_amount",
        ]),
        ("Collections", collections, [
            "collection_id",
            "loan_id",
            "collection_date",
            "amount_collected",
        ]),
    ]

    for name, rows, columns in required_checks:
        failures = []

        for column in columns:
            failures.extend(
                check_non_empty(rows, column)
            )

        if failures:
            print(
                f"{name:<25} FAIL - "
                f"{len(failures):,} empty required fields"
            )
        else:
            print(f"{name:<25} PASS")

    print("\nBUSINESS RANGE CHECKS")
    print("-" * 60)

    credit_score_errors = [
        row for row in customers
        if not 300 <= int(row["credit_score"]) <= 900
    ]

    income_errors = [
        row for row in customers
        if float(row["monthly_income"]) < 0
    ]

    loan_amount_errors = [
        row for row in loans
        if float(row["sanctioned_amount"]) <= 0
    ]

    interest_errors = [
        row for row in loans
        if not 0 < float(row["interest_rate"]) <= 40
    ]

    tenure_errors = [
        row for row in loans
        if int(row["tenure_months"]) <= 0
    ]

    checks = [
        ("Credit score 300-900", credit_score_errors),
        ("Income >= 0", income_errors),
        ("Sanctioned amount > 0", loan_amount_errors),
        ("Interest rate 0-40%", interest_errors),
        ("Loan tenure > 0", tenure_errors),
    ]

    for name, failures in checks:
        if failures:
            print(
                f"{name:<25} FAIL - "
                f"{len(failures):,} invalid records"
            )
        else:
            print(f"{name:<25} PASS")

    print("\n" + "=" * 60)
    print("VALIDATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()