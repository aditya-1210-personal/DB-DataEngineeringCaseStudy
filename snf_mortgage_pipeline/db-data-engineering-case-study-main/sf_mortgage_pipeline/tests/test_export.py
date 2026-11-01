from pathlib import Path
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from config.export_credentials import write_ci_credentials


def _secret():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                            serialization.BestAvailableEncryption(b"vault-passphrase"))
    return {"account": "account-id", "user": "ci-user", "private_key_pem": pem.decode(),
            "private_key_passphrase": "vault-passphrase"}


def test_export_only_key_file_and_nonsensitive_env(tmp_path):
    key_path, env_path = tmp_path / "key.pem", tmp_path / "github_env"
    write_ci_credentials(key_path, env_path, _secret())
    text = env_path.read_text()
    assert "SNOWFLAKE_ACCOUNT=account-id" in text
    assert "SNOWFLAKE_USER=ci-user" in text
    assert "SNOWFLAKE_PRIVATE_KEY_PATH=" in text
    assert "vault-passphrase" not in text
    assert "PRIVATE_KEY_PASSPHRASE" not in text
    assert "BEGIN PRIVATE KEY" not in text
    assert key_path.stat().st_mode & 0o777 == 0o600
    assert serialization.load_pem_private_key(key_path.read_bytes(), password=None)


def test_no_overwrite_existing_key(tmp_path):
    key_path, env_path = tmp_path / "key.pem", tmp_path / "github_env"
    key_path.write_text("existing")
    with pytest.raises(FileExistsError):
        write_ci_credentials(key_path, env_path, _secret())
    assert key_path.read_text() == "existing"


def test_reject_missing_fields(tmp_path):
    with pytest.raises(ValueError, match="private_key_pem"):
        write_ci_credentials(tmp_path / "key.pem", tmp_path / "env", {"account": "a", "user": "u"})
