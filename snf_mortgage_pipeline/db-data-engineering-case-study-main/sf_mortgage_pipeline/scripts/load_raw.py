
import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).resolve().parents[1]


def connect():
    required = ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError("Missing environment variables: " + ", ".join(missing))
    args = {key.lower(): os.environ[key] for key in required}
    args.update(
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "MORTGAGE_WH"),
        database=os.getenv("SNOWFLAKE_DATABASE", "MORTGAGE_DB"),
    )
    if os.getenv("SNOWFLAKE_AUTHENTICATOR"):
        args["authenticator"] = os.environ["SNOWFLAKE_AUTHENTICATOR"]
    return snowflake.connector.connect(**{key: value for key, value in args.items() if value})


def row_hash(payload):
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def main():
    apps = json.loads((ROOT / "data/mortgage_applications.json").read_text(encoding="utf-8"))
    with (ROOT / "data/credit_bureau.csv").open(newline="", encoding="utf-8") as handle:
        credits = list(csv.DictReader(handle))

    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute("CREATE DATABASE IF NOT EXISTS MORTGAGE_DB")
        cur.execute("CREATE SCHEMA IF NOT EXISTS MORTGAGE_DB.RAW")
        cur.execute("""CREATE TABLE IF NOT EXISTS MORTGAGE_DB.RAW.MORTGAGE_APPLICATIONS_RAW (
            APPLICATION_ID STRING, APPLICANT_ID STRING, PAYLOAD VARIANT,
            SOURCE_FILE STRING, ROW_HASH STRING,
            INGESTED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP())""")
        cur.execute("""CREATE TABLE IF NOT EXISTS MORTGAGE_DB.RAW.CREDIT_BUREAU_RAW (
            APPLICANT_ID STRING, SSN STRING, FICO_SCORE NUMBER(3,0), MONTHLY_DEBT NUMBER(14,2),
            SOURCE_FILE STRING, ROW_HASH STRING,
            INGESTED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP())""")
        
        cur.execute("ALTER TABLE MORTGAGE_DB.RAW.MORTGAGE_APPLICATIONS_RAW ADD COLUMN IF NOT EXISTS ROW_HASH STRING")
        cur.execute("ALTER TABLE MORTGAGE_DB.RAW.CREDIT_BUREAU_RAW ADD COLUMN IF NOT EXISTS ROW_HASH STRING")

        # Keep the existing canonical Python hashes so previously loaded records
        # remain compatible with the new bulk loader's de-duplication check.
        with tempfile.TemporaryDirectory(prefix="mortgage_raw_load_") as temp_dir:
            temp_path = Path(temp_dir)
            apps_path = temp_path / "mortgage_applications.ndjson"
            with apps_path.open("w", encoding="utf-8") as handle:
                for app in apps:
                    record = {
                        "application_id": app.get("application_id"),
                        "applicant_id": app.get("applicant_id"),
                        "payload": app,
                        "row_hash": row_hash(app),
                    }
                    handle.write(json.dumps(record, separators=(",", ":"), ensure_ascii=False) + "\n")

            credits_path = temp_path / "credit_bureau_with_hash.csv"
            with credits_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["APPLICANT_ID", "SSN", "FICO_SCORE", "MONTHLY_DEBT", "ROW_HASH"])
                for credit in credits:
                    normalized = {
                        "applicant_id": credit.get("applicant_id"),
                        "ssn": credit.get("ssn"),
                        "fico_score": int(credit["fico_score"]) if credit.get("fico_score") else None,
                        "monthly_debt": float(credit["monthly_debt"]) if credit.get("monthly_debt") else None,
                    }
                    writer.writerow([
                        normalized["applicant_id"], normalized["ssn"],
                        normalized["fico_score"], normalized["monthly_debt"], row_hash(normalized),
                    ])

            cur.execute("CREATE STAGE IF NOT EXISTS MORTGAGE_APP_INGEST_STAGE")
            cur.execute("CREATE STAGE IF NOT EXISTS MORTGAGE_CREDIT_INGEST_STAGE")
            cur.execute("CREATE TEMPORARY TABLE TMP_MORTGAGE_APPLICATIONS (RECORD VARIANT)")

            cur.execute(f"PUT file://{"file_path.json"} @MORTGAGE_APP_INGEST_STAGE AUTO_COMPRESS=TRUE OVERWRITE=TRUE")
            cur.execute(f"PUT file://{"file_path.csv"} @MORTGAGE_CREDIT_INGEST_STAGE AUTO_COMPRESS=TRUE OVERWRITE=TRUE")

            app_copy = cur.execute("""COPY INTO TMP_MORTGAGE_APPLICATIONS
                FROM @MORTGAGE_APP_INGEST_STAGE
                FILE_FORMAT = (TYPE = JSON)
                ON_ERROR = ABORT_STATEMENT""")
            app_copy_results = app_copy.fetchall()
            credit_copy = cur.execute("""COPY INTO CREDIT_BUREAU_RAW
                FROM @MORTGAGE_CREDIT_INGEST_STAGE
                FILE_FORMAT = (
                    TYPE = CSV SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                    EMPTY_FIELD_AS_NULL = TRUE
                )
                ON_ERROR = ABORT_STATEMENT""")

            cur.execute("""INSERT INTO MORTGAGE_DB.RAW.MORTGAGE_APPLICATIONS_RAW
                (APPLICATION_ID, APPLICANT_ID, PAYLOAD, SOURCE_FILE, ROW_HASH)
                SELECT
                    RECORD:application_id::STRING,
                    RECORD:applicant_id::STRING,
                    RECORD:payload,
                    'mortgage_applications.json'
                FROM TMP_MORTGAGE_APPLICATIONS s
                """)
            conn.commit()

            print("Raw bulk load complete for Raw tables")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
