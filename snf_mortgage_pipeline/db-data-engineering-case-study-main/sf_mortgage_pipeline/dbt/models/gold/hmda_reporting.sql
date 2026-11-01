
{{ config(
    materialized='table',
    schema='curated'
) }}

WITH decisions AS (
    SELECT
        DATE_TRUNC('MONTH', decision_at)::DATE
            AS reporting_month,
        decision_status,
        decision_reason_code,
        loan_amount,
        fico_score
    FROM {{ ref('underwriting_decisions') }}
)

SELECT
    reporting_month,
    decision_status,
    decision_reason_code,

    COUNT(*) AS total_applications,

    SUM(loan_amount) AS total_loan_amount,

    ROUND(AVG(loan_amount), 2)
        AS avg_loan_amount,

    COUNT_IF(decision_status = 'APPROVED')
        AS approved_count,

    COUNT_IF(decision_status = 'DECLINED')
        AS declined_count,

    ROUND(
        AVG(
            CASE
                WHEN decision_status = 'APPROVED'
                THEN fico_score
            END
        ),
        2
    ) AS avg_approved_fico

FROM decisions
GROUP BY
    reporting_month,
    decision_status,
    decision_reason_code
