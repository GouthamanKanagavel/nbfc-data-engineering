SELECT
    loan_id,
    application_date,
    disbursement_date
FROM {{ ref('fact_loan_qa') }}
WHERE disbursement_date < application_date