"""Cache-operations simulators — Download, Index, Validate, Status, Checksum.

Mirrors the public functions the FFL handlers in
``genomics.handlers.operations_handlers`` register under the
``genomics.cache.Operations`` namespace.
"""

from __future__ import annotations

from typing import Any


def download(*, cache: dict[str, Any]) -> dict[str, Any]:
    """Pass-through: simulate downloading an already-cached resource."""
    return {"cache": dict(cache)}


def index(*, cache: dict[str, Any], aligner: str = "bwa") -> dict[str, Any]:
    """Simulate building an aligner index from a cached reference."""
    source_path = cache.get("path", "")
    return {
        "cache": {
            "source_path": source_path,
            "index_dir": f"/cache/index/{aligner}/",
            "aligner": aligner,
            "date": "2026-02-08",
            "size": 4_500_000_000,
            "wasInCache": True,
            "version": f"{aligner}-latest",
            "contig_count": 195,
            "total_bases": 3_088_286_401,
        }
    }


def validate(*, cache: dict[str, Any] | None = None) -> dict[str, Any]:  # noqa: ARG001
    """Simulate validating a cached resource by checksum."""
    return {"valid": True, "message": "Checksum verified"}


def status(*, cache: dict[str, Any]) -> dict[str, Any]:
    """Simulate reporting cache hit / size for a cached resource."""
    return {
        "path": cache.get("path", ""),
        "size": cache.get("size", 0),
        "wasInCache": True,
        "available": True,
    }


def checksum(*, cache: dict[str, Any]) -> dict[str, Any]:
    """Simulate computing a checksum for a cached resource."""
    path = cache.get("path", "")
    return {
        "path": path,
        "algorithm": "sha256",
        "digest": "a" * 64,
    }
