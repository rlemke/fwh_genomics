"""Aligner-index simulator (used by the factory in handlers/index_handlers.py).

Given ``aligner`` (``bwa`` / ``star`` / ``bowtie2``) and ``reference``
(``GRCh38`` / etc.), returns the simulated ``IndexCache`` record. The
contig counts and version strings live in
``genomics.tools._lib.resources``.
"""

from __future__ import annotations

from typing import Any

from .resources import (
    ALIGNER_SIZE_MULTIPLIERS,
    ALIGNER_VERSIONS,
    REFERENCE_CONTIGS,
)


def index_entry(
    *,
    aligner: str,
    reference: str,
    source_path: str | None = None,
) -> dict[str, Any]:
    """Return the simulated index-cache record for one aligner/reference pair.

    *source_path* defaults to the canonical cached reference path; pass
    an override when chaining off an upstream cache step.
    """
    contigs, bases = REFERENCE_CONTIGS.get(reference, (0, 0))
    version = ALIGNER_VERSIONS.get(aligner, aligner)
    multiplier = ALIGNER_SIZE_MULTIPLIERS.get(aligner, 1.0)
    src = source_path or f"/cache/reference/{reference}/{reference}.fa.gz"
    return {
        "source_path": src,
        "index_dir": f"/cache/index/{aligner}/{reference}/",
        "aligner": aligner,
        "date": "2026-02-08",
        "size": int(3_000_000_000 * multiplier),
        "wasInCache": True,
        "version": version,
        "contig_count": contigs,
        "total_bases": bases,
    }
