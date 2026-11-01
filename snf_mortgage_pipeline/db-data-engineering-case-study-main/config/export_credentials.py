"""Write ephemeral PEM key for dbt and Terraform; caller must delete it."""
import os
from pathlib import Path
from config.vault import get_snowflake_secret

def export_secret(path):
    secret = get_snowflake_secret()
    path = Path(path)
    path.write_text(secret["private_key_pem"], encoding="utf-8")
    path.chmod(0o600)
    return {"SNOWFLAKE_ACCOUNT": secret["account"], "SNOWFLAKE_USER": secret["user"], "SNOWFLAKE_PRIVATE_KEY_PATH": str(path), "SNOWFLAKE_PRIVATE_KEY_PASSPHRASE": secret.get("private_key_passphrase", "")}

if __name__ == "__main__":
    import sys
    import shlex
    result = export_secret(sys.argv[1])
    for key, value in result.items():
        print(f"export {key}={shlex.quote(value)}")
