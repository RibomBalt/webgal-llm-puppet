import pytest
import httpx
import subprocess
import signal
import os
import time
import sys
from urllib.parse import quote
from fastapi.testclient import TestClient
from .. import create_app
from ..dependencies import init_cache


# MODEL = os.environ.get("MODEL", "mockai")


# @pytest.fixture(scope="module")
# def start_mockai():
#     if MODEL == "mockai":
#         mockai = subprocess.Popen(
#             ["npm", "start"], cwd="../mockai", preexec_fn=os.setpgrp
#         )
#         print(f"::mockai start, pid={mockai.pid}")
#         time.sleep(1)

#     yield

#     if (MODEL == "mockai") and (mockai.poll() is None):
#         os.killpg(os.getpgid(mockai.pid), signal.SIGTERM)
#         print("::mockai end")

def get_change_scene_url(scene: str):
    change_scene_line = next(
        line
        for line in scene.splitlines(keepends=False)
        if line.startswith("changeScene:")
    )
    change_scene_url = change_scene_line.split(':', maxsplit=1)[1].split(' ')[0]
    return change_scene_url


def test_webgal():
    """ """
    with TestClient(create_app()) as client:

        # health
        resp = client.get("/webgal")
        assert resp.status_code == 200

        # create chat
        resp = client.get("/webgal/newchat.txt?bot=sakiko")
        assert resp.status_code == 200

        # not fill in templates, simulating prefetching
        next_url_path = get_change_scene_url(resp.text)
        assert 'chat.txt' in next_url_path
        resp = client.get(next_url_path)
        assert resp.status_code == 200

        # still chat.txt, but template is filled
        next_url_path = next_url_path.replace('{prompt}', '你好').replace('{pending}','1')
        resp = client.get(next_url_path)
        assert resp.status_code == 200, next_url_path

        next_url_path = get_change_scene_url(resp.text)
        while 'next.txt' in next_url_path:
            time.sleep(1)
            resp = client.get(next_url_path)
            assert resp.status_code == 200, next_url_path
            next_url_path = get_change_scene_url(resp.text)
            
        assert 'chat.txt' in next_url_path






    