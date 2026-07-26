# Resource Cache — Reference / Annotation / SRA Downloads

**Namespaces:** `genomics.cache.reference` · `genomics.cache.annotation` ·
`genomics.cache.sra` · `genomics.cache.types` (schemas) ·
**FFL:** `src/genomics/ffl/genomics_cache.ffl`, `src/genomics/ffl/genomics_cache_types.ffl` ·
**Handlers:** `src/genomics/handlers/cache_handlers.py` (factory-built) ·
**Simulators:** `src/genomics/tools/_lib/cache.py`, `src/genomics/tools/_lib/resources.py` ·
**Tests:** `tests/mocked/py/test_cache_pipeline.py`, `test_handler_dispatch_genomics.py`

## Overview

The download/cache layer answers "get me the *bytes* a pipeline needs": reference
genome FASTAs, variant-annotation databases, and SRA read archives. It is the
genomics analogue of the OSM example's PBF/Geofabrik cache — a fixed catalog of
named resources, each with a real upstream URL and a simulated on-disk cache
record.

Each resource is exposed as its own zero-argument **event facet** (e.g.
`genomics.cache.reference.GRCh38`, `genomics.cache.annotation.ClinVar`,
`genomics.cache.sra.SRR622461`). These are **factory-built** from a single
registry table, so the catalog is data, not hand-written handlers.

## How it works

`RESOURCE_REGISTRY` in `tools/_lib/resources.py` is the source of truth: a nested
dict `namespace → {facet_name → (url, path, size_bytes, resource_type)}`.
`cache_handlers._build_dispatch()` walks it once at import time and, for every
entry, registers `<namespace>.<facet_name>` → a closure from `_make_handler(...)`.
The closure returns `{"cache": cache_entry(url, path, size, resource_type)}`, where
`tools/_lib/cache.py::cache_entry` stamps a `GenomicsCache` record (adds today's
`date`, `wasInCache=True`, a `sha256:<hex>` `checksum` derived from the path hash).

Because dispatch is factory-built, **adding a row to `RESOURCE_REGISTRY`
automatically yields a registered facet** — no new handler code. The dispatch
table is verified at 17 entries by
`test_handler_dispatch_genomics.py::TestGenomicsCacheHandlers`.

## Fan-out

**Single-task per resource — no fan-out inside this namespace.** There is no
`foreach`; each download facet is one atomic lookup. Fleet parallelism comes from
higher workflows fanning many `PrepareSample` / `SamplePipeline` runs across
runners, not from anything here.

## Data & fields

Registry contents (namespace → facets), from `resources.py`:

- **`genomics.cache.reference`** (5): `GRCh38`, `GRCh37`, `T2TCHM13`, `Hg19`,
  `GRCm39` — real NCBI/UCSC/T2T FASTA URLs, ~2.7–3.2 GB, `resource_type="reference"`.
- **`genomics.cache.annotation`** (7): `DbSNP156`, `DbSNP155`, `ClinVar`,
  `GnomAD4`, `GnomAD3`, `VepCache112`, `Gencode46` — real NCBI / gnomAD (GCS) /
  Ensembl / EBI URLs, 50 MB–450 GB, `resource_type="annotation"`.
- **`genomics.cache.sra`** (5): `SRR622461`, `SRR622458`, `SRR622459`,
  `ERR009378`, `SRR13604789` — 1000 Genomes samples on the SRA S3 mirror,
  18–30 GB, `resource_type="sra"`.

Output schema `GenomicsCache` (`genomics.cache.types`): url, path, date, size,
wasInCache, checksum, resource_type.

The `path` is formatted under `CACHE_BASE` = `FW_GENOMICS_CACHE_DIR` (default
`/cache`), e.g. `/cache/reference/GRCh38/GRCh38.fa.gz`. `CACHE_BASE` also accepts
`hdfs://` URIs per the module comment.

## External libraries / binaries

**None.** `cache_entry` uses only `datetime` + the builtin `hash()`; no HTTP
client, no download, no checksum of real bytes. The URLs are genuine upstreams but
are never fetched. Only runtime deps are `facetwork` + `PyYAML`.

## Facets & workflows

17 zero-arg **event facets**, all `() => (cache: GenomicsCache)` with
`Effect(kind="external")`, `Cost(tier="expensive")`, `Timeout(minutes=120)` (the
real thing would be a large network download). Examples with their FFL docstrings:

| Facet | Models |
|---|---|
| `genomics.cache.reference.GRCh38()` | GRCh38 (hg38) primary human reference |
| `genomics.cache.reference.T2TCHM13()` | T2T-CHM13 telomere-to-telomere reference |
| `genomics.cache.annotation.DbSNP156()` | dbSNP build 156 variant IDs |
| `genomics.cache.annotation.ClinVar()` | ClinVar clinical-significance DB |
| `genomics.cache.annotation.GnomAD4()` | gnomAD v4 population allele frequencies |
| `genomics.cache.sra.SRR622461()` | 1000 Genomes high-coverage WGS sample |

These per-entry facets are served **only** by the factory in `cache_handlers.py`;
they ship **no individual CLI** (there is no parameter to vary) — inspect them via
`resolve.sh --list` or `resolve.sh --reference GRCh38`. See
[resource-resolution](resource-resolution.md).

## Cache / output

No bytes are downloaded or written. The output is the in-memory `GenomicsCache`
dict. `wasInCache` is unconditionally `True`; the `checksum` is a deterministic
hash of the path string, not of any file. `CACHE_BASE` only shapes the `path`
field. The canonical (aspirational) on-disk contract — per-entry sidecars,
staging-then-rename, mirror-source paths — is documented in
`agent-spec/cache-layout.agent-spec.yaml`, but this simulator does not implement
it.

## Gotchas & notes

- **Facet names are CamelCase, aliases are lowercase.** The facet is
  `genomics.cache.annotation.DbSNP156`; users type `dbsnp` / `dbsnp156`. That
  mapping lives in the resolver, not here — see
  [resource-resolution](resource-resolution.md).
- **`resource_type` is the category key** (`reference` / `annotation` / `sra`) used
  by `ListResources` filtering and by `ResolveSample`/`ResolveAnnotation` category
  routing.
- **README count drift:** the repo README says "250+ factory-built handlers"; the
  registry actually defines **17** cache download facets (plus 10 index facets —
  see [aligner-indexes](aligner-indexes.md)). The "factory" claim is real; the
  count is aspirational.

## Related specs

- [resource-resolution](resource-resolution.md) — name/accession/alias → these
  registry entries.
- [aligner-indexes](aligner-indexes.md) — the derived index caches built from these
  reference downloads.
- [cache-operations](cache-operations.md) — the generic Download/Validate/Status
  ops over a `GenomicsCache`.
- [pipeline](pipeline.md) — the consumer of resolved references + annotations.
