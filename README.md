# NBFC Data Engineering Platform

A hands-on data engineering project for an NBFC (Non-Banking Financial Company) loan and credit-risk domain, built with Python, AWS S3, Snowflake, SQL, and dbt.

## Business Domain

The platform processes synthetic financial-services data covering:

- Customers and branches
- Loan applications and loan accounts
- EMI schedules
- Payments and collections
- Days Past Due (DPD)
- Portfolio at Risk (PAR)
- Loan portfolio analytics

## Technology Stack

**Implemented and validated**
- Python for synthetic data generation
- AWS S3 for raw data storage
- Snowflake for data warehousing
- SQL and dbt for ELT transformations and data quality tests
- Git for source control

**Planned extensions**
- Snowpipe automated ingestion
- Apache Airflow orchestration
- Docker-based execution
- GitHub Actions CI/CD
- Expanded operational monitoring and recovery workflows

## Architecture

```text
Python Synthetic Data Generator
              |
              v
           AWS S3
              |
              v
       Snowflake RAW
              |
              v
        dbt STAGING
              |
              v
     dbt INTERMEDIATE
              |
              v
     dbt ANALYTICS MARTS
              |
              v
       FACT_LOAN
```

The current Snowflake RAW refresh uses staged CSV files and `COPY INTO`. Automated Snowpipe ingestion and Airflow orchestration are planned extensions, not yet part of the validated workflow.

## Data Model

The synthetic dataset contains seven source entities:

| Entity | Rows |
|---|---:|
| Branches | 50 |
| Customers | 10,000 |
| Loan applications | 10,000 |
| Loans | 10,000 |
| EMI schedules | 329,970 |
| Payments | 111,420 |
| Collections | 11,091 |

Generated CSVs are excluded from Git. Use the Python generator to recreate the data locally.

## dbt Models

### Staging
Seven staging models standardize the source entities.

### Intermediate
Intermediate models join loan, customer, EMI, payment, and collection data. The DPD model calculates overdue installments using successful payments and an oldest-due-first allocation assumption.

### Analytics Mart
`FACT_LOAN` combines loan, customer, EMI, payment, collection, and DPD metrics at loan grain.

The current DPD snapshot uses a reporting date of **2026-10-07** to make results reproducible.

## Validation Results

Original baseline

The original synthetic dataset contains 10,000 loan records. The initial loan and application datasets were generated independently, resulting in inconsistencies between loan accounts and their application records. The original baseline is retained for comparison and is not the corrected QA dataset.

Corrected QA pipeline

A separate QA pipeline was created using corrected loan, EMI schedule, payment, and collection data. The corrected loan dataset contains only loans linked to approved applications.

Validated results:

8,476 rows in NBFC_DW.QA_ANALYTICS.FACT_LOAN_QA

8,476 distinct loan IDs

12 dbt models built successfully

2 QA-specific dbt tests passed with zero warnings or errors

Zero missing application links

Zero loans linked to non-approved applications

Zero customer ID, branch ID, or requested-amount mismatches against the application source

Monetary values retain two decimal places in the QA fact table

The QA models use dedicated QA_STAGING, QA_INTERMEDIATE, and QA_ANALYTICS schemas. The original model SQL files were left unchanged.

Business logic and limitations

The DPD snapshot uses a fixed reporting date of 2026-10-07 and a simplified oldest-due-first allocation of successful payments. The synthetic EMI schedules, payment records, and collections are not a fully reconciled financial ledger. DPD and portfolio-at-risk metrics are intended for demonstration and require additional business validation before production use.

The original NBFC_DW.ANALYTICS.FACT_LOAN table could not be verified in the current Snowflake environment during the QA validation. Its existence and state remain unconfirmed.

## Running dbt

From the repository root:

```bash
cd dbt/nbfc_dbt
source .venv/bin/activate
dbt debug --profile nbfc_dbt
dbt run --profile nbfc_dbt
dbt test --profile nbfc_dbt
```

Configure the `nbfc_dbt` profile in `~/.dbt/profiles.yml` and provide Snowflake connection settings through environment variables. Never commit passwords, private keys, or local credential files.

## Roadmap

1. Repository foundation and documentation
2. Synthetic NBFC data generation
3. AWS S3 and IAM setup
4. Snowflake RAW ingestion
5. Automated Snowpipe ingestion
6. dbt staging and intermediate transformations
7. DPD, PAR, and loan portfolio analytics
8. Airflow orchestration
9. CI/CD with GitHub Actions
10. Expanded testing, monitoring, and recovery procedures

## Disclaimer

This project is intended for learning and demonstration. It does not contain real customer data and is not certified for production financial reporting.
