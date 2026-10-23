SELECT
    collection_id,
    loan_id,
    amount_collected,
    collection_status
FROM {{ ref('stg_qa_collections') }}
WHERE amount_collected < 0