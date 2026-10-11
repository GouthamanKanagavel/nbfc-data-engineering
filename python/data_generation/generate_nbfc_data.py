from pathlib import Path
from datetime import date, timedelta
import csv
import random


random.seed(42)

OUTPUT_DIR = Path("data/generated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CUSTOMERS = 10_000
BRANCHES = 50
LOANS = 10_000

REPORTING_DATE = date(2026, 10, 7)


def random_date(start, end):
    if start > end:
        return start

    days = (end - start).days
    return start + timedelta(days=random.randint(0, days))


def write_csv(filename, rows, fieldnames):
    path = OUTPUT_DIR / filename

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {path}: {len(rows):,} rows")


def generate_branches():
    rows = []

    states = [
        "Tamil Nadu",
        "Karnataka",
        "Kerala",
        "Andhra Pradesh",
        "Telangana",
        "Maharashtra",
        "Gujarat",
        "Delhi",
    ]

    cities = [
        "Chennai",
        "Bengaluru",
        "Coimbatore",
        "Madurai",
        "Hyderabad",
        "Pune",
        "Mumbai",
        "Kochi",
    ]

    for i in range(1, BRANCHES + 1):
        rows.append(
            {
                "branch_id": f"BR{i:04d}",
                "branch_name": f"NBFC Branch {i:04d}",
                "city": random.choice(cities),
                "state": random.choice(states),
                "region": random.choice(
                    ["South", "West", "North", "Central"]
                ),
                "branch_manager": f"Manager {i:04d}",
                "opening_date": random_date(
                    date(2015, 1, 1),
                    date(2024, 1, 1),
                ).isoformat(),
            }
        )

    write_csv(
        "branches.csv",
        rows,
        [
            "branch_id",
            "branch_name",
            "city",
            "state",
            "region",
            "branch_manager",
            "opening_date",
        ],
    )


def generate_customers():
    rows = []

    employment_types = [
        "SALARIED",
        "SELF_EMPLOYED",
        "BUSINESS_OWNER",
    ]

    segments = [
        "PRIME",
        "STANDARD",
        "SUB_PRIME",
    ]

    cities = [
        "Chennai",
        "Bengaluru",
        "Coimbatore",
        "Madurai",
        "Hyderabad",
        "Pune",
        "Mumbai",
        "Kochi",
    ]

    for i in range(1, CUSTOMERS + 1):
        rows.append(
            {
                "customer_id": f"CUST{i:06d}",
                "customer_name": f"Customer {i:06d}",
                "date_of_birth": random_date(
                    date(1970, 1, 1),
                    date(2000, 12, 31),
                ).isoformat(),
                "gender": random.choice(["M", "F"]),
                "city": random.choice(cities),
                "state": random.choice(
                    [
                        "Tamil Nadu",
                        "Karnataka",
                        "Kerala",
                        "Andhra Pradesh",
                        "Telangana",
                        "Maharashtra",
                    ]
                ),
                "employment_type": random.choice(employment_types),
                "monthly_income": round(
                    random.uniform(20_000, 250_000), 2
                ),
                "credit_score": random.randint(550, 850),
                "customer_segment": random.choice(segments),
                "kyc_status": random.choice(
                    ["VERIFIED", "VERIFIED", "VERIFIED", "PENDING"]
                ),
                "created_at": random_date(
                    date(2023, 1, 1),
                    date(2026, 9, 30),
                ).isoformat(),
            }
        )

    write_csv(
        "customers.csv",
        rows,
        [
            "customer_id",
            "customer_name",
            "date_of_birth",
            "gender",
            "city",
            "state",
            "employment_type",
            "monthly_income",
            "credit_score",
            "customer_segment",
            "kyc_status",
            "created_at",
        ],
    )



def generate_loan_applications():
    rows = []

    for i in range(1, LOANS + 1):
        application_date = random_date(
            date(2024, 1, 1),
            date(2026, 9, 20),
        )

        rows.append(
            {
                "application_id": f"APP{i:08d}",
                "customer_id": f"CUST{random.randint(1, CUSTOMERS):06d}",
                "branch_id": f"BR{random.randint(1, BRANCHES):04d}",
                "application_date": application_date.isoformat(),
                "loan_type": random.choice(
                    [
                        "PERSONAL",
                        "VEHICLE",
                        "BUSINESS",
                        "CONSUMER_DURABLE",
                    ]
                ),
                "requested_amount": round(
                    random.uniform(50_000, 2_000_000), 2
                ),
                "tenure_months": random.choice(
                    [12, 18, 24, 36, 48, 60]
                ),
                "application_status": random.choices(
                    ["APPROVED", "REJECTED", "PENDING"],
                    weights=[85, 10, 5],
                    k=1,
                )[0],
                "risk_grade": random.choice(["A", "B", "C", "D", "E"]),
            }
        )

    write_csv(
        "loan_applications.csv",
        rows,
        [
            "application_id",
            "customer_id",
            "branch_id",
            "application_date",
            "loan_type",
            "requested_amount",
            "tenure_months",
            "application_status",
            "risk_grade",
        ],
    )

    return rows


def generate_loans(application_rows):
    rows = []

    for application in application_rows:
        if application["application_status"] != "APPROVED":
            continue

        application_date = date.fromisoformat(
            application["application_date"]
        )
        disbursement_date = application_date + timedelta(
            days=random.randint(1, 15)
        )

        amount = float(application["requested_amount"])
        tenure = int(application["tenure_months"])

        rows.append(
            {
                "loan_id": f"LOAN{len(rows) + 1:08d}",
                "application_id": application["application_id"],
                "customer_id": application["customer_id"],
                "branch_id": application["branch_id"],
                "application_date": application["application_date"],
                "loan_type": application["loan_type"],
                "requested_amount": amount,
                "sanctioned_amount": amount,
                "disbursed_amount": amount,
                "disbursement_date": disbursement_date.isoformat(),
                "interest_rate": round(random.uniform(9.5, 24.0), 2),
                "tenure_months": tenure,
                "loan_status": random.choice(
                    ["ACTIVE", "ACTIVE", "ACTIVE", "CLOSED", "NPA"]
                ),
                "risk_grade": application["risk_grade"],
            }
        )

    write_csv(
        "loans.csv",
        rows,
        [
            "loan_id",
            "application_id",
            "customer_id",
            "branch_id",
            "application_date",
            "loan_type",
            "requested_amount",
            "sanctioned_amount",
            "disbursed_amount",
            "disbursement_date",
            "interest_rate",
            "tenure_months",
            "loan_status",
            "risk_grade",
        ],
    )

    return rows


def generate_emi_schedule(loan_rows):
    rows = []

    for loan in loan_rows:
        loan_id = loan["loan_id"]
        principal = float(loan["disbursed_amount"])
        tenure = int(loan["tenure_months"])

        # First EMI approximately one month after disbursement.
        disbursement_date = date.fromisoformat(
            loan["disbursement_date"]
        )

        emi = round(principal / tenure, 2)

        for installment in range(1, tenure + 1):
            due_date = disbursement_date + timedelta(
                days=30 * installment
            )

            principal_due = round(emi * 0.80, 2)
            interest_due = round(emi * 0.20, 2)

            rows.append(
                {
                    "loan_id": loan_id,
                    "installment_number": installment,
                    "due_date": due_date.isoformat(),
                    "principal_due": principal_due,
                    "interest_due": interest_due,
                    "emi_amount": emi,
                }
            )

    write_csv(
        "emi_schedule.csv",
        rows,
        [
            "loan_id",
            "installment_number",
            "due_date",
            "principal_due",
            "interest_due",
            "emi_amount",
        ],
    )

    return rows


def generate_payments(loan_rows, emi_rows):
    rows = []
    payment_id = 1

    emi_by_loan = {}

    for emi in emi_rows:
        emi_by_loan.setdefault(
            emi["loan_id"],
            []
        ).append(emi)

    for loan in loan_rows:
        loan_id = loan["loan_id"]
        disbursement_date = date.fromisoformat(
            loan["disbursement_date"]
        )

        loan_emis = emi_by_loan[loan_id]

        due_emis = [
            emi
            for emi in loan_emis
            if date.fromisoformat(emi["due_date"]) <= REPORTING_DATE
        ]

        if not due_emis:
            continue

        # Payment behavior:
        # 75% regular/current
        # 15% delayed
        # 10% severely delinquent/no payment
        behavior = random.choices(
            ["CURRENT", "DELAYED", "DELINQUENT"],
            weights=[75, 15, 10],
            k=1,
        )[0]

        if behavior == "DELINQUENT":
            payment_ratio = random.uniform(0.0, 0.30)

        elif behavior == "DELAYED":
            payment_ratio = random.uniform(0.40, 0.80)

        else:
            payment_ratio = random.uniform(0.85, 1.00)

        target_payment_count = max(
            1,
            int(len(due_emis) * payment_ratio)
        )

        selected_emis = due_emis[:target_payment_count]

        for emi in selected_emis:
            due_date = date.fromisoformat(
                emi["due_date"]
            )

            if behavior == "CURRENT":
                payment_date = due_date + timedelta(
                    days=random.randint(-3, 5)
                )

            elif behavior == "DELAYED":
                payment_date = due_date + timedelta(
                    days=random.randint(10, 45)
                )

            else:
                payment_date = due_date + timedelta(
                    days=random.randint(30, 120)
                )

            # Never create a payment before disbursement
            if payment_date < disbursement_date:
                payment_date = disbursement_date

            # Never create a future payment
            if payment_date > REPORTING_DATE:
                continue

            payment_amount = round(
                float(emi["emi_amount"])
                * random.uniform(0.80, 1.05),
                2,
            )

            payment_status = random.choices(
                ["SUCCESS", "FAILED"],
                weights=[95, 5],
                k=1,
            )[0]

            rows.append(
                {
                    "payment_id": f"PAY{payment_id:09d}",
                    "loan_id": loan_id,
                    "payment_date": payment_date.isoformat(),
                    "payment_amount": payment_amount,
                    "payment_mode": random.choice(
                        [
                            "UPI",
                            "BANK_TRANSFER",
                            "NACH",
                            "CHEQUE",
                            "CASH",
                        ]
                    ),
                    "payment_status": payment_status,
                }
            )

            payment_id += 1

    write_csv(
        "payments.csv",
        rows,
        [
            "payment_id",
            "loan_id",
            "payment_date",
            "payment_amount",
            "payment_mode",
            "payment_status",
        ],
    )

    return rows


def generate_collections(loan_rows, emi_rows):
    rows = []
    collection_id = 1

    emi_by_loan = {}

    for emi in emi_rows:
        emi_by_loan.setdefault(
            emi["loan_id"],
            []
        ).append(emi)

    for loan in loan_rows:
        loan_id = loan["loan_id"]

        loan_emis = emi_by_loan[loan_id]

        overdue_emis = [
            emi
            for emi in loan_emis
            if date.fromisoformat(emi["due_date"]) < REPORTING_DATE
        ]

        if not overdue_emis:
            continue

        # Collections are concentrated on delinquent loans.
        if random.random() > 0.35:
            continue

        collection_count = random.randint(
            1,
            min(6, len(overdue_emis))
        )

        selected_emis = random.sample(
            overdue_emis,
            collection_count
        )

        for emi in selected_emis:
            due_date = date.fromisoformat(
                emi["due_date"]
            )

            collection_date = due_date + timedelta(
                days=random.randint(1, 30)
            )

            if collection_date > REPORTING_DATE:
                collection_date = REPORTING_DATE

            amount_collected = round(
                float(emi["emi_amount"])
                * random.uniform(0.30, 1.00),
                2,
            )

            collection_status = random.choices(
                ["SUCCESS", "PARTIAL", "FAILED"],
                weights=[75, 20, 5],
                k=1,
            )[0]

            rows.append(
                {
                    "collection_id": f"COL{collection_id:09d}",
                    "loan_id": loan_id,
                    "collection_date": collection_date.isoformat(),
                    "amount_collected": amount_collected,
                    "collection_method": random.choice(
                        [
                            "FIELD_AGENT",
                            "CALL_CENTER",
                            "BRANCH",
                            "DIGITAL",
                        ]
                    ),
                    "collection_status": collection_status,
                }
            )

            collection_id += 1

    write_csv(
        "collections.csv",
        rows,
        [
            "collection_id",
            "loan_id",
            "collection_date",
            "amount_collected",
            "collection_method",
            "collection_status",
        ],
    )

    return rows


def main():
    generate_branches()
    generate_customers()
    application_rows = generate_loan_applications()
    loan_rows = generate_loans(application_rows)

    emi_rows = generate_emi_schedule(
        loan_rows
    )

    generate_payments(
        loan_rows,
        emi_rows,
    )

    generate_collections(
        loan_rows,
        emi_rows,
    )

    print("\nNBFC synthetic data generation completed.")


if __name__ == "__main__":
    main()