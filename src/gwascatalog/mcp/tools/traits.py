"""Implementation for the gwascatalog_get_traits MCP tool."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gwascatalog.mcp.models import (
    EfoTraitResponse,
    GetTraitsParams,
    ToolResponse,
    TraitResult,
)

if TYPE_CHECKING:
    from gwascatalog.mcp.client import GwasCatalogClient


async def get_traits(
    client: GwasCatalogClient, params: GetTraitsParams
) -> ToolResponse[TraitResult]:
    fetch = await client.get_efo_traits(params)
    traits = [EfoTraitResponse.model_validate(item) for item in fetch["items"]]
    return ToolResponse.from_results(
        [t.to_result() for t in traits], params, fetch["page"]
    )
