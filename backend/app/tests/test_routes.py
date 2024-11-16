import pytest
import requests
import subprocess
import signal
import os
import time
import sys


MODEL = os.environ.get("MODEL", "mockai")


@pytest.fixture(scope="module")
def start_mockai():
    if MODEL == "mockai":
        mockai = subprocess.Popen(
            ["npm", "start"], cwd="../mockai", preexec_fn=os.setpgrp
        )
        print(f"::mockai start, pid={mockai.pid}")
        time.sleep(1)

    yield

    if (MODEL == "mockai") and (mockai.poll() is None):
        os.killpg(os.getpgid(mockai.pid), signal.SIGTERM)
        print("::mockai end")


@pytest.fixture(scope="module")
def start_app():
    app = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=".",
        preexec_fn=os.setpgrp,
        env={
            "DEBUG": "1",
            "MODEL_NAME": MODEL,
            "PORT": "10228",
            "SQLITE_URI": "sqlite://",
        },
    )
    print(f"::main app, pid={app.pid}")
    time.sleep(1)

    yield

    if app.poll() is None:
        os.killpg(os.getpgid(app.pid), signal.SIGTERM)
        print("::main app end")


def test_chat(start_app, start_mockai):
    """ """
    APP_HOST = "http://localhost:10228"

    # empty
    assert not requests.get(f"{APP_HOST}/chat_sessions").json()

    resp = requests.put(
        f"{APP_HOST}/chat_sessions",
        json={
            "secret_key": MODEL,
            "system_prompt": "Act as a cute little catgirl.",
            "model_params": {"temperature": 1.5},
        },
    ).json()

    sess_id = resp["session_id"]

    resp = requests.post(
        f"{APP_HOST}/chat",
        json={
            "session_id": sess_id,
            "user_prompt": "Hello, how are you today?",
        },
        stream=True,
    )

    for chunk in resp.iter_lines(512):
        print(chunk)
