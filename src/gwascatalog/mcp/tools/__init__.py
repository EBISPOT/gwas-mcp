"""MCP tool implementations for the GWAS Catalog server."""

from gwascatalog.mcp.tools.associations import get_associations
from gwascatalog.mcp.tools.studies import get_studies
from gwascatalog.mcp.tools.traits import get_traits

__all__ = ["get_associations", "get_studies", "get_traits"]
