
{{ config(materialized='view') }}

WITH params AS (
    SELECT TO_DATE('2026-10-07') AS reporting_date
),

emi AS (
    SELECT
        loan_id,
        installment_number,
        due_date,
        emi_amount
    FROM {{ ref('stg_emi_schedule') }}
),

payments AS (
    SELECT
        p.loan_id,
        SUM(p.payment_amount) AS successful_paid
    FROM {{ ref('stg_payments') }} p
    CROSS JOIN params prm
    WHERE UPPER(p.payment_status) = 'SUCCESS'
      AND p.payment_date <= prm.reporting_date
    GROUP BY p.loan_id
),

emi_running AS (
    SELECT
        e.loan_id,
        e.installment_number,
        e.due_date,
        e.emi_amount,

        COALESCE(
            SUM(e.emi_amount) OVER (
                PARTITION BY e.loan_id
                ORDER BY e.due_date, e.installment_number
                ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
            ),
            0
        ) AS prior_cumulative_due

    FROM emi e
),

allocation AS (
    SELECT
        e.loan_id,
        e.installment_number,
        e.due_date,
        e.emi_amount,
        COALESCE(p.successful_paid, 0) AS successful_paid,

        GREATEST(
            LEAST(
                COALESCE(p.successful_paid, 0)
                    - e.prior_cumulative_due,
                e.emi_amount
            ),
            0
        ) AS allocated_amount

    FROM emi_running e
    LEFT JOIN payments p
        ON e.loan_id = p.loan_id
),

installment_status AS (
    SELECT
        a.loan_id,
        a.installment_number,
        a.due_date,
        a.emi_amount,
        a.allocated_amount,

        GREATEST(
            a.emi_amount - a.allocated_amount,
            0
        ) AS remaining_installment_balance,

        CASE
            WHEN a.due_date > prm.reporting_date THEN 0
            WHEN a.emi_amount - a.allocated_amount > 0
                THEN DATEDIFF(
                    'day',
                    a.due_date,
                    prm.reporting_date
                )
            ELSE 0
        END AS dpd

    FROM allocation a
    CROSS JOIN params prm
)

SELECT
    loan_id,
    MAX(dpd) AS max_dpd,

    MAX(CASE WHEN dpd >= 30 THEN 1 ELSE 0 END) AS is_par_30,
    MAX(CASE WHEN dpd >= 60 THEN 1 ELSE 0 END) AS is_par_60,
    MAX(CASE WHEN dpd >= 90 THEN 1 ELSE 0 END) AS is_par_90,

    MIN(
        CASE
            WHEN dpd > 0
             AND remaining_installment_balance > 0
            THEN due_date
        END
    ) AS oldest_overdue_date,

    SUM(
        CASE
            WHEN due_date <= TO_DATE('2026-10-07')
            THEN remaining_installment_balance
            ELSE 0
        END
    ) AS total_unpaid_emi_amount

FROM installment_status
GROUP BY loan_id
