"""Name-based resource resolvers.

Four pure functions corresponding to the ``genomics.cache.Resolve``
event facets: reference / annotation / SRA accession / list. They all
read from :data:`genomics.tools._lib.resources.RESOURCE_REGISTRY`.
"""

from __future__ import annotations

from typing import Any

from .resources import (
    ANNOTATION_ALIASES,
    REFERENCE_ALIASES,
    RESOURCE_REGISTRY,
)

_EMPTY_CACHE: dict[str, Any] = {
    "url": "",
    "path": "",
    "date": "",
    "size": 0,
    "wasInCache": False,
    "checksum": "",
    "resource_type": "unknown",
}


def _resolved_cache(namespace: str, facet_name: str) -> dict[str, Any]:
    """Look up a resource in the registry and return its cache entry."""
    entry = RESOURCE_REGISTRY.get(namespace, {}).get(facet_name)
    if not entry:
        return dict(_EMPTY_CACHE)
    url, path, size, rtype = entry
    return {
        "url": url,
        "path": path,
        "date": "2026-02-08",
        "size": size,
        "wasInCache": True,
        "checksum": f"sha256:{hash(path) & 0xFFFFFFFF:08x}",
        "resource_type": rtype,
    }


def _resolution(
    *,
    query: str,
    category: str,
    matched_name: str = "",
    resource_namespace: str = "",
    source_url: str = "",
    is_ambiguous: bool = False,
    disambiguation: str = "",
) -> dict[str, Any]:
    return {
        "query": query,
        "matched_name": matched_name,
        "resource_namespace": resource_namespace,
        "category": category,
        "source_url": source_url,
        "is_ambiguous": is_ambiguous,
        "disambiguation": disambiguation,
    }


def resolve_reference(*, name: str) -> dict[str, Any]:
    """Resolve a reference genome name to its cache entry."""
    norm = name.lower().strip()
    if norm in REFERENCE_ALIASES:
        ns, facet = REFERENCE_ALIASES[norm]
        cache = _resolved_cache(ns, facet)
        return {
            "cache": cache,
            "resolution": _resolution(
                query=name,
                category="reference",
                matched_name=facet,
                resource_namespace=ns,
                source_url=cache["url"],
            ),
        }

    ref_ns = "genomics.cache.reference"
    for facet_name in RESOURCE_REGISTRY.get(ref_ns, {}):
        if facet_name.lower() == norm:
            cache = _resolved_cache(ref_ns, facet_name)
            return {
                "cache": cache,
                "resolution": _resolution(
                    query=name,
                    category="reference",
                    matched_name=facet_name,
                    resource_namespace=ref_ns,
                    source_url=cache["url"],
                ),
            }

    return {
        "cache": dict(_EMPTY_CACHE),
        "resolution": _resolution(
            query=name,
            category="reference",
            is_ambiguous=True,
            disambiguation=f"Unknown reference: '{name}'. Known: "
            + ", ".join(sorted(REFERENCE_ALIASES.keys())),
        ),
    }


def resolve_annotation(*, name: str) -> dict[str, Any]:
    """Resolve an annotation database name to its cache entry."""
    norm = name.lower().strip()
    if norm in ANNOTATION_ALIASES:
        ns, facet = ANNOTATION_ALIASES[norm]
        cache = _resolved_cache(ns, facet)
        return {
            "cache": cache,
            "resolution": _resolution(
                query=name,
                category="annotation",
                matched_name=facet,
                resource_namespace=ns,
                source_url=cache["url"],
            ),
        }

    return {
        "cache": dict(_EMPTY_CACHE),
        "resolution": _resolution(
            query=name,
            category="annotation",
            is_ambiguous=True,
            disambiguation=f"Unknown annotation: '{name}'. Known: "
            + ", ".join(sorted(ANNOTATION_ALIASES.keys())),
        ),
    }


def resolve_sample(*, accession: str) -> dict[str, Any]:
    """Resolve an SRA accession to its cache entry."""
    sra_ns = "genomics.cache.sra"
    facets = RESOURCE_REGISTRY.get(sra_ns, {})
    acc = accession.strip()
    if acc in facets:
        cache = _resolved_cache(sra_ns, acc)
        return {
            "cache": cache,
            "resolution": _resolution(
                query=accession,
                category="sra",
                matched_name=acc,
                resource_namespace=sra_ns,
                source_url=cache["url"],
            ),
        }

    return {
        "cache": dict(_EMPTY_CACHE),
        "resolution": _resolution(
            query=accession,
            category="sra",
            is_ambiguous=True,
            disambiguation=f"Unknown SRA accession: '{accession}'. Known: "
            + ", ".join(sorted(facets.keys())),
        ),
    }


def list_resources(*, category: str = "") -> dict[str, Any]:
    """List all available cached resources, optionally filtered by category."""
    cat = category.lower().strip()
    resources: list[dict[str, Any]] = []
    categories: dict[str, int] = {}
    for namespace, facets in RESOURCE_REGISTRY.items():
        for facet_name, (url, path, size, rtype) in facets.items():
            if cat and rtype != cat:
                continue
            resources.append(
                {
                    "name": facet_name,
                    "namespace": namespace,
                    "url": url,
                    "path": path,
                    "size": size,
                    "resource_type": rtype,
                }
            )
            categories[rtype] = categories.get(rtype, 0) + 1
    return {
        "resource_count": len(resources),
        "resources": resources,
        "category_count": len(categories),
        "categories": categories,
    }
