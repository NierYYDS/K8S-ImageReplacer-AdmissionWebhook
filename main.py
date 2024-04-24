import os
import sys
import logging
import uvicorn
from image_replacer_webhook.main import app
from image_replacer_webhook.setting import settings


if __name__ == "__main__":
    # 启动服务
    logging.basicConfig(level=logging.INFO)
    # 读取配置文件
    logging.info("Reading configuration file..., %s", settings)
    if not os.path.exists(settings.tls_cert_dir):
        logging.error("TLS Cert directory %s does not exists.", dir)
        sys.exit(1)

    ssl_config = {
        "ssl_keyfile": os.path.join(settings.tls_cert_dir, "tls.key"),
        "ssl_certfile": os.path.join(settings.tls_cert_dir, "tls.crt"),
    }
    if not settings.ignore_ca_cert:
        ssl_config["ssl_ca_certs"] = os.path.join(settings.tls_cert_dir, "ca.crt")

    uvicorn.run(
        app,
        log_level="debug",
        host="0.0.0.0",
        **ssl_config,
    )
