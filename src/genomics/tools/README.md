# genomics tools

CLI utilities for every operation the genomics example exposes. Each
operation has:

- a pure-function simulator under `_lib/<domain>.py`,
- a CLI script `<verb>_<noun>.py` that argparse-parses input and prints
  JSON,
- a thin shell wrapper `<verb>-<noun>.sh`.

The FFL handlers in `src/genomics/handlers/` call into the same
`_lib/` modules via `handlers/shared/genomics_utils.py`, so both
surfaces share one implementation — no drift.

## CLI map

### Per-sample + cohort pipeline (`tools/_lib/pipeline.py`)

| CLI | Facet |
|-----|-------|
| `ingest-reference.sh` | `genomics.Facets.IngestReference` |
| `qc-reads.sh` | `genomics.Facets.QcReads` |
| `align-reads.sh` | `genomics.Facets.AlignReads` |
| `call-variants.sh` | `genomics.Facets.CallVariants` |
| `joint-genotype.sh` | `genomics.Facets.JointGenotype` |
| `normalize-filter.sh` | `genomics.Facets.NormalizeFilter` |
| `annotate.sh` | `genomics.Facets.Annotate` |
| `cohort-analytics.sh` | `genomics.Facets.CohortAnalytics` |
| `publish.sh` | `genomics.Facets.Publish` |

### Cache operations (`tools/_lib/operations.py` + `tools/_lib/index.py`)

| CLI | Facet |
|-----|-------|
| `download.sh` | `genomics.cache.Operations.Download` |
| `index.sh` | `genomics.cache.Operations.Index` (factory-built via `tools/_lib/index.py`) |
| `validate.sh` | `genomics.cache.Operations.Validate` |

### Resource resolvers (`tools/_lib/resolve.py`)

| CLI | Facet |
|-----|-------|
| `resolve.sh --reference X` | `genomics.cache.Resolve.ResolveReference` |
| `resolve.sh --annotation X` | `genomics.cache.Resolve.ResolveAnnotation` |
| `resolve.sh --sample X` | `genomics.cache.Resolve.ResolveSample` |
| `resolve.sh --list` | `genomics.cache.Resolve.ListResources` |

The per-registry-entry cache handlers
(`genomics.cache.reference.GRCh38`,
`genomics.cache.annotation.ClinVar`, etc.) don't ship individual CLI
wrappers because their job is to be a *data lookup* into
`RESOURCE_REGISTRY` — there's no parameter to vary. Use
`resolve.sh --reference GRCh38` (or `--list`) to inspect them from
the shell, or read `tools/_lib/resources.py` directly.

## Conventions

- Help: `<cli>.sh --help` — every CLI uses argparse.
- Stderr: one-line human summary mirroring the FFL step log.
- Stdout: pretty-printed JSON dict (matching the FFL handler shape — minus the outer `{"result": …}` wrapper, since CLIs print the inner result directly).
- Exit code: 0 on success, non-zero on argparse error.
- Imports: every CLI uses `from genomics.tools._lib.<name> import …` so this package coexists cleanly with sibling Facetwork example packages on `sys.modules`.

## Example: one-sample pipeline from the shell

```bash
src/genomics/tools/ingest-reference.sh --reference-build GRCh38
src/genomics/tools/qc-reads.sh --sample-id NA12878
src/genomics/tools/align-reads.sh --sample-id NA12878
src/genomics/tools/call-variants.sh --sample-id NA12878
src/genomics/tools/joint-genotype.sh --cohort-id ashkenazi-trio
src/genomics/tools/normalize-filter.sh --vcf-path /vcf/ashkenazi-trio/cohort.vcf.gz
src/genomics/tools/annotate.sh --vcf-path /vcf/ashkenazi-trio/cohort.norm.vcf.gz
src/genomics/tools/cohort-analytics.sh --cohort-id ashkenazi-trio
src/genomics/tools/publish.sh --cohort-id ashkenazi-trio --report-dir /reports/
```
