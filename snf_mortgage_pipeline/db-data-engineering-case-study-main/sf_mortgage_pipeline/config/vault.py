"""HashiCorp Vault KV v2 secret retrieval (no credentials committed to Git)."""
import os
import hvac

def vault_config(env=None):
    env = env or os.environ
    return {"url": env.get("VAULT_ADDR"), "mount_point": env.get("VAULT_KV_MOUNT", "secret"), "path": env.get("VAULT_SECRET_PATH", "mortgage/snowflake")}

def get_snowflake_secret(client=None, env=None):
    env = env or os.environ
    config = vault_config(env)
    if not config["url"]:
        raise RuntimeError("VAULT_ADDR is required")
    if client is None:
        token = env.get("VAULT_TOKEN")
        if not token:
            raise RuntimeError("VAULT_TOKEN is required (use short-lived auth in production)")
        client = hvac.Client(url=config["url"], token=token)
    if not client.is_authenticated():
        raise RuntimeError("Vault authentication failed")
    response = client.secrets.kv.v2.read_secret_version(path=config["path"], mount_point=config["mount_point"])
    return response["data"]["data"]
