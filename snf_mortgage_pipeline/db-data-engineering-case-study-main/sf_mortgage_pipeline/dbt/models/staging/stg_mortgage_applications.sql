{{ config(materialized='table') }}

/* This model is optional, if we need to handle duplicate then we need this*/

select 
 application_id, 
 applicant_id,
 payload:applicant_name::string as applicant_name,
 try_to_decimal(payload:loan_amount::string,14,2) as loan_amount,
 try_to_decimal(payload:property_value::string,14,2) as property_value,
 try_to_decimal(payload:monthly_gross_income::string,14,2) as monthly_gross_income,
 ingested_at as application_ingested_at
from {{ source('raw','mortgage_applications_raw') }}
