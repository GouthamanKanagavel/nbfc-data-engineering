{{ config(materialized='view') }}

SELECT
    TRIM(loan_id) AS loan_id,
    TRIM(application_id) AS application_id,
    TRIM(customer_id) AS customer_id,
    TRIM(branch_id) AS branch_id,
    application_date,
    TRIM(loan_type) AS loan_type,
    requested_amount,
    sanctioned_amount,
    disbursed_amount,
    disbursement_date,
    interest_rate,
    tenure_months,
    TRIM(loan_status) AS loan_status,
    TRIM(risk_grade) AS risk_grade
FROM {{ source('qa', 'raw_loans_v2') }}
