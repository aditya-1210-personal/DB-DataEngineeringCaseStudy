# Design answers

## Credit bureau API delayed
Land application data in Bronze immediately with event/ingestion timestamps, batch ID and stable application key. Do not underwrite without a bureau match. Track unmatched applications as pending and log `MISSING_CREDIT_RECORD` in the technical rejection/control output, also will implement lookback refresh to handle the late ariving data. When the bureau record arrives, rerun affected application keys using an idempotent MERGE/incremental model. Alert when source lag exceeds SLA. In production, do not truncate Bronze; preserve source batches and deduplicate by business key/version.

## Time Travel audit for approval 30 days ago
Query the decision table at the recorded approval timestamp, if the table's configured Time Travel retention covers that point:
```sql
SELECT *
FROM MORTGAGE_DB.GOLD.UNDERWRITING_DECISIONS
AT (TIMESTAMP => '2026-09-29 10:15:00'::TIMESTAMP_NTZ)
WHERE APPLICATION_ID='APP1001';
```
Record the approval timestamp, source batch IDs, model/code version and query IDs. Retention is finite and 30 days is not guaranteed by default; for longer audit needs, write immutable decision snapshots to a governed audit table/archive.

## 1,000x end-of-quarter spike
Buffer source data in durable cloud storage/queue and use Snowpipe or Snowpipe Streaming as appropriate. Scale ingestion, dbt transformation and BI compute separately; use incremental models, idempotent keys, retries, backpressure and dead-letter handling. Monitor queue lag, warehouse queueing, credits, run duration and decision distribution. Load-test representative peak volumes; do not assume a 1,000x spike is handled without capacity validation.

## Operational controls
Prefect retries transient failures and stops before dbt if ingestion fails. Configure Prefect notifications/deployment automations for email or Slack without embedding credentials. Test source freshness, duplicates, nulls, unmatched bureau records, LTV/DTI bounds, decision distributions, and model runtime. The sample HMDA projection is not a complete regulatory filing because the supplied inputs omit required reporting attributes.


## Incremental model strategy
Silver and Gold use `materialized='incremental'`, `unique_key='application_id'`, and Snowflake `merge`. The Bronze loader also uses idempotent MERGE instead of TRUNCATE/reload so unchanged rows retain their ingestion watermark. dbt filters to source records ingested in the configurable lookback window (`incremental_lookback_days`, default 7). Before reprocessing, a shared pre-hook deletes the changed application IDs from the existing target; this is essential because an application can change from valid to technically rejected, or vice versa, and a plain MERGE of only the currently valid rows would leave stale rows behind. Gold uses the same source-change pre-hook to remove decisions/reporting rows for applications no longer present in Silver clean. Use a full refresh for historical backfills or transformation logic changes.
