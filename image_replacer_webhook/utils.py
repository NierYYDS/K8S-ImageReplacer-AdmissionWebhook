"""
Author: NierYYDS
"""

import os
import sys
import logging


def check_tls_cert_dir(dir: str):
    if not os.path.exists(dir):
        logging.error("TLS Cert directory %s does not exists.", dir)
        sys.exit(1)
