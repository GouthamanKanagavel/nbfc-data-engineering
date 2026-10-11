{{ config(materialized='view') }}

SELECT
    TRIM(application_id) AS application_id,
    TRIM(customer_id) AS customer_id,
    TRIM(branch_id) AS branch_id,
    application_date,
    TRIM(loan_type) AS loan_type,
    requested_amount,
    tenure_months,
    TRIM(application_status) AS application_status,
    TRIM(risk_grade) AS risk_grade
FROM {{ source('raw', 'raw_loan_applications') }}
