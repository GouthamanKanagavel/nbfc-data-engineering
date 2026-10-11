{{ config(materialized='view') }}

SELECT
    CURRENT_DATE() AS today,

    MIN(due_date) AS earliest_due_date,
    MAX(due_date) AS latest_due_date,

    COUNT_IF(due_date <= CURRENT_DATE()) AS installments_due,
    COUNT_IF(due_date > CURRENT_DATE()) AS installments_future,

    COUNT(DISTINCT loan_id) AS total_loans,
    COUNT(DISTINCT CASE
        WHEN due_date <= CURRENT_DATE() THEN loan_id
    END) AS loans_with_due_installments,

    COUNT(DISTINCT CASE
        WHEN due_date > CURRENT_DATE() THEN loan_id
    END) AS loans_with_future_installments

FROM {{ ref('stg_emi_schedule') }}
