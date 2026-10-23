SELECT
    loan_id,
    requested_amount,
    sanctioned_amount,
    disbursed_amount,
    total_principal_due,
    total_interest_due,
    total_scheduled_emi,
    total_successful_payment,
    total_successful_collection,
    estimated_outstanding_principal
FROM {{ ref('fact_loan_qa') }}
WHERE requested_amount < 0
   OR sanctioned_amount < 0
   OR disbursed_amount < 0
   OR total_principal_due < 0
   OR total_interest_due < 0
   OR total_scheduled_emi < 0
   OR total_successful_payment < 0
   OR total_successful_collection < 0
   OR estimated_outstanding_principal < 0