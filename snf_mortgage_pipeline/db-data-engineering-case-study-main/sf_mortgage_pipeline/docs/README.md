# Mortgage Underwriting ELT — Snowflake + dbt + Prefect + Terraform

Reference implementation of the three-layer mortgage case study. Synthetic data only.

## Architecture
- **RAW:** append-only source tables. Mortgage applications arrive as JSON in VARIANT; credit bureau data arrives as CSV. Every ingestion run appends all source records as received; RAW does not perform record-level deduplication. Duplicate handling and latest-record selection happen downstream in dbt.
- **STAGE:** dbt incremental records and select the latest event per business key. `joined_customer_applications` joins application and credit data and masks SSN to `***-**-last-four`. `master_customer_applications` is incremental and contains validated rows; `technical_rejections` is an incremental exception table.
- **GOLD:** incremental application-level `underwriting_decisions`, structured loan-level `hmda_reporting`, and aggregate `bi_dashboard_daily` for BI dashboards.

## Business rules
- LTV = loan amount / property value * 100; decline above 95%.
- DTI = monthly debt / monthly gross income * 100; decline above 43%.
- FICO below 620 declines.
- Co-signer flag: FICO 620–660 inclusive and DTI 36–43% inclusive, only when no decline rule applies.
- Critical missing/invalid data and unmatched bureau records are technical rejections, not business declines.

## Security and regulatory scope
Raw tables contain sensitive source data and should be restricted to the ingestion/service roles. Stage masks SSN before it reaches the master application model. Analysts should receive access to Gold only. The HMDA model is a reporting-oriented projection, not a complete regulatory filing: the supplied data lacks required HMDA attributes. Review grants, retention, data lineage, model tests, and regulatory requirements before production use.


