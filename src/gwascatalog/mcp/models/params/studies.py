from __future__ import annotations

from typing import final

from gwascatalog.mcp.models.params.base import Params
from gwascatalog.mcp.models.params.types import (
    AccessionId,
    AncestralGroup,
    Cohort,
    DiseaseTrait,
    EfoId,
    EfoTrait,
    FullPValueSet,
    GxE,
    MappedGene,
    PubmedId,
    ShowChildTrait,
)


@final
class GetStudiesParams(Params):
    """
    Parameters for GET https://ebi.ac.uk/gwas/api/rest/v2/studies
    """

    accession_id: AccessionId | None = None
    efo_trait: EfoTrait | None = None
    efo_id: EfoId | None = None
    disease_trait: DiseaseTrait | None = None
    mapped_gene: MappedGene | None = None
    pubmed_id: PubmedId | None = None
    ancestral_group: AncestralGroup | None = None
    cohort: Cohort | None = None
    full_pvalue_set: FullPValueSet | None = None
    gxe: GxE | None = None
    show_child_trait: ShowChildTrait | None = None
