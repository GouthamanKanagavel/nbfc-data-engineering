{{ config(materialized='view') }}

SELECT
    loan_id,
    COUNT(*) AS payment_count,
    MIN(payment_date) AS first_payment_date,
    MAX(payment_date) AS last_payment_date,
    SUM(
        CASE
            WHEN UPPER(payment_status) = 'SUCCESS'
            THEN payment_amount
            ELSE 0
        END
    ) AS total_successful_payment,
    SUM(
        CASE
            WHEN UPPER(payment_status) <> 'SUCCESS'
            THEN payment_amount
            ELSE 0
        END
    ) AS total_failed_payment
FROM {{ ref('stg_payments') }}
GROUP BY loan_id
