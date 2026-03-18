from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from gwascatalog.mcp.models.response.traits import EfoTraitResponse


class AssociationResponse(BaseModel):
    association_id: int
    risk_frequency: str | None = None
    pvalue_description: str | None = None
    range: str | None = None
    beta: str | None = None
    p_value: float | None = None
    efo_traits: list[EfoTraitResponse] = Field(default_factory=list)
    reported_trait: list[str] = Field(default_factory=list)
    accession_id: str | None = None
    locations: list[str] = Field(default_factory=list)
    mapped_genes: list[str] = Field(default_factory=list)
    pubmed_id: str | None = None
    first_author: str | None = None
    ci_lower: float | None = None
    ci_upper: float | None = None
    snp_effect_allele: list[str] = Field(default_factory=list)
    snp_allele: list[dict] = Field(default_factory=list)

    def _ci(self) -> str:
        ci = self.range or ""
        if not ci and self.ci_lower is not None and self.ci_upper is not None:
            ci = f"[{self.ci_lower}-{self.ci_upper}]"
        return ci

    def format_detail(self, loci_data: list[dict[str, Any]]) -> dict[str, Any]:
        rs_ids = [a.get("rs_id", "") for a in self.snp_allele]
        result: dict[str, Any] = {"association_id": self.association_id}
        if rs_ids:
            result["variants"] = rs_ids
        if self.mapped_genes:
            result["mapped_genes"] = self.mapped_genes
        if self.snp_effect_allele:
            result["risk_alleles"] = self.snp_effect_allele
        if self.risk_frequency:
            result["risk_frequency"] = self.risk_frequency
        if self.locations:
            result["locations"] = self.locations
        if self.p_value is not None:
            result["p_value"] = self.p_value
        if self.pvalue_description:
            result["p_value_context"] = self.pvalue_description
        if self.beta:
            result["beta"] = self.beta
        ci = self._ci()
        if ci:
            result["ci"] = ci
        if self.efo_traits:
            result["efo_traits"] = [
                {"efo_id": t.efo_id, "efo_trait": t.efo_trait} for t in self.efo_traits
            ]
        if self.reported_trait:
            result["reported_traits"] = self.reported_trait
        if self.accession_id:
            result["study_accession"] = self.accession_id
        if self.first_author:
            result["first_author"] = self.first_author
        if self.pubmed_id:
            result["pubmed_id"] = self.pubmed_id
        if loci_data:
            result["loci"] = loci_data
        return result
