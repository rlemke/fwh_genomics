# Aligner Index Caches

**Namespaces:** `genomics.cache.index.bwa` · `genomics.cache.index.star` ·
`genomics.cache.index.bowtie2` ·
**FFL:** `src/genomics/ffl/genomics_index_cache.ffl` ·
**Handlers:** `src/genomics/handlers/index_handlers.py` (factory-built) ·
**Simulators:** `src/genomics/tools/_lib/index.py`, `src/genomics/tools/_lib/resources.py` ·
**Tests:** `test_handler_dispatch_genomics.py::TestGenomicsIndexHandlers`

## Overview

Aligners can't map reads against a raw FASTA — they need a pre-built index (BWT /
suffix array / STAR genome dir). This feature is the **derived-artifact** layer:
given a cached reference genome, build (simulate) the aligner-specific index for
it. It is analogous to the OSM example's GraphHopper/Valhalla graph caches — a
second cache tier derived from the primary download.

Each `(aligner, reference)` pair is its own **event facet**, e.g.
`genomics.cache.index.bwa.GRCh38`, factory-built from a small registry.

## How it works

`INDEX_REGISTRY` in `tools/_lib/resources.py` maps each index namespace to the
reference names it supports:

```
genomics.cache.index.bwa      -> [GRCh38, GRCh37, T2TCHM13, Hg19, GRCm39]
genomics.cache.index.star     -> [GRCh38, GRCh37, T2TCHM13]
genomics.cache.index.bowtie2  -> [GRCh38, GRCh37]
```

`index_handlers._build_dispatch()` walks it, derives the aligner from the last
namespace segment (`namespace.rsplit(".",1)[-1]`), and registers
`<namespace>.<reference>` → a closure that returns
`{"index": index_entry(aligner, reference, source_path)}`. `source_path` is taken
from the upstream `cache.path` in the payload when chaining off a cache step, else
defaults to the canonical `/cache/reference/<ref>/<ref>.fa.gz`.

`tools/_lib/index.py::index_entry` sizes the index from two lookup tables in
`resources.py`: `REFERENCE_CONTIGS` (per-reference `(contig_count, total_bases)`,
e.g. `GRCh38 → (195, 3_088_286_401)`) and `ALIGNER_SIZE_MULTIPLIERS`
(`bwa 1.5×`, `star 10×`, `bowtie2 1.2×` over a 3 GB base) plus `ALIGNER_VERSIONS`
(`bwa-mem2-2.2.1`, `STAR-2.7.11b`, `bowtie2-2.5.3`). The dispatch table is verified
at **10** entries by the test (5 bwa + 3 star + 2 bowtie2).

## Fan-out

**Single-task per (aligner, reference) pair — no fan-out.** One index build per
facet call; no `foreach`.

## Data & fields

Output schema `IndexCache` (`genomics.cache.types`): source_path, index_dir,
aligner, date, size, wasInCache, version, contig_count, total_bases.

`index_dir` is formatted as `/cache/index/<aligner>/<reference>/`. `size` is
`int(3_000_000_000 × multiplier)`; `contig_count`/`total_bases` come straight from
`REFERENCE_CONTIGS` (0/0 for an unknown reference — a silent fallback, see
Gotchas).

## External libraries / binaries

**None.** No `bwa index`, `STAR --runMode genomeGenerate`, or `bowtie2-build` is
run. `bwa-mem2` / `STAR` / `bowtie2` appear only as simulated `version` strings.

## Facets & workflows

10 **event facets**, all with `Effect(kind="external")`, `Cost(tier="expensive")`,
`Timeout(minutes=180)`:

| Facet | Signature | Notes |
|---|---|---|
| `genomics.cache.index.bwa.<Ref>` | `(cache: GenomicsCache, recreate: Boolean = false) => (index: IndexCache)` | BWA-MEM2, all 5 references |
| `genomics.cache.index.star.<Ref>` | `(cache: GenomicsCache, annotation: GenomicsCache, recreate: Boolean = false) => (index: IndexCache)` | RNA-seq, splice-aware — **takes an extra `annotation` param** (needs a GTF) |
| `genomics.cache.index.bowtie2.<Ref>` | `(cache: GenomicsCache, recreate: Boolean = false) => (index: IndexCache)` | short-read, 2 references |

All are factory-built in `index_handlers.py`; none ship a dedicated CLI (the
generic `index.sh` / `genomics.cache.Operations.Index` covers ad-hoc index builds —
see [cache-operations](cache-operations.md)).

## Cache / output

No bytes written. Output is the in-memory `IndexCache` dict; `index_dir` and
`source_path` are formatted strings; `wasInCache` is always `True`.

## Gotchas & notes

- **STAR needs an annotation; BWA/Bowtie2 don't.** The STAR facets carry a second
  `annotation: GenomicsCache` param — pass a GTF-bearing cache entry (e.g. from
  `ResolveAnnotation("gencode")`). BWA/Bowtie2 facets take only the reference cache.
- **The factory handler ignores `recreate` and `annotation`.** The closure only
  reads `cache.path` for `source_path`; the `recreate` flag and STAR's `annotation`
  input are declared in FFL but not consumed by the simulator.
- **Unknown reference → zero contigs.** `index_entry` falls back to `(0, 0)` if the
  reference isn't in `REFERENCE_CONTIGS`, silently. Only the references listed in
  `INDEX_REGISTRY` have real contig data, so in practice this can't happen through
  the factory-built facets, but a direct `index_entry(...)` call with an unknown
  name would.
- **Generic vs per-pair index:** `genomics.cache.Operations.Index(cache, aligner)`
  ([cache-operations](cache-operations.md)) builds an index for an arbitrary
  aligner string via `tools/_lib/operations.py::index`, whereas these facets are
  the pre-enumerated `(aligner, reference)` catalog entries.

## Related specs

- [resource-cache](resource-cache.md) — the reference downloads these indexes
  derive from.
- [cache-operations](cache-operations.md) — the generic `Index` op.
- [composed-workflows](composed-workflows.md) — `PrepareReference` chains
  resolve → `Index`.
