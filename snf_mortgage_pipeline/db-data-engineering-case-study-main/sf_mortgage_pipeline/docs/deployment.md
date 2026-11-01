# Deployment and CI setup

## Prerequisites

Python 3.11, Terraform >=1.5, a Snowflake account, HashiCorp Vault KV v2 and a Snowflake user with an RSA public key registered. Use a dedicated CI service user and separate Snowflake account or database for CI.

## Key-pair setup

Generate a key pair securely outside the repository (example):

```bash
openssl genrsa 2048 > snowflake_private.pem
openssl rsa -in snowflake_private.pem -pubout > snowflake_public.pem
```

Register the public key with Snowflake using an authorized admin:

```sql
ALTER USER MORTGAGE_SERVICE_USER SET RSA_PUBLIC_KEY='<base64 public key body>';
```

Store the private PEM content and connection identifiers at Vault KV v2 path `secret/mortgage/snowflake`:

```json
{"account":"ORG-ACCOUNT","user":"MORTGAGE_SERVICE_USER","private_key_pem":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"}
```

Optional field: `private_key_passphrase`. Never store this JSON or PEM in Git.

## Local execution

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export VAULT_ADDR=https://vault.example.com
export VAULT_TOKEN=... # short-lived token, never save in shell history
python -m config.export_credentials /tmp/mortgage_key.pem > /tmp/mortgage_env.sh
source /tmp/mortgage_env.sh
terraform -chdir=terraform init
terraform -chdir=terraform plan
terraform -chdir=terraform apply
# Ensure RAW tables exist using sql/snf_ddl.sql (avoid recreating Terraform-managed resources).
python -m ingestion.generate_data
python -m ingestion.load_raw
cp dbt/profiles.yml.example dbt/profiles.yml
dbt build --project-dir dbt --profiles-dir dbt
dbt test --project-dir dbt --profiles-dir dbt
pytest -q
rm -f /tmp/mortgage_key.pem /tmp/mortgage_env.sh
```

**Important:** Terraform provider key-pair authentication needs explicit provider-version validation before running `apply`. The example CI workflow runs Terraform plan by default and gates apply. Also configure a remote state backend, a narrowly scoped CI role, and a per-PR cleanup strategy before enabling CI apply.

## GitHub Actions secrets and variables

- Secrets: `VAULT_ADDR`, `VAULT_TOKEN` (prefer GitHub OIDC to Vault JWT auth for production).
- Variables: `VAULT_KV_MOUNT`, `VAULT_SECRET_PATH`, `SNOWFLAKE_ROLE`.
- `ENABLE_CI_TERRAFORM_APPLY=true` only after CI environment and backend are secured.
- `ENABLE_CI_DBT_TEST=true` only after CI source data has been loaded and dbt model permissions are granted.
- Forked PRs are skipped to avoid exposing secrets.

## Limitations

CI is intentionally fail-closed for infrastructure apply and live dbt execution. Both require your account-specific configuration and credentials. `terraform plan` requires access to the target Snowflake account; this workflow has not been run against a live account.
