"""
Author: NierYYDS
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """config"""

    tls_cert_dir: str = "./certs"
    ignore_ca_cert: bool = False  # 服务启动时不依赖CA证书，用于k8s部署
    cache_enabled: bool = True
    cache_registry: str = "m.daocloud.io"
    skip_registries: List[str] = []  # 不进行替换的源


settings = Settings()
