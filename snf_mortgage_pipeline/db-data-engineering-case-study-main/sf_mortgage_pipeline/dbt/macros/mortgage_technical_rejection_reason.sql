{% macro mortgage_technical_rejection_reason(application_alias='a', credit_alias='c') -%}
case
    when {{ application_alias }}.applicant_id is null then 'MISSING_APPLICANT_ID'
    when {{ credit_alias }}.applicant_id is null then 'MISSING_CREDIT_RECORD'
    when {{ credit_alias }}.fico_score is null then 'MISSING_CREDIT_SCORE'
    when {{ application_alias }}.property_value is null
         or {{ application_alias }}.property_value <= 0 then 'INVALID_PROPERTY_VALUE'
    when {{ application_alias }}.loan_amount is null
         or {{ application_alias }}.loan_amount <= 0 then 'INVALID_LOAN_AMOUNT'
    when {{ application_alias }}.monthly_gross_income is null
         or {{ application_alias }}.monthly_gross_income <= 0 then 'INVALID_MONTHLY_GROSS_INCOME'
    when {{ credit_alias }}.monthly_debt is null
         or {{ credit_alias }}.monthly_debt < 0 then 'INVALID_MONTHLY_DEBT'
    else null
end
{%- endmacro %}
