"""Pydantic models returned by MCP tool functions."""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class _ExcludeNoneModel(BaseModel):
    """Base that drops None values and empty lists during serialization.

    This is important to reduce the size of MCP tool responses, which can
    be large when many fields are null or empty.
    """

    model_config = ConfigDict(
        ser_json_inf_nan="constants",
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        kwargs.setdefault("exclude_none", True)
        result = super().model_dump(**kwargs)
        return {k: v for k, v in result.items() if v != []}


class PageSummary(BaseModel):
    """Pagination summary for paginated tool responses."""

    page: int
    total_pages: int
    total_results: int


class TraitResult(_ExcludeNoneModel):
    """A single EFO trait result."""

    efo_id: str
    efo_trait: str
    uri: str | None = None


class AncestryResult(_ExcludeNoneModel):
    """A single ancestry entry for a study."""

    type: str | None = None
    n: int | None = None
    ancestral_groups: list[str] = Field(default_factory=list)
    recruitment_countries: list[str] = Field(default_factory=list)


class StudyResult(_ExcludeNoneModel):
    """A single GWAS study result with ancestry details."""

    accession_id: str
    initial_sample_size: str | None = None
    replication_sample_size: str | None = None
    gxe: bool | None = None
    gxg: bool | None = None
    snp_count: int | None = None
    full_summary_stats_available: bool | None = None
    pubmed_id: int | None = None
    platforms: str | None = None
    disease_trait: str | None = None
    genotyping_technologies: list[str] = Field(default_factory=list)
    efo_traits: list[TraitResult] = Field(default_factory=list)
    discovery_ancestry: list[str] = Field(default_factory=list)
    replication_ancestry: list[str] = Field(default_factory=list)
    cohort: list[str] = Field(default_factory=list)
    ancestries: list[AncestryResult] = Field(default_factory=list)


class AssociationResult(_ExcludeNoneModel):
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
    loci: list[dict[str, Any]] = Field(default_factory=list)


class ToolResponse[T](BaseModel):
    """Standard wrapper for all MCP tool responses."""

    results: list[T]
    summary: PageSummary
    truncated: bool
