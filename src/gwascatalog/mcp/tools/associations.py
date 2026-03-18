"""Implementation for the gwascatalog_get_associations MCP tool."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gwascatalog.mcp.models import (
    AssociationResponse,
    GetAssociationsParams,
    PaginationInfo,
)

_EMBEDDED_ASSOCIATIONS = "associations"
_EMBEDDED_LOCI = "loci"


if TYPE_CHECKING:
    from gwascatalog.mcp.client import GwasCatalogClient


async def get_associations(
    client: GwasCatalogClient, params: GetAssociationsParams
) -> str:
    data = await client.get_associations(params)

    # Detail mode
    if params.association_id is not None:
        assoc = AssociationResponse.model_validate(data)
        try:
            loci_data = await client.get_association_loci(params.association_id)
            loci_items = loci_data.get("_embedded", {}).get(_EMBEDDED_LOCI, [])
        except RuntimeError:
            loci_items = []
        return assoc.format_detail(loci_items)

    # List mode
    items = data.get("_embedded", {}).get(_EMBEDDED_ASSOCIATIONS, [])
    if not items:
        return "No associations found. Try different search terms or broader filters."

    associations = [AssociationResponse.model_validate(item) for item in items]
    page_info = PaginationInfo.model_validate(data["page"])
    csv_text = AssociationResponse.to_csv(associations)
    footer = page_info.format_footer()
    return f"{csv_text}\n\n{footer}"
