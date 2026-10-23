SELECT
    payment_id,
    loan_id,
    payment_amount,
    payment_status
FROM {{ ref('stg_qa_payments') }}
WHERE payment_amount < 0