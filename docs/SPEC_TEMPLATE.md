<!-- SPEC TEMPLATE — every docs/<feature>.md follows this shape so the set reads
consistently. Delete this comment in real specs. Keep sections in this order;
omit a section only if it genuinely does not apply (say so in one line rather
than dropping the heading silently). Ground every claim in the actual FFL
docstrings / handler code / tools — do not invent behaviour. This package is a
deterministic SIMULATOR: no fastp / bwa / GATK / VEP actually run, so "External
libraries / binaries" is usually about what the step *models*, not what it
shells out to. -->

# <Feature Name>

**Namespace(s):** `genomics.<ns>` · **FFL:** `src/genomics/ffl/<file>.ffl` ·
**Handlers:** `src/genomics/handlers/<name>_handlers.py` ·
**Simulators:** `src/genomics/tools/_lib/<name>.py` · **CLIs:** `src/genomics/tools/<verb>-<noun>.sh` (if any)

## Overview
One or two paragraphs: what this feature is for, the request it answers, and where
it sits in the pipeline (resolve → cache → per-sample → cohort fan-in → publish).

## How it works
The algorithm / data flow, step by step. Name the concrete steps and the shape of
the data at each (FASTQ → clean FASTQ → BAM → gVCF → cohort VCF → variant table →
package). Note the tools/handler/`_lib` split: both the CLI and the FFL handler
call the same `_lib/<name>.py` simulator via `handlers/shared/genomics_utils.py`.

## Fan-out
Does it fan out across the fleet? If yes: what is the fan-out unit (per-sample /
per-resource), which facet drives it (a `foreach` over what list), and why it
reduces wall-clock. If it is single-task, say "single-task — no fan-out" and why.

## Data & fields
The schemas this feature produces (from `genomics.types` / `genomics.cache.types`)
and their fields, plus the registry/alias tables it reads
(`RESOURCE_REGISTRY`, `REFERENCE_ALIASES`, `ANNOTATION_ALIASES`, `INDEX_REGISTRY`,
`REFERENCE_CONTIGS`, `ALIGNER_VERSIONS`). Name concrete example values
(`GRCh38`, `dbSNP156`, `SRR622461`, `bwa`/`star`/`bowtie2`) where they matter. If
the feature does no lookup/filtering, say so.

## External libraries / binaries
Every non-stdlib dependency this feature relies on and what for. For this package
that is mostly **stdlib + PyYAML** — the "real" tools it *models* (fastp, bwa-mem2,
GATK, bcftools, VEP, STAR, bowtie2) are named in the simulated `tool_version` /
`version` strings but are **not** invoked. Say so explicitly; distinguish a
**binary** dependency from a **pip** one where a real one exists.

## Facets & workflows
The key event facets and workflows, with signatures and a one-line purpose taken
from the FFL docstrings. Mark event facets (need a handler) vs pure facets, and
note `Effect`/`Cost`/`Timeout` mixins where present. State whether the facet is
served by a hand-written `_DISPATCH` handler or a factory-built one, or is
FFL-only (composed, no handler).

## Cache / output
What the simulator "caches" or emits. Because nothing touches disk, be precise:
the output is an in-memory JSON dict (a `GenomicsCache` / `IndexCache` /
`AnalysisPackage` record); `CACHE_BASE` (`FW_GENOMICS_CACHE_DIR`, default `/cache`)
only formats the `path` string. Note the canonical (aspirational) cache contract in
`agent-spec/cache-layout.agent-spec.yaml` where relevant.

## Gotchas & notes
Known pitfalls, drift between the FFL schema and the `_lib` simulator output, or
non-obvious constraints (worth capturing anything a future maintainer would trip
on).

## Related specs
Links to the specs this feature composes with or depends on.
