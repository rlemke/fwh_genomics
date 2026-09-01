"""The simulators are DOCUMENTED as deterministic; this enforces it.

README.md and CLAUDE.md both describe these handlers as "deterministic
simulators", and downstream work relies on it: the package is the reference
example for cohort fan-out, and a reproduction check across two runs of this
pipeline is only meaningful if the pipeline itself is stable.

Verified live on the fleet 2026-09-01 — two independent SamplePipeline runs over
the same three samples produced byte-identical CallVariants output. That was a
one-off manual check; this makes it a standing guarantee, because a claim nothing
tests is a claim that quietly stops being true.

⚠️ Determinism here means "same inputs -> same outputs", NOT "the same object
every call". A function that returned a fresh timestamp, a uuid, or iterated a
set would pass casual inspection and fail this.
"""
from __future__ import annotations

import pytest

from genomics.tools._lib import pipeline

SAMPLES = ["NA12878", "NA12891", "NA12892"]

# (function, kwargs) for every per-sample simulator that takes a sample id.
PER_SAMPLE = [
    (pipeline.qc_reads, "qc_reads"),
    (pipeline.align_reads, "align_reads"),
    (pipeline.call_variants, "call_variants"),
]


@pytest.mark.parametrize("fn,name", PER_SAMPLE, ids=[n for _f, n in PER_SAMPLE])
@pytest.mark.parametrize("sample_id", SAMPLES)
def test_per_sample_simulator_is_deterministic(fn, name, sample_id):
    first = fn(sample_id=sample_id)
    second = fn(sample_id=sample_id)
    assert first == second, f"{name}({sample_id}) is not deterministic"


@pytest.mark.parametrize("sample_id", SAMPLES)
def test_distinct_samples_give_distinct_results(sample_id):
    """Determinism must not be achieved by ignoring the input.

    A simulator returning one constant for every sample would pass every test
    above while making the whole cohort fan-out meaningless.
    """
    others = [s for s in SAMPLES if s != sample_id]
    mine = pipeline.call_variants(sample_id=sample_id)
    for other in others:
        assert mine != pipeline.call_variants(sample_id=other), \
            "call_variants ignores sample_id — determinism is vacuous"


def test_reference_ingest_is_deterministic():
    for build in ("GRCh38", "GRCh37"):
        assert pipeline.ingest_reference(reference_build=build) == \
               pipeline.ingest_reference(reference_build=build)


def test_repeated_full_per_sample_chain_is_stable():
    """The whole per-sample chain, twice — the shape a reproduction compares."""
    def chain(sid):
        qc = pipeline.qc_reads(sample_id=sid)
        al = pipeline.align_reads(sample_id=sid)
        cv = pipeline.call_variants(sample_id=sid)
        return {"qc": qc, "align": al, "call": cv}

    for sid in SAMPLES:
        assert chain(sid) == chain(sid), f"per-sample chain unstable for {sid}"
