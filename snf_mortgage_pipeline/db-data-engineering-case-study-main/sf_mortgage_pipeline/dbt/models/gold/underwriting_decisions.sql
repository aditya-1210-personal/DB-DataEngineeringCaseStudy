{{ config(
    materialized='incremental',
    unique_key='application_id',
    incremental_strategy='merge'
) }}

with m as (
    select 
       application_id, 
       applicant_id, 
       applicant_name, 
       ssn, 
       loan_amount,
       property_value, 
       monthly_gross_income, 
       monthly_debt, 
       fico_score,
       application_ingested_at, 
       credit_ingested_at,
       round(loan_amount / nullif(property_value, 0) * 100, 2) as ltv_pct,
       round(monthly_debt / nullif(monthly_gross_income, 0) * 100, 2) as dti_pct
    from {{ ref('clean_applications') }}
), r as (
    select *,
           ltv_pct > 95 as fails_ltv,
           dti_pct > 43 as fails_dti,
           fico_score < 620 as fails_fico,
           (fico_score between 620 and 660 and dti_pct between 36 and 43) as requires_cosigner
    from m
)
select 
 application_id, 
 applicant_id, 
 applicant_name, 
 ssn,
 loan_amount, 
 property_value,
 monthly_gross_income, 
 monthly_debt, 
 fico_score, 
 ltv_pct, 
 dti_pct,
 case when fails_ltv then 'DECLINED_LTV_EXCEEDED'
      when fails_dti then 'DECLINED_DTI_EXCEEDED'
      when fails_fico then 'DECLINED_FICO_BELOW_620'
      when requires_cosigner then 'REQUIRES_COSIGNER'
      else 'APPROVED' 
 end as decision_reason_code,
 case when fails_ltv or fails_dti or fails_fico then 'DECLINED'
      when requires_cosigner then 'REQUIRES_COSIGNER' 
      else 'APPROVED' 
 end as decision_status,
 current_timestamp()::timestamp_ntz as decision_at,
 application_ingested_at, credit_ingested_at,
 fails_ltv, fails_dti, fails_fico, requires_cosigner
from r
{% if is_incremental() %}
where greatest(application_ingested_at, coalesce(credit_ingested_at, to_timestamp_ntz('1900-01-01'))) >= 
 dateadd(day, -{{ var('incremental_lookback_days', 7) }}, current_timestamp())
{% endif %}
