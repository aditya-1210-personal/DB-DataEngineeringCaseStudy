from pathlib import Path
import pytest
from scripts.execute_sql import resolve_script, execute_sql_file, main

def test_resolve_allowed():
    assert resolve_script("raw_tables.sql").name == "raw_tables.sql"

@pytest.mark.parametrize("name", ["../README.md", "snf_ddl.sql", "secure_data_share_consumer.sql", "/tmp/evil.sql"])
def test_reject_unapproved(name):
    with pytest.raises(ValueError):
        resolve_script(name)

def test_execute_sql_file_with_fake_connection():
    class Cursor:
        closed = False
        def close(self): self.closed = True
    class Connection:
        closed = False
        def execute_string(self, sql, **kwargs):
            assert "CREATE TABLE IF NOT EXISTS" in sql
            assert kwargs["remove_comments"] is True
            self.cursor = Cursor()
            return [self.cursor]
        def close(self): self.closed = True
    conn = Connection()
    execute_sql_file("raw_tables.sql", lambda: conn)
    assert conn.closed and conn.cursor.closed

def test_connection_closed_on_error():
    class Connection:
        closed = False
        def execute_string(self, sql, **kwargs): raise RuntimeError("Snowflake failed")
        def close(self): self.closed = True
    conn = Connection()
    with pytest.raises(RuntimeError, match="Snowflake failed"):
        execute_sql_file("raw_tables.sql", lambda: conn)
    assert conn.closed

def test_cli_rejects_unapproved():
    with pytest.raises(SystemExit):
        main(["secure_data_share_consumer.sql"])
