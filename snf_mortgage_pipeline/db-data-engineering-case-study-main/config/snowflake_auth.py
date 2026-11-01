"""Snowflake key-pair auth with private key stored in HashiCorp Vault."""
import os
from cryptography.hazmat.primitives import serialization
from config.vault import get_snowflake_secret

def private_key_der(pem, passphrase=None):
    key = serialization.load_pem_private_key(pem.encode() if isinstance(pem, str) else pem, password=passphrase.encode() if isinstance(passphrase, str) else passphrase)
    return key.private_bytes(encoding=serialization.Encoding.DER, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption())

def connection_parameters(secret, env=None):
    env = env or os.environ
    required = ("account", "user", "private_key_pem")
    missing = [field for field in required if not secret.get(field)]
    if missing:
        raise ValueError("Vault secret missing: " + ", ".join(missing))
    return {"account": secret["account"], "user": secret["user"], "private_key": private_key_der(secret["private_key_pem"], secret.get("private_key_passphrase")), "role": env.get("SNOWFLAKE_ROLE", "MORTGAGE_PIPELINE_ROLE"), "warehouse": env.get("SNOWFLAKE_WAREHOUSE", "MORTGAGE_WH"), "database": env.get("SNOWFLAKE_DATABASE", "MORTGAGE_DB")}

def connect():
    import snowflake.connector
    return snowflake.connector.connect(**connection_parameters(get_snowflake_secret()))
