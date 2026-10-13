{{ config(materialized='view') }}

SELECT
    TRIM(loan_id) AS loan_id,
    installment_number,
    due_date,
    principal_due,
    interest_due,
    emi_amount
FROM {{ source('qa', 'raw_emi_schedule_v2') }}
