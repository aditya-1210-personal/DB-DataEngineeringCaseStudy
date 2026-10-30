{{ config(materialized='table') }}

/* This model is optional, if we need to handle duplicate then we need this*/
select 
 applicant_id, 
 ssn, 
 try_to_number(fico_score) as fico_score,
 try_to_decimal(monthly_debt,14,2) as monthly_debt, 
 ingested_at as credit_ingested_at
from {{ source('raw','credit_bureau_raw') }}
qualify row_number() over (
 partition by applicant_id order by ingested_at desc
 )=1
