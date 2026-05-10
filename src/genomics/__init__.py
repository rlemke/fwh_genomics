"""Genomics cohort analysis example package — Facetwork workflows +
handlers that simulate a complete germline variant-calling pipeline.

The example showcases:

- `foreach` fan-out (per-sample processing) and linear fan-in (cohort analysis)
- Factory-built handlers from a resource registry (250+ cache entries
  for reference genomes, annotation tracks, and example samples)
- Composed facets: `ProcessSample` (QC → Align → CallVariants) and
  `AnalyzeCohort` (joint genotyping → normalization → annotation → analytics)
- 18 simulator handlers across genomics.Facets, genomics.cache.*,
  genomics.cache.Operations, and genomics.cache.Resolve

Discovered by the Facetwork runner via the ``facetwork.examples`` entry
point declared in ``pyproject.toml``::

    [project.entry-points."facetwork.examples"]
    genomics = "genomics:example"

Once ``pip install -e .`` has been run from this repository, Facetwork's
``scripts/start-runner --example genomics`` and ``scripts/seed-examples``
will pick this package up automatically.
"""

from __future__ import annotations

from pathlib import Path

from facetwork.examples import ExamplePackage

from .handlers import register_all_registry_handlers

example = ExamplePackage(
    name="genomics",
    ffl_dir=Path(__file__).parent / "ffl",
    register_handlers=register_all_registry_handlers,
)
