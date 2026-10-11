{{ config(materialized='view') }}

SELECT
    TRIM(collection_id) AS collection_id,
    TRIM(loan_id) AS loan_id,
    collection_date,
    amount_collected,
    TRIM(collection_method) AS collection_method,
    TRIM(collection_status) AS collection_status
FROM {{ source('raw', 'raw_collections') }}
