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


def joint_genotype(*, cohort_id: str = "unknown") -> dict[str, Any]:
    """Simulate joint genotyping across a cohort of gVCFs."""
    return {
        "cohort_id": cohort_id,
        "joint_vcf_path": f"/vcf/{cohort_id}/cohort.vcf.gz",
        "sample_count": 100,
        "variant_count": 12_000_000,
    }


def normalize_filter(*, vcf_path: str = "/vcf/cohort.vcf.gz") -> dict[str, Any]:
    """Simulate normalizing + filtering a joint-called VCF."""
    return {
        "input_vcf": vcf_path,
        "output_vcf": vcf_path.replace(".vcf.gz", ".norm.vcf.gz"),
        "passed_variants": 11_400_000,
        "filtered_variants": 600_000,
        "tool_version": "bcftools-1.18",
    }


def annotate(*, vcf_path: str = "/vcf/cohort.norm.vcf.gz") -> dict[str, Any]:
    """Simulate annotating a VCF with functional consequences."""
    return {
        "input_vcf": vcf_path,
        "output_vcf": vcf_path.replace(".vcf.gz", ".annot.vcf.gz"),
        "annotated_variants": 11_400_000,
        "high_impact": 250_000,
        "moderate_impact": 1_200_000,
        "tool_version": "vep-110",
    }


def cohort_analytics(*, cohort_id: str = "unknown") -> dict[str, Any]:
    """Simulate cohort-level analytics on annotated variants."""
    return {
        "cohort_id": cohort_id,
        "report_path": f"/reports/{cohort_id}/cohort_analytics.json",
        "sample_count": 100,
        "shared_variants": 8_000_000,
        "private_variants": 3_400_000,
        "ancestry_groups": ["EUR", "AFR", "AMR", "EAS", "SAS"],
    }


def publish(
    *,
    cohort_id: str = "unknown",
    report_dir: str = "/reports/",
) -> dict[str, Any]:
    """Simulate publishing the final cohort report bundle."""
    return {
        "cohort_id": cohort_id,
        "published_path": f"{report_dir.rstrip('/')}/{cohort_id}/index.html",
        "artifact_count": 8,
        "total_size_bytes": 500_000_000,
    }
