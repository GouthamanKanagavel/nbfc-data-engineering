WITH source_aggregates AS (
    SELECT
        loan_id,
        COUNT(*) AS source_payment_count,
        MIN(payment_date) AS source_first_payment_date,
        MAX(payment_date) AS source_last_payment_date,
        SUM(
            CASE
                WHEN UPPER(payment_status) = 'SUCCESS'
                THEN payment_amount
                ELSE 0
            END
        ) AS source_total_successful_payment,
        SUM(
            CASE
                WHEN UPPER(payment_status) <> 'SUCCESS'
                THEN payment_amount
                ELSE 0
            END
        ) AS source_total_failed_payment
    FROM {{ ref('stg_qa_payments') }}
    GROUP BY loan_id
),

intermediate_aggregates AS (
    SELECT
        loan_id,
        payment_count,
        first_payment_date,
        last_payment_date,
        total_successful_payment,
        total_failed_payment
    FROM {{ ref('int_qa_loan_payments') }}
)

SELECT
    s.loan_id,
    s.source_payment_count,
    i.payment_count,
    s.source_first_payment_date,
    i.first_payment_date,
    s.source_last_payment_date,
    i.last_payment_date,
    s.source_total_successful_payment,
    i.total_successful_payment,
    s.source_total_failed_payment,
    i.total_failed_payment
FROM source_aggregates s
FULL OUTER JOIN intermediate_aggregates i
    ON s.loan_id = i.loan_id
WHERE s.loan_id IS NULL
   OR i.loan_id IS NULL
   OR s.source_payment_count <> i.payment_count
   OR s.source_first_payment_date <> i.first_payment_date
   OR s.source_last_payment_date <> i.last_payment_date
   OR ABS(
       s.source_total_successful_payment
       - i.total_successful_payment
   ) > 0.01
   OR ABS(
       s.source_total_failed_payment
       - i.total_failed_payment
   ) > 0.01