{{ config(
    materialized='incremental',
    unique_key='application_id',
    incremental_strategy='merge'
) }}

select 
 application_id, 
 applicant_id, 
 decision_at::date as action_date, 
 loan_amount,
 property_value, 
 ltv_pct, 
 dti_pct, 
 fico_score, 
 decision_status, 
 decision_reason_code
from {{ ref('underwriting_decisions') }}
{% if is_incremental() %}
where decision_at >= dateadd(day, -{{ var('incremental_lookback_days', 7) }}, current_timestamp())
{% endif %}
