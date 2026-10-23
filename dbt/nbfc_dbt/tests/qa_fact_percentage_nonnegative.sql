SELECT
    loan_id,
    payment_coverage_pct,
    collection_efficiency_pct
FROM {{ ref('fact_loan_qa') }}
WHERE payment_coverage_pct < 0
   OR collection_efficiency_pct < 0