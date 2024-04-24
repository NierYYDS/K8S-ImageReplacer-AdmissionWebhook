"""
Author: NierYYDS
"""

import os
import sys
import logging


def normalize_image_name(image_name: str) -> str:
    """
    将一些短镜像名还原成完成的镜像名
    redis => docker.io/library/redis
    nginx/nginx => docker.io/nginx/nginx
    quay.io/nginx/nginx => quay.io/nginx/nginx
    """
    slash_count = image_name.count("/")
    name = image_name
    if slash_count == 0:
        name = f"docker.io/library/{image_name}"
    elif slash_count == 1:
        name = f"docker.io/{image_name}"

    return name


def skip_registries_check(image_name: str, skip_registries: list) -> bool:
    """检查是否在忽略列表里面的镜像"""
    for registry in skip_registries:
        if image_name.startswith(registry):
            return True
    return False


def image_add_prefix_cache(image_name: str, cache_registry: str) -> str:
    """
    使用前缀缓存镜像
    """
    image_name = normalize_image_name(image_name)
    if image_name.startswith(cache_registry):
        return image_name
    return f"{cache_registry}/{image_name}"


def check_tls_cert_dir(cert_dir: str) -> None:
    """check if tls cert diretory exist"""
    if not os.path.exists(cert_dir):
        logging.error("TLS Cert directory %s does not exists.", dir)
        sys.exit(1)
