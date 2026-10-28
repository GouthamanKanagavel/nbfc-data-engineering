{{ config(materialized='view') }}

SELECT
    TRIM(branch_id) AS branch_id,
    TRIM(branch_name) AS branch_name,
    TRIM(city) AS city,
    TRIM(state) AS state,
    TRIM(region) AS region,
    TRIM(branch_manager) AS branch_manager,
    opening_date
FROM {{ source('raw', 'raw_branches') }}
