"""
Author: NierYYDS
"""

import copy
import base64
import json
import logging
from typing import Optional
from fastapi import Body, FastAPI
from pydantic import BaseModel
from image_replacer_webhook.setting import settings
from image_replacer_webhook.utils import (
    image_add_prefix_cache,
    skip_registries_check,
)


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


@app.post("/mutate")
async def mutate(req=Body(...)) -> AdmissionReviewResponse:
    """Mutate container image of pod"""

    req_uid = req["request"]["uid"]

    logging.info(
        "req_uid=%s, Received a mutation request: %s",
        req_uid,
        json.dumps(req, indent=2),
    )

    def replace_container_image(containers: list) -> list:
        """Replace container image"""
        for container in containers:
            original_image = container["image"]
            if skip_registries_check(original_image, settings.skip_registries):
                continue
            new_image = image_add_prefix_cache(original_image, settings.cache_registry)
            if original_image == new_image:
                logging.info(
                    "req_uid=%s, container(%s) image %s not replaced",
                    req_uid,
                    container["name"],
                    original_image,
                )
                continue
            logging.info(
                "req_uid=%s, container(%s) image %s replaced with %s",
                req_uid,
                container["name"],
                original_image,
                new_image,
            )
            container["image"] = new_image

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
        replace_container_image(containers)
        # 遍历init容器
        init_containers = req_obj["spec"].get("initContainers", [])
        origin_init_containers = copy.deepcopy(init_containers)
        replace_container_image(init_containers)
        # 如果容器没有变化，则直接返回
        if (
            containers == origin_containers
            and init_containers == origin_init_containers
        ):
            logging.info("req_uid=%s, No changes to the pod spec were made.", req_uid)
            return AdmissionReviewResponse(response=Response(uid=req_uid, allowed=True))

        # 构造patch
        patch = [{"op": "replace", "path": "/spec/containers", "value": containers}]
        if init_containers:
            patch.append(
                {
                    "op": "replace",
                    "path": "/spec/initContainers",
                    "value": init_containers,
                }
            )
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
