# Architecture

```mermaid
flowchart LR
  SRC[Generated JSON and CSV] --> PY[Python bulk ingestion]
  V[HashiCorp Vault KV v2] --> AUTH[Snowflake key-pair authentication]
  AUTH --> PY
  AUTH --> DBT[dbt transformations]
  PY --> RAW[(Snowflake RAW append-only)]
  RAW --> STG[dbt staging]
  STG --> SIL[dbt silver business logic]
  SIL --> GOLD[(Snowflake CURATED / gold)]
  GOLD --> SHARE[Secure data share / auditors]
  GOLD --> BI[Analytics consumers]
  PREF[Prefect] -. orchestrates .-> PY
  PREF -. orchestrates .-> DBT
  TF[Terraform] --> INFRA[Snowflake database, schemas, warehouse, roles]
  GHA[GitHub Actions] --> TF
  GHA --> TEST[pytest and dbt tests]
```

## Design principles

- RAW ingestion is append-only; repeated runs may produce duplicate records. Deduplication belongs downstream in dbt.
- Synthetic records only. SSNs are test fixtures, never real customer information.
- Terraform creates infrastructure; the loader creates RAW tables (see `sql/raw_table.sql` for an explicit DDL alternative).
- Separate CI Snowflake resources from production. Never expose real customer data to pull-request workflows.
- Vault holds the private key; the public key is registered on the Snowflake user.
