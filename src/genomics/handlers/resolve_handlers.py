"""Name-based resource resolution handlers.

Handles event facets in the ``genomics.cache.Resolve`` namespace.
The simulator logic — alias lookup, fallback to facet-name match,
catalog listing — lives in :mod:`genomics.tools._lib.resolve`.
"""

import logging
import os
from typing import Any

from .shared.genomics_utils import (
    list_resources,
    resolve_annotation,
    resolve_reference,
    resolve_sample,
)

log = logging.getLogger(__name__)

NAMESPACE = "genomics.cache.Resolve"


def _resolve_reference_handler(payload: dict) -> dict[str, Any]:
    name = payload.get("name", "")
    step_log = payload.get("_step_log")
    result = resolve_reference(name=name)
    if step_log:
        matched = result["resolution"]["matched_name"]
        step_log(f"ResolveReference: '{name}' -> {matched or '?'}")
    return result


def _resolve_annotation_handler(payload: dict) -> dict[str, Any]:
    name = payload.get("name", "")
    step_log = payload.get("_step_log")
    result = resolve_annotation(name=name)
    if step_log:
        matched = result["resolution"]["matched_name"]
        step_log(f"ResolveAnnotation: '{name}' -> {matched or '?'}")
    return result


def _resolve_sample_handler(payload: dict) -> dict[str, Any]:
    accession = payload.get("accession", "")
    step_log = payload.get("_step_log")
    result = resolve_sample(accession=accession)
    if step_log:
        matched = result["resolution"]["matched_name"]
        step_log(f"ResolveSample: '{accession}' -> {matched or '?'}")
    return result


def _list_resources_handler(payload: dict) -> dict[str, Any]:
    category = payload.get("category", "")
    step_log = payload.get("_step_log")
    if step_log:
        step_log(f"ListResources: category={category or 'all'}")
    return {"result": list_resources(category=category)}


_DISPATCH = {
    f"{NAMESPACE}.ResolveReference": _resolve_reference_handler,
    f"{NAMESPACE}.ResolveAnnotation": _resolve_annotation_handler,
    f"{NAMESPACE}.ResolveSample": _resolve_sample_handler,
    f"{NAMESPACE}.ListResources": _list_resources_handler,
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


def register_resolve_handlers(poller) -> None:
    for fqn, func in _DISPATCH.items():
        poller.register(fqn, func)
        log.debug("Registered resolve handler: %s", fqn)
