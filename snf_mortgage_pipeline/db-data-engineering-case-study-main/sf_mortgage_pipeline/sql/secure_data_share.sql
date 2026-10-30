-- Securely share the curated regulatory reporting projection with an external auditor.
-- Run as a role with CREATE SHARE and ownership/grant privileges on the target objects.
-- Replace the consumer account identifier at the bottom with the auditor's Snowflake
-- organization/account name (or supported account locator for the region).

USE DATABASE MORTGAGE_DB;

-- Expose only the approved reporting columns. Do not include SSN, masked SSN,
-- applicant name, or other direct identifiers in this auditor-facing view.
CREATE OR REPLACE SECURE VIEW CURATED.VW_AUDITOR_HMDA_REPORTING AS
SELECT
    APPLICATION_ID,
    ACTION_DATE,
    LOAN_AMOUNT,
    PROPERTY_VALUE,
    LTV_PCT,
    DTI_PCT,
    FICO_SCORE,
    DECISION_STATUS,
    DECISION_REASON_CODE
FROM CURATED.HMDA_REPORTING;

CREATE SHARE IF NOT EXISTS MORTGAGE_HMDA_AUDITOR_SHARE;
GRANT USAGE ON DATABASE MORTGAGE_DB
    TO SHARE MORTGAGE_HMDA_AUDITOR_SHARE;
GRANT USAGE ON SCHEMA MORTGAGE_DB.CURATED
    TO SHARE MORTGAGE_HMDA_AUDITOR_SHARE;
GRANT SELECT ON VIEW MORTGAGE_DB.CURATED.VW_AUDITOR_HMDA_REPORTING
    TO SHARE MORTGAGE_HMDA_AUDITOR_SHARE;

-- REQUIRED: replace <AUDITOR_ORG>.<AUDITOR_ACCOUNT> before executing.
-- Example shape only: ALTER SHARE MORTGAGE_HMDA_AUDITOR_SHARE
--   ADD ACCOUNTS = AUDITOR_ORG.AUDITOR_ACCOUNT;

-- Review the share configuration before communicating it to the auditor.
SHOW SHARES LIKE 'MORTGAGE_HMDA_AUDITOR_SHARE';
