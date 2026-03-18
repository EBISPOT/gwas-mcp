"""Implementation for the gwascatalog_get_studies MCP tool."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gwascatalog.mcp.models import (
    AncestryResponse,
    GetStudiesParams,
    PaginationInfo,
    StudyResponse,
)

_EMBEDDED_STUDIES = "studies"
_EMBEDDED_ANCESTRIES = "ancestries"

if TYPE_CHECKING:
    from gwascatalog.mcp.client import GwasCatalogClient


async def get_studies(client: GwasCatalogClient, params: GetStudiesParams) -> str:
    data = await client.get_studies(params)

    # Detail mode
    if params.accession_id is not None:
        study = StudyResponse.model_validate(data)
        try:
            ancestry_data = await client.get_study_ancestries(params.accession_id)
            ancestry_items = ancestry_data.get("_embedded", {}).get(
                _EMBEDDED_ANCESTRIES, []
            )
        except RuntimeError:
            ancestry_items = []
        ancestries = [AncestryResponse.model_validate(a) for a in ancestry_items]
        return study.format_detail(ancestries)

    # List mode
    items = data.get("_embedded", {}).get(_EMBEDDED_STUDIES, [])
    if not items:
        return "No studies found. Try different search terms or broader filters."

    studies = [StudyResponse.model_validate(item) for item in items]
    page_info = PaginationInfo.model_validate(data["page"])
    csv_text = StudyResponse.to_csv(studies)
    footer = page_info.format_footer()
    return f"{csv_text}\n\n{footer}"
