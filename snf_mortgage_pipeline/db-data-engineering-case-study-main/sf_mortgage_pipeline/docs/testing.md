# Testing

`pytest -q` covers ingestion parsing, serialization, SQL execution behavior, Vault secret lookup, key conversion, orchestration command wrapper, synthetic data generation and credential export. All network calls are mocked. Live Snowflake and Vault integration tests are **not** included.

`dbt test --project-dir dbt --profiles-dir dbt` requires built models and a live CI Snowflake account. dbt schema tests and custom SQL tests are under `dbt/models/schema.yml` and `dbt/tests`.
