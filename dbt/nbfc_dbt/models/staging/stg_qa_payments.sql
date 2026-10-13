{{ config(materialized='view') }}

SELECT
    TRIM(payment_id) AS payment_id,
    TRIM(loan_id) AS loan_id,
    payment_date,
    payment_amount,
    TRIM(payment_status) AS payment_status
FROM {{ source('qa', 'raw_payments_v2') }}
