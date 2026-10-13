{{ config(materialized='view') }}

SELECT
    loan_id,
    COUNT(*) AS collection_count,
    MIN(collection_date) AS first_collection_date,
    MAX(collection_date) AS last_collection_date,
    SUM(
        CASE
            WHEN UPPER(collection_status) = 'SUCCESS'
            THEN amount_collected
            ELSE 0
        END
    ) AS total_successful_collection,
    SUM(
        CASE
            WHEN UPPER(collection_status) <> 'SUCCESS'
            THEN amount_collected
            ELSE 0
        END
    ) AS total_failed_collection
FROM {{ ref('stg_qa_collections') }}
GROUP BY loan_id
