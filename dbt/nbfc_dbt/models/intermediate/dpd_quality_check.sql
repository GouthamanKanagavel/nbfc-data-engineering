{{ config(materialized='view') }}

SELECT
    COUNT_IF(is_par_30 = 1 AND max_dpd < 30) AS invalid_par_30,
    COUNT_IF(is_par_60 = 1 AND max_dpd < 60) AS invalid_par_60,
    COUNT_IF(is_par_90 = 1 AND max_dpd < 90) AS invalid_par_90,
    COUNT_IF(max_dpd < 0) AS negative_dpd
FROM {{ ref('int_loan_dpd') }}
