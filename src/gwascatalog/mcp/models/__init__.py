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

__all__ = [
    "GetTraitsParams",
    "GetStudiesParams",
    "GetAssociationsParams",
    "AssociationResponse",
    "StudyResponse",
    "AncestryResponse",
    "PaginationInfo",
    "EfoTraitResponse",
]
