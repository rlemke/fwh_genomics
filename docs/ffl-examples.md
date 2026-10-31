# FFL Examples — `genomics`

Every numbered scenario is a **complete, compilable FFL file**. Copy one into
`my.ffl` and run it:

```bash
fw ffl run --primary my.ffl \
  --library ~/fw_handlers/fwh_genomics/src/genomics/ffl/genomics.ffl \
  --library ~/fw_handlers/fwh_genomics/src/genomics/ffl/genomics_cache.ffl \
  --workflow my.genomics.<WorkflowName>
```

(Repeat `--library` for whichever of the domain's FFL files you use;
`fw ffl seed --include genomics` seeds them all once instead.) A runner serving
the `genomics` namespace must be up (`fw runner start --domain genomics`). Every
block below is compile-checked against the domain's FFL.

New to the language? Start with the
[FFL grammar](https://github.com/rlemke/facetwork/blob/main/docs/reference/language/grammar.md)
and the [canonical examples](https://github.com/rlemke/facetwork/tree/main/examples/canonical).

---

## The building blocks

A GATK-style pipeline: per-sample work fans out, then joint genotyping fans it
back in. Every stage carries a real `Timeout` mixin (up to 4 hours) — this domain
is where long-running-handler behaviour is visible.

| Declaration | Role |
|---|---|
| `genomics.Facets.IngestReference(reference_build) => (result: ReferenceBundle)` | Fetch/cache a reference genome (`Timeout(minutes = 180)`) |
| `genomics.Facets.QcReads(sample_id, r1_uri, r2_uri) => (result: QcReport)` | Per-sample QC → clean FASTQ |
| `genomics.Facets.AlignReads(sample_id, clean_fastq_path, reference_build) => (result: AlignmentResult)` | Per-sample alignment (`Timeout(minutes = 240)`) |
| `genomics.Facets.CallVariants(sample_id, bam_path, reference_build) => (result: VariantResult)` | Per-sample gVCF |
| `genomics.Facets.JointGenotype(gvcf_dir, reference_build, sample_count) => (result: CohortVariantResult)` | The **fan-in** |
| `genomics.Facets.NormalizeFilter` / `Annotate` / `CohortAnalytics` / `Publish` | Cohort post-processing |
| `genomics.pipeline.SamplePipeline(samples: Json, reference_build)` | The shipped per-sample fan-out |
| `genomics.pipeline.CohortAnalysis(dataset_id, reference_build, gvcf_dir)` | The shipped cohort stage |
| `genomics.cache.reference.*` / `annotation.*` / `sra.*` | Named cache facets (`GRCh38()`, `ClinVar()`, `SRR622461()`, …) |

Results are **schemas**, so fields nest: `qc.result.clean_fastq_path`,
`aln.result.bam_path`.

---

## 1. Run what ships — no FFL to write

```bash
fw ffl seed --include genomics

fw ffl run --workflow genomics.pipeline.SamplePipeline \
  --inputs '{"samples": [{"sample_id": "NA12878", "r1_uri": "s3://…/r1.fq.gz", "r2_uri": "s3://…/r2.fq.gz"}], "reference_build": "GRCh38"}'

fw ffl run --workflow genomics.pipeline.CohortAnalysis \
  --inputs '{"dataset_id": "trio-2026", "gvcf_dir": "s3://…/gvcfs/", "reference_build": "GRCh38"}'
```

Write FFL when you want a different *shape* — a different cohort split, extra QC
gates, your own error handling, or a pipeline that stops after alignment.

## 2. The smallest workflow you can write

Every FFL workflow needs a `namespace`, a `use` per namespace it calls into, and a
`yield` back to itself.

```ffl
namespace my.genomics {

    use genomics.Facets

    /** QC one sample. */
    workflow QcOne(sample_id: String, r1_uri: String, r2_uri: String) => (pass_rate: Double, clean: String) andThen {

        qc = genomics.Facets.QcReads(sample_id = $.sample_id, r1_uri = $.r1_uri, r2_uri = $.r2_uri)

        yield QcOne(pass_rate = qc.result.pass_rate, clean = qc.result.clean_fastq_path)
    }
}
```

Rules visible above: `=>` sits on the **same line** as the closing `)`; references
are always `step.field` and schema results nest one level
(`qc.result.pass_rate`); `$.sample_id` reads the workflow's parameter.

## 3. The per-sample chain

QC → align → call. Each step references the previous one, so the runtime enforces
that order; nothing else needs saying.

```ffl
namespace my.genomics {

    use genomics.Facets

    /** One sample, FASTQ → gVCF. */
    workflow OneSample(sample_id: String, r1_uri: String, r2_uri: String,
        reference_build: String = "GRCh38") => (gvcf: String, variants: Long) andThen {

        qc = genomics.Facets.QcReads(sample_id = $.sample_id, r1_uri = $.r1_uri, r2_uri = $.r2_uri)

        aln = genomics.Facets.AlignReads(
            sample_id = $.sample_id,
            clean_fastq_path = qc.result.clean_fastq_path,
            reference_build = $.reference_build)

        var = genomics.Facets.CallVariants(
            sample_id = $.sample_id,
            bam_path = aln.result.bam_path,
            reference_build = $.reference_build)

        yield OneSample(gvcf = var.result.gvcf_path, variants = var.result.variant_count)
    }
}
```

## 4. Fan out over a cohort — `foreach`

`andThen foreach v in <list>` runs the body once per sample, each as its own set of
runtime steps that the fleet claims in parallel. Here the `foreach` hangs off the
**workflow**, so the loop variable and the workflow's parameters share one `$`;
loop items are Json objects, so `$.s.sample_id` walks into one.

```ffl
namespace my.genomics {

    use genomics.Facets

    /** One QC→align→call chain per sample, all samples in parallel. */
    workflow CohortSamples(samples: Json, reference_build: String = "GRCh38") => (gvcfs: [String]) andThen foreach s in $.samples {

        qc = genomics.Facets.QcReads(
            sample_id = $.s.sample_id, r1_uri = $.s.r1_uri, r2_uri = $.s.r2_uri)

        aln = genomics.Facets.AlignReads(
            sample_id = $.s.sample_id,
            clean_fastq_path = qc.result.clean_fastq_path,
            reference_build = $.reference_build)

        var = genomics.Facets.CallVariants(
            sample_id = $.s.sample_id,
            bam_path = aln.result.bam_path,
            reference_build = $.reference_build)

        yield CohortSamples(gvcfs = [var.result.gvcf_path])
    }
}
```

Wall clock is the slowest sample, not the sum. `yield`ing a one-element array is
how the per-sample results accumulate into one list.

## 5. Fan in — joint genotyping and the cohort tail

`JointGenotype` reads a directory of gVCFs rather than a value from the loop, so
pass `sample_count` as the signal and chain the rest by reference.

```ffl
namespace my.genomics {

    use genomics.Facets

    /** Joint genotype → normalize → annotate → analytics → publish. */
    workflow CohortTail(dataset_id: String, gvcf_dir: String, sample_count: Long,
        reference_build: String = "GRCh38", annotation_path: String = "") => (package_path: String, variants: Long) andThen {

        joint = genomics.Facets.JointGenotype(
            gvcf_dir = $.gvcf_dir,
            reference_build = $.reference_build,
            sample_count = $.sample_count)

        norm = genomics.Facets.NormalizeFilter(
            vcf_path = joint.result.cohort_vcf_path,
            reference_build = $.reference_build)

        ann = genomics.Facets.Annotate(
            vcf_path = norm.result.filtered_vcf_path,
            annotation_path = $.annotation_path)

        stats = genomics.Facets.CohortAnalytics(
            variant_table_path = ann.result.variant_table_path,
            dataset_id = $.dataset_id)

        pub = genomics.Facets.Publish(
            variant_table_path = ann.result.variant_table_path,
            qc_report_path = stats.result.qc_report_path,
            stats_path = stats.result.stats_path,
            dataset_id = $.dataset_id)

        yield CohortTail(
            package_path = pub.result.package_path,
            variants = ann.result.variant_count)
    }
}
```

## 6. Warm the caches first

The `genomics.cache.*` namespaces expose each reference/annotation/SRA artifact as
its own zero-argument facet. They're independent, so they download **in parallel**.

```ffl
namespace my.genomics {

    use genomics.cache.reference
    use genomics.cache.annotation

    /** Pull the reference + annotation bundles concurrently. */
    workflow WarmCaches() => (status: String) andThen {

        ref = genomics.cache.reference.GRCh38()
        clinvar = genomics.cache.annotation.ClinVar()
        gnomad = genomics.cache.annotation.GnomAD4()

        yield WarmCaches(status = "cached")
    }
}
```

## 7. Gate on QC — `when`

A `when` block hangs off the step it inspects: inside a case `$` is that step and
`$$` reaches the workflow. Don't burn four hours of alignment on a sample that
failed QC. Every `when` needs a default case, last.

```ffl
namespace my.genomics {

    use genomics.Facets

    /** Align only if QC passed the threshold. */
    workflow GatedAlign(sample_id: String, r1_uri: String, r2_uri: String,
        min_pass_rate: Double = 0.8, reference_build: String = "GRCh38") => (status: String, bam: String) andThen {

        qc = genomics.Facets.QcReads(
            sample_id = $.sample_id, r1_uri = $.r1_uri, r2_uri = $.r2_uri) andThen when {
            case $.result.pass_rate >= $$.min_pass_rate => {
                aln = genomics.Facets.AlignReads(
                    sample_id = $$.sample_id,
                    clean_fastq_path = $.result.clean_fastq_path,
                    reference_build = $$.reference_build)
                yield GatedAlign(status = "aligned", bam = aln.result.bam_path)
            }
            case _ => {
                yield GatedAlign(status = "qc_failed", bam = "")
            }
        }
    }
}
```

## 8. One bad sample shouldn't sink the cohort — `catch`

`catch` fires when its step errors after retries are exhausted. Inside a `foreach`
it is per-iteration.

```ffl
namespace my.genomics {

    use genomics.Facets

    /** Best-effort cohort QC. */
    workflow BestEffortQc(samples: Json) => (clean: [String]) andThen foreach s in $.samples {

        qc = genomics.Facets.QcReads(
            sample_id = $.s.sample_id, r1_uri = $.s.r1_uri, r2_uri = $.s.r2_uri) catch {
            yield BestEffortQc(clean = ["failed"])
        }

        yield BestEffortQc(clean = [qc.result.clean_fastq_path])
    }
}
```

## 9. Call-time mixins — long stages need long clocks

Every facet here ships a `Timeout`; a call site can raise it for an unusually big
sample without forking the facet.

```ffl
namespace my.genomics {

    use genomics.Facets

    /** A deep-coverage genome: 8 hours, and one retry. */
    workflow DeepAlign(sample_id: String, clean_fastq_path: String,
        reference_build: String = "GRCh38") => (bam: String) andThen {

        aln = genomics.Facets.AlignReads(
            sample_id = $.sample_id,
            clean_fastq_path = $.clean_fastq_path,
            reference_build = $.reference_build) with Timeout(minutes = 480) with Retry(maxAttempts = 2, backoffSeconds = 300)

        yield DeepAlign(bam = aln.result.bam_path)
    }
}
```

Handlers that block for hours without heart-beating should register with
`timeout_ms=0` and rely on the global execution timeout — see
[long-running handlers](https://github.com/rlemke/facetwork/blob/main/docs/guides/long-running-handlers.md).

---

## Cheat sheet

| You want to… | Write |
|---|---|
| Read a workflow/step parameter | `$.name` (`$$.name` one level out) |
| Read a field of a Json loop variable | `$.s.sample_id` |
| Read a previous step's result | `stepname.field` — schema results nest: `qc.result.pass_rate` |
| Fan out over a list | `workflow W(items: Json) … andThen foreach i in $.items { … }` |
| Collect fan-out results | `yield W(gvcfs = [var.result.gvcf_path])` — the arrays accumulate |
| Run steps in parallel | write them with no reference between them |
| More time / retries for one call | `… with Timeout(minutes = 480) with Retry(maxAttempts = 2, backoffSeconds = 300)` |
| Handle a step failure | `step = Facet(…) catch { yield … }` |
| Branch | `step = Facet(…) andThen when { case <bool> => { … } case _ => { … } }` |

**Validate before you run:** `fw ffl compile --check --primary my.ffl --library <this domain's .ffl>` or MCP `fw_validate`. Every error
carries a `rule_id` — fetch `fw://docs/rules/{rule_id}` for a wrong/right pair.

## See also

- [`docs/README.md`](README.md) — per-feature specs for this domain
- [Long-running handlers](https://github.com/rlemke/facetwork/blob/main/docs/guides/long-running-handlers.md)
- [FFL grammar](https://github.com/rlemke/facetwork/blob/main/docs/reference/language/grammar.md) ·
  [canonical examples](https://github.com/rlemke/facetwork/tree/main/examples/canonical) ·
  [relative `$`-scoping](https://github.com/rlemke/facetwork/blob/main/docs/architecture/ffl-relative-scoping.md)
- The domain's FFL under `src/genomics/ffl/` — the source of truth for every signature above
