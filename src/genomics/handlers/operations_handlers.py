"""Genomics cache operations event facet handlers.

Handles event facets in ``genomics.cache.Operations``: Download, Index,
Validate, Status, Checksum. The simulator logic lives in
:mod:`genomics.tools._lib.operations`.
"""

import logging
import os
from typing import Any

from .shared.genomics_utils import (
    checksum,
    download,
    index_op,
    status,
    validate,
)

log = logging.getLogger(__name__)

NAMESPACE = "genomics.cache.Operations"


def _download_handler(payload: dict) -> dict[str, Any]:
    step_log = payload.get("_step_log")
    cache = payload.get("cache", {})
    if step_log:
        step_log(f"Download: {cache.get('path', '')}")
    return download(cache=cache)


def _index_handler(payload: dict) -> dict[str, Any]:
    step_log = payload.get("_step_log")
    cache = payload.get("cache", {})
    aligner = payload.get("aligner", "bwa")
    if step_log:
        step_log(f"Index: {aligner} from {cache.get('path', '')}")
    return index_op(cache=cache, aligner=aligner)


def _validate_handler(payload: dict) -> dict[str, Any]:
    step_log = payload.get("_step_log")
    if step_log:
        step_log("Validate: verifying checksum")
    return validate(cache=payload.get("cache"))


def _status_handler(payload: dict) -> dict[str, Any]:
    step_log = payload.get("_step_log")
    cache = payload.get("cache", {})
    if step_log:
        step_log(f"Status: {cache.get('path', '')}")
    return status(cache=cache)


def _checksum_handler(payload: dict) -> dict[str, Any]:
    step_log = payload.get("_step_log")
    cache = payload.get("cache", {})
    if step_log:
        step_log(f"Checksum: {cache.get('path', '')}")
    return checksum(cache=cache)


# RegistryRunner dispatch adapter
_DISPATCH = {
    f"{NAMESPACE}.Download": _download_handler,
    f"{NAMESPACE}.Index": _index_handler,
    f"{NAMESPACE}.Validate": _validate_handler,
    f"{NAMESPACE}.Status": _status_handler,
    f"{NAMESPACE}.Checksum": _checksum_handler,
}


def handle(payload: dict) -> dict:
    facet_name = payload["_facet_name"]
    handler = _DISPATCH.get(facet_name)
    if handler is None:
        raise ValueError(f"Unknown facet: {facet_name}")
    return handler(payload)


def register_handlers(runner) -> None:
    for facet_name in _DISPATCH:
        runner.register_handler(
            facet_name=facet_name,
            module_uri=f"file://{os.path.abspath(__file__)}",
            entrypoint="handle",
        )


def register_operations_handlers(poller) -> None:
    for fqn, func in _DISPATCH.items():
        poller.register(fqn, func)
        log.debug("Registered genomics operation handler: %s", fqn)
