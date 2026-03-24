"""Association result model."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BeforeValidator, Field

from gwascatalog.mcp.models.results.baseresult import BaseResult
from gwascatalog.mcp.models.results.traits import TraitResult

_PLACEHOLDERS = frozenset(("-", ""))


def _none_if_placeholder(v: object) -> object:
    """Coerce placeholder strings to None, preserving 'NR'."""
    if isinstance(v, str) and v in _PLACEHOLDERS:
        return None
    return v


# meaningful absences distinct from missing data
# (checked by human curators!)
NR = Literal["NR"]
NA = Literal["NA"]

_NRStr = Annotated[
    NR | NA | str | None,
    BeforeValidator(_none_if_placeholder),
    Field(
        description="String field that may be 'NR' (Not Reported) or 'NA' (Not "
        "Applicable). Human curators have checked NR/NA fields while None "
        "just means missing or unverified."
    ),
]


class AssociationResult(BaseResult):
    """A single variant-trait association result with loci details."""

    association_id: int
    risk_frequency: _NRStr = None
    pvalue_description: _NRStr = None
    range: _NRStr = None
    beta: _NRStr = None
    p_value: float | None = None
    efo_traits: list[TraitResult] = Field(default_factory=list)
    reported_trait: list[str] = Field(default_factory=list)
    accession_id: str | None = None
    locations: list[str] = Field(default_factory=list)
    mapped_genes: list[str] = Field(default_factory=list)
    pubmed_id: str | None = None
    first_author: str | None = None
    ci_lower: float | None = None
    ci_upper: float | None = None
    snp_effect_allele: list[str] = Field(default_factory=list)
    snp_allele: list[dict[str, Any]] = Field(default_factory=list)
