# Composed Cache-Aware Workflows

**Namespace:** `genomics.cache.workflows` ·
**FFL:** `src/genomics/ffl/genomics_cache_workflows.ffl` ·
**Handlers:** none — FFL-only composition ·
**Tests:** `tests/mocked/py/test_cache_pipeline.py`

## Overview

The lower-level features (resolve, cache, index, pipeline) are building blocks;
this namespace is where they compose into **one-call, cache-aware entry points**.
Instead of "resolve hg38, then download it, then index it, then run the pipeline"
as four separate submissions, `CachedCohortAnalysis` runs it end-to-end from names
alone. These are the workflows a caller (or `fw_catalog_match`) should reach for
first.

## How it works

Three workflows, all defined purely in FFL as `andThen` blocks that wire together
facets from other namespaces — there are **no handlers** in this namespace; the
runtime dispatches each referenced facet to its own handler.

- **`PrepareReference(reference_name, aligner = "bwa")`** — `ResolveReference` →
  `Index`, yielding the resolved `GenomicsCache` + the built `IndexCache`. The "get
  a reference ready to align against" block.
- **`PrepareSample(accession, sample_id = "")`** — `ResolveSample` → `Download`,
  yielding the staged sample cache + its resolution. The "fetch a sample's reads by
  accession" block feeding `SamplePipeline`.
- **`CachedCohortAnalysis(dataset_id, reference_name = "hg38", accessions: Json)`** —
  the full end-to-end: `ResolveReference` + `ResolveAnnotation` → `Index` →
  `JointGenotype` → `NormalizeFilter` → `Annotate` → `CohortAnalytics` → `Publish`.
  It is `CohortAnalysis` ([pipeline](pipeline.md)) with automatic resource
  resolution and caching folded in — the preferred "analyze a cohort by name"
  entry point.

## Fan-out

**Linear `andThen` — no `foreach` fan-out in these three.** They chain single
steps. The fan-out lives one layer down in `SamplePipeline`
([pipeline](pipeline.md)); these compose the fan-**in** cohort side plus resource
prep. (`PrepareSample` is the per-accession block you would drive once per sample
to stage reads before the fan-out.)

## Data & fields

Consumes/produces the shared cache + pipeline schemas: `GenomicsCache`,
`IndexCache`, `ResourceResolution` (`genomics.cache.types`) and the cohort outputs
of the pipeline facets. Workflow outputs:

- `PrepareReference => (cache: GenomicsCache, index: IndexCache)`
- `PrepareSample => (cache: GenomicsCache, resolution: ResourceResolution)`
- `CachedCohortAnalysis => (package_path: String, variant_count: Long, sample_count: Long)`

## External libraries / binaries

**None** — composition only; the referenced facets are the (simulated) workers.

## Facets & workflows

All three are **workflows** (`entry_point: true` in `catalog.yaml`), no `Effect`/
`Cost` mixins (mixins live on the leaf event facets they call). They reference
facets across four namespaces: `genomics.cache.Resolve.*`,
`genomics.cache.Operations.*`, and `genomics.Facets.*`.

`CachedCohortAnalysis` hard-codes `ResolveAnnotation(name = "dbsnp")`,
`Index(aligner = "bwa")`, `gvcf_dir = "/gvcf/cohort/"`, and `sample_count = 4` in
the FFL body — the `accessions` parameter is declared but not consumed by the body
(the gVCF directory is fixed, not derived from the accessions).

## Cache / output

Whatever the composed leaf facets emit — in this simulator, in-memory dicts. No
files written.

## Gotchas & notes

- **FFL-only: no handler module.** Nothing under `src/genomics/handlers/` registers
  these; they exist solely as compiled workflow ASTs. The runtime executes them by
  dispatching each inner facet to its handler.
- **`CachedCohortAnalysis` ignores `accessions`.** The parameter is part of the
  signature (and `test_cache_pipeline.py` passes four accessions), but the body
  reads from the fixed `gvcf_dir = "/gvcf/cohort/"` — it does not resolve or
  download the accessions. It models the cohort *fan-in* assuming per-sample gVCFs
  already exist; pair it with `PrepareSample` + `SamplePipeline` for the real
  upstream.
- **Uses the generic `Operations.Index`, not the per-pair index facets** — so it
  works for any resolved reference without a pre-enumerated
  `genomics.cache.index.*` entry.
- **Reference build passed by matched name.** `JointGenotype`/`NormalizeFilter`
  receive `ref.resolution.matched_name` (e.g. `GRCh38`), i.e. the canonical name
  from the resolver, not the user's alias (`hg38`).

## Related specs

- [pipeline](pipeline.md) — the per-sample fan-out + cohort fan-in these wrap.
- [resource-resolution](resource-resolution.md) — the resolve step each begins with.
- [resource-cache](resource-cache.md) · [aligner-indexes](aligner-indexes.md) ·
  [cache-operations](cache-operations.md) — the cache/index/download blocks they
  compose.
