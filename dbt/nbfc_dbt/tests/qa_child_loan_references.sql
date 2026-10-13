select
    'EMI_SCHEDULE' as dataset,
    e.loan_id
from {{ source('qa', 'raw_emi_schedule_v2') }} as e
left join {{ source('qa', 'raw_loans_v2') }} as l
    on e.loan_id = l.loan_id
where l.loan_id is null

union all

select
    'PAYMENTS' as dataset,
    p.loan_id
from {{ source('qa', 'raw_payments_v2') }} as p
left join {{ source('qa', 'raw_loans_v2') }} as l
    on p.loan_id = l.loan_id
where l.loan_id is null

union all

select
    'COLLECTIONS' as dataset,
    c.loan_id
from {{ source('qa', 'raw_collections_v2') }} as c
left join {{ source('qa', 'raw_loans_v2') }} as l
    on c.loan_id = l.loan_id
where l.loan_id is null
