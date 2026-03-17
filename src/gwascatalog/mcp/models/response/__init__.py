"""
Response models for the GWAS Catalog API.

These models facilitate parsing and structuring data returned by the GWAS Catalog API,
optimising it for use by MCP tools and agents. In contrast with the params models,
the focus here isn't on structural data validation.
"""

from gwascatalog.mcp.models.response.ancestry import AncestryResponse
from gwascatalog.mcp.models.response.associations import AssociationResponse
from gwascatalog.mcp.models.response.pagination import PaginationInfo
from gwascatalog.mcp.models.response.studies import StudyResponse
from gwascatalog.mcp.models.response.traits import EfoTraitResponse

__all__ = [
    "AncestryResponse",
    "AssociationResponse",
    "StudyResponse",
    "EfoTraitResponse",
    "PaginationInfo",
]
