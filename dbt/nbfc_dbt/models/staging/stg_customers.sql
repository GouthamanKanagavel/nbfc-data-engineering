{{ config(materialized='view') }}

SELECT
    TRIM(customer_id) AS customer_id,
    TRIM(customer_name) AS customer_name,
    date_of_birth,
    TRIM(gender) AS gender,
    TRIM(city) AS city,
    TRIM(state) AS state,
    TRIM(employment_type) AS employment_type,
    monthly_income,
    credit_score,
    TRIM(customer_segment) AS customer_segment,
    TRIM(kyc_status) AS kyc_status,
    created_at
FROM {{ source('raw', 'raw_customers') }}
