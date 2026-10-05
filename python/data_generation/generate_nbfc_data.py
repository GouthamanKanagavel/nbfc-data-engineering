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


def random_date(start, end):
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


def generate_loans():
    rows = []

    loan_types = [
        "PERSONAL",
        "VEHICLE",
        "BUSINESS",
        "CONSUMER_DURABLE",
    ]

    statuses = [
        "ACTIVE",
        "ACTIVE",
        "ACTIVE",
        "CLOSED",
        "NPA",
    ]

    start_date = date(2024, 1, 1)
    end_date = date(2026, 9, 30)

    for i in range(1, LOANS + 1):
        application_date = random_date(start_date, end_date)
        disbursement_date = application_date + timedelta(
            days=random.randint(1, 15)
        )

        amount = round(random.uniform(50_000, 2_000_000), 2)
        interest_rate = round(random.uniform(9.5, 24.0), 2)
        tenure = random.choice([12, 18, 24, 36, 48, 60])

        rows.append(
            {
                "loan_id": f"LOAN{i:08d}",
                "application_id": f"APP{i:08d}",
                "customer_id": f"CUST{random.randint(1, CUSTOMERS):06d}",
                "branch_id": f"BR{random.randint(1, BRANCHES):04d}",
                "application_date": application_date.isoformat(),
                "loan_type": random.choice(loan_types),
                "requested_amount": amount,
                "sanctioned_amount": amount,
                "disbursed_amount": amount,
                "disbursement_date": disbursement_date.isoformat(),
                "interest_rate": interest_rate,
                "tenure_months": tenure,
                "loan_status": random.choice(statuses),
                "risk_grade": random.choice(
                    ["A", "B", "C", "D", "E"]
                ),
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


def generate_loan_applications():
    rows = []

    for i in range(1, LOANS + 1):
        rows.append(
            {
                "application_id": f"APP{i:08d}",
                "customer_id": f"CUST{random.randint(1, CUSTOMERS):06d}",
                "branch_id": f"BR{random.randint(1, BRANCHES):04d}",
                "application_date": random_date(
                    date(2024, 1, 1),
                    date(2026, 9, 30),
                ).isoformat(),
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
                "application_status": random.choice(
                    ["APPROVED", "APPROVED", "REJECTED", "PENDING"]
                ),
                "risk_grade": random.choice(
                    ["A", "B", "C", "D", "E"]
                ),
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


def generate_emi_schedule():
    rows = []

    for loan_number in range(1, LOANS + 1):
        loan_id = f"LOAN{loan_number:08d}"

        principal = round(
            random.uniform(50_000, 2_000_000), 2
        )

        tenure = random.choice([12, 18, 24, 36])

        emi = round(principal / tenure, 2)

        start = date(2024, 1, 1)

        for installment in range(1, tenure + 1):
            due_date = start + timedelta(
                days=30 * installment
            )

            rows.append(
                {
                    "loan_id": loan_id,
                    "installment_number": installment,
                    "due_date": due_date.isoformat(),
                    "principal_due": round(
                        emi * 0.8, 2
                    ),
                    "interest_due": round(
                        emi * 0.2, 2
                    ),
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

def generate_payments():
    rows = []
    payment_id = 1

    for loan_number in range(1, LOANS + 1):
        loan_id = f"LOAN{loan_number:08d}"

        # Not every loan has payment history yet
        if random.random() > 0.70:
            continue

        payment_count = random.randint(3, 18)

        for _ in range(payment_count):
            payment_date = random_date(
                date(2024, 2, 1),
                date(2026, 9, 30)
            )

            payment_amount = round(
                random.uniform(2_000, 80_000),
                2
            )

            payment_mode = random.choice([
                "UPI",
                "BANK_TRANSFER",
                "NACH",
                "CHEQUE",
                "CASH"
            ])

            payment_status = random.choices(
                ["SUCCESS", "FAILED"],
                weights=[95, 5],
                k=1
            )[0]

            rows.append({
                "payment_id": f"PAY{payment_id:09d}",
                "loan_id": loan_id,
                "payment_date": payment_date,
                "payment_amount": payment_amount,
                "payment_mode": payment_mode,
                "payment_status": payment_status
            })

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
            "payment_status"
        ]

)


def generate_collections():
    rows = []
    collection_id = 1

    for loan_number in range(1, LOANS + 1):
        loan_id = f"LOAN{loan_number:08d}"

        # Collection activity is concentrated on a subset of loans
        if random.random() > 0.35:
            continue

        collection_count = random.randint(1, 6)

        for _ in range(collection_count):
            collection_date = random_date(
                date(2024, 3, 1),
                date(2026, 9, 30)
            )

            amount_collected = round(
                random.uniform(1_000, 50_000),
                2
            )

            collection_method = random.choice([
                "FIELD_AGENT",
                "CALL_CENTER",
                "BRANCH",
                "DIGITAL"
            ])

            collection_status = random.choices(
                ["SUCCESS", "PARTIAL", "FAILED"],
                weights=[75, 20, 5],
                k=1
            )[0]

            rows.append({
                "collection_id": f"COL{collection_id:09d}",
                "loan_id": loan_id,
                "collection_date": collection_date,
                "amount_collected": amount_collected,
                "collection_method": collection_method,
                "collection_status": collection_status
            })

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
        "collection_status"
    ],
    )

def main():
    generate_branches()
    generate_customers()
    generate_loan_applications()
    generate_loans()
    generate_emi_schedule()
    generate_payments()
    generate_collections()

    print("\nNBFC synthetic data generation completed.")


if __name__ == "__main__":
    main()

