select application_id from {{ ref('underwriting_decisions') }}
where decision_status='APPROVED' and (ltv_pct>95 or dti_pct>43 or fico_score<620)
