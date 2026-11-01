import csv
import json
from unittest.mock import MagicMock
import pytest
from ingestion import load_raw

def test_read_applications(tmp_path):
    path = tmp_path / "a.json"
    path.write_text('[{"application_id":"A"}]')
    assert load_raw.read_applications(path)[0]["application_id"] == "A"

def test_read_applications_rejects_object(tmp_path):
    path = tmp_path / "a.json"
    path.write_text('{}')
    with pytest.raises(ValueError): load_raw.read_applications(path)

def test_read_credits(tmp_path):
    path = tmp_path / "c.csv"
    path.write_text('applicant_id,fico_score\nC1,700\n')
    assert load_raw.read_credits(path)[0]["fico_score"] == "700"

def test_write_ndjson(tmp_path):
    path = tmp_path / "a.ndjson"
    load_raw.write_ndjson([{"a": 1}, {"a": 2}], path)
    assert [json.loads(line) for line in path.read_text().splitlines()] == [{"a": 1}, {"a": 2}]

def test_write_credit_csv(tmp_path):
    path = tmp_path / "c.csv"
    load_raw.write_credit_csv([{"applicant_id":"C1", "ssn":"X", "fico_score":700, "monthly_debt":20}], path)
    with path.open() as f: assert list(csv.DictReader(f))[0]["applicant_id"] == "C1"

def test_run_sql():
    cursor = MagicMock()
    load_raw.run_sql(cursor, "SELECT 1")
    cursor.execute.assert_called_once_with("SELECT 1")

def test_load_raw_executes_copy_and_append(monkeypatch):
    conn = MagicMock()
    statements = []
    monkeypatch.setattr(load_raw, "run_sql", lambda cursor, statement: statements.append(statement))
    load_raw.load_raw([{"application_id":"A1", "applicant_id":"C1"}], [{"applicant_id":"C1", "ssn":"X", "fico_score":"700", "monthly_debt":"10"}], conn)
    assert sum("COPY INTO" in s for s in statements) == 2
    assert sum("INSERT INTO" in s for s in statements) == 2
    conn.commit.assert_called_once()

def test_main(monkeypatch):
    monkeypatch.setattr(load_raw, "read_applications", lambda p: [])
    monkeypatch.setattr(load_raw, "read_credits", lambda p: [])
    conn = MagicMock()
    monkeypatch.setattr(load_raw, "connect", lambda: conn)
    monkeypatch.setattr(load_raw, "load_raw", lambda a,b,c: None)
    load_raw.main()
    conn.close.assert_called_once()
