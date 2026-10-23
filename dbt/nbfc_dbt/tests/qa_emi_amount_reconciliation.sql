SELECT
    loan_id,
    total_principal_due,
    total_interest_due,
    total_scheduled_emi,
    total_scheduled_emi
        - (total_principal_due + total_interest_due)
        AS reconciliation_difference
FROM {{ ref('int_qa_loan_emi') }}
WHERE ABS(
    total_scheduled_emi
        - (total_principal_due + total_interest_due)
) > 0.01