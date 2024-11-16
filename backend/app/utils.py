import os
import json


def get_environ_int(env_key, default=0) -> int:
    """snippets to get environ int"""
    try:
        return int(os.environ.get(env_key, default))
    except (ValueError,):
        return int(default)


def load_secret(name="mockai", secret_path="../secrets.json"):
    with open(secret_path, "r") as fp:
        secrets = json.load(fp)

    if name is None:
        return secrets
    else:
        return secrets[name]
