"""Execute reviewed Snowflake deployment SQL using Vault-backed key-pair auth.

Usage: python -m scripts.execute_sql sql/raw_tables.sql
Only scripts explicitly listed in ALLOWED_SCRIPTS can be executed.
"""
import argparse
from pathlib import Path
from config.snowflake_auth import connect

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_SCRIPTS = {
    "raw_tables.sql", "security_post_deploy.sql", "secure_data_share.sql"
}

def resolve_script(name):
    path = (ROOT / "sql" / name).resolve()
    if path.parent != (ROOT / "sql").resolve() or path.name not in ALLOWED_SCRIPTS:
        raise ValueError("SQL script is not an approved provider-side deployment script")
    return path

def execute_sql_file(name, connection_factory=connect):
    path = resolve_script(name)
    sql = path.read_text(encoding="utf-8")
    if not sql.strip():
        raise ValueError("SQL script is empty")
    connection = connection_factory()
    try:
        # execute_string supports multiple Snowflake statements; fail on first error.
        cursors = connection.execute_string(sql, remove_comments=True, return_cursors=True)
        for cursor in cursors:
            try:
                cursor.close()
            except Exception:
                pass
    finally:
        connection.close()

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", choices=sorted(ALLOWED_SCRIPTS))
    args = parser.parse_args(argv)
    execute_sql_file(args.script)

if __name__ == "__main__":
    main()
