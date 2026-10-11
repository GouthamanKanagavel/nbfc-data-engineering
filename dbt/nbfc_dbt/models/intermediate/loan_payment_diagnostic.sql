{{ config(materialized='view') }}

WITH loan_dates AS (

    SELECT
        loan_id,
        disbursement_date
    FROM {{ ref('stg_loans') }}

),

payment_summary AS (

    SELECT
        loan_id,
        MIN(payment_date) AS first_payment_date,
        MAX(payment_date) AS last_payment_date,
        SUM(payment_amount) AS total_payment_amount,
        COUNT(*) AS payment_count
    FROM {{ ref('stg_payments') }}
    WHERE UPPER(payment_status) = 'SUCCESS'
    GROUP BY loan_id

)

SELECT
    COUNT(*) AS loan_count,

    COUNT_IF(p.loan_id IS NULL) AS loans_without_successful_payment,

    COUNT_IF(
        p.first_payment_date <= DATEADD('day', 30, l.disbursement_date)
    ) AS loans_with_payment_within_30_days,

    COUNT_IF(
        p.first_payment_date <= DATEADD('day', 60, l.disbursement_date)
    ) AS loans_with_payment_within_60_days,

    COUNT_IF(
        p.first_payment_date <= DATEADD('day', 90, l.disbursement_date)
    ) AS loans_with_payment_within_90_days,

    ROUND(
        AVG(COALESCE(p.payment_count, 0)),
        2
    ) AS avg_successful_payments_per_loan

FROM loan_dates l

LEFT JOIN payment_summary p
    ON l.loan_id = p.loan_id
