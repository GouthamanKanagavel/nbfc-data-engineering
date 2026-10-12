select
    l.loan_id,
    l.application_id,
    l.customer_id as loan_customer_id,
    a.customer_id as application_customer_id,
    l.branch_id as loan_branch_id,
    a.branch_id as application_branch_id,
    l.application_date as loan_application_date,
    a.application_date as source_application_date,
    l.loan_type as loan_loan_type,
    a.loan_type as application_loan_type,
    l.requested_amount as loan_requested_amount,
    a.requested_amount as application_requested_amount,
    l.tenure_months as loan_tenure_months,
    a.tenure_months as application_tenure_months,
    l.risk_grade as loan_risk_grade,
    a.risk_grade as application_risk_grade,
    a.application_status
from {{ ref('stg_loans') }} as l
inner join {{ ref('stg_loan_applications') }} as a
    on l.application_id = a.application_id
where l.customer_id is distinct from a.customer_id
   or l.branch_id is distinct from a.branch_id
   or l.application_date is distinct from a.application_date
   or l.loan_type is distinct from a.loan_type
   or l.requested_amount is distinct from a.requested_amount
   or l.tenure_months is distinct from a.tenure_months
   or l.risk_grade is distinct from a.risk_grade
   or a.application_status is distinct from 'APPROVED'