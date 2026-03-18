"""Implementation for the gwascatalog_get_studies MCP tool."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

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


async def _fetch_detail(
    client: GwasCatalogClient, study: StudyResponse
) -> dict[str, Any]:
    try:
        ancestry_data = await client.get_study_ancestries(study.accession_id)
        ancestry_items = ancestry_data.get("_embedded", {}).get(
            _EMBEDDED_ANCESTRIES, []
        )
    except RuntimeError:
        ancestry_items = []
    ancestries = [AncestryResponse.model_validate(a) for a in ancestry_items]
    return study.format_detail(ancestries)


async def get_studies(
    client: GwasCatalogClient, params: GetStudiesParams
) -> dict[str, Any]:
    data = await client.get_studies(params)

    if params.accession_id is not None:
        study = StudyResponse.model_validate(data)
        detail = await _fetch_detail(client, study)
        return {
            "results": [detail],
            "summary": {"total_results": 1},
            "truncated": False,
        }

    items = data.get("_embedded", {}).get(_EMBEDDED_STUDIES, [])
    studies = [StudyResponse.model_validate(item) for item in items]
    page_info = PaginationInfo.model_validate(data["page"])
    results = await asyncio.gather(*[_fetch_detail(client, s) for s in studies])
    return {
        "results": list(results),
        "summary": page_info.to_summary(),
        "truncated": page_info.is_truncated,
    }
