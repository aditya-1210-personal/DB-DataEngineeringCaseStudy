from unittest.mock import MagicMock
import pytest
from config.vault import vault_config, get_snowflake_secret
from config.snowflake_auth import connection_parameters, private_key_der

def test_vault_config():
    assert vault_config({"VAULT_ADDR":"https://vault.test", "VAULT_SECRET_PATH":"path"})["path"] == "path"

def test_vault_fetch():
    client = MagicMock()
    client.is_authenticated.return_value = True
    client.secrets.kv.v2.read_secret_version.return_value = {"data":{"data":{"account":"test"}}}
    assert get_snowflake_secret(client, {"VAULT_ADDR":"https://vault.test"})["account"] == "test"

def test_vault_requires_address():
    with pytest.raises(RuntimeError): get_snowflake_secret(env={})

def test_missing_secret_fields():
    with pytest.raises(ValueError): connection_parameters({})

def test_key_der():
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    assert private_key_der(pem)
    args = connection_parameters({"account":"acct", "user":"user", "private_key_pem":pem}, {})
    assert args["private_key"]
