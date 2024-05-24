"""
Author: NierYYDS
"""

import re
import json
import base64
import pytest
from fastapi.testclient import TestClient
from image_replacer_webhook.server import app


# pylint: disable=redefined-outer-name
@pytest.fixture
def client():
    """test client"""
    yield TestClient(app)


def test_mutate_post(client):
    """test of mutate"""
    with open(
        "./tests/data/mutating-webhook-request-payload.json", "r", encoding="utf-8"
    ) as f:
        payload = json.loads(f.read())
    resp = client.post("/mutate", json=payload)
    assert resp.status_code == 200
    assert resp.json()["response"]["allowed"] is True
    assert resp.json()["response"]["patchType"] == "JSONPatch"
    patch = json.loads(
        base64.decodebytes(resp.json()["response"]["patch"].encode()).decode()
    )
    for p in patch:
        assert p["op"] == "replace"
        assert re.match(r"(/spec/(initContainers|containers)/(\d+)/image)", p["path"]) is not None
        assert p["value"].startswith("m.daocloud.io/docker.io/")
