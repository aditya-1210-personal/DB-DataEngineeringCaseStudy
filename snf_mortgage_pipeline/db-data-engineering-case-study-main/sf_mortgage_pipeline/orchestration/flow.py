import os
import subprocess
import sys
from prefect import flow, task
from prefect.logging import get_run_logger

@task(retries=2, retry_delay_seconds=30)
def generate_data():
    subprocess.run(
        [sys.executable, "ingestion/generate_data.py"],
        check=True
    )

@task(retries=2, retry_delay_seconds=30)
def load_sources():
    subprocess.run(
        [sys.executable, "ingestion/load_raw.py"],
        cwd="scripts",
        check=True
    )

@task
def dbt_build():
    logger = get_run_logger()

    p = subprocess.run(
        ["dbt", "build", "--project-dir", "dbt", "--profiles-dir", "dbt"],
        cwd="dbt",
        env=os.environ.copy(),
        text=True,
        capture_output=True
    )

    logger.info(p.stdout)

    if p.returncode:
        logger.error(p.stderr)
        raise RuntimeError(f"dbt build failed: {p.returncode}")

@flow(
    name="mortgage-underwriting-pipeline",
    log_prints=True
)
def mortgage_pipeline():
    generate_data()
    load_sources()
    dbt_build()

if __name__ == "__main__":
    mortgage_pipeline.serve(
        name="mortgage-underwriting-schedule",
        cron="0 8,12,16 * * *",
        timezone="Asia/Kolkata"
    )
