{{ config(materialized='view') }}

SELECT
    loan_id,
    COUNT(*) AS total_installments,
    MIN(due_date) AS first_due_date,
    MAX(due_date) AS last_due_date,
    SUM(principal_due) AS total_principal_due,
    SUM(interest_due) AS total_interest_due,
    SUM(emi_amount) AS total_scheduled_emi
FROM {{ ref('stg_emi_schedule') }}
GROUP BY loan_id
