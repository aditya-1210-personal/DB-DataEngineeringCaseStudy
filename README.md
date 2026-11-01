# Snowflake Mortgage Underwriting Data Engineering Case Study

Production-oriented demonstration of a synthetic mortgage pipeline using **Python, Snowflake, dbt, Prefect, Terraform, HashiCorp Vault and GitHub Actions**.

## Architecture

See [architecture and Mermaid diagram](snf_mortgage_pipeline/db-data-engineering-case-study-main/sf_mortgage_pipeline/docs/architecture.md).


## Repository layout

- `ingestion/`: source generation and append-only bulk loader
- `config/`: Vault KV v2 and Snowflake RSA key-pair authentication
- `dbt/`: staging, silver and curated transformation models and tests
- `orchestration/`: Prefect pipeline
- `terraform/`: infrastructure provisioning
- `sql/`: optional DDL, security and secure data sharing
- `tests/`: isolated pytest unit tests
- `.github/workflows/`: PR validation and gated deployment stages
- `docs/`: architecture, deployment, testing and security

## Getting started

Read [deployment guide](docs/deployment.md) before executing any infrastructure changes. Configure a dedicated Snowflake service user, public key, Vault KV v2 secret, and least-privilege roles.

```bash
pip install -r requirements.txt
pytest -q
```

For real Snowflake deployment follow [deployment guide](docs/deployment.md). For operational and security considerations see [security](docs/security.md) and [testing](docs/testing.md).

## Data behavior

RAW is append-only; `COPY INTO` loads files to temporary tables, then `INSERT` appends into RAW. dbt performs business logic and downstream deduplication. The dataset is synthetic. Existing SQL for security and secure sharing remains in `sql/` and must be reviewed before production use.

## CI/CD caveat

PR pipeline installs dependencies, validates and plans Terraform, executes pytest, and has gated Terraform apply and dbt build/test steps. Live apply and dbt testing are **disabled by default** until Vault, Snowflake access, isolated CI environment and remote Terraform state are configured. No live infrastructure deployment has been verified.

## SQL deployment

See [SQL deployment guide](docs/sql_deployment.md). Approved provider-side SQL runs via `python -m scripts.execute_sql raw_tables.sql`, `security_post_deploy.sql`, or `secure_data_share.sql`, with separate gated CI stages. Auditor consumer SQL is not run in provider CI.
