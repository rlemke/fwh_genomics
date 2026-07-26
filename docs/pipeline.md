# Cohort Variant-Calling Pipeline

**Namespaces:** `genomics.types` (schemas) · `genomics.Facets` (event facets) ·
`genomics.pipeline` (workflows) ·
**FFL:** `src/genomics/ffl/genomics.ffl` ·
**Handlers:** `src/genomics/handlers/genomics_handlers.py` ·
**Simulators:** `src/genomics/tools/_lib/pipeline.py` ·
**CLIs:** `src/genomics/tools/{ingest-reference,qc-reads,align-reads,call-variants,joint-genotype,normalize-filter,annotate,cohort-analytics,publish}.sh` ·
**Tests:** `tests/mocked/py/test_cohort_analysis.py`

## Overview

This is the **flagship feature** and the reason the package exists: a simulated
**germline variant-calling pipeline** over a cohort of samples, expressed as two
complementary FFL workflow shapes.

- **`SamplePipeline`** — the per-sample **`foreach` fan-out**: for each sample in a
  batch, run QC → align → call variants, in parallel, yielding one gVCF per sample.
- **`CohortAnalysis`** — the cohort **linear fan-in**: ingest the reference, joint-
  genotype the per-sample gVCFs into one cohort VCF, then normalize/filter →
  annotate → compute statistics → publish a deliverable package.

Together they model the standard GATK-style germline workflow (single-sample HaplotypeCaller
in gVCF mode, then joint genotyping across the cohort). Every step here is a
**deterministic simulator** — no fastp / bwa-mem2 / GATK / bcftools / VEP is
actually invoked — so the whole thing runs offline with realistic output shapes.

## How it works

Data flow across the two workflows:

```
per sample:   FASTQ (r1,r2) --QcReads--> clean FASTQ --AlignReads--> sorted BAM --CallVariants--> gVCF
cohort:       gVCF dir --JointGenotype--> cohort VCF --NormalizeFilter--> filtered VCF
              --Annotate--> variant table --CohortAnalytics--> stats --Publish--> package
```

Each `genomics.Facets.*` step is served by `genomics_handlers.py`, whose handlers
are thin `payload → pure-function` adapters. The pure functions live in
`tools/_lib/pipeline.py` (`qc_reads`, `align_reads`, `call_variants`,
`ingest_reference`, `joint_genotype`, `normalize_filter`, `annotate`,
`cohort_analytics`, `publish`) and are reached through the
`handlers/shared/genomics_utils.py` shim. The **same** `_lib` functions back the
`*.sh` CLIs, so the shell surface and the FFL surface never drift in
implementation (they do differ in output shape for the cohort steps — see
Gotchas). Each handler wraps the inner dict as `{"result": …}` to match the FFL
`=> (result: …)` return clause.

`RegistryRunner` dispatch is name-keyed: `genomics_handlers._DISPATCH` maps all
nine `genomics.Facets.<Name>` qualified names to their handler (verified at 9
entries by `test_handler_dispatch_genomics.py::TestGenomicsHandlers`).

## Fan-out

**`SamplePipeline` fans out per sample.** Its body is
`andThen foreach sample in $.samples { qc → aligned → called; yield … }` — the
runtime materializes one parallel sub-block per element of the `samples: Json`
array, each running the three sequential event steps (QC → Align → CallVariants).
This is the canonical `foreach` fan-out pattern: with N samples the QC/align/call
work runs across N fleet runners instead of serially, and per-sample failures are
isolated to their sub-block. `test_cohort_analysis.py` drives 4 samples (NA12878,
NA12891, NA12892, HG00096 — a CEU/GBR trio-plus) and asserts 4 distinct sample
sub-blocks complete.

**`CohortAnalysis` is single-task / linear — no fan-out.** Joint genotyping is a
fan-**in**: it must see all per-sample gVCFs at once, so the six cohort steps run
as one sequential `andThen` block. The two workflows compose: `SamplePipeline`'s
gVCFs feed `CohortAnalysis`'s `gvcf_dir`.

## Data & fields

Schemas are declared in `namespace genomics.types` (`src/genomics/ffl/genomics.ffl`):

| Schema | Key fields |
|---|---|
| `QcReport` | sample_id, total_reads, passed_reads, failed_reads, pass_rate, clean_fastq_path, tool_version |
| `AlignmentResult` | sample_id, bam_path, total_reads, mapped_reads, mapping_rate, duplicate_rate, mean_coverage |
| `VariantResult` | sample_id, gvcf_path, variant_count, snp_count, indel_count |
| `ReferenceBundle` | fasta_path, annotation_path, build, size_bytes |
| `CohortVariantResult` | cohort_vcf_path, filtered_vcf_path, sample_count, variant_count, pass_rate |
| `AnnotationResult` | variant_table_path, variant_count, annotated_count, gene_count |
| `CohortStatsResult` | qc_report_path, stats_path, sample_count, mean_depth, variant_count |
| `AnalysisPackage` | package_path, manifest_path, dataset_id, sample_count, variant_count, build |

The simulator emits realistic constants — `qc_reads` returns 1e9 total reads at a
97% pass rate and `fastp-0.23.4`; `call_variants` returns ~4.8M variants
(4.2M SNP / 0.6M indel) and `gatk-4.5`; `ingest_reference` returns a
3.2 GB `GRCh38` bundle. These are fixed illustrative values, not computed from any
input file.

