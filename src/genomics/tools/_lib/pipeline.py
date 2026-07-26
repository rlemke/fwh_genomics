"""Per-sample + cohort pipeline simulators.

Each function returns the **inner** result dict (without the outer
``{"result": …}`` wrapper). The FFL handlers in
``genomics.handlers.genomics_handlers`` wrap the dict in whatever
shape the FFL output schema demands — keeping the wrapping concern
out of the simulator means the CLIs can print the result directly.
"""

from __future__ import annotations

from typing import Any


def ingest_reference(*, reference_build: str = "GRCh38") -> dict[str, Any]:
    """Simulate downloading and indexing a reference genome build."""
    return {
        "fasta_path": f"/ref/{reference_build}/{reference_build}.fa",
        "annotation_path": f"/ref/{reference_build}/annotation.gtf",
        "build": reference_build,
        "size_bytes": 3_200_000_000,
    }


def qc_reads(*, sample_id: str = "unknown") -> dict[str, Any]:
    """Simulate quality control on paired-end FASTQ reads."""
    return {
        "sample_id": sample_id,
        "total_reads": 1_000_000_000,
        "passed_reads": 970_000_000,
        "failed_reads": 30_000_000,
        "pass_rate": 97,
        "clean_fastq_path": f"/fastq/{sample_id}/{sample_id}_clean.fq.gz",
        "tool_version": "fastp-0.23.4",
    }


def align_reads(*, sample_id: str = "unknown") -> dict[str, Any]:
    """Simulate aligning cleaned reads to the reference genome."""
    return {
        "sample_id": sample_id,
        "bam_path": f"/bam/{sample_id}/{sample_id}.sorted.bam",
        "total_reads": 970_000_000,
        "mapped_reads": 965_000_000,
        "mapping_rate": 99,
        "duplicate_rate": 8,
        "mean_coverage": 30,
    }


def call_variants(*, sample_id: str = "unknown") -> dict[str, Any]:
    """Simulate calling genomic variants from an aligned BAM file."""
    return {
        "sample_id": sample_id,
        "gvcf_path": f"/vcf/{sample_id}/{sample_id}.g.vcf.gz",
        "variant_count": 4_800_000,
        "snp_count": 4_200_000,
        "indel_count": 600_000,
        "tool_version": "gatk-4.5",
    }


def joint_genotype(
    *,
    gvcf_dir: str = "/gvcf",
    reference_build: str = "GRCh38",
    sample_count: int = 100,
) -> dict[str, Any]:
    """Simulate joint genotyping across a cohort of gVCFs.

    Returns a ``CohortVariantResult`` (see ``genomics.ffl``): the joint-called
    cohort VCF plus the hard-filtered VCF, with cohort-level counts.
    """
    base = gvcf_dir.rstrip("/")
    return {
        "cohort_vcf_path": f"{base}/cohort.{reference_build}.vcf.gz",
        "filtered_vcf_path": f"{base}/cohort.{reference_build}.filtered.vcf.gz",
        "sample_count": int(sample_count),
        "variant_count": 12_000_000,
        "pass_rate": 0.95,
    }


def normalize_filter(
    *,
    vcf_path: str = "/vcf/cohort.vcf.gz",
    reference_build: str = "GRCh38",
) -> dict[str, Any]:
    """Simulate normalizing + filtering a joint-called VCF.

    Returns a ``CohortVariantResult`` — same shape as :func:`joint_genotype`,
    with the normalized+filtered VCF as ``filtered_vcf_path``.
    """
    return {
        "cohort_vcf_path": vcf_path,
        "filtered_vcf_path": vcf_path.replace(".vcf.gz", ".norm.filtered.vcf.gz"),
        "sample_count": 100,
        "variant_count": 11_400_000,
        "pass_rate": 0.95,
    }


def annotate(
    *,
    vcf_path: str = "/vcf/cohort.norm.vcf.gz",
    annotation_path: str = "/ref/annotations.gff",
) -> dict[str, Any]:
    """Simulate annotating a VCF with functional consequences.

    Returns an ``AnnotationResult``: the flattened per-variant table plus
    variant / annotated / gene counts.
    """
    return {
        "variant_table_path": vcf_path.replace(".vcf.gz", ".annotated.tsv"),
        "variant_count": 11_400_000,
        "annotated_count": 11_400_000,
        "gene_count": 20_000,
    }


def cohort_analytics(
    *,
    variant_table_path: str = "/vcf/cohort.annotated.tsv",
    dataset_id: str = "cohort",
) -> dict[str, Any]:
    """Simulate cohort-level analytics on annotated variants.

    Returns a ``CohortStatsResult``: the QC report + stats JSON paths and
    cohort summary statistics.
    """
    base = f"/reports/{dataset_id}"
    return {
        "qc_report_path": f"{base}/qc_report.html",
        "stats_path": f"{base}/cohort_stats.json",
        "sample_count": 100,
        "mean_depth": 32.5,
        "variant_count": 11_400_000,
    }


def publish(
    *,
    variant_table_path: str = "/vcf/cohort.annotated.tsv",
    qc_report_path: str = "/reports/qc_report.html",
    stats_path: str = "/reports/cohort_stats.json",
    dataset_id: str = "cohort",
) -> dict[str, Any]:
    """Simulate publishing the final cohort analysis bundle.

    Returns an ``AnalysisPackage``: the packaged tarball + manifest and the
    dataset identity / counts.
    """
    base = f"/published/{dataset_id}"
    return {
        "package_path": f"{base}/analysis_package.tar.gz",
        "manifest_path": f"{base}/manifest.json",
        "dataset_id": dataset_id,
        "sample_count": 100,
        "variant_count": 11_400_000,
        "build": "GRCh38",
    }
