"""Implementation for the gwascatalog_get_traits MCP tool."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gwascatalog.mcp.models import EfoTraitResponse, GetTraitsParams, PaginationInfo

_EMBEDDED_TRAITS = "efo_traits"

if TYPE_CHECKING:
    from gwascatalog.mcp.client import GwasCatalogClient


async def get_traits(client: GwasCatalogClient, params: GetTraitsParams) -> str:
    data = await client.get_efo_traits(params)

    # Detail mode
    if params.efo_id is not None:
        trait = EfoTraitResponse.model_validate(data)
        return trait.format_detail()

    # List mode
    items = data.get("_embedded", {}).get(_EMBEDDED_TRAITS, [])
    if not items:
        return "No traits found. Try a different search term or broader query."

    traits = [EfoTraitResponse.model_validate(item) for item in items]
    page_info = PaginationInfo.model_validate(data["page"])
    csv_text = EfoTraitResponse.to_csv(traits)
    footer = page_info.format_footer()
    return f"{csv_text}\n\n{footer}"
