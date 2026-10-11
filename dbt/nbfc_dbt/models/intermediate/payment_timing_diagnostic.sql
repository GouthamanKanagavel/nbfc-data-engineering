{{ config(materialized='view') }}

SELECT
    COUNT(*) AS payment_count,

    MIN(payment_date) AS earliest_payment_date,
    MAX(payment_date) AS latest_payment_date,

    COUNT_IF(payment_date <= CURRENT_DATE()) AS payments_to_date,

    COUNT_IF(payment_date > CURRENT_DATE()) AS future_payments,

    COUNT_IF(payment_date >= DATEADD('day', -30, CURRENT_DATE()))
        AS payments_last_30_days,

    COUNT_IF(payment_date >= DATEADD('day', -90, CURRENT_DATE()))
        AS payments_last_90_days

FROM {{ ref('stg_payments') }}
