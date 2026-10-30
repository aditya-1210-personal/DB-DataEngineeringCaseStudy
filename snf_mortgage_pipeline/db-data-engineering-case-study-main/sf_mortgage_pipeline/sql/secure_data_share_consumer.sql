-- Run in the external auditor's Snowflake account after the provider adds its account
-- to MORTGAGE_HMDA_AUDITOR_SHARE. The provider shares data without unloading/copying it.
CREATE DATABASE MORTGAGE_AUDIT_DATA
    FROM SHARE <PROVIDER_ORG>.<PROVIDER_ACCOUNT>.MORTGAGE_HMDA_AUDITOR_SHARE;

-- Grant access only to the auditor role that needs the regulatory reporting data.
GRANT IMPORTED PRIVILEGES ON DATABASE MORTGAGE_AUDIT_DATA
    TO ROLE AUDITOR_READ_ONLY;

-- Example query:
SELECT *
FROM MORTGAGE_AUDIT_DATA.CURATED.VW_AUDITOR_HMDA_REPORTING;
