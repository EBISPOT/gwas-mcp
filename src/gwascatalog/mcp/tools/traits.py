"""Implementation for the gwascatalog_get_traits MCP tool."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gwascatalog.mcp.models import (
    EfoTraitResponse,
    GetTraitsParams,
    PageSummary,
    PaginationInfo,
    ToolResponse,
    TraitResult,
)

_EMBEDDED_TRAITS = "efo_traits"

if TYPE_CHECKING:
    from gwascatalog.mcp.client import GwasCatalogClient


async def get_traits(
    client: GwasCatalogClient, params: GetTraitsParams
) -> ToolResponse[TraitResult]:
    data = await client.get_efo_traits(params)

    if params.efo_id is not None:
        trait = EfoTraitResponse.model_validate(data)
        return ToolResponse(
            results=[trait.to_result()],
            summary=PageSummary(page=0, total_pages=1, total_results=1),
            truncated=False,
        )

    items = data.get("_embedded", {}).get(_EMBEDDED_TRAITS, [])
    traits = [EfoTraitResponse.model_validate(item) for item in items]
    page_info = PaginationInfo.model_validate(data["page"])
    return ToolResponse(
        results=[t.to_result() for t in traits],
        summary=page_info.to_summary(),
        truncated=page_info.is_truncated,
    )
