# Mortgage Underwriting ELT — Snowflake + dbt + Prefect + Terraform

Reference implementation for the attached case study. Uses synthetic data only.

## Run
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and set Snowflake credentials.
3. Run `snowsql -f sql/bootstrap.sql` (or provision objects with Terraform).
4. `python scripts/generate_data.py`
5. `python scripts/load_bronze.py`
6. `cp dbt/profiles.yml.example ~/.dbt/profiles.yml`, then `cd dbt && dbt debug && dbt build`
7. From the repo root: `python orchestration/flow.py`

## Layers
- Bronze: raw application JSON in VARIANT and credit bureau CSV fields.
- Silver: typed/joined records, plus technical rejections.
- Gold: underwriting decisions and HMDA-oriented reporting projection.

## Rules
LTV = loan amount / property value * 100; decline above 95%.
DTI = monthly debt / monthly gross income * 100; decline above 43%.
FICO below 620 declines. Optional co-signer flag: FICO 620–660 inclusive and DTI 36–43% inclusive, only when no decline rule applies.
Critical missing/invalid data and unmatched bureau records are technical rejections, not business declines.

## Security and scope
Terraform creates roles, schemas, warehouse, and a masking policy. Run `sql/security_post_deploy.sql` after dbt creates Silver. Restrict Bronze to pipeline roles; analysts should query curated outputs. HMDA model is a reporting-oriented projection only: source data lacks several fields needed for a complete regulatory filing. Review all provider versions, grants, retention and security controls before production use.

See `docs/design_answers.md` for late bureau data, Time Travel audit, and 1,000x spike design.
