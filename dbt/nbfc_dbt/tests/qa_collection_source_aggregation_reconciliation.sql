WITH source_aggregates AS (
    SELECT
        loan_id,
        COUNT(*) AS source_collection_count,
        MIN(collection_date) AS source_first_collection_date,
        MAX(collection_date) AS source_last_collection_date,
        SUM(
            CASE
                WHEN UPPER(collection_status) = 'SUCCESS'
                THEN amount_collected
                ELSE 0
            END
        ) AS source_total_successful_collection,
        SUM(
            CASE
                WHEN UPPER(collection_status) <> 'SUCCESS'
                THEN amount_collected
                ELSE 0
            END
        ) AS source_total_failed_collection
    FROM {{ ref('stg_qa_collections') }}
    GROUP BY loan_id
),

intermediate_aggregates AS (
    SELECT
        loan_id,
        collection_count,
        first_collection_date,
        last_collection_date,
        total_successful_collection,
        total_failed_collection
    FROM {{ ref('int_qa_loan_collections') }}
)

SELECT
    s.loan_id,
    s.source_collection_count,
    i.collection_count,
    s.source_first_collection_date,
    i.first_collection_date,
    s.source_last_collection_date,
    i.last_collection_date,
    s.source_total_successful_collection,
    i.total_successful_collection,
    s.source_total_failed_collection,
    i.total_failed_collection
FROM source_aggregates s
FULL OUTER JOIN intermediate_aggregates i
    ON s.loan_id = i.loan_id
WHERE s.loan_id IS NULL
   OR i.loan_id IS NULL
   OR s.source_collection_count <> i.collection_count
   OR s.source_first_collection_date <> i.first_collection_date
   OR s.source_last_collection_date <> i.last_collection_date
   OR ABS(
       s.source_total_successful_collection
       - i.total_successful_collection
   ) > 0.01
   OR ABS(
       s.source_total_failed_collection
       - i.total_failed_collection
   ) > 0.01