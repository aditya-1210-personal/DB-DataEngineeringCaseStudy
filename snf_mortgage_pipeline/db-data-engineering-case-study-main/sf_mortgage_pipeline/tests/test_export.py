from config import export_credentials

def test_export_secret(tmp_path, monkeypatch):
    monkeypatch.setattr(export_credentials, "get_snowflake_secret", lambda: {"account":"a", "user":"u", "private_key_pem":"TEST"})
    target = tmp_path / "key.pem"
    assert export_credentials.export_secret(target)["SNOWFLAKE_ACCOUNT"] == "a"
    assert target.read_text() == "TEST"
