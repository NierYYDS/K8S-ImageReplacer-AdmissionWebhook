"""
Author: NierYYDS
"""

import pytest
from image_replacer_webhook.utils import normalize_image_name, skip_registries_check


@pytest.mark.parametrize(
    "name,result",
    [
        ("redis", "docker.io/library/redis"),
        ("nginx/nginx", "docker.io/nginx/nginx"),
        ("quay.io/nginx/nginx", "quay.io/nginx/nginx"),
    ],
)
def test_normalize_image_name(name: str, result: str):
    assert normalize_image_name(name) == result


@pytest.mark.parametrize(
    "name,skip_registries,result",
    [
        ("redis", [], False),
        ("my-registry.com/nginx/nginx", ["other-registry.com"], False),
        ("my-registry.com/nginx/nginx", ["my-registry.com"], True),
        (
            "my-registry.com/nginx/nginx",
            ["my-registry.com", "other-registry.com"],
            True,
        ),
    ],
)
def test_skip_registries_check(name: str, skip_registries: list, result: bool):
    assert skip_registries_check(name, skip_registries) == result
