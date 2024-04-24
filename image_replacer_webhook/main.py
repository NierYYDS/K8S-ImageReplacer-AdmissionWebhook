"""
Author: NierYYDS
"""

import os
import copy
import base64
import json
import logging
from typing import Optional
import uvicorn
from fastapi import Body, FastAPI
from pydantic import BaseModel
from setting import settings
from utils import check_tls_cert_dir


class Response(BaseModel):
    """webhook response核心payload"""

    uid: str
    allowed: bool
    patchType: Optional[str] = None
    patch: Optional[str] = None


class AdmissionReviewResponse(BaseModel):
    """webhook请求返回数据"""

    apiVersion: str = "admission.k8s.io/v1"
    kind: str = "AdmissionReview"
    response: Response


app = FastAPI()


@app.get("/")
async def index():
    """index"""
    return {"message": "Hello, this is Image Replacer AdmissionWebhook!"}


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


def image_add_prefix_cache(image_name: str, cache_registry: str) -> str:
    """
    使用前缀缓存镜像
    """
    image_name = normalize_image_name(image_name)
    if image_name.startswith(cache_registry):
        return image_name
    return f"{cache_registry}/{image_name}"


@app.post("/mutate")
async def mutate(req=Body(...)) -> AdmissionReviewResponse:
    """Mutate container image of pod"""

    req_uid = req["request"]["uid"]

    logging.info(
        "req_uid=%s, Received a mutation request: %s",
        req_uid,
        json.dumps(req, indent=2),
    )
    # 遍历pod的每个container
    try:
        # 提取请求中的 Pod 对象
        req_obj = req["request"]["object"]
        if req_obj["kind"] != "Pod":
            logging.error(
                "req_uid=%s, This webhook only supports pod mutation.", req_uid
            )
            return AdmissionReviewResponse(
                response=Response(uid=req_uid, allowed=False)
            )
        # 遍历所有容器，修改镜像名称
        containers = req_obj["spec"]["containers"]
        origin_containers = copy.deepcopy(containers)
        for container in containers:
            original_image = container["image"]
            new_image = image_add_prefix_cache(original_image, settings.cache_registry)
            if original_image != new_image:
                container["image"] = new_image
                logging.info(
                    "req_uid=%s, container(%s) image %s replaced with %s",
                    req_uid,
                    container["name"],
                    original_image,
                    new_image,
                )
        if containers == origin_containers:  # 如果容器没有变化，则直接返回
            logging.info("req_uid=%s, No changes to the pod spec were made.", req_uid)
            return AdmissionReviewResponse(response=Response(uid=req_uid, allowed=True))

        # 构造patch
        patch = [{"op": "replace", "path": "/spec/containers", "value": containers}]
        image_patch = base64.b64encode(json.dumps(patch).encode()).decode()
        logging.info("req_uid=%s, Patching pod with %s", req_uid, patch)
        resp = Response(
            uid=req_uid,
            allowed=True,
            patchType="JSONPatch",
            patch=image_patch,
        )
        return AdmissionReviewResponse(response=resp)
    except KeyError:
        logging.exception(
            "req_uid=%s, the API server sent a request that did not have the required information.",
            req_uid,
        )
        return AdmissionReviewResponse(response=Response(uid=req_uid, allowed=True))


if __name__ == "__main__":
    # 启动服务
    logging.basicConfig(level=logging.INFO)
    # 读取配置文件
    logging.info("Reading configuration file..., %s", settings)
    check_tls_cert_dir(settings.tls_cert_dir)
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
