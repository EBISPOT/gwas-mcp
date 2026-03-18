from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from gwascatalog.mcp.models.response.ancestry import AncestryResponse
from gwascatalog.mcp.models.response.traits import EfoTraitResponse


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

    def format_detail(self, ancestries: list[AncestryResponse]) -> dict[str, Any]:
        result: dict[str, Any] = {"accession_id": self.accession_id}
        if self.disease_trait:
            result["disease_trait"] = self.disease_trait
        if self.efo_traits:
            result["efo_traits"] = [
                {"efo_id": t.efo_id, "efo_trait": t.efo_trait} for t in self.efo_traits
            ]
        if self.pubmed_id is not None:
            result["pubmed_id"] = self.pubmed_id
        if self.initial_sample_size:
            result["initial_sample_size"] = self.initial_sample_size
        if self.replication_sample_size:
            result["replication_sample_size"] = self.replication_sample_size
        if self.discovery_ancestry:
            result["discovery_ancestry"] = self.discovery_ancestry
        if self.replication_ancestry:
            result["replication_ancestry"] = self.replication_ancestry
        if self.snp_count:
            result["snp_count"] = self.snp_count
        if self.genotyping_technologies:
            result["genotyping_technologies"] = self.genotyping_technologies
        if self.platforms:
            result["platforms"] = self.platforms
        if self.cohort:
            result["cohort"] = self.cohort
        if self.gxe:
            result["gxe"] = self.gxe
        if self.gxg:
            result["gxg"] = self.gxg
        if self.full_summary_stats_available:
            result["full_summary_stats_available"] = True
        if ancestries:
            result["ancestries"] = [
                {
                    "type": a.type,
                    "n": a.number_of_individuals,
                    "ancestral_groups": [
                        g.ancestral_group
                        for g in a.ancestral_groups
                        if g.ancestral_group
                    ],
                    "recruitment_countries": [
                        c.country_name
                        for c in a.country_of_recruitment
                        if c.country_name
                    ],
                }
                for a in ancestries
            ]
        return result
