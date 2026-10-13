select
    l.loan_id,
    l.application_id
from {{ source('qa', 'raw_loans_v2') }} as l
left join {{ source('raw', 'raw_loan_applications') }} as a
    on l.application_id = a.application_id
where a.application_id is null
