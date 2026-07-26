# Resource Resolution

**Namespace:** `genomics.cache.Resolve` ·
**FFL:** `src/genomics/ffl/genomics_resolve.ffl` ·
**Handlers:** `src/genomics/handlers/resolve_handlers.py` ·
**Simulators:** `src/genomics/tools/_lib/resolve.py`, `src/genomics/tools/_lib/resources.py` ·
**CLIs:** `src/genomics/tools/resolve.sh` ·
**Tests:** `test_handler_dispatch_genomics.py::TestGenomicsResolveHandlers`, `test_cache_pipeline.py`

## Overview

Users think in friendly names — "hg38", "dbsnp", "clinvar", an SRA accession — not
in CamelCase facet names like `genomics.cache.reference.GRCh38`. This feature is the
**name → canonical cache entry** resolver: it maps an alias, a case-insensitive
facet name, or an accession onto its `RESOURCE_REGISTRY` row and returns both the
`GenomicsCache` and a `ResourceResolution` explaining the match. It's the friendly
front door to [resource-cache](resource-cache.md).

## How it works

`resolve_handlers.py` hand-registers four handlers (verified at 4 entries by the
test), all over `tools/_lib/resolve.py`, all reading `RESOURCE_REGISTRY` +
alias maps from `resources.py`:

- `ResolveReference(name)` — normalizes `name` (lowercase/strip), looks it up in
  `REFERENCE_ALIASES` (e.g. `hg38 → GRCh38`, `t2t/chm13 → T2TCHM13`, `mm39 →
  GRCm39`); on miss, falls back to a case-insensitive match against the
  `genomics.cache.reference` facet names; on total miss returns an **empty cache +
  `is_ambiguous=True`** resolution listing the known aliases.
- `ResolveAnnotation(name)` — same shape over `ANNOTATION_ALIASES`
  (`dbsnp → DbSNP156`, `gnomad → GnomAD4`, `vep → VepCache112`, `gencode →
  Gencode46`, …).
- `ResolveSample(accession)` — exact match of the accession against the
  `genomics.cache.sra` facet names (no alias table); miss → ambiguous with the
  known accessions.
- `ListResources(category)` — enumerates the whole registry, optionally filtered by
  `resource_type` (`reference`/`annotation`/`sra`), returning counts + the rows.

The matched cache record is built by `resolve._resolved_cache`, which stamps the
same `GenomicsCache` shape as `cache_entry` (date `2026-02-08`, `wasInCache=True`,
a path-hash checksum).

## Fan-out

**Single-task per lookup — no fan-out.** Pure in-memory dict lookups.

## Data & fields

Output schemas (`genomics.cache.types`):

- `GenomicsCache` — the resolved resource (url, path, date, size, wasInCache,
  checksum, resource_type).
- `ResourceResolution` — query, matched_name, resource_namespace, category,
  source_url, is_ambiguous, disambiguation.
- `ResourceListResult` — resource_count, resources (Json), category_count,
  categories (Json).

Alias tables (`resources.py`): `REFERENCE_ALIASES` (11 aliases → 5 references),
`ANNOTATION_ALIASES` (11 aliases → 7 annotation DBs). SRA has no alias table.

## External libraries / binaries

**None.** All four resolvers are pure functions over static dicts — the
`Effect(kind="pure")` tag is accurate here (unlike most facets in this package,
these really are side-effect-free).

## Facets & workflows

Four **event facets**, all `Effect(kind="pure")`, `Cost(tier="cheap")`, no timeout:

| Facet | Signature |
|---|---|
| `ResolveReference(name, prefer_source = "")` | `=> (cache: GenomicsCache, resolution: ResourceResolution)` |
| `ResolveAnnotation(name, version = "latest")` | `=> (cache: GenomicsCache, resolution: ResourceResolution)` |
| `ResolveSample(accession)` | `=> (cache: GenomicsCache, resolution: ResourceResolution)` |
| `ListResources(category = "")` | `=> (result: ResourceListResult)` |

CLI: one `resolve.sh` with mode flags — `--reference X`, `--annotation X`,
`--sample X`, `--list` (per `tools/README.md`).

## Cache / output

Nothing written; outputs are in-memory dicts. This is the recommended way to
*inspect* the resource catalog from the shell (`resolve.sh --list`), since the
per-entry cache facets ship no CLI.

## Gotchas & notes

- **`prefer_source` and `version` params are declared but ignored.** The FFL
  signatures carry `prefer_source` (ResolveReference) and `version`
  (ResolveAnnotation), but `resolve.py` never reads them — annotation always
  resolves to the pinned build in the alias table (`dbsnp → DbSNP156`, not a
  version-selected one).
- **Miss is soft, not an error.** An unknown name returns an empty `GenomicsCache`
  plus `is_ambiguous=True` and a `disambiguation` string listing the known keys —
  it does not raise. Downstream steps must check `is_ambiguous` / `matched_name`.
- **SRA is exact-match only.** `ResolveSample("srr622461")` (lowercase) will
  **miss** — accessions are matched verbatim against the registry keys, with no
  normalization, unlike reference/annotation which lowercase first.
- **These are `pure`**, so a cost-aware composer will prefer them; resolve first,
  then pay for the `external`/`expensive` download/index/pipeline steps.

## Related specs

- [resource-cache](resource-cache.md) — the registry these names resolve into.
- [cache-operations](cache-operations.md) — the `Download`/`Index` ops that
  usually follow a resolve.
- [composed-workflows](composed-workflows.md) — `PrepareReference` /
  `PrepareSample` / `CachedCohortAnalysis` all start with a resolve.
