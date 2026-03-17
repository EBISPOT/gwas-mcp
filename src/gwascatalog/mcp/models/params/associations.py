from __future__ import annotations

from typing import final

from pydantic import ConfigDict

from gwascatalog.mcp.models.params.base import Params
from gwascatalog.mcp.models.params.types import (
    AccessionId,
    AssociationId,
    EfoId,
    EfoTrait,
    FullPValueSet,
    MappedGene,
    PubmedId,
    RsId,
    ShowChildTrait,
)


@final
class GetAssociationsParams(Params):
    """Parameters for GET https://ebi.ac.uk/gwas/api/rest/v2/associations"""

    model_config = ConfigDict(coerce_numbers_to_str=True)

    association_id: AssociationId | None = None
    efo_trait: EfoTrait | None = None
    efo_id: EfoId | None = None
    rs_id: RsId | None = None
    mapped_gene: MappedGene | None = None
    accession_id: AccessionId | None = None
    pubmed_id: PubmedId | None = None
    full_pvalue_set: FullPValueSet | None = None
    show_child_trait: ShowChildTrait | None = None
