from __future__ import annotations

from typing import Any, ClassVar

from pydantic import Field

from gwascatalog.mcp.models.response._helpers import _format_detail
from gwascatalog.mcp.models.response.abc import GwasCatalogResponse
from gwascatalog.mcp.models.response.ancestry import AncestryResponse
from gwascatalog.mcp.models.response.traits import EfoTraitResponse


class StudyResponse(GwasCatalogResponse):
    CSV_COLUMNS: ClassVar[list[str]] = [
        "accession_id",
        "disease_trait",
        "efo_trait",
        "pubmed_id",
        "sample_size",
        "ancestral_groups",
    ]

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

    def to_csv_row(self) -> dict[str, Any]:
        """Return a flat dict suitable for CSV output."""
        efo_trait = "; ".join(t.efo_trait for t in self.efo_traits)
        ancestral_groups = "; ".join(self.discovery_ancestry)
        return {
            "accession_id": self.accession_id,
            "disease_trait": self.disease_trait or "",
            "efo_trait": efo_trait,
            "pubmed_id": (self.pubmed_id if self.pubmed_id is not None else ""),
            "sample_size": self.initial_sample_size or "",
            "ancestral_groups": ancestral_groups,
        }

    def format_detail(
        self,
        ancestries: list[AncestryResponse],
    ) -> str:
        """Format this study as structured detail text with ancestry enrichment."""
        data: dict[str, Any] = {"Accession": self.accession_id}

        if self.disease_trait:
            data["Disease/Trait"] = self.disease_trait
        if self.efo_traits:
            data["EFO Traits"] = [
                f"{t.efo_id} — {t.efo_trait}" for t in self.efo_traits
            ]
        if self.pubmed_id is not None:
            data["PubMed ID"] = self.pubmed_id
        if self.initial_sample_size:
            data["Initial Sample Size"] = self.initial_sample_size
        if self.replication_sample_size:
            data["Replication Sample Size"] = self.replication_sample_size
        if self.discovery_ancestry:
            data["Discovery Ancestry"] = self.discovery_ancestry
        if self.replication_ancestry:
            data["Replication Ancestry"] = self.replication_ancestry
        if self.snp_count:
            data["SNP Count"] = self.snp_count
        if self.genotyping_technologies:
            data["Genotyping Technologies"] = self.genotyping_technologies
        if self.platforms:
            data["Platforms"] = self.platforms
        if self.cohort:
            data["Cohort"] = self.cohort
        if self.gxe:
            data["GxE"] = self.gxe
        if self.gxg:
            data["GxG"] = self.gxg
        if self.full_summary_stats_available:
            data["Full Summary Stats"] = True

        enrichment: dict[str, Any] | None = None
        if ancestries:
            ancestry_lines: list[str] = []
            for a in ancestries:
                parts: list[str] = []
                if a.type:
                    parts.append(f"Type: {a.type}")
                groups = [getattr(g, "ancestral_group", "") for g in a.ancestral_groups]
                groups = [g for g in groups if g]
                if groups:
                    parts.append(f"Ancestral Groups: {', '.join(groups)}")
                if a.number_of_individuals:
                    parts.append(f"N: {a.number_of_individuals}")
                countries = [
                    getattr(c, "country_name", "") for c in a.country_of_recruitment
                ]
                countries = [c for c in countries if c]
                if countries:
                    parts.append(f"Recruitment: {', '.join(countries)}")
                ancestry_lines.append(", ".join(parts))
            enrichment = {"Ancestries": ancestry_lines}

        return _format_detail(data, enrichment)
