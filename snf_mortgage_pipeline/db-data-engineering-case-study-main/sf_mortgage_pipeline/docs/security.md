# Security

Snowflake Python connector uses a private key from Vault KV v2. dbt consumes a temporary PEM file that must be deleted. Do not commit private keys, tokens, `.env`, dbt `profiles.yml`, Terraform state or customer data. Use Vault short-lived JWT/OIDC authentication in production rather than a static Vault token. CI requires a trusted PR and protected environment. Restrict Snowflake roles to least privilege; SQL under `sql/` contains additional security/data-sharing scripts and requires a separate approved deployment.