## External libraries / binaries

**None invoked.** The pipeline is pure Python stdlib. The real tools it *models* —
**fastp** (QC), **bwa-mem2** (align), **GATK 4.5** HaplotypeCaller/GenotypeGVCFs
(call + joint genotype), **bcftools 1.18** (normalize/filter), **VEP 110**
(annotate) — appear only as simulated `tool_version` strings in the returned dicts.
Nothing shells out; there is no binary or heavyweight pip dependency in this
feature (the package's only runtime deps are `facetwork` and `PyYAML`, per
`pyproject.toml`).

Despite that, every facet is tagged as if it were the real thing (see below), so
the capability index and cost-aware composition behave as they would in a real
deployment.

## Facets & workflows

All nine are **event facets** in `genomics.Facets` (each needs a handler); every
one carries `Effect`/`Cost` mixins and most a long `Timeout`:

| Facet | Effect / Cost | Timeout | Purpose (from FFL docstring) |
|---|---|---|---|
| `IngestReference(reference_build)` | external / expensive | 180 min | Download + index a reference genome for a build |
| `QcReads(sample_id, r1_uri, r2_uri)` | io / moderate | 30 min | Trim adapters, filter low-quality paired-end reads |
| `AlignReads(sample_id, clean_fastq_path, reference_build)` | external / expensive | 240 min | Align cleaned reads → sorted BAM |
| `CallVariants(sample_id, bam_path, reference_build)` | external / expensive | 240 min | Haplotype-based single-sample variant calling |
| `JointGenotype(gvcf_dir, reference_build, sample_count)` | external / expensive | 240 min | Merge per-sample gVCFs → joint cohort VCF |
| `NormalizeFilter(vcf_path, reference_build)` | external / moderate | 60 min | Left-align, decompose, quality-filter variants |
| `Annotate(vcf_path, annotation_path)` | external / expensive | 120 min | Gene / consequence / population-frequency annotation |
| `CohortAnalytics(variant_table_path, dataset_id)` | io / moderate | 30 min | Summary stats + QC across the cohort |
| `Publish(variant_table_path, qc_report_path, stats_path, dataset_id)` | io / moderate | — | Package variants + QC + stats for delivery |

Workflows (both `entry_point: true` in `catalog.yaml`, **FFL-only**, no handler —
they orchestrate the facets above):

- `SamplePipeline(samples: Json, reference_build = "GRCh38") => (gvcf_path, sample_id, variant_count)`
- `CohortAnalysis(dataset_id, reference_build = "GRCh38", gvcf_dir) => (package_path, cohort_vcf_path, variant_table_path, total_variants, sample_count)`

## Cache / output

No files are written. Each handler returns an in-memory JSON dict matching its
schema; the `*_path` fields (`/fastq/<id>/…`, `/bam/<id>/…`, `/vcf/<id>/…`,
`/publish/<dataset>/package.tar.gz`) are **formatted strings**, not real
artifacts. In a live deployment these would land on the durable storage backend
(`FW_STORAGE` / MinIO / S3), but this simulator only produces the metadata shape.

## Gotchas & notes

- **Cohort-stage simulator output does NOT match the FFL cohort schemas.** The
  per-sample simulators (`qc_reads`, `align_reads`, `call_variants`,
  `ingest_reference`) return keys that line up with `QcReport` / `AlignmentResult`
  / `VariantResult` / `ReferenceBundle`. The cohort-stage simulators do **not**:
  `joint_genotype` returns `joint_vcf_path` (schema wants `cohort_vcf_path`), omits
  `filtered_vcf_path`/`pass_rate`, and reads `payload["cohort_id"]` — but the FFL
  `JointGenotype` passes `gvcf_dir`/`reference_build`/`sample_count`, no
  `cohort_id`, so it defaults to `"unknown"`. Likewise `normalize_filter` /
  `annotate` / `cohort_analytics` / `publish` return illustrative shapes
  (`input_vcf`/`output_vcf`, `high_impact`, `ancestry_groups`, `published_path`, …)
  that don't populate the declared cohort schema fields. The end-to-end tests
  paper over this by substituting **inline** schema-correct mock handlers
  (`test_cohort_analysis.py::MOCK_HANDLERS`) rather than calling the `_lib`
  functions. Treat the cohort `_lib` functions as CLI demos, not schema-faithful
  runtime handlers.
- **`sample_count = 4` is hard-coded** in the `CohortAnalysis` FFL body's
  `JointGenotype` call — the workflow does not derive the cohort size from the
  gVCF directory.
- **Entry-point drift:** `README.md` / `CLAUDE.md` say the package registers via
  `facetwork.examples`, but `pyproject.toml` actually declares the
  `facetwork.domains` entry point (`genomics = "genomics:domain"`) and
  `__init__.py` exports `domain = DomainPackage(...)`. It is discovered as a
  **domain**, not an example.

## Related specs

- [resource-resolution](resource-resolution.md) — turns friendly names
  ("hg38", "dbsnp", an SRA accession) into the cache entries these steps consume.
- [resource-cache](resource-cache.md) / [aligner-indexes](aligner-indexes.md) —
  the reference/annotation/read downloads and aligner indexes the pipeline aligns
  against.
- [composed-workflows](composed-workflows.md) — `CachedCohortAnalysis` wraps this
  pipeline with automatic resolve + cache + index.
