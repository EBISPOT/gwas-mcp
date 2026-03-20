"""Implementation for the gwascatalog_get_associations MCP tool."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from gwascatalog.mcp.models import (
    AssociationResponse,
    AssociationResult,
    GetAssociationsParams,
    ToolResponse,
)

if TYPE_CHECKING:
    from gwascatalog.mcp.client import GwasCatalogClient


async def _enrich(
    client: GwasCatalogClient, assoc: AssociationResponse
) -> AssociationResult:
    """Resolve loci for an association."""
    try:
        loci_items = await client.get_association_loci(assoc.association_id)
    except RuntimeError:
        loci_items = []
    return assoc.to_result(loci_items)


async def get_associations(
    client: GwasCatalogClient, params: GetAssociationsParams
) -> ToolResponse[AssociationResult]:
    fetch = await client.get_associations(params)
    associations = [AssociationResponse.model_validate(item) for item in fetch["items"]]
    results = await asyncio.gather(*[_enrich(client, a) for a in associations])
    return ToolResponse.from_results(list(results), params, fetch["page"])
