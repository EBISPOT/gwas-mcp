from __future__ import annotations

from pydantic import BaseModel, Field

from gwascatalog.mcp.models.response.traits import EfoTraitResponse
from gwascatalog.mcp.models.results import AssociationResult


class AssociationResponse(BaseModel):
    association_id: int
    risk_frequency: str | None = None
    pvalue_description: str | None = None
    range: str | None = None
    beta: str | None = None
    or_value: str | None = None
    pvalue_mantissa: int | None = None
    pvalue_exponent: int | None = None
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

    def to_result(self) -> AssociationResult:
        return AssociationResult(
            association_id=self.association_id,
            risk_frequency=self.risk_frequency,
            pvalue_description=self.pvalue_description,
            range=self.range,
            beta=self.beta,
            p_value=self.p_value,
            efo_traits=[t.to_result() for t in self.efo_traits],
            reported_trait=self.reported_trait,
            accession_id=self.accession_id,
            locations=self.locations,
            mapped_genes=self.mapped_genes,
            pubmed_id=self.pubmed_id,
            first_author=self.first_author,
            snp_effect_allele=self.snp_effect_allele,
            or_value=self.or_value,
            pvalue_mantissa=self.pvalue_mantissa,
            pvalue_exponent=self.pvalue_exponent,
        )
