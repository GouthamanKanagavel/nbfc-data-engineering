{{ config(materialized='view') }}

SELECT
    DATE_TRUNC('month', disbursement_date) AS disbursement_month,
    COUNT(*) AS loan_count,
    SUM(disbursed_amount) AS total_disbursed_amount
FROM {{ ref('stg_loans') }}
GROUP BY 1
ORDER BY 1
