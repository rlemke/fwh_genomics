# Cache Operations

**Namespaces:** `genomics.cache.Operations` · `genomics.cache.Operations.Data` (config) ·
**FFL:** `src/genomics/ffl/genomics_operations.ffl` ·
**Handlers:** `src/genomics/handlers/operations_handlers.py` ·
**Simulators:** `src/genomics/tools/_lib/operations.py`, `src/genomics/tools/_lib/index.py` ·
**CLIs:** `src/genomics/tools/{download,index,validate}.sh` ·
**Tests:** `test_handler_dispatch_genomics.py::TestGenomicsOperationsHandlers`

## Overview

Where [resource-cache](resource-cache.md) exposes one facet *per named resource*,
this namespace provides the **generic verbs** that operate on any `GenomicsCache`
handed to them: download it, build an index from it, verify it, report its status,
checksum it. These are the small operational primitives a workflow composes after
resolving a resource by name.

## How it works

`operations_handlers.py` hand-registers five handlers (verified at 5 entries by the
test), each a thin adapter over `tools/_lib/operations.py`:

- `Download(cache)` → `operations.download` — **pass-through**: returns
  `{"cache": dict(cache)}` unchanged (models "already cached").
- `Index(cache, aligner)` → `operations.index` — builds an `IndexCache` for the
  given aligner string from `cache.path`; returns fixed illustrative sizing
  (4.5 GB, 195 contigs, `<aligner>-latest`).
- `Validate(cache)` → `operations.validate` — returns `{"valid": True, "message":
  "Checksum verified"}` (always valid).
- `Status(cache)` → `operations.status` — returns path, size, `wasInCache`,
  `available` from the passed cache dict.
- `Checksum(cache)` → `operations.checksum` — returns a fixed `sha256` digest of
  `"a"*64` for the path.

The `genomics.cache.Operations.Data` namespace holds two **pure config facets**
(`CacheDate(date="latest")`, `CacheForce(force=false)`) — declaration-only
defaults, no handler and no `_DISPATCH` entry.

## Fan-out

**Single-task per op — no fan-out.** Each verb is one atomic call.

## Data & fields

- `Download` / `Index` consume and produce `GenomicsCache` / `IndexCache`
  (see [resource-cache](resource-cache.md), [aligner-indexes](aligner-indexes.md)).
- `Validate` → `(valid: Boolean, message: String)`.
- `Status` → `(status: String, size: Long, date: String)` in FFL; the simulator
  actually returns `path`/`size`/`wasInCache`/`available` — a shape mismatch (see
  Gotchas).
- `Checksum` → `(checksum: String, algorithm: String)` in FFL; the simulator
  returns `path`/`algorithm`/`digest` — also a mismatch (see Gotchas).

## External libraries / binaries

**None.** All five simulators are constant-returning pure functions; no download,
no hashing of real bytes, no aligner invocation.

## Facets & workflows

Five **event facets** in `genomics.cache.Operations`:

| Facet | Effect / Cost | Timeout | Purpose |
|---|---|---|---|
| `Download(cache)` | external / expensive | 120 min | Fetch a resource into the local cache |
| `Index(cache, aligner)` | external / expensive | 180 min | Build an aligner index from a cached reference |
| `Validate(cache)` | io / moderate | — | Verify integrity against checksum |
| `Status(cache)` | io / cheap | — | Report on-disk status/size/date |
| `Checksum(cache)` | io / moderate | — | Compute a cryptographic checksum |

Plus two **pure** config facets in `genomics.cache.Operations.Data`:
`CacheDate(date = "latest")`, `CacheForce(force = false)` — no mixins, no handler.

CLIs: `download.sh`, `index.sh` (the generic op, backed by `_lib/index.py`),
`validate.sh`. `Status`/`Checksum` have no CLI wrapper.

## Cache / output

No bytes written; outputs are in-memory dicts. `Download` is a pure pass-through,
so it never actually caches anything — it echoes the input `cache` record.

## Gotchas & notes

- **`Validate` always passes and `Checksum` is a constant.** `validate` returns
  `valid=True` unconditionally (its `cache` arg is even marked `# noqa: ARG001`),
  and `checksum` returns `"a"*64` for every input. They demonstrate the surface,
  not real verification.
- **`Status`/`Checksum` simulator keys don't match the FFL return clause.** FFL
  `Status` declares `(status, size, date)` but the simulator returns
  `path`/`size`/`wasInCache`/`available`; FFL `Checksum` declares
  `(checksum, algorithm)` but the simulator returns `path`/`algorithm`/`digest`.
  Only `size` (Status) overlaps. A runtime consumer reading `status`/`date`/
  `checksum` would get nulls.
- **`Operations.Index` vs the per-pair index facets.** This generic `Index` takes
  any `aligner` string and fixed 195-contig sizing; the pre-enumerated
  `genomics.cache.index.<aligner>.<Ref>` facets ([aligner-indexes](aligner-indexes.md))
  size from `REFERENCE_CONTIGS`. `test_cache_pipeline.py` and the
  `PrepareReference` workflow use this generic op.
- **The `Data` config facets are unused by the shipped workflows** — declared for
  completeness (force / date knobs) but not wired into any `andThen` block.

## Related specs

- [resource-cache](resource-cache.md) · [aligner-indexes](aligner-indexes.md) —
  the typed cache entries these verbs operate on.
- [resource-resolution](resource-resolution.md) — usually runs *before* these ops
  to turn a name into a `GenomicsCache`.
- [composed-workflows](composed-workflows.md) — `PrepareReference` / `PrepareSample`
  chain resolve → `Index` / `Download`.
