from __future__ import annotations

from pydantic import BaseModel, Field

from gwascatalog.mcp.models.params.types import StudySortKeys
from gwascatalog.mcp.models.response.ancestry import AncestryResponse
from gwascatalog.mcp.models.response.traits import EfoTraitResponse
from gwascatalog.mcp.models.results import StudyResult


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
    genotyping_technologies: list[str] = Field(default_factory=list)
    efo_traits: list[EfoTraitResponse] = Field(default_factory=list)
    discovery_ancestry: list[str] = Field(default_factory=list)
    replication_ancestry: list[str] = Field(default_factory=list)
    cohort: list[str] = Field(default_factory=list)
    sort: StudySortKeys | None = None

    def to_result(self, ancestries: list[AncestryResponse]) -> StudyResult:
        return StudyResult(
            accession_id=self.accession_id,
            initial_sample_size=self.initial_sample_size,
            replication_sample_size=self.replication_sample_size,
            gxe=self.gxe,
            gxg=self.gxg,
            snp_count=self.snp_count,
            full_summary_stats_available=self.full_summary_stats_available,
            pubmed_id=self.pubmed_id,
            platforms=self.platforms,
            disease_trait=self.disease_trait,
            genotyping_technologies=self.genotyping_technologies,
            efo_traits=[t.to_result() for t in self.efo_traits],
            discovery_ancestry=self.discovery_ancestry,
            replication_ancestry=self.replication_ancestry,
            cohort=self.cohort,
            ancestries=[a.to_summary() for a in ancestries],
        )
