# genomics

A standalone [Facetwork](https://github.com/rlemke/facetwork) example package
that simulates a germline variant-calling pipeline across a cohort of
samples:

- **Per-sample pipeline** — QC → Align → CallVariants for FASTQ to gVCF
- **Cohort analysis** — joint genotyping → normalization → annotation → analytics → publish
- **Resource cache** — 250+ factory-built handlers for reference genomes, annotation tracks, example samples
- **Resolve + Operations** — name-based lookup of cached resources plus a small operations API (download, index, validate, status, checksum)
- **18 simulator handlers** across `genomics.Facets`, `genomics.cache.<aligner>`, `genomics.cache.Operations`, `genomics.cache.Resolve`

All handlers are deterministic simulators that return realistic shapes
without actually running fastp / bwa / GATK / VEP — so the example runs
fully offline.

Discovered by the Facetwork runner via the `facetwork.examples` entry point
declared in `pyproject.toml`. After `pip install -e .`, Facetwork's
`scripts/start-runner --example genomics` and `scripts/seed-examples`
pick this package up automatically.

## Install

```bash
git clone https://github.com/rlemke/fwh_genomics.git ~/fw_handlers/fwh_genomics
cd ~/fw_handlers/fwh_genomics
pip install -e .
```

## Run from a Facetwork checkout

```bash
scripts/seed-examples --include genomics                  # one-time, seeds FFL
scripts/start-runner --example genomics -- --log-format text
```

## Run a single pipeline step from the command line

Every pipeline facet has a matching CLI under `src/genomics/tools/`,
backed by the same `tools/_lib/` modules the FFL handlers call:

```bash
src/genomics/tools/qc-reads.sh --sample-id NA12878
src/genomics/tools/align-reads.sh --sample-id NA12878
src/genomics/tools/call-variants.sh --sample-id NA12878
src/genomics/tools/joint-genotype.sh --cohort-id ashkenazi-trio
src/genomics/tools/annotate.sh --vcf-path /vcf/cohort.norm.vcf.gz
src/genomics/tools/cohort-analytics.sh --cohort-id ashkenazi-trio
src/genomics/tools/publish.sh --cohort-id ashkenazi-trio --report-dir /reports/

src/genomics/tools/download.sh --resource grch38
src/genomics/tools/index.sh --aligner bwa --resource grch38
src/genomics/tools/validate.sh --resource grch38
```

The CLIs print the JSON result that the FFL handler would emit, plus a
human-readable summary on stderr.

## Layout

```
fwh_genomics/
├── pyproject.toml                  # facetwork.examples entry point
├── README.md
├── CLAUDE.md                       # guidance for Claude Code in this repo
├── USER_GUIDE.md                   # human-facing walkthrough
├── agent-spec/                     # tools-pattern, cache-layout specs
├── agent.py                        # standalone AgentPoller variant
├── tests/                          # mocked + real test trees
└── src/genomics/
    ├── __init__.py                 # exports `example: ExamplePackage`
    ├── handlers/                   # 5 event-facet modules + shared/ shim
    │   ├── genomics_handlers.py    # 9 facets: QC, Align, CallVariants, …
    │   ├── operations_handlers.py  # 5 ops: download, index, validate, status, checksum
    │   ├── resolve_handlers.py     # 4 resolvers: reference, annotation, sample, list
    │   ├── cache_handlers.py       # factory-built handlers from resource registry
    │   ├── index_handlers.py       # factory-built index handlers (bwa, bowtie2, …)
    │   └── shared/genomics_utils.py # imports the real impl from tools/_lib
    ├── ffl/                        # 7 FFL files (pipeline + cache + ops)
    └── tools/
        ├── _lib/                   # pipeline, operations, resources, cache, index simulators
        ├── *.py                    # one CLI per facet (~14 total)
        └── *.sh                    # shell wrappers
```

## License

Apache 2.0 — see `LICENSE`.
