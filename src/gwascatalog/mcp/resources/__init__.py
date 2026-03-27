"""MCP resource primitives for controlled vocabularies and reference data."""

from gwascatalog.mcp.resources.cohorts import fetch_cohorts
from gwascatalog.mcp.resources.schema import fetch_schema
from gwascatalog.mcp.resources.static import (
    read_ancestry_labels,
    read_variant_consequences,
)

__all__ = [
    "fetch_cohorts",
    "fetch_schema",
    "read_ancestry_labels",
    "read_variant_consequences",
]
