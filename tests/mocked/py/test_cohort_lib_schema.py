#!/usr/bin/env python3
"""Guard: the cohort ``_lib`` simulators return exactly their FFL schema keys.

These functions back the ``genomics.Facets.{JointGenotype,NormalizeFilter,
Annotate,CohortAnalytics,Publish}`` handlers, which return their output
verbatim (``{"result": <fn(...)>}``). If a function's keys drift from the FFL
``=> (result: <Schema>)`` return clause, downstream ``$.result.<field>``
references in the CohortAnalysis workflow silently resolve to null. This test
pins each return shape to the schema declared in ``src/genomics/ffl/genomics.ffl``.
"""
from __future__ import annotations

from genomics.tools._lib.pipeline import (
    annotate,
    cohort_analytics,
    joint_genotype,
    normalize_filter,
    publish,
)

# Schema field sets, transcribed from src/genomics/ffl/genomics.ffl.
COHORT_VARIANT_RESULT = {
    "cohort_vcf_path", "filtered_vcf_path", "sample_count", "variant_count", "pass_rate",
}
ANNOTATION_RESULT = {"variant_table_path", "variant_count", "annotated_count", "gene_count"}
COHORT_STATS_RESULT = {"qc_report_path", "stats_path", "sample_count", "mean_depth", "variant_count"}
ANALYSIS_PACKAGE = {
    "package_path", "manifest_path", "dataset_id", "sample_count", "variant_count", "build",
}


def test_joint_genotype_matches_cohort_variant_result():
    assert set(joint_genotype(gvcf_dir="/g", reference_build="GRCh38", sample_count=4)) \
        == COHORT_VARIANT_RESULT


def test_normalize_filter_matches_cohort_variant_result():
    assert set(normalize_filter(vcf_path="/vcf/cohort.vcf.gz")) == COHORT_VARIANT_RESULT


def test_annotate_matches_annotation_result():
    assert set(annotate(vcf_path="/vcf/c.norm.vcf.gz", annotation_path="/ref/a.gff")) \
        == ANNOTATION_RESULT


def test_cohort_analytics_matches_cohort_stats_result():
    assert set(cohort_analytics(variant_table_path="/t.tsv", dataset_id="d")) \
        == COHORT_STATS_RESULT


def test_publish_matches_analysis_package():
    assert set(publish(variant_table_path="/t.tsv", qc_report_path="/qc.html",
                       stats_path="/s.json", dataset_id="d")) == ANALYSIS_PACKAGE
