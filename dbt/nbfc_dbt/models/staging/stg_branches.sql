{{ config(materialized='view') }}

SELECT
    TRIM(branch_id) AS branch_id,
    TRIM(branch_name) AS branch_name,
    TRIM(city) AS city,
    TRIM(state) AS state,
    TRIM(branch_type) AS branch_type,
    TRIM(manager_name) AS manager_name,
    opening_date
FROM {{ source('raw', 'raw_branches') }}
