from __future__ import annotations

from typing import final

from gwascatalog.mcp.models.params.base import Params
from gwascatalog.mcp.models.params.types import (
    URI,
    EfoId,
    EfoTrait,
    ExtendedGeneset,
    MappedGene,
    PubmedId,
)


@final
class GetTraitsParams(Params):
    """Parameters for GET https://ebi.ac.uk/gwas/api/rest/v2/traits"""

    efo_id: EfoId | None = None
    efo_trait: EfoTrait | None = None
    mapped_gene: MappedGene | None = None
    pubmed_id: PubmedId | None = None
    uri: URI | None = None
    extended_geneset: ExtendedGeneset | None = None
