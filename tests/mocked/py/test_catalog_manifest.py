"""Offline checks for the composability manifest (``src/genomics/catalog.yaml``).

Asserts the manifest loads, every workflow carries a non-empty intent summary +
tags + param_schema, every facet carries a valid effect/cost/namespace, every
listed qualified_name is plausibly real (its leaf name is declared as a
`workflow`/`facet` in the package's .ffl sources and its namespace exists), and
there are no duplicate entries. Also recompiles all package .ffl together so the
``with Effect(...) / with Cost(...) / with Timeout(...)`` annotations stay valid.
No runner, DB, or network needed.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from genomics import catalog

# Repo root: tests/mocked/py/ -> repo root is parents[3].
_REPO_ROOT = Path(__file__).resolve().parents[3]
_FFL_ROOT = _REPO_ROOT / "src" / "genomics"
_FFL_DIR = _FFL_ROOT / "ffl"


def _all_ffl_text() -> str:
    parts = [p.read_text(encoding="utf-8") for p in _FFL_ROOT.rglob("*.ffl")]
    assert parts, "no .ffl sources found under src/genomics"
    return "\n".join(parts)


@pytest.fixture(scope="module")
def ffl_text() -> str:
    return _all_ffl_text()


@pytest.fixture(scope="module")
def manifest():
    return catalog.load_manifest()


def test_manifest_loads(manifest):
    assert isinstance(manifest, dict)
    assert manifest.get("package") == "genomics"
    assert isinstance(catalog.workflows(), list) and catalog.workflows()
    assert isinstance(catalog.facets(), list) and catalog.facets()


def test_workflows_have_summary_and_tags():
    for wf in catalog.workflows():
        qn = wf.get("qualified_name", "<missing>")
        summary = wf.get("summary", "")
        assert isinstance(summary, str) and summary.strip(), f"empty summary for {qn}"
        tags = wf.get("tags")
        assert isinstance(tags, list) and tags, f"empty tags for {qn}"
        assert all(isinstance(t, str) and t.strip() for t in tags), f"bad tag in {qn}"
        assert wf.get("entry_point") is True, f"workflow {qn} not marked entry_point"
        assert isinstance(wf.get("param_schema"), dict), f"no param_schema for {qn}"


def test_facets_have_required_fields():
    valid_effects = {"pure", "external", "io"}
    valid_costs = {"free", "cheap", "moderate", "expensive"}
    for fc in catalog.facets():
        qn = fc.get("qualified_name", "<missing>")
        assert fc.get("purpose", "").strip(), f"empty purpose for {qn}"
        assert fc.get("signature", "").strip(), f"empty signature for {qn}"
        assert fc.get("effect") in valid_effects, f"bad effect for {qn}: {fc.get('effect')}"
        assert fc.get("cost") in valid_costs, f"bad cost for {qn}: {fc.get('cost')}"
        assert fc.get("namespace"), f"no namespace for {qn}"
        # The qualified name must live under its declared namespace.
        assert qn.startswith(fc["namespace"] + "."), f"{qn} not under namespace {fc['namespace']}"


def test_no_duplicate_entries():
    wf_names = [w["qualified_name"] for w in catalog.workflows()]
    fc_names = [f["qualified_name"] for f in catalog.facets()]
    assert len(wf_names) == len(set(wf_names)), "duplicate workflow qualified_names"
    assert len(fc_names) == len(set(fc_names)), "duplicate facet qualified_names"
    overlap = set(wf_names) & set(fc_names)
    assert not overlap, f"name listed as both workflow and facet: {overlap}"


def test_workflow_qualified_names_are_real(ffl_text):
    """Each workflow's leaf name must be declared as a `workflow <Leaf>` in the FFL."""
    for wf in catalog.workflows():
        qn = wf["qualified_name"]
        leaf = qn.rsplit(".", 1)[-1]
        pat = re.compile(rf"\bworkflow\s+{re.escape(leaf)}\b")
        assert pat.search(ffl_text), f"no `workflow {leaf}` found in FFL for {qn}"


def test_facet_qualified_names_are_real(ffl_text):
    """Each facet's leaf name must be declared as a `facet <Leaf>` in the FFL."""
    for fc in catalog.facets():
        qn = fc["qualified_name"]
        leaf = qn.rsplit(".", 1)[-1]
        pat = re.compile(rf"\bfacet\s+{re.escape(leaf)}\b")
        assert pat.search(ffl_text), f"no `facet {leaf}` found in FFL for {qn}"


def test_facet_namespaces_exist_in_ffl(ffl_text):
    """Each distinct facet namespace must be a declared `namespace` in the FFL."""
    namespaces = {f["namespace"] for f in catalog.facets()}
    for ns in namespaces:
        pat = re.compile(rf"\bnamespace\s+{re.escape(ns)}\b")
        assert pat.search(ffl_text), f"namespace {ns} not declared in any .ffl"


def test_all_ffl_compiles_with_annotations():
    """All package .ffl compile + validate together (Effect/Cost/Timeout mixins valid)."""
    from facetwork.parser import FFLParser
    from facetwork.source import CompilerInput, FileOrigin, SourceEntry
    from facetwork.validator import validate

    files = sorted(_FFL_DIR.glob("*.ffl"))
    assert files, "no .ffl files under src/genomics/ffl"
    entries = [
        SourceEntry(
            text=p.read_text(encoding="utf-8"),
            origin=FileOrigin(path=str(p)),
            is_library=(i > 0),
        )
        for i, p in enumerate(files)
    ]
    compiler_input = CompilerInput(
        primary_sources=[entries[0]],
        library_sources=entries[1:],
    )
    program_ast, _registry = FFLParser().parse_sources(compiler_input)
    result = validate(program_ast)
    assert not result.errors, "; ".join(str(e) for e in result.errors)
