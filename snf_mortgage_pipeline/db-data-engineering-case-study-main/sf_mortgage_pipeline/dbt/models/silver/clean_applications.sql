{{ config(
    materialized='incremental',
    unique_key='application_id',
    incremental_strategy='merge'
) }}

with joined as (
    select
        a.application_id, 
        a.applicant_id, 
        a.applicant_name,
        a.loan_amount, 
        a.property_value, 
        a.monthly_gross_income,
        c.ssn, 
        c.fico_score, 
        c.monthly_debt,
        a.application_ingested_at, 
        c.credit_ingested_at,
        {{ mortgage_technical_rejection_reason('a', 'c') }} as technical_rejection_reason
    from {{ ref('stg_mortgage_applications') }} a
    left join {{ ref('stg_credit_bureau') }} c using (applicant_id)
)
select *
from joined
where technical_rejection_reason is null
{% if is_incremental() %}
  and (application_ingested_at >= dateadd(day, -{{ var('incremental_lookback_days', 7) }}, current_timestamp())
       or credit_ingested_at >= dateadd(day, -{{ var('incremental_lookback_days', 7) }}, current_timestamp()))
{% endif %}
