"""Implementation for the gwascatalog_get_associations MCP tool."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from gwascatalog.mcp.models import (
    AssociationResponse,
    AssociationResult,
    GetAssociationsParams,
    PageSummary,
    PaginationInfo,
    ToolResponse,
)

_EMBEDDED_ASSOCIATIONS = "associations"
_EMBEDDED_LOCI = "loci"


if TYPE_CHECKING:
    from gwascatalog.mcp.client import GwasCatalogClient


async def _fetch_detail(
    client: GwasCatalogClient, assoc: AssociationResponse
) -> AssociationResult:
    try:
        loci_data = await client.get_association_loci(assoc.association_id)
        loci_items = loci_data.get("_embedded", {}).get(_EMBEDDED_LOCI, [])
    except RuntimeError:
        loci_items = []
    return assoc.to_result(loci_items)


async def get_associations(
    client: GwasCatalogClient, params: GetAssociationsParams
) -> ToolResponse[AssociationResult]:
    data = await client.get_associations(params)

    if params.association_id is not None:
        assoc = AssociationResponse.model_validate(data)
        detail = await _fetch_detail(client, assoc)
        return ToolResponse(
            results=[detail],
            summary=PageSummary(page=0, total_pages=1, total_results=1),
            truncated=False,
        )

    items = data.get("_embedded", {}).get(_EMBEDDED_ASSOCIATIONS, [])
    associations = [AssociationResponse.model_validate(item) for item in items]
    page_info = PaginationInfo.model_validate(data["page"])
    results = await asyncio.gather(*[_fetch_detail(client, a) for a in associations])
    return ToolResponse(
        results=list(results),
        summary=page_info.to_summary(),
        truncated=page_info.is_truncated,
    )
