"""Derived aligner index cache handlers.

Factory-built handlers for the ``genomics.cache.index.<aligner>``
namespaces. Source-of-truth for the registry + size multipliers +
version strings is :mod:`genomics.tools._lib.resources`; the per-pair
simulator is :func:`genomics.tools._lib.index.index_entry`.
"""

import logging
import os
from collections.abc import Callable
from typing import Any

from .shared.genomics_utils import INDEX_REGISTRY, index_entry

log = logging.getLogger(__name__)


def _make_index_handler(aligner: str, reference: str) -> Callable:
    """Factory: create an index handler returning an IndexCache dict."""

    def handler(payload: dict) -> dict[str, Any]:
        step_log = payload.get("_step_log")
        if step_log:
            step_log(f"Index: {aligner}/{reference}")
        source_path = ""
        if isinstance(payload.get("cache"), dict):
            source_path = payload["cache"].get("path", "")
        return {
            "index": index_entry(
                aligner=aligner,
                reference=reference,
                source_path=source_path or None,
            )
        }

    return handler


_DISPATCH: dict[str, Callable] = {}


def _build_dispatch() -> None:
    _DISPATCH.clear()
    for namespace, refs in INDEX_REGISTRY.items():
        aligner = namespace.rsplit(".", 1)[-1]
        for reference in refs:
            _DISPATCH[f"{namespace}.{reference}"] = _make_index_handler(
                aligner, reference
            )


_build_dispatch()


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


def register_index_handlers(poller) -> None:
    for fqn, handler in _DISPATCH.items():
        poller.register(fqn, handler)
        log.debug("Registered index handler: %s", fqn)
    log.debug("Registered %d genomics index handlers", len(_DISPATCH))
