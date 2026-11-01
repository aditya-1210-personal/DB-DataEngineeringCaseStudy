"""Append-only bulk ingestion of synthetic mortgage source files."""
import csv
import json
import tempfile
from pathlib import Path
from config.snowflake_auth import connect

ROOT = Path(__file__).resolve().parents[1]

def read_applications(path):
    records = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Mortgage applications JSON must contain an array")
    return records

def read_credits(path):
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))

def write_ndjson(records, path):
    with Path(path).open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

def write_credit_csv(records, path):
    columns = ["applicant_id", "ssn", "fico_score", "monthly_debt"]
    with Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

def run_sql(cursor, statement):
    return cursor.execute(statement)

def load_raw(applications, credits, connection):
    with tempfile.TemporaryDirectory(prefix="mortgage_ingest_") as directory:
        app_file = Path(directory) / "applications.ndjson"
        credit_file = Path(directory) / "credits.csv"
        write_ndjson(applications, app_file)
        write_credit_csv(credits, credit_file)
        cursor = connection.cursor()
        try:
            run_sql(cursor, "CREATE TEMPORARY STAGE MORTGAGE_APP_STAGE")
            run_sql(cursor, "CREATE TEMPORARY STAGE MORTGAGE_CREDIT_STAGE")
            run_sql(cursor, "CREATE TEMPORARY TABLE TMP_APPLICATIONS (PAYLOAD VARIANT)")
            run_sql(cursor, "CREATE TEMPORARY TABLE TMP_CREDITS (APPLICANT_ID STRING, SSN STRING, FICO_SCORE NUMBER(3,0), MONTHLY_DEBT NUMBER(14,2))")
            run_sql(cursor, f"PUT 'file://{app_file.as_posix()}' @MORTGAGE_APP_STAGE AUTO_COMPRESS=TRUE")
            run_sql(cursor, f"PUT 'file://{credit_file.as_posix()}' @MORTGAGE_CREDIT_STAGE AUTO_COMPRESS=TRUE")
            run_sql(cursor, "COPY INTO TMP_APPLICATIONS FROM @MORTGAGE_APP_STAGE FILE_FORMAT=(TYPE=JSON) ON_ERROR=ABORT_STATEMENT")
            run_sql(cursor, "COPY INTO TMP_CREDITS FROM @MORTGAGE_CREDIT_STAGE FILE_FORMAT=(TYPE=CSV SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='\"' EMPTY_FIELD_AS_NULL=TRUE) ON_ERROR=ABORT_STATEMENT")
            run_sql(cursor, "INSERT INTO MORTGAGE_DB.RAW.MORTGAGE_APPLICATIONS_RAW (APPLICATION_ID, APPLICANT_ID, PAYLOAD, SOURCE_FILE) SELECT PAYLOAD:application_id::STRING, PAYLOAD:applicant_id::STRING, PAYLOAD, 'mortgage_applications.json' FROM TMP_APPLICATIONS")
            run_sql(cursor, "INSERT INTO MORTGAGE_DB.RAW.CREDIT_BUREAU_RAW (APPLICANT_ID, SSN, FICO_SCORE, MONTHLY_DEBT, SOURCE_FILE) SELECT APPLICANT_ID, SSN, FICO_SCORE, MONTHLY_DEBT, 'credit_bureau.csv' FROM TMP_CREDITS")connection.commit()
        finally:
            cursor.close()

def main():
    applications = read_applications(ROOT / "data/mortgage_applications.json")
    credits = read_credits(ROOT / "data/credit_bureau.csv")
    connection = connect()
    try:
        load_raw(applications, credits, connection)
    finally:
        connection.close()

if __name__ == "__main__":
    main()
