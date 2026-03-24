"""Association result model."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from gwascatalog.mcp.models.results.baseresult import BaseResult
from gwascatalog.mcp.models.results.traits import TraitResult


class AssociationResult(BaseResult):
    """A single variant-trait association result with loci details."""

    association_id: int
    risk_frequency: str | None = None
    pvalue_description: str | None = None
    range: str | None = None
    beta: str | None = None
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
