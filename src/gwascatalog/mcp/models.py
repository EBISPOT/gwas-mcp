"""Pydantic models for GWAS Catalog MCP tools."""

from __future__ import annotations

from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

# --- Constrained types ---

EfoId = Annotated[str, Field(pattern=r"^[A-Za-z]+_\d+$")]
AccessionId = Annotated[str, Field(pattern=r"^GCST\d+$")]
RsId = Annotated[str, Field(pattern=r"^rs\d+$")]
PubmedId = Annotated[str, Field(pattern=r"^\d+$")]
Chromosome = Annotated[str, Field(pattern=r"^(1[0-9]|2[0-2]|[1-9]|X|Y|MT)$")]


# --- Parameter models ---


class GetAssociationsParams(BaseModel):
    association_id: int | None = None
    efo_trait: str | None = None
    efo_id: str | None = None
    rs_id: str | None = None
    mapped_gene: str | None = None
    accession_id: str | None = None
    pubmed_id: str | None = None
    full_pvalue_set: bool | None = None
    show_child_trait: bool | None = None
    page: int = 0
    size: int = 10
    sort: str | None = None
    direction: str | None = None


class GetStudiesParams(BaseModel):
    accession_id: str | None = None
    efo_trait: str | None = None
    efo_id: str | None = None
    disease_trait: str | None = None
    mapped_gene: str | None = None
    pubmed_id: str | None = None
    ancestral_group: str | None = None
    cohort: str | None = None
    full_pvalue_set: bool | None = None
    gxe: bool | None = None
    show_child_trait: bool | None = None
    page: int = 0
    size: int = 10
    sort: str | None = None
    direction: str | None = None


class GetTraitsParams(BaseModel):
    efo_id: str | None = None
    efo_trait: str | None = None
    mapped_gene: str | None = None
    pubmed_id: str | None = None
    uri: str | None = None
    page: int = 0
    size: int = 10
    sort: str | None = None
    direction: str | None = None


# --- Response models ---


class PaginationInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    size: int
    total_elements: int = Field(alias="totalElements")
    total_pages: int = Field(alias="totalPages")
    number: int


class EfoTraitResponse(BaseModel):
    efo_id: str
    efo_trait: str
    uri: str | None = None


class StudyResponse(BaseModel):
    accession_id: str
    initial_sample_size: str | None = None
    replication_sample_size: str | None = None
    gxe: bool | None = None
    gxg: bool | None = None
    snp_count: int | None = None
    imputed: bool | None = None
    pooled: bool | None = None
    full_summary_stats_available: bool | None = None
    pubmed_id: int | None = None
    platforms: str | None = None
    disease_trait: str | None = None
    genotyping_technologies: list[str] = Field(
        default_factory=list,
    )
    efo_traits: list[EfoTraitResponse] = Field(
        default_factory=list,
    )
    discovery_ancestry: list[str] = Field(default_factory=list)
    replication_ancestry: list[str] = Field(default_factory=list)
    cohort: list[str] = Field(default_factory=list)


class AssociationResponse(BaseModel):
    association_id: int
    risk_frequency: str | None = None
    pvalue_description: str | None = None
    range: str | None = None
    beta: str | None = None
    p_value: float | None = None
    efo_traits: list[EfoTraitResponse] = Field(
        default_factory=list,
    )
    reported_trait: list[str] = Field(default_factory=list)
    accession_id: str | None = None
    locations: list[str] = Field(default_factory=list)
    mapped_genes: list[str] = Field(default_factory=list)
    pubmed_id: str | None = None
    first_author: str | None = None
    ci_lower: float | None = None
    ci_upper: float | None = None
    snp_effect_allele: list[str] = Field(
        default_factory=list,
    )
    snp_allele: list[dict] = Field(default_factory=list)


class AncestryResponse(BaseModel):
    type: str | None = None
    number_of_individuals: int | None = None
    ancestral_groups: list[dict] = Field(default_factory=list)
    country_of_origin: list[dict] = Field(default_factory=list)
    country_of_recruitment: list[dict] = Field(
        default_factory=list,
    )


T = TypeVar("T")


class PagedResponse(BaseModel, Generic[T]):
    content: list[T]
    page: PaginationInfo
