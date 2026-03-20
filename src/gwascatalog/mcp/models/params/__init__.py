"""
Request parameter models for the GWAS Catalog API.

These models use custom types defined in `types.py` to implement a "parse, don't
validate" approach for untrusted input. This ensures rapid, accurate error reporting
for MCP tools interacting with the GWAS Catalog.
"""

from gwascatalog.mcp.models.params.associations import GetAssociationsParams
from gwascatalog.mcp.models.params.studies import GetStudiesParams
from gwascatalog.mcp.models.params.traits import GetTraitsParams
from gwascatalog.mcp.models.params.types import (
    URI,
    AccessionId,
    AncestralGroup,
    AssociationId,
    AssociationSortKeyField,
    Cohort,
    DiseaseTrait,
    EfoId,
    EfoTrait,
    FullPValueSet,
    GxE,
    MappedGene,
    PageField,
    PubmedId,
    RsId,
    ShowChildTrait,
    SizeField,
    SortDirectionField,
    StudySortKeyField,
    TraitSortKeyField,
)

__all__ = [
    "GetStudiesParams",
    "GetTraitsParams",
    "GetAssociationsParams",
    "AccessionId",
    "AncestralGroup",
    "AssociationId",
    "AssociationSortKeyField",
    "Cohort",
    "DiseaseTrait",
    "EfoId",
    "EfoTrait",
    "FullPValueSet",
    "GxE",
    "MappedGene",
    "PageField",
    "PubmedId",
    "RsId",
    "ShowChildTrait",
    "SizeField",
    "SortDirectionField",
    "StudySortKeyField",
    "TraitSortKeyField",
    "URI",
]
