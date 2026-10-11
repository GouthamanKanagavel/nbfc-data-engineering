{{ config(materialized='view') }}

SELECT
    COUNT(*) AS loan_count,
    COUNT_IF(max_dpd = 0) AS current_loans,
    COUNT_IF(max_dpd > 0) AS overdue_loans,
    COUNT_IF(max_dpd >= 30) AS par_30_loans,
    COUNT_IF(max_dpd >= 60) AS par_60_loans,
    COUNT_IF(max_dpd >= 90) AS par_90_loans,
    MAX(max_dpd) AS maximum_dpd
FROM {{ ref('int_loan_dpd') }}
