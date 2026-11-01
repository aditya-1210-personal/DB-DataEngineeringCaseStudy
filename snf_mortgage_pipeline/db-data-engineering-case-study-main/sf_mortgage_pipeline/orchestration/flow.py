
import os
import subprocess
import sys
from pathlib import Path

from prefect import flow, task
from prefect.logging import get_run_logger

ROOT = Path(__file__).resolve().parents[1]
DBT_DIR = ROOT / "dbt"


def execute(command, cwd=ROOT):
    """Run a command and fail on a nonzero exit code."""
    result = subprocess.run(
        [str(part) for part in command],
        cwd=str(cwd),
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): "
            f"{' '.join(map(str, command))}\n"
            f"{result.stderr[-4000:]}"
        )

    return result.stdout


@task(retries=2, retry_delay_seconds=30)
def generate_data():
    return execute([
        sys.executable,
        ROOT / "ingestion" / "generate_data.py",
    ])


@task(retries=2, retry_delay_seconds=30)
def load_sources():
    return execute([
        sys.executable,
        "-m",
        "ingestion.load_raw",
    ])


@task
def dbt_build():
    logger = get_run_logger()

    output = execute([
        "dbt",
        "build",
        "--project-dir",
        DBT_DIR,
        "--profiles-dir",
        DBT_DIR,
    ])

    logger.info(output[-4000:])


@flow(
    name="mortgage-underwriting-pipeline",
    log_prints=True,
)
def mortgage_pipeline():
    generate_data()
    load_sources()
    dbt_build()


if __name__ == "__main__":
    mortgage_pipeline.serve(
        name="mortgage-underwriting-schedule",
        cron="0 8,12,16 * * *",
        timezone="Asia/Kolkata",
    )
