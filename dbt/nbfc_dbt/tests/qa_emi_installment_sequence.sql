SELECT
    loan_id,
    COUNT(*) AS installment_count,
    MIN(installment_number) AS min_installment_number,
    MAX(installment_number) AS max_installment_number,
    COUNT(DISTINCT installment_number) AS distinct_installment_count
FROM {{ ref('stg_qa_emi_schedule') }}
GROUP BY loan_id
HAVING MIN(installment_number) <> 1
    OR MAX(installment_number) <> COUNT(*)
    OR COUNT(DISTINCT installment_number) <> COUNT(*)