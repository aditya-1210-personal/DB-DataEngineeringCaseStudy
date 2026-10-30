{{ config(
    materialized='incremental',
    unique_key='application_id',
    incremental_strategy='merge',
) }}

with joined as (
    select
        a.application_id, a.applicant_id, a.applicant_name,
        a.loan_amount, a.property_value, a.monthly_gross_income,
        c.fico_score, c.monthly_debt,
        a.application_ingested_at, c.credit_ingested_at,
        {{ mortgage_technical_rejection_reason('a', 'c') }} as rejection_reason
    from {{ ref('stg_mortgage_applications') }} a
    left join {{ ref('stg_credit_bureau') }} c using (applicant_id)
)
select *, current_timestamp()::timestamp_ntz as rejected_at
from joined
where rejection_reason is not null
{% if is_incremental() %}
  and greatest(application_ingested_at, coalesce(credit_ingested_at, to_timestamp_ntz('1900-01-01'))) >= 
 dateadd(day, -{{ var('incremental_lookback_days', 7) }}, current_timestamp())
{% endif %}
