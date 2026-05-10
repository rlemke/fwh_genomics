"""Shared shim layer for genomics handlers.

The handler modules in the parent package call into the simulators in
``genomics.tools._lib`` via this shim. The shim re-exports the
implementation under stable names so handlers don't need to track
module reorganizations under ``tools/_lib``.
"""
