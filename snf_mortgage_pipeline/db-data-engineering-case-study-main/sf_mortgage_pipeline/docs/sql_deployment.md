# SQL deployment lifecycle

Terraform owns database, warehouse, schemas and roles. Do not execute the old `sql/snf_ddl.sql` as part of CI.

1. After successful Terraform **apply**, run `python -m scripts.execute_sql raw_tables.sql`. This creates RAW tables only.
2. Load sample data using the ingestion pipeline, then run dbt build and tests. The custom `generate_schema_name` macro ensures the staging/silver models use `STAGE` and gold models use `CURATED` (rather than dbt's default `DBT_STAGE`/`DBT_CURATED`). This override is appropriate for this single-environment demo, but use isolated databases/schemas for concurrent CI runs.
3. Run `python -m scripts.execute_sql security_post_deploy.sql` to mask sensitive STAGE columns. The deploying role needs appropriate ownership and policy privileges. The script may require policy lifecycle adjustments when rerun against already-masked columns.
4. Run `python -m scripts.execute_sql secure_data_share.sql` only after approval, with share privileges. It creates a secure view and share but **does not add an auditor account**. Grant the actual auditor account separately after review.
5. `sql/secure_data_share_consumer.sql` is intentionally excluded: it must be executed manually by the auditor in the *consumer* Snowflake account after replacing its placeholders.

The Python runner uses Vault-backed RSA key-pair authentication in memory (`config.snowflake_auth.connect`). It only accepts approved provider-side SQL filenames and fails on Snowflake errors. No Snowflake credentials are embedded in SQL.

## GitHub Actions gates

- `ENABLE_CI_TERRAFORM_APPLY=true`: permits Terraform apply in an isolated CI account, with tested provider authentication and remote state.
- `ENABLE_CI_SQL_DEPLOY=true`: additionally permits RAW DDL after apply.
- `ENABLE_CI_DBT_TEST=true`: permits dbt build/test and then masking policy deployment.
- `ENABLE_AUDITOR_SHARE=true`: permits provider-side secure share creation **only on manual workflow dispatch** and when the other gates are true.

All gates default to disabled. The workflow does not run SQL against production on every PR. Ensure Vault is accessible, the deployment role has the needed grants, and dbt models exist before enabling these steps. In a full production system, prefer a dedicated post-merge deployment workflow with protected environments.
