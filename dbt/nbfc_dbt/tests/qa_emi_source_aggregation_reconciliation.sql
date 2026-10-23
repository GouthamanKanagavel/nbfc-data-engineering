WITH source_aggregates AS (
    SELECT
        loan_id,
        COUNT(*) AS source_installment_count,
        SUM(principal_due) AS source_principal_due,
        SUM(interest_due) AS source_interest_due,
        SUM(emi_amount) AS source_scheduled_emi
    FROM {{ ref('stg_qa_emi_schedule') }}
    GROUP BY loan_id
),

intermediate_aggregates AS (
    SELECT
        loan_id,
        total_installments,
        total_principal_due,
        total_interest_due,
        total_scheduled_emi
    FROM {{ ref('int_qa_loan_emi') }}
)

SELECT
    s.loan_id,
    s.source_installment_count,
    i.total_installments,
    s.source_principal_due,
    i.total_principal_due,
    s.source_interest_due,
    i.total_interest_due,
    s.source_scheduled_emi,
    i.total_scheduled_emi
FROM source_aggregates s
FULL OUTER JOIN intermediate_aggregates i
    ON s.loan_id = i.loan_id
WHERE s.loan_id IS NULL
   OR i.loan_id IS NULL
   OR s.source_installment_count <> i.total_installments
   OR ABS(s.source_principal_due - i.total_principal_due) > 0.01
   OR ABS(s.source_interest_due - i.total_interest_due) > 0.01
   OR ABS(s.source_scheduled_emi - i.total_scheduled_emi) > 0.01