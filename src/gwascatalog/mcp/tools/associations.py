"""Implementation for the gwascatalog_get_associations MCP tool."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gwascatalog.mcp.models import (
    AssociationResult,
    GetAssociationsParams,
    ToolResponse,
)

if TYPE_CHECKING:
    from gwascatalog.mcp.client import GwasCatalogClient


async def get_associations(
    client: GwasCatalogClient, params: GetAssociationsParams
) -> ToolResponse[AssociationResult]:
    fetch = await client.get_associations(params)
    results = [AssociationResult.model_validate(item) for item in fetch["items"]]
    return ToolResponse.from_results(results, params, fetch["page"])
