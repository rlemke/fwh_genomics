"""Handler-side compatibility shim for the genomics simulators.

The real implementation lives in ``genomics.tools._lib``. It is shared
verbatim by:

- the ``qc-reads`` / ``align-reads`` / ``call-variants`` / … CLI tools
  under ``src/genomics/tools/``, and
- the FFL pipeline / operations / cache / index / resolve handlers in
  this package.

Imports use the fully-qualified ``genomics.tools._lib.<name>`` path so
this package coexists cleanly with sibling Facetwork example packages
(osm-geocoder, noaa-weather, jenkins, osm-lz, census-us) that also
ship a ``tools/_lib/`` directory — there is no fight for the bare
``_lib`` name on ``sys.modules``.
"""

from __future__ import annotations

# Modules (handlers that want the full surface).
from genomics.tools._lib import (  # noqa: F401
    cache,
    index,
    operations,
    pipeline,
    resolve,
    resources,
)

# Cache + index simulators.
from genomics.tools._lib.cache import cache_entry  # noqa: F401
from genomics.tools._lib.index import index_entry  # noqa: F401

# Operations simulators.
from genomics.tools._lib.operations import (  # noqa: F401
    checksum,
    download,
    index as index_op,
    status,
    validate,
)

# Per-sample / cohort pipeline simulators.
from genomics.tools._lib.pipeline import (  # noqa: F401
    align_reads,
    annotate,
    call_variants,
    cohort_analytics,
    ingest_reference,
    joint_genotype,
    normalize_filter,
    publish,
    qc_reads,
)

# Resource catalog data.
from genomics.tools._lib.resources import (  # noqa: F401
    ANNOTATION_ALIASES,
    CACHE_BASE,
    INDEX_REGISTRY,
    REFERENCE_ALIASES,
    RESOURCE_REGISTRY,
)

# Resolvers.
from genomics.tools._lib.resolve import (  # noqa: F401
    list_resources,
    resolve_annotation,
    resolve_reference,
    resolve_sample,
)

__all__ = [
    "cache",
    "index",
    "operations",
    "pipeline",
    "resolve",
    "resources",
    "cache_entry",
    "index_entry",
    "checksum",
    "download",
    "index_op",
    "status",
    "validate",
    "align_reads",
    "annotate",
    "call_variants",
    "cohort_analytics",
    "ingest_reference",
    "joint_genotype",
    "normalize_filter",
    "publish",
    "qc_reads",
    "ANNOTATION_ALIASES",
    "CACHE_BASE",
    "INDEX_REGISTRY",
    "REFERENCE_ALIASES",
    "RESOURCE_REGISTRY",
    "list_resources",
    "resolve_annotation",
    "resolve_reference",
    "resolve_sample",
]
