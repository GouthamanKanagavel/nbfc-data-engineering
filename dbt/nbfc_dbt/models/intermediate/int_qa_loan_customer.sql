{{ config(materialized='view') }}

SELECT
    l.loan_id,
    l.application_id,
    l.customer_id,
    c.customer_name,
    c.customer_segment,
    c.employment_type,
    c.monthly_income,
    c.credit_score,
    c.kyc_status,
    l.branch_id,
    b.branch_name,
    b.city AS branch_city,
    b.state AS branch_state,
    l.loan_type,
    l.application_date,
    l.disbursement_date,
    l.requested_amount,
    l.sanctioned_amount,
    l.disbursed_amount,
    l.interest_rate,
    l.tenure_months,
    l.loan_status,
    l.risk_grade
FROM {{ ref('stg_qa_loans') }} l
LEFT JOIN {{ ref('stg_customers') }} c
    ON l.customer_id = c.customer_id
LEFT JOIN {{ ref('stg_branches') }} b
    ON l.branch_id = b.branch_id
