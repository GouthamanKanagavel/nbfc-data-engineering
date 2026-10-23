SELECT
    loan_id,
    is_par_30,
    is_par_60,
    is_par_90
FROM {{ ref('fact_loan_qa') }}
WHERE is_par_30 NOT IN (0, 1)
   OR is_par_60 NOT IN (0, 1)
   OR is_par_90 NOT IN (0, 1)
   OR (is_par_60 = 1 AND is_par_30 <> 1)
   OR (is_par_90 = 1 AND is_par_60 <> 1)