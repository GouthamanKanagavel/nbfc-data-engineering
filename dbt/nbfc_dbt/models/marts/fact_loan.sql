{{ config(materialized='table') }}

SELECT
    l.loan_id,
    l.application_id,
    l.customer_id,
    l.customer_name,
    l.customer_segment,
    l.employment_type,
    l.monthly_income,
    l.credit_score,
    l.kyc_status,

    l.branch_id,
    l.branch_name,
    l.branch_city,
    l.branch_state,

    l.loan_type,
    l.application_date,
    l.disbursement_date,

    l.requested_amount,
    l.sanctioned_amount,
    l.disbursed_amount,
    l.interest_rate,
    l.tenure_months,
    l.loan_status,
    l.risk_grade,

    COALESCE(e.total_installments, 0) AS total_installments,
    e.first_due_date,
    e.last_due_date,
    COALESCE(e.total_principal_due, 0) AS total_principal_due,
    COALESCE(e.total_interest_due, 0) AS total_interest_due,
    COALESCE(e.total_scheduled_emi, 0) AS total_scheduled_emi,

    COALESCE(p.payment_count, 0) AS payment_count,
    p.first_payment_date,
    p.last_payment_date,
    COALESCE(p.total_successful_payment, 0) AS total_successful_payment,
    COALESCE(p.total_failed_payment, 0) AS total_failed_payment,

    COALESCE(c.collection_count, 0) AS collection_count,
    c.first_collection_date,
    c.last_collection_date,
    COALESCE(c.total_successful_collection, 0) AS total_successful_collection,
    COALESCE(c.total_failed_collection, 0) AS total_failed_collection,

    COALESCE(d.max_dpd, 0) AS max_dpd,
    COALESCE(d.is_par_30, 0) AS is_par_30,
    COALESCE(d.is_par_60, 0) AS is_par_60,
    COALESCE(d.is_par_90, 0) AS is_par_90,
    d.oldest_overdue_date,
    COALESCE(d.total_unpaid_emi_amount, 0) AS total_unpaid_emi_amount,

    GREATEST(
        COALESCE(e.total_principal_due, 0)
        - COALESCE(p.total_successful_payment, 0),
        0
    ) AS estimated_outstanding_principal,

    CASE
        WHEN COALESCE(e.total_principal_due, 0) = 0 THEN 0
        ELSE
            ROUND(
                COALESCE(p.total_successful_payment, 0)
                / e.total_principal_due * 100,
                2
            )
    END AS payment_coverage_pct,

    CASE
        WHEN COALESCE(e.total_scheduled_emi, 0) = 0 THEN 0
        ELSE
            ROUND(
                COALESCE(c.total_successful_collection, 0)
                / e.total_scheduled_emi * 100,
                2
            )
    END AS collection_efficiency_pct

FROM {{ ref('int_loan_customer') }} l

LEFT JOIN {{ ref('int_loan_emi') }} e
    ON l.loan_id = e.loan_id

LEFT JOIN {{ ref('int_loan_payments') }} p
    ON l.loan_id = p.loan_id

LEFT JOIN {{ ref('int_loan_collections') }} c
    ON l.loan_id = c.loan_id

LEFT JOIN {{ ref('int_loan_dpd') }} d
    ON l.loan_id = d.loan_id