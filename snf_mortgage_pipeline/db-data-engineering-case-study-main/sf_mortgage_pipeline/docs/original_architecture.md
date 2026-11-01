# Architecture

```mermaid
flowchart LR
 A[Mortgage JSON] --> I[Python source loader]
 B[Credit CSV] --> I
 I --> BR[Snowflake Bronze]
 BR --> S[dbt Silver: typed join + rejects]
 S --> G[dbt Gold: underwriting decision]
 G --> H[HMDA-oriented reporting projection]
 P[Prefect orchestration] --> I
 P --> S
 P --> G
 T[Terraform] --> BR
 T --> S
 T --> G
```
