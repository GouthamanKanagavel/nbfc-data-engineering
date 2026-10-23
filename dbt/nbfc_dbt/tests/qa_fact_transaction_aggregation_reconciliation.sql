WITH expected AS (
    SELECT
        l.loan_id,
        COALESCE(p.payment_count, 0) AS expected_payment_count,
        COALESCE(p.total_successful_payment, 0)
            AS expected_successful_payment,
        COALESCE(p.total_failed_payment, 0)
            AS expected_failed_payment,
        COALESCE(c.collection_count, 0) AS expected_collection_count,
        COALESCE(c.total_successful_collection, 0)
            AS expected_successful_collection,
        COALESCE(c.total_failed_collection, 0)
            AS expected_failed_collection
    FROM {{ ref('int_qa_loan_customer') }} l
    LEFT JOIN {{ ref('int_qa_loan_payments') }} p
        ON l.loan_id = p.loan_id
    LEFT JOIN {{ ref('int_qa_loan_collections') }} c
        ON l.loan_id = c.loan_id
)

SELECT
    f.loan_id,
    f.payment_count,
    e.expected_payment_count,
    f.total_successful_payment,
    e.expected_successful_payment,
    f.total_failed_payment,
    e.expected_failed_payment,
    f.collection_count,
    e.expected_collection_count,
    f.total_successful_collection,
    e.expected_successful_collection,
    f.total_failed_collection,
    e.expected_failed_collection
FROM {{ ref('fact_loan_qa') }} f
FULL OUTER JOIN expected e
    ON f.loan_id = e.loan_id
WHERE f.loan_id IS NULL
   OR e.loan_id IS NULL
   OR f.payment_count <> e.expected_payment_count
   OR ABS(
       f.total_successful_payment
       - e.expected_successful_payment
   ) > 0.01
   OR ABS(
       f.total_failed_payment
       - e.expected_failed_payment
   ) > 0.01
   OR f.collection_count <> e.expected_collection_count
   OR ABS(
       f.total_successful_collection
       - e.expected_successful_collection
   ) > 0.01
   OR ABS(
       f.total_failed_collection
       - e.expected_failed_collection
   ) > 0.01