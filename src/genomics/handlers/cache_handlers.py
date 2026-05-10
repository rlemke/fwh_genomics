"""Per-entity genomics cache download handlers.

One handler per registry entry (reference genomes, annotation tracks,
SRA samples) in the ``genomics.cache.<namespace>`` family. Factory-
built from :data:`genomics.tools._lib.resources.RESOURCE_REGISTRY`;
the simulator logic for one cache row is
:func:`genomics.tools._lib.cache.cache_entry`.
"""

import logging
import os
from collections.abc import Callable
from typing import Any

from .shared.genomics_utils import RESOURCE_REGISTRY, cache_entry

log = logging.getLogger(__name__)


def _make_handler(url: str, path: str, size: int, resource_type: str) -> Callable:
    """Factory: create a cache handler returning a GenomicsCache dict."""

    def handler(payload: dict) -> dict[str, Any]:
        step_log = payload.get("_step_log")
        if step_log:
            step_log(f"Cache: {resource_type} {path}")
        return {
            "cache": cache_entry(
                url=url, path=path, size=size, resource_type=resource_type
            )
        }

    return handler


# RegistryRunner dispatch adapter — populated lazily so a future
# RESOURCE_REGISTRY edit (e.g. test fixture) is reflected.
_DISPATCH: dict[str, Callable] = {}


def _build_dispatch() -> None:
    _DISPATCH.clear()
    for namespace, facets in RESOURCE_REGISTRY.items():
        for facet_name, (url, path, size, rtype) in facets.items():
            _DISPATCH[f"{namespace}.{facet_name}"] = _make_handler(
                url, path, size, rtype
            )


_build_dispatch()


def handle(payload: dict) -> dict:
    """RegistryRunner dispatch entrypoint."""
    facet_name = payload["_facet_name"]
    handler = _DISPATCH.get(facet_name)
    if handler is None:
        raise ValueError(f"Unknown facet: {facet_name}")
    return handler(payload)


def register_handlers(runner) -> None:
    """Register all facets with a RegistryRunner."""
    for facet_name in _DISPATCH:
        runner.register_handler(
            facet_name=facet_name,
            module_uri=f"file://{os.path.abspath(__file__)}",
            entrypoint="handle",
        )


def register_cache_handlers(poller) -> None:
    """Register all per-entity genomics cache download handlers."""
    for fqn, handler in _DISPATCH.items():
        poller.register(fqn, handler)
        log.debug("Registered cache handler: %s", fqn)
    log.debug("Registered %d genomics cache handlers", len(_DISPATCH))
