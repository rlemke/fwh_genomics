"""Simulator implementation for the genomics example.

Each module here is a pure-function library that the CLIs in
``src/genomics/tools/*.py`` and the FFL handlers in
``src/genomics/handlers/`` both call into via the
``handlers/shared/genomics_utils.py`` shim. None of these modules
touch ``facetwork.runtime`` or MongoDB.

Modules:

- ``pipeline``    — 9 per-sample / cohort pipeline simulators (QC, Align, CallVariants, …)
- ``operations``  — 5 cache-operation simulators (Download, Index, Validate, Status, Checksum)
- ``resources``   — ``RESOURCE_REGISTRY`` data (reference genomes, annotations, samples)
- ``cache``       — factory that builds cache handlers from the registry
- ``resolve``     — name-based resolvers over the registry
"""
