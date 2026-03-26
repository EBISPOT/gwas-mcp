from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, StringConstraints

AssociationSortKeys = Literal["p_value", "risk_frequency", "or_value", "beta_num"]
StudySortKeys = Literal["accession_id", "snp_count"]
TraitSortKeys = Literal["efo_id", "efo_trait"]
SortDirection = Literal["asc", "desc"]


AssociationId = Annotated[str, Field(max_length=19, pattern=r"^\d{1,19}$")]
EfoId = Annotated[
    str,
    Field(
        pattern=r"^[A-Za-z]+_\d+$",
        description="The trait URI shortform",
        examples=["EFO_0001060", "MONDO_0005180"],
    ),
]
AccessionId = Annotated[
    str,
    Field(
        pattern=r"^GCST\d+$",
        description="GWAS Catalog study accession ID",
        examples=["GCST000854", "GCST004138"],
    ),
]
RsId = Annotated[
    str,
    Field(
        pattern=r"^rs\d+$",
        description="SNP rsID; if a haplotype it may include more than one rs number "
        "(multiple SNPs comprising the haplotype)",
        examples=["rs3093017"],
    ),
]
PubmedId = Annotated[
    str,
    Field(
        pattern=r"^[1-9][0-9]*$",
        min_length=1,
        max_length=12,
        description="Pubmed ID of the publication",
        examples=["35241825", "28256260"],
    ),
]
AssociationSortKeyField = Annotated[
    AssociationSortKeys, Field(description="Fields to sort by (associations)")
]
StudySortKeyField = Annotated[
    StudySortKeys, Field(description="Fields to sort by (studies)")
]
TraitSortKeyField = Annotated[
    TraitSortKeys, Field(description="Fields to sort by (traits)")
]
SortDirectionField = Annotated[SortDirection, Field(description="Direction to sort by")]


# reject lowercase letters and any punctuation
# reject hyphens at the start and end of a symbol
hgnc_regex = r"^[A-Z0-9]+(?:-[A-Z0-9]+)*$"

MappedGene = Annotated[
    str,
    StringConstraints(pattern=hgnc_regex),
    Field(
        description="Gene(s) overlapping the variant. If a variant is intergenic, the "
        "closest 5' and 3' genes are listed. Must be a HGNC symbol.",
        examples=["ISG20", "A2M", "A4GALT", "HLA-DRA", "MT-ND1"],
    ),
]

PageField = Annotated[int, Field(ge=0, description="Zero-based page index")]

SizeField = Annotated[
    int, Field(ge=1, le=50, description="The size of the page to be returned")
]

FullPValueSet = Annotated[
    bool,
    Field(description="Whether full summary statistics are available for this study"),
]

EfoTrait = Annotated[
    str, Field(description="The trait name or label", examples=["Celiac disease"])
]

ShowChildTrait = Annotated[
    bool,
    Field(description="Display entities for descendants of a parent Efo Trait Term"),
]

DiseaseTrait = Annotated[
    str,
    Field(
        description="Free text description of the trait investigated in this study",
        examples=["Early-onset Parkinson's disease"],
    ),
]
AncestralGroup = Annotated[
    str,
    Field(
        description="Ancestry category group label, assigned to reduce complexity "
        "within the data sets and place samples in context",
        examples=["European"],
    ),
]
Cohort = Annotated[
    str,
    Field(
        description="Discovery stage cohorts used in this study", examples=["BioImage"]
    ),
]

GxE = Annotated[
    bool,
    Field(description="Whether the study investigates a gene-environment interaction"),
]

URI = Annotated[
    str,
    Field(
        description="The trait URI or unique identifier",
        examples=["http://www.ebi.ac.uk/efo/EFO_0001060"],
    ),
]

ExtendedGeneset = Annotated[
    bool,
    Field(description="Show extended matching genes in addition to the mapped genes"),
]
