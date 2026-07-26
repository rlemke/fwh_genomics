"""Genomics cohort analysis event facet handlers.

Handles all event facets in the ``genomics.Facets`` namespace. Each
handler is a thin payload→pure-function adapter; the deterministic
simulator logic lives in
:mod:`genomics.tools._lib.pipeline` and is reached via
:mod:`genomics.handlers.shared.genomics_utils`.
"""

import logging
import os
from typing import Any

from .shared.genomics_utils import (
    align_reads,
    annotate,
    call_variants,
    cohort_analytics,
    ingest_reference,
    joint_genotype,
    normalize_filter,
    publish,
    qc_reads,
)

log = logging.getLogger(__name__)

NAMESPACE = "genomics.Facets"


def _ingest_reference_handler(payload: dict) -> dict[str, Any]:
    """Download and index a reference genome build."""
    build = payload.get("reference_build", "GRCh38")
    step_log = payload.get("_step_log")
    if step_log:
        step_log(f"IngestReference: {build}")
    return {"result": ingest_reference(reference_build=build)}


def _qc_reads_handler(payload: dict) -> dict[str, Any]:
    """Run quality control on paired-end FASTQ reads."""
    sample_id = payload.get("sample_id", "unknown")
    step_log = payload.get("_step_log")
    if step_log:
        step_log(f"QcReads: sample {sample_id}")
    return {"result": qc_reads(sample_id=sample_id)}


def _align_reads_handler(payload: dict) -> dict[str, Any]:
    """Align cleaned reads to the reference genome."""
    sample_id = payload.get("sample_id", "unknown")
    step_log = payload.get("_step_log")
    if step_log:
        step_log(f"AlignReads: sample {sample_id}")
    return {"result": align_reads(sample_id=sample_id)}


def _call_variants_handler(payload: dict) -> dict[str, Any]:
    """Call genomic variants from an aligned BAM file."""
    sample_id = payload.get("sample_id", "unknown")
    step_log = payload.get("_step_log")
    if step_log:
        step_log(f"CallVariants: sample {sample_id}")
    return {"result": call_variants(sample_id=sample_id)}


def _joint_genotype_handler(payload: dict) -> dict[str, Any]:
    """Joint genotype across a cohort of gVCFs (facet ``JointGenotype``)."""
    gvcf_dir = payload.get("gvcf_dir", "/gvcf")
    reference_build = payload.get("reference_build", "GRCh38")
    sample_count = payload.get("sample_count", 100)
    step_log = payload.get("_step_log")
    if step_log:
        step_log(f"JointGenotype: {sample_count} gVCFs from {gvcf_dir}")
    return {"result": joint_genotype(
        gvcf_dir=gvcf_dir, reference_build=reference_build, sample_count=sample_count)}


def _normalize_filter_handler(payload: dict) -> dict[str, Any]:
    """Normalize and filter a joint-called VCF (facet ``NormalizeFilter``)."""
    vcf_path = payload.get("vcf_path", "/vcf/cohort.vcf.gz")
    reference_build = payload.get("reference_build", "GRCh38")
    step_log = payload.get("_step_log")
    if step_log:
        step_log(f"NormalizeFilter: {vcf_path}")
    return {"result": normalize_filter(vcf_path=vcf_path, reference_build=reference_build)}


def _annotate_handler(payload: dict) -> dict[str, Any]:
    """Annotate a VCF with functional consequences (facet ``Annotate``)."""
    vcf_path = payload.get("vcf_path", "/vcf/cohort.norm.vcf.gz")
    annotation_path = payload.get("annotation_path", "/ref/annotations.gff")
    step_log = payload.get("_step_log")
    if step_log:
        step_log(f"Annotate: {vcf_path}")
    return {"result": annotate(vcf_path=vcf_path, annotation_path=annotation_path)}


def _cohort_analytics_handler(payload: dict) -> dict[str, Any]:
    """Run cohort-level analytics on annotated variants (facet ``CohortAnalytics``)."""
    variant_table_path = payload.get("variant_table_path", "/vcf/cohort.annotated.tsv")
    dataset_id = payload.get("dataset_id", "cohort")
    step_log = payload.get("_step_log")
    if step_log:
        step_log(f"CohortAnalytics: {dataset_id}")
    return {"result": cohort_analytics(
        variant_table_path=variant_table_path, dataset_id=dataset_id)}


def _publish_handler(payload: dict) -> dict[str, Any]:
    """Publish the final cohort analysis bundle (facet ``Publish``)."""
    variant_table_path = payload.get("variant_table_path", "/vcf/cohort.annotated.tsv")
    qc_report_path = payload.get("qc_report_path", "/reports/qc_report.html")
    stats_path = payload.get("stats_path", "/reports/cohort_stats.json")
    dataset_id = payload.get("dataset_id", "cohort")
    step_log = payload.get("_step_log")
    if step_log:
        step_log(f"Publish: {dataset_id}")
    return {"result": publish(
        variant_table_path=variant_table_path, qc_report_path=qc_report_path,
        stats_path=stats_path, dataset_id=dataset_id)}


# RegistryRunner dispatch adapter
_DISPATCH = {
    f"{NAMESPACE}.IngestReference": _ingest_reference_handler,
    f"{NAMESPACE}.QcReads": _qc_reads_handler,
    f"{NAMESPACE}.AlignReads": _align_reads_handler,
    f"{NAMESPACE}.CallVariants": _call_variants_handler,
    f"{NAMESPACE}.JointGenotype": _joint_genotype_handler,
    f"{NAMESPACE}.NormalizeFilter": _normalize_filter_handler,
    f"{NAMESPACE}.Annotate": _annotate_handler,
    f"{NAMESPACE}.CohortAnalytics": _cohort_analytics_handler,
    f"{NAMESPACE}.Publish": _publish_handler,
}


def handle(payload: dict) -> dict:
    """RegistryRunner dispatch entrypoint."""
    facet_name = payload["_facet_name"]
    handler = _DISPATCH.get(facet_name)
    if handler is None:
        raise ValueError(f"Unknown facet: {facet_name}")
    return handler(payload)


def register_handlers(runner) -> None:
    """Register all facets with a RegistryRunner."""
    for facet_name in _DISPATCH:
        runner.register_handler(
            facet_name=facet_name,
            module_uri=f"file://{os.path.abspath(__file__)}",
            entrypoint="handle",
        )


def register_genomics_handlers(poller) -> None:
    """Register all genomics event facet handlers with the poller."""
    for fqn, func in _DISPATCH.items():
        poller.register(fqn, func)
        log.debug("Registered genomics handler: %s", fqn)
