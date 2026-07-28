# Genomics — Feature Specifications

This directory holds one **spec per genomics feature**. Each document follows a
common shape ([`SPEC_TEMPLATE.md`](SPEC_TEMPLATE.md)) and states, for that feature:
how it works, whether and how it **fans out** across the fleet, the **schemas &
registry data** it produces or reads, the **external libraries/binaries** it relies
on (this package is a deterministic *simulator*, so mostly none), its **facets &
workflows**, and its **cache/output**. Claims are grounded in the FFL `/** … */`
docstrings, the handler code, and the `tools/_lib/` simulators — the source of
truth for each facet remains its FFL docstring; these specs are the feature-level
narrative over them.

**Start here:** [**Pipeline**](pipeline.md) — the flagship feature: the two-shape
germline cohort variant-calling pipeline (`SamplePipeline` `foreach` fan-out +
`CohortAnalysis` fan-in) that the whole package exists to demonstrate.

## Core pipeline

| Spec | What it covers |
|------|----------------|
| [pipeline.md](pipeline.md) | **Flagship.** Per-sample `foreach` fan-out (QC → Align → CallVariants) + cohort linear fan-in (IngestReference → JointGenotype → NormalizeFilter → Annotate → CohortAnalytics → Publish); the 9 `genomics.Facets` event facets and the `genomics.types` schemas. |

## Resource cache & resolution

| Spec | What it covers |
|------|----------------|
| [resource-cache.md](resource-cache.md) | Reference / annotation / SRA downloads — 17 factory-built per-entry facets from `RESOURCE_REGISTRY` (`GRCh38`, `dbSNP156`, `SRR622461`, …). |
| [aligner-indexes.md](aligner-indexes.md) | Derived aligner index caches (`bwa` / `star` / `bowtie2`) — 10 factory-built `(aligner, reference)` facets, sized from `REFERENCE_CONTIGS`. |
| [cache-operations.md](cache-operations.md) | The generic verbs over a `GenomicsCache`: Download / Index / Validate / Status / Checksum (+ the `Data` config facets). |
| [resource-resolution.md](resource-resolution.md) | Friendly name / alias / accession → canonical cache entry (`ResolveReference/Annotation/Sample`, `ListResources`); the only truly `pure` facets. |

## Composition

| Spec | What it covers |
|------|----------------|
| [composed-workflows.md](composed-workflows.md) | FFL-only cache-aware entry points: `PrepareReference`, `PrepareSample`, and `CachedCohortAnalysis` (resolve + cache + index + full cohort analysis in one call). |
| [ffl-examples.md](ffl-examples.md) | **Usage patterns.** A gallery of complete, compile-checked FFL examples over these facets — per-sample chain, cohort `foreach` fan-out + joint-genotype fan-in, cache warming, `when` QC gates, `catch`, long-run `Timeout` overrides. |

---

*See also the machine-readable composability manifest at
[`src/genomics/catalog.yaml`](../src/genomics/catalog.yaml) (workflows + facets by
intent, with effect/cost), the repo [`CLAUDE.md`](../CLAUDE.md) (domain contract +
handler/domain map), the [`USER_GUIDE.md`](../USER_GUIDE.md), and the tools map in
[`src/genomics/tools/README.md`](../src/genomics/tools/README.md). The
live/queryable interface is the MCP `fw_capabilities` / `fw_catalog_search` /
`fw_describe_handler` tools.*
