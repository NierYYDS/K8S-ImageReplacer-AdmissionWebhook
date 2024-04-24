"""
Author: NierYYDS
"""

import os
import sys
import logging


def check_tls_cert_dir(cert_dir: str) -> None:
    if not os.path.exists(cert_dir):
        logging.error("TLS Cert directory %s does not exists.", dir)
        sys.exit(1)
