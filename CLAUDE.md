# CLAUDE.md — genomics

This repository is a **standalone Facetwork example package**. The Facetwork
platform (workflow compiler + runtime) lives at
`/Users/ralph_lemke/facetwork`; this repo only contains the genomics-specific
FFL, handlers, and tools. The two are wired together via the
`facetwork.examples` entry point in `pyproject.toml`.

## Quick orientation

```
fwh_genomics/
├── pyproject.toml                       # declares the facetwork.examples entry point
├── src/genomics/__init__.py             # exports `example: ExamplePackage`
├── src/genomics/handlers/               # 5 modules + shared/ shim
├── src/genomics/ffl/                    # 7 FFL files
├── src/genomics/tools/                  # CLI utilities + _lib/ (simulators)
├── tests/                               # mocked + real test trees
└── agent-spec/                          # cross-cutting design specs
```

## Common operations

```bash
# Register this package with Facetwork's runner
pip install -e .

# From a Facetwork checkout:
scripts/seed-examples --include genomics
scripts/start-runner --example genomics -- --log-format text

# Run as a standalone agent
PYTHONPATH=src python agent.py

# CLIs — every pipeline facet has one, all backed by tools/_lib/
src/genomics/tools/qc-reads.sh --sample-id NA12878
src/genomics/tools/align-reads.sh --sample-id NA12878
src/genomics/tools/call-variants.sh --sample-id NA12878
src/genomics/tools/joint-genotype.sh --cohort-id ashkenazi-trio
src/genomics/tools/cohort-analytics.sh --cohort-id ashkenazi-trio
src/genomics/tools/download.sh --resource grch38
src/genomics/tools/index.sh --aligner bwa --resource grch38

# Tests
pytest tests/ src/genomics/handlers/ -v
```

## Key concepts

### Tools / handlers / _lib pattern

Every facet has two surfaces — a CLI under `src/genomics/tools/` and an
FFL handler under `src/genomics/handlers/` — and both call into the
**same** simulator implementation in `src/genomics/tools/_lib/`. The
shim at `src/genomics/handlers/shared/genomics_utils.py` re-exports the
`_lib` modules via the **fully-qualified** package path
(`from genomics.tools._lib.pipeline import …`) so this package
coexists cleanly with sibling Facetwork example packages on
`sys.modules`.

```
                       ┌─────────────────────────────┐
   CLI tool ───────────┤                             │
                       │   tools/_lib/<domain>.py    │ ← single source of truth
   FFL handler ────────┤   (deterministic simulator) │
   (via shared shim)   │                             │
                       └─────────────────────────────┘
```

### Handler / domain map

| Module | Domain (FFL namespace) | Facets |
|--------|----------------------|--------|
| `genomics_handlers.py` | `genomics.Facets` | IngestReference, QcReads, AlignReads, CallVariants, JointGenotype, NormalizeFilter, Annotate, CohortAnalytics, Publish |
| `operations_handlers.py` | `genomics.cache.Operations` | Download, Index, Validate, Status, Checksum |
| `resolve_handlers.py` | `genomics.cache.Resolve` | ResolveReference, ResolveAnnotation, ResolveSample, ListResources |
| `cache_handlers.py` | `genomics.cache.<aligner>.*` | Factory-built handlers from `RESOURCE_REGISTRY` (one per cached resource) |
| `index_handlers.py` | `genomics.cache.Index.<aligner>` | Factory-built index handlers per aligner (`bwa`, `bowtie2`, `star`, …) |

### Resource registry

The `RESOURCE_REGISTRY` in `tools/_lib/resources.py` is the source of truth
for the cached genomics resources (reference genomes, annotation tracks,
example samples). Both `cache_handlers.py` and `resolve_handlers.py`
walk this registry; the factory pattern means adding a new entry
(`{ "name": "...", "url": "...", "size": ... }`) automatically yields
a registered handler for it.

## Adding new facets

1. Add a simulator function to the right `tools/_lib/<domain>.py`
   (`pipeline.py` for per-sample / cohort steps; `operations.py` for
   small cache ops; or extend `resources.py` for new cached entries).
2. Re-export the simulator from
   `src/genomics/handlers/shared/genomics_utils.py`.
3. Add a CLI wrapper at `src/genomics/tools/<verb>-<noun>.py` (and a
   thin `<verb>-<noun>.sh` for ergonomics).
4. Add a handler to the right `handlers/<name>_handlers.py` and wire
   it into `_DISPATCH`.
5. Drop the FFL declaration into `src/genomics/ffl/`.
6. Re-run `scripts/seed-examples --include genomics` so the new flow
   shows up in the dashboard.

## Code review checklist

- For every state transition: "what if this crashes halfway?" Design the recovery path.
- For every retry: max count and backoff. No infinite loops.
- For every error handler: never silently return empty defaults. Fail explicitly or re-raise.
- Keep `_lib/` free of `facetwork.runtime` so CLIs stay runnable standalone.
- Resources added to `RESOURCE_REGISTRY` automatically wire handlers — make sure new names don't collide with existing facets.
