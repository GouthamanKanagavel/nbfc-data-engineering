{{ config(materialized='view') }}

SELECT
    COUNT(*) AS loan_count,

    COUNT_IF(max_dpd = 0) AS current_loans,
    COUNT_IF(max_dpd BETWEEN 1 AND 29) AS dpd_1_29,
    COUNT_IF(max_dpd BETWEEN 30 AND 59) AS dpd_30_59,
    COUNT_IF(max_dpd BETWEEN 60 AND 89) AS dpd_60_89,
    COUNT_IF(max_dpd >= 90) AS dpd_90_plus,

    ROUND(
        COUNT_IF(max_dpd >= 30)
        / NULLIF(COUNT(*), 0) * 100,
        2
    ) AS par_30_pct,

    ROUND(
        COUNT_IF(max_dpd >= 90)
        / NULLIF(COUNT(*), 0) * 100,
        2
    ) AS par_90_pct,

    MAX(max_dpd) AS maximum_dpd,

    SUM(total_unpaid_emi_amount) AS total_unpaid_emi_amount

FROM {{ ref('int_loan_dpd') }}
