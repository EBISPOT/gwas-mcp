"""Association result model."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BeforeValidator, Field

from gwascatalog.mcp.models import MappedGene, PubmedId
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

_NRStr = Annotated[
    Literal["NR", "NA"] | str | None,
    BeforeValidator(_none_if_placeholder),
    Field(
        description="String field that may be 'NR' (Not Reported) or 'NA' (Not "
        "Applicable). Human curators have checked NR/NA fields while None "
        "just means missing or unverified."
    ),
]

AssociationIdField = Annotated[int, Field(description="GWAS Catalog association ID")]
RiskFrequencyField = Annotated[
    _NRStr,
    Field(
        description=(
            "Reported risk/effect allele frequency associated with"
            " strongest SNP in controls"
        ),
        examples=["0.523756034"],
    ),
]

# p values
PValueDescriptionField = Annotated[
    _NRStr,
    BeforeValidator(_none_if_placeholder),
    Field(
        description="Information describing context of p-value",
        examples=["females", "smokers"],
    ),
]

PValueField = Annotated[
    float, Field(description="Reported p-value for the association")
]
PValueMantissaField = Annotated[
    int, Field(description="Reported p-value for strongest SNP risk allele (Mantissa)")
]
PValueExponentField = Annotated[
    int, Field(description="Reported p-value for strongest SNP risk allele (Exponent)")
]

# effect sizes

OrValue = Annotated[
    str,
    BeforeValidator(_none_if_placeholder),
    Field(description="Odds ratio string format", examples=["0.78137505"]),
]

BetaField = Annotated[
    str,
    BeforeValidator(_none_if_placeholder),
    Field(description="A concatenated text containing beta number, direction and unit"),
]
RangeField = Annotated[
    str,
    BeforeValidator(_none_if_placeholder),
    Field(description="95% confidence interval", examples=["12.41-19.61"]),
]
DescriptionField = Annotated[
    str,
    BeforeValidator(_none_if_placeholder),
    Field(
        description="Additional comment relating to beta or OR value",
        examples=["Discovery"],
    ),
]


# other fields
MultiSNPHaplotypeField = Annotated[
    bool, Field(description="Whether the association is for a multi-SNP haplotype")
]
SNPInteractionField = Annotated[
    bool, Field(description="Whether the association is for a SNP-SNP interaction")
]
LastMappingDateField = Annotated[
    datetime, Field(description="Last time this association was mapped to Ensembl")
]
LastUpdatedField = Annotated[
    datetime, Field(description="Last time this association was updated")
]

EfoTraitsField = Annotated[
    list[TraitResult],
    Field(description="Experimental Factor Ontology trait for this association"),
]
AccessionIdField = Annotated[
    str,
    Field(
        description="GWAS Catalog Accession ID linked to the association",
        examples=["GCST90566353"],
    ),
]
LocationsField = Annotated[list[str], Field(description="The SNP’s genomic locations")]
ReportedTraitField = Annotated[list[str], Field(description="Author-reported traits")]
FirstAuthorField = Annotated[str, Field(description="First author of the publication")]
SNPEffectAlleleField = Annotated[
    list[str],
    Field(
        description=(
            "SNP(s) and effect allele most strongly associated within the locus"
        ),
        examples=["rs7329174-G"],
    ),
]


class AssociationResult(BaseResult):
    """A single variant-trait association result with loci details."""

    association_id: AssociationIdField
    risk_frequency: RiskFrequencyField = None
    p_value: PValueField | None = None
    pvalue_description: PValueDescriptionField = None
    pvalue_mantissa: PValueMantissaField | None = None
    pvalue_exponent: PValueExponentField | None = None
    beta: BetaField | None = None
    or_value: OrValue | None = None
    range: RangeField | None = None
    efo_traits: EfoTraitsField = Field(default_factory=list)
    reported_trait: ReportedTraitField = Field(default_factory=list)
    accession_id: AccessionIdField | None = None
    locations: LocationsField = Field(default_factory=list)
    mapped_genes: list[MappedGene] = Field(default_factory=list)
    pubmed_id: PubmedId | None = None
    first_author: FirstAuthorField | None = None
    snp_effect_allele: SNPEffectAlleleField = Field(default_factory=list)
