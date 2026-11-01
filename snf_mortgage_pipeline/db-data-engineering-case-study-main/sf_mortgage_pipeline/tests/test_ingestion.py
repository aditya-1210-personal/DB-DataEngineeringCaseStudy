def test_load_raw_executes_copy_and_append(monkeypatch):
    from unittest.mock import MagicMock
    from ingestion import load_raw

    conn = MagicMock()
    statements = []

    monkeypatch.setattr(
        load_raw,
        "run_sql",
        lambda cursor, statement: statements.append(statement),
    )

    applications = [
        {"application_id": "A1", "applicant_id": "C1"}
    ]

    credits = [
        {
            "applicant_id": "C1",
            "ssn": "TEST",
            "fico_score": "700",
            "monthly_debt": "10",
        }
    ]

    load_raw.load_raw(applications, credits, conn)

    assert sum("COPY INTO" in s for s in statements) == 2
    assert sum("INSERT INTO" in s for s in statements) == 2

    conn.commit.assert_called_once()
