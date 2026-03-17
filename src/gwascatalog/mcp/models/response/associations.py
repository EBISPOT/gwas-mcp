from __future__ import annotations

from typing import Any, ClassVar

from pydantic import Field

from gwascatalog.mcp.models.response._helpers import _format_detail
from gwascatalog.mcp.models.response.abc import GwasCatalogResponse
from gwascatalog.mcp.models.response.traits import EfoTraitResponse


class AssociationResponse(GwasCatalogResponse):
    CSV_COLUMNS: ClassVar[list[str]] = [
        "association_id",
        "rs_id",
        "mapped_gene",
        "p_value",
        "beta",
        "ci",
        "risk_allele",
        "efo_trait",
        "study_accession",
    ]

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

    def to_csv_row(self) -> dict[str, Any]:
        """Return a flat dict suitable for CSV output."""
        rs_ids = [a.get("rs_id", "") for a in self.snp_allele]
        ci = self.range or ""
        if not ci and self.ci_lower is not None and self.ci_upper is not None:
            ci = f"[{self.ci_lower}-{self.ci_upper}]"
        return {
            "association_id": self.association_id,
            "rs_id": "; ".join(rs_ids),
            "mapped_gene": "; ".join(self.mapped_genes),
            "p_value": (self.p_value if self.p_value is not None else ""),
            "beta": self.beta or "",
            "ci": ci,
            "risk_allele": "; ".join(self.snp_effect_allele),
            "efo_trait": "; ".join(t.efo_trait for t in self.efo_traits),
            "study_accession": self.accession_id or "",
        }

    def format_detail(
        self,
        loci_data: list[dict[str, Any]],
    ) -> str:
        """Format this association as structured detail text with loci enrichment."""
        data: dict[str, Any] = {
            "Association ID": self.association_id,
        }

        rs_ids = [a.get("rs_id", "") for a in self.snp_allele]
        if rs_ids:
            data["Variant(s)"] = "; ".join(rs_ids)
        if self.mapped_genes:
            data["Mapped Gene(s)"] = "; ".join(self.mapped_genes)
        if self.snp_effect_allele:
            data["Risk Allele(s)"] = "; ".join(self.snp_effect_allele)
        if self.risk_frequency:
            data["Risk Frequency"] = self.risk_frequency
        if self.locations:
            data["Location(s)"] = "; ".join(self.locations)

        if self.p_value is not None:
            data["P-Value"] = self.p_value
        if self.pvalue_description:
            data["P-Value Context"] = self.pvalue_description

        if self.beta:
            data["Beta"] = self.beta
        ci = self.range or ""
        if not ci and self.ci_lower is not None and self.ci_upper is not None:
            ci = f"[{self.ci_lower}-{self.ci_upper}]"
        if ci:
            data["CI"] = ci

        if self.efo_traits:
            data["EFO Traits"] = [
                f"{t.efo_id} — {t.efo_trait}" for t in self.efo_traits
            ]
        if self.reported_trait:
            data["Reported Trait"] = "; ".join(self.reported_trait)

        if self.accession_id:
            data["Study"] = self.accession_id
        if self.first_author:
            data["First Author"] = self.first_author
        if self.pubmed_id:
            data["PubMed ID"] = self.pubmed_id

        enrichment: dict[str, Any] | None = None
        if loci_data:
            enrichment = {"Loci (detailed)": loci_data}

        return _format_detail(data, enrichment)
