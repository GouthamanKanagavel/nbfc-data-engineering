# NBFC Data Engineering Platform

Production-style data engineering platform for an NBFC loan and credit-risk domain.

## Business Domain

The platform processes financial-services data covering:

- Customers
- Loan applications
- Loan accounts
- EMI schedules
- Payments
- Collections
- Credit risk
- DPD
- NPA
- Portfolio performance
- Branch operations

## Technology Stack

- Snowflake
- SQL
- dbt
- Python
- AWS S3
- AWS IAM
- Snowpipe
- Apache Airflow
- Docker
- GitHub Actions

## Architecture

Source systems
→ AWS S3
→ Snowpipe
→ Snowflake RAW
→ dbt STAGING
→ dbt INTERMEDIATE
→ ANALYTICS / MARTS
→ Data Quality
→ Airflow Operations

## Engineering Goals

- Reliable ingestion
- Incremental ELT
- Data validation
- Rejection and audit framework
- DPD and NPA calculations
- Portfolio reconciliation
- Idempotent processing
- Workflow orchestration
- Operational monitoring
- CI/CD validation
- Production-safe recovery

## Project Status

Phase 1 — Repository foundation
Phase 2 — Synthetic NBFC data generation
Phase 3 — AWS S3 and IAM
Phase 4 — Snowflake RAW layer
Phase 5 — Snowpipe ingestion
Phase 6 — dbt transformations
Phase 7 — Credit risk and NPA analytics
Phase 8 — Airflow orchestration
Phase 9 — CI/CD
Phase 10 — Production testing and documentation
