"""
Data models for GWAS Catalog API request parameters and response structures.
"""

from gwascatalog.mcp.models.params import (
    GetAssociationsParams,
    GetStudiesParams,
    GetTraitsParams,
)
from gwascatalog.mcp.models.response import (
    AncestryResponse,
    AssociationResponse,
    EfoTraitResponse,
    PaginationInfo,
    StudyResponse,
)
from gwascatalog.mcp.models.results import (
    AncestryResult,
    AssociationResult,
    PageSummary,
    StudyResult,
    ToolResponse,
    TraitResult,
)

__all__ = [
    "AncestryResponse",
    "AncestryResult",
    "AssociationResponse",
    "AssociationResult",
    "EfoTraitResponse",
    "GetAssociationsParams",
    "GetStudiesParams",
    "GetTraitsParams",
    "PageSummary",
    "PaginationInfo",
    "StudyResponse",
    "StudyResult",
    "ToolResponse",
    "TraitResult",
]
