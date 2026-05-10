"""Cache-entry simulator (used by the factory in handlers/cache_handlers.py).

``cache_entry`` is the pure-function form of what each factory-built
handler emits: a single ``GenomicsCache``-shaped dict for one
registry entry. Both the FFL handler (via the shim) and the CLI tool
call this directly.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def cache_entry(
    *,
    url: str,
    path: str,
    size: int,
    resource_type: str,
) -> dict[str, Any]:
    """Return the simulated cache record for one resource."""
    return {
        "url": url,
        "path": path,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "size": size,
        "wasInCache": True,
        "checksum": f"sha256:{hash(path) & 0xFFFFFFFF:08x}",
        "resource_type": resource_type,
    }
